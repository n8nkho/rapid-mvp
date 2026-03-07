# RAPID API

FastAPI backend for the RAPID platform: AI-powered SAP S/4HANA scope item gap analysis and requirement management.

## Requirements

- Python 3.10+
- Supabase project (backend data and storage)

## Setup

1. Clone and create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. Copy environment template and set values:
   ```bash
   cp .env.example .env
   # Edit .env: set SUPABASE_URL, SUPABASE_KEY; optionally ANTHROPIC_API_KEY, CORS_ORIGINS, ADMIN_API_KEY, DATABASE_URL
   ```

3. Run locally:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   API: http://localhost:8000  
   Docs: http://localhost:8000/docs

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon or service role key |
| `ANTHROPIC_API_KEY` | No | For LLM-based gap analysis and extraction |
| `CORS_ORIGINS` | No | Comma-separated allowed origins (default: Vercel app + localhost:3000) |
| `DATABASE_URL` | No | Direct PostgreSQL URL for `/admin/migrate` auto-migration |
| `ADMIN_API_KEY` | No | If set, `/v1/admin/migrate` requires `X-Admin-Key` header or `?admin_key=` (no general API key needed for migrate) |
| `API_KEY` | No | If set, all `/v1` routes require `X-API-Key` or `Authorization: Bearer <key>` |

Application fails to start if required variables are missing. See `.env.example` for a template.

## Health and deployment

- **GET /health** — Liveness (app running).
- **GET /health/ready** — Readiness (app + DB reachable). Use for Kubernetes or load balancer probes.

Production: deploy to Railway (or similar). Set env vars in the platform; restrict CORS to your frontend origin(s).

**Deploy and run migration (one command):**

```bash
# Option A: Railway CLI (recommended). Install: npm i -g @railway/cli && railway link
ADMIN_API_KEY=your-admin-key ./scripts/deploy_and_migrate.sh

# Option B: Deploy via git push, then wait + migrate
git push origin main
SKIP_DEPLOY=1 ADMIN_API_KEY=your-admin-key ./scripts/deploy_and_migrate.sh

# Option C: Only run migration (after deploy is already live)
ADMIN_API_KEY=your-admin-key ./scripts/post_deploy.sh
```

Optional: put `ADMIN_API_KEY` and `API_URL` in a `.env` file in the repo root (do not commit); the scripts will load them. See **docs/DEPLOY_AND_MIGRATE.md** for full steps.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR: install deps, run `pytest tests/`. Set `SUPABASE_URL` and `SUPABASE_KEY` in the workflow (or use repo secrets) if tests need a real DB; otherwise conftest uses fake values and mocks.

## Docs and conventions

- **CLAUDE.md** — Context for AI and developers (models, endpoints, conventions).
- **PROJECT.md** — Product and scope notes.
- Commit format: `feat: ...`, `fix: ...`. Run tests and fix defects before committing.
# force redeploy Wed Mar  4 19:23:33 EST 2026
