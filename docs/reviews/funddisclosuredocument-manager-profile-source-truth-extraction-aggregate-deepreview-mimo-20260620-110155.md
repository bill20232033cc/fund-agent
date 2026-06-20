# Aggregate Deepreview: FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Aggregate Deepreview Gate`
- Review range: `4286987..HEAD` (5 commits: plan, slices 1-4)
- Current HEAD: `f89ff07`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`, `docs/current-startup-packet.md`
- Accepted plan: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- Plan controller judgment: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-controller-judgment-20260620.md`
- Slice controller judgments:
  - `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice1-code-review-controller-judgment-20260620.md`
  - `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-code-review-controller-judgment-20260620.md`
  - `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice3-code-review-controller-judgment-20260620.md`
  - `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice4-code-review-controller-judgment-20260620.md`
- AgentMiMo role: aggregate review only
- Verdict: `AGGREGATE_DEEPREVIEW_PASS`

## Scope

- Mode: aggregate deepreview across Slices 1-4 (current branch changes)
- Branch: `funddisclosure-return-attribution-source-truth`
- Base: `4286987`
- Included scope: all files changed in commits `4286987..HEAD` covering manager_profile.v1 source-truth direct extraction implementation, tests, facade regression, and docs sync
- Excluded scope: unrelated untracked files, other field families, live/PDF/FDR/provider evidence
- Parallel review coverage: none (single reviewer)

## Aggregate Review Questions

### Q1. Across Slices 1-4, does manager_profile.v1 proof-positive FDD source-truth direct extraction satisfy the accepted plan without weakening source-truth admission?

**Yes.**

Evidence across all four slices:

- **Slice 1** (`fund_disclosure_processor.py:872-895`): Added `manager_profile_source_truth` local variable in `_field_families_for_intermediate()`. Direct extraction only fires when `source_truth_extraction_allowed and content_intermediate is not None`, reusing the same admission gate as `product_essence.v1` and `return_attribution.v1`. Candidate evidence suppressed to `()` when direct result is present. Base admission invalid paths (missing provenance, non-empty failure_class) still block before field-family route. Candidate-boundary input remains blocked.

- **Slice 2** (`fund_disclosure_processor.py:1072-1695`): Implemented `_extract_manager_profile_source_truth()` orchestrator and three value selectors (`_select_manager_profile_portfolio_managers`, `_select_manager_profile_strategy_text`, `_select_manager_profile_turnover_rate`). All read only from `FundDisclosureDocumentContentIntermediate` protocol fields (sections, paragraph_blocks, table_blocks, cells). All require `locator_stability == "stable"`. All build public `EvidenceAnchor` with `source_kind="annual_report"` and `page_number=None`. Proof-positive result always returns `candidate_evidence=()`.

- **Slice 3** (`fund_disclosure_processor.py:1698-2536`): Added `_select_manager_profile_alignment` and `_select_manager_profile_holdings_snapshot`. Status/gap functions correctly implement missing/partial/accepted semantics. `manager_alignment["judgment"]` is hardcoded to `None`. Holdings snapshot does not emit concentration, style drift, current-stage, or core-risk conclusions. `_manager_profile_cell_original_index` raises `ValueError` for foreign cells (fix from Slice 3 DS finding).

- **Slice 4** (`tests/fund/test_data_extractor.py:1222-1364`, `docs/design.md`, `fund_agent/fund/README.md`): Facade regression proves proof-positive values project to `StructuredFundDataBundle` fields. Negative regression proves proof-missing leaves all five bundle fields missing. Docs synced to state three families implemented, three remain unimplemented.

The admission guard chain is: `_validate_source_truth_admission()` validates proof type/candidate_boundary/failure_class/source_provenance/dispatch identity → only then does `_field_families_for_intermediate()` call `_extract_manager_profile_source_truth()`. No shortcut or bypass exists. `source_truth_extraction_allowed` remains the only direct route switch.

### Q2. Are public missing/partial/accepted semantics, candidate_evidence suppression, anchors, and existing gap taxonomy preserved?

**Yes.**

- **missing**: `_build_manager_profile_value()` returns `{}` when no top-level value is selected. `_manager_profile_status()` returns `"missing"`. `_manager_profile_source_truth_gaps()` emits `field_family_missing`. `extraction_mode` set to `"missing"`. (`fund_disclosure_processor.py:2402-2408`, `2508-2512`, `2468-2478`)

- **partial**: at least one but fewer than five top-level values present. `_manager_profile_status()` returns `"partial"`. `_manager_profile_source_truth_gaps()` emits `field_family_partial` per missing allowed top-level key. (`fund_disclosure_processor.py:2510-2511`, `2479-2490`)

- **accepted**: all five top-level values present AND `ambiguous_paths` is empty. (`fund_disclosure_processor.py:2508-2509`). Ambiguity keeps status `partial` even when all five values are present (Slice 3 DS finding fix, verified by targeted re-review).

- **candidate_evidence suppression**: `_extract_manager_profile_source_truth()` always returns `candidate_evidence=()`. In `_field_families_for_intermediate()`, `manager_profile_evidence = ()` when `manager_profile_source_truth is not None`. (`fund_disclosure_processor.py:1108`, `895-897`)

- **anchors**: all anchors use existing `EvidenceAnchor` shape with `source_kind="annual_report"`, `document_year` from context, `page_number=None`. Deduplication via existing `_dedupe_anchors()`. No anchors created for missing/deferred subkeys. (`fund_disclosure_processor.py:1095-1098`)

- **gap taxonomy**: uses only existing `FundExtractionGapCode` values: `field_family_missing`, `field_family_partial`, `ambiguous_table_or_locator`, `source_truth_admission_missing`, `source_truth_admission_invalid`, `candidate_only_not_source_truth`. No new taxonomy added. (`fund_disclosure_processor.py:2436-2491`)

### Q3. Are facade tests and docs sync consistent with implementation and not overclaiming?

**Yes.**

- **Facade positive test** (`test_data_extractor.py:1222`): Asserts all five `StructuredFundDataBundle` fields receive proof-positive values with correct shapes, `extraction_mode="direct"`, non-empty anchors. Also asserts unrelated fields (`investor_return`, `holder_structure`, `share_change`, `bond_risk_evidence`) remain `None`.

- **Facade negative test** (`test_data_extractor.py:1318`): Asserts proof-missing/candidate-only FDD route leaves all five manager-profile bundle fields as `value=None`, `anchors=()`, `extraction_mode="missing"`. Asserts `note` contains `field_not_in_family:manager_profile.v1:...` diagnostic.

- **docs/design.md** changes: Version bumped to v2.30. Status补充 correctly states `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1` have proof-positive FDD source-truth direct extraction. Correctly states `manager_profile.v1` direct value covers only five listed subvalues. Correctly lists `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` as unimplemented. Preserves `NOT_READY`, candidate-only, not-proven boundaries. No parser replacement, readiness/release, or EvidenceSourceKind expansion claims.

- **fund_agent/fund/README.md** changes: Three locations updated to reflect manager_profile.v1 as third implemented source-truth family. All three remaining families explicitly listed as unimplemented. No release, readiness, or correctness claims.

- **Control docs** (`docs/implementation-control.md`, `docs/current-startup-packet.md`): Updated to reflect Slice 4 acceptance and next entry point as Aggregate Deepreview Gate. No unauthorized scope expansion.

### Q4. Did the work stay exactly within manager_profile.v1, without implementing investor_experience.v1, current_stage.v1, core_risk.v1 or leaking holdings_snapshot into risk/stage?

**Yes.**

- Only five commits in range, all prefixed `gateflow: accept fdd manager profile source truth`.
- Changed files: `fund_agent/fund/processors/fund_disclosure_processor.py`, `tests/fund/processors/test_fund_disclosure_processor.py`, `tests/fund/test_data_extractor.py`, `docs/design.md`, `fund_agent/fund/README.md`, control docs, and review artifacts.
- No changes to `contracts.py`, `data_extractor.py` production code, `extractors/**`, `documents/**`, or any Service/UI/Host/renderer code.
- `_field_families_for_intermediate()` only routes `manager_profile.v1` into direct extraction; `investor_experience_evidence`, `current_stage_evidence`, `core_risk_evidence` continue to use their existing S6-D/E/F/G candidate selectors unchanged. (`fund_disclosure_processor.py:898-903`)
- Tests explicitly assert `current_stage.v1` and `core_risk.v1` remain `status="missing"`, `value={}`, `anchors=()` when manager_profile gets direct extraction. (`test_fund_disclosure_processor.py:2611-2616`, `2698-2701`)
- `holdings_snapshot` is emitted only as a `manager_profile.v1` subvalue. No code routes it into `current_stage.v1` or `core_risk.v1`.

### Q5. Are all accepted review findings from slice reviews fixed or correctly dispositioned?

**Yes.** Full disposition trace:

**Slice 1** (both DS and MiMo PASS, no findings): No fix required.

**Slice 2**:
| Finding | Disposition | Verified |
|---|---|---|
| Roster broad heading / heading_path self-authorization (DS F1) | accepted and fixed | DS + MiMo targeted re-reviews |
| Strategy body text false positive (DS F2 / MiMo 001) | accepted and fixed | DS + MiMo targeted re-reviews |
| Missing-key test assertion used dict.get() (MiMo 002) | accepted and fixed | DS + MiMo targeted re-reviews |
| Roster same-name conflict / identical duplicate coverage (DS F3/F4 / MiMo 003) | accepted and fixed | DS + MiMo targeted re-reviews |
| Strategy ambiguity test (MiMo optional) | deferred-with-owner | future refinement gate |

**Slice 3**:
| Finding | Disposition | Verified |
|---|---|---|
| `_manager_profile_status` could return accepted while ambiguity gaps existed (DS medium) | accepted and fixed | DS + MiMo targeted re-reviews |
| `_manager_profile_cell_original_index` silently returned 0 for foreign cell (DS low) | accepted and fixed | DS + MiMo targeted re-reviews |
| Table-backed manager_alignment positive path lacked coverage (DS residual) | accepted and fixed | DS + MiMo targeted re-reviews |

**Slice 4**:
| Finding | Disposition | Verified |
|---|---|---|
| Evidence residual table mislabeled (DS F1 low) | accepted and fixed | DS + MiMo targeted re-reviews |
| Positive facade regression does not assert current_stage/core_risk separation (DS F2 low) | rejected-with-reason | Slice 3 tests already cover; not required for Slice 4 |
| Stub locality, timing variance, fixture section anchor hardcoding (DS F3-F5 info) | rejected-reason | informational only |
| MiMo residual risks | deferred-with-owner | processor/evidence or future gates |

No accepted finding remains open. No new blocker was reported by any targeted re-review.

## Findings

未发现实质性问题。

Cross-slice verification details:

1. **Admission guard integrity**: `_validate_source_truth_admission()` at `fund_disclosure_processor.py:821-850` is unchanged by this work unit. It validates proof type, `candidate_boundary`, `failure_class`, `source_provenance`, and dispatch identity before any field-family direct route. `manager_profile.v1` uses the identical guard path as `product_essence.v1` and `return_attribution.v1`.

2. **Status/gap correctness**: `_manager_profile_status()` at line 2494-2512 correctly requires all five top-level values AND empty `ambiguous_paths` for `accepted`. This was a Slice 3 fix (DS medium finding) confirmed by targeted re-review. The `ambiguous_paths` condition prevents `accepted` status when internal ambiguity exists.

3. **Candidate evidence isolation**: proof-positive direct route always returns `candidate_evidence=()` (line 1108). In `_field_families_for_intermediate()` (lines 895-897), `manager_profile_evidence = ()` when direct result exists. Proof-missing path falls through to `_select_manager_profile_candidate_evidence()` (line 898). No S6-D candidate records leak into direct-route output.

4. **Holdings snapshot boundary**: `_select_manager_profile_holdings_snapshot()` emits only `top_holdings`, `top_holdings_status`, `top_holdings_source`, `industry_distribution`, `industry_distribution_status`. No concentration, style drift, current-stage, core-risk, share-change, or QDII/FOF conclusions. This is enforced by code structure (no such keys exist in the value dict) and by test assertion (`test_manager_profile_source_truth_extracts_holdings_snapshot_without_risk_or_stage_fields`).

5. **Alignment judgment boundary**: `manager_alignment["judgment"]` is hardcoded to `None` at line 1780. No inference of motivation or interests alignment exists.

6. **Docs sync truthfulness**: `docs/design.md` v2.30 and `fund_agent/fund/README.md` accurately reflect implemented facts. All three remaining families explicitly listed as unimplemented. `NOT_READY`, candidate-only, and not-proven boundaries preserved throughout. No overclaiming of parser replacement, readiness/release, EvidenceSourceKind expansion, or upper-layer direct candidate consumption.

7. **Facade projection sufficiency**: No `data_extractor.py` production code was changed. Existing `_field_from_family()` already returns missing `ExtractedField` when a top-level key is absent. Slice 4 facade tests prove the existing projection path works for all five manager_profile bundle fields.

## Open Questions

无。

## Residual Risk

| Risk | Owner | Destination |
|---|---|---|
| Real-report manager-profile field correctness remains unproven | Future evidence worker | Separate evidence gate |
| `holdings_snapshot` shared relevance to `current_stage.v1` and `core_risk.v1` | Future field-family gates | `current_stage.v1` / `core_risk.v1` planning gates |
| Broader holdings shapes (all-stock details, bond holdings, QDII/FOF) | Future refinement gate | Later field-family refinement |
| Manager tenure normalization and current-manager inference | Future refinement gate | Later manager-profile refinement |
| Manager alignment judgment | Future analysis/template gate | Later CHAPTER_CONTRACT / analysis gate |
| Strategy ambiguity semantics beyond heading-gated concatenation | Future refinement owner | Future manager-profile refinement gate |
| `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` still lack FDD source-truth direct extraction | Controller / planning worker | Subsequent field-family planning gates |

All residual risks were already identified in the plan controller judgment and slice controller judgments. None are new. None block this aggregate gate.

## Validation

```text
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
194 passed in 0.88s
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
All checks passed!
```

```text
git diff --check
<no output>
```

## Verdict

`AGGREGATE_DEEPREVIEW_PASS`
