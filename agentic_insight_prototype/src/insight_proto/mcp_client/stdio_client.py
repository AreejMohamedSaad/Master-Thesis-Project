"""Spawn the insight MCP server over stdio and call a few tools (smoke test)."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _project_paths() -> tuple[Path, Path]:
    """Return (``src`` on PYTHONPATH, project root as cwd)."""
    here = Path(__file__).resolve()
    # .../src/insight_proto/mcp_client/stdio_client.py
    src = here.parents[2]
    project_root = here.parents[3]
    return src, project_root


def _default_server_params() -> StdioServerParameters:
    src, project_root = _project_paths()
    env = {**os.environ, "PYTHONPATH": str(src)}
    cwd = project_root
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "insight_proto.mcp_server.server"],
        cwd=str(cwd),
        env=env,
    )


async def run_smoke(repo_root: str) -> int:
    params = _default_server_params()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            names = [t.name for t in listed.tools]
            print("tools:", names, file=sys.stderr)

            hc = await session.call_tool("health_check", {})
            print("health_check:", _tool_text(hc), file=sys.stderr)

            payload = await session.call_tool(
                "scan_repository",
                {"root": repo_root, "extensions": ".py"},
            )
            print(_tool_text(payload))
            return 0


def _tool_text(result: object) -> str:
    from mcp.types import CallToolResult

    if not isinstance(result, CallToolResult):
        return str(result)
    for block in result.content:
        if hasattr(block, "text"):
            return block.text
    if result.structuredContent is not None:
        return json.dumps(result.structuredContent, indent=2)
    return str(result)


def main_sync() -> None:
    p = argparse.ArgumentParser(description="MCP stdio client smoke test")
    p.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Directory to pass to scan_repository (default: cwd)",
    )
    args = p.parse_args()
    root = str(Path(args.repo_root).resolve())
    raise SystemExit(asyncio.run(run_smoke(root)))


if __name__ == "__main__":
    main_sync()
