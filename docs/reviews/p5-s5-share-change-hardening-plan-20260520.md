# P5-S5 Share Change Hardening Plan - 2026-05-20

## Verdict

P5-S5 enters plan review.

This slice hardens `share_change` extraction for multi-share-class tables. The current extractor reads the first non-empty value after the row label. In A/C share tables this often happens to select A-class, but that is an implicit column-order dependency rather than a fund-code or share-class decision.

Next gate: `P5-S5 plan review`.

## Inputs

- Design truth: `docs/design.md`
- Template: `fund-analysis-template-draft.md`, chapter 4 investor experience / share change usage
- Current code:
  - `fund_agent/fund/extractors/holdings_share_change.py`
  - `tests/fund/extractors/test_holdings_share_change.py`
  - `fund_agent/fund/data_extractor.py`

## Current Facts

- `extract_holdings_share_change(report)` currently only receives `ParsedAnnualReport`.
- `ParsedAnnualReport.key.fund_code` is available to the extractor through `report.key.fund_code`.
- `_extract_share_change(table)` does not receive fund code, fund name, or basic identity.
- `_extract_share_value_from_row(row)` returns the first non-empty non-`-` value from `row[1:]`.
- Existing test `test_extract_holdings_share_change_outputs_share_change_from_subscription_redemption_table` uses headers `("项目", "A类份额", "C类份额")` and currently expects A-class values by column order.

## Root Cause

The extractor has no explicit share-class resolution step. It treats the first valid numeric value as the correct fund share class. This is fragile when:

- report tables contain `A类份额`, `C类份额`, or fund-name-specific columns;
- the selected fund code is a C-class code but A-class appears first;
- a column is `-` in one row but populated in another;
- total columns and class-specific columns coexist.

## Target Contract

### 1. Add explicit selected-column resolution

Create a module-level helper, for example:

```python
def _select_share_change_value_column(table: ParsedTable, fund_code: str) -> int | None:
    ...
```

The function should return a table column index, not a row-relative offset.

Initial deterministic rule:

1. If there is exactly one value column after the project column, select it.
2. If multiple value columns exist:
   - Prefer headers that contain the exact `fund_code`.
   - Else prefer `A类` only when there is exactly one `A类` value column, no exact-code match, and no conflicting code-specific column, because this is the current behavior for A-class fixtures and `004393`-style A-class products.
   - Else return `None` and make `share_change` missing with an explanatory note.

Rejected inference:

- Do not infer A/C class from the last character of `fund_code`. The current codebase has no reliable fund-code-to-share-class registry, and fund code alone is not a same-source class signal.

Total-column behavior:

- Headers containing `合计`, `总计`, `基金份额总额`, or `总份额` are total columns and must not be selected as class-specific fallback columns.
- If there is exactly one value column and it is a total column, select it because the table is not split by class.
- If total and A/C columns coexist without exact fund-code match, ignore total columns for fallback ambiguity; `A类` fallback is allowed only when exactly one A-class value column remains and no code-specific column conflicts.

### 2. Use selected column consistently across all rows

Change extraction from “first valid value per row” to “value at selected column per row”:

- Beginning share, ending share, and net change must come from the same selected column.
- If selected column value is empty/`-`, that row returns `None`.
- If net change is absent, calculate `ending - beginning` from selected column values only.

### 3. Expose selection metadata in `share_change.value`

Add conservative metadata:

```json
"share_class_column": "A类份额",
"share_class_selection_reason": "single_a_class_fallback"
```

or, when exact code matched:

```json
"share_class_selection_reason": "fund_code_header_match"
```

This gives downstream score/gate and human review a traceable reason without parsing notes.

Stable reason values:

- `single_value_column`
- `fund_code_header_match`
- `single_a_class_fallback`

Missing ambiguous cases do not produce metadata.

### 4. Missing behavior

If a multi-column table cannot be resolved:

- Return `ExtractedField(value=None, extraction_mode="missing", note="...")`.
- Do not silently take the first value.
- Preserve existing `profit_change_table` ignore behavior.

## Implementation Slices

1. `holdings_share_change.py`
   - Pass `report.key.fund_code` into `_extract_share_change(...)`.
   - Add `_select_share_change_value_column(...)`.
   - Add `_share_class_selection_reason(...)` or return a small private dataclass for column + reason.
   - Replace `_extract_share_value_from_row(row)` with a selected-column version.
   - Update `_build_share_change(...)` to return missing when selection is ambiguous.

2. Tests
   - Preserve single-column behavior.
   - Preserve A/C fixture behavior for A-class fund code by explicit A-class fallback.
   - Add a multi-column fixture where A appears first and C appears second but no exact code is present; if A fallback conditions are not met, assert `missing` rather than first-column extraction.
   - Add a total + A/C fixture to prove total columns are ignored for class fallback but selected when they are the only value column.
   - Add a mixed row fixture proving beginning/ending/net all use the same selected column.

3. Docs
   - Update `fund_agent/fund/README.md` current boundary for `share_change`.
   - Update `tests/README.md` extractor test coverage line.

## Non-Goals

- Do not add a new share-class registry or external fund-code lookup.
- Do not parse product names from PDF prose to infer class.
- Do not change public `StructuredFundDataBundle` fields beyond optional metadata inside `share_change.value`.
- Do not alter template rendering behavior unless tests show existing rendering cannot tolerate metadata keys.

## Review Questions

1. Is exact-code header match + explicit A-class fallback sufficient for this slice? Controller answer after review: yes; code-last-character inference is rejected.
2. Should ambiguous multi-column tables become `missing` instead of first-column fallback? Controller recommendation: yes.
3. Is metadata inside `share_change.value` acceptable? Controller recommendation: yes, because `share_change.value` is already a dict of raw structured extraction facts, but downstream consumers must ignore unknown keys.

## Validation Plan

- `pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q`
- `pytest tests/ -q`
- `ruff check .`
- `git diff --check`

## Gate Decision

Current gate advances from `P5-S5 plan review` to `P5-S5 plan patched after controller review`.

Next gate: `P5-S5 plan re-review`.
