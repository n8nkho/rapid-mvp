# RAPID Enterprise Upgrade — Checkpoint & Continuation Prompt

**Marker:** `ENTERPRISE_UPGRADE_CHECKPOINT`  
**Date:** 2026-03-04  
**Status:** Consolidated spec written; implementation not started. Current app unchanged and ready for browser testing.

---

## Context

Two design inputs were merged into a single improvements spec:

1. **RAPID Enterprise Upgrade Prompt** (12-part spec): workflow nav, mission-control home, Sources, dedicated Requirements page, referential integrity, Fit/Gap/HITL/RICEFW overhauls, forms, audit, onboarding, skeletons, backend endpoints.
2. **Design authority review (PDF):** Single Engagement Workspace, requirement as traceability node, Process Mirror (AS-IS/TO-BE), unified Capture Hub, HITL roles, agent personas, cursor-friendly API and regression.

**Consolidated document:** `docs/ENTERPRISE_UPGRADE_IMPROVEMENTS.md`

**Repos:** `rapid-mvp` (FastAPI backend), `rapid-ui` (Next.js frontend).  
**Production:** Backend Railway; frontend Vercel. See `CLAUDE.md` and `rapid-ui/CLAUDE.md`.

---

## Copy-paste prompt for a new agent

```
Continue the RAPID enterprise upgrade from this checkpoint.

1. Read this file: docs/ENTERPRISE_UPGRADE_CHECKPOINT.md
2. Read the full spec: docs/ENTERPRISE_UPGRADE_IMPROVEMENTS.md
3. Implement in the order specified (Phases A → G). Start with Phase A (Sources table + requirement columns; sources endpoints; deploy backend).
4. After each phase: run backend health and relevant tests; run frontend build; fix any errors; commit with a clear message (e.g. feat: Phase A — sources table and endpoints).
5. Follow CLAUDE.md and .cursor/rules/feature-completion.mdc (Build → Test → Defect clean → Commit → Deploy → Ready to check).
6. Do not change behavior of existing pages unless the spec explicitly requires it; the current app must remain testable in the browser.
```

---

## What’s done vs what’s next

- **Done:** Consolidated improvements document; checkpoint file; continuation prompt.
- **Next:** Phase A implementation (backend sources + requirement columns + endpoints), then Phases B–G per spec.

---

## Ready for browser

The **current application is unchanged**. You can test the existing app in the browser as-is. The improvements above are documented for the next agent to implement; no code changes have been made for the enterprise upgrade yet.
