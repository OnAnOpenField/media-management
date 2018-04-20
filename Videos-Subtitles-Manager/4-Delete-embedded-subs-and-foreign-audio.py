import io
import re
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

def processMKV(FILE):
    bOutput = subprocess.check_output('mkvmerge --identify-verbose "' + FILE + '"', shell=True)
    output = bOutput.decode()
    outputlines = output.split(sysEOL)

    nTrack = -1
    AUDIO_REG = re.compile(r'track id [0-9]+: audio', re.IGNORECASE)
    hasUnwantedAud = False
    hasWantedAud = False
    hasSubs = False
    param = ''

    for line in outputlines:
        m = AUDIO_REG.match(line)
        if m and not lineContains(line, 'language:und', 'language:eng') or lineContains(line, 'commentary'):
            hasUnwantedAud = True
        if lineContains(line, 'subtitles'):
            hasSubs = True

    if hasUnwantedAud:
        for line in outputlines:
            m = AUDIO_REG.match(line)
            if m and lineContains(line, 'language:eng') and not lineContains(line, 'commentary'):
                hasWantedAud = True
                break
            nTrack += 1

    if hasUnwantedAud and hasWantedAud: param += ' -a ' + str(nTrack)
    if hasSubs: param += ' -S'

    if param:
        TEMPFILE = FILE.replace('.mkv', '.TEMP.mkv')
        print('\nDeleting embedded subs and/or unwnated audio from ' + os.path.basename(FILE) + '\n')
        subprocess.call('mkvmerge -o "' + TEMPFILE + '" ' + param + ' "' + FILE + '"', shell=True)
        os.remove(FILE)
        os.rename(TEMPFILE, FILE)

def lineContains(line, *tup):
    for str in tup:
        if not str in line.lower(): return False
    return True

def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find \'config.ini\'')
    config = configparser.ConfigParser()
    config.read('config.ini')

    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']
    if not os.path.isfile(RECENT_VIDEOFILES_PATH): fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    fileList = io.open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8_sig').read().split('\n')
    while '' in fileList: fileList.remove('')

    nFiles = len(fileList)
    nCount = 0

    for file in fileList:
        nCount += 1
        if file.endswith('.mkv'):
            print('Analyzing file ', nCount, ' of ', nFiles, ': ', os.path.basename(file))
            processMKV(file)


if __name__ == '__main__':
    main()