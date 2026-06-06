# MVP Provider Endpoint/Path Diagnostic Gate — Local Config/Path Evidence

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `local-only config/path evidence gate`
- Gate number: Gate 2
- Based on accepted Gate 1 checkpoint: `a96a724 gateflow: accept provider endpoint path diagnostic plan`
- Role: local-only evidence; no provider/network/external-state call

This evidence does not authorize or execute a same-process provider adapter minimal check, full analyze rerun, retry, curl/DNS/socket/PASS-only probe, fallback, provider/default/runtime/budget change, Chapter calibration, Agent runtime, multi-year, score-loop, golden/readiness, PR, release, push, merge, or external comment.

## 2. Command Boundary

Command class:

```text
uv run python -c '<inline local inspection script>'
```

The script:

- imported existing repo modules only;
- called `load_llm_provider_config_from_env()`;
- constructed `OpenAICompatibleChapterLLMClient(config=config)` only to inspect local adapter URL shape;
- did not call `generate_chapter()`;
- did not execute `fund-analysis analyze`;
- did not execute network, provider, DNS, socket, curl, PASS-only, fallback, retry, or direct HTTP probe;
- did not print full environment, API key, Authorization header, bearer token, model value, base URL value, or full host value.

## 3. Safe Evidence Output

```json
{
  "adapter_class": "OpenAICompatibleChapterLLMClient",
  "adapter_generate_chapter_called": false,
  "adapter_generate_hash": "f40b569eb0982464",
  "adapter_init_hash": "5304cccc8a901e12",
  "adapter_object_constructed": true,
  "adapter_url_derivation_hash": "6697ea320bf02858",
  "api_key_env_var_label": "default",
  "auditor_timeout_seconds": 60.0,
  "base_url_has_no_query_fragment": true,
  "base_url_present": true,
  "base_url_shape": "absolute_http_url",
  "base_url_terminal_shape": "v1",
  "config_source": "load_llm_provider_config_from_env",
  "config_source_hash": "7f65c8773adc81d0",
  "config_validation": "pass",
  "derived_host_present": true,
  "derived_path_suffix_category": "v1_chat_completions",
  "derived_scheme_category": "http_or_https",
  "effective_api_key_present": true,
  "fund_analysis_analyze_rerun_performed": false,
  "http_client_constructor_path": "httpx.Client(timeout=config.timeout_seconds)",
  "httpx_explicit_proxy_config": "absent",
  "max_output_chars": 12000,
  "model_present": true,
  "network_or_provider_call_performed": false,
  "operation": "local_only_config_path_reconciliation",
  "outcome": "local_config_path_consistent_insufficient",
  "owner": "controller_to_decide_gate3",
  "provider_present": true,
  "provider_supported": true,
  "repair_timeout_fallback_used": true,
  "repair_timeout_seconds": 60.0,
  "schema_version": "provider_endpoint_path_local_evidence.v1",
  "timeout_backoff_seconds": 1.0,
  "timeout_max_attempts": 2,
  "timeout_seconds": 60.0,
  "writer_timeout_seconds": 60.0
}
```

## 4. Interpretation

Outcome: `local_config_path_consistent_insufficient`.

Direct findings:

- typed provider config loaded successfully;
- provider is present and supported;
- model is present, without recording the value;
- base URL is present, absolute HTTP(S), and has no query or fragment;
- API key env var uses the default label, without recording any key value;
- effective API key is present, without recording the value;
- adapter URL derivation produces `v1_chat_completions`;
- no local adapter path mismatch was found;
- the adapter object was constructed, but `generate_chapter()` was not called;
- no network/provider/external-state action occurred.

This local-only evidence is insufficient to explain the prior writer `llm_network_error` / `ConnectError`, because it intentionally stops before any provider connection attempt.

## 5. Owner Routing

- Not `local_config_path_blocked`: config validation passed.
- Not `repo_adapter_path_mismatch`: derived path suffix is expected.
- Accepted Gate 2 outcome: `local_config_path_consistent_insufficient`.

Next controller decision: decide whether to open Gate 3 and authorize exactly one same-process provider adapter minimal check.

## 6. Secret Safety

This artifact contains:

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

Chapter calibration remains blocked because this evidence contains no body chapter accepted draft or accepted conclusion.
