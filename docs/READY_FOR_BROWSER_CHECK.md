# Ready for Browser Check — Agent Team & Simulation

**Fallback:** To revert agent-team work: `git checkout pre-agent-team-2026` (backend). Create the same tag in rapid-ui if needed.

## What was built

### Backend (rapid-mvp)

1. **Tables (run migration once)**  
   - `agent_roles`, `agent_knowledge`, `agent_maturity_scores`, `platform_issues`, **audit_events**  
   - Created and seeded when you run **POST /v1/admin/migrate** with header `X-Admin-Key: <ADMIN_API_KEY>`, or run **`ADMIN_API_KEY=<key> ./scripts/post_deploy.sh`** (migrate + smoke checks).  
   - If migrate returns `manual_required`, run the returned `sql` in Supabase SQL Editor (then seed agent roles manually or call a one-off seed if added).

2. **Endpoints**  
   - **GET /v1/agent-roles** — list agent roles  
   - **GET /v1/agent-roles/{role_id}/maturity** — maturity scores for role  
   - **POST /v1/agent-roles/{role_id}/maturity** — record maturity (criterion, score 1–5, notes)  
   - **POST /v1/simulate/agent-response** — get agent reply (body: engagement_id, agent_role_id, phase?, context_message?, conversation_turn?); optional headers **X-Actor-Id**, **X-Actor-Role**; logs audit event.  
   - **POST /v1/platform-issues** — create platform issue (optional X-Actor-Id, X-Actor-Role); logs audit event.  
   - **PATCH /v1/platform-issues/{id}** — update status/priority (optional engagement_id query, X-Actor-* headers); logs audit event.  
   - **GET /v1/platform-issues** — list (optional: engagement_id, priority, status)  
   - **GET /v1/engagement/{engagement_id}/platform-backlog** — issues grouped by priority  
   - **GET /v1/engagement/{engagement_id}/audit-trail** — unified HITL + audit_events (compliance).  
   - **POST /v1/admin/migrate** — creates/updates tables including **audit_events** (run once per deploy if needed; header **X-Admin-Key: &lt;ADMIN_API_KEY&gt;**).  

3. **Simulation script**  
   - `python3 scripts/run_zero_ev_simulation.py`  
   - Creates or reuses client "Zero EV Motors" and engagement, seeds ~100 requirements, runs fit-gap on a subset, logs platform issues.  
   - Set `API_URL` (e.g. `http://localhost:8000/v1`) and `API_KEY` if required.

4. **Tests**  
   - New tests: `TestAgentRoles`, `TestPlatformIssues`, `TestSimulateAgentResponse`.  
   - Full suite: `python3 -m pytest tests/ -v`

### Frontend (rapid-ui)

- **Spec only:** See **docs/FRONTEND_AGENT_BACKLOG_SPEC.md** for API contract and UI suggestions (agent conversation page, platform backlog list/filters).  
- Implement in rapid-ui when the repo is available; backend is ready.

---

## How to check in the browser

### 1. Backend

- **Health:** Open `https://rapid-mvp-production.up.railway.app/health` (or local `http://localhost:8000/health`).  
- **Agent roles:**  
  `GET /v1/agent-roles` (with API key if set). Expect 7 roles (lead_consultant, ba, manufacturing_sme, supply_chain_sme, finance_sme, it_architect, change_ux).  
- **Simulate:**  
  POST `/v1/simulate/agent-response` with body  
  `{"engagement_id": "<any_valid_engagement_id>", "agent_role_id": "lead_consultant", "context_message": "What should we focus on first?"}`  
  Expect 200 and `reply` in response.  
- **Platform backlog:**  
  After running the simulation script, `GET /v1/engagement/<engagement_id>/platform-backlog` should return `by_priority` with issues.

### 2. Run Zero EV simulation (optional)

```bash
export API_URL=https://rapid-mvp-production.up.railway.app/v1
# export API_KEY=your_key   # if backend requires it
python3 scripts/run_zero_ev_simulation.py
```

Note the printed `engagement_id`. Then in the UI (or via API):

- Open that engagement; confirm requirements list has many items.  
- Open fit-gap board for that engagement; confirm assessments.  
- Call `GET /v1/engagement/<that_engagement_id>/platform-backlog` and confirm high/medium/low issues.

### 3. Frontend (once implemented)

- **Agent simulation:** Select engagement and agent role, type a message, submit; see agent reply.  
- **Platform backlog:** Open platform backlog page or engagement tab; see list of issues and priorities.

---

## Deploy checklist

- [ ] Run **POST /v1/admin/migrate** (or run the returned SQL in Supabase) so new tables and agent seed exist.  
- [ ] Deploy backend (Railway); confirm `/health` and `/v1/agent-roles` respond.  
- [ ] Optionally run `scripts/run_zero_ev_simulation.py` against production API_URL to seed Zero EV Motors.  
- [ ] Implement frontend from **docs/FRONTEND_AGENT_BACKLOG_SPEC.md** and deploy rapid-ui.  
- [ ] Smoke-test: agent-roles, simulate/agent-response, platform-backlog in browser.
