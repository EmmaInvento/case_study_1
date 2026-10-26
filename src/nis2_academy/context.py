"""Build only the evidence and reference context offered by the teaching case."""

from collections import defaultdict
import json
import re

from .sources import RESOURCES, read, verify_integrity

DEPENDENCIES = {"REQUIRES_CONTEXT_INTERNAL", "REQUIRES_CONTEXT_EXTERNAL", "HAS_POINT"}
RELATIONS = {"direct", "partial", "context"}
BANNED = {
    "expected_status",
    "expected_outcome",
    "expected_matches",
    "teacher_key",
    "teacher",
    "teacher_expected_distribution",
    "target_distribution",
    "historical_result",
}


def no_leakage(value):
    if isinstance(value, dict):
        if BANNED.intersection(value):
            raise ValueError("Expected-answer field in model input")
        for v in value.values():
            no_leakage(v)
    elif isinstance(value, list):
        for v in value:
            no_leakage(v)


def unique(items, key):
    result = {x[key]: x for x in items}
    if len(result) != len(items):
        raise ValueError(f"Duplicate source identifier: {key}")
    return result


def load_case(root=RESOURCES):
    hashes = verify_integrity(root)
    catalog = unique(read("acn.json", root)["requirements"], "id")
    graph = read("graph.json", root)
    nodes = unique(graph["nodes"], "key")
    unique(graph["edges"], "key")
    dossier = read("dossier.json", root)
    questions = unique(read("questionnaire.json", root)["questions"], "id")
    answers = unique(dossier["answers"], "question_id")
    if not dossier["fictional"] or len(dossier["records"]) != 20 or set(answers) != set(questions):
        raise ValueError("Incomplete fictional dossier")
    unique(dossier["records"], "id")
    for qid, q in questions.items():
        answer = answers[qid]
        selected = [o for o in q["options"] if o["value"] == answer["selected_value"]]
        if (
            len(selected) != 1
            or selected[0]["label"] != answer["selected_label"]
            or answer["question_text"] != q["text"]
        ):
            raise ValueError(f"Selected answer differs from questionnaire: {qid}")
        if condition := q.get("visible_if"):
            if answers[condition["question_id"]]["selected_value"] not in condition["values"]:
                raise ValueError(f"Answered hidden question: {qid}")
    for node in nodes.values():
        if node["type"] == "ACNRequirement":
            c = catalog[node["id"]]
            if (
                node["text"] != c["text"]
                or node["source_row"] != c["row"]
                or node["source_sheet"] != c["sheet"]
            ):
                raise ValueError(f"Graph/catalog mismatch: {node['id']}")
        if node["type"] == "Question" and node["text"] != questions[node["id"]]["text"]:
            raise ValueError(f"Graph/question mismatch: {node['id']}")
    for edge in graph["edges"]:
        if edge["source"] not in nodes or edge["target"] not in nodes:
            raise ValueError("Dangling graph edge")
        if edge.get("academy_acceptance_status") != "accepted_for_academy_use":
            raise ValueError("Unaccepted graph edge")
        if edge.get("relation") in DEPENDENCIES:
            if edge.get("review_status") != "editorially_reviewed":
                raise ValueError("Unreviewed dependency")
        elif edge.get("relation_display") not in RELATIONS:
            raise ValueError("Unknown matching relation")
    routes = read("enisa-routing.json", root)["by_requirement"]
    if set(routes) != set(graph["assessment_target_ids"]):
        raise ValueError("Editorial routing/target scope mismatch")
    return catalog, graph, nodes, dossier, questions, answers, routes, hashes


def dependencies(target, graph, nodes, catalog, register):
    adjacency = defaultdict(list)
    for edge in graph["edges"]:
        if edge.get("relation") in DEPENDENCIES:
            adjacency[edge["source"]].append(edge)
    found, cycles = {}, []

    def walk(keys, edges, relations):
        for edge in sorted(adjacency[keys[-1]], key=lambda e: e["key"]):
            child = edge["target"]
            path = {
                "node_ids": keys + [child],
                "edge_keys": edges + [edge["key"]],
                "relations": relations + [edge["relation"]],
            }
            if child in keys:
                cycles.append(path)
                continue
            n = nodes[child]
            if child not in found:
                if n["type"] == "ACNRequirement":
                    citation = {**catalog[n["id"]], "source_file": "acn.xlsx"}
                elif n["type"] == "ACNMeasure":
                    citation = {
                        "id": n["id"],
                        "measure_code": n["measure_code"],
                        "measure_description": n["measure_description"],
                        "source_file": "acn.xlsx",
                        "sheet": n["source_sheet"],
                        "source_rows": n["source_rows"],
                    }
                else:
                    raise ValueError("Non-ACN node in dependency context")
                found[child] = {
                    "citation": citation,
                    "reference_paths": [],
                    "role": "interpretation only; not company evidence or separate target",
                }
            found[child]["reference_paths"].append(path)
            walk(path["node_ids"], path["edge_keys"], path["relations"])

    walk(["acn:" + target], [], [])
    internal, external = [], []
    for _, entry in sorted(found.items()):
        bucket = (
            external
            if any("REQUIRES_CONTEXT_EXTERNAL" in p["relations"] for p in entry["reference_paths"])
            else internal
        )
        bucket.append(entry)
    reached = {target} | {v["citation"]["id"] for v in found.values()}
    unresolved = [
        r for r in register["out_of_catalogue_references"] if r["source_point_id"] in reached
    ]
    return {
        "internal": internal,
        "external": external,
        "unresolved_external_documents": unresolved,
        "cycles": cycles,
    }


def build_context(requirement_id, root=RESOURCES):
    catalog, graph, nodes, dossier, questions, answers, routes, hashes = load_case(root)
    if requirement_id not in catalog:
        raise ValueError(f"Unknown ACN ID: {requirement_id}")
    if requirement_id not in graph["assessment_target_ids"]:
        raise ValueError(
            f"ACN ID outside the 27 reviewed teaching targets: {requirement_id}; use list"
        )
    linked, candidate_paths = [], defaultdict(list)
    for edge in sorted(graph["edges"], key=lambda e: e["key"]):
        if edge["target"] != "acn:" + requirement_id or not edge["source"].startswith("q:"):
            continue
        qid = edge["source"][2:]
        linked.append(
            {
                "question_id": qid,
                "question_text": questions[qid]["text"],
                "selected_value": answers[qid]["selected_value"],
                "selected_label": answers[qid]["selected_label"],
                "relation": edge["relation_display"],
                "mapping_edge_key": edge["key"],
                "mapping_review_status": edge["review_status"],
                "academy_acceptance_status": edge["academy_acceptance_status"],
            }
        )
        for enisa_edge in graph["edges"]:
            if enisa_edge["source"] == edge["source"] and enisa_edge["target"].startswith("enisa:"):
                candidate_paths[enisa_edge["target"][6:]].append(
                    {
                        "path": ["acn:" + requirement_id, "q:" + qid, enisa_edge["target"]],
                        "traversal": "ACN <- question -> ENISA",
                        "edges": [
                            {
                                "key": e["key"],
                                "source": e["source"],
                                "target": e["target"],
                                "relation": e["relation_display"],
                                "review_status": e["review_status"],
                            }
                            for e in [edge, enisa_edge]
                        ],
                    }
                )
    pack = read("enisa-passages.json", root)
    passages = unique(pack["passages"], "passage_id")
    guidance = []
    for pid in sorted(set(routes[requirement_id])):
        p = passages[pid]
        if not candidate_paths[p["kg_node_id"]]:
            raise ValueError(f"Editorial ENISA passage lacks shared-question path: {pid}")
        guidance.append(
            {
                **p,
                "source_file": "enisa.pdf",
                "source_sha256": pack["source_pdf_sha256"],
                "printed_page": p["page"] - 1,
                "page_convention": "page is 1-based physical PDF page; printed_page is the printed label",
                "matching_paths": candidate_paths[p["kg_node_id"]],
                "role": "editorially filtered candidate guidance; not evidence of relevance or company compliance",
            }
        )
    norm = dependencies(requirement_id, graph, nodes, catalog, read("dependency-review.json", root))
    context = {
        "schema_version": 1,
        "target": {
            **catalog[requirement_id],
            "source_file": "acn.xlsx",
            "source_sha256": hashes["acn.xlsx"],
        },
        "acn_context": norm,
        "linked_question_answers": linked,
        "company": {
            k: dossier[k]
            for k in [
                "case_id",
                "fictional",
                "profile",
                "profile_assumption",
                "as_of_date",
                "description",
                "reading_notes",
            ]
        },
        "company_records": dossier["records"],
        "enisa_guidance": guidance,
        "enisa_retrieval": {
            "candidate_node_ids": sorted(candidate_paths),
            "selection": "historical editorial passage filter after shared-question traversal; empty selection is deliberate",
        },
        "source_sha256": {
            k: v for k, v in hashes.items() if k not in {"matching.txt", "assessment.txt"}
        },
    }
    no_leakage(context)
    return context


def substitute(template, values):
    needed = set(re.findall(r"\{\{([A-Z_]+)\}\}", template))
    if needed != set(values):
        raise ValueError(f"Template placeholders mismatch: {sorted(needed ^ set(values))}")
    return re.sub(
        r"\{\{([A-Z_]+)\}\}",
        lambda m: json.dumps(values[m[1]], ensure_ascii=False, indent=2),
        template,
    )


def assessment_prompt(context, schema, root=RESOURCES):
    norm = context["acn_context"]
    values = {
        "TARGET_ACN_POINT_ID_AND_TEXT": context["target"],
        "RELEVANT_INTERNAL_ACN_IDS_AND_TEXT": {
            "references": norm["internal"],
            "cycles": norm["cycles"],
        },
        "RELEVANT_EXTERNAL_ACN_IDS_AND_TEXT": {
            "references": norm["external"],
            "unresolved_external_documents": norm["unresolved_external_documents"],
        },
        "LINKED_QUESTION_TEXT_AND_AURORA_SELECTED_ANSWERS": context["linked_question_answers"],
        "DATED_COMPANY_RECORDS_WITH_AR_IDS_AND_TEXT": {
            "company": context["company"],
            "records": context["company_records"],
        },
        "VERIFIED_ENISA_PASSAGE_IDS_AND_TEXT": {
            "passages": context["enisa_guidance"],
            "retrieval": context["enisa_retrieval"],
        },
        "JSON_OUTPUT_FORMAT": schema,
    }
    no_leakage(values)
    return substitute((root / "assessment.txt").read_text(), values)


def matching_prompt(question_id, root=RESOURCES):
    catalog, _, _, _, questions, _, _, _ = load_case(root)
    q = questions[question_id]
    shape = {
        "acn_matches": [
            {
                "requirement_id": "offered ID",
                "relation_type": "direct | partial | context",
                "rationale": "reason",
                "self_reported_confidence": "high | medium | low",
            }
        ],
        "enisa_matches": [
            {
                "node_id": "offered ID",
                "relation_type": "direct | partial | context",
                "rationale": "reason",
                "self_reported_confidence": "high | medium | low",
            }
        ],
        "acn_no_match_reason": None,
        "enisa_no_match_reason": None,
    }
    return substitute(
        (root / "matching.txt").read_text(),
        {
            "QUESTION_PROMPT_ID": q["id"],
            "QUESTION_TEXT": q["text"],
            "ALL_OPTION_VALUE_LABEL_PAIRS": q["options"],
            "ESSENTIAL_ENTITY_PROFILE": "essenziale",
            "FULL_ACN_REQUIREMENT_CATALOG": list(catalog.values()),
            "ENISA_HIERARCHICAL_INDEX_NODES": read("enisa-index.json", root),
            "JSON_OUTPUT_FORMAT": shape,
        },
    )
