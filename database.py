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


def get_results_by_engagement(engagement_id: str, limit: int = 200) -> list:
    """Return gap results for engagement, newest first. Capped to avoid slow timeouts."""
    response = (
        supabase.table("gap_results")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


# ── Requirements & HITL ─────────────────────────────────────────────────────

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

    SQL migration — Sprint 5 process flow columns:
        ALTER TABLE requirements
          ADD COLUMN IF NOT EXISTS process_level_2 text,
          ADD COLUMN IF NOT EXISTS process_level_3 text;
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


def _next_hitl_event_id(engagement_id: str) -> str:
    """Generate next sequential HEV-XXX id, scoped per engagement."""
    response = (
        supabase.table("hitl_events")
        .select("event_id")
        .eq("engagement_id", engagement_id)
        .execute()
    )
    existing = response.data or []
    nums = []
    for row in existing:
        event_id = row.get("event_id") or ""
        if isinstance(event_id, str) and event_id.startswith("HEV-"):
            try:
                nums.append(int(event_id.split("-")[1]))
            except (IndexError, ValueError):
                pass
    return f"HEV-{max(nums, default=0) + 1:03d}"


def create_hitl_event(data: dict) -> dict:
    """Insert a HITL event; generates event_id if missing."""
    engagement_id = data.get("engagement_id")
    if not engagement_id:
        raise ValueError("engagement_id is required for HITL events")
    if not data.get("event_id"):
        data = {**data, "event_id": _next_hitl_event_id(engagement_id)}
    response = supabase.table("hitl_events").insert(data).execute()
    return response.data[0] if response.data else {}


def list_hitl_events(engagement_id: str) -> list:
    """Return HITL events for an engagement, newest first."""
    response = (
        supabase.table("hitl_events")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


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


def update_client(client_id: str, updates: dict) -> dict:
    """Update client by client_id. Returns updated row or {}."""
    response = (
        supabase.table("clients")
        .update(updates)
        .eq("client_id", client_id)
        .execute()
    )
    return response.data[0] if response.data else {}


# ── Benchmark hints (Phase E) ─────────────────────────────────────────────────

def get_benchmark_hints_by_engagement(engagement_id: str) -> list:
    response = (
        supabase.table("benchmark_hints")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def create_benchmark_hint(engagement_id: str, category: str, title: str, content: str) -> dict:
    record = {
        "engagement_id": engagement_id,
        "category": category or "general",
        "title": title,
        "content": content,
    }
    response = supabase.table("benchmark_hints").insert(record).execute()
    return response.data[0] if response.data else {}


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
    import logging as _logging
    _log = _logging.getLogger("rapid")
    response = (
        supabase.table("engagements")
        .select("*")
        .eq("engagement_id", engagement_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    if data:
        _log.warning("get_engagement keys: %s", sorted(data[0].keys()))
    return data[0] if data else None


def list_engagements(client_id: str = None) -> list:
    query = supabase.table("engagements").select("*").order("engagement_id")
    if client_id:
        query = query.eq("client_id", client_id)
    return query.execute().data or []


def update_engagement(engagement_id: str, updates: dict) -> dict:
    """Update engagement by engagement_id. Returns updated row or {}."""
    updates = {k: v for k, v in updates.items() if v is not None}
    if not updates:
        return get_engagement(engagement_id) or {}
    response = (
        supabase.table("engagements")
        .update(updates)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_engagement(engagement_id: str) -> bool:
    """Delete a single engagement. Returns True if deleted."""
    response = (
        supabase.table("engagements")
        .delete()
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return bool(response.data)


def delete_client(client_id: str) -> bool:
    """Delete a single client. Fails if engagements still reference it (FK)."""
    response = (
        supabase.table("clients")
        .delete()
        .eq("client_id", client_id)
        .execute()
    )
    return bool(response.data)


def get_engagement_with_client(engagement_id: str) -> dict:
    """Return engagement dict merged with its client as a 'client' key and client_name at top level."""
    eng = get_engagement(engagement_id)
    if not eng:
        return None
    client_id = eng.get("client_id")
    client = get_client(client_id) if client_id else {}
    client_name = (client or {}).get("name") if client else None
    return {**eng, "client": client or {}, "client_name": client_name}


# ── Sources (enterprise multi-source capture) ───────────────────────────────────

def _next_source_id() -> str:
    """Generate next sequential source_id (SRC-001) globally."""
    response = supabase.table("sources").select("source_id").execute()
    existing = response.data or []
    nums = []
    for row in existing:
        try:
            sid = row.get("source_id") or ""
            if sid.startswith("SRC-"):
                nums.append(int(sid.replace("SRC-", "").strip()))
        except (ValueError, AttributeError):
            pass
    return f"SRC-{max(nums, default=0) + 1:03d}"


def create_source(engagement_id: str, source_type: str, title: str, **kwargs) -> dict:
    """Create a source record. source_type: transcript|notes|excel|document|workshop."""
    source_id = _next_source_id()
    record = {
        "source_id": source_id,
        "engagement_id": engagement_id,
        "source_type": source_type,
        "title": title or "Untitled",
        "status": kwargs.get("status", "uploaded"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    for k in ("raw_content", "file_url", "file_name", "extracted_count", "created_by"):
        if kwargs.get(k) is not None:
            record[k] = kwargs[k]
    response = supabase.table("sources").insert(record).execute()
    return response.data[0] if response.data else {}


def get_source(source_id: str, engagement_id: str) -> dict:
    response = (
        supabase.table("sources")
        .select("*")
        .eq("source_id", source_id)
        .eq("engagement_id", engagement_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None


def list_sources_by_engagement(engagement_id: str) -> list:
    response = (
        supabase.table("sources")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def update_source(source_id: str, engagement_id: str, updates: dict) -> dict:
    updates = {k: v for k, v in updates.items() if v is not None}
    if not updates:
        return get_source(source_id, engagement_id) or {}
    response = (
        supabase.table("sources")
        .update(updates)
        .eq("source_id", source_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_source(source_id: str, engagement_id: str) -> bool:
    response = (
        supabase.table("sources")
        .delete()
        .eq("source_id", source_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return bool(response.data)


# ── Test Scripts ────────────────────────────────────────────────────────────────

def create_test_script(data: dict) -> dict:
    response = supabase.table("test_scripts").insert(data).execute()
    return response.data[0] if response.data else {}


def list_test_scripts_by_engagement(engagement_id: str) -> list:
    response = (
        supabase.table("test_scripts")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def list_test_scripts_by_ricefw(engagement_id: str, ricefw_id: str) -> list:
    response = (
        supabase.table("test_scripts")
        .select("*")
        .eq("engagement_id", engagement_id)
        .eq("ricefw_id", ricefw_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


# ── Assets ────────────────────────────────────────────────────────────────────

def _next_asset_id(engagement_id: str) -> str:
    """Generate next sequential AST-XXX id, globally unique across all engagements."""
    response = (
        supabase.table("assets")
        .select("asset_id")
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
    """Upload file to rapid-assets Supabase Storage bucket and return the public URL.
    Auto-creates the bucket if it does not exist."""
    bucket = "rapid-assets"
    path = f"{engagement_id}/{asset_id}/{file_name}"
    try:
        supabase.storage.from_(bucket).upload(
            path, file_bytes, {"content-type": content_type}
        )
    except Exception:
        # Bucket may not exist — attempt to create it (public) then retry
        try:
            supabase.storage.create_bucket(bucket, options={"public": True})
        except Exception:
            pass  # Already exists or can't create — let the retry surface the real error
        supabase.storage.from_(bucket).upload(
            path, file_bytes, {"content-type": content_type}
        )
    return supabase.storage.from_(bucket).get_public_url(path)


# ── Process Steps ─────────────────────────────────────────────────────────────
#
# SQL migration — run once in Supabase SQL editor:
#
#   CREATE TABLE IF NOT EXISTS process_steps (
#     id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
#     req_id          text NOT NULL,
#     engagement_id   text NOT NULL,
#     step_number     int NOT NULL DEFAULT 1,
#     title           text NOT NULL,
#     description     text,
#     performer_name  text,
#     performer_role  text,
#     shape           text DEFAULT 'process',
#     step_type       text DEFAULT 'manual',
#     duration_minutes float,
#     systems_used    text[],
#     kpis            jsonb,
#     is_pain_point   boolean DEFAULT false,
#     next_step_id    text,
#     branches        jsonb,
#     created_at      timestamptz DEFAULT now(),
#     updated_at      timestamptz DEFAULT now()
#   );
#   CREATE INDEX IF NOT EXISTS idx_process_steps_req ON process_steps (req_id, engagement_id);

import uuid as _uuid_module


def create_process_step(data: dict) -> dict:
    """Insert a new process step. data must include req_id and engagement_id."""
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": str(_uuid_module.uuid4()),
        "created_at": now,
        "updated_at": now,
        **data,
    }
    response = supabase.table("process_steps").insert(record).execute()
    return response.data[0] if response.data else {}


def get_process_steps(req_id: str, engagement_id: str) -> list:
    response = (
        supabase.table("process_steps")
        .select("*")
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .order("step_number")
        .execute()
    )
    return response.data or []


def get_process_step(step_id: str, req_id: str, engagement_id: str) -> dict:
    response = (
        supabase.table("process_steps")
        .select("*")
        .eq("id", step_id)
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None


def update_process_step(step_id: str, req_id: str, engagement_id: str, updates: dict) -> dict:
    updates = {**updates, "updated_at": datetime.now(timezone.utc).isoformat()}
    response = (
        supabase.table("process_steps")
        .update(updates)
        .eq("id", step_id)
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_process_step(step_id: str, req_id: str, engagement_id: str) -> bool:
    response = (
        supabase.table("process_steps")
        .delete()
        .eq("id", step_id)
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return bool(response.data)


def get_process_steps_by_engagement(engagement_id: str) -> list:
    """Return all process steps for an engagement (used for seed check)."""
    response = (
        supabase.table("process_steps")
        .select("req_id")
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return response.data or []


# ── RICEFW Customisation Inventory (Sprint 7) ──────────────────────────────────
#
# SQL migration — run once in Supabase SQL editor:
#
#   CREATE TABLE IF NOT EXISTS ricefw_inventory (
#     id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
#     engagement_id   text NOT NULL,
#     req_id          text,
#     type            text NOT NULL,
#     name            text NOT NULL,
#     description     text,
#     status          text DEFAULT 'identified',
#     created_at      timestamptz DEFAULT now(),
#     updated_at      timestamptz DEFAULT now()
#   );
#   CREATE INDEX IF NOT EXISTS idx_ricefw_engagement ON ricefw_inventory (engagement_id);
#   CREATE INDEX IF NOT EXISTS idx_ricefw_type ON ricefw_inventory (engagement_id, type);


import uuid as _uuid_module


def create_ricefw_item(
    engagement_id: str,
    item_type: str,
    name: str,
    req_id: str,
    description: str,
    status: str = "identified",
    complexity: str = None,
    priority: str = None,
    effort_days_low: int = None,
    effort_days_high: int = None,
    owner: str = None,
) -> dict:
    """item_type: R | I | C | E | F | W | A. req_id and description are required."""
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": str(_uuid_module.uuid4()),
        "engagement_id": engagement_id,
        "type": item_type,
        "name": name,
        "description": description or "",
        "req_id": req_id,
        "status": status,
        "created_at": now,
        "updated_at": now,
    }
    if complexity is not None:
        record["complexity"] = complexity
    if priority is not None:
        record["priority"] = priority
    if effort_days_low is not None:
        record["effort_days_low"] = effort_days_low
    if effort_days_high is not None:
        record["effort_days_high"] = effort_days_high
    if owner is not None:
        record["owner"] = owner
    response = supabase.table("ricefw_inventory").insert(record).execute()
    return response.data[0] if response.data else {}


def get_ricefw_by_engagement(engagement_id: str, item_type: str = None) -> list:
    query = supabase.table("ricefw_inventory").select("*").eq("engagement_id", engagement_id).order("type").order("name")
    if item_type:
        query = query.eq("type", item_type)
    return query.execute().data or []


def update_ricefw_item(item_id: str, engagement_id: str, updates: dict) -> dict:
    updates = {**updates, "updated_at": datetime.now(timezone.utc).isoformat()}
    response = (
        supabase.table("ricefw_inventory")
        .update(updates)
        .eq("id", item_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_ricefw_item(item_id: str, engagement_id: str) -> bool:
    response = (
        supabase.table("ricefw_inventory")
        .delete()
        .eq("id", item_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return bool(response.data)


# ── Fit/Gap Assessments (Phase B) ───────────────────────────────────────────────

def _next_fga_id(engagement_id: str) -> str:
    """Generate next FGA-XXX id per engagement."""
    response = (
        supabase.table("fit_gap_assessments")
        .select("assessment_id")
        .execute()
    )
    existing = response.data or []
    nums = []
    for row in existing:
        aid = row.get("assessment_id") or ""
        if isinstance(aid, str) and aid.startswith("FGA-"):
            try:
                nums.append(int(aid.split("-")[1]))
            except (IndexError, ValueError):
                pass
    return f"FGA-{max(nums, default=0) + 1:03d}"


def create_fit_gap_assessment(data: dict) -> dict:
    """Insert a fit/gap assessment. data must include engagement_id, req_id, fit_type, complexity."""
    engagement_id = data.get("engagement_id")
    if not data.get("assessment_id"):
        data = {**data, "assessment_id": _next_fga_id(engagement_id)}
    response = supabase.table("fit_gap_assessments").insert(data).execute()
    return response.data[0] if response.data else {}


def get_fit_gap_by_engagement(engagement_id: str) -> list:
    response = (
        supabase.table("fit_gap_assessments")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("assessment_id")
        .execute()
    )
    return response.data or []


def get_fit_gap_by_assessment_id(assessment_id: str, engagement_id: str) -> dict:
    response = (
        supabase.table("fit_gap_assessments")
        .select("*")
        .eq("assessment_id", assessment_id)
        .eq("engagement_id", engagement_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None


def update_fit_gap_assessment(assessment_id: str, engagement_id: str, updates: dict) -> dict:
    response = (
        supabase.table("fit_gap_assessments")
        .update(updates)
        .eq("assessment_id", assessment_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_fit_gap_assessment(assessment_id: str, engagement_id: str) -> bool:
    """Delete a fit-gap assessment. Caller must verify no linked RICEFW first."""
    response = (
        supabase.table("fit_gap_assessments")
        .delete()
        .eq("assessment_id", assessment_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return bool(response.data)


def delete_requirement(req_id: str, engagement_id: str) -> bool:
    """Delete requirement and cascade: process_steps, gap_results, fit_gap_assessments, hitl_events.
    Caller must verify no approved FGA and no linked RICEFW first."""
    for table, col in [
        ("process_steps", "req_id"),
        ("gap_results", "req_id"),
        ("fit_gap_assessments", "req_id"),
        ("hitl_events", "req_id"),
    ]:
        try:
            supabase.table(table).delete().eq(col, req_id).eq("engagement_id", engagement_id).execute()
        except Exception:
            pass
    response = (
        supabase.table("requirements")
        .delete()
        .eq("req_id", req_id)
        .eq("engagement_id", engagement_id)
        .execute()
    )
    return bool(response.data)


# ── Feedback & Pattern Library (Phase D) ────────────────────────────────────

def create_feedback_event(engagement_id: str = None, event_type: str = "", payload: dict = None) -> dict:
    record = {
        "event_type": event_type or "general",
        "payload": payload or {},
    }
    if engagement_id:
        record["engagement_id"] = engagement_id
    response = supabase.table("feedback_events").insert(record).execute()
    return response.data[0] if response.data else {}


def list_feedback_events(engagement_id: str = None, limit: int = 50) -> list:
    query = supabase.table("feedback_events").select("*").order("created_at", desc=True).limit(limit)
    if engagement_id:
        query = query.eq("engagement_id", engagement_id)
    return query.execute().data or []


def get_pattern_library(limit: int = 50) -> list:
    response = (
        supabase.table("pattern_library")
        .select("*")
        .order("use_count", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


def increment_pattern_use(pattern_id: str) -> None:
    """Increment use_count for a pattern. No-op if pattern not found."""
    try:
        row = supabase.table("pattern_library").select("use_count").eq("id", pattern_id).limit(1).execute()
        if not row.data or len(row.data) == 0:
            return
        current = row.data[0].get("use_count") or 0
        supabase.table("pattern_library").update({"use_count": current + 1}).eq("id", pattern_id).execute()
    except Exception:
        pass


# ── Agent Team & Simulation ─────────────────────────────────────────────────

def list_agent_roles() -> list:
    response = supabase.table("agent_roles").select("*").order("role_id").execute()
    return response.data or []


def get_agent_role_by_role_id(role_id: str) -> dict:
    response = supabase.table("agent_roles").select("*").eq("role_id", role_id).limit(1).execute()
    data = response.data or []
    return data[0] if data else None


def get_agent_knowledge_by_role(role_id: str = None, limit: int = 50) -> list:
    query = supabase.table("agent_knowledge").select("*").order("category").limit(limit)
    if role_id:
        query = query.eq("role_id", role_id)
    return query.execute().data or []


def create_agent_maturity_score(role_id: str, criterion: str, score: int, notes: str = None) -> dict:
    record = {"role_id": role_id, "criterion": criterion, "score": max(1, min(5, score)), "notes": notes or ""}
    response = supabase.table("agent_maturity_scores").insert(record).execute()
    return response.data[0] if response.data else {}


def get_agent_maturity_scores(role_id: str = None, limit: int = 100) -> list:
    query = supabase.table("agent_maturity_scores").select("*").order("assessed_at", desc=True).limit(limit)
    if role_id:
        query = query.eq("role_id", role_id)
    return query.execute().data or []


def create_platform_issue(data: dict) -> dict:
    record = {
        "engagement_id": data.get("engagement_id", ""),
        "agent_role_id": data.get("agent_role_id"),
        "phase": data.get("phase", "requirements"),
        "context": data.get("context", {}),
        "problem_description": data.get("problem_description", ""),
        "issue_type": data.get("issue_type", "missing_feature"),
        "suggested_improvement": data.get("suggested_improvement", ""),
        "priority": data.get("priority", "medium"),
        "status": data.get("status", "open"),
    }
    response = supabase.table("platform_issues").insert(record).execute()
    return response.data[0] if response.data else {}


def list_platform_issues(engagement_id: str = None, priority: str = None, status: str = None, limit: int = 200) -> list:
    query = supabase.table("platform_issues").select("*").order("created_at", desc=True).limit(limit)
    if engagement_id:
        query = query.eq("engagement_id", engagement_id)
    if priority:
        query = query.eq("priority", priority)
    if status:
        query = query.eq("status", status)
    return query.execute().data or []


def update_platform_issue(issue_id: str, updates: dict) -> dict:
    response = supabase.table("platform_issues").update(updates).eq("id", issue_id).execute()
    return response.data[0] if response.data else {}


# ── Audit events (agentic era, HITL, compliance) ─────────────────────────────

def create_audit_event(engagement_id: str, action: str, entity_type: str = None, entity_id: str = None, actor_id: str = None, actor_role: str = None, details: dict = None) -> dict:
    record = {
        "engagement_id": engagement_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "details": details or {},
    }
    response = supabase.table("audit_events").insert(record).execute()
    return response.data[0] if response.data else {}


def list_audit_events_by_engagement(engagement_id: str, limit: int = 200) -> list:
    response = (
        supabase.table("audit_events")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


# ── RACI Matrix (per engagement) ─────────────────────────────────────────────

def get_raci_matrix(engagement_id: str) -> dict:
    """Return raci_matrix row for engagement or None."""
    try:
        r = (
            supabase.table("raci_matrix")
            .select("*")
            .eq("engagement_id", engagement_id)
            .limit(1)
            .execute()
        )
        return r.data[0] if r.data else None
    except Exception:
        return None


def upsert_raci_matrix(
    engagement_id: str,
    matrix: list,
    finalized: bool = False,
    finalized_at: str = None,
    finalized_by: str = None,
    change_log: list = None,
) -> dict:
    """Insert or update RACI matrix for engagement."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "engagement_id": engagement_id,
        "matrix": matrix,
        "finalized": finalized,
        "finalized_at": finalized_at,
        "finalized_by": finalized_by,
        "change_log": change_log if change_log is not None else [],
        "updated_at": now,
    }
    try:
        supabase.table("raci_matrix").upsert(record, on_conflict="engagement_id").execute()
        return get_raci_matrix(engagement_id) or record
    except Exception:
        return {}


# ── Engagement scope (L1/L2/L3 business processes) ───────────────────────────

def get_engagement_scope(engagement_id: str) -> dict:
    """Return engagement_scope row for engagement or None."""
    try:
        r = (
            supabase.table("engagement_scope")
            .select("*")
            .eq("engagement_id", engagement_id)
            .limit(1)
            .execute()
        )
        return r.data[0] if r.data else None
    except Exception:
        return None


def upsert_engagement_scope(engagement_id: str, scope: dict) -> dict:
    """Insert or update scope for engagement."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "engagement_id": engagement_id,
        "scope": scope,
        "updated_at": now,
    }
    try:
        supabase.table("engagement_scope").upsert(record, on_conflict="engagement_id").execute()
        return get_engagement_scope(engagement_id) or record
    except Exception:
        return {}


def retain_only_engagement(engagement_id: str) -> dict:
    """Remove all data for clients/engagements other than the given engagement.
    engagement_id is normalized (e.g. ENG016 -> ENG-016). Returns counts deleted or error."""
    # Normalize: ENG016 -> ENG-016
    raw = (engagement_id or "").strip().upper()
    if raw.startswith("ENG"):
        num = raw.replace("ENG", "").replace("-", "").strip()
        try:
            target = f"ENG-{int(num):03d}" if num else raw
        except ValueError:
            target = raw
    else:
        target = raw or engagement_id

    all_engs = list_engagements()
    if not any(e.get("engagement_id") == target for e in all_engs):
        return {"ok": False, "error": f"Engagement {target} not found. Nothing deleted."}

    to_delete = [e["engagement_id"] for e in all_engs if e["engagement_id"] != target]
    if not to_delete:
        return {"ok": True, "message": f"Only {target} exists; no other data to remove.", "deleted": {}}

    counts = {}
    for table, col in [
        ("hitl_events", "engagement_id"),
        ("fit_gap_assessments", "engagement_id"),
        ("process_steps", "engagement_id"),
        ("requirements", "engagement_id"),
        ("ricefw_inventory", "engagement_id"),
        ("gap_results", "engagement_id"),
        ("assets", "engagement_id"),
        ("sources", "engagement_id"),
        ("platform_issues", "engagement_id"),
        ("audit_events", "engagement_id"),
        ("benchmark_hints", "engagement_id"),
        ("feedback_events", "engagement_id"),
        ("raci_matrix", "engagement_id"),
        ("engagement_scope", "engagement_id"),
    ]:
        try:
            r = supabase.table(table).delete().filter(col, "in", to_delete).execute()
            counts[table] = len(r.data) if r.data else 0
        except Exception:
            # feedback_events may have null engagement_id; table might not exist
            counts[table] = 0

    for eid in to_delete:
        try:
            delete_engagement(eid)
            counts["engagements"] = counts.get("engagements", 0) + 1
        except Exception:
            pass

    remaining = list_engagements()
    client_ids_kept = {e.get("client_id") for e in remaining if e.get("client_id")}
    all_clients = list_clients()
    for c in all_clients:
        cid = c.get("client_id")
        if cid and cid not in client_ids_kept:
            try:
                delete_client(cid)
                counts["clients"] = counts.get("clients", 0) + 1
            except Exception:
                pass

    return {"ok": True, "message": f"Retained only {target}. Removed other engagements and orphan clients.", "deleted": counts}


# ── Portal Users (client-facing portal) ──────────────────────────────────────

def create_portal_user(engagement_id: str, client_id: str, name: str, email: str, role: str, access_token: str, token_expires_at: str) -> dict:
    record = {
        "engagement_id": engagement_id,
        "client_id": client_id,
        "name": name,
        "email": email,
        "role": role,
        "access_token": access_token,
        "token_expires_at": token_expires_at,
    }
    response = supabase.table("portal_users").insert(record).execute()
    return response.data[0] if response.data else {}


def get_portal_user_by_token(token: str) -> dict:
    import logging as _logging
    _log = _logging.getLogger("rapid")
    try:
        response = (
            supabase.table("portal_users")
            .select("*")
            .eq("access_token", token)
            .limit(1)
            .execute()
        )
        data = response.data or []
        if not data:
            _log.warning("portal_token_lookup_empty: token_prefix=%s (check RLS on portal_users or verify token stored correctly)", token[:8])
        return data[0] if data else None
    except Exception as exc:
        _log.error("portal_token_lookup_error: %s", exc)
        return None


def update_portal_user_last_access(portal_user_id: str) -> None:
    try:
        now = datetime.now(timezone.utc).isoformat()
        supabase.table("portal_users").update({"last_access": now}).eq("id", portal_user_id).execute()
    except Exception:
        pass


# ── Go-Live Checklist ─────────────────────────────────────────────────────────

def create_go_live_checklist_item(engagement_id: str, category: str, item: str, owner: str = None, due_date_offset_days: int = None) -> dict:
    record = {
        "engagement_id": engagement_id,
        "category": category,
        "item": item,
        "owner": owner,
        "due_date_offset_days": due_date_offset_days,
        "status": "not_started",
    }
    response = supabase.table("go_live_checklist").insert(record).execute()
    return response.data[0] if response.data else {}


def get_go_live_checklist(engagement_id: str) -> list:
    response = (
        supabase.table("go_live_checklist")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("category")
        .order("due_date_offset_days")
        .execute()
    )
    return response.data or []


def update_go_live_checklist_item(item_id: str, updates: dict) -> dict:
    response = supabase.table("go_live_checklist").update(updates).eq("id", item_id).execute()
    return response.data[0] if response.data else {}


# ── Agent Action Queue ────────────────────────────────────────────────────────

def create_queue_item(engagement_id: str, action_type: str, payload: dict,
                      risk_level: str, status: str, confidence: float | None = None,
                      source: str | None = None) -> dict:
    record = {
        "engagement_id": engagement_id,
        "action_type": action_type,
        "payload": payload,
        "risk_level": risk_level,
        "status": status,
        "confidence": confidence,
        "source": source,
    }
    if status == "auto_executed":
        record["executed_at"] = datetime.now(timezone.utc).isoformat()
    response = supabase.table("agent_action_queue").insert(record).execute()
    return response.data[0] if response.data else {}


def get_queue_items(engagement_id: str, status: str | None = None) -> list:
    q = supabase.table("agent_action_queue").select("*").eq("engagement_id", engagement_id)
    if status:
        q = q.eq("status", status)
    return (q.order("created_at", desc=True).execute().data or [])


def update_queue_item_status(item_id: str, status: str, reviewed_by: str | None = None) -> dict:
    update = {"status": status}
    if reviewed_by:
        update["reviewed_by"] = reviewed_by
    if status in ("approved", "rejected"):
        update["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    if status in ("approved", "auto_executed"):
        update["executed_at"] = datetime.now(timezone.utc).isoformat()
    response = supabase.table("agent_action_queue").update(update).eq("id", item_id).execute()
    return response.data[0] if response.data else {}


def update_engagement_mode(engagement_id: str, mode: str, autonomy_config: dict | None = None) -> dict:
    update: dict = {"mode": mode}
    if autonomy_config is not None:
        update["autonomy_config"] = autonomy_config
    response = supabase.table("engagements").update(update).eq("engagement_id", engagement_id).execute()
    return response.data[0] if response.data else {}


# ── Pattern Library Create ────────────────────────────────────────────────────

def create_pattern(name: str, category: str, content: str, industry_tag: str = None) -> dict:
    record = {"name": name, "category": category, "content": content, "use_count": 0}
    if industry_tag:
        record["industry_tag"] = industry_tag
    response = supabase.table("pattern_library").insert(record).execute()
    return response.data[0] if response.data else {}
