# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Aggregate Deepreview

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Aggregate Deepreview Gate`
- Role: AgentDS, review-only
- Review range: `4286987..HEAD` (5 commits, f89ff07 HEAD)
- Artifact path: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-aggregate-deepreview-ds-20260620-110155.md`
- Verdict: `AGGREGATE_DEEPREVIEW_PASS`

## Review Scope

Review all 5 commits across Slices 1-4 against the accepted plan, plan controller judgment, 4 slice controller judgments, and binding amendments.

### Commits Reviewed

| Commit | Slice | Description |
|---|---|---|
| `5e4c8ff` | Plan | gateflow: accept fdd manager profile source truth plan |
| `e6df71b` | 1 | gateflow: accept fdd manager profile source truth slice1 |
| `30054f3` | 2 | gateflow: accept fdd manager profile source truth slice2 |
| `6c30386` | 3 | gateflow: accept fdd manager profile source truth slice3 |
| `f89ff07` | 4 | gateflow: accept fdd manager profile source truth slice4 |

### Changed Files

| File | Lines Added | Classification |
|---|---|---|
| `fund_agent/fund/processors/fund_disclosure_processor.py` | 1590 | Implementation |
| `tests/fund/processors/test_fund_disclosure_processor.py` | 1485 | Tests |
| `tests/fund/test_data_extractor.py` | 399 | Facade tests |
| `docs/design.md` | 12 | Docs sync |
| `fund_agent/fund/README.md` | 6 | Docs sync |
| `docs/implementation-control.md` | 17 | Controller bookkeeping |
| `docs/current-startup-packet.md` | 8 | Controller bookkeeping |
| `docs/reviews/*` (26 artifacts) | ~4200 | Evidence chain |

## Validation Results

```
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
194 passed in 0.91s

uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
All checks passed!

git diff --check
<no output>
```

All validation commands pass with zero failures, zero lint issues, zero whitespace issues.

## Aggregate Question 1: Source-Truth Admission Integrity

**Question**: Across Slices 1-4, does `manager_profile.v1` proof-positive FDD source-truth direct extraction satisfy the accepted plan without weakening source-truth admission?

**Verdict: PASS**

Evidence:

1. **Admission gate unchanged**. Manager profile extraction is only reached when `source_truth_extraction_allowed and content_intermediate is not None` (`fund_disclosure_processor.py:877`). The existing `_validate_source_truth_admission()` is not altered.

2. **Proof-positive only**. No alternative path bypasses the proof gate. Base admission failures (`source_provenance=None`, non-empty `failure_class`, identity mismatch) remain blocked at the admission layer before field-family routing (`fund_disclosure_processor.py:860-871`).

3. **Candidate-boundary remains blocked**. Content with `candidate_boundary is not None` follows the existing blocked path and never reaches source-truth extraction. No proof object can upgrade a candidate-boundary input.

4. **All 5 approved top-level subvalues implemented** per plan Section 4 exact shape:
   - `portfolio_managers` — tenure-list shape with name/role/start_date/end_date/source_anchor
   - `manager_strategy_text` — `{strategy_summary, market_outlook}`
   - `turnover_rate` — `{turnover_rate, turnover_basis}`
   - `manager_alignment` — `{manager_holding, employee_holding, judgment: None}`
   - `holdings_snapshot` — `{top_holdings, top_holdings_status, top_holdings_source, industry_distribution, industry_distribution_status}`

5. **Source selection follows plan Section 5 rules**:
   - Only reads `sections`, `paragraph_blocks`, `table_blocks`, `table_blocks[*].cells`
   - Requires `locator_stability == "stable"`
   - Uses heading-path-gated matching (not free text search)
   - Roster requires row/role context containing `基金经理`; broad headings alone insufficient
   - Strategy uses only allowed headings; text body false positives rejected
   - Turnover requires parseable percent literal
   - Alignment requires guard context for generic tokens
   - Holdings uses heading + context heading double gate

6. **No admission weakening anywhere**: no new proof mechanism, no new source kind, no schema expansion, no `candidate_boundary is None` treated as sufficient.

## Aggregate Question 2: Semantics Preservation

**Question**: Are public missing/partial/accepted semantics, candidate_evidence suppression, anchors, and existing gap taxonomy preserved?

**Verdict: PASS**

Evidence:

1. **Status semantics** (`_manager_profile_status`, `fund_disclosure_processor.py`):
   - `accepted`: all 5 required top-level keys present AND `ambiguous_paths` empty
   - `partial`: 1-4 subvalues, or all 5 with internal ambiguity (Slice 3 fix verified)
   - `missing`: no allowed subvalue emitted
   - `extraction_mode`: `"direct"` for accepted/partial, `"missing"` for missing

2. **candidate_evidence suppression**:
   - Direct route always returns `candidate_evidence=()` (line 1108)
   - Proof-missing path preserves S6-D candidate evidence (`fund_disclosure_processor.py:898-901`)
   - Binding amendment 4 verified: `test_manager_profile_source_truth_route_suppresses_candidate_evidence` asserts `candidate_evidence == ()` on direct-route missing (test line 2591)

3. **Anchors**:
   - Only existing `EvidenceAnchor` used; all have `source_kind="annual_report"`, `page_number=None`
   - Row locator formats match plan Section 7 required formats
   - Anchors only for emitted values; missing subkeys produce no anchors
   - Deduplication via existing `_dedupe_anchors()`

4. **Gap taxonomy**:
   - Only existing `FundExtractionGapCode` values used
   - `field_family_missing`, `field_family_partial`, `ambiguous_table_or_locator` used per plan Section 6
   - `candidate_only_not_source_truth` preserved on proof-missing path
   - `source_truth_admission_missing` / `source_truth_admission_invalid` inherited from existing guard
   - No new gap codes added

5. **Direct-route missing shape**: `value={}`, `anchors=()`, `candidate_evidence=()` — no `schema_version` key present (plan Slice 3 requirement verified).

## Aggregate Question 3: Facade Tests and Docs Sync

**Question**: Are facade tests and docs sync consistent with implementation and not overclaiming real-report correctness, parser replacement, readiness/release, EvidenceSourceKind expansion, or upper-layer direct candidate consumption?

**Verdict: PASS**

Evidence:

1. **Positive facade regression** (`test_explicit_disclosure_source_truth_manager_profile_projects_to_bundle`, `test_data_extractor.py:1226`):
   - Uses explicit FDD route via `disclosure_intermediate`
   - Asserts all 5 bundle fields: `portfolio_managers`, `turnover_rate`, `manager_alignment`, `manager_strategy_text`, `holdings_snapshot`
   - Asserts `extraction_mode == "direct"` for all 5
   - Asserts exact value shapes match plan Section 4
   - Asserts `judgment: None` for `manager_alignment`
   - No claim of real-report correctness, parser replacement, or readiness

2. **Negative facade regression** (`test_explicit_disclosure_non_candidate_admitted_produces_missing_bundle`, `test_data_extractor.py:1578`):
   - Non-candidate FDD stub keeps bundle fields missing
   - Manager strategy text, portfolio managers value is None, anchors empty
   - No candidate evidence consumed as source truth

3. **No production `data_extractor.py` changes**: Existing `_field_from_family()` already handles projection. Zero production code changed in `fund_agent/fund/data_extractor.py`.

4. **Docs sync** (`docs/design.md v2.30`, `fund_agent/fund/README.md`):
   - Updates exact count from 2 to 3 implemented families
   - Names `manager_profile.v1` 5 subvalues
   - Explicitly states remaining 3 families (`investor_experience.v1`, `current_stage.v1`, `core_risk.v1`) unimplemented
   - Preserves `candidate_only / not_proven / NOT_READY`
   - No claim of real-report correctness, parser replacement, readiness, release, or `EvidenceSourceKind` expansion

5. **No overclaiming detected**: No mention of production readiness, golden correctness, parser replacement, live evidence, or upper-layer consumption in any changed doc or test.

## Aggregate Question 4: Scope Boundary

**Question**: Did the work stay exactly within `manager_profile.v1`, without implementing `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` or leaking `holdings_snapshot` into risk/stage?

**Verdict: PASS**

Evidence:

1. **Only `manager_profile.v1` has source-truth extraction**:
   - `product_essence.v1` and `return_attribution.v1` unchanged
   - `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` remain candidate-only (`fund_disclosure_processor.py:903-905`)
   - No code in `_extract_manager_profile_source_truth` or any `_select_manager_profile_*` helper references other families

2. **Cross-family leakage check (negative)**:
   - grep for `current_stage` and `core_risk` in manager extraction code: **zero hits**
   - grep for `holdings_snapshot` cross-referencing other families: **zero hits**
   - `holdings_snapshot` stays within `manager_profile.v1` boundary

3. **Binding amendment 5 verified**: Regression test `test_current_stage_and_core_risk_remain_missing_for_fdd_source_truth` exists and passes (from Slice 3 test suite).

4. **No forbidden files touched**:
   - `fund_agent/fund/processors/contracts.py` — not touched
   - `fund_agent/fund/data_extractor.py` production code — not touched
   - `fund_agent/fund/extractors/**` — not touched
   - `fund_agent/fund/documents/**` — not touched
   - `fund_agent/services/**` — not touched
   - renderer, quality gate, repository/source code — not touched

5. **Binding amendment 6 verified**: `holdings_snapshot` and `turnover_rate` emit disclosed data only; no concentration, style drift, current-stage, core-risk, or manager-quality conclusions.

6. **Binding amendment 7 verified**: `manager_alignment.value["judgment"]` is `None` (line 1780).

## Aggregate Question 5: Slice Review Finding Disposition

**Question**: Are all accepted review findings from slice reviews fixed or correctly dispositioned?

**Verdict: PASS**

### Slice 1 — No Findings

DS PASS, MiMo PASS. Zero findings to disposition.

### Slice 2 — All 5 Findings Fixed

| Finding | Source | Disposition | Fix Verified By |
|---|---|---|---|
| Roster broad heading / heading-path self-authorization | DS F1 | Fixed | DS re-review (`095926`), MiMo re-review (`100152`) |
| Strategy body text false positive | DS F2 / MiMo 001 | Fixed | Both re-reviews verify heading-path gated matching |
| Missing-key test used `dict.get()` | MiMo 002 | Fixed | Both re-reviews verify explicit key absence checks |
| Roster same-name conflict + identical duplicate coverage | DS F3/F4 / MiMo 003 | Fixed | Both re-reviews verify new conflict/duplicate tests |
| Strategy ambiguity test | MiMo optional | Deferred-with-owner | Deferred to future refinement; no blocker |

All accepted findings closed or deferred with owner. Zero open findings.

### Slice 3 — All 3 Findings Fixed

| Finding | Source | Disposition | Fix Verified By |
|---|---|---|---|
| Status could return `accepted` while ambiguity gaps existed | DS medium | Fixed | DS/MiMo re-reviews verify `accepted` requires empty `ambiguous_paths` |
| `_manager_profile_cell_original_index` silently returned 0 for foreign cell | DS low | Fixed | DS/MiMo re-reviews verify `ValueError` and regression |
| Table-backed `manager_alignment` positive path lacked coverage | DS residual | Fixed | DS/MiMo re-reviews verify new coverage |

All accepted findings closed. Zero open findings.

### Slice 4 — All Findings Dispositioned

| Finding | Source | Disposition | Rationale |
|---|---|---|---|
| Evidence residual table mislabeled as `fixed in current slice` | DS F1 low | Fixed | Verified by both re-reviews; changed to `preserved in current slice` |
| Positive facade regression lacks `current_stage.v1` / `core_risk.v1` separation assertion | DS F2 low | Rejected-with-reason | `StructuredFundDataBundle` has no equivalent fields; processor-layer Slice 3 tests already cover no leakage |
| Stub locality, timing variance, fixture anchor hardcoding | DS F3-F5 info | Rejected-with-reason | Informational only; no behavior, contract, or artifact correctness issue |
| Anchor source_kind / row_locator detail, partial facade behavior, real-report correctness | MiMo review | Deferred-with-owner | Belongs to processor/evidence or future gates, not Slice 4 blockers |

All accepted findings either fixed, rejected with valid reasoning, or deferred with owner. Zero open blockers.

## Binding Amendment Compliance

| # | Amendment | Status | Evidence |
|---|---|---|---|
| 1 | Only `manager_profile.v1`; no other families | PASS | See Q4 |
| 2 | Source-truth behind existing proof validation | PASS | Line 877; `_validate_source_truth_admission()` unchanged |
| 3 | Direct route suppresses candidate_evidence | PASS | Line 1108; binding amendment 4 test coverage |
| 4 | Direct-route missing test with `candidate_evidence == ()` | PASS | `test_manager_profile_source_truth_route_suppresses_candidate_evidence` line 2591 |
| 5 | Regression: `current_stage.v1` / `core_risk.v1` remain missing | PASS | Existing S6-F/S6-G tests pass; no leakage |
| 6 | No concentration/style-drift/current-stage/core-risk conclusions | PASS | `holdings_snapshot` emits disclosed rows only, no interpretation |
| 7 | `manager_alignment.judgment = None` | PASS | Line 1780 |
| 8 | Use only existing `EvidenceAnchor` and `FundExtractionGapCode` | PASS | No new types or gap codes |
| 9 | If facade insufficient, stop; no production `data_extractor.py` patch | PASS | Existing projection sufficient; zero production changes |
| 10 | Docs sync after tests pass, preserving NOT_READY | PASS | See Q3 |

## Residual Risks (Carried Forward)

| Risk | Severity | Owner | Destination |
|---|---|---|---|
| Real-report manager-profile field correctness remains unproven | HIGH | Future evidence worker | Separate evidence gate with live/manual verification |
| `holdings_snapshot` semantic overlap with `current_stage.v1` / `core_risk.v1` | MEDIUM | Future field-family gates | `current_stage.v1` / `core_risk.v1` planning gates must decide whether to share or re-extract |
| Broader holdings shapes (all-stock, bond, QDII/FOF) not covered | LOW | Future refinement owner | Future holdings refinement gate |
| Manager tenure normalization not implemented | LOW | Future refinement owner | Future manager-profile refinement gate |
| Manager alignment judgment remains `None` by design | LOW | Future analysis owner | Later CHAPTER_CONTRACT / analysis gate |
| `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` still lack FDD source-truth | MEDIUM | Controller / planning worker | Subsequent family planning gates |
| Facade partial/missing behavior beyond negative proof-missing route is processor-layer proof only | LOW | Processor/evidence owner | Future refinement only if needed |

## Stop Confirmation

- No code was changed during this review
- No staging, commit, push, PR, or merge was performed
- No next gate action was taken
- Release/readiness remains `NOT_READY`

## Verdict

**AGGREGATE_DEEPREVIEW_PASS**

All 5 aggregate review questions pass with evidence from code, tests, docs, and controller judgments. The work unit implements exactly `manager_profile.v1` proof-positive FDD source-truth direct extraction within the accepted plan and binding amendments. Source-truth admission is not weakened. All public semantics are preserved. No overclaiming in facade tests or docs sync. Scope is strictly `manager_profile.v1` with no cross-family leakage. All accepted slice review findings are fixed or correctly dispositioned.
