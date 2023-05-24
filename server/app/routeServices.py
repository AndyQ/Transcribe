import os
import csv
import shutil
import json

from .constants import Status, Paths
from . import database
from . import utils
from urllib.parse import urlparse, parse_qs, urlencode

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
    waiting = [x for x in items if x['status'] == Status.waiting or x['status'] == Status.pending]
    error = [x for x in items if x['status'] == Status.error]
    
    return {
        "completed": done,
        "processing": inprogress,
        "waiting": waiting,
        "error": error,
    }

def createFolder( id ):
    path = f"{Paths.data}/{id}"
    if not os.path.exists(path):
        os.makedirs(path)

def getInfoForYouTubeVideo(url):

    u = urlparse(url)
    query = parse_qs(u.query, keep_blank_values=True)
    index = int(query.get('index',[-1])[0]) - 1
    if query.get('v') is not None:
        # remove all values from query dict that aren't v
        query = {k: v for k, v in query.items() if k == 'v'}

        u = u._replace(query=urlencode(query, True))
        inputFile = u.geturl()
    else:
        inputFile = url

    ydl = yt_dlp.YoutubeDL({})
    info = ydl.extract_info(inputFile, download=False)
    if info != None and info.get('entries', None) is not None:
        if index > 0:
            info = info['entries'][index]
        else:
            raise ValueError("Invalid or missing list index")
    else:
        raise ValueError("Invalid or missing list index")

    return info



def loadTranscription( file ):
    # Load CSV file
    with open( file, 'r' ) as f:
        reader = csv.reader(f, quotechar='"', delimiter=',', escapechar='\\', 
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)
        contents = list(reader)

    transcription = []
    for i in range( len( contents ) ):
        if contents[i][0] == 'start':
            continue
        item = { 'id': i, 'start':  int(contents[i][0]), 'end': int(contents[i][1]), 'text': contents[i][2]}
        transcription.append( item )
    return transcription


def importTranscriptions():
    # Read items from ./data/import folder
    path = f'{Paths.data}/import'
    files = os.listdir(path)
    files = [file for file in files if file.endswith('.json')]
    for file in files:
        print( f"Importing item: {file}" )
        # Read json file into dict
        with open( f'{path}/{file}', 'r' ) as f:
            item = json.loads( f.read() )

            # Create new item in database
            id = database.addItem(item)
            createFolder( id )
            database.updateTranscriptionFile( id, f'{Paths.data}/{id}/transcription.csv' )

            print( f"Created new record with id {id}" )

            # Save transcription file
            with open( f'{Paths.data}/{id}/transcription.csv', 'w' ) as f:
                writer = csv.writer(f, quotechar='"', delimiter=',', escapechar='\\', 
                     doublequote=False, quoting=csv.QUOTE_NONNUMERIC, skipinitialspace=True)

                writer.writerow( ["start", "end", "text"] )
                for line in item['transcription']:
                    writer.writerow( [line["start"],line["end"], line["text"]] )

            # Remove file from import folder
            os.remove( f'{path}/{file}' )


    
def exportTranscription( item, path_to_file ):
    transcription = loadTranscription( item['transcription_file'] )
    item['transcription'] = transcription

    # write to json file
    with open( path_to_file, 'w' ) as f:
        f.write( json.dumps( item ) )


def deleteItem( id ):
    path = f'{Paths.data}/{id}'
    if os.path.exists(path):
        shutil.rmtree( path )

    database.deleteItem( id )

