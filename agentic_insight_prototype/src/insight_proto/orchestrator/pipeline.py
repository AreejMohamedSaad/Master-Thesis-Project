"""In-process pipelines: file selection and practice detection."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from insight_proto.detectors.b1 import detect_b1_routing
from insight_proto.detectors.pr2 import detect_pr2_logging
from insight_proto.detectors.pr8 import detect_pr8_validation
from insight_proto.tools import file_selection as fs

_DETECTOR_BY_RULE: dict[str, Callable[[str | Path], dict[str, Any]]] = {
    "B1": detect_b1_routing,
    "PR2": detect_pr2_logging,
    "PR8": detect_pr8_validation,
}


def run_file_selection(
    root: str | Path,
    *,
    extensions: tuple[str, ...] = (".py",),
    ml_min_score: float = 0.15,
) -> dict[str, Any]:
    """
    Steps: scan → categorize → rank by ML heuristics.

    Returns a JSON-serializable dict for logging or downstream agents.
    """
    root_s = str(Path(root).resolve())
    paths = fs.scan_repository(root_s, extensions=extensions)
    categories = fs.categorize_paths(paths)
    ml_ranked = fs.rank_ml_files(root_s, paths, min_score=ml_min_score)
    return {
        "root": root_s,
        "scan_count": len(paths),
        "categories": categories,
        "ml_ranked": ml_ranked,
        "ml_ranked_count": len(ml_ranked),
    }


def run_detection(
    root: str | Path,
    *,
    paths: list[str] | None = None,
    rules: tuple[str, ...] = ("PR2",),
    ml_min_score: float = 0.15,
    exclude: tuple[str, ...] = (),
) -> dict[str, Any]:
    """
    Run practice detectors on selected files under ``root``.

    If ``paths`` is omitted, uses ML-ranked paths from file selection (same as
    ``run_file_selection``). Returns one JSON-serializable report dict.
    """
    root_path = Path(root).resolve()
    root_s = str(root_path)

    if paths is None:
        selection = run_file_selection(root_s, ml_min_score=ml_min_score)
        rel_paths = [item["path"] for item in selection["ml_ranked"]]
    else:
        selection = None
        rel_paths = list(paths)

    if exclude:
        rel_paths = fs.apply_excludes(rel_paths, exclude)

    unknown_rules = [rule for rule in rules if rule not in _DETECTOR_BY_RULE]
    if unknown_rules:
        raise ValueError(f"unknown rule ids: {unknown_rules}")

    findings: list[dict[str, Any]] = []
    for rel in rel_paths:
        abs_path = root_path / rel
        for rule in rules:
            result = _DETECTOR_BY_RULE[rule](abs_path)
            result["path"] = rel
            findings.append(result)

    summary: dict[str, int] = {}
    for rule in rules:
        rule_findings = [f for f in findings if f["rule_id"] == rule]
        summary[rule] = {
            "files_scanned": len(rule_findings),
            "present": sum(1 for f in rule_findings if f["verdict"] == "present"),
            "unclear": sum(1 for f in rule_findings if f["verdict"] == "unclear"),
            "absent": sum(1 for f in rule_findings if f["verdict"] == "absent"),
        }

    report: dict[str, Any] = {
        "root": root_s,
        "rules": list(rules),
        "files_scanned": len(rel_paths),
        "findings": findings,
        "summary": summary,
    }
    if selection is not None:
        report["file_selection"] = {
            "scan_count": selection["scan_count"],
            "ml_ranked_count": selection["ml_ranked_count"],
        }
    return report

