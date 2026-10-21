import os

from dotenv import load_dotenv

# Load environment variables from .env before anything reads os.environ.
# override=False keeps any real shell/CI env vars authoritative over the file.
load_dotenv(override=False)

from webapp.web import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", "8080"))
    debug = os.environ.get("FLASK_DEBUG", "1") not in ("0", "false", "False")
    app.run(host="0.0.0.0", port=port, debug=debug)
