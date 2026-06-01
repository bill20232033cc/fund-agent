# Redemption Share Class Column Alignment Repair — Code Review (DS)

> Date: 2026-05-28
> Role: code review worker (DS), not controller, not fix worker
> Gate: `redemption share class column alignment repair gate`
> Verdict: **PASS_WITH_FINDINGS**

## Scope Check

Reviewed files:
- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`

No changes to drawdown, credit_risk (beyond accepted reusable baseline), score, quality gate, schema, snapshot, Service, UI, Host, Agent, dayu, golden, or release. Scope boundary respected.

## Review Checklist Results

### 1. No-Class-Header Positional Fallback Guardrails

**Verdict: PASS**

The unlabeled positional alignment path in `_align_share_change_columns()` (`bond_risk_evidence.py:1099–1106`) is only reached when ALL preconditions hold:

- `_share_change_value_columns()` confirms `headers[0]` is non-numeric AND at least one body `row[0]` contains share-change row-label semantics (`期初`/`申购`/`赎回`/`期末`/`拆分`/`变动`/`份额`/`项目`). Failure → empty tuple → `share_class_column_count_mismatch`.
- `len(value_columns) == len(mapping.class_labels)` — count must match §2 mapping.
- Explicit header matching tried first; only falls through if NO class gets a unique match.
- `signal_count` computed across ALL (header × class) pairs; any positive signal (mixed case) → `share_class_column_alignment_ambiguous`.
- Only when `signal_count == 0` (fully unlabeled) does positional alignment activate.
- In `_aggregate_share_change()` (line 1000), the §2 ending cross-check is enforced exclusively for `alignment_note == _SHARE_CHANGE_ALIGNMENT_UNLABELED`.

The implementation correctly gates the positional path behind: row-label precondition → count match → explicit-first → fully-unlabeled-only → arithmetic → §2 cross-check. No shortcut exists.

### 2. §2 Cross-Check Source Restriction (No Self-Certification)

**Verdict: PASS**

`_share_class_ending_cross_check_from_profile_tables()` (`bond_risk_evidence.py:1174–1234`):

- Excludes current §10 table by `(page_number, table_index)` identity (line 1196–1199).
- Requires all three rows in the SAME table: `下属分级基金的基金简称`, `下属分级基金的交易代码`, `报告期末下属分级基金的份额总额` — enforced by `_profile_cross_check_rows()`.
- Does NOT scan for generic `期末基金份额总额` across arbitrary tables.
- Validates that cross-check table's class_labels and fund_codes match the §2 mapping (line 1213).
- Cross-check source identity is preserved in the output anchor (`page_number`, `table_id`, `row_locator`), making it auditable.

Test `test_redemption_share_pressure_does_not_self_certify_cross_check_with_section_ten()` confirms: when the profile table shares `(page=65, table_index=0)` with §10, it is excluded → `share_class_ending_cross_check_missing`. The real-fixture test asserts `cross_check_anchor.table_id == "page-5-table-0"` (not page 65).

### 3. Fail-Closed Scenarios

**Verdict: PASS**

All required fail-closed paths verified in both implementation and tests:

| Scenario | Mechanism | na_reason | Test |
|---|---|---|---|
| Mixed class-label headers | `signal_count > 0` in `_align_share_change_columns` | `share_class_column_alignment_ambiguous` | `test_redemption_share_pressure_fails_closed_on_mixed_header_signal` |
| Mixed fund-code headers | Same signal_count check | `share_class_column_alignment_ambiguous` | `test_redemption_share_pressure_fails_closed_on_mixed_fund_code_header_signal` |
| Numeric `headers[0]` | `_parse_plain_decimal(headers[0]) is not None` → empty value_columns | `share_class_column_count_mismatch` | `test_redemption_share_pressure_unlabeled_path_fails_closed_on_numeric_row_label_header` |
| Non-standard body shape | No row[0] matches share-change keywords → empty value_columns | `share_class_column_count_mismatch` | `test_redemption_share_pressure_unlabeled_path_fails_closed_on_non_standard_body_shape` |
| All-zero aggregate beginning | `aggregate_beginning == Decimal("0")` check | `aggregate_beginning_zero` | `test_redemption_share_pressure_unlabeled_path_fails_closed_on_all_zero_aggregate_beginning` |
| §2 cross-check missing | `cross_check is None` after profile table search | `share_class_ending_cross_check_missing` | `test_redemption_share_pressure_fails_closed_when_unlabeled_cross_check_missing` |
| §2 cross-check mismatch | `_decimal_close(item.ending, expected_ending)` fails | `share_class_ending_cross_check_mismatch` | `test_redemption_share_pressure_fails_closed_when_unlabeled_cross_check_mismatch` |
| Arithmetic mismatch (unlabeled) | `_decimal_close(beginning + net_change, ending)` fails | `share_change_arithmetic_mismatch` | `test_redemption_share_pressure_unlabeled_path_fails_closed_on_arithmetic_mismatch` |
| Arithmetic mismatch (explicit) | Same check in `_calculate_share_class_changes` | `share_change_arithmetic_mismatch` | `test_redemption_share_pressure_fails_closed_on_arithmetic_mismatch` |
| Non-parseable value | `_parse_share_decimal` returns None | `non_parseable_share_value` | `test_redemption_share_pressure_fails_closed_on_non_parseable_share_value` |
| Column count mismatch | `len(value_columns) != len(mapping.class_labels)` | `share_class_column_count_mismatch` | `test_redemption_share_pressure_fails_closed_when_class_columns_do_not_align` |
| Missing rows | `_find_share_change_rows` returns None or drafts < 4 | `incomplete_share_change_rows` | `test_redemption_share_pressure_anchor_missing_not_accepted` |

No A-only acceptance path exists. Per-class `beginning == 0` is allowed only when aggregate beginning is non-zero (real F class case).

### 4. A/C/E/F Completeness

**Verdict: PASS**

- `_share_class_mapping()` returns ALL class labels and fund codes from §2 (not just the current fund's class).
- `_aggregate_share_change()` iterates all classes in mapping order.
- `_format_share_change_metric()` includes per-class breakdown for every class (lines 1573–1582).
- Anchors include: §10 beginning/subscription/redemption/ending (4 required, `len(drafts) < 4` → fail), optional split, §2 mapping anchor, §2 cross-check anchor (unlabeled path).
- Test `test_redemption_share_pressure_not_a_only()` confirms aggregate values ≠ A-only values.
- Test `test_redemption_share_pressure_aligns_real_unlabeled_section_ten_by_section_two_order()` confirms all 6 anchor roles present.

### 5. Non-Regression: drawdown / credit_risk / score / gate / schema / Service / UI / Host / Agent / dayu

**Verdict: PASS**

- `drawdown_stress` extraction unchanged; existing qualitative-weak test still passes.
- `credit_risk` refactoring present in diff is from the previous accepted narrow-gate baseline, as classified by controller judgment. Not modified by this gate.
- No score, quality gate, schema, snapshot, or golden changes.
- No Service/UI/Host/Agent/dayu imports or references added.
- Financial statement rejection (`_SHARE_CHANGE_FINANCIAL_STATEMENT_KEYWORDS`) correctly prevents净资产表 from being selected as §10.

## Findings

### F1: Row-Label Precondition Failure Uses Imprecise na_reason (LOW)

- **File**: `fund_agent/fund/extractors/bond_risk_evidence.py`
- **Function**: `_share_change_value_columns()` → `_align_share_change_columns()`
- **Lines**: 1122–1136 (value_columns), 1059–1064 (count check)

When `_share_change_value_columns()` returns `()` because `headers[0]` is numeric or body rows lack share-change semantics, the na_reason surfaced to the caller is `share_class_column_count_mismatch`. This is technically correct (0 columns ≠ expected count) but semantically imprecise: the root cause is that column 0 cannot be confirmed as a row-label column, not that the class column count is wrong.

The plan (Slice 6) allows `share_class_column_alignment_ambiguous or share_class_column_count_mismatch` for these cases. Current behavior is plan-compliant.

- **Severity**: LOW
- **Fix**: Consider surfacing a distinct na_reason (e.g., `share_change_row_label_column_not_confirmed`) for row-label precondition failure, or returning a structured result from `_share_change_value_columns` that separates "no value columns found" from "wrong count." Not blocking; can be addressed in a future hardening gate.

### F2: `_profile_cross_check_rows` Uses `elif` for Mutually-Distinct Row Types (VERY LOW)

- **File**: `fund_agent/fund/extractors/bond_risk_evidence.py`
- **Function**: `_profile_cross_check_rows()`
- **Lines**: 1259–1271

The three row-type matches use `if/elif/elif`:
```python
if _PROFILE_CLASS_NAME_ROW_KEYWORD in row_label:
    name_match = ...
elif _PROFILE_CLASS_CODE_ROW_KEYWORD in row_label:
    code_match = ...
elif _PROFILE_CLASS_ENDING_ROW_KEYWORD in row_label:
    ending_match = ...
```

In practice, the three keywords (`基金简称`, `交易代码`, `份额总额`) are semantically disjoint and will never co-occur in the same row. If a future report merged them (extremely unlikely), only the first match would be recorded.

- **Severity**: VERY LOW (theoretical only; no known real-world table merges these row labels)
- **Fix**: Change `elif` to `if` for defensive independence. Not blocking.

## Test Coverage Assessment

19 redemption_share_pressure tests added/preserved, covering:
- Real-shape unlabeled alignment with §2 cross-check
- Explicit header regression
- Mixed signal fail-closed (class label variant + fund code variant)
- §2 cross-check missing / mismatch
- Self-certification protection
- Arithmetic mismatch (explicit path + unlabeled path)
- Numeric headers[0] fail-closed
- Non-standard body shape fail-closed
- All-zero aggregate beginning fail-closed
- A-only rejection
- Financial statement table rejection
- Total subscription/redemption row preference (净/累计 exclusion)
- Non-parseable value fail-closed
- Full-width dash as zero
- Missing anchors fail-closed
- §2 table mapping with intervening rows
- Column count mismatch

Existing credit_risk, drawdown, leverage, and convertible tests preserved and passing (56 total, per implementation report).

## Verdict

**PASS_WITH_FINDINGS** — the implementation correctly implements all five required guardrail categories. No blocking issues. Two low-severity findings (F1: imprecise na_reason for row-label failure, F2: elif vs if in cross-check row matching). Neither requires rework before controller acceptance.
