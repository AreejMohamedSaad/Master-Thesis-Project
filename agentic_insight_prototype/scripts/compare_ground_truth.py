#!/usr/bin/env python3
"""Compare detector verdicts against a labeled ground-truth CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def _load_report_verdicts(report_path: Path) -> dict[str, str]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    verdicts: dict[str, str] = {}
    for item in report.get("findings", []):
        path = str(item.get("path", ""))
        if path:
            verdicts[path] = str(item.get("verdict", "")).strip().lower()
    return verdicts


def compare(csv_path: Path, *, report_path: Path | None = None) -> dict:
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    if not rows:
        raise ValueError(f"no rows in {csv_path}")

    status_key = "status" if "status" in rows[0] else "your_label"
    if status_key not in rows[0]:
        raise ValueError("CSV must include a 'status' (or 'your_label') column")

    report_verdicts = _load_report_verdicts(report_path) if report_path else {}

    compared = []
    for row in rows:
        status = (row.get(status_key) or "").strip().lower()
        path = row.get("path", "")
        if report_verdicts and path in report_verdicts:
            detector = report_verdicts[path]
        else:
            detector = (row.get("detector_verdict") or "").strip().lower()
        if not status:
            continue
        compared.append(
            {
                "path": path,
                "detector_verdict": detector,
                "status": status,
                "match": detector == status,
            }
        )

    if not compared:
        raise ValueError("no labeled rows (fill the status column)")

    matches = sum(1 for item in compared if item["match"])
    total = len(compared)
    mismatches = [item for item in compared if not item["match"]]

    by_status: dict[str, dict[str, int]] = {}
    for item in compared:
        bucket = by_status.setdefault(item["status"], {"total": 0, "match": 0})
        bucket["total"] += 1
        if item["match"]:
            bucket["match"] += 1

    result = {
        "csv": str(csv_path.resolve()),
        "report": str(report_path.resolve()) if report_path else None,
        "labeled_rows": total,
        "exact_matches": matches,
        "accuracy": round(matches / total, 3),
        "mismatches": mismatches,
        "by_status": by_status,
    }
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="Compare detector output to ground-truth CSV labels.")
    p.add_argument(
        "--csv",
        type=Path,
        default=Path("results/ground_truth_detection_report_trl_top15.csv"),
        help="Ground-truth CSV with status column",
    )
    p.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional detection report JSON (for metadata only)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write comparison JSON (default: print summary to stdout)",
    )
    args = p.parse_args()

    if not args.csv.is_file():
        print(f"Error: CSV not found: {args.csv}", file=sys.stderr)
        return 1

    try:
        result = compare(args.csv.resolve(), report_path=args.report)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Labeled rows: {result['labeled_rows']}", file=sys.stderr)
    print(f"Exact matches: {result['exact_matches']} ({result['accuracy']:.1%})", file=sys.stderr)
    if result["mismatches"]:
        print("Mismatches:", file=sys.stderr)
        for item in result["mismatches"]:
            print(
                f"  {item['path']}: detector={item['detector_verdict']} status={item['status']}",
                file=sys.stderr,
            )
    else:
        print("No mismatches.", file=sys.stderr)

    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
