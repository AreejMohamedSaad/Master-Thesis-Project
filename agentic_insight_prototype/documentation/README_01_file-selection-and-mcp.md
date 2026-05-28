# Documentation 01: File selection and MCP

## What this covers

- **File selection:** scan a repo, bucket paths, rank ML-relevant `.py` files (`ml_ranked`).
- **MCP (stdio):** same logic exposed as MCP tools for external hosts.
- **Tests and CLI:** pytest, `insight-scan-external-repo` for a remote clone → JSON report.

Practice detection (PR2, PR8, B1) is in `README_03`–`README_05`. Rule definitions: `docs/CATALOG.md`.

---

## Layout

```text
agentic_insight_prototype/
├── src/insight_proto/
│   ├── tools/file_selection.py
│   ├── orchestrator/pipeline.py
│   ├── mcp_server/server.py
│   ├── mcp_client/stdio_client.py
│   └── cli/scan_external_repo.py
├── scripts/run_external_scan.sh
└── tests/test_file_selection.py
```

Selection logic lives in `file_selection.py`. The pipeline, MCP server, and CLI call into that module.

---

<img src="architecture_diagram.png" alt="Architecture diagram" width="600"/>

---

## Install

```bash
cd agentic_insight_prototype
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Run

**Tests:**

```bash
pytest -q
```

**Pipeline (no MCP):**

```bash
python -c "from insight_proto.orchestrator.pipeline import run_file_selection; import json; print(json.dumps(run_file_selection('.'), indent=2))"
```

**MCP smoke test:**

```bash
insight-mcp-client .
```

---

## MCP server

```bash
insight-mcp-server
```

Stdio mode: reads MCP messages on stdin. Logs go to stderr so stdout stays clean for the protocol.

**Tools:** `health_check`, `scan_repository`, `categorize_files`, `filter_ml_relevant_files` (`exclude` e.g. `tests,examples`).

---

## Scan a GitHub repo

Shallow clone, write JSON, delete clone by default:

```bash
insight-scan-external-repo \
  --url https://github.com/huggingface/trl.git \
  -o artifacts/trl_scan.json \
  --exclude tests,examples
```

Default output path without `-o`: `results/scan_results.json`.

Keep the clone under `/tmp`:

```bash
insight-scan-external-repo --no-cleanup
```

---

## Scan JSON fields

- `scan_count` — number of `.py` files scanned
- `categories` — path buckets
- `ml_ranked` — `[{path, score}, ...]` sorted by score
- `ml_ranked_count` — files with score ≥ threshold (default 0.15)
