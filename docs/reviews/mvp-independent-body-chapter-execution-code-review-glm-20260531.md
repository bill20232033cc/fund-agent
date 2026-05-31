# MVP Independent Body Chapter Execution — Code Review (GLM)

## Review Context

- Gate: `MVP independent body chapter execution gate`
- Role: Gateflow code review worker (GLM), not implementation worker
- Branch: `codex/local-reconciliation`
- Approved plan: `docs/reviews/mvp-independent-body-chapter-execution-plan-20260531.md`
- Implementation evidence: `docs/reviews/mvp-independent-body-chapter-execution-implementation-evidence-20260531.md`
- Reviewer: GLM
- Date: 2026-05-31

## Scope

Reviewed files:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `fund_agent/services/final_chapter_assembler.py` (read-only, no production change)
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_final_chapter_assembler.py`
- `tests/ui/test_cli.py`

Not modified, read for context:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-independent-body-chapter-execution-plan-20260531.md`
- `docs/reviews/mvp-independent-body-chapter-execution-implementation-evidence-20260531.md`

## Verdict: PASS

No blocking findings. All seven review criteria are satisfied.

## Findings

### Criterion 1: Chapter 1-6 independent execution

**PASS.** `orchestrate_chapters()` at `chapter_orchestrator.py:601-612` uses a simple per-chapter loop that calls `_run_single_chapter()` for every `chapter_id` in `policy.target_chapter_ids`. There is no `stop_remaining` flag, no early-exit on failure, and no `_skipped_result()` call for prior body chapter failures. Chapter 2-6 always receive real writer requests regardless of chapter 1 outcome.

Tests:
- `test_chapter_1_timeout_does_not_skip_chapters_2_to_6` (`test_chapter_orchestrator.py:1643`): verifies all 6 chapters enter writer after chapter 1 timeout.
- `test_mixed_body_chapter_matrix_preserves_each_chapter_outcome` (`test_chapter_orchestrator.py:1674`): verifies mixed accepted/failed/blocked matrix with correct per-chapter status/stop_reason/failure_category/failure_subcategory.
- `test_all_blocked_body_chapters_all_execute_and_status_blocked` (`test_chapter_orchestrator.py:1726`): verifies all 6 chapters execute even when all fail.

### Criterion 2: fail_fast is legacy/no-op

**PASS.** `ChapterOrchestrationPolicy.fail_fast` defaults to `False` (`chapter_orchestrator.py:291`). The docstring at line 283 explicitly states it is a legacy parameter for API compatibility. The body chapter loop at lines 601-612 does not branch on `policy.fail_fast`. No code path in `orchestrate_chapters()` reads `fail_fast`.

Test:
- `test_fail_fast_true_is_legacy_noop_and_later_chapter_executes` (`test_chapter_orchestrator.py:1613`): verifies `fail_fast=True` does not prevent chapter 2 from executing after chapter 1 timeout.

### Criterion 3: dependency_missing only for true dependency

**PASS.** `_WRITER_STOP_REASON_MAPPING` at `chapter_orchestrator.py:115` maps only `chapter_requires_accepted_conclusions` to `("blocked", "dependency_missing")`. No body chapter failure produces `dependency_missing` — the mapping is exclusively for a true writer-contract dependency stop reason. Prior body chapter failures produce their own real stop reasons (e.g. `llm_timeout`, `prompt_contract`, `fact_gap`).

Test:
- `test_dependency_missing_only_for_true_writer_dependency_not_prior_failure` (`test_chapter_orchestrator.py:1745`): verifies `_map_writer_stop_reason` produces `dependency_missing` only for `chapter_requires_accepted_conclusions`, and that a full orchestration with chapter 1 timeout has no `dependency_missing` in any result row.

### Criterion 4: Final assembly fail-closed

**PASS.** `final_chapter_assembler.py:247-253` collects `body_conclusions` only from chapters where `accepted_conclusion is not None`. `source_chapter_ids` is derived exclusively from these accepted conclusions. Any blocked/failed body chapter has `accepted_conclusion=None` and is excluded. `_validate_orchestration()` ensures orchestration must be `accepted` for a complete report. `report_markdown` is `None` for incomplete status.

No production change was made to `final_chapter_assembler.py`.

Tests:
- `test_partial_orchestration_with_all_rows_excludes_blocked_required_chapter` (`test_final_chapter_assembler.py:119`): verifies `source_accepted_chapter_ids == (1, 2, 4, 5, 6)` and chapter 3 is excluded.
- `test_blocked_orchestration_with_all_rows_has_no_report_and_only_accepted_sources` (`test_final_chapter_assembler.py:172`): verifies `source_accepted_chapter_ids == ()` and `report_markdown is None`.
- `test_incomplete_when_orchestration_not_accepted` (`test_final_chapter_assembler.py:64`): verifies `report_markdown is None` for partial/blocked status.

### Criterion 5: CLI chapter matrix safe output

**PASS.** `_chapter_matrix_summary()` at `cli.py:874-899` reads only `chapter_id`, `status`, `stop_reason`, `failure_category`, `failure_subcategory` via `getattr()` with `"unknown"` defaults. No issue messages, prompts, drafts, provider responses, API keys, or headers are accessed.

Tests:
- `test_analyze_cli_use_llm_incomplete_prints_safe_all_chapter_matrix` (`test_cli.py:1579`): verifies stderr contains `chapter_matrix=` with rows for all 3 chapters (failed/accepted/blocked), no `dependency_missing` skips for chapters 2-3, and negative assertions for 13 forbidden terms including `message`, `Authorization`, `Bearer`, `sk-`, `api_key`, `system_prompt`, `user_prompt`, `draft_markdown`, `raw_response`, `raw audit`, `provider_response`, `provider body`, `model_name`, `header`, `key`.
- `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` (`test_cli.py:1668`): verifies additional negative assertions for `writer` (allowed), `auditor` (forbidden), `programmatic` (forbidden), plus all standard leakage checks.

### Criterion 6: Test coverage

**PASS.** All gate acceptance criteria are covered by targeted tests:

| Acceptance criterion | Test(s) |
|---|---|
| Ch 1 failure does not skip ch 2-6 | `test_chapter_1_timeout_does_not_skip_chapters_2_to_6`, `test_fail_fast_true_is_legacy_noop_and_later_chapter_executes` |
| Mixed matrix preserves each outcome | `test_mixed_body_chapter_matrix_preserves_each_chapter_outcome` |
| All blocked still executes all | `test_all_blocked_body_chapters_all_execute_and_status_blocked` |
| `dependency_missing` only for true dep | `test_dependency_missing_only_for_true_writer_dependency_not_prior_failure` |
| `first_failed` does not hide matrix | `test_first_failed_diagnostic_keeps_full_chapter_matrix` |
| Final assembly fail-closed on partial | `test_partial_orchestration_with_all_rows_excludes_blocked_required_chapter` |
| Final assembly fail-closed on blocked | `test_blocked_orchestration_with_all_rows_has_no_report_and_only_accepted_sources` |
| `source_accepted_chapter_ids` excludes blocked | Same two tests above |
| CLI matrix has all rows | `test_analyze_cli_use_llm_incomplete_prints_safe_all_chapter_matrix` |
| CLI matrix no leakage | Same test + `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` |
| CLI exit 1 + empty stdout | All `--use-llm` incomplete tests |

### Criterion 7: No forbidden scope touched

**PASS.** Changed files are limited to `chapter_orchestrator.py`, `cli.py`, and their tests + `test_final_chapter_assembler.py`. No changes to:

- `fund_agent/fund/chapter_writer.py` or `fund_agent/fund/chapter_auditor.py`
- `fund_agent/config/` or `fund_agent/services/llm_provider.py`
- Score, quality gate, golden, fixture, snapshot, manifest files
- `AGENTS.md`, `docs/fund-analysis-template-draft.md`
- Host/Agent/dayu packages

`final_chapter_assembler.py` was read but not modified in production code.

## Residual Risks

1. **No real provider smoke.** The evidence confirms validation was limited to targeted pytest and lint. Real provider behavior under independent chapter execution is untested.
2. **`_skipped_result()` retained.** The function at `chapter_orchestrator.py:2742` still exists but is unreachable in the normal body chapter path. It could be removed in a later cleanup, but its presence is not a safety risk since no code path calls it for body chapter failures.
3. **Full suite not run by implementation worker.** Controller should run broader validation before accepting.
4. **Score loop remains unimplemented.** This is by design and not a risk for this gate.

## Summary

The implementation correctly removes body chapter fail-fast behavior, preserves independent execution for chapters 1-6, keeps `dependency_missing` exclusive to true writer-contract dependency, maintains final assembly fail-closed semantics, and adds a safe CLI chapter matrix with comprehensive leakage tests. No blocking findings.
