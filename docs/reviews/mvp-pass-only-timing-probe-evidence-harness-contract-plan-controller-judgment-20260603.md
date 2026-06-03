# MVP PASS-only timing probe evidence harness contract plan controller judgment

## Judgment

ACCEPTED.

The `MVP PASS-only timing probe evidence harness contract gate` is accepted as a design/control-only checkpoint. It pins the future evidence harness contract for the accepted `single-attempt current-timeout PASS-only probe`; it does not authorize a live PASS-only probe in this gate.

## Accepted Artifacts

- Plan: `docs/reviews/mvp-pass-only-timing-probe-evidence-harness-contract-plan-20260603.md`
- Review A: `docs/reviews/mvp-pass-only-timing-probe-evidence-harness-contract-plan-review-a-20260603.md`
- Review B: `docs/reviews/mvp-pass-only-timing-probe-evidence-harness-contract-plan-review-b-20260603.md`

Both independent reviews PASS with no blocking findings. Review B's must-fix items are accepted as hard entry criteria for the next live evidence gate.

## Accepted Harness Contract

The future evidence gate may use a temporary one-shot Python script only under this contract:

- no committed source/test/provider/default/runtime/template/auditor/score/golden/readiness changes;
- no `fund-analysis analyze --use-llm`;
- no report artifact, retained LLM run artifact, Host artifact, score-loop, quality gate, renderer, document repository or Agent runtime linkage;
- config must be loaded through `load_llm_provider_config_from_env()`;
- probe-local config must be cloned with `dataclasses.replace(loaded_config, timeout_max_attempts=1, timeout_backoff_seconds=0)`;
- all other provider config fields stay identical and must not be printed or persisted;
- provider path must be `build_chapter_llm_clients(probe_config).auditor.audit_chapter(ChapterAuditLLMRequest(...))`;
- direct adapter construction is no longer accepted unless a future controller judgment records why the factory path is impossible;
- synthetic request fields must exactly match the accepted PASS-only `ChapterAuditLLMRequest`;
- accepted body literals are limited to `Return exactly PASS.` and `PASS`;
- output must be allowlist-only scalar timing/classification evidence;
- no provider/model/key/base URL values, endpoint path, request id, raw request JSON, raw response JSON, raw body, raw diagnostics object, exception repr, prompt body, draft/report body or env/config dump may be printed or persisted.

## Hard Requirements For The Next Evidence Gate

The next gate is `MVP PASS-only timing probe evidence gate`, classification `heavy`. Before or during that evidence gate:

1. Include the full redacted-safe temporary script body in the evidence artifact and record a digest. The script body must contain no secrets.
2. Run presence-only readiness first; readiness may report only pass/fail booleans and construction status, not provider values.
3. Run exactly one logical PASS-only auditor probe. No rerun, no writer probe, no default-budget report run.
4. Explicitly check `clients.auditor is not None`; if absent, classify `construction_error` / `blocked_before_probe`.
5. Ensure `user_prompt_chars` records the provider-bound auditor payload length, not the literal `PASS` length.
6. If JSON sidecar is produced, validate both syntax and positive allowlist schema: exact key set, scalar types, enum values, no extra fields, and forbidden fields absent by construction.
7. Run the accepted secret scan. Label-only matches are acceptable only when no values are present. Any value leak quarantines the artifact without pasting the value.
8. Treat script exit `0` as "measurement captured"; timeout remains adverse provider-runtime evidence.
9. Obtain independent evidence reviews and controller judgment before any endpoint/config/default/runtime disposition gate.

## Classification Boundaries

- Success below `0.8 * timeout_ms`: `refutes_endpoint_wide_for_time_window` only for the observed time window.
- Success at or above `0.8 * timeout_ms`: `ambiguous_near_timeout`.
- Timeout: `supports_endpoint_or_provider_latency_for_future_disposition_design`.
- Rate limit, network, HTTP error, malformed response or unexpected non-safety exception: `ambiguous_non_timeout`.
- Config or construction failure: `blocked_before_probe`.

None of these classifications authorize endpoint, config, default timeout, retry, provider runtime, prompt, auditor, score-loop, quality gate, golden/readiness or deterministic fallback changes.

## Explicit Non-Changes

This checkpoint does not change current template truth, chapter ids `0-7`, `docs/fund-analysis-template-draft.md`, `contracts.py`, auditor rules, deterministic `analyze/checklist`, `--use-llm` fail-closed behavior, provider timeout/retry defaults, endpoint config, retained report behavior, score-loop, quality gate, golden/readiness, Agent runtime or Dayu dependency status.

## Next Entry

Start `MVP PASS-only timing probe evidence gate`. The only authorized next work is to create the reviewed-safe temporary script body in that gate, run presence-only readiness, run one PASS-only auditor probe under the accepted contract, validate/scan the resulting evidence, obtain evidence reviews and then record controller judgment.
