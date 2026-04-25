"""
Clone a real Git repository, run the file-selection pipeline, write JSON, then remove the clone.

Requires ``git`` on PATH. Uses a shallow clone (``--depth 1``) to limit size and time.

Examples::

    insight-scan-external-repo
    insight-scan-external-repo --url https://github.com/pytorch/examples.git -o results/pytorch_examples.json
    insight-scan-external-repo --no-cleanup   # keep temp dir; path printed on stderr
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _git_clone_shallow(url: str, dest: Path) -> None:
    """Clone ``url`` into new directory ``dest`` (must not exist yet)."""
    r = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(dest)],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        msg = r.stderr.strip() or r.stdout.strip() or f"exit {r.returncode}"
        raise RuntimeError(f"git clone failed: {msg}")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Shallow-clone a repo, run file selection, save JSON, delete clone by default.",
    )
    p.add_argument(
        "--url",
        default="https://github.com/karpathy/micrograd.git",
        help="Git remote URL (default: small educational ML repo)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("results/scan_results.json"),
        help="Where to write pipeline JSON (default: ./results/scan_results.json)",
    )
    p.add_argument(
        "--ml-min-score",
        type=float,
        default=0.15,
        help="Minimum ML heuristic score for ranked list (default: 0.15)",
    )
    p.add_argument(
        "--exclude",
        default="",
        help="Comma-separated path groups to exclude (e.g. tests,examples). Default: none",
    )
    p.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Do not delete the clone; print its path on stderr",
    )
    args = p.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="insight_proto_scan_"))
    clone_root = tmp / "repo"
    try:
        print(f"Cloning (depth=1): {args.url}", file=sys.stderr)
        print(f"  -> {clone_root}", file=sys.stderr)
        _git_clone_shallow(args.url, clone_root)

        from insight_proto.tools import file_selection as fs

        paths = fs.scan_repository(str(clone_root), extensions=(".py",))
        excl = tuple(x.strip() for x in args.exclude.split(",") if x.strip())
        if excl:
            paths = fs.apply_excludes(paths, excl)

        categories = fs.categorize_paths(paths)
        ml_ranked = fs.rank_ml_files(str(clone_root), paths, min_score=args.ml_min_score)
        result = {
            "root": str(clone_root),
            "scan_count": len(paths),
            "exclude": list(excl),
            "categories": categories,
            "ml_ranked": ml_ranked,
            "ml_ranked_count": len(ml_ranked),
        }
        args.output = args.output.resolve()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Wrote: {args.output}", file=sys.stderr)
        print(f"  scan_count={result['scan_count']} ml_ranked_count={result['ml_ranked_count']}", file=sys.stderr)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if getattr(exc, "__cause__", None) is not None:
            print(f"Cause: {exc.__cause__}", file=sys.stderr)
        return 1
    finally:
        if args.no_cleanup:
            print(f"Clone kept at: {clone_root}", file=sys.stderr)
        else:
            shutil.rmtree(tmp, ignore_errors=True)
            print("Removed temporary clone.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
