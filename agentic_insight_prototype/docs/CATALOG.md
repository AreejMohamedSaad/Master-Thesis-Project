# Practice catalog

Working list of **lifecycle and agentic practices** for the thesis prototype: where each rule comes from (Ntentos & Zdun paper, *Agentic Design Patterns* book, `resourses/topic.tex`), why it matters for **collaboration footprint** analysis, and what **code evidence** detection v1 will search for.

**Status:** five rules defined below; **PR2, PR8, and B1** implemented as heuristic detectors (see `src/insight_proto/detectors/`). PR6 and B5 are documented for a later pass.

---

## How this catalog fits the thesis

The thesis mines a **collaboration footprint** from agentic repositories: orchestration logic, communication channels, and validation gates (`resourses/topic.tex`). The paper’s **15 RL lifecycle practices (PR1–PR15)** give a proven catalog + detection pattern; this file picks a **first slice** adapted to multi-agent / LLM systems and maps each rule to **smells** we want to flag when the practice is missing or weak.

| Thesis concept | Catalog role |
|----------------|--------------|
| Collaboration footprint | Rules point at orchestration, handoffs, tool boundaries, gates |
| Smell detection | Absence or weakness of a practice supports a smell claim with evidence |
| Insight-as-a-Service | Detectors produce structured reports (present / absent / unclear + quotes) |

---

## Baseline: PR1–PR15 (Ntentos & Zdun)

The paper defines fifteen RL pipeline practices used by CPA/AVA-style architecture: metadata, logging, registry, evaluation, validation gates, rollback, staging environments, and related MLOps controls.

| ID | Practice (short) | Relevance to this thesis |
|----|------------------|---------------------------|
| PR1 | Structured metadata | Observability - what is recorded about runs |
| PR2 | Runtime logs / traces | **Selected** - trace tool calls and handoffs |
| PR3 | Immutable model versioning | Secondary - unless agent configs are versioned |
| PR4 | Pinned loading | Reproducibility of pipeline versions |
| PR5 | Centralized registry | Analogy: registry of agents / artifacts |
| PR6 | Automated selection / promotion | **Selected** - quality gates before next step |
| PR7 | Standardized evaluation | Collaboration-quality metrics |
| PR8 | Validate deployment artifacts | **Selected** - validation gates between stages |
| PR9 | Rollback | Recovery when agent chain fails |
| PR10 | Versioned API contracts | Protocols between agents |
| PR11–PR15 | Triggers, canary, staging, sandbox | Lower priority for v1 detection |

**Thesis extension:** same engineering idea (catalog + detection + gates), applied to **agent collaboration** indicators and smells, not only RL MLOps.

---

## First detection batch (5 rules)

Implementation order: **PR2 → PR8 → B1 → PR6 → B5** (easiest heuristics first).

| ID | Practice | Source | Detector v1 | Status |
|----|----------|--------|-------------|--------|
| PR2 | Runtime logs / traces | Ntentos & Zdun (PR2) | regex + keyword | defined |
| PR8 | Validation between stages | Ntentos & Zdun (PR8) | regex + AST (calls) | defined |
| B1 | Routing / handoff | *Agentic Design Patterns*, Ch. 2 (Routing) | keyword + class/function names | defined |
| PR6 | Selection / promotion (quality gates) | Ntentos & Zdun (PR6) | regex + keyword | defined |
| B5 | Tool use / tool boundaries | *Agentic Design Patterns*, Ch. 5 (Tool Use) | regex + decorator names | defined |

---

## PR2 - Runtime logs / traces

**Source:** Ntentos & Zdun - PR2 (runtime logs / traces).

### Why it matters

Multi-agent pipelines fail in ways that are hard to replay: one agent’s output becomes another’s input, and errors compound. Without runtime logs or traces around steps, tool calls, and handoffs, you cannot explain *why* agent B ran after agent A or what data crossed the boundary. This directly supports smell detection for **missing observability** and **impossible-to-debug decisions** (`topic.tex` Phase 2).

### Problem it addresses

- No audit trail when collaboration goes wrong
- Tool calls and reasoning steps invisible in orchestration code
- Cannot correlate agent actions across a pipeline

### Evidence in code (what to search for)

| Signal type | Examples |
|-------------|----------|
| Imports | `logging`, `loguru`, `structlog`, `wandb`, `mlflow`, `opentelemetry`, `trace` |
| Calls | `logger.info`, `logger.debug`, `logging.getLogger`, `print(` (weak signal) |
| Structured fields | `extra=`, `trace_id`, `span`, `step=`, `agent=`, `tool=` in log messages |
| Context managers | `with ...log`, tracing wrappers around tool or agent calls |

### Detector v1 method

- **Primary:** regex for `import logging`, `from loguru`, `logger\.(info|debug|warning|error)`, `logging\.getLogger`
- **Secondary:** keyword scan for `trace`, `span`, `wandb`, `mlflow` near orchestration functions
- **File scope:** only paths from `ml_ranked` (file selection output)
- **Verdict:** `present` if ≥1 strong signal; `unclear` if only `print`; `absent` if none

### Example pass

An orchestrator module logs each delegation: `logger.info("handoff", extra={"from_agent": "planner", "to_agent": "coder", "task_id": task_id})`.

### Example fail

An orchestration file runs multiple `invoke()` / `run()` calls with no logging or tracing imports anywhere in the file.

### Smell link

| Smell (`topic.tex`) | If PR2 absent / weak |
|---------------------|----------------------|
| Missing observability for tool calls and reasoning | Strong indicator |
| Impossible to debug why an agent made a specific decision | Strong indicator |
| Erroneous data propagates (compounding errors) | Supporting - harder to localize without traces |

---

## PR8 - Validation between stages

**Source:** Ntentos & Zdun - PR8 (validate deployment artifacts). In the thesis framing: **validation gates between agents or pipeline steps** (analogous to AVA gates in the paper).

### Why it matters

Agentic systems pass unstructured outputs (text, JSON, files) between components. Without explicit checks before the next stage runs, bad output propagates and errors compound, which is one of the core smells in `topic.tex`. Detecting validation patterns shows whether the repo **guards handoffs** or blindly forwards state.

### Problem it addresses

- Next agent consumes unchecked output from the previous step
- No schema, type, or sanity checks on artifacts between stages
- Failures discovered late instead of at the gate

### Evidence in code (what to search for)

| Signal type | Examples |
|-------------|----------|
| Explicit checks | `if not`, `if ... is None`, `assert`, `raise ValueError`, `raise TypeError` |
| Validation libs | `pydantic`, `jsonschema`, `marshmallow`, `.validate(`, `ValidationError` |
| Gate language | `validate`, `validator`, `check_output`, `verify`, `schema`, `guard` in function names |
| Early return / block | `return` / `raise` before next agent or step when check fails |

### Detector v1 method

- **Primary:** regex for `\bassert\b`, `\braise\s+(ValueError|TypeError|ValidationError)`, `\bvalidate\w*\(`, `\bjsonschema\b`, `\bpydantic\b`
- **Secondary:** function names matching `validate_*`, `check_*`, `verify_*`
- **Context heuristic:** validation within N lines before a call that looks like handoff (`invoke`, `run`, `send`, `delegate`, `next_agent`)
- **Verdict:** `present` if ≥2 signals or 1 validation lib usage; `unclear` if only generic `if not`; `absent` if no checks in orchestration-heavy files

### Example pass

Before calling the next agent: `if not output.get("result"): raise ValueError("empty handoff payload")` or a Pydantic model validates the message.

### Example fail

Orchestrator passes `state["messages"]` directly to the next node with no checks on shape or required fields.

### Smell link

| Smell (`topic.tex`) | If PR8 absent / weak |
|---------------------|----------------------|
| Erroneous data propagates through the pipeline | Strong indicator |
| Inconsistent assumptions between agents | Supporting indicator |
| Validation gates missing in collaboration footprint | Direct footprint gap |

---

## B1 - Routing / handoff

**Source:** *Agentic Design Patterns*, Chapter 2 - **Routing** (delegate work to the right agent, tool, or sub-workflow).

### Why it matters

The **orchestration logic** slice of the collaboration footprint (`topic.tex` Phase 1) lives in routing: who runs next, how tasks are split, and how control passes between agents. Repos without explicit routing often hide ad-hoc `if/else` chains or single monolithic agents, which are harder to analyze and more prone to collaboration smells.

### Problem it addresses

- Unclear delegation boundaries between agents
- No explicit router / orchestrator component
- Handoffs implicit in shared state updates only

### Evidence in code (what to search for)

| Signal type | Examples |
|-------------|----------|
| Names | `Router`, `Orchestrator`, `Handoff`, `Delegate`, `Route` in classes/functions |
| Framework patterns | LangGraph `add_conditional_edges`, CrewAI `Process`, AutoGen `GroupChat`, `route` methods |
| Keywords | `handoff`, `delegate`, `routing`, `next_agent`, `assign_to`, `dispatch` |
| Control flow | Branch that selects among named agents or tools based on state / intent |

### Detector v1 method

- **Primary:** keyword scan (case-insensitive) for routing vocabulary in file path and content
- **Secondary:** class/function name patterns via regex `\b(Router|Orchestrat\w*|Handoff)\b`
- **Path boost:** filenames like `*router*`, `*orchestrat*`
- **Verdict:** `present` if named component or ≥3 routing keywords; `unclear` if only generic `if/else`; `absent` if no routing signals in an orchestration candidate file

### Example pass

An `OrchestratorAgent` class with `route(task) -> Agent` or explicit `handoff(to="researcher", payload=...)`.

### Example fail

Single `main()` calls one LLM in a loop with no delegation or agent selection logic.

### Smell link

| Smell (`topic.tex`) | If B1 absent / weak |
|---------------------|---------------------|
| Circular dependencies in agent planning | Supporting - routing clarity helps analysis |
| Collaboration footprint incomplete | Direct - orchestration logic not surfaced |
| Agents stuck in reasoning loops | Supporting - explicit routing can limit loops |

---

## PR6 - Selection / promotion (quality gates)

**Source:** Ntentos & Zdun - PR6 (automated selection / promotion). In agentic terms: **only promote or continue when a metric or check passes**.

### Why it matters

Quality gates differ slightly from PR8: PR8 is “is this artifact valid before the next step?” PR6 is “does this candidate **meet a bar** (metric, threshold, test) before we **select or promote** it?” In multi-agent setups this appears as choosing the best draft, passing an eval score, or blocking pipeline progress until KPIs are met. This ties to **collaboration quality** and measurable goals (`topic.tex` smells around weak KPIs / goal models).

### Problem it addresses

- Every agent output treated equally; no selection among alternatives
- Pipeline never blocks on quality metrics
- Hard-coded flows with no promotion logic

### Evidence in code (what to search for)

| Signal type | Examples |
|-------------|----------|
| Thresholds | comparisons with `threshold`, `min_score`, `>=`, `best_score`, `top_k` |
| Selection | `max(`, `argmax`, `select`, `promote`, `rank`, `choose_best` |
| Metrics | `accuracy`, `score`, `metric`, `evaluate`, `pass` / `fail` branches |
| Gate + block | `if score < ...: return` / `continue` / `raise` before next stage |

### Detector v1 method

- **Primary:** regex for `\b(threshold|min_score|best_score|promote|select_best)\b`, metric comparisons before continue/next step
- **Secondary:** eval hooks - `evaluate(`, `compute_metric`, integration with `wandb` / custom eval
- **Verdict:** `present` if threshold + branch blocks progress; `unclear` if metrics logged but not gating; `absent` if no selection/promotion patterns

### Example pass

`if eval_result.score >= PROMOTION_THRESHOLD: registry.promote(model_id) else: log rejection`.

### Example fail

Training or agent loop always proceeds to the next epoch/agent regardless of validation metrics.

### Smell link

| Smell (`topic.tex`) | If PR6 absent / weak |
|---------------------|----------------------|
| Hard-coded prompts lacking measurable KPIs | Supporting indicator |
| Agent actions diverge from intended goal | Supporting - no quality bar enforced |
| Compounding errors | Supporting - bad outputs not filtered early |

---

## B5 - Tool use / tool boundaries

**Source:** *Agentic Design Patterns*, Chapter 5 - **Tool Use** (agents call external functions with clear boundaries).

### Why it matters

Tool use is where agents **act** on the world and where collaboration often breaks (wrong args, silent failures, no logging). Explicit tool registration and decorators mark **boundaries** between LLM reasoning and side effects, which matters for footprint analysis of **communication channels** and tool-call observability (pairs with PR2).

### Problem it addresses

- Tools invoked ad hoc without registration or schema
- No clear separation between agent logic and external calls
- Hard to trace which agent invoked which tool

### Evidence in code (what to search for)

| Signal type | Examples |
|-------------|----------|
| Decorators | `@tool`, `@function_tool`, `@mcp.tool`, `@staticmethod` tool defs |
| Framework APIs | `bind_tools`, `StructuredTool`, `ToolNode`, `register_tool`, `tools=[...]` |
| Schemas | function docstrings used as tool description, `args_schema`, JSON schema for tools |
| MCP | `FastMCP`, `mcp.server`, tool registration in server modules |

### Detector v1 method

- **Primary:** regex for `@tool\b`, `bind_tools`, `StructuredTool`, `register_tool`, `FastMCP`
- **Secondary:** functions passed in a `tools=` list to an agent constructor
- **Verdict:** `present` if ≥1 explicit tool pattern; `unclear` if raw API calls only; `absent` if no tool boundary markers in agent-facing modules

### Example pass

`@tool`-decorated function registered on an agent via `tools=[search_docs]`, with a schema or docstring describing arguments.

### Example fail

Agent code uses `requests.get` inline inside a prompt loop with no tool abstraction or registration.

### Smell link

| Smell (`topic.tex`) | If B5 absent / weak |
|---------------------|---------------------|
| Missing observability for tool calls | Often co-occurring with weak PR2 |
| Unsafe or unbounded agent actions | Supporting - no structured tool boundary |
| Collaboration footprint (communication) incomplete | Tools are a primary channel |

---

## Cross-rule map: footprint ↔ practices

| Footprint element (`topic.tex`) | Primary rules |
|---------------------------------|---------------|
| Orchestration logic | B1, PR6 |
| Communication channels | B5, PR2 |
| Validation gates | PR8, PR6 |

| Smell (`topic.tex`) | Rules that help detect the *abs/indicator* side |
|---------------------|--------------------------------------------------------|
| Missing observability / traces | PR2, B5 |
| Erroneous data propagates | PR8, PR6 |
| Impossible to debug decisions | PR2 |
| Weak KPIs / goal models | PR6 |
| Orchestration unclear | B1 |

---

## Detection report shape (planned)

Each file × rule entry in the JSON report:

```json
{
  "rule_id": "PR2",
  "path": "src/agents/orchestrator.py",
  "verdict": "present",
  "confidence": "high",
  "evidence": [
    {"line": 42, "snippet": "logger.info(\"handoff\", extra={\"to_agent\": name})"}
  ]
}
```

Verdicts: `present` | `absent` | `unclear`. Confidence: `high` | `medium` | `low` (v1 mostly rule-count heuristics).

---

## Relation to the current prototype

- **File selection** (implemented): `insight_proto.tools.file_selection` - scan, categorize, rank, exclude.
- **Entry points:** orchestrator (`run_file_selection`), MCP tools, CLI external scan.
- **Detectors** (implemented): `insight_proto.detectors` (PR2, PR8, B1) on `ml_ranked` paths via `run_detection(...)`.

Optional later: LLM pass on ambiguous files only, not part of v1.

---

## Open questions

1. **PR6 vs B5 priority:** keep both in v1, or implement PR6 after PR2/PR8/B1 stabilize?
2. **PR2 strictness:** count any `logging` call, or require structured / step-level logs?
3. **PR8 vs PR6 overlap:** document as separate gates (validity vs promotion) or merge heuristics in code?
4. **Book patterns:** add Ch. 7 (Multi-Agent) later as **B7**, or is B1 + B5 enough for orchestration footprint?

---

Last updated: 2026-05-23 - first batch finalized (PR2, PR8, B1, PR6, B5).
