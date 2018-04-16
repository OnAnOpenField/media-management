#!/bin/bash

# Base video folder to start in
VIDEO_BASEPATH="/path/to/base-video-folder"

# simple function for handling fatal erros. (It outputs an error, and exits the program.)
fatal() {
    echo "[FATAL] $1";
    echo "[FATAL] Program is now exiting.";
    exit 1;
}

# Remux to mp4. $1 is original file
startRemux() {
    EXT="${1##*.}"
    TARGETFILE="${1//.$EXT/.mp4}"
    ffmpeg -i "$1" -c copy "$TARGETFILE"
    rm -f "$1"
}

[[ ! -d "$VIDEO_BASEPATH" ]] && fatal "Directory $VIDEO_BASEPATH does not exist. Make sure to set the folder in the script."
AVCTrack="video: h264"

while read -r file; do
    # this if selection statement checks if the file exists before proceeding.
    [[ ! -f "$file" ]] && continue

    # tests if file is H264 encoded. Skip conversion if H264 found
    OUTPUT=$(ffmpeg -i "$file")
    [[ ${OUTPUT,,} =~ $AVCTrack ]] && [[ $file != *.mp4 ]] && {
        startRemux "$file"
        continue
    }
    [[ ${OUTPUT,,} =~ $AVCTrack ]] && continue

    EXT=${file##*.}                         # Get file extension
    FILENAME=$file                          # %FILE% - Filename of original file
    BAKFILE="${FILENAME//.$EXT/.bak.$EXT}"      # Temporary File for transcoding
    mv "$FILENAME" "$BAKFILE"                       # Rename original file to [name].bak.[ext]
    FILENAME="${FILENAME//.$EXT/.mp4}"

    # Uncomment if you want to adjust the bandwidth for this thread
    #MYPID=$$    # Process ID for current script
    # Adjust niceness of CPU priority for the current process
    #renice 19 $MYPID

    echo "********************************************************"
    echo "Transcoding, Converting to H.264 w/Handbrake"
    echo "********************************************************"
    HandBrakeCLI -i "$BAKFILE" -f mp4 --aencoder copy -e qsv_h264 --x264-preset veryfast --x264-profile auto -q 16 --maxHeight 1080 --decomb bob -o "$FILENAME" || fatal "Handbreak has failed (Is it installed?)"

    echo "********************************************************"
    echo "Delete $BAKFILE"
    echo "********************************************************"

    rm -f "$BAKFILE"
    chmod 777 "$FILENAME" # This step may no tbe neccessary, but hey why not.
done <<< $(find "$VIDEO_BASEPATH" -type f -name "*.ts" -or -name "*.mp4" -or -name "*.mkv" -or -name "*.avi" -or -name "*.m4v")

Sleep 2
