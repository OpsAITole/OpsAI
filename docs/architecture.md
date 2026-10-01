# OpsAI Architecture — Foundation (Phase 1)

OpsAI is an intelligent IT operations assistant. The MVP is **assistance-only** and never auto-executes production changes.

For the full Phase 1 architecture (data model, APIs, roadmap 1–12, decisions), see the project store document or the sections below.

## Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | Next.js (TypeScript, Tailwind)                  |
| Backend  | FastAPI + Pydantic + SQLAlchemy                 |
| Database | PostgreSQL 16                                   |
| Runtime  | Docker Compose (`frontend`, `backend`, `postgres`) |

## Layout

```
frontend/   backend/   database/   docs/   scripts/   docker/
docker-compose.yml   .env.example   README.md
```

Backend layers: `api/` → `services/` → `repositories/` → `models/`, plus `core/`, `schemas/`, and stub packages `ai/`, `rag/`.

## Key decisions

- **Monorepo** — one Compose stack and coordinated changes.
- **API versioning** — `/api/v1` prefix.
- **SQLAlchemy + Alembic** — models and migrations folder ready; Phase 1 proves DB connectivity.
- **AIProvider** — interface stub only; no fake AI.
- **Security** — secrets via env, CORS allowlist, nothing sensitive in git.

## Phase 1 endpoints

| Path | Purpose |
|------|---------|
| `GET /health` | Liveness |
| `GET /readiness` | DB readiness |
| `GET /api/v1/status` | Product status for the frontend |

Auth and incidents routes are stub contracts (`501`) for later phases.

## Roadmap (summary)

1 Foundation → 2 Auth → 3 Incidents CRUD → 4 Observability intake → 5 AI adapters → 6 RAG → 7 Analysis assistant → 8 Operator agent (approval-gated) → 9 Prometheus/Grafana → 10 Billing/tenancy → 11 Hardening → 12 Kubernetes.
