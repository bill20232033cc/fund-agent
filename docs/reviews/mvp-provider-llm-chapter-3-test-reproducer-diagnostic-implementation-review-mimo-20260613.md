# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Review (AgentMiMo)

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Gate`

Role: AgentMiMo review worker only.

Mode: current changes (no-live implementation review)

Base: `main` (uncommitted workspace changes)

Verdict: **PASS**

## Scope

- Mode: current changes
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: `main`
- Output file: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-review-mimo-20260613.md`
- Included scope:
  - `fund_agent/services/chapter_orchestrator.py` (source)
  - `fund_agent/services/agent_bridge.py` (source)
  - `tests/agent/test_runner.py` (test)
  - `tests/services/test_fund_analysis_service_llm.py` (test)
  - `tests/services/test_chapter_orchestrator.py` (test)
  - `tests/services/test_llm_run_artifacts.py` (test)
  - Evidence artifact: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md`
  - Accepted plan: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-20260613.md`
  - Controller judgment: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-controller-judgment-20260613.md`
- Excluded scope: live/provider/LLM/network/PDF/FDR/source/cache/analyze/checklist/readiness/release/PR/push/merge
- Parallel review coverage: none

## Findings

未发现实质性问题。

## Boundary Checks

### S1/S2/S3/S4 Plan Alignment

| Plan slice | Expected behavior | Actual behavior | Match |
|---|---|---|---|
| S1 Agent reproducer | Chapter 3 ValueError → `blocked_internal_code_bug` / `code_bug` / `llm_exception`, no secret leakage | `tests/agent/test_runner.py:164-193`: task terminal_state `blocked_internal_code_bug`, failure_category `code_bug`, stop_reason `llm_exception`, blocked_reasons do not contain `Authorization`/`Bearer`/`sk-secret`/`prompt raw` | Yes |
| S1 Service reproducer | Chapter 3 ValueError → orchestration `blocked`, final assembly `incomplete`, chapter `failed` / `llm_exception` / `code_bug`, diagnostic error_type `ValueError`, max_output_chars `12000`, no deterministic fallback, no secret leakage | `tests/services/test_fund_analysis_service_llm.py:1021-1069`: all assertions pass per evidence artifact | Yes |
| S2 diagnostic propagation | `_exception_runtime_diagnostics` accepts `max_output_chars` keyword; bridge threads `input_data.policy.max_output_chars` through task/attempt/diagnostic paths | `chapter_orchestrator.py:1050` adds `max_output_chars: int | None = None`; `agent_bridge.py:76,351,406,579,660` thread `max_output_chars` through all diagnostic construction points | Yes |
| S2 code-bug terminal selection | `_is_code_bug_runtime_diagnostic` helper; used in `_terminal_runtime_diagnostic` before provider-runtime fallback; used in `_diagnostic_matches_terminal` | `chapter_orchestrator.py:2615-2617` and `chapter_orchestrator.py:2685-2686` call `_is_code_bug_runtime_diagnostic` at correct positions | Yes |
| S2 no `llm_exception` in provider mapping | `_RUNTIME_STOP_REASON_CATEGORY` must not include `llm_exception` | `chapter_orchestrator.py:190-197`: only `llm_timeout`, `llm_rate_limited`, `llm_malformed_response`, `llm_network_error` | Yes |
| S3 artifact fixture | `_incomplete_code_bug_pre_provider_result()` helper; artifact test verifies summary.json and chapter-03.json retain code-bug lineage | `tests/services/test_llm_run_artifacts.py:502-575` (fixture) and `tests/services/test_llm_run_artifacts.py:172-224` (test): all assertions pass per evidence artifact | Yes |
| S4 validation | All focused no-live tests pass; ruff passes | Evidence artifact shows `129 passed` for focused suite, `All checks passed!` for ruff | Yes |

### Source Policy Preservation

- Current annual-report source remains EID single-source only: `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`.
- No Eastmoney, fund-company/CDN, CNINFO or fallback invocation was introduced.
- No source acquisition, PDF/cache/download or FundDocumentRepository access was added.
- No provider config, defaults, model, base URL or timeout budget was changed.

### No Live/Provider/LLM/Network/PDF/FDR/Source/Cache/Analyze/Checklist/Readiness/Release/PR/Push/Merge Commands

- Implementation only modifies diagnostic/test files.
- No live/provider/LLM/network/PDF/FDR/source/cache commands were introduced.
- No `fund-analysis analyze`, `fund-analysis checklist` or `fund-analysis analyze-annual-period` was added.
- No readiness/release/PR/push/merge actions were taken.

### Safe Diagnostic Behavior

- Pre-provider Chapter 3 `ValueError` maps to `llm_exception` / `code_bug` correctly:
  - `_chapter_failure_category_from_exception(exc)` returns `code_bug` for non-provider exceptions (`chapter_orchestrator.py:1301`).
  - `_provider_runtime_category_from_exception(exc)` returns `None` for `ValueError` (not in the provider exception hierarchy).
  - Resulting diagnostic has `provider_runtime_category=None`, `chapter_failure_category="code_bug"`, `error_type="ValueError"`.
- Provider attempt count is `0` (no attempts made before pre-provider failure).
- `max_output_chars=12000` propagated as safe scalar through `_exception_runtime_diagnostics` fallback path (`chapter_orchestrator.py:1099`).
- Provider diagnostics preserve their own caps; `max_output_chars` is only set on the fallback unknown-exception diagnostic.
- `_sanitize_text()` (`chapter_orchestrator.py:2062-2081`) redacts `Authorization`, `Bearer`, `FUND_AGENT_LLM_API_KEY`, `api_key`, `sk-`, and `prompt` from exception messages.
- No raw exception/prompt/provider/secret leakage verified by tests at all three layers (Agent, Service, artifact).

### No `llm_exception` in Provider Runtime Category Mapping

- `_RUNTIME_STOP_REASON_CATEGORY` (`chapter_orchestrator.py:190-197`) does not include `llm_exception`.
- `_is_code_bug_runtime_diagnostic` (`chapter_orchestrator.py:2691-2714`) correctly requires `provider_runtime_category is None` as one of its four conjunction conditions, keeping code bugs distinguishable from provider runtime failures.

### Test Meaningfulness

Tests are meaningful and not merely asserting implementation artifacts:

- **Agent reproducer** (`test_runner.py:164-193`): asserts task terminal state, failure category, stop reason, and secret non-leakage — all behavioral outcomes.
- **Service reproducer** (`test_fund_analysis_service_llm.py:1021-1069`): asserts orchestration status, final assembly status, chapter status, stop reason, failure category, diagnostic properties, secret non-leakage, and no deterministic fallback — end-to-end behavioral outcomes.
- **Orchestrator test** (`test_chapter_orchestrator.py:1603-1641`): asserts serialized first_failed metadata, runtime matrix row, diagnostic payload, terminal diagnostic presence, consistency status, and secret non-leakage — observable contract outcomes.
- **Artifact test** (`test_llm_run_artifacts.py:172-224`): asserts summary.json retention, chapter-03.json diagnostic lineage, and secret canary absence — persistence contract outcomes.

### Service Reproducer Legacy Path Acceptability

Evidence note states: "the Service reproducer uses the existing legacy execution path helper because the typed path can block before the Chapter 3 writer call on current fixture inputs."

After inspection, this is acceptable:

- The Service test `_execution_request` helper (`test_fund_analysis_service_llm.py:1369-1383`) now threads `typed_template_path` from `chapter_policy` through both `FundLLMRuntimePlan` and `FundLLMExecutionRequest`, so the test actually exercises the typed cap propagation path.
- The orchestrator test (`test_chapter_orchestrator.py:1603-1641`) directly covers the typed `max_output_chars` propagation through `ChapterOrchestrationPolicy` and `serialize_chapter_runtime_diagnostics`.
- The bridge `max_output_chars` threading is covered by the Service reproducer exercising the full `service.analyze_with_llm_execution()` path.
- Therefore the "legacy path" characterization is a documentation artifact; the actual test does exercise typed cap propagation.

## Open Questions

无。

## Residual Risk

- **Exact live source identity `004393 / 2025` not replayed**: accepted planning constraint; this gate is no-live. The implementation reproduces exact safe-metadata failure shape only.
- **Underlying live Chapter 3 `ValueError` root code path may differ from fake no-live `ValueError`**: deferred to later controller-authorized diagnostic gate.
- **LLM content quality, provider readiness, 401/403 classification remain unproven**: deferred; not part of this diagnostic implementation.
- **Release/readiness remains `NOT_READY`**: preserved; this implementation cannot close release/readiness.
- **Multiple code-bug diagnostics from different operations** (e.g., writer + auditor both failing as code_bug): `_terminal_runtime_diagnostic` selects the first matching diagnostic; `_representative_runtime_diagnostics` filters by operation match with terminal. In the current single-operation failure scenario this is correct. If multi-operation code_bug failures arise, the representative set may exclude the second operation's diagnostic — a theoretical edge case that does not affect current correctness.

## Validation Reviewed

Evidence artifact (`docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md`) records:

```text
uv run pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime -q
# 1 passed

uv run pytest tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q
# 1 passed

uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap -q
# 1 passed

uv run pytest tests/services/test_llm_run_artifacts.py::test_artifact_records_chapter_3_pre_provider_code_bug_runtime_lineage -q
# 1 passed

uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py -q
# 129 passed

uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py fund_agent/services/agent_bridge.py fund_agent/agent/runner.py fund_agent/fund/chapter_writer.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py
# All checks passed!

git diff --check
# passed with no output
```

## NOT_READY Preservation

Release/readiness remains `NOT_READY`.

This implementation is no-live diagnostic/test coverage only. It does not prove live provider/LLM completion, LLM content quality, 401/403 provider-response classification, PR state, release state or readiness.

## Residuals

- No blocking stop reason encountered.
- Service typed-path exact Chapter 3 writer reproducer uses legacy execution helper path; typed cap propagation is covered by bridge/orchestrator tests. This is acceptable.
- Live/provider/network/PDF/FDR/source/cache/analyze/checklist/readiness/release commands were not run.
- No raw exception message, prompt text, provider body, raw response, header, credential or secret was required or stored.
