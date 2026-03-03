# RAPID — Value-Added Features Backlog (Refined)

**Aligned with:** Current system (rapid-mvp + rapid-ui).  
**Reference:** RAPID_NextGen_Build_Prompt.md — refined to remove redundancy and sequence for incremental delivery.  
**Fallback version:** Git tag `rapid-fallback-2026-03-02` in both repos.

---

## Already Built (Do Not Rebuild)

| Area | Backend | Frontend |
|------|---------|----------|
| Clients & engagements | CRUD, prefill-from-website | /clients, /clients/[id] |
| Requirements | CRUD, transcript extract, archaeologist | /capture, /engagement, /requirements |
| Gap analysis | 244 scope items, POST gap-analysis, analyse-all | /gap-analysis |
| **HITL pipeline** | hitl_state, hitl_events, hitl-advance, hitl-reject, hitl-queue, hitl-events | /hitl (Review Board) |
| Sign-off | sign_off_status, POST sign-off (sme/owner) | Engagement dashboard HITL simulation |
| Process steps | CRUD, extract-from-transcript | /workflow/[reqId] (BPMN) |
| Process flow | process-flow, process-flow/assign, process_level_2/3 | /flow |
| **RICEFW inventory** | ricefw_inventory table, GET/POST/PATCH/DELETE /engagement/{id}/ricefw, export Excel | Engagement dashboard #ricefw (list, add, edit, delete, export) |
| Assets | upload, by engagement/requirement | (upload exists; list UI can be enhanced) |
| Excel | Requirements export/import, RICEFW export | Engagement: Download Excel, Upload Excel, RICEFW Download |

---

## Implementation Sequence (Value-Added Only)

### Phase A — UX & HITL refinements (current release)
- **A1** Engagement dashboard: show **HITL state** per requirement; link “Review in HITL” to /hitl?engagement_id=.
- **A2** Engagement [id]: add “Review in HITL” and “As-Is Workflow” in requirement detail; ensure workflow link passes engagement_id.
- **A3** Synthetic seed: set `hitl_state='ai_draft'` on seeded requirements (DB default suffices); document “Seed synthetic → open HITL → advance a few” for browser test.
- **A4** Header: keep HITL, RICEFW, Engagement, Gap Analysis; ensure engagement_id is passed where needed.

### Phase B — Fit/Gap classification layer
- **B1** Supabase: create `fit_gap_assessments` table (per NextGen spec); no change to existing gap_results.
- **B2** Backend: POST /requirements/{req_id}/fit-gap-assess, GET /engagement/{id}/fit-gap-board, POST fit-gap-assessments/{id}/review, POST engagement/{id}/fit-gap-analyse-all.
- **B3** Frontend: /fitgap page (board by fit_type, process view, review flow).

### Phase C — RICEFW from gaps (optional enhancement)
- **C1** Backend: POST /engagement/{id}/ricefw-generate — from approved fit_gap_assessments where fit_type=gap_ricefw, create ricefw_inventory items (use existing table).
- **C2** Frontend: “Generate from Gaps” on RICEFW section (engagement #ricefw or future /ricefw page).

### Phase D — Pattern library & feedback loop
- **D1** Supabase: feedback_events, pattern_library tables.
- **D2** Backend: POST /feedback, GET /feedback, GET /pattern-library, update_pattern_library() on feedback; inject top patterns into archaeologist and fit-gap prompts.
- **D3** Seed pattern_library with 30+ patterns (seed_patterns.sql).

### Phase E — Sector archetype & benchmarks
- **E1** Supabase: clients.sector_archetype, complexity_drivers, erp_maturity, benchmark_opt_in; benchmark_hints table.
- **E2** Backend: GET /engagement/{id}/benchmark-hints, POST /clients/{id}/benchmark-opt-out.
- **E3** Frontend: client form fields; engagement [id] “Benchmark insights” section.

### Phase F — Excel and export polish
- **F1** Backend: optional second sheet “Fit-Gap” in requirements export (when fit_gap_assessments exist); GET /requirements/template/download.
- **F2** Frontend: “Download template” link; “Export RICEFW” already present.

---

## Removed / Deferred (No Duplication)

- **Separate “ricefw” table:** Use existing **ricefw_inventory** only; same schema intent (type, name, description, req_id, status, complexity, priority).
- **Duplicate HITL backend:** Already implemented; only UI/UX refinements in Phase A.
- **New sign-off workflow:** Existing sign_off_status (draft / sme_approved / owner_approved / confirmed) retained; HITL state machine is the primary review pipeline.

---

## Synthetic Data for Browser Test

1. **Create engagement:** Use /clients to create client and engagement, or use existing (e.g. ENG-001).
2. **Seed synthetic:** On /engagement, load engagement ID → click “Seed synthetic data” (POST /engagement/{id}/seed-synthetic). Requirements are created with default hitl_state=ai_draft.
3. **HITL:** Go to /hitl?engagement_id=ENG-001 → advance some items through SME → Architect → Approved; reject one to ai_draft.
4. **RICEFW:** Open RICEFW Inventory on engagement → add items linked to requirements; edit/delete; export Excel.
5. **Workflow:** Open a requirement → “View As-Is Workflow” → extract steps or add manually; export .bpmn.

---

## Definition of Done (Current Release — Phase A)

- [ ] Fallback tag `rapid-fallback-2026-03-02` exists in both repos.
- [ ] REFINED_BACKLOG.md committed.
- [ ] Engagement dashboard shows HITL state and “Review in HITL” where useful.
- [ ] Engagement [id] requirement detail links to HITL and workflow with engagement_id.
- [ ] Synthetic seed creates requirements with hitl_state=ai_draft (default).
- [ ] Backend tests pass; frontend build passes.
- [ ] Commits pushed; ready for browser test.

Later phases (B–F) follow the same backlog and are implemented in order after Phase A sign-off.
