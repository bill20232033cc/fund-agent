# Code Review: return_attribution.v1 Source-truth Direct Extraction — Slice 2

## Gate And Slice

- Work unit: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`
- Gate: `Code Review Gate - Slice 2: Value extraction`
- Review role: review + backup fix (review only, no modifications)
- Artifact path: `docs/reviews/code-review-20260620-065511-mimo-return-attribution-source-truth-slice2.md`
- Reviewer: AgentMiMo
- Date: 2026-06-20

## Verdict

**PASS_WITH_FINDINGS**

## Findings

### Finding 1 — Non-blocking: `_normalize_return_attribution_value` deduplicates by value content only, not by locator identity

- **Severity**: Low (non-blocking)
- **File**: `fund_agent/fund/processors/fund_disclosure_processor.py`, lines 1681–1696
- **Detail**: `_resolve_return_attribution_candidate` (line 1653) normalizes candidates for conflict detection via `_normalize_return_attribution_value`. For `TrackingErrorValue`, normalization uses `f"{value.value_text}|{value.period_label}|{value.annualized}"` — the value text, period label, and annualized flag. For string values (NAV/benchmark/fee), normalization uses `_normalize_match_text(str(value))`.
  - The plan specifies: "Omit a subvalue when multiple stable candidates for the same output path conflict." The current implementation detects conflict when normalized values differ across candidates for the same output path, which is correct.
  - However, when multiple candidates have identical normalized values, `_resolve_return_attribution_candidate` returns `candidates[0]` (the first by insertion order). This is deterministic but does not consider locator identity (different table/cell/paragraph origins). If two different stable cells produce the same tracking error value text, both are accepted silently and only the first is returned. This is fail-closed (no conflicting values emitted) and the ambiguity gap is not triggered.
  - In contrast, the NAV/benchmark same-row logic (`_select_return_attribution_nav_benchmark_values`) does explicitly track locator identity (row pairs from different tables trigger `ambiguous_paths.add`).
- **Risk**: Minimal. Two independent stable sources disclosing the same actual tracking error or fee rate is not a data integrity issue. The scenario is unlikely in real FDD content.
- **Recommendation**: No fix required for this slice. If future evidence shows same-value-different-source conflicts are common in real FDD content, consider adding locator identity to the normalization key or triggering `ambiguous_paths` when multiple candidates share the same output path regardless of value equality.

## Required Fixes

None. The single finding is non-blocking.

## Scope Verification

### 1. Public value shape limited to `schema_version`, `nav_benchmark_performance`, `fee_schedule`, `tracking_error`

**PASS**. `_build_return_attribution_value` (lines 1699–1726) constructs the value dict with only these four keys. When all three subvalues are absent, it returns `{}` (empty dict). When any subvalue is present, it prepends `schema_version: "return_attribution.v1"`. No other top-level key is ever added. Test `test_return_attribution_source_truth_extracts_exact_value_shape` (line 1646) explicitly asserts `set(value) == {"schema_version", "nav_benchmark_performance", "fee_schedule", "tracking_error"}`.

### 2. `TrackingErrorValue` construction supplies all required fields and uses correct direct-disclosure semantics

**PASS**. `_return_attribution_tracking_error_value` (lines 1508–1550) constructs `TrackingErrorValue` with all fields:
- `value=ratio` (Decimal parsed from percent text)
- `value_text=value_text` (percent text as disclosed)
- `unit="ratio"`
- `period_label` (row/heading/table context)
- `period_start=None`, `period_end=None`
- `annualized` (from "年化" in context text)
- `source_type="direct_disclosure"`
- `calculation_method="disclosed"`
- `benchmark_identity_status="missing"`
- `benchmark_index_name=None`, `benchmark_index_code=None`
- `fund_series_source=None`, `index_series_source=None`
- `observation_count=None`
- `frequency="annual_report_period"`
- `annualization_factor=None`
- `input_period_complete=True`
- `provenance_note` (includes "直接披露")

All direct-disclosure semantics from the plan are correctly applied. Test `test_return_attribution_source_truth_extracts_exact_value_shape` (line 1711–1730) asserts every field.

### 3. NAV/benchmark same-row and fee parsing are deterministic and fail closed

**PASS**.
- NAV/benchmark: `_select_return_attribution_nav_benchmark_values` (lines 989–1064) requires both NAV and benchmark labels in the same `row_index` within the same table. `setdefault` ensures first-match-per-row. Multiple row pairs trigger `ambiguous_paths.add("nav_benchmark_performance")` and return empty dict. Zero pairs also return empty. Tests `test_return_attribution_source_truth_nav_requires_both_sides_same_row` (line 1835) covers both missing-side and different-row cases.
- Fee parsing: `_return_attribution_percent_text` (lines 1608–1626) requires a percent literal match. `_match_return_attribution_fee_cell_output_path` (lines 1180–1198) matches only allowed labels. One-sided fee is allowed as partial. Test `test_return_attribution_source_truth_fee_schedule_one_side_is_partial` (line 1806) verifies this.

### 4. Tracking error target/control/limit contexts are rejected

**PASS**. `_return_attribution_tracking_error_rejected` (lines 1570–1587) checks for reject context tokens ("目标", "控制", "不超过", "力争", "偏离度绝对值") in normalized text. Both table cell and paragraph paths call this check before accepting a tracking error candidate. Test `test_return_attribution_source_truth_rejects_tracking_error_target_context` (line 1929) uses a paragraph containing multiple reject tokens ("力争将跟踪误差控制在不超过4.00%，偏离度绝对值目标较低") and verifies `family.status == "missing"`.

### 5. Missing/partial/accepted status and `extraction_mode` are correct; direct route keeps `candidate_evidence == ()`

**PASS**.
- `_return_attribution_status` (lines 1928–1945): `accepted` when all three required top-level keys present; `partial` when any value present but not all three; `missing` when value is empty.
- `_extract_return_attribution_source_truth` (lines 909–946): `extraction_mode="missing"` when status is "missing", otherwise `"direct"`. `candidate_evidence=()` always.
- `_field_families_for_intermediate` (lines 778–781): sets `return_attribution_evidence = ()` when direct result is present.
- Tests cover all three status paths: accepted (line 1646), partial (line 1736), missing (line 1778), and candidate evidence suppression (line 1485).

### 6. No unauthorized schema expansion

**PASS**. No changes to `EvidenceSourceKind`, `EvidenceAnchor`, `FundFieldFamilyId`, `FundFieldFamilyResult`, `FundProcessorResult`, `FundDisclosureDocumentContentIntermediate`, or `FundDisclosureSourceTruthAdmissionProof`. The `_ReturnAttributionValueCandidate` dataclass (lines 187–195) is a private implementation detail, not a public schema.

### 7. No unauthorized source policy/repository/facade/docs changes

**PASS**. Only two production/test files changed. No changes to `FundDocumentRepository`, annual-report source policy, fallback policy, cache/PDF behavior, provider behavior, facade code, or documentation files.

### 8. No other field families affected

**PASS**. `_field_families_for_intermediate` (lines 797–811) uses a conditional expression that only overrides `product_essence.v1` and `return_attribution.v1` with their source-truth results; all other families follow existing candidate/missing paths unchanged.

### 9. No parser replacement, upper-layer consumption, readiness/release claim, or live/network commands

**PASS**. Evidence document explicitly states these boundaries. No readiness/release claim in code or test. No live/network commands in validation.

## Validation Reviewed

| Check | Result |
|---|---|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | 133 passed in 0.59s |
| `uv run ruff check ...processor.py ...test_processor.py` | All checks passed! |
| `git diff --check` | No whitespace errors |
| Plan compliance | All 4 implementation decisions from plan are correctly implemented |
| Slice 1 controller judgment acceptance | Reused; no regression |
| Scope boundary | No violations detected |

## Residual Risks

1. **Real-report field correctness unproven**: Synthetic test stubs validate extraction logic, not real FDD content parsing. Owner: later evidence gate.
2. **Same-value multi-source tracking error ambiguity**: As noted in Finding 1, identical values from different stable sources are silently accepted. Not a correctness issue but may warrant explicit ambiguity handling if real FDD content exhibits this pattern. Owner: later field-specific evidence/refinement gate.
3. **Facade projection regression not validated in this slice**: Existing `_bundle_from_processor_result()` already maps `return_attribution.v1` keys, but no facade regression test is added in this slice. Owner: later Slice 4 if authorized.
4. **Docs/design/README sync**: Not performed in this slice per plan. Owner: later docs sync slice.

## Final Recommendation

**CODE_REVIEW_PASS_NOT_READY**

Slice 2 implementation is correct and complete. One non-blocking finding (deduplication by value content only, not locator identity) does not affect correctness or fail-closed behavior. The implementation faithfully follows the accepted plan, maintains all scope boundaries, and passes all validation. Release/readiness remains `NOT_READY`.
