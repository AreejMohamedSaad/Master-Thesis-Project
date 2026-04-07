# Experiments (CrewAI sandbox)

## Setup (once)

```bash
cd "/path/to/Master thesis"
python3 -m venv .venv
source .venv/bin/activate
pip install crewai python-dotenv
```

## Run the quickstart

### Option A — OpenAI (paid API)

1. Copy `../.env.example` to `../.env` and set `OPENAI_API_KEY`.
2. If you get **429 insufficient_quota**, your key works but the account has **no credits**. Add billing or credits: [OpenAI billing](https://platform.openai.com/settings/organization/billing).

### Option B — Ollama (local, no API bill)

1. Install [Ollama](https://ollama.com) and **download at least one model** (your machine had **zero** models until you pull):

   ```bash
   ollama pull llama3.2
   ```

   On a slower PC, a smaller model is fine:

   ```bash
   ollama pull tinyllama
   ```

   Check: `ollama list` should show the model name (e.g. `tinyllama:latest`).

2. In `.env` set:

   ```bash
   USE_OLLAMA=1
   OLLAMA_MODEL=tinyllama
   ```

   (Match `OLLAMA_MODEL` to what you pulled — `llama3.2` or `tinyllama`, etc.)

3. Run (same as below).

### Command

```bash
source .venv/bin/activate
python experiments/crewai_quickstart.py
```

You should see verbose logs and a short paragraph about multi-agent orchestration.

## Why this matters for your thesis

- **Agent** = role + goal + backstory (like a “specialist” in your collaboration footprint).
- **Task** = one unit of work with expected output (like a **validation** or **handoff** artifact).
- **Crew** = runs tasks in order (or parallel) — this is concrete **orchestration** you can compare to mined repos (Supervisor, Handoff, LangGraph nodes, etc.).
