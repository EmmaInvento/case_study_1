import json

import httpx
import pytest

from nis2_academy.api import APIConfig, api_completion, load_api_config
from nis2_academy.cli import main
from nis2_academy.context import assessment_prompt, build_context
from nis2_academy.model import ModelError, client_input
from nis2_academy.validation import result_schema

KEY = "synthetic-test-credential-only"


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name in [
        "OPENAI_BASE_URL",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "NIS2_RESPONSE_FORMAT",
        "OPENAI_REASONING_EFFORT",
    ]:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def config():
    return APIConfig("https://mock.example/v1", KEY, "test-model")


@pytest.fixture
def context():
    return build_context("PR.AA-03_P2")


def reply(c):
    rid = c["target"]["id"]
    return {
        "requirement_id": rid,
        "status": "Not determinable",
        "reason": "Synthetic API transport test.",
        "source_ids": {
            "acn_target": rid,
            "acn_context": [],
            "question_answers": [],
            "company_records": [],
            "enisa_passages": [],
        },
        "missing_information": ["Synthetic missing fact."],
    }


def envelope(c):
    return {
        "model": "test-model-snapshot",
        "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(reply(c))}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


def env_values():
    return {
        "OPENAI_BASE_URL": "https://mock.example/v1",
        "OPENAI_API_KEY": KEY,
        "OPENAI_MODEL": "env-model",
    }


def test_precedence_and_no_environment_mutation(tmp_path, monkeypatch):
    p = tmp_path / ".env"
    p.write_text(
        "OPENAI_BASE_URL=https://file.example/v1\nOPENAI_API_KEY=file-test-key\nOPENAI_MODEL=file-model\nNIS2_RESPONSE_FORMAT=json_object\n"
    )
    monkeypatch.setenv("OPENAI_MODEL", "environment-model")
    c = load_api_config()
    assert c.model == "environment-model" and c.api_key == "file-test-key"
    assert c.response_format == "json_object"
    assert load_api_config(model="cli-model", response_format="json_schema").model == "cli-model"
    import os

    assert "OPENAI_API_KEY" not in os.environ


def test_no_parent_search_and_explicit_path(tmp_path, monkeypatch):
    p = tmp_path / ".env"
    p.write_text("\n".join(k + "=" + v for k, v in env_values().items()))
    child = tmp_path / "child"
    child.mkdir()
    monkeypatch.chdir(child)
    with pytest.raises(ValueError, match="Missing API"):
        load_api_config()
    assert load_api_config(env_file=p).model == "env-model"
    with pytest.raises(ValueError, match="missing"):
        load_api_config(env_file=child / "absent")


def test_interpolation_disabled(tmp_path, monkeypatch):
    p = tmp_path / ".env"
    p.write_text(
        "OPENAI_BASE_URL=https://mock.example/v1\nOPENAI_MODEL=test\nOPENAI_API_KEY=${HIDDEN_TEST_VALUE}\n"
    )
    monkeypatch.setenv("HIDDEN_TEST_VALUE", "should-not-be-read")
    assert load_api_config().api_key == "${HIDDEN_TEST_VALUE}"


@pytest.mark.parametrize(
    "name,value",
    [
        ("OPENAI_BASE_URL", ""),
        ("OPENAI_API_KEY", ""),
        ("OPENAI_MODEL", ""),
        ("OPENAI_BASE_URL", "https://user:secret@mock.example/v1"),
        ("OPENAI_BASE_URL", "https://mock.example/v1?api_key=secret"),
        ("OPENAI_BASE_URL", "https://mock.example/v1#secret"),
        ("OPENAI_BASE_URL", "http://remote.example/v1"),
        ("OPENAI_BASE_URL", "https://mock.example/v1/chat/completions"),
        ("OPENAI_BASE_URL", "https://api.example.invalid/v1"),
        ("OPENAI_MODEL", KEY),
        ("OPENAI_API_KEY", "unsafe\nheader"),
        ("NIS2_RESPONSE_FORMAT", "automatic"),
    ],
)
def test_invalid_config_is_safe(name, value):
    env = env_values()
    env[name] = value
    with pytest.raises(ValueError) as e:
        load_api_config(environ=env)
    assert KEY not in str(e.value) and "unsafe\nheader" not in str(e.value)


def test_api_config_repr_hides_key(config):
    assert KEY not in repr(config)
    assert KEY not in json.dumps(config.public_metadata())


def test_request_endpoint_auth_schema_and_model(config, context):
    schema = result_schema(context["target"]["id"])
    prompt = assessment_prompt(context, schema)
    seen = []

    def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        assert str(request.url) == "https://mock.example/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer " + KEY
        assert KEY.encode() not in request.content
        assert body["model"] == "test-model"
        assert body["messages"] == [{"role": "user", "content": client_input(prompt)}]
        assert body["response_format"]["json_schema"]["schema"] == schema
        assert body["response_format"]["json_schema"]["strict"] is True
        assert "tools" not in body and "reasoning_effort" not in body
        return httpx.Response(200, json=envelope(context))

    result, meta = api_completion(prompt, schema, config, transport=httpx.MockTransport(handler))
    assert result == reply(context) and len(seen) == 1
    assert meta["returned_model"] == "test-model-snapshot"
    assert meta["usage"]["total_tokens"] == 30


def test_explicit_json_mode(context):
    c = APIConfig("https://mock.example/v1", KEY, "test", "json_object")

    def handler(req):
        assert json.loads(req.content)["response_format"] == {"type": "json_object"}
        return httpx.Response(200, json=envelope(context))

    api_completion(
        "prompt", result_schema("PR.AA-03_P2"), c, transport=httpx.MockTransport(handler)
    )


@pytest.mark.parametrize("status", [301, 307, 400, 401, 404, 422, 429, 500])
def test_http_errors_no_secrets_no_retry(config, status):
    count = []

    def handler(req):
        count.append(1)
        return httpx.Response(
            status, text=KEY, headers={"X-Secret": KEY, "Location": "https://elsewhere.example/"}
        )

    with pytest.raises(ModelError) as e:
        api_completion("prompt", {}, config, transport=httpx.MockTransport(handler))
    assert KEY not in str(e.value) and str(status) in str(e.value)
    assert len(count) == 1


@pytest.mark.parametrize(
    "error", [httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError]
)
def test_network_errors_safe(config, error):
    def handler(req):
        raise error("sensitive diagnostic " + KEY, request=req)

    with pytest.raises(ModelError) as e:
        api_completion("prompt", {}, config, transport=httpx.MockTransport(handler))
    assert KEY not in str(e.value)


@pytest.mark.parametrize(
    "fault",
    [
        "outer_json",
        "inner_json",
        "empty",
        "refusal",
        "length",
        "tools",
        "choices",
        "duplicate",
        "nan",
        "secret",
        "secret_escaped",
        "error_object",
    ],
)
def test_malformed_and_secret_responses(config, context, fault):
    o = envelope(context)
    msg = o["choices"][0]["message"]
    if fault == "outer_json":
        text = "invalid " + KEY
    elif fault == "inner_json":
        msg["content"] = "invalid"
    elif fault == "empty":
        msg["content"] = ""
    elif fault == "refusal":
        msg["refusal"] = "no"
    elif fault == "length":
        o["choices"][0]["finish_reason"] = "length"
    elif fault == "tools":
        msg["tool_calls"] = [{"function": "unused"}]
    elif fault == "choices":
        o["choices"] = []
    elif fault == "duplicate":
        msg["content"] = '{"a":1,"a":2}'
    elif fault == "nan":
        msg["content"] = '{"a":NaN}'
    elif fault == "secret":
        msg["content"] = json.dumps({"reason": KEY})
    elif fault == "secret_escaped":
        msg["content"] = KEY
    elif fault == "error_object":
        o = {"error": {"message": KEY}}
    if fault != "outer_json":
        text = json.dumps(o)
    if fault == "secret_escaped":
        text = text.replace(KEY, "".join("\\u%04x" % ord(c) for c in KEY))
    with pytest.raises(ModelError) as e:
        api_completion(
            "prompt",
            {},
            config,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, text=text)),
        )
    assert KEY not in str(e.value)


def test_api_safe_artifacts_without_external_executable(monkeypatch, tmp_path, context, capsys):
    for k, v in env_values().items():
        monkeypatch.setenv(k, v)

    monkeypatch.setenv("PATH", "")
    real = api_completion
    monkeypatch.setattr(
        "nis2_academy.cli.api_completion",
        lambda p, s, c, t: real(
            p,
            s,
            c,
            t,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=envelope(context))),
        ),
    )
    out = tmp_path / "run"
    assert main(["assess", "PR.AA-03_P2", "--out", str(out)]) == 0
    emitted = capsys.readouterr()
    assert json.loads(emitted.out) == reply(context)
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["backend"] == "api"
    assert manifest["client"]["requested_model"] == "env-model"
    assert manifest["client"]["returned_model"] == "test-model-snapshot"
    for p in out.iterdir():
        assert KEY not in p.read_text()
    assert KEY not in emitted.out + emitted.err


@pytest.mark.parametrize("mode", ["json_schema", "json_object"])
def test_local_validation_not_relaxed(monkeypatch, tmp_path, context, mode, capsys):
    for k, v in env_values().items():
        monkeypatch.setenv(k, v)
    bad = reply(context)
    bad["source_ids"]["company_records"] = ["AR-999"]
    monkeypatch.setattr("nis2_academy.cli.api_completion", lambda *a: (bad, {}))
    out = tmp_path / "run"
    assert main(["assess", "PR.AA-03_P2", "--response-format", mode, "--out", str(out)]) == 2
    assert not (out / "result.json").exists()
    assert (
        json.loads((out / "manifest.json").read_text())["status"] == "failed_no_assessment_accepted"
    )
    assert capsys.readouterr().out == ""


def test_missing_configuration_fails_before_run_or_client(monkeypatch, tmp_path, capsys):
    def forbidden(*a, **kw):
        raise AssertionError("No client may run")

    monkeypatch.setattr("nis2_academy.cli.api_completion", forbidden)
    out = tmp_path / "run"
    assert main(["assess", "PR.AA-03_P2", "--out", str(out)]) == 2
    assert not out.exists()
    assert "OPENAI_API_KEY" in capsys.readouterr().err


def test_offline_commands_never_load_env(monkeypatch, capsys):
    monkeypatch.setattr(
        "nis2_academy.cli.load_api_config",
        lambda *a: (_ for _ in ()).throw(AssertionError("No env read")),
    )
    assert main(["prompt", "PR.AA-03_P2"]) == 0
    capsys.readouterr()


def test_credentials_in_input_fail_before_artifacts(monkeypatch, tmp_path, capsys):
    for k, v in env_values().items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("OPENAI_API_KEY", "fictional")
    out = tmp_path / "rejected"
    assert main(["assess", "PR.AA-03_P2", "--out", str(out)]) == 3
    assert not out.exists()
    capsys.readouterr()


def test_double_encoded_secret_in_inner_result_rejected(config, context):
    answer = reply(context)
    answer["reason"] = KEY
    inner = json.dumps(answer).replace(KEY, "".join("\\u%04x" % ord(c) for c in KEY))
    outer = {"choices": [{"finish_reason": "stop", "message": {"content": inner}}]}
    assert KEY not in json.dumps(outer)
    with pytest.raises(ModelError):
        api_completion(
            "prompt",
            {},
            config,
            transport=httpx.MockTransport(lambda req: httpx.Response(200, json=outer)),
        )


@pytest.mark.parametrize("control", ["\x00", "\x01", "\x7f"])
def test_url_controls_rejected_without_echo(control):
    env = env_values()
    env["OPENAI_BASE_URL"] = "https://mock.example/" + control + "path"
    with pytest.raises(ValueError) as error:
        load_api_config(environ=env)
    assert control not in str(error.value)


def test_httpx_invalid_url_is_controlled(config):
    bad = APIConfig("https://mock.example/\x00", KEY, "test")
    with pytest.raises(ModelError) as error:
        api_completion(
            "prompt", {}, bad, transport=httpx.MockTransport(lambda r: httpx.Response(200))
        )
    assert KEY not in str(error.value)


def test_reasoning_configuration_and_precedence(tmp_path, monkeypatch):
    p = tmp_path / ".env"
    p.write_text(
        "\n".join(k + "=" + v for k, v in env_values().items()) + "\nOPENAI_REASONING_EFFORT=low\n"
    )
    assert load_api_config().reasoning_effort == "low"
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "medium")
    assert load_api_config().reasoning_effort == "medium"
    assert load_api_config(reasoning_effort="high").reasoning_effort == "high"
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "")
    assert load_api_config().reasoning_effort is None
    with pytest.raises(ValueError, match="REASONING"):
        load_api_config(reasoning_effort="unsupported")


def test_reasoning_request_and_honest_metadata(context):
    c = APIConfig("https://mock.example/v1", KEY, "test-model", reasoning_effort="medium")

    def handler(request):
        assert json.loads(request.content)["reasoning_effort"] == "medium"
        return httpx.Response(200, json=envelope(context))

    _, meta = api_completion("prompt", {}, c, transport=httpx.MockTransport(handler))
    assert meta["requested_model"] == "test-model"
    assert meta["requested_reasoning_effort"] == "medium"
    assert meta["effective_reasoning_effort"] is None
    assert "not independently observable" in meta["reasoning_support"]


def test_unsupported_reasoning_has_no_fallback(context):
    c = APIConfig("https://mock.example/v1", KEY, "test-model", reasoning_effort="high")
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(400, json={"error": "unsupported reasoning_effort"})

    with pytest.raises(ModelError, match="HTTP 400"):
        api_completion("prompt", {}, c, transport=httpx.MockTransport(handler))
    assert len(seen) == 1 and seen[0]["reasoning_effort"] == "high"


def test_cli_reasoning_recorded(monkeypatch, tmp_path, context, capsys):
    for k, v in env_values().items():
        monkeypatch.setenv(k, v)
    real = api_completion
    monkeypatch.setattr(
        "nis2_academy.cli.api_completion",
        lambda p, s, c, t: real(
            p,
            s,
            c,
            t,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json=envelope(context))),
        ),
    )
    out = tmp_path / "reasoning-run"
    assert main(["assess", "PR.AA-03_P2", "--reasoning-effort", "medium", "--out", str(out)]) == 0
    capsys.readouterr()
    body = json.loads((out / "api-request.json").read_text())
    meta = json.loads((out / "manifest.json").read_text())
    assert body["reasoning_effort"] == "medium"
    assert meta["client"]["requested_reasoning_effort"] == "medium"
    assert meta["client"]["effective_reasoning_effort"] is None


def test_reasoning_cannot_expose_credential():
    env = env_values()
    env["OPENAI_API_KEY"] = "medium"
    env["OPENAI_REASONING_EFFORT"] = "medium"
    with pytest.raises(ValueError) as error:
        load_api_config(environ=env)
    assert "medium" not in str(error.value)
