# Plan Review: return_attribution.v1 Source-truth Direct Extraction

## Review Metadata

- Review target: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
- Reviewer: AgentMiMo
- Classification: heavy (public field-family output path change under Processor/Extractor boundary)
- Date: 2026-06-20

## Verdict

**PASS_WITH_FINDINGS**

## Review Scope

Assessed whether the plan is code-generation-ready for exactly one field family `return_attribution.v1` without violating:
1. Source-truth admission contracts
2. Public value/anchor contracts
3. Existing gap taxonomy
4. Processor/Extractor boundaries
5. No parser replacement
6. NOT_READY constraints

## Blocking Findings

None.

## Non-blocking Findings

### Finding 1: TrackingErrorValue missing field specifications

**Severity**: non-blocking (implementation residual)

**Location**: Plan "Implementation Decisions > Allowed Field Selection > tracking_error"

**Evidence**: `fund_agent/fund/extractors/models.py:593-637` — `TrackingErrorValue` has 18 required fields. The plan specifies 10 fields explicitly (`value`, `value_text`, `unit`, `period_label`, `annualized`, `source_type`, `calculation_method`, `benchmark_identity_status`, `frequency`, `provenance_note`) but does not specify the remaining 8: `period_start`, `period_end`, `benchmark_index_name`, `benchmark_index_code`, `fund_series_source`, `index_series_source`, `observation_count`, `annualization_factor`.

**Impact**: Implementation worker must infer these should be `None` from the direct-disclosure semantics and the existing `_extract_tracking_error()` pattern in `fund_agent/fund/extractors/performance.py:395-478`. The plan's `provenance_note` specification ("direct annual-report disclosure; no benchmark-return/stddev derivation") strongly implies `None` for all 8 fields, but this is implicit.

**Recommendation**: Implementation worker should set all 8 unspecified fields to `None` consistent with direct-disclosure semantics. No plan correction required.

### Finding 2: `period_label` fallback wording

**Severity**: non-blocking (minor ambiguity)

**Location**: Plan "Implementation Decisions > Allowed Field Selection > tracking_error > period_label"

**Evidence**: Plan says "row/heading/table context when available; fallback to `annual_report_period`". The string `"annual_report_period"` is not a valid `TrackingErrorValue.period_label` value — it's a `frequency` literal. The existing `_extract_tracking_error()` in `performance.py` uses row/heading context for `period_label` and `"annual_report_period"` for `frequency`.

**Impact**: Low. The plan's intent is clear (fallback `period_label` to a descriptive string), but the specific fallback string `"annual_report_period"` as `period_label` would be semantically inconsistent. The implementation worker should use a descriptive fallback like `"报告期"` or the heading text rather than the frequency literal.

**Recommendation**: Implementation worker should use a human-readable fallback for `period_label`, not the frequency literal. No plan correction required; the plan's overall intent is sound.

### Finding 3: `_tracking_error_for_fund_type` facade behavior not explicitly tested

**Severity**: non-blocking (residual risk)

**Location**: Plan "Implementation Decisions > Facade/test/docs sync" and `fund_agent/fund/data_extractor.py:910-939`

**Evidence**: The facade's `_tracking_error_for_fund_type()` marks non-index-fund tracking error as `missing`. The plan mentions this in Slice 4 ("if `tracking_error` active-fund post-processing intentionally marks non-index tracking error missing, record it as current facade behavior") but does not specify whether the facade regression test should assert this behavior for FDD-sourced tracking error.

**Impact**: The existing `_bundle_from_processor_result()` already projects `return_attribution.v1` value keys through `_field_from_family()` (data_extractor.py:756-759). If FDD emits a valid `tracking_error` in the value dict, the facade will project it through `_tracking_error_for_fund_type()`. For non-index funds, this will mark it `missing`. This is existing facade behavior, not a bug. But the plan's Slice 4 test should explicitly assert this to prevent future confusion.

**Recommendation**: Slice 4 facade test should assert that FDD-sourced `tracking_error` for non-index funds is projected as `missing` by `_tracking_error_for_fund_type()`. This is a test completeness issue, not a code change.

### Finding 4: Fee schedule paragraph fallback scope

**Severity**: non-blocking (design clarity)

**Location**: Plan "Implementation Decisions > Allowed Field Selection > fee_schedule"

**Evidence**: The plan allows paragraph fallback "only for explicit `管理费率：...` / `托管费率：...` labeled text". The existing `_build_fee_schedule()` in `profile.py:982` uses `_FIELD_PATTERNS["management_fee"]` and `_FIELD_PATTERNS["custody_fee"]` which match `管理费率` and `托管费率` patterns. The FDD direct extractor should use the same label set.

**Impact**: The plan's label set (`管理费率`, `管理费`, `托管费率`, `托管费`) is slightly broader than the existing pattern but consistent with the `_RETURN_ATTRIBUTION_MATCH_GROUPS` labels already defined in `fund_disclosure_processor.py:119-131`. No conflict.

**Recommendation**: None. The plan's label set is consistent with existing code.

### Finding 5: `schema_version` in value dict

**Severity**: non-blocking (verification)

**Location**: Plan "Contract / Schema / State-machine / Public-interface Changes > Value shape"

**Evidence**: Plan says top-level keys include `schema_version: "return_attribution.v1"`. The existing `active_annual.py:356` sets `value: dict[str, object] = {"schema_version": field_family_id}` where `field_family_id` is `"return_attribution.v1"`. The `_field_from_family()` in `data_extractor.py:606` does `family_result.value.get(field_name)`, so `schema_version` in the value dict does not interfere with field projection.

**Impact**: None. The plan correctly specifies this.

**Recommendation**: None.

## Verification Matrix

| Check | Result | Evidence |
|---|---|---|
| Gap codes are valid `FundExtractionGapCode` values | PASS | `field_family_missing`, `field_family_partial`, `ambiguous_table_or_locator` all in contracts.py:43-62 |
| Value shape matches `ActiveFundAnnualProcessor` bundle projection | PASS | `schema_version`, `nav_benchmark_performance`, `fee_schedule`, `tracking_error` match active_annual.py:356 and data_extractor.py:756-758 |
| `TrackingErrorValue` construction matches public type | PASS | All specified fields match models.py:593-637; 8 unspecified fields are `None`-able in direct-disclosure semantics |
| nav/benchmark same-row extraction deterministic | PASS | Plan requires unique same-row pair; ambiguous pairs produce gap, not guess |
| Fee parsing deterministic | PASS | Plan requires explicit rate text; rejects label-only cells |
| No parser replacement authorized | PASS | Plan explicitly forbids in Non-goals |
| No source policy changes authorized | PASS | Plan explicitly forbids in Non-goals |
| No Service/UI/Host/renderer/quality-gate consumption | PASS | Plan explicitly forbids in Non-goals |
| No other field families authorized | PASS | Plan scopes to `return_attribution.v1` only |
| NOT_READY preserved | PASS | Plan explicitly preserves throughout |
| Offline validation only | PASS | Plan forbids live/network/PDF commands |

## Required Plan Fixes

None. All findings are non-blocking implementation residuals.

## Final Recommendation

**PLAN_REVIEW_PASS_NOT_READY**

The plan is code-generation-ready for exactly one field family `return_attribution.v1`. It correctly reuses the existing source-truth admission proof mechanism, follows the `product_essence.v1` extraction pattern, respects all boundary constraints, and preserves NOT_READY. The five non-blocking findings are implementation-level clarifications that the worker can resolve from existing code patterns without plan revision.
