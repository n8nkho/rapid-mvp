# RAPID API — Claude Context

## Project
FastAPI backend, Python, deployed on Railway.
Production URL: https://rapid-mvp-production.up.railway.app
**API base path:** All data/action routes are under `/v1` (e.g. `/v1/clients`, `/v1/requirements`). Health is unversioned: `/health`, `/health/ready`.
Frontend: https://rapid-ui-wine.vercel.app (must use base URL ending in `/v1`).
Run locally: uvicorn main:app --reload --port 8000

## CORS
Controlled by env: `CORS_ORIGINS` (comma-separated). If unset, defaults to https://rapid-ui-wine.vercel.app and http://localhost:3000. Do not use `*` in production.

## Config and security
- **Env validation:** Required vars (SUPABASE_URL, SUPABASE_KEY) are validated at startup; app fails fast if missing. See `.env.example` and README.md.
- **Admin:** `POST /v1/admin/migrate` is on a separate router and does not require the general API key. When `ADMIN_API_KEY` is set, send header `X-Admin-Key: <value>` or query `?admin_key=<value>`. When unset, migrate runs without auth.
- **5xx responses:** Global exception handlers return a generic message and `request_id`; internal details are logged only.

## Key Models
Client, Engagement, Requirement, Conversation, ProcessStep

## Client (extended)
- Standard: name, industry, employees, legal_entities, address, current_systems, systems_to_keep, systems_to_replace, countries, regulatory_environment
- Strategy/context (pre-fill from website): business_strategy, goals (array), key_products (array), value_proposition, senior_executives (array of {name, title}), direct_competitors (array), substitutes (array)
- **Prefill:** `POST /v1/clients/prefill-from-website` body `{ "url": "https://..." }` — fetches page, LLM extracts profile JSON to pre-populate Create Client form.
- **DB:** If adding new columns, run in Supabase SQL: `ALTER TABLE clients ADD COLUMN IF NOT EXISTS business_strategy text;` (and goals, key_products, value_proposition, senior_executives jsonb, direct_competitors jsonb, substitutes jsonb).

## Requirements: reference_id and RTM import
- **reference_id:** Optional field on requirements — stores external/source requirement ID (e.g. Excel RTM "Requirement ID" like FI-001) for audit trail. Internal id remains REQ-XXX.
- **New fields:** business_value, current_system, target_system_module, fit_type, related_test_case_id (all optional). Added via `POST /v1/admin/migrate`.
- **RTM Excel import:** `POST /v1/engagement/{engagement_id}/requirements/import` accepts RTM format (sheet "RTM" or first sheet with header row containing "Requirement ID", "Requirement Title", "Requirement Description"). Uses internal REQ-XXX numbering and stores Excel Requirement ID in reference_id. Map: Business Process Area → business_process, Sub-Process → process_level_2, Priority (High/Medium/Low) → Must-Have/Should-Have/Nice-to-Have, Source → stakeholder, Status → status, plus business_value, current_system, target_system_module, fit_type, related_test_case_id.
- **Script:** `python scripts/import_rtm_engagement.py ENG-001 /path/to/RAPID_RTM_Acme_S4.xlsx` to populate Engagement 001 from the RTM Excel.

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

## RICEFW Customisation Inventory (Sprint 7)
- Table: ricefw_inventory (id, engagement_id, req_id, type, name, description, status, created_at, updated_at)
- type: R | I | C | E | F | W (Reports, Interfaces, Conversions, Enhancements, Forms, Workflows)
- status: identified | approved | in_development | delivered | cancelled
- Endpoints: GET/POST /engagement/{engagement_id}/ricefw, PATCH/DELETE /engagement/{engagement_id}/ricefw/{item_id}
- Run POST /admin/migrate (or SQL in Supabase) to create ricefw_inventory.

## User–engagement access (reference table)
- **Table:** `user_engagement_access` — columns: `id` (uuid), `user_id` (text), `role` (text, e.g. owner/member/viewer), `engagement_id` (text), `created_at`, `updated_at`. Unique on (user_id, engagement_id).
- **Purpose:** Verify user and role per engagement; use to restrict access (e.g. list engagements by owner, enforce per-engagement checks). Created by `POST /v1/admin/migrate`. No API yet to populate or query; add when implementing real auth.

## Engagement scope and client data privacy
- **All work is scoped to a single engagement.** Requirements, RICEFW, process steps, assets, gap results, and analyses are always tied to an `engagement_id`. As a consulting company there are multiple engagements and clients; data must never be mixed across engagements.
- **Enforce engagement on every endpoint:** Read/update/delete must filter by `engagement_id`. When linking entities (e.g. RICEFW `req_id`), validate that the linked requirement belongs to the same engagement (return 400 if not).
- **Client data privacy is paramount.** Do not expose or combine data across engagements; do not allow cross-engagement references in create/update payloads.

## Conventions
- UUID for all IDs
- Return JSON always
- Fix all errors before committing
- Commit format: "feat: ...", "fix: ..."
- Test endpoints with curl after changes
- **Feature completion (must):** For every feature, confirm Build → Test → Defect clean → Commit → Deploy → Ready to check before done (see `.cursor/rules/feature-completion.mdc`).
- **Deploy tracking:** After pushing, track deployment (e.g. Railway) and pause until deploy succeeds before running post-deploy steps; no need to ask user permission.
- **Deploy + migrate:** Run `ADMIN_API_KEY=<key> ./scripts/deploy_and_migrate.sh` to deploy (Railway CLI), wait for health, then run migrations and smoke checks. Migrate-only: `ADMIN_API_KEY=<key> ./scripts/post_deploy.sh`. See docs/DEPLOY_AND_MIGRATE.md.
- **After every phase:** Update PROJECT.md and CLAUDE.md with current status / recent changes; create fallback git tag; run E2E tests.
- **After every feature completion:** Update docs/RAPID_Review_Spec_Standalone.md with current system state (new routes, nav, UX elements, pre-fill behaviour, Agent Testers, etc.) so the standalone spec stays accurate for reviewers.

## Fit/Gap (Phase B)
- **Table:** fit_gap_assessments (assessment_id e.g. FGA-001, req_id, engagement_id, fit_type, complexity, rationale, sap_scope_item_*, workaround_option, customisation_risk, clean_core_impact, estimated_effort_days_low/high, cost_band, confidence_score, hitl_state, reviewed_by, reviewed_at, reviewer_notes, …). Created via POST /admin/migrate or run_migrations().
- **Endpoints:** POST /v1/requirements/{req_id}/fit-gap-assess?engagement_id=… (idempotent); GET /v1/engagement/{engagement_id}/fit-gap-board; POST /v1/fit-gap-assessments/{assessment_id}/review?engagement_id=… (body: reviewer, notes?, approve, fit_type?, complexity?); POST /v1/engagement/{engagement_id}/fit-gap-analyse-all.
- **fit_type:** fit_standard | fit_config | fit_extension | gap_ricefw | gap_companion | out_of_scope. Board returns by_fit_type, by_process, summary (total, fit_count, gap_count, ai_draft, approved, effort days, complexity_breakdown).

## RICEFW from gaps (Phase C)
- **Endpoint:** POST /v1/engagement/{engagement_id}/ricefw-generate — from approved fit_gap_assessments where fit_type=gap_ricefw, creates ricefw_inventory items (type E, name=requirement title, description=rationale or title, status=identified). Skips req_ids that already have a RICEFW item. Returns { engagement_id, created, skipped, message }. Validates engagement exists (404 if not).

## Feedback & pattern library (Phase D)
- **Tables:** feedback_events (engagement_id, event_type, payload jsonb); pattern_library (name, category, content, use_count). Created via run_migrations; pattern_library seeded with 30 patterns if empty.
- **Endpoints:** POST /v1/feedback (body: engagement_id?, event_type, payload?; event_type=pattern_used + payload.pattern_id increments use_count); GET /v1/feedback?engagement_id=&limit=; GET /v1/pattern-library?limit=.
- **Prompt injection:** _get_top_patterns_text(limit=5) prepended to archaeologist and fit-gap system prompts when patterns exist.

## Sector & benchmarks (Phase E)
- **Client columns:** sector_archetype (text), complexity_drivers (jsonb array), erp_maturity (text), benchmark_opt_in (boolean, default true). Added via _CLIENTS_EXTRA_DDL in run_migrations.
- **Table:** benchmark_hints (id, engagement_id, category, title, content). Created via _BENCHMARK_HINTS_DDL.
- **Endpoints:** GET /v1/engagement/{engagement_id}/benchmark-hints — returns hints from table or derived from client (sector_archetype, erp_maturity, complexity_drivers); if client.benchmark_opt_in is false returns []. POST /v1/clients/{client_id}/benchmark-opt-out — sets benchmark_opt_in=false.
- **database.py:** update_client(client_id, updates), get_benchmark_hints_by_engagement(engagement_id), create_benchmark_hint(...).

## Current status / recent changes (for new agents)
- **Checkpoint marker:** **docs/RAPID_CHECKPOINT_2026-03-057.md**. Resume with prompt in that file (or "Continue RAPID from checkpoint"). Read PROJECT.md first.
- **PROJECT.md** has "Current Status / Recent Changes", "Open errors to fix", and "Next improvements to continue".
- **Open errors:** None.
- **Enterprise upgrade (Phases A–G done):** Sources table + POST/GET/PATCH/DELETE /sources, GET /engagement/{id}/sources, POST /sources/{id}/extract (LLM); requirement columns source_id, source_excerpt, extraction_confidence; GET /engagement/{id}/completion-check; GET /engagement/{id}/hitl-report (Excel). Frontend: left sidebar, mission-control home, /sources, /requirements (filters + drawer), /audit, Fit-Gap sticky summary + cost, HITL column descriptions + download report, completion checklist on engagement detail, onboarding wizard + empty states.
- **Sources:** create_source, list_sources_by_engagement, etc. in database.py; _SOURCES_DDL and _REQUIREMENTS_SOURCE_DDL in run_migrations.
- **HITL:** hitl-queue, hitl-events, **hitl-report** (Excel). Frontend: /hitl.
- **Fit/Gap:** fit_gap_assessments + endpoints. Frontend: /fitgap with sticky summary bar.
- **RICEFW from gaps:** POST ricefw-generate. **Agent Team:** agent_roles, platform_issues, simulate, platform-backlog.
- **Testing Command Center (RAPID Test Agents spec):** GET /v1/testing/scenarios, POST /v1/testing/run (body: scenario_ids, environment, engagement_id?, push_issues_to_backlog?). Runs API-level smoke/regression/import_export checks; returns run_id, summary (passed/failed/issues_count), issues[]. Optional push to platform_issues. Spec: docs/RAPID_TEST_AGENTS_SPEC.md. **Fallback:** rapid-fallback-2026-03-07; doc: docs/RAPID_FALLBACK_2026-03-07.md.
- **Frontend entity selectors:** rapid-ui has EngagementSelector, ClientSelector, RequirementSelector (app/components/); used on Audit, Sources, Gap Analysis, RACI, HITL, Requirements, Fit/Gap, Testing Command Center, Flow. GET /v1/engagements supports ?client_id= for filtered list.

## Excel export polish (Phase F)
- **Requirements export:** GET /v1/engagement/{engagement_id}/requirements/export — first sheet "Requirements" (unchanged). When fit_gap_assessments exist for the engagement, second sheet "Fit-Gap" is added (assessment_id, req_id, fit_type, complexity, rationale, sap_scope_item_*, effort days, cost_band, confidence_score, hitl_state, reviewed_by, reviewer_notes).
- **Template:** GET /v1/requirements/template/download — returns RAPID_requirements_template.xlsx with sheet "RTM" and header row (Requirement ID, Requirement Title, Requirement Description, Business Process Area, Sub-Process, etc.) for RTM import.
- **Frontend:** Engagement page has "Download template" button next to "Download Excel" and "Upload Excel".

## Agent Team & Simulation (Phase 1 / Phase 2)
- **Tables:** agent_roles (role_id, name, mandate, focus_areas jsonb, behavior_rules, escalation_rules); agent_knowledge (role_id, category, content, source); agent_maturity_scores (role_id, criterion, score 1–5, assessed_at, notes); platform_issues (engagement_id, agent_role_id?, phase, context jsonb, problem_description, issue_type, suggested_improvement, priority, status). Created via POST /v1/admin/migrate (includes _AGENT_ROLES_DDL and seed when agent_roles empty).
- **Ask RAPID (context-sensitive):** POST /v1/engagement/{engagement_id}/ask-rapid (body: question) — loads engagement, client, requirements, fit-gap, RICEFW; answers from context or directs user to human role. Fallback tag: rapid-fallback-2026-03-08.
- **Endpoints:** GET /v1/agent-roles; GET /v1/agent-roles/{role_id}/maturity; POST /v1/agent-roles/{role_id}/maturity (body: criterion, score, notes?); POST /v1/simulate/agent-response (body: engagement_id, agent_role_id, phase?, context_message?, conversation_turn?); **POST /v1/simulate/seed-requirements** (body: engagement_id, industry?, process_areas?; Claude Sonnet: creates requirements, runs fit-gap, HITL ai_draft); POST /v1/platform-issues (…); GET /v1/platform-issues?…; PATCH /v1/platform-issues/{id}; GET /v1/engagement/{engagement_id}/platform-backlog.
- **Fit-gap board:** fit_type is normalized (e.g. .replace(" ", "_")) so values like "fit standard" group correctly.
- **Simulation script:** `python3 scripts/run_zero_ev_simulation.py` — creates or reuses "Zero EV Motors" client/engagement, seeds ~100 requirements, runs fit-gap on subset, logs platform issues. Set API_URL and optionally API_KEY.
- **Frontend (to implement in rapid-ui):** Agent conversation page (select role, engagement; send context_message; display reply); Platform backlog page or engagement tab (list platform_issues, filter by priority, show suggested_improvement).
