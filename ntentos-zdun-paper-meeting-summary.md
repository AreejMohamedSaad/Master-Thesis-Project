# Ntentos & Zdun (2026) — meeting cheat sheet

**Full title:** *Agentic AI Architecture for Evaluating and Improving Reinforcement Learning Pipelines*  
**Authors:** Evangelos Ntentos, Uwe Zdun (University of Vienna, Software Architecture group)  
**Length:** 18 pages (ACM manuscript)  
**Artifact:** Tool on Zenodo — DOI in paper: `10.5281/zenodo.17422753`

---

## Half-page summary (bullets you can bring on one sheet)

### Problem

- RL systems are used in safety-sensitive settings (robotics, industry, vehicles). **Reliability** depends on **lifecycle engineering** (versioning, registry, evaluation, deployment, retraining, rollback), not only on algorithms.
- Those practices are often **spread across** Python code, configs, **CI/CD**, Kubernetes/Helm, etc. **Static rules** catch simple patterns but miss **cross-file**, **cross-format**, or **implicit** implementations.

### Idea

- An **agentic AI architecture**: several **specialized LLM-based agents** plus **orchestration** and **validation gates** to check RL pipelines against a **catalog of 15 practices** (PR1–PR15: metadata, logging, registry, pinned loading, evaluation, rollback, retraining triggers, staging, canary/A/B, etc.—see Table 1 in the paper).

### Agent roles (core four + two controllers)

- **File Selection Agent** — finds relevant source/config files.  
- **Detection Agent** — judges whether a practice is present (with evidence).  
- **Fix Suggestion Agent** — proposes corrections when something is missing.  
- **Code Generation Agent** — produces patches; can escalate to **human** review.  
- **Collaboration Protocol Agent (CPA)** — orchestrates the workflow **without** editing code: sequences **Select → Detect → Suggest → Generate**, issues **continue / retry / succeed / fail**.  
- **Automated Validation Agent (AVA)** — **non-LLM** structural checks at **gates** (file type, evidence, syntax, linter, etc.).

### Technical glue

- **Model Context Protocol (MCP)** for standardized context and messaging; **shared context store**; **event bus**; compliance reports (e.g. structured JSON).

### Research questions

- **RQ1:** To what extent can this system **recognize** compliance with lifecycle practices when evidence is **distributed** (code + infra + CI/CD)?  
- **RQ2:** How effectively can it **suggest and apply** corrections?

### Contributions (paper’s own list)

1. Agentic **evaluation + correction** architecture for RL lifecycle (specialized agents + gates + human oversight).  
2. **Catalog of 15** architectural practices for RL model versioning and lifecycle.  
3. **Empirical evaluation:** one **industrial** cyber-physical / production-automation case + **five open-source** RL repos (diverse styles).

### Results (abstract-level — verify exact wording in your copy)

- **Detection:** overall **F1 ≈ 0.80** (practice identification vs manual ground truth).  
- **Generation:** mean **quality score ≈ 2.40** on their ordinal scale (GQS: higher = better usable artifacts; Table 3 defines levels 1–4).

### Limitations / threats (good to mention in discussion)

- Depends on **LLM** quality and cost; evaluation used a specific **GPT-4o** snapshot for consistency.  
- Open-source cases **vary** in complexity vs industrial polyglot systems.  
- **Ground truth** required **manual** annotation of practices.

### One line: link to *your* thesis (`topic.tex`)

- **Same structure:** multi-agent LLM pipeline, **gates**, **catalog** of issues, **repos**, **empirical** evaluation.  
- **Different target:** this paper = **RL training/MLOps lifecycle** practices; your work = **collaboration footprint** and **architecture smells** in **agentic / multi-agent LLM** systems (CrewAI, LangGraph, …).

---

## ~2-minute spoken pitch (read aloud: about 240–280 words)

You can shorten the first paragraph if time is tight.

---

I read the paper *Agentic AI Architecture for Evaluating and Improving Reinforcement Learning Pipelines* by Ntentos and Zdun from your group.

The motivation is that reinforcement learning is not only about algorithms: in production, **model lifecycle** matters—registry, versioning, evaluation before promotion, retraining triggers, rollbacks, and so on. Those practices are often split across code, configuration, and CI/CD, so simple static checks miss many real gaps.

The authors propose a **multi-agent LLM system**. Four main agents **select files**, **detect** whether each best practice is implemented, **suggest** fixes, and **generate** patches. A **Collaboration Protocol Agent** orchestrates the pipeline in stages, and an **Automated Validation Agent** runs **validation gates** after each stage—so the workflow is deterministic and traceable, not one unconstrained chat. They use **fifteen** concrete practices, things like structured logging, centralized registry, pinned model loading, and safe deployment patterns.

They evaluate on an **industrial** RL platform and **five open-source** repositories, with **manual ground truth** for detection and a **quality score** for generated code. The reported **overall F1** for detection is around **0.8**, and the **mean generation quality** is about **2.4** on their scale—so the system is shown to find missing practices and produce usable fixes at scale.

For **my** thesis, I see the **same architectural idea**: specialized agents, orchestration, gates, and a catalog of rules—applied not to RL MLOps alone, but to **mining open-source agentic systems** for a **collaboration footprint** and **smells**, with a **detector** phase we still need to define precisely. I’d like to align scope and milestones with you—especially how large the repository study should be and how we evaluate Phase three.

---

## Timing tip

- **2 minutes** ≈ 240–270 words at a calm pace.  
- If you only have **1 minute**, say: **problem** (lifecycle scattered) → **solution** (4 agents + CPA + AVA + 15 practices) → **one result** (F1 / quality) → **your twist** (collaboration footprint + smells).

---

*Use together with `pre-meeting-learning-guide.md` and `meeting-prep-april-7.md`.*
