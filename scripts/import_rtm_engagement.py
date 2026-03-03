#!/usr/bin/env python3
"""
Upload RAPID RTM Excel (e.g. RAPID_RTM_Acme_S4.xlsx) to populate requirements for an engagement.
Uses internal REQ-XXX ids and stores Excel Requirement ID in reference_id for audit trail.

Usage:
  python scripts/import_rtm_engagement.py ENG-001 /path/to/RAPID_RTM_Acme_S4.xlsx
  API_URL defaults to http://localhost:8000/v1; set env API_URL to override.
"""
import os
import sys
import httpx

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/import_rtm_engagement.py <engagement_id> <path_to.xlsx>", file=sys.stderr)
        sys.exit(1)
    engagement_id = sys.argv[1]
    path = sys.argv[2]
    if not os.path.isfile(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)
    api_url = os.getenv("API_URL", "http://localhost:8000/v1").rstrip("/")
    url = f"{api_url}/engagement/{engagement_id}/requirements/import"
    with open(path, "rb") as f:
        content = f.read()
    filename = os.path.basename(path)
    with httpx.Client(timeout=60.0) as client:
        r = client.post(url, files={"file": (filename, content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    if r.status_code != 200:
        print(f"Import failed: {r.status_code}", file=sys.stderr)
        print(r.text, file=sys.stderr)
        sys.exit(1)
    data = r.json()
    print(f"Format: {data.get('format', 'legacy')}")
    print(f"Created: {data.get('created', 0)}")
    print(f"Updated: {data.get('updated', 0)}")
    if data.get("created_req_ids"):
        print("Created req_ids:", data["created_req_ids"][:10], "..." if len(data["created_req_ids"]) > 10 else "")
    if data.get("errors"):
        print("Errors:", data["errors"])

if __name__ == "__main__":
    main()
