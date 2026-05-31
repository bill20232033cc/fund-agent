# MVP Independent Body Chapter Execution Code Review (MiMo)

## Gate / Role

- Gate: MVP independent body chapter execution gate.
- Role: Gateflow code review worker (MiMo), not implementation worker.
- Approved plan: `docs/reviews/mvp-independent-body-chapter-execution-plan-20260531.md`.
- Implementation evidence: `docs/reviews/mvp-independent-body-chapter-execution-implementation-evidence-20260531.md`.
- Scope: review only; no code, commit, push, PR, provider run or state change.

## Reviewed Files

- `fund_agent/services/chapter_orchestrator.py` (diff)
- `fund_agent/ui/cli.py` (diff)
- `tests/services/test_chapter_orchestrator.py` (diff)
- `tests/services/test_final_chapter_assembler.py` (full read)
- `tests/ui/test_cli.py` (diff)
- `fund_agent/services/final_chapter_assembler.py` (full read, no change expected)

## Verdict

**PASS**

No blocking findings. Implementation correctly satisfies all 7 gate acceptance criteria.

## Review Criteria Analysis

### 1. Chapters 1-6 Independent Execution

**PASS.** The `stop_remaining` / `policy.fail_fast` branching in `orchestrate_chapters()` has been fully removed. The loop now unconditionally calls `_run_single_chapter()` for every `policy.target_chapter_ids` entry. `_skipped_result()` is no longer called for prior body chapter failure. `skipped_chapter_ids` is initialized as empty tuple `()` and never populated by the body loop.

Tests confirming:
- `test_fail_fast_true_is_legacy_noop_and_later_chapter_executes` (line 1613): chapter 1 timeout, chapter 2 still executes and is accepted.
- `test_chapter_1_timeout_does_not_skip_chapters_2_to_6` (line 1643): all 6 chapters receive writer requests after chapter 1 timeout.
- `test_mixed_body_chapter_matrix_preserves_each_chapter_outcome` (line 1674): mixed timeout/accepted/blocked/failed matrix, every row has its own status/stop_reason/failure_category/failure_subcategory.
- `test_all_blocked_body_chapters_all_execute_and_status_blocked` (line 1726): all 6 chapters execute even when all fail.

### 2. fail_fast Legacy/No-Op

**PASS.** `ChapterOrchestrationPolicy.fail_fast` default changed from `True` to `False`. Docstring updated to document it as a legacy/no-op. No code path in `orchestrate_chapters()` branches on `policy.fail_fast`. The field remains in the dataclass for API compatibility only.

### 3. dependency_missing Only for Real Dependency

**PASS.** `_WRITER_STOP_REASON_MAPPING` maps `"chapter_requires_accepted_conclusions" -> ("blocked", "dependency_missing")`. This is the only path producing `dependency_missing`. No prior body chapter failure path produces this stop reason.

Test confirming:
- `test_dependency_missing_only_for_true_writer_dependency_not_prior_failure` (line 1745): chapter 1 timeout does not produce `dependency_missing` on chapter 2; the explicit writer stop reason `"chapter_requires_accepted_conclusions"` does.

### 4. Final Assembly Fail-Closed

**PASS.** `final_chapter_assembler.py` is unchanged. Existing fail-closed logic in `_validate_orchestration()` and `_validate_required_chapter()` correctly rejects partial/blocked orchestration and non-accepted body chapters.

Tests confirming:
- `test_incomplete_when_orchestration_not_accepted` (line 64): partial and blocked orchestration → incomplete, `report_markdown is None`.
- `test_partial_orchestration_with_all_rows_excludes_blocked_required_chapter` (line 119): blocked body chapter produces incomplete assembly; `source_accepted_chapter_ids` includes only accepted chapters.
- `test_blocked_orchestration_with_all_rows_has_no_report_and_only_accepted_sources` (line 172): all-blocked → incomplete, `source_accepted_chapter_ids == ()`.

### 5. CLI Chapter Matrix Secret Safety

**PASS.** `_chapter_matrix_summary()` (cli.py:874) only outputs `chapter_id`, `status`, `stop_reason`, `failure_category`, `failure_subcategory` — all safe enums/scalars. `_first_failed_runtime_summary()` (cli.py:902) outputs only allowlisted scalars: `operation`, `provider_attempt_count`, `provider_max_attempts`, `provider_runtime_category`, `elapsed_ms_max`, `prompt_chars`, `approx_prompt_tokens`. No prompt, draft, raw response, raw audit, model_name, API key, Authorization header or provider body is serialized.

Tests confirming:
- `test_analyze_cli_use_llm_incomplete_prints_safe_all_chapter_matrix` (test_cli.py:1579): matrix includes accepted and failed rows; exhaustive negative assertions for `message`, `Authorization`, `Bearer`, `sk-`, `api_key`, `system_prompt`, `user_prompt`, `draft_markdown`, `raw_response`, `raw audit`, `provider_response`, `provider body`, `model_name`, `header`, `key`.
- `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` (test_cli.py:1668): runtime summary fields present; all secret-like strings absent from stderr.
- `test_sanitized_prompt_contract_serialization_excludes_raw_payloads` (test_chapter_orchestrator.py:976): serializer output excludes all sensitive fields.
- `test_runtime_diagnostic_serialization_exposes_only_safe_scalars` (test_chapter_orchestrator.py:1001): `_runtime_diagnostic_payload()` output excludes `model_name`, `message`, canary strings.

### 6. Tests Cover Gate Acceptance Criteria

**PASS.** All plan-specified acceptance tests are implemented:

| Plan Requirement | Test |
|---|---|
| fail_fast=True legacy/no-op | `test_fail_fast_true_is_legacy_noop_and_later_chapter_executes` |
| Chapter 1 timeout, 2-6 still enter writer | `test_chapter_1_timeout_does_not_skip_chapters_2_to_6` |
| Mixed matrix preserves each outcome | `test_mixed_body_chapter_matrix_preserves_each_chapter_outcome` |
| All-blocked, all execute, status blocked | `test_all_blocked_body_chapters_all_execute_and_status_blocked` |
| dependency_missing only for true dependency | `test_dependency_missing_only_for_true_writer_dependency_not_prior_failure` |
| first_failed does not hide full matrix | `test_first_failed_diagnostic_keeps_full_chapter_matrix` |
| Partial orchestration → incomplete assembly | `test_partial_orchestration_with_all_rows_excludes_blocked_required_chapter` |
| Blocked orchestration → incomplete assembly | `test_blocked_orchestration_with_all_rows_has_no_report_and_only_accepted_sources` |
| CLI matrix includes accepted + failed rows | `test_analyze_cli_use_llm_incomplete_prints_safe_all_chapter_matrix` |
| CLI matrix negative leakage assertions | `test_analyze_cli_use_llm_incomplete_prints_safe_all_chapter_matrix` |

### 7. No Forbidden Scope Touched

**PASS.** Changed files are exactly the plan-allowed set:
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_final_chapter_assembler.py`
- `tests/ui/test_cli.py`

No changes to: `chapter_writer.py`, `chapter_auditor.py`, `config/`, `llm_provider.py`, score/quality gate/golden/fixtures/snapshot/manifest, Host/Agent/dayu, `AGENTS.md`, `docs/fund-analysis-template-draft.md`. Import boundary test `test_chapter_orchestrator_imports_do_not_cross_forbidden_boundaries` confirms no forbidden module imports.

## Findings

No blocking findings.

### Residual: Dead Code `_skipped_result()`

**Severity: informational**
**File:** `fund_agent/services/chapter_orchestrator.py:2742`

`_skipped_result()` is no longer called by any production code path after the fail-fast removal. It remains as dead code. The plan explicitly allowed keeping it "for narrow internal compatibility" (plan slice 1, step 4). This is not blocking but could be cleaned in a follow-up if desired.

## Residual Risks

- `_skipped_result()` is dead code; no production path calls it. Not blocking per plan allowance.
- Real provider smoke was not run by instruction; this gate only verifies code-level independence, not provider-level chapter outcomes.
- Score loop remains unimplemented by scope.
- Full test suite was not run; controller will run broader validation.

## Completion

- All 7 review criteria PASS.
- No blocking findings.
- Artifact written to `docs/reviews/mvp-independent-body-chapter-execution-code-review-mimo-20260531.md`.
