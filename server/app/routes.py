from flask import (
    Blueprint, redirect, render_template, request,
    send_file
)

from . import routeServices
from . import database
from . import constants
from .constants import Paths

bp = Blueprint('app', __name__, url_prefix='/')


@bp.route('/')
def index():
    allOK = routeServices.checkAllInstalled()
    print( allOK )
    models = routeServices.getModels()
    queueDetails = routeServices.getQueueDetails()

    context = {
        'title': 'Whisper',
        'models' : models,
        'queueDetails' : queueDetails,
    }
    return render_template('index.html', **context)


@bp.route('/getQueueDetails')
def getQueueDetails():
    queueDetails = routeServices.getQueueDetails()
    return queueDetails

@bp.route('/addItem', methods=['POST'])
def transcribe():

    audioFile = request.files.get('file')
    if audioFile != None:
        inputFile = audioFile.filename
        id = database.addItem({"title": inputFile, "type": constants.audio_type, "file_name": inputFile, "status": "waiting"})
        audioFile.save( f"{Paths.waiting}/{id}.wav")
    else:

        url = request.form.get('youtubeURL')
        try:
            info = routeServices.getInfoForYouTubeVideo(url)
            title = info['title']
            ytId = info['id']
            database.addItem({"title": title, "type": constants.youtube_type, "file_name": ytId, "status": "waiting"})
        except Exception as e:
            return f"Error: Could handle find video - {e}"

    return "Added to queue"


@bp.route('/showTranscription/<id>', methods=['GET'])
def showTranscription( id ):
    print( "ID: " + id )

    # Load CSV file
    item = database.getItem(id)
    transcription = routeServices.loadTranscription( item['transcription_file'] )
    if item['type'] == 'audio':
        page = 'transcription.html'
    else:
        page = 'transcription_yt.html'

    context = {
        "title" : item['title'],
        "file" : item['file_name'],
        "id" : item['id'],
        "transcription" : transcription,
    }
    return render_template(page, **context)

@bp.route('/getItem/<id>', methods=['GET'])
def getItem( id ):
    item = database.getItem(id)
    transcription = routeServices.loadTranscription( item['transcription_file'] )
    context = {
        "title" : item['title'],
        "file" : item['file_name'],
        "id" : item['id'],
        "transcription" : transcription,
    }

    return context


@bp.route('/getFile/<id>', methods=['GET'])
def getFile( id ):
     path_to_file = f"../data/done/{id}.wav"

     return send_file(
         path_to_file, 
         mimetype="audio/wav")

@bp.route('/delete/<file_id>', methods=['GET'])
def delete(file_id):
    routeServices.deleteItem( file_id )
    return redirect( '/' )

@bp.route('/deleteItem', methods=['POST'])
def deleteItem():
    file_id = request.form.get('id', None)
    if file_id != None:
        routeServices.deleteItem( file_id )

        return {"status": "ok"}
    else:
        return {"status": "error"}

