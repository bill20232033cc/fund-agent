# Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Review

Date: 2026-06-14

Reviewer: AgentMiMo (independent implementation reviewer)

Gate: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Gate`

Release/readiness: `NOT_READY`

## 1. Scope

Independent implementation review of the no-live narrow fix for the Chapter 3 provider-before `ValueError` / `code_bug` path.

Review target:

- Unstaged diff in `fund_agent/agent/runner.py`, `tests/agent/test_runner.py`, `tests/services/test_chapter_orchestrator.py`.
- Evidence artifact: `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-evidence-procodex-20260614.md`.

Read first:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-controller-judgment-20260614.md`

Excluded:

- `AGENTS.md`, `README.md`, `docs/design.md` workspace changes are pre-existing and outside this gate's write set.
- No source/test/runtime behavior edits performed.
- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.

## 2. Evidence Reviewed

| Evidence | Source |
|---|---|
| Accepted plan and mandatory amendments | `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-controller-judgment-20260614.md` |
| Implementation evidence | `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-evidence-procodex-20260614.md` |
| Unstaged diff | `git diff -- fund_agent/agent/runner.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py` |
| Source: `_run_single_chapter` | `fund_agent/agent/runner.py:304-324` |
| Source: `_exception_task` guard | `fund_agent/agent/runner.py:935-962` |
| Source: `_typed_required_output_items` call site | `fund_agent/agent/runner.py:625` (inside `_writer_input` at line 595) |
| Source: `_terminal_from_exception` | `fund_agent/agent/runner.py:1399-1414` |
| Red test | `tests/agent/test_runner.py:197-247` |
| Orchestrator projection test | `tests/services/test_chapter_orchestrator.py:1649-1713` |
| Existing post-tool test | `tests/agent/test_runner.py:167-194` |
| Existing orchestrator test | `tests/services/test_chapter_orchestrator.py:1587-1646` |

## 3. Findings

未发现实质性问题。

Implementation review walkthrough:

### 3.1 Source change: `_run_single_chapter` (runner.py:304-324)

- `attempt_index = 0` moved before `_writer_input(...)` call. Original placement was after; moving it before the try block ensures `_exception_task` receives a valid `attempt_index=0` on exception. No behavioral change for the non-exception path since `attempt_index` was already `0` before the while loop.
- `_writer_input(...)` wrapped in `try/except Exception`. On exception, returns `_exception_task(title, chapter_id=chapter_id, attempt_index=attempt_index, traces=(), exception=exc, previous_attempts=tuple(attempts))`.
- `attempts` is `list[ChapterAttempt]` initialized as `[]` at line 306, so `tuple(attempts)` = `()`. Type-safe.
- `_chapter_title(...)` remains outside the try/except boundary as required by the narrow gate scope.

### 3.2 Source change: `_exception_task` guard (runner.py:939)

- Guard changed from `len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"` to `len(traces) == 0 or (len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter")`.
- For pre-tool path: `traces=()` → `len(traces) == 0` → True → `current_attempts = previous_attempts` = `()`. Correct.
- For existing writer-tool path: `len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"` → True → `current_attempts = previous_attempts` = `()`. Unchanged behavior.
- For programmatic-audit / LLM-audit paths: `len(traces) >= 1` and tool_name != `"fund.write_chapter"` → falls to else branch → constructs new `ChapterAttempt`. Unchanged behavior.
- The `or` extension is backward-compatible: the new `len(traces) == 0` branch was unreachable before this change (no caller passed `traces=()`), so existing behavior is fully preserved.

### 3.3 Red test: `test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool`

- Injection point: monkeypatches `fund_agent.agent.runner._typed_required_output_items` (module-level reference via `runner_module`). This is the preferred injection point per mandatory amendment #2.
- The monkeypatched function raises `ValueError("Authorization Bearer sk-secret prompt raw")` for `chapter_id == 3` only.
- `_typed_required_output_items` is called at `runner.py:625` inside `_writer_input(...)` at `runner.py:595`. The exception propagates to the new try/except at line 316.
- Assertions verify: `writer.requests == []` (no writer tool call), `task.status == "failed"`, `task.terminal_state == "blocked_internal_code_bug"`, `task.stop_reason == "llm_exception"`, `task.failure_category == "code_bug"`, `task.attempts == ()`.
- Sensitive text assertions verify `"Authorization"`, `"Bearer"`, `"sk-secret"`, `"prompt raw"` are absent from `repr(task.blocked_reasons)`.
- Evidence artifact records pre-fix failure: `FAILED` with `ValueError: Authorization Bearer sk-secret prompt raw` at `runner.py:307` / `runner.py:615`. Red-test-first requirement satisfied.

### 3.4 Orchestrator projection test: `test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool`

- Same monkeypatch injection point via string path `"fund_agent.agent.runner._typed_required_output_items"`.
- Verifies full orchestrator projection: `result.status == "blocked"`, `run.stop_reason == "llm_exception"`, `run.failure_category == "code_bug"`, `first_failed["provider_attempt_count"] == 0`, `first_failed["provider_runtime_categories"] == ()`, `first_failed["max_output_chars"] == 12000`, `first_failed["terminal_runtime_diagnostic_present"] is True`, `first_failed["diagnostic_consistency_status"] == "consistent"`.
- Verifies `diagnostics[0]["error_type"] == "ValueError"`, `diagnostics[0]["max_output_chars"] == 12000`, `diagnostics[0]["provider_runtime_category"] is None`.
- Sensitive text absent from serialized payload. Safe diagnostic projection confirmed.

### 3.5 Scope compliance

- Source write set: `fund_agent/agent/runner.py` only. No Service/Bridge/Orchestrator/Fund writer/source/provider/repair-budget/annual-period LLM changes.
- Test write set: `tests/agent/test_runner.py`, `tests/services/test_chapter_orchestrator.py` only.
- No `docs/design.md`, README, or control-doc changes in the implementation diff.
- EID single-source/no-fallback preserved (no source policy code touched).
- `NOT_READY` preserved (no readiness/release code touched).

### 3.6 Regression preservation

- Existing test `test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime` (post-tool path) passes. This test uses `_FakeWriter(actions={3: ValueError(...)})` which raises inside `write_chapter_tool`, hitting the existing exception handler in the while loop. The new try/except does not interfere.
- Existing test `test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap` passes.
- Existing test `test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic` passes.
- Full focused suite: 123 passed in 0.70s.

## 4. Validation Reviewed or Run

| ID | Command | Result |
|---|---|---|
| V1 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool -q` | Evidence records `1 passed in 0.85s` |
| V2 | `uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool -q` | Evidence records `1 passed in 0.45s` |
| V3 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q` | Independently verified: `3 passed in 0.52s` |
| V4 | `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py -q` | Independently verified: `123 passed in 0.70s` |
| V5 | `uv run ruff check fund_agent/agent/runner.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py` | Independently verified: `All checks passed!` |
| V6 | `git diff --check` | Independently verified: no output (passed) |

## 5. Verdict Table

| Criterion | Status | Evidence |
|---|---|---|
| Implementation matches accepted plan | PASS | Diff matches plan: try/except around `_writer_input`, `_exception_task` with `traces=()`, guard amendment applied |
| Mandatory amendment #1: red-test-first | PASS | Evidence records pre-fix `FAILED` with escaped `ValueError`; source fix proceeded only after red confirmation |
| Mandatory amendment #2: `_typed_required_output_items` injection point | PASS | Both new tests monkeypatch `_typed_required_output_items` |
| Mandatory amendment #3: exact empty-traces `_exception_task()` guard | PASS | `len(traces) == 0 or (len(traces) == 1 and ...)` at runner.py:939 |
| Mandatory amendment #4: preserve non-empty trace behavior | PASS | Existing writer-tool, programmatic-audit and LLM-audit paths unchanged; existing tests pass |
| Mandatory amendment #5: no scope expansion | PASS | No `_chapter_title()`, Service/Bridge/Orchestrator/Fund/provider/default/runtime/repair-budget/annual-period changes |
| Tests prove pre-tool ValueError | PASS | Red test and orchestrator test both inject at `_typed_required_output_items` inside `_writer_input` |
| Tests prove safe diagnostic projection | PASS | Orchestrator test verifies `provider_attempt_count=0`, `max_output_chars=12000`, no provider runtime category, no sensitive text |
| EID single-source/no-fallback preserved | PASS | No source policy code touched |
| `NOT_READY` preserved | PASS | No readiness/release code touched |
| No missing tests for covered paths | PASS | Pre-tool path (new), post-tool path (existing), orchestrator projection (new) all covered |
| No regressions | PASS | Focused suite 123 passed; regression trio 3 passed |
| No unsafe diagnostics | PASS | Sensitive text assertions in both new tests confirm injection text not serialized |

## 6. Residuals

| Residual | Status |
|---|---|
| Exact live `004393 / 2025` Route C full completion unproven | Deferred per plan |
| LLM content quality unproven | Deferred per plan |
| 401/403 provider-response classification unproven | Deferred per plan |
| Annual-period LLM route undesigned | Deferred per plan |
| Chapter repair budget uncalibrated | Deferred per plan |
| Broader pre-run/global `ValueError` paths and `_chapter_title()` failures outside this narrow fix | Accepted residual per plan |
| Release/readiness remains `NOT_READY` | Accepted residual |

## 7. Final Verdict

**PASS**

The implementation correctly applies all five mandatory plan amendments. The red reproducer was added first and confirmed to fail pre-fix by escaped `ValueError`. The `_exception_task` empty-traces guard preserves non-empty trace behavior. Tests prove both pre-tool `ValueError` classification and safe Service/orchestrator diagnostic projection. No scope violations, regressions, or unsafe diagnostics detected.
