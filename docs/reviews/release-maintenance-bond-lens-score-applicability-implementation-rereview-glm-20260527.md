# Code Review — Targeted Re-Review

## Scope

- Mode: current changes (targeted re-review)
- Branch: `codex/local-reconciliation`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-rereview-glm-20260527.md`
- Prior review: `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-review-glm-20260527.md`
- Included scope: fix for O3 (issue_id validation) in `fund_agent/fund/quality_gate.py` and new test in `tests/fund/test_quality_gate.py`
- Excluded scope: `extraction_score.py`, `test_extraction_score.py` — unchanged since prior review

## Prior Finding Closure

| Prior finding | Status |
|---|---|
| O1-[低]-raw_total_field_count 语义边界 | 已确认非 material defect；不在本次修复范围；维持原判 |
| O2-[低]-derive 函数重复按基金分组 | 已确认非 material defect；不在本次修复范围；维持原判 |
| **O3-[低]-issue_id 验证不检查 report_year 段** | **已修复并关闭** |

## Fix Walk-Through

### `_validate_score_applicability_issue_id` — `fund_agent/fund/quality_gate.py`

**Before**: prefix/suffix check only — `report_year` 段未被验证。

**After**: exact equality check reconstructing the full expected ID from all consumed fields:

```python
expected_id = (
    f"score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}"
)
if issue_id != expected_id:
    raise ValueError(...)
```

**New parameter**: `report_year: str` added to the function signature. Caller `_evaluate_score_applicability_issue` now reads `report_year` via `_required_applicability_text(row, "report_year", index)` and passes it through.

**Regression analysis**:

1. `_evaluate_score_applicability_issue` now extracts `report_year` as a required field. This means `score_applicability_issues` rows missing `report_year` will raise `ValueError` — correct fail-fast. Previously `report_year` was not consumed, so a missing field would have been silently accepted. This is a strictly tighter validation.
2. The `_score_applicability_issue()` test helper already includes `"report_year": "2024"`, so all existing tests continue to produce valid IDs. Verified: 30 passed.
3. No other caller of `_validate_score_applicability_issue_id` exists — it is a private function called only from `_evaluate_score_applicability_issue`.

### New test: `test_run_quality_gate_rejects_score_applicability_issue_wrong_report_year_id`

Constructs a valid-looking issue with `report_year="2024"` in the row but `issue_id` containing `2023` as the year segment. Asserts `ValueError` with `match="issue_id"`.

**Evidence**: The test sets `malformed_issue["issue_id"]` to the 2023 variant while the row still has `report_year: "2024"`. The validator reconstructs `expected_id` with `2024` and detects the mismatch. This directly covers the O3 gap.

## Findings

未发现实质性问题。修复正确且无回归风险。

## Verdict

**PASS**

Prior O3 已关闭。修复严格收紧了 issue_id 验证到全字段精确匹配，新增测试直接覆盖了 report_year 段篡改场景。无回归引入。

无需全量 re-review；本次仅 quality_gate.py 和 test_quality_gate.py 变更，已完整走读。30 tests passed。
