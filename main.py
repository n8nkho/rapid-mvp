from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import os
from datetime import datetime

# Import providers and database
from providers import get_provider
from database import save_gap_analysis
from scope_items import SCOPE_ITEMS, get_catalogue_text

app = FastAPI(
    title="RAPID Gap Analysis API",
    description="AI-powered SAP S/4HANA scope item gap analysis using semantic matching",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GapAnalysisRequest(BaseModel):
    engagement_id: str
    process_description: str
    top_n: Optional[int] = 5
    lob_filter: Optional[str] = None  # e.g. "Finance", "Procurement"

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
    process_description: str
    matches: List[ScopeItemMatch]
    total_scope_items_searched: int
    tokens_used: Optional[int] = None
    timestamp: str

def build_catalogue_for_prompt(lob_filter: Optional[str] = None) -> str:
    """Build catalogue string, optionally filtered by LOB."""
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

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.1.0",
        "scope_items_loaded": len(SCOPE_ITEMS),
        "release": "S/4HANA Cloud Public Edition 2602"
    }

@app.get("/catalogue")
def get_catalogue(lob: Optional[str] = None):
    """Browse scope item catalogue, optionally filtered by LOB."""
    items = SCOPE_ITEMS
    if lob:
        items = [i for i in items if i.get('lob', '').lower() == lob.lower()]
    return {
        "total": len(items),
        "items": items
    }

@app.get("/lobs")
def get_lobs():
    """Get available Lines of Business."""
    from collections import Counter
    counts = Counter(i['lob'] for i in SCOPE_ITEMS)
    return {"lobs": [{"name": k, "count": v} for k, v in sorted(counts.items())]}

@app.post("/gap-analysis", response_model=GapAnalysisResponse)
async def gap_analysis(request: GapAnalysisRequest):
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
{request.process_description}

SAP S/4HANA Cloud 2602 Scope Item Catalogue (2602 release):
{catalogue}

Return the top {request.top_n} most relevant scope items as JSON."""

    try:
        result = provider.complete(system_prompt, user_prompt)
        raw_text = result.get("content", "[]")
        tokens_used = result.get("tokens_used")
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON array found in response")
        
        matches_raw = json.loads(json_match.group())
        
        # Build full match objects
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
        
        # Persist to Supabase
        try:
            save_gap_analysis(
                engagement_id=request.engagement_id,
                process_description=request.process_description,
                matches=[m.dict() for m in matches],
                tokens_used=tokens_used,
                timestamp=timestamp
            )
        except Exception as db_err:
            print(f"DB save failed (non-fatal): {db_err}")
        
        return GapAnalysisResponse(
            engagement_id=request.engagement_id,
            process_description=request.process_description,
            matches=matches,
            total_scope_items_searched=len(SCOPE_ITEMS),
            tokens_used=tokens_used,
            timestamp=timestamp
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

