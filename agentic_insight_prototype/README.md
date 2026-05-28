# Agentic Insight Prototype

Prototype for the thesis pipeline: **file selection** (rank repo files) and **practice detection** (PR2, PR8, B1 heuristics on selected paths).

## Docs

- [README_01](documentation/README_01_file-selection-and-mcp.md) : file selection, MCP, scan CLI
- [README_03](documentation/README_03_detection-v1-pr2.md) : PR2 logging detector
- [README_04](documentation/README_04_detection-v1-pr8.md) : PR8 validation detector
- [README_05](documentation/README_05_detection-three-rules-two-repos.md) : three rules, TRL + CrewAI
- [CATALOG](docs/CATALOG.md) : practice rules

## Quickstart

```bash
cd agentic_insight_prototype
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Commands

| Command | Purpose |
|---------|---------|
| `insight-scan-external-repo` | Clone repo, run file selection, write JSON |
| `insight-run-detection` | Run PR2/PR8/B1 on paths from scan JSON |
| `insight-mcp-client` | Smoke-test MCP tools |
| `insight-mcp-server` | MCP server (stdio) |

Detection example:

```bash
insight-run-detection \
  --scan results/2026-04-30_trl_core_scan.json \
  --root ~/code/trl \
  --top 15 \
  --rules PR2,PR8,B1 \
  -o results/detection_report_trl_top15_pr2_pr8_b1.json
```

Scan JSON defaults to `results/` if `-o` is omitted. Large `results/*.json` reports are gitignored; regenerate locally.
