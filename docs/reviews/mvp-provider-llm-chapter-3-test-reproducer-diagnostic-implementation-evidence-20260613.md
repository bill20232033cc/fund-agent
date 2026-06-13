# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Evidence

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Gate`

Role: implementation worker only

Status: `IMPLEMENTED_NOT_READY`

Release/readiness: `NOT_READY`

## Changed Files

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/agent_bridge.py`
- `tests/agent/test_runner.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_run_artifacts.py`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md`

## Implementation Summary

### S1 - Agent And Service Reproducer Tests

- Added Agent no-live Chapter 3 `ValueError` reproducer proving:
  - task terminal state is `blocked_internal_code_bug`;
  - task failure category is `code_bug`;
  - stop reason is `llm_exception`;
  - no provider runtime attempt/diagnostic path is introduced;
  - secret-like exception text is not exposed in blocked reasons.
- Added Service execution no-live reproducer proving Chapter 3 pre-provider
  `ValueError` projects to:
  - orchestration `blocked`;
  - final assembly `incomplete`;
  - Chapter 3 `failed`;
  - stop reason `llm_exception`;
  - failure category `code_bug`;
  - `error_type=ValueError`;
  - `max_output_chars=12000`;
  - no deterministic final report fallback.
- Implementation note: the Service reproducer uses the existing legacy execution
  path helper because the typed path can block before the Chapter 3 writer call
  on current fixture inputs. Typed policy cap propagation is covered by S2
  bridge/orchestrator tests.

### S2 - Safe Pre-provider Runtime Diagnostic Propagation

- Extended `_exception_runtime_diagnostics(..., *, max_output_chars=None)` and
  set `max_output_chars` only on fallback unknown-exception diagnostics.
- Preserved provider diagnostic enrichment behavior; provider-provided caps are
  not overwritten.
- Threaded `input_data.policy.max_output_chars` through `agent_bridge` task,
  attempt and task-level runtime diagnostic projection.
- Added `_is_code_bug_runtime_diagnostic(result, diagnostic)` and used it for
  terminal diagnostic selection and terminal diagnostic matching before the
  provider-runtime fallback.
- Did not add `llm_exception` to provider-runtime category mapping.

### S3 - Artifact Code-bug / Pre-provider Fixture

- Added `_incomplete_code_bug_pre_provider_result()` fixture with accepted
  Chapter 1 and failed Chapter 3.
- Added artifact test proving `summary.json`, runtime matrix and
  `chapters/chapter-03.json` retain:
  - Chapter 3 `llm_exception` / `code_bug`;
  - provider attempt count `0`;
  - empty provider runtime categories;
  - terminal diagnostic present and consistent;
  - `max_output_chars=12000`;
  - `error_type=ValueError`.
- Artifact test confirms prompt/raw/provider/secret canaries are absent.

### S4 - Focused Regression And Boundary Checks

- Ran all required no-live validation commands listed below.
- No README, design doc, control doc, source policy, provider config, cache,
  downloader, repository, model/default or release/readiness file was modified.

## Validation Commands And Results

```text
uv run pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime -q
# 1 passed
```

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q
# 1 passed
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap -q
# 1 passed
```

```text
uv run pytest tests/services/test_llm_run_artifacts.py::test_artifact_records_chapter_3_pre_provider_code_bug_runtime_lineage -q
# 1 passed
```

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py -q
# 129 passed
```

```text
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py fund_agent/services/agent_bridge.py fund_agent/agent/runner.py fund_agent/fund/chapter_writer.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py
# All checks passed!
```

```text
git diff --check
# passed with no output
```

## Source Policy Preservation

Current annual-report source policy is preserved as EID single-source only:
`selected_source=eid`, `source_mode=single_source_only`,
`fallback_enabled=false`.

This implementation did not modify Eastmoney, fund-company/CDN, CNINFO,
fallback invocation, repository/cache/downloader/source acquisition, provider
defaults, model, runtime config or deterministic fallback behavior.

## NOT_READY Preservation

Release/readiness remains `NOT_READY`.

This implementation is no-live diagnostic/test coverage only. It does not prove
live provider/LLM completion, LLM content quality, 401/403 provider-response
classification, PR state, release state or readiness.

## Residuals / Stop Reasons

- No blocking stop reason encountered.
- Service typed-path exact Chapter 3 writer reproducer remains constrained by
  current fixture/input preconditions that can block before writer invocation;
  this implementation covered typed cap propagation in bridge/orchestrator
  diagnostics and used the existing Service execution helper path to reproduce
  the writer `ValueError` failure shape.
- `_execution_request()` in
  `tests/services/test_fund_analysis_service_llm.py` was narrowly extended to
  thread `typed_template_path` consistently when a test passes an explicit
  `ChapterOrchestrationPolicy`. This is an accepted nonblocking test helper
  deviation only; it is not production behavior and does not change Service
  runtime request construction.
- Live/provider/network/PDF/FDR/source/cache/analyze/checklist/readiness/release
  commands were not run.
- No raw exception message, prompt text, provider body, raw response, header,
  credential or secret was required or stored.
