# RAPID fallback marker — 2026-03-07

**Tag (both repos):** `rapid-fallback-2026-03-07`

Use this if something goes wrong after implementing the **RAPID Test Agents / Testing Command Center** feature (from the “Create a specification for building an agent or ag” PDF).

## How to restore

**Backend (rapid-mvp):**
```bash
cd /path/to/rapid-mvp
git fetch --tags
git checkout rapid-fallback-2026-03-07
# Or create a branch from it: git checkout -b restore-fallback rapid-fallback-2026-03-07
```

**Frontend (rapid-ui):**
```bash
cd /path/to/rapid-ui
git fetch --tags
git checkout rapid-fallback-2026-03-07
```

Then redeploy (Railway for backend, Vercel for frontend) if you need the deployed state to match this fallback.

## What this fallback represents

State **before** adding:
- Testing Command Center UI (/testing-command-center)
- Backend testing API (GET /v1/testing/scenarios, POST /v1/testing/run)
- RAPID Test Agents spec doc and fallback marker

All prior features (engagement workspace, Client context, hyperlinked IDs, checkpoint 2026-03-057, etc.) are included.
