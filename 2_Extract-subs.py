#!/usr/bin/python3

import configparser
import json
import os
import re
import subprocess
import time
import sys

# temporary EXTRACT_FORCEDSUBS value. Actual value gathered from config.ini
EXTRACT_FORCEDSUBS = True

# language identifiers for filename when checking if a subtitle companion exists for a video: eg. 'video_name.mkv' --> 'video_name.eng.srt'
ALLOWED_LANGUAGES = ['eng', 'und']

# subtitle extension identifiers for filename when checking if a subtitle companion exists for a video: eg. 'video_name.eng.srt'
# types of subtitles to search for in mkv containers and their corresponding file extension
# ordered from most preferred to least preferred
ALLOWED_SUBS = {
    'SubRip/SRT': 'srt', 
    'SubStationAlpha': 'ass'
}

def main():
    if not os.path.isfile('config.ini'):
        fatal('Cannot find "config.ini"')
        
    # open config.ini for reading
    config = configparser.ConfigParser()
    config.read('config.ini')

    # get values from config file
    global EXTRACT_FORCEDSUBS
    EXTRACT_FORCEDSUBS = config['DEFAULT']['ExtractForcedSubs'] == 'true'
    HONOR_SUBSBLACKLIST = config['DEFAULT']['HonorSubsBlacklist'] == 'true'
    RECENT_MEDIAFILES_PATH = config['Paths']['RecentMediaFilesPath']
    if HONOR_SUBSBLACKLIST: NOSUBS_LIST_PATH = config['Paths']['NoSubsListPath']

    if not os.path.isfile(RECENT_MEDIAFILES_PATH):
        fatal(RECENT_MEDIAFILES_PATH + ' not found. Make sure to set the config.ini')

    if HONOR_SUBSBLACKLIST:
        if not os.path.isfile(NOSUBS_LIST_PATH):
            fatal(NOSUBS_LIST_PATH + ' not found. Make sure to set the config.ini')
        with open(NOSUBS_LIST_PATH, 'r', encoding='utf_8') as f:
            noSubsList = json.load(f)
    else:
        noSubsList = []

    if len(sys.argv) < 2:
        with open(RECENT_MEDIAFILES_PATH, 'r', encoding='utf_8') as f:
            recentFiles = json.load(f)
        videoList = recentFiles['videos']
    else:
        videoList = [arg for arg in sys.argv[1:] if arg.endswith('.mkv')]

    print('Extracting subtitles')
    nFiles = len(videoList)

    for i, videoPath in enumerate(videoList):
        print('Analyzing MKV file {0} of {1}: {2}'.format(i + 1, nFiles, os.path.basename(videoPath)))
        if not os.path.isfile(videoPath):
            print(videoPath + ' does not exist.')
            continue
        if isPathBlacklisted(videoPath, noSubsList):
            continue
        processVideo(videoPath)

    print('\nDone')


def processVideo(videoPath):
    videoData = getVideoData(videoPath)

    # Extract english sub, no forced, no SDH
    if not hasAccompanyingSubtitle(videoPath): 
        extractSub(videoPath, videoData, wantedLang='eng', excludedTrackNames=['commentary', 'no.*english', 'forced', 'foreign', r'\bSDH\b', 'hard.*hearing', 'impaired'])

    # # If previous extraction failed, extract english SDH sub, no forced
    if not hasAccompanyingSubtitle(videoPath):
        extractSub(videoPath, videoData, wantedLang='eng', excludedTrackNames=['commentary', 'no.*english', 'forced', 'foreign'])

    # # In spite of previous extractions, and if allowed by the config.ini, extract english forced sub
    if EXTRACT_FORCEDSUBS and not hasAccompanyingSubtitle(videoPath, extraIdentifier='.forced'):
        extractSub(videoPath, videoData, wantedLang='eng', extraIdentifier='forced', allowForced=True)
        # if forcedSubsMatchRegularSubs():
        #     delete *.FORCED.eng.<ext>

    # # If previous extractions failed, extract undefined language sub, no forced, allow SDH
    if not hasAccompanyingSubtitle(videoPath):
        extractSub(videoPath, videoData, wantedLang='und', excludedTrackNames=['commentary', 'forced'])


def hasAccompanyingSubtitle(videoPath, extraIdentifier=''):
    if extraIdentifier: extraIdentifier = '.' + extraIdentifier

    dirname = os.path.dirname(videoPath)
    # basename == '$filename.$ext'
    basename = os.path.basename(videoPath)
    # filename == '$filename' # no extension
    filename, ext = os.path.splitext(basename)

    for codec in ALLOWED_SUBS:
        for lang in ALLOWED_LANGUAGES:
            subtitleName = '{0}{1}{2}{3}'.format(filename, '.' + lang, extraIdentifier, '.' + ALLOWED_SUBS[codec])
            if os.path.isfile(os.path.join(dirname, subtitleName)):
                return True

    return False


def extractSub(videoPath, videoData, wantedLang='eng', extraIdentifier='', allowForced=False, excludedTrackNames=[]):
    if extraIdentifier: extraIdentifier = '.' + extraIdentifier
    
    filename, ext = os.path.splitext(videoPath)

    for wantedCodec in ALLOWED_SUBS:
        for track in videoData['tracks']:
            if isWantedTrack(track, wantedLang, wantedCodec, allowForced, excludedTrackNames):
                subExt = ALLOWED_SUBS[track['codec']]
                print('')
                subprocess.call('mkvextract tracks "{0}" {1}:"{2}"'.format(videoPath, track['id'], filename + '.' + wantedLang + extraIdentifier + '.' + subExt), shell=True)
                print('')
                return


def isWantedTrack(track, wantedLang, wantedCodec, allowForced, excludedTrackNames):
    if track['properties']['language'] != wantedLang or track['codec'] != wantedCodec or track['properties']['forced_track'] != allowForced:
        return False

    trackName = track['properties'].get('track_name', '')
    for excludedTrackName in excludedTrackNames:
        exclude_re = re.compile(excludedTrackName, re.IGNORECASE)
        if exclude_re.search(trackName):
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
    time.sleep(2)
    