<p align="center">
  <img src="assets/academy-logo.png" alt="FusionAI Academy" width="125">&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/aurora-grid-logo.png" alt="Aurora Grid" width="150">
</p>

# NIS2 case study — Aurora Grid

**FusionAI Academy · Workshop and worked implementation**

Start with the [workshop brief](docs/workshop.md) to design your team's assessment methodology and use the [submission template](SUBMISSION_TEMPLATE.md) for the report. The original workshop is a discussion and design exercise; no coding is required for that activity.

This repository also includes the worked implementation presented after the workshop: a single-requirement assessment CLI, its processed inputs, and 27 saved results. The original [questionnaire](inputs/security-questionnaire.md) and [company dossier](inputs/aurora-grid-dossier.md) remain available for reading. The application uses the self-contained source snapshots in `src/nis2_academy/resources/`.

Assess one ACN requirement at a time against the fictional Aurora Grid company case. The application builds a traceable context, calls a configurable model API, and validates the returned JSON and its source references.

The catalogue contains 116 ACN points. **27 reviewed targets** are supported for assessment; other catalogue points may provide context. This teaching exercise is not a compliance certification or a check for later regulatory updates.

## Setup

Use Python 3.12 and [uv](https://docs.astral.sh/uv/):

```sh
uv sync --locked
cp .env.example .env
```

Edit your private `.env` with your provider's API base URL, key and model identifier:

```dotenv
OPENAI_BASE_URL=https://api.example.invalid/v1
OPENAI_API_KEY=replace-with-your-key
OPENAI_MODEL=replace-with-your-model
NIS2_RESPONSE_FORMAT=json_schema
OPENAI_REASONING_EFFORT=
```

The values above are placeholders. An API account with access to the selected model is required. Requests may incur provider charges. No graph database or container service is needed.

Only `.env` in the current directory is loaded, unless you supply `--env-file PATH`. Configuration priority is command-line overrides, process environment, then file. Values are not interpolated and no parent directories are searched. Keep keys out of URLs and source control. Private env filenames are ignored by Git; `.env.example` is the shareable template.

## Run and inspect

```sh
# Offline: no credentials or network needed
uv run main.py list
uv run main.py context PR.AA-03_P2
uv run main.py prompt PR.AA-03_P2
uv run main.py schema PR.AA-03_P2
uv run main.py verify
uv run main.py validate-reply PR.AA-03_P2 results/PR.AA-03_P2.json
uv run main.py matching-prompt mfa_implementation_status

# One live API request; choose a new output directory each time
uv run main.py assess PR.AA-03_P2 --out results/new/example

# Optional overrides: use values supported by your provider and model
uv run main.py assess PR.AA-03_P2 --model your-model --reasoning-effort medium
```

JSON output is UTF-8 and indented. Controlled errors go to stderr, leaving stdout empty. Exit codes: `0` success, `2` invalid input/configuration/sources/result, `3` model transport failure. Unknown IDs and catalogue IDs outside the 27-target scope produce distinct errors.

Each new run saves context, rendered prompt, exact model input, schema, API request body and a run manifest under `results/new/` by default. A result is saved only after local validation. Existing output directories are never overwritten. Authentication headers and raw provider error bodies are not saved.

## API contract and model settings

The client sends one non-streaming `POST {OPENAI_BASE_URL}/chat/completions` request with Bearer authentication, `model`, `messages`, and `response_format`. Provide the base URL without `/chat/completions`. HTTPS is required except for loopback test servers.

- `json_schema` sends the local schema with `strict: true`; the provider and model must support it.
- `json_object` is an explicit alternative for providers supporting JSON mode. Select it in `.env` or with `--response-format json_object`. The same local validator still applies.
- Optional `OPENAI_REASONING_EFFORT` / `--reasoning-effort` sends the top-level `reasoning_effort` field. Accepted configuration values are `none`, `minimal`, `low`, `medium`, `high`, `xhigh`; actual support depends on the provider and model. Empty omits the field. Unsupported settings fail visibly, with no retry, fallback or silent parameter removal.

The expected response has one `choices` entry, textual `message.content` containing JSON, and `finish_reason: "stop"`. Refusals, tool calls, incomplete output and invalid references are rejected. Redirects and environment-based proxy/TLS overrides are disabled.

This implements the [Chat Completions contract](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create), not universal provider compatibility. Responses API, streaming, tool calling and custom authentication are not implemented. Native Azure deployment endpoints requiring `api-version` and an `api-key` header need an adapter; a v1 endpoint or gateway works only if it satisfies this exact contract. Provider compatibility has been tested with offline mock responses, not live requests.

New run manifests record the requested model and reasoning setting, plus the model identifier reported by the response. A provider-reported identifier does not independently establish an exact server snapshot. A successful request records acceptance of the reasoning parameter, not proof of the server's effective thinking level; effective effort remains unknown.

## Included results

`results/<requirement_id>.json` contains each of the **27 accepted assessments**, with its original judgment, rationale and source IDs preserved. These files are outputs for inspection, never inputs to the model or expected-answer fixtures. They are directly readable in this repository.

The current run contains **8 Satisfied, 9 Partially satisfied, 8 Not satisfied and 2 Not determinable** assessments. It used **gpt-5.6-sol / medium reasoning effort**, as recorded in [results/provenance.json](results/provenance.json). An external authenticated client generated these results; they are not a live validation of the repository API client. The recorded model and reasoning settings identify the client configuration, not an independently verified server snapshot or effective internal reasoning level.

## Method and tests

Read [the methodology](docs/methodology.md) for dependency direction, evidence boundaries, ENISA retrieval and output validation.

```sh
uv sync --locked --extra dev --extra verify
uv run pytest
uv run ruff check .
uv run main.py verify --pdf
```

Tests cover context construction, schema/reference validation, API configuration, request formatting, safe error handling and persistence using synthetic replies. They do not establish the semantic correctness of the saved judgments.

```text
main.py                  CLI entry point
pyproject.toml, uv.lock   pinned installation
.env.example             safe API configuration template
src/nis2_academy/         application and packaged source inputs
docs/methodology.md       teaching methodology
tests/                   offline test source
results/                 27 readable assessments and essential provenance
```
