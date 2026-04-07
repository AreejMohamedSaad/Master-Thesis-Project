# Master thesis: full execution plan

This document merges **Topic.pdf** (official thesis framing), **`resourses/topic.tex`** (three-phase technical plan), and the **lab paper** on agentic evaluation of RL pipelines (methodological reference). Use it as your **single roadmap**; adjust dates and scope with your supervisor.

---

## Part A. What your thesis is (single narrative)

### A.1 Official objective (from Topic.pdf)

You design an **Agentic AI Collaboration Insight as a Service** architecture that:

- **Captures, analyzes, and evaluates** collaboration among **multiple AI agents** and their **pipelines**.
- Combines **interaction patterns**, **coordination mechanisms**, and **anti-patterns** into a **holistic** view of quality and effectiveness.
- Focuses on **structure, coordination, and governance** of the **system**, not on grading **one** agent in isolation.

**Deliverables implied by Topic.pdf**

1. **Systematic literature / practice review** of collaboration patterns, coordination strategies, and anti-patterns (agentic AI, multi-agent, LLM frameworks, autonomous workflows).  
2. **Collaboration indicators** (e.g. role clarity, delegation, protocols, handoffs, conflict handling, human-in-the-loop).  
3. **Architecture** for an **insight-as-a-service** model (analysis + structured feedback on quality, risks, improvements).  
4. **Prototype** that analyzes **real** agentic pipelines and produces **scalable, reusable** collaboration insights.

### A.2 Technical backbone (from `topic.tex`)

Your supervisor’s phased plan operationalizes the abstract goal:

| Phase | Goal |
|-------|------|
| **Phase 1** | **Collaboration footprint:** build a **corpus** (target **>100** open-source repos) of agentic / multi-agent / LLM pipelines; **mine artifacts** beyond raw code: **orchestration**, **communication channels**, **validation gates**. |
| **Phase 2** | **Smells / mining:** detect **bad patterns** (compounding errors, unsafe shared state, missing observability, planning cycles, weak prompts/KPIs, goal drift, …). |
| **Phase 3** | **Agentic detector:** configure a **detector** using an **agentic framework** to search for **indicators** of those smells (and, in the full thesis story, feed the **insight service**). |

### A.3 Methodological reference (lab paper, not your topic copy)

**Ntentos & Zdun**, *Agentic AI Architecture for Evaluating and Improving Reinforcement Learning Pipelines*: specialized LLM agents, **orchestration** (CPA), **validation gates** (AVA), **catalog** of practices, **empirical** evaluation on repositories.  

**Parallel:** multi-agent pipeline + catalog + gates + repos.  

**Different:** their **domain** is **RL MLOps lifecycle** (15 practices PR1–PR15); yours is **agentic collaboration footprint + smells** in **general** multi-agent LLM systems (CrewAI, LangGraph, ROS agents, etc.). Your thesis **extends the “analyze real codebases with agentic AI” idea** into **collaboration quality**, not replacing their RL contribution.

### A.4 Explicit mapping from `resourses/topic.tex`

Everything below is taken from your supervisor’s `topic.tex` and wired into **Part C** of this document.

| Content in `topic.tex` | Where it lives in this plan |
|------------------------|-----------------------------|
| **Phase 1 — Collaboration footprint** | **Part C → Phase 2** (corpus + footprint extraction): heterogeneous repos, **>100** target, frameworks (CrewAI, LangGraph, ROS agents). |
| **Artifact harvesting** (not “code only”) | Phase 2 steps **2.2–2.5**: orchestration, channels, gates as **first-class** extracted artifacts. |
| **Orchestration logic** (Supervisor, Handoff, Process) | Phase 2 **footprint** + Phase 3 **smell** context; detection design when orchestration is missing or tangled. |
| **Communication channels** (MessageQueue, SharedState, ContextStore) | Phase 2 **metadata + extraction**; Phase 3 smells around **shared state** and **race** conditions. |
| **Validation gates** (output checked before next agent) | Phase 2 footprint; Phase 4 **gates** in your own detector pipeline (same *engineering idea* as the lab paper’s AVA). |
| **Phase 2 — Smells (mining task)** | **Part C → Phase 3**: full **smell catalog** with definitions, baselines, ground truth. |
| **Listed smells** (compounding errors, direct mutation without locks, races, missing observability, debuggability, circular planning, reasoning loops, hard-coded prompts without KPIs, goal drift) | Phase 3 steps **3.1–3.2**; each smell gets a **detection strategy** (static / log / LLM). |
| **Phase 3 — Detector agent** | **Part C → Phase 4**: agentic framework, **selector / detector / reporter** roles, **Insight as a Service** prototype output. |
| *`topic.tex` stops after “indicators”* | **Part C Phase 4–5** and **Part G** add what is still open: **evaluation metrics**, thesis chapters, reproducibility—**confirm with your supervisor**. |

---

## Part B. Skills and requirements (from Topic.pdf)

Treat these as **throughout-thesis** competencies to demonstrate in the thesis text and prototype:

- **Python and Java** (backend and frontend as needed).  
- **Machine learning** and **reinforcement learning** (concepts; MARL only where your analysis touches it).  
- **Software architecture** patterns and practices.  
- **CI/CD** and **ML/RL pipelines** (MLOps / RLOps literacy).  
- **Large language models** (LLMs) and **agent frameworks**.

---

## Part C. End-to-end roadmap (phases with concrete steps)

### Phase 0: Setup and alignment (before heavy implementation)

**Purpose:** Lock scope, ethics, and tooling so later phases do not collapse under vague goals.

| Step | Action | Output |
|------|--------|--------|
| 0.1 | Re-read Topic.pdf, `topic.tex`, and the **18-page lab paper**; write **one page**: your contribution vs the lab paper. | Scope note |
| 0.2 | Meet supervisor: confirm **corpus size** (is **>100** repos mandatory or stretch?), **evaluation** criteria for Phase 3, **timeline**. | Agreed milestones |
| 0.3 | Choose **reference management** (Zotero, BibTeX, or JabRef) and **thesis template** (LaTeX via Overleaf or local; university template if required). | Bibliography workflow |
| 0.4 | Create **private GitHub repo** for thesis materials (you already have a script); branch strategy optional (`main` + `draft-chapters`). | Version-controlled workspace |
| 0.5 | **Ethics / data:** public GitHub code is generally OK to mine; document **licenses**, **no secrets** in cloned repos, **attribution** of frameworks. | Short ethics paragraph for thesis |

---

### Phase 1: Literature and systematic review (supports Topic.pdf “systematic review”)

**Purpose:** Ground your **indicators**, **smells**, and **architecture** in published and grey literature.

| Step | Action | Output |
|------|--------|--------|
| 1.1 | Define **search strategy** (keywords: multi-agent LLM, agentic AI, orchestration, LangGraph, CrewAI, observability, MLOps agents, MARL communication if relevant). | Search log |
| 1.2 | Collect **surveys** and **landmark papers** (e.g. Guo et al. LLM multi-agents survey; Plaat et al. agentic LLMs survey; design patterns PDF sections on orchestration). | Annotated bibliography |
| 1.3 | Synthesize **collaboration patterns** (hierarchical, peer-to-peer, hub-and-spoke, pipeline) and **anti-patterns** (unclear roles, chatty agents, no observability). | Literature chapter draft |
| 1.4 | Map patterns to **measurable indicators** (role overlap score, handoff count, message failure rate, etc.—align with your `collaboration-insight-thesis-foundation.md` if you use it). | Indicator table v1 |

**Collaboration tools for Phase 1**

- **Writing:** Overleaf (LaTeX) or Word/Google Docs per university rules.  
- **References:** Zotero + browser connector.  
- **Supervisor:** email + **shared calendar** for bi-weekly meetings; optional **shared folder** (university cloud, Google Drive, or private GitHub repo with `literature/` PDFs if license allows).  
- **Notes:** Obsidian, Notion, or Markdown in repo (`notes/literature/`).

---

### Phase 2: Corpus and “collaboration footprint” (Phase 1 of `topic.tex`)

**Purpose:** Build **evidence** from real systems—not only theory.

| Step | Action | Output |
|------|--------|--------|
| 2.1 | Define **inclusion criteria** (stars, last commit, language, uses LangGraph/CrewAI/AutoGen/ROS+LLM, etc.). | Corpus protocol (preregister if your chair likes it) |
| 2.2 | **Pilot:** manually analyze **5–10** repos; document **orchestration** (supervisor, graph, handoff), **channels** (queue, shared state, context store), **gates** (validation before next step). | Pilot spreadsheet + screenshots |
| 2.3 | Automate **cloning / listing** (Python scripts); store **metadata** (URL, commit hash, framework detected). | SQLite/CSV + scripts in repo |
| 2.4 | Scale toward **>100** repos **as agreed** with supervisor; track **failures** (empty agent code, only notebooks). | Corpus v1 |
| 2.5 | **Footprint extraction:** static analysis (AST, regex for class names), optional **LLM-assisted** labeling for ambiguous cases (document cost and bias). | Footprint dataset |

**Collaboration tools for Phase 2**

- **Code:** Git, GitHub (your private repo + **public** repos you clone locally—do not push third-party full clones into your repo unless license allows; prefer **URLs + commit hashes**).  
- **Tracking:** GitHub **Issues** or **Projects** for “repos screened / accepted / rejected”.  
- **Compute:** your machine or university VMs/GPU if you run LLM labeling at scale.

---

### Phase 3: Smell catalog and detection design (Phase 2 of `topic.tex`)

**Purpose:** Turn **Topic.pdf** “anti-patterns” + `topic.tex` list into **operational** rules or classifiers.

| Step | Action | Output |
|------|--------|--------|
| 3.1 | Finalize **smell definitions** with **examples** from your pilot (compounding errors, shared mutation without synchronization, missing traces, reasoning loops, hard-coded prompts without KPIs, goal drift, …). | Smell catalog (table: name, definition, example, severity) |
| 3.2 | For each smell, specify **detection strategy:** pure static, log pattern, graph analysis, or **LLM judge** (with prompt versioning). | Detection design doc |
| 3.3 | **Baseline:** simple static/heuristic detectors where possible (reproducible, cheap). | Baseline metrics |
| 3.4 | **Ground truth plan:** how you label a **subset** (you + rubric, or advisor spot-check)—needed to report **precision/recall** or qualitative agreement. | Annotation protocol |

---

### Phase 4: Agentic “Detector” and insight service (Phase 3 of `topic.tex` + Topic.pdf prototype)

**Purpose:** Implement the **agentic** pipeline that finds **indicators** and produces **structured insight** (the “as a service” core).

| Step | Action | Output |
|------|--------|--------|
| 4.1 | Choose **framework** (LangGraph, LangChain agents, AutoGen, CrewAI—align with corpus and your Java/Python skills; Java may back a **gateway** or **enterprise** demo if required). | Architecture diagram |
| 4.2 | Design **agents** by role (mirror lab paper: **selector** of files/snippets, **detector**, **explainer**, **report generator**; optional **fix suggester** if in scope). | Agent specification |
| 4.3 | Implement **orchestration** + **validation gates** (syntax checks, schema checks for JSON output—same *idea* as CPA/AVA in the lab paper). | Working pipeline |
| 4.4 | **API / CLI / small UI:** expose “analyze this repo path” and return **JSON report** (collaboration quality, risks, smells)—this is your **Insight as a Service** **prototype**. | Prototype + demo script |
| 4.5 | **Evaluate** against Phase 3 ground truth; compare to baseline. | Results chapter |

**Collaboration tools for Phase 4**

- **Pair programming / advisor code review:** GitHub **Pull Requests** on private repo.  
- **API docs:** OpenAPI/Swagger if you expose HTTP.  
- **Secrets:** never commit API keys; use `.env` + `.gitignore` (already partially set).

---

### Phase 5: Thesis writing and submission

| Step | Action | Output |
|------|--------|--------|
| 5.1 | **Chapter outline:** intro, related work, background (agents, RL/MARL as needed), corpus & footprint, smells, architecture, implementation, evaluation, threats to validity, ethics, conclusion. | `thesis/outline.md` or LaTeX `\include` files |
| 5.2 | **Figures:** corpus pipeline, footprint schema, detector architecture, example report. | Publication-ready figures |
| 5.3 | **Reproducibility:** README with how to run detectors, random seeds, LLM model names and versions. | README.md |
| 5.4 | **Review** with supervisor; incorporate feedback. | Final PDF |

---

## Part D. Tooling summary (what to use for what)

| Need | Suggested tools (pick what your university allows) |
|------|-----------------------------------------------------|
| Version control | **Git + GitHub** (private repo for thesis materials) |
| Writing thesis | **LaTeX/Overleaf** or Word; templates from faculty |
| References | **Zotero** or BibTeX |
| Literature notes | Markdown in repo, Obsidian, or Notion |
| Task tracking | GitHub **Issues/Projects**, or Trello, or paper backlog |
| Meetings with supervisor | Calendar invites; **agenda** + **notes** in `meetings/` folder |
| Agent framework for prototype | **LangGraph**, **LangChain**, **AutoGen**, or **CrewAI** (Python ecosystem strongest) |
| Java (if required by Topic.pdf) | Spring Boot or Quarkus for a **service façade** or **integration** component; or narrow scope to “Python prototype + Java case study” only if supervisor agrees |
| CI for your own code | **GitHub Actions** (lint, test, optional Docker) |
| Optional collaboration with peers | **GitHub** team repo, **Discord/Slack** (informal) |

---

## Part E. Mapping documents in your folder

These Markdown files are expected under **`preparation/`** (paths below are sibling filenames). Thesis repo root uses **`../`** (e.g. [`../resourses/topic.tex`](../resourses/topic.tex)).

| Asset | Role in the plan |
|-------|------------------|
| **Topic.pdf** (often repo root: [`../Topic.pdf`](../Topic.pdf)) | Official **objective**, **approach** bullets, **requirements**, **prototype** expectation |
| **[`resourses/topic.tex`](../resourses/topic.tex)** | **Three-phase** technical spine (footprint → smells → detector) |
| **Lab paper (RL pipelines)** (e.g. in `resourses/`) | **Method** reference: agents, gates, catalog, evaluation discipline |
| **[`agentic-ai-and-rl-primer.md`](agentic-ai-and-rl-primer.md)** | **Concepts** for writing background chapters |
| **[`collaboration-insight-thesis-foundation.md`](collaboration-insight-thesis-foundation.md)** | Optional extended notes on metrics and architecture |
| **[`ntentos-zdun-paper-meeting-summary.md`](ntentos-zdun-paper-meeting-summary.md)** | Short summary of lab paper for discussions |
| **[`pre-meeting-learning-guide.md`](pre-meeting-learning-guide.md)**, **[`meeting-prep-april-7.md`](meeting-prep-april-7.md)** | Prep checklists (update dates per meeting) |
| **[`meeting-prep-integrated-april-7.md`](meeting-prep-integrated-april-7.md)** | Full supervisor-meeting cheat sheet |

---

## Part F. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| **>100 repos** too heavy | Agree **minimum viable corpus** early; use **stratified sampling** (frameworks, sizes). |
| **LLM costs** for detection | Budget runs; cache outputs; small models for triage; report **cost per repo**. |
| **Subjective smells** | Ground truth rubric, **inter-rater** sample, **qualitative** examples in appendix. |
| **Scope creep** (“Insight as a Service” becomes full cloud product) | Bound prototype: **CLI/API + JSON report + one dashboard page** may be enough. |
| **Parallelism with lab paper** | One paragraph in thesis: **same orchestration philosophy**, **different domain and smell catalog**. |

---

## Part G. What to do next (order of operations)

1. **Confirm with supervisor** corpus size, evaluation, and Java vs Python emphasis.  
2. **Freeze** Phase 1 literature search protocol and Phase 2 inclusion criteria.  
3. **Run pilot** on 5–10 repos and **write up footprint + smells** with real examples.  
4. **Implement** baseline detectors, then **agentic detector**, then **evaluation**.  
5. **Draft thesis chapters** in parallel with implementation (do not leave all writing to the end).

---

## Part H. Version history

| Version | Date | Note |
|---------|------|------|
| 1.0 | 2026-03-28 | Initial full plan from Topic.pdf, `topic.tex`, and shared resources |
| 1.1 | 2026-03-28 | Added **A.4** — explicit line-by-line mapping from `resourses/topic.tex` |

---

*This plan is a living document: after each supervisor meeting, add a short **“Decisions log”** section at the bottom with dates and agreed changes.*
