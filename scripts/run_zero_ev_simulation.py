#!/usr/bin/env python3
"""
Phase 2 simulation: Create or use "Zero EV Motors" client/engagement, seed synthetic
requirements (80-150), run fit-gap on a subset to get 20-30 gaps, log platform issues.
Uses RAPID API; set API_URL and optionally API_KEY.

Usage:
  python scripts/run_zero_ev_simulation.py [--dry-run]
  API_URL=http://localhost:8000/v1 API_KEY=xxx python scripts/run_zero_ev_simulation.py
"""
import os
import sys
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

# Max concurrent fit-gap-assess calls (LLM); keep modest to avoid rate limits
FIT_GAP_WORKERS = 6

API_URL = os.getenv("API_URL", "http://localhost:8000/v1").rstrip("/")
API_KEY = os.getenv("API_KEY")
HEADERS = {}
if API_KEY:
    HEADERS["X-API-Key"] = API_KEY

ZERO_CLIENT_NAME = "Zero EV Motors"
ZERO_ENGAGEMENT_NAME = "Cloud ERP Discovery & Fit-Gap"

# Synthetic requirements by domain (title, description, business_process) — subset to reach ~100+
REQ_SEED = [
    # Manufacturing
    ("BOM multi-level for EV powertrain", "Support multi-level BOMs for battery pack and motor assemblies with variant configuration.", "Manufacturing"),
    ("Routing by work center and capacity", "Routings must respect work center capacity and shift calendars.", "Manufacturing"),
    ("Production order rework and scrap", "Capture rework and scrap at operation level with reason codes.", "Manufacturing"),
    ("Quality inspection at key operations", "Quality checks at incoming, in-process, and final assembly with hold/release.", "Manufacturing"),
    ("Engineering change impact on BOM", "ECN must propagate to BOM and trigger revision where applicable.", "Manufacturing"),
    ("Long lead battery procurement", "Planning must account for battery lead times (12+ weeks) and safety stock.", "Manufacturing"),
    ("Work center scheduling and PM", "Preventive maintenance windows per work center; schedule production around them.", "Manufacturing"),
    ("Serialization for battery and vehicle", "End-to-end serialization for battery and finished vehicle for warranty and recall.", "Manufacturing"),
    ("Make-to-order with configurable BOM", "MTO flow with configurable BOM and option-dependent components.", "Manufacturing"),
    ("Shop floor data collection", "Capture actual times and quantities at operation level from MES or manual.", "Manufacturing"),
    # Supply Chain
    ("Demand planning for EV and parts", "Demand plan at product family and component level; consensus with sales.", "Supply Chain"),
    ("Safety stock and reorder points", "Dynamic safety stock and reorder points by item and location.", "Supply Chain"),
    ("VMI for key suppliers", "Vendor-managed inventory for selected raw materials with min/max and replenishment.", "Supply Chain"),
    ("3PL outbound and tracking", "Outbound shipments via 3PL with ASN and tracking integration.", "Supply Chain"),
    ("Multi-plant stock transfer", "Inter-plant stock transfer with cost and lead time.", "Supply Chain"),
    ("OTIF and fill rate reporting", "On-time in-full and fill rate by customer and product.", "Supply Chain"),
    ("Purchase order approval workflow", "Multi-level PO approval by value and category.", "Supply Chain"),
    ("Supplier quality and incoming inspection", "Link PO to quality inspection and non-conformance.", "Supply Chain"),
    ("Warehouse bin and lot control", "Bin and lot control in warehouse; FIFO and expiry where applicable.", "Supply Chain"),
    ("Demand sensing and short-term forecast", "Short-term demand sensing from orders and channel data.", "Supply Chain"),
    # Finance
    ("Multi-currency and valuation", "Multi-currency transactions and period-end valuation (P&L and balance sheet).", "Finance"),
    ("Revenue recognition by milestone", "Revenue recognition for MTO/special orders by milestone or delivery.", "Finance"),
    ("Product costing and variance", "Standard costing with variance analysis; support by order or period.", "Finance"),
    ("Period close and reconciliation", "Period close with subledger reconciliation and audit trail.", "Finance"),
    ("Management reporting and profitability", "Profitability by product, customer, region; management pack.", "Finance"),
    ("Intercompany and eliminations", "Intercompany transactions and elimination entries.", "Finance"),
    ("Tax engine integration", "Integrate with tax engine for sales and use tax.", "Finance"),
    ("Fixed assets and depreciation", "Fixed asset register and depreciation by book.", "Finance"),
    ("Bank reconciliation and cash", "Bank statement import and reconciliation; cash positioning.", "Finance"),
    ("Multi-GAAP and statutory", "Support multiple GAAP and statutory reporting requirements.", "Finance"),
    # Quality
    ("NCR and CAPA", "Non-conformance and corrective action with root cause and closure.", "Quality"),
    ("Calibration and equipment", "Calibration schedule and records for measuring equipment.", "Quality"),
    ("Supplier quality scorecard", "Scorecard for supplier quality and delivery.", "Quality"),
    ("Audit trail for quality records", "Full audit trail for quality inspections and releases.", "Quality"),
    ("Regulatory and certification", "Support for regulatory and certification reporting (e.g. EV/safety).", "Quality"),
    # Service
    ("Warranty and returns", "Warranty registration and returns (RMA) with repair or replace.", "Service"),
    ("Field service and parts", "Field service orders and parts consumption.", "Service"),
    ("Spare parts planning", "Spare parts demand and replenishment.", "Service"),
    ("Service revenue and contracts", "Service contracts and revenue recognition.", "Service"),
    # Analytics / R2R
    ("Operational dashboards", "Real-time dashboards for production, quality, and delivery.", "Analytics"),
    ("Financial close analytics", "Analytics for close timeline and variance drivers.", "Analytics"),
    ("Supply chain visibility", "End-to-end visibility for inventory and orders.", "Analytics"),
]

# More to reach ~100 (duplicate domains with variations)
EXTRA_REQS = []
for i in range(1, 4):
    for title, desc, proc in REQ_SEED[:15]:
        EXTRA_REQS.append((f"{title} (variant {i})", desc + f" Variant {i}.", proc))
REQ_SEED_EXTENDED = REQ_SEED + EXTRA_REQS[:55]  # ~100 total


def get(path: str) -> dict:
    with httpx.Client(timeout=30.0) as c:
        r = c.get(API_URL + path, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def post(path: str, json_body: dict = None) -> dict:
    with httpx.Client(timeout=60.0) as c:
        r = c.post(API_URL + path, json=json_body or {}, headers=HEADERS)
    r.raise_for_status()
    return r.json() if r.content else {}


def patch(path: str, json_body: dict) -> dict:
    with httpx.Client(timeout=30.0) as c:
        r = c.patch(API_URL + path, json=json_body, headers=HEADERS)
    r.raise_for_status()
    return r.json() if r.content else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Only print planned actions")
    args = ap.parse_args()
    dry = args.dry_run

    if dry:
        print("DRY RUN: would create client, engagement, requirements, fit-gap, platform issues")
        print("Requirements to create:", len(REQ_SEED_EXTENDED))
        return

    # 1) Resolve or create client
    # /v1/clients returns {"clients": [...]}; use business key client_id (CLI-XXX), not row id.
    clients = get("/clients").get("clients") or []
    client_id = None
    for c in clients:
        if (c.get("name") or "").strip() == ZERO_CLIENT_NAME:
            client_id = c.get("client_id")
            print(f"Using existing client: {ZERO_CLIENT_NAME} ({client_id})")
            break
    if not client_id:
        body = {
            "name": ZERO_CLIENT_NAME,
            "industry": "EV / Discrete Manufacturing",
            "employees": 1200,
            "website": "https://zeroevmotors.example.com",
            "regulatory_environment": ["EV safety", "Battery compliance", "Multi-country"],
            "sector_archetype": "ev_discrete_manufacturing",
        }
        out = post("/clients", body)
        client_id = out.get("client_id")
        print(f"Created client: {ZERO_CLIENT_NAME} ({client_id})")

    # 2) Resolve or create engagement
    # /v1/engagements returns {"items": [...]}; link via engagement_id and client_id.
    engagements = get("/engagements").get("items") or []
    engagement_id = None
    for e in engagements:
        if e.get("client_id") == client_id and (e.get("name") or "").strip() == ZERO_ENGAGEMENT_NAME:
            engagement_id = e.get("engagement_id")
            print(f"Using existing engagement: {ZERO_ENGAGEMENT_NAME} ({engagement_id})")
            break
    if not engagement_id:
        out = post("/engagements", {"client_id": client_id, "name": ZERO_ENGAGEMENT_NAME})
        engagement_id = out.get("engagement_id")
        print(f"Created engagement: {ZERO_ENGAGEMENT_NAME} ({engagement_id})")

    # 3) Create requirements (up to ~100)
    created_reqs = 0
    req_ids = []
    for title, description, business_process in REQ_SEED_EXTENDED:
        try:
            out = post("/requirements", {
                "engagement_id": engagement_id,
                "title": title,
                "description": description,
                "business_process": business_process,
                "priority": "Must-Have" if created_reqs % 3 == 0 else "Should-Have",
            })
            rid = out.get("req_id")
            if rid:
                req_ids.append(rid)
                created_reqs += 1
        except Exception as e:
            print(f"Requirement create failed: {e}")
    print(f"Created {created_reqs} requirements")

    # 4) Run fit-gap on all requirements (parallel for speed; sequential would be 87 * ~2s)
    def _assess_one(rid: str):
        try:
            out = post(f"/requirements/{rid}/fit-gap-assess?engagement_id={engagement_id}")
            return (True, (out.get("fit_type") or "").startswith("gap"))
        except Exception as e:
            return (False, e)

    assessed = 0
    gap_count = 0
    first_fit_gap_error = None
    with ThreadPoolExecutor(max_workers=FIT_GAP_WORKERS) as ex:
        futures = {ex.submit(_assess_one, rid): rid for rid in req_ids}
        for fut in as_completed(futures):
            ok, val = fut.result()
            if ok:
                assessed += 1
                if val:
                    gap_count += 1
            elif first_fit_gap_error is None:
                first_fit_gap_error = val
    if first_fit_gap_error is not None and assessed == 0:
        print(f"Fit-gap note: all assess calls failed; first error: {first_fit_gap_error}")
    print(f"Fit-gap assessed: {assessed}; gap-type assessments: {gap_count}")

    # 5) Log a few platform issues
    for problem, improvement, priority in [
        ("Process hierarchy only to level 3; need level 4 for manufacturing.", "Add process_level_4 and hierarchy UI.", "medium"),
        ("No bulk fit-gap re-run when scope items change.", "Add 'Re-analyse all' with cache invalidation.", "low"),
        ("Agent simulation could not map requirement to test case.", "Add test_case_id to requirement and RTM view.", "high"),
    ]:
        try:
            post("/platform-issues", {
                "engagement_id": engagement_id,
                "agent_role_id": "ba",
                "phase": "requirements",
                "problem_description": problem,
                "suggested_improvement": improvement,
                "priority": priority,
                "issue_type": "missing_feature",
            })
        except Exception as e:
            print("Platform issue create failed:", e)
    print("Platform issues created (see GET /platform-issues or /engagement/{id}/platform-backlog)")

    print("\n--- Simulation summary ---")
    print(f"Engagement ID: {engagement_id}")
    print(f"Requirements: {created_reqs}")
    print(f"Fit-gap assessed: {assessed}; gaps: {gap_count}")
    print(f"Backend: {API_URL}")
    print("Check in browser: engagement dashboard, requirements list, fit-gap board, platform backlog.")


if __name__ == "__main__":
    main()
