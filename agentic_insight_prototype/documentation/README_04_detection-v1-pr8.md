# Documentation 04: PR8 detection (validation between stages)

PR8 heuristic detector. Builds on [README_03](README_03_detection-v1-pr2.md). Rule definition: `docs/CATALOG.md` (PR8).

---

## Components

| Piece | Location |
|-------|----------|
| PR8 detector v1.1 | `src/insight_proto/detectors/pr8.py` |
| Ground truth (TRL top 15) | `results/ground_truth_pr8_trl_top15.csv` |

v1 (any `raise` → present) was replaced by v1.1 (gate vs setup).

---

## PR8 definition

Catalog PR8 = validation **between stages** (handoff/artifact checks), not every `raise ValueError` in a Trainer `__init__`.

| | v1 detector | Manual labels (TRL top 15) |
|---|-------------|----------------------------|
| Loose: any validation code? | 15/15 present | 4 present, 11 unclear |
| Agreement | | 4/15 (27%) |

v1 counted setup raises like `` `train_dataset` is required `` as present; labels marked those **unclear**. That is a definition mismatch, not a broken pipeline.

**Labeled present (4 files):** `vllm_client.py` (`check_server`), `sdft.py` (dataset columns), `dppo_trainer.py` (rollout keys), `distillation_trainer.py` (teacher input checks).

---

## Detector v1.1

| Bucket | Examples | Verdict |
|--------|----------|---------|
| gate | `check_server`, `validate_*`, raise text with must return keys / must contain / required when | present |
| generic | other `raise`/`assert` | unclear |
| weak | `if not` without gate pattern | unclear |

Setup phrases → unclear: `train_dataset`, `model_kwargs`, `processing_class`, `is required`, etc.

---

## Run

```bash
source .venv/bin/activate

python -m insight_proto.cli.run_detection \
  --scan results/2026-04-30_trl_core_scan.json \
  --root ~/code/trl --top 15 \
  --rules PR2,PR8 \
  -o results/detection_report_trl_top15_pr2_pr8_v11.json

python scripts/generate_ground_truth_template.py \
  --report results/detection_report_trl_top15_pr2_pr8_v11.json \
  --rule PR8 \
  -o results/ground_truth_pr8_trl_top15.csv

python scripts/compare_ground_truth.py \
  --csv results/ground_truth_pr8_trl_top15.csv \
  --report results/detection_report_trl_top15_pr2_pr8_v11.json \
  -o results/pr8_evaluation_trl_top15_v11.json
```

---

## TRL results (top 15)

| Version | Agreement | Counts |
|---------|-----------|--------|
| v1 | 4/15 | 15 present |
| v1.1 | 15/15 | 5 present, 10 unclear, 0 absent |

v1.1 present: `distillation_trainer.py`, `dppo_trainer.py`, `grpo_trainer.py`, `sdft.py`, `vllm_client.py`.

GRPO was relabeled **present** (same rollout/tool gates as DPPO).

---

## Limits

- File-level regex only.
- Multi-line `raise` messages not fully handled.
- TRL has few agent-style handoff gates; mostly trainer setup checks → unclear.

---

## Tests

```bash
pytest tests/test_detection_pr8.py -q
```

See [README_05](README_05_detection-three-rules-two-repos.md) for B1 and CrewAI.
