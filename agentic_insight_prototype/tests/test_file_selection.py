import json
from pathlib import Path

from insight_proto.tools import file_selection as fs


def test_scan_and_rank(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "train.py").write_text("import torch\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")

    paths = fs.scan_repository(str(tmp_path))
    assert "src/train.py" in paths
    assert "README.md" not in paths

    cats = fs.categorize_paths(paths)
    assert "src/train.py" in cats["package_code"]

    ranked = fs.rank_ml_files(str(tmp_path), paths, min_score=0.1)
    assert any(r["path"] == "src/train.py" for r in ranked)


def test_orchestrator_pipeline(tmp_path: Path) -> None:
    from insight_proto.orchestrator.pipeline import run_file_selection

    (tmp_path / "model.py").write_text("from sklearn import datasets\n", encoding="utf-8")
    out = run_file_selection(tmp_path)
    assert out["scan_count"] >= 1
    assert out["ml_ranked_count"] >= 1
    data = json.loads(json.dumps(out))
    assert "categories" in data


def test_apply_excludes() -> None:
    paths = [
        "trl/trainer/ppo_trainer.py",
        "tests/test_something.py",
        "examples/scripts/train.py",
        "src/package/module.py",
    ]
    kept = fs.apply_excludes(paths, ("tests", "examples"))
    assert "tests/test_something.py" not in kept
    assert "examples/scripts/train.py" not in kept
    assert "trl/trainer/ppo_trainer.py" in kept
    assert "src/package/module.py" in kept
