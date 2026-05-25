"""PR2 - runtime logs / traces (heuristic detector v1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

RULE_ID = "PR2"

# Actual log/trace emission in this file.
_RUNTIME_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("logger_call", re.compile(r"\blogger\.(info|debug|warning|error|exception|critical)\s*\("), "logger.*("),
    (
        "logging_call",
        re.compile(r"\blogging\.(info|debug|warning|error|exception|critical)\s*\("),
        "logging.*(",
    ),
    ("logging_getLogger", re.compile(r"\blogging\.getLogger\s*\("), "logging.getLogger("),
    ("wandb_log", re.compile(r"\bwandb\.log\s*\("), "wandb.log("),
    ("wandb_run", re.compile(r"\bwandb\.run\b"), "wandb.run"),
)

# Logging infrastructure without a matched runtime call in this file.
_SETUP_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("import_logging", re.compile(r"^\s*import\s+logging\b"), "import logging"),
    ("from_logging", re.compile(r"^\s*from\s+logging\b"), "from logging"),
    ("from_accelerate_logging", re.compile(r"from\s+accelerate(?:\.\w+)*\s+import\s+.*\blogging\b"), "accelerate logging import"),
    ("from_accelerate_get_logger", re.compile(r"from\s+accelerate\.logging\s+import\s+get_logger"), "from accelerate.logging import get_logger"),
    ("get_logger", re.compile(r"\bget_logger\s*\("), "get_logger("),
    ("from_loguru", re.compile(r"^\s*from\s+loguru\s+import"), "from loguru import"),
    ("import_loguru", re.compile(r"^\s*import\s+loguru\b"), "import loguru"),
    ("from_structlog", re.compile(r"^\s*from\s+structlog\b"), "from structlog"),
    ("import_structlog", re.compile(r"^\s*import\s+structlog\b"), "import structlog"),
    ("import_wandb", re.compile(r"^\s*import\s+wandb\b"), "import wandb"),
    ("import_mlflow", re.compile(r"^\s*import\s+mlflow\b"), "import mlflow"),
    (
        "opentelemetry",
        re.compile(r"^\s*(import|from)\s+opentelemetry\b"),
        "opentelemetry import",
    ),
)

_WEAK_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("print_call", re.compile(r"\bprint\s*\("), "print("),
    ("trace_keyword", re.compile(r"\b(trace_id|trace\.|tracing)\b"), "trace keyword"),
    ("span_keyword", re.compile(r"\b(span_id|\.span\b|opentelemetry\.trace)\b"), "span keyword"),
)

_STRUCTURED_HINT = re.compile(
    r"\b(extra\s*=|trace_id|span_id|step\s*=|agent\s*=|tool\s*=)\b"
)
_TRAINER_SUBCLASS = re.compile(r"^\s*class\s+\w*Trainer\s*\(\s*\w*Trainer\s*[\):]")


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def _snippet(line: str, *, max_len: int = 120) -> str:
    text = line.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _is_doctest_line(line: str) -> bool:
    return line.lstrip().startswith(">>>")


def _collect_matches(
    lines: list[str],
    patterns: tuple[tuple[str, re.Pattern[str], str], ...],
    *,
    skip_doctest: bool = False,
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for line_no, line in enumerate(lines, start=1):
        if skip_doctest and _is_doctest_line(line):
            continue
        for signal, pattern, label in patterns:
            if pattern.search(line):
                key = (line_no, signal)
                if key in seen:
                    continue
                seen.add(key)
                evidence.append(
                    {
                        "line": line_no,
                        "signal": signal,
                        "label": label,
                        "snippet": _snippet(line),
                    }
                )
    return evidence


def _has_trainer_subclass(lines: list[str]) -> bool:
    return any(_TRAINER_SUBCLASS.search(line) for line in lines)


def detect_pr2_logging(path: str | Path) -> dict[str, Any]:
    """
    Scan one Python file for PR2 (runtime logs / traces) evidence.

    Verdicts:
      - present: runtime log/trace call in this file
      - unclear: setup-only logging, weak print/trace hints, or trainer subclass with no local logs
      - absent: no logging-related signals
    """
    file_path = Path(path)
    rel_path = str(file_path)
    if not file_path.is_file():
        return {
            "rule_id": RULE_ID,
            "path": rel_path,
            "verdict": "absent",
            "confidence": "high",
            "evidence": [],
            "error": "file not found or not a regular file",
        }

    lines = _read_lines(file_path)
    runtime = _collect_matches(lines, _RUNTIME_PATTERNS)
    setup = _collect_matches(lines, _SETUP_PATTERNS)
    weak = _collect_matches(lines, _WEAK_PATTERNS, skip_doctest=True)

    has_structured = any(_STRUCTURED_HINT.search(item["snippet"]) for item in runtime)

    if runtime:
        verdict = "present"
        confidence = "high" if len(runtime) >= 2 or has_structured else "medium"
        evidence = runtime + setup + [e for e in weak if e["line"] not in {s["line"] for s in runtime + setup}]
    elif setup or weak:
        verdict = "unclear"
        confidence = "medium" if setup else "low"
        evidence = setup + weak
    elif _has_trainer_subclass(lines):
        verdict = "unclear"
        confidence = "low"
        evidence = [
            {
                "line": line_no,
                "signal": "trainer_subclass",
                "label": "Trainer subclass",
                "snippet": _snippet(line),
            }
            for line_no, line in enumerate(lines, start=1)
            if _TRAINER_SUBCLASS.search(line)
        ][:1]
    else:
        verdict = "absent"
        confidence = "high"
        evidence = []

    return {
        "rule_id": RULE_ID,
        "path": rel_path,
        "verdict": verdict,
        "confidence": confidence,
        "evidence": evidence[:10],
        "signal_counts": {
            "runtime": len(runtime),
            "setup": len(setup),
            "weak": len(weak),
        },
    }
