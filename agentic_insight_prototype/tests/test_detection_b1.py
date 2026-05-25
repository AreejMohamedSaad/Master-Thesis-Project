from pathlib import Path

import pytest

from insight_proto.detectors.b1 import detect_b1_routing
from insight_proto.orchestrator.pipeline import run_detection


def test_detect_b1_present_supervisor_class(tmp_path: Path) -> None:
    target = tmp_path / "agents.py"
    target.write_text(
        "class SupervisorAgent:\n"
        "    def route(self, task: str) -> str:\n"
        "        return 'coder'\n",
        encoding="utf-8",
    )

    result = detect_b1_routing(target)

    assert result["verdict"] == "present"
    assert result["signal_counts"]["named"] >= 1


def test_detect_b1_present_many_keywords(tmp_path: Path) -> None:
    target = tmp_path / "flow.py"
    target.write_text(
        "def run():\n"
        "  handoff(to='a')\n"
        "  delegate(task)\n"
        "  dispatch(next_agent)\n",
        encoding="utf-8",
    )

    result = detect_b1_routing(target)

    assert result["verdict"] == "present"
    assert result["signal_counts"]["keyword_types"] >= 3


def test_detect_b1_present_path_boost(tmp_path: Path) -> None:
    target = tmp_path / "supervisor.py"
    target.write_text("def run():\n    pass\n", encoding="utf-8")

    result = detect_b1_routing(target)

    assert result["verdict"] == "present"
    assert result["signal_counts"]["path_boost"] == 1


def test_detect_b1_present_langgraph(tmp_path: Path) -> None:
    target = tmp_path / "graph.py"
    target.write_text(
        "from langgraph.graph import StateGraph\n"
        "g = StateGraph(dict)\n"
        "g.add_conditional_edges('router', pick)\n",
        encoding="utf-8",
    )

    result = detect_b1_routing(target)

    assert result["verdict"] == "present"
    assert result["signal_counts"]["named"] >= 1


def test_detect_b1_unclear_single_keyword(tmp_path: Path) -> None:
    target = tmp_path / "weak.py"
    target.write_text('message = "handoff complete"\n', encoding="utf-8")

    result = detect_b1_routing(target)

    assert result["verdict"] == "unclear"
    assert result["signal_counts"]["keyword_types"] == 1


def test_detect_b1_absent(tmp_path: Path) -> None:
    target = tmp_path / "plain.py"
    target.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

    result = detect_b1_routing(target)

    assert result["verdict"] == "absent"
    assert result["evidence"] == []


def test_detect_b1_missing_file(tmp_path: Path) -> None:
    result = detect_b1_routing(tmp_path / "missing.py")

    assert result["verdict"] == "absent"
    assert "error" in result


def test_run_detection_all_three_rules(tmp_path: Path) -> None:
    (tmp_path / "agent.py").write_text(
        "import logging\n"
        "logger = logging.getLogger(__name__)\n"
        "logger.info('step')\n\n"
        "class Router:\n"
        "    def handoff(self):\n"
        "        delegate()\n"
        "        dispatch(next_agent)\n",
        encoding="utf-8",
    )

    report = run_detection(tmp_path, paths=["agent.py"], rules=("PR2", "PR8", "B1"))

    assert report["summary"]["B1"]["present"] == 1
    assert len(report["findings"]) == 3


def test_run_detection_unknown_rule(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown rule ids"):
        run_detection(tmp_path, paths=["a.py"], rules=("B1", "PR99"))
