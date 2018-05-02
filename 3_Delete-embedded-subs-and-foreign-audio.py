import configparser
import io
import re
import os
import subprocess
import time

sysEOL = '\n' if os.name == 'posix' else '\r\n'

def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


def processMKV(file):
    bOutput = subprocess.check_output('mkvmerge --identify-verbose "{file}"'.format(file = file), shell=True)
    output = bOutput.decode()
    outputlines = output.split(sysEOL)

    AUDIO_REG = re.compile(r'track id [0-9]+: audio', re.IGNORECASE)
    hasWantedAud = False
    hasUnwantedAud = False
    hasSubs = False
    param = ''
    nTrack = -1

    for line in outputlines:
        m = AUDIO_REG.match(line)
        if m and not 'language:eng' in line.lower() and not 'language:und' in line.lower() or 'commentary' in line.lower():
            hasUnwantedAud = True
        if 'subtitles' in line.lower():
            hasSubs = True

    if hasUnwantedAud:
        for line in outputlines:
            m = AUDIO_REG.match(line)
            if m and 'language:eng' in line.lower() and not 'commentary' in line.lower():
                hasWantedAud = True
                break
            nTrack += 1

    if hasUnwantedAud and hasWantedAud: param += ' -a ' + str(nTrack)
    if hasSubs: param += ' -S'

    if param:
        TEMPFILE = file.replace('.mkv', '.TEMP.mkv')
        print('\nDeleting embedded subs and/or unwnated audio from ' + os.path.basename(file) + '\n')
        subprocess.call('mkvmerge -o "{outputFile}" {param} "{inputFile}"'.format(outputFile = TEMPFILE, param = param, inputFile = file), shell=True)
        os.remove(file)
        os.rename(TEMPFILE, file)


def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find "config.ini"')
    config = configparser.ConfigParser()
    config.read('config.ini')

    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']
    if not os.path.isfile(RECENT_VIDEOFILES_PATH): fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    fileList = io.open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8').read().split('\n')
    while '' in fileList: fileList.remove('')

    nFiles = len(fileList)
    nCount = 0

    for file in fileList:
        nCount += 1
        if file.endswith('.mkv'):
            print('Analyzing file ', nCount, ' of ', nFiles, ': ', os.path.basename(file))
            if not os.path.isfile(file):
                print(file + ' does not exist.')
                continue
            processMKV(file)


if __name__ == '__main__':
    main()
    print('\nDone')
    time.sleep(2)
