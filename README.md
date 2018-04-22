# media-manager
Variety of scripts to manage video files and its attributes

## Usage
Make sure to keep all these files together in a folder with the config.ini component. 

Set your preferred paths in the config.ini and then set a schedule to these scripts using your
OS's built-in scheduling software, such as Task Scheduler for windows

In order, these scripts will:

1. Get the most recent video files for your media library
2. Extract embedded SRT files from MKVs
3. Fetch online subtitles using [Filebot](https://www.filebot.net/) and [Subliminal's](https://subliminal.readthedocs.io/en/latest/) commandline components
4. Remove embedded subtitle files video files and any non-english foreign track, including english commentary tracks
5. Get the most recent subtitle files
6. Filter SRT files based on commonly used expressions included in SubCreditsList.txt, as well as
remove HI/SDH lines using the windows tool [Subtitle Edit's](http://www.nikse.dk/subtitleedit/) commandline component
