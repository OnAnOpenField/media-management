#!/usr/bin/python3

import configparser
import re
import os
import subprocess
import time

sysEOL = '\n' if os.name == 'posix' else '\r\n'
AUDIO_REG = re.compile(r'track id \d+: audio')

def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


def processMKV(file):
    bOutput = subprocess.check_output('mkvmerge --identify-verbose "{file}"'.format(file = file), shell=True)
    outputlines = [line.lower() for line in bOutput.decode().split(sysEOL)]

    hasWantedAud = False
    hasUnwantedAud = False
    hasSubs = False
    param = ''
    nTrack = -1

    for line in outputlines:
        m = AUDIO_REG.match(line)
        if m and not 'language:eng' in line and not 'language:und' in line or 'commentary' in line:
            hasUnwantedAud = True
        if 'subtitles' in line:
            hasSubs = True

    if hasUnwantedAud:
        for line in outputlines:
            m = AUDIO_REG.match(line)
            if m and 'language:eng' in line and not 'commentary' in line:
                hasWantedAud = True
                break
            nTrack += 1

    if hasUnwantedAud and hasWantedAud: param += ' -a ' + str(nTrack)
    if hasSubs: param += ' -S'

    if param:
        TEMPFILE = file.replace('.mkv', '.TEMP.mkv')
        print('Deleting embedded subs and/or unwnated audio from ' + os.path.basename(file) + '\n')
        subprocess.call('mkvmerge -o "{outputFile}" {param} "{inputFile}"'.format(outputFile = TEMPFILE, param = param, inputFile = file), shell=True)

        # allow time for previous process to properly close
        time.sleep(0.5)
        os.remove(file)
        # allow time for OS to remove file
        time.sleep(0.5)

        try:
            os.rename(TEMPFILE, file)
        except Exception as ex:
            print(' >> ', ex)
            pass

        print('')


def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find "config.ini"')
    config = configparser.ConfigParser()
    config.read('config.ini')

    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']
    if not os.path.isfile(RECENT_VIDEOFILES_PATH): fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    fileList = open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8').read().split('\n')
    while '' in fileList: fileList.remove('')

    nFiles = len(fileList)
    nCount = 0

    for file in fileList:
        nCount += 1
        if file.endswith('.mkv'):
            print('Analyzing file {nCount} of {nFiles}: {filename}'.format(nCount = nCount, nFiles = nFiles, filename = os.path.basename(file)))
            if not os.path.isfile(file):
                print(file + ' does not exist.')
                continue
            processMKV(file)
            

    print('\nDone')
    time.sleep(2)

if __name__ == '__main__':
    main()
