# Redemption Share Class Column Alignment Repair Implementation

> Date: 2026-05-28
> Role: implementation worker, not controller
> Gate: `redemption share class column alignment repair gate`
> Status: implemented locally, targeted validation passed

## Scope

Changed allowed files only:

- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- this implementation artifact

No schema, score, snapshot, quality gate, Service/UI/Host/Agent/dayu, golden, release, README, `docs/design.md`, commit, push, PR, or merge work was performed.

## Helper Changes

Implemented the column-alignment repair on top of the current narrow-gate dirty baseline:

- Added explicit alignment mode tracking in `_ShareChangeColumnMapping.alignment_note`.
- Added `_share_change_value_columns()` to confirm §10 row-label shape before treating column 0 as row labels:
  - `headers[0]` must not be an ordinary numeric value.
  - at least one body `row[0]` must contain share-change row-label semantics such as `期初` / `申购` / `赎回` / `期末` / `拆分` / `变动` / `份额` / `项目`.
  - total-like value headers remain excluded.
- Added `_normalized_header_text()` and `_header_has_explicit_share_class()` so explicit header matching remains first and supports line-break-normalized labels/codes.
- Added fully unlabeled positional fallback in `_align_share_change_columns()`:
  - if all candidate headers have no class/fund-code signal and value-column count equals §2 class count, columns map by §2 order.
  - for real 006597 this maps `A/C/E/F -> columns 1/2/3/4`.
  - mixed label/code signal fails closed with `share_class_column_alignment_ambiguous`.
- Added §2 ending-share cross-check helpers:
  - `_share_class_ending_cross_check_from_profile_tables()`
  - `_profile_cross_check_rows()`
  - `_profile_ending_values_by_class()`
  - `_validate_share_class_ending_cross_check()`

## Real §10 / §2 Alignment Logic

Explicit header alignment remains preferred and is marked with:

```text
column_alignment=explicit_headers
```

The unlabeled path is only accepted when:

- §10 candidate value column count equals the complete §2 class count.
- no candidate header contains any fund-code or share-class signal.
- required §10 rows are present and parseable.
- per-class arithmetic reconciles using `beginning + subscription - redemption + split = ending`.
- aggregate beginning is non-zero and aggregate arithmetic reconciles.
- §2 profile cross-check exists in a different table from current §10 `(page_number, table_index)`.
- the §2 cross-check table contains all three rows in the same table:
  - `下属分级基金的基金简称`
  - `下属分级基金的交易代码`
  - `报告期末下属分级基金的份额总额`

For the real 006597 shape covered by unit fixture:

```text
§10 table: page 65 table 0
§2 cross-check source: page 5 table 0 rows 9/10/11
A=006597 -> column 1 -> ending 5,711,224,267.09
C=006598 -> column 2 -> ending 4,760,029,015.27
E=014217 -> column 3 -> ending 25,795,859.12
F=022176 -> column 4 -> ending 52,531,021.84
column_alignment=section2_order_unlabeled_headers
```

Aggregate fixture result:

```text
beginning=12982005127.5
subscription=41674250439.28
redemption=44106675403.46
split=0
ending=10549580163.32
net_change=-2432424964.18
net_change_ratio=-0.187368...
```

Redemption values are treated as positive row values and subtracted in the formula.

## Tests Added / Preserved

Added focused tests for:

- real-shaped unlabeled §10 A/C/E/F positional alignment with §2 ending-share cross-check
- explicit headers regression and explicit alignment metric note
- mixed class-label header signal fail-closed
- mixed fund-code header signal fail-closed
- §2 ending cross-check missing
- §2 ending cross-check mismatch
- cross-check self-certification protection by excluding current §10 table identity
- unlabeled-path arithmetic mismatch
- numeric `headers[0]` fail-closed
- non-standard body row-label fail-closed
- all-zero aggregate beginning fail-closed

Existing credit-risk and drawdown non-regression tests are still passing, including:

- holding rating distribution accepted
- fund-own rating rejected
- qualitative drawdown control remains weak

## Validation

Commands run:

```bash
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q -k redemption_share_pressure
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
```

Results:

```text
19 passed, 37 deselected in redemption_share_pressure subset
56 passed in full targeted test file
ruff: All checks passed
```

## Residual Risks

- Full repository validation and real `FundDocumentRepository` 006597 extraction snapshot/score/quality-gate validation were not run by this implementation worker; controller/validation worker owns that step.
- `drawdown_stress` remains weak by gate design and was not repaired.
- Generic `share_change` extractor remains out of scope.
- This implementation does not change score/gate semantics, schema, golden readiness, or release status.
