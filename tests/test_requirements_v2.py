"""
pytest tests for RAPID MVP v2 — new endpoints and extended data model.
All Supabase and provider calls are mocked.
Env vars are set in conftest.py before any imports.
"""
import json
import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402

ENGAGEMENT = "eng-v2-test"

# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_req(req_id, **overrides):
    base = {
        "req_id": req_id,
        "engagement_id": ENGAGEMENT,
        "title": f"Requirement {req_id}",
        "description": "Finance team manually approves invoices over $5k",
        "source_type": "Conversation",
        "tags": ["manual_step", "pain_point"],
        "stakeholder": "CFO",
        "raw_input": None,
        "status": "open",
        "created_at": "2026-01-01T00:00:00",
        # v2 fields
        "business_process": "Record-to-Report",
        "priority": "Must-Have",
        "category": "Automation",
        "kpi_impact": {"metric": "invoice cycle time", "target": "reduce 50%", "unit": "days"},
        "confidence_score": 0.8,
        "current_state_ref": "Meeting notes 2026-01-10",
        "actors": [{"role": "AP Clerk", "type": "formal"}],
        "shadow_tools": ["Excel macro"],
        "sign_off_status": "draft",
        "sign_off_by": None,
        "sign_off_at": None,
        "sap_mapping_id": None,
        "fit_assessment": None,
    }
    base.update(overrides)
    return base


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=True)


# ── Phase 1: RequirementCreate with all new fields ────────────────────────────

class TestRequirementCreateV2:
    """POST /requirements accepts and returns all v2 fields."""

    def test_full_v2_payload(self, client):
        created = _make_req("REQ-001")
        with patch("main.create_requirement", return_value=created):
            resp = client.post("/requirements", json={
                "engagement_id": ENGAGEMENT,
                "title": "Invoice approval workflow",
                "description": "Finance team manually approves invoices",
                "source_type": "Conversation",
                "tags": ["manual_step", "pain_point"],
                "stakeholder": "CFO",
                "business_process": "Record-to-Report",
                "priority": "Must-Have",
                "category": "Automation",
                "kpi_impact": {"metric": "invoice cycle time", "target": "reduce 50%", "unit": "days"},
                "confidence_score": 0.9,
                "current_state_ref": "Meeting notes 2026-01-10",
                "actors": [{"role": "AP Clerk", "type": "formal"}],
                "shadow_tools": ["Excel macro"],
                "sign_off_status": "draft",
                "sap_mapping_id": None,
                "fit_assessment": None,
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data["req_id"] == "REQ-001"
        assert data["business_process"] == "Record-to-Report"
        assert data["priority"] == "Must-Have"
        assert data["category"] == "Automation"
        assert data["kpi_impact"]["metric"] == "invoice cycle time"
        assert data["shadow_tools"] == ["Excel macro"]
        assert data["actors"] == [{"role": "AP Clerk", "type": "formal"}]
        assert data["sign_off_status"] == "draft"

    def test_defaults_applied(self, client):
        """When optional v2 fields are omitted, defaults should be used."""
        created = _make_req("REQ-002", priority="Must-Have", sign_off_status="draft", confidence_score=0.8)
        with patch("main.create_requirement", return_value=created):
            resp = client.post("/requirements", json={
                "engagement_id": ENGAGEMENT,
                "title": "Minimal requirement",
                "description": "Just the basics",
            })
        assert resp.status_code == 201
        data = resp.json()
        # Defaults come from the DB/mock, confirm they're present in response
        assert data["priority"] == "Must-Have"
        assert data["sign_off_status"] == "draft"

    def test_new_fields_passed_to_create_requirement(self, client):
        """Ensure all new fields flow from endpoint body to create_requirement."""
        created = _make_req("REQ-003")
        with patch("main.create_requirement", return_value=created) as mock_create:
            client.post("/requirements", json={
                "engagement_id": ENGAGEMENT,
                "title": "Test",
                "description": "Test desc",
                "business_process": "Order-to-Cash",
                "priority": "Should-Have",
                "category": "Integration",
                "shadow_tools": ["WhatsApp"],
                "actors": [{"role": "Sales Rep", "type": "formal"}],
            })
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["business_process"] == "Order-to-Cash"
        assert call_kwargs["priority"] == "Should-Have"
        assert call_kwargs["category"] == "Integration"
        assert call_kwargs["shadow_tools"] == ["WhatsApp"]


# ── Phase 4: Sign-off workflow state transitions ───────────────────────────────

class TestSignOffWorkflow:
    """POST /requirements/{req_id}/sign-off state machine."""

    def _post_sign_off(self, client, req, level, signed_by, updated=None):
        if updated is None:
            updated = {**req}
        with (
            patch("main.get_requirement_by_id", return_value=req),
            patch("main.update_requirement", return_value=updated),
        ):
            return client.post(
                f"/requirements/{req['req_id']}/sign-off",
                params={"engagement_id": ENGAGEMENT},
                json={"level": level, "signed_by": signed_by},
            )

    def test_sme_sign_off_sets_sme_approved(self, client):
        req = _make_req("REQ-001", sign_off_status="draft")
        updated = {**req, "sign_off_status": "sme_approved", "sign_off_by": "Alice"}
        resp = self._post_sign_off(client, req, "sme", "Alice", updated)
        assert resp.status_code == 200
        assert resp.json()["sign_off_status"] == "sme_approved"
        assert resp.json()["sign_off_by"] == "Alice"

    def test_owner_after_sme_sets_confirmed(self, client):
        req = _make_req("REQ-001", sign_off_status="sme_approved")
        updated = {**req, "sign_off_status": "confirmed", "sign_off_by": "Bob"}
        resp = self._post_sign_off(client, req, "owner", "Bob", updated)
        assert resp.status_code == 200
        assert resp.json()["sign_off_status"] == "confirmed"

    def test_owner_on_draft_sets_owner_approved(self, client):
        req = _make_req("REQ-001", sign_off_status="draft")
        updated = {**req, "sign_off_status": "owner_approved", "sign_off_by": "Carol"}
        resp = self._post_sign_off(client, req, "owner", "Carol", updated)
        assert resp.status_code == 200
        assert resp.json()["sign_off_status"] == "owner_approved"

    def test_invalid_level_returns_400(self, client):
        resp = client.post(
            "/requirements/REQ-001/sign-off",
            params={"engagement_id": ENGAGEMENT},
            json={"level": "ceo", "signed_by": "Dave"},
        )
        assert resp.status_code == 400
        assert "level" in resp.json()["detail"].lower()

    def test_missing_requirement_returns_404(self, client):
        with patch("main.get_requirement_by_id", return_value=None):
            resp = client.post(
                "/requirements/REQ-999/sign-off",
                params={"engagement_id": ENGAGEMENT},
                json={"level": "sme", "signed_by": "Eve"},
            )
        assert resp.status_code == 404

    def test_sign_off_at_timestamp_is_set(self, client):
        req = _make_req("REQ-001", sign_off_status="draft")
        updated = {**req, "sign_off_status": "sme_approved", "sign_off_by": "Frank", "sign_off_at": "2026-02-01T10:00:00+00:00"}
        resp = self._post_sign_off(client, req, "sme", "Frank", updated)
        assert resp.status_code == 200
        assert resp.json()["sign_off_at"] is not None

    def test_sign_off_status_summary(self, client):
        reqs = [
            _make_req("REQ-001", sign_off_status="draft"),
            _make_req("REQ-002", sign_off_status="sme_approved"),
            _make_req("REQ-003", sign_off_status="confirmed"),
            _make_req("REQ-004", sign_off_status="owner_approved"),
            _make_req("REQ-005", sign_off_status="draft"),
        ]
        with patch("main.get_requirements_by_engagement", return_value=reqs):
            resp = client.get(f"/engagement/{ENGAGEMENT}/sign-off-status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert data["draft"] == 2
        assert data["sme_approved"] == 1
        assert data["owner_approved"] == 1
        assert data["confirmed"] == 1

    def test_sign_off_status_by_process(self, client):
        reqs = [
            _make_req("REQ-001", sign_off_status="draft", business_process="Order-to-Cash"),
            _make_req("REQ-002", sign_off_status="sme_approved", business_process="Order-to-Cash"),
            _make_req("REQ-003", sign_off_status="confirmed", business_process="Procure-to-Pay"),
        ]
        with patch("main.get_requirements_by_engagement", return_value=reqs):
            resp = client.get(f"/engagement/{ENGAGEMENT}/sign-off-status")
        data = resp.json()
        assert "Order-to-Cash" in data["by_process"]
        assert data["by_process"]["Order-to-Cash"]["draft"] == 1
        assert data["by_process"]["Order-to-Cash"]["sme_approved"] == 1
        assert data["by_process"]["Procure-to-Pay"]["confirmed"] == 1


# ── Phase 5: Templates endpoint ────────────────────────────────────────────────

class TestDomainTemplates:
    """GET /requirements/templates?domain= returns correct items."""

    @pytest.mark.parametrize("domain,expected_min", [
        ("finance", 3),
        ("sales", 2),
        ("procurement", 2),
        ("manufacturing", 2),
        ("hr", 2),
    ])
    def test_domain_returns_min_templates(self, client, domain, expected_min):
        resp = client.get(f"/requirements/templates?domain={domain}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain"] == domain
        assert data["total"] >= expected_min
        assert len(data["templates"]) >= expected_min

    def test_finance_has_automation_must_have(self, client):
        resp = client.get("/requirements/templates?domain=finance")
        data = resp.json()
        automation = [t for t in data["templates"] if t["category"] == "Automation" and t["priority"] == "Must-Have"]
        assert len(automation) >= 1

    def test_finance_has_control_compliance(self, client):
        resp = client.get("/requirements/templates?domain=finance")
        data = resp.json()
        ctrl = [t for t in data["templates"] if t["category"] == "Control/Compliance"]
        assert len(ctrl) >= 1

    def test_finance_month_end_kpi(self, client):
        resp = client.get("/requirements/templates?domain=finance")
        data = resp.json()
        reporting = [t for t in data["templates"] if t["category"] == "Reporting"]
        assert len(reporting) >= 1
        assert reporting[0]["kpi_impact"] is not None

    def test_templates_have_required_fields(self, client):
        resp = client.get("/requirements/templates?domain=sales")
        data = resp.json()
        for t in data["templates"]:
            assert "title" in t
            assert "description" in t
            assert "business_process" in t
            assert "priority" in t
            assert "category" in t
            assert "tags" in t

    def test_templates_not_persisted(self, client):
        """Templates endpoint must not call create_requirement."""
        with patch("main.create_requirement") as mock_create:
            resp = client.get("/requirements/templates?domain=procurement")
        mock_create.assert_not_called()
        assert resp.status_code == 200

    def test_invalid_domain_returns_400(self, client):
        resp = client.get("/requirements/templates?domain=logistics")
        assert resp.status_code == 400
        assert "Valid options" in resp.json()["detail"]

    def test_case_insensitive_domain(self, client):
        resp = client.get("/requirements/templates?domain=Finance")
        assert resp.status_code == 200
        assert resp.json()["domain"] == "finance"

    def test_manufacturing_has_automation(self, client):
        resp = client.get("/requirements/templates?domain=manufacturing")
        data = resp.json()
        automation = [t for t in data["templates"] if t["category"] == "Automation"]
        assert len(automation) >= 1

    def test_hr_hire_to_retire_process(self, client):
        resp = client.get("/requirements/templates?domain=hr")
        data = resp.json()
        for t in data["templates"]:
            assert t["business_process"] == "Hire-to-Retire"


# ── Phase 6: Traceability endpoint structure ───────────────────────────────────

class TestTraceability:
    """GET /requirements/{req_id}/traceability?engagement_id="""

    SAMPLE_GAP = {
        "id": "gr-1",
        "engagement_id": ENGAGEMENT,
        "req_id": "REQ-001",
        "matches": [{"id": "J45", "name": "Vendor Management", "confidence": "HIGH"}],
        "tokens_used": 300,
        "timestamp": "2026-01-02T00:00:00",
    }

    def test_happy_path_structure(self, client):
        req = _make_req("REQ-001")
        with (
            patch("main.get_requirement_by_id", return_value=req),
            patch("main.get_gap_results_by_req_id", return_value=[self.SAMPLE_GAP]),
        ):
            resp = client.get(f"/requirements/REQ-001/traceability?engagement_id={ENGAGEMENT}")
        assert resp.status_code == 200
        data = resp.json()
        assert "requirement" in data
        assert "as_is_evidence" in data
        assert "gap_analysis" in data
        assert "answer_to" in data

    def test_requirement_is_full_object(self, client):
        req = _make_req("REQ-001")
        with (
            patch("main.get_requirement_by_id", return_value=req),
            patch("main.get_gap_results_by_req_id", return_value=[]),
        ):
            resp = client.get(f"/requirements/REQ-001/traceability?engagement_id={ENGAGEMENT}")
        data = resp.json()
        assert data["requirement"]["req_id"] == "REQ-001"
        assert data["requirement"]["business_process"] == "Record-to-Report"

    def test_as_is_evidence_fields(self, client):
        req = _make_req("REQ-001",
                        current_state_ref="Video timestamp 12:34",
                        shadow_tools=["Excel macro", "WhatsApp"],
                        actors=[{"role": "AP Clerk", "type": "formal"}])
        with (
            patch("main.get_requirement_by_id", return_value=req),
            patch("main.get_gap_results_by_req_id", return_value=[]),
        ):
            resp = client.get(f"/requirements/REQ-001/traceability?engagement_id={ENGAGEMENT}")
        data = resp.json()
        ev = data["as_is_evidence"]
        assert ev["current_state_ref"] == "Video timestamp 12:34"
        assert "Excel macro" in ev["shadow_tools"]
        assert ev["actors"][0]["role"] == "AP Clerk"
        assert "manual_step" in ev["tags"]

    def test_gap_analysis_section(self, client):
        req = _make_req("REQ-001")
        with (
            patch("main.get_requirement_by_id", return_value=req),
            patch("main.get_gap_results_by_req_id", return_value=[self.SAMPLE_GAP]),
        ):
            resp = client.get(f"/requirements/REQ-001/traceability?engagement_id={ENGAGEMENT}")
        data = resp.json()
        ga = data["gap_analysis"]
        assert ga["total_analyses"] == 1
        assert ga["matches"][0]["id"] == "J45"

    def test_gap_analysis_empty_when_no_results(self, client):
        req = _make_req("REQ-001")
        with (
            patch("main.get_requirement_by_id", return_value=req),
            patch("main.get_gap_results_by_req_id", return_value=[]),
        ):
            resp = client.get(f"/requirements/REQ-001/traceability?engagement_id={ENGAGEMENT}")
        data = resp.json()
        assert data["gap_analysis"]["matches"] == []
        assert data["gap_analysis"]["total_analyses"] == 0

    def test_answer_to_who_asked_includes_stakeholder(self, client):
        req = _make_req("REQ-001",
                        stakeholder="CFO",
                        actors=[{"role": "AP Clerk", "type": "formal"}])
        with (
            patch("main.get_requirement_by_id", return_value=req),
            patch("main.get_gap_results_by_req_id", return_value=[]),
        ):
            resp = client.get(f"/requirements/REQ-001/traceability?engagement_id={ENGAGEMENT}")
        data = resp.json()
        who = data["answer_to"]["who_asked"]
        assert "CFO" in who
        assert "AP Clerk" in who

    def test_answer_to_what_problem_mentions_pain_tags(self, client):
        req = _make_req("REQ-001",
                        tags=["pain_point", "manual_step"],
                        shadow_tools=["Excel macro"])
        with (
            patch("main.get_requirement_by_id", return_value=req),
            patch("main.get_gap_results_by_req_id", return_value=[]),
        ):
            resp = client.get(f"/requirements/REQ-001/traceability?engagement_id={ENGAGEMENT}")
        data = resp.json()
        problem = data["answer_to"]["what_problem"]
        assert "pain_point" in problem or "manual_step" in problem
        assert "Excel macro" in problem

    def test_not_found_returns_404(self, client):
        with patch("main.get_requirement_by_id", return_value=None):
            resp = client.get(f"/requirements/REQ-999/traceability?engagement_id={ENGAGEMENT}")
        assert resp.status_code == 404

    def test_db_error_returns_500(self, client):
        with patch("main.get_requirement_by_id", side_effect=Exception("DB error")):
            resp = client.get(f"/requirements/REQ-001/traceability?engagement_id={ENGAGEMENT}")
        assert resp.status_code == 500


# ── Phase 7: KPI Summary ───────────────────────────────────────────────────────

class TestKpiSummary:
    """GET /engagement/{engagement_id}/kpi-summary"""

    def test_happy_path(self, client):
        reqs = [
            _make_req("REQ-001", business_process="Order-to-Cash",
                      kpi_impact={"metric": "invoice cycle time", "target": "50%", "unit": "days"}),
            _make_req("REQ-002", business_process="Procure-to-Pay",
                      kpi_impact={"metric": "stockout events", "target": "80%", "unit": "incidents"}),
            _make_req("REQ-003", business_process="Order-to-Cash",
                      kpi_impact={"metric": "days sales outstanding", "target": "30 days", "unit": "days"}),
            _make_req("REQ-004", business_process="Record-to-Report", kpi_impact=None),
        ]
        with patch("main.get_requirements_by_engagement", return_value=reqs):
            resp = client.get(f"/engagement/{ENGAGEMENT}/kpi-summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_with_kpi"] == 3
        assert "Order-to-Cash" in data["by_process"]
        assert len(data["by_process"]["Order-to-Cash"]) == 2
        assert len(data["by_process"]["Procure-to-Pay"]) == 1
        assert "Record-to-Report" not in data["by_process"]

    def test_kpi_entry_structure(self, client):
        reqs = [_make_req("REQ-001", business_process="Order-to-Cash",
                          kpi_impact={"metric": "close time", "target": "3 days", "unit": "days"})]
        with patch("main.get_requirements_by_engagement", return_value=reqs):
            resp = client.get(f"/engagement/{ENGAGEMENT}/kpi-summary")
        data = resp.json()
        entry = data["by_process"]["Order-to-Cash"][0]
        assert entry["req_id"] == "REQ-001"
        assert entry["kpi_impact"]["metric"] == "close time"
        assert "title" in entry
        assert "priority" in entry

    def test_empty_when_no_kpi(self, client):
        reqs = [_make_req("REQ-001", kpi_impact=None), _make_req("REQ-002", kpi_impact=None)]
        with patch("main.get_requirements_by_engagement", return_value=reqs):
            resp = client.get(f"/engagement/{ENGAGEMENT}/kpi-summary")
        data = resp.json()
        assert data["total_with_kpi"] == 0
        assert data["by_process"] == {}

    def test_unclassified_process(self, client):
        reqs = [_make_req("REQ-001", business_process=None,
                          kpi_impact={"metric": "time", "target": "50%", "unit": "hours"})]
        with patch("main.get_requirements_by_engagement", return_value=reqs):
            resp = client.get(f"/engagement/{ENGAGEMENT}/kpi-summary")
        data = resp.json()
        assert "Unclassified" in data["by_process"]

    def test_db_error_returns_500(self, client):
        with patch("main.get_requirements_by_engagement", side_effect=Exception("timeout")):
            resp = client.get(f"/engagement/{ENGAGEMENT}/kpi-summary")
        assert resp.status_code == 500
