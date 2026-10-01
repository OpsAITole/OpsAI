# OpsAI

Intelligent IT operations assistant. The MVP is **assistance-only**: it can suggest actions, but it never auto-executes production changes.

Phase 3 (Incidents) adds full incident CRUD, ticket numbers, RBAC, and an operator UI with list / create / detail views.

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

- **frontend/** — Next.js (TypeScript, Tailwind) with SaaS shell (Dashboard, Incidents, Settings)
- **backend/** — FastAPI + Pydantic + SQLAlchemy (layered: `api`, `core`, `models`, `schemas`, `services`, `repositories`)
- **postgres** — PostgreSQL 16 via Compose
- **docs/architecture.md** — architecture notes

## Environment

Copy `.env.example` to `.env`. Important keys:

- `DATABASE_URL`, `POSTGRES_*`
- `JWT_SECRET` (required for auth)
- `CORS_ORIGINS` (default includes `http://localhost:3000`)
- `AI_PROVIDER` / `AI_API_KEY` / `AI_MODEL` (placeholders — unused until later phases)
- `NEXT_PUBLIC_API_URL` (browser URL for the API, default `http://localhost:8000`)

Do not commit real secrets.

## Auth & incidents (smoke)

```bash
# Register first user as ADMIN (bootstrap)
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"password123","name":"Admin","role":"ADMIN"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"password123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# Create incident
curl -s -X POST http://localhost:8000/api/v1/incidents \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"title":"VPN down","description":"Users cannot connect","category":"VPN","priority":"HIGH","affected_service":"vpn-gw","affected_system":"edge"}'

# List
curl -s http://localhost:8000/api/v1/incidents -H "Authorization: Bearer $TOKEN"
```

Open http://localhost:3000 — sign in, then use **Incidents** in the sidebar.

## Tests

```bash
cd backend && python -m pytest -q
```

## Intentionally deferred

AI analyze (Phase 4+), OAuth providers, RAG, logs upload, agent, Prometheus, Grafana, billing, Kubernetes.

If you previously ran Phase 1/2 Compose volumes and see schema errors, reset with `docker compose down -v` then `up --build` again.
