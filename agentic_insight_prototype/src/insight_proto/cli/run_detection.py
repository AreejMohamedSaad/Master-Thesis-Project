"""
Run practice detection on paths from a file-selection scan JSON (or on a repo directly).

The scan JSON from ``insight-scan-external-repo`` lists ``ml_ranked`` paths but its
``root`` field often points at a deleted temp clone. Pass ``--root`` to the real
checkout on disk.

Examples::

    insight-run-detection --root . -o results/detection_report.json
    insight-run-detection --scan results/2026-04-30_trl_core_scan.json --root ~/code/trl
    insight-run-detection --scan results/scan.json --root ~/code/trl --rules PR2 --top 15
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_scan_paths(scan_path: Path, *, top: int | None = None) -> tuple[list[str], dict[str, Any]]:
    """Read ``ml_ranked`` paths from a file-selection JSON report."""
    data = json.loads(scan_path.read_text(encoding="utf-8"))
    ml_ranked = data.get("ml_ranked")
    if not isinstance(ml_ranked, list):
        raise ValueError(f"{scan_path}: expected 'ml_ranked' list in scan JSON")

    paths: list[str] = []
    for item in ml_ranked:
        if isinstance(item, dict) and "path" in item:
            paths.append(str(item["path"]))
        elif isinstance(item, str):
            paths.append(item)

    if not paths:
        raise ValueError(f"{scan_path}: no paths found in 'ml_ranked'")

    if top is not None:
        if top < 1:
            raise ValueError("--top must be >= 1")
        paths = paths[:top]

    meta = {
        "scan_file": str(scan_path.resolve()),
        "scan_root": data.get("root"),
        "scan_count": data.get("scan_count"),
        "ml_ranked_count": data.get("ml_ranked_count", len(data.get("ml_ranked", []))),
        "exclude": data.get("exclude", []),
        "paths_used": len(paths),
    }
    return paths, meta


def main() -> int:
    p = argparse.ArgumentParser(
        description="Run practice detection on ml_ranked paths from a scan JSON or on a repo.",
    )
    p.add_argument(
        "--scan",
        type=Path,
        help="File-selection JSON (uses its ml_ranked paths). Requires --root.",
    )
    p.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Repository root on disk (where those paths exist)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("results/detection_report.json"),
        help="Where to write detection JSON (default: ./results/detection_report.json)",
    )
    p.add_argument(
        "--rules",
        default="PR2",
        help="Comma-separated rule ids (default: PR2)",
    )
    p.add_argument(
        "--top",
        type=int,
        default=None,
        help="Only scan the first N ml_ranked paths from --scan (useful for ground-truth subsets)",
    )
    p.add_argument(
        "--ml-min-score",
        type=float,
        default=0.15,
        help="When --scan is omitted, minimum ML score for auto file selection (default: 0.15)",
    )
    p.add_argument(
        "--exclude",
        default="",
        help="Comma-separated path groups to exclude when auto-selecting files (ignored with --scan)",
    )
    args = p.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"Error: --root is not a directory: {root}", file=sys.stderr)
        return 1

    rules = tuple(r.strip() for r in args.rules.split(",") if r.strip())
    if not rules:
        print("Error: --rules must list at least one rule id", file=sys.stderr)
        return 1

    if args.top is not None and args.scan is None:
        print("Error: --top requires --scan", file=sys.stderr)
        return 1

    try:
        from insight_proto.orchestrator.pipeline import run_detection

        scan_meta: dict[str, Any] | None = None
        if args.scan is not None:
            if not args.scan.is_file():
                print(f"Error: scan file not found: {args.scan}", file=sys.stderr)
                return 1
            paths, scan_meta = load_scan_paths(args.scan.resolve(), top=args.top)
            report = run_detection(root, paths=paths, rules=rules)
            report["source_scan"] = scan_meta
        else:
            exclude = tuple(x.strip() for x in args.exclude.split(",") if x.strip())
            report = run_detection(
                root,
                rules=rules,
                ml_min_score=args.ml_min_score,
                exclude=exclude,
            )

        args.output = args.output.resolve()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote: {args.output}", file=sys.stderr)
        for rule in rules:
            s = report["summary"][rule]
            print(
                f"  {rule}: scanned={s['files_scanned']} "
                f"present={s['present']} unclear={s['unclear']} absent={s['absent']}",
                file=sys.stderr,
            )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
