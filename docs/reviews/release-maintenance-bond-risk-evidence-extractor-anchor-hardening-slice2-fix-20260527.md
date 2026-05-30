# Bond Risk Evidence Extractor / Anchor Hardening Slice 2 Fix

> Date: 2026-05-28
> Role: fix worker
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Slice: Slice 2 accepted-finding fix before re-review
> Status: verified complete, not staged

## Worker Self-Check

### Before Start

- Self-check: pass
- Role confirmed: fix worker only, not controller.
- Current gate confirmed: Slice 2 accepted-finding fix for `bond_risk_evidence.v1`.
- Workflow boundary confirmed: no workflow command, no skill, no review, no staging, no commit, no push, no PR, no golden promotion.
- Allowed files confirmed:
  - `fund_agent/fund/extractors/bond_risk_evidence.py`
  - `tests/fund/extractors/test_bond_risk_evidence.py`
  - this fix artifact

### Before Completion

- Self-check: pass
- All five accepted fixes implemented within allowed files.
- No files outside allowed scope touched.
- Unrelated dirty/untracked files preserved.

## Changed Files

- `fund_agent/fund/extractors/bond_risk_evidence.py`
  - Removed dead `or _MISSING_NOTE` fallback in `_field_note` (line 1354).
  - Tightened `duration_rate_risk` keyword matching: `("利率风险",)` now requires co-occurrence with `"管理"`, `"控制"`, or `"调整"`.
- `tests/fund/extractors/test_bond_risk_evidence.py`
  - Added `test_none_fund_type_returns_missing_without_scanning_group_extractors`.
  - Added `test_partial_extraction_with_mixed_groups_produces_estimated_mode`.
  - Added `test_incomplete_seven_group_coverage_does_not_masquerade_as_complete`.
  - Added `test_non_zero_equity_row_does_not_produce_accepted_absence`.
  - Added `test_boilerplate_rate_risk_text_alone_does_not_satisfy_duration_group`.
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-fix-20260527.md`
  - This handoff artifact.

## Accepted Findings Fixed

### Fix 1: dedicated test for `classified_fund_type=None`

**Finding**: F5 (DS review) / R4 (DS review) — code correct but plan-explicitly-required `None` case lacked dedicated test.

**Fix**: Added `test_none_fund_type_returns_missing_without_scanning_group_extractors` with `monkeypatch` guard proving no group extractor is called. Passes `None` directly and asserts `value=None`, `extraction_mode="missing"`, `note="not_applicable_non_bond_fund"`.

### Fix 2: focused tests for weak/partial path and extraction_mode behavior

**Finding**: Test gap noted by both reviewers — no test verifies partial extraction scenario where `contract_status="partial"` and `extraction_mode="estimated"`.

**Fix**: Added two tests:
- `test_partial_extraction_with_mixed_groups_produces_estimated_mode`: credit table + duration text accepted, five groups missing. Asserts `contract_status="partial"`, `extraction_mode="estimated"`, fewer than seven satisfied groups, and explicitly asserts `!= "direct"` and `!= "satisfied"`.
- `test_incomplete_seven_group_coverage_does_not_masquerade_as_complete`: only weak drawdown text present, no satisfied groups. Asserts extraction_mode is not `"direct"` and contract_status is not `"satisfied"`.

### Fix 3: negative absence-value test

**Finding**: Test gap (DS review §Test Gaps #4, MiMo review §Test Gaps #3) — no test verifies `_row_has_absence_value` with non-absence values.

**Fix**: Added `test_non_zero_equity_row_does_not_produce_accepted_absence`. Creates a table with row `("股票", "100,000.00", "5.00%")` and asserts `convertible_bond_equity_exposure` group status is `"missing"`, not `"accepted_absence"`.

### Fix 4: remove dead fallback in `_field_note`

**Finding**: F6 (DS review) — `or _MISSING_NOTE` suffix is unreachable because the formatted string always starts with `contract_id=...`.

**Fix**: Removed `or _MISSING_NOTE` from `_field_note` return statement.

### Fix 5: tighten duration_rate_risk text acceptance

**Finding**: F3 (DS review) — single keyword `"利率风险"` produces `accepted` on mandatory boilerplate risk disclosure present in virtually every bond fund annual report.

**Fix**: Changed `keyword_groups` from `(("久期",), ("利率风险",))` to `(("久期",), ("利率风险", "管理"), ("利率风险", "控制"), ("利率风险", "调整"))`. Now `"利率风险"` alone does not satisfy; it must co-occur with a management action word. `"久期"` alone remains accepted as it is specific to duration strategy and not mandatory boilerplate. Added `test_boilerplate_rate_risk_text_alone_does_not_satisfy_duration_group` proving bare "本基金面临利率风险。" produces `missing`, not `accepted`.

## Deferred Residuals (unchanged)

- ParsedTable has no `section_id`; table anchors carry rule-assigned section ids. Recorded as residual with Slice 6/real-report validation owner. No parser schema change in this slice.
- ExtractionMode lacks literal `partial`; existing compatible mapping (`estimated`) retained. Residual owner Slice 4 integration.
- No edits to `data_extractor`, `snapshot`, `score`, `quality gate`, `design/control docs`, `README`, `fixtures`, `PDF/cache/source code`.

## Validation Results

- `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q`
  - Passed: **28 passed in 0.77s** (was 23, +5 new tests)
- `uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py`
  - Passed: **All checks passed!**

## Stop Status

- No stop condition triggered.
- All five accepted fixes implemented within allowed scope.
- No validation failures.
