import os
import atexit
from flask import Flask
from flask_cors import CORS
import logging


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "whisper.sqlite"),
    )

    CORS(app, resources={r"/*": {"origins": "*"}})

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # stop getQueueDetails route from being logged as it
    # happens every 5 seconds
    class AjaxFilter(logging.Filter):
        def filter(self, record):
            return "/getQueueDetails" not in record.getMessage()

    log = logging.getLogger("werkzeug")
    log.addFilter(AjaxFilter())

    # Import our Jinja template filters
    @app.template_filter()
    def to_secs(value):
        return value / 1000

    @app.template_filter()
    def format_millis(value):
        seconds = int(value / 1000) % 60
        minutes = int(value / (1000 * 60)) % 60
        hours = int(value / (1000 * 60 * 60)) % 24
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    from . import routes

    app.register_blueprint(routes.bp)
    from . import api

    app.register_blueprint(api.bp)

    # # a simple page that says hello
    # @app.route('/status')
    # def status():
    #     return 'OK'

    return app
