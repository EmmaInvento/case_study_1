"""OpenAI-compatible, non-streaming Chat Completions. No secret persistence."""

from dataclasses import dataclass, field
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from dotenv import dotenv_values
import httpx

from .model import ModelError, client_input
from .validation import parse_json


def contains_credential(value, credential):
    """Check decoded strings at every JSON level, including object keys."""
    if isinstance(value, str):
        return credential in value
    if isinstance(value, dict):
        return any(
            contains_credential(k, credential) or contains_credential(v, credential)
            for k, v in value.items()
        )
    if isinstance(value, list):
        return any(contains_credential(v, credential) for v in value)
    return False


@dataclass(frozen=True)
class APIConfig:
    base_url: str
    api_key: str = field(repr=False)
    model: str
    response_format: str = "json_schema"
    reasoning_effort: str | None = None

    def public_metadata(self):
        return {
            "backend": "openai-compatible-chat-completions",
            "base_url": self.base_url,
            "requested_model": self.model,
            "response_format": self.response_format,
            "requested_reasoning_effort": self.reasoning_effort,
            "effective_reasoning_effort": None,
            "reasoning_support": "not verified",
            "stream": False,
            "automatic_retries": 0,
            "automatic_fallback": False,
        }


def load_api_config(
    env_file=None, model=None, response_format=None, environ=None, *, reasoning_effort=None
):
    """CLI > process environment > exact .env path; no parent search or mutation."""
    env = os.environ if environ is None else environ
    path = Path(env_file) if env_file is not None else Path.cwd() / ".env"
    if env_file is not None and not path.is_file():
        raise ValueError("Explicit environment file is missing")
    try:
        values = dotenv_values(dotenv_path=path, interpolate=False) if path.is_file() else {}
    except (OSError, UnicodeError):
        raise ValueError("Environment file could not be read") from None
    names = [
        "OPENAI_BASE_URL",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "NIS2_RESPONSE_FORMAT",
        "OPENAI_REASONING_EFFORT",
    ]
    selected = {k: env[k] if k in env else values.get(k) for k in names}
    if model is not None:
        selected["OPENAI_MODEL"] = model
    if response_format is not None:
        selected["NIS2_RESPONSE_FORMAT"] = response_format
    if reasoning_effort is not None:
        selected["OPENAI_REASONING_EFFORT"] = reasoning_effort
    effort = selected["OPENAI_REASONING_EFFORT"] or None
    if effort is not None and effort not in {"none", "minimal", "low", "medium", "high", "xhigh"}:
        raise ValueError("Unsupported OPENAI_REASONING_EFFORT value")
    missing = [k for k in names[:3] if not selected[k] or not selected[k].strip()]
    if missing:
        raise ValueError("Missing API configuration: " + ", ".join(missing))
    base, key, model_id = (selected[k].strip() for k in names[:3])
    if effort is not None and key in effort:
        raise ValueError("API credential unexpectedly occurs in reasoning configuration")
    mode = selected["NIS2_RESPONSE_FORMAT"] or "json_schema"
    if mode not in {"json_schema", "json_object"}:
        raise ValueError("NIS2_RESPONSE_FORMAT must be json_schema or json_object")
    if key == "replace-with-your-key" or model_id == "replace-with-your-model":
        raise ValueError("Replace API key and model placeholders before assessing")
    if len(key) < 4 or not key.isascii() or any(ord(c) < 33 or ord(c) > 126 for c in key):
        raise ValueError("Invalid API key format")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}", model_id) or key in model_id:
        raise ValueError("Invalid API model identifier")
    try:
        url = urlsplit(base)
        _ = url.port
    except ValueError:
        raise ValueError("Invalid API base URL") from None
    if (
        not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
        or key in unquote(base)
        or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in base)
    ):
        raise ValueError("API base URL must not contain credentials, query, fragment or whitespace")
    if url.scheme != "https" and not (
        url.scheme == "http" and url.hostname in {"127.0.0.1", "localhost", "::1"}
    ):
        raise ValueError("API requires HTTPS; HTTP is allowed only for loopback servers")
    if url.hostname.endswith(".invalid"):
        raise ValueError("Replace the example API endpoint before assessing")
    if url.path.rstrip("/").endswith("/chat/completions"):
        raise ValueError("Configure the API base URL, without /chat/completions")
    return APIConfig(base.rstrip("/"), key, model_id, mode, effort)


def api_request_body(prompt, schema, config):
    output = {"type": config.response_format}
    if config.response_format == "json_schema":
        output["json_schema"] = {"name": "acn_assessment", "strict": True, "schema": schema}
    body = {
        "model": config.model,
        "messages": [{"role": "user", "content": client_input(prompt)}],
        "response_format": output,
        "stream": False,
    }
    if config.reasoning_effort is not None:
        body["reasoning_effort"] = config.reasoning_effort
    return body


def api_completion(prompt, schema, config, timeout=180, *, transport=None):
    body = api_request_body(prompt, schema, config)
    # A malicious/incorrect endpoint must not turn reflected authentication into an artifact.
    if config.api_key in client_input(prompt):
        raise ModelError("API credential unexpectedly occurs in request content")
    try:
        with httpx.Client(
            timeout=timeout, trust_env=False, follow_redirects=False, transport=transport
        ) as client:
            response = client.post(
                config.base_url + "/chat/completions",
                json=body,
                headers={
                    "Authorization": "Bearer " + config.api_key,
                    "Content-Type": "application/json",
                },
            )
    except httpx.TimeoutException:
        raise ModelError("API request timed out; no automatic retry") from None
    except (httpx.HTTPError, httpx.InvalidURL):
        raise ModelError("API network or protocol error; response details suppressed") from None
    if not 200 <= response.status_code < 300:
        hint = (
            (
                "; check endpoint/model support for the selected response_format; "
                "json_object may be selected explicitly, never automatically"
            )
            if response.status_code in {400, 404, 422}
            else ""
        )
        raise ModelError(f"API HTTP {response.status_code}{hint}; body and headers suppressed")
    if config.api_key in response.text:
        raise ModelError("API response contains authentication material; response rejected")
    try:
        envelope = parse_json(response.text)
        if contains_credential(envelope, config.api_key):
            raise ValueError()
        if not isinstance(envelope, dict) or "error" in envelope:
            raise ValueError()
        choices = envelope["choices"]
        if not isinstance(choices, list) or len(choices) != 1:
            raise ValueError()
        choice = choices[0]
        message = choice["message"]
        if (
            choice.get("finish_reason") != "stop"
            or message.get("refusal")
            or message.get("tool_calls")
        ):
            raise ValueError()
        text = message["content"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError()
        result = parse_json(text)
        if contains_credential(result, config.api_key):
            raise ValueError()
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ModelError(
            "API returned invalid, refused, incomplete or unsupported output"
        ) from None
    metadata = config.public_metadata()
    metadata["reasoning_support"] = (
        "request accepted; effective effort not independently observable"
        if config.reasoning_effort is not None
        else "not requested"
    )
    returned = envelope.get("model")
    metadata["returned_model"] = (
        returned
        if isinstance(returned, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}", returned)
        else "not reported"
    )
    usage = envelope.get("usage", {})
    metadata["usage"] = {
        k: usage[k]
        for k in ["prompt_tokens", "completion_tokens", "total_tokens"]
        if isinstance(usage, dict) and type(usage.get(k)) is int and usage[k] >= 0
    }
    return result, metadata
