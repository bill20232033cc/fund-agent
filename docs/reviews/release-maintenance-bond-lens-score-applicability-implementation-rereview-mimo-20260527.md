# Re-review: bond-lens score applicability implementation (finding 01 fix)

## Scope

- Mode: targeted re-review
- Branch: `codex/local-reconciliation`
- Base: `main`
- Target finding: `01-issue_id 确定性校验只检查前缀和后缀` from `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-review-mimo-20260527.md`
- Output file: `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-rereview-mimo-20260527.md`
- Included scope: `fund_agent/fund/quality_gate.py`, `tests/fund/test_quality_gate.py`
- Verification: `uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` → `72 passed in 0.79s`; `uv run ruff check` → `All checks passed!`; `git diff --check` → clean

## Fix Analysis

### What changed

1. `_validate_score_applicability_issue_id()` (`quality_gate.py:1154-1187`) now uses full exact string match instead of prefix/suffix check:
   - Before: `issue_id.startswith(expected_prefix)` + `issue_id.endswith(expected_suffix)`
   - After: `issue_id != expected_id` where `expected_id = f"score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}"`

2. `_evaluate_score_applicability_issue()` now extracts `report_year` via `_required_applicability_text(row, "report_year", index)` and passes it to validation.

3. Five new tests added:
   - `test_run_quality_gate_projects_score_applicability_issue_as_fq2f_warn` — FQ2F warn projection
   - `test_run_quality_gate_rejects_malformed_score_applicability_issue` — bad issue_id fail-fast
   - `test_run_quality_gate_rejects_score_applicability_issue_wrong_report_year_id` — wrong year segment fail-fast (directly targets finding 01)
   - `test_run_quality_gate_treats_missing_score_applicability_issues_as_empty` — old score.json compatibility
   - `test_run_quality_gate_preserves_fq4_thresholds_with_score_applicability_issue` — FQ4 threshold preservation
   - `test_run_quality_gate_synthetic_006597_like_bond_exclusion_does_not_mis_pass` — anti-mis-pass evidence

4. `_score_applicability_issue()` test helper added with full deterministic issue fields including `report_year`.

### Regression check

- Total test count: 71 → 72 (one new test for wrong report_year)
- All 72 tests pass
- Ruff clean
- `git diff --check` clean
- No changes to `extraction_score.py` or extraction-score tests — no upstream regression path

### Correctness verdict

The fix correctly closes finding 01:

- `_validate_score_applicability_issue_id` now requires `issue_id == expected_id`, which includes the `report_year` segment. A malformed ID like `score-applicability:006597:WRONG:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1` or `score-applicability:006597:2023:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1` (wrong year) now raises `ValueError`.
- The new `test_run_quality_gate_rejects_score_applicability_issue_wrong_report_year_id` directly verifies the prior gap: issue_id with `2023` when report_year is `2024` fails fast.
- `_evaluate_score_applicability_issue` now requires `report_year` as a non-empty string field, which is consistent with extraction_score emitting it.

No new findings from this fix.

## Findings

未发现实质性问题。

## Open Questions

- 无。

## Residual Risk

- Finding 02 (unknown issue_code silently dropped) was not targeted by this fix and remains a low-severity forward-compatibility observation. No action required for current gate.

## Verdict

**PASS**

Finding 01 is closed. Full re-review is not required — the fix is narrow, targeted, and introduces no new coupling or regression risk.
