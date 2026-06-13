# Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Plan Controller Judgment

Date: 2026-06-14

Controller: `AgentController`

Gate: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Gate`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment accepts or rejects the no-live fix plan for the Chapter 3 provider-before `ValueError` / `code_bug` path.

In scope:

- Review procodex plan artifact.
- Aggregate MiMo and DS plan reviews.
- Decide whether the next gate may enter implementation.
- Preserve source policy, fail-closed semantics and release/readiness posture.

Out of scope:

- Source/test/runtime changes.
- Live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.
- Annual-period LLM route design.
- Repair budget calibration.
- EID source policy, fallback or provider default changes.

## 2. Evidence Reviewed

Truth/control sources:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter3-diagnostic-disposition-20260613.md`
- `docs/reviews/workspace-scope-artifact-disposition-closeout-20260613.md`

Plan and reviews:

- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-procodex-20260613.md`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-review-mimo-20260614.md`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-review-ds-20260614.md`

## 3. Accepted Current Facts

| Fact | Status |
|---|---|
| Prior live Provider/LLM execution for exact `004393 / 2025` failed closed before provider attempt for Chapter 3. | Accepted historical live fact only; not readiness proof. |
| Accepted failure shape is Chapter 3 `llm_exception` / `code_bug` / `ValueError`, provider attempt count `0`. | Accepted failure fact. |
| Disposition artifact chose `PROCEED_TO_NO_LIVE_FIX_GATE`. | Accepted routing basis. |
| Existing no-live tests cover fake writer/client post-request `ValueError`, not the earlier `_writer_input(...)` construction boundary. | Accepted plan/review fact. |
| `_run_single_chapter()` currently calls `_writer_input(...)` before `attempt_index` initialization and before the writer tool call. | Accepted repo fact. |
| `_writer_input(...)`, `build_chapter_writer_input(...)` and typed required-output evidence planning can raise `ValueError` before provider/tool execution. | Accepted repo fact. |
| Release/readiness remains `NOT_READY`. | Accepted residual. |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS` | Accepted. Two low-risk findings are non-blocking but useful implementation constraints. |
| AgentDS | `PASS` | Accepted. Recommended `_exception_task()` guard amendment is accepted as mandatory implementation instruction. |

## 5. Controller Findings

| Finding | Disposition | Reason |
|---|---|---|
| Candidate code path is directly supported by repo facts. | ACCEPT | Both reviews verified `_run_single_chapter()` builds `writer_input` before writer tool execution and before accepted tool-exception handling. |
| Red-test-first stop condition is sufficient. | ACCEPT | The plan requires Test A to fail by escaped `ValueError` before source fix; otherwise implementation must return `NEED_MORE_NO_LIVE_EVIDENCE`. |
| Minimal write set is properly constrained. | ACCEPT | Source write set is limited to `fund_agent/agent/runner.py`; test write set is limited to `tests/agent/test_runner.py` and `tests/services/test_chapter_orchestrator.py`. |
| `_exception_task()` change is under-specified in the plan text. | ACCEPT_WITH_MANDATORY_AMENDMENT | Implementation handoff must use an exact guard condition for empty traces rather than interpreting "preferred minimal behavior". |
| Test injection point could be narrower. | ACCEPT_WITH_NONBLOCKING_AMENDMENT | Implementation should prefer monkeypatching `fund_agent.agent.runner._typed_required_output_items` for the red test. Broader injection alternatives are not needed unless this path cannot reproduce. |
| `_chapter_title()` remains outside the new try/except boundary. | ACCEPTED_RESIDUAL | This gate targets the directly evidenced `_writer_input(...)` boundary only. Full pre-tool/global exception coverage is deferred. |

## 6. Mandatory Implementation Amendments

The next implementation gate must apply these amendments:

1. Add the red test first. If it does not fail before the source fix by escaped pre-tool `ValueError`, stop and report `NEED_MORE_NO_LIVE_EVIDENCE`.
2. Use `fund_agent.agent.runner._typed_required_output_items` as the preferred monkeypatch injection point for Chapter 3 pre-tool `ValueError`.
3. If `_exception_task(...)` is changed, the allowed behavior change is limited to empty traces:

```python
if len(traces) == 0 or (len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"):
    attempts = tuple(previous_attempts)
else:
    ...
```

4. Preserve existing writer-tool, programmatic-audit and LLM-audit exception behavior for non-empty traces.
5. Do not expand the fix to `_chapter_title()`, global pre-run exception coverage, Service/Bridge/Orchestrator/Fund writer code, provider defaults, repair budget, source policy or annual-period LLM route.

## 7. Accepted Validation Matrix

| ID | Command | Status |
|---|---|---|
| V1 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool -q` | Required after implementation. |
| V2 | `uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool -q` | Required after implementation. |
| V3 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q` | Required regression. |
| V4 | `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py -q` | Required focused suite. |
| V5 | `uv run ruff check fund_agent/agent/runner.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py` | Required static check. |
| V6 | `git diff --check` | Required whitespace check. |

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command is authorized by this plan acceptance.

## 8. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Exact live `004393 / 2025` Route C full completion remains unproven. | Deferred | Separately bounded live re-evidence gate only after no-live fix acceptance. |
| LLM content quality remains unproven. | Deferred | Future content-quality/readiness gate. |
| 401/403 provider-response classification remains unproven. | Deferred | Future provider-response negative evidence gate. |
| Annual-period LLM route remains undesigned. | Deferred | Separate design gate. |
| Chapter repair budget remains uncalibrated. | Deferred | Separate calibration gate. |
| Broader pre-run/global `ValueError` paths remain outside this narrow fix. | Accepted residual | Separate no-live evidence/planning gate if needed. |
| Release/readiness remains `NOT_READY`. | Accepted residual | Release/readiness gate only. |

## 9. Final Verdict

VERDICT: ACCEPT_PLAN_WITH_MANDATORY_AMENDMENTS

NEXT_ENTRY: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Gate`
