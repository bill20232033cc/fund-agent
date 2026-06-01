# Bond Risk Evidence Extractor Investigation: 006597/2024 Unsatisfied Groups

> Date: 2026-05-28
> Role: investigation worker (GLM)
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Work unit: Slice 6 investigation — real 006597/2024 path for credit_risk, drawdown_stress, redemption_share_pressure
> Method: FundDocumentRepository only; no direct PDF/cache access; no code changes
> Status: complete

## Worker Self-Check

### Before Start

- Self-check: pass
- Role confirmed: investigation worker only; no code modification, no review, no controller judgment.
- Current gate confirmed: investigation within the accepted bond risk evidence extractor / anchor hardening design gate.
- External-state boundary confirmed: no workflow command, no skill, no implementation, no commit, no PR, no golden promotion.
- Document access method: all annual report data accessed through `FundDocumentRepository().load_annual_report("006597", 2024)`, per `AGENTS.md` hard constraint.

### Before File Edit

- Self-check: pass
- Allowed write path: this artifact only.
- No source code, test, or configuration file touched.

### Before Completion

- Self-check: pass
- Root causes identified for all three groups.
- Real evidence located where available.
- Recommended rule adjustments specified for two groups; honest data absence confirmed for one group.

## Executive Summary

Extractor output for 006597/2024:

| Group | Status | Strength | na_reason |
|---|---|---|---|
| duration_rate_risk | accepted | qualitative_direct | — |
| **credit_risk** | **weak** | qualitative_direct | credit_risk_table_not_found |
| leverage_liquidity | accepted | quantitative_direct | — |
| asset_allocation_holdings_mix | accepted | quantitative_direct | — |
| **drawdown_stress** | **weak** | qualitative_control_intent | drawdown_metric_not_found |
| **redemption_share_pressure** | **ambiguous** | ambiguous | ambiguous_share_class_selection |
| convertible_bond_equity_exposure | accepted_absence | quantitative_absence | — |

Of the three unsatisfied groups:

- **credit_risk**: real quantitative table evidence EXISTS but is missed due to a row-keyword mismatch. Fixable by rule adjustment.
- **drawdown_stress**: no quantitative evidence exists in this annual report. Correctly classified as weak. Not fixable by rule adjustment.
- **redemption_share_pressure**: real share change table EXISTS (Table #78, page 65) but extractor finds wrong table (Table #23, page 28) AND §2 share-class disambiguation fails. Fixable by rule adjustment.

---

## Group 1: credit_risk

### Current Extractor Behavior

`_extract_credit_risk` at `bond_risk_evidence.py:186-237`:

1. First attempts `_first_row_anchor_draft` with:
   - `table_keywords=("信用", "评级")` — table-level filter
   - `row_keywords=("信用", "评级")` — row-level filter, requires BOTH keywords in a single row
   - `section_id=_SECTION_PORTFOLIO` (§8) — but note: `_first_row_anchor_draft` iterates ALL tables and does NOT filter by section_id
2. Falls back to `_find_text_match` for qualitative text evidence.

### Root Cause

The table-level filter (`table_keywords`) PASSES for Tables #59-#62 (pages 53-54), which contain "信用" and "评级" in their joined text. However, the row-level filter (`row_keywords`) FAILS because:

- **"信用评级" appears in table headers, not data rows.**
- Table #59 header: `("短期信用评级", "本期末\n2024年12月31日", "上年度末\n2023年12月31日")`
- Table #60 header: `("长期信用评级", "本期末\n2024年12月31日", "上年度末\n2023年12月31日")`
- Data rows only contain rating LEVELS: "A-1", "AAA", "AAA以下", "未评级", "合计"
- NO data row contains both "信用" AND "评级" simultaneously
- The row closest to matching is "未评级" rows which contain "评级" but not "信用"

Therefore the extractor falls through to the text-match fallback and produces `status="weak"`.

### Real Annual Report Evidence

The following tables contain accepted-grade quantitative credit risk evidence:

**Table #59** (page 53): Short-term credit rating distribution
- Header: `("短期信用评级", "本期末 2024年12月31日", "上年度末 2023年12月31日")`
- row[0]: A-1 = `- / 350,905,243.85`
- row[1]: A-1以下 = `- / -`
- row[2]: 未评级 = `6,353,108,138.08 / 6,284,132,252.49`
- row[3]: 合计 = `6,353,108,138.08 / 6,635,037,496.34`

**Table #60** (page 53): Long-term credit rating distribution
- Header: `("长期信用评级", "本期末 2024年12月31日", "上年度末 2023年12月31日")`
- row[0]: AAA = `2,351,107,087.67 / 2,965,435,011.41`
- row[1]: AAA以下 = `604,590,889.09 / 1,156,312,758.11`
- row[2]: 未评级 = `2,135,570,155.83 / 6,587,163,266.27`
- row[3]: 合计 = `5,091,268,132.59 / 10,708,911,035.79`

**Table #61** (page 54): Short-term credit rating for another instrument category
- Header: `("AAA", "118,947,137.22", "-")`

**Table #62** (page 54): Long-term credit rating for another instrument category
- Header: `("长期信用评级", "本期末 2024年12月31日", "上年度末 2023年12月31日")`
- row[0]: AAA = `- / -`
- row[1]: AAA以下 = `543,392,188.50 / 623,266,826.97`
- row[2]: 未评级 = `- / -`
- row[3]: 合计 = `543,392,188.50 / 623,266,826.97`

This evidence clearly shows credit rating distribution with AAA concentration and amounts — matching the plan's `measurement_kind="actual_exposure"` and `strength="quantitative_direct"` expectations.

### Recommended Rule Adjustment

Change the credit_risk extractor to use a two-phase approach:

**Phase 1 — Header-level table detection**: Find tables where the header row contains "信用" + "评级" (already works via `_table_contains_all`).

**Phase 2 — Row-level extraction from rating-level rows**: After finding a matching table, extract from data rows using relaxed row keywords. Instead of requiring both "信用" AND "评级" in each row, match rows that contain actual rating levels such as "AAA", "A-1", "未评级", or "合计". Or: change `row_keywords` to `("评级",)` combined with a header-presence check, or add a dedicated `_credit_rating_table_anchor_draft` helper that:

1. Identifies tables where headers contain "信用" + "评级".
2. Uses the header row itself as the primary anchor (since "短期信用评级" / "长期信用评级" IS the row label).
3. Extracts the first meaningful data row (e.g., the "AAA" or "未评级" row) for metric_value.

Expected result after fix: `status="accepted"`, `strength="quantitative_direct"`, `measurement_kind="actual_exposure"`, with anchors pointing to Table #59 or #60 rows.

### Anchor References (for implementation)

- `bond-risk:006597:2024:credit_risk:1` → section_id=§8 (or the actual parsed section), page=53, table_id=page-53-table-0, row_locator for "短期信用评级" header or first data row, evidence_role=credit_rating_distribution
- `bond-risk:006597:2024:credit_risk:2` → page=53, table_id=page-53-table-1, row_locator for "长期信用评级" header or first data row, evidence_role=credit_rating_distribution

---

## Group 2: drawdown_stress

### Current Extractor Behavior

`_extract_drawdown_stress` at `bond_risk_evidence.py:343-394`:

1. First attempts `_first_row_anchor_draft` with `table_keywords=("回撤",)` and `row_keywords=("最大回撤",)`.
2. Falls back to `_find_text_match` with `keyword_groups=(("控制回撤",), ("回撤",))` in §4 and §5.

### Root Cause

This is **correctly classified as weak**. The annual report genuinely does NOT contain:

- Any max drawdown metric or table.
- Any volatility metric or table.
- Any stress test result or table.
- Any "下行风险" metric.

The only evidence found is in §4 line 189: `控制回撤的前提下提供持续稳定的组合净值表现` — qualitative drawdown control intent.

Full text search results for drawdown-related keywords:

| Section | Line | Content | Classification |
|---|---|---|---|
| §4 | 189 | 控制回撤的前提下提供持续稳定的组合净值表现 | qualitative_control_intent |
| §4 | 146-164 | Multiple lines with "下行" | Yield curve direction, NOT drawdown risk |

Lines 146-164 all use "下行" in the context of "债市收益率下行" (bond market yield decline), which is interest rate direction, NOT downside risk or drawdown.

### Why This Cannot Be Resolved

The 006597/2024 annual report is a standard Chinese bond fund disclosure. Chinese bond fund annual reports are NOT required to disclose max drawdown, volatility, or stress test results. These metrics would need to be:

- Extracted from the fund's net asset value series (calculated, not disclosed).
- Or found in supplementary marketing materials (outside the annual report scope).

Per the plan: `drawdown_control_intent alone is status="weak"`, `strength="qualitative_control_intent"`, and does not satisfy the required group. The safe option is correctly selected.

### Residual Owner Statement

`drawdown_stress` should remain in `weak_group_ids` for 006597/2024. To resolve this group, a future gate would need to either:

1. Accept calculated max drawdown from NAV data as evidence (requires explicit authorization).
2. Accept qualitative drawdown control intent as satisfying for bond funds (weakens the contract — not recommended).
3. Mark this group as `baseline_blocking=False` for bond funds that don't disclose drawdown (requires contract change).

---

## Group 3: redemption_share_pressure

### Current Extractor Behavior

`_extract_redemption_share_pressure` at `bond_risk_evidence.py:397-470`:

1. `_find_share_change_table(report.tables)` — searches for tables containing "期初" + "期末" + ("申购" OR "赎回").
2. `_share_class_evidence(report)` — tries to identify which share class (A/C/E/F) corresponds to fund code 006597 from §2 text.
3. `_select_share_change_column` — uses share class evidence to select the correct column in the share change table.

### Root Cause (Compound Failure)

Two bugs compound:

**Bug A — Wrong table found**: `_find_share_change_table` returns Table #23 (page 28, 净资产变动表 — Statement of Changes in Net Assets) instead of Table #78 (page 65, §10 基金份额变动表 — Share Change Table). Both tables contain "期初"/"期末"/"申购"/"赎回" keywords, but:

- Table #23 is a financial statement with columns: `项目 | 实收基金 | 未分配利润 | 净资产合计`. It does NOT have share-class-level columns.
- Table #78 is the actual §10 share change table with columns for each share class (A/C/E/F).

The function returns the FIRST table matching the keywords, which happens to be Table #23.

**Bug B — §2 share class mapping failure**: `_share_class_evidence` returns `None` because the §2 text splits share class names across 3 lines:

- Line 13: `国泰利享中 国泰利享中 国泰利享中 国泰利享中` (prefix without suffix)
- Line 14: `下属分级基金的基金简称` (label line)
- Line 15: `短债债券A 短债债券C 短债债券E 短债债券F` (suffix without prefix)
- Line 16: `下属分级基金的交易代码 006597 006598 014217 022176`

The `_share_class_evidence_from_profile_lines` function expects "基金简称" and "交易代码" on nearby lines with extractable class labels, but the actual text has:
- Line 14 contains "基金简称" but the names are split across lines 13 and 15 (prefix and suffix).
- Line 16 has "交易代码" with codes, but the name-code pairing requires understanding the multi-line structure.

Additionally, `_section_two_contains_class_mapping` checks distance between fund code "006597" and class label "A" within 80 characters of compacted text — this may fail because the §2 compact text interleaves codes and class labels in a table structure.

**However**: Table #0 (page 5, the parsed §2 table) cleanly contains the mapping:

| row[9] | header[1] | header[2] | header[3] | header[4] |
|---|---|---|---|---|
| 下属分级基金的基金简称 | 国泰利享中短债债券A | 国泰利享中短债债券C | 国泰利享中短债债券E | 国泰利享中短债债券F |
| row[10] | **006597** | **006598** | **014217** | **022176** |

This table clearly maps: fund code 006597 → A share → column index 1.

### Real Annual Report Evidence

**Table #78** (page 65): §10 Share Change Table

| Row label | Column 1 (A=006597) | Column 2 (C=006598) | Column 3 (E=014217) | Column 4 (F=022176) |
|---|---|---|---|---|
| 基金合同生效日基金份额总额 | 191,879,496.71 | 46,593,432.66 | - | - |
| 本报告期期初基金份额总额 | 7,699,969,800.13 | 5,252,561,821.84 | 29,473,505.53 | - |
| 本报告期基金总申购份额 | 27,623,952,157.07 | 13,075,203,360.10 | 910,677,227.41 | 64,417,694.70 |
| 减：本报告期基金总赎回份额 | 29,612,697,690.11 | 13,567,736,166.67 | 914,354,873.82 | 11,886,672.86 |
| 本报告期基金拆分变动份额 | - | - | - | - |
| 本报告期期末基金份额总额 | 5,711,224,267.09 | 4,760,029,015.27 | 25,795,859.12 | 52,531,021.84 |

Net redemption for A share: 申购 276.2 亿 - 赎回 296.1 亿 = 净赎回 19.9 亿.

This is clearly accepted-grade quantitative evidence for `redemption_share_pressure`.

### Recommended Rule Adjustment

**Fix A — Improve share change table detection**: Change `_find_share_change_table` to:

1. Prefer tables that contain "基金份额" + ("申购份额" OR "总申购") + ("赎回份额" OR "总赎回") + ("期初" OR "期") + ("期末" OR "期末").
2. Deprioritize tables where headers contain "实收基金" / "未分配利润" / "净资产" (financial statement patterns).
3. Or: search for "基金份额变动" / "份额总额" as stronger signals for the actual §10 table.

**Fix B — Use parsed §2 table (Table #0) for share class mapping**: Change `_share_class_evidence` to:

1. Check parsed tables (Table #0) for "下属分级基金的基金简称" and "下属分级基金的交易代码" rows.
2. When Table #0 row[9] has "基金简称" in the first cell and subsequent cells contain share class names with A/C/E/F labels, AND row[10] has "交易代码" with fund codes in subsequent cells, extract the column mapping directly.
3. This is more reliable than raw text parsing for multi-line §2 layouts.

**Fix C — Column selection**: When Table #78 headers don't contain fund codes directly (they contain numeric values instead), use the §2 table mapping to determine which column corresponds to the target fund code. Position-based: if §2 table maps 006597 → column 1, then Table #78 column 1 is the A share data.

Expected result after fix: `status="accepted"`, `strength="quantitative_direct"`, `measurement_kind="actual_exposure"`, with anchors for share_beginning, subscription, redemption, and share_ending rows in Table #78.

### Anchor References (for implementation)

- `bond-risk:006597:2024:redemption_share_pressure:1` → section_id=§10, page=65, table_id=page-65-table-0, row_locator for "期初基金份额" row, column=A, evidence_role=share_beginning
- `bond-risk:006597:2024:redemption_share_pressure:2` → row_locator for "总申购份额" row, evidence_role=subscription
- `bond-risk:006597:2024:redemption_share_pressure:3` → row_locator for "总赎回份额" row, evidence_role=redemption
- `bond-risk:006597:2024:redemption_share_pressure:4` → row_locator for "期末基金份额" row, evidence_role=share_ending

---

## Residual Impact on Blocker Status

| Group | Fixable? | After Fix Status | Blocker Resolved? |
|---|---|---|---|
| credit_risk | Yes | accepted | Contributes to unblock |
| drawdown_stress | No (genuine data absence) | weak (unchanged) | Remains in missing issue |
| redemption_share_pressure | Yes | accepted | Contributes to unblock |

After applying the recommended rule adjustments for credit_risk and redemption_share_pressure:

- Satisfied groups: 6 of 7 (duration_rate_risk, credit_risk, leverage_liquidity, asset_allocation_holdings_mix, redemption_share_pressure, convertible_bond_equity_exposure)
- Weak groups: 1 of 7 (drawdown_stress)
- Contract status: `partial` (not `satisfied`)
- `bond_risk_evidence_missing` would still be emitted, but ONLY for `drawdown_stress`

The blocker CANNOT be fully resolved by rule adjustment alone because `drawdown_stress` lacks quantitative evidence in this annual report. A separate contract decision would be needed to either accept qualitative evidence for this group or designate it as non-blocking for bond funds.

---

## Validation Evidence

All data in this report was obtained through the following command:

```python
import asyncio
from fund_agent.fund.documents import FundDocumentRepository
from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence

repo = FundDocumentRepository()
report = asyncio.get_event_loop().run_until_complete(repo.load_annual_report("006597", 2024))
result = extract_bond_risk_evidence(report, "bond_fund")
```

No direct PDF/cache access, no source helper calls, no network operations outside `FundDocumentRepository`.

## Completion Statement

Self-check: pass. All three unsatisfied groups investigated. Root causes identified with same-source evidence. Real annual report evidence located for two groups. Honest data absence confirmed for one group. No code, test, or configuration file was modified.
