"""PR8 - validation between stages (heuristic detector v1.1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

RULE_ID = "PR8"

# Handoff / artifact gates (PR8).
_GATE_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "def_gate",
        re.compile(r"^\s*def\s+(validate_\w+|check_\w+|verify_\w+)\s*\("),
        "def validate_/check_/verify_",
    ),
    ("check_server", re.compile(r"\bcheck_server\s*\("), "check_server("),
    ("validate_call", re.compile(r"\bvalidate\w*\s*\("), "validate*("),
    ("pydantic", re.compile(r"\bpydantic\b"), "pydantic"),
    ("jsonschema", re.compile(r"\bjsonschema\b"), "jsonschema"),
    ("marshmallow", re.compile(r"\bmarshmallow\b"), "marshmallow"),
    ("validation_error", re.compile(r"\bValidationError\b"), "ValidationError"),
    ("model_validate", re.compile(r"\.model_validate\s*\("), ".model_validate("),
    (
        "artifact_raise",
        re.compile(
            r"\braise\s+\w+\(.*"
            r"(must contain|must return keys|required when|must match|not found|"
            r"expects a dataset|named splits|teacher model or teacher server|"
            r"align teacher|output dict|handoff|empty handoff)",
            re.IGNORECASE,
        ),
        "raise with artifact/handoff message",
    ),
)

# Generic Python validation (config, constructor, type checks).
_GENERIC_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("assert", re.compile(r"\bassert\b"), "assert"),
    ("raise_value_error", re.compile(r"\braise\s+ValueError\b"), "raise ValueError"),
    ("raise_type_error", re.compile(r"\braise\s+TypeError\b"), "raise TypeError"),
    ("raise_validation_error", re.compile(r"\braise\s+ValidationError\b"), "raise ValidationError"),
    ("check_call", re.compile(r"\bcheck_\w+\s*\("), "check_*("),
    ("verify_call", re.compile(r"\bverify_\w+\s*\("), "verify_*("),
)

_SETUP_RAISE = re.compile(
    r"(is required|already instantiated|must be either|train_dataset|"
    r"model_kwargs|processing_class|padding_side|model_name_or_path)",
    re.IGNORECASE,
)

_WEAK_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("if_not", re.compile(r"\bif\s+not\s+"), "if not"),
    ("if_is_none", re.compile(r"\bif\s+.*\bis\s+None\b"), "if ... is None"),
)

_LIB_SIGNALS = frozenset({"pydantic", "jsonschema", "marshmallow", "validation_error"})


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


def _is_skipped_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("#") or stripped.startswith(">>>")


def _collect_matches(
    lines: list[str],
    patterns: tuple[tuple[str, re.Pattern[str], str], ...],
    *,
    skip_comments: bool = False,
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for line_no, line in enumerate(lines, start=1):
        if skip_comments and _is_skipped_line(line):
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


def _split_setup_raises(generic: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    setup: list[dict[str, Any]] = []
    other: list[dict[str, Any]] = []
    for item in generic:
        if _SETUP_RAISE.search(item["snippet"]):
            setup.append({**item, "signal": "setup_raise", "label": "setup/config raise"})
        else:
            other.append(item)
    return setup, other


def detect_pr8_validation(path: str | Path) -> dict[str, Any]:
    """
    Scan one Python file for PR8 (validation between stages) evidence.

    Verdicts (v1.1 - handoff/artifact focused):
      - present: gate/artifact validation (named checks, schema libs, handoff messages)
      - unclear: generic validation only (config/setup raises, weak guards)
      - absent: no validation-related signals
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
    gate = _collect_matches(lines, _GATE_PATTERNS, skip_comments=True)
    generic_all = _collect_matches(lines, _GENERIC_PATTERNS, skip_comments=True)
    setup, generic = _split_setup_raises(generic_all)
    weak = _collect_matches(lines, _WEAK_PATTERNS, skip_comments=True)

    gate_lines = {item["line"] for item in gate}

    if gate:
        verdict = "present"
        has_lib = any(item["signal"] in _LIB_SIGNALS for item in gate)
        confidence = "high" if has_lib or len(gate) >= 2 else "medium"
        evidence = gate + generic + setup + weak
    elif generic or setup or weak:
        verdict = "unclear"
        confidence = "medium" if generic or setup else "low"
        evidence = generic + setup + weak
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
            "gate": len(gate),
            "setup": len(setup),
            "generic": len(generic),
            "weak": len(weak),
        },
    }
