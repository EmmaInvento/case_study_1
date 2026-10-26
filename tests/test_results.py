"""Check saved outputs as artifacts, without using their judgments as model fixtures."""

import hashlib
import json
from pathlib import Path

from nis2_academy.context import build_context, load_case
from nis2_academy.validation import parse_json, validate_result


def test_saved_results_cover_supported_targets_and_validate():
    root = Path(__file__).resolve().parents[1] / "results"
    provenance = json.loads((root / "provenance.json").read_text())
    files = sorted(p for p in root.glob("*.json") if p.name != "provenance.json")
    target_ids = set(load_case()[1]["assessment_target_ids"])
    assert {p.stem for p in files} == target_ids
    assert len(files) == provenance["result_count"] == 27
    for path in files:
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == provenance["files_sha256"][path.name]
        result = parse_json(raw.decode("utf-8"))
        assert result["requirement_id"] == path.stem
        validate_result(result, build_context(path.stem))
