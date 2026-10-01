# OpsAI

Intelligent IT operations assistant. The MVP is **assistance-only**: it can suggest actions, but it never auto-executes production changes.

Phase 1 (Foundation) ships a runnable monorepo with Next.js, FastAPI, PostgreSQL, and Docker Compose — health/status endpoints and a frontend that shows **OpsAI API: online**.

## Quick start

```bash
cp .env.example .env
# Optional on hosts with broken Docker bridge FORWARD (e.g. mixed nft/legacy):
#   sudo ./scripts/fix-docker-bridge.sh
docker compose up --build
```

| Surface   | URL |
|-----------|-----|
| Frontend  | http://localhost:3000 |
| Backend   | http://localhost:8000 |
| API docs  | http://localhost:8000/docs |
| Health    | http://localhost:8000/health |
| Readiness | http://localhost:8000/readiness |
| Status    | http://localhost:8000/api/v1/status |

## Stack

- **frontend/** — Next.js (TypeScript, Tailwind)
- **backend/** — FastAPI + Pydantic + SQLAlchemy (layered: `api`, `core`, `models`, `schemas`, `services`, `repositories`, stub `ai` / `rag`)
- **postgres** — PostgreSQL 16 via Compose
- **docs/architecture.md** — foundation architecture notes

## Environment

Copy `.env.example` to `.env`. Important keys:

- `DATABASE_URL`, `POSTGRES_*`
- `JWT_SECRET` (placeholder for Phase 2)
- `CORS_ORIGINS` (default `http://localhost:3000`)
- `AI_PROVIDER` / `AI_API_KEY` / `AI_MODEL` (placeholders — unused in Phase 1)
- `NEXT_PUBLIC_API_URL` (browser URL for the API, default `http://localhost:8000`)

Do not commit real secrets.

## Verify

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/readiness
curl -s http://localhost:8000/api/v1/status
# Open http://localhost:3000 — should show "OpsAI API: online"
```

## Intentionally deferred

Auth (beyond stubs), incidents CRUD, IA analysis, RAG, OAuth, logs upload, agent, Prometheus, Grafana, billing, Kubernetes.
