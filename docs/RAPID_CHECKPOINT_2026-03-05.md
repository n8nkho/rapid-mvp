# RAPID checkpoint — continue with a new agent

**Marker:** `RAPID_CHECKPOINT_2026-03-05`  
**Date:** 2026-03-05  
**Repos:** rapid-mvp (backend), rapid-ui (frontend)

---

## What’s done (enterprise upgrade Phases A–G)

- **Phase A:** Sources table, sources CRUD + extract (LLM), requirement columns (source_id, source_excerpt, etc.), GET completion-check.
- **Phase B:** Left sidebar nav (SETUP, DISCOVER, ANALYSE, GOVERN, COLLABORATE, SYSTEM), engagement banner, mission-control home (summary pills + Next Actions).
- **Phase C:** /sources two-panel page, Add source (paste text), Extract requirements (AI), link reqs to source.
- **Phase D:** /requirements filters (sessionStorage), table with HITL/fit type/source, pagination, right-side detail drawer.
- **Phase E:** Fit-Gap sticky summary bar + cost estimate; HITL column descriptions; GET hitl-report (Excel); Download HITL report on /hitl.
- **Phase F:** Completion checklist on engagement detail (GET completion-check).
- **Phase G:** Onboarding wizard on Home when no engagements (3 steps); empty-state “Learn more” on sources and requirements.

---

## Where to read next

- **rapid-mvp:** `PROJECT.md` (status, open errors, next improvements), `CLAUDE.md` (API, models, conventions).
- **rapid-ui:** `PROJECT.md`, `CLAUDE.md`.
- **Enterprise spec (future work):** `docs/ENTERPRISE_UPGRADE_IMPROVEMENTS.md`, `docs/ENTERPRISE_UPGRADE_CHECKPOINT.md`.

---

## Copy-paste prompt for a new agent

```
Continue RAPID from checkpoint. Read rapid-mvp/PROJECT.md and rapid-mvp/CLAUDE.md first, then rapid-ui/PROJECT.md and rapid-ui/CLAUDE.md. Fix any open errors, then pick the next improvement from PROJECT.md "Next improvements". Follow .cursor/rules/feature-completion.mdc (Build, Test, Commit, Deploy, Ready to check). Checkpoint marker: docs/RAPID_CHECKPOINT_2026-03-05.md.
```
