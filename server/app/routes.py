import os
from flask import Blueprint, redirect, render_template, request, send_file, flash, current_app

from . import routeServices
from . import database
from . import constants
from .constants import Paths

bp = Blueprint("app", __name__, url_prefix="/")


@bp.route("/")
def home():
    allOK = routeServices.checkAllInstalled()
    print(allOK)
    models = routeServices.getModels()
    queueDetails = routeServices.getQueueDetails()

    context = {
        "title": "Whisper",
        "models": models,
        "queueDetails": queueDetails,
    }

    return render_template("home.html", **context)


@bp.route("/getQueueDetails")
def getQueueDetails():
    queueDetails = routeServices.getQueueDetails()
    return queueDetails


@bp.route("/addItem", methods=["POST"])
def transcribe():

    audioFile = request.files.get("file")
    youTubeURL = request.form.get('youtubeURL')
    youTubeURLList = request.form.get('youTubeURLList')

    rc = "Nothing done"
    if audioFile != None:
       rc = routeServices.addAudioFileItem( audioFile )

    elif youTubeURL != None and youTubeURL != "":

        url = request.form.get("youtubeURL")
        if url.find("youtu.be") == -1 and url.find("youtube.com") == -1:
            rc = "Error: Invalid YouTube URL"
        else:
            routeServices.addYouTubeURLItem( url )
    elif youTubeURLList != None and youTubeURLList != "":
        # split the text into lines
        youTubeURLList = youTubeURLList.replace("\r", "")
        lines = youTubeURLList.split("\n")

        for line in lines:
            line = line.strip()
            if line == "":
                continue

            url = line
            if url.find("youtu.be") == -1 and url.find("youtube.com") == -1:
                flash( f"Error: Invalid YouTube URL - {url}" )
                rc = f"Error: Invalid YouTube URL - {url}"
            else:
                routeServices.addYouTubeURLItem( url )

    return rc


@bp.route("/showTranscription/<id>", methods=["GET"])
def showTranscription(id):
    print("ID: " + id)

    # Load CSV file
    item = database.getItem(id)
    transcription = routeServices.loadTranscription(item["transcription_file"])
    if request.args.get("transcription_only"):
        page = "transcription_only.html"
    elif item["type"] == constants.audio_type:
        page = "transcription.html"
    elif item["type"] == constants.video_type:
        page = "transcription_vid.html"
    else:
        page = "transcription_yt.html"

    context = {
        "title": item["title"],
        "file": item["file_name"],
        "source_url": item["source_url"],
        "id": item["id"],
        "transcription": transcription,
    }
    return render_template(page, **context)


@bp.route("/getItem/<id>", methods=["GET"])
def getItem(id):
    item = database.getItem(id)
    transcription = routeServices.loadTranscription(item["transcription_file"])
    context = {
        "title": item["title"],
        "file": item["file_name"],
        "id": item["id"],
        "transcription": transcription,
    }

    return context


@bp.route("/getFile/<id>", methods=["GET"])
def getFile(id):
    item = database.getItem(id)

    path_to_file = f"../data/{id}/{item['file_name']}"

    return send_file(path_to_file, mimetype="audio/wav")


@bp.route("/delete/<file_id>", methods=["GET"])
def delete(file_id):
    routeServices.deleteItem(file_id)
    return redirect("/")


@bp.route("/exportItem", methods=["POST"])
def export():
    id = request.form.get("id", None)
    if id != None:
        item = database.getItem(id)
        path_to_file = f"./data/export/{id}.json"
        routeServices.exportTranscription(item, path_to_file)
        return {"status": "ok"}
    else:
        return {"status": "error"}


@bp.route("/deleteItem", methods=["POST"])
def deleteItem():
    file_id = request.form.get("id", None)
    if file_id != None:
        routeServices.deleteItem(file_id)

        return {"status": "ok"}
    else:
        return {"status": "error"}
