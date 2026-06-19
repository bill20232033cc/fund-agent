# Plan Review: return_attribution.v1 Source-truth Direct Extraction

## Review Metadata

- **Review artifact**: `docs/reviews/plan-review-20260620-063812-ds-return-attribution-source-truth.md`
- **Plan under review**: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
- **Role**: AgentDS (review-only)
- **Review classification**: standard planreview — adversarial review of plan correctness, scope, boundary adherence, contract consistency, and test adequacy

## Verdict: PASS_WITH_FINDINGS

## Design/Control Truth Referenced

- `AGENTS.md` — Processor/Extractor boundary, no direct candidate consumption by upper layers
- `docs/design.md` v2.29 — Source-truth Slice A/B/C current state; only `product_essence.v1` has FDD direct extraction
- `docs/implementation-control.md` — current gate is PR #29 disposition accepted; next entry is separate future gate only
- `docs/current-startup-packet.md` — S6-C return attribution remains candidate evidence only; NOT_READY

## Code Truth Referenced

- `fund_agent/fund/processors/fund_disclosure_processor.py` — `_field_families_for_intermediate()` (line 688-758), `_validate_source_truth_admission()` (line 761-807), `_extract_product_essence_source_truth()` (line 810-847), `_select_return_attribution_candidate_evidence()` (line 1807-1838), `_candidate_missing_field_family()` (line 3492-3533), `_missing_field_family()` (line 3536-3575), `_with_source_truth_admission_gap()` (line 3577-3618), `_derive_contract_status()` (line 1493-1513), `_dedupe_anchors()` (line 1516-1536), `_content_intermediate_or_none()` (line 1539-1559)
- `fund_agent/fund/processors/active_annual.py` — `FIELD_FAMILY_MAPPINGS` return_attribution.v1 rows (line 105-112), `_build_field_family_result()` (line 331-384)
- `fund_agent/fund/extractors/performance.py` — `_build_nav_benchmark_performance()` (line 1052-1097), `_extract_tracking_error()` (line 395-450), `TrackingErrorValue` construction pattern
- `fund_agent/fund/extractors/profile.py` — `_build_fee_schedule()` (line 982-1016) value shape: `{"management_fee": ..., "custody_fee": ...}`
- `fund_agent/fund/extractors/models.py` — `TrackingErrorValue` (line 593-637), `EvidenceAnchor` (line 87-107)
- `fund_agent/fund/data_extractor.py` — `_active_processor_result_to_bundle()` return_attribution projection (line 731-759), `_tracking_error_for_fund_type()` (line 910-939)
- `fund_agent/fund/processors/contracts.py` — `FundExtractionGapCode` (line 43-62), `FundFieldFamilyResult` (line 571-619), `FundExtractionSourceBoundary` (line 63-74)
- `tests/fund/processors/test_fund_disclosure_processor.py` — existing source-truth admission tests (line 435+), product_essence source-truth tests (line 576+), return_attribution candidate-only tests (line 1423+)
- `tests/fund/test_data_extractor.py` — `test_explicit_disclosure_intermediate_routes_to_registry` (line 1092)

## Blocking Findings

None.

## Non-blocking Findings

### Finding 1: TrackingErrorValue field completeness is underspecified but not blocking

**Plan reference**: line 204-215 (TrackingErrorValue construction specification)

**Code truth**: `TrackingErrorValue` (`extractors/models.py` line 593-637) has 20 fields. The plan explicitly specifies 14 fields (value, value_text, unit, period_label, annualized, source_type, calculation_method, benchmark_identity_status, frequency, provenance_note). It does not explicitly name: `period_start`, `period_end`, `benchmark_index_name`, `benchmark_index_code`, `fund_series_source`, `index_series_source`, `observation_count`, `annualization_factor`, `input_period_complete`.

**Assessment**: For direct-disclosure semantics, all unnamed fields default to `None` (or `True` for `input_period_complete` in the existing `_extract_tracking_error()` pattern at `performance.py` line 444). The plan explicitly says "Use direct-disclosure semantics" and references the existing `TrackingErrorValue` type. An implementation worker reading the code truth would see the existing `_extract_tracking_error()` construction pattern (performance.py line 426-449) and follow it. The risk of the implementation worker omitting required fields is low because `TrackingErrorValue.__init__` will fail at construction time.

**Recommendation**: Implementation worker should explicitly verify that the `TrackingErrorValue` constructor receives all required fields by following the existing pattern in `performance.py` line 426-449. This finding does not require plan amendment.

### Finding 2: `input_period_complete` default is implicit

**Plan reference**: line 204-215

**Code truth**: `TrackingErrorValue.input_period_complete: bool` has no default value. The existing direct-disclosure pattern sets it to `True` (performance.py line 444).

**Assessment**: The plan does not specify this boolean. For FDD source-truth extraction, `True` is the correct default since the extraction uses complete annual-report content. Implementation worker should explicitly set it. Low risk.

### Finding 3: Fee schedule paragraph fallback scope is narrower than existing extractor

**Plan reference**: line 192 — "paragraph fallback only for explicit `管理费率：...` / `托管费率：...` labeled text"

**Code truth**: The existing `profile.py` `_build_fee_schedule()` has a sophisticated `7.4.10.2` subsection fallback mechanism (line 227-323) that handles both paragraph text and table-semantic extraction with subsection boundary detection, context tracking, and fee rate pattern matching.

**Assessment**: The plan's fee extraction scope for FDD content is intentionally narrower than the existing `ParsedAnnualReport`-based extractor. The plan's paragraph-only approach for FDD is reasonable because:
1. FDD content provides stable locators (cell/paragraph/table IDs) rather than raw subsection scanning
2. The table/cell path is prioritized before paragraph fallback
3. The plan explicitly says "Do not change `product_essence.v1`" — so the existing `profile.py` extractor path is untouched
4. Sales service fee remains candidate-only, preserving boundary

The plan correctly notes (risk at line 467) that FDD content may not have enough sibling/header information for safe extraction, and mitigation is to emit partial/missing with local gaps.

### Finding 4: Active-fund tracking error facade suppression is correctly deferred

**Plan reference**: line 380-388 (Slice 4), line 469 (risk)

**Code truth**: `_tracking_error_for_fund_type()` (`data_extractor.py` line 910-939) marks tracking error as missing for non-index funds with note "非指数基金不适用跟踪误差." The FDD processor's `return_attribution.v1` tracking_error value would be suppressed downstream by this facade function for active funds.

**Assessment**: The plan correctly identifies this as current facade behavior, not a processor bug. The plan says "do not change it unless a failing test proves a boundary mismatch." This is the correct disposition: the processor extracts what the document discloses; the facade decides what downstream consumers see. If the team later decides active-fund tracking error should surface (e.g., for Chapter 6 risk assessment), that's a separate facade policy gate.

### Finding 5: Plan says page_number is None for FDD anchors, which matches existing product_essence pattern

**Plan reference**: line 135 — "`page_number` remains `None` for FDD content when no page-level source-truth mapping exists"

**Code truth**: The existing `_product_essence_cell_anchor()` (`fund_disclosure_processor.py` line 996-1030) sets `page_number=None` for FDD cell anchors. The plan's anchor specification is consistent with this pattern.

### Finding 6: No candidate evidence for direct source-truth family

**Plan reference**: Slice 1 — "Set `return_attribution_evidence = ()` when direct result is present"

**Code truth**: The existing `_field_families_for_intermediate()` lines 720-724 show this pattern for `product_essence.v1`: `product_essence_evidence = () if product_essence_source_truth is not None else _select_product_essence_candidate_evidence(intermediate)`. The plan correctly follows this pattern.

### Finding 7: `_derive_contract_status()` interaction correctly acknowledged

**Plan reference**: line 155-157

**Code truth**: `_derive_contract_status()` (line 1493-1513) derives `partial` when any family is `accepted` or `partial`. If `return_attribution.v1` transitions from missing to accepted/partial while other families remain missing, the contract status changes from `missing` to `partial`. This is explicitly described in the plan's state machine section and is correct behavior.

## Test Coverage Assessment

### Tests specified by plan vs existing test patterns

| Plan slice | Tests specified | Follows existing pattern |
|---|---|---|
| Slice 1: Admission guard | `test_return_attribution_source_truth_requires_proof_even_when_candidate_boundary_none()` | Yes — mirrors `test_product_essence_source_truth_requires_proof_even_when_candidate_boundary_none()` (line 670) |
| Slice 1: Admission guard | `test_return_attribution_source_truth_rejects_failure_class_at_base_admission()` | Yes — mirrors `test_product_essence_source_truth_rejects_failure_class_at_base_admission()` (line 745) |
| Slice 2: Value extraction | `test_return_attribution_source_truth_extracts_exact_value_shape()` | Yes — mirrors `test_product_essence_source_truth_extracts_exact_value_shape()` (line 576) |
| Slice 2: Value extraction | `test_return_attribution_source_truth_partial_when_required_groups_missing()` | Yes — mirrors `test_product_essence_source_truth_partial_when_required_groups_missing()` (line 1098) |
| Slice 2: Value extraction | `test_return_attribution_source_truth_missing_keeps_family_missing()` | Yes — mirrors `test_product_essence_source_truth_missing_keeps_family_missing()` (line 1063) |
| Slice 3: Anchors/gaps | `test_return_attribution_source_truth_ambiguous_duplicate_omits_conflicting_path()` | Yes — mirrors `test_product_essence_source_truth_ambiguous_duplicate_omits_conflicting_path()` (line 789) |
| Slice 3: Anchors/gaps | `test_return_attribution_source_truth_skips_unstable_table_or_cell_locator()` | Yes — mirrors `test_product_essence_source_truth_skips_unstable_table_or_cell_locator()` (line 896) |
| Slice 3: Anchors/gaps | `test_return_attribution_source_truth_rejects_tracking_error_target_or_limit_context()` | New — specific to tracking_error fail-closed rules |
| Slice 4: Facade | Facade regression in `test_data_extractor.py` | Yes — follows `test_explicit_disclosure_intermediate_routes_to_registry` pattern (line 1092) |

**Additional tests that should exist but are not listed in the plan**:
- Tracking error direct disclosure with table+text inconsistency (parallel to existing `_TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT`)
- Tracking error multi-match rejection
- Fee schedule with only one of management_fee/custody_fee → partial
- Nav/benchmark with only one of the pair → partial (not same-row)
- Candidate evidence is empty when source truth is present

These are implicit in the plan's fail-closed rules but not explicitly enumerated as test names. The plan's general test structure ("prove accepted/partial/missing direct extraction behavior" at Slice 2 completion signal) provides sufficient guidance. The implementation worker should exercise judgment for edge cases.

## Scope Boundary Verification

### What the plan correctly excludes

| Constraint | Plan adherence |
|---|---|
| No parser replacement | ✓ — explicitly in non-goals (line 30) and repeated throughout |
| No other field families | ✓ — line 27-28 explicitly excludes manager_profile, investor_experience, current_stage, core_risk |
| No EvidenceSourceKind expansion | ✓ — line 139-140 |
| No EvidenceAnchor expansion | ✓ — line 140-141 |
| No new FundFieldFamilyId | ✓ — line 141 |
| No new FundFieldFamilyResult fields | ✓ — line 141-142 |
| No source provenance schema change | ✓ — line 142 |
| No Service/UI/Host/renderer/quality-gate changes | ✓ — line 161-162 |
| No LLM prompt consumption of candidate artifacts | ✓ — line 162 |
| No live/network/PDF commands | ✓ — repeatedly enforced in forbidden validation |
| No candidate-only fields in public value | ✓ — line 127 |
| No derived tracking error from NAV/benchmark | ✓ — line 321 |
| No fee expansion to sales service fee | ✓ — line 323-324 |
| No cross-year or NAV-series computation | ✓ — line 325 |

### What the plan correctly reuses

| Reused mechanism | Plan reference |
|---|---|
| `source_truth_extraction_allowed` from existing admission guard | line 169 |
| `_validate_source_truth_admission()` unchanged | line 169-176, stop condition line 283 |
| `_dedupe_anchors()` | line 234, 347 |
| `_derive_contract_status()` unchanged | line 154-158 |
| `FundFieldFamilyResult` contract unchanged | line 265 |
| `TrackingErrorValue` type unchanged | line 204 |
| `FundExtractionGapCode` existing values only | line 230-232 |
| `EvidenceAnchor` with `source_kind="annual_report"` | line 131-135 |

### Gap code usage audit

All gap codes proposed by the plan are existing valid `FundExtractionGapCode` literals (`contracts.py` line 43-62):

| Gap code | Used by plan | Exists in code |
|---|---|---|
| `field_family_missing` | line 230 | ✓ line 44 |
| `field_family_partial` | line 231 | ✓ line 45 |
| `ambiguous_table_or_locator` | line 232 | ✓ line 60 |
| `source_truth_admission_missing` | (reused via existing guard) | ✓ line 57 |
| `source_truth_admission_invalid` | (reused via existing guard) | ✓ line 58 |
| `candidate_only_not_source_truth` | (reused via existing `_candidate_missing_field_family`) | ✓ line 56 |

No new gap code is needed. ✓

## Value Shape Contract Verification

### return_attribution.v1 value shape: Plan vs ActiveFundAnnualProcessor

| Plan key | ActiveFundAnnualProcessor mapping | Match |
|---|---|---|
| `schema_version: "return_attribution.v1"` | `value["schema_version"] = field_family_id` (line 356) | ✓ |
| `nav_benchmark_performance` | `performance.nav_benchmark_performance` → `value["nav_benchmark_performance"]` (line 108) | ✓ |
| `fee_schedule` | `profile.fee_schedule` → `value["fee_schedule"]` (line 112) | ✓ |
| `tracking_error` | `performance.tracking_error` → `value["tracking_error"]` (line 111) | ✓ |

### Subvalue shapes: Plan vs extractors

| Subvalue | Plan shape | Extractor shape | Match |
|---|---|---|---|
| `nav_benchmark_performance` | `{"nav_growth_rate": ..., "benchmark_return_rate": ...}` | `performance.py` line 1091-1093: same shape | ✓ |
| `fee_schedule` | `{"management_fee": ..., "custody_fee": ...}` | `profile.py` line 1009-1011: same shape | ✓ |
| `tracking_error` | `TrackingErrorValue` with direct-disclosure semantics | `performance.py` line 426-449: same type, same semantics | ✓ |

### Bundle projection: Plan vs data_extractor.py

| Bundle field | Projection source | Plan acknowledges |
|---|---|---|
| `fee_schedule` | `_field_from_family(return_attribution, "fee_schedule")` (line 756) | ✓ — plan line 85 |
| `nav_benchmark_performance` | `_field_from_family(return_attribution, "nav_benchmark_performance")` (line 757) | ✓ — plan line 85 |
| `tracking_error` | `_field_from_family(return_attribution, "tracking_error")` then `_tracking_error_for_fund_type()` (line 758-759) | ✓ — plan line 85, facade behavior acknowledged at line 380-388 |

## Required Plan Fixes

None. The plan is code-generation-ready without amendment.

## Residual Risks

1. **FDD content protocol adequacy** (plan line 467): The FDD content protocols may not contain enough sibling/header information for all three subvalues. Mitigation is already specified: emit partial/missing with local gaps, do not broaden schema.
2. **Tracking error target/control confusion** (plan line 468): The plan's label-based rejection (`目标`, `控制`, `不超过`, `力争`, `偏离度绝对值`) is sound but may not cover all real-report patterns. Mitigation: fail closed when uncertain.
3. **Active-fund tracking error facade suppression** (plan line 469): The facade currently marks tracking error missing for active funds. This is deferred to a separate gate. No action needed now.
4. **Docs over-updating risk** (plan line 471): Mitigation specified: update only current implemented scope and preserve NOT_READY.

## Final Recommendation

**Recommendation Token: PLAN_REVIEW_PASS_NOT_READY**

The plan is code-generation-ready for exactly one field family, `return_attribution.v1`. It correctly:
- Reuses the existing source-truth admission proof guard without weakening it
- Follows the accepted `product_essence.v1` direct extraction pattern
- Uses only existing `FundExtractionGapCode` values
- Matches existing `ActiveFundAnnualProcessor` / bundle projection value shapes
- Respects all boundary constraints: no parser replacement, no schema expansion, no upper-layer changes, no other field families
- Specifies fail-closed rules for all uncertain extraction paths
- Has adequate test coverage mapped to existing test patterns
- Acknowledges the active-fund tracking error facade edge case

The plan does NOT authorize real-report correctness, parser replacement, source policy changes, Service/UI/Host/renderer/quality-gate consumption, or other field families. Release/readiness remains `NOT_READY`.
