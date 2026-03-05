# Seed Zero EV data for full engagement browser check

Use this to create **Zero EV Motors** client and engagement with synthetic requirements, fit-gap assessments, and platform issues so you can verify all built features in the UI.

## Prerequisites

- Backend deployed and reachable (e.g. Railway production or local).
- If the backend requires API key auth:
  - Have the same key set when running the script: `API_KEY=xxx`.
  - **Frontend (Vercel):** set **`NEXT_PUBLIC_API_KEY`** in the project environment to that same value and redeploy. Otherwise the UI will get 401 and show empty clients/engagements.
- Migrations applied (`POST /v1/admin/migrate` or `./scripts/post_deploy.sh`), so tables `agent_roles`, `platform_issues`, `audit_events`, `fit_gap_assessments`, etc. exist.

## 1. Run the simulation script

From the **rapid-mvp** repo:

```bash
cd /path/to/rapid-mvp

# Production (set API_KEY if your backend returns 401 without it)
export API_URL=https://rapid-mvp-production.up.railway.app/v1
export API_KEY=your_key_here   # omit if backend does not require auth
python3 scripts/run_zero_ev_simulation.py
```

For **local** backend (no auth):

```bash
export API_URL=http://localhost:8000/v1
python3 scripts/run_zero_ev_simulation.py
```

The script will:

- Create or reuse client **Zero EV Motors** and engagement **Cloud ERP Discovery & Fit-Gap**.
- Create ~100 synthetic requirements.
- Run fit-gap assessment on all of them (LLM calls; may take a few minutes).
- Create 3 platform issues (high/medium/low).

At the end it prints the **engagement_id** (e.g. `ENG-001`). Use that in the frontend.

## 2. Browser check URLs (production frontend)

- **Login:** https://rapid-ui-wine.vercel.app/login  
- **Home:** https://rapid-ui-wine.vercel.app/  
- **Clients & engagements:** https://rapid-ui-wine.vercel.app/clients  
  - Load the Zero EV engagement from the table or “Choose existing engagement”.
- **Engagement detail (replace `ENG-XXX` with printed id):**  
  https://rapid-ui-wine.vercel.app/engagement/ENG-XXX  
  - Requirements list, Audit trail, Benchmark insights, Actions (Capture, RACI, Gap Analysis, **Agent simulation**, **Platform backlog**).
- **Agent simulation (with engagement):**  
  https://rapid-ui-wine.vercel.app/simulate?engagement_id=ENG-XXX  
- **Platform backlog:**  
  https://rapid-ui-wine.vercel.app/platform-backlog?engagement_id=ENG-XXX  
- **Fit/Gap board:**  
  https://rapid-ui-wine.vercel.app/fitgap?engagement_id=ENG-XXX  

## 3. What to check

- **Engagement page:** Many requirements; summary; audit trail; links to Simulate and Platform backlog.
- **Simulate:** Select engagement + agent role, send message, see “Agent reply (draft)”.
- **Platform backlog:** Issues by priority (high/medium/low); Add issue, Start, Resolve.
- **Audit trail (on engagement):** Events for simulate and platform-issue actions (actor, action, time).
- **Fit/Gap:** Board by fit type; process view; review modal.

## Fallback

If you need to revert:  
- Backend: `git checkout rapid-fallback-pre-zero-ev-2026-03-04`  
- Frontend: `git checkout rapid-ui-fallback-pre-zero-ev-2026-03-04`
