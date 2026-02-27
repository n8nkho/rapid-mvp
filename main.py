from fastapi import FastAPI
from pydantic import BaseModel
from providers import get_llm_provider
from database import save_gap_analysis

app = FastAPI()
llm = get_llm_provider()

COST_PER_MILLION_INPUT_TOKENS = 0.25

SAP_SCOPE_ITEMS = [
    "Order-to-Cash (OTC): Sales order processing, billing, and accounts receivable",
    "Procure-to-Pay (PTP): Purchase requisitions, purchase orders, and accounts payable",
    "Record-to-Report (RTR): General ledger, financial close, and financial reporting",
    "Plan-to-Product (PTP): Production planning, shop floor execution, and quality management",
    "Hire-to-Retire (HTR): Employee lifecycle, payroll, and HR administration",
    "Forecast-to-Deliver (FTD): Demand planning, inventory management, and warehouse management",
    "Lead-to-Quote (LTQ): CRM, sales pipeline, and quotation management",
    "Acquire-to-Decommission (ATD): Asset accounting, depreciation, and asset retirement",
    "Treasury and Cash Management: Cash positioning, liquidity forecasting, and bank reconciliation",
    "Environment, Health & Safety (EHS): Incident management, compliance reporting, and risk assessment",
]

class PromptRequest(BaseModel):
    prompt: str

class GapAnalysisRequest(BaseModel):
    engagement_id: str
    process_description: str

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/usage")
def usage():
    estimated_cost = (llm.total_input_tokens / 1_000_000) * COST_PER_MILLION_INPUT_TOKENS
    return {
        "call_count": llm.call_count,
        "total_input_tokens": llm.total_input_tokens,
        "total_output_tokens": llm.total_output_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
    }

@app.post("/test-llm")
def test_llm(request: PromptRequest):
    response = llm.complete(request.prompt)
    return {"response": response}

@app.post("/gap-analysis")
def gap_analysis(request: GapAnalysisRequest):
    scope_list = "\n".join(f"- {item}" for item in SAP_SCOPE_ITEMS)
    prompt = (
        f"A customer described their business process as follows:\n"
        f"\"{request.process_description}\"\n\n"
        f"From the list of SAP S/4HANA scope items below, return only the ones that are "
        f"relevant to the described process. Be selective — only include genuinely relevant matches.\n\n"
        f"{scope_list}\n\n"
        f"Reply with a JSON array of matching scope item strings exactly as written above, "
        f"and nothing else. Example: [\"item one\", \"item two\"]"
    )
    system = "You are an SAP S/4HANA solution architect. Return only valid JSON with no explanation."
    raw = llm.complete(prompt, system=system)
    import json, re
    match = re.search(r"\[.*?\]", raw, re.DOTALL)
    matches = json.loads(match.group()) if match else []
    save_gap_analysis(request.engagement_id, request.process_description, matches)
    return {"matches": matches}
