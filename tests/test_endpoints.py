"""
pytest tests for RAPID MVP new endpoints.
All Supabase and provider calls are mocked.
Env vars (SUPABASE_URL etc.) are set in conftest.py before any imports.
"""
import json
import sys
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402 — conftest.py has already set env vars

# ── Fixtures / helpers ─────────────────────────────────────────────────────────

ENGAGEMENT = "eng-test-001"

SAMPLE_REQS = [
    {
        "req_id": "REQ-001",
        "engagement_id": ENGAGEMENT,
        "title": "Invoice approval workflow",
        "description": "Finance team manually approves invoices over $5k",
        "source_type": "Conversation",
        "tags": ["manual_step", "pain_point"],
        "stakeholder": "CFO",
        "raw_input": None,
        "status": "open",
        "created_at": "2026-01-01T00:00:00",
    },
    {
        "req_id": "REQ-002",
        "engagement_id": ENGAGEMENT,
        "title": "Vendor onboarding process",
        "description": "Procurement team uses spreadsheets to track vendor documents",
        "source_type": "Document",
        "tags": ["workaround"],
        "stakeholder": "Procurement Manager",
        "raw_input": None,
        "status": "analysed",
        "created_at": "2026-01-01T00:00:00",
    },
    {
        "req_id": "REQ-003",
        "engagement_id": ENGAGEMENT,
        "title": "No-tag requirement",
        "description": "Something with no tags",
        "source_type": "Conversation",
        "tags": [],
        "stakeholder": "CEO",
        "raw_input": None,
        "status": "open",
        "created_at": "2026-01-01T00:00:00",
    },
]

SAMPLE_GAP_RESULTS = [
    {
        "id": "gr-1",
        "engagement_id": ENGAGEMENT,
        "req_id": "REQ-002",
        "process_description": "Vendor onboarding",
        "matches": [
            {"id": "J45", "name": "Vendor Management", "confidence": "HIGH", "rationale": "Direct match"},
            {"id": "MF1", "name": "Invoice Processing", "confidence": "MEDIUM", "rationale": "Related"},
        ],
        "tokens_used": 500,
        "timestamp": "2026-01-02T00:00:00",
    }
]


@pytest.fixture
def client_live():
    """Return TestClient; env vars from conftest.py allow database.py to import cleanly."""
    return TestClient(app, raise_server_exceptions=True)


# ── GET /engagement/{id}/summary ───────────────────────────────────────────────

class TestSummary:
    def test_happy_path(self, client_live):
        with (
            patch("main.get_requirements_by_engagement", return_value=SAMPLE_REQS),
            patch("main.get_results_by_engagement", return_value=SAMPLE_GAP_RESULTS),
        ):
            resp = client_live.get(f"/engagement/{ENGAGEMENT}/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["engagement_id"] == ENGAGEMENT
        assert data["total_requirements"] == 3
        assert data["requirements_by_status"]["open"] == 2
        assert data["requirements_by_status"]["analysed"] == 1
        assert data["requirements_by_tag"]["manual_step"] == 1
        assert data["requirements_by_tag"]["pain_point"] == 1
        assert data["requirements_by_tag"]["workaround"] == 1
        assert data["total_analysed"] == 1
        assert len(data["gap_results_summary"]) == 1
        summary_item = data["gap_results_summary"][0]
        assert summary_item["req_id"] == "REQ-002"
        assert summary_item["top_match_id"] == "J45"
        assert summary_item["top_match_name"] == "Vendor Management"
        assert summary_item["top_confidence"] == "HIGH"

    def test_empty_engagement(self, client_live):
        with (
            patch("main.get_requirements_by_engagement", return_value=[]),
            patch("main.get_results_by_engagement", return_value=[]),
        ):
            resp = client_live.get(f"/engagement/empty-eng/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_requirements"] == 0
        assert data["total_analysed"] == 0
        assert data["gap_results_summary"] == []

    def test_db_error_returns_500(self, client_live):
        with patch("main.get_requirements_by_engagement", side_effect=Exception("DB down")):
            resp = client_live.get(f"/engagement/{ENGAGEMENT}/summary")
        assert resp.status_code == 500
        assert "DB down" in resp.json()["detail"]


# ── POST /engagement/{id}/analyse-all ─────────────────────────────────────────

class TestAnalyseAll:
    def _mock_provider(self):
        provider = MagicMock()
        provider.complete.return_value = {
            "content": '[{"id":"J45","confidence":"HIGH","rationale":"Match"}]',
            "tokens_used": 300,
        }
        return provider

    def test_happy_path(self, client_live):
        open_reqs = [r for r in SAMPLE_REQS if r["status"] == "open"]
        with (
            patch("main.get_requirements_by_engagement", return_value=SAMPLE_REQS),
            patch("main.get_provider", return_value=self._mock_provider()),
            patch("main.save_gap_analysis"),
            patch("main.update_requirement"),
        ):
            resp = client_live.post(f"/engagement/{ENGAGEMENT}/analyse-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["processed"] == len(open_reqs)
        assert len(data["results"]) == len(open_reqs)
        result_ids = {r["req_id"] for r in data["results"]}
        assert "REQ-001" in result_ids
        assert "REQ-003" in result_ids

    def test_no_open_requirements(self, client_live):
        all_analysed = [{**r, "status": "analysed"} for r in SAMPLE_REQS]
        with patch("main.get_requirements_by_engagement", return_value=all_analysed):
            resp = client_live.post(f"/engagement/{ENGAGEMENT}/analyse-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["processed"] == 0
        assert data["results"] == []

    def test_db_error_returns_500(self, client_live):
        with patch("main.get_requirements_by_engagement", side_effect=Exception("timeout")):
            resp = client_live.post(f"/engagement/{ENGAGEMENT}/analyse-all")
        assert resp.status_code == 500

    def test_top_match_in_result(self, client_live):
        with (
            patch("main.get_requirements_by_engagement", return_value=[SAMPLE_REQS[0]]),
            patch("main.get_provider", return_value=self._mock_provider()),
            patch("main.save_gap_analysis"),
            patch("main.update_requirement"),
        ):
            resp = client_live.post(f"/engagement/{ENGAGEMENT}/analyse-all")
        data = resp.json()
        assert data["results"][0]["top_match_id"] == "J45"


# ── POST /requirements/extract-from-transcript ────────────────────────────────

class TestExtractFromTranscript:
    TRANSCRIPT = (
        "We currently have a painful manual process where the finance team "
        "downloads reports from three systems and consolidates them in Excel. "
        "There's also a secret workaround where approvals are sent by email."
    )

    def _mock_provider(self):
        provider = MagicMock()
        provider.complete.return_value = {
            "content": json.dumps([
                {
                    "title": "Manual Excel consolidation",
                    "description": "Finance downloads reports and consolidates manually",
                    "tags": ["manual_step", "pain_point"],
                },
                {
                    "title": "Email approval workaround",
                    "description": "Approvals sent by email instead of system",
                    "tags": ["workaround"],
                },
            ]),
            "tokens_used": 400,
        }
        return provider

    def _created_req(self, req_id, title, tags):
        return {
            "req_id": req_id,
            "engagement_id": ENGAGEMENT,
            "title": title,
            "description": "desc",
            "source_type": "Conversation",
            "tags": tags,
            "stakeholder": "CFO",
            "raw_input": self.TRANSCRIPT,
            "status": "open",
            "created_at": "2026-01-01T00:00:00",
        }

    def test_happy_path(self, client_live):
        side_effects = [
            self._created_req("REQ-001", "Manual Excel consolidation", ["manual_step", "pain_point"]),
            self._created_req("REQ-002", "Email approval workaround", ["workaround"]),
        ]
        with (
            patch("main.get_provider", return_value=self._mock_provider()),
            patch("main.create_requirement", side_effect=side_effects),
        ):
            resp = client_live.post("/requirements/extract-from-transcript", json={
                "engagement_id": ENGAGEMENT,
                "stakeholder": "CFO",
                "transcript_text": self.TRANSCRIPT,
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data["created"] == 2
        assert data["requirements"][0]["req_id"] == "REQ-001"
        assert "manual_step" in data["requirements"][0]["tags"]
        assert data["requirements"][1]["tags"] == ["workaround"]

    def test_invalid_tags_filtered(self, client_live):
        provider = MagicMock()
        provider.complete.return_value = {
            "content": json.dumps([
                {
                    "title": "Some requirement",
                    "description": "desc",
                    "tags": ["invalid_tag", "pain_point", "not_a_tag"],
                }
            ]),
            "tokens_used": 100,
        }
        created = self._created_req("REQ-001", "Some requirement", ["pain_point"])
        with (
            patch("main.get_provider", return_value=provider),
            patch("main.create_requirement", return_value=created) as mock_create,
        ):
            resp = client_live.post("/requirements/extract-from-transcript", json={
                "engagement_id": ENGAGEMENT,
                "stakeholder": "User",
                "transcript_text": "some transcript",
            })
        assert resp.status_code == 201
        # Only valid tag should have been passed to create_requirement
        call_kwargs = mock_create.call_args
        assert call_kwargs.kwargs["tags"] == ["pain_point"]

    def test_empty_transcript_returns_no_requirements(self, client_live):
        provider = MagicMock()
        provider.complete.return_value = {"content": "[]", "tokens_used": 50}
        with (
            patch("main.get_provider", return_value=provider),
            patch("main.create_requirement") as mock_create,
        ):
            resp = client_live.post("/requirements/extract-from-transcript", json={
                "engagement_id": ENGAGEMENT,
                "stakeholder": "User",
                "transcript_text": "nothing useful here",
            })
        assert resp.status_code == 201
        assert resp.json()["created"] == 0
        mock_create.assert_not_called()

    def test_provider_error_returns_500(self, client_live):
        provider = MagicMock()
        provider.complete.side_effect = Exception("API down")
        with patch("main.get_provider", return_value=provider):
            resp = client_live.post("/requirements/extract-from-transcript", json={
                "engagement_id": ENGAGEMENT,
                "stakeholder": "User",
                "transcript_text": "some text",
            })
        assert resp.status_code == 500

    def test_missing_fields_returns_422(self, client_live):
        resp = client_live.post("/requirements/extract-from-transcript", json={
            "engagement_id": ENGAGEMENT,
            # missing stakeholder and transcript_text
        })
        assert resp.status_code == 422


# ── GET /engagement/{id}/process-mirror ───────────────────────────────────────

class TestProcessMirror:
    def test_happy_path(self, client_live):
        with patch("main.get_requirements_by_engagement", return_value=SAMPLE_REQS):
            resp = client_live.get(f"/engagement/{ENGAGEMENT}/process-mirror")
        assert resp.status_code == 200
        data = resp.json()
        assert data["engagement_id"] == ENGAGEMENT
        assert "generated_at" in data
        assert data["summary"]["total_requirements"] == 3
        assert data["summary"]["by_tag"]["manual_step"] == 1
        assert data["summary"]["by_tag"]["pain_point"] == 1
        assert data["summary"]["by_tag"]["workaround"] == 1
        # REQ-001 has manual_step and pain_point — appears in both
        assert any(r["req_id"] == "REQ-001" for r in data["by_tag"]["manual_step"])
        assert any(r["req_id"] == "REQ-001" for r in data["by_tag"]["pain_point"])
        assert any(r["req_id"] == "REQ-002" for r in data["by_tag"]["workaround"])
        # REQ-003 has no tags → untagged
        assert any(r["req_id"] == "REQ-003" for r in data["untagged"])

    def test_all_untagged(self, client_live):
        untagged_reqs = [{**r, "tags": []} for r in SAMPLE_REQS]
        with patch("main.get_requirements_by_engagement", return_value=untagged_reqs):
            resp = client_live.get(f"/engagement/{ENGAGEMENT}/process-mirror")
        assert resp.status_code == 200
        data = resp.json()
        assert data["by_tag"] == {}
        assert len(data["untagged"]) == 3

    def test_empty_engagement(self, client_live):
        with patch("main.get_requirements_by_engagement", return_value=[]):
            resp = client_live.get(f"/engagement/empty-eng/process-mirror")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["total_requirements"] == 0
        assert data["by_tag"] == {}
        assert data["untagged"] == []

    def test_db_error_returns_500(self, client_live):
        with patch("main.get_requirements_by_engagement", side_effect=Exception("connection refused")):
            resp = client_live.get(f"/engagement/{ENGAGEMENT}/process-mirror")
        assert resp.status_code == 500
        assert "connection refused" in resp.json()["detail"]

    def test_req_with_multiple_tags_appears_in_each_group(self, client_live):
        multi_tag_req = [{
            "req_id": "REQ-001",
            "engagement_id": ENGAGEMENT,
            "title": "Complex req",
            "description": "desc",
            "source_type": "Conversation",
            "tags": ["pain_point", "manual_step", "workaround"],
            "stakeholder": "CTO",
            "raw_input": None,
            "status": "open",
            "created_at": "2026-01-01T00:00:00",
        }]
        with patch("main.get_requirements_by_engagement", return_value=multi_tag_req):
            resp = client_live.get(f"/engagement/{ENGAGEMENT}/process-mirror")
        data = resp.json()
        assert len(data["by_tag"]) == 3
        for tag in ["pain_point", "manual_step", "workaround"]:
            assert data["by_tag"][tag][0]["req_id"] == "REQ-001"
        assert data["untagged"] == []
