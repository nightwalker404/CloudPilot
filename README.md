# CloudPilot

A conversational AI agent that provisions real infrastructure from natural language. Tell it what you want ("a vps with 5gb ram and 20gb storage and 2 core, name it rtx234, ubuntu") and it calls tools that actually create it — starting with VMs via the [Incus](https://linuxcontainers.org/incus/) REST API.

## Architecture

```
┌────────────┐     ┌──────────────┐     ┌────────────────────┐
│  Frontend  │────▶│   FastAPI    │────▶│  Ollama (LLM host)  │
│ (index.html)│     │   backend    │     └────────────────────┘
└────────────┘     │              │
                    │  dispatcher  │────▶ tool: create_vm ──▶ Incus API (mTLS)
                    │  + registry  │────▶ tool: web_search ─▶ Tavily API
                    │              │
                    └──────┬───────┘
                           ▼
                       MongoDB
                  (conversation history)
```

- **Backend** — FastAPI, talks to an [Ollama](https://ollama.com/) server for chat + tool-calling.
- **Tool calling** — the model decides when to call a tool; `app/tools/dispatcher.py` runs it and feeds the result back in; `app/tools/registry.py` is the single place both tool sets (`hosting`, `websearch`) get merged.
- **Hosting tool (`create_vm`)** — builds a payload (CPU/memory/disk/OS/name), calls the Incus REST API over mTLS, waits for the create operation, starts the VM, polls for its IP, and returns a human-readable summary with login creds from cloud-init.
- **Web search tool (`web_search`)** — Tavily-backed search for anything outside the model's own knowledge.
- **Storage** — conversations persist to MongoDB so a `conversation_id` can be resumed across requests.
- **Frontend** — a single static `frontend/index.html`, no build step, that exercises every route for testing/demo purposes.

## Requirements

- Docker + Docker Compose
- An Incus server reachable from the backend, with mTLS client cert/key + its server cert (see `certs/`)
- A GPU host for Ollama if you want reasonable latency (see `docker-compose.yml`, GPU reservation is already wired up)
- (Optional) A [Tavily](https://tavily.com) API key for `web_search`

## Setup

1. Drop your Incus mTLS certs into `certs/`: `client.crt`, `client.key`, `server.crt`.
2. Fill in the environment variables (see table below) — either in `docker-compose.yml` directly or via a `.env` file.
3. Pull an Ollama model that actually supports tool calling reliably (see **Known issues** — the default in `docker-compose.yml`, `qwen2.5-coder:1.5b`, is not a good choice):
   ```
   docker exec -it ollama ollama pull qwen2.5:7b-instruct
   ```
4. Bring everything up:
   ```
   docker compose up -d --build
   ```
5. Check it's alive:
   ```
   curl http://localhost:8000/health
   ```
6. Open the frontend. Don't just double-click `index.html` (some browsers handle `fetch()` from `file://` unreliably) — serve it instead:
   ```
   cd frontend && python3 -m http.server 5500
   ```
   then visit `http://localhost:5500/index.html`, set the Base URL to your backend, and set any `X-User-ID` value.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `APP_NAME` | yes | Display name |
| `DEBUG_MODE` | no (default `False`) | Verbose logging |
| `APP_HOST` / `APP_PORT` | yes | Where uvicorn binds |
| `MODEL` | yes | Ollama model tag to use for chat + tool calling |
| `LLM_BASE_URL` | yes | Ollama server URL |
| `MONGO_URI` | yes | Mongo connection string |
| `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` | yes | Mongo root credentials |
| `MONGO_DB_NAME` | no (default `cloudpilot`) | Mongo database name |
| `INCUS_URL` | yes | Incus API base URL (e.g. `https://127.0.0.1:8443`) |
| `TAVILY_API_KEY` | no | Enables `web_search`; without it the tool raises a clear config error instead of a silent failure |

## API routes

| Method | Path | Notes |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/chat` | Body: `{ messages, conversation_id?, model?, stream?, temperature?, max_tokens? }`. Requires `X-User-ID` header. |
| `POST` | `/conversations` | Create an empty conversation |
| `GET` | `/conversations` | List conversations for the user |
| `GET` | `/conversations/{id}` | Full message history |
| `DELETE` | `/conversations/{id}` | Delete a conversation |

All routes except `/health` require an `X-User-ID` header — there's no auth beyond that yet, so don't expose this publicly as-is.

## Available tools

| Tool | What it does |
|---|---|
| `create_vm(cpu, memory, disk, vm_name?, os?)` | Creates + starts a VM via Incus, returns name/creds/IP |
| `web_search(query, max_results?)` | Tavily search, returns a summarized answer + top results |

## Known issues

- **Tool-calling reliability depends heavily on the model.** `qwen2.5-coder:1.5b` (the current `docker-compose.yml` default) is a small, code-tuned model and frequently responds in plain text instead of emitting a structured tool call — especially for requests that pack several parameters into one sentence. Use a larger instruction-tuned model (`qwen2.5:7b-instruct` or similar) if you're seeing "it didn't call the tool" behavior.
- **No input bounds on `create_vm`.** CPU/memory/disk are type-checked but not range-checked — a bad request will be forwarded to Incus as-is.
- **CORS is wide open (`allow_origins=["*"]`)** in `main.py` for local testing. Restrict this before deploying anywhere reachable outside your dev machine.
- **No auth beyond the `X-User-ID` header** — anyone who can reach the API can act as any user by setting that header themselves.

## Roadmap

This is the first piece of a bigger multi-channel hosting agent (website chat, Telegram, later WhatsApp) that can check user balance, provision infra, generate payment links, and deliver credentials end-to-end. Planned infra additions: Ansible, Packer golden images, Kubernetes.