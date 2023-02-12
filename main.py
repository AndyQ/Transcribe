# main.py
import atexit
import os

from app import create_app
from app.worker import watchdog
app = create_app()

if __name__ == "__main__":
    # start out watchdog thread on startup
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        watchdog.start_watchdog()
        atexit.register(watchdog.stop_watchdog)

    app.run(debug=True, host="0.0.0.0", port=8080)
