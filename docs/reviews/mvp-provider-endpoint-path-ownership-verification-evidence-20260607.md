# MVP Provider Endpoint/Path Ownership Verification Evidence

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `provider endpoint/path ownership verification gate`
- Classification: `heavy`
- User authorization: current conversation request, "授权你验证一下，根据结果判断是否改变ownership"
- Plan artifact: `docs/reviews/mvp-provider-endpoint-path-ownership-verification-plan-20260607.md`
- Role: one bounded same-process comparison to decide whether active residual ownership changes

This evidence does not authorize full analyze rerun, retry loop, curl/DNS/socket/PASS-only probe, fallback, provider/default/runtime/budget change, Chapter calibration, Agent runtime, multi-year, score-loop, golden/readiness, PR, release, push, merge, or external comment.

## 2. Command Boundary

Command class:

```text
uv run python -c '<inline adapter-vs-direct-httpx comparison>'
```

The script:

- loaded typed config through `load_llm_provider_config_from_env()`;
- derived the same OpenAI-compatible chat completions URL shape without printing URL or host;
- called `OpenAICompatibleChapterLLMClient.generate_chapter()` exactly once;
- called direct `httpx.Client.post()` exactly once using the same typed config, same derived URL semantics, same minimal message shape, and same timeout class;
- did not run `fund-analysis analyze`;
- did not use Host, orchestration, or fund document access;
- did not run curl, DNS, socket, PASS-only, private metadata, fallback, or retry loop;
- did not override provider/model/base URL/API key/timeout/attempt/backoff/max-output/runtime budget/default/config/env.

## 3. Capture Files

| Capture | Path | Byte count |
|---|---:|---:|
| stdout | `reports/llm-runs/provider-endpoint-path-ownership-verification-20260607/stdout.txt` | `1283` |
| stderr | `reports/llm-runs/provider-endpoint-path-ownership-verification-20260607/stderr.txt` | `0` |

The capture directory is ignored by `.gitignore` under `reports/llm-runs/`.

## 4. Safe Evidence Output

```json
{
  "adapter_generate_chapter_call_count": 1,
  "adapter_result": {
    "call": "adapter",
    "diagnostics": [
      {
        "operation": "writer",
        "provider_attempt_index": 1,
        "provider_max_attempts": 2,
        "provider_runtime_category": "network",
        "status_code": null,
        "timeout_seconds": 60.0
      }
    ],
    "elapsed_seconds": 8.212,
    "exception_label": "ConnectError",
    "outcome": "network"
  },
  "curl_dns_socket_pass_probe_performed": false,
  "derived_host_present": true,
  "derived_path_suffix_category": "v1_chat_completions",
  "derived_scheme_category": "http_or_https",
  "direct_httpx_equivalent_call_count": 1,
  "direct_httpx_equivalent_result": {
    "call": "direct_httpx_equivalent",
    "elapsed_seconds": 7.686,
    "exception_label": "ConnectError",
    "outcome": "network",
    "status_code": null
  },
  "elapsed_seconds": 15.926,
  "fallback_used": false,
  "fund_analysis_analyze_rerun_performed": false,
  "host_orchestration_fund_document_access_performed": false,
  "operation": "same_process_adapter_vs_direct_httpx_equivalent",
  "ownership_disposition": "ownership_operator_environment",
  "provider_defaults_overridden": false,
  "schema_version": "provider_endpoint_path_ownership_verification.v1"
}
```

## 5. Interpretation

Outcome: `ownership_operator_environment`.

Direct findings:

- production adapter minimal call failed as `network` / `ConnectError`;
- direct same-process `httpx` equivalent call also failed as `network` / `ConnectError`;
- both calls used the same derived path category `v1_chat_completions`;
- no HTTP status code was available in either call;
- the failure reproduced outside the repo adapter wrapper while preserving the same config/path/request class;
- there is no evidence that direct HTTP succeeds while adapter fails.

This result does not support changing ownership to repo adapter/request-shape implementation.

## 6. Secret Safety

This artifact and the captured safe JSON contain:

- no API key value;
- no Authorization header value;
- no bearer token;
- no model value;
- no base URL value;
- no full host value;
- no full environment dump;
- no prompt text;
- no raw provider response body.

Mentions of forbidden terms are policy descriptions only.

## 7. Ownership Decision Input

Accepted disposition candidate: keep ownership with provider runtime operator / environment owner.

The evidence does not identify whether the exact external cause is DNS, TLS, proxy, provider account, route, endpoint availability, local egress policy, or another environment/provider condition. That remains operator-owned unless future same-source evidence proves otherwise.
