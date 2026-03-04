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
**Last updated:** 2026-03-04 (Agent team, simulation, Railway repo connected)

**Checkpoint tag:** `rapid-checkpoint-2026-03-04` — use this to resume or for a new agent.

**WORKING:**
- Requirements CRUD, transcript extract, archaeologist agent
- Gap analysis (244 scope items), analyse-all
- HITL pipeline: hitl_state, hitl-advance, hitl-reject, hitl-queue, hitl-events
- **Fit/Gap:** fit_gap_assessments table (create in Supabase if missing — see Open errors); POST fit-gap-assess, GET fit-gap-board, POST review, POST fit-gap-analyse-all
- **RICEFW from gaps:** POST /engagement/{id}/ricefw-generate (from approved gap_ricefw assessments → ricefw_inventory)
- Engagement summary, process-mirror, KPI summary
- Process steps CRUD + extract; workflow BPMN
- RICEFW inventory (list, add, edit, delete, export Excel)
- Requirements + RICEFW Excel export/import; **Phase F:** requirements export includes optional second sheet "Fit-Gap" when fit_gap_assessments exist; GET /requirements/template/download (RTM template)
- **Feedback & pattern library (Phase D):** feedback_events, pattern_library tables; POST /feedback, GET /feedback, GET /pattern-library; top patterns injected into archaeologist and fit-gap prompts; 30 patterns seeded in migration
- **Sector & benchmarks (Phase E):** clients.sector_archetype, complexity_drivers, erp_maturity, benchmark_opt_in; benchmark_hints table; GET /engagement/{id}/benchmark-hints (derived from client or stored); POST /clients/{id}/benchmark-opt-out
- **Agent Team & Simulation:** agent_roles, agent_knowledge, agent_maturity_scores, platform_issues tables; GET /agent-roles, POST /simulate/agent-response, POST/GET/PATCH /platform-issues, GET /engagement/{id}/platform-backlog. Simulation script: `scripts/run_zero_ev_simulation.py` (Zero EV Motors client/engagement, ~87 requirements). Railway connected to GitHub n8nkho/rapid-mvp; platform-issues returns 200.
- Supabase: requirements, gap_results, process_steps, ricefw_inventory, hitl_events, fit_gap_assessments (create if missing), feedback_events, pattern_library, benchmark_hints, agent_roles, agent_knowledge, agent_maturity_scores, platform_issues

**OPEN ERRORS TO FIX:**
- None (fit_gap_assessments and ANTHROPIC_API_KEY fixed; simulation runs: 87 requirements, 87 fit-gap assessed, gaps populated).

**NEXT IMPROVEMENTS TO CONTINUE:**
1. **Frontend (rapid-ui):** implement Agent Simulation page and Platform Backlog per **docs/FRONTEND_AGENT_BACKLOG_SPEC.md** (GET /agent-roles, POST /simulate/agent-response, GET/POST /platform-issues, GET /engagement/{id}/platform-backlog).
2. Optional: manual browser test per docs/READY_FOR_BROWSER_CHECK.md; verify latest engagement (e.g. ENG-016) in UI — requirements, fit-gap board, platform backlog.
3. Further simulation/agent: maturity scoring UI, Phase 2 deliverables (lessons learned export, backlog prioritisation).

**RECENT CHANGES:**
- 2026-03-04: Errors fixed; simulation ENG-016: 87 requirements, 87 fit-gap assessed, 9 gaps. Stricter fit-gap prompt (niche/EV → gap_ricefw or gap_companion). Simulation script: parallel fit-gap-assess (6 workers) for faster run. Next phase: frontend Agent Simulation + Platform Backlog.
- 2026-03-04: Agent team + platform-issues APIs; Railway connected to n8nkho/rapid-mvp; checkpoint tag: rapid-checkpoint-2026-03-04.
- Phase F complete: requirements export second sheet "Fit-Gap"; GET /requirements/template/download; frontend "Download template".
- Fallback tag: `rapid-fallback-2026-03-02`; phase tags rapid-fallback-phase-b through -f.

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
1. Share PROJECT.md and CLAUDE.md (this repo).
2. **Short prompt:** `Continue RAPID` or `RAPID checkpoint`
3. New agent should: read PROJECT.md (Open errors + Next improvements), then CLAUDE.md; fix open errors first, then pick next improvements.
4. Checkpoint tag to resume from: `rapid-checkpoint-2026-03-04`.


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
