import json
from pathlib import Path

from insight_proto.cli.run_detection import load_scan_paths


def test_load_scan_paths(tmp_path: Path) -> None:
    scan = {
        "root": "/tmp/old",
        "ml_ranked": [
            {"path": "a.py", "score": 0.9},
            {"path": "b.py", "score": 0.8},
            {"path": "c.py", "score": 0.7},
        ],
    }
    scan_file = tmp_path / "scan.json"
    scan_file.write_text(json.dumps(scan), encoding="utf-8")

    paths, meta = load_scan_paths(scan_file)
    assert paths == ["a.py", "b.py", "c.py"]
    assert meta["paths_used"] == 3

    top_paths, top_meta = load_scan_paths(scan_file, top=2)
    assert top_paths == ["a.py", "b.py"]
    assert top_meta["paths_used"] == 2


def test_load_scan_paths_missing_ml_ranked(tmp_path: Path) -> None:
    scan_file = tmp_path / "scan.json"
    scan_file.write_text("{}", encoding="utf-8")
    try:
        load_scan_paths(scan_file)
        raised = False
    except ValueError as exc:
        raised = True
        assert "ml_ranked" in str(exc)
    assert raised
