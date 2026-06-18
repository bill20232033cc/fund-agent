# MVP Provider Endpoint/Path Diagnostic Gate — Local Config/Path Controller Judgment

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `local-only config/path evidence gate`
- Gate number: Gate 2
- Classification: `heavy`
- Prior accepted checkpoint: `a96a724 gateflow: accept provider endpoint path diagnostic plan`
- Role: controller judgment for local-only evidence

This judgment does not authorize full analyze rerun, retry, curl/DNS/socket/PASS-only probe, fallback, provider/default/runtime/budget change, Chapter calibration, Agent runtime, multi-year, score-loop, golden/readiness, PR, release, push, merge, or external comment.

## 2. Reviewed Inputs

- Gate 1 plan: `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-20260606.md`
- Gate 1 controller judgment: `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-controller-judgment-20260606.md`
- Gate 2 evidence: `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-local-config-path-evidence-20260606.md`

## 3. Evidence Acceptance

Decision: `EVIDENCE_ACCEPTED`.

Direct accepted facts:

- `load_llm_provider_config_from_env()` loaded typed provider config successfully.
- Provider is present and supported.
- Model is present, with no model value recorded.
- Base URL is present, absolute HTTP(S), and has no query or fragment; no URL value or full host value was recorded.
- Effective API key is present, with no key value recorded.
- API key env var label is `default`, with no custom env var name recorded.
- Adapter construction reached `OpenAICompatibleChapterLLMClient(config=config)`.
- Adapter URL derivation shape is `v1_chat_completions`.
- No `generate_chapter()` call occurred.
- No network/provider/external-state action occurred.
- No `fund-analysis analyze` rerun occurred.

## 4. Outcome

Accepted outcome: `local_config_path_consistent_insufficient`.

Reasoning:

- Not `local_config_path_blocked`, because config validation passed.
- Not `repo_adapter_path_mismatch`, because derived path suffix category is expected.
- The local-only check cannot explain the prior writer `llm_network_error` / `ConnectError`, because it intentionally stops before provider connection.

## 5. Residual Owner

Current residual remains `provider_runtime_error_non_timeout`.

No repo implementation gate is opened by Gate 2, because there is no local evidence of adapter path mismatch.

No operator defer disposition is final yet, because Gate 2 deliberately cannot test whether the adapter can complete a minimal provider request.

## 6. Gate 3 Authorization

Gate 3 is authorized to open as `same-process adapter minimal check gate`.

Authorization is narrow:

- exactly one Python process;
- exactly one minimal `OpenAICompatibleChapterLLMClient.generate_chapter()` call;
- no `fund-analysis analyze`;
- no orchestration;
- no Host;
- no fund document access;
- no retry command or loop;
- no curl/DNS/socket/PASS-only/direct HTTP/private metadata probe;
- no fallback;
- no provider/model/base URL/API key/timeout/attempt/backoff/max-output/runtime budget/default/config/env change;
- no prompt text, raw provider response, API key, Authorization header, bearer token, model value, base URL value, full host value, or full environment dump in evidence.

The adapter may perform its current timeout-only internal behavior if the existing config already does so. This judgment does not change those defaults.

## 7. Chapter Calibration Boundary

Chapter calibration remains blocked.

Gate 2 contains no body chapter accepted draft or accepted conclusion. A future Gate 3 `minimal_adapter_success` would prove only that the same-process adapter can complete a tiny request; it still would not unlock Chapter calibration without separate same-source report-generation evidence.

## 8. Staging Boundary

Stage only:

- `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-local-config-path-evidence-20260606.md`
- `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-local-config-path-controller-judgment-20260606.md`

Do not stage unrelated dirty files, control docs, runtime code, tests, config, README, provider defaults, or report captures.

## 9. Verdict

`ACCEPTED`

Proceed to Gate 3 same-process adapter minimal check under the exact authorization above.
