# Redemption Share Class Column Alignment Repair — Code Review (MiMo)

> Date: 2026-05-28
> Role: adversarial code review worker
> Scope: current uncommitted diff in `bond_risk_evidence.py` and `test_bond_risk_evidence.py`
> Focus: real 006597 acceptance correctness, cross-check integrity, test realism
> Verdict: **PASS**

## Review Inputs

- Plan: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-20260528.md`
- Controller judgment: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-controller-judgment-20260528.md`
- Implementation report: `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-implementation-20260528.md`
- `git diff -- fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py`

## Adversarial Trace: Real 006597 Page 65 Table 0 + Page 5 Table 0

### 1. §10 Table Selection (`_find_share_change_table`)

Real page 65 table 0 `_share_change_table_score`:

- `has_boundary_row`: "期初" in table_text → True
- `has_flow_row`: "申购" in table_text → True
- `has_share_semantics`: "基金份额" in table_text → True
- Score keywords: "基金份额"(+2), "份额总额"(+2), "基金总申购份额"(+2), "基金总赎回份额"(+2), "基金份额总额"(+2), "拆分"(+1) → score = 1 + 10 + 1 = 12
- No financial-statement keywords (`实收基金`/`未分配利润`/`净资产合计`) in this table → not rejected

**Result**: page 65 table 0 is correctly selected as the unique best candidate.

### 2. §10 Value Column Identification (`_share_change_value_columns`)

Real headers:

```python
("基金合同生\n效日（2018\n年12月3日）\n基金份额总\n额", "191,879,496.71", "46,593,432.66", "-", "-")
```

- `_parse_plain_decimal(headers[0])`: `_compact_text("基金合同生效日（2018年12月3日）基金份额总额")` = `"基金合同生效日（2018年12月3日）基金份额总额"` → `Decimal(...)` raises `InvalidOperation` → returns `None` → passes numeric-header check
- Row-label keyword check: real rows contain `期初`, `申购`, `赎回`, `期末`, `拆分`, `份额` → passes
- `_is_total_share_header` on headers[1..4]: `"191879496.71"`, `"46593432.66"`, `"-"`, `"-"` → none contain `合计`/`总计`/`总份额`/`基金份额总额` → all kept
- Returns `(1, 2, 3, 4)` → 4 value columns

**Result**: correctly identifies 4 value columns matching §2 class count.

### 3. §10 Column Alignment (`_align_share_change_columns`)

- `value_columns` count = 4 = `len(mapping.class_labels)` → passes count check
- Explicit matching loop: none of the 4 headers contain `006597`/`006598`/`014217`/`022176`/`A`/`C`/`E`/`F` as class labels → loop breaks
- `signal_count` = 0 → no mixed signal
- Falls through to unlabeled positional alignment: `{A: 1, C: 2, E: 3, F: 4}`
- `alignment_note = "section2_order_unlabeled_headers"`

**Result**: positional alignment correctly applied for real unlabeled headers.

### 4. §2 Row 11 Parsing: Line-Break Numbers and "份" Unit

Real §2 profile table row 11 (page 5 table 0):

```python
("报告期末下属分级基金的份额总额", "5,711,224,267.09", "4,760,029,015.27", "25,795,859.12", "52,531,021.84")
```

`_profile_ending_values_by_class`:

- `value_cells = ending_row[1:5]` → 4 cells
- `_parse_share_decimal("5,711,224,267.09")`: `_compact_text(...)` → `"5,711,224,267.09"`, `.replace(",", "")` → `"5711224267.09"`, `Decimal("5711224267.09")` → success
- Same for all 4 cells → `ending_values = {A: 5711224267.09, C: 4760029015.27, E: 25795859.12, F: 52531021.84}`

The "份" character in the row label `份额总额` does not interfere with value parsing; only `row[1:]` cells are parsed as decimals.

**Result**: all 4 ending values correctly parsed with comma removal and Decimal conversion.

### 5. §2 Cross-Check: No Generic 期末基金份额总额, No §10 Self-Certification

`_share_class_ending_cross_check_from_profile_tables`:

- `excluded_identity = (65, 0)` — excludes §10 share-change table
- Iterates all tables; for page 5 table 0: `(5, 0) != (65, 0)` → not excluded
- `_profile_cross_check_rows(page5_table0)`: searches for three exact row-label keywords in the same table:
  - `下属分级基金的基金简称` in row[0] of row 9 → `name_match`
  - `下属分级基金的交易代码` in row[0] of row 10 → `code_match`
  - `报告期末下属分级基金的份额总额` in row[0] of row 11 → `ending_match`
- All three present → returns `(name_match, code_match, ending_match)`

Key: the cross-check does **not** scan for generic `期末基金份额总额` text. It requires the specific three-row profile-table shape (`基金简称` + `交易代码` + `报告期末下属分级基金的份额总额` in the same table). The §10 table's ending row label `本报告期期末基金份额总额` does **not** contain `报告期末下属分级基金的份额总额`, so it cannot self-certify.

- `class_labels` from profile name cells: `_share_class_labels_from_profile_name_line("易方达安悦A")` → regex `[A-Z](?:类|份额)?(?=[一-鿿]|$)` matches `A` → `("A", "C", "E", "F")`
- `fund_codes` from code row: `re.fullmatch(r"\d{6}", "006597")` → `"006597"` → `("006597", "006598", "014217", "022176")`
- `class_labels == mapping.class_labels` and `fund_codes == mapping.fund_codes` → accepts
- Cross-check ending values match §10 computed endings within tolerance → passes

**Result**: cross-check correctly uses profile-table shape, excludes §10, avoids generic labels, and reconciles.

### 6. metric_value Aggregate and Class Breakdown

`_format_share_change_metric` output for real 006597:

- Aggregate: `beginning=12982005127.5, subscription=41674250439.28, redemption=44106675403.46, split=0, ending=10549580163.32, net_change=-2432424964.18, net_change_ratio=-0.187368...`
- Per-class breakdown: `A(code=006597, beginning=7699969800.13, ..., ending=5711224267.09, ...)`, `C(...)`, `E(...)`, `F(code=022176, beginning=0, ..., note=class_beginning_zero)`
- `mapping=§2 下属分级基金简称/交易代码表: A=006597; C=006598; E=014217; F=022176`
- `column_alignment=section2_order_unlabeled_headers`

Test assertion `test_redemption_share_pressure_aligns_real_unlabeled_section_ten_by_section_two_order` checks all these with `in` substring matches and `_format_decimal`-consistent values.

**Result**: metric_value correctly includes both aggregate totals and full A/C/E/F class breakdown with fund codes and notes.

### 7. Anchor Roles

`_share_change_row_anchor_drafts` produces 5 row anchors (beginning, subscription, redemption, split_or_change, share_ending). Combined with mapping and cross-check anchors:

| evidence_role | section_id | source |
|---|---|---|
| share_beginning | §10 | page 65 table 0 |
| subscription | §10 | page 65 table 0 |
| redemption | §10 | page 65 table 0 |
| split_or_change | §10 | page 65 table 0 |
| share_ending | §10 | page 65 table 0 |
| share_class_mapping | §2 | page 8 table 0 (or text) |
| share_class_ending_cross_check | §2 | page 5 table 0 |

Test asserts `{anchor.evidence_role for anchor in anchors} >= {"share_beginning", "subscription", "redemption", "share_ending", "share_class_mapping", "share_class_ending_cross_check"}`.

**Result**: all required anchor roles present for both §10 row-level evidence and §2 mapping/cross-check.

### 8. Test Fixture Realism

Tests use the real 006597 parsed shape:

- `_real_unlabeled_share_change_table`: exact header and row cell values from the plan's real §10 evidence, including `\n` line breaks in headers and row labels, comma-formatted decimals, and `-` dashes
- `_real_profile_cross_check_table`: 11-row table with rows 9/10/11 matching the real §2 profile shape
- Row label text matches real parsed cell content (e.g., `"本报告期期\n初基金份额\n总额"` with embedded newlines)
- Header `"基金合同生\n效日（2018\n年12月3日）\n基金份额总\n额"` matches the real inception-date header

Tests are not limited to synthetic ideal shapes. Fail-closed tests cover: mixed header signal, cross-check missing, cross-check mismatch, arithmetic mismatch, numeric headers[0], non-standard body, all-zero aggregate, self-certification protection.

**Result**: fixtures closely match real parsed table structure; test coverage is comprehensive for both happy path and fail-closed paths.

## Findings

None. All adversarial checks pass.

## Verdict

**PASS**

The implementation correctly handles the real 006597 §10 unlabeled column alignment with §2 cross-check. All guardrails (column count, row labels, arithmetic, cross-check exclusion, self-certification protection) are correctly implemented. Tests use realistic fixtures matching the real parsed table shape. The `redemption_share_pressure` group will move from `ambiguous` to `accepted` for real 006597/2024.
