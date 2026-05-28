# Documentation 03: PR2 detection (runtime logs / traces)

PR2 heuristic detector on file-selected paths. Requires [README_01](README_01_file-selection-and-mcp.md) (file selection) and `docs/CATALOG.md` (rule definition).

---

## Components

| Piece | Location |
|-------|----------|
| PR2 detector | `src/insight_proto/detectors/pr2.py` |
| `run_detection()` | `src/insight_proto/orchestrator/pipeline.py` |
| CLI | `insight-run-detection` → `src/insight_proto/cli/run_detection.py` |
| Ground truth | `scripts/generate_ground_truth_template.py`, `scripts/compare_ground_truth.py` |
| PR8, B1 | `README_04`, `README_05` |

---

## Flow

```text
scan JSON or repo  →  ml_ranked paths  →  detect_pr2_logging  →  detection_report.json
                                                              →  ground_truth CSV (manual status)
                                                              →  compare_ground_truth.py
```

---

## PR2 rule

**Practice:** runtime logs / traces (Ntentos & Zdun PR2).

**In code:** logging calls, `wandb.log`, etc. Missing traces relate to observability smells in `resourses/topic.tex`.

Full spec: `docs/CATALOG.md` (PR2).

---

## Detector (v1.1)

| Bucket | Examples | Verdict |
|--------|----------|---------|
| Runtime | `logger.info`, `logging.warning`, `wandb.log`, `wandb.run` | present |
| Setup only | `import logging`, `get_logger` without calls | unclear |
| Weak | `print(`, trace keywords; doctest `>>>` ignored | unclear alone |

Trainer subclass with no local logging → **unclear** (may inherit from parent).

Verdicts: `present` | `unclear` | `absent`. Confidence: `high` | `medium` | `low`.

---

## Ground truth labels (TRL top 15)

Manual `status` in CSV after reading each file:

1. **present** — runtime trace in file (`logger.*`, `logging.*`, `wandb.log`), including guarded `wandb.log`.
2. **unclear** — setup only, subclass with no local logs, or weak `print` only.
3. **absent** — no logging code (comments/help text do not count).

**PPO:** `ppo_trainer.py` has conditional `wandb.log` like `gold_trainer.py` → labeled **present**, confidence medium.

**Result:** 15/15 agreement with detector on the labeled set.

---

## Run

```bash
source .venv/bin/activate

python -m insight_proto.cli.run_detection \
  --scan results/2026-04-30_trl_core_scan.json \
  --root ~/code/trl \
  --top 15 \
  -o results/detection_report_trl_top15_v2.json

python scripts/generate_ground_truth_template.py \
  --report results/detection_report_trl_top15_v2.json \
  -o results/ground_truth_detection_report_trl_top15.csv

# Fill status and notes in the CSV, then:

python scripts/compare_ground_truth.py \
  --csv results/ground_truth_detection_report_trl_top15.csv \
  --report results/detection_report_trl_top15_v2.json \
  -o results/pr2_evaluation_trl_top15.json
```

---

## TRL results (top 15 `ml_ranked`)

| | Value |
|---|--------|
| Repo | [huggingface/trl](https://github.com/huggingface/trl), exclude tests/examples |
| Files | 15 |
| Detector | 12 present, 2 unclear, 1 absent |
| vs labels | 15/15 |

**Examples — present:** `vllm_client.py` (`logger.info`), `grpo_trainer.py` (`logger.warning`), `ppo_trainer.py` (conditional `wandb.log`).

**unclear:** `dppo_trainer.py` (subclass), `utils.py` (`get_logger` never called).

**absent:** `sdft.py` (CLI, no runtime logging in file).

---

## Limits

- File-level only; no inheritance into parent trainers.
- Regex/keywords only; no LLM.
- PR6, B5 not implemented.

---

## Tests

```bash
pytest tests/test_detection_pr2.py tests/test_run_detection_cli.py -q
```
