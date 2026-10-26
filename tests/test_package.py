"""Behavioral checks with synthetic replies, not expected compliance answers."""

import copy
import json

import pytest

from nis2_academy.cli import main
from nis2_academy.context import (
    assessment_prompt,
    build_context,
    load_case,
    matching_prompt,
    no_leakage,
)
from nis2_academy.model import ModelError, client_input
from nis2_academy.sources import RESOURCES, read
from nis2_academy.validation import parse_json, result_schema, validate_result


@pytest.fixture
def context():
    return build_context("PR.AA-03_P2")


def synthetic_reply(context):
    target = context["target"]["id"]
    return {
        "requirement_id": target,
        "status": "Not determinable",
        "reason": "Synthetic response used solely to exercise validation.",
        "source_ids": {
            "acn_target": target,
            "acn_context": [],
            "question_answers": [],
            "company_records": [],
            "enisa_passages": [],
        },
        "missing_information": ["Synthetic unanswered question."],
    }


def test_all_contexts_have_full_dossier_and_only_selected_answers():
    _, graph, _, dossier, questions, answers, _, _ = load_case()
    for rid in graph["assessment_target_ids"]:
        c = build_context(rid)
        assert c["company_records"] == dossier["records"]
        assert len(c["company_records"]) == 20
        for q in c["linked_question_answers"]:
            assert q["question_text"] == questions[q["question_id"]]["text"]
            assert q["selected_value"] == answers[q["question_id"]]["selected_value"]
            assert "options" not in q and "options_text" not in q
        p = assessment_prompt(c, result_schema(rid))
        assert "{{" not in p
        for marker in [
            "expected_status",
            "teacher_expectations",
            "assessment-results.json",
            "EV3-",
            "V6-E",
        ]:
            assert marker not in p
        assert not any(key in p for key in ['"historical_result"', '"target_distribution"'])
        no_leakage(c)


def test_no_answer_leakage_guard():
    with pytest.raises(ValueError):
        no_leakage({"nested": [{"expected_status": "Satisfied"}]})


def test_outside_scope_and_unknown_are_distinct():
    with pytest.raises(ValueError, match="Unknown ACN"):
        build_context("MADE-UP")
    with pytest.raises(ValueError, match="outside the 27"):
        build_context("GV.PO-01_P1")


def test_dependency_direction_and_transitivity():
    c = build_context("PR.AA-03_P2")
    n = c["acn_context"]
    assert n["external"]
    assert any(len(p["edge_keys"]) > 1 for e in n["external"] for p in e["reference_paths"])
    graph = read("graph.json")
    edges = {e["key"]: e for e in graph["edges"]}
    for entry in n["internal"] + n["external"]:
        assert entry["citation"]["id"] != "PR.AA-03_P2"
        for path in entry["reference_paths"]:
            assert path["node_ids"][0] == "acn:PR.AA-03_P2"
            for i, key in enumerate(path["edge_keys"]):
                assert edges[key]["source"] == path["node_ids"][i]
                assert edges[key]["target"] == path["node_ids"][i + 1]
    # The referencing point is not pulled in by reverse traversal.
    assert not build_context("GV.RR-02_P1")["acn_context"]["internal"]
    assert build_context("GV.RR-02_P3")["acn_context"]["unresolved_external_documents"]


def test_enisa_paths_and_editorial_filter():
    _, graph, _, _, _, _, routes, _ = load_case()
    for rid in graph["assessment_target_ids"]:
        c = build_context(rid)
        guidance = c["enisa_guidance"]
        assert {p["passage_id"] for p in guidance} == set(routes[rid])
        assert len(guidance) == len(set(p["passage_id"] for p in guidance))
        for p in guidance:
            assert p["printed_page"] == p["page"] - 1
            assert p["matching_paths"]
            for path in p["matching_paths"]:
                assert path["edges"][0]["source"] == path["edges"][1]["source"]
                assert path["edges"][0]["target"] == "acn:" + rid
                assert path["edges"][1]["target"] == "enisa:" + p["kg_node_id"]
    assert build_context("DE.CM-01_P5")["enisa_guidance"] == []


def test_matching_is_offline_and_has_all_options():
    p = matching_prompt("mfa_implementation_status")
    assert "{{" not in p
    q = next(
        q for q in read("questionnaire.json")["questions"] if q["id"] == "mfa_implementation_status"
    )
    for option in q["options"]:
        assert json.dumps(option["value"]) in p
        assert option["label"] in p
    assert '"selected_value"' not in p and '"company_records"' not in p


def test_valid_structure(context):
    r = synthetic_reply(context)
    assert validate_result(r, context) == r


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.update(status="Compliant"),
        lambda r: r.update(requirement_id="GV.RR-02_P1"),
        lambda r: r.update(reason=" "),
        lambda r: r.update(missing_information=[]),
        lambda r: r.update(extra_field=True),
        lambda r: r["source_ids"].update(company_records=["AR-99"]),
        lambda r: r["source_ids"].update(company_records=["AR-01", "AR-01"]),
        lambda r: r["source_ids"].update(company_records=["V5-ENISA-0051-01"]),
        lambda r: r["source_ids"].update(enisa_passages=["V5-ENISA-0004-01"]),
        lambda r: r["source_ids"].update(question_answers=["ciso_appointment_status"]),
        lambda r: r.update(status="Satisfied"),
    ],
)
def test_invalid_outputs(context, mutation):
    r = copy.deepcopy(synthetic_reply(context))
    mutation(r)
    with pytest.raises(ValueError):
        validate_result(r, context)


@pytest.mark.parametrize("text", ['{"a":1,"a":2}', '{"a":NaN}', "```json\n{}\n```", "not JSON"])
def test_strict_json(text):
    with pytest.raises(ValueError):
        parse_json(text)


def test_cli_stdout_json_and_errors(capsys):
    assert main(["context", "GV.RR-02_P1"]) == 0
    out = capsys.readouterr()
    assert json.loads(out.out)["target"]["id"] == "GV.RR-02_P1"
    assert out.out.startswith('{\n  "') and out.err == ""
    assert main(["context", "MISSING"]) == 2
    out = capsys.readouterr()
    assert out.out == "" and json.loads(out.err)["error"] == "ValueError"


def test_cli_run_persistence_and_no_overwrite(monkeypatch, tmp_path, capsys):
    from nis2_academy.api import APIConfig

    monkeypatch.setattr(
        "nis2_academy.cli.load_api_config",
        lambda *a, **k: APIConfig("https://mock.example/v1", "synthetic-key", "test"),
    )
    c = build_context("PR.AA-03_P2")
    monkeypatch.setattr(
        "nis2_academy.cli.api_completion",
        lambda *args: (synthetic_reply(c), {"backend": "synthetic test"}),
    )
    out = tmp_path / "run"
    assert main(["assess", "PR.AA-03_P2", "--out", str(out)]) == 0
    emitted = capsys.readouterr()
    assert json.loads(emitted.out) == json.loads((out / "result.json").read_text())
    meta = json.loads((out / "manifest.json").read_text())
    assert meta["status"] == "validated" and meta["semantic_review_required"]
    assert (out / "client-input.txt").read_text() == client_input((out / "prompt.txt").read_text())
    assert main(["assess", "PR.AA-03_P2", "--out", str(out)]) == 2
    capsys.readouterr()


def test_failed_run_has_no_assessment(monkeypatch, tmp_path, capsys):
    from nis2_academy.api import APIConfig

    monkeypatch.setattr(
        "nis2_academy.cli.load_api_config",
        lambda *a, **k: APIConfig("https://mock.example/v1", "synthetic-key", "test"),
    )

    def fail(*args):
        raise ModelError("synthetic client failure")

    monkeypatch.setattr("nis2_academy.cli.api_completion", fail)
    out = tmp_path / "failed"
    assert main(["assess", "PR.AA-03_P2", "--out", str(out)]) == 3
    assert not (out / "result.json").exists()
    assert (
        json.loads((out / "manifest.json").read_text())["status"] == "failed_no_assessment_accepted"
    )
    assert capsys.readouterr().out == ""


def test_integrity_tampering(tmp_path):
    from nis2_academy.sources import verify_integrity

    (tmp_path / "integrity.json").write_text(json.dumps({"dossier.json": "wrong"}))
    (tmp_path / "dossier.json").write_text("{}")
    with pytest.raises(ValueError, match="integrity"):
        verify_integrity(tmp_path)


def test_no_secret_files_packaged():
    assert not any(p.name.startswith(".env") for p in RESOURCES.rglob("*"))
