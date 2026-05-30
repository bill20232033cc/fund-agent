# Bond Risk Evidence Narrow False-Negative — Code Review (MiMo)

> Date: 2026-05-28
> Role: code review worker (MiMo), not controller, not fix worker
> Gate: `bond risk evidence narrow false-negative gate`
> Scope: `fund_agent/fund/extractors/bond_risk_evidence.py`, `tests/fund/extractors/test_bond_risk_evidence.py`
> Status: review complete

## Verdict

**PASS_WITH_FINDINGS**

## Summary

Implementation faithfully follows the accepted plan and controller judgment. The two false-negative fixes (credit_risk as portfolio credit exposure, redemption_share_pressure as A/C/E/F aggregate) are correctly implemented with proper fail-closed behavior. The drawdown boundary is preserved. All required tests exist and cover the specified negative cases. No schema/score/snapshot/quality-gate/Host/Agent/dayu changes were made.

Three findings were identified. None are blockers for this gate, but F1 warrants attention before real-path validation.

## Findings

### F1 — Current-period column detection assumes first non-percentage numeric column is current period

- **File**: `fund_agent/fund/extractors/bond_risk_evidence.py`
- **Function**: `_current_period_value_column_index` (line 1200-1218)
- **Severity**: Medium
- **Evidence**: The function iterates `row[1:]` and returns the first cell where `_parse_plain_decimal(cell) is not None` and `"%" not in cell`. It does not inspect header text for period semantics.
- **Risk**: In real `006597/2024` annual report tables, if the column order is `("长期信用评级", "上年度末公允价值", "本期末公允价值")` rather than `("长期信用评级", "本期末公允价值", "上年度末公允价值")`, the function would select prior-period values as current-period values. This would produce a false positive `credit_risk: accepted` with wrong `metric_value` (prior-period amounts reported as current-period).
- **Plan alignment**: Plan §Slice 1 requires "current-period numeric amount" but does not specify how to distinguish current from prior period columns.
- **Suggested fix**: Prefer columns whose header text contains `本期` or `本期末` when available. If no such header exists, fall back to the first non-percentage numeric column with a reviewer note documenting the assumption.
- **Test gap**: No test covers a table where the prior-period column appears before the current-period column (see F3).

### F2 — Rating label row matching uses loose substring logic

- **File**: `fund_agent/fund/extractors/bond_risk_evidence.py`
- **Function**: `_rating_label_from_row` (line 1161-1178)
- **Severity**: Low
- **Evidence**: The matching logic `label.upper() in row_label` is a substring check. For `_CREDIT_RATING_LABELS` entries like `A`, this means any row whose first cell contains uppercase `A` (after compacting) would match, e.g. `A+评级债券` matches `A+` but also `A`.
- **Risk**: False-positive row inclusion could add spurious rows to the rating distribution. In practice, real annual report rating distribution tables use clean labels (`AAA`, `AA+`, etc.), so this is unlikely to trigger on real data. However, the matching is not defensive against unexpected row formats.
- **Plan alignment**: Plan §Slice 1 says "Recognized row labels include at minimum: A-1, AAA, AA+, ...". The current implementation matches these but also matches substrings.
- **Suggested fix**: Use exact match (`row_label == label.upper()`) as primary, substring as fallback only for compound labels like `AAA以下`. Or sort `_CREDIT_RATING_LABELS` by length descending so longer labels match first (current order already does this for `A-1` vs `A`, but `A` could still match `AAA` if `AAA` didn't match first due to iteration order — actually `AAA` comes after `A-1` in the tuple, so `A-1` is checked first, then `AAA`, then the rest; `A` is checked after `AA+`, `AA-`, `AA`, `A+`, so a row label `AAA` would match `AAA` before reaching `A`).

### F3 — Missing test for prior-period-first column ordering

- **File**: `tests/fund/extractors/test_bond_risk_evidence.py`
- **Severity**: Low (test gap, not implementation bug)
- **Evidence**: All rating distribution test tables use headers like `("长期信用评级", "本期末公允价值", ...)` where the current-period column is first. No test verifies behavior when headers are `("长期信用评级", "上年度末公允价值", "本期末公允价值")`.
- **Risk**: The real `006597/2024` annual report could have prior-period column first. Without this test, the controller's real-path validation is the only safety net.
- **Suggested fix**: Add a test with reversed column order and assert either: (a) correct current-period values are selected (if fix F1 is applied), or (b) the test documents the assumption and expected behavior.

## Verified Correct Behaviors

### Credit Rating Distribution — Portfolio Exposure, Not Fund Rating

- `_is_holding_rating_distribution_table` (line 1136-1158): Correctly rejects `_FUND_OWN_RATING_KEYWORDS` (`本基金评级`, `基金评级信息`, `基金自身评级`) before checking holding qualifiers.
- `_extract_credit_risk` (line 312-356): Uses `summary="年报表格披露持有债券/证券的信用评级分布"`, `metric_name="持仓评级分布"`, `evidence_role="holding_rating_distribution"`. No forbidden fund-rating wording.
- `test_fund_own_rating_table_is_rejected_for_credit_risk`: Confirms `本基金评级` header → `status="weak"`.
- `test_holding_rating_distribution_table_is_credit_risk_portfolio_exposure_not_fund_rating`: Confirms no `基金评级` or `本基金评级` in combined text.

### Multiple Rating Tables — All Anchors Preserved

- `_credit_rating_distribution_evidence` (line 1047-1079): Iterates all tables, extends `drafts` from every matching table. `representative_metric` taken from first match only (per plan).
- `test_multiple_holding_rating_distribution_tables_preserve_all_anchors`: Confirms 5 anchors from 2 tables, both table_ids present.

### A/C/E/F Mapping — §2 Table + Text Fallback

- `_share_class_mapping` (line 1297-1316): Tries parsed table mapping first, text lines as fallback. Both require `len(class_labels) == len(fund_codes)` and unique class labels.
- `_align_share_change_columns` (line 1507-1545): Excludes total columns, requires exact column count match, tracks used columns to prevent duplicate assignment.
- `test_share_class_evidence_from_section_two_table`: Confirms table-based mapping with `source_anchor_draft`.
- `test_redemption_share_pressure_fails_closed_when_class_columns_do_not_align`: Confirms `share_class_column_count_mismatch`.

### §10 Table Selection — Scoring, Not First-Match

- `_find_share_change_table` (line 1238-1263): Scores all candidates, selects unique best. Ties → `ambiguous_share_change_table`.
- `_share_change_table_score` (line 1266-1294): Rejects tables with `实收基金`, `未分配利润`, `净资产合计`. Requires boundary + flow + share semantics.
- `test_redemption_share_pressure_rejects_net_asset_statement_table`: Confirms financial-statement table is rejected.

### F-Class Beginning Zero — Not a Failure

- `_calculate_share_class_changes` (line 1602-1646): `beginning == 0` → `ratio = None`, `note = "class_beginning_zero"`. No failure.
- `_aggregate_share_change` (line 1447-1504): `aggregate_beginning == 0` → fail closed. Individual class zero is fine.
- `test_redemption_share_pressure_parses_full_width_dash_as_zero`: Confirms `－` parsed as 0, F class included.

### Non-Parseable / Arithmetic Mismatch — Fail-Closed

- `_parse_share_decimal` → `_parse_plain_decimal` → `InvalidOperation` → `None` → `"non_parseable_share_value"`.
- `_decimal_close` with `Decimal("0.01")` tolerance for both class and aggregate reconciliation.
- `test_redemption_share_pressure_fails_closed_on_non_parseable_share_value`: Confirms `non_parseable_share_value`.
- `test_redemption_share_pressure_fails_closed_on_arithmetic_mismatch`: Confirms `share_change_arithmetic_mismatch`.

### Drawdown Boundary — Preserved

- `_extract_drawdown_stress` (line 462-513): No changes. Qualitative `控制回撤` → `weak / qualitative_control_intent / control_intent`.
- `test_drawdown_control_text_alone_is_weak`: Confirms unsatisfied.

### Anchor Structure — Consistent

- `_build_group_anchors` (line 793-847): Deterministic sort by `(section_id, page_number, table_id, row_locator, evidence_role)`. Sequential ordinal assignment.
- All accepted groups have row-level or line-level anchors with `page_number`, `table_id`, `row_locator`.

## Files Reviewed

| File | Lines changed (approx) | Review status |
|---|---|---|
| `fund_agent/fund/extractors/bond_risk_evidence.py` | +500/-200 | Reviewed |
| `tests/fund/extractors/test_bond_risk_evidence.py` | +400/-30 | Reviewed |

## Recommendation

Proceed to controller validation. F1 (current-period column detection) is the most actionable finding — the controller should verify during real `006597/2024` validation that the actual rating distribution table has the current-period column in the expected position. If it does not, F1 should be fixed before final acceptance.
