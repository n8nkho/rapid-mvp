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
**Last updated:** 2026-03-07 (checkpoint 2026-03-057; PDF engagement workspace)

**Checkpoint tag:** `RAPID_CHECKPOINT_2026-03-057` — resume from **docs/RAPID_CHECKPOINT_2026-03-057.md**; prompt: see that file or "Continue RAPID from checkpoint".

**WORKING:**
- Requirements CRUD, transcript extract, archaeologist agent
- Gap analysis (244 scope items), analyse-all
- HITL pipeline: hitl_state, hitl-advance, hitl-reject, hitl-queue, hitl-events; **GET /engagement/{id}/hitl-report** (Excel)
- **Fit/Gap:** fit_gap_assessments table; POST fit-gap-assess, GET fit-gap-board, POST review, POST fit-gap-analyse-all
- **Sources (enterprise):** sources table; POST/GET/PATCH/DELETE /sources, GET /engagement/{id}/sources, **POST /sources/{id}/extract** (LLM); requirement columns source_id, source_excerpt, extraction_confidence
- **GET /engagement/{id}/completion-check** — engagement completion checklist (all reqs have fit-gap, all assessments reviewed)
- **RICEFW from gaps:** POST /engagement/{id}/ricefw-generate
- Engagement summary, process-mirror, KPI summary
- Process steps CRUD + extract; workflow BPMN
- RICEFW inventory (list, add, edit, delete, export Excel)
- Requirements + RICEFW Excel export/import; Phase F: requirements export optional "Fit-Gap" sheet; GET /requirements/template/download
- Feedback & pattern library, Sector & benchmarks, Agent Team & Simulation, Audit (audit_events, audit-trail)
- Supabase: … **sources**, audit_events, etc. (run POST /admin/migrate for sources table)

**OPEN ERRORS TO FIX:**
- None.

**NEXT IMPROVEMENTS TO CONTINUE:**
1. **docs/ENTERPRISE_UPGRADE_IMPROVEMENTS.md** — further items (referential integrity block delete, duplicate-check, HITL role-based views, etc.).
2. Optional: browser test; commit and deploy any uncommitted changes.
3. Further: maturity scoring UI, lessons-learned export, backlog prioritisation.

**RECENT CHANGES:**
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
