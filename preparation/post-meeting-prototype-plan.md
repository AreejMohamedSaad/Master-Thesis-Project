# Post-meeting plan — prototype (supervisor agreement)

**Context:** Follow-up after the first supervisor meeting. The transcript was noisy; this document aligns with **`agentic_insight_prototype/README.md`** in the repo root.

---

## Agreed first milestone

1. **Custom orchestrator** (no LangGraph/CrewAI as the base — understand your own flow first).  
2. **MCP server** exposing **tools**; **MCP client** to test from outside.  
3. **File-selection** focus: multiple tools (repo scan, **categorize**, heuristics / keywords for ML-relevant imports, optional LLM pass with explicit instructions).  
4. **Catalog:** extend paper **15 PR** with **book** (+ other sources); pick **3–4** simpler practices to implement **after** file selection.  
5. **Document** evidence per practice (how it shows up in code) for later **smell** work.  
6. **Memory:** research + simple implementation (state, short vs long — see `agentic_insight_prototype/docs/MEMORY_NOTES.md`).  
7. **Validation gates:** later (like AVA in the paper), not blocking the first slice.

---

## Explicit non-goals (for now)

- Do **not** anchor v1 on LangGraph or CrewAI **as the orchestration framework**.  
- Do **not** analyze the whole repo with an LLM — **select files first**.

---

## Logistics

- **Progress reports** ~every 2 weeks.  
- **Next meeting:** ~**3 weeks** after the last, **1 PM** (confirm **27 April / 4 May** week).  
- **GitLab/Git:** document from the start; branch/repo for prototype + thesis notes.

---

## Where the code lives

| Path | Role |
|------|------|
| [`../agentic_insight_prototype/`](../agentic_insight_prototype/) | Prototype repo folder |
| [`../agentic_insight_prototype/README.md`](../agentic_insight_prototype/README.md) | Full charter + directory layout |

---

*This file is the preparation-folder pointer; the executable plan lives next to the code.*
