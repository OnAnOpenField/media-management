import io
import os
import time
import configparser

def fatal(errMsg):
    print('[FATAL] ' + exitMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()

def main():
    if not os.path.isfile('config.ini'):
        fatal('Cannot find \'config.ini\'')
    config = configparser.ConfigParser()
    config.read('config.ini')

    TVSHOWS_PATH = config['Paths']['TVShowsPath']
    MOVIES_PATH = config['Paths']['MoviesPath']
    RECENT_SUBFILES_TXT = config['Paths']['RecentSubsPath']
    MAX_AGE = float(config['DEFAULT']['MaxAgeForSubs'])

    if not os.path.isdir(TVSHOWS_PATH):
        fatal(TVSHOWS_PATH + ' not found. Make sure to set the config.ini')
    if not os.path.isdir(MOVIES_PATH):
        fatal(MOVIES_PATH + ' not found. Make sure to set the config.ini')

    print('Getting recent sub files\n')
    wfile = io.open(RECENT_SUBFILES_TXT, 'w')

    currTime = time.time()
    for root, dirs, files in os.walk(TVSHOWS_PATH):
        for filename in files:
            if filename.endswith('.srt'):
                filefound = os.path.join(root,filename)
                crTime = os.path.getctime(filefound)
                if ((currTime-crTime)/(60*60*24)) <= MAX_AGE:
                    print('Added ' + os.path.basename(filefound))
                    wfile.write(filefound + '\n')

    for root, dirs, files in os.walk(MOVIES_PATH):
        for filename in files:
            if filename.endswith('.srt'):
                filefound = os.path.join(root,filename)
                crTime = os.path.getctime(filefound)
                if ((currTime-crTime)/(60*60*24)) <= MAX_AGE:
                    print('Added ' + os.path.basename(filefound))
                    wfile.write(filefound + '\n')

    print('\nDone')
    time.sleep(2)

if __name__ == '__main__':
    main()