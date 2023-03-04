from enum import Enum

# Type of files we handle
audio_type = "audio"
video_type = "video"
youtube_type = "youtube"

# Statuses
class Status:
    waiting = "waiting"
    pending = "pending"
    inprogress = "inprogress"
    complete = "complete"
    error = "error"

    @classmethod
    def list(cls):
        return list(map(lambda c: c, cls))


# Paths
class Paths:
    data = "./data"
    waiting = "./data/waiting"
    inprogress = "./data/inprogress"
    done = "./data/done"
    instance = "./instance"
    whisper = "./3rdparty/whisper"
    models = "./3rdparty/models"

    @classmethod
    def list(cls):
        return list(map(lambda c: c, cls))