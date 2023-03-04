import os
import subprocess
import uuid

from app import constants
from app.constants import Paths, Status
from app import database
from app import utils

import yt_dlp


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
        transcriptionFile = transcribe(id, convertedFile, "transcription")
        if transcriptionFile == None:
            return

        # remove tmp file
        #os.remove(convertedFile)

    elif type == constants.youtube_type:
        ytName = f"{task['file_name']}"
        fileName = f"transcription"

        convertedFile = convertYoutubeFile(id, ytName)
        if convertedFile == None:
            return
        transcriptionFile = transcribe(id, convertedFile, fileName)
        if transcriptionFile == None:
            return

        # remove converted file
        os.remove(convertedFile)

        database.updateItemStatus(task['id'], "complete")

    database.updateTranscriptionFile( id, transcriptionFile )
    database.updateItemStatus(id, Status.complete)

def convertAudioFile(id, sourceFile):
    inputFile = f"{Paths.data}/{id}/{sourceFile}"
    outputFile = f"{Paths.data}/{id}/processed.wav"

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

def convertYoutubeFile(id, youtubeID):
    inputFile = f"https://www.youtube.com/watch?v={youtubeID}"
    outputFile = f"{Paths.data}/{id}/processed"

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

def transcribe(id, inputFile, saveAs):
    outputFile = f"{Paths.data}/{id}/{saveAs}"

    command = f"{Paths.whisper} -f '{inputFile}'  -m {Paths.models}/ggml-base.bin -ocsv -of '{outputFile}'"
    rc = subprocess.call(command, shell=True)
    if rc < 0:
        # process was killed by signal
        return None
    elif rc > 0:
        database.updateItemStatus( id, constants.Status.error )
    return outputFile + ".csv"
