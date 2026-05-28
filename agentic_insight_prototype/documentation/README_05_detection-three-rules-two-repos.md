# Documentation 05: PR2, PR8, B1 on TRL and CrewAI

Runs all three detectors on two repos. See [README_03](README_03_detection-v1-pr2.md) and [README_04](README_04_detection-v1-pr8.md).

| Repo | Role |
|------|------|
| [huggingface/trl](https://github.com/huggingface/trl) | ML trainers; PR2/PR8 common, B1 rare |
| [crewAIInc/crewAI-examples](https://github.com/crewAIInc/crewAI-examples) | Crews/flows; B1 more common |

---

## Detectors

| ID | File | Version |
|----|------|---------|
| PR2 | `detectors/pr2.py` | v1.1 |
| PR8 | `detectors/pr8.py` | v1.1 |
| B1 | `detectors/b1.py` | v1 |

PR6, B5: catalog only (`docs/CATALOG.md`).

---

## CLI

```bash
python -m insight_proto.cli.run_detection \
  --scan results/<scan>.json \
  --root ~/code/<repo> \
  --rules PR2,PR8,B1 \
  -o results/detection_report_<name>.json
```

---

## TRL (top 15 `ml_ranked`)

**Scan:** `results/2026-04-30_trl_core_scan.json`  
**Clone:** `~/code/trl`  
**Report:** `results/detection_report_trl_top15_pr2_pr8_b1.json`

| Rule | present | unclear | absent |
|------|---------|---------|--------|
| PR2 | 12 | 2 | 1 |
| PR8 | 5 | 10 | 0 |
| B1 | 0 | 1 | 14 |

TRL is a training library, not an orchestration repo. B1 absent on most files is expected.

Ground truth CSVs for PR2/PR8 on this set: 15/15 agreement (see README_03, README_04).

---

## CrewAI examples (31 files)

```bash
git clone --depth 1 https://github.com/crewAIInc/crewAI-examples.git ~/code/crewai-examples
```

Default scan (`ml_min_score=0.15`) kept only **11** files (mostly `agents.py`). ML path/content scoring misses many agent entrypoints.

For this run: `min_score=0.0` plus extra paths:

- `integrations/CrewAI-LangGraph/src/graph.py`
- `integrations/CrewAI-LangGraph/src/nodes.py`
- `integrations/CrewAI-LangGraph/src/crew/crew.py`
- `crews/*/crew.py`, some `flows/*/main.py`

**Report:** `results/detection_report_crewai_examples_pr2_pr8_b1.json`

| Rule | present | unclear | absent |
|------|---------|---------|--------|
| PR2 | 2 | 9 | 20 |
| PR8 | 4 | 6 | 21 |
| B1 | 8 | 2 | 21 |

B1 present examples: `graph.py` (`StateGraph`, `add_conditional_edges`), crew modules.

---

## TRL vs CrewAI

| | TRL | CrewAI |
|---|-----|--------|
| PR2 | common | sparse |
| PR8 | many setup raises | some flow checks |
| B1 | almost absent | present in graph/crew files |

Same detectors, different counts. File selection tuned for ML repos under-ranks `crew.py` / `graph.py` unless threshold or paths are adjusted.

---

## Reproduce CrewAI run

```bash
cd agentic_insight_prototype
source .venv/bin/activate

python - <<'PY'
from pathlib import Path
import json
from insight_proto.tools import file_selection as fs
from insight_proto.orchestrator.pipeline import run_detection

root = Path.home() / "code/crewai-examples"
paths = fs.apply_excludes(fs.scan_repository(str(root)), ("tests",))
ranked = [r["path"] for r in fs.rank_ml_files(str(root), paths, min_score=0.0)[:25]]
extra = [
    "integrations/CrewAI-LangGraph/src/graph.py",
    "integrations/CrewAI-LangGraph/src/nodes.py",
    "integrations/CrewAI-LangGraph/src/crew/crew.py",
    "crews/recruitment/src/recruitment/crew.py",
    "flows/lead-score-flow/src/lead_score_flow/main.py",
]
rel = list(dict.fromkeys(ranked + extra))
report = run_detection(root, paths=rel, rules=("PR2", "PR8", "B1"))
out = Path("results/detection_report_crewai_examples_pr2_pr8_b1.json")
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("wrote", out)
print(json.dumps(report["summary"], indent=2))
PY
```

---

## Limits

- ML-biased file selection; CrewAI needed manual path additions.
- No ground truth CSV for CrewAI.
- PR6, B5 not implemented.
- Regex detectors only.

---

## Tests

```bash
pytest tests/test_detection_pr2.py tests/test_detection_pr8.py tests/test_detection_b1.py -q
```

33 tests.
