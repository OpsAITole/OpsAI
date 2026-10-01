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

## AI diagnosis (Phase 4)

- `AIProvider` interface with `analyze_incident` (+ thin stubs for summary/steps/report)
- Switch via `AI_PROVIDER`: `mock` (default) | `openai` | `ollama`
- `DiagnosisService` builds context + similar incidents (category/service/keywords), calls provider, validates with Pydantic, persists `incident_analyses`
- `POST /api/v1/incidents/{id}/analyze` — TECHNICIAN/ADMIN; `GET .../analysis` — latest saved
- Assistance-only: prompts forbid inventing facts and claim no production execution

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
| `POST /api/v1/incidents/{id}/analyze` | Run AI diagnosis |
| `GET /api/v1/incidents/{id}/analysis` | Latest saved analysis |

## Roadmap (summary)

1 Foundation → 2 Auth → 3 Incidents CRUD → 4 AI diagnosis → 5 Observability / RAG → 6 Operator agent (approval-gated) → 7 Prometheus/Grafana → 8 Billing/tenancy → 9 Hardening → 10 Kubernetes.
