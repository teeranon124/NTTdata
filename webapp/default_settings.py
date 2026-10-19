import os

SECRET_KEY = os.environ.get("SECRET_KEY", "autoprocure-secret-key-2026")
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
DEBUG = True
