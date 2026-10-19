import os
import json
from flask import Flask
from . import views

def load_config(app):
    app.config.from_object("webapp.default_settings")
    if os.environ.get("APP_SETTINGS"):
        app.config.from_envvar("APP_SETTINGS")

    # Load custom env variables if present
    for k, v in os.environ.items():
        if v in ["True", "TRUE", "False", "FALSE"]:
            v = v.lower()
        try:
            app.config[k] = json.loads(v)
        except Exception:
            app.config[k] = v

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )
    load_config(app)
    views.register_blueprint(app)

    return app
