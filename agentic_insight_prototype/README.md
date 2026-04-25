# Agentic Insight Prototype

This repository contains a **first working prototype** for the thesis project: a small, explicit **file-selection pipeline** (scan → categorize → rank) and an **MCP server** exposing that pipeline as callable tools.

For detailed documentation, start here:

- `documentation/README_01_file-selection-and-mcp.md`

## Quickstart

```bash
cd agentic_insight_prototype
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Run

### In-process pipeline (no MCP)

```bash
python -c "from insight_proto.orchestrator.pipeline import run_file_selection; import json; print(json.dumps(run_file_selection('.'), indent=2))"
```

### MCP smoke test (recommended)

This starts the MCP server as a subprocess and calls a couple of tools.

```bash
insight-mcp-client .
```

### External scan output location

`insight-scan-external-repo` writes a JSON report. If `-o` is omitted, it defaults to `results/scan_results.json`.

### MCP server (stdio)

Use this if you want to connect from an MCP host (e.g., an inspector / desktop client).

```bash
insight-mcp-server
```

