"""Structural and offered-reference validation; never a semantic oracle."""

import json
from jsonschema import Draft202012Validator

STATUSES = ["Satisfied", "Partially satisfied", "Not satisfied", "Not determinable"]


def result_schema(target):
    string = {"type": "string"}
    array = {"type": "array", "items": string}
    refs = {
        "acn_target": {"type": "string", "enum": [target]},
        **{
            k: array
            for k in ["acn_context", "question_answers", "company_records", "enisa_passages"]
        },
    }
    properties = {
        "requirement_id": {"type": "string", "enum": [target]},
        "status": {"type": "string", "enum": STATUSES},
        "reason": string,
        "source_ids": {
            "type": "object",
            "properties": refs,
            "required": list(refs),
            "additionalProperties": False,
        },
        "missing_information": array,
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def parse_json(text):
    def pairs(items):
        obj = {}
        for k, v in items:
            if k in obj:
                raise ValueError(f"Duplicate JSON key: {k}")
            obj[k] = v
        return obj

    def reject(value):
        raise ValueError(f"Non-JSON numeric value: {value}")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=reject)


def validate_result(result, context):
    errors = list(Draft202012Validator(result_schema(context["target"]["id"])).iter_errors(result))
    if errors:
        # Do not echo model strings or unexpected content into logs.
        raise ValueError("Result schema validation failed at " + "/".join(map(str, errors[0].path)))
    norm = context["acn_context"]
    allowed = {
        "acn_context": {x["citation"]["id"] for x in norm["internal"] + norm["external"]},
        "question_answers": {x["question_id"] for x in context["linked_question_answers"]},
        "company_records": {x["id"] for x in context["company_records"]},
        "enisa_passages": {x["passage_id"] for x in context["enisa_guidance"]},
    }
    for field, ids in allowed.items():
        cited = result["source_ids"][field]
        if len(cited) != len(set(cited)) or not set(cited).issubset(ids):
            raise ValueError(f"Invalid, unoffered, wrong-type or duplicate references: {field}")
    if not result["reason"].strip() or any(not x.strip() for x in result["missing_information"]):
        raise ValueError("Blank rationale or missing-information entry")
    if result["status"] == "Not determinable" and not result["missing_information"]:
        raise ValueError("Not determinable requires specific missing information")
    if result["status"] != "Not determinable" and not (
        result["source_ids"]["question_answers"] or result["source_ids"]["company_records"]
    ):
        raise ValueError("A determinate judgment requires company evidence references")
    return result
