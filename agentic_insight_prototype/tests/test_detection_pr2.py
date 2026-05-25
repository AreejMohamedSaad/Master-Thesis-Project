from pathlib import Path

import pytest

from insight_proto.detectors.pr2 import detect_pr2_logging
from insight_proto.orchestrator.pipeline import run_detection


def test_detect_pr2_present(tmp_path: Path) -> None:
    target = tmp_path / "trainer.py"
    target.write_text(
        "import logging\n\n"
        "logger = logging.getLogger(__name__)\n\n"
        "def train():\n"
        '    logger.info("epoch", extra={"step": 1})\n',
        encoding="utf-8",
    )

    result = detect_pr2_logging(target)

    assert result["rule_id"] == "PR2"
    assert result["verdict"] == "present"
    assert result["confidence"] in {"medium", "high"}
    assert result["signal_counts"]["runtime"] >= 1
    assert any("logger" in e["snippet"] for e in result["evidence"])


def test_detect_pr2_accelerate_setup_only_unclear(tmp_path: Path) -> None:
    target = tmp_path / "utils.py"
    target.write_text(
        "from accelerate import PartialState, logging\n\n"
        "logger = logging.get_logger(__name__)\n",
        encoding="utf-8",
    )

    result = detect_pr2_logging(target)

    assert result["verdict"] == "unclear"
    assert result["signal_counts"]["runtime"] == 0
    assert result["signal_counts"]["setup"] >= 1


def test_detect_pr2_logging_warning_present(tmp_path: Path) -> None:
    target = tmp_path / "utils.py"
    target.write_text(
        "import logging\n\n"
        'logging.warning("no layers matched")\n',
        encoding="utf-8",
    )

    result = detect_pr2_logging(target)

    assert result["verdict"] == "present"
    assert result["signal_counts"]["runtime"] >= 1


def test_detect_pr2_unclear_print_only(tmp_path: Path) -> None:
    target = tmp_path / "debug.py"
    target.write_text('def run():\n    print("debug")\n', encoding="utf-8")

    result = detect_pr2_logging(target)

    assert result["verdict"] == "unclear"
    assert result["confidence"] == "low"
    assert result["signal_counts"]["runtime"] == 0
    assert result["signal_counts"]["weak"] >= 1


def test_detect_pr2_skips_doctest_print(tmp_path: Path) -> None:
    target = tmp_path / "docs.py"
    target.write_text(
        '"""Example:\n>>> print("x")\n"""\n'
        "from accelerate import logging\n"
        "logger = logging.get_logger(__name__)\n",
        encoding="utf-8",
    )

    result = detect_pr2_logging(target)

    assert result["verdict"] == "unclear"
    assert result["signal_counts"]["weak"] == 0


def test_detect_pr2_trainer_subclass_unclear(tmp_path: Path) -> None:
    target = tmp_path / "dppo_trainer.py"
    target.write_text(
        "class DPPOTrainer(GRPOTrainer):\n"
        "    def train(self):\n"
        "        return 1\n",
        encoding="utf-8",
    )

    result = detect_pr2_logging(target)

    assert result["verdict"] == "unclear"
    assert any(e["signal"] == "trainer_subclass" for e in result["evidence"])


def test_detect_pr2_absent(tmp_path: Path) -> None:
    target = tmp_path / "plain.py"
    target.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

    result = detect_pr2_logging(target)

    assert result["verdict"] == "absent"
    assert result["confidence"] == "high"
    assert result["evidence"] == []


def test_detect_pr2_missing_file(tmp_path: Path) -> None:
    result = detect_pr2_logging(tmp_path / "missing.py")

    assert result["verdict"] == "absent"
    assert "error" in result


def test_run_detection_pipeline(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "train.py").write_text(
        "import logging\n"
        "logger = logging.getLogger(__name__)\n"
        'logger.info("start")\n',
        encoding="utf-8",
    )
    (tmp_path / "src" / "utils.py").write_text("def noop():\n    pass\n", encoding="utf-8")

    report = run_detection(tmp_path, rules=("PR2",), ml_min_score=0.0)

    assert report["rules"] == ["PR2"]
    assert report["files_scanned"] >= 1
    assert "PR2" in report["summary"]
    assert report["summary"]["PR2"]["present"] >= 1
    assert any(f["verdict"] == "present" for f in report["findings"])


def test_run_detection_unknown_rule(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown rule ids"):
        run_detection(tmp_path, paths=["a.py"], rules=("PR99",))
