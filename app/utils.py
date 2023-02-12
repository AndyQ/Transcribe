import os
from shutil import which

def getPath(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which
    path = os.environ.get('PATH')
    path += ":./instance"
    os.environ['PATH'] = path

    path = which(name)
    return None if path is None else path
