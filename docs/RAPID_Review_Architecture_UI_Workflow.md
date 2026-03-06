# RAPID — System Architecture, UI & Workflow Review

**Document purpose:** Standalone specification for a third-party reviewer to understand the RAPID system and provide structured feedback, with emphasis on **user experience (UX)** and improvement opportunities.  
**Audience:** Design authority, UX lead, or consultant reviewing the product.  
**Version:** As of March 2026.  
**Live app:** https://rapid-ui-wine.vercel.app (frontend) | API: https://rapid-mvp-production.up.railway.app  

---

## 1. Executive summary

RAPID is an AI-powered platform for SAP S/4HANA scope and gap analysis used in implementation engagements. Consultants capture requirements from multiple sources, run fit/gap assessments, manage RICEFW (Reports, Interfaces, Conversions, Enhancements, Forms, Workflows), and use human-in-the-loop (HITL) review for quality and traceability. This document describes the **system architecture**, **user interface**, and **end-to-end workflows** so a reviewer can assess clarity, consistency, and UX and suggest improvements.

---

## 2. System architecture

### 2.1 High-level topology

- **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS. Hosted on Vercel. Single-page feel with client-side navigation; auth is mock (sessionStorage).
- **Backend:** FastAPI (Python), REST over JSON. Hosted on Railway. All data/action APIs are under `/v1` (e.g. `/v1/clients`, `/v1/requirements`).
- **Data:** Supabase (PostgreSQL + optional storage). All engagement-scoped data is isolated by `engagement_id`; client data is never mixed across engagements.
- **Integrations:** Optional Anthropic (LLM) for gap analysis, requirement extraction, and process-step extraction. Optional API key for backend; CORS restricted to known origins.

### 2.2 Core data model (simplified)

| Entity        | Purpose |
|---------------|--------|
| **Client**    | Organisation (name, industry, strategy, benchmarks). One client has many engagements. |
| **Engagement**| Project/workspace. All requirements, RICEFW, fit-gap, HITL, and assets are scoped to one engagement. |
| **Requirement** | Single requirement (title, description, business process, priority, status, HITL state, optional source_id). |
| **Fit-gap assessment** | Per-requirement fit/gap result (fit_type, complexity, effort, HITL state, reviewer). |
| **RICEFW inventory** | R/I/C/E/F/W items linked to requirements; created manually or “from gaps”. |
| **Process steps** | As-is process steps per requirement (BPMN-like; used in workflow view). |
| **Sources** | Multi-source capture (transcript, notes, document, Excel) with optional AI extraction. |
| **Audit / HITL events** | Audit trail and HITL state changes for compliance. |

### 2.3 API surface (relevant to UX)

- **Setup:** Clients CRUD, Engagements CRUD, client prefill from URL.
- **Discover:** Capture (extract from transcript), Sources CRUD, source extract (stub).
- **Analyse:** Requirements CRUD, Fit-Gap (analyse-all, board, review), RICEFW CRUD, ricefw-generate from gaps, process-steps CRUD + extract.
- **Govern:** HITL queue, HITL events, audit-trail, completion-check, pattern library, feedback.
- **Collaborate:** Agent roles, simulate agent response, platform issues, engagement platform-backlog.
- **Export:** Requirements Excel export, template download, (planned) HITL report Excel.

### 2.4 Security and constraints

- Engagement and client IDs are required filters on all relevant endpoints.
- No cross-engagement data exposure. Optional API key and admin key for migrate/retain.
- 5xx responses return a generic message and request_id; details are server-log only.

---

## 3. User interface specification

### 3.1 Layout and navigation

- **Layout:** Left sidebar (primary nav) + main content area. Top bar shows current user and Log out.
- **Sidebar sections (workflow-oriented):**
  - **Home**
  - **SETUP:** Clients, Engagements
  - **DISCOVER:** Capture, Sources
  - **ANALYSE:** Requirements, Fit/Gap, RICEFW (RICEFW is engagement page with #ricefw)
  - **GOVERN:** HITL Review, Audit Trail, Patterns
  - **COLLABORATE:** Agent simulation, Platform backlog
  - **SYSTEM:** System Health
- **Engagement context:** A “Working in” banner under the logo shows current engagement (and client when loaded) with a “Change” link. Links to Fit/Gap, HITL, Requirements, Sources, etc. carry `engagement_id` in the URL when an engagement is selected.
- **Active state:** Current nav item has an indigo left border and distinct background.

### 3.2 Design system (current)

- **Theme:** Dark. Background #0d1117 / #0f172a; surfaces #161b22–#1e293b; text white/slate; accent indigo.
- **Typography:** Geist/Inter family; monospace for IDs (e.g. REQ-001, ENG-001).
- **Tags/badges:** Pain Point (red), Manual Step (orange), Secret Sauce (purple), Workaround (yellow), Hand-off (cyan). Priority: Must-Have (red), Should-Have (amber), Nice-to-Have (slate). Status: open (blue), in_progress (amber), analysed (emerald), closed (slate).
- **Cards/tables:** Rounded corners (e.g. 8px), bordered panels; tables with header row and alternating or hover states where applicable.

### 3.3 Key screens (as implemented)

| Screen        | Route(s)        | Purpose |
|---------------|-----------------|--------|
| **Home**      | `/`             | Welcome; mission control (engagement summary pills + Next Actions when engagement set); “What would you like to do today?”; shortcuts to Clients / Engagements; recent open engagements table. |
| **Login**     | `/login`        | Mock sign-in (any username/password). |
| **Clients**   | `/clients`      | List clients; create client/engagement; engagements table. |
| **Client detail** | `/clients/[id]` | Client info; list of engagements. |
| **Engagement**| `/engagement`, `/engagement/[id]` | List/select engagement; detail with requirements list, RICEFW tab (#ricefw), benchmark insights, import/export. |
| **Capture**   | `/capture`      | Conversation capture; engagement selector; extract requirements from transcript. |
| **Sources**   | `/sources`      | List sources for engagement; empty state when none. |
| **Requirements** | `/requirements` | List requirements for engagement; table with Open to engagement. |
| **Fit/Gap**   | `/fitgap`       | Engagement selector; Analyse All; board by fit type; process view; review modal. |
| **HITL Review** | `/hitl`         | HITL queue by state; review and approve assessments. |
| **Audit Trail** | `/audit`        | Timeline of audit and HITL events for engagement. |
| **Patterns**  | `/patterns`     | Pattern library by category. |
| **Agent simulation** | `/simulate`  | Select engagement and role; send message; view agent reply. |
| **Platform backlog** | `/platform-backlog` | List and manage platform issues by engagement. |
| **Workflow**  | `/workflow/[reqId]` | BPMN-style process steps for a requirement. |
| **System Health** | `/system-health` | Checks for API, clients, engagements (e.g. Zero EV seed). |

### 3.4 Engagement context and empty states

- When no engagement is selected, pages such as Sources, Requirements, Audit show an empty state: “Select an engagement to…” with a link to the Engagement list.
- Recent engagements on Home show Reqs · RICEFW · Gaps counts where available.
- Mission control (Home) shows summary pills (Reqs, Gaps, Approved, RICEFW, HITL %) and Next Actions (e.g. “N requirements need Fit-Gap assessment”) only when an engagement is loaded.

---

## 4. Workflows (end-to-end)

### 4.1 Setup: Client and engagement

1. User signs in (mock).
2. From Home or SETUP, goes to Clients; creates a client (or chooses existing).
3. Creates an engagement for that client (or selects existing).
4. “Load” or “Open” an engagement sets the global engagement context and optionally stores it in session; sidebar shows “Working in” for that engagement.

**UX focus:** Ease of creating client vs engagement; clarity of “current engagement”; discoverability of “Change” engagement.

### 4.2 Discover: Capture and sources

1. User selects an engagement (if not already set).
2. **Capture:** Enters or pastes conversation/transcript; triggers “Extract requirements”; requirements are created and linked to the engagement.
3. **Sources:** Lists sources for the engagement (e.g. transcript, notes, document). Extract per source is available as an API (stub in UI). Future: “Accept All” / “Review Each” and link requirements to sources.

**UX focus:** Clarity of “Add source” vs “Capture”; feedback during extraction; linking sources to requirements; empty states.

### 4.3 Analyse: Requirements, Fit/Gap, RICEFW

1. **Requirements:** User sees list of requirements for the engagement; can open engagement detail to see full requirement detail, process steps, and RICEFW.
2. **Fit/Gap:** User runs “Analyse All” (or per-requirement) to generate fit-gap assessments; views board by fit type or by process; opens review modal to approve or send back with notes.
3. **RICEFW:** From engagement detail (#ricefw), user runs “Generate from Gaps” to create RICEFW items from approved gap assessments; can edit/link RICEFW items.

**UX focus:** Number of clicks to “analyse then review”; clarity of board columns and states; visibility of “what’s left to do”; traceability from requirement → fit-gap → RICEFW.

### 4.4 Govern: HITL and audit

1. **HITL:** User opens HITL Review; sees queue grouped by state (e.g. ai_draft, needs_sme_review, approved); reviews and approves or rejects with notes.
2. **Audit:** User opens Audit Trail; sees chronological list of HITL and audit events for the engagement.

**UX focus:** Ease of moving items through states; clarity of “who does what” (SME vs architect); value of audit for compliance; export (e.g. Excel) for auditors.

### 4.5 Collaborate: Agent and platform backlog

1. **Agent simulation:** User selects engagement and agent role; sends a message; sees agent reply (draft).
2. **Platform backlog:** User views platform issues for the engagement; can add, start, resolve issues.

**UX focus:** Usefulness of agent in context of the engagement; clarity of platform backlog vs requirement backlog.

---

## 5. Specification for reviewer feedback

The following sections are for the **third-party reviewer** to structure their feedback. Please comment on each area where you have observations; **user experience (UX)** is of particular interest.

### 5.1 Architecture and information flow

- Is the split between “setup → discover → analyse → govern → collaborate” clear and logical for a consultant?
- Are there missing concepts or entities (e.g. “project phase”, “deliverable”, “sign-off”) that would improve real-world use?
- Any concerns about engagement-scoped data isolation or performance (e.g. large requirement lists, many fit-gap cards)?

### 5.2 Navigation and wayfinding

- Is the **left sidebar** structure (SETUP, DISCOVER, ANALYSE, GOVERN, COLLABORATE, SYSTEM) intuitive? Would you rename, reorder, or group items differently?
- Is the **engagement context** (“Working in …”) always visible and sufficient? Should “Change” be more prominent or repeated in the main content?
- Do you find yourself losing context (e.g. “which engagement am I in?”) on any screen? Which ones?

### 5.3 Home and mission control

- Does the **mission control** block (summary pills + Next Actions) help you decide what to do next? What’s missing (e.g. deadlines, assignees, risk)?
- Is the balance right between “guidance” (Next Actions) and “free choice” (Clients / Engagements links)? Would you prefer a stronger “wizard” or a more minimal home?

### 5.4 Key workflows (UX)

- **Capture → Requirements:** Is it clear how to go from “I have a transcript” to “I have requirements in the system”? What would reduce friction?
- **Fit/Gap:** Is “Analyse All” then “board then review” the right mental model? Are the columns and states (e.g. ai_draft, approved) clear? What would make batch approval or “re-assess” clearer?
- **RICEFW from gaps:** Is “Generate from Gaps” discoverable and understandable? Is traceability (requirement ↔ RICEFW) obvious enough?
- **HITL:** Is the queue view (by state) useful? Do you need role-based views (SME vs architect)? What would make approval/reject faster and safer?

### 5.5 Consistency and polish

- **Empty states:** When there are no requirements, no sources, or no engagement selected, are the messages and primary actions (e.g. “Choose engagement”, “Capture your first requirement”) clear and consistent?
- **Loading and errors:** Where do you see spinners or generic errors? Would skeleton loaders or more specific messages help?
- **Terminology:** Is the use of “engagement”, “requirement”, “fit-gap”, “RICEFW”, “HITL”, “source” consistent and appropriate for your audience (e.g. SAP consultants, PMs)?

### 5.6 Accessibility and inclusivity

- Can you complete the main flows using only keyboard and/or a screen reader? What’s missing (focus order, labels, contrast)?
- Is the dark theme comfortable for long sessions? Any issues with contrast or readability of badges/tables?

### 5.7 Gaps and improvements (open list)

- List up to 10 improvements (in order of impact if possible) that would most improve **user experience** or **adoption**.
- List any **missing features** (e.g. reporting, notifications, collaboration, mobile) that you consider important for a v2.

---

## 6. How to use this document

- **Reviewer:** Read sections 2–4 for architecture, UI, and workflows; use section 5 to structure written or verbal feedback. Focus on UX where possible.
- **Product owner:** Share this document (e.g. as a file or PDF) with the reviewer; collect feedback and prioritise changes.
- **No dependency:** This document is standalone and is not part of the in-repo “system design” or implementation specs; it is for review and feedback only.

---

## 7. Document metadata

| Field   | Value |
|---------|--------|
| Title   | RAPID — System Architecture, UI & Workflow Review |
| Purpose | Third-party review and feedback (architecture, UI, workflow, UX) |
| Live app | https://rapid-ui-wine.vercel.app |
| API     | https://rapid-mvp-production.up.railway.app |
| As of   | March 2026 |
