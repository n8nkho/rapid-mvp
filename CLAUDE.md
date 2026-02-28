# RAPID MVP — Backend

## What this is
FastAPI backend for RAPID, an AI-powered SAP S/4HANA gap analysis tool.
Deployed on Railway at: https://rapid-mvp-production.up.railway.app

## Stack
- Python + FastAPI
- Claude Haiku (via Anthropic SDK) for semantic gap analysis
- Supabase (write-only) for persisting results per engagement
- scope_items.py loaded in-memory at startup (244 SAP scope items)

## Key files
- main.py — FastAPI app, /gap-analysis, /requirements, /health, /catalogue, /lobs endpoints
- providers.py — AnthropicProvider class, complete(system_prompt, user_prompt) returns {content, tokens_used}
- scope_items.py — 244 SAP S/4HANA Cloud 2602 scope items, SCOPE_ITEMS list + get_catalogue_text()
- database.py — Supabase client, save_gap_analysis(), requirements CRUD
- requirements.txt — dependencies
- Procfile — web: uvicorn main:app --host 0.0.0.0 --port $PORT

## Supabase tables
- gap_results — engagement_id, process_description, matches (JSON), tokens_used, timestamp
- requirements — req_id (REQ-001 per engagement), engagement_id, title, description, source_type, tags, stakeholder, raw_input, status, created_at

## Requirements API (Phase 1)
- POST /requirements — create requirement, auto-generates REQ-XXX per engagement
- GET /requirements?engagement_id=X — list all for engagement
- GET /requirements/{req_id}?engagement_id=X — get single
- PATCH /requirements/{req_id}?engagement_id=X — update status/tags/title/description/stakeholder
- POST /gap-analysis accepts optional req_id — looks up description from requirements table

## Environment variables (in .env and Railway)
- ANTHROPIC_API_KEY
- SUPABASE_URL
- SUPABASEy
git push origin main — Railway auto-deploys on push
Or: railway up

## Testing
pytest tests/ for unit tests
curl https://rapid-mvp-production.up.railway.app/health to verify live

## Rules
- Never hardcode scope items — always use scope_items.py
- Never read scope items from Supabase — in-memory only
- Supabase is write-only (results storage)
- providers.py complete() always returns dict with content and tokens_used
- scope_items.py refresh cadence: every SAP release (Feb/Aug)
