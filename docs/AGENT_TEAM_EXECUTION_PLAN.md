# Agent Team & Zero EV Motors Simulation — Execution Plan

**Source:** Curated prompt (multi‑agent Cloud ERP project team + Phase 2 simulation).  
**Fallback marker:** Git tag `pre-agent-team-2026` created in both repos before any build.  
**One permission:** Execute full sequence below; E2E test and fix errors; system ready for browser check when complete.

---

## Scope Summary

| Phase | Goal | Key deliverables |
|-------|------|-------------------|
| **Phase 1** | Build and train agent team | Agent roles, knowledge bases, behavioral rules, self‑learning (feedback → pattern store), maturity scoring (1–5; proceed when ≥4). |
| **Phase 2** | Simulate real project (Zero EV Motors) | Full flow on platform; 80–150 requirements, 20–30 gaps, RTM; platform_issues → backlog; synthetic case + backlog + lessons. |

---

## Execution Sequence

### 0. Fallback marker (before any code changes)

- Create tag `pre-agent-team-2026` in **rapid-mvp** and **rapid-ui**.
- Document: “To revert agent-team work: `git checkout pre-agent-team-2026` (or reset to that tag).”

### 1. Data model & migrations

- **Backend (rapid-mvp)**  
  - **agent_roles** table: id, role_id (e.g. `lead_consultant`, `ba`, `manufacturing_sme`, `supply_chain_sme`, `finance_sme`, `it_architect`, `change_ux`), name, mandate, focus_areas (text[] or jsonb), behavior_rules (text), escalation_rules (text), created_at.  
  - **agent_knowledge** table (optional; or reuse/expand pattern_library): id, role_id, category, content, source. Seed with manufacturing/ERP/Zero‑like bullets.  
  - **agent_maturity_scores** table: id, role_id, criterion (domain_knowledge | reasoning_quality | authenticity | collaboration), score (1–5), assessed_at, notes.  
  - **platform_issues** table: id, engagement_id, agent_role_id, phase (pre_engagement | current_state | requirements | fit_gap), context (jsonb), problem_description (text), issue_type (usability | data_model_gap | missing_feature | performance | integration), suggested_improvement (text), priority (high | medium | low), status (open | triaged | backlog), created_at.  
  - Add to `run_migrations()` / admin migrate and document in CLAUDE.md.

### 2. Agent role definitions & seed data

- Seed **agent_roles** with the 7 roles (Lead ERP Consultant, BA, Manufacturing Ops SME, Supply Chain & Logistics SME, Finance & Controlling SME, IT/Integration Architect, Change Management/UX).  
- Seed **agent_knowledge** (or pattern_library) with:  
  - Manufacturing ERP best practices (discrete/EV, multi‑plant, Clean Core, fit‑to‑standard).  
  - Zero‑like context: EV motorcycles, mid‑market, multi‑currency, multi‑GAAP, quality/regulatory.  
  - Cross‑industry RTM and governance norms.  
- Optional: small “competitor zone” seed (e.g. typical maturity benchmarks).

### 3. Agent behavior & simulation APIs

- **POST /v1/simulate/agent-response** (or under `/v1/engagement/{engagement_id}/simulate/...`)  
  - Body: `engagement_id, agent_role_id, phase?, context_message?, conversation_turn?`  
  - Load agent role + knowledge; build role‑specific system prompt (mandate, focus, behavior_rules, escalation); call LLM; return reply.  
- **GET /v1/agent-roles**  
  - List configured agents (for UI/dropdown).  
- **GET /v1/agent-roles/{role_id}/maturity**  
  - Return latest maturity scores per criterion.  
- **POST /v1/agent-roles/{role_id}/maturity** (internal or admin)  
  - Record assessment (criterion, score 1–5, notes).  
- **Logic:** “Proceed to Phase 2 only when all agents have average ≥4” can be a helper or script; no need to block APIs.

### 4. Self‑learning & HITL integration

- Ensure **feedback_events** and **pattern_library** (existing) are used:  
  - On human correction or HITL reject, POST /feedback (if not already); **update_pattern_library** from feedback.  
- **Inject patterns into agent prompts:** when calling simulate/agent-response, optionally pass `industry` / `business_process` and inject top patterns from pattern_library into the agent’s system prompt so responses align with learned patterns.

### 5. Platform issues & backlog

- **POST /v1/platform-issues**  
  - Body: engagement_id, agent_role_id?, phase, context, problem_description, issue_type, suggested_improvement, priority.  
  - Creates **platform_issues** row (status=open).  
- **GET /v1/platform-issues**  
  - Query params: engagement_id, priority, status.  
- **PATCH /v1/platform-issues/{id}**  
  - Update status (e.g. triaged, backlog), priority.  
- **GET /v1/engagement/{engagement_id}/platform-backlog**  
  - Returns issues grouped by priority (high/medium/low) for display.

### 6. Phase 2 simulation runner

- **Script or endpoint:** `scripts/run_zero_ev_simulation.py` or **POST /v1/engagement/{id}/simulate/run-phase** (or multi‑step script).  
  - Steps:  
    1. Create or use client “Zero EV Motors” (Zero‑like) and engagement.  
    2. Pre‑engagement: IT + Lead Consultant + BA agents “fill” context (call agent-response, optionally persist to client/engagement metadata or synthetic notes).  
    3. Current state: Manufacturing & Supply Chain SME agents “describe” processes (conversation turns); create requirements/process steps via existing APIs (transcript extract or direct create).  
    4. Requirements capture: Lead Consultant + SME agents drive structured capture; BA normalizes (create requirements with correct template/process mapping).  
    5. Fit/Gap: Call existing fit-gap-assess (or analyse-all) for requirements; agents “confirm” or log issues.  
  - Throughout: when an agent “cannot express something” or “has to work around,” call **POST /platform-issues** with context and suggested_improvement.  
  - Target: 80–150 requirements, 20–30 gaps (fit_gap_assessments with fit_type gap_*), RTM links (existing req ↔ process ↔ gap).  
- **Deliverables:**  
  - Agent definitions + maturity scores (stored; GET endpoints).  
  - Synthetic client case: Zero EV Motors engagement populated.  
  - Platform backlog: GET platform-issues / engagement backlog.  
  - Lessons learned: optional markdown or JSON export (e.g. “where agents struggled,” “workarounds used”).

### 7. Frontend (rapid-ui)

- **Agent / Simulation:**  
  - Page or section to “Talk to an agent” (dropdown: role, engagement); call POST simulate/agent-response; show reply. Optional: list agent roles and maturity.  
- **Platform backlog:**  
  - Page or engagement tab “Platform issues” listing issues from GET platform-issues (or engagement backlog); filter by priority; show type, description, suggested improvement.

### 8. E2E testing & fixes

- Backend: pytest for new endpoints (agent-roles, maturity, platform-issues, simulate/agent-response with mocked LLM).  
- Frontend: build and smoke‑test (npm run build; manual check of new pages).  
- Fix any failing tests or build errors; address backlog items that block the flow (e.g. missing fields, unclear UX) so the “team” can proceed through the simulated project.

### 9. Deploy & readiness

- Deploy backend (Railway) and frontend (Vercel).  
- Run migration (or provide SQL for Supabase) so agent_roles, agent_maturity_scores, platform_issues (and optional agent_knowledge) exist.  
- Seed agent roles and knowledge.  
- Confirm: no errors in health/ready; new routes return 200.  
- Document for you: “Ready for browser check: &lt;URLs&gt;; do X, Y, Z to verify agent team and Zero EV simulation.”

---

## Order of implementation (concrete)

1. **Fallback tag** `pre-agent-team-2026` (both repos).  
2. **DB migrations**: agent_roles, agent_knowledge (or extended pattern_library), agent_maturity_scores, platform_issues.  
3. **Seed data**: Insert 7 agent roles + manufacturing/ERP/Zero‑like knowledge.  
4. **APIs**: GET agent-roles; POST simulate/agent-response; GET/POST agent maturity; POST/GET/PATCH platform-issues; GET engagement platform-backlog.  
5. **Self‑learning**: Wire feedback → pattern_library; inject patterns into simulate/agent-response.  
6. **Simulation script/runner**: Zero EV Motors client + engagement; multi‑phase steps; create requirements, fit/gap, log platform_issues; target 80–150 reqs, 20–30 gaps.  
7. **Frontend**: Agent conversation UI (by role); Platform issues/backlog view.  
8. **Tests**: Pytest + frontend build; fix failures.  
9. **Deploy**: Migrate, seed, deploy; document “ready for browser check.”

---

## Definition of done

- [x] Tag `pre-agent-team-2026` exists in rapid-mvp (rapid-ui tag when repo available).  
- [x] All new tables created and seeded (agent roles + knowledge) via POST /v1/admin/migrate.  
- [x] Agent-response and platform-issues APIs work; maturity and backlog queryable.  
- [x] Zero EV Motors simulation script: `scripts/run_zero_ev_simulation.py`; run to populate engagement + requirements + fit-gap + platform_issues.  
- [ ] Frontend: agent chat and platform backlog — spec in docs/FRONTEND_AGENT_BACKLOG_SPEC.md; implement in rapid-ui when repo available.  
- [x] E2E tests pass (75 tests including TestAgentRoles, TestPlatformIssues, TestSimulateAgentResponse).  
- [ ] Deploy backend; run migrate (or manual SQL); optionally run simulation script; then ready for browser check — see docs/READY_FOR_BROWSER_CHECK.md.

---

*One permission to Go: after you approve this sequence, implementation will start from step 1 (fallback tag) and proceed through step 9.*
