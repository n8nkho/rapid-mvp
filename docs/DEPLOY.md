# Deploy Railway and run migration

This doc describes how to deploy the backend to Railway and run migrations so the agent (or a developer) can do it in one flow.

## Prerequisites

1. **Railway project** linked to this repo (e.g. `rapid-mvp` on GitHub). Railway deploys on push to the branch you configured.
2. **Admin key** — Set `ADMIN_API_KEY` in the Railway project (Dashboard → rapid-mvp → Variables). Use the same value when running migration locally so `post_deploy.sh` can call `/v1/admin/migrate`.
3. **Optional (for deploy from this machine):** [Railway CLI](https://docs.railway.app/develop/cli) — `npm i -g @railway/cli`, then in this repo run `railway link` and select the project.

## One-command deploy + migrate

From the **rapid-mvp** repo root:

```bash
ADMIN_API_KEY=your-admin-key ./scripts/deploy_and_migrate.sh
```

- If Railway CLI is installed and linked: runs `railway up`, waits for `https://rapid-mvp-production.up.railway.app/health` to return 200, then runs `scripts/post_deploy.sh` (migrate + smoke checks).
- If Railway CLI is not installed: script exits with instructions. You can deploy by pushing to `main`, then run:

  ```bash
  SKIP_DEPLOY=1 ADMIN_API_KEY=your-admin-key ./scripts/deploy_and_migrate.sh
  ```

## Env vars (optional .env)

Create a `.env` in the repo root (do **not** commit it; it’s in `.gitignore`):

```bash
ADMIN_API_KEY=your-admin-key
API_URL=https://rapid-mvp-production.up.railway.app
```

Then you can run:

```bash
./scripts/deploy_and_migrate.sh
```

without passing env on the command line.

## Migrate only (no deploy)

After a deploy is already live (e.g. from GitHub push):

```bash
ADMIN_API_KEY=your-admin-key ./scripts/post_deploy.sh
```

Or with custom API base:

```bash
API_URL=https://rapid-mvp-production.up.railway.app ADMIN_API_KEY=your-admin-key ./scripts/post_deploy.sh
```

## Script reference

| Script | Purpose |
|--------|--------|
| `scripts/deploy_and_migrate.sh` | Deploy (Railway CLI or git push), wait for health, then run migrate + smoke checks. |
| `scripts/post_deploy.sh` | Run `POST /v1/admin/migrate` (with `X-Admin-Key`) and smoke checks (`/health`, optional audit-trail). |

**Variables:**

- `ADMIN_API_KEY` — Required for migrate; send as `X-Admin-Key`.
- `API_URL` — Base URL without `/v1` (default: `https://rapid-mvp-production.up.railway.app`).
- `DEPLOY` — For `deploy_and_migrate.sh`: `railway` (default), `git`, or `none`.
- `WAIT_TIMEOUT` / `WAIT_INTERVAL` — Wait for health (default 300s timeout, 15s interval).
