import io
import subprocess
import os
import time
import configparser

sysEOL = '\n' if os.name == 'posix' else '\r\n'

def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


def isPathBlacklisted(FILEPATH, noSubsList):
    for str in noSubsList:
        if str in FILEPATH.lower(): return True
    return False


def lineContains(line, *tup):
    for str in tup:
        if not str in line.lower(): return False
    return True


def beginExtraction(file, EXTRACT_FORCEDSUBS):
    filename, ext = os.path.splitext(file)
    bOutput = subprocess.check_output('mkvmerge --identify-verbose "' + file + '"', shell=True)
    output = bOutput.decode()
    outputlines = output.split(sysEOL)

    nTrack = -1
    # Extract english sub, no forced, no SDH
    for line in outputlines:
        if not os.path.isfile(file.replace(ext, '.eng.srt')) and lineContains(line, 'language:eng', 'subrip/srt', 'forced_track:0') and not 'track_name:sdh' in line.lower():
            print('')
            subprocess.call('mkvextract tracks "' + file + '" ' + str(nTrack) + ':"' + file.replace(ext, '.eng.srt' + '"'), shell=True)
            print('')
        nTrack += 1

    nTrack = -1
    # If previous extraction failed, extract english SDH sub, no forced
    for line in outputlines:
        if not os.path.isfile(file.replace(ext, '.eng.srt')) and lineContains(line, 'language:eng', 'subrip/srt', 'forced_track:0', 'track_name:sdh'):
            print('')
            subprocess.call('mkvextract tracks "' + file + '" ' + str(nTrack) + ':"' + file.replace(ext, '.eng.srt' + '"'), shell=True)
            print('')
        nTrack += 1

    nTrack = -1
    # In spite of previous extractions, and if allowed by the config.ini, extract english forced sub
    for line in outputlines:
        if EXTRACT_FORCEDSUBS and not os.path.isfile(file.replace(ext, '.FORCED.eng.srt')) and lineContains(line, 'language:eng', 'subrip/srt', 'forced_track:1'):
            print('')
            subprocess.call('mkvextract tracks "' + file + '" ' + str(nTrack) + ':"' + file.replace(ext, 'FORCED.eng.srt' + '"'), shell=True)
            print('')
        nTrack += 1

    nTrack = -1
    # If previous extractions failed, extract undefined language sub, no forced, allow SDH
    for line in outputlines:
        if not os.path.isfile(file.replace(ext, '.eng.srt')) and lineContains(line, 'language:und', 'subrip/srt', 'forced_track:0'):
            print('')
            subprocess.call('mkvextract tracks "' + file + '" ' + str(nTrack) + ':"' + file.replace(ext, '.UND.eng.srt' + '"'), shell=True)
            print('')
        nTrack += 1


def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find \'config.ini\'')
    # open config.ini for reading
    config = configparser.ConfigParser()
    config.read('config.ini')

    # get values from config file
    HONOR_SUBSBLACKLIST = config['DEFAULT']['HonorSubsBlacklist'] == 'true'
    EXTRACT_FORCEDSUBS = config['DEFAULT']['ExtractForcedSubs'] == 'true'
    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']
    if HONOR_SUBSBLACKLIST: NOSUBS_LIST_PATH = config['Paths']['NoSubsListPath']

    if not os.path.isfile(RECENT_VIDEOFILES_PATH): fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    if HONOR_SUBSBLACKLIST:
        if not os.path.isfile(NOSUBS_LIST_PATH): fatal(NOSUBS_LIST_PATH + ' not found. Make sure to set the config.ini')
        noSubsList = io.open(NOSUBS_LIST_PATH, 'r', encoding='utf_8').read().split('\n')
        while '' in noSubsList: noSubsList.remove('')

    fileList = io.open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8').read().split('\n')
    while '' in fileList: fileList.remove('')

    nFiles = len(fileList)
    nCount = 0

    for file in fileList:
        nCount += 1
        print('Analyzing file ', nCount, ' of ', nFiles, ': ', os.path.basename(file))
        if HONOR_SUBSBLACKLIST and not isPathBlacklisted(file, noSubsList):
            beginExtraction(file, EXTRACT_FORCEDSUBS)
        elif not HONOR_SUBSBLACKLIST:
            beginExtraction(file, EXTRACT_FORCEDSUBS)


if __name__ == '__main__':
    main()
    print('\nDone')
    time.sleep(2)
