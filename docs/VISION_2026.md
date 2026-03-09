# RAPID — Next-Generation Design Document
**Version:** 2026-03 | **Author:** Architecture Session | **Horizon:** 90 days

---

## PREFACE: WHAT THIS DOCUMENT IS

This is a product redesign brief grounded in what RAPID actually is today — not a greenfield vision. 
Every recommendation maps to real pages, real endpoints, and real constraints (solopreneur, Railway + Vercel + Supabase, no external funding).

The core thesis: **RAPID is currently a collection of tools. It needs to become a workflow.** 
A workflow that drives itself, surfaces decisions, and produces deliverables — not just captures data.

---

## A. REVISED INFORMATION ARCHITECTURE

### A1. The Problem With Today's IA

Current sidebar: `SETUP / DISCOVER / ANALYSE / GOVERN / COLLABORATE / SYSTEM`

This is a phase-based taxonomy, which sounds logical but fails in practice because:
- Consultants don't work linearly. They're in "Analyse" and "Discover" simultaneously.
- The sidebar offers 20+ destinations with no hierarchy of importance.
- A consultant logging in at 9am before a steering committee has no immediate signal: *what needs my attention right now?*
- A client has no entry point at all.

### A2. New Navigation Model

**Three-layer structure:**

```
LAYER 1: FOCUS (what needs you NOW)
├── Command Center           ← replaces /page.tsx home
├── Pending Decisions        ← replaces /hitl (renamed, reframed)
└── Open Sign-Offs           ← new; pulls from fit-gap assessments awaiting client review

LAYER 2: ENGAGEMENT WORKSPACE (engagement-scoped work)
├── Overview                 ← replaces /engagement/[id] (enhanced)
├── Deliverables             ← NEW: Blueprint %, RICEFW %, Test Scripts %, Go-Live Checklist %
├── Requirements             ← /requirements (enhanced)
├── Fit/Gap Board            ← /fitgap (enhanced)  
├── RICEFW Registry          ← current RICEFW section of engagement
├── Process Flows            ← /flow + /workflow/[reqId]
└── Sources                  ← /sources

LAYER 3: PLATFORM (cross-engagement)
├── Portfolio                ← NEW: all engagements at a glance
├── Pattern Library          ← /patterns (enhanced)
├── Client Portal            ← NEW: external-facing view
└── Settings / Admin         ← /user-management, /system-health
```

**Routing convention change:**
- All engagement-scoped pages become `/e/[engagementId]/[module]`
- This enables the engagement context to live in the URL permanently, eliminating the current dropdown-per-page UX tax
- Current: `/fitgap?engagement_id=xxx` → New: `/e/xxx/fitgap`

### A3. Role-Based Views

| Role | What They See | What They Can Do |
|------|--------------|-----------------|
| **Lead Consultant** | Everything. All agents, all raw data, all costs | Full CRUD, agent controls, approve/reject HITL |
| **Functional Consultant** | Their assigned modules only | Capture, HITL for their scope, RICEFW edit |
| **Client Executive** | Client Portal only — no jargon, no costs | Approve sign-offs, view milestones, ask questions |
| **Client Project Manager** | Client Portal + read-only fit/gap in plain English | Track progress, escalate blockers |
| **Platform Admin** | System health, all engagements, billing | User mgmt, pattern library admin |

Role is set at `users` table level. Client users get a separate subdomain: `client.rapid-ui.vercel.app/[clientSlug]`.

---

## B. SCREEN-BY-SCREEN UX REDESIGN

### B1. COMMAND CENTER (replaces `/page.tsx`)

**What it is:** The consultant's morning briefing. Not a dashboard — a triage surface.

**What it shows today vs. what it should show:**

Today: Summary pills + "Next Actions" (generic) + recent engagements table.

New design — two-column layout:
```
LEFT (60%): TODAY'S ACTIONS — agent-generated, ranked by urgency
┌─────────────────────────────────────────────────────┐
│ 🔴 URGENT (3)                                        │
│   • Acme Corp: 4 fit-gap assessments awaiting        │
│     consultant review [gap_type: Custom Dev] →       │
│   • RetailCo: Steering committee in 2 days.          │
│     Blueprint is 34% complete. [Generate draft] →   │
│   • GlobalMfg: HITL queue has 8 items stale >48h →  │
│                                                      │
│ 🟡 THIS WEEK (5)                                     │
│   • Acme Corp: RICEFW estimate missing on 12 items → │
│   • RetailCo: Client hasn't signed off Sprint 2 →   │
│   • ...                                              │
│                                                      │
│ 🟢 AGENT WORKING (automated, no action needed)       │
│   • GlobalMfg: Running fit-gap-analyse-all... (61%)  │
│   • Acme Corp: Generating RICEFW from 3 new gaps...  │
└─────────────────────────────────────────────────────┘

RIGHT (40%): PORTFOLIO HEALTH
┌──────────────────────────────┐
│ ACME CORP    [Go-Live: 94d]  │
│ Blueprint ████░░ 68%         │
│ RICEFW    ██░░░░ 31%         │
│ Sign-offs ████░░ 72% ✓       │
│                              │
│ RETAILCO     [Go-Live: 134d] │
│ Blueprint ██░░░░ 34%  ⚠️     │
│ RICEFW    █░░░░░ 12%         │
│ Sign-offs █░░░░░ 18%  🔴     │
│                              │
│ [+ New Engagement]           │
└──────────────────────────────┘
```

**What the agent does automatically:**
- Scans all engagements every 4h: HITL queue age, sign-off staleness, go-live proximity
- Scores urgency and writes to a `command_center_alerts` table
- Surfaces "Generate draft" CTAs when deliverables are near a threshold (Blueprint > 60% data complete → offer to generate)

**What the human decides:** Priority order, which alerts to act on, dismissals.

**Next-step CTA:** Every alert card has one action button. No menus.

---

### B2. ENGAGEMENT OVERVIEW (replaces `/engagement/[id]`)

**Current state:** Tabs for phases, completion checklist, client context, audit trail, seed button.

**New design:** Mission control for a single engagement.

```
HEADER BAR:
[Acme Corp — SAP S/4HANA] [Go-Live: Oct 15] [Phase: Explore & Realize] [Health: ⚠️ At Risk]

DELIVERABLE PROGRESS (always visible, not hidden in tab):
Blueprint    ████████░░ 78%   [Open] [Generate Section]
RICEFW Inv.  █████░░░░░ 52%   [Open] [Auto-Fill Estimates]  
Test Scripts ██░░░░░░░░ 19%   [Open] [Generate from RICEFW]
Go-Live CL   █░░░░░░░░░  8%   [Open] [Start Checklist]

TABS: Overview | Requirements (47) | Fit/Gap (47) | RICEFW (23) | Flows | Sources | Audit
```

**The deliverable progress bars** are the single most important new element. They answer the question both shoes care about: *"where are we?"* without clicking into five different pages.

Progress calculation (backend):
- Blueprint %: (reqs with approved fit-gap / total reqs) × 0.6 + (RICEFW items with description / total) × 0.4
- RICEFW %: items with effort estimate + assigned owner / total items
- Test Scripts %: items with at least one test case generated / RICEFW count
- Go-Live CL %: checklist items marked complete / total

**Agent actions on this screen:**
- "Generate Section" → calls the Blueprint Draft Agent (new, see D3) with the engagement's approved fit-gap data
- "Auto-Fill Estimates" → RICEFW Estimator Agent suggests effort days based on fit_type and pattern library
- "Generate from RICEFW" → Test Script Agent creates Gherkin-style test cases per RICEFW item

**Next-step CTA:** Dynamically chosen by agent based on what's blocking progress. If Blueprint is at 78% but 6 reqs have no fit-gap review → "Review 6 gaps to unlock Blueprint completion."

---

### B3. FIT/GAP BOARD (replaces `/fitgap`)

**Current state:** Sticky summary bar, Analyse All, board grouped by fit_type, review modal.

This page is actually well-structured. The changes are additive:

**Add to existing:**

1. **Effort Impact Column** — for each "Gap" or "Custom Development" item, show the RICEFW item if it exists, or a button "→ Create RICEFW". This closes the loop from gap → build item.

2. **Client Translation Layer** — toggle in the header: `[Consultant View] / [Client View]`. 
   - Consultant: current view
   - Client: plain-English cards. "Gap" becomes "SAP doesn't cover this process out of the box." "Custom Dev" becomes "We'll need to build this specifically for you (adds cost + risk)."

3. **Batch Sign-Off Request** — select multiple "Fit" items → "Request Client Sign-Off" sends them to the client portal as a bundle, not one at a time.

4. **Agent Insight Banner** — per item, agent flags: "⚠️ Pattern match: RetailCo 2024 had same gap. Resolution: Used SAP BTP extension, effort 8 days." Pulls from pattern library.

**Next-step CTA:** After reviewing last item → "All gaps reviewed. Ready to generate RICEFW for 7 custom development items?" [Generate RICEFW]

---

### B4. REQUIREMENTS (replaces `/requirements`)

**Current state:** Good — filters, drawer, pagination, HITL/fit_type/source columns.

**Changes:**

1. **Source Traceability Column** — show source excerpt snippet inline (not just source_id). Hovering shows the raw excerpt.

2. **Completeness Score** — per requirement: a small score badge (0–100) calculated from: has description + has process step + has fit-gap + has sign-off + has source. Consultants know at a glance which reqs are half-baked.

3. **Requirement Health Heatmap** — above the table, a small visual matrix: rows = process areas, columns = completeness stages. Red cells = gaps in coverage. Tells you where you haven't workshopped yet.

4. **Bulk Actions** — checkbox select → "Run Fit-Gap on Selected" | "Export Selected" | "Request Sign-Off on Selected"

**Next-step CTA:** "12 requirements have no fit-gap assessment. [Analyse All] or [Select and Analyse]"

---

### B5. HITL QUEUE → "PENDING DECISIONS" (replaces `/hitl`)

**The rename matters.** "HITL" is engineer speak. Consultants don't use it.

**Current state:** Queue table, advance/reject, download Excel report.

**New framing:** This is the consultant's judgment queue. Every item here exists because an agent hit its confidence limit and needs a human call.

**New design:**

```
PENDING DECISIONS                              [8 items] [Download Report]

FILTER: [All Engagements ▼] [All Types ▼] [Oldest First ▼]

┌─────────────────────────────────────────────────────────────────────────┐
│ REQ-034  Acme Corp  |  FIT TYPE UNCERTAIN                    [2 days]   │
│ "Vendor invoice approval workflow with 3-level hierarchy"               │
│                                                                         │
│ Agent says: "Could be Fit (J60 AP) or Gap (custom approval matrix).     │
│ Confidence: 61%. Recommend reviewing vendor payment terms in source."   │
│                                                                         │
│ Source excerpt: "...Finance Director approval required above $50k..."   │
│                                                                         │
│ [✓ Mark as Fit — J60]  [✗ Mark as Gap]  [📝 Reclassify]  [Skip →]     │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key change:** Show the agent's reasoning and confidence score. Today, the consultant has to re-read the requirement cold. The new design shows *why the agent stopped* and *what it suggests* — the consultant just validates, they don't re-derive.

**Next-step CTA:** After clearing queue → "Queue empty. 3 new gaps were confirmed — [Generate RICEFW for them]?"

---

### B6. RICEFW REGISTRY (enhances current RICEFW section)

**Current state:** Table with list/add/edit/delete/export Excel. Good foundation.

**Missing entirely:**
- Effort estimates (person-days)
- Priority (linked to go-live risk)
- Owner assignment
- Status (Not Started / In Progress / Dev Complete / Tested / Go-Live Ready)
- Dependency mapping between RICEFW items

**New columns to add to the table:**
`ID | Type | Name | Linked Req | Effort (days) | Owner | Status | Priority | Dependencies | Last Updated`

**Agent action — RICEFW Estimator:**
- On "Auto-Fill Estimates" (from Engagement Overview), agent reads each RICEFW item's description + fit_type + linked requirement
- Compares to pattern library for similar items from past engagements
- Suggests: effort days (low/high range), complexity (Simple/Medium/Complex), recommended SAP standard alternative if one exists
- Human reviews suggestions in a batch modal and approves/adjusts

**Next-step CTA:** "RICEFW registry complete. Ready to generate Test Scripts?" [Generate Test Scripts]

---

### B7. SOURCE CAPTURE (enhances `/sources` and `/capture`)

**Current issue:** `/sources` and `/capture` are two separate pages doing related things. Sources = documents; Capture = requirements entry. The flow should be: ingest source → extract requirements → requirements go to HITL for review.

**Unified Capture Flow (new `/e/[id]/capture`):**
```
Step 1: INGEST
  [Paste text] [Upload file (PDF/DOCX/XLSX)] [Paste transcript] [Use template]
  ↓
Step 2: AGENT EXTRACTION (runs automatically)
  "Extracting requirements from uploaded document... found 23 candidates"
  ↓  
Step 3: HUMAN REVIEW
  Side-by-side: source excerpt | extracted requirement
  [Accept] [Edit] [Reject] per requirement
  ↓
Step 4: CONFIRM → requirements enter the main list
```

This collapses 3 current pages (`/sources`, `/capture` tabs, `/requirements`) into one directed flow.

---

## C. NEW FEATURES TO BUILD — PRIORITIZED BY EFFORT vs. IMPACT

### TIER 1: HIGH IMPACT, LOW EFFORT (build in weeks 1–3)

#### C1. Deliverable Progress Engine
**What it is:** A backend endpoint `GET /engagement/{id}/deliverable-progress` that returns % complete for Blueprint, RICEFW, Test Scripts, Go-Live Checklist.

**Agent does:** Calculates based on existing data (requirements, fit_gap_assessments, ricefw_inventory, HITL states). No new AI calls needed — pure database aggregation.

**Human does:** Nothing. It auto-updates as work progresses.

**Deliverable:** Drives the progress bars on Engagement Overview + Portfolio view.

**Effort:** 1 day backend + 2 days frontend. **Impact:** Immediately answers the #1 question from both shoes.

---

#### C2. Command Center Alerts Engine
**What it is:** Background job (or on-demand endpoint) that scans engagements and generates prioritized action items.

**Agent does:** Queries HITL queue age, sign-off staleness, go-live date proximity, deliverable % vs. time remaining. Outputs structured alerts with urgency score + suggested action.

**Human does:** Dismisses, acts on, or delegates alerts.

**Deliverable:** `GET /command-center/alerts` → feeds the new home screen.

**Effort:** 2 days backend + 1 day frontend. **Impact:** Transforms the home from passive to active.

---

#### C3. URL-Based Engagement Context
**What it is:** Move all engagement-scoped pages to `/e/[engagementId]/[module]` routing.

**Agent does:** Nothing. Pure frontend refactor.

**Human does:** Normal navigation — but now engagement context persists across pages without re-selecting dropdowns.

**Effort:** 2 days frontend refactor. **Impact:** Eliminates the #1 UX friction on every page.

---

#### C4. HITL Queue — Agent Reasoning Display
**What it is:** Store agent confidence score + reasoning text in `hitl_events` table. Display in the HITL/Pending Decisions UI.

**Agent does:** On gap analysis, writes `confidence_score` (0–100) and `reasoning` (1–2 sentences) to the HITL event.

**Human does:** Reads agent reasoning before deciding. Faster, more accurate decisions.

**Effort:** 1 day backend (add fields to gap analysis prompt + save), 1 day frontend. **Impact:** Cuts consultant review time per item by ~60%.

---

#### C5. Batch Sign-Off Requests
**What it is:** Select multiple fit-gap items + send to client as a sign-off bundle with one email/portal notification.

**Agent does:** Groups items by process area, generates a plain-English summary of each fit decision for client consumption.

**Human does:** Selects items, reviews the agent-generated summary, sends.

**Deliverable:** A sign-off record in the DB; client sees it in the portal (see Section E).

**Effort:** 1 day backend + 2 days frontend. **Impact:** Eliminates email chains for sign-off.

---

### TIER 2: HIGH IMPACT, MEDIUM EFFORT (weeks 4–8)

#### C6. Blueprint Draft Generator
**What it is:** Takes all approved requirements + fit-gap assessments for an engagement and generates a structured Blueprint document (Word/PDF).

**Structure of Blueprint output:**
```
1. Executive Summary
2. Scope Overview (process areas covered)
3. Fit Analysis Summary (X Fit, Y Gap, Z Custom)
4. Process-by-Process Detail (one section per L1 process area)
   - Current state (from requirements/sources)
   - Future state (SAP standard process)
   - Gaps and decisions
5. RICEFW Summary Table
6. Open Items / Risks
```

**Agent does:** Generates sections 1–6 from engagement data. Uses Sonnet for narrative sections.

**Human does:** Reviews, edits narrative, approves.

**Deliverable:** Actual Blueprint document. This is a $50,000 consulting artifact delivered in minutes.

**Effort:** 3 days backend (generation prompt + DOCX output via python-docx) + 2 days frontend (preview + download). **Impact:** ⭐ This is RAPID's flagship differentiator.

---

#### C7. RICEFW Effort Estimator Agent
**What it is:** For each RICEFW item, agent suggests person-days based on type (Report/Interface/Conversion/Enhancement/Form/Workflow), complexity, and historical patterns.

**Agent does:** Reads RICEFW item description + fit_type + linked req. Checks pattern library for similar items. Returns: low estimate, high estimate, rationale, similar past items.

**Human does:** Accepts or adjusts estimates. This becomes the basis for the project budget.

**Deliverable:** Completed RICEFW inventory with effort estimates → feeds a simple budget model.

**Effort:** 2 days backend + 2 days frontend. **Impact:** Justifies consultant fees; gives client cost visibility.

---

#### C8. Test Script Generator
**What it is:** From each RICEFW item, generate structured test cases (happy path + key exception paths).

**Format:**
```
Test Case ID: TC-001
RICEFW: WRICEF-007 (Custom Approval Workflow)
Test Objective: Verify 3-level approval triggers correctly
Preconditions: Invoice > $50k created in system
Steps:
  1. Create vendor invoice for $52,000
  2. Submit for approval
  3. Verify L1 approver notified
  4. L1 approves → verify L2 notified
  5. ...
Expected Result: Invoice posted after L3 approval
```

**Agent does:** Generates test cases from RICEFW description + linked requirement. 

**Human does:** Reviews, marks as ready for UAT.

**Effort:** 2 days backend + 2 days frontend. **Impact:** Test preparation is a huge consultant time sink. This automates it.

---

#### C9. Engagement Memory & Pattern Auto-Suggest
**What it is:** When starting a new engagement in the same industry, RAPID pre-suggests requirements based on what similar past engagements looked like.

**Agent does:** On engagement creation (same industry selected), queries pattern_library and past requirements. Suggests a starter pack: "Based on 3 past Retail engagements, here are 28 common requirements. Accept all / Review one by one."

**Human does:** Accepts/rejects suggestions; they enter as draft requirements.

**Effort:** 2 days backend (similarity query + suggestion prompt) + 2 days frontend. **Impact:** Cuts discovery time by 40% on repeat-industry engagements.

---

### TIER 3: GAME-CHANGING, HIGHER EFFORT (weeks 8–12)

#### C10. Client Portal (full design in Section E)

#### C11. Milestone Timeline View
**What it is:** A visual project timeline showing phases, milestones, and go-live date. Client-facing version is the killer feature.

**Agent does:** On engagement creation, generates a draft timeline based on scope + industry norms (SAP Activate phases). Updates milestone completion as deliverables progress.

**Effort:** 4 days frontend (timeline component) + 2 days backend. **Impact:** Directly answers client question: "Are we on track?"

---

#### C12. Steering Committee Report Generator
**What it is:** One-click report for steering committee: RAG status, decisions made since last meeting, decisions pending, risks, next steps.

**Agent does:** Reads engagement data since last report date, generates executive-level narrative. No jargon.

**Human does:** Edits, approves, sends or presents.

**Deliverable:** A PDF/slide deck that takes 2 hours to build manually. Generated in 30 seconds.

**Effort:** 3 days backend + 2 days frontend. **Impact:** Directly solves "scrambling before steering committee."

---

## D. AGENT UPGRADE PLAN

### D1. Current Agent Inventory (what exists)

| Agent | Current Capability | Problem |
|-------|--------------------|---------|
| Gap Analysis Agent | Maps req → SAP scope item | No confidence score, no reasoning shown to human |
| Archaeologist Agent | Extracts reqs from transcript | Good. Needs to also extract from uploaded files |
| RICEFW Generator | Creates RICEFW from confirmed gaps | No effort estimates, no pattern matching |
| Benchmark/KPI Agent | Industry benchmarks | Isolated, not surfaced proactively |
| Ask RAPID | Context-sensitive Q&A on engagement | Good start. Needs memory of past answers. |
| Simulation/Seed Agent | Seeds test requirements | Good for demos. Not a production agent. |

### D2. Agent Enhancements (upgrade existing)

**Gap Analysis Agent → "Fit Assessment Agent"**
- Add: `confidence_score` (0–100) output field
- Add: `reasoning` (1–2 sentences) explaining the classification
- Add: `alternative_scope_items` (list of 2-3 close matches considered)
- Add: `pattern_match` — check pattern library before calling LLM; if confidence > 85% match, skip LLM call (saves cost)
- Trigger: runs automatically after requirement creation if confidence not yet set

**Archaeologist Agent → "Source Intelligence Agent"**  
- Add: PDF/DOCX ingestion via `python-docx` / `pdfplumber`
- Add: Confidence score per extracted requirement
- Add: Automatic duplicate detection against existing requirements
- Add: Process area auto-classification

**RICEFW Generator → "RICEFW Estimator Agent"**
- Add: Effort estimate (low/high range, person-days)
- Add: Complexity classification (Simple/Medium/Complex/Very Complex)
- Add: SAP BTP/standard alternative check — "Before building custom, check if SAP standard X covers this"
- Add: Pattern library match — if similar RICEFW from past project, surface estimate

### D3. New Agents to Build

**Blueprint Draft Agent** (highest priority)
- Trigger: Manual ("Generate Blueprint") or when Blueprint % crosses 70%
- Input: All approved requirements + fit-gap for the engagement
- Output: Structured Blueprint in sections (see C6)
- Model: Sonnet (quality over cost here — this is client-facing)
- Human gate: Review + approve each section before final export

**Test Script Agent**
- Trigger: After RICEFW item marked "Dev Complete"
- Input: RICEFW description + linked requirement + process steps
- Output: Structured test cases (see C8 format)
- Model: Haiku (structured, templated output)
- Human gate: Review and mark "Ready for UAT"

**Go-Live Checklist Agent**
- Trigger: When Test Scripts reach 80% complete
- Input: Engagement data + RICEFW inventory + standard SAP go-live checklist template
- Output: Customized go-live checklist with ownership and due dates
- Model: Haiku (template-driven)
- Human gate: Review and assign owners

**Steering Committee Agent**
- Trigger: Manual ("Generate SteerCo Report") or weekly automated
- Input: Engagement data + last report date
- Output: Executive summary with RAG status, decisions, risks, next steps
- Model: Sonnet
- Human gate: Review and approve before sending

**Memory/Pattern Agent** (runs in background)
- Trigger: When engagement marked complete
- Input: All engagement data
- Output: Writes N new patterns to pattern_library (successful RICEFW resolutions, fit decisions, estimation accuracy)
- Model: Sonnet (reflection task)
- Human gate: None — writes draft patterns; human curates library periodically

### D4. Agent Chain: Autonomous Implementation Workflow

```
[Source Uploaded]
      ↓
Source Intelligence Agent → extracts requirements (confidence scored)
      ↓ (high confidence auto-approved, low confidence → Pending Decisions queue)
[Requirements in DB]
      ↓
Fit Assessment Agent → classifies each req vs 244 SAP scope items
      ↓ (confidence > 80% auto-sets; < 80% → Pending Decisions queue)
[Fit/Gap Board Populated]
      ↓  (on human approval of gaps)
RICEFW Estimator Agent → creates RICEFW items with effort estimates
      ↓
Blueprint Draft Agent → (when threshold reached) generates Blueprint sections
      ↓  (on human approval)
Test Script Agent → generates test cases per RICEFW item
      ↓
Go-Live Checklist Agent → generates checklist
      ↓
Steering Committee Agent → generates SteerCo report on cadence
      ↓
Memory/Pattern Agent → at close, writes to pattern library
```

Human intervention points: Pending Decisions queue, Blueprint review, Sign-Off requests, SteerCo report approval.

Everything else is autonomous.

---

## E. CLIENT PORTAL DESIGN

### E1. The Portal Philosophy

The client portal is not a stripped-down version of the consultant tool. It is a completely different product that *happens to read from the same data*.

The consultant tool is for *doing the work*. The client portal is for *feeling in control of the project*.

Every screen answers one of four questions:
1. Are we on track?
2. What do I need to decide?
3. What did we agree on?
4. What's coming next?

### E2. Access Model

- Client users are created by the Lead Consultant in `/user-management`
- They receive an email with a magic link (no password to manage)
- URL: `rapid-ui-wine.vercel.app/portal/[clientSlug]` (or custom domain eventually)
- Client sees ONLY their own engagement. No awareness of other clients.

### E3. Client Portal Screens

**PORTAL HOME**
```
Good morning, Sarah.

YOUR PROJECT: SAP S/4HANA for Acme Corp
Go-Live: October 15, 2026  (94 days)

Project Health: 🟡 On Track with Risks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 NEEDS YOUR ATTENTION (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Sign off on 8 process decisions from Sprint 2 Workshop
   [Review & Sign Off →]

2. Decision required: SAP standard vs. custom invoice approval
   Your current process needs a workaround. We need your call.
   [See details →]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 PROJECT PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Discovery Complete      ████████████ 100% ✓
Blueprint               ████████░░░░  68%
Build & Test            ░░░░░░░░░░░░   0%
Go-Live Prep            ░░░░░░░░░░░░   0%
```

No jargon. No "RICEFW." No "HITL." No "scope items."

---

**SIGN-OFF CENTER (client's most used screen)**

When consultant sends a batch sign-off request, client sees:

```
DECISIONS FROM SPRINT 2 WORKSHOP
8 items for your review

How this works: Your consultant team has mapped your current processes to SAP.
Where SAP covers it well, it's marked ✓ Fit. Where there's a gap, we need 
your decision on how to handle it.

┌─────────────────────────────────────────────────────────────────────┐
│ 3 of 8 ✓                                            [Sign Off All] │
├─────────────────────────────────────────────────────────────────────┤
│ ✅ Your Purchase Order Process                                       │
│ SAP handles this out of the box. No changes needed.                 │
│ [✓ Approved]                                                        │
├─────────────────────────────────────────────────────────────────────┤
│ ⚠️  Your Invoice Approval Workflow                                   │
│ SAP's standard approval has 2 levels. You use 3 levels. We need     │
│ to build a small customization (est. 5–8 days of development).      │
│ Alternatively, we can simplify your process to 2 levels — saving    │
│ time and money.                                                      │
│                                                                     │
│ Your call:  [Accept customization]  [Simplify the process]          │
│             [Ask a question]        [Escalate to John (consultant)] │
└─────────────────────────────────────────────────────────────────────┘
```

**Every "Ask a question" creates a threaded comment on that requirement, visible to the consultant.** No emails. Everything tracked in RAPID.

---

**MILESTONE TIMELINE (mobile-first)**

```
ACME CORP — SAP GO-LIVE TIMELINE

MAR 2026  ●────────────────── Discovery & Prepare ✓
APR 2026          ●────────── Explore Workshops ← YOU ARE HERE
JUN 2026                   ●─ Blueprint Sign-Off
AUG 2026                       ●── Build & Configure
SEP 2026                            ●── User Acceptance Testing
OCT 2026                                 ●── Go-Live 🚀
```

Tapping any milestone shows: what's included, what's complete, what's pending.

---

**DECISIONS MADE (audit for the client)**

Client-facing view of all approved sign-offs, with dates and who approved.

"On April 3rd, you approved: SAP standard Purchase Order process."

This answers: "I approved 12 things last sprint — what happened to them?"

Shows: Decision made → what it means for the project → current status.

---

### E4. Mobile-First Considerations

Client portal is built mobile-first. 70% of client interaction happens on phone between meetings.

- Touch-optimized: sign-off cards are swipeable (right = approve, left = question)
- Notification: consultant can send "nudge" via portal → client gets email with deep link to specific decision
- No tables. Cards only. No horizontal scroll.
- Progress rings instead of progress bars (more scannable on small screen)

Consultant tool can be desktop-focused. Client portal is mobile-native.

---

## F. IMPLEMENTATION ROADMAP

### F1. What Exists That You Can Build On Immediately

Existing stack is sound. No new infrastructure needed for 90% of this vision:
- FastAPI on Railway → add new endpoints, background jobs via `asyncio`
- Supabase → add new columns and tables as needed (already doing this via /admin/migrate)
- Next.js on Vercel → new pages and refactored routing
- Anthropic API via `providers.py` → already handles Haiku + Sonnet selection

### F2. What Needs New Infrastructure (defer unless revenue justifies)

| Capability | Requires | When to add |
|------------|---------|-------------|
| Background job processing | APScheduler in Railway OR a free-tier worker | Week 4: needed for Command Center alerts |
| File upload (PDF/DOCX) | Supabase Storage (already configured) + `pdfplumber`, `python-docx` | Week 3: Source Intelligence Agent |
| DOCX export (Blueprint) | `python-docx` pip package | Week 5 |
| Client portal auth | Supabase Auth magic links (already in Supabase) | Week 8 |
| Real-time updates | Supabase Realtime OR polling | Week 10: agent progress bars |

### F3. The 90-Day Sprint Plan

**SPRINT 1 (Days 1–7): Make Existing Data Work Harder**

These are zero-new-feature changes with high visible impact:

1. Add `confidence_score` + `reasoning` to gap analysis output and HITL events table
2. Build `GET /engagement/{id}/deliverable-progress` endpoint (pure aggregation)
3. Add effort + status + owner columns to `ricefw_inventory` table
4. Fix navigation: implement `/e/[engagementId]/[module]` routing in Next.js

Outcome: Command Center can show real data. HITL queue shows reasoning. Progress bars have numbers.

---

**SPRINT 2 (Days 8–21): Command Center + Pending Decisions**

5. Build `GET /command-center/alerts` backend (scan all engagements, return prioritized actions)
6. Redesign home page as Command Center (two-column: alerts + portfolio health)
7. Redesign `/hitl` as "Pending Decisions" with agent reasoning display
8. Build pattern library auto-suggest: on gap analysis, check pattern library first
9. Add process area completeness heatmap to `/requirements`

Outcome: Consultants start every day in RAPID. HITL queue is faster to process.

---

**SPRINT 3 (Days 22–35): Unified Capture + RICEFW Estimator**

10. Unify `/sources` + `/capture` into `/e/[id]/capture` with 4-step flow
11. Add PDF/DOCX upload via `pdfplumber` + `python-docx` to Source Intelligence Agent
12. Build RICEFW Estimator Agent: effort estimate per item + batch review UI
13. Add batch sign-off request: select fit-gap items → generate plain-English bundle → mark as "sent to client"

Outcome: Document ingestion is production-quality. RICEFW registry has real estimates. Sign-off workflow doesn't need email.

---

**SPRINT 4 (Days 36–56): Blueprint Generator + Deliverable Engine**

14. Build Blueprint Draft Agent (the big one): structured prompt → section-by-section generation → DOCX export
15. Build Blueprint review UI: side-by-side source data | generated text, section-by-section approval
16. Build Milestone Timeline view (read-only for now): phases + go-live date
17. Build Test Script Agent: per-RICEFW test case generation
18. Wire all deliverable progress bars on Engagement Overview

Outcome: RAPID produces its first actual deliverable. This is the demo you show to prospects.

---

**SPRINT 5 (Days 57–75): Client Portal MVP**

19. Supabase Auth magic links for client users
20. Build `/portal/[clientSlug]` portal home with project health + action items
21. Build Sign-Off Center (client-facing): card-based approval UI
22. Build Decisions Made history view (client audit)
23. Build Milestone Timeline for client (simplified)
24. Consultant sends sign-off bundle → client receives email with portal link

Outcome: First client can use RAPID without a consultant explaining anything. This is the pricing unlock.

---

**SPRINT 6 (Days 76–90): Steering Committee Report + Memory Agent**

25. Build Steering Committee Report Generator: weekly executive summary
26. Build Memory/Pattern Agent: runs at engagement close, writes to pattern library
27. Build Portfolio view: cross-engagement health for multi-engagement consultants
28. Go-Live Checklist Agent: auto-generate from RICEFW + standard SAP checklist

Outcome: RAPID can run a full implementation end-to-end. From discovery to go-live checklist. All documented.

---

### F4. Pricing Implications of the Roadmap

This sequence of features maps directly to pricing tiers:

| Tier | What unlocks it | Price point |
|------|----------------|-------------|
| **Starter** | Existing RAPID today | $200/mo per engagement |
| **Professional** | Sprint 1–3 complete | $500/mo per engagement |
| **Enterprise** | Sprint 4–5 complete (Blueprint + Client Portal) | $2,000/mo per engagement |
| **Platform** | Sprint 6 (multi-engagement + memory) | $5,000/mo (unlimited engagements) |

**First prospect demo should happen at end of Sprint 4.** By then, RAPID can take a source document, extract requirements, classify against SAP, flag gaps, estimate build cost, and output a Blueprint. That's a $50,000 consultant deliverable in one afternoon.

---

### F5. What NOT to Build in 90 Days

- Native mobile apps (portal is mobile-responsive web — sufficient)
- Multi-LLM provider switching UI (Anthropic is fine; complexity not worth it)
- Real-time collaboration (single user per engagement is fine at this stage)
- Custom SAP connector (data comes from workshops/documents, not live SAP)
- Video/meeting ingestion (transcripts are sufficient; Zoom integration is a later feature)
- Billing/subscription management (manual invoicing until >5 paying clients)

---

## APPENDIX: QUICK REFERENCE — PAGE INVENTORY

| Current URL | New URL | Status |
|-------------|---------|--------|
| `/` | `/` (Command Center redesign) | Redesign |
| `/engagement` | `/portfolio` | Rename |
| `/engagement/[id]` | `/e/[id]/overview` | Major enhancement |
| `/fitgap` | `/e/[id]/fitgap` | Enhancement |
| `/requirements` | `/e/[id]/requirements` | Enhancement |
| `/hitl` | `/pending-decisions` | Rename + redesign |
| `/raci` | `/e/[id]/raci` | Minor enhancement |
| `/sources` + `/capture` | `/e/[id]/capture` | Merge into one flow |
| `/flow` + `/workflow/[reqId]` | `/e/[id]/flows` | Minor enhancement |
| `/audit` | `/e/[id]/audit` | Move to scoped |
| `/patterns` | `/platform/patterns` | Move to platform section |
| `/simulate` | `/platform/simulate` | Move to platform section |
| `/platform-backlog` | `/platform/backlog` | Move |
| `/system-health` | `/platform/system` | Move |
| `/user-management` | `/platform/users` | Move |
| NEW | `/e/[id]/deliverables` | New |
| NEW | `/e/[id]/ricefw` | New (extract from engagement detail) |
| NEW | `/portal/[clientSlug]` | New (client portal) |
| NEW | `/portal/[clientSlug]/signoff` | New |
| NEW | `/portal/[clientSlug]/timeline` | New |

---

*End of document. Build order: Sprint 1 → 6. Show to prospects at Sprint 4. First paying client at Sprint 5.*
