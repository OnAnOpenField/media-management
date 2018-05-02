# media-manager
Variety of scripts to manage video files and their attributes.

These scripts utilize the [mkvmerge](https://mkvtoolnix.download/doc/mkvmerge.html) commandline utility, included 
in the [MKVToolNix](https://mkvtoolnix.download/) toolset, to analyze videos, as well as [Subliminal's](https://subliminal.readthedocs.io/en/latest/) commandline component to download subtitles.

## Install instructions
Download from the release page and run the setup batch file as administrator.

## Usage
Make sure to keep all the scripts in the same folder together along with their config.ini component.

Set your preferred paths in the config.ini and then set a run schedule to these scripts using your
OS's built-in scheduling software to run while you sleep, such as Task Scheduler for windows.

These scripts will:

1. Get the most recent videos and list them in a txt file, and
2. Extract embedded SRT subtitles from MKVs
3. Remove embedded subtitles from video files and any non-english audio tracks, as well as english commentary tracks
4. Automatically fetch missing subtitles online from OpenSubtitles, addic7ed and other subtitle sources
5. Get the most recent subtitle files and list them in a txt file
6. Remove ads from SRT subtitles based on commonly used expressions included in SubCreditsList.txt, strip color coding from text, and remove HI/SDH lines
