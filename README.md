# Recipe App

This repository contains the greenfield scaffold for the social recipe app described in the approved PRD/TDD: chef-driven recipe publishing, social engagement, AI cooking assistance, and local-first development tooling.

## Current implementation status

This is the first implementation milestone: the local platform foundation is in place so subsequent backend/frontend work can build on a consistent stack.

## Stack

- Backend: FastAPI + Python
- Frontend: React + TypeScript + Vite
- Database: PostgreSQL 16
- Object storage: LocalStack S3
- AI runtime: Ollama (qwen2.5-coder:14b)
- Email testing: Mailpit
- Local orchestration: Docker Compose

## Local startup

Docker Desktop (or Docker Engine with the Compose plugin) is required. The committed `.env.example`
contains non-secret, local-only defaults. To start with the documented configuration:

1. Copy the sample environment file to `.env` (ignored by Git): `cp .env.example .env`.
2. Add your `LOCALSTACK_AUTH_TOKEN` to `.env` (details below).
3. Start the stack: `docker compose up --build`. The first startup downloads the configured Ollama
  model and may take a while.
4. Open the local services: frontend at <http://localhost:5173>, API health at
  <http://localhost:8000/health>, Mailpit at <http://localhost:8025>, and the LocalStack S3
  gateway at <http://localhost:4566>.

LocalStack requires an auth token associated with an active license. Set `LOCALSTACK_AUTH_TOKEN`
in your ignored `.env` before starting Compose; obtain it from your LocalStack workspace. Do not
commit or paste the token into project files. See the [LocalStack auth token guide](https://docs.localstack.cloud/aws/getting-started/auth-token/).

### Compose environment variables

Compose provides fallbacks for the non-secret settings below. `LOCALSTACK_AUTH_TOKEN` is required
and must be added to `.env`. Set other overrides in your ignored `.env` file. Variable names are
grouped by the service that reads or uses them; shared variables are listed for each relevant service.

| Service | Environment variables |
| --- | --- |
| `postgres` | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` |
| `localstack` | `LOCALSTACK_AUTH_TOKEN` |
| `s3-init` | `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` |
| `ollama` | `OLLAMA_MODEL` (model pulled at startup) |
| `mailpit` | None |
| `api` | `APP_ENV`, `APP_NAME`, `DATABASE_URL`, `S3_ENDPOINT`, `S3_PUBLIC_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `MAILPIT_SMTP_HOST`, `MAILPIT_SMTP_PORT`, `FRONTEND_URL` |
| `worker` | `APP_ENV`, `APP_NAME`, `DATABASE_URL`, `S3_ENDPOINT`, `S3_PUBLIC_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `MAILPIT_SMTP_HOST`, `MAILPIT_SMTP_PORT` |
| `frontend` | `VITE_API_URL`, `VITE_APP_NAME` |

`API_URL` and `MAILPIT_WEB_UI` in `.env.example` are convenience URLs for local reference; Compose
does not pass them to a service. The current Compose/backend configuration has no session-signing-key
environment variable, so no such setting is required to start this scaffold.

The database password (`app_password`) and LocalStack S3 credentials (`test` / `test`) are
development-only defaults. Mailpit accepts local test email without SMTP
credentials. These values and the local-only service setup are not suitable for production; use
deployment-managed secrets and production-specific credentials there. Never place real credentials
in `.env.example` or commit `.env`.

## Architecture notes

- The Docker Compose setup is intentionally scoped to the local MVP environment and does not include production deployment topology.
- The default AI/frontend choices follow the approved TDD defaults: React + TypeScript + Vite on the frontend, and Ollama + qwen2.5-coder:14b for the local AI service.
- Local development uses LocalStack S3 in place of the TDD's MinIO recommendation, per requester decision; the application retains its boto3/S3 API contract.
- LocalStack needs an active license for its auth token. Check the [LocalStack S3 guide](https://docs.localstack.cloud/aws/services/s3/) for endpoint behavior and the [LocalStack pricing page](https://www.localstack.cloud/pricing) for current plan costs.
- OTQ-001 (final frontend/CI/email-provider decision) is documented as an explicit follow-up item, not a blocker for starting the scaffold.

## Project structure

- `backend/` — FastAPI service and worker scaffold
- `frontend/` — Vite + React app scaffold
- `docker-compose.yml` — local Compose stack for API, worker, Postgres, LocalStack S3 and its bucket initializer, Ollama, frontend, and Mailpit
- `backend/app/s3_init.py` — idempotently creates local S3 buckets using the backend's existing boto3 dependency
- `README.md` — developer onboarding and local build instructions

## Agentic AI Workteam (Claude Code)

This project is built with the [Agentic AI Workteam](https://github.com/msg4wale/Agentic-AI-Workteam) (framework 1.0.0, Claude Code package). Agents live in `.claude/agents/`, skills in `.claude/skills/`, and the team's quality bar in `Constitution.md`. Durable progress (stage approvals, task board, decisions) lives in `.workteam/`. See `CLAUDE.md` for how to continue the run.
