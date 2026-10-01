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

## Incidents (Phase 3)

Fields: `id`, `ticket_number`, `title`, `description`, `status`, `priority`, `severity`, `category`, `affected_service`, `affected_system`, `created_by`, `created_at`, `updated_at`, `resolved_at`.

- Status: `NEW`, `INVESTIGATING`, `WAITING`, `RESOLVED`, `CLOSED`
- Priority / severity: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- Categories: `NETWORK`, `WINDOWS`, `LINUX`, `DATABASE`, `APPLICATION`, `SECURITY`, `VPN`, `DNS`, `CLOUD`, `HARDWARE`, `OTHER`
- Ticket numbers: `INC-0001`, …
- RBAC: all authenticated roles can read; `TECHNICIAN` / `ADMIN` can write
- `POST /api/v1/incidents/{id}/analyze` stays `501` until Phase 4

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
| `GET/POST /api/v1/incidents` | List / create |
| `GET/PUT/DELETE /api/v1/incidents/{id}` | Read / update / delete |

## Roadmap (summary)

1 Foundation → 2 Auth → 3 Incidents CRUD → 4 Observability intake → 5 AI adapters → 6 RAG → 7 Analysis assistant → 8 Operator agent (approval-gated) → 9 Prometheus/Grafana → 10 Billing/tenancy → 11 Hardening → 12 Kubernetes.
