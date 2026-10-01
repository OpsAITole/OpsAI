# OpsAI

Asistente inteligente de operaciones IT. El MVP es **solo asistencia**: puede sugerir acciones, pero nunca ejecuta cambios en producción de forma automática.

La interfaz de usuario y las respuestas de asistencia IA están en **español (es-ES)**. El nombre de marca **OpsAI** se mantiene; los códigos de enum de API/BD (p. ej. `NEW`, `ADMIN`, `VPN`) permanecen en inglés.

La fase 4 (IA) añade proveedores desacoplados, diagnóstico estructurado de incidentes, persistencia y el control **Analizar con IA** en el detalle del incidente.

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

- **frontend/** — Next.js (TypeScript, Tailwind) with SaaS shell (Panel, Incidentes, Ajustes)
- **backend/** — FastAPI + Pydantic + SQLAlchemy (layered: `api`, `core`, `models`, `schemas`, `services`, `repositories`, `ai`)
- **postgres** — PostgreSQL 16 via Compose
- **docs/architecture.md** — architecture notes

## Environment

Copy `.env.example` to `.env`. Important keys:

- `DATABASE_URL`, `POSTGRES_*`
- `JWT_SECRET` (required for auth)
- `CORS_ORIGINS` (default includes `http://localhost:3000`)
- `AI_PROVIDER` — `mock` (default) | `openai` | `ollama`
- `AI_API_KEY` / `AI_MODEL` / `AI_BASE_URL` — required for real providers; unused with `mock`
- `NEXT_PUBLIC_API_URL` (browser URL for the API, default `http://localhost:8000`)

Do not commit real secrets.

## Auth, incidents & AI (smoke)

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
INC=$(curl -s -X POST http://localhost:8000/api/v1/incidents \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"title":"VPN caída","description":"Los usuarios no pueden conectar","category":"VPN","priority":"HIGH","affected_service":"vpn-gw","affected_system":"edge"}')
ID=$(echo "$INC" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')

# Analyze with mock AI (TECHNICIAN/ADMIN)
curl -s -X POST "http://localhost:8000/api/v1/incidents/$ID/analyze" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Latest analysis
curl -s "http://localhost:8000/api/v1/incidents/$ID/analysis" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Abre http://localhost:3000 — inicia sesión, abre un incidente y pulsa **Analizar con IA**.

## Tests

```bash
cd backend && python -m pytest -q
```

## Intentionally deferred

OAuth providers, RAG / pgvector, logs upload, agent auto-execution, Prometheus, Grafana, billing, Kubernetes.

If you previously ran older Compose volumes and see schema errors, reset with `docker compose down -v` then `up --build` again.
