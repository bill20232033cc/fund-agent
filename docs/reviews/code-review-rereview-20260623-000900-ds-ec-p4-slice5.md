# Code Re-Review: EC-P4 Slice 5 Code Review Fix — F-01 Targeted

## Gate

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: targeted re-review for Slice 5 code review fix
- Slice: Slice 5 - No-Live Semantic Companion Propagation
- Branch: evidence-confirm-productionization
- Reviewer: AgentDS
- Date: 2026-06-23
- Accepted finding under re-review: F-01 from `docs/reviews/code-review-20260623-000500-mimo-ec-p4-slice5.md`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-slice5-code-review-fix-20260623.md`

## Scope

Targeted re-review of F-01 fix only. No new review of already-passed areas.

## Re-Review Targets

| Target | Purpose |
|---|---|
| `tests/fund/test_evidence_confirm_semantic.py:517-555` | New parameterized F-01 regression test |
| Production lines `evidence_confirm_production.py:283-303` | Context only — verify guard implementation unchanged |
| Fix artifact | Statement of fix scope and validation claims |

## Validation

| Check | Result |
|---|---|
| `uv run pytest tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py -q` | **78 passed in 0.60s** |
| `uv run ruff check tests/fund/test_evidence_confirm_semantic.py` | **All checks passed!** |
| `git diff --check` | **Clean** |
| Production file diff (`evidence_confirm_production.py`, `quality_gate_integration.py`) | **No changes in fix** (only test file modified) |
| `rg` forbidden imports in production files | **No matches** |

## F-01 Fix Verification

### What was broken

Original finding F-01: `_validate_semantic_result_identity()` at `evidence_confirm_production.py:283-303` raises `ValueError` when `semantic_result.fund_code != result.fund_code` or `semantic_result.report_year != result.report_year`. No test covered this path.

### What the fix delivers

New parameterized test `test_semantic_result_identity_mismatch_fails_closed_before_propagation` (lines 517-555):

```
@pytest.mark.parametrize(
    ("field_name", "field_value"),
    (
        ("fund_code", "999999"),
        ("report_year", 2023),
    ),
)
```

- **mismatched `fund_code`**: `semantic_result.fund_code="110011"` → `mismatched_result.fund_code="999999"` vs `_repository_run_result("pass").fund_code="110011"` → `ValueError`
- **mismatched `report_year`**: `semantic_result.report_year=2024` → `mismatched_result.report_year=2023` vs `_repository_run_result("pass").report_year=2024` → `ValueError`
- Both paths assert `pytest.raises(ValueError, match="身份不一致")` on `summary_from_repository_result(..., semantic_result=mismatched_result)`

### Verification checklist

| Criterion | Status | Evidence |
|---|---|---|
| Direct regression coverage for mismatched `fund_code` | ✅ | `("fund_code", "999999")` parameterization |
| Direct regression coverage for mismatched `report_year` | ✅ | `("report_year", 2023)` parameterization |
| Asserts `ValueError` from `summary_from_repository_result()` | ✅ | `pytest.raises(ValueError, match="身份不一致")` |
| Asserts on `semantic_result=mismatched_result` injection | ✅ | `summary_from_repository_result(_repository_run_result("pass"), "block", semantic_result=mismatched_result)` |
| Production code unchanged in fix | ✅ | Zero diff on production files |
| `_validate_semantic_result_identity()` called before status extraction in production path | ✅ | Verified at `evidence_confirm_production.py:104` — call precedes `_semantic_status()` at :107 |

## Scope Boundary Check

| Check | Status |
|---|---|
| No production code changed | ✅ |
| No new imports added to production path | ✅ |
| No provider/OpenAI/LLM client construction | ✅ |
| No Service/UI/renderer expansion | ✅ |
| No PDF/repository source adapter access | ✅ |
| No live/network behavior introduced | ✅ |
| No quality-gate semantics altered | ✅ |
| No schema or public contract changed | ✅ |

## New Blocker Check

No new blockers found. The fix:
- Adds only test code within the existing test boundary
- Uses existing helper `_repository_run_result` from service test module
- Uses standard `dataclasses.replace` pattern already in use elsewhere in the file
- Uses standard `pytest.mark.parametrize` / `pytest.raises` patterns
- Has proper docstring (Chinese) matching project conventions

## Adversarial Failure Pass (Targeted to Fix)

| Attack Vector | Result |
|---|---|
| Both mismatched params exercise the same `or` clause in guard | Covered — each param hits a different operand: `fund_code` mismatch hits first operand, `report_year` mismatch hits second |
| Guard bypass via mutation of result after validation | Not applicable — `EvidenceConfirmRepositoryRunResult` is not mutated in the test |
| Test fixture mismatch (result has `fund_code="999999"` too) | Not applicable — `_repository_run_result("pass")` defaults to `fund_code="110011"`, `report_year=2024`, confirmed in source |

## Findings

None. F-01 is fully addressed.

## Verdict

**PASS**

## Finding Status

- **F-01**: 已修复 — direct regression coverage now proves both mismatched `fund_code` and mismatched `report_year` raise `ValueError` from `summary_from_repository_result()` before semantic propagation.

## Artifact Path

`docs/reviews/code-review-rereview-20260623-000900-ds-ec-p4-slice5.md`
