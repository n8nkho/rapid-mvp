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
    **kwargs,
) -> dict:
    """Create a requirement record.

    SQL migration — run once in Supabase SQL editor to add Phase 1 columns:
        ALTER TABLE requirements
          ADD COLUMN IF NOT EXISTS business_process text,
          ADD COLUMN IF NOT EXISTS priority text DEFAULT 'Must-Have',
          ADD COLUMN IF NOT EXISTS category text,
          ADD COLUMN IF NOT EXISTS kpi_impact jsonb,
          ADD COLUMN IF NOT EXISTS confidence_score float DEFAULT 0.8,
          ADD COLUMN IF NOT EXISTS current_state_ref text,
          ADD COLUMN IF NOT EXISTS actors jsonb,
          ADD COLUMN IF NOT EXISTS shadow_tools text[],
          ADD COLUMN IF NOT EXISTS sign_off_status text DEFAULT 'draft',
          ADD COLUMN IF NOT EXISTS sign_off_by text,
          ADD COLUMN IF NOT EXISTS sign_off_at timestamptz,
          ADD COLUMN IF NOT EXISTS sap_mapping_id text,
          ADD COLUMN IF NOT EXISTS fit_assessment text;
    """
    req_id = _next_req_id(engagement_id)
    record = {
        "req_id": req_id,
        "engagement_id": engagement_id,
        "title": title,
        "description": description,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": kwargs.pop("tags", None) or [],
    }
    # Merge remaining kwargs; skip None values so Supabase uses column defaults
    record.update({k: v for k, v in kwargs.items() if v is not None})
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


def get_gap_results_by_req_id(req_id: str, engagement_id: str) -> list:
    response = (
        supabase.table("gap_results")
        .select("*")
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .order("timestamp", desc=True)
        .execute()
    )
    return response.data or []


def update_requirement(req_id: str, engagement_id: str, updates: dict) -> dict:
    response = (
        supabase.table("requirements")
        .update(updates)
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return response.data[0] if response.data else {}


# ── Clients ───────────────────────────────────────────────────────────────────

def _next_client_id() -> str:
    """Generate next sequential CLI-XXX id, globally unique."""
    response = supabase.table("clients").select("client_id").execute()
    existing = response.data or []
    nums = []
    for row in existing:
        try:
            nums.append(int(row["client_id"].split("-")[1]))
        except (IndexError, ValueError):
            pass
    return f"CLI-{max(nums, default=0) + 1:03d}"


def create_client(data: dict) -> dict:
    client_id = _next_client_id()
    record = {"client_id": client_id, **data}
    response = supabase.table("clients").insert(record).execute()
    return response.data[0] if response.data else {}


def get_client(client_id: str) -> dict:
    response = (
        supabase.table("clients")
        .select("*")
        .eq("client_id", client_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None


def list_clients() -> list:
    response = supabase.table("clients").select("*").order("client_id").execute()
    return response.data or []


# ── Engagements ───────────────────────────────────────────────────────────────

def _next_engagement_id() -> str:
    """Generate next sequential ENG-XXX id, globally unique."""
    response = supabase.table("engagements").select("engagement_id").execute()
    existing = response.data or []
    nums = []
    for row in existing:
        try:
            nums.append(int(row["engagement_id"].split("-")[1]))
        except (IndexError, ValueError):
            pass
    return f"ENG-{max(nums, default=0) + 1:03d}"


def create_engagement(data: dict) -> dict:
    engagement_id = _next_engagement_id()
    record = {
        "engagement_id": engagement_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **data,
    }
    response = supabase.table("engagements").insert(record).execute()
    return response.data[0] if response.data else {}


def get_engagement(engagement_id: str) -> dict:
    response = (
        supabase.table("engagements")
        .select("*")
        .eq("engagement_id", engagement_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None


def list_engagements(client_id: str = None) -> list:
    query = supabase.table("engagements").select("*").order("engagement_id")
    if client_id:
        query = query.eq("client_id", client_id)
    return query.execute().data or []


def get_engagement_with_client(engagement_id: str) -> dict:
    """Return engagement dict merged with its client as a 'client' key."""
    eng = get_engagement(engagement_id)
    if not eng:
        return None
    client_id = eng.get("client_id")
    client = get_client(client_id) if client_id else {}
    return {**eng, "client": client or {}}


# ── Assets ────────────────────────────────────────────────────────────────────

def _next_asset_id(engagement_id: str) -> str:
    """Generate next sequential AST-XXX id, unique within an engagement."""
    response = (
        supabase.table("assets")
        .select("asset_id")
        .eq("engagement_id", engagement_id)
        .execute()
    )
    existing = response.data or []
    nums = []
    for row in existing:
        try:
            nums.append(int(row["asset_id"].split("-")[1]))
        except (IndexError, ValueError):
            pass
    return f"AST-{max(nums, default=0) + 1:03d}"


def create_asset(data: dict) -> dict:
    engagement_id = data.get("engagement_id")
    asset_id = _next_asset_id(engagement_id)
    record = {"asset_id": asset_id, **data}
    response = supabase.table("assets").insert(record).execute()
    return response.data[0] if response.data else {}


def get_assets_by_engagement(engagement_id: str) -> list:
    response = (
        supabase.table("assets")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("asset_id")
        .execute()
    )
    return response.data or []


def get_assets_by_requirement(req_id: str, engagement_id: str) -> list:
    response = (
        supabase.table("assets")
        .select("*")
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .order("asset_id")
        .execute()
    )
    return response.data or []


def update_asset(asset_id: str, updates: dict) -> dict:
    response = (
        supabase.table("assets")
        .update(updates)
        .eq("asset_id", asset_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def upload_file_to_storage(
    engagement_id: str, asset_id: str, file_name: str, file_bytes: bytes, content_type: str
) -> str:
    """Upload file to rapid-assets Supabase Storage bucket and return the public URL."""
    path = f"{engagement_id}/{asset_id}/{file_name}"
    supabase.storage.from_("rapid-assets").upload(
        path, file_bytes, {"content-type": content_type}
    )
    return supabase.storage.from_("rapid-assets").get_public_url(path)
