#!/bin/bash

# Base video folder to start in
VIDEO_BASEPATH="/path/to/base-video-folder"
[[ ! -d "$VIDEO_BASEPATH" ]] && fatal "Directory $VIDEO_BASEPATH does not exist. Make sure to set the directory inside the script."

AVCTRACK="avc/h.264"

# simple function for handling fatal errors. (It outputs an error, and exits the program.)
fatal() {
	echo "[FATAL] $1"
	echo "[FATAL] Program is now exiting."
	exit 1
}

# Remux to mp4. $1
remux() {
	echo "********************************************************"
	echo "Remuxing $1"
	echo "********************************************************"
	
	EXT="${1##*.}"
	TARGETFILE="${1//.$EXT/.mp4}"
	ffmpeg -i "$1" -c copy "$TARGETFILE"
	rm -f "$1"
}

# re encode to mp4 h264. 
reencode() {
	echo "********************************************************"
	echo "Re-encoding $1"
	echo "********************************************************"
	EXT=${1##*.}									# Get file extension
	TEMPFILE="${1//.$EXT/.TEMP.mp4}"				# Set temporary output file
	TARGETFILE="${1//.$EXT/.mp4}"					# Set target file

	# Uncomment if you want to adjust the bandwidth for this thread
	#MYPID=$$    # Process ID for current script
	# Adjust niceness of CPU priority for the current process
	#renice 19 $MYPID

	echo "********************************************************"
	echo "Re-encoding to MP4 H.264"
	echo "********************************************************"
	
	# begin conversion
	HandBrakeCLI -i "$1" -f mp4 --aencoder copy -e qsv_h264 --x264-preset medium --x264-profile auto -q 18 --decomb bob -o "$TEMPFILE" || fatal "Handbreak has failed (Is it installed?)"

	rm -f "$1"
	mv "$TEMPFILE" "$TARGETFILE"
	# chmod 777 "$TARGETFILE" # This step may not be necessary, but hey why not.
}


while read -r file; do
	# this if statement checks if the file exists before proceeding
	[[ ! -f "$file" ]] && continue	
	
	OUTPUT=$(mkvmerge -i "$file")	
	# check if file is H264 and not mp4. Remux if true
	[[ ${OUTPUT,,} =~ $AVCTRACK ]] && [[ $file != *.mp4 ]] && {
		remux "$file"
		continue
	}
	# check if file is not H264 encoded. Begin conversion if true
	[[ ! ${OUTPUT,,} =~ $AVCTRACK ]] && reencode "$file"
done <<< $(find "$VIDEO_BASEPATH" -type f -name "*.ts" -or -name "*.mp4" -or -name "*.mkv" -or -name "*.avi" -or -name "*.m4v")
