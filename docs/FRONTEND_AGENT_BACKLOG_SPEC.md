# Frontend: Agent Conversation & Platform Backlog (rapid-ui)

Use this spec to implement the Agent Team and Platform Backlog UI in the rapid-ui repo. Backend endpoints are live under `/v1`.

## 1. Agent roles list

- **GET /v1/agent-roles**  
  Returns `{ items: Array<{ role_id, name, mandate, focus_areas, behavior_rules, escalation_rules }>, total }`.
- **Use:** Dropdown or list to pick an agent role for “Talk to an agent” or simulation.

## 2. Agent conversation (simulate)

- **POST /v1/simulate/agent-response**  
  Body: `{ engagement_id, agent_role_id, phase?, context_message?, conversation_turn? }`.  
  Returns `{ agent_role_id, phase, reply }`.
- **UI:**  
  - Page or section: “Agent simulation” or “Talk to an agent”.  
  - Select engagement (from URL or dropdown), select agent role (from GET agent-roles).  
  - Optional: phase selector (pre_engagement | current_state | requirements | fit_gap).  
  - Text input for “Your message” (context_message).  
  - Optional: show conversation_turn history and append assistant reply.  
  - On submit, call POST simulate/agent-response; display `reply` in the UI.

## 3. Agent maturity (optional)

- **GET /v1/agent-roles/{role_id}/maturity**  
  Returns `{ role_id, scores: Array<{ criterion, score, assessed_at, notes }> }`.
- **POST /v1/agent-roles/{role_id}/maturity**  
  Body: `{ criterion, score (1–5), notes? }`.  
  Use for admin or “Assess maturity” flow.

## 4. Platform issues / backlog

- **POST /v1/platform-issues**  
  Body: `engagement_id, problem_description, agent_role_id?, phase?, context?, issue_type?, suggested_improvement?, priority?`.  
  Creates an issue (e.g. when simulation hits a limitation).
- **GET /v1/platform-issues?engagement_id=&priority=&status=**  
  Returns `{ items, total }`.
- **PATCH /v1/platform-issues/{id}**  
  Body: `{ status?, priority? }`.
- **GET /v1/engagement/{engagement_id}/platform-backlog**  
  Returns `{ engagement_id, by_priority: { high: [], medium: [], low: [] }, total }`.
- **UI:**  
  - New page `/platform-backlog` or tab on engagement “Platform issues”.  
  - List issues; filter by priority (high/medium/low) and status.  
  - Show: problem_description, suggested_improvement, issue_type, priority, status.  
  - Optional: form to create issue (engagement_id, problem_description, priority, suggested_improvement).

## 5. Navigation

- Add “Agent simulation” (or “Simulate”) and “Platform backlog” to header/nav, with engagement context where needed.

## 6. API base and auth

- Base URL: same as rest of app (e.g. `process.env.NEXT_PUBLIC_API_URL` ending in `/v1`).  
- Send `X-API-Key` or `Authorization: Bearer <key>` if the backend requires it.
