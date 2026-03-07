# RAPID fallback marker — 2026-03-08

**Tag (both repos):** `rapid-fallback-2026-03-08`

Use this to restore state **before** the Enterprise UX & feature improvements batch (client address, display-only + versioning, engagement client name, phases, scope, Ask RAPID context, User management, RACI table, links/messages/spellcheck).

## How to restore

**Backend (rapid-mvp):**
```bash
cd /path/to/rapid-mvp
git fetch --tags
git checkout rapid-fallback-2026-03-08
```

**Frontend (rapid-ui):**
```bash
cd /path/to/rapid-ui
git fetch --tags
git checkout rapid-fallback-2026-03-08
```

Then redeploy (Railway backend, Vercel frontend) if needed.

## What this fallback represents

State before:
- Client address field; client/engagement display-only view + Edit + version/audit logs
- Engagement Overview showing Client name; modern phases (Discovery & Prepare, etc.); scope L1/L2/L3
- Engagement dashboard dropdown + correct requirement count; engagement listings with Client name
- Ask RAPID context-sensitive to engagement/client data; fallback to human
- User management section (users + agents, roles)
- RACI table with roles columns, checkboxes, Finalize/Change, audit log
- UX: back links, de-clutter, error/warning/help messages, spellcheck, enterprise polish

All prior features (Testing Command Center, entity selectors, engagement workspace, etc.) are included.
