# RAPID checkpoint — continue with a new agent

**Marker:** `RAPID_CHECKPOINT_2026-03-057`  
**Date:** 2026-03-07 (Prompt for new Agent — 3.7.2026)  
**Repos:** rapid-mvp (backend), rapid-ui (frontend)

---

## Purpose

Use this file if something goes wrong. A **new agent** can resume from here by reading the docs below and following the prompt in the "Copy-paste prompt" section.

---

## What’s done (since last checkpoint)

- **PDF-driven engagement workspace (from Review latest built specification):**
  - **Client context:** On `/engagement/[id]`, read-only "Client context" section (Client 360 slice) when engagement has client_id; link to full client.
  - **Hyperlinked IDs:** EngagementLabel links to `/engagement/[id]`; ClientIdLink component (engagement detail + client detail); ReqIdLink unchanged.
  - **Engagement workspace tabs:** Sticky tab bar on engagement detail — Overview, Client context, Completion, Benchmark, Business case, Audit, Requirements (in-page); Fit/Gap, RICEFW, HITL, Assets, Agent (links out with engagement_id).
- **Spec doc:** `docs/RAPID_Review_Spec_Standalone.md` v1.2 (Client context, hyperlinked IDs, workspace tabs).
- **Previous:** Enterprise Phases A–G (sources, sidebar, mission-control home, /sources, /requirements, Fit-Gap summary, HITL report, completion checklist, onboarding wizard). See `docs/RAPID_CHECKPOINT_2026-03-05.md`.

---

## Where to read next

- **rapid-mvp:** `PROJECT.md` (status, open errors, next improvements), `CLAUDE.md` (API, models, conventions).
- **rapid-ui:** `PROJECT.md`, `CLAUDE.md`.
- **Feature completion rule:** `.cursor/rules/feature-completion.mdc` (Build, Test, Commit, Deploy, Ready to check).

---

## Copy-paste prompt for a new agent

Use this exact prompt with a new agent at any time to resume from this checkpoint:

```
Continue RAPID from checkpoint. Read rapid-mvp/PROJECT.md and rapid-mvp/CLAUDE.md first, then rapid-ui/PROJECT.md and rapid-ui/CLAUDE.md. Fix any open errors, then pick the next improvement from PROJECT.md "Next improvements". Follow .cursor/rules/feature-completion.mdc (Build, Test, Commit, Deploy, Ready to check). Checkpoint marker: docs/RAPID_CHECKPOINT_2026-03-057.md.
```
