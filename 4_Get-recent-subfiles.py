#!/usr/bin/python3

import configparser
import json
import os
import platform
import time

def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find "config.ini"')
    # open config.ini for reading
    config = configparser.ConfigParser()
    config.read('config.ini')

    # get values from config file
    TVSHOWS_PATH = config['Paths']['TVShowsPath']
    MOVIES_PATH = config['Paths']['MoviesPath']
    RECENT_MEDIAFILES_PATH = config['Paths']['RecentMediaFilesPath']
    MAX_AGE = float(config['DEFAULT']['MaxAgeForSubs'])

    if not os.path.isdir(TVSHOWS_PATH): fatal(TVSHOWS_PATH + ' not found. Make sure to set the config.ini')
    if not os.path.isdir(MOVIES_PATH): fatal(MOVIES_PATH + ' not found. Make sure to set the config.ini')

    # open file for writing
    print('Getting recent sub files\n')
    with open(RECENT_MEDIAFILES_PATH, 'r', encoding='utf_8') as f:
        recentFiles = json.load(f)

    recentFiles['subtitles'] = []
    currTime = time.time()

    # recursively walk through tv shows and movies paths and find srt files
    for path in [TVSHOWS_PATH, MOVIES_PATH]:
        for ROOT, DIRS, FILENAMES in os.walk(path):
            for filename in FILENAMES:
                if filename.endswith('.srt'):
                    file = os.path.join(ROOT, filename)
                    crTime = getCrTime(file)
                    if ((currTime-crTime)/(60*60*24)) <= MAX_AGE:
                        print('Added ' + os.path.basename(file))
                        recentFiles['subtitles'].append(file)

    with open(RECENT_MEDIAFILES_PATH, 'w', encoding='utf_8') as f:
        json.dump(recentFiles, f, indent=4)                            

    print('\nDone')
    

def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


def getCrTime(file):
    if platform.system() == 'Darwin': return os.stat(file).st_birthtime
    return os.path.getctime(file)


if __name__ == '__main__':
    main()
    time.sleep(2)
    