from enum import Enum

# Type of files we handle
audio_type = "audio"
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
    waiting = "./data/waiting"
    inprogress = "./data/inprogress"
    done = "./data/done"
    instance = "./instance"
    whisper = "./instance/whisper"
    models = "./instance/models"

    @classmethod
    def list(cls):
        return list(map(lambda c: c, cls))