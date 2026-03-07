# RAPID — System Architecture, UI & Workflow Review Spec

**Purpose:** Standalone document for a third-party reviewer to understand the RAPID system and provide structured feedback, especially on **user experience (UX)** and improvements.  
**Audience:** Reviewer (consultant, designer, or stakeholder) who will not have access to the codebase.  
**Do not integrate this file into the system design** — it is for external review only.

---

## 1. Executive Summary

RAPID is an AI-powered tool for SAP S/4HANA implementation. It helps consulting teams and clients:

- **Capture** business requirements (conversation, transcript, templates).
- **Map** requirements to SAP scope (gap analysis, fit/gap assessment).
- **Manage** RICEFW customisation inventory, HITL review, and audit trail.
- **Simulate** agent personas (Business and Consulting) and track platform issues.

The system consists of a **FastAPI backend** (Python, Railway), a **Next.js frontend** (TypeScript, Vercel), and **Supabase** for persistence. All work is **scoped to a single engagement**; client data is isolated per engagement.

---

## 2. System Architecture

### 2.1 High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  User (Browser)                                                  │
│  https://rapid-ui-wine.vercel.app                                │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (Next.js 16, TypeScript, Tailwind)                     │
│  - App Router, dark theme (#0f172a)                              │
│  - Session storage for auth + current engagement                 │
└────────────────────────────┬────────────────────────────────────┘
                             │ /v1/* (JSON, optional X-API-Key)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend (FastAPI, Python)                                       │
│  https://rapid-mvp-production.up.railway.app                    │
│  - /v1: clients, engagements, requirements, fit-gap, RICEFW,     │
│    agent-roles, simulate, platform-issues, audit-trail, etc.     │
│  - /health, /health/ready                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Supabase (PostgreSQL + Storage)                                 │
│  - clients, engagements, requirements, process_steps,            │
│    ricefw_inventory, fit_gap_assessments, hitl_events,           │
│    audit_events, agent_roles, platform_issues, assets, etc.      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Backend (API)

- **Stack:** FastAPI, Python 3.x, Supabase client, OpenAI/Anthropic for LLM features.
- **Base path:** All data/action routes under `/v1` (e.g. `/v1/clients`, `/v1/engagement/{id}/fit-gap-board`).
- **Auth:** Optional API key via header `X-API-Key`; admin operations use `X-Admin-Key` when `ADMIN_API_KEY` is set.
- **Key domains:**
  - **Clients & Engagements:** CRUD; client prefill from website (LLM extracts many fields: name, industry, sub_industry, employees, locations, revenue, systems, countries, regulatory, strategy, goals, products, value proposition, executives, competitors, substitutes, sector_archetype, erp_maturity, complexity_drivers); PATCH for auto-save.
  - **Requirements:** CRUD; RTM Excel import/export; template download.
  - **Process steps:** CRUD per requirement; extract from transcript (LLM); BPMN generation.
  - **Fit/Gap:** Create assessment, get board, review (approve/notes), analyse-all.
  - **RICEFW:** List/add/edit/delete per engagement; generate from gaps; export Excel.
  - **Agent team:** Agent roles (incl. A_Engagement_Manager for client/engagement setup), simulate agent response, platform issues, platform backlog. A_Engagement_Manager assists on Create Client and Create Engagement (Ask Eng Manager); when user pastes a company URL, UI can auto run pre-fill from website.
  - **Audit:** Audit trail per engagement (HITL + audit events).
- **Engagement scope:** Every endpoint that reads/writes data filters by `engagement_id`; client data is never mixed across engagements.

### 2.3 Frontend (UI)

- **Stack:** Next.js 16 (App Router), TypeScript, Tailwind CSS.
- **Theme:** Dark background `#0f172a`; indigo/slate accents; consistent status and priority colours.
- **Auth:** Mock login (sessionStorage); all routes except `/login` require auth.
- **Engagement context:** Current engagement stored in context + sessionStorage; header shows “Working in: &lt;client&gt; · ENG-XXX · &lt;name&gt;” when set.
- **API usage:** Central `apiGet` / `apiFetch` with `API_URL` and optional `X-API-Key`; errors show `request_id` and user-friendly messages.

### 2.4 Data Model (Simplified)

- **Client:** name, industry, employees, legal_entities, systems, countries, regulatory, strategy fields, sector_archetype, erp_maturity, benchmark_opt_in.
- **Engagement:** client_id, name, description, status, planned/actual dates, project_manager, sponsor, risk_level, health.
- **Requirement:** req_id, engagement_id, title, description, status, priority, business_process, tags, sign_off_status, hitl_state, kpi_impact, etc.
- **ProcessStep:** req_id, engagement_id, step_number, title, performer_name, shape (start/end/process/decision/document), step_type (manual/system/agentic), is_pain_point, branches.
- **Fit/Gap assessment:** req_id, engagement_id, fit_type, complexity, rationale, effort days, hitl_state, reviewed_by, reviewer_notes.
- **RICEFW item:** engagement_id, req_id (optional), type (R|I|C|E|F|W), name, description, status, complexity, priority.
- **Agent role:** role_id, name (e.g. A_Process_Owner), mandate, focus_areas, behavior_rules, escalation_rules.
- **Platform issue:** engagement_id, problem_description, suggested_improvement, priority, status.
- **Audit event:** engagement_id, action, entity_type, entity_id, actor_id, actor_role, details.

---

## 3. User Interface (UI) Specification

### 3.1 Navigation & Layout

- **Header:** Logo “RAPID”, “SAP Implementation”, current engagement pill (when set), global search (when engagement set), nav links, user name, logout, “AI-Powered” badge.
- **Nav links:** Home, Setup (Clients, Engagements), Discover (Capture, Sources), Analyse (Requirements, Fit/Gap, RICEFW), Govern (HITL Review, Audit Trail, Patterns), Collaborate (Agent simulation, Platform backlog), **Agent Testers** (Agent Testers), System (health).
- **Engagement-scoped links:** When an engagement is loaded, RACI, HITL, Fit/Gap, Simulate, Platform backlog, and engagement detail links carry `engagement_id` in the URL.

### 3.2 Pages (Routes)

| Route | Purpose | Key UX elements |
|-------|--------|------------------|
| `/` | Home dashboard | “What would you like to do today?” prompt (Ctrl+Enter to submit); tiles: Choose/Create client, Choose/Create engagement; table of top 5 open engagements with Reqs · RICEFW · Gaps; most recent engagement link. |
| `/login` | Sign in | Username + password (mock); any input succeeds. |
| `/clients` | Clients & Engagements | **Two columns:** Create Client (left), Create Engagement (right). **Ask Eng Manager** at top of each column: paste company URL to auto pre-fill the form from website, or ask for help per field; when the agent summarizes a client record, use **Apply to form** to copy values into the form. Pre-fill from website (LLM fills name, industry, sub_industry, employees, locations, revenue, systems, countries, regulatory, strategy, goals, products, executives, competitors, sector_archetype, erp_maturity, complexity_drivers). Download Excel templates. Auto-save after create. Clients list; All Engagements table. |
| `/clients/[id]` | Client detail | Client info; list of engagements; link to engagement detail. |
| `/engagement` | Engagement dashboard | Load engagement by ID; quick links (RACI, Gap Analysis, RICEFW, Import/Export); stats (Total Requirements, Confirmed, Pending Sign-off, Analysed, With KPI) — **clickable** to filter requirements table; requirement filters (status, priority); sortable requirements table; HITL simulation; RICEFW tab (#ricefw); Process Mirror, KPI Summary, Seed synthetic. |
| `/engagement/[id]` | Engagement detail | **Workspace tab nav** (Overview, Client context, Completion, Benchmark, Business case, Audit, Requirements, Fit/Gap, RICEFW, HITL, Assets, Agent). **Client context** read-only panel (Client 360 slice when client_id set). Name, phase, status; client link (hyperlinked); Benchmark insights; Business case; Requirements list with Full Detail; action tiles; Audit trail. |
| `/engagement/import-export` | Import/Export | Engagement selector; Download Excel, Download template, Upload Excel. |
| `/capture` | Requirements capture | Engagement selector; tabs: Conversation, Single Requirement, Paste Transcript, Use Template; assets; link to “View process flow”. |
| `/flow` | Process flow | Engagement selector; Generate Flow; swimlane view of requirements; “Capture requirements” link. |
| `/fitgap` | Fit/Gap board | Engagement selector; Analyse All; summary pills; board by fit_type (columns); process view; review modal (approve + notes); “Gap Analysis” link. |
| `/gap-analysis` | Gap Analysis | Engagement ID, process description, LOB filter; Run Analysis; matched scope items; “RICEFW inventory” and “Fit/Gap board” links. |
| `/hitl` | HITL review | Engagement selector; columns by state (AI Draft, Needs SME Review, …); Advance / “Approve as SME” / Reject / Out of scope. |
| `/workflow/[reqId]` | BPMN workflow | Back to engagement; req_id + title; BPMN vs Table view; Extract from transcript; add/edit step drawer. |
| `/simulate` | Agent simulation | Engagement + agent role dropdowns; phase; message input; “Agent reply (draft)”. |
| `/platform-backlog` | Platform backlog | Engagement selector; list by priority; Add issue; Start/Resolve. |
| `/agent-testers` | Agent Testers | Lists agent roles; A_Engagement_Manager featured with manifesto (Discovery/Assessment EM); link to use on Create Client / Engagement. |
| `/patterns` | Pattern library | GET pattern-library; grouped by category. |
| `/system-health` | System health | Checks API, key, backend health, clients/engagements sample; links to key pages. |

### 3.3 Design System (Summary)

- **Background:** `#0f172a` (dark).
- **Tags:** Pain Point (red), Manual Step (orange), Secret Sauce (purple), Workaround (yellow), Hand-off (cyan).
- **Priority:** Must-Have (red), Should-Have (amber), Nice-to-Have (slate).
- **Status:** open (blue), in_progress (amber), analysed (emerald), closed (slate).
- **Fit/Gap:** fit_standard, fit_config, fit_extension, gap_ricefw, gap_companion, out_of_scope (distinct pill colours).
- **HITL states:** ai_draft, needs_sme_review, needs_architect_review, approved, out_of_scope.

### 3.4 Forms & Behaviour

- **Create Client:** Name (required), industry, sub_industry, employees, legal_entities, locations, revenue, systems, countries, regulatory, strategy fields, sector/benchmark fields (sector_archetype, erp_maturity, complexity_drivers). **Ask Eng Manager** at top: paste URL to auto pre-fill (many fields), or get questions/suggestions per field; **Apply to form** copies agent summary into the form. Pre-fill from URL fills as many fields as the LLM can extract or infer. After create, form retained and **auto-save** (debounced PATCH).
- **Create Engagement:** Client (required), name, description, phase, status, dates, project_manager, sponsor, risk_level, health. Submit disabled until client selected and at least one client exists. After create, **auto-save** (debounced PATCH).
- **Templates:** Downloadable Excel templates for Client, Engagement, Requirements (RTM), RICEFW; note to “Save to your Documents folder to fill and re-upload”.

---

## 4. Workflow Specification

### 4.1 Core User Journeys

1. **Setup**
   - Log in → Home.
   - Create client (Clients page, left column); optionally use “Pre-fill from website”.
   - Create engagement (right column); select the client.
   - Optionally download Excel templates; fill offline; use Import/Export to upload requirements.

2. **Requirements**
   - Load engagement on Engagement page or open engagement detail.
   - Capture: go to Capture, select engagement; use Conversation, Single Requirement, Transcript, or Template.
   - View requirements on Engagement dashboard; filter/sort; open Full Detail; go to BPMN workflow per requirement.
   - Import/Export: download template or Excel; upload Excel for bulk requirements.

3. **Fit/Gap**
   - On Engagement page: “Analyse All Open” or run fit-gap per requirement.
   - Open Fit/Gap board (or via nav); review by column (fit_type); use review modal to approve/reject and add notes.
   - “Generate from Gaps” on RICEFW tab creates RICEFW items from approved gap_ricefw assessments.

4. **HITL**
   - Open HITL page; select engagement.
   - Move items: Advance, “Approve as SME”, Reject, Out of scope.

5. **Agent & Backlog**
   - Simulate: select engagement and agent role (e.g. A_Process_Owner); send message; view draft reply.
   - Platform backlog: add issues; filter by priority; Start/Resolve.
   - Audit trail: on engagement detail, view recent actions and events.

6. **Business case & Reporting**
   - Engagement detail: Business case section (benchmark KPIs, TCO, benefits calculator).
   - Export: requirements Excel (with optional Fit-Gap sheet); RICEFW export; templates.

### 4.2 Engagement-Scoped Flow

- User selects or creates an engagement → it becomes “current” (header pill, sessionStorage).
- All subsequent actions (requirements, RICEFW, Fit/Gap, Simulate, Platform backlog, Capture, Flow) use that engagement.
- Switching engagement: load another on Engagement page or open another engagement detail; context updates.

### 4.3 Cross-Linking

- Engagement dashboard ↔ RACI, Gap Analysis, RICEFW (#ricefw), Import/Export.
- Gap Analysis page ↔ RICEFW inventory, Fit/Gap board.
- Fit/Gap page ↔ Gap Analysis.
- Capture ↔ Process flow (links both ways).
- Requirement detail ↔ Workflow (BPMN), HITL, Assets (Capture).

---

## 5. Specification for Third-Party Review (UX & Improvements)

This section is for the reviewer to use when giving feedback. Please consider the following areas and note **specific improvements** (with examples where possible).

### 5.1 Clarity & Information Architecture

- Is the **purpose of each page** clear on first visit (e.g. Home vs Clients vs Engagement vs Fit/Gap)?
- Is **engagement context** always obvious (e.g. “Working in: …” in header)? What would make it clearer?
- Are **section headers and labels** sufficient? Where would you add or rename sections?
- Is the **relationship between Client → Engagement → Requirements → RICEFW → Fit/Gap** clear to a new user? What’s missing?

### 5.2 Navigation & Wayfinding

- Can users **get to the next logical step** without guessing (e.g. after creating a client, is “create engagement” obvious)?
- Are **back/cancel** and “Create another” flows clear?
- Is the **main nav** (Home, Clients, Engagements, Capture, Fit/Gap, Simulate, Platform backlog, Patterns, System) the right set and order? What would you add/remove/rename?
- Are **quick links** (RACI, Gap Analysis, RICEFW, Import/Export) in the right place and labelled well?

### 5.3 Forms & Data Entry

- **Create Client / Create Engagement** side by side: does this layout work? Is “client must be set up first” clear and enforced enough?
- **Auto-save** after create: is the behaviour (and “Changes auto-save” message) clear? Any risk of confusion or data loss?
- **Excel templates**: is the “Download templates” block easy to find? Is the guidance “Save to your Documents folder” sufficient?
- Where would you add **validation messages**, **defaults**, or **progressive disclosure** (e.g. optional sections collapsed)?

### 5.4 Tables, Filters & Lists

- **Requirements table** (Engagement dashboard): are filter/sort and “X of Y” clear? Are clickable stat cards (Total, Confirmed, Analysed, etc.) discoverable and useful?
- **Clients and Engagements** lists: are filter/sort and the transition to detail/create clear?
- **Fit/Gap board**: is the column-based view (by fit_type) usable? Is the review modal (approve, notes) clear?
- **HITL columns**: is the flow (Advance, Approve as SME, Reject) obvious?

### 5.5 Feedback, Errors & Loading

- Are **success messages** (e.g. “Client saved”, “Engagement created”) visible and dismissible enough?
- Are **errors** (e.g. API failures, validation) shown in plain language and with a suggested next step?
- Where do you notice **missing loading states** or **abrupt transitions**?

### 5.6 Accessibility & Usability

- **Keyboard:** Is Ctrl/Cmd+Enter for “What would you like to do today?” sufficient? Where else should Enter or Escape do something?
- **Labels:** Are all inputs and actions associated with visible labels (for screen readers and clarity)?
- **Colour:** Does the dark theme work for you? Are status/priority colours distinguishable?

### 5.7 Gaps & Missing Flows

- What **critical user goals** are hard or impossible with the current UI?
- What **reports or exports** are missing (e.g. audit report, HITL summary)?
- Is **onboarding** (first-time user) supported enough? What would you add?

### 5.8 Performance & Responsiveness

- Where did the app feel **slow** (e.g. loading engagement, Fit/Gap board, flow)?
- Is **mobile/tablet** use a requirement? If yes, what breaks or feels wrong?

---

## 6. How to Submit Feedback

Please provide feedback in whatever format is convenient (e.g. bullet list, table, or short narrative). For each point, if possible include:

- **Area** (e.g. Navigation, Create Client, Fit/Gap board).
- **Current behaviour or issue.**
- **Suggested improvement.**
- **Priority** (e.g. Must-have / Nice-to-have).

Example:

| Area        | Issue                                      | Suggestion                                      | Priority   |
|------------|---------------------------------------------|-------------------------------------------------|------------|
| Engagement | “Working in” pill is easy to miss           | Add engagement name to page title or breadcrumb | Nice-to-have |
| Create Client | No hint that website pre-fill exists   | Short inline tip above the form                 | Must-have  |

### Implemented (from review feedback)

- **Document title:** Browser tab title includes current engagement (e.g. "Client · ENG-001 · Phoenix Discovery – RAPID") when an engagement is set, improving wayfinding.
- **Change engagement:** Requirements and Fit/Gap pages show "Working in this engagement. Change engagement" in the main content with a link to the engagement list.
- **Create Client pre-fill hint:** Short tip above the Create Client form: "Paste a company website URL in Ask Eng Manager or in the Pre-fill from company website box below to auto-fill many fields."
- **HITL report:** GET /v1/engagement/{id}/hitl-report returns Excel; the HITL page has a "Download HITL report (Excel)" button.
- **Client context (engagement workspace):** On engagement detail (`/engagement/[id]`), a read-only "Client context" section shows a Client 360 slice (name, industry, sector, employees, legal entities, countries, current systems, regulatory, strategy/value proposition, ERP maturity) with link to full client. Fetched when engagement has a client_id.
- **Hyperlinked IDs:** Engagement ID is clickable (EngagementLabel links to `/engagement/[id]`). Client ID is clickable via ClientIdLink (engagement detail and client detail). Requirement IDs remain linked via ReqIdLink to workflow.
- **Engagement workspace tabs:** Sticky tab bar on engagement detail: Overview, Client context, Completion, Benchmark, Business case, Audit, Requirements (scroll to section); Fit/Gap, RICEFW, HITL, Assets, Agent (links to respective pages with engagement_id). Section IDs and scroll-margin for smooth jump.

---

## 7. Document Info

- **Version:** 1.2 (standalone review spec; added Client context, hyperlinked IDs, engagement workspace tab nav).
- **Generated for:** Third-party review and UX improvement feedback.
- **Not part of:** In-repo system design or architecture docs; for external use only.
- **Live system:** Frontend https://rapid-ui-wine.vercel.app — Backend https://rapid-mvp-production.up.railway.app
