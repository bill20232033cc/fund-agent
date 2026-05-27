# Redemption Share Class Column Alignment Repair Plan

> Date: 2026-05-28
> Role: planning worker, not controller, not implementation worker
> Gate: `redemption share class column alignment repair gate`
> Status: code-generation-ready plan
> Blocking questions: none

## Worker Boundary

- This artifact is planning-only.
- Do not start or use gateflow.
- Do not modify production code, tests, generated reports, score, quality gate, schema, README, control doc, golden fixtures, Service/UI/Host/Agent/dayu, Git state, remote branches, PRs, or releases in this worker step.
- The implementation worker may edit only the planned narrow files unless controller expands scope:
  - `fund_agent/fund/extractors/bond_risk_evidence.py`
  - `tests/fund/extractors/test_bond_risk_evidence.py`
  - follow-up `docs/reviews/` implementation/review artifacts

## Truth And Evidence Read

Required sources were read:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-validation-failure-controller-judgment-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-implementation-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-rereview-ds-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-rereview-mimo-20260528.md`
- `reports/extraction-snapshots/bond-risk-narrow-006597-2024-20260528/snapshot.jsonl`
- `reports/scoring-runs/bond-risk-narrow-006597-2024-20260528/score.json`
- `reports/quality-gate-runs/bond-risk-narrow-006597-2024-20260528/quality_gate.json`
- current `git diff -- fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py`
- `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-review-ds-20260528.md`
- `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-review-mimo-20260528.md`

## Current Dirty Scope Classification

### Reuse As Narrow-Gate Baseline

The current dirty diff in `fund_agent/fund/extractors/bond_risk_evidence.py` and `tests/fund/extractors/test_bond_risk_evidence.py` is the implementation baseline for this repair. Reuse these parts:

- `credit_risk` holding-rating distribution path: accepted in real validation and re-reviewed by DS/MiMo.
- `drawdown_stress` boundary: qualitative control text remains weak and unsatisfied.
- §2 A/C/E/F mapping dataclass and helpers:
  - `_ShareClassMapping`
  - `_share_class_mapping_from_profile_tables`
  - `_share_class_mapping_from_profile_lines`
  - mapping anchor support
- §10 table selection and financial-statement rejection:
  - `_find_share_change_table`
  - `_share_change_table_score`
- row identification and fail-closed behavior:
  - `_find_share_change_rows`
  - `_find_share_change_row`
  - total申购/总赎回 preferred matching and 净申购/累计申购 exclusions
- Decimal share parsing:
  - comma/whitespace cleanup
  - `-` / `－` / `—` / `--` as zero
  - `Decimal("0.01")` tolerance
- class/aggregate arithmetic checks, metric formatting, and §10 row anchors.

Important implementation gap: the current dirty diff does **not** contain the unlabeled positional alignment path and does **not** contain the §2 ending-share cross-check. Slices 2 and 4 below are new code that the implementation worker must add. Do not treat the current dirty diff as already having repaired the real 006597 failure.

### Failure Evidence To Repair

Real validation stopped because `redemption_share_pressure` remained:

```text
status=ambiguous
strength=ambiguous
na_reason=share_class_column_count_mismatch
```

The snapshot row for `bond_risk_evidence` has:

```text
contract_status=partial
satisfied_groups=duration_rate_risk,credit_risk,leverage_liquidity,asset_allocation_holdings_mix,convertible_bond_equity_exposure
weak_groups=drawdown_stress
ambiguous_groups=redemption_share_pressure
```

`score.json` still reports `bond_risk_evidence_missing` with `baseline_blocking=true`; its `missing_evidence_groups` include `drawdown_stress` and `redemption_share_pressure`. `quality_gate.json` remains `warn` with FQ2F `reason=bond_risk_evidence_missing`. These are validation evidence, not fixtures to update in this gate.

### Unrelated / Out Of Scope

- Untracked `--help`, unrelated review artifacts, comprehensive review artifacts, and `docs/tmux-agent-memory-store.md`.
- Generated `reports/...` artifacts are validation outputs, not production fixtures.
- Generic `share_change` extractor row remains missing for 006597; it is a separate extractor problem and must not be repaired here.
- `drawdown_stress`, NAV-derived drawdown, credit risk, score policy, FQ0-FQ6 semantics, quality gate, baseline/golden readiness, Service/UI/Host/Agent/dayu, QDII/FOF/110020, PR/push/release are non-goals.

## Real §10 Structure Evidence

The real table was reproduced through `FundDocumentRepository` for `006597 / 2024`, page 65, table 0.

Headers:

```python
(
    "基金合同生\n效日（2018\n年12月3日）\n基金份额总\n额",
    "191,879,496.71",
    "46,593,432.66",
    "-",
    "-",
)
```

Rows:

```python
0 ("本报告期期\n初基金份额\n总额", "7,699,969,800.13", "5,252,561,821.84", "29,473,505.53", "-")
1 ("本报告期基\n金总申购份\n额", "27,623,952,157.07", "13,075,203,360.10", "910,677,227.41", "64,417,694.70")
2 ("减：本报告期\n基金总赎回\n份额", "29,612,697,690.11", "13,567,736,166.67", "914,354,873.82", "11,886,672.86")
3 ("本报告期基\n金拆分变动\n份额", "-", "-", "-", "-")
4 ("本报告期期\n末基金份额\n总额", "5,711,224,267.09", "4,760,029,015.27", "25,795,859.12", "52,531,021.84")
```

Known §2 mapping:

```text
A=006597, C=006598, E=014217, F=022176
```

Critical observation: the real §10 table has no A/C/E/F class labels in `headers`; columns 1..4 are class value columns whose header cells are inception-date class totals. Therefore explicit header matching by fund code or class label cannot work.

## Real §2 Profile Table Evidence

The real §2 profile table shape for `006597 / 2024` is implementable for the required ending-share cross-check. The cross-check must use this same-source profile table shape, not generic row text found anywhere in the annual report.

Source table:

```text
page_number=5
table_index=0
```

Rows in that same table:

```text
row 9  下属分级基金的基金简称             A / C / E / F
row 10 下属分级基金的交易代码             006597 / 006598 / 014217 / 022176
row 11 报告期末下属分级基金的份额总额     5,711,224,267.09 / 4,760,029,015.27 / 25,795,859.12 / 52,531,021.84
```

This table gives the independent §2 ending-share evidence needed to prove the real §10 unlabeled positional alignment:

```text
A 006597 ending=5,711,224,267.09
C 006598 ending=4,760,029,015.27
E 014217 ending=25,795,859.12
F 022176 ending=52,531,021.84
```

Cross-check implementation requirement:

- The §2 cross-check table must be a profile table that contains all three same-table row labels:
  - `下属分级基金的基金简称`
  - `下属分级基金的交易代码`
  - `报告期末下属分级基金的份额总额`
- The current §10 share-change table must be excluded by `(page_number, table_index)`; for the real table this means excluding `(65, 0)`.
- Do not use generic `期末基金份额总额` / `报告期末基金份额总额` candidates outside the profile-table shape above. Those labels can appear in §10 and would create a circular proof.
- The implementation must retain/report the table used for the cross-check through the §2 cross-check anchor or implementation report so reviewers can verify it is not the §10 table.

## Root Cause

Current `_align_share_change_columns()` does two things:

1. Builds `value_columns` from `table.headers[1:]`, excluding total-like headers.
2. For each mapped class, requires exactly one value-column header to contain either the fund code or class label.

For the real §10 table:

- `len(value_columns) == 4`, which matches the four §2 classes.
- But every value-column header is numeric or dash:
  - `191,879,496.71`
  - `46,593,432.66`
  - `-`
  - `-`
- No header contains `006597`, `006598`, `014217`, `022176`, `A`, `C`, `E`, or `F`.
- The per-class `unique_matches` are empty, and the helper returns `share_class_column_count_mismatch`.

So the failure reason is not actual count mismatch; it is a label-based alignment false negative reported through the same `na_reason`.

## Repair Goal

Add a conservative unlabeled-column positional alignment path for real §10 A/C/E/F tables:

- Use explicit header labels when they exist.
- If §10 has no class labels, align columns 1..N to §2 mapping order only when all guardrails pass:
  - §2 mapping has a complete ordered class/code sequence.
  - §10 value column count equals class count.
  - required rows are present and unique.
  - every class value parses.
  - class arithmetic reconciles.
  - aggregate arithmetic reconciles.
  - §2 ending share cross-check reconciles each class against the same-source §2 profile table described above, using annual-report evidence available through `ParsedAnnualReport`.
- If any condition fails, return `ambiguous` and do not guess.

## Design Constraints

- Production annual-report access remains through `FundDocumentRepository`; extractor implementation consumes `ParsedAnnualReport` only.
- Keep the repair inside Agent-layer fund extractor code.
- Do not change public models, snapshot schema, score schema, quality gate rules, or Service/UI behavior.
- Do not weaken evidence semantics: only accepted all-class aggregation satisfies `redemption_share_pressure`.
- Preserve class breakdown and row anchors.
- Maintain Chinese docstrings for new/changed functions.
- Prefer module-level private helper functions; no nested functions/classes.

## Implementation Plan

### Slice 1: Normalize §10 Table Shape

File: `fund_agent/fund/extractors/bond_risk_evidence.py`

Add or refactor helpers around `_align_share_change_columns()`:

- `_share_change_value_columns(table) -> tuple[int, ...]`
  - Return candidate value column indexes that are neither row-label columns nor total/aggregate columns.
  - For the real table, return `(1, 2, 3, 4)`.
  - Default to `headers[0]` / column index `0` as the row-label/current item column even when it contains inception-date wording.
  - This default is valid only after a row-label precondition passes:
    - at least one required row has `row[0]` text matching row-label semantics such as `期初`, `申购`, `赎回`, `期末`, `拆分`, `变动`, `份额`, or `项目`;
    - `headers[0]` must not parse as an ordinary numeric value. If `_parse_plain_decimal(headers[0])` or equivalent strict numeric parsing succeeds, fail closed by returning an empty tuple.
  - If the row-label column cannot be confirmed, return an empty tuple and let the caller fail closed with a precise alignment/count reason.
  - Reuse `_is_total_share_header` or equivalent total-header detection to exclude total/aggregate columns.
  - Do not require `headers[0]` to literally be `项目`.

- `_normalized_header_text(header) -> str`
  - Use `_normalize_cell()` and `_compact_text()` so cross-line header text becomes stable.
  - Example: `"基金合同生\n效日..."` becomes compact single text.

- `_header_has_explicit_share_class(header, class_label, fund_code) -> bool`
  - Encapsulate current explicit matching:
    - fund code in compact header
    - `_contains_share_class_label(header, class_label)`
  - Must support class names split by line breaks through normalization.

Keep existing explicit header path first. It remains correct for synthetic and future tables with labels like `易方达安悦 A` / `A类` / `006597`.

### Slice 2: Add Conservative Unlabeled Positional Alignment

Modify `_align_share_change_columns(table, mapping)`:

1. Build candidate value columns.
2. If candidate count differs from `len(mapping.class_labels)`, return `share_class_column_count_mismatch`.
3. Try explicit header matching exactly as current behavior.
4. If explicit matching succeeds uniquely, return it.
5. Define header signal with the same criteria as explicit matching:
   - mapped fund code appears in compact header text; or
   - `_contains_share_class_label(header, class_label)` is true.
6. If no candidate header contains any class/fund-code signal, try unlabeled positional alignment:
   - align `mapping.class_labels[0]` to `value_columns[0]`
   - align `mapping.class_labels[1]` to `value_columns[1]`
   - align `mapping.class_labels[2]` to `value_columns[2]`
   - align `mapping.class_labels[3]` to `value_columns[3]`
7. If some but not all candidate headers/classes contain class/fund-code signal, fail closed with `share_class_column_alignment_ambiguous` or `share_class_column_count_mismatch`.

For real 006597:

```text
A -> column 1
C -> column 2
E -> column 3
F -> column 4
```

Do not use this positional fallback unless the table is fully unlabeled. A mixed case is too risky because it may indicate parsed header drift.

### Slice 3: Add Row And Value Shape Guardrails Before Acceptance

The current aggregation already checks rows and arithmetic after column alignment. Strengthen the positional fallback with preconditions or postconditions:

- Required rows:
  - beginning: `期初` + `基金份额总额`
  - subscription: preferred `总申购` / `申购份额`, excluding `净申购` / `累计申购`
  - redemption: preferred `总赎回` / `赎回份额`, excluding `净赎回` / `累计赎回`
  - ending: `期末` + `基金份额总额`
  - split/change optional, dash treated as zero
- Row count:
  - each required row must have at least all aligned class columns.
  - if any aligned column is out of range, return `share_class_column_count_mismatch`.
- Numeric parsing:
  - every aligned value in required rows must parse via `_parse_share_decimal`.
  - `-`, `－`, `—`, and `--` remain zero.
  - non-parseable values return `non_parseable_share_value`.
- Arithmetic:
  - per class: `beginning + subscription - redemption + split == ending`, tolerance `Decimal("0.01")`.
  - aggregate: sum classes and reconcile aggregate beginning + net change to aggregate ending.
  - per-class beginning zero is allowed with `class_beginning_zero`; aggregate beginning zero fails closed.
  - §10 redemption row values are positive numbers under a row label beginning with `减：`; compute `subscription - redemption + split`. Do not import negative-number semantics from balance-sheet or cash-flow statement contexts into this §10 share-change table.

The real table should reconcile:

```text
A: 7,699,969,800.13 + 27,623,952,157.07 - 29,612,697,690.11 + 0 = 5,711,224,267.09
C: 5,252,561,821.84 + 13,075,203,360.10 - 13,567,736,166.67 + 0 = 4,760,029,015.27
E: 29,473,505.53 + 910,677,227.41 - 914,354,873.82 + 0 = 25,795,859.12
F: 0 + 64,417,694.70 - 11,886,672.86 + 0 = 52,531,021.84
```

Aggregate expected values:

```text
beginning=12,982,005,127.50  # _format_decimal emits 12982005127.5 in metric strings
subscription=41,674,250,439.28
redemption=44,106,675,403.46
split=0
ending=10,549,580,163.32
net_change=-2,432,424,964.18
net_change_ratio≈-0.18737
```

### Slice 4: Cross-Check Against §2 Ending Shares

The user explicitly requires §2 report-period-ending cross-check. Implement this without schema changes.

Add helper:

- `_share_class_ending_shares_from_profile_tables(report, mapping, group_id) -> _ShareClassEndingCrossCheck | None`

Implementation shape:

- Search parsed tables only for a same-source §2 profile table that contains all three required row labels in the same table:
  - `下属分级基金的基金简称`
  - `下属分级基金的交易代码`
  - `报告期末下属分级基金的份额总额`
- Exclude the current §10 share-change table by `(page_number, table_index)` before accepting any cross-check source. For real 006597, the §10 table is `(65, 0)` and the §2 profile table is `(5, 0)`.
- Do not scan all tables for generic `期末基金份额总额` or `报告期末基金份额总额`; those can match the §10 share-change table and would self-certify the alignment.
- In the matched §2 profile table, use the fund-short-name row and fund-code row to prove the A/C/E/F order, then parse the ending-share row in that same order.
- Parse Decimal values with dash-as-zero.
- Return per-class ending shares and an optional §2 anchor draft.
- If no reliable §2 ending-share row exists, fail closed for positional §10 fallback with a precise reason such as `share_class_ending_cross_check_missing`.
- If values exist but do not reconcile with §10 ending per class within `Decimal("0.01")`, fail closed with `share_class_ending_cross_check_mismatch`.

Keep this cross-check required only for the unlabeled positional path. Explicit header alignment can retain current behavior unless controller decides to make §2 ending cross-check universal.

Implementation note: The real §2 table shape above shows this cross-check is implementable for 006597. If another fixture or future report lacks the three-row profile shape, fail closed and report the exact parsed table shape rather than guessing. Do not silently downgrade this requirement.

### Slice 5: Preserve Anchors And Metric Breakdown

Keep existing output contract:

- `metric_name="A/C/E/F 份额变动汇总"`
- `summary="年报份额变动表可按 §2 A/C/E/F 映射聚合全份额类别申购赎回数据"`
- §10 anchors for at least:
  - `share_beginning`
  - `subscription`
  - `redemption`
  - `share_ending`
  - optional `split_or_change`
- §2 mapping anchor when mapping comes from table.
- Add §2 ending cross-check anchor if implemented cleanly.

`metric_value` must include:

- aggregate beginning/subscription/redemption/split/ending/net_change/net_change_ratio
- class breakdown for A/C/E/F with fund codes
- `class_beginning_zero` for F if applicable
- mapping source
- optional alignment note such as `column_alignment=section2_order_unlabeled_headers`

Do not remove existing class breakdown to make the string shorter; the breakdown is part of the evidence surface.

### Slice 6: Fail-Closed Reasons

Use precise `na_reason` values:

- Keep `share_class_column_count_mismatch` for actual count mismatch or mixed/partial explicit header signals.
- Add `share_class_column_alignment_ambiguous` if the code needs to distinguish mixed label states.
- Add `share_class_ending_cross_check_missing` for missing §2 ending shares under unlabeled positional fallback.
- Add `share_class_ending_cross_check_mismatch` for §2/§10 ending mismatch.
- Keep existing:
  - `ambiguous_share_class_selection`
  - `ambiguous_share_change_table`
  - `incomplete_share_change_rows`
  - `non_parseable_share_value`
  - `share_change_arithmetic_mismatch`
  - `aggregate_beginning_zero`

Any inability to prove alignment must return `ambiguous`; no A-only fallback and no positional guessing without all guardrails.

## Required Tests

File: `tests/fund/extractors/test_bond_risk_evidence.py`

Add focused tests; no network in unit tests.

### 1. Real-Shape Unlabeled §10 Alignment

Create a fixture matching the real page 65 table:

```python
headers=(
    "基金合同生\n效日（2018\n年12月3日）\n基金份额总\n额",
    "191,879,496.71",
    "46,593,432.66",
    "-",
    "-",
)
rows=(
    ("本报告期期\n初基金份额\n总额", "7,699,969,800.13", "5,252,561,821.84", "29,473,505.53", "-"),
    ("本报告期基\n金总申购份\n额", "27,623,952,157.07", "13,075,203,360.10", "910,677,227.41", "64,417,694.70"),
    ("减：本报告期\n基金总赎回\n份额", "29,612,697,690.11", "13,567,736,166.67", "914,354,873.82", "11,886,672.86"),
    ("本报告期基\n金拆分变动\n份额", "-", "-", "-", "-"),
    ("本报告期期\n末基金份额\n总额", "5,711,224,267.09", "4,760,029,015.27", "25,795,859.12", "52,531,021.84"),
)
```

Include §2 A/C/E/F mapping and §2 ending-share cross-check fixture. Assert:

- `redemption_share_pressure.status == "accepted"`
- `redemption_share_pressure` is in `satisfied_group_ids`
- `na_reason is None`
- metric includes `A(code=006597`, `C(code=006598`, `E(code=014217`, `F(code=022176`
- metric includes the real aggregate values, using `_format_decimal` output rather than hand-preserved trailing zeroes:
  - `beginning=12982005127.5`
  - `subscription=41674250439.28`
  - `redemption=44106675403.46`
  - `ending=10549580163.32`
  - `net_change=-2432424964.18`
- do not assert a full exact `net_change_ratio` long decimal string; either assert a stable prefix such as `net_change_ratio=-0.18737` or parse the metric value and compare the Decimal/float within a documented tolerance.
- metric includes `class_beginning_zero` for F.
- anchors include §10 beginning/subscription/redemption/ending and §2 mapping/cross-check anchors.

### 2. Explicit Headers Still Work

Keep existing synthetic `易方达安悦 A/C/E/F` test passing. Add assertion that explicit path does not require unlabeled positional note.

### 3. Mixed Header Signals Fail Closed

Use headers like:

```python
("项目", "国泰利享中短债债券A", "46,593,432.66", "-", "-")
```

Assert:

- `status == "ambiguous"`
- `na_reason` is `share_class_column_alignment_ambiguous` or `share_class_column_count_mismatch`
- not satisfied

Also cover a mixed-signal variant where one column contains a fund code while other class columns are numeric/dash. It must fail closed rather than combining explicit and positional alignment.

### 4. §2 Ending Cross-Check Missing Fails Closed

Use real-shaped §10 table and §2 mapping but omit §2 ending-share row. Assert:

- `status == "ambiguous"`
- `na_reason == "share_class_ending_cross_check_missing"`

### 5. §2 Ending Cross-Check Mismatch Fails Closed

Change one §2 ending value, e.g. A ending from `5,711,224,267.09` to `5,711,224,267.10`. Assert:

- `status == "ambiguous"`
- `na_reason == "share_class_ending_cross_check_mismatch"`

### 6. Arithmetic Guard Still Fails Closed

Use unlabeled real-shaped headers but alter §10 ending A by a material amount. Assert:

- `status == "ambiguous"`
- `na_reason == "share_change_arithmetic_mismatch"`

### 7. Column Count Mismatch Still Fails Closed

Use §2 A/C/E/F mapping but only three unlabeled value columns. Assert:

- `status == "ambiguous"`
- `na_reason == "share_class_column_count_mismatch"`

### 8. Row-Label Column Precondition Fails Closed For Numeric `headers[0]`

Use a real-shaped §10 body but set `headers[0]` to an ordinary numeric value such as `"123,456.78"`. Assert:

- `status == "ambiguous"`
- `na_reason` is `share_class_column_alignment_ambiguous` or `share_class_column_count_mismatch`
- no positional alignment is accepted.

### 9. Row-Label Column Precondition Fails Closed For Non-Standard Body Shape

Use headers with no explicit class signal and rows whose `row[0]` cells do not contain required row-label semantics (`期初`, `申购`, `赎回`, `期末`, `拆分`, `变动`, `份额`, `项目`). Assert fail-closed. This protects `_share_change_value_columns()` from treating column 0 as a row-label column when the table shape is not a §10 share-change table.

### 10. All-Zero / Dash Aggregate Beginning Fails Closed

Use an unlabeled table where all class value columns are dash/zero in all required rows. Assert:

- `status == "ambiguous"`
- `na_reason == "aggregate_beginning_zero"`

Per-class zero beginning remains allowed only when the aggregate beginning is non-zero, as in real 006597 F.

### 11. §2 Cross-Check Source Must Not Self-Certify With §10

Use a fixture where the only table with ending-share-like wording is the §10 share-change table and there is no §2 profile table containing all three required rows (`基金简称`, `交易代码`, `报告期末下属分级基金的份额总额`). Assert:

- `status == "ambiguous"`
- `na_reason == "share_class_ending_cross_check_missing"`

Use a second fixture with a proper §2 profile table but one mismatched ending value. Assert:

- `status == "ambiguous"`
- `na_reason == "share_class_ending_cross_check_mismatch"`

### 12. Drawdown And Credit Non-Regression

Keep existing tests for:

- qualitative drawdown remains weak
- holding rating distribution remains accepted
- fund own rating remains rejected

Do not add score/gate/golden tests in this narrow repair.

## Real 006597 Validation Plan

Implementation worker may run targeted local tests. Controller or authorized validation worker should run real-path validation after implementation:

```bash
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; repo = FundDocumentRepository(); report = asyncio.run(repo.load_annual_report("006597", 2024, force_refresh=True)); print(report.key.fund_code, report.key.year, len(report.sections), len(report.tables))'
uv run fund-analysis extraction-snapshot --run-id bond-risk-redemption-column-alignment-006597-2024-20260528 --fund-code 006597 --report-year 2024 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/bond-risk-redemption-column-alignment-006597-2024-20260528
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-redemption-column-alignment-006597-2024-20260528/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-redemption-column-alignment-006597-2024-20260528/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/bond-risk-redemption-column-alignment-006597-2024-20260528
uv run fund-analysis quality-gate --score-path reports/scoring-runs/bond-risk-redemption-column-alignment-006597-2024-20260528/score.json --output-dir reports/quality-gate-runs/bond-risk-redemption-column-alignment-006597-2024-20260528
```

Expected real validation:

- `redemption_share_pressure` moves from ambiguous to satisfied.
- `credit_risk` remains satisfied.
- `drawdown_stress` remains weak.
- Snapshot:
  - `bond_risk_satisfied_groups` includes `redemption_share_pressure`
  - `bond_risk_ambiguous_groups` does not include `redemption_share_pressure`
  - `bond_risk_weak_groups` still includes `drawdown_stress`
- Score:
  - `missing_evidence_groups` drops to only `["drawdown_stress"]`
  - `bond_risk_evidence_missing.baseline_blocking` remains `true`
- Quality gate:
  - remains `warn` while drawdown is unresolved
  - no FQ0-FQ6 semantic change

Generated reports remain local validation outputs and must not be promoted as fixtures in this gate.

## Review Checklist

Plan/implementation reviewers must explicitly check:

- The repair only touches `redemption_share_pressure` column alignment and directly related tests.
- Explicit header alignment remains supported.
- Unlabeled positional alignment is allowed only for fully unlabeled class columns and only with all guardrails passing.
- §2 mapping order is used only after §2 mapping is complete and ordered.
- §2 ending-share cross-check is enforced for unlabeled positional alignment.
- Class and aggregate arithmetic are still fail-closed.
- Class breakdown and §10/§2 anchors are preserved.
- No A-only acceptance path is reintroduced.
- No drawdown, credit_risk, score, quality gate, schema, snapshot, Service/UI/Host/Agent/dayu, golden, PR, or release behavior changes.

## Completion Report Required From Implementation Worker

Report:

- files changed
- helper/function changes
- whether explicit header path and unlabeled positional path both exist
- real §10 alignment result for A/C/E/F columns
- §2 ending cross-check source and result
- aggregate totals and class breakdown
- anchor counts and roles
- tests added
- validation commands run and results
- explicit confirmation that drawdown, score/gate semantics, schema, and golden were not changed

## Final Non-Goals

- No drawdown repair.
- No credit_risk repair.
- No generic `share_change` repair.
- No score/quality gate/golden/schema changes.
- No baseline/golden promotion.
- No Service/UI/Host/Agent/dayu work.
- No commit/push/PR/release.
