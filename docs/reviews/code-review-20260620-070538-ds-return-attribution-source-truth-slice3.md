# Code Review: FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction — Slice 3 Anchor/Gap Hardening

## Gate Metadata

- Gate: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Implementation Gate`
- Slice: `Slice 3: Anchor/Gap Hardening`
- Classification: `heavy`
- Reviewer: AgentDS (review-only)
- Review target: working tree diff (uncommitted)
- Artifact path: `docs/reviews/code-review-20260620-070538-ds-return-attribution-source-truth-slice3.md`
- Accepted references:
  - Plan: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
  - Slice 2 controller: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice2-code-review-controller-judgment-20260620.md`
  - Slice 3 evidence: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice3-implementation-evidence-20260620.md`
- Verdict: `PASS`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py` — 5 lines changed (3 removed, 4 added)
- `tests/fund/processors/test_fund_disclosure_processor.py` — 91 lines added

## Findings

### F1: Redundant Assignment Cleanup Preserves Proof-Positive Candidate Suppression (No Issue)

**File/Line**: `fund_agent/fund/processors/fund_disclosure_processor.py:778-782`

The old code unconditionally called `_select_return_attribution_candidate_evidence(intermediate)` then overwrote the result with `()` when `return_attribution_source_truth is not None`. The new code matches the established `product_essence_evidence` pattern: call the candidate selector only when source truth is `None`.

Behavioral equivalence verified:

| Condition | Old | New |
|---|---|---|
| Source truth present (`is not None`) | `()` | `()` |
| Source truth absent (`is None`) | `_select_...()` result | `_select_...()` result |

Validation: all 58 selector tests pass. `test_return_attribution_source_truth_route_suppresses_candidate_evidence` confirms proof-positive path has `candidate_evidence == ()`. `test_return_attribution_selector_adds_candidate_evidence_only` confirms proof-missing path still collects candidate evidence.

### F2: Table-Cell Tracking-Error Rejection Test Correctly Exercises Table Path (No Issue)

**File/Line**: `tests/fund/processors/test_fund_disclosure_processor.py:2019-2049`

This test fills the Slice 2 controller's finding #3 gap: "No table-cell-specific tracking-error rejection test was added."

Code path trace:

1. Cell `row_label_path=("跟踪误差控制目标",)`, `cell_text="不超过4.00%"`
2. `_return_attribution_cell_context_text()` concatenates table headers, heading_path, row_label_path, column_header_path, cell_text → context_text contains "跟踪误差控制目标" and "不超过4.00%"
3. `_return_attribution_mentions_tracking_error()` matches "跟踪误差" substring in "跟踪误差控制目标"
4. `_return_attribution_tracking_error_rejected()` matches both "控制" and "目标" from `_RETURN_ATTRIBUTION_TRACKING_ERROR_REJECT_CONTEXT` → returns `True`
5. Cell rejected before percent parsing — no candidate created
6. Family remains `missing`, `value={}`, `anchors=()`

The test exercises the table-cell branch of `_collect_return_attribution_tracking_error_candidates()` (lines 1136-1171), which is distinct from the paragraph branch (lines 1172-1177) already covered by `test_return_attribution_source_truth_rejects_tracking_error_target_context`.

### F3: NAV/Benchmark Ambiguity Test Correctly Asserts Fail-Closed Behavior (No Issue)

**File/Line**: `tests/fund/processors/test_fund_disclosure_processor.py:1890-1945`

This test creates two rows each with a valid NAV+benchmark pair:

- Row 0: NAV "8.00%" (col 1) + Benchmark "6.00%" (col 2)
- Row 1: NAV "9.00%" (col 1) + Benchmark "7.00%" (col 2)

Code path trace:

1. `_select_return_attribution_nav_benchmark_values()` groups by row_index
2. Both rows have complete pairs → `len(row_pairs) == 2 > 1`
3. `ambiguous_paths.add("nav_benchmark_performance")` executed
4. Function returns `{}` — no NAV/benchmark pair emitted
5. No other value candidates exist → `_build_return_attribution_value({})` returns `{}`
6. `_return_attribution_source_truth_gaps({}, {"nav_benchmark_performance"})` produces:
   - `ambiguous_table_or_locator` gap with `source_field_path="nav_benchmark_performance"`
   - `field_family_missing` gap
7. Status derived as `"missing"`

All assertions verified against implementation logic. The test correctly documents that multi-row ambiguity fails closed with both gap types.

### F4: Scope Boundary Preserved (No Issue)

Verified no:
- Other field family changes (`manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` untouched)
- Schema expansion (`EvidenceAnchor`, `EvidenceSourceKind`, `FundFieldFamilyResult`, processor contract unchanged)
- Public value shape changes (same `schema_version`, top-level keys, `TrackingErrorValue` structure)
- Anchor schema or `source_kind` changes
- Parser replacement
- Source/repository/facade/docs modifications
- Readiness or real-report correctness claims

### F5: Same-Value Different-Locator Deduping Unchanged (Non-Blocking, Previously Accepted)

The Slice 2 controller accepted this behavior (finding #4). Slice 3 does not change it. The evidence document explicitly confirms this decision. No new risk introduced.

## Required Fixes

None.

## Residual Risks

1. **Table-cell tracking error rejection relies on label context matching**. If a real-report table cell contains an actual tracking-error value in a row whose label text also contains a reject-context token (e.g., a row labeled "跟踪误差控制机制说明" alongside a separate row for actual tracking error), the current implementation could false-negative reject the actual value. Owner: future real-report evidence gate.
2. **Same-value duplicate disclosures from different stable locators** continue to accept the first locator. Owner: future field-specific refinement gate if real-report evidence proves unsafe.
3. **Real-report field correctness** remains unproven for all three subvalues. Owner: later evidence gate.
4. **Remaining four FDD field families** (`manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, `core_risk.v1`) remain missing for source-truth direct extraction. Owner: separate future gates.

## Validation Reviewed

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
→ 135 passed in 0.65s (Slice 2: 133; +2 new tests)

uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
→ All checks passed!

git diff --check
→ PASS: no output
```

All new tests individually verified. All existing return_attribution tests (20) and selector tests (58) pass.

## Recommendation

`CODE_REVIEW_PASS_NOT_READY`
