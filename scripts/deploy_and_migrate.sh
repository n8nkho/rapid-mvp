#!/usr/bin/env bash
# Deploy backend to Railway, wait for health, then run migrations and smoke checks.
# Usage:
#   ADMIN_API_KEY=your-key ./scripts/deploy_and_migrate.sh
#   ADMIN_API_KEY=your-key API_URL=https://rapid-mvp-production.up.railway.app ./scripts/deploy_and_migrate.sh
# Optional: source .env first so ADMIN_API_KEY and API_URL are set:
#   set -a; [ -f .env ] && . .env; set +a; ./scripts/deploy_and_migrate.sh
#
# Deploy step: if Railway CLI is available and project is linked, runs `railway up`.
# Otherwise run `git push origin main` yourself and use SKIP_DEPLOY=1 to only wait + migrate.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Load .env if present (do not override already-set env)
if [ -f .env ]; then
  set -a
  # shellcheck source=/dev/null
  . .env
  set +a
fi

BASE="${API_URL:-https://rapid-mvp-production.up.railway.app}"
BASE="${BASE%/}"
case "$BASE" in
  */v1) BASE="${BASE%/v1}" ;;
esac
ADMIN_KEY="${ADMIN_API_KEY:-}"

# ---- Deploy ----
if [ "${SKIP_DEPLOY:-0}" != "1" ]; then
  if command -v railway >/dev/null 2>&1; then
    echo "Deploying to Railway (railway up)..."
    railway up
  else
    echo "Railway CLI not found. Push to main to trigger deploy, then run:"
    echo "  SKIP_DEPLOY=1 ADMIN_API_KEY=<key> ./scripts/deploy_and_migrate.sh"
    echo "Or install Railway CLI: npm i -g @railway/cli"
    exit 1
  fi
fi

# ---- Wait for health ----
echo "Waiting for $BASE/health (max 5 min)..."
MAX_ATTEMPTS=30
INTERVAL=10
for i in $(seq 1 "$MAX_ATTEMPTS"); do
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$BASE/health" 2>/dev/null || true)
  if [ "$HTTP" = "200" ]; then
    echo "  /health: 200"
    break
  fi
  if [ "$i" -eq "$MAX_ATTEMPTS" ]; then
    echo "  Timeout waiting for health (last HTTP: $HTTP). Run migrate manually:"
    echo "  ADMIN_API_KEY=<key> API_URL=$BASE ./scripts/post_deploy.sh"
    exit 1
  fi
  echo "  Attempt $i/$MAX_ATTEMPTS: $HTTP (retry in ${INTERVAL}s)"
  sleep "$INTERVAL"
done

# ---- Migrate + smoke checks ----
if [ -z "$ADMIN_KEY" ]; then
  echo "Set ADMIN_API_KEY to run migrate (e.g. ADMIN_API_KEY=your-key $0)"
  echo "Smoke check only..."
  API_URL="$BASE" ./scripts/post_deploy.sh
else
  API_URL="$BASE" ADMIN_API_KEY="$ADMIN_KEY" ./scripts/post_deploy.sh
fi
echo "Deploy and migrate done."
