# MVP Provider Endpoint/Path Diagnostic Gate — Same-Process Adapter Minimal Evidence

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `same-process adapter minimal check gate`
- Gate number: Gate 3
- Classification: `heavy`
- Based on accepted Gate 2 checkpoint: `764ca00 gateflow: accept provider endpoint local path evidence`
- Role: exactly one same-process provider adapter minimal check

This evidence does not authorize or execute a full analyze rerun, retry command, curl/DNS/socket/PASS-only probe, fallback, provider/default/runtime/budget change, Chapter calibration, Agent runtime, multi-year, score-loop, golden/readiness, PR, release, push, merge, or external comment.

## 2. Command Boundary

Command class:

```text
uv run python -c '<inline same-process adapter minimal check>'
```

The script:

- loaded typed config with `load_llm_provider_config_from_env()`;
- constructed `OpenAICompatibleChapterLLMClient(config=config)`;
- called `OpenAICompatibleChapterLLMClient.generate_chapter()` exactly once;
- used a minimal `ChapterLLMRequest` with no fund document access;
- did not run `fund-analysis analyze`;
- did not run orchestration;
- did not use Host;
- did not use fallback;
- did not use curl, DNS, socket, PASS-only, direct handwritten HTTP, or private provider metadata probe;
- did not override provider/model/base URL/API key/timeout/attempt/backoff/max-output/runtime budget/default/config/env.

The adapter used current configured provider behavior. Its internal timeout-only attempt policy was not changed by this gate.

## 3. Capture Files

| Capture | Path | Byte count |
|---|---:|---:|
| stdout | `reports/llm-runs/provider-endpoint-path-diagnostic-20260606/stdout.txt` | `742` |
| stderr | `reports/llm-runs/provider-endpoint-path-diagnostic-20260606/stderr.txt` | `0` |

The capture directory is ignored by `.gitignore` under `reports/llm-runs/`.

## 4. Safe Evidence Output

```json
{
  "command_kind": "same_process_adapter_minimal_check",
  "curl_dns_socket_pass_probe_performed": false,
  "diagnostics": [
    {
      "operation": "writer",
      "provider_attempt_index": 1,
      "provider_max_attempts": 2,
      "provider_runtime_category": "network",
      "status_code": null,
      "timeout_root_cause_hint": null,
      "timeout_seconds": 60.0
    }
  ],
  "elapsed_seconds": 7.93,
  "fallback_used": false,
  "fund_analysis_analyze_rerun_performed": false,
  "generate_chapter_call_count": 1,
  "provider_defaults_overridden": false,
  "provider_runtime_subcategory": "ConnectError",
  "schema_version": "provider_endpoint_path_adapter_minimal_check.v1",
  "typed_outcome": "provider_runtime_error_non_timeout"
}
```

## 5. Interpretation

Outcome: `provider_runtime_error_non_timeout`.

Direct findings:

- same-process adapter path reached the writer operation;
- provider runtime category is `network`;
- terminal subcategory is `ConnectError`;
- no HTTP status code was available;
- the adapter did not reach a successful response;
- the adapter minimal request failed before any report-generation path, orchestration, Host, or fund document access;
- no full analyze rerun occurred;
- no retry command, external probe, fallback, or defaults override occurred.

This confirms the repo adapter path can reproduce the active non-timeout provider runtime class with a minimal same-process request. It does not identify the exact external root cause, such as DNS, TLS, proxy, route, provider account, provider endpoint, or local egress policy.

## 6. Secret Safety

This artifact and the captured safe JSON contain:

- no API key value;
- no Authorization header;
- no bearer token;
- no model value;
- no base URL value;
- no full host value;
- no full environment dump;
- no prompt text;
- no raw provider response.

Mentions of forbidden terms are policy descriptions only.

## 7. Residual State

Current residual remains `provider_runtime_error_non_timeout`.

Chapter calibration remains blocked because this evidence contains no body chapter accepted draft or accepted conclusion. The minimal adapter check is not a report-generation gate and cannot provide chapter calibration substrate.
