# Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Evidence

Date: 2026-06-14

Worker: AgentCodex / implementation worker

Gate: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Gate`

Release/readiness: `NOT_READY`

## 1. Scope

Implemented the accepted no-live narrow fix for the Chapter 3 provider-before `ValueError` / `code_bug` path.

In scope:

- Add the red reproducer first for `_writer_input(...)` construction failure before the writer tool call.
- Convert the directly proven pre-tool writer input exception into a fail-closed `ChapterTask`.
- Preserve safe Service/orchestrator diagnostic projection for `provider_attempt_count=0` and `max_output_chars=12000`.
- Preserve existing writer-tool, programmatic-audit and LLM-audit exception behavior for non-empty traces.

Out of scope and not performed:

- Live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.
- Eastmoney, fund-company/CDN, CNINFO or fallback re-entry.
- EID source policy, annual-period LLM route, repair budget, provider default, model/base URL, runtime budget or config changes.
- `AGENTS.md`, README, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`.
- Stage, commit, push, PR, delete, archive, cleanup or ignore actions.

## 2. Files Changed

- `fund_agent/agent/runner.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-evidence-procodex-20260614.md`

## 3. Red Test Evidence

Red reproducer added first:

- `tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool`
- Injection point: monkeypatched `fund_agent.agent.runner._typed_required_output_items`
- Injected exception: `ValueError("Authorization Bearer sk-secret prompt raw")`
- Target: Chapter 3, before writer request/tool execution

Pre-fix command:

```text
uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool -q
```

Pre-fix result:

```text
FAILED tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool
ValueError: Authorization Bearer sk-secret prompt raw
```

Failure location:

- `fund_agent/agent/runner.py:307` in `_run_single_chapter(...)`
- `fund_agent/agent/runner.py:615` in `_writer_input(...)`
- The exception escaped before any writer tool call.

Disposition: red reproducer matched the required pre-fix escaped pre-tool `ValueError`; source fix was allowed to proceed.

## 4. Implementation Summary

- Moved `attempt_index = 0` before initial writer input construction in `_run_single_chapter(...)`.
- Wrapped only the initial `_writer_input(...)` call in `try/except Exception`.
- On exception, return `_exception_task(...)` with `traces=()` and the existing chapter title, chapter id and attempt index.
- Updated `_exception_task(...)` with the controller-required guard shape:

```python
if len(traces) == 0 or (len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"):
    attempts = tuple(previous_attempts)
else:
    ...
```

- Added Service/orchestrator projection coverage:
  - `tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool`
  - Confirms no writer request, `llm_exception`, `code_bug`, provider attempt count `0`, no provider runtime category, `max_output_chars=12000`, and no sensitive injected text in serialized diagnostics.

## 5. Validation Results

All authorized validation commands were run.

| ID | Command | Result |
|---|---|---|
| V1 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool -q` | `1 passed in 0.85s` |
| V2 | `uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool -q` | `1 passed in 0.45s` |
| V3 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q` | `3 passed in 0.44s` |
| V4 | `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py -q` | `123 passed in 0.67s` |
| V5 | `uv run ruff check fund_agent/agent/runner.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py` | `All checks passed!` |
| V6 | `git diff --check` | Passed with no output |

## 6. Guardrail Compliance

- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands were run.
- No Service/Bridge/Orchestrator/Fund writer source code was changed.
- No provider defaults, repair budget, runtime budget, config, source policy, fallback or annual-period LLM route was changed.
- `_chapter_title()` remains outside the new try/except boundary as required by the narrow gate.
- Existing writer-tool exception behavior is preserved by the non-empty writer trace guard.
- Programmatic-audit and LLM-audit exception behavior for non-empty traces is preserved.
- Diagnostics assertions confirm injected sensitive text is not serialized.
- `release/readiness` remains `NOT_READY`.

Worker self-check: pass. Assigned gate and allowed write set were preserved; no commit, push or PR action was performed.

## 7. Residuals

| Residual | Status | Owner / next handling |
|---|---|---|
| Exact live `004393 / 2025` Route C full completion remains unproven. | Deferred | Separately authorized bounded live re-evidence gate only. |
| LLM content quality remains unproven. | Deferred | Future content-quality/readiness gate. |
| 401/403 provider-response classification remains unproven. | Deferred | Future provider-response negative evidence gate. |
| Annual-period LLM route remains undesigned. | Deferred | Separate design gate. |
| Chapter repair budget remains uncalibrated. | Deferred | Separate calibration gate. |
| Broader pre-run/global exceptions and `_chapter_title()` failures remain outside this narrow fix. | Accepted residual | Separate no-live evidence/planning gate if needed. |
| Release/readiness remains `NOT_READY`. | Accepted residual | Release/readiness gate only. |

## 8. Final Status

IMPLEMENTATION_COMPLETE_NOT_READY

The accepted no-live narrow fix was implemented and the authorized validation matrix passed. Stop after this artifact; no commit or external-state action was performed.
