#!/usr/bin/python3

import configparser
import json
import os
import subprocess
import sys
import time

# list of languages to keep in mkv. any others are considered foreign
ALLOWED_LANGUAGES = ['eng', 'spa', 'und']
EXCLUDED_TRACK_NAMES = ['commentary', 'cast']

def main():
    if not os.path.isfile('config.ini'):
        fatal('Cannot find "config.ini"')

    config = configparser.ConfigParser()
    config.read('config.ini')
    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']
    
    if not os.path.isfile(RECENT_VIDEOFILES_PATH):
        fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    if len(sys.argv) < 2:
        with open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8') as pathsFile:
            videoList = [l for l in (line.strip() for line in pathsFile) if l and l.endswith('.mkv')]
    else:
        videoList = [arg for arg in sys.argv[1:] if arg.endswith('.mkv')]

    nFiles = len(videoList)

    for i, videoPath in enumerate(videoList):
        print('Analyzing file {0} of {1}: {2}'.format(i + 1, nFiles, os.path.basename(videoPath)))
        if not os.path.isfile(videoPath):
            print(videoPath + ' does not exist.')
            continue
        processMKV(videoPath)
            

    print('\nDone')
    time.sleep(2)


def processMKV(videoPath):
    videoData = getVideoData(videoPath)

    hasSubs = isVideoSubtitled(videoData['tracks'])
    properAudioTracks, numberOfAudioTracks = getAudioTracks(videoData['tracks'])

    param = ''

    if len(properAudioTracks) < numberOfAudioTracks:
        param += ' -a ' + ','.join(properAudioTracks)
    if hasSubs:
        param += ' -S '

    print('"' + param + '"')

    if param:
        filename, ext = os.path.splitext(videoPath)
        TEMPFILE = filename + '.TEMP.mkv'
        
        print('Deleting embedded subs and/or unwanted audio from {0}\n'.format(os.path.basename(videoPath)))
        subprocess.call('mkvmerge -o "{outputFile}" {param} "{inputFile}"'.format(outputFile=TEMPFILE, param=param, inputFile=videoPath), shell=True)
        os.remove(videoPath)

        for i in range(5):
            try:
                os.rename(TEMPFILE, videoPath)
                break
            except Exception as e:
                time.sleep(0.3)
                pass

        print('')


def getVideoData(videoPath):
    rawOutput = subprocess.check_output('mkvmerge -J "{0}"'.format(videoPath), shell=True)
    output = rawOutput.decode()
    videoData = json.loads(output)

    return videoData


def getAudioTracks(tracks):
    properAudioTracks = []
    num = 0

    for track in tracks:
        if track['type'] == 'audio':
            num += 1
        for lang in ALLOWED_LANGUAGES:
            if track['properties']['language'] == lang and track['type'] == 'audio' and not isTrackNameDirty(track['properties'].get('track_name', '')):
                properAudioTracks.append(str(track['id']))

    return properAudioTracks, num


def isVideoSubtitled(tracks):
    for track in tracks:
        if track['type'] == 'subtitles':
            return True

    return False


def isTrackNameDirty(trackName):
    for excludedTrackName in EXCLUDED_TRACK_NAMES:
        if excludedTrackName in trackName.lower():
            return True

    return False



def processMKV2(file):
    bOutput = subprocess.check_output('mkvmerge --identify-verbose "{0}"'.format(file), shell=True)
    outputlines = [line.lower() for line in bOutput.decode().split(sysEOL)]

    hasWantedAud = False
    hasUnwantedAud = False
    hasSubs = False
    param = ''
    nTrack = -1

    for line in outputlines:
        m = AUDIO_RE.match(line)
        if m and not 'language:eng' in line and not 'language:und' in line or 'commentary' in line:
            hasUnwantedAud = True
        if 'subtitles' in line:
            hasSubs = True

    if hasUnwantedAud:
        for line in outputlines:
            m = AUDIO_RE.match(line)
            if m and 'language:eng' in line and not 'commentary' in line:
                hasWantedAud = True
                break
            nTrack += 1


    if hasUnwantedAud and hasWantedAud:
        param += ' -a ' + str(nTrack)
    if hasSubs:
        param += ' -S'

    if param:
        TEMPFILE = file.replace('.mkv', '.TEMP.mkv')
        print('Deleting embedded subs and/or unwanted audio from ' + os.path.basename(file) + '\n')
        subprocess.call('mkvmerge -o "{outputFile}" {param} "{inputFile}"'.format(outputFile=TEMPFILE, param=param, inputFile=file), shell=True)

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


def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


if __name__ == '__main__':
    main()
