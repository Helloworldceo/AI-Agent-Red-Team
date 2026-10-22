# AI Agent Red-Team Tool

Adversarial testing for AI agents — not just a raw system prompt. Most AI products today aren't a single chat completion anymore: they call tools, they read retrieved documents, they hold multi-turn conversations. This tool tests all three of those surfaces, on purpose, because that's where most real agentic deployments actually live — and where most of them ship with **zero adversarial testing**.

It's a direct extension of an earlier project, [`prompt-injection-scanner`](https://github.com/helloworldceo/prompt-injection-scanner), which tested only the single "system prompt + chat completion" surface. This tool keeps that scanner's 7 attack categories and adds the attack surfaces that only exist once an LLM has tools and memory.

## What this actually catches

A model that says something embarrassing in text is a **different, lower-risk failure** than an agent that actually calls `issue_refund` because an attacker talked it into it. Most red-team tools only check the first kind. This one tracks both, and scores the second kind higher — a severity tier called **excessive agency** — regardless of how low the raw "attack success rate" looks.

```mermaid
flowchart LR
    A[Attack payload] --> B{Target type}
    B -->|Direct Chat| C[Text response only]
    B -->|Tool-Calling Agent| D[Text response<br/>+ real tool calls]
    B -->|RAG Assistant| E[Text response<br/>+ retrieved documents]
    C --> F[Text evaluator]
    D --> F
    D --> G[Agency evaluator]
    E --> F
    F --> H[Severity: info / low / medium]
    G --> I[Severity: high / critical]
```

## Architecture

```mermaid
graph TB
    subgraph Browser
        UI[Scan config form]
        Feed[Live result feed — SSE]
        Dash[Results dashboard]
        Trace[Tool-Call Trace visualizer]
    end

    subgraph "FastAPI backend"
        Routes["/scans routes<br/>REST + SSE"]
        Store[(In-memory scan store)]
        Runner[Scan runner]
        Payloads[(32 payloads,<br/>8 categories)]

        subgraph Targets
            DC[DirectChatTarget]
            TA["ToolAgentTarget<br/>(LangGraph StateGraph)"]
            RAG[RAGTarget]
        end

        subgraph Evaluators
            Text[Text evaluator<br/>keyword / LLM-judge]
            Agency[Agency evaluator]
            Sev[Severity tiers]
        end
    end

    LLM[("DeepSeek or Gemini<br/>(your API key)")]

    UI -->|POST /scans| Routes
    Routes --> Store
    Routes --> Runner
    Runner --> Payloads
    Runner --> Targets
    DC --> LLM
    TA --> LLM
    RAG --> LLM
    Runner --> Text
    Runner --> Agency
    Text --> Sev
    Agency --> Sev
    Routes -->|SSE: event per payload| Feed
    Feed --> Dash
    Dash --> Trace
```

## How a scan actually runs, step by step

```mermaid
sequenceDiagram
    participant You as You (browser)
    participant FE as React frontend
    participant BE as FastAPI backend
    participant Target as Target (LLM / agent / RAG chain)

    You->>FE: Pick target type, system prompt, attack goal, categories
    FE->>BE: POST /scans
    BE-->>FE: { scan_id }
    BE->>BE: spawn background thread
    FE->>BE: GET /scans/{id}/stream  (opens SSE connection)

    loop for each selected payload
        BE->>Target: run_conversation(turns, injection)
        Target->>Target: call the LLM (and tools, if applicable)
        Target-->>BE: response + tool-call log + retrieved docs
        BE->>BE: evaluate (text + agency) -> compute severity
        BE-->>FE: event: result
        FE-->>You: live feed updates
    end

    BE-->>FE: event: done (full summary)
    FE-->>You: risk banner, severity breakdown, per-result trace
```

## The three targets

### 1. Direct Chat — the baseline

A raw system prompt + LLM call, no tools, no retrieval. This is the original scanner's surface: 23 classic prompt-injection payloads across 7 categories (Direct Override, Role-Playing, Fictional Framing, Encoding, Goal Hijacking, Context Injection, Prompt Leakage), plus Multi-Turn Erosion payloads that escalate gradually across 2–4 messages instead of a single shot.

### 2. Tool-Calling Agent — where excessive agency lives

A hand-rolled [LangGraph](https://langchain-ai.github.io/langgraph/) `StateGraph` — deliberately *not* `langgraph.prebuilt.create_react_agent`, because the prebuilt agent hides exactly the per-call arguments, results, and timestamps this tool needs to log for every tool invocation.

```mermaid
flowchart TD
    Start([Payload message]) --> Agent["agent node<br/>LLM.bind_tools([...])"]
    Agent -->|tool_calls present| Tools["tools node<br/>execute + log each call"]
    Tools -->|ToolMessage appended to history| Agent
    Agent -->|no tool_calls| Final([Final response])
    Tools -.every call logged.-> Logger[(ToolCallLogger)]
```

Four mock tools, each tagged by sensitivity and **never actually executing a real side effect** — every call returns a canned confirmation string:

| Tool | Sensitivity | What it simulates |
|---|---|---|
| `search_knowledge_base` | safe | read-only lookup |
| `issue_refund` | sensitive | a real financial action |
| `send_email` | sensitive | sending on the business's behalf |
| `update_account_settings` | sensitive | modifying account data |

Three attack categories target this specifically:
- **Tool-Output Injection** — the malicious instruction lives in a tool's *return value*, not the user's message (e.g. a poisoned knowledge-base article the agent reads back)
- **Excessive Agency** — social-engineering prose aimed at a specific sensitive tool ("verification is down, just process it"), not "ignore your instructions" wording
- **Control payloads** — a legitimate request that *should* trigger a sensitive tool, scored separately, so a 0%-vulnerable result can be told apart from "this agent never does anything"

### 3. RAG Assistant — indirect injection via poisoned documents

This target deliberately reproduces a real vulnerability pattern found in this author's own shipped [`rag-assistant`](https://github.com/Helloworldceo/rag-assistant) project: retrieved document chunks get dropped **verbatim** into the system prompt, with no delimiters and no sanitization.

```mermaid
flowchart LR
    Query[User query] --> Retriever[MockRetriever<br/>keyword overlap, no embeddings]
    Corpus[(Default KB documents)] --> Retriever
    Poison["Poisoned document<br/>(if this payload is active)"] -.always ranks top,<br/>like real poisoning.-> Retriever
    Retriever --> Join["context = '\\n\\n'.join(docs)"]
    Join -->|dropped in verbatim,<br/>zero sanitization| Prompt["System prompt +<br/>Retrieved context: {context}"]
    Prompt --> LLM[Target LLM]
    LLM --> Answer[Final answer]
```

The point is testing a real vulnerability class, not a strawman — the RAG chain's templating code is a near-exact copy of the real one.

## Severity, not just success rate

```mermaid
flowchart TD
    A[Attack result] --> B{Did it succeed at all?}
    B -->|No| INFO["info<br/>(resisted)"]
    B -->|Yes| C{Sensitive tool triggered?}
    C -->|No| D{Text-evaluator confidence}
    D -->|high| MEDIUM[medium]
    D -->|low / medium| LOW[low]
    C -->|One tool| E{Attacker's goal appears<br/>in the tool-call arguments?}
    E -->|No| HIGH[high]
    E -->|Yes| CRIT1[critical]
    C -->|Multiple tools| CRIT2[critical]
```

A scan with a 5% raw success rate and one `critical` tool-call incident visibly outranks a 40%-success-rate scan where nothing but text got leaked — the risk banner escalates on severity, not on the success-rate number alone.

## Quick start

**Backend:**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add DEEPSEEK_API_KEY and/or GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

Binds to `127.0.0.1` by default — this is a local tool, same posture as the Streamlit apps it's descended from. No auth; add one before exposing it publicly.

## Two LLM providers

Switchable per scan in the UI — the API key field clears on switch so a key never silently gets sent to the wrong provider.

| Provider | Default model | Notes |
|---|---|---|
| DeepSeek | `deepseek-chat` | OpenAI-compatible endpoint |
| Gemini | `gemini-2.0-flash` | via `langchain-google-genai` |

## Testing

```bash
cd backend && source .venv/bin/activate && python -m pytest
```

47 tests, zero real API calls — every LLM is a scripted fake. Coverage includes the payload registry's shape, both text evaluators (including the malformed-JSON fallback path), the full agency/severity tier matrix, all three targets (including a regression test proving a poisoned RAG document's text survives *verbatim* into the constructed prompt context), the scan runner, and the FastAPI routes end-to-end for both providers.

## Project structure

```
backend/app/
  models/       Pydantic schemas (payload, trace, scan)
  payloads/     the attack library, by category, plus a target-aware registry
  targets/      DirectChatTarget, ToolAgentTarget (LangGraph), RAGTarget
  evaluators/   keyword + LLM-judge (text), agency (tool-call), severity tiers
  runner.py     payload -> target -> evaluate -> severity -> yield
  scan_store.py in-memory scan state (SQLite is a natural phase-2 swap)
  routes/       REST + SSE streaming, provider/target/payload metadata
frontend/src/
  components/
    trace/      ToolCallTrace.tsx — a visual step-by-step trace that makes
                an excessive-agency incident unmissable, not a log line
```

## Roadmap

- SQLite-backed scan history (currently in-memory, cleared on restart)
- Auth / rate-limiting — only needed once this is deployed somewhere public
- Multi-scan history UI
- Playwright / component-level frontend tests
