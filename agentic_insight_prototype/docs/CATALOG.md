# Practice catalog

This file is a **working list**: which lifecycle / agentic practices matter for the thesis, where they come from (paper, book, topic notes), and what kind of **code evidence** we would look for later. Nothing here is enforced by the code yet; the prototype currently stops at **file selection**. Detection for these rows comes in a later milestone.


---

## Baseline: PR1–PR15 (Ntentos & Zdun)

The paper defines fifteen RL pipeline practices (metadata, logging, registry, evaluation, validation gates, rollback, staging environments, and so on).

---

## First batch to implement after file selection

The rows below are the first slice we want to **detect in code** once the catalog is stable. They line up with multi-agent concerns (observability, gates, routing) and with the directions in `resourses/topic.tex` (orchestration, validation gates, traces).

| ID | Practice | Source                                       | What we would look for in code | Status |
|----|----------|----------------------------------------------|--------------------------------|--------|
| PR2 | Runtime logs / traces | Dr.Ntentos & Prof.Zdun                       | Logging around steps, tool calls, handoffs; structured trace fields | planned |
| PR6 | Selection / promotion (quality gates) | Dr.Ntentos & Prof.Zdun                       | Branches that block the next stage until a metric or check passes | planned |
| PR8 | Validation between stages | Dr.Ntentos & Prof.Zdun                       | Explicit checks on outputs or artifacts before the next agent or step runs | planned |
| B1 | Routing / handoff | Agentic Design Patterns, Chapter 2 (Routing) | Router/supervisor component, explicit delegation, tool routing, handoff payloads | planned |

B1 can be swapped for another book pattern (for example planning or memory) if a different chapter fits better.

---

## Relation to the current prototype

File selection is implemented in `insight_proto.tools.file_selection` and exposed as MCP tools (`scan_repository`, `categorize_files`, `filter_ml_relevant_files`). The catalog above defines **what we analyze next**, on the paths those tools return.

Optional later: a second pass with an LLM to shorten the candidate list; not part of the current code path.

---

Last updated: we will keep this file in sync when the first four rows are finalized or replaced.
