# Redemption Share Class Column Alignment Repair Plan Fix

> Date: 2026-05-28
> Role: plan-fix worker, not controller, not implementation worker
> Source plan: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-20260528.md`
> Review inputs:
> - `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-review-ds-20260528.md`
> - `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-review-mimo-20260528.md`
> Status: plan updated; no production code changed

## Scope

This worker only revised the plan artifact and created this plan-fix artifact. It did not start gateflow, edit production code, edit tests, run validation, change generated reports, update control docs, commit, push, open PRs, or alter release state.

## Mandatory Controller Fixes

### 1. §2 ending cross-check source narrowed

Status: **resolved in plan**

Plan changes:

- Removed the open-ended "scan all tables for ending-share row text" design.
- Required the §2 cross-check to use a same-source profile table containing all three row labels:
  - `下属分级基金的基金简称`
  - `下属分级基金的交易代码`
  - `报告期末下属分级基金的份额总额`
- Required exclusion of the current §10 table by `(page_number, table_index)`.
- Explicitly prohibited generic `期末基金份额总额` / `报告期末基金份额总额` matching outside the profile-table shape because it can self-certify against §10.

Residual risk:

- If a future annual report has a materially different §2 profile table shape, the plan requires fail-closed with `share_class_ending_cross_check_missing` rather than guessing.

### 2. Real §2 table shape added

Status: **resolved in plan**

Plan changes:

- Added real `006597 / 2024` §2 evidence:
  - `page_number=5`, `table_index=0`
  - row 9: A/C/E/F fund short names
  - row 10: `006597 / 006598 / 014217 / 022176`
  - row 11: `5,711,224,267.09 / 4,760,029,015.27 / 25,795,859.12 / 52,531,021.84`
- Stated that the cross-check is implementable for the real target case.

Residual risk:

- The plan-fix worker did not re-run repository extraction. The accepted table shape is written into the plan as controller-mandated evidence for the implementation worker to encode and validate.

### 3. Current dirty diff gap made explicit

Status: **resolved in plan**

Plan changes:

- Added an "Important implementation gap" note under current dirty scope classification.
- Stated that the dirty diff does not contain positional fallback and does not contain §2 ending-share cross-check.
- Stated that Slices 2 and 4 are new implementation work.

Residual risk:

- None at plan level. Implementation review must verify the worker did not only add tests or assume the repair already exists.

### 4. `headers[0]` row-label precondition added

Status: **resolved in plan**

Plan changes:

- Added `_share_change_value_columns()` precondition:
  - at least one required row's `row[0]` must match row-label semantics such as `期初`, `申购`, `赎回`, `期末`, `拆分`, `变动`, `份额`, or `项目`;
  - `headers[0]` must fail strict ordinary-number parsing; if it parses as a numeric value, fail closed.
- Added required tests for numeric `headers[0]` and non-standard body shape.

Residual risk:

- The exact helper name for strict numeric parsing may differ in implementation. The behavior is mandatory even if implemented through an equivalent parser.

### 5. `_share_change_value_columns` contract clarified

Status: **resolved in plan**

Plan changes:

- Defined return value as indexes that are neither row-label nor total/aggregate columns.
- Defined index 0 as the default row-label column only after the row-label precondition passes.
- Required empty tuple / fail-closed behavior when the row-label column cannot be confirmed.
- Required reuse of total/aggregate header detection.

Residual risk:

- The final `na_reason` may be either `share_class_column_alignment_ambiguous` or `share_class_column_count_mismatch` for this precondition failure, as the plan allows either. Review should verify it is ambiguous and unsatisfied.

### 6. Test assertion format corrected

Status: **resolved in plan**

Plan changes:

- Changed aggregate metric assertion from `beginning=12982005127.50` to `_format_decimal` output `beginning=12982005127.5`.
- Required `net_change_ratio` tests to use a stable prefix or parse-and-compare approach rather than exact long-string assertion.

Residual risk:

- Metric string parsing remains brittle if implementation changes delimiters. The plan allows either substring checks or comparable parsed values.

### 7. Missing fail-closed tests added

Status: **resolved in plan**

Plan changes:

- Added tests for:
  - numeric `headers[0]` fail-closed;
  - non-standard row-label/body shape fail-closed;
  - all-zero/dash aggregate beginning returning `aggregate_beginning_zero`;
  - mixed header signal with fund-code/numeric combination fail-closed;
  - §2 cross-check missing without a proper profile table;
  - §2 cross-check mismatch with a proper profile table.

Residual risk:

- Test numbering was expanded from 8 to 12. The implementation worker may consolidate cases if coverage remains equivalent and review confirms all mandatory behaviors are asserted.

### 8. Redemption row sign semantics clarified

Status: **resolved in plan**

Plan changes:

- Added explicit arithmetic note: §10 redemption values are positive numbers under a `减：` row label.
- Required formula remains `beginning + subscription - redemption + split == ending`.
- Prohibited importing negative-number semantics from balance sheet or cash-flow statement contexts.

Residual risk:

- None at plan level. Unit tests and real validation should verify the positive redemption values reconcile.

## DS Review Findings

### DS F1: §2 cross-check circularity risk

Status: **resolved**

Disposition:

- Addressed by same-source §2 profile-table requirement and explicit `(page_number, table_index)` exclusion of the §10 table.
- Removed reliance on generic `期末基金份额总额` candidates.
- Required implementation reporting/anchoring of the cross-check table.

Residual risk:

- Future reports with different §2 wording will fail closed until a separately reviewed rule is added.

### DS F2: real §2 table shape not verified in plan

Status: **resolved**

Disposition:

- Added real page/table/row shape and values for 006597/2024.

Residual risk:

- Plan-fix did not run extraction; implementation validation remains responsible for proving the coded helper finds the same table in `ParsedAnnualReport`.

### DS F3: `headers[0]` row-label identification too permissive

Status: **resolved**

Disposition:

- Added row-label semantic precondition and numeric-header fail-closed rule.

Residual risk:

- Exact implementation reason code is allowed to vary within the plan's ambiguous fail-closed options.

### DS F4: `_share_change_value_columns` semantics underspecified

Status: **resolved**

Disposition:

- Return contract now explicitly excludes row-label and total/aggregate columns.
- Unknown row-label means empty tuple and fail-closed.

Residual risk:

- None beyond implementation review.

### DS F5: missing test for non-standard `headers[0]`

Status: **resolved**

Disposition:

- Added numeric `headers[0]` and non-standard body-shape tests.

Residual risk:

- None at plan level.

### DS F6: missing all-zero dash value columns test

Status: **resolved**

Disposition:

- Added all-zero/dash aggregate beginning fail-closed test.

Residual risk:

- None at plan level.

### DS F7: split-line explicit class labels

Status: **no plan change required**

Disposition:

- Existing plan already requires normalization and support for split-line labels via `_normalized_header_text()` and `_header_has_explicit_share_class()`.

Residual risk:

- Implementation review should verify the explicit path still normalizes line breaks.

### DS F8: per-class zero vs aggregate zero assertion

Status: **resolved**

Disposition:

- Added all-zero/dash aggregate beginning fail-closed test.
- Preserved plan statement that per-class zero beginning is allowed only when aggregate beginning is non-zero.

Residual risk:

- None at plan level.

## MiMo Review Findings

### MiMo F-1: positional fallback and §2 cross-check not in current diff

Status: **resolved**

Disposition:

- Added explicit dirty-diff gap note: no positional fallback and no §2 ending cross-check currently exist.

Residual risk:

- Implementation review must verify these are actually added.

### MiMo F-2: §2 ending cross-check source unverified

Status: **resolved**

Disposition:

- Added the real §2 profile table shape and values.
- Replaced hypothetical generic row scanning with the profile-table contract.

Residual risk:

- The implementation worker must still prove the helper discovers this table through existing `ParsedAnnualReport` tables.

### MiMo F-3: `_format_decimal` output mismatch

Status: **resolved**

Disposition:

- Updated metric assertion guidance for stripped trailing zeroes and non-exact `net_change_ratio`.

Residual risk:

- None at plan level.

### MiMo F-4: mixed header detection imprecise

Status: **resolved**

Disposition:

- Defined signal as the same criteria used by explicit matching: mapped fund code in compact header or `_contains_share_class_label`.
- Added mixed fund-code/numeric signal test requirement.

Residual risk:

- None at plan level.

### MiMo F-5: redemption sign handling

Status: **confirmed and clarified**

Disposition:

- Added an explicit note that §10 redemption values are positive and subtracted by formula.

Residual risk:

- None at plan level.

### MiMo F-6: `_find_share_change_row` preferred keyword fallback limitation

Status: **accepted residual**

Disposition:

- No plan change beyond preserving narrow scope. The review marked this acceptable for the narrow repair scope and real 006597 should match preferred `总申购` / `总赎回` rows.

Residual risk:

- Future funds using weaker labels like `本期申购份额` without `总` may still fail closed with `incomplete_share_change_rows`. This is acceptable for this gate and should be handled in a separate rule-expansion gate if needed.

### MiMo F-7: commit/validation boundary clarity

Status: **no change required**

Disposition:

- Plan already states no commit/push/PR/release for this planning worker and treats current dirty diff as implementation baseline.

Residual risk:

- None at plan level.

### MiMo F-8: score/quality gate expectations

Status: **no change required**

Disposition:

- Plan already expects `redemption_share_pressure` to become satisfied while `drawdown_stress` remains weak and quality gate remains `warn`.

Residual risk:

- None at plan level.

## Final Residual Risks

- The implementation worker must code Slices 2 and 4 from scratch; they are not present in the dirty diff.
- The §2 profile-table contract is intentionally narrow. That protects against circular proof but can fail closed on reports with different disclosure layouts.
- The plan-fix did not execute tests or real extraction validation because this was a planning-only worker step.
