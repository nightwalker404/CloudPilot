# CloudPilot Frontend (Agent Inspector)

React + Vite + Tailwind, no shadcn CLI dependency — the primitives in
`src/components/ui/` are hand-written in the same style (rounded-md,
zinc palette, variant props) so you can swap in real shadcn components
later without restructuring anything.

## Setup

```
npm install
cp .env.example .env      # set VITE_API_BASE_URL if not localhost:8000
npm run dev
```

Make sure the backend has CORS enabled (see the `main.py` update from
earlier) and is reachable at the URL in Settings → API Base URL.

## Layout

- **Top bar** — Chat / Tool Call Log / Settings, a health dot, and the
  drawer toggle.
- **Conversation drawer** — session history (`GET /conversations`),
  new/select/delete.
- **Chat view (split pane)**
  - Left: bubble chat, `POST /chat`.
  - Right: **Agent Execution Inspector** — a dark, monospace panel
    showing parsed tool calls (name, arguments, result, ok/error) for
    the active conversation, plus the raw request/response JSON of the
    last `/chat` call.
  - On narrow screens the split becomes two tabs (Chat / Inspector)
    instead of side-by-side panes.
- **Tool Call Log view** — aggregates tool executions across *all* of
  the current user's conversations into one table.
- **Settings view** — API base URL + `X-User-ID`, both stored in
  `localStorage`; "Test connection" hits `/health`.

## Backend gaps this works around

- `role: "tool"` messages in your schema carry no `tool_call_id` and no
  tool name — only a stringified result. The inspector pairs each
  assistant message's `tool_calls` with the *next* message in the array
  as a best-effort match. This works for the current one-tool-per-turn
  flow but will misattribute results if a turn ever calls multiple
  tools back to back. If you want this to be reliable, have the
  dispatcher store `{"role": "tool", "name": tool_name, "content": result}`
  instead of just `content`.
- Nothing in the schema timestamps individual messages, so the Tool
  Call Log's "Updated" column is the *conversation's* `updated_at`, not
  the moment each tool actually ran.
- The Tool Call Log builds itself by fetching every conversation in
  full on load — fine for a demo, but it's an N+1 pattern that won't
  scale; a dedicated `/tool-calls` endpoint would be the real fix.

## Design notes

Left pane follows the brief's "ChatGPT/Claude-style" direction closely
on purpose — that's a legible, trusted pattern for the chat half. The
right pane is deliberately a different register: dark, monospace,
terminal-like, because its job is different — it's there to make the
agent's *decisions* legible and auditable, which is the actual point
of this internal tool. The contrast between the two panes is the one
intentional design move here; everything else stays quiet so that
contrast reads clearly instead of competing with itself.
