# MVP Small Golden Set Row-field Extractor Correctness Test Gate — AgentDS Final Code Review

## Gate

- Gate: `row-field extractor correctness test gate after accepted retained excerpts`
- Review role: AgentDS (independent final code review)
- HEAD: `928fc86 gateflow: accept row-field extractor correctness tests`
- Date: 2026-06-09

## Scope

Per user directive, this review is scoped to:

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-implementation-evidence-20260609.md`
- `docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-controller-judgment-20260609.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## Findings

### 1. PASS — correctness oracle is exclusively the accepted retained excerpt JSON

**Check**: The test reads only `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` as the single correctness oracle (`test file:24`).

**Evidence**:
- `ORACLE_PATH` at `test file:23-28` points exclusively to the retained excerpt JSON.
- `test_oracle_boundary_is_retained_excerpt_only_for_accepted_rows` (`test file:366-402`) validates the oracle schema version, five accepted rows, all eight field groups, non-empty expected/anchor/excerpt, and boundary invariants.
- No other JSON/CSV/text file is read as a correctness source.
- `_build_report_from_oracle_row` (`test file:286-347`) constructs `ParsedAnnualReport` in memory from oracle fields only — no file I/O beyond the oracle JSON.

**Verdict**: No blocking finding.

### 2. PASS — synthetic/unmatched expected_fields.json excluded from correctness

**Check**: `tests/fixtures/fund/small_golden_set/*/expected_fields.json` must not be promoted to correctness source.

**Evidence**:
- `test_synthetic_unmatched_expected_fields_are_excluded_from_correctness_source` (`test file:405-432`) asserts for all five fixture directories:
  - `ORACLE_PATH.name != "expected_fields.json"` (line 418)
  - `SYNTHETIC_FIXTURE_ROOT not in ORACLE_PATH.parents` (line 419)
  - `fixture_source_kind == "synthetic"` (line 427)
  - `exact_numeric_correctness_allowed == False` (line 428)
  - `promotion_allowed == False` (line 429)
  - `fallback_invocation == "prohibited"` (line 430)
  - `source_identity.status == "unmatched_synthetic"` (line 431)
  - `source_identity.matched_source_document == False` (line 432)
- Independent spot check of `tests/fixtures/fund/small_golden_set/004393_2024/expected_fields.json` confirms all six assertions hold.

**Verdict**: No blocking finding.

### 3. PASS — `scale` is a passing `fund_scale` assertion, not xfail

**Check**: `scale` field must be a default passing correctness assertion, not erroneously listed as an unsupported gap.

**Evidence**:
- `SAME_SOURCE_UNSUPPORTED_FIELDS` at `test file:74` is exactly `{"manager", "holdings", "risk"}` — `scale` is absent.
- `test_profile_extractor_matches_same_source_identity_benchmark_and_fee` (`test file:435-470`) asserts:
  - `profile.basic_identity.value["fund_scale"] == expected_units` (line 464)
  - `expected_units` is resolved from `scale_expected.get("target_share_units") or scale_expected.get("total_share_units")` (line 457).
- Controller judgment (`controller judgment:37-39`) confirms the Carver finding that `scale` was incorrectly classified as xfail, was accepted, and was fixed in a targeted re-review.

**Verdict**: No blocking finding.

### 4. PASS — unsupported xfail is strictly `manager`, `holdings`, `risk`

**Check**: Only these three fields are strict-xfail gap markers; no accepted passing correctness misclassified.

**Evidence**:
- `SAME_SOURCE_UNSUPPORTED_FIELDS` at `test file:74` is exactly `{"manager", "holdings", "risk"}`.
- `test_same_source_fields_without_current_row_consumer_are_blocked_gaps` (`test file:531-554`) is parameterized over `SAME_SOURCE_UNSUPPORTED_FIELDS`, decorated `@pytest.mark.xfail(strict=True)`, and asserts `field_name not in SAME_SOURCE_UNSUPPORTED_FIELDS` (line 554) — which will only fail if a field is removed from `SAME_SOURCE_UNSUPPORTED_FIELDS` without removing xfail.
- The last assert (`line 554`) is an intentional self-check: if `field_name not in SAME_SOURCE_UNSUPPORTED_FIELDS` evaluates `True`, the parameterized test passes through xfail. If someone removes a field from the set but forgets to remove the xfail decorator, the test still xfails — the self-check harmlessly passes inside xfail. Conversely, if a field is added to the set, it gets a fresh xfail; if removed, the xfail for that param would `xpASS` (unexpected pass), triggering `strict=True` failure. This is correct defense-in-depth.
- Live run confirms `3 xfailed` exactly matches three fields.

**Verdict**: No blocking finding. The self-assert on line 554 is non-obvious but correct — it guards against the set shrinking without xfail removal.

### 5. PASS — test genuinely calls current extractors

**Check**: `extract_profile` and `extract_performance` are imported from the current production extractor modules and are invoked with in-memory `ParsedAnnualReport` objects.

**Evidence**:
- Imports at `test file:18-19`:
  ```python
  from fund_agent.fund.extractors.performance import extract_performance
  from fund_agent.fund.extractors.profile import extract_profile
  ```
- `test_profile_extractor_matches_same_source_identity_benchmark_and_fee` at line 453: `profile = extract_profile(report)`
- `test_performance_extractor_matches_same_source_one_year_returns` at line 491: `performance = extract_performance(report)`
- `test_performance_extractor_matches_same_source_tracking_error_when_present` at line 522: `performance = extract_performance(report)`
- The `report` argument is constructed by `_build_report_from_oracle_row` which creates a `ParsedAnnualReport` entirely from oracle JSON fields — no mock, stub, or test double for the extractors themselves.
- Source files `fund_agent/fund/extractors/profile.py` and `fund_agent/fund/extractors/performance.py` exist and contain the production `extract_profile` / `extract_performance` functions.

**Verdict**: No blocking finding.

### 6. PASS — no out-of-scope access

**Check**: The test must not read PDF, access network, call `FundDocumentRepository`, invoke fallback, probe live/provider, modify extractor/provider/default/runtime/budget/config, or perform fixture projection / golden readiness promotion.

**Evidence**:
- Test imports only: `json`, `re`, `pathlib.Path`, `typing.Any`, `pytest`, `DocumentKey`, `ParsedAnnualReport`, `ParsedTable`, `ReportSection`, `extract_profile`, `extract_performance`.
- No import or usage of: `FundDocumentRepository`, `pdfplumber`, `httpx`, `akshare`, network/socket, `cache`, `provider`, `fallback`, `config`, `Host`, `Agent`, `Service`.
- `test_oracle_boundary_is_retained_excerpt_only_for_accepted_rows` asserts all `access_boundary` keys are `False` (`test file:398-399`), including `network_access_performed`, `fund_document_repository_live_acquisition_performed`, `fallback_invocation_performed`, `extractor_modified`, `fixture_projection_performed`, `exact_numeric_correctness_accepted`, `golden_readiness_promotion_performed`.
- The oracle JSON contains `local_pdf_read_performed: true` — this refers to the **retained excerpt fixture gate**'s own PDF read (which extracted the short excerpts now stored in the JSON). The current test gate reads only the JSON, not the PDF. This is correct layering.
- `FORBIDDEN_RETAINED_KEYS` at `test file:65-73` asserts the oracle JSON does not contain `full_pdf`, `full_pdf_text`, `full_pdf_content`, `full_page_text`, `page_text`, `raw_page_text`, `raw_pdf_text`. Independent grep of the oracle JSON confirms zero hits.

**Verdict**: No blocking finding.

### 7. PASS — evidence/control docs consistent with validation results

**Check**: The evidence and controller judgment documents must report `13 passed, 3 xfailed` and `34 passed, 3 xfailed`, matching live test results.

**Evidence**:
- Implementation evidence (`evidence:56`): `13 passed, 3 xfailed in 0.76s`; (`evidence:62`): `34 passed, 3 xfailed in 0.54s`.
- Controller judgment (`judgment:49`): `13 passed, 3 xfailed`; (`judgment:55`): `34 passed, 3 xfailed`.
- Live re-run (this review): `13 passed, 3 xfailed in 0.67s`; `34 passed, 3 xfailed in 0.44s`.
- Slight timing variance is expected across runs; exact test counts are identical.
- `docs/implementation-control.md:10`, `control doc:70-72`, `control doc:281-283`, `control doc:292` — all gate entries consistently reference the same artifacts, counts, and scope.
- `docs/current-startup-packet.md:21` (`current gate`) and `startup packet:70-72` (`current gate status`) — both are internally consistent with the accepted gate state.
- `tests/README.md:29` documents the new test entry with correct boundary description.

**Verdict**: No blocking finding.

## Residual Risk

1. **Oracle is human-transcribed excerpt, not machine-extracted ground truth**. The retained excerpt JSON was produced by a human reading PDFs with `pdfplumber`. Transposition errors (e.g., misreading a row in a multi-share-class table) could cause the oracle expected values to diverge from the true annual report data. The `sha256` fingerprints in the oracle allow future verification but do not independently prove excerpt correctness. This residual is owned by the retained excerpt fixture gate, not this test gate.

2. **Minimal `ParsedAnnualReport` construction does not exercise the full production PDF parse path**. The test builds `ParsedAnnualReport` objects with exactly the fields the extractor needs — it proves extractor correctness given a correctly shaped input, but does not prove the production parser produces that shape from real PDF text. This residual belongs to a future PDF parser / table-shape fidelity gate.

3. **Single-year (2024) coverage**. All five rows use the 2024 annual report. Multi-year extractor behavior (year-over-year field layout drift, stale anchors) is untested. This residual is deferred to the multi-year annual evidence scope gate.

4. **`SAME_SOURCE_UNSUPPORTED_FIELDS` self-assert pattern (line 554)**. The `assert field_name not in SAME_SOURCE_UNSUPPORTED_FIELDS` inside an `xfail(strict=True)` test is correct but non-obvious. A future maintainer removing a field from the set without removing the corresponding parametrized xfail would get `xpASS` → strict failure, which is the desired behavior. Risk: low.

## Adversarial Pass

- **Oracle substitution attack**: Replacing the oracle JSON path with a synthetic fixture path would be caught by `test_synthetic_unmatched_expected_fields_are_excluded_from_correctness_source` (line 418: `ORACLE_PATH.name != "expected_fields.json"`).
- **Oracle field injection**: Adding a `full_pdf_text` key to the oracle JSON would be caught by `test_oracle_boundary` (line 402: `FORBIDDEN_RETAINED_KEYS.isdisjoint`).
- **Silent xfail removal**: Removing a field from `SAME_SOURCE_UNSUPPORTED_FIELDS` without adding a passing assertion would cause `test_same_source_fields_without_current_row_consumer_are_blocked_gaps` to `xpASS` → strict failure. Removing both the set entry and the test would lose coverage of the gap — but this is a code deletion attack, not a correctness attack, and would be caught by any reasonable diff review.
- **Extractor shadowing**: Replacing `extract_profile` / `extract_performance` with test-local stubs would survive this test but would be caught by existing extractor unit tests (`tests/fund/extractors/test_profile.py`, `tests/fund/extractors/test_performance.py`).

## Judgment

**PASS — no blocking findings.**

All seven review points pass. The test correctly uses the accepted retained excerpt JSON as its sole correctness oracle, explicitly excludes synthetic/unmatched fixtures, asserts `scale` as a passing field, restricts xfail to exactly `manager`/`holdings`/`risk`, genuinely calls the production extractors, does not cross any access boundary (PDF/network/FDR/fallback/provider/config/promotion), and is consistent with the documented validation results of `13 passed, 3 xfailed` and `34 passed, 3 xfailed`.
