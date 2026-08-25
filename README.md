# Self-Evaluating Lesson Generator

An agentic lesson-generation system that plans, writes, evaluates, and improves its own lessons
before returning a final result — for **any topic you give it**. See `CLAUDE.md` for the full
design spec, `plan.md` for the implementation plan this build followed, and `update.md` for a
step-by-step build log (including bugs found and fixed along the way).

- **Agents**: Planner → Generator → Evaluator → Improver, orchestrated with LangGraph
  (`backend/graph.py`), with a max of 2 retries before the loop terminates.
- **LLM**: Groq (`langchain-groq`), default model `openai/gpt-oss-120b`.
- **Evaluator**: hybrid — 5 deterministic checks (length, section flow, summary, simple language,
  jargon explained) in `backend/utils/helpers.py`, plus one LLM call for 5 semantic checks
  (definition, motivation, workflow, example, accuracy). All 10 are strict pass/fail, no scores.
- **Memory**: `backend/memory/memory.json` persists common failure patterns and the prompt
  guidance learned from them, shared across every topic and every run.
- **Interface**: a small React page that calls a FastAPI backend.

## Prerequisites

- Python 3.10+ (built and tested on 3.13)
- Node.js 18+ / npm (built and tested on Node 24)
- A free Groq API key from [console.groq.com](https://console.groq.com/keys)

## Setup

### 1. Backend

```
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and set your real key:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Run the server **from inside `backend/`** (its internal imports, e.g. `from config import ...`,
are written relative to that directory):

```
cd backend
uvicorn main:app --reload --port 8001
```

You should see `Uvicorn running on http://127.0.0.1:8001`. Leave this terminal running.

### 2. Frontend

In a second terminal:

```
cd frontend
npm install
npm run dev
```

Open the printed local URL (typically `http://localhost:5173`). The Vite dev server proxies
`/api/*` requests to the backend at `http://127.0.0.1:8001` (see `frontend/vite.config.js`).

## Using it

Type any topic into the input box — the placeholder shows the assignment's example topic,
"Introduction to Retrieval-Augmented Generation (RAG)", but nothing is hardcoded to it, any subject
works — and click **Generate Lesson**. The page then shows:

1. The final lesson
2. The evaluation report (10 pass/fail checks + reasons)
3. Retry history (what failed on each attempt, up to 2 retries)
4. What the system has learned in memory so far (shared across all topics)

A single generation makes 2-4 real Groq calls (planner, generator, evaluator, and one improver
call per failed retry), so expect it to take a few seconds up to roughly a minute in the worst
case (2 retries).

## API

- `POST /api/generate` — `{ "topic": "..." }` → runs the full graph, returns
  `final_lesson`, `evaluation`, `retry_count`, `rejection_log`, `memory_updates`.
- `GET /api/memory` — current persisted memory.
- `GET /api/history` — summary of past runs.
- `GET /api/example-topic` — the placeholder topic shown in the UI.

Interactive API docs are available at `http://127.0.0.1:8001/docs` while the backend is running.

## Project layout

```
backend/
  main.py           FastAPI app (routes, CORS)
  graph.py           LangGraph StateGraph (planner -> generator -> evaluator -> [improver loop])
  config.py           env loading, retry limit, learner profile, section template
  llm.py               shared Groq client + prompt-file loader
  agents/               planner.py, generator.py, evaluator.py, improver.py, memory.py
  prompts/               one .md prompt template per agent
  schemas/               pydantic/TypedDict models for state and each agent's I/O
  memory/                memory.json, history.json (created/updated at runtime)
  logs/                   attempts.json, rejections.json (created/updated at runtime)
  utils/                  helpers.py (deterministic rubric checks), logger.py

frontend/
  src/
    App.jsx             page shell
    api.js                fetch wrappers
    components/            TopicForm, LessonView, EvaluationChecklist, RetryHistory, MemoryPanel
```

See `plan.md` for the full design rationale behind this structure.

## Troubleshooting

- **`WinError 10013` / can't bind to the port**: something else (often a leftover uvicorn process)
  is already listening on that port. Check with
  `Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue`, then either stop that
  process or run uvicorn on a different `--port` (and update `frontend/vite.config.js`'s proxy
  target to match).
- **Frontend requests to `/api/*` return 502**: the backend isn't running, or Vite's proxy can't
  reach it. Confirm the backend is up (`curl http://127.0.0.1:8001/api/example-topic`) and that
  `vite.config.js`'s proxy target uses `127.0.0.1`, not `localhost` (Node can resolve `localhost`
  to the IPv6 `::1`, which uvicorn's default IPv4-only bind will refuse).
- **`/api/generate` returns 500**: check the backend terminal for a traceback. Common causes are an
  invalid/missing `GROQ_API_KEY`, or `GROQ_MODEL` pointing at a model your key doesn't have access
  to (list what's available with a GET to `https://api.groq.com/openai/v1/models` using your key).
- **Vite config changes not taking effect**: restart `npm run dev` — `vite.config.js` isn't
  hot-reloaded.
