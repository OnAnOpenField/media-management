# media-manager
Variety of scripts to manage video files and their attributes.

These scripts utilize the [mkvmerge](https://mkvtoolnix.download/doc/mkvmerge.html) commandline utility, included 
in the [MKVToolNix](https://mkvtoolnix.download/) toolset, to analyze videos.

## Install instructions
Download from the release page and run the setup batch file as administrator, then clone or download this repo.

## Usage
Make sure to keep all the scripts in the same folder together along with their config.ini component.

Set your preferred paths in the config.ini and then set a run schedule to these scripts using your
OS's built-in scheduling software to run while you sleep, such as Task Scheduler for Windows.

These scripts will:

1. Get the most recent videos and list them in a json file, and
2. Extract embedded SRT or ASS subtitles from MKV files
3. Remove embedded subtitles from video files and any "foreign" language audio tracks, as well as commentary tracks
4. Get the most recent subtitle files and list them in a json file
5. Remove ads from SRT subtitles based on commonly used expressions included in SubCreditsList.json, strip color coding from text, and remove HI/SDH lines
