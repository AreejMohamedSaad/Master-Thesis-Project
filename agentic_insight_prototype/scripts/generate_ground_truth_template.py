#!/usr/bin/env python3
"""Build a ground-truth labeling CSV from a detection report JSON."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def _evidence_preview(evidence: list[dict], *, max_items: int = 2) -> str:
    parts: list[str] = []
    for item in evidence[:max_items]:
        line = item.get("line", "?")
        snippet = str(item.get("snippet", "")).replace("\n", " ")
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        parts.append(f"L{line}: {snippet}")
    return " | ".join(parts)


def _review_priority(verdict: str, confidence: str) -> str:
    if verdict in {"absent", "unclear"}:
        return "high"
    if verdict == "present" and confidence == "medium":
        return "medium"
    return "low"


def generate_template(report_path: Path, output_path: Path, *, rule_id: str | None = None) -> int:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    root = report.get("root", "")
    findings = report.get("findings", [])
    if rule_id:
        findings = [item for item in findings if str(item.get("rule_id", "")) == rule_id]
    if not findings:
        msg = "no findings in report"
        if rule_id:
            msg += f" for rule {rule_id}"
        print(f"Error: {msg}", file=sys.stderr)
        return 1

    rows: list[dict[str, str]] = []
    for item in findings:
        evidence = item.get("evidence") or []
        counts = item.get("signal_counts") or {}
        verdict = str(item.get("verdict", ""))
        confidence = str(item.get("confidence", ""))
        strong = counts.get("strong")
        if strong is None:
            strong = counts.get("gate", counts.get("runtime", 0))
            if "setup" in counts:
                strong = counts.get("runtime", 0) + counts.get("setup", 0)
            elif "generic" in counts:
                strong = counts.get("gate", 0) + counts.get("generic", 0)
        weak = counts.get("weak", 0)
        rows.append(
            {
                "rule_id": str(item.get("rule_id", "")),
                "path": str(item.get("path", "")),
                "repo_root": root,
                "detector_verdict": verdict,
                "detector_confidence": confidence,
                "strong_signals": str(strong),
                "weak_signals": str(weak),
                "evidence_preview": _evidence_preview(evidence),
                "review_priority": _review_priority(verdict, confidence),
                "status": "",
                "notes": "",
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    high = sum(1 for r in rows if r["review_priority"] == "high")
    print(f"Wrote: {output_path}", file=sys.stderr)
    print(f"  rows={len(rows)} high_priority={high}", file=sys.stderr)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Generate ground-truth labeling CSV from detection JSON.")
    p.add_argument(
        "--report",
        type=Path,
        default=Path("results/detection_report_trl_top15.json"),
        help="Detection report JSON (default: results/detection_report_trl_top15.json)",
    )
    p.add_argument(
        "--rule",
        default=None,
        help="Only include findings for this rule id (e.g. PR8)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output CSV path (default: results/ground_truth_<report_stem>[_rule].csv)",
    )
    args = p.parse_args()

    if not args.report.is_file():
        print(f"Error: report not found: {args.report}", file=sys.stderr)
        return 1

    stem = args.report.stem
    if args.rule:
        stem = f"{stem}_{args.rule.lower()}"
    output = args.output or Path("results") / f"ground_truth_{stem}.csv"
    return generate_template(args.report.resolve(), output.resolve(), rule_id=args.rule)


if __name__ == "__main__":
    raise SystemExit(main())
