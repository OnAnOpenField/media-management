import io
import subprocess
import os
import time
import configparser

def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()

def isPathBlacklisted(FILEPATH, noSubsList):
    for str in noSubsList:
        if str in FILEPATH.lower(): return True
    return False

def fetchSubs(FILE):
    filename, EXT = os.path.splitext(FILE)

    if not os.path.isfile(FILE.replace(EXT, '.eng.srt')): print('\nFetching subtitles for ' + os.path.basename(FILE) + '\n')
    if not os.path.isfile(FILE.replace(EXT, '.eng.srt')): subprocess.call('filebot -get-subtitles "' + FILE + '"', shell=True)
    if not os.path.isfile(FILE.replace(EXT, '.eng.srt')): subprocess.call('subliminal download -l en "' + FILE + '"', shell=True)
    if os.path.isfile(FILE.replace(EXT, '.en.srt')): os.rename(FILE.replace(EXT, '.en.srt'), FILE.replace(EXT, '.eng.srt'))

def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find \'config.ini\'')
    config = configparser.ConfigParser()
    config.read('config.ini')

    honorSubsBlacklist = config['DEFAULT']['HonorSubsBlacklist'] == 'true'
    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']
    if honorSubsBlacklist: NOSUBS_LIST_PATH = config['Paths']['NoSubsListPath']

    if not os.path.isfile(RECENT_VIDEOFILES_PATH): fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    if honorSubsBlacklist:
        if not os.path.isfile(NOSUBS_LIST_PATH): fatal(NOSUBS_LIST_PATH + ' not found. Make sure to set the config.ini')
        noSubsList = io.open(NOSUBS_LIST_PATH, 'r', encoding='utf_8_sig').read().split('\n')
        while '' in noSubsList: noSubsList.remove('')

    nCount = 0
    fileList = io.open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8_sig').read().split('\n')
    while '' in fileList: fileList.remove('')

    for file in fileList:
        nCount += 1
        if honorSubsBlacklist and not isPathBlacklisted(file, noSubsList):
            fetchSubs(file)
        elif not honorSubsBlacklist:
            fetchSubs(file)

if __name__ == '__main__':
    main()
    print('\nDone')
    time.sleep(2)
