# RAPID API — Claude Context

## Project
FastAPI backend, Python, deployed on Railway.
Production URL: https://rapid-mvp-production.up.railway.app
Frontend: https://rapid-ui-wine.vercel.app
Run locally: uvicorn main:app --reload --port 8000

## CORS
Allow all origins from https://rapid-ui-wine.vercel.app and localhost:3000.

## Key Models
Client, Engagement, Requirement, Conversation, ProcessStep

## ProcessStep Schema
- id (uuid)
- req_id (foreign key to requirements)
- engagement_id
- step_number (int, ordering)
- title (str)
- description (str)
- performer_name (str)
- performer_role (str)
- shape: "start" | "end" | "process" | "decision" | "document"
- step_type: "manual" | "system" | "agentic"
- duration_minutes (float, nullable)
- systems_used (list of str)
- kpis: { error_rate_pct, volume_per_month, rework_rate_pct } (nullable floats)
- is_pain_point (bool, default false)
- next_step_id (str, nullable)
- branches: [{ label: str, target_step_id: s }] (for decision nodes)
- created_at, updated_at

## ProcessStep Endpoints
- GET    /requirements/{req_id}/process-steps
- POST   /requirements/{req_id}/process-steps
- PUT    /requirements/{req_id}/process-steps/{step_id}
- DELETE /requirements/{req_id}/process-steps/{step_id}
- POST   /requirements/{req_id}/process-steps/extract
  → fetch requirement + transcript, call LLM, extract steps as JSON array,
    infer shapes/branches/performers/pain points, save and return steps.
  → if no transcript, generate 5 sample steps relevant to requirement title.

## Conventions
- UUID for all IDs
- Return JSON always
- Fix all errors before committing
- Commit format: "feat: ...", "fix: ..."
- Test endpoints with curl after changes
