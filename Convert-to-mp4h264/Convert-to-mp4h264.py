import subprocess
import os

VIDEO_BASEPATH = '/path/to/base-video-folder'
AVCTRACK = 'avc/h.264'

# simple function for handling fatal errors. (It outputs an error, and exits the program.)
def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    exit()

# Remux to mp4.
def remux(FILE):
    FILENAME, EXT = os.path.splitext(FILE)
    subprocess.call('ffmpeg -i "' + FILE + '" -c copy "' + FILE.replace(EXT, '.mp4') + '"', shell=True)
    os.remove(FILE)

def reencode(FILE):
    FILENAME, EXT = os.path.splitext(FILE)  # Get file extension
    TEMPFILE = FILE.replace(EXT, '.TEMP.mp4')  # Set set temporary output filename
    TARGETFILE = TEMPFILE.replace('.TEMP.mp4', '.mp4') # set target filename

    FFMPEG_COMMAND = 'ffmpeg -i "' + FILE + '" -c:v libx264 -crf 18 -preset:v medium -c:a copy "' + TEMPFILE + '"'
    HANDBRAKE_COMMAND = 'HandBrakeCLI -i "' + FILE + '" -f mp4 --aencoder copy -e qsv_h264 --x264-preset medium --x264-profile auto -q 18 --decomb bob -o "' + TEMPFILE + '"'

    print('** Transcoding, Converting to H.264')
    subprocess.call(HANDBRAKE_COMMAND, shell=True)

    print('** Deleting original file')
    os.remove(FILE)
    os.rename(TEMPFILE, TARGETFILE)

def main():
    # check if path provided exists
    if not os.path.isdir(VIDEO_BASEPATH):
        fatal(VIDEO_BASEPATH + " is not a directory. Make sure to set the path inside the script.")

    fileList = []
    # searches for video files with specified extensions
    for ROOT, DIRS, FILENAMES in os.walk(VIDEO_BASEPATH):
        for filename in FILENAMES:
            if filename.endswith('.ts') or filename.endswith('.avi') or filename.endswith('.mp4') or filename.endswith('.m4v') or filename.endswith('.mkv'):
                FILE = os.path.join(ROOT, filename)
                if not os.path.isfile(FILE): continue
                bOutput = subprocess.check_output('mkvmerge -i "' + FILE + '"', shell=True)
                OUTPUT = bOutput.decode()

                # check if file is H264 and not mp4. Remux if true, else check if file is not H264 encoded
                if AVCTRACK in OUTPUT.lower() and not filename.endswith('.mp4'):
                    remux(FILE)
                elif not AVCTRACK in OUTPUT.lower():
                    reencode(FILE)

if __name__ == '__main__':
    main()