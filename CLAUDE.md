# RAPID MVP — Backend

## What this is
FastAPI backend for RAPID, a two-phase AI-powered SAP S/4HANA implementation tool.
Deployed on Railway at: https://rapid-mvp-production.up.railway.app

## Two-Phase Architecture
Phase 1 - Requirements Capture (Process Mirror)
  Capture how the business actually works today before any SAP mapping.
  Output: structured requirements with tags, stakeholders, source types.

Phase 2 - Gap Analysis
  Map validated requirements to SAP S/4HANA Cloud 2602 scope items.
  Output: scope item matches with confidence, rationale, migration objects.

## Stack
- Python + FastAPI
- Claude Haiku via Anthropic SDK for semantic gap analysis
- Supabase for requirements storage and gap analysis results
- scope_items.py loaded in-memory at startup (244 SAP scope items, FSD 2602)

## Key files
- main.py — all endpoints
- providers.py — AnthropicProvider, complete(system_prompt, user_prompt) returns dict with content and tokens_used
- scope_items.py — 244 SAP scope items, SCOPE_ITEMS list, get_catalogue_text()
- database.py — all Supabase functions
- requirements.txt — dependencies
- Procfile — web: uvicorn main:app --host 0.0.0.0 --port $PORT

## Supabase tables
requirements:
  id, req_id (REQ-001...), engagement_id, title, description,
  source_type (Conversation/Document/Whiteboard/Video/SOP),
  tags (text array: pain_point/manual_step/secret_sauce/workaround/hand_off),
  stakeholder, raw_input, status (open/in_progress/analysed/closed), created_at

gap_results:
  id, engagement_id, req_id, process_description, matches (jsonb), tokens_used, timestamp

## Endpoints
GET  /health
GET  /lobs
GET  /catalogue?lob=
POST /requirements
GET  /requirements?engagement_id=
GET  /requirements/{req_id}?engagement_id=
PATCH /requirements/{req_id}?engagement_id=
POST /gap-analysis
GET  /results?engagement_id=
GET  /engagement/{engagement_id}/summary
POST /engagement/{engagement_id}/analyse-all
POST /requirements/extract-from-transcript
GET  /engagement/{engagement_id}/process-mirror

## Environment variables
ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_KEY

## Deploy
git push origin main — Railway auto-deploys
Or: railway up

## Testing
pytest tests/
curl "https://rapid-mvp-production.up.railway.app/health"

## Rules
- Never hardcode scope items — always use scope_items.py
- Supabase requirements table is read/write
- Supabase gap_results is write-only from gap analysis
- providers.py complete() always returns dict with content and tokens_used
- scope_items.py refresh every SAP release Feb/Aug
- All new endpoints must have error handling and meaningful HTTP status codes