import os
import subprocess

from app import constants
from app.constants import Paths, Status
from app import database
from app import utils

import yt_dlp
import wave
import contextlib


def handleTask( task ):
    type = task['type']
    id = task['id']
    filename = task['file_name']

    database.updateItemStatus(task['id'], Status.inprogress)
    if type == constants.audio_type or type == constants.video_type:
        workingFile = filename

        convertedFile = convertAudioFile(id, workingFile)
        if convertedFile == None:
            return
        transcriptionFile = transcribe_audio(id, convertedFile, "transcription")
        if transcriptionFile == None:
            return

        # remove tmp file
        #os.remove(convertedFile)

    elif type == constants.youtube_type:
        url = f"{task['source_url']}"
        ytName = f"{task['file_name']}"
        fileName = f"transcription"

        convertedFile = convertYoutubeFile(id, ytName, url)
        if convertedFile == None:
            return
        transcriptionFile = transcribe_audio(id, convertedFile, fileName)
        if transcriptionFile == None:
            return

        if url.find('youtube.com') != -1:
            # remove converted file
            os.remove(convertedFile)
        else:
            database.updateItemType(task['id'], constants.audio_type)
            database.updateItemFilename(task['id'], "processed.wav")

        database.updateItemStatus(task['id'], "complete")

    database.updateTranscriptionFile( id, transcriptionFile )
    database.updateItemStatus(id, Status.complete)

def convertAudioFile(id, sourceFile):
    inputFile = f"{Paths.data}/{id}/{sourceFile}"
    outputFile = f"{Paths.data}/{id}/processed.wav"

    # Only convert if we don't already have a file!
    if os.path.exists(outputFile):
        print( "Not re-converting file as conversion already exists")
        return outputFile

    ffmpeg_location = utils.getPath('ffmpeg')
    command = f"'{ffmpeg_location}' -y -i '{inputFile}' -ar 16000 -ac 1 -acodec pcm_s16le '{outputFile}'"
    rc = subprocess.call(command, shell=True)
    if rc < 0:
        # process was killed by signal
        return None
    elif rc > 0:
        database.updateItemStatus( id, constants.Status.error )
        return None

    return outputFile

def convertYoutubeFile(id, youtubeID, url):
    inputFile = url #f"https://www.youtube.com/watch?v={youtubeID}"
    outputFile = f"{Paths.data}/{id}/processed"

    # Only convert if we don't already have a file!
    if os.path.exists(outputFile+".wav"):
        print( "Not re-converting file as conversion already exists")
        return outputFile+".wav"

    ffmpeg_location = utils.getPath('ffmpeg')

    URLS = [inputFile]

    ydl_opts = {
        'format': 'bestaudio/best',
        '--ffmpeg-location': ffmpeg_location,
        'quiet': True,
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav'
        }],
        'postprocessor_args': [
            '-osr', '16000',
            '-ac', '1'
        ],
        'prefer_ffmpeg': True,
        'outtmpl': outputFile,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            error_code = ydl.download(URLS)
            if error_code != 0:
                database.updateItemStatus( id, constants.Status.error )
                return None
        except Exception as e:
            database.updateItemStatus( id, constants.Status.error )
            return None

    return outputFile+".wav"


def transcribe_audio(id, inputFile, saveAs):
    outputFile = f"{Paths.data}/{id}/{saveAs}"

    lengthOfFile = getDuration(inputFile)

    command = [Paths.whisper, '-f', inputFile, '-m', f'{Paths.models}/ggml-base.en.bin', '-ocsv', '-of', outputFile]
    # command = [Paths.whisper, '-f', inputFile, '-m', f'{Paths.models}/ggml-small.en-tdrz.bin', '-tdrz', '-ocsv', '-of', outputFile]
    try:
        for line in execute(command):
            if line.startswith("["):
                time = line.split(' ')[0].replace('[', '')
                time = timeToSecs(time)
                percent = int((time / lengthOfFile) * 100)
                print( "Transcribing: " + str(percent) + "%" )
                database.updateItemStatus( id, f"Transcribing: {percent:.2f}%" )
    except Exception as e:
        database.updateItemStatus( id, constants.Status.error )
        print(e)
        return None

    database.updateItemStatus( id, constants.Status.complete )
    return outputFile + ".csv"

    rc = subprocess.call(command, shell=True)
    if rc < 0:
        # process was killed by signal
        return None
    elif rc > 0:
        database.updateItemStatus( id, constants.Status.error )
    return outputFile + ".csv"

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def getDuration(inputFile):
    fname = inputFile
    with wave.open(fname,'r') as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


def timeToSecs( time ):
    # Convert HH:MM:SS.mmm to seconds with ms as fraction
    h, m, s = time.split(':')
    secs = int(h) * 3600 + int(m) * 60 + float(s)
    ms = time.split('.')[1]
    return secs + (int(ms) / 1000)


