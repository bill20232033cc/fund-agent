# MVP PASS-only timing probe evidence harness contract plan

## 1. Scope / No-goals

- Gate: `MVP PASS-only timing probe evidence harness contract gate`
- Classification: `heavy`
- Role: planning/design specialist, not controller
- Scope: design/control only

This plan pins the exact future evidence harness contract for the accepted `single-attempt current-timeout PASS-only probe`. It does not authorize a live provider call.

No-goals:

- Do not run a live PASS-only probe in this gate.
- Do not create `/tmp/fund-agent-pass-only-timing-probe.py` in this gate.
- Do not run `fund-analysis analyze --use-llm`.
- Do not modify source code, tests, provider endpoint, provider defaults, provider config, env values, timeout defaults, retry defaults, prompt contract, auditor rule, CHAPTER_CONTRACT, score-loop, quality gate, golden/readiness, retained report behavior, fail-closed semantics, PR state or release state.
- Do not connect this probe to report generation, retained LLM run artifacts, score-loop, quality gate, renderer, document repository, Host run artifacts, Agent runtime or final assembly.
- Do not print or persist provider/model/key/base URL values, request ids, raw diagnostics, request JSON, response JSON, exception reprs, raw prompt/response/report bodies, except the accepted PASS literals.

## 2. Harness Choice

Chosen future harness: temporary one-shot Python script executed from the future evidence gate command.

Rationale:

- The next evidence gate asks one narrow question: can the existing auditor-labeled provider path complete a tiny PASS-only request under the current effective auditor timeout?
- A temporary script minimizes new project surface. It uses existing typed config parsing and existing public provider adapter behavior without creating new production or dev-only API surface.
- A committed dev-only helper would require a separate implementation/review gate before evidence collection because it adds committed code. That is unnecessary for a one-shot timing observation.

Contract:

- The temporary script is not committed.
- The script body is used only inside the future evidence gate command.
- If reviewers reject an uncommitted one-shot script, the fallback is a separate `dev-only helper implementation gate`; that helper must be reviewed and accepted before any live probe.

## 3. Exact Public API Path

The future harness must use this public path:

1. `load_llm_provider_config_from_env()`
2. `dataclasses.replace(...)` to clone probe-local config
3. `build_chapter_llm_clients(probe_config)`
4. `clients.auditor.audit_chapter(ChapterAuditLLMRequest(...))`

Allowed equivalent: direct construction of `OpenAICompatibleChapterLLMClient(config=probe_config)` followed by `.audit_chapter(...)`.

Preferred path is `build_chapter_llm_clients(...).auditor.audit_chapter(...)` because it stays closest to the current Service-owned provider factory boundary.

Forbidden:

- Do not call private `OpenAICompatibleChapterLLMClient._complete()`.
- Do not hand-write HTTP requests.
- Do not inspect or serialize the provider request body.
- Do not bypass `load_llm_provider_config_from_env()`.
- Do not call Service analyze, `ChapterOrchestrator`, Host runner, Agent runtime, renderer, quality gate, score-loop or document repository.

## 4. Exact Config Clone Method

The future harness must load current effective env config, then clone it in memory exactly as:

```python
probe_config = dataclasses.replace(
    loaded_config,
    timeout_max_attempts=1,
    timeout_backoff_seconds=0,
)
```

Rules:

- Keep all other fields identical to `loaded_config`.
- Do not print or persist any config value.
- It is acceptable to record presence-only readiness booleans and scalar timeout metadata from the probe-local runtime path.
- This is probe-local measurement policy only. It is not a provider default, endpoint, model, base URL, key, timeout or retry behavior change.

## 5. Exact Synthetic Request

The future harness must construct this synthetic `ChapterAuditLLMRequest`:

```python
ChapterAuditLLMRequest(
    chapter_id=0,
    fund_code="PASS_ONLY_PROBE",
    report_year=0,
    system_prompt="Return exactly PASS.",
    user_prompt="PASS",
    draft_markdown="PASS",
    allowed_fact_ids=(),
    allowed_anchor_ids=(),
    audit_focus=(),
)
```

These fields are synthetic protocol fillers only. They are not fund identity, not report identity, not report facts and must not enter report artifacts or retained LLM run artifacts.

The accepted PASS literals may be documented:

- `Return exactly PASS.`
- `PASS`

No other prompt, draft, response or report body may be written.

## 6. Allowlist Output Schema

If a JSON sidecar is produced, it must be one object with this exact schema:

| Field | Type | Allowed values / rule |
|---|---|---|
| `schema_version` | string | exactly `pass_only_provider_timing_probe.v1` |
| `probe_name` | string | exactly `single-attempt current-timeout PASS-only probe` |
| `operation_label` | string | exactly `auditor_pass_only` |
| `api_path` | string | exactly `load_config_replace_build_clients_auditor_audit_chapter` |
| `logical_attempt_index` | integer | exactly `1` |
| `provider_attempt_index` | integer or null | `1` when available, else `null` |
| `provider_max_attempts` | integer | exactly `1` |
| `outcome_class` | string | `success`, `timeout`, `rate_limit`, `network`, `http_error`, `malformed`, `config_error`, `construction_error`, `unexpected_exception` |
| `classification` | string | `refutes_endpoint_wide_for_time_window`, `ambiguous_near_timeout`, `supports_endpoint_or_provider_latency_for_future_disposition_design`, `ambiguous_non_timeout`, `blocked_before_probe` |
| `elapsed_ms` | integer or null | non-negative integer if measured |
| `timeout_seconds` | number or null | effective auditor timeout seconds used |
| `timeout_threshold_ms` | integer or null | `int(timeout_seconds * 1000)` |
| `near_timeout_threshold_ms` | integer or null | `int(0.8 * timeout_seconds * 1000)` |
| `timeout_max_attempts` | integer | exactly `1` |
| `timeout_backoff_seconds` | number | exactly `0` |
| `timeout_budget_kind` | string or null | `auditor` or `null` |
| `provider_runtime_category` | string or null | `success`, `timeout`, `rate_limit`, `malformed`, `network`, `http_error`, or `null` |
| `status_code` | integer or null | HTTP status only if available |
| `exception_class` | string or null | class name only |
| `error_type` | string or null | allowlisted diagnostic class/type name only |
| `response_char_count` | integer or null | `len(response.raw_text)` on success only |
| `system_prompt_chars` | integer | length of accepted PASS-only system literal |
| `user_prompt_chars` | integer | length of provider-bound PASS-only audit user payload |
| `approx_prompt_tokens` | integer or null | scalar diagnostic only |
| `allowed_fact_count` | integer | exactly `0` |
| `allowed_anchor_count` | integer | exactly `0` |
| `body_recorded` | boolean | exactly `false` |
| `provider_values_recorded` | boolean | exactly `false` |
| `request_id_recorded` | boolean | exactly `false` |
| `raw_diagnostics_recorded` | boolean | exactly `false` |
| `request_json_recorded` | boolean | exactly `false` |
| `response_json_recorded` | boolean | exactly `false` |
| `exception_repr_recorded` | boolean | exactly `false` |
| `report_artifact_created` | boolean | exactly `false` |

Forbidden fields and values:

- provider value, model value, base URL value, endpoint path, API key, API key env value, Authorization header, Bearer token, request id;
- raw request JSON, raw response JSON, raw response body, raw diagnostics object, exception repr;
- raw provider response, raw audit response, draft/report markdown body;
- env dump or config object serialization.

## 7. No-body-by-construction Rule

On success:

- The script may compute `response_char_count = len(response.raw_text)`.
- It must immediately discard the response object.
- It must not compare, print, store or serialize `response.raw_text`.
- It must not persist `model_name` or `finish_reason`, because the accepted contract forbids provider/model values and raw response diagnostics for this probe.

On exception:

- Record only `type(exc).__name__`.
- If the exception exposes `diagnostics`, read only the allowlisted scalar fields above from the terminal diagnostic.
- Do not serialize the exception object, `repr(exc)`, `str(exc)` wholesale, `exc.__dict__`, raw diagnostics object or chained cause.
- Do not record request id even if current diagnostics expose it.

## 8. Future Command Shape and Destinations

Future evidence artifact destination:

- Markdown: `docs/reviews/mvp-pass-only-provider-timing-probe-evidence-20260603.md`
- Optional JSON sidecar: `docs/reviews/mvp-pass-only-provider-timing-probe-evidence-20260603.json`

Exact future command shape:

```bash
uv run python /tmp/fund-agent-pass-only-timing-probe.py
```

The temporary script must:

- load config with `load_llm_provider_config_from_env()`;
- clone config with `dataclasses.replace(loaded_config, timeout_max_attempts=1, timeout_backoff_seconds=0)`;
- build clients with `build_chapter_llm_clients(probe_config)`;
- call `clients.auditor.audit_chapter(request)` exactly once;
- measure wall-clock elapsed with monotonic time;
- emit only the allowlisted JSON object or enough scalar stdout for the markdown artifact;
- exit `0` when a measurement outcome is safely collected, including timeout;
- exit non-zero only for harness safety failure, schema validation failure, secret-scan failure or inability to write the intended artifact.

Presence-only readiness must run before the live probe. It may report only pass/fail for required config presence and construction readiness, never values.

If JSON sidecar is produced, validate it:

```bash
python -m json.tool docs/reviews/mvp-pass-only-provider-timing-probe-evidence-20260603.json
```

Secret scan command for generated evidence files:

```bash
rg -n "Authorization|Bearer |FUND_AGENT_LLM_API_KEY=|api_key[=:]|sk-[A-Za-z0-9._-]{20,}|raw_response|provider response|request_id|base_url|model_name|request JSON|response JSON|draft_markdown|system_prompt[^_]|user_prompt[^_]" \
  docs/reviews/mvp-pass-only-provider-timing-probe-evidence-20260603.md \
  docs/reviews/mvp-pass-only-provider-timing-probe-evidence-20260603.json
```

Expected handling:

- Matches for forbidden-output labels inside a forbidden-fields paragraph are acceptable only if they do not include values.
- Any actual provider value, key, endpoint, request id, raw body or serialized object match means quarantine and stop without pasting the matched value.

## 9. Classification Thresholds

Let `timeout_ms = timeout_seconds * 1000`.

Success:

- If `elapsed_ms < 0.8 * timeout_ms`, classify as `refutes_endpoint_wide_for_time_window`.
- Meaning: this refutes endpoint-wide/provider latency for the observed time window only; it does not prove all provider behavior healthy.
- Next investigation should move toward report-specific auditor payload/timing design.

Near-timeout success:

- If `elapsed_ms >= 0.8 * timeout_ms`, classify as `ambiguous_near_timeout`.
- It must not be treated as a clean endpoint-health refutation.

Timeout:

- If outcome is timeout, classify as `supports_endpoint_or_provider_latency_for_future_disposition_design`.
- Meaning: this supports endpoint/provider latency only enough to open a future heavy disposition design gate.
- It does not authorize endpoint/config/default/runtime changes.

Other outcomes:

- `rate_limit`, `network`, `http_error`, `malformed` => `ambiguous_non_timeout`.
- `config_error` or `construction_error` => `blocked_before_probe`.
- `unexpected_exception` => `ambiguous_non_timeout` unless safety failure requires quarantine.

All production changes remain blocked for every classification.

## 10. Acceptance Criteria

This harness contract gate is acceptable only if the plan pins:

- design/control-only scope and no live call;
- temporary one-shot script as the chosen future harness;
- public API path through config loader and `audit_chapter()`;
- exact config clone method;
- exact synthetic `ChapterAuditLLMRequest` fields;
- exact allowlist schema and forbidden fields;
- no-body-by-construction handling;
- future command shape, artifact destinations, secret scan and JSON validation;
- thresholding rules and next-gate consequences;
- review matrix and controller judgment requirement.

Future evidence gate acceptance requires:

- controller authorization before the live command;
- presence-only config readiness;
- exactly one logical PASS-only auditor probe;
- no report artifact or retained LLM run artifact;
- markdown evidence and optional validated JSON sidecar;
- secret scan with no unsafe value leakage;
- two independent evidence reviews, unless controller records reviewer unavailability;
- controller judgment before any endpoint/config/default/runtime disposition gate.

## 11. Review Matrix

| Reviewer focus | Required checks |
|---|---|
| Boundary review | Confirms no Service analyze/orchestrator/report assembly, no Host/Agent/dayu, no score-loop, no quality gate, no retained report artifacts |
| Provider path review | Confirms use of `load_llm_provider_config_from_env()` plus public `audit_chapter()` path; no `_complete()` or handwritten HTTP |
| Secret-safety review | Confirms allowlist-only fields, no provider/model/key/base URL/request id/raw body/raw diagnostics/exception repr |
| Evidence-method review | Confirms single logical attempt, probe-local `timeout_max_attempts=1`, no rerun, no writer probe |
| Classification review | Confirms `<0.8*timeout`, `>=0.8*timeout`, timeout and ambiguous outcomes are interpreted exactly as pinned |
| Control review | Confirms no production change is authorized and next gate remains heavy |

## 12. Next Gate Recommendation

Next gate should be:

`MVP PASS-only timing probe evidence gate`

Classification: `heavy`.

Recommended scope:

- Run the exact temporary one-shot script once, only after controller authorization.
- Produce the markdown evidence artifact and optional JSON sidecar.
- Run JSON validation if sidecar exists.
- Run the secret scan.
- Obtain independent reviews and controller judgment.

Do not open endpoint/config/default/runtime disposition until the evidence gate is accepted.
