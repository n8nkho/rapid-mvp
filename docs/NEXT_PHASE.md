# Next phase / open items

**As of:** 2026-03-04 (after audit trail, migrate, post-deploy)

---

## Done this phase

- **Backend:** audit_events table, GET /engagement/{id}/audit-trail, audit logging on simulate + platform-issues (X-Actor-Id, X-Actor-Role).
- **Migrations:** audit_events in POST /v1/admin/migrate; manual SQL run in Supabase.
- **Post-deploy:** scripts/post_deploy.sh (migrate + smoke checks; handles manual_required; fixed /v1 double prefix).
- **Docs:** FRONTEND_AGENT_BACKLOG_SPEC includes Audit trail (§5) and actor headers; AGENTIC_ERA_UI_DESIGN.md; IMPLEMENTATION_COMPLETE.md.
- **PROJECT.md:** Updated working list, open errors (none), next improvements.

---

## Open items (in order)

### 1. Frontend — rapid-ui (not in this repo)

Implement in the **rapid-ui** repo per **docs/FRONTEND_AGENT_BACKLOG_SPEC.md**:

| Item | Spec section | Notes |
|------|----------------|------|
| Agent Simulation page | §1, §2 | GET agent-roles, POST simulate/agent-response; send X-Actor-Id, X-Actor-Role. |
| Platform Backlog | §4 | GET/POST/PATCH platform-issues, GET platform-backlog; send actor headers on create/update. |
| Audit Trail view | §5 | GET /engagement/{id}/audit-trail; list events, filter by _source, optional export. |
| Nav | §6 | Add "Simulate", "Platform backlog"; "Audit trail" on engagement. |

Reference: **docs/AGENTIC_ERA_UI_DESIGN.md** for HITL, consultant vs business user, compliance.

### 2. Optional — manual browser check

Per **docs/READY_FOR_BROWSER_CHECK.md**: verify engagement (e.g. ENG-016) — requirements, fit-gap board, platform backlog, health.

### 3. Later — simulation / agent

- Maturity scoring UI (GET/POST /agent-roles/{id}/maturity).
- Phase 2: lessons-learned export, backlog prioritisation.

---

## Commands

- **Post-deploy (after each deploy):**  
  `ADMIN_API_KEY=your-key ./scripts/post_deploy.sh`
- **Backend tests:**  
  `cd rapid-mvp && python3 -m pytest tests/ -v`
- **Resume for a new agent:**  
  Share PROJECT.md and CLAUDE.md; prompt: "Continue RAPID" or "RAPID checkpoint".
