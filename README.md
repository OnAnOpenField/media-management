# media-manager
Variety of scripts to manage video files and their attributes.

## Usage
Make sure to keep all these files together along with the config.ini component. 

Set your preferred paths in the config.ini and then set a run schedule to these scripts using your
OS's built-in scheduling software to run while you sleep, such as Task Scheduler for windows

These scripts utilize the [mkvmerge](https://mkvtoolnix.download/doc/mkvmerge.html) commandline utility, included 
in the [MKVToolNix](https://mkvtoolnix.download/) toolset, to analyze videos

These scripts will:

1. Get the most recent video files and list them in a txt file
2. Extract embedded SRT files from MKVs
3. Fetch online subtitles using [Filebot](https://www.filebot.net/) and [Subliminal's](https://subliminal.readthedocs.io/en/latest/) commandline components
4. Remove embedded subtitles from video files and any non-english audio tracks, as well as english commentary tracks
5. Get the most recent subtitle files and list them in a txt file
6. Filter SRT files based on commonly used expressions included in SubCreditsList.txt, as well as
remove HI/SDH lines using the windows tool [Subtitle Edit's](http://www.nikse.dk/subtitleedit/) commandline component
