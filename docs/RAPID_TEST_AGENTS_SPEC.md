# RAPID Test Agents — Specification

*From: "Create a specification for building an agent or agents" (PDF). Blueprint for autonomous test agents and a Testing Command Center.*

## 1. Objectives

- Build test agents that **log in and use RAPID end-to-end** (UI + APIs) like consultants/business users.
- **Run scenario-based tests on demand** (button click) from a **Testing Command Center**.
- **Identify:** defects (functional failures, broken flows); UX/efficiency issues; complex features (high cognitive load).
- **Produce structured findings** that feed into the product backlog.
- Agents must be **engagement-aware**, **configurable**, and **repeatable**.

## 2. Agent Types

| Agent | Role | Capabilities |
|-------|------|--------------|
| **Navigator** | E2E flow tester | Happy path (Client → Engagement → Capture → Requirements → Fit/Gap → RICEFW → Export); edge cases (multiple engagements, switching, partial data); detect broken nav, wrong context, dead ends. |
| **Data Integrity** | CRUD & referential tester | Create/update/delete clients, engagements, requirements, process steps, fit/gap, RICEFW; verify required fields, error messages, no orphans, cross-links work; stress bulk import/export, concurrency. |
| **UX & Efficiency** | Usability tester | Measure steps/clicks per task; time to completion; complexity signals (back-and-forth, overloaded forms, disconnected flows); score discoverability, cognitive load, input effort (0–5). |
| **Orchestrator** | Command Center brain | Maintain scenario catalog; start runs by button or webhook/CLI; assign tasks to agents; aggregate results (summary, issues by severity/area, pass/fail, UX scores). |

## 3. Testing Command Center UI

- **Environment selector:** DEV, STAGING, SANDBOX.
- **Scenario selector (multi-select):** Smoke, Regression, Data Integrity, UX Deep-Dive, Import/Export.
- **Engagement template selector:** Real or synthetic engagement.
- **Run Tests** button; **live status:** progress per scenario, active agents.
- **Results:** Overall pass/fail; counts (defects, warnings, UX hotspots); filter by area (Client, Engagement, Current State, Requirements, Fit/Gap, RICEFW, HITL, Assets, Navigation); drill-down per issue (scenario, agent, URL, steps, expected vs actual, severity, suggested improvement).

## 4. Agent Behaviors & APIs

- **Auth/context:** System credentials (e.g. Tester_Consultant); per run: choose/create test client/engagement; pass `engagement_id` to all agents.
- **Interaction:** Prefer public APIs and UI; log every action (HTTP/UI event, payloads masked, results); for UX, model click paths and measure “distance” to goal.
- **Test case library:** Client & Engagement (create min/full, state transitions, context persistence); Current State (upload assets, AS-IS in Process Mirror, linking); Requirements (form, agent suggestion, RTM export, Fit/Gap); Fit/Gap (Analyse All, classifications, RICEFW generation); HITL & Agent (state moves, audit trail, engagement context).

## 5. Issue Classification & Backlog

- **Per issue:** area, type (bug, UX issue, complexity, data integrity, performance, documentation), severity (blocker, high, medium, low), repro_steps, expected vs actual, screenshot_ref, agent_id, scenario_id.
- **Store** in RAPID’s **Platform Backlog** (platform_issues); flag cross-engagement/cross-flow issues for prioritization.
- **Summaries:** “Top 10 issues by complexity impact”; “Areas with highest defect density.”

## 6. Running Modes

- **Smoke:** Fast, small subset after each deploy.
- **Regression:** Full, nightly or pre-release.
- **Scenario:** Focused on one domain (e.g. Current State).
- **Stress:** High volume imports/updates for performance and integrity.

## Implementation status

- **Fallback marker:** `rapid-fallback-2026-03-07` (both repos); doc: `docs/RAPID_FALLBACK_2026-03-07.md`.
- **Phase 1 (this implementation):** Testing Command Center page; GET /v1/testing/scenarios; POST /v1/testing/run (API-level smoke/checks); results viewer; optional push issues to platform_issues.
- **Future:** Full Navigator/Data Integrity/UX agents (UI automation), Orchestrator scheduling, webhook/CLI, running modes presets.
