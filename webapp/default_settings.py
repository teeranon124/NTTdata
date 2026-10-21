import os

SECRET_KEY = os.environ.get("SECRET_KEY", "autoprocure-secret-key-2026")
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

DEBUG = True
