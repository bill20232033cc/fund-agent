# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Controller Judgment

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Gate`

Controller verdict: `ACCEPT_WITH_NONBLOCKING_RESIDUALS_NOT_READY`

Release/readiness: `NOT_READY`

## Basis

- Rules truth: `AGENTS.md`
- Design truth: `docs/design.md`
- Control truth: `docs/current-startup-packet.md`, `docs/implementation-control.md`
- Accepted implementation plan: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-20260613.md`
- Accepted plan controller judgment: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-controller-judgment-20260613.md`
- Implementation evidence: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md`
- DS review: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-review-ds-20260613.md`
- MiMo review: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-review-mimo-20260613.md`
- DS re-review: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-re-review-ds-20260613.md`
- MiMo re-review: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-re-review-mimo-20260613.md`

## Scope Judgment

Accepted changed files:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/agent_bridge.py`
- `tests/agent/test_runner.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_run_artifacts.py`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-review-ds-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-review-mimo-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-re-review-ds-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-re-review-mimo-20260613.md`

The implementation stayed within the accepted source/test/review write set. No README, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, source acquisition policy, provider default, model, repository/cache/downloader, live command, release command, PR action, push, merge, cleanup, delete, archive or unrelated residue disposition was introduced by this gate.

## Implementation Acceptance

| Slice | Controller disposition | Evidence |
|---|---|---|
| S1 Agent and Service reproducer tests | `ACCEPT` | Agent test proves Chapter 3 pre-provider `ValueError` maps to `blocked_internal_code_bug` / `code_bug` / `llm_exception` with no provider attempt and no secret leakage. Service execution test proves `blocked` orchestration, incomplete final assembly, Chapter 3 `llm_exception` / `code_bug`, `ValueError`, `max_output_chars=12000`, no deterministic fallback and no secret leakage. |
| S2 safe diagnostic propagation | `ACCEPT` | `_exception_runtime_diagnostics(..., max_output_chars=None)` now preserves provider diagnostic caps and adds the safe scalar only to fallback unknown-exception diagnostics. `agent_bridge` threads `input_data.policy.max_output_chars` into task, attempt and runtime diagnostic projection. `_is_code_bug_runtime_diagnostic` is used before provider-runtime fallback in terminal selection and terminal matching. |
| S3 artifact fixture | `ACCEPT` | Incomplete-run artifact test verifies `summary.json`, runtime matrix and `chapters/chapter-03.json` retain Chapter 3 pre-provider `llm_exception` / `code_bug`, provider attempt count `0`, empty provider runtime categories, terminal diagnostic consistency and `max_output_chars=12000`, without raw prompt/provider/secret canaries. |
| S4 validation | `ACCEPT` | Controller reran targeted tests, focused suite, ruff and `git diff --check`; all passed. |

## Finding Disposition

| Finding | Source | Controller disposition | Rationale |
|---|---|---|---|
| F1-LOW: orchestrator test should directly assert `diagnostic.message` redaction | DS review | `ACCEPT_FIXED` | ProCodex added direct assertions on `diagnostics[0].get("message")` for `Authorization`, `Bearer`, `sk-secret` and `prompt raw`; DS re-review marked F1 closed and MiMo re-review found no new issue. |
| F2-LOW: `_execution_request` test helper typed path extension should be recorded as deviation | DS review | `ACCEPT_FIXED_AS_DOCUMENTATION` | Implementation evidence now records the `_execution_request()` `typed_template_path` threading as an accepted nonblocking test helper deviation only, not production behavior; DS re-review marked F2 closed. |
| Service reproducer uses helper path while exact typed writer path can block before writer call | Implementation evidence / reviewer focus item | `ACCEPT_WITH_RESIDUAL` | The Service test still exercises `FundAnalysisService.analyze_with_llm_execution()` and fail-closed behavior; typed cap propagation is independently covered by bridge/orchestrator diagnostics. Exact live/CLI reproduction remains a future controlled diagnostic/live gate, not a blocker for this no-live implementation gate. |
| Exact live `004393 / 2025` provider/LLM completion, content quality and 401/403 provider-response classification | Control truth / review residuals | `DEFER` | This gate is no-live implementation only. Live/provider execution and readiness remain separately authorized future gates. |

## Boundary Judgment

- EID single-source annual-report source policy is preserved. Current operational truth remains `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`.
- Eastmoney, fund-company/CDN, CNINFO, annual-report fallback invocation and source expansion did not re-enter current path.
- `llm_exception` was not added to provider runtime category mapping.
- Pre-provider code bugs remain distinguishable from provider runtime failures by requiring `provider_runtime_category is None`.
- Raw exception messages, prompts, provider bodies, raw responses, headers and credentials are not stored in diagnostics or artifacts.
- Release/readiness remains `NOT_READY`.

## Controller Validation

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

## Accepted Checkpoint Recommendation

This implementation is accepted for local checkpointing. Stage only the accepted files listed in this judgment plus this controller judgment. Do not stage unrelated untracked residue.

Recommended next entry point after local checkpoint and control sync:

`Provider/LLM Chapter 3 Diagnostic Ready-state Disposition Gate`

Purpose: update control truth to record the accepted implementation checkpoint, keep release/readiness `NOT_READY`, and decide whether the next actionable branch is a controlled no-live diagnostic disposition or a separately authorized controlled live provider/LLM re-evidence gate. This next entry must not claim release readiness or provider/LLM content quality.
