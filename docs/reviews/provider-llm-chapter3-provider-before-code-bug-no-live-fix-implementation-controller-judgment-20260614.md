# Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Controller Judgment

Date: 2026-06-14

Controller: `AgentController`

Gate: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Gate`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment accepts or rejects the no-live implementation for the directly evidenced Chapter 3 provider-before `ValueError` / `code_bug` path.

In scope:

- Review the AgentCodex implementation diff and implementation evidence.
- Aggregate MiMo and DS implementation reviews.
- Verify the accepted no-live validation matrix.
- Decide whether this implementation gate is accepted.

Out of scope:

- Live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.
- EID source policy changes or fallback re-entry.
- Service/Bridge/Orchestrator/Fund writer implementation changes.
- Annual-period LLM route design.
- Repair budget calibration or provider default/runtime/config changes.

## 2. Evidence Reviewed

Truth/control sources:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-controller-judgment-20260614.md`

Implementation and review artifacts:

- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-evidence-procodex-20260614.md`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-review-mimo-20260614.md`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-review-ds-20260614.md`

Implementation diff:

- `fund_agent/agent/runner.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`

## 3. Accepted Implementation Facts

| Fact | Disposition |
|---|---|
| Red reproducer was added before source fix and failed pre-fix by escaped pre-tool `ValueError`. | ACCEPT |
| The red reproducer uses `fund_agent.agent.runner._typed_required_output_items` as the preferred injection point. | ACCEPT |
| `_run_single_chapter(...)` now catches exceptions from initial `_writer_input(...)` construction and returns `_exception_task(...)` with `traces=()`. | ACCEPT |
| `_exception_task(...)` now treats empty traces as no-attempt pre-tool failures and preserves prior writer-tool behavior for one `fund.write_chapter` trace. | ACCEPT |
| Existing non-empty trace behavior for writer-tool, programmatic-audit and LLM-audit exception paths is preserved. | ACCEPT |
| New tests cover Agent runner pre-tool `ValueError` classification and Service/orchestrator safe diagnostic projection. | ACCEPT |
| No Service/Bridge/Orchestrator/Fund writer/source/provider/repair-budget/annual-period LLM implementation changed. | ACCEPT |
| Release/readiness remains `NOT_READY`. | ACCEPTED_RESIDUAL |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS` | Accepted. No material findings. |
| AgentDS | `PASS` | Accepted. No material findings. |

## 5. Validation Results

Controller re-ran the accepted no-live validation matrix.

| ID | Command | Result |
|---|---|---|
| V1 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool -q` | `1 passed in 0.85s` |
| V2 | `uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool -q` | `1 passed in 0.86s` |
| V3 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q` | `3 passed in 0.87s` |
| V4 | `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py -q` | `123 passed in 0.67s` |
| V5 | `uv run ruff check fund_agent/agent/runner.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py` | `All checks passed!` |
| V6 | `git diff --check` | Passed with no output |

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command was run.

## 6. Controller Findings

| Finding | Disposition | Reason |
|---|---|---|
| Implementation matches accepted plan and all mandatory amendments. | ACCEPT | Both reviewers independently verified the red-test-first sequence, exact empty-traces guard and no scope expansion. |
| Diagnostics remain safe. | ACCEPT | New tests inject sensitive text and assert it is absent from Agent blocked reasons and serialized runtime diagnostics; only `ValueError` type is exposed. |
| Non-empty trace behavior is preserved. | ACCEPT | The guard only adds `len(traces) == 0`; existing writer-tool and auditor exception paths remain covered and pass focused tests. |
| `_chapter_title()` and broader pre-run/global exceptions remain outside the fix. | ACCEPTED_RESIDUAL | This was explicitly accepted in the plan judgment and remains future scope unless evidence requires it. |

## 7. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Exact live `004393 / 2025` Route C full completion remains unproven. | Deferred | Separately authorized bounded live re-evidence gate only. |
| LLM content quality remains unproven. | Deferred | Future content-quality/readiness gate. |
| 401/403 provider-response classification remains unproven. | Deferred | Future provider-response negative evidence gate. |
| Annual-period LLM route remains undesigned. | Deferred | Separate design gate. |
| Chapter repair budget remains uncalibrated. | Deferred | Separate calibration gate. |
| Broader pre-run/global `ValueError` paths and `_chapter_title()` failures remain outside this narrow fix. | Accepted residual | Separate no-live evidence/planning gate if needed. |
| Release/readiness remains `NOT_READY`. | Accepted residual | Release/readiness gate only. |

## 8. Final Verdict

VERDICT: ACCEPT_IMPLEMENTATION_NOT_READY

NEXT_ENTRY: `Provider/LLM Chapter 3 Bounded Live Re-evidence Gate`
