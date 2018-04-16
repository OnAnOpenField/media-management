#!/bin/bash

# Base video folder to start in
VIDEO_BASEPATH="/path/to/base-video-folder"

# simple function for handling fatal errors. (It outputs an error, and exits the program.)
fatal() {
	echo "[FATAL] $1"
	echo "[FATAL] Program is now exiting."
	exit 1
}

# Remux to mp4. $1 is original file
startRemux() {
	EXT="${1##*.}"
	TARGETFILE="${1//.$EXT/.mp4}"
	ffmpeg -i "$1" -c copy "$TARGETFILE"
	rm -f "$1"
}

[[ ! -d "$VIDEO_BASEPATH" ]] && fatal "Directory $VIDEO_BASEPATH does not exist. Make sure to set the directory inside the script."
AVCTrack="video: h264"

while read -r file; do
	# this if statement checks if the file exists before proceeding
	[[ ! -f "$file" ]] && continue
	
	OUTPUT=$(ffmpeg -i "$file")
	# check if file is H264 and not mp4. Remux if true
	[[ ${OUTPUT,,} =~ $AVCTrack ]] && [[ $file != *.mp4 ]] && {
		startRemux "$file"
		continue
	}
	# check if file is H264 encoded. Skip conversion if true
	[[ ${OUTPUT,,} =~ $AVCTrack ]] && continue
	
	EXT=${file##*.}                         	# Get file extension
	TARGETFILE="${file//.$EXT/.mp4}"			# Set the output filename
	BAKFILE="${file//.$EXT/.bak.$EXT}"      	# Set temporary file for transcoding
	mv "$file" "$BAKFILE"                       # Rename original file to [name].bak.[ext]

	# Uncomment if you want to adjust the bandwidth for this thread
	#MYPID=$$    # Process ID for current script
	# Adjust niceness of CPU priority for the current process
	#renice 19 $MYPID

	echo "********************************************************"
	echo "Transcoding, Converting to H.264 w/Handbrake"
	echo "********************************************************"
	HandBrakeCLI -i "$BAKFILE" -f mp4 --aencoder copy -e qsv_h264 --x264-preset veryfast --x264-profile auto -q 16 --decomb bob -o "$TARGETFILE" || fatal "Handbreak has failed (Is it installed?)"

	echo "********************************************************"
	echo "Delete $BAKFILE"
	echo "********************************************************"

	rm -f "$BAKFILE"
	chmod 777 "$TARGETFILE" # This step may not be necessary, but hey why not.
done <<< $(find "$VIDEO_BASEPATH" -type f -name "*.ts" -or -name "*.mp4" -or -name "*.mkv" -or -name "*.avi" -or -name "*.m4v")
