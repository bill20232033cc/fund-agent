# Aggregate Deepreview: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

> **Gate**: Aggregate Deepreview Gate
> **Reviewer**: AgentMiMo aggregate deepreviewer
> **Date**: 2026-06-20
> **Branch**: `funddisclosure-investor-experience-source-truth`
> **Review range**: `git diff 1bf4187..HEAD` (HEAD `8dac1fc`)
> **Classification**: heavy

---

## 1. Validation Results

| Validation | Result |
|---|---|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | **175 passed** in 0.89s |
| `uv run pytest tests/fund/test_data_extractor.py -k disclosure_source_truth_investor_experience` | **1 passed** in 0.39s |
| `uv run ruff check` (3 files) | **All checks passed!** |
| `git diff --check 1bf4187..HEAD` | **Clean** (no whitespace errors) |

---

## 2. Scope Verification

### 2.1 proof-positive investor_experience.v1 direct extraction exists only for investor_return, holder_structure, share_change

**PASS.**

- `_extract_investor_experience_source_truth()` (line 5220) calls `_select_investor_experience_values()` which only selects three candidates: `investor_return`, `holder_structure`, `share_change` (line 5281-5284).
- `_build_investor_experience_value()` (line 6304) only emits keys present in `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL = ("investor_return", "holder_structure", "share_change")` (line 276).
- `subscription_redemption` and `income_distribution` do not appear anywhere in the source-truth extraction code path. They exist only in the candidate evidence selector `_select_investor_experience_candidate_evidence()` (line 6587).

### 2.2 subscription_redemption and income_distribution remain candidate-only

**PASS.**

- `subscription_redemption` and `income_distribution` are not in `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL`.
- They appear only in `_select_investor_experience_candidate_evidence()` which is the candidate-only path invoked when source-truth admission proof is absent.
- No constant, label set, or extraction function references them as public value targets.
- Design.md explicitly states: "subscription_redemption and income_distribution remain candidate-only."
- Implementation-control.md explicitly states: "subscription_redemption and income_distribution are not public source-truth subvalues."

### 2.3 proof-missing, proof-invalid, candidate-boundary stay public missing and candidate-only

**PASS.**

- When `source_truth_admission=None`, `_extract_investor_experience_source_truth()` is never called; the processor falls through to `_select_investor_experience_candidate_evidence()` which returns `status="missing"`, `value={}`, `anchors=()` with candidate evidence records.
- Test `test_investor_experience_source_truth_requires_proof_even_when_candidate_boundary_none` (line 5479) confirms candidate_boundary=None without proof still produces missing.
- Test `test_investor_experience_source_truth_rejects_base_admission_invalid_paths` (line 5524) confirms invalid admission paths stay missing.
- Test `test_investor_experience_source_truth_candidate_boundary_remains_blocked` (line 5567) confirms candidate boundary stays blocked.

### 2.4 direct route candidate_evidence is empty

**PASS.**

- `_extract_investor_experience_source_truth()` explicitly sets `candidate_evidence=()` (line 5258).
- Test `test_investor_experience_source_truth_route_suppresses_candidate_evidence` (line 5444) verifies this.

### 2.5 current_stage.v1 and core_risk.v1 remain unimplemented and unaffected

**PASS.**

- No code in the diff touches `current_stage` or `core_risk` extraction logic.
- Tests `test_current_stage_selector_*` and `test_core_risk_selector_*` remain unchanged.
- `test_investor_experience_source_truth_does_not_populate_stage_or_risk` (line 6100) explicitly verifies non-interference.
- Design.md and implementation-control.md both state these remain unimplemented.

### 2.6 facade projection only maps the three accepted keys

**PASS.**

- `data_extractor.py` lines 767-769 extract only `investor_return`, `holder_structure`, `share_change` from `investor_experience.v1` family.
- `StructuredFundDataBundle` fields `subscription_redemption` and `income_distribution` do not exist.
- Test `test_explicit_disclosure_source_truth_investor_experience_projects_to_bundle` (line 1317 in test_data_extractor.py) verifies facade projection of the three keys with correct values and extraction_mode="direct".

### 2.7 docs/control truth are accurate

**PASS.**

All documentation changes in the diff (design.md, implementation-control.md, current-startup-packet.md, fund README) accurately reflect the implementation:

- design.md v2.31: correctly lists `investor_experience.v1` alongside the three other proof-positive families; correctly limits to `investor_return`, `holder_structure`, `share_change`; explicitly excludes `subscription_redemption` and `income_distribution` from public value; explicitly disclaims parser replacement, real-report correctness, upper-layer consumption, readiness, and release.
- implementation-control.md: correctly updates gate status to "Implementation / Code Review Gate Accepted"; correctly references all accepted review artifacts; correctly sets next entry point to "Aggregate Deepreview Gate".
- current-startup-packet.md: correctly mirrors implementation-control.md state.
- fund README: correctly states direct route clears candidate_evidence; correctly separates proof-missing from proof-positive paths.

### 2.8 no forbidden files or architecture boundary violations

**PASS.**

Changed files in the diff:
1. `docs/design.md` - docs sync (allowed)
2. `docs/implementation-control.md` - docs sync (allowed)
3. `docs/current-startup-packet.md` - docs sync (allowed)
4. `fund_agent/fund/README.md` - docs sync (allowed)
5. `fund_agent/fund/processors/fund_disclosure_processor.py` - processor implementation (allowed)
6. `tests/fund/processors/test_fund_disclosure_processor.py` - processor tests (allowed)
7. `tests/fund/test_data_extractor.py` - facade regression tests (allowed)
8. `docs/reviews/*` (7 files) - review artifacts (allowed)

No forbidden files touched. No Service/UI/Host/renderer/quality-gate boundary violations.

---

## 3. Code Quality Analysis

### 3.1 Implementation Pattern Consistency

The investor_experience extraction follows the same architectural pattern as the three preceding families (product_essence, return_attribution, manager_profile):

- Constants: label tuples for each subfield (lines 276-356)
- Value candidate: `_InvestorExperienceValueCandidate` frozen dataclass (line 391)
- Entry function: `_extract_investor_experience_source_truth()` (line 5220)
- Value selector: `_select_investor_experience_values()` delegates to three sub-selectors (line 5262)
- Sub-selectors: `_select_investor_experience_return()`, `_select_investor_experience_holder_structure()`, `_select_investor_experience_share_change()`
- Resolution: `_resolve_investor_experience_candidate()` handles deduplication and ambiguity (line 6252)
- Value builder: `_build_investor_experience_value()` (line 6304)
- Candidate evidence: `_select_investor_experience_candidate_evidence()` for proof-missing path (line 6587)

### 3.2 Fail-Closed Behavior

- Ambiguous duplicates: normalized values compared; multiple distinct values → path added to `ambiguous_paths`, candidate returns None (line 6276).
- Missing proof: source-truth extraction never invoked; candidate evidence path returns missing (verified by tests).
- Invalid admission: `admit_disclosure_intermediate()` blocks before extraction.
- Identity mismatch: fund_code and report_year checked before extraction.

### 3.3 Share Change Column Selection

The share_change extraction has a sophisticated column selection strategy:
1. Filter out label columns by header/content heuristic (line 5999)
2. If single value column → select it with reason "single_value_column" (line 6074)
3. If multiple value columns → try matching fund_code in column header (line 6076-6083)
4. If still ambiguous → return None, add to ambiguous_paths (line 6084)
5. Net change calculated via Decimal when missing from disclosure (line 6205)

Tests verify all four paths: single column, fund_code match, ambiguous rejection, and net change calculation.

### 3.4 Holder Structure Guard

Table extraction requires heading/caption/path to match `_HOLDER_STRUCTURE_GUARD_LABELS` before scanning cells (line 5760). This prevents false matches from unrelated tables containing institutional/individual labels.

### 3.5 Investor Return Priority

Estimated labels are checked before direct labels in `_investor_return_label_kind()` (line 5447-5451). This ensures "加权平均投资者收益率（估算）" is not incorrectly matched by the shorter "加权平均投资者收益率" label. The first-in-label function `_first_investor_return_label()` (line 5501) also prioritizes estimated by position in the combined label tuple.

---

## 4. Test Coverage Assessment

### 4.1 Processor Tests (29 investor_experience-specific tests)

| Category | Tests | Status |
|---|---|---|
| Candidate evidence selector (S6-E) | 11 tests | All passing |
| Source-truth route behavior | 4 tests | All passing |
| investor_return extraction | 4 tests | All passing |
| holder_structure extraction | 1 test | All passing |
| share_change extraction | 5 tests | All passing |
| Cross-family non-interference | 1 test | All passing |
| Subscription/redemption guard | 2 tests | All passing |
| Other processor tests (identity, fail-closed, registry) | 11 tests | All passing |
| **Total processor tests** | **175** | **All passing** |

### 4.2 Facade Regression Tests

- `test_explicit_disclosure_source_truth_investor_experience_projects_to_bundle`: verifies proof-positive values project through facade with correct extraction_mode, anchors, and source_kind.
- `test_explicit_disclosure_candidate_only_investor_experience_stays_missing`: verifies candidate-only path produces missing bundle fields.

### 4.3 Plan Required Tests (18 + 2 facade)

All 18 required processor tests from the plan are present and passing. Both required facade tests are present and passing. The F1 finding from MiMo code review (missing `test_investor_experience_source_truth_share_change_selects_single_value_column`) has been fixed and confirmed by targeted re-review.

---

## 5. Findings

No findings. All scope checks pass. All validations pass. Documentation is accurate and does not overclaim.

---

## 6. Residual Risks

1. `subscription_redemption` and `income_distribution` are well-separated from public value but have no explicit test asserting their absence from `_build_investor_experience_value()` output (mitigated by the `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL` constant being exhaustive and tested implicitly through the shape test).
2. Real-report correctness remains unproven (by design; out of scope).
3. `current_stage.v1` and `core_risk.v1` source-truth extraction remain unimplemented (by design; out of scope).

---

## 7. Verdict

**AGGREGATE_DEEPREVIEW_PASS**

The `investor_experience.v1` source-truth direct extraction implementation is correct, well-scoped, and accurately documented. Proof-positive extraction covers exactly `investor_return`, `holder_structure`, and `share_change`. `subscription_redemption` and `income_distribution` remain candidate-only. `current_stage.v1` and `core_risk.v1` are unaffected. Facade projection maps only the three accepted keys. All 175+1 tests pass, ruff is clean, whitespace is clean. No forbidden files touched. No architecture boundary violations. Documentation does not overclaim readiness, parser replacement, real-report correctness, or upper-layer consumption.
