#!/usr/bin/env bash
# Post-deploy: run migrations then smoke checks.
# Usage: ADMIN_API_KEY=your-key [API_KEY=your-key] [API_URL=...] ./scripts/post_deploy.sh
# - ADMIN_API_KEY: required for migrate (X-Admin-Key). If API_KEY is unset, also used as X-API-Key for /v1.
# - API_KEY: optional; when set, used as X-API-Key for /v1 routes (production often uses same value as ADMIN_API_KEY).
# - API_URL: base URL without /v1 (default: https://rapid-mvp-production.up.railway.app).

set -e
BASE="${API_URL:-https://rapid-mvp-production.up.railway.app}"
BASE="${BASE%/}"
# Avoid double /v1 when API_URL already ends with /v1 (e.g. Railway or proxy)
case "$BASE" in
  */v1) BASE="${BASE%/v1}" ;;
esac
ADMIN_KEY="${ADMIN_API_KEY:-}"
API_KEY="${API_KEY:-$ADMIN_KEY}"
if [ -z "$ADMIN_KEY" ]; then
  echo "Set ADMIN_API_KEY to run migrate (e.g. ADMIN_API_KEY=rapid-admin-2026 $0)"
  echo "Skipping migrate; running smoke checks only."
else
  echo "Running migrate..."
  # /v1 routes require X-API-Key when API_KEY env is set on server; migrate also requires X-Admin-Key
  CURL_HEADERS=(-H "X-Admin-Key: $ADMIN_KEY" -H "Content-Type: application/json")
  [ -n "$API_KEY" ] && CURL_HEADERS+=(-H "X-API-Key: $API_KEY")
  HTTP=$(curl -s -o /tmp/migrate.json -w "%{http_code}" -X POST "$BASE/v1/admin/migrate" "${CURL_HEADERS[@]}")
  if [ "$HTTP" != "200" ]; then
    echo "Migrate returned HTTP $HTTP: $(cat /tmp/migrate.json)"
    echo "Tip: If 401, check ADMIN_API_KEY. If 404, ensure API_URL is correct (e.g. no /api prefix)."
    exit 1
  fi
  STATUS=$(python3 -c "import json; d=json.load(open('/tmp/migrate.json')); print(d.get('status',''))")
  MSG=$(python3 -c "import json; d=json.load(open('/tmp/migrate.json')); print(d.get('message',''))")
  if [ "$STATUS" = "ok" ]; then
    echo "Migrate OK: $MSG"
  else
    echo "Migrate: $MSG"
    if python3 -c "import json; d=json.load(open('/tmp/migrate.json')); exit(0 if d.get('sql') else 1)" 2>/dev/null; then
      python3 -c "import json; d=json.load(open('/tmp/migrate.json')); open('/tmp/rapid_migrate.sql','w').write(d.get('sql',''))"
      echo "  SQL saved to /tmp/rapid_migrate.sql — run it in Supabase SQL Editor (Dashboard → SQL Editor → New query → paste → Run)."
    fi
  fi
fi

echo "Smoke checks..."
# Health (no key)
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health")
if [ "$HTTP" != "200" ]; then echo "Health failed: $HTTP"; exit 1; fi
echo "  /health: 200"

# Audit trail (v1 routes require X-API-Key when API_KEY is set on server)
if [ -n "$API_KEY" ]; then
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" "$BASE/v1/engagement/ENG-016/audit-trail?limit=5")
  if [ "$HTTP" != "200" ]; then echo "  /v1/.../audit-trail: $HTTP"; exit 1; fi
  echo "  /v1/engagement/ENG-016/audit-trail: 200"
else
  echo "  (Set ADMIN_API_KEY or API_KEY to check audit-trail)"
fi
echo "Post-deploy checks done."
