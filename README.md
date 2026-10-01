# OpsAI

Intelligent IT operations assistant. The MVP is **assistance-only**: it can suggest actions, but it never auto-executes production changes.

Phase 2 (Authentication) adds register/login/logout, JWT sessions, password hashing, `GET /api/v1/auth/me`, and RBAC-ready role guards (`ADMIN`, `TECHNICIAN`, `VIEWER`).

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
| Login     | http://localhost:3000/login |
| Register  | http://localhost:3000/register |
| Backend   | http://localhost:8000 |
| API docs  | http://localhost:8000/docs |
| Health    | http://localhost:8000/health |
| Readiness | http://localhost:8000/readiness |
| Status    | http://localhost:8000/api/v1/status |

## Auth API

| Method | Path | Auth |
|--------|------|------|
| `POST` | `/api/v1/auth/register` | public |
| `POST` | `/api/v1/auth/login` | public |
| `POST` | `/api/v1/auth/logout` | Bearer JWT |
| `GET` | `/api/v1/auth/me` | Bearer JWT |
| `GET` | `/api/v1/auth/oauth/{provider}` | stub `501` |
| `GET` | `/api/v1/auth/oauth/{provider}/callback` | stub `501` |

User fields: `id`, `email`, `password_hash`, `name`, `role`, `created_at`, `updated_at`.

## Stack

- **frontend/** — Next.js (TypeScript, Tailwind)
- **backend/** — FastAPI + Pydantic + SQLAlchemy (layered: `api`, `core`, `models`, `schemas`, `services`, `repositories`, stub `ai` / `rag`)
- **postgres** — PostgreSQL 16 via Compose
- **docs/architecture.md** — foundation + auth notes

## Environment

Copy `.env.example` to `.env`. Important keys:

- `DATABASE_URL`, `POSTGRES_*`
- `JWT_SECRET` (required for signing tokens)
- `CORS_ORIGINS` (default `http://localhost:3000`)
- `AI_PROVIDER` / `AI_API_KEY` / `AI_MODEL` (placeholders — unused)
- `NEXT_PUBLIC_API_URL` (browser URL for the API, default `http://localhost:8000`)

Do not commit real secrets.

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

## Verify

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"ops@example.com","password":"password123","name":"Ops"}'
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ops@example.com","password":"password123"}'
```

## Intentionally deferred

Incidents CRUD, IA analysis, RAG, OAuth (stubs only), logs upload, agent, Prometheus, Grafana, billing, Kubernetes.
