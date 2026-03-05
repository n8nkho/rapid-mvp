# Agentic-Era UI Design: Human-in-the-Loop, Safeguards & Audit Compliance

This document describes the target experience for RAPID in the agentic era: a future-proof UI that puts **humans in the loop**, enforces **safeguards**, and stays **audit compliant**, while delivering a world-class experience for **consultants** and **business users**.

---

## 1. Design principles

- **Human-in-the-loop (HITL)**  
  AI proposes; humans decide. Every material change (approvals, scope, fit/gap) flows through explicit human review and action.

- **Audit compliance**  
  Every material action is logged (who, what, when, context). The UI surfaces an audit trail and supports export for compliance.

- **Role-aware experience**  
  Consultants get power-user flows (bulk actions, maturity, platform backlog). Business users get guided, low-friction flows with clear approvals and explanations.

- **Safeguards**  
  Destructive or high-impact actions require confirmation; sensitive data is scoped by engagement and role; agent outputs are clearly labeled as draft until approved.

---

## 2. Human-in-the-loop (HITL) flows

### 2.1 Requirement lifecycle (HITL states)

- **States:** `ai_draft` → `needs_sme_review` → `needs_architect_review` → `approved` | `out_of_scope`
- **UI:**
  - **HITL queue** (GET `/v1/engagement/{id}/hitl-queue`): Board or list grouped by state. Consultants can move items between columns; business users see “Needs your review” and simple Approve / Request changes.
  - **Per-requirement:** Show current state, “Last reviewed by” and timestamp. Buttons: “Submit for SME review”, “Approve”, “Mark out of scope”, “Send back to draft”.
  - **Bulk actions (consultant):** “Submit all in AI draft for SME review”, “Approve all in architect review”.

### 2.2 Agent conversation (simulate)

- **Safeguards:**
  - Every agent reply is visually labeled: “Agent suggestion (draft)”.
  - Option to “Log as platform issue” from the same screen (POST `/v1/platform-issues`) so limitations are captured without leaving context.
- **Audit:** Frontend sends `X-Actor-Id` and `X-Actor-Role` (e.g. `consultant`, `business_user`) on POST `/v1/simulate/agent-response` so the backend can log who triggered the conversation (see Audit trail below).
- **Consultant vs business:** Consultants can pick phase and role; business users get a simplified “Ask the agent” with a single role and current phase.

### 2.3 Fit/gap and scope

- **Fit/gap board** (GET `/v1/engagement/{id}/fit-gap-board`): Read-only view of by_fit_type, by_process, summary. Changing fit/gap is done via requirement-level actions (which are HITL and audited).
- **Approvals:** “Approve scope” or “Approve fit/gap” are explicit actions that should write to the audit trail (when implemented in backend).

---

## 3. Audit trail and compliance

### 3.1 Unified audit trail API

- **GET /v1/engagement/{engagement_id}/audit-trail**  
  Returns a merged list of:
  - **HITL events** (e.g. requirement state changes, approvals).
  - **Audit events** (e.g. `agent_response`, `platform_issue_created`, `platform_issue_updated`).

- Each event includes:
  - `created_at`, `action`, `entity_type`, `entity_id`
  - `actor_id`, `actor_role` (when provided via headers)
  - `details` (JSON) and `_source` (`"hitl"` | `"audit"`) for filtering and compliance reporting.

### 3.2 UI: Audit trail view

- **Location:** Engagement-level tab or page: “Audit trail” or “Activity log”.
- **Content:** Chronological list (newest first). Show: timestamp, actor (id/role), action, entity type/id, and a short summary from `details`.
- **Filters:** By `_source` (HITL vs audit), by action type, by date range.
- **Export:** “Export for compliance” (CSV/JSON) scoped to engagement and filters. Backend can add a dedicated export endpoint later; initially use client-side export of the same API response.

### 3.3 Sending actor context (compliance)

- For actions that support it, frontend should send:
  - **X-Actor-Id:** current user id (or “anonymous” if not logged in).
  - **X-Actor-Role:** `consultant` | `business_user` | `admin`.
- Used today for: POST `/v1/simulate/agent-response`, POST `/v1/platform-issues`, PATCH `/v1/platform-issues/{id}`.

---

## 4. Consultant vs business user experience

| Area | Consultant | Business user |
|------|------------|----------------|
| **Agent simulation** | Full control: role, phase, context; multi-turn. | Simple “Ask” with one role and current phase. |
| **HITL queue** | Board view; bulk submit/approve; move between states. | List “Needs your review”; single-item Approve / Request changes. |
| **Platform backlog** | Create, triage, assign priority/status; link to agent context. | View only (or create with minimal fields). |
| **Audit trail** | Full view; filter by source/action; export. | Read-only timeline for their engagement. |
| **Fit/gap** | Drill into by_fit_type, by_process; drive approvals. | Summary and high-level status. |

Differentiation can be done via role claims (e.g. from auth) or feature flags; the same APIs support both.

---

## 5. Safeguards in the UI

- **Destructive actions:** “Mark out of scope”, “Delete”, “Bulk approve” require confirmation modal with short explanation.
- **Agent output:** All agent-generated text (replies, suggested requirements) is visually distinct (e.g. “Draft”, “AI suggestion”) and not treated as approved until a human action is recorded.
- **Scoping:** All lists and audit trail are engagement-scoped; no cross-engagement data in one view unless explicitly an admin view.
- **Platform issues:** Creating an issue from the agent screen pre-fills context (phase, role) so the audit trail can link issue to conversation.

---

## 6. Implementation checklist (frontend)

When implementing in **rapid-ui**:

1. **Agent simulation page**  
   Use GET agent-roles and POST simulate/agent-response; send `X-Actor-Id` and `X-Actor-Role`; label agent replies as draft; add “Log as platform issue”.

2. **Platform backlog page**  
   Use GET/POST/PATCH platform-issues and GET platform-backlog; send actor headers on create/update.

3. **Audit trail view**  
   GET `/v1/engagement/{id}/audit-trail`; display merged timeline; filters by `_source` and action; export (client-side or future API).

4. **HITL queue**  
   GET hitl-queue; board or list by state; state-change actions (with audit logged in backend when those endpoints exist).

5. **Fit/gap board**  
   GET fit-gap-board; read-only by_fit_type/summary; link to requirement-level HITL.

6. **Role-aware layout**  
   Show/hide or simplify sections based on consultant vs business_user (from auth or flags).

---

## 7. Backend alignment

- **Audit events:** Stored in `audit_events`; key actions (agent_response, platform_issue_created/updated) already logged with optional actor headers.
- **Audit trail API:** Merges HITL events and audit_events; returns `_source` for compliance.
- **E2E tests:** `tests/test_e2e_agent_audit.py` covers agent roles, simulate+audit, platform issues+audit, audit-trail merge, fit-gap-board, hitl-queue.

Production: ensure `audit_events` table exists (run migrations or apply `_AUDIT_EVENTS_DDL` in Supabase).
