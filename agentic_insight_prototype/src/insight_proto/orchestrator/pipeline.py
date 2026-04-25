"""In-process file-selection pipeline (same logic as MCP tools; no subprocess)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from insight_proto.tools import file_selection as fs


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
