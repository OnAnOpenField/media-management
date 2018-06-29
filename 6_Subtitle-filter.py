#!/usr/bin/python3

import chardet
import configparser
import os
import re
import time
import sys

FONT_TAG_RE = re.compile(r'(< *font.+?>).+?(< */? *font *>)', re.IGNORECASE)
TEXT_FOR_HI_RE = re.compile(r'(\[|\(|\{).*?(\]|\)|\})')
TIMESTAMP_RE = re.compile(r'[ ]*\d{1,2}:\d{1,2}:\d{1,2},\d{1,3} *-+> *\d{1,2}:\d{1,2}:\d{1,2},\d{1,3}[ ]*$')
NON_SPOKEN_WORD_RE = re.compile(r'< *(?:i|b|strong) *>[\W_]*?< */? *(?:i|b|strong) *>|[\W_]')
EPISODE_BASENAME_RE = re.compile(r'(.+) - S(\d\d)E(\d\d) - (.+)\.\w+')
MOVIE_BASENAME_RE = re.compile(r'(.+) \((\d\d\d\d)\)\.\w+')

ENTITIES_DICT = {
    ' ': ['&nbsp;', '&#160;'],
    '<': ['&lt;', '&#60;'],
    '>': ['&gt;', '&#62;'],
    '&': ['&amp;', '&#38;'],
    '"': ['&quot;', '&#34;'],
    '\'': ['&apos;', '&#39;']
}
# '’
# \w[ ]+\W

def main():
    # .test. line
    # CONFIG_PATH = 'E:\\Videos\\_Scripts\\config.ini'
    CONFIG_PATH = 'config.ini'
    if not os.path.isfile(CONFIG_PATH):
        fatal('Cannot find "config.ini"')

    # open config.ini for reading
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    # Get paths from config.ini
    SUBFILTER_LOG_PATH = config['Paths']['LogFilePath']
    CREDITS_LIST_PATH = config['Paths']['SubCreditsListPath']
    RECENT_SUBS_PATH = config['Paths']['RecentSubsPath']

    # Check if files are readable
    if not os.access(SUBFILTER_LOG_PATH, os.R_OK): fatal(SUBFILTER_LOG_PATH + ' could not be opened for reading')
    if not os.access(CREDITS_LIST_PATH, os.R_OK): fatal(CREDITS_LIST_PATH + ' could not be opened for reading')
    if not os.access(RECENT_SUBS_PATH, os.R_OK): fatal(RECENT_SUBS_PATH + ' could not be opened for reading')

    logFile = open(SUBFILTER_LOG_PATH, 'w', encoding='utf_8')

    filesFiltered = 0
    totalFiles = 0
    CREDITS_LIST = []
    SUBFILES_LIST = []

    with open(CREDITS_LIST_PATH, 'r', encoding='utf_8') as f:
        CREDITS_LIST = [l for l in (line.strip() for line in f) if l]

    if len(sys.argv) < 2:
        with open(RECENT_SUBS_PATH, 'r', encoding='utf_8') as f:
            SUBFILES_LIST = [l for l in (line.strip() for line in f) if l]
    else:
        SUBFILES_LIST = sys.argv[1:]

    totalFiles = len(SUBFILES_LIST)

    for i, subFilePath in enumerate(SUBFILES_LIST):
        tempList = getIdentifyingVideoExp(subFilePath)
        print('Processing file {0} of {1}: {2}'.format(i + 1, totalFiles, os.path.basename(subFilePath)))
        filesFiltered += processSubtitles(subFilePath, CREDITS_LIST + tempList, logFile)

    print('\n{0} of {1} files were filtered'.format(filesFiltered, totalFiles))
    print('SubFilter.log updated')

    time.sleep(2)


def processSubtitles(subFilePath, CREDITS_LIST, logFile):
    subfileContents = []
    subblock = []
    subblockList = []
    CREDITS_RE = re.compile('|'.join(CREDITS_LIST))

    # Check if subtitle file is readable
    if not subFilePath.endswith('.srt') or not os.access(subFilePath, os.R_OK):
        print('"{}" could not be opened for reading'.format(subFilePath))
        return 0

    # Read from subtitle file
    encoding = getEncoding(subFilePath)
    # .test. line
    # encoding = 'iso8859_1'

    try:
        with open(subFilePath, 'r', encoding=encoding) as subFile:
            subfileContents = [l for l in (line.strip() for line in subFile) if l]
    except UnicodeDecodeError as e:
        subFile.close()
        print(' <> UnicodeDecodeError, {0}, {1}: {2}'.format(os.path.basename(subFilePath), encoding, e))
        logFile.write(' <> UnicodeDecodeError, {0}, {1}: {2}'.format(os.path.basename(subFilePath), encoding, e))
        return 0

    subFile.close()
    organizeSubtitles(subfileContents, subblockList)
    subFileisDirty = isSubFileDirty(CREDITS_RE, subblockList)

    if not subFileisDirty:
        return 0

    # Open subtitle file for writing
    # .test. line.
    # subFile = open(subFilePath + '.TEST.srt', 'w', encoding=encoding)
    subFile = open(subFilePath, 'w', encoding=encoding)

    print(' - Filtering subtitle: {0}\n'.format(subFilePath))
    logFile.write(' - Filtering subtitle: {0}\n\n'.format(subFilePath))

    newSubblockList = []
    filterSubtitles(subblockList, newSubblockList, CREDITS_RE, logFile)

    wLineNum = 1
    # Write clean subs back to subtitle file
    for subblock in newSubblockList:
        if len(subblock) == 1:
            continue
        subFile.write(str(wLineNum) + '\n')
        for line in subblock:
            subFile.write(line + '\n')

        subFile.write('\n')
        wLineNum += 1

    subFile.close()

    return 1


def organizeSubtitles(subfileContents, subblockList):
    subblock = []
    for i, line in enumerate(subfileContents[:-1]):
        isLineNum = isTimeStamp(subfileContents[i + 1])
        # If not at end of subblock
        if not isLineNum:
            subblock.append(subfileContents[i])

        # If at end of subblock or file
        if subblock and isLineNum or i + 2 == len(subfileContents):
            if i + 2 == len(subfileContents):
                subblock.append(subfileContents[i + 1])

            subblockList.append(subblock)
            subblock = []


def filterSubtitles(subblockList, newSubblockList, CREDITS_RE, logFile):
    for lineNum, subblock in enumerate(subblockList):
        tempBlock = []

        # check for credits
        if isSubblockDirty(subblock, CREDITS_RE, regex=True):
            logFile.write('\t>> Removed line {0}:\n'.format(str(lineNum + 1)))
            logFile.write('\t\t' + '\n\t\t'.join(subblock) + '\n\n')
            continue

        # check for font tags
        if isSubblockDirty(subblock, FONT_TAG_RE, regex=True):
            logFile.write('\t>> Stripped font tags from line {0}:\n'.format(str(lineNum + 1)))
            logFile.write('\t\t' + '\n\t\t'.join(subblock) + '\n')
            removeFontTags(subblock)
            logFile.write('\t\t\t-->\n\t\t' + '\n\t\t'.join(subblock) + '\n\n')

        # check for HI/SDH text
        if isSubblockDirty(subblock, TEXT_FOR_HI_RE, regex=True):
            logFile.write('\t>> Removed Text-For-HI from line {0}:\n'.format(str(lineNum + 1)))
            logFile.write('\t\t' + '\n\t\t'.join(subblock) + '\n')
            removeTextForHI(subblock)
            logFile.write('\t\t\t-->\n\t\t' + '\n\t\t'.join(subblock) + '\n\n')

        # check for HTML entities
        if isSubblockDirty(subblock, *ENTITIES_DICT, dict=True):
            logFile.write('\t>> Fixed entities in line {0}:\n'.format(str(lineNum + 1)))
            logFile.write('\t\t' + '\n\t\t'.join(subblock) + '\n')
            fixEntities(subblock)
            logFile.write('\t\t\t-->\n\t\t' + '\n\t\t'.join(subblock) + '\n\n')

        # check for non-spoken lines
        for line in subblock:
            if isNonSpokenLine(line):
                if line:
                    logFile.write('\t>> Removed Non-Spoken text from line {0}:\n'.format(str(lineNum + 1)))
                    logFile.write('\t\t"' + line + '"\n\n')
                continue
            tempBlock.append(line.strip())

        fixExtraSpaces(tempBlock)
        subblock = tempBlock
        newSubblockList.append(subblock)


def isSubFileDirty(CREDITS_RE, subblockList):
    for subblock in subblockList:
        text = ''

        for line in subblock:
            text += line.lower() + ' '
            if isNonSpokenLine(line):
                return True

        # Check for credits
        if re.search(CREDITS_RE, text):
            return True

        # Check for font tags
        m = FONT_TAG_RE.search(text)
        if m:
            return True

        # Check for HI/SDH text
        if re.search(TEXT_FOR_HI_RE, text):
            return True

        # Check for entities
        for key in ENTITIES_DICT:
            for entity in ENTITIES_DICT[key]:
                if entity in text:
                    return True

    return False


def isSubblockDirty(subblock, *args, regex=False, dict=False):
    text = ''
    for line in subblock:
        text += line.lower() + ' '

    for arg in args:
        if regex:
            m = arg.search(text)
            if m:
                return True
        elif dict:
            for value in ENTITIES_DICT[arg]:
                if value in text:
                    return True
        elif arg in text:
            return True

    return False


def isNonSpokenLine(line):
    matches = re.finditer(NON_SPOKEN_WORD_RE, line)
    matchSpanList = [match.span() for match in matches]

    count = 0
    for span in matchSpanList:
        count += span[1] - span[0]

    return count == len(line)


def removeFontTags(subblock):
    text = ''
    breakSpanList = []
    groupsSpanList = []
    prevIndex = 0

    for line in subblock:
        text += line + '<br>'
        breakSpanList.append((prevIndex + len(line), prevIndex + len(line) + 4))
        prevIndex += len(line) + 4

    matches = re.finditer(FONT_TAG_RE, text)
    for match in matches:
        for i in range(len(match.groups())):
            i += 1
            groupsSpanList.append(match.span(i))

    i = 0
    tempLine = ''
    tempBlock = []

    while i < len(text):
        cont = False
        k = 0
        while k < len(breakSpanList):
            if i == breakSpanList[k][0]:
                i += 4
                tempBlock.append(tempLine)
                tempLine = ''
                cont = True
                break
            k += 1

        m = 0
        while m < len(groupsSpanList):
            if i == groupsSpanList[m][0]:
                i += groupsSpanList[m][1] - groupsSpanList[m][0]
                cont = True
                break
            m += 1

        if cont: continue
        tempLine += text[i]
        i += 1

    subblock[:] = tempBlock


def removeTextForHI(subblock):
    prevIndex = 0
    text = ''
    breakSpanList = []
    matchSpanList = []

    for line in subblock:
        text += line + '<br>'
        breakSpanList.append((prevIndex + len(line), prevIndex + len(line) + 4))
        prevIndex += len(line) + 4

    matches = re.finditer(TEXT_FOR_HI_RE, text)
    matchSpanList = [match.span() for match in matches]

    i = 0
    tempLine = ''
    tempBlock = []

    while i < len(text):
        cont = False
        k = 0
        while k < len(breakSpanList):
            if i == breakSpanList[k][0]:
                i += 4
                tempBlock.append(tempLine)
                tempLine = ''
                cont = True
                break
            k += 1

        m = 0
        while m < len(matchSpanList):
            if i == matchSpanList[m][0]:
                i += matchSpanList[m][1] - matchSpanList[m][0]
                cont = True
                break
            m += 1

        if cont: continue
        tempLine += text[i]
        i += 1

    subblock[:] = tempBlock


def fixEntities(subblock):
    tempBlock = []
    for line in subblock:
        for key in ENTITIES_DICT:
            for entity in ENTITIES_DICT[key]:
                while entity in line:
                    line = line.replace(entity, key)
        tempBlock.append(line)

    subblock[:] = tempBlock


def fixExtraSpaces(subblock):
    subblock[:] = [' '.join(line.split()) for line in subblock]


def getIdentifyingVideoExp(subFilePath):
    basename = os.path.basename(subFilePath)
    dirtStrings = []

    if EPISODE_BASENAME_RE.match(basename):
        mGroups = EPISODE_BASENAME_RE.match(basename).groups()

        seriesName = mGroups[0].lower()
        seasonNum = int(mGroups[1])
        episodeNum = int(mGroups[2])
        episodeTitle = mGroups[3].lower()

        dirtStrings.append(r'{0} *x *\d?{1}'.format(seasonNum, episodeNum))
        dirtStrings.append(r's(eason)?\D*\d?{0}.*e(pisode)?\D*\d?{1}'.format(seasonNum, episodeNum))
        dirtStrings.append('({0}|{1}).*{2}'.format(re.escape(seriesName), episodeNum, re.escape(episodeTitle)))
    elif MOVIE_BASENAME_RE.match(basename):
        mGroups = MOVIE_BASENAME_RE.match(basename).groups()

        movieName = mGroups[0].lower()
        movieYear = mGroups[1]

        dirtStrings.append(r'{0}.*\(?{1}\)?'.format(movieName, movieYear))

    return dirtStrings


def isTimeStamp(sTest):
    m = TIMESTAMP_RE.match(sTest)
    return m is not None


def getEncoding(subFilePath):
    f = open(subFilePath, 'rb')
    raw_contents = f.read()
    encoding = chardet.detect(raw_contents)['encoding']
    f.close()

    if b't\x00h\x00e\x00' in raw_contents:  # only for english-written files. looks for byte sequence that resolves to 'the'
        return 'utf_16_le'
    elif encoding == 'ascii':
        return 'utf_8'

    return encoding


def fatal(errMsg):
    print('[FATAL] {}'.format(errMsg))
    print('[FATAL] Program is now exiting.')
    exit(1)


if __name__ == '__main__':
    main()
