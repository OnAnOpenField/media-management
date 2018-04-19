import subprocess
import os

VIDEO_BASEPATH = '/path/to/base-video-folder'
AVCTrack = 'video: h264'

# simple function for handling fatal errors. (It outputs an error, and exits the program.)
def fatal(errMsg):
    print('[FATAL] ' + errMsg)
    print('[FATAL] Program is now exiting.')
    exit()

# Remux to mp4.
def beginRemux(file):
    filename, EXT = os.path.splitext(file)
    TARGETFILE = file.replace(EXT, '.mp4')

    errcode = subprocess.call('ffmpeg -i "' + file + '" -c copy "' + TARGETFILE + '"', shell=True)
    if errcode != 0:
        fatal('ffmpeg has failed. Is it installed?')

    os.remove(file)

def main():
    # check if path provided exists
    if not os.path.isdir(VIDEO_BASEPATH):
        fatal(VIDEO_BASEPATH + " is not a directory. Make sure to set the path inside the script.")

    fileList = []
    # searches for video files with specified extensions
    for root, dirs, files in os.walk(VIDEO_BASEPATH):
        for file in files:
            if file.endswith('.ts') or file.endswith('.mp4') or file.endswith('.mkv') or file.endswith('.avi') or file.endswith('') or file.endswith('.m4v'):
                fileList.append(os.path.join(root, file))

    for file in fileList:
        # this if statement checks if the file exists before proceeding
        if not os.path.isfile(file):
            continue

        bOutput = subprocess.check_output('ffmpeg -i "' + file + '"', shell=True)
        OUTPUT = bOutput.decode()

        # check if file is H264 and not mp4. Remux if true
        if AVCTrack in OUTPUT.lower() and not file.endswith('.mp4'):
            beginRemux(file)
            continue

        # check if file is H264 encoded. Skip conversion if true
        if AVCTrack in OUTPUT.lower():
            continue

        FILENAME, EXT = os.path.splitext(file)                      # Get file extension
        TARGETFILE = file.replace('.' + EXT, '.mp4')                # Set the output filename
        BAKFILE = file.replace('.' + EXT, '.BAK.' + EXT)            # Set temporary file for transcoding
        os.rename(file, BAKFILE)                                    # Rename original file to [name].bak.[ext]

        print('** Transcoding, Converting to H.264 w/Handbrake')
        errcode = subprocess.call('HandBrakeCLI -i "' + BAKFILE + '" -f mp4 --aencoder copy -e qsv_h264 --x264-preset veryfast --x264-profile auto -q 16 --decomb bob -o "' + TARGETFILE + '"', shell=True)
        if errcode != 0:
            fatal("HandBrakeCLI has failed. Is it installed?")

        print('** Deleting ' + BAKFILE)
        os.remove(BAKFILE)

if __name__ == '__main__':
    main()