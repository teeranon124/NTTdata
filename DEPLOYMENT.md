# AutoProcure.AI — Deployment Guide (Phase E)

Cloud-native packaging and AWS deployment for the NTT DATA Digital Innovation
Challenge 2026. The app runs in three modes with zero code changes:

| Mode | Storage | Command |
| :--- | :--- | :--- |
| Local dev (zero-config) | SQLite / JSON files | `python app.py` |
| Local production-like | PostgreSQL 16 (compose) | `docker compose up --build` |
| AWS serverless (POC) | RDS PostgreSQL | App Runner / ECS Fargate |

---

## 1. Container image (Dockerfile)

- **Multi-stage build** on `python:3.12-slim`: a `builder` stage compiles
  dependencies into an isolated virtualenv; the `runtime` stage copies only that
  venv + app code, so the build toolchain never ships in the final image.
- **Non-root**: runs as the unprivileged `appuser`.
- **WSGI server**: Gunicorn with **`gthread` workers** (`gunicorn.conf.py`).
  The workload is I/O-bound — long-lived SSE streams plus blocking Amazon Bedrock
  calls — so threaded workers serve many concurrent connections per process
  without gevent/eventlet monkey-patching (which can conflict with `boto3`).
- **Healthcheck**: `GET /api/events` returns 200 when healthy.

Build & run locally:

```bash
docker build -t autoprocure:latest .
docker run -p 8080:8080 autoprocure:latest          # SQLite fallback mode
```

Tunables (env): `WEB_CONCURRENCY` (workers), `GUNICORN_THREADS`, `GUNICORN_TIMEOUT`.

---

## 2. Local production-like stack (docker-compose.yml)

Runs the web app against **PostgreSQL 16** with a healthcheck and a persistent
volume. Tables auto-create and seed (60 deals + 2,500 PRs) on first boot.

```bash
docker compose up --build
# Web  -> http://localhost:8080
# DB   -> localhost:5432 (autoprocure / autoprocure_pw)
```

The `web` service waits on the DB's `service_healthy` condition before starting.

---

## 3. AWS serverless deployment (pay-as-you-go POC)

Per the Mentor's Cloud Cost guidance, the POC targets **serverless, pay-as-you-go**
compute (scale toward zero when idle) instead of an always-on EC2 box.

### 3a. Push the image to Amazon ECR

```bash
AWS_REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr create-repository --repository-name autoprocure --region $AWS_REGION

aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

docker build -t autoprocure:latest .
docker tag autoprocure:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/autoprocure:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/autoprocure:latest
```

### 3b. Option A — AWS App Runner (simplest, recommended for POC)

Config: `deploy/apprunner.yaml`. App Runner pulls the ECR image, injects `PORT`,
and manages TLS, scaling, and health checks.

```bash
# Create from the console (Source = ECR image) or via copilot/IaC.
# Service settings:
#   Port 8080 | Health check: HTTP /api/events
#   Instance: 1 vCPU / 2 GB | Auto scaling: min 1, max 3
#   Instance role: bedrock:InvokeModel, bedrock:Converse,
#                  bedrock:ApplyGuardrail, ses:SendEmail (least privilege)
#   Secrets: DATABASE_URL, SECRET_KEY (from AWS Secrets Manager)
```

### 3c. Option B — AWS ECS Fargate

Config: `deploy/ecs-task-definition.json` (1 vCPU / 2 GB, awsvpc, CloudWatch logs,
secrets via Secrets Manager).

```bash
aws ecs register-task-definition --cli-input-json file://deploy/ecs-task-definition.json
# Then create a Fargate service behind an ALB (target group health check: /api/events).
```

### 3d. Database

Provision **Amazon RDS for PostgreSQL** and set `DATABASE_URL` (via Secrets
Manager), e.g. `postgresql+psycopg2://user:pass@host:5432/autoprocure`. On first
boot the app auto-creates tables, runs the lightweight column auto-migration, and
seeds the catalog. For a bootstrap you can also run the seed loader as a one-off
task: `python -m webapp.database.seed_loader --force`.

---

## 4. Cost analysis (for the pitch deck)

> Figures are planning estimates for `us-east-1`, rounded for comparison. Compute
> rates follow AWS public pricing; token rates follow Amazon Bedrock public
> pricing. Validate against the AWS Pricing Calculator before quoting externally.
> Content was rephrased/condensed for compliance with source licensing.

### 4a. Compute: Provisioned EC2 vs Serverless Fargate (POC profile)

Assumptions: 1 vCPU / 2 GB task; demo/POC traffic that is bursty and mostly idle
outside live sessions (~8 active hours/day).

| Option | Billing model | Idle cost | Est. monthly (POC) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| EC2 `t3.small` (provisioned, always-on) | Per-hour, 24×7 | Pays while idle | ~**$15–20** + EBS/ops | You patch/scale the box yourself |
| **Fargate (serverless, ~8h/day)** | Per-second vCPU+GB | Scale to min | ~**$7–12** | No server management; fits bursty POC |
| **App Runner (serverless)** | Per-second active + small idle | Low idle | ~**$10–18** | Simplest; built-in TLS/scaling/health |

Takeaway: for a bursty POC, **serverless (Fargate/App Runner) avoids paying for
idle 24×7 capacity** and removes undifferentiated server management — the
pay-as-you-go posture the Mentor recommended.

### 4b. Model tier: Dynamic Model Gateway savings (the big lever)

Per-turn token estimate: Router/intent ≈ 400 in / 80 out; Strategic negotiation ≈
1,200 in / 400 out. Public Bedrock rates (per 1M tokens):

| Model | Tier (gateway) | Input $/1M | Output $/1M | Source |
| :--- | :--- | ---: | ---: | :--- |
| Amazon Nova Lite | FAST (LIGHT tasks) | ~$0.06 | ~$0.24 | [markaicode 2026](https://markaicode.com/benchmarks/aws-bedrock-production-benchmark-latency/) |
| Claude 3.5 Sonnet | STRONG (HEAVY tasks) | ~$3.00 | ~$15.00 | [bigdataboutique](https://bigdataboutique.com/blog/aws-bedrock-pricing-guide) |

Cost per negotiation turn (1 router call + 1 negotiator call):

| Strategy | Router model | Negotiator model | Est. $/turn | Relative |
| :--- | :--- | :--- | ---: | :--- |
| Single strong model (Sonnet for everything) | Sonnet | Sonnet | ~**$0.0109** | 1.0× (baseline) |
| **Dynamic Gateway (Nova Lite router + Sonnet negotiator)** | Nova Lite | Sonnet | ~**$0.0096** | ~**0.88×** |
| All-light (demo/fallback, Nova Lite only) | Nova Lite | Nova Lite | ~**$0.0002** | ~0.02× |

The gateway routes cheap LIGHT work (intent parsing, validation) to Nova Lite and
reserves Claude 3.5 Sonnet for HEAVY strategic synthesis. The per-turn saving is
modest in isolation but compounds across **2,500 PRs → 60 deals × multiple rounds
× many suppliers**, and the architecture lets us shift more tasks to the fast tier
(or Claude Haiku) without touching business logic. Running fully in deterministic
fallback (no AWS) costs **$0** in model fees — ideal for safe on-stage demos.

### 4c. Supporting services (rough POC monthly)

| Service | Usage | Est. monthly |
| :--- | :--- | :--- |
| RDS PostgreSQL (`db.t4g.micro`) | Single-AZ POC | ~$13–16 |
| Amazon SES | <1k invite emails | <$1 |
| ECR storage | 1 small image | <$1 |
| CloudWatch logs | Low volume | ~$1–3 |

Overall a POC footprint runs on the order of **tens of USD per month**, with model
inference being usage-driven (and $0 in fallback) — well within a pay-as-you-go
POC budget.

---

## 5. Verification checklist

- `docker build .` produces a non-root image; `/api/events` healthcheck passes.
- `docker compose up` brings up web + Postgres; app seeds on first boot.
- App Runner / ECS use `/api/events` as the health probe and read secrets from
  Secrets Manager (never from committed files).
- Unit tests: `python tests/test_market_benchmark.py` and
  `python tests/test_audit_governance.py` (both backends) pass.
