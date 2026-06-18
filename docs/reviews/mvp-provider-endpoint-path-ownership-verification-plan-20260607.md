# MVP Provider Endpoint/Path Ownership Verification Plan

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `provider endpoint/path ownership verification gate`
- Classification: `heavy`
- User authorization: current conversation request, "授权你验证一下，根据结果判断是否改变ownership"
- Role: one bounded same-process comparison to decide whether current ownership should change

This gate does not authorize full analyze rerun, retry loop, curl/DNS/socket/PASS-only probe, fallback, provider/default/runtime/budget change, Chapter calibration, Agent runtime, multi-year, score-loop, golden/readiness, PR, release, push, merge, or external comment.

## 2. Current Accepted Baseline

Prior accepted disposition:

- Gate 2 local config/path: internally consistent; derived suffix `v1_chat_completions`.
- Gate 3 minimal adapter: `provider_runtime_error_non_timeout` / `network` / `ConnectError`.
- Gate 4 disposition: `OPERATOR_DEFER_REPO_PAUSE`.

Current owner: provider runtime operator / environment owner.

## 3. Verification Question

Does a same-process direct `httpx` call using the same typed config, same derived URL semantics, and a minimal chat-completions payload succeed while the production adapter call fails?

Interpretation:

- adapter fails and direct equivalent succeeds => ownership may change to repo adapter/request-shape implementation.
- adapter succeeds and direct equivalent succeeds => provider path is currently available; do not infer full report readiness, but ownership may move to later controlled report-generation evidence planning.
- adapter and direct equivalent both fail with same `ConnectError`/network class => ownership remains provider runtime operator / environment owner.
- direct equivalent fails with HTTP/auth/quota while adapter fails network => ownership remains external/provider/operator unless same-source evidence proves repo request-shape mismatch.

## 4. Exact Check

Run one inline Python process that:

1. Loads typed config through `load_llm_provider_config_from_env()`.
2. Constructs `OpenAICompatibleChapterLLMClient(config=config)`.
3. Calls `generate_chapter()` exactly once with a minimal `ChapterLLMRequest`.
4. Calls direct `httpx.Client.post()` exactly once with:
   - the adapter-derived URL value, but without printing it;
   - the same API key header, but without printing it;
   - the same model value, but without printing it;
   - the same minimal messages shape;
   - current configured timeout;
   - no response body printing.

The direct `httpx` call is not curl/DNS/socket/PASS-only. It is a same-process direct HTTP comparison against the adapter path.

## 5. Evidence Safety

Capture only:

- exit code;
- elapsed seconds;
- stdout/stderr byte counts;
- per-call typed outcome;
- per-call operation;
- provider runtime category;
- safe exception type label;
- HTTP status code if any;
- response JSON shape booleans if success;
- no URL, host, model, API key, Authorization header, bearer token, prompt text, raw response body, full environment dump, or provider body.

## 6. Disposition Rules

- `ownership_repo_adapter_request_shape`: adapter fails but direct equivalent succeeds.
- `ownership_operator_environment`: both fail with network/ConnectError, or direct equivalent fails with external HTTP/auth/quota/network class.
- `ownership_evidence_insufficient`: outcomes diverge in a way not attributable without another plan.
- `path_available_but_report_unproven`: both minimal calls succeed; this does not authorize Chapter calibration or full rerun.

## 7. Staging Boundary

Stage only this gate's plan/evidence/disposition artifacts and, if needed, the two control docs. Do not stage unrelated dirty files, runtime code, tests, config, README, provider defaults, or ignored captures.
