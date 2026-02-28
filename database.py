import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Gap Analysis ─────────────────────────────────────────────────────────────

def save_gap_analysis(
    engagement_id: str,
    process_description: str,
    matches: list,
    tokens_used: int = None,
    timestamp: str = None,
    req_id: str = None,
) -> dict:
    record = {
        "engagement_id": engagement_id,
        "process_description": process_description,
        "matches": matches,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
    }
    if tokens_used is not None:
        record["tokens_used"] = tokens_used
    if req_id is not None:
        record["req_id"] = req_id
    response = supabase.table("gap_results").insert(record).execute()
    return response.data[0] if response.data else {}


def get_results_by_engagement(engagement_id: str) -> list:
    response = (
        supabase.table("gap_results")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("timestamp", desc=True)
        .execute()
    )
    return response.data or []


# ── Requirements ─────────────────────────────────────────────────────────────

def _next_req_id(engagement_id: str) -> str:
    """Generate next sequential REQ-XXX id, unique within an engagement."""
    response = (
        supabase.table("requirements")
        .select("req_id")
        .eq("engagement_id", engagement_id)
        .execute()
    )
    existing = response.data or []
    nums = []
    for row in existing:
        try:
            nums.append(int(row["req_id"].split("-")[1]))
        except (IndexError, ValueError):
            pass
    return f"REQ-{max(nums, default=0) + 1:03d}"


def create_requirement(
    engagement_id: str,
    title: str,
    description: str,
    source_type: str = None,
    tags: list = None,
    stakeholder: str = None,
    raw_input: str = None,
) -> dict:
    req_id = _next_req_id(engagement_id)
    record = {
        "req_id": req_id,
        "engagement_id": engagement_id,
        "title": title,
        "description": description,
        "source_type": source_type,
        "tags": tags or [],
        "stakeholder": stakeholder,
        "raw_input": raw_input,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    response = supabase.table("requirements").insert(record).execute()
    return response.data[0] if response.data else {}


def get_requirements_by_engagement(engagement_id: str) -> list:
    response = (
        supabase.table("requirements")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("req_id")
        .execute()
    )
    return response.data or []


def get_requirement_by_id(req_id: str, engagement_id: str) -> dict:
    response = (
        supabase.table("requirements")
        .select("*")
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None


def update_requirement(req_id: str, engagement_id: str, updates: dict) -> dict:
    response = (
        supabase.table("requirements")
        .update(updates)
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return response.data[0] if response.data else {}
