import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from . import __version__
from .api import api_completion, api_request_body, contains_credential, load_api_config
from .context import assessment_prompt, build_context, load_case, matching_prompt
from .model import ModelError, client_input
from .sources import RESOURCES, json_hash, read, verify_pdf, workbook
from .validation import parse_json, result_schema, validate_result


def formatted(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def write_new(path, content):
    with path.open("x", encoding="utf-8") as f:
        f.write(content)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Assess one of the 27 reviewed ACN teaching points"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List supported targets")
    verify = sub.add_parser("verify", help="Check packaged inputs offline")
    verify.add_argument(
        "--pdf", action="store_true", help="Re-extract all PDF excerpts; requires verify extra"
    )
    for name in ["context", "prompt", "schema", "assess", "validate-reply"]:
        p = sub.add_parser(name)
        p.add_argument("requirement_id")
        if name == "assess":
            p.add_argument("--model", help="API model identifier override")
            p.add_argument(
                "--env-file",
                type=Path,
                help="Exact API .env path; default: .env in current directory",
            )
            p.add_argument(
                "--response-format",
                choices=["json_schema", "json_object"],
                help="Explicit API output format override",
            )
            p.add_argument(
                "--reasoning-effort",
                choices=["none", "minimal", "low", "medium", "high", "xhigh"],
                help="Explicit API reasoning_effort; provider/model support required",
            )
            p.add_argument("--timeout", type=int, default=180)
            p.add_argument("--out", type=Path, help="New run directory; refuses existing paths")
        elif name == "validate-reply":
            p.add_argument("reply", type=Path)
    matching = sub.add_parser(
        "matching-prompt", help="Offline matching teaching prompt; no model call or graph mutation"
    )
    matching.add_argument("question_id")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            _, graph, _, _, _, _, _, _ = load_case()
            result = {"supported_target_ids": graph["assessment_target_ids"], "catalog_points": 116}
        elif args.command == "verify":
            catalog, graph, _, _, _, _, _, _ = load_case()
            if workbook(RESOURCES / "acn.xlsx", "Security Measures") != list(catalog.values()):
                raise ValueError("Processed ACN catalog differs from workbook")
            original = workbook(RESOURCES / "acn-it.xlsx", "Misure di sicurezza")
            if [(r["id"], r["row"]) for r in original] != [
                (r["id"], r["row"]) for r in catalog.values()
            ]:
                raise ValueError("ACN English/Italian row alignment differs")
            for rid in graph["assessment_target_ids"]:
                c = build_context(rid)
                assessment_prompt(c, result_schema(rid))
            result = {
                "catalog_points": len(catalog),
                "contexts_and_prompts_checked": len(graph["assessment_target_ids"]),
                "graph_nodes": len(graph["nodes"]),
                "graph_edges": len(graph["edges"]),
                "structural_checks": "passed",
                "semantic_correctness": "not established by these checks",
            }
            if args.pdf:
                result["pdf"] = verify_pdf()
        elif args.command == "matching-prompt":
            sys.stdout.write(matching_prompt(args.question_id))
            return 0
        else:
            c = build_context(args.requirement_id)
            schema = result_schema(args.requirement_id)
            if args.command == "context":
                result = c
            elif args.command == "schema":
                result = schema
            elif args.command == "prompt":
                sys.stdout.write(assessment_prompt(c, schema))
                return 0
            elif args.command == "validate-reply":
                result = validate_result(parse_json(args.reply.read_text(encoding="utf-8")), c)
            else:
                if args.timeout < 1:
                    raise ValueError("Timeout must be positive")
                prompt = assessment_prompt(c, schema)
                config = load_api_config(
                    args.env_file,
                    args.model,
                    args.response_format,
                    reasoning_effort=args.reasoning_effort,
                )
                if contains_credential(
                    {"context": c, "schema": schema, "prompt": client_input(prompt)}, config.api_key
                ):
                    raise ModelError(
                        "API credential unexpectedly occurs in assessment input; no artifacts written"
                    )
                run = args.out or Path("results/new") / (
                    datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
                    + "_"
                    + args.requirement_id
                )
                run.mkdir(parents=True, exist_ok=False)
                meta = {
                    "schema_version": 1,
                    "package_version": __version__,
                    "kind": "new_live_assessment",
                    "backend": "api",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "requirement_id": args.requirement_id,
                    "status": "started",
                    "context_sha256": json_hash(c),
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "client_input_sha256": hashlib.sha256(
                        client_input(prompt).encode()
                    ).hexdigest(),
                    "schema_sha256": json_hash(schema),
                    "source_sha256": read("integrity.json"),
                    "semantic_review_required": True,
                }
                write_new(run / "context.json", formatted(c))
                write_new(run / "prompt.txt", prompt)
                write_new(run / "client-input.txt", client_input(prompt))
                write_new(run / "schema.json", formatted(schema))
                request_body = api_request_body(prompt, schema, config)
                # Credentials are only HTTP headers; never persisted.
                write_new(run / "api-request.json", formatted(request_body))
                meta["api_request_sha256"] = json_hash(request_body)
                meta["client"] = config.public_metadata()
                try:
                    raw, client = api_completion(prompt, schema, config, args.timeout)
                    result = validate_result(raw, c)
                    write_new(run / "result.json", formatted(result))
                    meta.update(
                        status="validated",
                        client=client,
                        result_sha256=json_hash(result),
                        validation="JSON schema and offered-reference membership; not semantic certification",
                    )
                except (ModelError, ValueError) as failure:
                    meta["error"] = {"type": type(failure).__name__, "message": str(failure)}
                    meta["status"] = "failed_no_assessment_accepted"
                    raise
                finally:
                    meta["finished_at"] = datetime.now(timezone.utc).isoformat()
                    write_new(run / "manifest.json", formatted(meta))
                print(f"Saved new run: {run}", file=sys.stderr)
        sys.stdout.write(formatted(result))
        return 0
    except (ValueError, KeyError, OSError, ImportError, ModelError) as error:
        # Controlled failures always leave stdout empty; JSON diagnostics go to stderr.
        message = "Unknown question ID" if isinstance(error, KeyError) else str(error)
        sys.stderr.write(formatted({"error": type(error).__name__, "message": message}))
        return 3 if isinstance(error, ModelError) else 2
