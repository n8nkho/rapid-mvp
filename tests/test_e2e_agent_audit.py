"""
E2E-style tests for agentic era: agent roles, simulate (mocked), platform-issues, audit trail, HITL queue.
All external calls mocked; validates API contracts and audit logging.
"""
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from tests.conftest import API_PREFIX

ENGAGEMENT = "eng-e2e-001"


@pytest.fixture
def client():
    return TestClient(app)


class TestAgentRolesE2E:
    def test_get_agent_roles_returns_seven(self, client):
        with patch("main.list_agent_roles") as m:
            m.return_value = [
                {"role_id": "lead_consultant", "name": "Lead Consultant"},
                {"role_id": "ba", "name": "BA"},
            ] + [{"role_id": f"r{i}", "name": f"R{i}"} for i in range(5)]
            r = client.get(f"{API_PREFIX}/agent-roles")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert data["total"] >= 2


class TestSimulateAgentResponseE2E:
    def test_simulate_logs_audit_event(self, client):
        role = {"role_id": "lead_consultant", "name": "Lead", "mandate": "M", "focus_areas": [], "behavior_rules": "", "escalation_rules": ""}
        with (
            patch("main.get_agent_role_by_role_id", return_value=role),
            patch("main.get_agent_knowledge_by_role", return_value=[]),
            patch("main.get_provider") as p,
            patch("main.create_audit_event") as audit,
        ):
            p.return_value.complete.return_value = {"content": "Use fit-to-standard."}
            r = client.post(
                f"{API_PREFIX}/simulate/agent-response",
                json={"engagement_id": ENGAGEMENT, "agent_role_id": "lead_consultant", "context_message": "What next?"},
                headers={"X-Actor-Id": "user-1", "X-Actor-Role": "consultant"},
            )
        assert r.status_code == 200
        assert r.json().get("reply") == "Use fit-to-standard."
        audit.assert_called_once()
        call_kw = audit.call_args[1] if audit.call_args[1] else {}
        assert call_kw.get("action") == "agent_response"
        assert call_kw.get("actor_id") == "user-1"
        assert call_kw.get("actor_role") == "consultant"


class TestPlatformIssuesE2E:
    def test_create_platform_issue_logs_audit(self, client):
        with (
            patch("main.create_platform_issue") as m,
            patch("main.create_audit_event") as audit,
        ):
            m.return_value = {"id": "pi-1", "engagement_id": ENGAGEMENT}
            r = client.post(
                f"{API_PREFIX}/platform-issues",
                json={"engagement_id": ENGAGEMENT, "problem_description": "Missing field X"},
                headers={"X-Actor-Role": "business_user"},
            )
        assert r.status_code == 201
        audit.assert_called_once()
        assert audit.call_args[1].get("action") == "platform_issue_created"


class TestAuditTrailE2E:
    def test_audit_trail_merges_hitl_and_audit(self, client):
        with (
            patch("main.list_hitl_events", return_value=[{"event_id": "HEV-001", "created_at": "2026-03-04T10:00:00Z", "actor": "Jane"}]),
            patch("main.list_audit_events_by_engagement", return_value=[{"id": "ae-1", "action": "agent_response", "created_at": "2026-03-04T10:01:00Z"}]),
        ):
            r = client.get(f"{API_PREFIX}/engagement/{ENGAGEMENT}/audit-trail")
        assert r.status_code == 200
        data = r.json()
        assert data["engagement_id"] == ENGAGEMENT
        assert "events" in data
        assert len(data["events"]) == 2
        sources = {e.get("_source") for e in data["events"]}
        assert "hitl" in sources and "audit" in sources


class TestFitGapBoardE2E:
    def test_fit_gap_board_structure(self, client):
        with (
            patch("main.get_requirements_by_engagement", return_value=[
                {"req_id": "REQ-001", "title": "R1", "business_process": "P2P"},
                {"req_id": "REQ-002", "title": "R2", "business_process": "O2C"},
            ]),
            patch("main.get_fit_gap_by_engagement", return_value=[
                {"assessment_id": "FGA-001", "req_id": "REQ-001", "fit_type": "fit_standard", "complexity": "S"},
                {"assessment_id": "FGA-002", "req_id": "REQ-002", "fit_type": "gap_ricefw", "complexity": "M"},
            ]),
        ):
            r = client.get(f"{API_PREFIX}/engagement/{ENGAGEMENT}/fit-gap-board")
        assert r.status_code == 200
        data = r.json()
        assert "by_fit_type" in data
        assert "summary" in data
        assert data["summary"]["total"] == 2


class TestHitlQueueE2E:
    def test_hitl_queue_returns_requirements_by_state(self, client):
        with patch("main.get_requirements_by_engagement", return_value=[
            {"req_id": "REQ-001", "hitl_state": "ai_draft", "title": "Req 1", "business_process": "P2P"},
            {"req_id": "REQ-002", "hitl_state": "needs_sme_review", "title": "Req 2", "business_process": "O2C"},
        ]):
            r = client.get(f"{API_PREFIX}/engagement/{ENGAGEMENT}/hitl-queue")
        assert r.status_code == 200
        data = r.json()
        assert "summary" in data
        assert data["summary"]["total"] == 2
        assert "by_state" in data["summary"]
