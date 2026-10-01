# OpsAI Architecture

OpsAI is an intelligent IT operations assistant. The MVP is **assistance-only** and never auto-executes production changes.

## Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | Next.js (TypeScript, Tailwind)                  |
| Backend  | FastAPI + Pydantic + SQLAlchemy                 |
| Database | PostgreSQL 16                                   |
| Runtime  | Docker Compose (`frontend`, `backend`, `postgres`) |

## Auth (Phase 2)

- Password hashing via bcrypt (`passlib`)
- JWT access tokens (`PyJWT`, HS256)
- Roles: `ADMIN`, `TECHNICIAN`, `VIEWER` with `require_roles(...)` dependency
- OAuth routes exist as `501` stubs only

User model fields: `id`, `email`, `password_hash`, `name`, `role`, `created_at`, `updated_at`.

## Endpoints

| Path | Purpose |
|------|---------|
| `GET /health` | Liveness |
| `GET /readiness` | DB readiness |
| `GET /api/v1/status` | Product status |
| `POST /api/v1/auth/register` | Create user |
| `POST /api/v1/auth/login` | Issue JWT |
| `POST /api/v1/auth/logout` | Acknowledge logout |
| `GET /api/v1/auth/me` | Current user |
| `GET /api/v1/incidents*` | Protected stubs (Phase 3) |

## Roadmap (summary)

1 Foundation → 2 Auth → 3 Incidents CRUD → 4 Observability intake → 5 AI adapters → 6 RAG → 7 Analysis assistant → 8 Operator agent (approval-gated) → 9 Prometheus/Grafana → 10 Billing/tenancy → 11 Hardening → 12 Kubernetes.
