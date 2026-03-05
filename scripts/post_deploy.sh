#!/usr/bin/env bash
# Post-deploy: run migrations then smoke checks.
# Usage: ADMIN_API_KEY=<your-key> [API_URL=https://rapid-mvp-production.up.railway.app] ./scripts/post_deploy.sh
# Set API_URL without /v1 (script appends /v1 for migrate and paths).

set -e
BASE="${API_URL:-https://rapid-mvp-production.up.railway.app}"
BASE="${BASE%/}"
API_KEY="${ADMIN_API_KEY:-}"
if [ -z "$API_KEY" ]; then
  echo "Set ADMIN_API_KEY to run migrate (e.g. ADMIN_API_KEY=xxx $0)"
  echo "Skipping migrate; running smoke checks only."
else
  echo "Running migrate..."
  HTTP=$(curl -s -o /tmp/migrate.json -w "%{http_code}" -X POST "$BASE/v1/admin/migrate" -H "X-Admin-Key: $API_KEY" -H "Content-Type: application/json")
  if [ "$HTTP" = "200" ]; then
    echo "Migrate OK: $(python3 -c "import json; d=json.load(open('/tmp/migrate.json')); print(d.get('message',''))")"
  else
    echo "Migrate returned HTTP $HTTP: $(cat /tmp/migrate.json)"
    exit 1
  fi
fi

echo "Smoke checks..."
# Health (no key)
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health")
if [ "$HTTP" != "200" ]; then echo "Health failed: $HTTP"; exit 1; fi
echo "  /health: 200"

# Audit trail (v1 routes require X-API-Key; use ADMIN_API_KEY if set)
if [ -n "$API_KEY" ]; then
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" "$BASE/v1/engagement/ENG-016/audit-trail?limit=5")
  if [ "$HTTP" != "200" ]; then echo "  /v1/.../audit-trail: $HTTP"; exit 1; fi
  echo "  /v1/engagement/ENG-016/audit-trail: 200"
else
  echo "  (Set ADMIN_API_KEY to run migrate and check audit-trail)"
fi
echo "Post-deploy checks done."
