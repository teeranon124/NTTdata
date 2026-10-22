import logging
import os

_DEFAULT_SECRET = "autoprocure-secret-key-2026"
SECRET_KEY = os.environ.get("SECRET_KEY", _DEFAULT_SECRET)

# Warn loudly if running without a real secret while not in debug (i.e. production).
_is_debug = os.environ.get("FLASK_DEBUG", "1") not in ("0", "false", "False")
if SECRET_KEY == _DEFAULT_SECRET and not _is_debug:
    logging.getLogger(__name__).warning(
        "SECRET_KEY is using the built-in default in a non-debug environment. "
        "Set a strong SECRET_KEY via environment/Secrets Manager before production."
    )

AWS_REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

# Model IDs (kept in sync with webapp/agents/bedrock_client.py defaults).
BEDROCK_NEGOTIATOR_MODEL_ID = (
    os.environ.get("BEDROCK_NEGOTIATOR_MODEL_ID")
    or os.environ.get("BEDROCK_NEGOTIATOR_MODEL")
    or "anthropic.claude-3-5-sonnet-20240620-v1:0"
)
BEDROCK_ROUTER_MODEL_ID = (
    os.environ.get("BEDROCK_ROUTER_MODEL_ID")
    or os.environ.get("BEDROCK_ROUTER_MODEL")
    or "amazon.nova-lite-v1:0"
)

# AWS SES (email invites) — disabled by default so demos never block on a verified identity.
SES_ENABLED = os.environ.get("SES_ENABLED", "false").lower() in ("1", "true", "yes")
SES_SENDER_EMAIL = os.environ.get("SES_SENDER_EMAIL", "procurement-agent@autoprocure.nttdata.co.th")

# DEBUG follows FLASK_DEBUG (default on for local dev, off in the container which sets FLASK_DEBUG=0).
DEBUG = _is_debug
