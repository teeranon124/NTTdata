# syntax=docker/dockerfile:1
# ==========================================================================
# AutoProcure.AI — Production image (multi-stage, non-root, Python 3.12-slim)
# ==========================================================================

# ---- Stage 1: builder — compile wheels into an isolated venv ----
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# Build deps for psycopg2 (libpq) — only needed at build time.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a self-contained virtual environment we can copy to the runtime stage.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


# ---- Stage 2: runtime — slim, non-root, no build toolchain ----
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_DEBUG=0

# Runtime-only native lib for psycopg2 (libpq), plus curl for the healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appgroup \
    && useradd --system --gid appgroup --home-dir /app --no-create-home appuser

# Copy the pre-built virtual environment from the builder stage.
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
# Copy application code (see .dockerignore for exclusions).
COPY . .

# Writable data dir for the SQLite file / session JSON; owned by the non-root user.
RUN mkdir -p /app/webapp/data/sessions \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8080

# Container-level healthcheck hits a cheap JSON endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8080/api/events || exit 1

# Gunicorn config lives in gunicorn.conf.py (gthread workers tuned for SSE/Bedrock I/O).
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
