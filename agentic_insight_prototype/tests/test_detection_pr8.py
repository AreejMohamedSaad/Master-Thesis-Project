from pathlib import Path

import pytest

from insight_proto.detectors.pr8 import detect_pr8_validation
from insight_proto.orchestrator.pipeline import run_detection


def test_detect_pr8_present_handoff_gate(tmp_path: Path) -> None:
    target = tmp_path / "orchestrator.py"
    target.write_text(
        "def handoff(output):\n"
        "    if not output.get('result'):\n"
        "        raise ValueError('empty handoff payload')\n",
        encoding="utf-8",
    )

    result = detect_pr8_validation(target)

    assert result["verdict"] == "present"
    assert result["signal_counts"]["gate"] >= 1


def test_detect_pr8_present_pydantic(tmp_path: Path) -> None:
    target = tmp_path / "schema.py"
    target.write_text(
        "from pydantic import BaseModel\n\n"
        "class Handoff(BaseModel):\n"
        "    result: str\n",
        encoding="utf-8",
    )

    result = detect_pr8_validation(target)

    assert result["verdict"] == "present"
    assert result["confidence"] in {"medium", "high"}


def test_detect_pr8_present_check_server(tmp_path: Path) -> None:
    target = tmp_path / "client.py"
    target.write_text(
        "class Client:\n"
        "    def check_server(self, timeout: float = 0.0):\n"
        "        pass\n",
        encoding="utf-8",
    )

    result = detect_pr8_validation(target)

    assert result["verdict"] == "present"
    assert any(e["signal"] == "check_server" for e in result["evidence"])


def test_detect_pr8_unclear_setup_raise(tmp_path: Path) -> None:
    target = tmp_path / "trainer.py"
    target.write_text(
        "class Trainer:\n"
        "    def __init__(self):\n"
        '        raise ValueError("`train_dataset` is required")\n',
        encoding="utf-8",
    )

    result = detect_pr8_validation(target)

    assert result["verdict"] == "unclear"
    assert result["signal_counts"]["gate"] == 0


def test_detect_pr8_unclear_if_only(tmp_path: Path) -> None:
    target = tmp_path / "weak.py"
    target.write_text(
        "def run(x):\n"
        "    if not x:\n"
        "        return None\n",
        encoding="utf-8",
    )

    result = detect_pr8_validation(target)

    assert result["verdict"] == "unclear"
    assert result["signal_counts"]["gate"] == 0
    assert result["signal_counts"]["weak"] >= 1


def test_detect_pr8_absent(tmp_path: Path) -> None:
    target = tmp_path / "plain.py"
    target.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

    result = detect_pr8_validation(target)

    assert result["verdict"] == "absent"
    assert result["evidence"] == []


def test_detect_pr8_missing_file(tmp_path: Path) -> None:
    result = detect_pr8_validation(tmp_path / "missing.py")

    assert result["verdict"] == "absent"
    assert "error" in result


def test_run_detection_pr2_and_pr8(tmp_path: Path) -> None:
    (tmp_path / "agent.py").write_text(
        "import logging\n"
        "logger = logging.getLogger(__name__)\n"
        "logger.info('step')\n\n"
        "def go(data):\n"
        "    if not data:\n"
        "        raise ValueError('missing data')\n",
        encoding="utf-8",
    )

    report = run_detection(tmp_path, paths=["agent.py"], rules=("PR2", "PR8"))

    assert report["summary"]["PR2"]["present"] == 1
    assert report["summary"]["PR8"]["unclear"] == 1
    assert len(report["findings"]) == 2


def test_run_detection_unknown_rule_pr8_ok(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown rule ids"):
        run_detection(tmp_path, paths=["a.py"], rules=("PR8", "PR99"))
