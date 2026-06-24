# Code Review Re-Review

## Scope

- Mode: targeted re-review
- Branch: evidence-confirm-productionization
- Finding under re-review: F-01
- Original artifact: docs/reviews/code-review-20260623-000500-mimo-ec-p4-slice5.md
- Fix artifact: docs/reviews/evidence-confirm-productionization-ec-p4-slice5-code-review-fix-20260623.md
- Output file: docs/reviews/code-review-rereview-20260623-000900-mimo-ec-p4-slice5.md

## Re-Review Checklist

### 1. F-01 direct regression coverage exists for mismatched fund_code

**PASS.** `test_semantic_result_identity_mismatch_fails_closed_before_propagation` (line 524) is parameterized with `("fund_code", "999999")`. The base `EvidenceSemanticResult` uses `fund_code="110011"` (line 531); `replace(semantic_result, fund_code="999999")` creates a mismatched identity. The test asserts `pytest.raises(ValueError, match="身份不一致")`.

### 2. F-01 direct regression coverage exists for mismatched report_year

**PASS.** Same parameterized test includes `("report_year", 2023)`. The base uses `report_year=2024` (line 532); `replace(semantic_result, report_year=2023)` creates a mismatched identity. Same `ValueError` assertion.

### 3. Test asserts ValueError from summary_from_repository_result(..., semantic_result=mismatched_result)

**PASS.** Lines 550-555: the `with pytest.raises(ValueError, match="身份不一致")` block calls `summary_from_repository_result(_repository_run_result("pass"), "block", semantic_result=mismatched_result)`. The `ValueError` originates from `_validate_semantic_result_identity()` at `evidence_confirm_production.py:303`.

### 4. Production code was not changed in the fix

**PASS.** `git diff -- fund_agent/fund/evidence_confirm_production.py` shows only the Slice 5 implementation changes (semantic result injection, `_semantic_status`, `_semantic_issue_count`, `_validate_semantic_result_identity`), which are pre-existing on the branch. No additional production code changes were introduced by this fix.

### 5. No new blocker, scope expansion, provider/live/PDF behavior, or boundary violation

**PASS.** Fix adds only:
- Two new imports: `EvidenceSemanticClaimResult`, `EvidenceSemanticResult` (from `evidence_confirm_semantic`, which is already a dependency of the test module).
- One new import: `summary_from_repository_result` (from `evidence_confirm_production`, the module under test).
- One new import: `_repository_run_result` (test helper from `test_fund_analysis_service`).
- Two new test functions using `pytest.mark.parametrize` and `dataclasses.replace`.
- `pathlib.Path` and `pytest` imports for the existing AST-based import isolation test.

No provider, live, PDF, or boundary violation introduced. No scope expansion beyond the accepted finding.

## Validation Results

```text
uv run pytest tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py -q
78 passed in 0.59s
```

```text
uv run ruff check tests/fund/test_evidence_confirm_semantic.py
All checks passed!
```

```text
git diff --check -- tests/fund/test_evidence_confirm_semantic.py docs/reviews/evidence-confirm-productionization-ec-p4-slice5-code-review-fix-20260623.md
<no output>
```

## Finding Status

- F-01: 已修复. Direct regression coverage now proves mismatched `fund_code` and mismatched `report_year` raise `ValueError` via `_validate_semantic_result_identity()` before no-live semantic companion propagation.

## New Blockers

无。

## Open Questions

无。

## Residual Risk

- Provider-backed semantic quality remains unproven; classification: assigned to later provider-backed semantic gate.
- Checklist CLI semantic support remains absent; classification: covered by later approved slice/gate per EC-P4 plan.
- Release/readiness remains `NOT_READY`; classification: tracked by existing EC-P4 / PR-40 control state.

## Verdict

PASS
