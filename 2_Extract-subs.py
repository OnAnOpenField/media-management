#!/usr/bin/python3

import configparser
import os
import subprocess
import time

sysEOL = '\n' if os.name == 'posix' else '\r\n'

def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


def isPathBlacklisted(FILEPATH, noSubsList):
    for str in noSubsList:
        if str in FILEPATH.lower():
            return True

    return False


def lineContains(line, *tup):
    for str in tup:
        if not str in line:
            return False

    return True


def beginExtraction(file, EXTRACT_FORCEDSUBS):
    filename, ext = os.path.splitext(file)
    bOutput = subprocess.check_output('mkvmerge --identify-verbose "{file}"'.format(file = file), shell=True)
    outputlines = [line.lower() for line in bOutput.decode().split(sysEOL)]

    nTrack = -1
    # Extract english sub, no forced, no SDH
    if not os.path.isfile(file.replace(ext, '.eng.srt')):
        for line in outputlines:
            if lineContains(line, 'language:eng', 'subrip/srt', 'forced_track:0') and not 'sdh' in line and not 'commentary' in line:
                print('')
                subprocess.call('mkvextract tracks "{file}" {nTrack}:"{outputName}"'.format(file = file, nTrack = nTrack, outputName = file.replace(ext, '.eng.srt')), shell=True)
                print('')
                break
            nTrack += 1


    nTrack = -1
    # If previous extraction failed, extract english SDH sub, no forced
    if not os.path.isfile(file.replace(ext, '.eng.srt')):
        for line in outputlines:
            if lineContains(line, 'language:eng', 'subrip/srt', 'forced_track:0', 'sdh') and not 'commentary' in line:
                print('')
                subprocess.call('mkvextract tracks "{file}" {nTrack}:"{outputName}"'.format(file = file, nTrack = nTrack, outputName = file.replace(ext, '.eng.srt')), shell=True)
                print('')
                break
            nTrack += 1


    nTrack = -1
    # In spite of previous extractions, and if allowed by the config.ini, extract english forced sub
    if EXTRACT_FORCEDSUBS and not os.path.isfile(file.replace(ext, '.FORCED.eng.srt')):
        for line in outputlines:
            if lineContains(line, 'language:eng', 'subrip/srt', 'forced_track:1') and not 'commentary' in line:
                print('')
                subprocess.call('mkvextract tracks "{file}" {nTrack}:"{outputName}"'.format(file = file, nTrack = nTrack, outputName = file.replace(ext, '.FORCED.eng.srt')), shell=True)
                print('')
                break
            nTrack += 1


    nTrack = -1
    # If previous extractions failed, extract undefined language sub, no forced, allow SDH
    if not os.path.isfile(file.replace(ext, '.eng.srt')) and not os.path.isfile(file.replace(ext, '.UND.srt')):
        for line in outputlines:
            if lineContains(line, 'language:und', 'subrip/srt', 'forced_track:0'):
                print('')
                subprocess.call('mkvextract tracks "{file}" {nTrack}:"{outputName}"'.format(file = file, nTrack = nTrack, outputName = file.replace(ext, '.UND.srt')), shell=True)
                print('')
                break
            nTrack += 1


def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find "config.ini"')
    # open config.ini for reading
    config = configparser.ConfigParser()
    config.read('config.ini')

    # get values from config file
    HONOR_SUBSBLACKLIST = config['DEFAULT']['HonorSubsBlacklist'] == 'true'
    EXTRACT_FORCEDSUBS = config['DEFAULT']['ExtractForcedSubs'] == 'true'
    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']

    if HONOR_SUBSBLACKLIST:
        NOSUBS_LIST_PATH = config['Paths']['NoSubsListPath']

    if not os.path.isfile(RECENT_VIDEOFILES_PATH):
        fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    if HONOR_SUBSBLACKLIST:
        if not os.path.isfile(NOSUBS_LIST_PATH): fatal(NOSUBS_LIST_PATH + ' not found. Make sure to set the config.ini')
        noSubsList = open(NOSUBS_LIST_PATH, 'r', encoding='utf_8').read().split('\n')
        while '' in noSubsList: noSubsList.remove('')

    fileList = open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8').read().split('\n')
    while '' in fileList: fileList.remove('')

    nFiles = len(fileList)
    nCount = 0

    for file in fileList:
        nCount += 1
        print('Analyzing file ', nCount, ' of ', nFiles, ': ', os.path.basename(file))
        if not os.path.isfile(file):
            print(file + ' does not exist.')
            continue

        if HONOR_SUBSBLACKLIST and isPathBlacklisted(file, noSubsList): continue
        beginExtraction(file, EXTRACT_FORCEDSUBS)


if __name__ == '__main__':
    main()
    print('\nDone')
    time.sleep(2)
