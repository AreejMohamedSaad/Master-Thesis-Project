"""B1 - routing / handoff (heuristic detector v1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

RULE_ID = "B1"

# Explicit routing components (classes, functions, framework APIs).
_NAMED_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "class_router",
        re.compile(
            r"^\s*class\s+\w*(Router|Supervisor|Orchestrat\w*|Handoff|Delegate)\w*\s*[\(:]",
            re.IGNORECASE,
        ),
        "class Router/Supervisor/Orchestrator/Handoff",
    ),
    (
        "def_route",
        re.compile(
            r"^\s*def\s+(route\w*|handoff\w*|delegate\w*|dispatch\w*)\s*\(",
            re.IGNORECASE,
        ),
        "def route_/handoff_/delegate_",
    ),
    (
        "named_identifier",
        re.compile(
            r"\b(Router|Supervisor|Orchestrat\w*|HandoffTool|Handoff)\b",
        ),
        "Router/Supervisor/Orchestrator/Handoff identifier",
    ),
    ("langgraph_edges", re.compile(r"\badd_conditional_edges\s*\("), "add_conditional_edges("),
    ("langgraph_graph", re.compile(r"\bStateGraph\s*\("), "StateGraph("),
    ("crewai_process", re.compile(r"\bProcess\s*\.\s*(sequential|hierarchical)\b"), "CrewAI Process"),
    ("autogen_groupchat", re.compile(r"\bGroupChat\b"), "GroupChat"),
)

_KEYWORD_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("kw_handoff", re.compile(r"\bhandoff\b", re.IGNORECASE), "handoff"),
    ("kw_delegate", re.compile(r"\bdelegat(e|ion|ed|ing)\b", re.IGNORECASE), "delegate"),
    ("kw_routing", re.compile(r"\brouting\b", re.IGNORECASE), "routing"),
    ("kw_next_agent", re.compile(r"\bnext_agent\b", re.IGNORECASE), "next_agent"),
    ("kw_assign_to", re.compile(r"\bassign_to\b", re.IGNORECASE), "assign_to"),
    ("kw_dispatch", re.compile(r"\bdispatch\b", re.IGNORECASE), "dispatch"),
    ("kw_route_to", re.compile(r"\broute_to\b", re.IGNORECASE), "route_to"),
    ("kw_supervisor", re.compile(r"\bsupervisor\b", re.IGNORECASE), "supervisor"),
)

_PATH_BOOST = re.compile(r"(router|supervisor|orchestrat|handoff|delegate)", re.IGNORECASE)


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


def _path_boost(path: Path) -> list[dict[str, Any]]:
    name = path.name
    if _PATH_BOOST.search(name):
        return [
            {
                "line": 0,
                "signal": "path_boost",
                "label": "routing keyword in filename",
                "snippet": name,
            }
        ]
    return []


def detect_b1_routing(path: str | Path) -> dict[str, Any]:
    """
    Scan one Python file for B1 (routing / handoff) evidence.

    Verdicts:
      - present: named router/supervisor component, framework routing API, path boost,
        or >=3 routing keyword hits
      - unclear: 1-2 routing keywords only
      - absent: no routing signals
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
    named = _collect_matches(lines, _NAMED_PATTERNS, skip_comments=True)
    keywords = _collect_matches(lines, _KEYWORD_PATTERNS, skip_comments=True)
    path_hits = _path_boost(file_path)

    # Unique keyword signal types (not line count)
    keyword_types = {item["signal"] for item in keywords}

    if named or path_hits or len(keyword_types) >= 3:
        verdict = "present"
        if named or path_hits:
            confidence = "high" if len(named) >= 2 or path_hits else "medium"
        else:
            confidence = "medium"
        evidence = path_hits + named + keywords
    elif keyword_types:
        verdict = "unclear"
        confidence = "low"
        evidence = keywords
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
            "named": len(named),
            "path_boost": len(path_hits),
            "keyword_types": len(keyword_types),
        },
    }
