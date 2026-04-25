"""FastMCP stdio server: file selection tools for agentic insight prototype."""

from __future__ import annotations

import json
import logging
import sys

from mcp.server.fastmcp import FastMCP

from insight_proto.tools import file_selection as fs

# Never log to stdout in stdio mode — it breaks JSON-RPC on stdout.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
_log = logging.getLogger(__name__)

mcp = FastMCP(
    "AgenticInsightPrototype",
    json_response=True,
)


@mcp.tool()
def health_check() -> str:
    """Return server name and status (for connectivity tests)."""
    return json.dumps({"status": "ok", "server": "agentic-insight-prototype"})


@mcp.tool()
def scan_repository(root: str, extensions: str = ".py") -> str:
    """
    List files under ``root`` with given extensions (comma-separated, e.g. ``.py,.yaml``).
    Paths are relative to ``root``. Common ignored dirs (``.git``, ``.venv``, …) are skipped.
    """
    raw = [x.strip() for x in extensions.split(",") if x.strip()]
    exts = tuple(raw) if raw else (".py",)
    paths = fs.scan_repository(root, extensions=exts)
    return json.dumps({"root": root, "paths": paths, "count": len(paths)})


@mcp.tool()
def categorize_files(root: str, extensions: str = ".py") -> str:
    """Scan the repo, then bucket paths into tests / configs / scripts / package_code / other."""
    raw = [x.strip() for x in extensions.split(",") if x.strip()]
    exts = tuple(raw) if raw else (".py",)
    paths = fs.scan_repository(root, extensions=exts)
    categories = fs.categorize_paths(paths)
    return json.dumps({"root": root, "categories": categories, "scan_count": len(paths)})


@mcp.tool()
def filter_ml_relevant_files(
    root: str,
    extensions: str = ".py",
    min_score: float = 0.15,
    exclude: str = "",
) -> str:
    """
    Rank files by ML-library keywords and path hints; keep scores >= ``min_score``.

    Optionally exclude path groups with ``exclude`` (comma-separated), e.g. ``tests,examples``.
    """
    raw = [x.strip() for x in extensions.split(",") if x.strip()]
    exts = tuple(raw) if raw else (".py",)
    paths = fs.scan_repository(root, extensions=exts)
    excl = tuple(x.strip() for x in exclude.split(",") if x.strip())
    if excl:
        paths = fs.apply_excludes(paths, excl)
    ranked = fs.rank_ml_files(root, paths, min_score=min_score)
    return json.dumps(
        {
            "root": root,
            "min_score": min_score,
            "exclude": list(excl),
            "ranked": ranked,
            "count": len(ranked),
        }
    )


def main() -> None:
    _log.info("Starting MCP server (stdio)")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
