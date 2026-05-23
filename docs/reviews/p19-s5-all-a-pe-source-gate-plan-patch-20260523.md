# P19-S5 All-A PE Source Gate Plan Patch（2026-05-23）

## Scope

Patched `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md` after controller judgment `BLOCKED UNTIL PLAN PATCH`.

Inputs read:

- `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md`
- `docs/reviews/p19-s5-plan-review-mimo-20260523.md`
- `docs/reviews/p19-s5-plan-review-glm-20260523.md`
- `docs/reviews/p19-s5-plan-review-controller-judgment-20260523.md`

No source code or test files were modified.

## Patch Summary

### 1. Added mandatory `stock_a_ttm_lyr()` probe

The source gate now treats `akshare.stock_a_ttm_lyr()` as a mandatory all-A PE candidate probe.

Reviewer probe evidence recorded in the plan:

- local module: `.venv/lib/python3.11/site-packages/akshare/stock_feature/stock_ttm_lyr.py`
- page URL: `https://www.legulegu.com/stockdata/a-ttm-lyr`
- API URL: `https://legulegu.com/api/stock-data/market-ttm-lyr`
- rows: about 5186
- date range: 2005-01-05 to 2026-05-22
- fields: `middlePETTM`, `averagePETTM`, `middlePELYR`, `averagePELYR`
- common dates with `stock_a_all_pb()`: about 4828

The plan explicitly says this is reviewer probe evidence only. The source feasibility worker must re-run, verify, and freeze exact source-contract evidence before acceptance.

### 2. Replaced absolute unresolved PE language

The plan no longer says all-A PE history is absolutely unresolved. It now says an all-A PE candidate exists and requires source-contract validation.

### 3. Strengthened acceptance gate

`ACCEPT_IMPLEMENTATION_PLAN` now requires:

- PE and PB match the current design's equal-weight / median-oriented thermometer semantics.
- PE basis, such as TTM, LYR, or static PE, matches the existing accepted index thermometer basis or has explicit design decision before implementation.
- PB basis matches the accepted thermometer contract.

If exact all-A PE/PB data exists but weighting method, statistic type, PE basis, PB basis, or universe identity does not match the current design, the required outcome is `NEEDS_DESIGN_CHANGE`, not implementation acceptance.

### 4. Expanded probe matrix

The probe matrix now includes:

- `universe_definition`
- `identity_reconciliation`
- `weighting_method`
- `statistic_type`
- `pe_basis`
- `pb_basis`

### 5. Preserved implementation gate boundary

The plan now explicitly states that if `stock_a_ttm_lyr()` plus `stock_a_all_pb()` passes source-contract validation, the next step is still `ACCEPT_IMPLEMENTATION_PLAN` followed by implementation plan/review. It must not proceed directly to coding.

## Validation

```text
git diff --check
passed
```
