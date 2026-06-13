# Controlled Live Provider/LLM Evidence Planning and Authorization

Date: 2026-06-13

Gate: `Controlled Live Provider/LLM Evidence Planning and Authorization Gate`

Classification: `heavy`; planning/authorization only

Status: `PLANNING_READY_FOR_REVIEW_NOT_EXECUTED`

Release/readiness: `NOT_READY`

## Scope

This gate defines a bounded plan for a later, separately authorized
`Controlled Live Provider/LLM Evidence Execution Gate`.

The planned execution is limited to one live `fund-analysis analyze --use-llm`
Route C sample. It may collect bounded live provider/LLM evidence only. It must
not change runtime behavior, provider defaults, source acquisition policy,
sample scope, readiness state, release state or PR/external state.

This planning gate does not execute live provider/LLM.

## Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth for gate classification, source policy and live/external authorization. |
| `docs/design.md` | Design truth for explicit opt-in provider-backed `--use-llm` Route C and EID single-source/no fallback. |
| `docs/current-startup-packet.md` | Startup truth for current gate and `NOT_READY` posture. |
| `docs/implementation-control.md` | Control truth for accepted L3/L4/Post-L4 checkpoints and next entry. |
| `docs/reviews/mvp-provider-llm-post-l4-ready-state-disposition-controller-judgment-20260613.md` | Accepted Post-L4 routing basis. |
| `docs/reviews/mvp-provider-llm-l3-no-live-static-contract-evidence-controller-judgment-20260613.md` | Accepted L3 static/contract boundary. |
| `docs/reviews/mvp-provider-llm-l4-negative-fail-closed-evidence-controller-judgment-20260613.md` | Accepted L4 negative/fail-closed boundary. |
| `fund_agent/ui/cli.py` | Current CLI option contract. |
| `fund_agent/config/llm.py` | Current typed provider env contract. |

## Non-goals

- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR/push/merge/cleanup command in this planning gate.
- No source, tests, runtime behavior, provider default, manifest, fixture, golden-answer, README or design edit.
- No source acquisition policy change.
- No Eastmoney, fund-company website, CNINFO, fallback or direct PDF/cache/source helper use.
- No deterministic default behavior change.
- No release/readiness claim; state remains `NOT_READY`.
- No LLM content quality acceptance beyond bounded evidence fields.
- No retention of credentials, headers, raw prompts, raw provider request/response bodies, raw auditor response, raw PDF/cache body, source body excerpts or accepted final report body.

## Proposed Live Sample

| Field | Value |
|---|---|
| Fund code | `004393` |
| Report year | `2025` |
| CLI route | `fund-analysis analyze` |
| LLM mode | explicit opt-in `--use-llm` Route C |
| Quality gate policy | `warn` only under `--dev-override` |
| Valuation state | `unavailable` to avoid unrelated thermometer live path |
| Progress | `--no-llm-progress` |
| Source policy | EID single-source / no fallback |
| Sample expansion | Forbidden |

Rationale:

- `004393 / 2025` aligns with the current accepted tracked golden and source-body evidence surface, while still exercising the provider-backed `--use-llm` Route C path.
- A single sample cannot prove provider readiness, model quality, content acceptance, release readiness or broader fund/year coverage.

## Command Boundary

Future execution gate may authorize exactly one live command:

```bash
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Execution requirements:

- Run once only.
- Global wall-clock timeout: 15 minutes.
- Provider single-request timeout: no more than 60 seconds.
- Provider timeout attempts: exactly `1`.
- Provider timeout backoff: exactly `0`.
- stdout/stderr retention cap: maximum 80 lines or 12 KiB per stream, whichever is smaller.
- Capture exit code, start timestamp and end timestamp.
- Do not run shell snippets that print env, credentials, headers, raw prompts, raw provider payloads, cache bodies or PDF bodies.

Allowed execution-gate commands:

```bash
git status --branch --short
git status --short
git diff --check
FUND_AGENT_LLM_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS=60 FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1 FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0 FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000 uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --dev-override --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Allowed after execution only for safe artifact metadata inspection:

```bash
rg --files reports/llm-runs
sed -n '<range>p' reports/llm-runs/<safe-run-dir>/manifest.json
sed -n '<range>p' reports/llm-runs/<safe-run-dir>/summary.json
```

Forbidden commands and actions:

- second live sample or repeated live run;
- `fund-analysis checklist`;
- `fund-analysis analyze-annual-period`;
- direct provider probes outside CLI Route C;
- direct PDF/FDR/source/cache helper calls;
- Eastmoney/CNINFO/fund-company fallback checks;
- readiness/release/checklist/score-loop/golden promotion commands;
- cleanup/archive/ignore commands;
- stage/commit/push/PR/merge/mark-ready in the execution gate;
- reading credentials, headers, raw provider payloads, raw prompts, raw PDF/cache body, source body excerpts or accepted final report body.

## Environment/Credential Boundary

Required provider env must already exist in the execution process environment:

| Env var | Rule |
|---|---|
| `FUND_AGENT_LLM_PROVIDER` | Required; must be `openai_compatible`. |
| `FUND_AGENT_LLM_MODEL` | Required; model identifier may be recorded if not secret. |
| `FUND_AGENT_LLM_BASE_URL` | Required; may record only if controller classifies the endpoint as non-secret. |
| `FUND_AGENT_LLM_API_KEY_ENV_VAR` | Optional; record env var name only, not value. |
| `FUND_AGENT_LLM_API_KEY` or referenced key env | Required by current config, but value must never be printed, retained or summarized. |
| `FUND_AGENT_LLM_TIMEOUT_SECONDS` | Forced to `60` by command prefix. |
| `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS` | Forced to `60` by command prefix. |
| `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` | Forced to `60` by command prefix. |
| `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` | Forced to `60` by command prefix. |
| `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` | Forced to `1` by command prefix. |
| `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS` | Forced to `0` by command prefix. |
| `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` | Forced to `12000` by command prefix. |

Credential rules:

- Do not print, echo, grep or persist secret values.
- Evidence may record key presence as `present` / `missing` only if that can be observed without exposing the value.
- Headers, Authorization values, cookies, tokens, raw request bodies, raw response bodies and provider error bodies must not be retained.
- Missing/invalid credential must fail closed and must not trigger deterministic fallback.

## Evidence Artifact Requirements

Future execution evidence artifact path:

```text
docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-20260613.md
```

Runtime artifacts, if the application writes them, may remain only under ignored local path:

```text
reports/llm-runs/<safe-run-id>/
```

The evidence artifact must retain only safe fields:

| Field | Required |
|---|---|
| Gate name | Yes |
| Explicit execution authorization reference | Yes |
| Exact command | Yes, without secrets |
| Exact sample | `004393 / 2025` |
| Start/end timestamps | Yes |
| Exit code | Yes |
| stdout/stderr capped summary | Yes |
| Safe Host run id | Yes, if emitted |
| Host terminal status | Yes |
| Host timeout classification | Yes, if any |
| Chapter matrix | Yes, scalar status only |
| Provider runtime categories | Yes |
| Provider attempt count | Yes |
| Timeout/attempt settings | Yes |
| Redaction result | Yes |
| Safe artifact paths | Yes, if any |
| EID source/no-fallback fields | Only if safely emitted by CLI/artifact metadata |
| `fallback_used` | Must not be `true` if present |
| `fallback_enabled` | Must not be `true` if present |
| Readiness status | Must remain `NOT_READY` |

Forbidden retained fields:

- API key, token, Authorization/header/cookie values;
- raw prompts;
- raw provider request payload;
- raw provider response payload;
- raw provider error body;
- raw auditor response;
- raw PDF/cache body;
- source body excerpts;
- accepted final report body;
- uncapped stdout/stderr.

## Redaction Requirements

Before acceptance, retained evidence must distinguish value-bearing sensitive or
raw-body retention from safe scalar/policy metadata.

Sensitive value-bearing fields or values must stop acceptance and classify as
`SENSITIVE_DATA_LEAK`:

- API key values, tokens, cookies, Authorization header values or bearer values;
- raw prompt text;
- raw provider request payload;
- raw provider response payload;
- raw provider error body;
- raw auditor response body;
- raw PDF/cache/source body or source body excerpts.

Safe scalar/policy metadata is allowed when it does not include the underlying
value or body:

- `redaction_policy.forbidden_categories`;
- `system_prompt_chars`;
- `user_prompt_chars`;
- `approx_prompt_tokens`;
- `max_output_chars`;
- provider/runtime category names;
- timeout/attempt/backoff scalar settings;
- allowlist/forbidden-category names that describe redaction policy.

Source-policy terms such as `Eastmoney`, `CNINFO`, `fund-company`, `fallback`
and `source helper` are not sensitive leaks by themselves. They are allowed in
negative assertions, rejected-claim text and guardrail tables. They become
`UNEXPECTED_SOURCE_ACCESS` only when retained evidence shows actual command
execution, runtime access, provenance selection or fallback result using those
sources.

Redacting with `[REDACTED]` is not sufficient if raw prompt/provider/PDF/cache
or source body was already retained.

## Stop Conditions

Immediate stop and reject execution evidence if any occurs:

- live command differs from the exact authorized command;
- more than one live command is run;
- sample is not exactly `004393 / 2025`;
- provider attempts exceed `1`;
- provider retry/backoff occurs;
- `max_output_chars` is not exactly `12000` in retained safe metadata;
- timeout exceeds accepted limits;
- deterministic fallback occurs;
- `--use-llm` is absent;
- `--dev-override` is absent while `--quality-gate-policy warn` is used;
- default deterministic path is modified or invoked as fallback proof;
- `fallback_used=true`;
- `fallback_enabled=true` in current source path;
- Eastmoney/CNINFO/fund-company fallback/source access appears;
- direct PDF/cache/source helper access appears from provider/LLM path;
- credential/header/token/raw prompt/raw provider payload/raw PDF/cache/source body is retained;
- accepted final report body is retained as evidence;
- execution artifact claims release/readiness/PR readiness;
- output cap is exceeded without truncation;
- provider/LLM evidence is used to alter source policy.

Failure classification:

| Failure | Classification | Disposition |
|---|---|---|
| Missing provider config | `CONFIG_FAIL_CLOSED` | Accept as fail-closed evidence only. |
| Missing key | `AUTH_BLOCKED` | No retry; no body/header/key retention. |
| 401/403 | `AUTH_BLOCKED_RESIDUAL` | No retry; classify residual unless current evidence proves precise mapping. |
| Non-auth 4xx | `PROVIDER_REQUEST_REJECTED` | Fail closed; no retry. |
| 429 | `PROVIDER_UNAVAILABLE` | Fail closed; no retry. |
| 5xx/network | `PROVIDER_UNAVAILABLE` | Fail closed; no deterministic fallback. |
| Timeout | `LLM_TIMEOUT` | Fail closed after one attempt. |
| Malformed response | `PROVIDER_SCHEMA_DRIFT` | Fail closed. |
| LLM protocol parse failure | `LLM_CONTRACT_VIOLATION` | Fail closed. |
| Empty/model-blocked output | `MODEL_OUTPUT_BLOCKED` | Fail closed or use existing bounded repair only; no budget expansion. |
| Host/Agent mismatch | `CONTRACT_MISMATCH` | Reject. |
| Source/fallback access | `UNEXPECTED_SOURCE_ACCESS` | Reject. |
| Sensitive retention | `SENSITIVE_DATA_LEAK` | Reject. |

## Validation Matrix

| ID | Evidence target | Method | Accepted conclusion | Forbidden conclusion |
|---|---|---|---|---|
| CLLM-0 | Authorization boundary | Confirm separate explicit execution authorization exists before live command. | Execution gate may run exact one command. | Planning gate authorized execution. |
| CLLM-1 | Exact sample | Record command args and sample identity. | Evidence covers only `004393 / 2025`. | Broader sample coverage. |
| CLLM-2 | Explicit opt-in Route C | Verify command includes `--use-llm` and observe safe Host/Agent/provider fields. | Live path used explicit provider-backed Route C. | Deterministic default changed. |
| CLLM-3 | CLI parameter correctness | Verify `--dev-override --quality-gate-policy warn` pair. | Warn policy was an explicit development evidence override. | Product default quality gate semantics changed. |
| CLLM-4 | Provider availability | Record exit code and provider runtime category. | Provider responded or failed with typed category for this one run. | Provider readiness proven. |
| CLLM-5 | LLM chapter status | Record chapter matrix and terminal states. | Specific chapter acceptance/block status observed. | LLM content quality globally accepted. |
| CLLM-6 | Host/Agent bridge | Record Host status, timeout classification, safe run id and safe event count. | Host/Agent bridge handled this run. | Full production Agent runtime proven. |
| CLLM-7 | Source policy | Inspect safe emitted provenance/fallback fields only. | No observed fallback/source expansion in this run. | Source policy changed or source correctness globally proven. |
| CLLM-8 | Redaction/artifact safety | Inspect retained evidence and safe manifest/summary metadata only. | Retained evidence is safe and capped. | Raw prompts/provider/PDF/cache/source bodies are safe to keep. |
| CLLM-9 | Failure classification | Map any failure to accepted classification table. | Failure is typed and fail-closed. | Failure closes readiness blocker. |
| CLLM-10 | Readiness/PR boundary | Confirm artifact states `NOT_READY` and no external actions. | Evidence chain improved only. | Release/readiness/PR ready. |

## Residual Disposition

| Residual | Disposition | Reason |
|---|---|---|
| 401/403 provider-response classification | `DEFER_NONBLOCKING` | L3/L4 accepted missing config/key and no-live fail-closed behavior, but precise 401/403 provider-response body classification remains unproven. Live execution may classify it as residual if encountered, without retry/body retention. |
| Live provider/LLM availability | `NEXT_EXECUTION_SCOPE` | Single live run may observe one provider outcome, but cannot prove readiness. |
| LLM content quality/chapter acceptance | `DEFER_AFTER_EXECUTION` | Chapter status may be observed, but content acceptance needs separate content-quality review gate if controller chooses. |
| Source/PDF/cache body leak absence | `DEFER` | Execution evidence must not read bodies; only safe metadata/redaction can be accepted. |
| Release/readiness | `ACCEPT_BLOCKER` | Remains `NOT_READY`. |
| PR/push/merge/mark-ready | `DEFER_EXTERNAL_STATE` | Separate authorization only. |

## Review Plan

After this plan artifact is written:

- DS reviews command compliance, failure classification, credential boundary,
  redaction and stop-condition completeness.
- MiMo reviews source-policy/no-fallback preservation, overclaim prevention,
  artifact safety and readiness posture.
- Controller judges findings, applies accepted amendments and creates an
  accepted planning checkpoint if no blocking finding remains.

After later execution artifact is produced:

- DS reviews exact command, exact sample, failure classification and redaction.
- MiMo reviews no fallback/source expansion, no readiness overclaim and artifact safety.
- Controller accepts or rejects bounded live evidence and routes the next gate.

## Acceptance Criteria

Accept this plan only if:

- it preserves `NOT_READY`;
- it recommends exactly one next entry;
- it requires separate explicit live execution authorization;
- it limits execution to one exact command and one exact sample;
- it uses real current CLI/env contracts;
- it prevents source expansion and deterministic fallback;
- it forbids sensitive/raw body/final report retention;
- it classifies 401/403 as residual unless proven by direct evidence;
- it keeps release/readiness and PR/external state out of scope.

Reject or amend this plan if any command/env/sample boundary is ambiguous.

## Next Entry

Unique next entry:

```text
Controlled Live Provider/LLM Evidence Execution Gate
```

Execution still requires separate explicit authorization before any
live/provider/LLM/network command is run.
