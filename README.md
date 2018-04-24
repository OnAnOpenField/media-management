# media-manager
Variety of scripts to manage video files and their attributes.

These scripts utilize the [mkvmerge](https://mkvtoolnix.download/doc/mkvmerge.html) commandline utility, included 
in the [MKVToolNix](https://mkvtoolnix.download/) toolset, to analyze videos, as well as [Filebot](https://www.filebot.net/) and [Subliminal's](https://subliminal.readthedocs.io/en/latest/) commandline components

## Install instructions

Easiest way to get up and running and using these scripts is to install the [Chocolatey Package Manager](https://chocolatey.org/). From an elevated command prompt, run:

```
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
```
then close the command prompt window, then open an elevated command prompt again and run these install commands:

```
choco install python
```
```
choco install mkxtoolnix
```
```
choco install filebot
```
```
choco install subtitleedit
```
Install the latest .whl file for python3 from [Subliminal's](https://github.com/Diaoul/subliminal/releases) github release page
using the command
```
pip install filename.whl
```

## Usage
Make sure to keep all these files together along with the config.ini component.

Set your preferred paths in the config.ini and then set a run schedule to these scripts using your
OS's built-in scheduling software to run while you sleep, such as Task Scheduler for windows.

These scripts will:

1. Get the most recent videos and list them in a txt file, and
2. Extract embedded SRT subtitles from MKVs
3. Remove embedded subtitles from video files and any non-english audio tracks, as well as english commentary tracks
4. Automatically fetch missing subtitles online from OpenSubtitles, addic7ed and other subtitle sources
5. Get the most recent subtitle files and list them in a txt file
6. Remove ads from SRT subtitles based on commonly used expressions included in SubCreditsList.txt, remove color coded text, as well as
remove HI/SDH lines using the windows tool [Subtitle Edit's](http://www.nikse.dk/subtitleedit/) commandline component
