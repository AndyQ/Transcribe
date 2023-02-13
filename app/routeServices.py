import os
import subprocess
import csv

from . import constants
from .constants import Status, Paths
from . import database
from . import utils

import yt_dlp

def checkAllInstalled():
    ffmpegInstalled = utils.getPath('ffmpeg')
    whisperInstalled = utils.getPath('whisper')
    yt_dplInstalled = utils.getPath('yt-dlp')

    return {
        'ffmpeg': ffmpegInstalled,
        'whisper': whisperInstalled,
        'yt-dlp': yt_dplInstalled
    }


def getModels():
    path = Paths.models
    models = os.listdir(path)
    models = [model for model in models if model.startswith( 'ggml' ) and model.endswith('.bin')]
    return models


def getQueueDetails():

    items = database.getItems()   
    done = [x for x in items if x['status'] == Status.complete]
    inprogress = [x for x in items if x['status'] == Status.inprogress]
    waiting = [x for x in items if x['status'] == Status.waiting]
    error = [x for x in items if x['status'] == Status.error]
    
    return {
        "done": done,
        "inprogress": inprogress,
        "waiting": waiting,
        "error": error,
    }

def getNameOfYouTubeVideo(youtubeID):
    inputFile = f"https://www.youtube.com/watch?v={youtubeID}"

    try:
        ydl = yt_dlp.YoutubeDL({})
        info = ydl.extract_info(inputFile, download=False)
        return info['title']
    except Exception as e:
        print( e )
        database.updateItemStatus( id, constants.Status.error )

    # command = f"yt-dlp --get-title {inputFile}"
    # try:
    #     output = subprocess.check_output(command, shell=True)
    # except subprocess.CalledProcessError as e:
        
    #     if e.returncode < 0:
    #         # process was killed by signal
    #         return None
    #     elif e.returncode > 0:
    #         database.updateItemStatus( id, constants.Status.error )
    #         return None

    # return output.decode("utf-8").strip()



def loadTranscription( file ):
    # Load CSV file
    with open( file, 'r' ) as f:
        reader = csv.reader(f, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)
        transcription = list(reader)

    for i in range( len( transcription ) ):
        transcription[i][0] = int(transcription[i][0])
        transcription[i][1] = int(transcription[i][1])
    return transcription
    

def deleteItem( id ):
    item = database.getItem( id )

    for path in ['./data/waiting/','./data/inprogress/','./data/done/']:
        file =  path + id + ".wav" 
        if os.path.exists(file):
            os.remove(file)

    if item['transcription_file'] != None and os.path.exists( item['transcription_file']):
        os.remove( item['transcription_file'] )
    database.deleteItem( id )

