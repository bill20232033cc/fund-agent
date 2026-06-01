# Section2 Profile Ending-Share Cross-Check Unit Suffix Repair Plan

> Date: 2026-05-28
> Role: Gateflow controller, not implementation worker
> Gate: `section2 profile ending-share cross-check repair gate`
> Classification: `fast_path`
> Status: plan ready for review

## Classification Justification

`fast_path` — the fix is a single-site parse resilience change (strip `份` suffix before Decimal parsing) that:
- Does not change public contract, schema, quality gate semantics, final judgment, Host/Agent/dayu, or external source strategy.
- Does not weaken fail-closed behavior; a value that fails Decimal parsing after suffix stripping still returns None.
- Does not change any acceptance path or arithmetic.
- Is a docs-only-adjacent low-risk fix: adding a known unit-suffix strip to an existing parse helper.

If either reviewer disagrees, escalate to `standard`.

## Worker Boundary

- This artifact is planning-only.
- Do not start or use gateflow.
- Do not modify production code, tests, reports, score, quality gate, schema, README, control doc, golden fixtures, Service/UI/Host/Agent/dayu, Git state, remote branches, PRs, or releases.
- The implementation worker may edit only:
  - `fund_agent/fund/extractors/bond_risk_evidence.py`
  - `tests/fund/extractors/test_bond_risk_evidence.py`
  - follow-up `docs/reviews/` implementation/review artifacts

## Dirty Scope Classification

Current workspace state from `git status --short` and `git branch --show-current`:
- Branch: `codex/local-reconciliation`
- Modified (dirty, uncommitted): `fund_agent/fund/extractors/bond_risk_evidence.py`, `tests/fund/extractors/test_bond_risk_evidence.py`
- These are the implementation baseline from the prior `redemption share class column alignment repair gate`, which was blocked at validation failure (`share_class_ending_cross_check_missing`).
- Untracked review artifacts from prior gates are present; none should be staged in this gate.

**Reusable**: All code from the prior column alignment gate (unlabeled positional alignment, §2 mapping, §10 table selection, row matching, arithmetic checks, cross-check skeleton, and all tests).

**To repair**: Only the `份` unit-suffix parse failure in `_parse_plain_decimal` / `_parse_share_decimal`.

**Non-goal**: No changes to explicit header path, row-label precondition, arithmetic, aggregate, anchors, drawdown, credit_risk, score, gate, schema, Service/UI/Host/Agent/dayu, golden, PR, push, merge, release.

## Root Cause Evidence

### Real §2 Profile Table Structure (006597 / 2024, page 5, table 0)

Diagnosed via `FundDocumentRepository`:

```
Headers: ('基金名称', '国泰利享中短债债券型证券投资基金', '', '', '')

row[9]:  ('下属分级基金的基金简称',           '国泰利享中\n短债债券A', '国泰利享中\n短债债券C', '国泰利享中\n短债债券E', '国泰利享中\n短债债券F')
row[10]: ('下属分级基金的交易代码',           '006597',              '006598',              '014217',              '022176')
row[11]: ('报告期末下属分级基金的份\n额总额', '5,711,224,267\n.09份', '4,760,029,01\n5.27份', '25,795,859.1\n2份', '52,531,021.8\n4份')
```

三行语义：
- row 9: 下属分级基金的基金简称 → A/C/E/F 份额类别标签列
- row 10: 下属分级基金的交易代码 → 006597/006598/014217/022176 基金代码列
- row 11: 报告期末下属分级基金的份额总额 → 各类别期末份额数值（带 `份` 单位后缀）

### Cross-Check Logic Current Expectation

`_share_class_ending_cross_check_from_profile_tables()` expects:
1. Same-table three rows found by `_profile_cross_check_rows()` — uses `_compact_text(row[0])` substring match against keywords `下属分级基金的基金简称` / `下属分级基金的交易代码` / `报告期末下属分级基金的份额总额`
2. `_share_class_labels_from_profile_name_cells()` extracts A/C/E/F from name cells
3. `fund_codes` extracted from code row cells via `re.fullmatch(r"\d{6}", ...)`
4. `class_labels == mapping.class_labels and fund_codes == mapping.fund_codes`
5. `_profile_ending_values_by_class()` parses ending values via `_parse_share_decimal()`

### Why Real §2 Table Is Not Matched

Steps 1–4 all succeed for the real table. Step 5 fails:

```
_parse_share_decimal('5,711,224,267\n.09份')
  → _parse_plain_decimal('5,711,224,267\n.09份', dash_as_zero=True)
    → _compact_text → '5,711,224,267.09份'
    → replace(',', '') → '5711224267.09份'
    → Decimal('5711224267.09份') → InvalidOperation ('份' is not a valid Decimal char)
    → return None
```

`_profile_ending_values_by_class` receives `None` for any cell → returns `None` → `_share_class_ending_cross_check_from_profile_tables` skips the table → no cross-check found → `share_class_ending_cross_check_missing`.

### Why §10 Values Are Unaffected

Real §10 share-change table cells are pure numbers (e.g., `"7,699,969,800.13"`) without unit suffixes. Only §2 profile table cells carry `份` suffixes because the profile table is a summary disclosure table, not a numeric data table.

## Repair Design

### Change: Strip `份` Unit Suffix in `_parse_plain_decimal`

**File**: `fund_agent/fund/extractors/bond_risk_evidence.py`

Add a constant:

```python
_DECIMAL_UNIT_SUFFIXES: Final[tuple[str, ...]] = ("份",)
```

In `_parse_plain_decimal`, after comma removal and before Decimal parsing, strip known unit suffixes:

```python
for suffix in _DECIMAL_UNIT_SUFFIXES:
    if normalized.endswith(suffix):
        normalized = normalized[:-len(suffix)]
        break
```

This is placed after `replace(",", "")` and before `Decimal(normalized)`.

### Rationale

- `份` is the standard Chinese unit for fund shares (份额). §2 profile tables commonly append it to ending-share values.
- Stripping known suffixes is safer than stripping all non-numeric characters (which could mask real parse failures).
- The suffix tuple is extensible for future unit suffixes (`元`, `万元`) without changing parse logic.
- Fail-closed preserved: if stripping `份` still yields an invalid Decimal, `InvalidOperation` still returns None.

### No Other Changes

- `_parse_share_decimal` calls `_parse_plain_decimal(value, dash_as_zero=True)` — inherits the fix automatically.
- No changes to `_profile_ending_values_by_class`, `_profile_cross_check_rows`, `_share_class_ending_cross_check_from_profile_tables`, or `_validate_share_class_ending_cross_check`.
- No changes to §10 alignment, row matching, arithmetic, aggregate, anchors, or metric formatting.

## Cross-Check Comparison Rules (Unchanged)

- §2 ending per class vs §10 ending per class compared via `_decimal_close(Decimal, Decimal)` with tolerance `Decimal("0.01")`.
- Missing class in cross-check → `share_class_ending_cross_check_missing`.
- Mismatch (diff > 0.01) → `share_class_ending_cross_check_mismatch`.
- Both are fail-closed; no guessing.

## Fail-Closed Behavior (Unchanged)

| Scenario | na_reason |
|---|---|
| No §2 table with all three rows | `share_class_ending_cross_check_missing` |
| Class labels or fund codes don't match mapping | `share_class_ending_cross_check_missing` |
| Ending values can't be parsed (even after suffix strip) | `share_class_ending_cross_check_missing` |
| Ending values parse but don't match §10 within 0.01 | `share_class_ending_cross_check_mismatch` |

## Required Tests

File: `tests/fund/extractors/test_bond_risk_evidence.py`

### 1. Real-Shape §2 Profile Cross-Check With `份` Suffix

Use `_real_profile_cross_check_table()` with default ending_row containing `份` suffix values matching the real parsed shape:

```python
ending_row=(
    "报告期末下属分级基金的份额总额",
    "5,711,224,267.09份",
    "4,760,029,015.27份",
    "25,795,859.12份",
    "52,531,021.84份",
)
```

Assert cross-check passes and `redemption_share_pressure.status == "accepted"`.

### 2. `份` Suffix With Newlines And Commas

Use cells like `"5,711,224,267\n.09份"` (real parsed shape with embedded newlines). Assert parsing succeeds.

### 3. Suffix Strip Does Not Mask Invalid Values

Use a cell like `"N/A份"` — assert `_parse_share_decimal` still returns None after stripping `份` because `"N/A"` is not a valid Decimal.

### 4. Existing Tests Still Pass

All existing cross-check mismatch/missing tests produce the same na_reason. Explicit header path tests unaffected.

### 5. Real Unlabeled Alignment End-to-End With Suffixed §2

Modify `test_redemption_share_pressure_aligns_real_unlabeled_section_ten_by_section_two_order` (or add a variant) where the profile cross-check table ending_row uses `份`-suffixed values. This is the regression test for the real 006597 failure.

## Hard Constraints (Reaffirmed)

- 不得只取 A 类代表总体。
- 不得用 §2 单行或错误行替代 A/C/E/F all-class aggregate。
- 不得把 cross-check 缺失改成通过（只能修复 parse，不能跳过 cross-check）。
- 不得修改 score policy / quality gate 来掩盖 extractor 失败。
- 不得绕过 `FundDocumentRepository` 访问生产年报/PDF/cache。
- 不得削弱 FQ0-FQ6。
- 不得处理 drawdown、NAV-derived evidence、QDII、FOF、110020、golden-readiness、release、Host/Agent/dayu。
- 显式参数不得塞进 `extra_payload`。
- 保持 UI -> Service -> Host -> Agent 边界。

## Validation Plan

Implementation worker or validation worker should run:

```bash
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; repo = FundDocumentRepository(); report = asyncio.run(repo.load_annual_report("006597", 2024, force_refresh=True)); print(report.key.fund_code, report.key.year, len(report.sections), len(report.tables))'
uv run fund-analysis extraction-snapshot --run-id bond-risk-crosscheck-suffix-006597-2024-20260528 --fund-code 006597 --report-year 2024 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528
uv run fund-analysis quality-gate --score-path reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json --output-dir reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528
```

Expected real validation:
- `redemption_share_pressure.status == "accepted"`
- `bond_risk_satisfied_groups` includes `redemption_share_pressure`
- `bond_risk_ambiguous_groups` does NOT include `redemption_share_pressure`
- `drawdown_stress` remains weak
- Score `missing_evidence_groups` drops to `["drawdown_stress"]`
- Quality gate remains `warn`
- No FQ0-FQ6 semantic change

## Stop Conditions

- `份` suffix stripping introduces false-positive parsing of invalid values.
- Fix requires changes beyond `_parse_plain_decimal` / `_parse_share_decimal`.
- Real validation still shows `share_class_ending_cross_check_missing` after fix.
- Any test regression in explicit header path, arithmetic, anchors, credit_risk, or drawdown.
- Scope creep into schema, score, quality gate, Service/UI/Host/Agent/dayu, golden, or release.
