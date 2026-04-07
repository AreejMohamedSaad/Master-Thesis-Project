"""
Minimal CrewAI demo (thesis sandbox): one agent, one task, sequential process.

LLM backends (pick one in `.env`):

1) OpenAI (cloud, paid): set OPENAI_API_KEY. If you see 429 `insufficient_quota`,
   add billing / credits at https://platform.openai.com/settings/organization/billing

2) Ollama (local, free): install https://ollama.com , run `ollama pull llama3.2`, then set:
     USE_OLLAMA=1

Then:
  source .venv/bin/activate
  python experiments/crewai_quickstart.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv

# Load .env from project root (parent of experiments/)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_ROOT, ".env"))

# Avoid interactive "view traces?" prompt on failure (non-interactive / CI friendly)
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")


def _use_ollama() -> bool:
    return os.getenv("USE_OLLAMA", "").strip().lower() in ("1", "true", "yes")


def _build_llm() -> LLM | None:
    if _use_ollama():
        model = os.getenv("OLLAMA_MODEL", "llama3.2").strip()
        return LLM(model=model, provider="ollama")
    return None


def _ollama_tags() -> tuple[list[str] | None, str | None]:
    """Return (installed model names, error_message). error_message set if server unreachable."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5) as resp:
            payload = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return None, (
            "Cannot reach Ollama at http://127.0.0.1:11434\n"
            "  Start it: run `ollama serve` in a terminal, or launch the Ollama app.\n"
            f"  Details: {e}"
        )

    names = [m.get("name", "") for m in payload.get("models", []) if m.get("name")]
    return names, None


def _ollama_has_model(model: str, installed: list[str]) -> bool:
    if not installed:
        return False
    base = model.split(":")[0].strip()
    for name in installed:
        if name == model or name.startswith(base + ":") or name == base:
            return True
    return False


def main() -> int:
    llm = _build_llm()

    if llm is not None and _use_ollama():
        model_name = os.getenv("OLLAMA_MODEL", "llama3.2").strip()
        tags, ollama_err = _ollama_tags()
        if ollama_err:
            print(ollama_err)
            return 1
        assert tags is not None
        if not _ollama_has_model(model_name, tags):
            print(
                "Ollama is running, but this model is not installed locally yet.\n"
                f"  You asked for: {model_name}\n"
                f"  Installed models: {tags if tags else '(none)'}\n\n"
                "Download one (free, runs on your PC):\n"
                f"  ollama pull {model_name}\n\n"
                "Smaller / faster on older laptops (~637 MB):\n"
                "  ollama pull tinyllama\n"
                "Then in .env set:  OLLAMA_MODEL=tinyllama\n"
            )
            return 1

    if llm is None and not os.getenv("OPENAI_API_KEY"):
        print(
            "No LLM configured.\n"
            "  Option A — OpenAI: set OPENAI_API_KEY in .env (needs billing if quota is 0).\n"
            "  Option B — Ollama (local): install Ollama, `ollama pull llama3.2`, set USE_OLLAMA=1 in .env.\n"
            "  See experiments/README.md"
        )
        return 1

    agent_kwargs: dict = {
        "role": "Research assistant",
        "goal": "Give short, clear answers for a thesis student.",
        "backstory": "You explain software and AI concepts in plain language.",
        "verbose": True,
    }
    if llm is not None:
        agent_kwargs["llm"] = llm

    researcher = Agent(**agent_kwargs)

    task = Task(
        description=(
            "In 3-5 sentences, explain what 'orchestration' means in a "
            "multi-agent LLM system (e.g. supervisor, handoff between agents)."
        ),
        expected_output="A short paragraph in English.",
        agent=researcher,
    )

    crew = Crew(
        agents=[researcher],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    print("\n--- Crew output ---\n", result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
