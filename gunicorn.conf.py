"""
Gunicorn configuration for AutoProcure.AI.

Worker model: gthread (threaded sync workers). The app is I/O-bound — it holds
long-lived Server-Sent Events (SSE) streams open and makes blocking calls to
Amazon Bedrock. Threads let a single worker serve many concurrent SSE clients
and in-flight model calls without pulling in gevent/eventlet (which can monkey-
patch and conflict with boto3). Tune via env for the target instance size.
"""
import os

# Bind to the platform-provided port (App Runner/ECS set PORT), default 8080.
bind = f"0.0.0.0:{os.environ.get('PORT', os.environ.get('FLASK_PORT', '8080'))}"

# Processes & threads. For a 1 vCPU Fargate/App Runner task, 2 workers x 8 threads
# gives solid SSE concurrency. Override with WEB_CONCURRENCY / GUNICORN_THREADS.
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = int(os.environ.get("GUNICORN_THREADS", "8"))
worker_class = "gthread"

# SSE streams are long-lived; disable the request timeout killing them. The
# generator emits a heartbeat every ~15s, so idle connections stay healthy.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = 30
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "75"))

# Recycle workers periodically to bound any memory growth.
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = 100

# Logging to stdout/stderr for container log drivers (CloudWatch, etc.).
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# Preloading would run app import (and DB init/seed) once in the master before
# forking. We keep it off so each worker initializes its own DB engine cleanly.
preload_app = False
