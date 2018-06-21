#!/usr/bin/python3

import configparser
import json
import os
import re
import subprocess
import time
import sys

# Temporary EXTRACT_FORCEDSUBS value. Actual value gathered from config.ini
EXTRACT_FORCEDSUBS = True

# language identifiers for filename when checking if a subtitle companion exists for a video: eg. 'video_name.eng.srt'
ALLOWED_LANGUAGES = ['eng', 'und']

# types of subtitles to search for in mkv containers and their corresponding file extension
ALLOWED_SUBS = {
    'SubRip/SRT': 'srt', 
    'SubStationAlpha': 'ass'
}

def main():
    if not os.path.isfile('config.ini'): fatal('Cannot find "config.ini"')
    # open config.ini for reading
    config = configparser.ConfigParser()
    config.read('config.ini')

    # get values from config file
    global EXTRACT_FORCEDSUBS
    EXTRACT_FORCEDSUBS = config['DEFAULT']['ExtractForcedSubs'] == 'true'
    HONOR_SUBSBLACKLIST = config['DEFAULT']['HonorSubsBlacklist'] == 'true'
    RECENT_VIDEOFILES_PATH = config['Paths']['RecentVideosPath']
    if HONOR_SUBSBLACKLIST: NOSUBS_LIST_PATH = config['Paths']['NoSubsListPath']

    if not os.path.isfile(RECENT_VIDEOFILES_PATH):
        fatal(RECENT_VIDEOFILES_PATH + ' not found. Make sure to set the config.ini')

    if HONOR_SUBSBLACKLIST:
        if not os.path.isfile(NOSUBS_LIST_PATH):
            fatal(NOSUBS_LIST_PATH + ' not found. Make sure to set the config.ini')
        with open(NOSUBS_LIST_PATH, 'r', encoding='utf_8') as noSubsPaths:
            noSubsList = [l for l in (line.strip() for line in noSubsPaths) if l]
    else:
        noSubsList = []


    if len(sys.argv) < 2:
        with open(RECENT_VIDEOFILES_PATH, 'r', encoding='utf_8') as pathsFile:
            videoList = [l for l in (line.strip() for line in pathsFile) if l and l.endswith('.mkv')]
    else:
        videoList = [arg for arg in sys.argv[1:] if arg.endswith('.mkv')]


    nFiles = len(videoList)

    for i, videoPath in enumerate(videoList):
        print('Analyzing mkv file {0} of {1}: {2}'.format(i + 1, nFiles, os.path.basename(videoPath)))
        if not os.path.isfile(videoPath):
            print(videoPath + ' does not exist.')
            continue
        if isPathBlacklisted(videoPath, noSubsList):
            continue
        processVideo(videoPath)

    print('\nDone')
    time.sleep(2)


def processVideo(videoPath):
    videoData = getVideoData(videoPath)

    # Extract english sub, no forced, no SDH
    if not hasAccompanyingSubtitle(videoPath): 
        extractSub(videoPath, videoData, wantedLang='eng', excludedTrackNames=['commentary', 'no.*english', 'forced', 'foreign', r'\bSDH\b', '(deaf)?hard.*hearing', '(hearing)?.*impaired'])

    # # If previous extraction failed, extract english SDH sub, no forced
    if not hasAccompanyingSubtitle(videoPath):
        extractSub(videoPath, videoData, wantedLang='eng', excludedTrackNames=['commentary', 'no.*english', 'forced', 'foreign'])

    # # In spite of previous extractions, and if allowed by the config.ini, extract english forced sub
    if EXTRACT_FORCEDSUBS and not hasAccompanyingSubtitle(videoPath, extraIdentifier='.forced'):
        extractSub(videoPath, videoData, wantedLang='eng', extraIdentifier='.forced', allowForced=True)
        # if forcedSubsMatchRegularSubs():
        #     delete *.FORCED.eng.<ext>

    # # If previous extractions failed, extract undefined language sub, no forced, allow SDH
    if not hasAccompanyingSubtitle(videoPath):
        extractSub(videoPath, videoData, wantedLang='und', allowForced=False, excludedTrackNames=['commentary', 'forced'])


def hasAccompanyingSubtitle(videoPath, extraIdentifier=''):
    dirname = os.path.dirname(videoPath)
    # basename == '$filename.$ext'
    basename = os.path.basename(videoPath)
    # filename == '$filename' # no extension
    filename, ext = os.path.splitext(basename)

    for codec in ALLOWED_SUBS:
        for lang in ALLOWED_LANGUAGES:
            subtitleName = '{0}{1}{2}{3}'.format(filename, extraIdentifier, '.' + lang, '.' + ALLOWED_SUBS[codec])
            if os.path.isfile(os.path.join(dirname, subtitleName)):
                return True

    return False


def extractSub(videoPath, videoData, wantedLang='eng', extraIdentifier='', allowForced=False, excludedTrackNames=[]):
    filename, ext = os.path.splitext(videoPath)

    for track in videoData['tracks']:
        if isWantedTrack(track, wantedLang, allowForced, excludedTrackNames):
            subExt = ALLOWED_SUBS[track['codec']]
            subprocess.call('mkvextract tracks "{0}" {1}:"{2}"'.format(videoPath, track['id'], filename + extraIdentifier+ '.' + wantedLang + '.' + subExt), shell=True)
            print('')
            break


def isWantedTrack(track, wantedLang, allowForced, excludedTrackNames):
    if track['properties']['language'] == wantedLang and track['properties']['forced_track'] == allowForced:
        if not track['codec'] in ALLOWED_SUBS:
            return False
        trackName = track['properties'].get('track_name', '')
        for excludedTrackName in excludedTrackNames:
            exclude_re = re.compile(excludedTrackName, re.IGNORECASE)
            if exclude_re.search(trackName):
                return False
    else:
        return False

    return True
                        

def getVideoData(videoPath):
    rawOutput = subprocess.check_output('mkvmerge -J "{0}"'.format(videoPath), shell=True)
    output = rawOutput.decode()
    videoData = json.loads(output)

    return videoData


def isPathBlacklisted(videoPath, noSubsList):
    for str in noSubsList:
        if str in videoPath.lower():
            return True

    return False


def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    time.sleep(2)
    exit()


if __name__ == '__main__':
    main()
