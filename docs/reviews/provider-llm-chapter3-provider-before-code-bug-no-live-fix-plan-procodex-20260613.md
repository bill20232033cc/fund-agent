# Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Plan

Date: 2026-06-13

Worker: AgentCodex / implementation-planning worker

Gate: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Gate`

Release/readiness: `NOT_READY`

## 1. Scope

This is a no-live implementation plan artifact only.

In scope:

- Identify the narrow no-live code path still capable of producing a Chapter 3 provider-before `ValueError` / `code_bug` or equivalent internal failure.
- Specify a minimal source fix only where the path is directly supported by current code/test evidence.
- Specify focused no-live tests and validation commands for a later implementation worker.

Out of scope:

- Source, test, runtime doc or control-doc edits in this planning gate.
- Live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.
- Eastmoney, fund-company/CDN, CNINFO or fallback re-entry.
- EID source policy changes, annual-period LLM route design, repair budget calibration, provider default/model/base URL/runtime budget/config changes.
- `AGENTS.md`, README, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`.
- stage, commit, push, PR, delete, archive, cleanup or ignore actions.

Worker self-check:

- Current role is planning worker, not controller.
- This artifact is the only file written.
- Evidence is no-live code/test/static artifact evidence only.
- No validation command was run in this gate.

## 2. Evidence Reviewed

Control and disposition evidence:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter3-diagnostic-disposition-20260613.md`
- `docs/reviews/workspace-scope-artifact-disposition-closeout-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-controller-judgment-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-controller-judgment-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-controller-judgment-20260613.md`

Allowed source/test evidence:

- `fund_agent/agent/runner.py`
- `fund_agent/services/agent_bridge.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/chapter_writer.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`

Direct code/test anchors:

- `fund_agent/agent/runner.py:305-313`: `_run_single_chapter()` builds `writer_input` before entering the writer tool call and before `writer_execution.exception` handling.
- `fund_agent/agent/runner.py:338-346`: exceptions returned from the writer tool are converted to `_exception_task(...)`.
- `fund_agent/agent/runner.py:588-619`: `_writer_input(...)` calls `build_chapter_writer_input(...)` and `_typed_required_output_items(...)`; its docstring says it can raise `ValueError`.
- `fund_agent/fund/chapter_writer.py:544-596`: `build_chapter_writer_input(...)` can raise `ValueError` before any LLM/provider call.
- `fund_agent/fund/chapter_writer.py:918-1025`: typed required-output evidence plan construction can raise `ValueError` for missing or inconsistent typed availability behavior.
- `fund_agent/agent/runner.py:1389-1471`: unknown non-provider exceptions map to `blocked_internal_code_bug`, `llm_exception`, and `code_bug`.
- `fund_agent/services/agent_bridge.py:659-696`: task-level exceptions are projected to Service runtime diagnostics with `max_output_chars`.
- `fund_agent/services/chapter_orchestrator.py:1043-1102`: unknown exception diagnostics are safe scalar diagnostics and keep `provider_attempt_index=None`.
- `fund_agent/services/chapter_orchestrator.py:2606-2714`: runtime diagnostic terminal selection now accepts pre-provider non-provider `code_bug`.
- `tests/agent/test_runner.py:167-194`: existing Chapter 3 reproducer covers a fake writer/client `ValueError` after the writer request is built.
- `tests/services/test_chapter_orchestrator.py:1606-1645`: existing serialization test covers fake writer/client `ValueError`, provider attempt count `0`, safe cap, and redaction.
- `tests/services/test_fund_analysis_service_llm.py:1024-1065`: existing Service execution test covers fake writer/client `ValueError` projection.

## 3. Current Accepted Facts

- Current accepted live Provider/LLM execution for exact `004393 / 2025` failed closed before provider attempt for Chapter 3: `llm_exception` / `code_bug` / `ValueError`, provider attempt count `0`.
- Accepted root-cause classification is `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`; broader failure class is `PRE_PROVIDER_CODE_BUG_NOT_PROVIDER_RUNTIME`.
- Diagnostic propagation for fake writer/client Chapter 3 `ValueError` is accepted: no-live tests now preserve `max_output_chars=12000`, provider attempt count `0`, safe redaction, and incomplete-run artifact lineage.
- These accepted facts do not prove live provider completion, LLM content quality, 401/403 provider-response classification, readiness or release.
- Existing tests prove the writer/client exception path after a writer request is constructed. They do not directly prove fail-closed behavior for a `ValueError` thrown while constructing `writer_input` before the writer tool is called.

## 4. Candidate Root Code Path

The remaining narrow provider-before code path is:

```text
Service Route C / no-live orchestration
-> run_agent_chapter_orchestration_bridge(...)
-> run_agent_body_chapters(...)
-> _run_single_chapter(...)
-> _writer_input(...)
-> _typed_required_output_items(...) / build_chapter_writer_input(...)
-> ValueError before write_chapter_tool(...)
```

Why this path is still capable:

- `_run_single_chapter()` computes `title` and then calls `_writer_input(...)` before `attempt_index` is initialized and before `write_chapter_tool(...)`.
- `_writer_input(...)` is explicitly documented as raising `ValueError` when Fund writer input construction fails.
- `build_chapter_writer_input(...)` and the typed required-output evidence plan contain `ValueError` branches that can be Chapter-specific and provider-before.
- The existing accepted reproducer injects `ValueError` through the fake writer/client, after the writer request has been built. It does not exercise the pre-tool input construction failure boundary.

Failure shape before fix:

- A Chapter 3 `ValueError` from `_writer_input(...)` can escape the Agent runner instead of becoming a `ChapterTask`.
- If it escapes, Service cannot project it through the accepted `llm_exception` / `code_bug` / provider attempt count `0` diagnostic path.
- This is equivalent to the accepted pre-provider internal failure class, but it is earlier than the currently covered fake writer/client exception path.

## 5. Proposed Minimal Fix

Implementation slice: `S1-pre-tool-writer-input-fail-closed`

Allowed source file:

- `fund_agent/agent/runner.py`

Exact source change:

- In `_run_single_chapter(...)`, initialize `attempt_index = 0` before `writer_input` construction.
- Wrap only the initial `_writer_input(...)` call in `try/except Exception as exc`.
- On exception, return `_exception_task(...)` with:
  - `title`
  - `chapter_id=chapter_id`
  - `attempt_index=attempt_index`
  - `traces=()`
  - `exception=exc`
  - `previous_attempts=tuple(attempts)`
- Adjust `_exception_task(...)` so zero-trace pre-tool exceptions do not create a synthetic attempt record unless the existing dataclass contract requires it. Preferred minimal behavior is:
  - keep `attempts == previous_attempts` when `traces == ()`;
  - keep existing behavior unchanged for writer tool exceptions and auditor/programmatic exceptions.

Expected behavior after fix:

- Chapter 3 pre-tool `ValueError` returns a failed task instead of escaping.
- Task classification remains:
  - `status="failed"`
  - `terminal_state="blocked_internal_code_bug"`
  - `stop_reason="llm_exception"`
  - `failure_category="code_bug"`
  - provider attempt count `0` after Service projection
  - safe `max_output_chars=12000` when projected through Service diagnostics
- No provider runtime category is assigned.
- No prompt, raw exception message, draft, provider body, model name, API key, header, credential or secret is stored in diagnostics or artifacts.

Do not change:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/agent_bridge.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/chapter_writer.py`
- provider defaults, model, base URL, runtime budget, repair budget, source policy, fallback, annual-period LLM route or config.

Conditional stop rule:

- If the first red test below does not reproduce the current escaped `ValueError`, stop and report `NEED_MORE_NO_LIVE_EVIDENCE`; do not force this source fix.

## 6. Proposed Tests

Implementation slice: `S2-focused-no-live-tests`

Allowed test files:

- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`

Test A: Agent runner pre-tool input construction failure

- Add `test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool`.
- Use `monkeypatch` to patch `fund_agent.agent.runner._typed_required_output_items` or another narrow `_writer_input(...)` dependency to raise `ValueError("Authorization Bearer sk-secret prompt raw")` only for `chapter_id == 3`.
- Call `run_agent_body_chapters(...)` with:
  - `_projection((3,))`
  - `AgentLLMClients(writer=_FakeWriter(), auditor=_FakeAuditor())`
  - `AgentRunPolicy(target_chapter_ids=(3,), max_output_chars=12000, typed_template_path="typed_template_contract")`
- Pre-fix expected result: escaped `ValueError`.
- Post-fix expected assertions:
  - no exception escapes;
  - writer client receives no request;
  - run status is `blocked` or `failed`;
  - task `chapter_id == 3`;
  - task `status == "failed"`;
  - task `terminal_state == "blocked_internal_code_bug"`;
  - task `stop_reason == "llm_exception"`;
  - task `failure_category == "code_bug"`;
  - `task.attempts == ()`;
  - `repr(task.blocked_reasons)` contains no `Authorization`, `Bearer`, `sk-secret`, or `prompt raw`.

Test B: Service/orchestrator runtime diagnostic projection

- Add `test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool`.
- Use the same monkeypatch against the Agent runner dependency.
- Call the existing `_orchestrate(...)` helper with:
  - `ChapterOrchestrationPolicy(target_chapter_ids=(3,), max_output_chars=12000, typed_template_path="typed_template_contract")`
  - existing fake writer/auditor clients.
- Post-fix expected assertions:
  - no exception escapes;
  - writer client receives no request;
  - result status is `blocked`;
  - first chapter result has `chapter_id == 3`, `status == "failed"`, `stop_reason == "llm_exception"`, `failure_category == "code_bug"`;
  - `serialize_chapter_runtime_diagnostics(result)["first_failed"]` has:
    - `chapter_id == 3`
    - `stop_reason == "llm_exception"`
    - `category == "code_bug"`
    - `provider_attempt_count == 0`
    - `provider_runtime_categories == ()`
    - `max_output_chars == 12000`
    - `terminal_runtime_diagnostic_present is True`
    - `diagnostic_consistency_status == "consistent"`
  - first runtime diagnostic has `error_type == "ValueError"`, `provider_runtime_category is None`, `max_output_chars == 12000`;
  - serialized payload contains no `Authorization`, `Bearer`, `sk-secret`, or `prompt raw`.

Do not add a full `FundAnalysisService` test unless Test B cannot project through Service bridge. The allowed focused path is sufficient because the proposed source change is in Agent runner and existing Service execution tests already cover fake writer/client exception projection.

## 7. Validation Matrix

Recommended commands for the later implementation gate; do not run live/provider/network commands.

| ID | Command | Purpose | Expected result |
|---|---|---|---|
| V1 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool -q` | Red/green reproducer for the exact pre-tool Agent runner boundary. | Fails before fix by escaped `ValueError`; passes after fix. |
| V2 | `uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool -q` | Service/orchestrator projection and safe runtime diagnostic serialization. | Fails before fix by escaped `ValueError`; passes after fix. |
| V3 | `uv run pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q` | Regression for accepted fake writer/client Chapter 3 diagnostic behavior. | Passes. |
| V4 | `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py -q` | Focused no-live Service/Agent body-run suite. | Passes. |
| V5 | `uv run ruff check fund_agent/agent/runner.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py` | Style/static check for touched files and adjacent accepted tests. | All checks passed. |
| V6 | `git diff --check` | Whitespace sanity. | No output. |

No `fund-analysis analyze`, `fund-analysis checklist`, `fund-analysis analyze-annual-period`, provider, LLM, network, PDF, FDR, source, readiness, release or PR command is authorized by this plan.

## 8. Non-goals / Guardrails

- Preserve EID single-source/no-fallback policy.
- Preserve fail-closed behavior; do not introduce deterministic fallback for `--use-llm`.
- Keep provider-before code bugs distinct from provider runtime failures.
- Do not add `llm_exception` to provider runtime category mapping.
- Do not change repair budget, provider defaults, model/base URL, runtime budget or config.
- Do not design annual-period LLM route or inject multi-year annual evidence into Route C.
- Do not touch `FundDocumentRepository`, source helpers, PDF/cache/parser/Docling paths, Eastmoney, fund-company/CDN, CNINFO or fallback.
- Do not store raw exception messages, prompts, drafts, provider bodies, model names, API keys, headers, credentials or secrets in diagnostics/artifacts.
- Do not update README/control/design docs in this fix gate unless a later controller handoff explicitly authorizes a separate doc-sync artifact.
- Preserve release/readiness as `NOT_READY`.

## 9. Residuals

| Residual | Status | Owner / next handling |
|---|---|---|
| Exact live `004393 / 2025` Route C full completion remains unproven. | Deferred | Separately authorized bounded live re-evidence gate after no-live fix acceptance. |
| LLM content quality remains unproven. | Deferred | Future content-quality/readiness gate. |
| 401/403 provider-response classification remains unproven. | Deferred | Future provider-response negative evidence gate. |
| Annual-period LLM route remains undesigned. | Deferred | Separate annual-period LLM route design gate. |
| Chapter repair budget remains uncalibrated. | Deferred | Separate repair budget calibration gate. |
| Broader pre-run global `ValueError` paths before any target chapter task remain outside this narrow fix. | Deferred | Separate no-live evidence/planning gate if controller wants global fail-closed semantics. |
| Release/readiness remains `NOT_READY`. | Accepted residual | Release/readiness gate only. |

## 10. Stop Condition

Implementation worker must stop and return control to controller if any condition occurs:

- The proposed Test A does not fail before the source fix by escaped `ValueError`.
- The fix requires touching files outside `fund_agent/agent/runner.py`, `tests/agent/test_runner.py`, or `tests/services/test_chapter_orchestrator.py`.
- The fix requires changing provider defaults, model/base URL, runtime budget, repair budget, config, source policy, fallback, annual-period LLM route or runtime docs.
- Any recommended validation command attempts live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR behavior.
- Diagnostics would need to store raw exception text, prompt, draft, provider body, model name, API key, header, credential or secret.
- Focused tests or ruff fail after the minimal fix and the failure is not directly caused by this narrow runner boundary.

If the red test does not reproduce, final recommendation must become:

`NEED_MORE_NO_LIVE_EVIDENCE`

## 11. Final Recommendation

Recommendation: `PROCEED_TO_MINIMAL_NO_LIVE_FIX`

Rationale:

- Current accepted diagnostics already cover fake writer/client provider-before Chapter 3 `ValueError`.
- Code evidence shows an earlier pre-tool `writer_input` construction boundary can still throw `ValueError` before the accepted writer tool exception path.
- The minimal fix is limited to Agent runner fail-closed conversion for that pre-tool boundary and does not alter provider runtime, source policy, fallback, repair budget, config, annual-period LLM route, deterministic default path or readiness posture.

Required next entry:

`Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Implementation Gate`

The next gate should first add the focused red reproducer. If it does not reproduce the escaped pre-tool failure, do not implement the source change; return `NEED_MORE_NO_LIVE_EVIDENCE`.
