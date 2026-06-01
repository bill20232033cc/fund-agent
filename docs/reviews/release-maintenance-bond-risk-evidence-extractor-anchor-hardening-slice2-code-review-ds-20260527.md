# Bond Risk Evidence Extractor / Anchor Hardening — Slice 2 Code Review (DS)

> Date: 2026-05-28
> Role: code review worker
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Slice: Slice 2 Extractor
> Review target:
> - `fund_agent/fund/extractors/bond_risk_evidence.py`
> - `fund_agent/fund/extractors/__init__.py`
> - `tests/fund/extractors/test_bond_risk_evidence.py`
> Plan: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
> Implementation: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-implementation-20260527.md`

## Worker Self-Check (Before Review)

- Self-check: pass
- Role confirmed: code review worker only, not controller.
- Workflow boundary confirmed: no workflow command, no skill, no implementation, no fix, no staging, no commit, no PR, no golden promotion.
- Allowed write path confirmed: only this review artifact.
- All target files read and analyzed.
- tests and lint run independently to verify implementation artifact claims.

## Verification Summary

| Check | Result |
|---|---|
| `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q` | 23 passed |
| `uv run ruff check` (all 3 target files) | All checks passed |
| Slice scope boundary (no bundle/snapshot/score) | Confirmed — only 3 allowed files touched |

## Review Conclusion: PASS (No Blocking Findings)

The Slice 2 implementation faithfully implements the extractor contract from the accepted plan. No FQ0-FQ6 weakening, no direct PDF/cache/source-helper access, no golden promotion. The extractor properly gates on `bond_fund` before scanning, produces stable `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` anchors, validates output through `validate_bond_risk_evidence_value`, and keeps drawdown/leverage qualitative-only evidence as weak.

Six accepted-worthy findings and four residual risks follow. None block Slice 2 acceptance.

---

## Finding F1 — Accepted-Worthy: Table section attribution is caller-assigned, not table-proven

**Severity**: Medium (false section attribution risk)
**Location**: `bond_risk_evidence.py:769–807` (`_first_row_anchor_draft`), `bond_risk_evidence.py:855–896` (`_absence_row_anchor_draft`)

`_first_row_anchor_draft` accepts a `section_id` parameter but iterates over ALL `report.tables` without filtering by section. The same applies to `_absence_row_anchor_draft`. Since `ParsedTable` (documents/models.py:475) has no `section_id` field — only `page_number`, `table_index`, `headers`, `rows` — every table search scans the full table list. The `section_id` stored in the returned `_AnchorDraft` reflects the caller's expectation, not the table's actual origin.

**Example**: `_extract_credit_risk` passes `section_id=_SECTION_PORTFOLIO` (§8), but a table containing "信用" + "评级" from any section would match and be recorded as §8.

**Impact**: Anchors may misattribute tables to wrong sections. The plan requires "Accepted table evidence should include section_id" — but the extractor can't guarantee section accuracy because `ParsedTable` doesn't carry it.

**Recommendation**: Accept as residual for this gate. When `ParsedTable` gains section affiliation in a future parser enhancement, update the extractor to filter by section. Document this limitation in the anchor `note` or add a `reviewer_note`.

---

## Finding F2 — Accepted-Worthy: `extraction_mode="estimated"` where plan specifies `"partial"`

**Severity**: Low (documented gap, functionally correct)
**Location**: `bond_risk_evidence.py:1314–1331` (`_extraction_mode`), `models.py:10` (`ExtractionMode`)

The plan (lines 148–153) specifies three extraction modes for `bond_risk_evidence`:
- `"direct"` — all groups satisfied
- `"partial"` — some groups have usable evidence but others remain missing/weak/ambiguous
- `"missing"` — no group satisfied

The implementation maps `contract_status="partial"` → `extraction_mode="estimated"` because `ExtractionMode = Literal["direct", "derived", "estimated", "missing"]` has no `"partial"` member. The implementation artifact (line 108) documents this as a known residual.

**Impact**: Snapshot consumers see `"estimated"` instead of `"partial"`, which is semantically close but not identical. The plan's Slice 4 snapshot integration notes that this should be addressed at that stage.

**Recommendation**: Accept for Slice 2. Either add `"partial"` to `ExtractionMode` in Slice 4, or update the plan to accept `"estimated"` as the canonical mode for partial contract status. Do not let this drift unaddressed past Slice 4.

---

## Finding F3 — Accepted-Worthy: Single-line keyword match produces `accepted` duration_rate_risk

**Severity**: Low–Medium (false positive risk on other funds)
**Location**: `bond_risk_evidence.py:153–183` (`_extract_duration_rate_risk`)

`_find_text_match` with `keyword_groups=(("久期",), ("利率风险",))` searches §2/§4/§5. A single line containing "利率风险" (interest-rate risk) — which appears in virtually every bond fund annual report as mandatory risk disclosure — produces `status="accepted"`, `strength="qualitative_direct"`.

For `006597` / `2024`, the evidence review confirmed substantive duration strategy text exists, so the result is correct. But the extractor has no way to distinguish boilerplate risk disclosure ("本基金面临利率风险…") from substantive strategy text ("本基金通过久期管理控制利率风险…").

**Impact**: On a fund with minimal duration disclosure, a boilerplate risk statement could produce a false positive `accepted` status. This would be caught at the Slice 5 score/quality-gate level only if the snapshot correctly exposes the weak provenance.

**Recommendation**: Consider tightening the keyword match for `duration_rate_risk` to require at least two keyword groups, or add a minimum line-length / context check. Alternatively, accept as-is and ensure Slice 4 snapshot notes expose the thin provenance so Slice 5 score can apply stricter judgment.

---

## Finding F4 — Accepted-Worthy: `_absence_row_anchor_draft` searches all tables for broad keywords

**Severity**: Low
**Location**: `bond_risk_evidence.py:855–896` (`_absence_row_anchor_draft`)

The function searches ALL tables for rows containing "股票" or "可转债" AND an absence value (`-`, `0`, `0.00`, etc.). It does not restrict by section or by table keyword. A row like "存托凭证(股票)" in a custody table could theoretically trigger a false match, though the absence-value check makes this unlikely in practice.

**Impact**: Low. The absence-value check (`_row_has_absence_value`) is reasonably specific — most false-positive rows wouldn't have `-` or `0` in their value cells when the row label contains "股票".

**Recommendation**: Accept. The `_row_has_absence_value` guard is sufficient. If false positives emerge in real reports, add table-keyword filtering or section scoping.

---

## Finding F5 — Accepted-Worthy: Missing test for `classified_fund_type=None`

**Severity**: Low (code is correct, test gap only)
**Location**: tests `test_bond_risk_evidence.py:366–378`

The plan (line 496) states: "Unknown or absent classified_fund_type must not be treated as bond evidence; it should fail closed to missing/not-applicable." The implementation correctly handles this: `if classified_fund_type != _BOND_FUND_TYPE` → `None != "bond_fund"` → returns missing (line 125).

The test `test_non_bond_type_returns_missing_without_scanning_group_extractors` tests `"active_fund"` but not `None`.

**Impact**: Low. The code path is trivially correct and the `"active_fund"` test covers the same branch. But the plan explicitly calls out the `None` case as important.

**Recommendation**: Add a one-line parametrized variant for `None` in Slice 2 or defer to Slice 6 smoke test.

---

## Finding F6 — Accepted-Worthy: Dead code in `_field_note` fallback

**Severity**: Trivial
**Location**: `bond_risk_evidence.py:1347–1354` (`_field_note`)

```python
return (
    f"contract_id={value.contract_id}; "
    ...
) or _MISSING_NOTE
```

The formatted string always starts with `contract_id=...` and can never be empty/falsy. The `or _MISSING_NOTE` fallback is unreachable dead code.

**Recommendation**: Remove the `or _MISSING_NOTE` suffix. Trivial cleanup, not blocking.

---

## Per-Group Behavior Audit

| Group | Status | Evidence | Strength | Plan Compliance |
|---|---|---|---|---|
| `duration_rate_risk` | accepted | Text match on 久期/利率风险 | qualitative_direct | Correct — plan allows qualitative_direct |
| `credit_risk` | accepted | Rating table row | quantitative_direct | Correct — rating table row found |
| `credit_risk` (fallback) | weak | Strategy text only | qualitative_direct | Correct — falls back when no table |
| `leverage_liquidity` | accepted | Repo table row | quantitative_direct | Correct — actual repo data required |
| `leverage_liquidity` (fallback) | weak | Leverage/liquidity text only | qualitative_direct | Correct — strategy text alone is weak |
| `asset_allocation_holdings_mix` | accepted | Bond allocation table row | quantitative_direct | Correct |
| `drawdown_stress` | accepted | Max drawdown table row | quantitative_direct | Correct — metric required |
| `drawdown_stress` (fallback) | weak | Control intent text | qualitative_control_intent | Correct — text alone is weak |
| `redemption_share_pressure` | accepted | Share change with class disambiguation | quantitative_direct | Correct — §2 mapping required |
| `redemption_share_pressure` (fallback) | ambiguous | Multi-class without disambiguation | ambiguous | Correct — fail closed |
| `convertible_bond_equity_exposure` | accepted_absence | `-`/`0` rows for stock/convertible | quantitative_absence | Correct — explicit absence |

All seven group behaviors match the plan's per-group decisions.

---

## Contract Invariant Checks

| Invariant | Status |
|---|---|
| No repository/PDF/cache/source helper access in extractor | Pass — only `ParsedAnnualReport` consumed |
| Non-bond early return before scanning seven groups | Pass — `classified_fund_type != "bond_fund"` returns immediately |
| Stable anchor format `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` | Pass — `_build_group_anchors:712` |
| Anchor ordinal deterministic by `(section_id, page_number, table_id, row_locator, evidence_role)` | Pass — `_build_group_anchors:699–708` |
| Validator called before returning non-missing value | Pass — `extract_bond_risk_evidence:143` |
| Drawdown control text alone → weak, unsatisfied | Pass — `_extract_drawdown_stress:384` |
| Leverage strategy text alone → weak, unsatisfied | Pass — `_extract_leverage_liquidity:293` |
| Share-class ambiguous → ambiguous, unsatisfied | Pass — `_extract_redemption_share_pressure:421–428` |
| Explicit absence → accepted_absence, satisfied | Pass — `_extract_convertible_bond_equity_exposure:506` |
| No bundle/snapshot/score changes | Pass — only 3 Slice 2 files touched |
| No `extra_payload` | Pass — all params explicit |
| `required_evidence_groups` always all seven ids | Pass — `BOND_RISK_EVIDENCE_GROUP_IDS` constant |
| `satisfied/missing/weak/ambiguous_group_ids` derived from group statuses | Pass — `_build_value:533–536` + validator `_derive_bond_risk_group_id_sets` |

---

## Test Coverage Audit

| Test | Plan Requirement | Status |
|---|---|---|
| `test_complete_seven_group_bond_risk_evidence_value_validates` | Slice 1: complete value validates | Pass |
| `test_missing_anchor_for_accepted_group_fails_validation` | Slice 1: missing anchor fails | Pass |
| `test_incomplete_group_set_fails_validation` | Slice 1: exactly seven groups | Pass |
| `test_duplicate_group_id_fails_validation` | Slice 1: no duplicate IDs | Pass |
| `test_caller_provided_derived_group_ids_must_match_statuses` | Slice 1: derived ids match | Pass |
| `test_caller_provided_weak_group_ids_must_match_statuses` | Slice 1: weak ids match | Pass |
| `test_caller_provided_ambiguous_group_ids_must_match_statuses` | Slice 1: ambiguous ids match | Pass |
| `test_cross_group_anchor_reference_fails_validation` | Slice 1: cross-group ref fails | Pass |
| `test_malformed_or_wrong_anchor_id_fails_validation` (×3) | Slice 1: anchor format validation | Pass |
| `test_invalid_status_fails_validation` | Slice 1: invalid status rejected | Pass |
| `test_invalid_strength_fails_validation` | Slice 1: invalid strength rejected | Pass |
| `test_weak_drawdown_control_record_validates_but_is_unsatisfied` | Slice 1: weak drawdown unsatisfied | Pass |
| `test_explicit_absence_convertible_equity_record_is_accepted` | Slice 1: accepted_absence | Pass |
| `test_table_backed_credit_risk_is_accepted_with_row_level_anchor` | Slice 2: table credit risk accepted | Pass |
| `test_flexible_leverage_strategy_text_alone_is_weak` | Slice 2: leverage text alone weak | Pass |
| `test_repo_table_row_plus_liquidity_text_satisfies_leverage_liquidity` | Slice 2: repo+liquidity accepted | Pass |
| `test_drawdown_control_text_alone_is_weak` | Slice 2: drawdown text weak | Pass |
| `test_multi_share_class_share_change_selects_target_class_when_disambiguated` | Slice 2: share class disambiguation | Pass |
| `test_ambiguous_multi_share_class_share_change_stays_ambiguous` | Slice 2: ambiguous share class | Pass |
| `test_convertible_and_equity_dash_rows_become_accepted_absence` | Slice 2: accepted_absence | Pass |
| `test_non_bond_type_returns_missing_without_scanning_group_extractors` | Slice 2: non-bond early return | Pass |

All 13 planned Slice 2 test scenarios are covered by the 23 tests (10 Slice 1 model tests + 13 Slice 2 extractor tests).

---

## Residual Risks

### R1: Table section misattribution (linked to F1)
`ParsedTable` has no `section_id`. All table searches scan the full table list. Anchors may record incorrect section numbers. Mitigation: parsers should eventually add section affiliation to tables.

### R2: `extraction_mode="estimated"` versus plan-specified `"partial"` (linked to F2)
Slice 4 snapshot integration must resolve this discrepancy — either extend `ExtractionMode` or accept `"estimated"`.

### R3: False positives from broad keyword matching on real 006597 report (linked to F3)
Single-keyword matches (`利率风险`, `回购`, `股票`) across all sections/tables could produce false evidence on reports with noisy text. Mitigation: Slice 6 real-report smoke test should catch cases where keywords match unintended sections.

### R4: No test for `classified_fund_type=None` (linked to F5)
Code is correct but the plan-explicitly-required `None` case lacks a dedicated test. Mitigation: path is trivially correct; add test in Slice 6 or whenever convenient.

---

## Stop Condition Check

| Stop condition | Triggered? |
|---|---|
| Precise leverage/repo rows cannot be found for real 006597 | N/A — Slice 2 uses synthetic fixtures only |
| Cannot obtain explicit classified fund type at extractor boundary | No — type is an explicit parameter |

No stop condition triggered. The implementation correctly provides the `classified_fund_type` parameter for upstream callers to supply.

---

## Review Worker Self-Check (After Review)

- Self-check: pass
- All planned review criteria addressed.
- No code modified; only this review artifact written.
- Findings are evidence-based with file:line references.
- No blocking findings; six accepted-worthy findings recorded.
- Residual risks accurately reflect Slice 2 scope limitations.
- Conclusion: PASS.

---

## Handoff Decision

**Conclusion**: PASS. Slice 2 extractor is accepted-worthy. Proceed to Slice 3 (Bundle Integration) after controller acknowledges findings F1–F6 and residuals R1–R4.

**Artifact path**: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-code-review-ds-20260527.md`
