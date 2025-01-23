import os
from flask import Blueprint, redirect, render_template, request, send_file, current_app

from . import routeServices
from . import database
from . import constants
from .constants import Paths

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/jobs")
def getJobs():
    queueDetails = routeServices.getQueueDetails()
    return queueDetails


@bp.route("/getItem/<id>")
def getItem(id):
    item = database.getItem(id)
    transcription = routeServices.loadTranscription(item["transcription_file"])
    item["transcription"] = transcription

    return item
