# Primer: Agentic AI, Agents, and Reinforcement Learning

This note is a **conceptual map** for thesis preparation: what people mean by *agentic AI*, **collaboration between agents**, how that relates to classical *intelligent agents*, and where **reinforcement learning (RL)** fits. It ends with a **short reading list** (surveys, a textbook chapter path, and landmark papers).

> **Note:** Your file `Topic.pdf` was not found in this project folder. Once you add it (or paste the official title), you can map sections below directly to your supervisor’s wording.

---

## 1. What is an “agent” in AI?

In AI textbooks, an **agent** is anything that **perceives** an environment and **acts** in it to achieve a goal. A minimal picture:

- **Perception:** observations (sensor readings, API responses, text from a user).
- **Action:** moves in the world (clicking, calling a tool, sending a command to a robot).
- **Policy / controller:** the rule that chooses actions given what was perceived.
- **Objective:** what “good” means (explicit reward, implicit preference, task success).

Russell & Norvig’s *Artificial Intelligence: A Modern Approach* is the standard place for this framing (agents, environments, rationality). See the latest edition from Pearson / associated resources for your university’s version.

---

## 2. What is “agentic AI” (today’s usage)?

**Agentic AI** usually refers to systems built around **large language models (LLMs)** or other foundation models that do **more than one-shot text generation**. Typical ingredients:

| Idea | Plain-language meaning |
|------|-------------------------|
| **Tool use** | The model decides *when* to call an external function (search, calculator, database, code execution) and *with what arguments*. |
| **Planning / decomposition** | Breaking a user goal into steps, revising the plan when something fails. |
| **Memory** | Storing notes, retrieval over documents (RAG), or a scratchpad across turns. |
| **Reflection** | Critiquing its own draft answer or trajectory and trying again. |
| **Multi-agent setups** | Several LLM-based processes (or specialized bots) coordinate, debate, or hand off subtasks. |

So “agentic” emphasizes **closed loops**: *think → act → observe → update*, not only *prompt → answer*.

A concrete early pattern for that loop is **ReAct** (reasoning traces interleaved with actions). See Section 6.

**Important distinction:** *Agentic* does **not** automatically mean “uses reinforcement learning.” Many deployed agents are mostly **prompted** or **fine-tuned** with supervised data; RL enters mainly when you want **learning from interaction or human feedback** at scale (Section 5).

---

## 3. Collaboration between agents and “collaborative agentic AI”

The first version of this primer only **mentioned** multi-agent setups in passing. This section spells out what **collaboration between AI agents** means here, and what people often intend by **collaborative agentic AI**.

### 3.1 When is it “multi-agent”?

You have a **multi-agent** setup when **more than one agent** (each with its own role, policy, or LLM instance) **shares a task or environment** and **influences each other** through **communication or shared state**—not when a single model silently talks to itself in one chain-of-thought.

Typical building blocks:

- **Message passing:** agents read each other’s **natural-language** (or structured) outputs: proposals, critiques, summaries, votes.
- **Shared artifacts:** a common **whiteboard** (file, database, ticket queue) that several agents read and update.
- **Orchestration:** a **meta-controller** or workflow engine decides which agent runs next (like a project manager), versus **peer** agents negotiating turns.
- **Division of labor:** different **profiles** (researcher, coder, reviewer, “user proxy”) each specialized by **prompt**, **tools**, or **fine-tuning**.

Classical **multi-agent systems** (game theory, distributed AI, robotics teams) studied incentives, coordination protocols, and emergent behavior long before LLMs; today’s **LLM-based multi-agent** work reuses those ideas with **language** as the main coordination interface. A dedicated survey is Guo et al. (Section 7.4).

### 3.2 What counts as “collaboration”?

**Collaboration** means agents **jointly** advance a goal in a way that **depends on mutual information**: one agent’s output **changes** what another does next. Mere **pipelines** (Agent A always hands a file to B with no feedback loop) are weakly collaborative; **loops** (A drafts, B criticizes, A revises) are strongly collaborative.

Common patterns in research and products:

| Pattern | Idea |
|--------|------|
| **Debate / critique** | One agent argues or checks another; reduces single-model blind spots. |
| **Handoff workflow** | Specialized sub-agents for search, coding, testing; explicit state handover. |
| **Committee or voting** | Several agents propose answers; aggregation or discussion picks the outcome. |
| **Human in the loop** | People and agents collaborate; the human approves tools or plans. |

### 3.3 “Collaborative agentic AI” (terminology)

**Collaborative agentic AI** is not a single formal standard; in papers and grant language it usually means:

1. **Agentic** (Section 2): steps, tools, memory, planning—not one-shot generation.  
2. **Collaborative**: **multiple** such agents (and sometimes humans) **coordinate** toward one **shared objective** (write software, analyze a policy, run a simulation).

So: **collaborative agentic AI** = **multi-agent systems built from agentic LLM (or hybrid) components**, emphasizing **coordination and joint problem solving** rather than a lone autonomous bot.

**Contrast with “single agentic AI”:** one LLM agent with tools serving one user thread—still agentic, but not *collaborative* in the multi-party sense.

### 3.4 Challenges you will see in the literature

- **Communication cost and noise:** long message chains drift; agents **misunderstand** each other or **hallucinate** shared facts.  
- **Credit assignment:** who caused success or failure when many agents contributed?  
- **Safety and control:** tool access multiplied across agents; **conflicting** sub-goals.  
- **Evaluation:** harder than single-agent benchmarks; need **protocols** and **interaction traces**.

Plaat et al. treat **interaction** (including multi-agent themes) as one pillar of agentic LLM research; Guo et al. survey **LLM-based multi-agent** systems specifically (domains, communication, benchmarks).

---

## 4. Reinforcement learning (RL) in one pass

RL studies **sequential decision making under uncertainty**. The usual formalism is a **Markov decision process (MDP)**:

- States \(s\), actions \(a\), transitions \(P(s' \mid s, a)\), rewards \(R(s, a, s')\).
- A **policy** \(\pi(a \mid s)\) chooses actions.
- The agent seeks to maximize **expected cumulative (discounted) reward**.

Core concepts you will see in every RL thesis or paper:

- **Exploration vs. exploitation:** trying new actions vs. repeating what already pays off.
- **Value functions:** how good it is to be in a state (or take an action there).
- **Policy gradients / actor–critic:** directly optimizing a parameterized policy.
- **Function approximation & deep RL:** neural nets represent values or policies (used in robotics, games, recommender-style bandits, etc.).

The standard free textbook is Sutton & Barto, *Reinforcement Learning: An Introduction* (2nd ed., 2018). The authors host the PDF and teaching materials here: [http://www.incompleteideas.net/book/the-book-2nd.html](http://www.incompleteideas.net/book/the-book-2nd.html)

---

## 5. Where RL meets LLMs and “agentic” systems

These connections are the ones most often relevant for a thesis at the intersection of agents + ML:

1. **RL from human feedback (RLHF)**  
   After supervised fine-tuning, a reward model trained on human preferences can be used to **align** the policy (the language model) with human judgments. This is RL on **sequences of tokens** (often treated with policy-gradient-style algorithms such as PPO in the influential literature).

2. **Preference optimization without explicit RL**  
   Methods like **DPO** and related approaches optimize for preferences with a **different objective** than classical MDP control, but they address the **same alignment problem** RLHF was built for. (Useful to know even if your thesis is “agentic” rather than “RL-only.”)

3. **Interactive environments**  
   Benchmarks such as **ALFWorld** and **WebShop** (see the ReAct paper) treat language as an interface to an environment; **RL and imitation learning** baselines appear there. An LLM agent can be compared to or **combined with** RL-style training.

4. **Robotics and embodied agents**  
   Classical RL dominates when actions are low-level (torques, waypoints) and safety and sample efficiency matter. LLMs may provide high-level plans; RL may refine control.

5. **Bandits**  
   Multi-armed bandits are RL with a single step. They matter for **adaptive tool selection**, A/B testing of prompts, or online recommendation—sometimes closer to your application than “full” MDP RL.

---

## 6. Landmark paper: ReAct (reasoning + acting)

**Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models.”**  
arXiv: [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)  
PDF: [https://arxiv.org/pdf/2210.03629](https://arxiv.org/pdf/2210.03629)

This paper is widely cited as a **reference pattern** for tool-using LLM agents and for comparing LLM agents to RL / imitation baselines on interactive tasks.

---

## 7. Surveys worth reading first

1. **Plaat et al., “Agentic Large Language Models, a Survey.”**  
   arXiv: [https://arxiv.org/abs/2503.23037](https://arxiv.org/abs/2503.23037)  
   Organizes agentic LLM work into broad themes (reasoning, acting, interaction / multi-agent) and is useful as a **map of the field**.

2. **“Agentic AI: A Comprehensive Survey of Architectures, Applications, and Future Directions.”**  
   *Artificial Intelligence Review* (Springer).  
   Open access link (publisher): [https://link.springer.com/article/10.1007/s10462-025-11422-4](https://link.springer.com/article/10.1007/s10462-025-11422-4)  
   Useful for **enterprise / governance** framing and hybrid (symbolic + neural) angles.

3. **LLM + planning (if your topic mentions planning).**  
   Example survey (check for updates on arXiv): *A Survey on Large Language Model based Autonomous Agents* — search arXiv for the latest year; the field moves quickly and multiple surveys overlap.

4. **Guo et al., “Large Language Model based Multi-Agents: A Survey of Progress and Challenges.”**  
   arXiv: [https://arxiv.org/abs/2402.01680](https://arxiv.org/abs/2402.01680)  
   Use this when your topic is **collaboration**, **communication between agents**, or **multi-agent** LLM systems (profiles, interaction, benchmarks).

---

## 8. Suggested reading order (practical)

1. Skim **one agent chapter** in Russell & Norvig (terminology: agent, environment, utility).  
2. Read **Section 3** of this primer if your thesis stresses **collaboration** or **multi-agent** systems.  
3. Read **ReAct** (Section 6) for the modern LLM agent loop.  
4. Read **Plaat et al.** survey (Section 7.1) for the overall agentic-LLM map; add **Guo et al.** (Section 7.4) if collaboration is central.  
5. If RL is central to your thesis: Sutton & Barto **Chapters 1–4** (foundations), then **6–7** (temporal-difference ideas), then skim **13–15** (policy gradients / deep RL pointers).  
6. If alignment / training is central: follow citations from **InstructGPT** / **RLHF** papers from your advisor’s reading list (names and venues change; use their canonical references).

---

## 9. References (compact bibliography)

- Russell, S., & Norvig, P. *Artificial Intelligence: A Modern Approach* (current edition). Pearson.  
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press. Free PDF: [http://www.incompleteideas.net/book/the-book-2nd.html](http://www.incompleteideas.net/book/the-book-2nd.html)  
- Yao, S., et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. *ICLR 2023*. arXiv:2210.03629. [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)  
- Plaat, A., et al. Agentic Large Language Models, a Survey. arXiv:2503.23037. [https://arxiv.org/abs/2503.23037](https://arxiv.org/abs/2503.23037)  
- Agentic AI: A Comprehensive Survey… *Artificial Intelligence Review*. DOI: 10.1007/s10462-025-11422-4. [https://link.springer.com/article/10.1007/s10462-025-11422-4](https://link.springer.com/article/10.1007/s10462-025-11422-4)  
- Guo, T., et al. (2024). Large Language Model based Multi-Agents: A Survey of Progress and Challenges. *IJCAI 2024* (also arXiv). arXiv:2402.01680. [https://arxiv.org/abs/2402.01680](https://arxiv.org/abs/2402.01680)

---

## 10. Next step for you

Add `Topic.pdf` to this folder **or** paste the **exact thesis title and 2–3 bullet objectives** from your supervisor. Then this primer can be trimmed to **only** the parts that matter for *your* formulation (e.g., multi-agent vs. RLHF vs. robotics).
