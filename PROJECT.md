# RAPID Project State

## What RAPID is
Two-phase AI-powered SAP S/4HANA implementation tool.
Phase 1: Requirements Capture (Process Mirror) - capture how business works today
Phase 2: Gap Analysis - map requirements to SAP S/4HANA Cloud 2602 scope items

## Live URLs
Backend: https://rapid-mvp-production.up.railway.app
Frontend: https://rapid-ui-wine.vercel.app
GitHub: https://github.com/n8nkho/rapid-mvp

## Current Status (2026-02-28)
WORKING:
- POST /requirements - creates REQ-001, REQ-002 per engagement
- GET /requirements?engagement_id= - lists requirements
- POST /gap-analysis - semantic match against 244 SAP scope items
- GET /results?engagement_id= - retrieves past results
- /capture page - form to capture requirements with tags
- / page - gap analysis with expandable cards, LOB filter
- Supabase tables: requirements, gap_results

IN PROGRESS:
- GET /engagement/{id}/summary
- POST /engagement/{id}/analyse-all
- POST /requirements/extract-from-transcript
- GET /engagement/{id}/process-mirror
- /engagement page - dashboard
- Transcript ingestion tab on /capture

## Architecture decisions
- scope_items.py in-memory (not Supabase) - avoids timeout
- providers.py complete() returns dict with content and tokens_used
- REQ IDs auto-increment per engagement (REQ-001, REQ-002...)
- Railway for backend, Vercel for frontend
- No UI libraries - Tailwind only
- Claude Haiku for gap analysis (cost efficient)

## Key commands
Backend deploy: cd ~/Documents/rapid-mvp && railway up
Frontend deploy: cd ~/Documents/rapid-ui && npx vercel --prod --force
Run Claude Code: cd ~/Documents/rapid-mvp && claude
Test backend: curl https://rapid-mvp-production.up.railway.app/health

## How to continue with any AI
1. Share this PROJECT.md and both CLAUDE.md files
2. Say: Continue building RAPID - read PROJECT.md first
3. The AI has full context to continue any feature


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
