# RAPID Enterprise Upgrade — Comprehensive Improvements

**Source:** Design authority review (top-tier consulting) + RAPID Enterprise Upgrade Prompt.  
**Purpose:** Single consolidated spec for UX, workflows, data capture, referential integrity, and agentic HITL.  
**Use with:** `docs/ENTERPRISE_UPGRADE_CHECKPOINT.md` and continuation prompt for a new agent.

---

## 1. Information Architecture & Navigation

### 1.1 Workflow-driven left sidebar (replace top nav)

- **Primary nav:** Left sidebar, always visible on desktop; collapsible to icon-only on mobile.
- **Sections in order:**
  - **RAPID** [logo]
  - **Home**
  - **SETUP:** Clients, Engagements
  - **DISCOVER:** Capture, Sources (new)
  - **ANALYSE:** Requirements, Fit/Gap, RICEFW
  - **GOVERN:** HITL Review, Audit Trail (promoted), Patterns
  - **COLLABORATE:** Agent Team, Platform Backlog
  - **SYSTEM:** System Health
- **Engagement context:** Persistent banner below logo: `[Client name] · [ENG-XXX] · [Engagement name]` with change button.
- **Active item:** Indigo left border on current nav item.
- **Progress in DISCOVER/ANALYSE:** e.g. "87 reqs · 9 gaps · 0 approved".

### 1.2 Single Engagement Workspace (design authority)

- **Engagement as primary workspace:** One engagement = one workspace with internal tabs:
  - Overview (KPIs, status, risks)
  - Current State (AS-IS mirror)
  - Requirements
  - Fit/Gap
  - RICEFW
  - HITL Review
  - Assets & Evidence
  - Agent Simulation & Platform Backlog
- **Routing:** Either `/engagement/[id]` with internal tabs or dedicated routes that always inherit `engagement_id`; no accidental cross-engagement actions.
- **Common layout:** Engagement context + HITL status indicators in every view.

### 1.3 Home page — Mission control dashboard

- Replace free-text "What would you like to do today?" with:
  - **Active engagement summary** (if set): pills for Reqs, Gaps, Approved, RICEFW count, HITL %.
  - **Next Actions** (AI-suggested, engagement-aware), e.g.:
    - "87 requirements need Fit-Gap assessment"
    - "9 gaps need RICEFW generation"
    - "0 assessments approved — start HITL review"
  - **Recent engagements** (last 5, clickable).
- Next Actions driven by GET hitl-queue + fit-gap-board; refresh on load.

---

## 2. Multi-Source Requirements Capture & Unified Capture Hub

### 2.1 Sources data model and API

- **New table `sources`:**
  - source_id (SRC-001), engagement_id, source_type (transcript|notes|excel|document|workshop), title, raw_content, file_url, file_name, status (uploaded|processing|extracted|reviewed), extracted_count, created_by, created_at.
- **Endpoints:** POST/GET /v1/sources, GET /v1/engagement/{id}/sources, POST /v1/sources/{id}/extract, PATCH, DELETE.
- **Requirements:** Add source_id, source_excerpt, extraction_confidence (and acceptance_criteria, kpi_impact, archived per upgrade prompt).

### 2.2 New /sources page

- **Left panel:** List of sources with status (Uploaded / Extracting / N reqs extracted).
- **Right panel:** Source detail, raw content preview, extracted requirements.
- **Actions:** "Extract Requirements" per source (AI extraction); "Accept All" / "Review Each"; link accepted requirements to source via source_id.
- **AI extraction prompt:** Senior SAP BA; extract requirements as JSON (title, description, business_process, priority, source_excerpt); return array only.

### 2.3 Capture Hub (design authority)

- **Modes:** Conversation (voice/text), File upload (docs, PPT, spreadsheets, PDFs), Consultant note paste, Excel template upload.
- **Asset record per captured item:** asset_id, engagement_id, asset_type, upload_source, raw_location, processed_status (pending|processing|processed|error).
- **LLM/vision jobs:** Extract candidate requirements, process steps, actors, systems, pain points; attach to Requirement/ProcessStep with source_asset_id and offset/timestamp.
- **Review Extracted Items queue:** Group by Asset, Process, confidence; show source snippet; Accept / Edit / Merge / Discard; update hitl_state and audit_event.

### 2.4 Capture page redesign

- **Header:** Active engagement pill + change.
- **Add Source:** [Upload File] [Paste Text] [Chat] [Use Template].
- **Sources for this engagement:** List (e.g. SRC-001 transcript ✅ 23 reqs; SRC-002 notes ⏳ Extracting; SRC-003 template 📥 Extract →).
- Chat creates a source record of type "conversation".

---

## 3. Requirements as Central Traceability Node

### 3.1 Requirement model enrichment

- **Minimum fields:** req_id, engagement_id, title, description, business_process (L2), subprocess (L3/L4 optional), status, priority, source_type, source_ref (FK to asset/source), kpi_impact (multi-select), fit_gap_status, hitl_state, acceptance_criteria, source_id, source_excerpt, extraction_confidence, archived.
- **business_process:** Mandatory; do not allow save without it.
- **Duplicate detection:** On create, call search by title_keywords; warn if similar requirements exist (POST /v1/requirements/{id}/duplicate-check or equivalent).

### 3.2 Dedicated /requirements page (first-class)

- **Filters (persistent, sessionStorage):** Engagement, Source (multi), Business process, Status, HITL state, Fit type, Priority, Has fit-gap (y/n), Has RICEFW (y/n), Text search.
- **Table:** REQ-ID (link), Title, Process, Priority, HITL pill, Fit type pill, Source (SRC-XXX tooltip), Created, Actions [Assess] [Review] [BPMN] [•••].
- **Bulk actions (when rows selected):** Run Fit-Gap on selected, Move HITL state, Export selected, Tag, Delete (with confirm).
- **Inline quick-edit:** Right-side drawer (not new page) with all fields, fit-gap summary, HITL history, source excerpt, links to BPMN and RICEFW.
- **Pagination:** Default 25 rows; 10/25/50/100 selector.

---

## 4. Referential Integrity & Completion Rules

### 4.1 Enforcement rules

- **Rule 1:** Cannot delete requirement with approved fit-gap assessment → "Archive instead"; add `archived` status.
- **Rule 2:** Cannot delete fit-gap assessment with linked RICEFW → "Remove RICEFW link first."
- **Rule 3:** Engagement "complete" only if: all requirements have fit-gap assessment; all assessments have HITL approved or out_of_scope; show completion checklist on engagement detail.
- **Rule 4:** RICEFW must reference at least one requirement (or type = standalone); show orphaned RICEFW warning.
- **Backend:** Return HTTP 409 with detail, conflict_type, blocking_ids when violated.

### 4.2 DB constraints

- req_id unique per engagement.
- FitGapAssessment requires Requirement.
- ProcessStep requires Requirement.
- Cascade/block deletes per rules above.
- GET /v1/engagement/{id}/completion-check for checklist data.

---

## 5. Fit-Gap Page Overhaul

### 5.1 Summary and filters

- **Sticky summary bar:** Total; counts per fit_type; approved count; effort range; cost estimate (effort × $2,500/day, configurable).
- **Filter bar:** Process (chips), Complexity (XS–XL), HITL state, "Show gaps only" toggle.
- **Process view toggle:** Group by business_process with fit_type breakdown per process.

### 5.2 Cards and batch actions

- **Cards:** source_id badge (tooltip: title), confidence_score (green/amber/red), effort_days, one-click approve, "Override" for full review modal.
- **Batch:** Select all in column; "Approve all selected"; "Generate RICEFW from selected gaps".
- **Inline Fit/Gap on Requirements tab (design authority):** Inline fit/gap status; click opens side panel with scope IDs, rationale, complexity/effort; bulk "Analyse All Open" with hitl_state = needs_sme_review.

### 5.3 AI confidence and re-assessment

- confidence_score < 0.7 → "Low confidence — review recommended".
- "Re-assess" per card (force_refresh=true); POST analyse-all?force=true option.

---

## 6. HITL Review Page Overhaul

### 6.1 Column and card design

- **Column headers:** Count + short description (e.g. "AI DRAFT — Auto-assessed; review confidence before moving").
- **Cards:** AI rationale (first sentence, expandable), fit_type, confidence, source_id; [Approve] [Needs SME Review] [Reject] [Out of Scope]; approved cards show reviewer + timestamp.
- **Detail panel (click card):** Full requirement, source excerpt, AI rationale, fit-gap details, HITL history timeline, review form (notes + actions).

### 6.2 HITL states and roles

- **States:** ai_draft → needs_sme_review → needs_architect_review → approved → implemented.
- **Role-based:** SME can move to needs_architect_review or back to ai_draft; Architect can approve or out_of_scope.
- **HITL report:** GET /v1/engagement/{id}/hitl-report → Excel (requirements + state, HITL events log, summary by process/fit_type).

---

## 7. RICEFW Page Overhaul

- **Summary bar:** Total; by type (R/I/C/E/F/W/A); by status; effort range.
- **Table:** RICEFW-ID, Type badge, Name, Linked REQ-IDs (clickable chips), Complexity, Status (inline edit), Priority, [Edit] [Link Req] [Delete].
- **Traceability:** Each item shows linked requirements; REQ chip opens requirement drawer.
- **Generate from Gaps:** Show diff "N new created, M already existed"; auto-link to source requirements.

---

## 8. Process Steps & Process Mirror (AS-IS / TO-BE)

- **ProcessStep upgrade:** view_type (current_state | future_state), lane (role/system), is_pain_point, is_secret_sauce, is_control_point, step_type, branch_id.
- **Current State tab:** Auto-updating Process Mirror from AS-IS ProcessSteps; click step → linked requirements, pain points, evidence.
- **Future State tab:** TO-BE flows from requirements and fit/gap; visual diff (added/removed/changed steps).

---

## 9. Audit Trail & Governance

- **Standalone /audit page:** Filter (entity_type, action, date range, actor); timeline newest first; each event: timestamp, actor, action badge, entity link, summary, [Expand] for full JSON.
- **Export:** Download audit trail as Excel for compliance.
- **Audit:** Every state-changing action writes audit_event (actor, action, source, entity); export per engagement for auditors.

---

## 10. Data Capture & Forms

### 10.1 Client form

- Inline validation (blur) on required fields.
- "Import from Excel template" at top.
- After create → auto-navigate to Create Engagement with client pre-selected.
- Client completeness score (0–100%) on client detail.

### 10.2 Engagement form

- **Project setup wizard (3 steps):** Basic info → Team (PM, sponsor) → Scope (processes, countries, regulatory).
- **Engagement health score:** % requirements with assessments, % approved, % RICEFW status > identified.

### 10.3 Requirement form

- Duplicate detection warning (similar title).
- Mandatory business_process.
- KPI impact multi-select (Cost Reduction, Revenue Growth, Risk Mitigation, Compliance, Efficiency, Customer Experience).
- Acceptance criteria textarea.

---

## 11. Onboarding & Empty States

### 11.1 First-time user wizard

- When no engagements: 3-step guided setup:
  - Step 1: Create client (name, industry, website pre-fill).
  - Step 2: Set up engagement (name, dates).
  - Step 3: Add first requirements (Upload / Paste / Chat).
- [Back] [Next] [Launch].

### 11.2 Empty states

- Every empty state: explanation + primary action + optional "Learn more".
- Examples: No requirements → [Capture your first requirement →]; No fit-gap → [Analyse All →]; No RICEFW → [Generate from Gaps →]; No sources → [Add Source →].

---

## 12. Performance & UX Polish

- **Loading:** Skeleton loaders (table rows, cards, pills) instead of spinners; match content shape.
- **Optimistic updates:** HITL and fit-gap approve update UI immediately; "Saving..."; revert on API failure.
- **Parallel fetch:** Fit-Gap board uses single fit-gap-board call; no per-requirement calls.
- **No modals for destructive actions:** Inline confirmation patterns.
- **IDs:** Monospace; copy-to-clipboard on click.

---

## 13. Backend Additions (Summary)

- **New:** POST/GET/PATCH/DELETE sources; POST /sources/{id}/extract; GET completion-check; GET hitl-report; GET audit (or rename audit-trail); POST requirements duplicate-check.
- **Modified:** POST requirements (business_process required, duplicate check); DELETE requirement (block if approved FGA); POST ricefw (req_id required unless standalone); DELETE fit-gap (block if linked RICEFW).
- **Schema:** sources table; requirements: source_id, source_excerpt, extraction_confidence, acceptance_criteria, kpi_impact, archived.
- **Self-test:** /v1/engagement/self-test (or per-domain) for integrity checks; expose on /system-health.

---

## 14. Agent Personas & Learning

- **Agent roles:** A_Lead_Consultant, A_Business_Analyst, A_Manufacturing_SME, A_Finance_SME, A_Integration_Architect (and existing A_*); mandate, focus_areas, behavior_rules, escalation_rules.
- **Simulate tab:** Agent operates on current engagement_id; reads context (client, industry, processes, requirements); suggests next steps, missing requirements, fit/gap refinements.
- **Learning loop:** User marks suggestion good/bad → hitl_events; use to adjust prompts/weights over time.

---

## 15. Enterprise & Cursor-Friendly

- **Security:** engagement_id + client_id mandatory filters; optional user/role (SME by process, Architect all).
- **API contracts:** OpenAPI accurate; required/optional clear; errors with machine-readable codes, human message, request_id, entity_ref.
- **Seed data:** Synthetic engagement (e.g. 50–100 requirements, process flows, fit/gap, RICEFW, HITL history).
- **Regression:** "Run regression scenario" button or script (Client → Engagement → Capture → Fit/Gap → RICEFW → Export).
- **Design constraints:** Dark theme #0d1117/#161b22/#30363d/#e6edf3; indigo primary; status colours; Geist/Inter; 8px radius cards; pagination 25 default.

---

## 16. Implementation Order (Phases)

- **Phase A — Foundation:** Sources table + requirement columns; sources endpoints; deploy backend.
- **Phase B — Navigation:** Left sidebar; engagement banner; empty states; skeleton loaders.
- **Phase C — Sources & Capture:** /sources page; AI extract; link reqs to source; duplicate detection.
- **Phase D — Requirements:** Dedicated /requirements page; filters; drawer; bulk actions; referential integrity on delete.
- **Phase E — Fit-Gap & HITL:** Fit-gap filters, batch approve, cost bar; HITL cards, detail panel, hitl-report.
- **Phase F — Referential integrity:** completion-check; engagement completion checklist; RICEFW link enforcement; block delete when needed.
- **Phase G — Onboarding:** First-time wizard; Next Actions on home.

Test after each phase (health, sources, fit-gap-board, requirements, frontend build); deploy before next phase.
