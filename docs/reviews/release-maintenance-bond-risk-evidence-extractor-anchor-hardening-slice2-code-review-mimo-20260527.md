# Bond Risk Evidence Extractor / Anchor Hardening Slice 2 Code Review

> Date: 2026-05-28
> Role: code review worker
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Slice: Slice 2 Extractor only
> Reviewer: MiMo (mimo-v2.5-pro)
> Status: **PASS**

## Worker Self-Check

### Before Start

- Self-check: pass
- Role confirmed: code review worker only, not controller.
- Current gate confirmed: Slice 2 code review for `bond_risk_evidence.v1` extractor.
- Workflow boundary confirmed: no workflow command, no skill, no implementation, no staging, no commit, no push, no PR, no golden promotion.
- Allowed write path confirmed: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-code-review-mimo-20260527.md`.

### Before Completion

- Self-check: pass
- All review criteria checked against accepted plan.
- Evidence-based findings with code-line references.
- Blocking findings: none.

## Review Scope

| File | Review Status |
|---|---|
| `fund_agent/fund/extractors/bond_risk_evidence.py` | Reviewed |
| `fund_agent/fund/extractors/__init__.py` | Reviewed |
| `tests/fund/extractors/test_bond_risk_evidence.py` | Reviewed |

## Plan Conformance Check

### Non-bond early return before scanning

**PASS.** `bond_risk_evidence.py:125-131` — `classified_fund_type != "bond_fund"` returns `ExtractedField(value=None, anchors=(), extraction_mode="missing", note="not_applicable_non_bond_fund")`. Verified with `None`, empty string, and `"active_fund"` — all return missing without invoking group extractors. Test `test_non_bond_type_returns_missing_without_scanning_group_extractors` uses `monkeypatch` to fail if any group extractor is called.

### Seven group behavior

**PASS.** All seven group extractors implemented in `bond_risk_evidence.py:153-514`:
- `duration_rate_risk`: text match → accepted/qualitative_direct; missing when no match.
- `credit_risk`: table row → accepted/quantitative_direct; text-only → weak; missing when neither.
- `leverage_liquidity`: repo table → accepted/quantitative_direct; leverage/liquidity text → weak; missing when neither.
- `asset_allocation_holdings_mix`: table row → accepted/quantitative_direct; missing when no match.
- `drawdown_stress`: max-drawdown table → accepted/quantitative_direct; control text → weak; missing when neither.
- `redemption_share_pressure`: share-change table with disambiguation → accepted; ambiguous without disambiguation; missing when no table.
- `convertible_bond_equity_exposure`: explicit absence rows → accepted_absence; missing when no rows.

### Stable anchors and validator use

**PASS.** `bond_risk_evidence.py:712` — anchor format `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` matches plan spec. Ordinal is deterministic, starting from 1, ordered by `(section_id, page_number, table_id, row_locator, evidence_role)` at line 699-708. `validate_bond_risk_evidence_value(value)` called at line 143 before returning non-missing values.

### Drawdown-control text remains weak

**PASS.** `bond_risk_evidence.py:378-393` — `_find_text_match` with keyword groups `("控制回撤",)` and `("回撤",)` produces `status="weak"`, `strength="qualitative_control_intent"`, `measurement_kind="control_intent"`. Test `test_drawdown_control_text_alone_is_weak` confirms weak-only behavior. The plan constraint is upheld: qualitative drawdown-control intent is not promoted to max-drawdown or volatility evidence.

### Leverage strategy text remains weak

**PASS.** `bond_risk_evidence.py:286-302` — leverage/liquidity text without repo table produces `status="weak"`, `strength="qualitative_direct"`, `measurement_kind="strategy_text"`, `na_reason="repo_or_liquidity_table_not_found"`. Test `test_flexible_leverage_strategy_text_alone_is_weak` confirms. Test `test_repo_table_row_plus_liquidity_text_satisfies_leverage_liquidity` confirms accepted path requires actual repo table row.

### Share-class disambiguation correctness

**PASS.** `bond_risk_evidence.py:954-992` — `_select_share_change_column` resolves value column by: (1) single code match in header; (2) single value column; (3) §2 code/name-to-class evidence. Returns `None` (→ ambiguous) when multiple code matches or no disambiguation evidence. Tests `test_multi_share_class_share_change_selects_target_class_when_disambiguated` and `test_ambiguous_multi_share_class_share_change_stays_ambiguous` confirm both paths.

### Explicit absence → accepted_absence

**PASS.** `bond_risk_evidence.py:486-514` — `_absence_row_anchor_draft` checks `_row_has_absence_value` (line 1189-1206) for `-`, `0`, `0.00`, etc. Produces `status="accepted_absence"`, `strength="quantitative_absence"`, `measurement_kind="explicit_absence"`. Tests `test_convertible_and_equity_dash_rows_become_accepted_absence` and `test_explicit_absence_convertible_equity_record_is_accepted` confirm.

### Ambiguity/missing fail closed

**PASS.** Missing evidence → `status="missing"`, `strength="missing"`. Ambiguous share-class → `status="ambiguous"`, `strength="ambiguous"`. Neither satisfies required groups. `contract_status` is `"missing"` when all groups are missing, `"partial"` when any group is satisfied/weak/ambiguous. Edge case: bond_fund with no tables produces all seven groups missing, `contract_status="missing"`, `extraction_mode="missing"`.

### No bundle/snapshot/score changes

**PASS.** Only three files changed:
- `bond_risk_evidence.py` (new extractor)
- `__init__.py` (exports)
- `test_bond_risk_evidence.py` (tests)

Verified `data_extractor.py` has no `bond_risk_evidence` field on `StructuredFundDataBundle`. No changes to `extraction_snapshot.py` or `extraction_score.py`.

### No repository/PDF/cache/source helper access

**PASS.** `bond_risk_evidence.py:1-6` docstring explicitly states: "不访问文档仓库、PDF 缓存或来源 helper". Function signature `extract_bond_risk_evidence(report: ParsedAnnualReport, classified_fund_type: str | None)` receives already-parsed report. No imports of `FundDocumentRepository`, PDF, cache, or download helpers.

### Tests prove required behavior

**PASS.** 23 tests pass, covering all eight required plan scenarios:

| Plan requirement | Test | Status |
|---|---|---|
| Table-backed credit risk accepted with row-level anchors | `test_table_backed_credit_risk_is_accepted_with_row_level_anchor` | ✅ |
| Flexible leverage strategy text alone is weak | `test_flexible_leverage_strategy_text_alone_is_weak` | ✅ |
| Repo/liquidity table row + liquidity text satisfies leverage | `test_repo_table_row_plus_liquidity_text_satisfies_leverage_liquidity` | ✅ |
| Drawdown-control text alone is weak | `test_drawdown_control_text_alone_is_weak` | ✅ |
| Multi-share-class selects target class when disambiguated | `test_multi_share_class_share_change_selects_target_class_when_disambiguated` | ✅ |
| Ambiguous share class stays ambiguous | `test_ambiguous_multi_share_class_share_change_stays_ambiguous` | ✅ |
| Convertible/equity explicit `-` rows → accepted_absence | `test_convertible_and_equity_dash_rows_become_accepted_absence` | ✅ |
| Non-bond returns missing, no group scan | `test_non_bond_type_returns_missing_without_scanning_group_extractors` | ✅ |

Full fund suite regression: **687 passed in 1.33s** — zero regressions.

## Accepted-Worthy Findings

### FINDING-1: `extraction_mode="estimated"` for partial status (accepted, documented residual)

**Location:** `bond_risk_evidence.py:1329`

**Evidence:** `_extraction_mode` maps `contract_status="partial"` to `extraction_mode="estimated"`. The plan specifies `extraction_mode="partial"` for partial contract status. However, `ExtractedField.extraction_mode` is `Literal["direct", "derived", "estimated", "missing"]` (models.py:10) — `"partial"` is not a valid mode in the Slice 1 model.

**Decision:** Accepted. The implementation artifact at line 108 explicitly documents this as a known limitation: "the plan's 'partial' mode requires a later model/integration slice if desired." The `"estimated"` mode is the closest available semantic match. No model contract is violated.

### FINDING-2: `_first_row_anchor_draft` searches all tables regardless of section (accepted, residual risk)

**Location:** `bond_risk_evidence.py:795-807`

**Evidence:** `_first_row_anchor_draft` iterates `report.tables` without filtering by `section_id`. The `section_id` parameter is passed through to the anchor draft, but table selection is not section-scoped. If a table in an unexpected section (e.g., §9 holder structure) contains both `table_keywords` and `row_keywords`, it would match.

**Decision:** Accepted as residual risk. Current synthetic test tables are §8/§10 scoped. The broad keyword set (`"债券"`, `"回购"`, `"回撤"`, `"信用"` + `"评级"`) is specific enough that cross-section false positives are unlikely with real annual reports. A future integration slice with real `006597` tables should verify section-scoped matching if needed.

### FINDING-3: `asset_allocation_holdings_mix` table keyword "债券" is broad (accepted, residual risk)

**Location:** `bond_risk_evidence.py:320-327`

**Evidence:** `table_keywords=("债券",)` and `row_keywords=("债券",)` would match any §8 table row containing "债券" — including top-holdings tables where "债券" appears in a bond name. The plan lists "top five bonds and top ABS holdings" as accepted evidence, so matching top-holdings rows with "债券" is technically within scope. However, a row like `("某债券基金名称", "5.00%")` in a non-allocation context could produce a misleading anchor.

**Decision:** Accepted as residual risk. Tested: a top-holdings table with "债券" in headers but "国债" in row data correctly returns missing (row-level keyword not found). The risk is low because real row content would need "债券" specifically in the row cells, not just headers.

## Residual Risks

1. **`extraction_mode` gap**: `"partial"` mode not available in Slice 1 model; `"estimated"` used as closest match. Requires later model/integration slice to add `"partial"` to `ExtractionMode` if desired.

2. **Table section scoping**: `_first_row_anchor_draft` does not filter tables by `section_id`. Cross-section false positives are unlikely but not impossible with real reports. Integration slice should verify.

3. **Real `006597` leverage/repo locators**: The plan notes that precise page/table/row anchors for `006597` leverage/liquidity evidence need normalization. This slice uses synthetic fixtures; real-report validation is a later slice concern.

4. **`drawdown_stress` remains weak for `006597`**: The plan confirms that current `006597` annual report evidence for drawdown is qualitative control-intent only. This group will remain in `weak_group_ids` and keep `bond_risk_evidence_missing` active for `drawdown_stress`.

5. **Broad keyword matching**: Keywords like `"回撤"` (line 382) and `"杠杆"` (line 290) are broad and could match in unintended contexts. Both paths produce `weak` status only, limiting false-positive impact.

## Test Gaps

1. **No partial-extraction test**: No test verifies a scenario where exactly 3-4 groups are satisfied and the rest are missing/weak, confirming `contract_status="partial"` and `extraction_mode="estimated"`.

2. **No test for `_find_text_match` returning match in first section only**: Tests verify text matching works but don't explicitly verify that section priority (§2 before §4 before §5) produces the expected first-match section.

3. **No test for table keyword match without row keyword match**: The `_table_contains_all` check passes but `_row_anchor_draft` finds no matching row — this path is implicitly tested by `test_top_holdings_with_债券_in_header_only_returns_missing` (manual verification) but not in the automated suite.

4. **No negative test for `_row_has_absence_value` with non-absence values**: A row like `("股票", "100,000.00", "5.00%")` should NOT be treated as absence. The function correctly handles this, but no explicit test exists.

## Conclusion

**PASS.** No blocking findings. The Slice 2 extractor implementation correctly follows the accepted plan: non-bond early return, seven group extractors with specified status/strength/measurement_kind, stable anchor IDs, validator invocation, conservative ambiguity handling, no bundle/snapshot/score changes, no repository/PDF/cache access. All 23 tests pass with zero regressions across the full fund suite (687 tests). Four accepted-worthy findings documented as residual risks for later integration slices.

## Artifact Path

`docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-code-review-mimo-20260527.md`
