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

def _maybe_init_database():
    """Initialize the ORM schema + seed data when USE_DATABASE is enabled."""
    if os.environ.get("USE_DATABASE", "false").strip().lower() not in ("1", "true", "yes"):
        return
    try:
        from ..database.seed_loader import seed
        seed(force=False)  # idempotent: creates tables + seeds only if empty
    except Exception as e:  # pragma: no cover - never block app startup
        import logging
        logging.getLogger(__name__).warning("Database init/seed skipped: %s", e)


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )
    load_config(app)
    _maybe_init_database()
    views.register_blueprint(app)

    return app
