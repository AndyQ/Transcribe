# Transcribe 

Transcribe is a Flask server that uses a combination of FFMpeg, yt-dlp (a fork of youtube-dl), and Whisper.cpp (https://github.com/ggerganov/whisper.cpp) to  create a transcription of audio (wav,mp3, etc), video(mp4, mkv, etc) and YouTube videos.

The transcription can be viewed and listened to  within a generated webpage, and for YouTube vidoes a side-by-side player is shown. The playback is matched to the transcription (see screenshots).


## Screenshots

## Requirements
Note - this has been developed and tested on an M1 Mac.  It should work on other systems but your mileage may vary (and I can't provide any support for these).

Python 3.8 - other versions may also work
ffmpeg (https://ffmpeg.org/download.html) - Required to convert to 16bit mono audio
whisper.cpp (https://github.com/ggerganov/whisper.cpp) - v1.20 for Arm Macs is included in instance folder - if you require a different platform or version, then you would need to get the version from https://github.com/ggerganov/whisper.cpp and build as appropriate.

## Install

Install above dependancies

- FFMpeg needs to be linked or copied into the instance folder.
- Whisper.cpp needs to be compiled and copied or linked into the instance folder as `whisper`

(I'm be working on seeing if I can dynamically do this and maybe create a binding wrapper to directly integrate).

## Setup
python -m venv venv
. ./venv/bin/activate
pip install --upgrade pip

## Usage
To Start, simply run `run.sh` (or manually using `python3 main.py`)

## Credits
This was inspired by David Smith's (https://mastodon.social/@_Davidsmith) PodSearch (https://podsearch.david-smith.org), and Web-Whisper (https://github.com/pluja/web-whisper)
