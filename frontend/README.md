# OpsAI frontend — Phase 1 status shell

## Local (without Docker)

```bash
cp ../.env.example ../.env
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Prefer `docker compose up --build` from the repo root.
