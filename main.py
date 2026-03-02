from fastapi import FastAPI, APIRouter, HTTPException, File, Form, UploadFile, Request, Header, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
import io
import json
import logging
import os
import re
import uuid
from uuid import UUID
import psycopg2
import httpx
from datetime import datetime, timezone
from openpyxl import Workbook, load_workbook

# Import config and validate env before any DB or providers
from config import validate_config, get_cors_origins
from auth import require_api_key

validate_config()  # fail fast if required env missing

from providers import get_provider, MODEL_HAIKU, MODEL_SONNET
from database import (
    save_gap_analysis,
    get_results_by_engagement,
    get_gap_results_by_req_id,
    create_requirement,
    get_requirements_by_engagement,
    get_requirement_by_id,
    update_requirement,
    create_client,
    get_client,
    list_clients,
    create_engagement,
    get_engagement,
    list_engagements,
    get_engagement_with_client,
    create_asset,
    get_assets_by_engagement,
    get_assets_by_requirement,
    update_asset,
    upload_file_to_storage,
    create_process_step,
    get_process_steps,
    get_process_step,
    update_process_step,
    delete_process_step,
    get_process_steps_by_engagement,
    create_ricefw_item,
    get_ricefw_by_engagement,
    update_ricefw_item,
    delete_ricefw_item,
)
from scope_items import SCOPE_ITEMS, get_catalogue_text

# Structured logging; config validated in lifespan
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rapid")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Config already validated at import; use lifespan for future startup (e.g. connection pools)
    yield


app = FastAPI(
    title="RAPID Gap Analysis API",
    description="AI-powered SAP S/4HANA scope item gap analysis using semantic matching",
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handlers (enterprise: stable JSON, no internal leak on 5xx) ──

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation error",
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code >= 500:
        request_id = getattr(request.state, "request_id", None) or str(uuid.uuid4())[:8]
        logger.exception(
            "HTTP 5xx: request_id=%s path=%s detail=%s",
            request_id,
            request.url.path,
            exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": "An internal error occurred. Please try again or contact support.",
                "request_id": request_id,
            },
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())[:8]
    logger.exception(
        "Unhandled exception: request_id=%s path=%s",
        request_id,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again or contact support.",
            "request_id": request_id,
        },
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())[:8]
    response = await call_next(request)
    return response


# v1 API: all routes under /v1; optional API key when API_KEY env is set
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])


# ── Pydantic models ───────────────────────────────────────────────────────────

class GapAnalysisRequest(BaseModel):
    engagement_id: str
    process_description: Optional[str] = None  # required unless req_id provided
    req_id: Optional[str] = None               # looks up description from requirements
    top_n: Optional[int] = 5
    lob_filter: Optional[str] = None

class ScopeItemMatch(BaseModel):
    id: str
    name: str
    lob: str
    process_group: str
    description: str
    confidence: str
    rationale: str
    migration_objects: List[str]

class GapAnalysisResponse(BaseModel):
    engagement_id: str
    req_id: Optional[str] = None
    process_description: str
    matches: List[ScopeItemMatch]
    total_scope_items_searched: int
    tokens_used: Optional[int] = None
    timestamp: str

class RequirementCreate(BaseModel):
    engagement_id: str
    title: str
    description: str
    source_type: Optional[str] = None
    tags: Optional[List[str]] = []
    stakeholder: Optional[str] = None
    raw_input: Optional[str] = None
    # Phase 1 extended fields
    business_process: Optional[str] = None         # LOB, e.g. Finance / Sales / Supply Chain
    priority: Optional[str] = "Must-Have"          # Must-Have / Should-Have / Nice-to-Have
    category: Optional[str] = None                 # Automation / Control/Compliance / Reporting / Integration / UX / Data Migration
    kpi_impact: Optional[Dict] = None              # {"metric": "...", "target": "...", "unit": "..."}
    confidence_score: Optional[float] = 0.8
    current_state_ref: Optional[str] = None        # quote, file name, video timestamp
    actors: Optional[List[Dict]] = None            # [{"role": "AP Clerk", "type": "formal"}, ...]
    shadow_tools: Optional[List[str]] = None       # ["Excel macro", "WhatsApp group", ...]
    sign_off_status: Optional[str] = "draft"       # draft / sme_approved / owner_approved / confirmed
    sign_off_by: Optional[str] = None
    sign_off_at: Optional[str] = None
    sap_mapping_id: Optional[str] = None           # nearest scope item ID
    fit_assessment: Optional[str] = None           # Fit-to-Standard / Soft-Gap / Hard-Gap
    # Sprint 5 process flow fields
    process_level_2: Optional[str] = None          # e.g. Record to Report, Procure to Pay
    process_level_3: Optional[str] = None          # e.g. Accounts Payable, General Ledger
    # Audit / RTM: external reference ID and source fields
    reference_id: Optional[str] = None            # e.g. Excel/source requirement ID for audit trail
    business_value: Optional[str] = None
    current_system: Optional[str] = None
    target_system_module: Optional[str] = None
    fit_type: Optional[str] = None
    related_test_case_id: Optional[str] = None

class RequirementUpdate(BaseModel):
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    stakeholder: Optional[str] = None
    # Phase 1 extended fields
    business_process: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    kpi_impact: Optional[Dict] = None
    confidence_score: Optional[float] = None
    current_state_ref: Optional[str] = None
    actors: Optional[List[Dict]] = None
    shadow_tools: Optional[List[str]] = None
    sign_off_status: Optional[str] = None
    sign_off_by: Optional[str] = None
    sign_off_at: Optional[str] = None
    sap_mapping_id: Optional[str] = None
    fit_assessment: Optional[str] = None
    # Sprint 5 process flow fields
    process_level_2: Optional[str] = None
    process_level_3: Optional[str] = None
    reference_id: Optional[str] = None
    business_value: Optional[str] = None
    current_system: Optional[str] = None
    target_system_module: Optional[str] = None
    fit_type: Optional[str] = None
    related_test_case_id: Optional[str] = None

class TranscriptExtractRequest(BaseModel):
    engagement_id: str
    stakeholder: str
    transcript_text: str

class ArchaeologistSessionRequest(BaseModel):
    engagement_id: str
    stakeholder: str
    role: str
    business_process: str
    message: str
    session_history: Optional[List[Dict]] = []

class ClientCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    employees: Optional[int] = None
    legal_entities: Optional[int] = None
    current_systems: Optional[List[str]] = None
    systems_to_keep: Optional[List[str]] = None
    systems_to_replace: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    regulatory_environment: Optional[List[str]] = None
    # Strategy & context (pre-fill from website)
    business_strategy: Optional[str] = None
    goals: Optional[List[str]] = None
    key_products: Optional[List[str]] = None
    value_proposition: Optional[str] = None
    senior_executives: Optional[List[Dict[str, str]]] = None  # [{"name": "...", "title": "..."}]
    direct_competitors: Optional[List[str]] = None
    substitutes: Optional[List[str]] = None

class ClientPrefillFromWebsiteRequest(BaseModel):
    url: str


class EngagementCreate(BaseModel):
    client_id: str
    name: str
    description: Optional[str] = None
    go_live_date: Optional[str] = None
    project_type: Optional[str] = None
    # Control: status & dates
    status: Optional[str] = "open"          # open | completed | abandoned
    planned_start_date: Optional[str] = None
    planned_end_date: Optional[str] = None
    actual_start_date: Optional[str] = None
    actual_end_date: Optional[str] = None
    # Additional engagement control fields
    project_manager: Optional[str] = None
    sponsor: Optional[str] = None
    risk_level: Optional[str] = None        # low | medium | high
    health: Optional[str] = None            # on_track | at_risk | off_track

class SignOffRequest(BaseModel):
    level: str      # "sme" or "owner"
    signed_by: str

class AssetUpdate(BaseModel):
    req_id: Optional[str] = None
    process_level_2: Optional[str] = None
    process_level_3: Optional[str] = None
    confirmed: Optional[bool] = None
    suggested_tags: Optional[List[str]] = None

class RequirementResponse(BaseModel):
    req_id: str
    engagement_id: str
    title: str
    description: str
    source_type: Optional[str] = None
    tags: Optional[List[str]] = []
    stakeholder: Optional[str] = None
    raw_input: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    # Phase 1 extended fields
    business_process: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    kpi_impact: Optional[Any] = None
    confidence_score: Optional[float] = None
    current_state_ref: Optional[str] = None
    actors: Optional[Any] = None
    shadow_tools: Optional[List[str]] = None
    sign_off_status: Optional[str] = None
    sign_off_by: Optional[str] = None
    sign_off_at: Optional[str] = None
    sap_mapping_id: Optional[str] = None
    fit_assessment: Optional[str] = None
    # Sprint 5 process flow fields
    process_level_2: Optional[str] = None
    process_level_3: Optional[str] = None
    # Audit / RTM: external reference and source fields
    reference_id: Optional[str] = None
    business_value: Optional[str] = None
    current_system: Optional[str] = None
    target_system_module: Optional[str] = None
    fit_type: Optional[str] = None
    related_test_case_id: Optional[str] = None


class ProcessFlowAssignRequest(BaseModel):
    req_id: str
    process_level_2: str
    process_level_3: Optional[str] = None


class ProcessStepCreate(BaseModel):
    step_number: int
    title: str
    description: str
    performer_name: str
    performer_role: str
    shape: str = "process"      # start | end | process | decision | document
    step_type: str = "manual"   # manual | system | agentic
    duration_minutes: Optional[float] = None
    systems_used: Optional[List[str]] = []
    kpis: Optional[Dict] = None
    is_pain_point: bool = False
    next_step_id: Optional[str] = None
    branches: Optional[List[Dict]] = None


class ProcessStepUpdate(BaseModel):
    step_number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    performer_name: Optional[str] = None
    performer_role: Optional[str] = None
    shape: Optional[str] = None
    step_type: Optional[str] = None
    duration_minutes: Optional[float] = None
    systems_used: Optional[List[str]] = None
    kpis: Optional[Dict] = None
    is_pain_point: Optional[bool] = None
    next_step_id: Optional[str] = None
    branches: Optional[List[Dict]] = None


# Sprint 7: RICEFW = Reports, Interfaces, Conversions, Enhancements, Forms, Workflows, Agents
_RICEFW_COMPLEXITY = {"very_high", "high", "medium", "low"}
_RICEFW_PRIORITY = {"must", "should", "could", "noneed"}

class RICEFWCreate(BaseModel):
    type: str       # R | I | C | E | F | W | A
    name: str
    description: str
    req_id: str     # required: link to requirement
    status: Optional[str] = "identified"
    complexity: Optional[str] = None   # very_high | high | medium | low
    priority: Optional[str] = None     # must | should | could | noneed


class RICEFWUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    req_id: Optional[str] = None
    status: Optional[str] = None
    complexity: Optional[str] = None
    priority: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────


def _normalize_tag(value: str) -> str:
    """Normalise tag strings to canonical snake_case form, similar to frontend."""
    if not value:
        return ""
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug


def build_catalogue_for_prompt(lob_filter: Optional[str] = None) -> str:
    items = SCOPE_ITEMS
    if lob_filter:
        items = [i for i in items if i.get('lob', '').lower() == lob_filter.lower()]
    lines = []
    for item in items:
        lines.append(
            f"ID:{item['id']} | {item['name']} | {item['lob']} > {item['process_group']}\n"
            f"  {item['description']}"
        )
    return "\n".join(lines)


_GAP_SYSTEM_PROMPT = """You are an expert SAP S/4HANA implementation consultant specializing in Fit-to-Standard gap analysis.

Your task: Given a business process description, identify the most relevant SAP S/4HANA Cloud Public Edition scope items from the provided catalogue.

Instructions:
1. Analyze the business process description semantically - look beyond keywords to understand intent
2. Return the top matching scope items ranked by relevance
3. For each match, provide confidence (HIGH / MEDIUM / LOW) and a brief rationale
4. Consider that one business requirement often maps to multiple scope items
5. Always return valid JSON only

Response format (JSON array):
[
  {
    "id": "scope_item_code",
    "confidence": "HIGH|MEDIUM|LOW",
    "rationale": "One sentence explaining why this scope item matches"
  }
]"""


def _run_gap_analysis(
    provider,
    process_description: str,
    top_n: int = 5,
    lob_filter: Optional[str] = None,
) -> tuple:
    """Returns (matches: List[ScopeItemMatch], tokens_used: int)."""
    catalogue = build_catalogue_for_prompt(lob_filter)
    user_prompt = (
        f"Business Process Description:\n{process_description}\n\n"
        f"SAP S/4HANA Cloud 2602 Scope Item Catalogue (2602 release):\n{catalogue}\n\n"
        f"Return the top {top_n} most relevant scope items as JSON."
    )
    # Haiku is cheap and sufficient; keep max output small
    result = provider.complete(_GAP_SYSTEM_PROMPT, user_prompt, max_tokens=512, model=MODEL_HAIKU)
    raw_text = result.get("content", "[]")
    tokens_used = result.get("tokens_used")

    json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON array found in response")

    matches_raw = json.loads(json_match.group())
    scope_lookup = {item['id']: item for item in SCOPE_ITEMS}
    matches = []
    for m in matches_raw[:top_n]:
        item_id = m.get('id', '')
        scope = scope_lookup.get(item_id, {})
        if scope:
            matches.append(ScopeItemMatch(
                id=item_id,
                name=scope['name'],
                lob=scope['lob'],
                process_group=scope['process_group'],
                description=scope['description'],
                confidence=m.get('confidence', 'MEDIUM'),
                rationale=m.get('rationale', ''),
                migration_objects=scope.get('migration_objects', []),
            ))
    return matches, tokens_used


# ── Health / Catalogue / LOBs ─────────────────────────────────────────────────

@app.get("/health")
def health():
    """Liveness: app is running."""
    return {
        "status": "ok",
        "version": "1.2.0",
        "scope_items_loaded": len(SCOPE_ITEMS),
        "release": "S/4HANA Cloud Public Edition 2602"
    }


@app.get("/health/ready")
def health_ready():
    """Readiness: app and dependencies (e.g. DB) are reachable."""
    try:
        list_clients()
        return {"status": "ok", "checks": {"database": "ok"}}
    except Exception as e:
        logger.warning("Readiness check failed: %s", e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.get("/catalogue")
def get_catalogue(lob: Optional[str] = None):
    items = SCOPE_ITEMS
    if lob:
        items = [i for i in items if i.get('lob', '').lower() == lob.lower()]
    return {"total": len(items), "items": items}

@router.get("/lobs")
def get_lobs():
    from collections import Counter
    counts = Counter(i['lob'] for i in SCOPE_ITEMS)
    return {"lobs": [{"name": k, "count": v} for k, v in sorted(counts.items())]}

@router.get("/results")
def get_results(engagement_id: str):
    try:
        results = get_results_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"engagement_id": engagement_id, "total": len(results), "results": results}


# ── Client context helper ─────────────────────────────────────────────────────

def _build_client_context_line(engagement_id: str) -> str:
    """Return a single context sentence from engagement + client, or empty string."""
    try:
        ctx = get_engagement_with_client(engagement_id)
    except Exception:
        return ""
    if not ctx:
        return ""
    client = ctx.get("client") or {}
    parts = []
    if client.get("name"):
        parts.append(f"Client: {client['name']}")
    if client.get("industry"):
        parts.append(f"Industry: {client['industry']}")
    if client.get("employees"):
        parts.append(f"Size: {client['employees']} employees")
    if client.get("legal_entities"):
        parts.append(f"{client['legal_entities']} legal entities")
    if client.get("current_systems"):
        parts.append(f"Current systems: {client['current_systems']}")
    if client.get("countries"):
        parts.append(f"Countries: {client['countries']}")
    if client.get("regulatory_environment"):
        parts.append(f"Regulatory: {client['regulatory_environment']}")
    return ", ".join(parts) if parts else ""


# ── Clients ───────────────────────────────────────────────────────────────────

@router.post("/clients", status_code=201)
def post_client(body: ClientCreate):
    try:
        client = create_client(body.dict(exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not client:
        raise HTTPException(status_code=500, detail="Failed to create client")
    return client

@router.get("/clients")
def list_all_clients():
    try:
        return {"clients": list_clients()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _html_to_plain_text(html: str, max_chars: int = 35000) -> str:
    """Strip HTML tags and collapse whitespace for LLM consumption."""
    text = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] if len(text) > max_chars else text


_CLIENT_PREFILL_SYSTEM = """You are extracting structured company/client profile data from website content.
Return a single JSON object with these keys only. Use null for unknown. For arrays use [] if none found.
- name (string): company name
- industry (string): industry sector
- employees (number or null): employee count if mentioned
- legal_entities (number or null): number of legal entities if mentioned
- current_systems (array of strings): ERP or IT systems mentioned
- countries (array of strings): countries of operation
- regulatory_environment (array of strings): e.g. SOX, GDPR, HIPAA
- business_strategy (string): brief description of business strategy
- goals (array of strings): strategic or business goals
- key_products (array of strings): main products or services
- value_proposition (string): value proposition or differentiator
- senior_executives (array of objects with "name" and "title")
- direct_competitors (array of strings): direct competitors (Porter 5 forces)
- substitutes (array of strings): substitute products/services (Porter 5 forces)
Return only the JSON object, no markdown or explanation."""


@router.post("/clients/prefill-from-website", response_model=Dict[str, Any])
def prefill_client_from_website(body: ClientPrefillFromWebsiteRequest):
    """Fetch URL, extract text, and use LLM to pre-populate client profile (Create Client form)."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Pre-fill is not available: ANTHROPIC_API_KEY is not configured. Enter client details manually.",
        )
    raw = (body.url or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="url is required")
    # Heuristic: if input doesn't look like a full URL, treat it as a host or keyword
    candidates: List[str] = []
    base_inputs: List[str] = []
    if "." not in raw and " " in raw:
        # Keyword like "Carrier Global" -> carrier, carrierglobal
        slug = "".join(raw.lower().split())
        base_inputs = [slug]
    elif "." not in raw:
        base_inputs = [raw.lower()]
    else:
        base_inputs = [raw]

    for base in base_inputs:
        if base.startswith(("http://", "https://")):
            candidates.append(base)
        else:
            candidates.append(f"https://{base}")
            candidates.append(f"https://www.{base}")

    # Try base and a few common paths to find a usable page
    discovered: List[str] = []
    html = None
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        for base_url in candidates:
            for path in ["", "/", "/en", "/en-us", "/about", "/about-us", "/company", "/en/worldwide/"]:
                try:
                    url = base_url.rstrip("/") + path
                    resp = client.get(url)
                    if resp.status_code < 400:
                        if html is None:
                            html = resp.text
                            chosen_url = url
                        if url not in discovered:
                            discovered.append(url)
                    # Stop early if we already found a good primary URL and a handful of alternates
                    if html and len(discovered) >= 3:
                        break
                except httpx.HTTPError:
                    continue
            if html and len(discovered) >= 3:
                break

    if html is None:
        # Could not fetch any usable page; surface discovered candidates (if any) to the UI
        detail = "Could not fetch URL. Try choosing a specific About/Company page."
        raise HTTPException(
            status_code=422,
            detail={"message": detail, "candidates": discovered} if discovered else detail,
        )

    text = _html_to_plain_text(html)
    if len(text) < 100:
        raise HTTPException(status_code=422, detail="Page content too short to extract meaningful data")
    provider = get_provider()
    user_prompt = f"Website content (excerpt):\n\n{text}\n\nExtract company profile JSON."
    try:
        result = provider.complete(_CLIENT_PREFILL_SYSTEM, user_prompt, max_tokens=1024, model=MODEL_HAIKU)
        raw = result.get("content", "{}")
        data = _extract_json_object(raw)
    except Exception as e:
        logger.exception("prefill LLM failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to extract company data from page")
    # Normalize keys to match ClientCreate; drop unknown keys
    allowed = {
        "name", "industry", "employees", "legal_entities", "current_systems", "countries",
        "regulatory_environment", "business_strategy", "goals", "key_products", "value_proposition",
        "senior_executives", "direct_competitors", "substitutes",
    }
    return {k: v for k, v in data.items() if k in allowed}


@router.get("/clients/{client_id}")
def get_single_client(client_id: str):
    try:
        client = get_client(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not client:
        raise HTTPException(status_code=404, detail=f"{client_id} not found")
    return client


# ── Engagements ───────────────────────────────────────────────────────────────

@router.post("/engagements", status_code=201)
def post_engagement(body: EngagementCreate):
    try:
        data = body.dict(exclude_none=True)
        status = data.get("status")
        if status and status not in {"open", "completed", "abandoned"}:
            raise HTTPException(status_code=400, detail="Invalid engagement status. Must be one of: open, completed, abandoned")
        risk = data.get("risk_level")
        if risk and risk not in {"low", "medium", "high"}:
            raise HTTPException(status_code=400, detail="Invalid risk_level. Must be one of: low, medium, high")
        health = data.get("health")
        if health and health not in {"on_track", "at_risk", "off_track"}:
            raise HTTPException(status_code=400, detail="Invalid health. Must be one of: on_track, at_risk, off_track")
        eng = create_engagement(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not eng:
        raise HTTPException(status_code=500, detail="Failed to create engagement")
    return eng

@router.get("/engagements")
def list_all_engagements(client_id: Optional[str] = None):
    try:
        return {"engagements": list_engagements(client_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/engagements/{engagement_id}")
def get_single_engagement(engagement_id: str):
    try:
        eng = get_engagement_with_client(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not eng:
        raise HTTPException(status_code=404, detail=f"{engagement_id} not found")
    return eng


@router.get("/engagement/{engagement_id}/label")
def get_engagement_label(engagement_id: str):
    """Lightweight: engagement_id, project name, company name for display (e.g. header)."""
    try:
        eng = get_engagement_with_client(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not eng:
        raise HTTPException(status_code=404, detail=f"{engagement_id} not found")
    client = eng.get("client") or {}
    return {
        "engagement_id": eng.get("engagement_id"),
        "name": eng.get("name") or "",
        "client_name": client.get("name") or "",
    }


@router.get("/engagement/{engagement_id}/search")
def search_engagement(engagement_id: str, q: str = ""):
    """Search within engagement by keywords and match code (req_id, type, etc). Returns requirements and RICEFW matches with navigation paths."""
    q = (q or "").strip().lower()
    if not q:
        return {"engagement_id": engagement_id, "query": "", "requirements": [], "ricefw": []}
    try:
        requirements = get_requirements_by_engagement(engagement_id)
        ricefw_items = get_ricefw_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    req_matches = []
    for r in requirements:
        req_id = (r.get("req_id") or "").lower()
        title = (r.get("title") or "").lower()
        desc = (r.get("description") or "").lower()
        tags = " ".join((r.get("tags") or [])).lower()
        if q in req_id or q in title or q in desc or q in tags:
            req_matches.append({
                "type": "requirement",
                "req_id": r.get("req_id"),
                "title": r.get("title"),
                "path": f"/workflow/{r.get('req_id')}?engagement_id={engagement_id}",
            })
    ricefw_matches = []
    for item in ricefw_items:
        name = (item.get("name") or "").lower()
        desc = (item.get("description") or "").lower()
        typ = (item.get("type") or "").lower()
        req_id = (item.get("req_id") or "").lower()
        if q in name or q in desc or q in typ or q in req_id:
            ricefw_matches.append({
                "kind": "ricefw",
                "id": item.get("id"),
                "name": item.get("name"),
                "type": item.get("type"),
                "req_id": item.get("req_id"),
                "path": f"/engagement?engagement_id={engagement_id}#ricefw",
            })
    return {
        "engagement_id": engagement_id,
        "query": q,
        "requirements": req_matches[:20],
        "ricefw": ricefw_matches[:20],
    }


# ── Requirements ──────────────────────────────────────────────────────────────

_ALLOWED_PRIORITIES = {"Must-Have", "Should-Have", "Nice-to-Have"}
_ALLOWED_CATEGORIES = {"Automation", "Control/Compliance", "Reporting", "Integration", "UX", "Data Migration"}
_ALLOWED_FIT = {"Fit-to-Standard", "Soft-Gap", "Hard-Gap"}


@router.post("/requirements", response_model=RequirementResponse, status_code=201)
def post_requirement(body: RequirementCreate):
    kwargs = body.dict()
    engagement_id = kwargs.pop("engagement_id")
    title = kwargs.pop("title")
    description = kwargs.pop("description")

    priority = kwargs.get("priority")
    if priority and priority not in _ALLOWED_PRIORITIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority. Must be one of: {sorted(_ALLOWED_PRIORITIES)}",
        )
    category = kwargs.get("category")
    if category and category not in _ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {sorted(_ALLOWED_CATEGORIES)}",
        )
    fit = kwargs.get("fit_assessment")
    if fit and fit not in _ALLOWED_FIT:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fit_assessment. Must be one of: {sorted(_ALLOWED_FIT)}",
        )

    try:
        req = create_requirement(
            engagement_id=engagement_id,
            title=title,
            description=description,
            **kwargs,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=500, detail="Failed to create requirement")
    return req

@router.get("/requirements", response_model=List[RequirementResponse])
def list_requirements(engagement_id: str):
    try:
        return get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/requirements/extract-from-transcript", status_code=201)
def extract_from_transcript(body: TranscriptExtractRequest):
    provider = get_provider()
    client_context = _build_client_context_line(body.engagement_id)
    system_prompt = """You are an expert business analyst capturing requirements from conversation transcripts for SAP S/4HANA implementation projects.

Extract discrete business requirements from the transcript. For each requirement identify:
- title: Brief descriptive title (max 10 words)
- description: Detailed description of the business need or process
- tags: Array — use only: pain_point, manual_step, secret_sauce, workaround, hand_off
- business_process: One of Procure-to-Pay, Order-to-Cash, Record-to-Report, Plan-to-Produce, Hire-to-Retire (pick closest)
- priority: Must-Have if the pain is severe or a compliance/control need; Should-Have if clearly beneficial; Nice-to-Have if aspirational
- category: One of Automation, Control/Compliance, Reporting, Integration, UX, Data Migration
- shadow_tools: Array of unofficial tools mentioned (e.g. "Excel macro", "WhatsApp", "Access DB"). Empty array if none.
- actors: Array of objects {"role": "job title or name", "type": "formal" or "informal"} for people mentioned
- kpi_impact: Object {"metric": "...", "current": "...", "target": "...", "unit": "..."} if any measurable metric is implied (e.g. "takes 3 days" → target to reduce). null if no metric.

Return a JSON array only — no markdown fences:
[
  {
    "title": "requirement title",
    "description": "detailed description",
    "tags": ["tag1"],
    "business_process": "Order-to-Cash",
    "priority": "Must-Have",
    "category": "Automation",
    "shadow_tools": [],
    "actors": [{"role": "AP Clerk", "type": "formal"}],
    "kpi_impact": null
  }
]

Rules:
- Each requirement must be distinct and actionable
- tags must only come from: pain_point, manual_step, secret_sauce, workaround, hand_off
- Return [] if no clear requirements are found"""

    if client_context:
        system_prompt = system_prompt + f"\n\nEngagement context: {client_context}"

    user_prompt = f"Stakeholder: {body.stakeholder}\n\nExtract requirements from this transcript:\n\n{body.transcript_text}\n\nReturn JSON array."

    try:
        # Use cheaper model with tight token limit for extraction
        result = provider.complete(system_prompt, user_prompt, max_tokens=768, model=MODEL_HAIKU)
        raw_text = result.get("content", "[]")

        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON array found in response")

        extracted = json.loads(json_match.group())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

    valid_tags = {"pain_point", "manual_step", "secret_sauce", "workaround", "hand_off"}
    created = []
    for item in extracted:
        tags = [t for t in (item.get("tags") or []) if t in valid_tags]
        try:
            req = create_requirement(
                engagement_id=body.engagement_id,
                title=item.get("title", "Untitled"),
                description=item.get("description", ""),
                source_type="Conversation",
                tags=tags,
                stakeholder=body.stakeholder,
                raw_input=body.transcript_text,
                business_process=item.get("business_process") or None,
                priority=item.get("priority") or "Must-Have",
                category=item.get("category") or None,
                shadow_tools=item.get("shadow_tools") or None,
                actors=item.get("actors") or None,
                kpi_impact=item.get("kpi_impact") or None,
            )
            if req:
                created.append({
                    "req_id": req["req_id"],
                    "title": req["title"],
                    "tags": req.get("tags", []),
                    "business_process": req.get("business_process"),
                    "priority": req.get("priority"),
                    "category": req.get("category"),
                    "shadow_tools": req.get("shadow_tools"),
                    "actors": req.get("actors"),
                    "kpi_impact": req.get("kpi_impact"),
                })
        except Exception as e:
            print(f"Failed to create requirement '{item.get('title')}': {e}")

    return {"created": len(created), "requirements": created}


# ── Domain Templates ───────────────────────────────────────────────────────────

_DOMAIN_TEMPLATES: Dict[str, List[Dict]] = {
    "finance": [
        {
            "title": "Automated customer invoicing on goods issue",
            "description": "Automatically generate and send customer invoices when goods issue is posted, eliminating manual invoice creation and reducing billing cycle time.",
            "business_process": "Order-to-Cash",
            "priority": "Must-Have",
            "category": "Automation",
            "tags": ["manual_step", "pain_point"],
            "shadow_tools": [],
            "actors": [{"role": "Billing Clerk", "type": "formal"}],
            "kpi_impact": {"metric": "invoice cycle time", "target": "reduce by 50%", "unit": "days"},
        },
        {
            "title": "Vendor payment approval with three-way match",
            "description": "Enforce three-way match (PO / GR / invoice) before any vendor payment is approved, with automatic blocking of mismatched invoices.",
            "business_process": "Procure-to-Pay",
            "priority": "Must-Have",
            "category": "Control/Compliance",
            "tags": ["manual_step", "workaround"],
            "shadow_tools": ["Excel spreadsheet"],
            "actors": [{"role": "AP Manager", "type": "formal"}, {"role": "Auditor", "type": "formal"}],
            "kpi_impact": None,
        },
        {
            "title": "Month-end closing time reduction to 3 days",
            "description": "Automate journal entries, intercompany reconciliation, and reporting to compress financial close from current state to 3 business days.",
            "business_process": "Record-to-Report",
            "priority": "Must-Have",
            "category": "Reporting",
            "tags": ["pain_point", "manual_step"],
            "shadow_tools": ["Excel macro", "Access DB"],
            "actors": [{"role": "Controller", "type": "formal"}, {"role": "CFO", "type": "formal"}],
            "kpi_impact": {"metric": "month-end close days", "target": "3 days", "unit": "days"},
        },
    ],
    "sales": [
        {
            "title": "Credit risk check and automatic order blocking",
            "description": "Run automated credit risk checks when sales orders are created and block orders that exceed the customer credit limit, with workflow for manual override approval.",
            "business_process": "Order-to-Cash",
            "priority": "Must-Have",
            "category": "Control/Compliance",
            "tags": ["manual_step", "workaround"],
            "shadow_tools": [],
            "actors": [{"role": "Credit Manager", "type": "formal"}, {"role": "Sales Rep", "type": "formal"}],
            "kpi_impact": None,
        },
        {
            "title": "Shipping and warehouse integration triggers",
            "description": "Automatically trigger warehouse pick/pack/ship tasks when sales orders are confirmed, with real-time status updates back to the sales order.",
            "business_process": "Order-to-Cash",
            "priority": "Should-Have",
            "category": "Integration",
            "tags": ["manual_step", "hand_off"],
            "shadow_tools": ["WhatsApp group"],
            "actors": [{"role": "Warehouse Operator", "type": "formal"}, {"role": "Shipping Clerk", "type": "formal"}],
            "kpi_impact": {"metric": "order-to-ship time", "target": "reduce by 30%", "unit": "hours"},
        },
    ],
    "procurement": [
        {
            "title": "Purchase requisition approval workflow",
            "description": "Implement configurable multi-level approval workflow for purchase requisitions based on value thresholds, cost centre, and category, replacing email-based approvals.",
            "business_process": "Procure-to-Pay",
            "priority": "Must-Have",
            "category": "Control/Compliance",
            "tags": ["manual_step", "workaround"],
            "shadow_tools": ["Email", "Excel spreadsheet"],
            "actors": [{"role": "Requester", "type": "formal"}, {"role": "Budget Holder", "type": "formal"}, {"role": "Procurement Manager", "type": "formal"}],
            "kpi_impact": None,
        },
        {
            "title": "Automatic stock replenishment",
            "description": "Automatically generate purchase requisitions when inventory falls below reorder points, using MRP logic to calculate quantities and lead times.",
            "business_process": "Procure-to-Pay",
            "priority": "Should-Have",
            "category": "Automation",
            "tags": ["manual_step"],
            "shadow_tools": [],
            "actors": [{"role": "Inventory Planner", "type": "formal"}],
            "kpi_impact": {"metric": "stockout events", "target": "reduce by 80%", "unit": "incidents/month"},
        },
    ],
    "manufacturing": [
        {
            "title": "MRP capacity-aware order conversion",
            "description": "Convert planned orders to production orders only when capacity is available, integrating MRP with capacity planning to prevent overloading work centres.",
            "business_process": "Plan-to-Produce",
            "priority": "Must-Have",
            "category": "Automation",
            "tags": ["manual_step", "pain_point"],
            "shadow_tools": ["Excel macro"],
            "actors": [{"role": "Production Planner", "type": "formal"}, {"role": "Shop Floor Supervisor", "type": "formal"}],
            "kpi_impact": {"metric": "schedule adherence", "target": "above 95%", "unit": "percent"},
        },
        {
            "title": "Production variance alerts",
            "description": "Automatically detect and alert when actual production costs or quantities deviate from standard by more than a configurable threshold.",
            "business_process": "Plan-to-Produce",
            "priority": "Should-Have",
            "category": "Reporting",
            "tags": ["pain_point"],
            "shadow_tools": [],
            "actors": [{"role": "Cost Accountant", "type": "formal"}, {"role": "Production Manager", "type": "formal"}],
            "kpi_impact": None,
        },
    ],
    "hr": [
        {
            "title": "Digital onboarding workflow for new hires",
            "description": "Automate the end-to-end onboarding process — contract generation, IT provisioning, payroll setup, and training assignment — triggered on hire date.",
            "business_process": "Hire-to-Retire",
            "priority": "Must-Have",
            "category": "Automation",
            "tags": ["manual_step", "hand_off"],
            "shadow_tools": ["Email", "Shared Drive"],
            "actors": [{"role": "HR Business Partner", "type": "formal"}, {"role": "Line Manager", "type": "formal"}, {"role": "IT Admin", "type": "formal"}],
            "kpi_impact": {"metric": "onboarding time to productivity", "target": "reduce by 40%", "unit": "days"},
        },
        {
            "title": "Automated payroll variance reporting",
            "description": "Generate monthly payroll variance reports comparing current vs prior period, flagging anomalies above threshold for payroll manager review before approval.",
            "business_process": "Hire-to-Retire",
            "priority": "Must-Have",
            "category": "Reporting",
            "tags": ["manual_step", "pain_point"],
            "shadow_tools": ["Excel macro"],
            "actors": [{"role": "Payroll Manager", "type": "formal"}, {"role": "Finance Controller", "type": "formal"}],
            "kpi_impact": None,
        },
    ],
}

_VALID_DOMAINS = list(_DOMAIN_TEMPLATES.keys())


@router.get("/requirements/templates")
def get_requirement_templates(domain: str):
    key = domain.lower()
    if key not in _DOMAIN_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown domain '{domain}'. Valid options: {', '.join(_VALID_DOMAINS)}",
        )
    templates = _DOMAIN_TEMPLATES[key]
    return {"domain": key, "total": len(templates), "templates": templates}


_ARCHAEOLOGIST_SYSTEM_PROMPT = """You are a senior business analyst and process archaeologist conducting a discovery interview for a Cloud ERP transformation. Your job is to deeply understand how work actually happens today — not how it should work, but how it really works, including workarounds, exceptions, and shadow tools.

Your behaviour:
- Ask one focused question at a time
- Probe for: who actually does each step (not just job titles), what breaks, what is manual, what tools people use unofficially, what the person is proud of and wants to preserve
- Adapt your questions to the person role: ask a warehouse operator about physical flows and exceptions; ask a CFO about controls, reporting pain, and month-end pressure
- When you learn something significant, summarise it back: "So if I understand correctly, you manually reconcile the bank statement every morning in Excel before the ERP is updated — is that right?"
- After 3-4 exchanges, offer to extract what you have learned as a structured requirement

Response format — always return valid JSON only, no markdown fences:
{
  "reply": "your next question or summary to the user",
  "extracted": {
    "ready": false,
    "title": "",
    "description": "",
    "tags": [],
    "shadow_tools": [],
    "actors": [],
    "pain_points": [],
    "secret_sauce": []
  },
  "suggested_follow_ups": ["question 1", "question 2"]
}

When extracted.ready is true, populate all extracted fields with what you have learned."""


def _extract_json_object(text: str) -> dict:
    """Extract first complete JSON object from text, stripping markdown fences."""
    text = re.sub(r'```(?:json)?\s*', '', text).strip()
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object found in response")
    depth = 0
    for i, c in enumerate(text[start:], start):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("No complete JSON object found in response")


@router.post("/requirements/archaeologist-session")
def archaeologist_session(body: ArchaeologistSessionRequest):
    provider = get_provider()

    # Inject client context into system prompt
    system_prompt = _ARCHAEOLOGIST_SYSTEM_PROMPT
    client_context = _build_client_context_line(body.engagement_id)
    if client_context:
        system_prompt = system_prompt + f"\n\nEngagement context: {client_context}"

    # Build conversation as a single user message (history + current turn)
    lines = [
        f"Context:",
        f"  Stakeholder: {body.stakeholder} | Role: {body.role} | Business Process: {body.business_process}",
        "",
    ]
    if body.session_history:
        lines.append("Conversation so far:")
        for msg in body.session_history:
            prefix = "Analyst" if msg.get("role") == "assistant" else "Stakeholder"
            lines.append(f"  {prefix}: {msg.get('content', '')}")
        lines.append("")
    lines.append(f"Stakeholder: {body.message}")
    lines.append("")
    lines.append("Respond as the analyst. Return valid JSON only.")
    user_prompt = "\n".join(lines)

    try:
        # Use cheaper model with modest response size for dialogue
        result = provider.complete(system_prompt, user_prompt, max_tokens=512, model=MODEL_HAIKU)
        raw_text = result.get("content", "{}")
        parsed = _extract_json_object(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Archaeologist LLM error: {e}")

    extracted = parsed.get("extracted", {})
    response: Dict = {
        "reply": parsed.get("reply", ""),
        "extracted": extracted,
        "suggested_follow_ups": parsed.get("suggested_follow_ups", []),
    }

    if extracted.get("ready"):
        valid_tags = {"pain_point", "manual_step", "secret_sauce", "workaround", "hand_off"}
        tags = [t for t in (extracted.get("tags") or []) if t in valid_tags]
        try:
            req = create_requirement(
                engagement_id=body.engagement_id,
                title=extracted.get("title", "Extracted Requirement"),
                description=extracted.get("description", ""),
                source_type="Conversation",
                tags=tags,
                stakeholder=body.stakeholder,
                business_process=body.business_process,
                actors=extracted.get("actors") or None,
                shadow_tools=extracted.get("shadow_tools") or None,
            )
            if req:
                response["req_id"] = req.get("req_id")
        except Exception as e:
            print(f"Auto-create requirement failed (non-fatal): {e}")

    return response


@router.get("/requirements/{req_id}", response_model=RequirementResponse)
def get_requirement(req_id: str, engagement_id: str):
    try:
        req = get_requirement_by_id(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=404, detail=f"{req_id} not found for engagement {engagement_id}")
    return req

@router.patch("/requirements/{req_id}", response_model=RequirementResponse)
def patch_requirement(req_id: str, engagement_id: str, body: RequirementUpdate):
    updates = {k: v for k, v in body.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    try:
        req = update_requirement(req_id, engagement_id, updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=404, detail=f"{req_id} not found for engagement {engagement_id}")
    return req


@router.post("/requirements/{req_id}/sign-off", response_model=RequirementResponse)
def sign_off_requirement(req_id: str, engagement_id: str, body: SignOffRequest):
    """Sign-off state machine:
      level=sme   → sme_approved
      level=owner, current=sme_approved → confirmed
      level=owner, otherwise            → owner_approved
    """
    if body.level not in ("sme", "owner"):
        raise HTTPException(status_code=400, detail="level must be 'sme' or 'owner'")

    try:
        req = get_requirement_by_id(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=404, detail=f"{req_id} not found for engagement {engagement_id}")

    current_status = req.get("sign_off_status", "draft")
    if body.level == "sme":
        new_status = "sme_approved"
    elif current_status == "sme_approved":
        new_status = "confirmed"
    else:
        new_status = "owner_approved"

    now = datetime.now(timezone.utc).isoformat()
    updates = {
        "sign_off_status": new_status,
        "sign_off_by": body.signed_by,
        "sign_off_at": now,
    }
    try:
        updated = update_requirement(req_id, engagement_id, updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail=f"{req_id} not found for engagement {engagement_id}")
    return updated


@router.get("/requirements/{req_id}/traceability")
def get_traceability(req_id: str, engagement_id: str):
    try:
        req = get_requirement_by_id(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=404, detail=f"{req_id} not found for engagement {engagement_id}")

    try:
        gap_records = get_gap_results_by_req_id(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Derive answer_to from requirement fields
    tags = req.get("tags") or []
    pain_tags = {"pain_point", "manual_step", "workaround"}
    pain_points = [t for t in tags if t in pain_tags]
    actors = req.get("actors") or []
    actor_names = [a.get("role", "") for a in actors if isinstance(a, dict)]
    who_asked_parts = [req.get("stakeholder")] + actor_names
    who_asked = ", ".join(p for p in who_asked_parts if p)

    description = req.get("description", "")
    why_needed = description[:200] + ("..." if len(description) > 200 else "")
    what_problem = (
        f"Tags indicate: {', '.join(pain_points)}. " if pain_points else ""
    ) + (
        f"Shadow tools in use: {', '.join(req.get('shadow_tools') or [])}." if req.get("shadow_tools") else ""
    )

    return {
        "requirement": req,
        "as_is_evidence": {
            "current_state_ref": req.get("current_state_ref"),
            "actors": actors,
            "shadow_tools": req.get("shadow_tools"),
            "tags": tags,
        },
        "gap_analysis": {
            "matches": gap_records[0].get("matches") if gap_records else [],
            "total_analyses": len(gap_records),
        },
        "answer_to": {
            "why_needed": why_needed,
            "who_asked": who_asked or "Unknown",
            "what_problem": what_problem or "No pain points tagged",
        },
    }


# ── Gap Analysis ──────────────────────────────────────────────────────────────

@router.post("/gap-analysis", response_model=GapAnalysisResponse)
async def gap_analysis(request: GapAnalysisRequest):
    # Resolve process_description: from req_id lookup or direct input
    req_id = request.req_id
    process_description = request.process_description

    if req_id:
        try:
            req = get_requirement_by_id(req_id, request.engagement_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Requirement lookup failed: {e}")
        if not req:
            raise HTTPException(status_code=404, detail=f"Requirement {req_id} not found for engagement {request.engagement_id}")
        process_description = req["description"]
    elif not process_description:
        raise HTTPException(status_code=422, detail="Provide either process_description or req_id")

    provider = get_provider()
    catalogue = build_catalogue_for_prompt(request.lob_filter)

    system_prompt = """You are an expert SAP S/4HANA implementation consultant specializing in Fit-to-Standard gap analysis.

Your task: Given a business process description, identify the most relevant SAP S/4HANA Cloud Public Edition scope items from the provided catalogue.

Instructions:
1. Analyze the business process description semantically - look beyond keywords to understand intent
2. Return the top matching scope items ranked by relevance
3. For each match, provide confidence (HIGH / MEDIUM / LOW) and a brief rationale
4. Consider that one business requirement often maps to multiple scope items
5. Always return valid JSON only

Response format (JSON array):
[
  {
    "id": "scope_item_code",
    "confidence": "HIGH|MEDIUM|LOW",
    "rationale": "One sentence explaining why this scope item matches"
  }
]"""

    user_prompt = f"""Business Process Description:
{process_description}

SAP S/4HANA Cloud 2602 Scope Item Catalogue (2602 release):
{catalogue}

Return the top {request.top_n} most relevant scope items as JSON."""

    try:
        result = provider.complete(system_prompt, user_prompt)
        raw_text = result.get("content", "[]")
        tokens_used = result.get("tokens_used")

        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON array found in response")

        matches_raw = json.loads(json_match.group())

        scope_lookup = {item['id']: item for item in SCOPE_ITEMS}
        matches = []
        for m in matches_raw[:request.top_n]:
            item_id = m.get('id', '')
            scope = scope_lookup.get(item_id, {})
            if scope:
                matches.append(ScopeItemMatch(
                    id=item_id,
                    name=scope['name'],
                    lob=scope['lob'],
                    process_group=scope['process_group'],
                    description=scope['description'],
                    confidence=m.get('confidence', 'MEDIUM'),
                    rationale=m.get('rationale', ''),
                    migration_objects=scope.get('migration_objects', [])
                ))

        timestamp = datetime.utcnow().isoformat()

        try:
            save_gap_analysis(
                engagement_id=request.engagement_id,
                process_description=process_description,
                matches=[m.dict() for m in matches],
                tokens_used=tokens_used,
                timestamp=timestamp,
                req_id=req_id,
            )
        except Exception as db_err:
            print(f"DB save failed (non-fatal): {db_err}")

        return GapAnalysisResponse(
            engagement_id=request.engagement_id,
            req_id=req_id,
            process_description=process_description,
            matches=matches,
            total_scope_items_searched=len(SCOPE_ITEMS),
            tokens_used=tokens_used,
            timestamp=timestamp
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Engagement Summary ────────────────────────────────────────────────────────

@router.get("/engagement/{engagement_id}/summary")
def get_engagement_summary(engagement_id: str):
    try:
        requirements = get_requirements_by_engagement(engagement_id)
        gap_results = get_results_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    by_status: dict = {}
    for req in requirements:
        s = req.get("status", "open")
        by_status[s] = by_status.get(s, 0) + 1

    by_tag: dict = {}
    for req in requirements:
        for tag in (req.get("tags") or []):
            by_tag[tag] = by_tag.get(tag, 0) + 1

    # Index latest gap result per req_id (most recent first, results ordered desc)
    results_by_req: dict = {}
    for gr in gap_results:
        rid = gr.get("req_id")
        if rid and rid not in results_by_req:
            results_by_req[rid] = gr

    gap_results_summary = []
    for req in requirements:
        if req.get("status") == "analysed":
            rid = req["req_id"]
            gr = results_by_req.get(rid)
            if gr:
                matches = gr.get("matches") or []
                top = matches[0] if matches else {}
                gap_results_summary.append({
                    "req_id": rid,
                    "title": req.get("title"),
                    "top_match_id": top.get("id"),
                    "top_match_name": top.get("name"),
                    "top_confidence": top.get("confidence"),
                })

    return {
        "engagement_id": engagement_id,
        "total_requirements": len(requirements),
        "requirements_by_status": by_status,
        "requirements_by_tag": by_tag,
        "total_analysed": by_status.get("analysed", 0),
        "gap_results_summary": gap_results_summary,
    }


# ── Analyse All ───────────────────────────────────────────────────────────────

@router.post("/engagement/{engagement_id}/analyse-all")
def analyse_all(engagement_id: str):
    try:
        requirements = get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    open_reqs = [r for r in requirements if r.get("status") == "open"]
    if not open_reqs:
        return {"processed": 0, "results": []}

    provider = get_provider()
    results = []

    for req in open_reqs:
        req_id = req["req_id"]
        try:
            matches, tokens_used = _run_gap_analysis(provider, req["description"])
            timestamp = datetime.utcnow().isoformat()
            try:
                save_gap_analysis(
                    engagement_id=engagement_id,
                    process_description=req["description"],
                    matches=[m.dict() for m in matches],
                    tokens_used=tokens_used,
                    timestamp=timestamp,
                    req_id=req_id,
                )
            except Exception as db_err:
                print(f"DB save failed for {req_id} (non-fatal): {db_err}")

            update_requirement(req_id, engagement_id, {"status": "analysed"})

            top = matches[0] if matches else None
            results.append({
                "req_id": req_id,
                "title": req.get("title"),
                "top_match_id": top.id if top else None,
                "top_match_name": top.name if top else None,
            })
        except Exception as e:
            print(f"Analysis failed for {req_id}: {e}")

    return {"processed": len(results), "results": results}


# ── Process Mirror ────────────────────────────────────────────────────────────

@router.get("/engagement/{engagement_id}/process-mirror")
def get_process_mirror(engagement_id: str):
    try:
        requirements = get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    tag_counts: dict = {}
    for req in requirements:
        for tag in (req.get("tags") or []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    by_tag: dict = {}
    untagged = []
    for req in requirements:
        tags = req.get("tags") or []
        entry = {
            "req_id": req["req_id"],
            "title": req.get("title"),
            "description": req.get("description"),
            "stakeholder": req.get("stakeholder"),
        }
        if not tags:
            untagged.append(entry)
        else:
            for tag in tags:
                by_tag.setdefault(tag, []).append(entry)

    return {
        "engagement_id": engagement_id,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_requirements": len(requirements),
            "by_tag": tag_counts,
        },
        "by_tag": by_tag,
        "untagged": untagged,
    }


# ── Sign-off Status ────────────────────────────────────────────────────────────

@router.get("/engagement/{engagement_id}/sign-off-status")
def get_sign_off_status(engagement_id: str):
    try:
        requirements = get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    counts: dict = {"draft": 0, "sme_approved": 0, "owner_approved": 0, "confirmed": 0}
    by_process: dict = {}

    for req in requirements:
        status = req.get("sign_off_status") or "draft"
        counts[status] = counts.get(status, 0) + 1

        process = req.get("business_process") or "Unclassified"
        by_process.setdefault(process, {"draft": 0, "sme_approved": 0, "owner_approved": 0, "confirmed": 0})
        by_process[process][status] = by_process[process].get(status, 0) + 1

    return {
        "engagement_id": engagement_id,
        "total": len(requirements),
        **counts,
        "by_process": by_process,
    }


# ── KPI Summary ────────────────────────────────────────────────────────────────

@router.get("/engagement/{engagement_id}/kpi-summary")
def get_kpi_summary(engagement_id: str):
    try:
        requirements = get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    by_process: dict = {}
    total_with_kpi = 0

    for req in requirements:
        kpi = req.get("kpi_impact")
        if not kpi:
            continue
        total_with_kpi += 1
        process = req.get("business_process") or "Unclassified"
        by_process.setdefault(process, []).append({
            "req_id": req["req_id"],
            "title": req.get("title"),
            "kpi_impact": kpi,
            "priority": req.get("priority"),
            "stakeholder": req.get("stakeholder"),
        })

    return {
        "engagement_id": engagement_id,
        "total_with_kpi": total_with_kpi,
        "by_process": by_process,
    }


# ── Assets ────────────────────────────────────────────────────────────────────

_SUPPORTED_EXTENSIONS = {
    "pdf", "docx", "xlsx", "png", "jpg", "jpeg",
    "mp3", "mp4", "wav", "mov", "txt",
}

_CONTENT_TYPE_MAP = {
    "pdf":  "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "png":  "image/png",
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
    "mp3":  "audio/mpeg",
    "mp4":  "video/mp4",
    "wav":  "audio/wav",
    "mov":  "video/quicktime",
    "txt":  "text/plain",
}


@router.post("/assets/upload", status_code=201)
async def upload_asset(
    file: UploadFile = File(...),
    engagement_id: str = Form(...),
    uploaded_by: Optional[str] = Form(None),
    req_id: Optional[str] = Form(None),
    process_level_2: Optional[str] = Form(None),
    process_level_3: Optional[str] = Form(None),
):
    file_name = file.filename or "unnamed"
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    if ext not in _SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(_SUPPORTED_EXTENSIONS))}",
        )

    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded file: {e}")

    content_type = _CONTENT_TYPE_MAP[ext]

    # Build asset record (asset_id assigned inside create_asset via _next_asset_id)
    asset_data: Dict[str, Any] = {
        "engagement_id": engagement_id,
        "file_name": file_name,
        "file_type": ext,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if uploaded_by:
        asset_data["uploaded_by"] = uploaded_by
    if req_id:
        asset_data["req_id"] = req_id
    if process_level_2:
        asset_data["process_level_2"] = process_level_2
    if process_level_3:
        asset_data["process_level_3"] = process_level_3

    # Extract text for plain-text files
    if ext == "txt":
        try:
            asset_data["extracted_text"] = file_bytes.decode("utf-8", errors="replace")
        except Exception:
            pass

    # Create DB record first to get asset_id, then upload to storage
    try:
        asset = create_asset(asset_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create asset record: {e}")

    if not asset:
        raise HTTPException(status_code=500, detail="Failed to create asset record")

    asset_id = asset["asset_id"]

    try:
        storage_url = upload_file_to_storage(engagement_id, asset_id, file_name, file_bytes, content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {e}")

    try:
        asset = update_asset(asset_id, {"storage_url": storage_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save storage URL: {e}")

    return {
        "asset_id": asset_id,
        "file_name": file_name,
        "file_type": ext,
        "storage_url": storage_url,
        "engagement_id": engagement_id,
    }


@router.get("/assets")
def list_assets(engagement_id: str):
    try:
        assets = get_assets_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"engagement_id": engagement_id, "total": len(assets), "assets": assets}


@router.get("/assets/requirement/{req_id}")
def list_assets_for_requirement(req_id: str, engagement_id: str):
    try:
        assets = get_assets_by_requirement(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"req_id": req_id, "engagement_id": engagement_id, "total": len(assets), "assets": assets}


@router.patch("/assets/{asset_id}")
def patch_asset(asset_id: UUID, body: AssetUpdate):
    aid = str(asset_id)
    updates = {k: v for k, v in body.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    try:
        asset = update_asset(aid, updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not asset:
        raise HTTPException(status_code=404, detail=f"{aid} not found")
    return asset


# ── Process Hierarchy (Sprint 4) ───────────────────────────────────────────────

_PROCESS_HIERARCHY: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    "Finance": {
        "Record to Report": {
            "General Ledger":       ["Journal Entry", "Period Close", "Financial Statements"],
            "Accounts Payable":     ["Invoice Entry", "Payment Run", "Vendor Reconciliation"],
            "Accounts Receivable":  ["Customer Invoice", "Cash Application", "Dunning"],
            "Asset Accounting":     ["Asset Acquisition", "Depreciation Run", "Asset Retirement"],
            "Tax Compliance":       ["Tax Return", "Tax Reporting", "Withholding Tax"],
            "Period Close":         ["Month-End Close", "Year-End Close", "Accruals"],
            "Intercompany":         ["Intercompany Billing", "Intercompany Reconciliation", "Elimination"],
            "Treasury":             ["Bank Account Management", "Cash Position", "Liquidity Planning"],
            "Cash Management":      ["Cash Flow Forecast", "Bank Statement", "Payment Advice"],
        },
        "Management Accounting": {
            "Cost Center Accounting":    ["Cost Allocation", "Assessment", "Distribution"],
            "Internal Orders":           ["Order Settlement", "Budget Monitoring", "Cost Collection"],
            "Profit Center":             ["Profit Center Assignment", "Transfer Pricing", "Reporting"],
            "Product Costing":           ["Standard Cost Estimate", "Actual Costing", "Variance Analysis"],
            "Profitability Analysis":    ["Contribution Margin", "Segment Reporting", "CO-PA Settlement"],
            "Planning and Budgeting":    ["Annual Budget", "Rolling Forecast", "Plan Upload"],
        },
        "Group Reporting": {
            "Legal Consolidation":      ["Consolidation Entry", "Minority Interest", "Statutory Report"],
            "Management Consolidation": ["Management Report", "Segment Elimination", "Interunit Reconciliation"],
        },
    },
    "Sourcing and Procurement": {
        "Procure to Pay": {
            "Purchase Requisition": ["PR Creation", "PR Approval", "PR Conversion"],
            "Purchase Order":       ["PO Creation", "PO Approval", "PO Amendment"],
            "Goods Receipt":        ["GR Posting", "Quality Inspection", "Tolerance Check"],
            "Invoice Verification": ["Invoice Entry", "3-Way Match", "Exception Handling"],
            "Supplier Payment":     ["Payment Proposal", "Payment Run", "Bank Transfer"],
        },
        "Supplier Management": {
            "Supplier Evaluation":    ["Scorecard", "KPI Tracking", "Audit"],
            "Supplier Qualification": ["Onboarding", "Risk Assessment", "Certification"],
            "Contract Management":    ["Contract Creation", "Contract Renewal", "Compliance Monitoring"],
        },
        "Sourcing": {
            "RFQ":          ["RFQ Creation", "Supplier Invitation", "Response Collection"],
            "Bid Evaluation": ["Price Comparison", "Technical Evaluation", "Scoring"],
            "Award":        ["Award Decision", "Contract Award", "PO Creation"],
        },
    },
    "Sales": {
        "Order to Cash": {
            "Quotation":    ["Quotation Creation", "Pricing", "Approval"],
            "Sales Order":  ["Order Entry", "Order Confirmation", "Credit Check"],
            "Delivery":     ["Picking", "Packing", "Goods Issue"],
            "Goods Issue":  ["Stock Reduction", "Delivery Completion", "Shipment"],
            "Billing":      ["Invoice Creation", "Revenue Recognition", "Tax Calculation"],
            "Cash Collection": ["Payment Receipt", "Bank Reconciliation", "Cash Application"],
        },
        "Customer Management": {
            "Credit Management": ["Credit Limit", "Credit Check", "Risk Classification"],
            "Returns":           ["Return Order", "Goods Receipt", "Credit Memo"],
            "Complaints":        ["Complaint Entry", "Root Cause Analysis", "Resolution"],
            "Rebates":           ["Rebate Agreement", "Accrual", "Settlement"],
        },
        "Contract Management": {
            "Customer Contracts":    ["Contract Creation", "Renewal", "Termination"],
            "Subscription Management": ["Subscription Order", "Billing Schedule", "Renewal"],
        },
    },
    "Supply Chain": {
        "Inventory Management": {
            "Goods Movement":    ["Goods Issue", "Goods Receipt", "Transfer Posting"],
            "Stock Transfer":    ["STO Creation", "Delivery", "Goods Receipt"],
            "Physical Inventory": ["Inventory Count", "Difference Posting", "Count Document"],
            "Batch Management":  ["Batch Creation", "Batch Classification", "Shelf Life"],
        },
        "Warehouse Management": {
            "Inbound Processing":  ["Putaway", "Goods Receipt", "Deconsolidation"],
            "Outbound Processing": ["Pick", "Pack", "Ship"],
            "Internal Warehouse":  ["Stock Transfer", "Replenishment", "Inventory"],
            "Yard Management":     ["Truck Arrival", "Door Assignment", "Departure"],
        },
        "Transportation": {
            "Freight Order":     ["Freight Order Creation", "Carrier Assignment", "Execution"],
            "Carrier Selection": ["Rate Comparison", "Tender", "Award"],
            "Freight Settlement": ["Freight Cost", "Invoice Verification", "Payment"],
        },
        "Demand and Supply Planning": {
            "Demand Forecasting": ["Statistical Forecast", "Consensus Demand", "Adjustment"],
            "MRP":               ["MRP Run", "Planned Order", "Exception Messages"],
            "Supply Planning":   ["Supply Network", "Heuristics", "Optimizer"],
            "ATP":               ["ATP Check", "Backorder Processing", "Confirmation"],
        },
    },
    "Manufacturing": {
        "Plan to Produce": {
            "Production Order":         ["Order Creation", "Release", "Confirmation"],
            "Process Order":            ["Batch Production", "Process Instruction", "GR"],
            "Repetitive Manufacturing": ["Rate-Based Planning", "Backflush", "Reporting"],
            "Kanban":                   ["Kanban Signal", "Replenishment", "Status Update"],
        },
        "Quality Management": {
            "Inspection Planning": ["Inspection Plan", "Sampling Procedure", "Characteristic"],
            "Inspection Lot":      ["Lot Creation", "Sample Drawing", "Results Recording"],
            "Usage Decision":      ["Acceptance", "Rejection", "Follow-Up Action"],
            "Defect Recording":    ["Defect Notification", "Root Cause", "CAPA"],
        },
        "Engineering": {
            "BOM Management":    ["BOM Creation", "BOM Change", "Validity"],
            "Routing":           ["Operation", "Work Center", "Standard Values"],
            "Engineering Change": ["Change Order", "Revision Level", "Implementation"],
        },
    },
    "Asset Management": {
        "Maintain to Operate": {
            "Preventive Maintenance":  ["Maintenance Plan", "Scheduling", "Work Order"],
            "Corrective Maintenance":  ["Breakdown Notification", "Repair Order", "Completion"],
            "Predictive Maintenance":  ["Condition Monitoring", "Alert", "Predictive Work Order"],
            "Calibration":             ["Calibration Plan", "Measurement", "Certificate"],
        },
        "Asset Lifecycle": {
            "Asset Acquisition": ["Asset Creation", "Capitalization", "Settlement"],
            "Depreciation":      ["Depreciation Run", "Adjustment", "Reporting"],
            "Asset Retirement":  ["Retirement Posting", "Disposal", "Write-off"],
        },
    },
    "Human Resources": {
        "Hire to Retire": {
            "Recruitment":    ["Job Posting", "Application Review", "Offer"],
            "Onboarding":     ["New Hire Setup", "Equipment", "Training"],
            "Time Management": ["Time Recording", "Approval", "Absence"],
            "Payroll":        ["Payroll Run", "Posting", "Pay Slip"],
            "Offboarding":    ["Exit Interview", "Clearance", "Final Settlement"],
        },
        "Talent Management": {
            "Performance":   ["Goal Setting", "Mid-Year Review", "Annual Appraisal"],
            "Learning":      ["Course Assignment", "Completion", "Certification"],
            "Compensation":  ["Salary Review", "Bonus", "Equity"],
        },
    },
    "Professional Services": {
        "Project to Cash": {
            "Project Planning":   ["WBS", "Scheduling", "Budgeting"],
            "Resource Management": ["Resource Request", "Assignment", "Utilization"],
            "Time Recording":     ["Timesheet", "Approval", "Cost Posting"],
            "Project Billing":    ["Milestone Billing", "T&M Billing", "Revenue Recognition"],
        },
    },
}


@router.get("/process-hierarchy")
def get_process_hierarchy():
    return _PROCESS_HIERARCHY


@router.get("/process-hierarchy/flat")
def get_process_hierarchy_flat():
    flat = []
    for lob, level2_map in _PROCESS_HIERARCHY.items():
        for level2, level3_map in level2_map.items():
            for level3, level4 in level3_map.items():
                flat.append({
                    "lob": lob,
                    "level2": level2,
                    "level3": level3,
                    "level4": level4,
                })
    return flat


# ── Process Flow (Sprint 5) ────────────────────────────────────────────────────

def _build_process_flow(requirements: list, engagement_id: str) -> dict:
    """Build the swimlane / edge / stats payload from a list of requirement dicts."""
    # Group nodes by (lob, level2); requirements without both go to unassigned
    grouped: Dict[tuple, list] = {}
    unassigned_nodes: list = []

    for req in requirements:
        tags = req.get("tags") or []
        node = {
            "id": req["req_id"],
            "label": req.get("title", ""),
            "tags": tags,
            "priority": req.get("priority"),
            "status": req.get("status"),
            "pain_point": "pain_point" in tags,
            "secret_sauce": "secret_sauce" in tags,
            "manual_step": "manual_step" in tags,
            "process_level_3": req.get("process_level_3"),
        }
        lob = req.get("business_process")
        level2 = req.get("process_level_2")
        if lob and level2:
            grouped.setdefault((lob, level2), []).append(node)
        else:
            unassigned_nodes.append(node)

    # Build ordered swimlanes
    swimlanes = [
        {"lob": lob, "level2": level2, "nodes": nodes}
        for (lob, level2), nodes in sorted(grouped.items())
    ]
    if unassigned_nodes:
        swimlanes.append({"lob": "Unassigned", "level2": "Unassigned", "nodes": unassigned_nodes})

    # Edges: sequential links between requirements sharing the same level2 group
    edges: list = []
    for (_, _), nodes in sorted(grouped.items()):
        req_ids = [n["id"] for n in nodes]
        for i in range(len(req_ids) - 1):
            edges.append({"source": req_ids[i], "target": req_ids[i + 1], "label": "same process"})

    # Stats
    def _count_tag(tag: str) -> int:
        return sum(1 for r in requirements if tag in (r.get("tags") or []))

    return {
        "engagement_id": engagement_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "swimlanes": swimlanes,
        "edges": edges,
        "stats": {
            "total_nodes": len(requirements),
            "pain_points": _count_tag("pain_point"),
            "manual_steps": _count_tag("manual_step"),
            "secret_sauce": _count_tag("secret_sauce"),
            "unassigned_process": len(unassigned_nodes),
        },
    }


@router.get("/engagement/{engagement_id}/process-flow")
def get_process_flow(engagement_id: str):
    try:
        requirements = get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return _build_process_flow(requirements, engagement_id)


@router.post("/engagement/{engagement_id}/process-flow/assign")
def assign_process_flow(engagement_id: str, body: ProcessFlowAssignRequest):
    updates: Dict[str, Any] = {"process_level_2": body.process_level_2}
    if body.process_level_3 is not None:
        updates["process_level_3"] = body.process_level_3
    try:
        updated = update_requirement(body.req_id, engagement_id, updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"{body.req_id} not found in engagement {engagement_id}",
        )
    try:
        requirements = get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return _build_process_flow(requirements, engagement_id)


# ── Process Steps (Sprint 6) ───────────────────────────────────────────────────

_VALID_SHAPES = {"start", "end", "process", "decision", "document"}
_VALID_STEP_TYPES = {"manual", "system", "agentic"}

_STEP_EXTRACT_SYSTEM_PROMPT = """You are a senior business analyst mapping As-Is process flows for SAP S/4HANA implementations.

Given a business requirement and its conversation transcript, extract the As-Is process steps as a structured JSON array.

For each step infer:
- step_number: integer starting at 1, in execution order
- title: short action label (max 8 words)
- description: what actually happens at this step
- performer_name: the person's name or generic role name who does it
- performer_role: their job title or function
- shape: choose from → "start" (first step only), "end" (last step only), "decision" (approval/check/condition), "document" (form/report/record), "process" (default action)
- step_type: "manual" if done by a human without system, "system" if automated/done in a system, "agentic" if AI-driven
- duration_minutes: estimated time in minutes if mentioned or inferable, null otherwise
- systems_used: list of IT systems or tools mentioned for this step (e.g. ["SAP ECC", "Excel"])
- kpis: object with nullable float fields → {"error_rate_pct": null, "volume_per_month": null, "rework_rate_pct": null}
- is_pain_point: true if words like "manual", "error-prone", "time-consuming", "tedious", "slow", "broken", "workaround" apply
- next_step_id: null (will be assigned after creation)
- branches: for decision nodes only → [{"label": "Approved", "target_step_id": null}, {"label": "Rejected", "target_step_id": null}], else null

Return a JSON array only — no markdown fences, no commentary.

Example shape rules:
- Approval step → shape="decision", branches=[{"label":"Approved","target_step_id":null},{"label":"Rejected","target_step_id":null}]
- Filling in a form → shape="document"
- Starting trigger → shape="start"
- Final confirmation → shape="end"
- Everything else → shape="process"

If the transcript is empty or insufficient, generate a realistic 5-step As-Is process based on the requirement title and description."""


def _sample_steps_for_requirement(req: dict) -> list:
    """Generate 5 generic sample process steps based on the requirement title."""
    title = req.get("title", "Business Process")
    process = req.get("business_process", "Operations")
    return [
        {
            "step_number": 1,
            "title": f"Receive {title} request",
            "description": f"Requestor submits a new {title} request via email or paper form to the responsible team.",
            "performer_name": "Requestor",
            "performer_role": "Business User",
            "shape": "start",
            "step_type": "manual",
            "duration_minutes": 10.0,
            "systems_used": ["Email"],
            "kpis": {"error_rate_pct": None, "volume_per_month": None, "rework_rate_pct": None},
            "is_pain_point": False,
            "next_step_id": None,
            "branches": None,
        },
        {
            "step_number": 2,
            "title": "Log and validate request",
            "description": f"The {process} team logs the request in a spreadsheet and checks for completeness and duplicates.",
            "performer_name": "Process Owner",
            "performer_role": "Team Lead",
            "shape": "process",
            "step_type": "manual",
            "duration_minutes": 20.0,
            "systems_used": ["Excel"],
            "kpis": {"error_rate_pct": 12.0, "volume_per_month": None, "rework_rate_pct": None},
            "is_pain_point": True,
            "next_step_id": None,
            "branches": None,
        },
        {
            "step_number": 3,
            "title": "Management approval",
            "description": "Manager reviews the request and approves or rejects via email. No formal workflow exists.",
            "performer_name": "Line Manager",
            "performer_role": "Manager",
            "shape": "decision",
            "step_type": "manual",
            "duration_minutes": 1440.0,
            "systems_used": ["Email"],
            "kpis": {"error_rate_pct": None, "volume_per_month": None, "rework_rate_pct": None},
            "is_pain_point": True,
            "next_step_id": None,
            "branches": [
                {"label": "Approved", "target_step_id": None},
                {"label": "Rejected", "target_step_id": None},
            ],
        },
        {
            "step_number": 4,
            "title": "Process and record outcome",
            "description": f"The approved {title} is processed and the result is recorded in the relevant system.",
            "performer_name": "Clerk",
            "performer_role": "Operations Clerk",
            "shape": "document",
            "step_type": "system",
            "duration_minutes": 30.0,
            "systems_used": ["ERP System"],
            "kpis": {"error_rate_pct": None, "volume_per_month": 200.0, "rework_rate_pct": 8.0},
            "is_pain_point": False,
            "next_step_id": None,
            "branches": None,
        },
        {
            "step_number": 5,
            "title": "Notify requestor of completion",
            "description": "Requestor is notified by email that the process is complete.",
            "performer_name": "Process Owner",
            "performer_role": "Team Lead",
            "shape": "end",
            "step_type": "manual",
            "duration_minutes": 5.0,
            "systems_used": ["Email"],
            "kpis": {"error_rate_pct": None, "volume_per_month": None, "rework_rate_pct": None},
            "is_pain_point": False,
            "next_step_id": None,
            "branches": None,
        },
    ]


@router.get("/requirements/{req_id}/process-steps")
def list_process_steps(req_id: str, engagement_id: str):
    try:
        steps = get_process_steps(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"req_id": req_id, "engagement_id": engagement_id, "total": len(steps), "steps": steps}


@router.post("/requirements/{req_id}/process-steps/seed", status_code=201)
def seed_process_steps(req_id: str, engagement_id: str):
    """Create 5 sample process steps for a requirement that has no steps yet."""
    try:
        existing = get_process_steps(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if existing:
        return {"req_id": req_id, "seeded": 0, "steps": existing, "message": "Steps already exist"}

    try:
        req = get_requirement_by_id(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=404, detail=f"{req_id} not found for engagement {engagement_id}")

    sample = _sample_steps_for_requirement(req)
    created = []
    for s in sample:
        try:
            step = create_process_step({"req_id": req_id, "engagement_id": engagement_id, **s})
            if step:
                created.append(step)
        except Exception as e:
            print(f"Failed to seed step {s['step_number']}: {e}")

    return {"req_id": req_id, "seeded": len(created), "steps": created}


@router.post("/requirements/{req_id}/process-steps/extract", status_code=201)
def extract_process_steps(req_id: str, engagement_id: str):
    """AI-extract As-Is process steps from the requirement's transcript. Clears existing steps first."""
    try:
        req = get_requirement_by_id(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=404, detail=f"{req_id} not found for engagement {engagement_id}")

    transcript = req.get("raw_input") or ""
    title = req.get("title", "")
    description = req.get("description", "")

    if not transcript.strip():
        steps_data = _sample_steps_for_requirement(req)
    else:
        provider = get_provider()
        user_prompt = (
            f"Requirement title: {title}\n"
            f"Requirement description: {description}\n\n"
            f"Conversation transcript:\n{transcript}\n\n"
            "Extract the As-Is process steps as a JSON array."
        )
        try:
            # Use cheaper model and cap tokens for step extraction
            result = provider.complete(_STEP_EXTRACT_SYSTEM_PROMPT, user_prompt, max_tokens=768, model=MODEL_HAIKU)
            raw_text = result.get("content", "[]")
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON array in response")
            steps_data = json.loads(json_match.group())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    # Clear existing steps for this req
    try:
        existing = get_process_steps(req_id, engagement_id)
        for s in existing:
            delete_process_step(s["id"], req_id, engagement_id)
    except Exception as e:
        print(f"Step cleanup warning (non-fatal): {e}")

    # Validate and persist
    created = []
    for i, s in enumerate(steps_data, start=1):
        shape = s.get("shape", "process")
        if shape not in _VALID_SHAPES:
            shape = "process"
        step_type = s.get("step_type", "manual")
        if step_type not in _VALID_STEP_TYPES:
            step_type = "manual"
        kpis = s.get("kpis") or {}
        kpis_clean = {
            "error_rate_pct": kpis.get("error_rate_pct"),
            "volume_per_month": kpis.get("volume_per_month"),
            "rework_rate_pct": kpis.get("rework_rate_pct"),
        }
        record = {
            "req_id": req_id,
            "engagement_id": engagement_id,
            "step_number": s.get("step_number", i),
            "title": s.get("title", f"Step {i}"),
            "description": s.get("description", ""),
            "performer_name": s.get("performer_name", ""),
            "performer_role": s.get("performer_role", ""),
            "shape": shape,
            "step_type": step_type,
            "duration_minutes": s.get("duration_minutes"),
            "systems_used": s.get("systems_used") or [],
            "kpis": kpis_clean,
            "is_pain_point": bool(s.get("is_pain_point", False)),
            "next_step_id": s.get("next_step_id"),
            "branches": s.get("branches"),
        }
        try:
            step = create_process_step(record)
            if step:
                created.append(step)
        except Exception as e:
            print(f"Failed to create step {i}: {e}")

    return {"req_id": req_id, "engagement_id": engagement_id, "extracted": len(created), "steps": created}


@router.post("/requirements/{req_id}/process-steps", status_code=201)
def create_step(req_id: str, engagement_id: str, body: ProcessStepCreate):
    if body.shape not in _VALID_SHAPES:
        raise HTTPException(status_code=400, detail=f"Invalid shape '{body.shape}'. Must be one of: {sorted(_VALID_SHAPES)}")
    if body.step_type not in _VALID_STEP_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid step_type '{body.step_type}'. Must be one of: {sorted(_VALID_STEP_TYPES)}")
    data = body.dict()
    data["req_id"] = req_id
    data["engagement_id"] = engagement_id
    try:
        step = create_process_step(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not step:
        raise HTTPException(status_code=500, detail="Failed to create process step")
    return step


@router.put("/requirements/{req_id}/process-steps/{step_id}")
def update_step(req_id: str, step_id: UUID, engagement_id: str, body: ProcessStepUpdate):
    step_id_str = str(step_id)
    updates = {k: v for k, v in body.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    if "shape" in updates and updates["shape"] not in _VALID_SHAPES:
        raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {sorted(_VALID_SHAPES)}")
    if "step_type" in updates and updates["step_type"] not in _VALID_STEP_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid step_type. Must be one of: {sorted(_VALID_STEP_TYPES)}")
    try:
        step = update_process_step(step_id_str, req_id, engagement_id, updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not step:
        raise HTTPException(status_code=404, detail=f"Step {step_id_str} not found")
    return step


@router.delete("/requirements/{req_id}/process-steps/{step_id}", status_code=204)
def delete_step(req_id: str, step_id: UUID, engagement_id: str):
    try:
        deleted = delete_process_step(str(step_id), req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Step {step_id_str} not found")
    return None


@router.post("/engagement/{engagement_id}/seed-process-steps", status_code=201)
def seed_all_process_steps(engagement_id: str):
    """Seed sample process steps for every requirement in the engagement that has none."""
    try:
        requirements = get_requirements_by_engagement(engagement_id)
        existing_steps = get_process_steps_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    reqs_with_steps = {s["req_id"] for s in existing_steps}
    seeded_reqs = []

    for req in requirements:
        req_id = req["req_id"]
        if req_id in reqs_with_steps:
            continue
        sample = _sample_steps_for_requirement(req)
        count = 0
        for s in sample:
            try:
                step = create_process_step({"req_id": req_id, "engagement_id": engagement_id, **s})
                if step:
                    count += 1
            except Exception as e:
                print(f"Seed failed for {req_id} step {s['step_number']}: {e}")
        if count:
            seeded_reqs.append({"req_id": req_id, "title": req.get("title"), "steps_created": count})

    return {
        "engagement_id": engagement_id,
        "requirements_seeded": len(seeded_reqs),
        "seeded": seeded_reqs,
    }


# ── Excel Upload / Download for Requirements (Sprint 6) ────────────────────────

_EXCEL_TAGS_ALLOWED = {"pain_point", "manual_step", "secret_sauce", "workaround", "hand_off"}


def _parse_excel_tags(raw: Optional[str]) -> List[str]:
    """Parse a tags cell from Excel into canonical tag list."""
    if not raw:
        return []
    parts = re.split(r"[;,]", str(raw))
    result: List[str] = []
    for p in parts:
        norm = _normalize_tag(p)
        if norm in _EXCEL_TAGS_ALLOWED and norm not in result:
            result.append(norm)
    return result


@router.get("/engagement/{engagement_id}/requirements/export")
def export_requirements_excel(engagement_id: str):
    """Download all requirements for an engagement as an Excel file."""
    try:
        requirements = get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    wb = Workbook()
    ws = wb.active
    ws.title = "Requirements"

    headers = [
        "req_id",
        "reference_id",
        "engagement_id",
        "title",
        "description",
        "business_process",
        "priority",
        "category",
        "tags",
        "stakeholder",
        "sign_off_status",
        "business_value",
        "current_system",
        "target_system_module",
        "fit_type",
        "related_test_case_id",
    ]
    ws.append(headers)

    for r in requirements:
        tags = r.get("tags") or []
        tags_str = ", ".join(tags)
        ws.append([
            r.get("req_id"),
            r.get("reference_id"),
            r.get("engagement_id"),
            r.get("title"),
            r.get("description"),
            r.get("business_process"),
            r.get("priority"),
            r.get("category"),
            tags_str,
            r.get("stakeholder"),
            r.get("sign_off_status"),
            r.get("business_value"),
            r.get("current_system"),
            r.get("target_system_module"),
            r.get("fit_type"),
            r.get("related_test_case_id"),
        ])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"{engagement_id}_requirements.xlsx"
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _normalize_header_cell(c: Any) -> str:
    if c is None:
        return ""
    return str(c).strip().lower()


def _rtm_find_header_row(rows: List[tuple]) -> Optional[int]:
    """Return row index of RTM header (row with 'Requirement ID', 'Requirement Title', 'Requirement Description')."""
    for idx, row in enumerate(rows[:5]):
        header = [_normalize_header_cell(c) for c in row]
        if any("requirement id" in h for h in header) and any("requirement title" in h for h in header) and any("requirement description" in h for h in header):
            return idx
    return None


def _priority_rtm_to_rapid(p: Optional[str]) -> Optional[str]:
    if not p:
        return None
    p = p.strip().lower()
    if p in ("high", "must", "must-have"):
        return "Must-Have"
    if p in ("medium", "should", "should-have"):
        return "Should-Have"
    if p in ("low", "could", "nice", "nice-to-have"):
        return "Nice-to-Have"
    return p.title() if p else None


def _status_rtm_to_rapid(s: Optional[str]) -> str:
    if not s:
        return "open"
    s = s.strip().lower()
    if s in ("planned", "draft", "new"):
        return "open"
    if s in ("in progress", "in_progress", "inprogress"):
        return "in_progress"
    if s in ("analysed", "analyzed", "done", "complete"):
        return "analysed"
    if s in ("closed", "cancelled"):
        return "closed"
    return "open"


@router.post("/engagement/{engagement_id}/requirements/import")
async def import_requirements_excel(engagement_id: str, file: UploadFile = File(...)):
    """Upload an Excel file to create or update requirements for an engagement.

    Supports two formats:
    - RTM format: Header row contains 'Requirement ID', 'Requirement Title', 'Requirement Description'
      (e.g. RAPID_RTM_Acme_S4.xlsx). Uses internal REQ-XXX ids; stores Excel Requirement ID in reference_id.
    - Legacy format: Header row contains 'req_id', 'title', 'description'. Existing req_id updates; blank creates new.
    """
    filename = file.filename or ""
    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx Excel files are supported")

    try:
        contents = await file.read()
        wb = load_workbook(io.BytesIO(contents), data_only=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read Excel file: {e}")

    ws = wb["RTM"] if "RTM" in wb.sheetnames else wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise HTTPException(status_code=400, detail="Excel file is empty")

    def _cell(row_values, idx: Optional[int]) -> Optional[str]:
        if idx is None or idx >= len(row_values):
            return None
        value = row_values[idx]
        if value is None:
            return None
        return str(value).strip() or None

    # Detect RTM format: find row with Requirement ID, Requirement Title, Requirement Description
    rtm_header_row = _rtm_find_header_row(rows)
    if rtm_header_row is not None:
        header = [_normalize_header_cell(c) for c in rows[rtm_header_row]]
        data_start = rtm_header_row + 1

        def _rtm_col(name_substr: str) -> Optional[int]:
            for i, h in enumerate(header):
                if name_substr in h:
                    return i
            return None

        # Requirement ID = Excel/source ID (stored as reference_id); must not be "requirement title"
        col_ref_id = next((i for i, h in enumerate(header) if h == "requirement id" or (h and "requirement id" in h and "title" not in h)), _rtm_col("requirement id"))
        col_title = _rtm_col("requirement title")
        col_desc = _rtm_col("requirement description")
        col_bp = _rtm_col("business process")
        col_sub = _rtm_col("sub-process")
        col_type = _rtm_col("requirement type")
        col_priority = _rtm_col("priority")
        col_biz_val = _rtm_col("business value")
        col_source = _rtm_col("source")
        col_cur_sys = _rtm_col("current system")
        col_tgt_sys = _rtm_col("target system")
        col_fit = _rtm_col("fit type")
        col_tc = _rtm_col("test case")
        col_status = _rtm_col("status")

        if col_title is None or col_desc is None:
            raise HTTPException(status_code=400, detail="RTM sheet must contain Requirement Title and Requirement Description columns")

        created_ids: List[str] = []
        errors: List[Dict[str, Any]] = []
        for row_idx, row in enumerate(rows[data_start:], start=data_start + 1):
            if not any(row):
                continue
            title = _cell(row, col_title)
            description = _cell(row, col_desc)
            if not title or not description:
                errors.append({"row": row_idx, "error": "Missing title or description"})
                continue
            reference_id = _cell(row, col_ref_id)
            if not reference_id:
                errors.append({"row": row_idx, "error": "Missing Requirement ID (reference_id)"})
                continue
            try:
                created = create_requirement(
                    engagement_id=engagement_id,
                    title=title,
                    description=description,
                    source_type="Excel",
                    reference_id=reference_id,
                    business_process=_cell(row, col_bp),
                    process_level_2=_cell(row, col_sub),
                    category=_cell(row, col_type),
                    priority=_priority_rtm_to_rapid(_cell(row, col_priority)),
                    stakeholder=_cell(row, col_source),
                    status=_status_rtm_to_rapid(_cell(row, col_status)),
                    business_value=_cell(row, col_biz_val),
                    current_system=_cell(row, col_cur_sys),
                    target_system_module=_cell(row, col_tgt_sys),
                    fit_type=_cell(row, col_fit),
                    related_test_case_id=_cell(row, col_tc),
                )
                if created:
                    created_ids.append(created.get("req_id"))
            except Exception as e:
                errors.append({"row": row_idx, "error": str(e)})

        return {
            "engagement_id": engagement_id,
            "format": "RTM",
            "created": len(created_ids),
            "updated": 0,
            "created_req_ids": created_ids,
            "updated_req_ids": [],
            "errors": errors,
        }

    # Legacy format: header in first row
    header = [_normalize_header_cell(c) for c in rows[0]]

    def _col(name: str) -> Optional[int]:
        try:
            return header.index(name)
        except ValueError:
            return None

    col_req_id = _col("req_id")
    col_title = _col("title")
    col_desc = _col("description")
    col_bp = _col("business_process")
    col_priority = _col("priority")
    col_category = _col("category")
    col_tags = _col("tags")
    col_stakeholder = _col("stakeholder")
    col_sign_off_status = _col("sign_off_status")

    if col_title is None or col_desc is None:
        raise HTTPException(status_code=400, detail="Excel must contain 'title' and 'description' header columns")

    try:
        existing = get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    existing_by_req = {r.get("req_id"): r for r in existing if r.get("req_id")}

    created_ids = []
    updated_ids = []
    errors = []

    for row_idx, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue
        title = _cell(row, col_title)
        description = _cell(row, col_desc)
        if not title or not description:
            errors.append({"row": row_idx, "error": "Missing title or description"})
            continue
        req_id = _cell(row, col_req_id)
        tags_raw = _cell(row, col_tags)
        tags = _parse_excel_tags(tags_raw)
        payload = {"title": title, "description": description}
        bp = _cell(row, col_bp)
        if bp:
            payload["business_process"] = bp
        priority = _cell(row, col_priority)
        if priority:
            payload["priority"] = priority
        category = _cell(row, col_category)
        if category:
            payload["category"] = category
        stakeholder = _cell(row, col_stakeholder)
        if stakeholder:
            payload["stakeholder"] = stakeholder
        sign_off_status = _cell(row, col_sign_off_status)
        if sign_off_status:
            payload["sign_off_status"] = sign_off_status
        try:
            if req_id and req_id in existing_by_req:
                updates = {k: v for k, v in payload.items() if k not in {"title", "description"}}
                updates["title"] = title
                updates["description"] = description
                if tags:
                    updates["tags"] = tags
                updated = update_requirement(req_id=req_id, engagement_id=engagement_id, updates=updates)
                if updated:
                    updated_ids.append(updated.get("req_id", req_id))
            else:
                created = create_requirement(
                    engagement_id=engagement_id,
                    title=title,
                    description=description,
                    source_type="Excel",
                    tags=tags,
                    business_process=payload.get("business_process"),
                    priority=payload.get("priority"),
                    category=payload.get("category"),
                    stakeholder=payload.get("stakeholder"),
                    sign_off_status=payload.get("sign_off_status"),
                )
                if created:
                    created_ids.append(created.get("req_id"))
        except Exception as e:
            errors.append({"row": row_idx, "error": str(e)})

    return {
        "engagement_id": engagement_id,
        "created": len(created_ids),
        "updated": len(updated_ids),
        "created_req_ids": created_ids,
        "updated_req_ids": updated_ids,
        "errors": errors,
    }


# ── RICEFW Customisation Inventory (Sprint 7) ──────────────────────────────────

_RICEFW_TYPES = {"R", "I", "C", "E", "F", "W", "A"}
_RICEFW_STATUSES = {"identified", "approved", "in_development", "delivered", "cancelled"}


@router.get("/engagement/{engagement_id}/ricefw")
def list_ricefw(engagement_id: str, type: Optional[str] = None):
    """List RICEFW customisation items for an engagement. type filter: R | I | C | E | F | W."""
    if type and type.upper() not in _RICEFW_TYPES:
        raise HTTPException(status_code=400, detail=f"type must be one of: {', '.join(sorted(_RICEFW_TYPES))}")
    try:
        items = get_ricefw_by_engagement(engagement_id, type=type.upper() if type else None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"engagement_id": engagement_id, "total": len(items), "items": items}


@router.get("/engagement/{engagement_id}/ricefw/export")
def export_ricefw_excel(engagement_id: str, type: Optional[str] = None):
    """Download RICEFW inventory for an engagement as an Excel file. Optional type filter: R|I|C|E|F|W."""
    if type and type.upper() not in _RICEFW_TYPES:
        raise HTTPException(status_code=400, detail=f"type must be one of: {', '.join(sorted(_RICEFW_TYPES))}")
    try:
        items = get_ricefw_by_engagement(engagement_id, item_type=type.upper() if type else None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    wb = Workbook()
    ws = wb.active
    ws.title = "RICEFW Inventory"
    headers = ["id", "engagement_id", "type", "name", "description", "req_id", "status", "complexity", "priority", "created_at"]
    ws.append(headers)
    for item in items:
        ws.append([
            item.get("id"),
            item.get("engagement_id"),
            item.get("type"),
            item.get("name"),
            item.get("description") or "",
            item.get("req_id") or "",
            item.get("status") or "",
            item.get("complexity") or "",
            item.get("priority") or "",
            item.get("created_at") or "",
        ])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    suffix = f"_{type}" if type else ""
    filename = f"{engagement_id}_ricefw{suffix}.xlsx"
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _check_ricefw_complexity_priority(complexity: Optional[str], priority: Optional[str]) -> None:
    if complexity and complexity.lower() not in _RICEFW_COMPLEXITY:
        raise HTTPException(status_code=400, detail=f"complexity must be one of: {', '.join(sorted(_RICEFW_COMPLEXITY))}")
    if priority and priority.lower() not in _RICEFW_PRIORITY:
        raise HTTPException(status_code=400, detail=f"priority must be one of: {', '.join(sorted(_RICEFW_PRIORITY))}")


@router.post("/engagement/{engagement_id}/ricefw", status_code=201)
def create_ricefw(engagement_id: str, body: RICEFWCreate):
    if body.type.upper() not in _RICEFW_TYPES:
        raise HTTPException(status_code=400, detail=f"type must be one of: {', '.join(sorted(_RICEFW_TYPES))}")
    if body.status and body.status.lower() not in _RICEFW_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of: {', '.join(sorted(_RICEFW_STATUSES))}")
    _check_ricefw_complexity_priority(body.complexity, body.priority)
    # Ensure req_id belongs to this engagement (no cross-engagement data linkage)
    req = get_requirement_by_id(body.req_id, engagement_id)
    if not req:
        raise HTTPException(
            status_code=400,
            detail=f"Requirement {body.req_id} not found in this engagement. All RICEFW items must link to requirements within the same engagement.",
        )
    try:
        item = create_ricefw_item(
            engagement_id=engagement_id,
            item_type=body.type.upper(),
            name=body.name,
            req_id=body.req_id,
            description=body.description,
            status=(body.status or "identified").lower(),
            complexity=body.complexity.lower() if body.complexity else None,
            priority=body.priority.lower() if body.priority else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not item:
        raise HTTPException(status_code=500, detail="Failed to create RICEFW item")
    return item


@router.patch("/engagement/{engagement_id}/ricefw/{item_id}")
def update_ricefw(engagement_id: str, item_id: UUID, body: RICEFWUpdate):
    updates = {k: v for k, v in body.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    if "type" in updates and updates["type"].upper() not in _RICEFW_TYPES:
        raise HTTPException(status_code=400, detail=f"type must be one of: {', '.join(sorted(_RICEFW_TYPES))}")
    if "status" in updates and updates["status"].lower() not in _RICEFW_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of: {', '.join(sorted(_RICEFW_STATUSES))}")
    if "type" in updates:
        updates["type"] = updates["type"].upper()
    if "status" in updates:
        updates["status"] = updates["status"].lower()
    _check_ricefw_complexity_priority(updates.get("complexity"), updates.get("priority"))
    if "complexity" in updates and updates["complexity"]:
        updates["complexity"] = updates["complexity"].lower()
    if "priority" in updates and updates["priority"]:
        updates["priority"] = updates["priority"].lower()
    if "req_id" in updates:
        req = get_requirement_by_id(updates["req_id"], engagement_id)
        if not req:
            raise HTTPException(
                status_code=400,
                detail=f"Requirement {updates['req_id']} not found in this engagement. All RICEFW items must link to requirements within the same engagement.",
            )
    try:
        item = update_ricefw_item(str(item_id), engagement_id, updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not item:
        raise HTTPException(status_code=404, detail="RICEFW item not found")
    return item


@router.delete("/engagement/{engagement_id}/ricefw/{item_id}", status_code=204)
def delete_ricefw(engagement_id: str, item_id: UUID):
    try:
        deleted = delete_ricefw_item(str(item_id), engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=404, detail="RICEFW item not found")
    return None


# ── Admin Migrations ──────────────────────────────────────────────────────────

_PROCESS_STEPS_DDL = """
CREATE TABLE IF NOT EXISTS process_steps (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  req_id          text NOT NULL,
  engagement_id   text NOT NULL,
  step_number     int NOT NULL DEFAULT 1,
  title           text NOT NULL,
  description     text,
  performer_name  text,
  performer_role  text,
  shape           text DEFAULT 'process',
  step_type       text DEFAULT 'manual',
  duration_minutes float,
  systems_used    text[],
  kpis            jsonb,
  is_pain_point   boolean DEFAULT false,
  next_step_id    text,
  branches        jsonb,
  created_at      timestamptz DEFAULT now(),
  updated_at      timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_process_steps_req ON process_steps (req_id, engagement_id);
"""

_RICEFW_DDL = """
CREATE TABLE IF NOT EXISTS ricefw_inventory (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  engagement_id   text NOT NULL,
  req_id          text,
  type            text NOT NULL,
  name            text NOT NULL,
  description     text,
  status          text DEFAULT 'identified',
  complexity      text,
  priority        text,
  created_at      timestamptz DEFAULT now(),
  updated_at      timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ricefw_engagement ON ricefw_inventory (engagement_id);
CREATE INDEX IF NOT EXISTS idx_ricefw_type ON ricefw_inventory (engagement_id, type);
ALTER TABLE ricefw_inventory ADD COLUMN IF NOT EXISTS complexity text;
ALTER TABLE ricefw_inventory ADD COLUMN IF NOT EXISTS priority text;
"""

_CLIENTS_EXTRA_DDL = """
ALTER TABLE clients ADD COLUMN IF NOT EXISTS business_strategy text;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS goals jsonb;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS key_products jsonb;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS value_proposition text;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS senior_executives jsonb;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS direct_competitors jsonb;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS substitutes jsonb;
"""

_ENGAGEMENTS_EXTRA_DDL = """
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS status text DEFAULT 'open';
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS planned_start_date text;
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS planned_end_date text;
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS actual_start_date text;
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS actual_end_date text;
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS project_manager text;
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS sponsor text;
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS risk_level text;
ALTER TABLE engagements ADD COLUMN IF NOT EXISTS health text;
"""

_REQUIREMENTS_EXTRA_DDL = """
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS reference_id text;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS business_value text;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS current_system text;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS target_system_module text;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS fit_type text;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS related_test_case_id text;
"""

# Reference table: user, role, engagement_id — for verifying access and future restriction
_USER_ENGAGEMENT_ACCESS_DDL = """
CREATE TABLE IF NOT EXISTS user_engagement_access (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         text NOT NULL,
  role            text NOT NULL DEFAULT 'member',
  engagement_id   text NOT NULL,
  created_at      timestamptz DEFAULT now(),
  updated_at      timestamptz DEFAULT now(),
  UNIQUE(user_id, engagement_id)
);
CREATE INDEX IF NOT EXISTS idx_user_engagement_access_user ON user_engagement_access (user_id);
CREATE INDEX IF NOT EXISTS idx_user_engagement_access_engagement ON user_engagement_access (engagement_id);
COMMENT ON TABLE user_engagement_access IS 'Reference: verify user and role per engagement for access control';
"""


def _get_pg_dsn() -> str:
    """Build PostgreSQL DSN from Supabase URL and key."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        return db_url
    project_ref = supabase_url.split("//")[-1].split(".")[0] if supabase_url else ""
    # Supabase Transaction Pooler (port 6543) or Direct (port 5432)
    return (
        f"postgresql://postgres.{project_ref}:{supabase_key}"
        f"@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
    )


def _require_admin_key(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """If ADMIN_API_KEY is set, require X-Admin-Key header to match."""
    key = os.getenv("ADMIN_API_KEY")
    if key and x_admin_key != key:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/admin/migrate", status_code=200, dependencies=[Depends(_require_admin_key)])
def run_migrations():
    """Create required tables if they don't exist.
    Set DATABASE_URL env var to a direct PostgreSQL connection string (e.g., from Supabase dashboard).
    If not set, returns the SQL to run manually in Supabase SQL Editor.
    When ADMIN_API_KEY is set, call with header: X-Admin-Key: <value>.
    """
    dsn = _get_pg_dsn()
    if dsn:
        try:
            conn = psycopg2.connect(dsn, connect_timeout=15)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(_PROCESS_STEPS_DDL)
            cur.execute(_RICEFW_DDL)
            cur.execute(_CLIENTS_EXTRA_DDL)
            cur.execute(_ENGAGEMENTS_EXTRA_DDL)
            cur.execute(_REQUIREMENTS_EXTRA_DDL)
            cur.execute(_USER_ENGAGEMENT_ACCESS_DDL)
            cur.close()
            conn.close()
            return {"status": "ok", "message": "process_steps, ricefw_inventory, clients columns, engagements columns, requirements columns, and user_engagement_access ensured"}
        except Exception as e:
            return {
                "status": "manual_required",
                "error": str(e),
                "message": "Auto-migration failed. Run the SQL below in Supabase SQL Editor.",
                "sql": (_PROCESS_STEPS_DDL + _RICEFW_DDL + _CLIENTS_EXTRA_DDL + _ENGAGEMENTS_EXTRA_DDL + _REQUIREMENTS_EXTRA_DDL + _USER_ENGAGEMENT_ACCESS_DDL).strip(),
            }
    return {
        "status": "manual_required",
        "message": "Set DATABASE_URL env var for auto-migration. Run the SQL below in Supabase SQL Editor.",
        "sql": (_PROCESS_STEPS_DDL + _RICEFW_DDL + _CLIENTS_EXTRA_DDL + _ENGAGEMENTS_EXTRA_DDL + _REQUIREMENTS_EXTRA_DDL + _USER_ENGAGEMENT_ACCESS_DDL).strip(),
    }


app.include_router(router)
