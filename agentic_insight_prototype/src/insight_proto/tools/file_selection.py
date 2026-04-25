"""Repository scan, coarse categorization, and ML-relevance heuristics (no LLM)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Skip heavy / non-source trees when walking a repo
DEFAULT_IGNORE_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        "dist",
        "build",
        ".eggs",
        ".tox",
    }
)

ML_KEYWORDS = (
    "torch",
    "tensorflow",
    "tf.",
    "keras",
    "sklearn",
    "stable_baselines",
    "gymnasium",
    "gym.",
    "jax",
    "flax",
    "lightning",
    "transformers",
    "datasets",
    "mlflow",
    "wandb",
    "ray",
    "rllib",
)

def apply_excludes(paths: list[str], exclude: tuple[str, ...]) -> list[str]:
    """
    Remove paths matching high-level exclude tokens (e.g. ``tests``, ``examples``).

    Tokens are matched against normalized (POSIX) paths. For known tokens we apply
    common conventions; for unknown tokens we exclude if the token appears as a
    path segment (``/token/``) or leading segment (``token/...``).
    """
    if not exclude:
        return paths

    tokens = tuple(t.strip().lower() for t in exclude if t.strip())
    if not tokens:
        return paths

    def is_excluded(p: str) -> bool:
        pl = p.replace("\\", "/").lower()
        for t in tokens:
            if t == "tests":
                if pl.startswith("tests/") or "/tests/" in pl or pl.startswith("test/") or "/test/" in pl:
                    return True
                continue
            if t == "examples":
                if pl.startswith("examples/") or "/examples/" in pl or pl.startswith("example/") or "/example/" in pl:
                    return True
                continue
            # generic segment match
            if pl.startswith(f"{t}/") or f"/{t}/" in pl:
                return True
        return False

    return [p for p in paths if not is_excluded(p)]


def scan_repository(
    root: str,
    extensions: tuple[str, ...] = (".py",),
    *,
    max_files: int | None = None,
) -> list[str]:
    """Return sorted relative paths under ``root`` (POSIX-style)."""
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise ValueError(f"Not a directory: {root}")

    out: list[str] = []
    for p in root_path.rglob("*"):
        if not p.is_file():
            continue
        if any(part in DEFAULT_IGNORE_DIRS for part in p.parts):
            continue
        if extensions and p.suffix not in extensions:
            continue
        try:
            rel = p.relative_to(root_path)
        except ValueError:
            continue
        out.append(rel.as_posix())
        if max_files is not None and len(out) >= max_files:
            break
    return sorted(out)


def categorize_paths(paths: list[str]) -> dict[str, list[str]]:
    """Assign paths to coarse buckets (heuristic; overlaps resolved by order)."""
    buckets: dict[str, list[str]] = {
        "tests": [],
        "configs": [],
        "scripts": [],
        "package_code": [],
        "other": [],
    }
    for p in paths:
        pl = p.replace("\\", "/").lower()
        base = Path(p).name.lower()
        if (
            "/tests/" in pl
            or "/test/" in pl
            or base.startswith("test_")
            or base.endswith("_test.py")
        ):
            buckets["tests"].append(p)
        elif any(
            base.endswith(s) for s in (".yaml", ".yml", ".json", ".toml", ".ini", ".cfg")
        ) or "/config" in pl:
            buckets["configs"].append(p)
        elif "/scripts/" in pl or base.startswith(("train_", "run_")) or base == "main.py":
            buckets["scripts"].append(p)
        elif "/src/" in pl or "/lib/" in pl or p.endswith(".py"):
            buckets["package_code"].append(p)
        else:
            buckets["other"].append(p)
    return buckets


def score_ml_relevance(path: str, root: str, *, max_bytes: int = 200_000) -> float:
    """Score 0.0–1.0 from path hints + keyword scan of file text."""
    full = Path(root) / path
    score = 0.0
    pl = path.lower()
    for hint in ("model", "train", "policy", "reward", "agent", "rl", "ppo", "sac"):
        if hint in pl:
            score += 0.05
    score = min(score, 0.3)

    if full.suffix not in (".py", ".yaml", ".yml", ".json", ".toml", ".md"):
        return min(1.0, score)

    try:
        text = full.read_text(encoding="utf-8", errors="replace")[:max_bytes]
    except OSError:
        return score

    t = text.lower()
    for kw in ML_KEYWORDS:
        if kw in t:
            score += 0.12
    if re.search(r"^\s*(?:from|import)\s+\w+", t, re.MULTILINE):
        score += 0.05
    return min(1.0, score)


def rank_ml_files(
    root: str,
    paths: list[str],
    *,
    min_score: float = 0.15,
) -> list[dict[str, Any]]:
    """Return paths with score >= ``min_score``, sorted by score descending."""
    ranked: list[dict[str, Any]] = []
    for p in paths:
        s = score_ml_relevance(p, root)
        if s >= min_score:
            ranked.append({"path": p, "score": round(s, 4)})
    ranked.sort(key=lambda x: (-x["score"], x["path"]))
    return ranked
