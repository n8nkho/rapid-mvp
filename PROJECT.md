# RAPID Project State

## What RAPID is
Two-phase AI-powered SAP S/4HANA implementation tool.
Phase 1: Requirements Capture (Process Mirror) - capture how business works today
Phase 2: Gap Analysis - map requirements to SAP S/4HANA Cloud 2602 scope items

## Live URLs
Backend: https://rapid-mvp-production.up.railway.app
Frontend: https://rapid-ui-wine.vercel.app
GitHub: https://github.com/n8nkho/rapid-mvp

## Current Status / Recent Changes
**Last updated:** 2026-03-09 (Sprint 5-6 backend: client portal auth, SteerCo report, memory/pattern agent close-and-learn, go-live checklist agent)

**Checkpoint tag:** `RAPID_CHECKPOINT_2026-03-057` — resume from **docs/RAPID_CHECKPOINT_2026-03-057.md**; prompt: see that file or "Continue RAPID from checkpoint".

**WORKING:**
- Requirements CRUD, transcript extract, archaeologist agent
- Gap analysis (244 scope items), analyse-all
- HITL pipeline: hitl_state, hitl-advance, hitl-reject, hitl-queue, hitl-events; **GET /engagement/{id}/hitl-report** (Excel)
- **Fit/Gap:** fit_gap_assessments table; POST fit-gap-assess (returns reasoning + confidence_score), GET fit-gap-board, POST review, POST fit-gap-analyse-all
- **GET /engagement/{id}/deliverable-progress** — blueprint_pct, ricefw_pct, test_scripts_pct, go_live_pct with detail breakdown
- **GET /command-center/alerts** — scan all engagements; HITL queue (high/medium), sign-off completeness, RICEFW missing estimates (low)
- **RICEFW inventory:** effort_days_low, effort_days_high, owner fields added (POST + PATCH support)
- **Pattern pre-check in fit-gap:** title word-overlap match injects relevant past resolution into user prompt
- **Sources (enterprise):** sources table; POST/GET/PATCH/DELETE /sources, GET /engagement/{id}/sources, **POST /sources/{id}/extract** (LLM); **POST /sources/{id}/upload-file** (PDF/DOCX/TXT → extracts text to sources.content + raw_content); requirement columns source_id, source_excerpt, extraction_confidence
- **GET /engagement/{id}/completion-check** — engagement completion checklist (all reqs have fit-gap, all assessments reviewed)
- **RICEFW from gaps:** POST /engagement/{id}/ricefw-generate
- **RICEFW Estimator Agent:** POST /engagement/{id}/ricefw-estimate-all — AI estimates effort_days_low/high for all unestimated items using Haiku + pattern library
- **Batch sign-off:** POST /engagement/{id}/signoff-batch-request — generates plain-English fit decision summary; marks reqs sme_approved; audits event
- **Blueprint Agent:** GET /engagement/{id}/blueprint/preview (JSON) + GET /engagement/{id}/blueprint/export (DOCX download with exec summary, scope, fit analysis, process docs, RICEFW table, risk register, sign-off page)
- **Test Script Generator:** POST /engagement/{id}/test-scripts/generate (body: ricefw_id?); GET /engagement/{id}/test-scripts. Haiku generates structured test cases (title, objective, preconditions, steps[], expected_result) per RICEFW item. Table: test_scripts.
- **Client Portal (Sprint 5-6):** portal_users table (token-based, 30-day expiry). POST /portal/invite → returns access_token + portal_url; GET /portal/auth/{token} → validate; GET /portal/{token}/overview (RAG health, progress, milestones, recent decisions); GET /portal/{token}/signoffs (pending with plain-English fit desc); POST /portal/{token}/signoffs/{req_id}/approve (sets confirmed); POST /portal/{token}/signoffs/{req_id}/query (stores HITL client_query); GET /portal/{token}/decisions; GET /portal/{token}/timeline.
- **SteerCo Report (Sprint 5-6):** POST /engagement/{id}/steerco-report (body: since_date, format="json"|"docx"). RAG computed (green/amber/red). LLM (Sonnet) writes 4-section narrative. DOCX export streams.
- **Memory/Pattern Agent (Sprint 5-6):** POST /engagement/{id}/close-and-learn. Sonnet extracts 3-5 reusable fit/RICEFW patterns → saved to pattern_library with industry_tag. Marks engagement status=closed. Audit event logged.
- **Go-Live Checklist Agent (Sprint 5-6):** go_live_checklist table. POST /engagement/{id}/go-live-checklist/generate (Haiku, 20-30 items by category/owner/due_date_offset_days); GET /engagement/{id}/go-live-checklist (with go_live_pct); PATCH /go-live-checklist/{item_id}. deliverable-progress now returns real go_live_pct.
- Engagement summary, process-mirror, KPI summary
- Process steps CRUD + extract; workflow BPMN
- RICEFW inventory (list, add, edit, delete, export Excel)
- Requirements + RICEFW Excel export/import; Phase F: requirements export optional "Fit-Gap" sheet; GET /requirements/template/download
- Feedback & pattern library, Sector & benchmarks, Agent Team & Simulation, Audit (audit_events, audit-trail)
- **POST /v1/simulate/seed-requirements** — body: engagement_id, industry?, process_areas?; Claude Sonnet generates requirements, runs fit-gap, sets HITL ai_draft
- **Fit-gap board:** fit_type normalized (e.g. spaces → underscores) for consistent grouping
- Supabase: … **sources**, audit_events, **test_scripts**, etc. (run POST /admin/migrate for new tables)

**OPEN ERRORS TO FIX:**
- None.

**POST-DEPLOY MIGRATION REQUIRED:**
Run these 3 SQL statements in Supabase SQL Editor (Dashboard → SQL Editor → New query):
```sql
CREATE TABLE IF NOT EXISTS portal_users (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), engagement_id text NOT NULL, client_id text NOT NULL, name text NOT NULL, email text NOT NULL, role text DEFAULT 'client_executive', access_token text UNIQUE, token_expires_at timestamptz, created_at timestamptz DEFAULT now(), last_access timestamptz);
CREATE INDEX IF NOT EXISTS idx_portal_users_token ON portal_users (access_token);
CREATE TABLE IF NOT EXISTS go_live_checklist (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), engagement_id text NOT NULL, category text NOT NULL, item text NOT NULL, owner text, due_date_offset_days integer, status text DEFAULT 'not_started', notes text, created_at timestamptz DEFAULT now());
CREATE INDEX IF NOT EXISTS idx_go_live_checklist_engagement ON go_live_checklist (engagement_id);
ALTER TABLE pattern_library ADD COLUMN IF NOT EXISTS industry_tag text;
```
Or: `curl -X POST https://rapid-mvp-production.up.railway.app/v1/admin/migrate -H "X-Admin-Key: rapid-admin-2026"` (returns full SQL if DATABASE_URL not configured).

**NEXT IMPROVEMENTS TO CONTINUE:**
1. Run new migration SQL in Supabase SQL Editor (two ALTER TABLE + CREATE TABLE test_scripts) — see _SOURCES_CONTENT_DDL + _TEST_SCRIPTS_DDL in main.py or POST /v1/admin/migrate response sql field.
2. **docs/ENTERPRISE_UPGRADE_IMPROVEMENTS.md** — further items (referential integrity block delete, duplicate-check, HITL role-based views, etc.).
3. Frontend: Blueprint preview page + export button; Test Scripts tab on RICEFW; upload-file for sources.
4. Further: maturity scoring UI, lessons-learned export, backlog prioritisation.

**RECENT CHANGES:**
- 2026-03-09: **Sprint 5-6 backend:** (1) Client Portal: portal_users table + POST /portal/invite, GET /portal/auth/{token}, 6× /portal/{token}/* endpoints (overview, signoffs, approve, query, decisions, timeline) — token auth, 30-day expiry, RAG health, plain-English fit labels; (2) SteerCo Report: POST /engagement/{id}/steerco-report — RAG computation, Sonnet 4-section narrative, JSON + DOCX export; (3) Memory/Pattern Agent: POST /engagement/{id}/close-and-learn — Sonnet extracts patterns to pattern_library with industry_tag, marks engagement closed; (4) Go-Live Checklist: go_live_checklist table + POST/GET/PATCH endpoints, Haiku generates 20-30 checklist items, deliverable-progress now returns real go_live_pct. DDL: _PORTAL_USERS_DDL, _GO_LIVE_CHECKLIST_DDL, _PATTERN_LIBRARY_EXTRA_DDL. Deployed to Railway.
- 2026-03-09: **Sprint 3-4 backend:** (1) POST /sources/{id}/upload-file (PDF/DOCX/TXT text extraction → raw_content + content); (2) POST /engagement/{id}/ricefw-estimate-all (RICEFW Estimator Agent, Haiku, pattern hint); (3) POST /engagement/{id}/signoff-batch-request (batch sign-off with plain-English fit summary + audit event); (4) GET /engagement/{id}/blueprint/preview + /blueprint/export (DOCX with 7 sections, LLM exec summary + risk register via Sonnet, per-process docs via Haiku); (5) POST /engagement/{id}/test-scripts/generate + GET /test-scripts (test script generator via Haiku, test_scripts table). Deps: pdfplumber, python-docx added. Migration: _SOURCES_CONTENT_DDL + _TEST_SCRIPTS_DDL.
- 2026-03-09: **Sprint 1 backend:** fit_gap_assessments + hitl_events now store `reasoning` and `confidence_score` (LLM returns 1-2 sentence fit_type justification); GET /engagement/{id}/deliverable-progress (blueprint_pct/ricefw_pct); RICEFW inventory adds effort_days_low, effort_days_high, owner to POST+PATCH; GET /command-center/alerts (prioritized action items across all engagements: hitl queue / sign-off completeness / ricefw estimates); fit-gap prompt now injects matching pattern library hint by title word overlap. Migration: _SPRINT1_ALTER_DDL adds 8 new columns. Run POST /v1/admin/migrate (needs DATABASE_URL on Railway for auto-run; SQL in response otherwise).
- 2026-03-09: **Seed requirements + fit-gap board fix (backend):** POST /v1/simulate/seed-requirements (Claude Sonnet: requirements + fit-gap + HITL ai_draft); fit-gap board normalizes fit_type with .replace(" ", "_"). **Frontend:** HITL and Assets/Capture use X-API-Key (fallback rapid-admin-2020); engagement detail shows "Seed test data" when requirements count is 0 (modal: industry + processes → POST seed-requirements, toast, refresh).
- 2026-03-08: **RACI + Scope + User mgmt (backend):** raci_matrix table (matrix, finalized, change_log); engagement_scope table (scope jsonb); GET/PATCH engagement/{id}/raci, GET/PATCH engagement/{id}/scope. Run POST /v1/admin/migrate to create new tables.
- 2026-03-08: **Enterprise UX batch (backend):** Client address (column + ClientCreate/ClientUpdate); engagements list and get_engagement_with_client return client_name; POST /v1/engagement/{engagement_id}/ask-rapid for context-sensitive Ask RAPID (engagement + client + requirements + fit-gap + RICEFW); fallback doc docs/RAPID_FALLBACK_2026-03-08.md; tag rapid-fallback-2026-03-08.
- 2026-03-07: **Frontend entity dropdowns:** rapid-ui uses EngagementSelector, ClientSelector, RequirementSelector across Audit, Sources, Gap Analysis, RACI, HITL, Requirements, Fit/Gap (client filter), Testing Command Center, Flow (jump to requirement). URL sync for engagement_id. No backend changes.
- 2026-03-07: **RAPID Test Agents / Testing Command Center** (from “Create a specification for building an agent or ag” PDF): fallback `rapid-fallback-2026-03-07` + **docs/RAPID_FALLBACK_2026-03-07.md**; **docs/RAPID_TEST_AGENTS_SPEC.md**; GET /v1/testing/scenarios, POST /v1/testing/run (API-level smoke/regression/import_export checks); optional push issues to platform_issues. Frontend: /testing-command-center (Environment, Scenario multi-select, Run Tests, results viewer). Nav: SYSTEM → Testing Command Center.
- 2026-03-07: Checkpoint **docs/RAPID_CHECKPOINT_2026-03-057.md** (Prompt for new Agent 3.7.2026). PDF-driven engagement workspace: Client context on engagement detail, hyperlinked IDs (EngagementLabel, ClientIdLink), workspace tab nav; spec v1.2.
- 2026-03-05: Enterprise Phases A–G: sources table + LLM extract; left sidebar + mission-control home; /sources two-panel + add source + extract; /requirements filters + drawer + pagination; Fit-Gap sticky summary + cost; HITL column descriptions + hitl-report Excel; completion checklist on engagement detail; onboarding wizard + empty states. Marker: **docs/RAPID_CHECKPOINT_2026-03-05.md**.
- 2026-03-04: Audit trail, Agent Simulation, Platform Backlog; checkpoint rapid-checkpoint-2026-03-04.
- Fallback tag: `rapid-fallback-2026-03-02`; phase tags rapid-fallback-phase-b through -f.

## Architecture decisions
- scope_items.py in-memory (not Supabase) - avoids timeout
- providers.py complete() returns dict with content and tokens_used
- REQ IDs auto-increment per engagement (REQ-001, REQ-002...)
- Railway for backend, Vercel for frontend
- No UI libraries - Tailwind only
- Claude Haiku for gap analysis (cost efficient)

## Key commands
Backend deploy + migrate: cd ~/Documents/rapid-mvp && ADMIN_API_KEY=<key> ./scripts/deploy_and_migrate.sh  (or railway up then ./scripts/post_deploy.sh)
Frontend deploy: cd ~/Documents/rapid-ui && npx vercel --prod --force
Run Claude Code: cd ~/Documents/rapid-mvp && claude
Test backend: curl https://rapid-mvp-production.up.railway.app/health

## How to continue with any AI
1. Share PROJECT.md and CLAUDE.md (this repo); for frontend also share rapid-ui PROJECT.md and CLAUDE.md.
2. **Short prompt:** Use the copy-paste prompt in **docs/RAPID_CHECKPOINT_2026-03-057.md** (or say: "Continue RAPID from checkpoint").
3. New agent should: read PROJECT.md (Open errors + Next improvements), then CLAUDE.md; fix open errors first, then pick next improvements.
4. Checkpoint marker: **docs/RAPID_CHECKPOINT_2026-03-057.md**.


## Feature Backlog (prioritised sprints)
Sprint 1: Client and Engagement Context
Sprint 2: Cross-linking and Navigation
Sprint 3: Multimodal Upload
Sprint 4: Process Hierarchy Levels 2-5
Sprint 5: Flow Visualisation As-Is and To-Be
Sprint 6: Excel Upload and Download
Sprint 7: RICEFW Customisation Inventory

## Current working features (confirmed 2026-02-28)
- /capture page: Conversation tab, Single Requirement, Paste Transcript, Use Template
- Requirements list with inline gap analysis, Sign Off, Traceability buttons
- /engagement dashboard (HITL state column, Review in HITL link)
- /engagement/[id] with workflow + HITL links
- /hitl HITL Review Board (advance/reject pipeline)
- /gap-analysis page
- /workflow/[reqId] BPMN As-Is workflow, extract from transcript
- RICEFW inventory (engagement #ricefw): list, add, edit, delete, export Excel
- 244 SAP scope items in-memory
- Archaeologist agent using Sonnet
- Gap analysis using Haiku
- Supabase: requirements, gap_results, process_steps, ricefw_inventory, hitl_events

## Value-added backlog and sequence
See **REFINED_BACKLOG.md** — phased plan aligned with current system (no duplicate modules). Fallback tag: `rapid-fallback-2026-03-02`.
