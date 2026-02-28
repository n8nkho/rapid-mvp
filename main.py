from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import re
from datetime import datetime

# Import providers and database
from providers import get_provider
from database import (
    save_gap_analysis,
    get_results_by_engagement,
    create_requirement,
    get_requirements_by_engagement,
    get_requirement_by_id,
    update_requirement,
)
from scope_items import SCOPE_ITEMS, get_catalogue_text

app = FastAPI(
    title="RAPID Gap Analysis API",
    description="AI-powered SAP S/4HANA scope item gap analysis using semantic matching",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

class RequirementUpdate(BaseModel):
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    stakeholder: Optional[str] = None

class TranscriptExtractRequest(BaseModel):
    engagement_id: str
    stakeholder: str
    transcript_text: str

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


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    result = provider.complete(_GAP_SYSTEM_PROMPT, user_prompt)
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
    return {
        "status": "ok",
        "version": "1.2.0",
        "scope_items_loaded": len(SCOPE_ITEMS),
        "release": "S/4HANA Cloud Public Edition 2602"
    }

@app.get("/catalogue")
def get_catalogue(lob: Optional[str] = None):
    items = SCOPE_ITEMS
    if lob:
        items = [i for i in items if i.get('lob', '').lower() == lob.lower()]
    return {"total": len(items), "items": items}

@app.get("/lobs")
def get_lobs():
    from collections import Counter
    counts = Counter(i['lob'] for i in SCOPE_ITEMS)
    return {"lobs": [{"name": k, "count": v} for k, v in sorted(counts.items())]}

@app.get("/results")
def get_results(engagement_id: str):
    try:
        results = get_results_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"engagement_id": engagement_id, "total": len(results), "results": results}


# ── Requirements ──────────────────────────────────────────────────────────────

@app.post("/requirements", response_model=RequirementResponse, status_code=201)
def post_requirement(body: RequirementCreate):
    try:
        req = create_requirement(
            engagement_id=body.engagement_id,
            title=body.title,
            description=body.description,
            source_type=body.source_type,
            tags=body.tags,
            stakeholder=body.stakeholder,
            raw_input=body.raw_input,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=500, detail="Failed to create requirement")
    return req

@app.get("/requirements", response_model=List[RequirementResponse])
def list_requirements(engagement_id: str):
    try:
        return get_requirements_by_engagement(engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/requirements/extract-from-transcript", status_code=201)
def extract_from_transcript(body: TranscriptExtractRequest):
    provider = get_provider()
    system_prompt = """You are an expert business analyst capturing requirements from conversation transcripts for SAP S/4HANA implementation projects.

Extract discrete business requirements from the transcript. For each requirement identify:
- title: Brief descriptive title (max 10 words)
- description: Detailed description of the business need or process
- tags: Array of applicable tags — use only values from: pain_point, manual_step, secret_sauce, workaround, hand_off

Return a JSON array only:
[
  {
    "title": "requirement title",
    "description": "detailed description of the requirement",
    "tags": ["tag1", "tag2"]
  }
]

Rules:
- Each requirement must be distinct and actionable
- Tags must only come from: pain_point, manual_step, secret_sauce, workaround, hand_off
- Return [] if no clear requirements are found"""

    user_prompt = f"Extract business requirements from this transcript:\n\n{body.transcript_text}\n\nReturn JSON array."

    try:
        result = provider.complete(system_prompt, user_prompt)
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
            )
            if req:
                created.append({
                    "req_id": req["req_id"],
                    "title": req["title"],
                    "tags": req.get("tags", []),
                })
        except Exception as e:
            print(f"Failed to create requirement '{item.get('title')}': {e}")

    return {"created": len(created), "requirements": created}


@app.get("/requirements/{req_id}", response_model=RequirementResponse)
def get_requirement(req_id: str, engagement_id: str):
    try:
        req = get_requirement_by_id(req_id, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not req:
        raise HTTPException(status_code=404, detail=f"{req_id} not found for engagement {engagement_id}")
    return req

@app.patch("/requirements/{req_id}", response_model=RequirementResponse)
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


# ── Gap Analysis ──────────────────────────────────────────────────────────────

@app.post("/gap-analysis", response_model=GapAnalysisResponse)
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

@app.get("/engagement/{engagement_id}/summary")
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

@app.post("/engagement/{engagement_id}/analyse-all")
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

@app.get("/engagement/{engagement_id}/process-mirror")
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
