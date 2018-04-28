import io
import configparser
import os
import platform
import time

def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


def getCrTime(file):
    if platform.system() == 'Darwin': return os.stat(file).st_birthtime
    return os.path.getctime(file)


def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find "config.ini"')
    # open config.ini for reading
    config = configparser.ConfigParser()
    config.read('config.ini')

    # get values from config file
    TVSHOWS_PATH = config['Paths']['TVShowsPath']
    MOVIES_PATH = config['Paths']['MoviesPath']
    RECENT_VIDEOFILES_PATH = config['Paths']['RecentSubsPath']
    MAX_AGE = float(config['DEFAULT']['MaxAgeForSubs'])

    if not os.path.isdir(TVSHOWS_PATH): fatal(TVSHOWS_PATH + ' not found. Make sure to set the config.ini')
    if not os.path.isdir(MOVIES_PATH): fatal(MOVIES_PATH + ' not found. Make sure to set the config.ini')

    # open file for writing
    print('Getting recent sub files\n')
    wfile = io.open(RECENT_VIDEOFILES_PATH, 'w', encoding='utf_8')

    # recursively walk through tv shows path and find srt files
    currTime = time.time()
    for ROOT, DIRS, FILENAMES in os.walk(TVSHOWS_PATH):
        for filename in FILENAMES:
            if filename.endswith('.srt'):
                file = os.path.join(ROOT, filename)
                crTime = getCrTime(file)
                if ((currTime-crTime)/(60*60*24)) <= MAX_AGE:
                    print('Added ' + os.path.basename(file))
                    wfile.write(file + '\n')


    # recursively walk through movies path and find srt files
    for ROOT, DIRS, FILENAMES in os.walk(MOVIES_PATH):
        for filename in FILENAMES:
            if filename.endswith('.srt'):
                file = os.path.join(ROOT, filename)
                crTime = getCrTime(file)
                if ((currTime-crTime)/(60*60*24)) <= MAX_AGE:
                    print('Added ' + os.path.basename(file))
                    wfile.write(file + '\n')


if __name__ == '__main__':
    main()
    print('\nDone')
    time.sleep(2)
