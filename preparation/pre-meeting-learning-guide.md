# What to understand before the supervisor meeting (April 7)

**Paths:** This file is in **`preparation/`**. The primer and related `.md` files use **same-folder** names; [`../resourses/topic.tex`](../resourses/topic.tex) is at repo root under `resourses/`.

This guide answers: **Is [`agentic-ai-and-rl-primer.md`](agentic-ai-and-rl-primer.md) enough?**  
**No** — it is **general background**. After your professor’s email, he expects you to **engage with his materials** (especially the **RL + agentic architecture paper** and **`topic.tex`**), not only generic concepts.

Use this file as your **checklist**. Tick boxes when done.

---

## 1. Three layers of knowledge (all three matter)

| Layer | Source | Purpose |
|-------|--------|---------|
| **A. General concepts** | `agentic-ai-and-rl-primer.md` | Vocabulary: agents, agentic AI, RL vs prompting, multi-agent collaboration, ReAct, survey pointers. |
| **B. His research line** | `resourses/Agentic_AI_Architecture_for_Evaluating_and_Improving_Reinforcement_Learning_Pipelines-2.pdf` (18 pp.) | **What his group actually builds**: multi-LLM pipeline, practices catalog, validation gates, evaluation. **Highest priority after the primer.** |
| **C. Your thesis direction** | `resourses/topic.tex` | **Your** phases: collaboration footprint → smells → detector agent. You must **not** confuse this with “only RL pipelines” — know the **similarity and difference**. |

**Optional / reference:** `resourses/Agentic_Design_Patterns.pdf` — large book; **do not read cover-to-cover** before the meeting. Skim **TOC** + any section on **orchestration / multi-agent** if time.

---

## 2. What the primer already gives you (sufficient for “A”)

After reading the primer, you should be able to explain in **your own words**:

- [ ] What an **agent** is (perceive → act → goal).  
- [ ] What **agentic AI** usually means today (tools, loops, planning, memory; **not** always RL).  
- [ ] **RL** in one paragraph (reward, policy, environment; where it touches LLMs, e.g. RLHF).  
- [ ] **Multi-agent** vs **single** LLM; **collaboration** (messages, shared state, orchestration).  
- [ ] That **ReAct** is an example of reasoning + acting (name only is fine).

**You do not need** to master Sutton & Barto or MARL theory **before April 7** unless your advisor already said RL theory is the focus — your `topic.tex` is heavier on **repos, smells, mining** than on RL math.

---

## 3. What you must add beyond the primer (“B” — the paper)

Read the **18-page paper** completely. Before the meeting you should understand:

### 3.1 Problem and setting

- [ ] **Why** RL pipelines need lifecycle practices (versioning, registry, evaluation, deployment, retraining) — not only algorithm quality.  
- [ ] Why **static/heuristic-only** tools are **insufficient** when practices span **code + config + CI/CD + infra**.

### 3.2 Their solution (agentic architecture)

- [ ] They use **multiple specialized LLM-based agents** (e.g. roles like file selection, **detection**, fix suggestion, **code generation** — exact names from the paper).  
- [ ] **Orchestration** + **automated validation gates** between steps.  
- [ ] Goal: detect **missing or weak** lifecycle **practices**, suggest or apply fixes, with evidence and human oversight where needed.

### 3.3 Research questions and contributions

- [ ] **RQ1** (roughly): How well can the system **recognize compliance** with practices, including **distributed** evidence across files?  
- [ ] **RQ2** (roughly): How well can it **suggest/apply corrections**?  
- [ ] **Contributions:** architecture + **catalog of practices** (they use **15** in the paper) + **empirical evaluation** (case studies / repos).

### 3.4 Evaluation (high level)

- [ ] They report things like **detection performance** (e.g. F1) and **quality of generated artifacts** — you don’t need to memorize numbers, but know **what** was measured.

### 3.5 Connection to YOUR topic (critical)

Be able to say **one short paragraph**:

- **Same idea:** specialized agents, orchestration, **validation gates**, analyzing **real repositories**, **catalog** of issues/practices, **empirical** evaluation.  
- **Different focus:** their paper targets **RL training/deployment lifecycle** practices; your `topic.tex` targets **agentic / multi-agent application architectures**, **collaboration footprint**, and **smells** (compounding errors, shared state, observability, loops, …).

If you only know the primer and **not** this distinction, the meeting will feel shallow.

---

## 4. What you must know from `topic.tex` (“C”)

- [ ] **Phase 1:** **>100 repos**, heterogeneous (e.g. CrewAI, LangGraph, ROS agents); extract **orchestration**, **communication channels**, **validation gates** = “collaboration footprint.”  
- [ ] **Phase 2:** **Smells** — the list in `topic.tex` (compounding errors, shared mutation without locks, missing traces, planning cycles, hard-coded prompts without KPIs, goal drift, …).  
- [ ] **Phase 3:** **Detector** built with an **agentic framework** to find **indicators** of smells — **your file stops here**; it’s OK to say you will **define evaluation and scope** with him.

---

## 5. What your professor likely expects (realistic bar)

| Expectation | “Enough” looks like |
|-------------|---------------------|
| You read **his paper** | You can summarize problem, agent roles, gates, RQs in **5 minutes**. |
| You understood **your topic** | You can walk through **3 phases** and **one example smell**. |
| You connected A + B + C | You can state **overlap vs difference** (section 3.5 above). |
| You prepared **next steps** | You have **questions** about scope (corpus size, evaluation) — see `meeting-prep-april-7.md`. |

He does **not** need you to be an RL researcher in week one — he needs **engagement with the materials he sent**.

---

## 6. Suggested study order (time-boxed)

1. **45–60 min:** Re-skim `agentic-ai-and-rl-primer.md` (refresh).  
2. **2–3 hours:** Read the **18-page PDF** once carefully; take **half a page of notes** (RQs, figure of pipeline, 3 contributions).  
3. **30 min:** Re-read `topic.tex`; write **5 bullets**: what you will **mine**, what you will **detect**, what is **open**.  
4. **30 min (optional):** Open `Agentic_Design_Patterns.pdf` → **table of contents only**; bookmark 1–2 chapters for later.  
5. **30 min:** Fill `meeting-prep-april-7.md` (questions + risks).

---

## 7. File map

| File | Role for this meeting |
|------|-------------------------|
| [`agentic-ai-and-rl-primer.md`](agentic-ai-and-rl-primer.md) | Concepts only — **not** sufficient alone. |
| `Agentic_AI_Architecture_..._Pipelines-2.pdf` | **Core** — must read. |
| `topic.tex` | **Core** — your thesis contract. |
| `Agentic_Design_Patterns.pdf` | **Optional** skim. |
| [`meeting-prep-april-7.md`](meeting-prep-april-7.md) | Questions + checklist. |
| [`meeting-prep-integrated-april-7.md`](meeting-prep-integrated-april-7.md) | Full integrated brief. |
| `pre-meeting-learning-guide.md` | **This file** — what “done” means. |

---

*If something in the paper is hard (e.g. a figure), note the **page number** and ask your professor — that counts as good preparation.*
