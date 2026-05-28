# Bond Risk Evidence Narrow False-Negative — Code Fix

> Date: 2026-05-28
> Role: fix worker, not controller, not reviewer
> Scope:
> - `fund_agent/fund/extractors/bond_risk_evidence.py`
> - `tests/fund/extractors/test_bond_risk_evidence.py`
> - this code-fix artifact

## Inputs Read

- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-review-ds-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-review-mimo-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-implementation-20260528.md`

## Fixes Applied

### 1. Current-Period Rating Column

Fixed `_current_period_value_column_index` to choose the rating-distribution current-period value column using table header semantics, not the first parseable non-percentage value.

- Current-period headers such as `本期`, `本期末`, `期末`, and `报告期末` are preferred.
- Prior-period headers such as `上年度`, `上期`, `期初`, and `年初` are excluded.
- Percentage headers are not treated as amount columns.
- If multiple parseable value columns exist and no reliable current-period header can be identified, the table fails closed for accepted credit-risk evidence.
- Single parseable non-prior value columns remain supported.

Added `test_credit_risk_uses_current_period_column_when_prior_period_appears_first`, asserting `metric_value` and extractor anchor note use the `本期末` column when `上年度末` appears first.

### 2. Share-Change Row Matching

Tightened `_find_share_change_row` for subscription and redemption rows.

- Subscription now requires preferred semantics such as `总申购` or `申购份额`.
- Redemption now requires preferred semantics such as `总赎回` or `赎回份额`.
- `净申购` / `累计申购` and `净赎回` / `累计赎回` are excluded as matching rows.

Added `test_redemption_share_pressure_uses_total_subscription_and_redemption_rows`, covering `净申购` / `累计申购` and `净赎回` / `累计赎回` rows before the required total rows.

### 3. Profile Code Row Window

Changed `_next_profile_code_row` to scan from the fund-name row through the remaining table rows instead of only a short fixed window.

Added `test_share_class_evidence_from_section_two_table_with_intervening_rows`, covering comments and blank rows between `基金简称` and `交易代码`.

### 4. Rating Label Matching

Hardened `_rating_label_from_row`.

- Exact rating-label match is attempted first.
- Compound labels remain supported when the rating token is separated from adjacent rating-token characters.
- Added explicit rejection keyword `基金信用评级` to avoid fund-own credit-rating false positives.

Added:

- `test_compound_rating_labels_are_matched_without_loose_substring_false_positive`
- `test_fund_own_credit_rating_table_is_rejected_for_credit_risk`

### 5. LOW Cleanup

Cleaned the test-only items from review.

- Renamed `test_credit_risk_anchor_missing_not_accepted` to `test_credit_risk_percentage_only_table_not_accepted`.
- Changed `_share_change_table_ac_ef` default fixture to avoid negative ending shares.
- Kept mismatch behavior covered by `test_redemption_share_pressure_fails_closed_on_arithmetic_mismatch`, which now creates the inconsistency explicitly.

## Validation

Commands run:

```bash
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
```

Results:

- Targeted pytest: `46 passed`
- Targeted ruff: `All checks passed`

## Boundaries Preserved

- No schema changes.
- No score, snapshot, or quality-gate semantic changes.
- No drawdown upgrade.
- No `FundDocumentRepository` boundary change.
- No Service, UI, Host, Agent, dayu, baseline, golden, release, push, PR, or merge changes.

## Residual Risks

- Real `006597 / 2024` repository-path validation was not run by this fix worker.
- Credit-risk current-period detection remains intentionally conservative: ambiguous multi-value rating tables without reliable current-period headers do not become accepted evidence.
- `drawdown_stress` remains weak qualitative evidence by contract.
