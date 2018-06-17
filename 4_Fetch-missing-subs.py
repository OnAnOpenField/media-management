#!/usr/bin/python3

import configparser
import os
import subprocess
import time

def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


def isPathBlacklisted(FILEPATH, noSubsList):
    for str in noSubsList:
        if str in FILEPATH.lower(): return True
    return False


def fetchSubs(file):
    filename, ext = os.path.splitext(file)

    if not os.path.isfile(file.replace(ext, '.eng.srt')): print('\nFetching subtitles for ' + os.path.basename(file) + '\n')
    if not os.path.isfile(file.replace(ext, '.eng.srt')): subprocess.call('subliminal download -l en "{file}"'.format(file = file), shell=True)
    if os.path.isfile(file.replace(ext, '.en.srt')): os.rename(file.replace(ext, '.en.srt'), file.replace(ext, '.eng.srt'))


def main():
    if not os.path.isfile('config.ini'):
        fatal('Cannot find "config.ini"')

    config = configparser.ConfigParser()
    config.read('config.ini')

    HONOR_SUBSBLACKLIST = config['DEFAULT']['HonorSubsBlacklist'] == 'true'
    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']
    if HONOR_SUBSBLACKLIST:
        NOSUBS_LIST_PATH = config['Paths']['NoSubsListPath']

    if not os.path.isfile(RECENT_VIDEOFILES_PATH):
        fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    if HONOR_SUBSBLACKLIST:
        if not os.path.isfile(NOSUBS_LIST_PATH): fatal(NOSUBS_LIST_PATH + ' not found. Make sure to set the config.ini')
        noSubsList = open(NOSUBS_LIST_PATH, 'r', encoding='utf_8').read().split('\n')
        while '' in noSubsList: noSubsList.remove('')


    nCount = 0
    fileList = open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8').read().split('\n')
    while '' in fileList: fileList.remove('')

    for file in fileList:
        nCount += 1
        if HONOR_SUBSBLACKLIST and not isPathBlacklisted(file, noSubsList):
            fetchSubs(file)
        elif not HONOR_SUBSBLACKLIST:
            fetchSubs(file)


if __name__ == '__main__':
    main()
    print('\nDone')
    time.sleep(2)
