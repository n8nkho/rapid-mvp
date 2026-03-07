# Deploy to Railway and Run Migration

## One-time setup

1. **Railway**
   - Connect the repo to Railway (GitHub → Railway → New Project from repo).
   - Set env vars in Railway dashboard: `SUPABASE_URL`, `SUPABASE_KEY`, optionally `DATABASE_URL`, `ANTHROPIC_API_KEY`, `CORS_ORIGINS`, `ADMIN_API_KEY`, `API_KEY`.
   - Production URL: `https://rapid-mvp-production.up.railway.app` (or your Railway URL).

2. **Railway CLI (optional, for deploy from machine)**
   - Install: `npm i -g @railway/cli`
   - In repo: `railway link` and select the project.
   - Then you can run `railway up` (or use the script below).

3. **Admin key for migrate**
   - Set `ADMIN_API_KEY` in Railway (so the app accepts migrate calls).
   - For running migrate from your machine, use the same value: set `ADMIN_API_KEY` in `.env` or pass it when running the script.

## Deploy + migrate (from this repo)

**Option A – Full flow (deploy then migrate)**

```bash
cd /path/to/rapid-mvp
# If you use .env for ADMIN_API_KEY:
set -a; [ -f .env ] && . .env; set +a
ADMIN_API_KEY=your-admin-key ./scripts/deploy_and_migrate.sh
```

- If Railway CLI is installed and the project is linked, this runs `railway up`, waits for `/health` (max 5 min), then runs migrations and smoke checks.
- If Railway CLI is not installed, the script exits with instructions: push to `main` yourself, then run with `SKIP_DEPLOY=1`.

**Option B – Only migrate (after you’ve already deployed)**

```bash
ADMIN_API_KEY=your-admin-key ./scripts/post_deploy.sh
```

Optional: set `API_URL` if the app is not at the default:

```bash
API_URL=https://rapid-mvp-production.up.railway.app ADMIN_API_KEY=your-key ./scripts/post_deploy.sh
```

**Option C – Deploy via Git only**

1. `git push origin main` (Railway deploys from `main`).
2. After deploy is live, run migrate:

   ```bash
   ADMIN_API_KEY=your-key ./scripts/post_deploy.sh
   ```

## What the scripts do

- **`scripts/deploy_and_migrate.sh`**: Runs `railway up` (if CLI available), waits for `$API_URL/health` to return 200, then calls `post_deploy.sh` with the same `API_URL` and `ADMIN_API_KEY`.
- **`scripts/post_deploy.sh`**: POSTs to `/v1/admin/migrate` with header `X-Admin-Key: $ADMIN_API_KEY`, then runs smoke checks (`/health`, optional audit-trail). Migrate does **not** require the general API key.

## Troubleshooting

- **401 on migrate**: Ensure `ADMIN_API_KEY` matches the value set in Railway and the value you pass (or put in `.env`).
- **Railway CLI not found**: Install with `npm i -g @railway/cli` or use Option B/C and run migrate after pushing.
- **Health timeout**: Railway may still be building; run migrate manually later: `ADMIN_API_KEY=your-key ./scripts/post_deploy.sh`.
