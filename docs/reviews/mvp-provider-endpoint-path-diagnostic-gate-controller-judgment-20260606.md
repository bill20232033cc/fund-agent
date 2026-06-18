# MVP Provider Endpoint/Path Diagnostic Gate — Controller Judgment

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `provider endpoint/path diagnostic planning gate`
- Classification: `heavy`
- Current accepted checkpoint before this gate: `21cf21f gateflow: accept post-operator controlled live rerun evidence`
- Role: controller judgment for Gate 1 planning only

This judgment does not authorize local evidence execution, same-process provider adapter call, full analyze rerun, retry, curl/DNS/socket/PASS-only probe, fallback, provider/default/runtime/budget change, Chapter calibration, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR, release, push, merge, or external issue/comment action.

## 2. Reviewed Inputs

- Plan: `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-20260606.md`
- AgentDS revised plan review: `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-review-ds-20260606.md`
- AgentMiMo unavailable + local fallback review: `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-review-mimo-20260606.md`
- Control truth: `docs/implementation-control.md`
- Startup packet: `docs/current-startup-packet.md`
- Source facts referenced by plan/reviews:
  - `fund_agent/config/llm.py`
  - `fund_agent/services/llm_provider.py`
  - `fund_agent/fund/chapter_writer.py`

## 3. Review Disposition

AgentDS verdict: `PASS`.

AgentMiMo was dispatched twice through clean tmux pane `agents:0.2`; both attempts failed before artifact creation with:

```text
API Error: Unable to connect to API (UNKNOWN_CERTIFICATE_VERIFICATION_ERROR)
```

This is reviewer availability failure, not a plan finding. A local fallback adversarial review was written to the intended MiMo review artifact path and returned `PASS_WITH_NON_BLOCKING_OBSERVATIONS`.

Controller disposition: review sufficiency accepted for this docs-only planning gate. The fallback deviation is acceptable because Gate 1 changes no code, config, runtime defaults, provider behavior, external state, or control docs.

## 4. Plan Finding Disposition

No blocking findings.

Accepted non-blocking improvements:

- Gate 2's third local-only outcome now has a stable label: `local_config_path_consistent_insufficient`.
- Gate 1 validation now explicitly checks `git diff --cached --name-only` and restricts staging to this gate's plan/review/controller artifacts.

Deferred non-blocking watchpoints:

- Gate 2 evidence must avoid printing raw `LLMProviderConfigError` messages if doing so would reveal an explicit custom API key env var name.
- Gate 2 evidence should record whether its inspection was executed inline or from an ignored temporary path.

These watchpoints belong to the Gate 2 local-only evidence artifact and, if needed, the Gate 4 diagnostic disposition artifact.

## 5. Accepted Gate 1 Plan

Decision: `PLAN_ACCEPTED`.

The accepted Gate 1 plan defines this exact sequence:

1. Gate 2 `local-only config/path evidence gate`
   - use existing repo code only;
   - inspect typed provider config and adapter path semantics;
   - output only boolean/hash/redacted evidence;
   - no network, no provider call, no curl/DNS/socket/PASS-only probe, no defaults/config/runtime changes.
2. Gate 3 `same-process adapter minimal check gate`
   - may open only if Gate 2 outcome is `local_config_path_consistent_insufficient`;
   - requires a separate controller judgment authorizing external state;
   - allows exactly one minimal `OpenAICompatibleChapterLLMClient.generate_chapter()` call;
   - saves no prompt, no raw response, no model value, no base URL value, no full host, no API key, no Authorization/Bearer token.
3. Gate 4 `diagnostic disposition gate`
   - routes to repo implementation, operator defer, or later request-shape / long-running provider path diagnostic.
4. Gate 5 `controlled live rerun evidence gate`
   - may open only after path diagnostic shows environment and repo provider path are available;
   - allows exactly one unchanged-default `006597 / 2024 --use-llm`;
   - success signal is body chapter accepted draft/conclusion evidence, not merely exit code.
5. Gate 6 `Chapter acceptance calibration gate`
   - may open only after at least one body chapter has accepted draft/conclusion evidence.

Long-line ordering remains: Chapter calibration before Agent runtime planning; Agent runtime before multi-year; multi-year before score-loop. PR/release remain out of scope until separately authorized.

## 6. Current Residual And Blockers

The current residual remains `provider_runtime_error_non_timeout`.

The latest accepted live evidence still shows:

- operator evidence asserted `environment_available=yes`;
- one controller-authorized unchanged-default live rerun exited `1`;
- stdout was independently captured as `0` bytes;
- retained artifact exists at `reports/llm-runs/006597-2024-20260606T142143Z-host_run_55732009db674b9/`;
- all six body chapters failed at writer operation with `llm_network_error` / `ConnectError`;
- no body chapter has accepted draft or accepted conclusion.

Chapter calibration remains blocked because there is no accepted draft/conclusion substrate.

## 7. Explicit Non-Authorization

Gate 1 authorizes no diagnostic evidence execution.

Specifically not authorized:

- Check A execution in this gate;
- Check B / same-process provider adapter call in this gate;
- full `fund-analysis analyze` rerun;
- retry command or loop;
- curl/DNS/socket/PASS-only/direct HTTP/private provider metadata probe;
- fallback;
- provider/model/base URL/API key/timeout/attempt/backoff/max-output/runtime budget/default/config/env change;
- runtime code, tests, config, README, template, Host, Agent, multi-year runtime, score-loop, golden/readiness changes;
- Chapter acceptance calibration;
- PR, push, release, merge, mark-ready, reviewer request, branch deletion, or public comment.

## 8. Next Entry Point

Next gate: `local-only config/path evidence gate`.

Gate 2 objective:

- confirm the repo's actual provider factory, adapter, httpx/proxy/config source path;
- produce only boolean/hash/redacted evidence;
- classify outcome as `local_config_path_blocked`, `repo_adapter_path_mismatch`, or `local_config_path_consistent_insufficient`;
- stop before any network/provider/external-state action.

Gate 3 is not authorized by this judgment. It can open only after Gate 2 is insufficient and a separate controller judgment authorizes external state.

## 9. Staging Boundary

Stage only:

- `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-20260606.md`
- `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-review-ds-20260606.md`
- `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-review-mimo-20260606.md`
- `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-controller-judgment-20260606.md`

Do not stage tracked `pyproject.toml`, unrelated untracked review artifacts, `fund_agent/tools/`, `reports/manual-llm-smoke/`, `reviews/`, `scripts/claude_mimo_simple.py`, control docs, runtime code, tests, config, README, provider defaults, or report captures.

## 10. Verdict

`PLAN_ACCEPTED`

Gate 1 is accepted as a planning/controller gate only. Proceed to Gate 2 local-only config/path evidence after this Gate 1 accepted checkpoint is validated locally.
