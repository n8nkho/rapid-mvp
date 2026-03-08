# RAPID fallback marker — 2026-03-09

**Tag (both repos):** `rapid-fallback-2026-03-09`

Use this to restore state **before** the UX & feature batch: Flow 401 fix, asset upload linked to requirement, Create requirement in capture, Client/Engagement defaults and header, stacked Create Client/Engagement tabs, responsive scaling, dashboard filter, scope L1–L3 side-by-side, requirements expand/collapse, L2/L3 in capture, display client all fields, template download/upload with agent, and related improvements.

## How to restore

**Backend (rapid-mvp):**
```bash
cd /path/to/rapid-mvp
git fetch --tags
git checkout rapid-fallback-2026-03-09
```

**Frontend (rapid-ui):**
```bash
cd /path/to/rapid-ui
git fetch --tags
git checkout rapid-fallback-2026-03-09
```

Then redeploy (Railway backend, Vercel frontend) if needed.

## What this fallback represents

State after Fix Round 3 (fit/gap board, assets table, seed dedup, sign-off labels, next actions count) and before the 2026-03-09 improvement batch:

- Generate Flow 401 fixed (X-API-Key on flow page)
- Asset upload: req_id required in UI; PATCH assets by string asset_id (AST-001)
- Capture: Create requirement button; L2/L3 process hierarchy; all capture tagged to requirement
- Working engagement: Client dropdown default to engagement’s client; header shows “Working in: Client ID · Engagement ID · Name”
- Create Client / Create Engagement as stacked tabs on Clients page
- Responsive layout; engagement dashboard Client–Engagement filter and keyword search
- Scope: L1–L3 side-by-side; no layout shift on check/uncheck
- Requirements list: expand/collapse and filters
- Display client: all Create Client fields shown
- Template: download Excel (Single Requirement fields + Source requirement ID), upload with agent fix and user confirm

All prior features (sources, fit-gap, HITL, RICEFW, Testing Command Center, entity selectors, etc.) are included.
