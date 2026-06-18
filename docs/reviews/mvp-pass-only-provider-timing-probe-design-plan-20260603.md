# MVP PASS-only provider timing probe design plan

## 1. Scope

- Role: planning/design specialist, not controller.
- Gate: `MVP PASS-only provider timing probe design gate`.
- Classification: heavy.
- Scope: design-only.

No live provider call is authorized in this gate. No source code, tests, provider endpoint, provider config, default timeout, retry default, prompt contract, auditor rule, fail-closed behavior, score-loop, quality gate, golden/readiness, PR/release or report-generation behavior is changed by this plan.

No-goals:

- Do not run `fund-analysis analyze --use-llm`.
- Do not run a PASS-only live probe in this gate.
- Do not change provider endpoint, model, key, base URL, timeout defaults, retry defaults or env values.
- Do not create report artifacts, retained LLM run artifacts, raw provider response artifacts or prompt artifacts.
- Do not infer root cause from indirect stderr anecdotes; classification must use same-source timing/status fields.

## 2. Future Probe Goal

Future evidence gate goal:

Collect one minimal PASS-only provider timing observation to distinguish:

- endpoint-wide/provider health or latency: even a tiny PASS-only request cannot complete within the current effective auditor timeout budget;
- report-specific auditor timeout: a tiny PASS-only auditor request completes, while real chapter auditor calls timeout on report payloads.

The probe must not generate report content artifacts. It must not call `FundAnalysisService.analyze*`, `ChapterOrchestrator`, report assembly, quality gate, artifact retention, document repository, renderer or score-loop. It may only call the provider through the existing typed config and Service provider adapter path, record scalar timing/status fields, and discard response body.

## 3. Provider Path Decision

Use the existing provider config loader and current Service provider adapter semantics:

- Load config through `load_llm_provider_config_from_env()`.
- Construct the current OpenAI-compatible Service provider adapter.
- Use the public audit-labeled call path, `ChapterAuditLLMClient.audit_chapter()`, because the accepted post-repair live blocker is auditor-clustered runtime timeout.
- Do not issue a writer-labeled probe in the first PASS-only evidence gate. Writer comparison is a separate future gate if controller needs it.

Controller feasibility note:

- Current `OpenAICompatibleChapterLLMClient._complete()` is a private method. The future evidence harness must not rely on that private method as an accepted public contract.
- If the future evidence gate uses a temporary one-shot script, it should call the public `audit_chapter()` method with minimal synthetic `ChapterAuditLLMRequest` fields.
- If direct public-call construction proves too awkward, the next gate should first design a dev-only probe helper. That helper would still require a separate implementation/review checkpoint before any live probe.

Reasoning:

- Reusing the current typed config and provider adapter preserves endpoint URL derivation, HTTP payload shape, timeout exception mapping and runtime error classes.
- Bypassing the adapter with hand-written HTTP would weaken same-source attribution.
- A first writer+auditor pair would double live calls without answering the active auditor-timeout question more directly.

## 4. Future Probe Shape

Future evidence gate may use a temporary one-shot command. Preferred human artifact:

- `docs/reviews/mvp-pass-only-provider-timing-probe-evidence-20260603.md`

Optional machine-readable sidecar only if needed:

- `docs/reviews/mvp-pass-only-provider-timing-probe-evidence-20260603.json`

The probe request may use these literal PASS-only strings:

- `system_prompt = "Return exactly PASS."`
- `user_prompt = "PASS"`
- `draft_markdown = "PASS"`

These literals are safe because they contain no fund facts, no report body, no provider values and no secrets. The evidence artifact may document these exact literals. It must not store any provider response body, model value, endpoint/base URL value, key value, Authorization header, raw env dump, request body, response JSON, report draft or raw audit response.

Synthetic protocol fields may be used only to satisfy current dataclass construction, for example synthetic chapter/fund/year values. They must not be interpreted as report identity and must not enter report artifacts.

## 5. Stop Conditions

Future evidence gate stop rules:

- Run presence-only provider config readiness first. Print only presence/pass/fail fields, no values.
- If config readiness fails, stop. Do not patch env or retry.
- If provider client construction fails, stop.
- Run exactly one logical PASS-only auditor probe.
- Do not run a writer probe in the same gate.
- Do not rerun after success, timeout, rate limit, network error, malformed response or HTTP error.
- Do not run a full report smoke after the PASS-only result.
- If the evidence artifact or sidecar secret scan finds provider values, keys, Authorization headers, raw prompts beyond the documented PASS literals, raw responses or report content, quarantine and stop without pasting the matching value.

### Attempt Policy

Preferred attempt policy for the future evidence gate:

- Use the current effective auditor timeout seconds from the loaded config.
- Clone the loaded config in-memory for the evidence harness with `timeout_max_attempts=1` and `timeout_backoff_seconds=0`.
- Record explicitly that this is probe-local measurement policy, not a production default change.

Reasoning:

- One provider attempt makes `elapsed_ms` directly interpretable.
- Current report path already proved auditor timeout under `60s x2`; the PASS-only probe's first question is whether a tiny auditor call can complete once under the same effective timeout seconds.
- Keeping retries in the PASS-only probe would make the evidence more expensive and blur endpoint health vs retry-window duration.

Alternative if reviewers reject probe-local attempt override:

- Use the loaded config unchanged and record all provider diagnostic attempts.
- This is more production-similar but less minimal. It should still be exactly one logical PASS-only probe.

## 6. Measurement Fields

Record only these scalar fields:

| Field | Meaning |
|---|---|
| `schema_version` | `pass_only_provider_timing_probe.v1` |
| `operation_label` | `auditor_pass_only` |
| `logical_attempt_index` | fixed `1` |
| `provider_attempt_index` | `1` for preferred probe-local measurement |
| `elapsed_ms` | wall-clock elapsed time for the provider call |
| `timeout_seconds` | effective auditor timeout seconds used by the probe |
| `timeout_max_attempts` | `1` for preferred probe-local measurement |
| `timeout_backoff_seconds` | `0` for preferred probe-local measurement |
| `outcome_class` | `success`, `timeout`, `rate_limit`, `network`, `http_error`, `malformed`, `config_error`, `construction_error`, `unexpected_exception` |
| `exception_class` | class name only, if any |
| `status_code` | integer only, if available |
| `response_char_count` | character count only on success; no body |
| `body_recorded` | must be `false` |
| `provider_values_recorded` | must be `false` |
| `report_artifact_created` | must be `false` |

Forbidden fields:

- provider/model/base URL/key values;
- Authorization header;
- raw request JSON;
- raw response JSON/body;
- report markdown;
- chapter draft;
- raw audit response;
- request id unless a separate security review authorizes it.

## 7. Classification Logic

Supports endpoint-wide/provider latency:

- PASS-only auditor probe times out under the current effective auditor timeout seconds, with tiny PASS-only prompt and `response_char_count = null`.
- Combined with the accepted post-repair report run, this supports that provider health/latency can affect even non-report auditor calls.
- It still does not authorize automatic endpoint/config/default changes. It authorizes a separate heavy disposition gate to decide whether to change provider endpoint/config/runtime defaults or pause provider-backed acceptance.

Refutes endpoint-wide/provider latency for the observed time window:

- PASS-only auditor probe succeeds with a small response count and elapsed time comfortably below timeout.
- This shifts the next investigation toward report-specific auditor timeout: real chapter audit payload size, draft/context shape, audit prompt construction, or bounded semantic auditor behavior.
- Next gate should be a report-specific auditor timing/payload diagnostic design gate, not endpoint/config/default change.

Ambiguous:

- PASS-only succeeds but elapsed time is close to timeout.
- PASS-only returns rate limit, network, HTTP error or malformed response.
- Config or construction fails.
- Temporary harness cannot call the public audit client without implementation work.

Ambiguous outcomes require a separate gate. Do not classify them as report-specific auditor timeout or endpoint-wide latency without more same-source evidence.

## 8. Future Evidence Command Contract

Future controller may authorize a one-shot temporary command with this shape:

```bash
uv run python <temporary-pass-only-probe-script>
```

The script contract:

- imports current config loader and current Service provider client;
- builds a probe-local cloned config with same provider/model/base URL/key/timeouts but `timeout_max_attempts=1` and `timeout_backoff_seconds=0`;
- calls `audit_chapter()` once with PASS-only literals through a synthetic `ChapterAuditLLMRequest`;
- measures elapsed with monotonic time;
- catches current provider runtime/config/construction exceptions;
- prints or writes only the measurement fields above;
- exits `0` for successful measurement collection, even if `outcome_class=timeout`, unless secret-safety validation fails.

The future evidence artifact must include:

- command run;
- config readiness presence-only output;
- scalar measurement table;
- explicit statement that no report artifact was created;
- secret scan command and result;
- classification using the matrix above.

## 9. Validation And Review Requirements

Design acceptance requires:

- two independent plan reviews for this design gate;
- controller judgment accepting or rejecting the exact future PASS-only probe shape;
- control/startup sync only after controller acceptance.

Future evidence acceptance requires:

- presence-only config readiness;
- exactly one PASS-only auditor probe;
- no raw response/body/provider values in artifact;
- JSON validation if a sidecar JSON is produced;
- secret scan over any generated evidence files;
- evidence review by at least two independent reviewers, or explicit controller-recorded reviewer unavailability;
- controller judgment before any follow-up endpoint/config/default/runtime gate.

## 10. Accepted Checkpoint

This design gate is accepted only when the plan, independent reviews, controller judgment and any authorized control/startup sync are committed locally.

This plan alone does not authorize a live PASS-only probe. It only defines the future evidence gate shape.
