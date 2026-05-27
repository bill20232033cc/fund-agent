# Bond Risk Evidence Extractor / Anchor Hardening — Slice 2 Re-Review (DS)

> Date: 2026-05-28
> Role: re-review worker
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Slice: Slice 2 re-review after accepted-finding fix
> Fix artifact: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-fix-20260527.md`
> Review scope:
> - `fund_agent/fund/extractors/bond_risk_evidence.py`
> - `tests/fund/extractors/test_bond_risk_evidence.py`
> - `fund_agent/fund/extractors/__init__.py`

## Worker Self-Check (Before Review)

- Self-check: pass
- Role confirmed: re-review worker only, not controller. No implementation, no edit, no commit, no push, no PR, no golden promotion.
- Allowed write path confirmed: only this re-review artifact.
- All required source documents read: AGENTS.md, plan, slice2 implementation, DS review, MiMo review, fix artifact.
- All three target files read in full.
- Validation run independently.

## Validation Summary

| Check | Result |
|---|---|
| `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q` | 28 passed in 0.50s |
| `uv run ruff check` (all 3 target files) | All checks passed |

## Re-Review Question 1: Were the accepted fixes closed?

### Fix 1: `classified_fund_type=None` early return test

**Closed.** Test `test_none_fund_type_returns_missing_without_scanning_group_extractors` at test line 381–393. Passes `None` directly, uses `monkeypatch` guard proving no group extractor is called. Asserts `value=None`, `extraction_mode="missing"`, `note="not_applicable_non_bond_fund"`. Implementation at line 125 (`classified_fund_type != _BOND_FUND_TYPE` → `None != "bond_fund"` → early return) is trivially correct.

### Fix 2: partial/estimated tests

**Closed.** Two tests added:

- `test_partial_extraction_with_mixed_groups_produces_estimated_mode` (test line 396–420): credit table + duration text accepted, five groups missing. Asserts `contract_status="partial"`, `extraction_mode="estimated"`, fewer than seven satisfied, and explicitly asserts `!= "direct"` and `!= "satisfied"`.
- `test_incomplete_seven_group_coverage_does_not_masquerade_as_complete` (test line 423–435): only weak drawdown text present, no satisfied groups. Asserts `extraction_mode != "direct"`, `contract_status != "satisfied"`.

Both tests exercise the partial-contract path that was previously untested.

### Fix 3: non-zero absence negative test

**Closed.** `test_non_zero_equity_row_does_not_produce_accepted_absence` (test line 438–459). Creates table with row `("股票", "100,000.00", "5.00%")`. Asserts `convertible_bond_equity_exposure` group status is `"missing"` (not `"accepted_absence"`), and group is not in `satisfied_group_ids`. The `_row_has_absence_value` function (line 1189–1206) correctly returns `False` for `"100,000.00"`.

### Fix 4: dead fallback removal

**Closed.** `_field_note` at line 1347–1354 no longer has `or _MISSING_NOTE`. The formatted string always starts with `contract_id=...` and can never be falsy. Dead code removed cleanly. No functional change.

### Fix 5: duration/rate boilerplate tightening

**Closed.** `_extract_duration_rate_risk` at line 170 now uses:
```python
keyword_groups=(("久期",), ("利率风险", "管理"), ("利率风险", "控制"), ("利率风险", "调整"))
```

Previously: `(("久期",), ("利率风险",))` — bare "利率风险" alone produced `accepted`.

Now: "利率风险" must co-occur in the same line with "管理", "控制", or "调整". "久期" alone remains accepted (duration-specific, not mandatory boilerplate).

Test `test_boilerplate_rate_risk_text_alone_does_not_satisfy_duration_group` (test line 462–475) proves bare "本基金面临利率风险。" produces `status="missing"`, not `accepted`.

**Minor residual note:** Substring matching means "管理人" (fund manager) contains "管理", so text like "本基金面临利率风险，管理人将密切关注" would still match `("利率风险", "管理")`. This is a known limitation of substring-based keyword matching, not a regression. The fix is a meaningful improvement — bare "利率风险" boilerplate is now blocked. Full semantic disambiguation (管理 as verb vs 管理人 as noun) requires NLP beyond this slice's scope.

**Verdict: All five accepted fixes are closed.** No partial or skipped fixes.

---

## Re-Review Question 2: Did the fix preserve hard constraints?

| Constraint | Status | Evidence |
|---|---|---|
| No `FundDocumentRepository` bypass in extractor | **Pass** | `bond_risk_evidence.py` imports only `ParsedAnnualReport`, `ParsedTable` from `documents.models`. No import of `FundDocumentRepository`, PDF, cache, or download helpers. |
| No direct PDF/cache/source helper | **Pass** | Extractors consume only already-parsed `ParsedAnnualReport`. |
| No FQ gate weakening | **Pass** | Extractor has no FQ0–FQ6 code. Score/quality-gate files untouched. |
| No weak qualitative → strong quantitative promotion | **Pass** | All group status/strength mappings unchanged by fix: duration → `qualitative_direct`; drawdown weak → `qualitative_control_intent`; leverage weak → `qualitative_direct` with `na_reason`. |
| No `extra_payload` | **Pass** | All parameters explicit in function signatures. No `extra_payload` dict or free-form payload. |
| No data_extractor/snapshot/score/golden changes | **Pass** | Only 3 files touched: `bond_risk_evidence.py`, `__init__.py`, `test_bond_risk_evidence.py`. Verified no changes to `data_extractor.py`, `extraction_snapshot.py`, `extraction_score.py`, golden/baseline fixtures. |
| `classified_fund_type != "bond_fund"` early return | **Pass** | Line 125 unchanged by fix. Returns missing/not-applicable without scanning. |
| Stable anchor format `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` | **Pass** | Line 712 unchanged by fix. Ordinal deterministic by `(section_id, page_number, table_id, row_locator, evidence_role)` at line 699–708. |
| Validator called before non-missing return | **Pass** | Line 143 unchanged. `validate_bond_risk_evidence_value(value)` before `ExtractedField` construction. |
| `required_evidence_groups` always all seven ids | **Pass** | `BOND_RISK_EVIDENCE_GROUP_IDS` constant unchanged. |
| `satisfied/missing/weak/ambiguous_group_ids` derived from statuses | **Pass** | `_build_value` lines 533–536 unchanged. |

**Verdict: All hard constraints preserved.** No regression introduced by fix.

---

## Re-Review Question 3: Are there new blocking findings introduced by fix?

**No new blocking findings.**

Detailed audit of each changed code path:

### `_field_note` dead code removal (line 1347–1354)

Removal of unreachable `or _MISSING_NOTE`. No functional change. The `_MISSING_NOTE` constant (line 37) is now unused — but constants are harmless and removing it would touch scope beyond the fix. Not blocking.

### Duration keyword tightening (line 170)

Changed from `(("久期",), ("利率风险",))` to `(("久期",), ("利率风险", "管理"), ("利率风险", "控制"), ("利率风险", "调整"))`.

- Existing test `test_table_backed_credit_risk_is_accepted_with_row_level_anchor` still passes (28/28) — no regression on credit risk path.
- New test `test_boilerplate_rate_risk_text_alone_does_not_satisfy_duration_group` proves boilerplate is blocked.
- The `_find_text_match` function unchanged — only keyword_groups argument changed. No change to matching logic.

**Substring limitation (not blocking):** "管理" appears as substring of "管理人" (fund manager). Text "管理人将密切关注利率风险" would match `("利率风险", "管理")` because compacted text contains both substrings. This is a pre-existing limitation of substring matching, not a fix-introduced regression. The fix is strictly better than before: bare "利率风险" is now blocked. Defer full semantic disambiguation to future slice with NLP/LLM assistance.

### New tests (5 added)

All 5 new tests pass. No test modifies production behavior — they only assert existing behavior. No flakiness, no global state pollution, no monkeypatch leakage beyond test scope.

**Verdict: PASS. No new blocking findings.**

---

## Re-Review Question 4: Confirm deferred residuals are still correctly deferred

| Residual | Owner | Still Deferred? | Evidence |
|---|---|---|---|
| `ParsedTable` has no `section_id`; table anchors carry rule-assigned section ids | Slice 6 / real-report validation | **Yes** | No parser schema change. `_first_row_anchor_draft` still iterates all `report.tables` without section filtering (line 795). Section attribution remains caller-assigned. |
| `ExtractionMode` lacks literal `"partial"` | Slice 4 (snapshot integration) | **Yes** | `_extraction_mode` at line 1329 still maps `"partial"` → `"estimated"`. No `ExtractionMode` literal change. |
| Broader table keyword/section hardening | Later slices / real-report validation | **Yes** | No changes to table-keyword filtering, section scoping, or keyword specificity beyond the duration fix (which addresses a different concern). |
| Real `006597` leverage/repo locator normalization | Slice 6 (real report path) | **Yes** | This slice uses synthetic fixtures only. No real-report table normalization. |
| `drawdown_stress` remains weak for real `006597` | Slice 6 | **Yes** | Qualitative control-intent path unchanged at lines 378–393. |

**Verdict: All deferred residuals remain correctly deferred.** No deferred item was accidentally resolved or regressed.

---

## Per-Group Behavior Re-Audit (Post-Fix)

| Group | Status | Strength | Fix Impact |
|---|---|---|---|
| `duration_rate_risk` | accepted (久期 or 利率风险+管理/控制/调整) | qualitative_direct | **Tightened** — bare 利率风险 now → missing |
| `credit_risk` | accepted (table) / weak (text) | quantitative_direct / qualitative_direct | Unchanged |
| `leverage_liquidity` | accepted (repo table) / weak (text only) | quantitative_direct / qualitative_direct | Unchanged |
| `asset_allocation_holdings_mix` | accepted (table) / missing | quantitative_direct | Unchanged |
| `drawdown_stress` | accepted (metric table) / weak (text) | quantitative_direct / qualitative_control_intent | Unchanged |
| `redemption_share_pressure` | accepted (disambiguated) / ambiguous | quantitative_direct / ambiguous | Unchanged |
| `convertible_bond_equity_exposure` | accepted_absence / missing | quantitative_absence | Unchanged |

Only `duration_rate_risk` behavior changed — tightened as intended.

---

## Test Coverage Summary (Post-Fix)

28 tests (was 23, +5):

| Category | Count | Tests |
|---|---|---|
| Slice 1 model contract | 13 | Complete value, missing anchor, incomplete groups, duplicate ID, derived ID mismatch (×3), cross-group ref, malformed anchor (×3), invalid status, invalid strength, weak drawdown, accepted_absence |
| Slice 2 extractor behavior | 10 | Credit table accepted, leverage text weak, repo+liquidity accepted, drawdown text weak, share-class disambiguated, share-class ambiguous, convertible absence, non-bond early return |
| Slice 2 fix additions | 5 | None type early return, partial extraction mode, incomplete coverage guard, non-zero absence negative, boilerplate duration blocked |

---

## Re-Review Conclusion

**PASS.** All five accepted fixes are closed. All hard constraints preserved. No new blocking findings introduced. All deferred residuals remain correctly deferred.

The fix is safe to accept for Slice 2. Proceed to Slice 3 (Bundle Integration).

---

## Artifact Path

`docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-rereview-ds-20260527.md`
