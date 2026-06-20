# FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Aggregate Deepreview Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`
- Gate: Aggregate Deepreview Gate
- Branch: `funddisclosure-core-risk-source-truth`
- Reviewed range: `origin/funddisclosure-current-stage-source-truth..HEAD`
- Accepted commits:
  - `75cd23d` plan
  - `8332595` implementation / code review
- Aggregate deepreviews:
  - `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-aggregate-deepreview-ds-20260620.md`
  - `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-aggregate-deepreview-mimo-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-aggregate-deepreview-controller-judgment-20260620.md`

## Verdict

`ACCEPT_AGGREGATE_DEEPREVIEW_READY_FOR_COMMIT_NOT_READY`

AgentDS and AgentMiMo both returned `AGGREGATE_DEEPREVIEW_PASS`. No aggregate deepreview finding remains open.

## Controller Decision

The core-risk work unit is accepted through aggregate deepreview for exactly one source-truth subvalue:

- `core_risk.v1.risk_characteristic_text`

The implementation remains bounded to proof-positive `FundDisclosureDocument` direct extraction. It does not implement complete `core_risk.v1` source truth and does not promote `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, or `concentration_risk` to public values or anchors.

## Accepted Evidence

- Plan and implementation are consistent across all five accepted slices.
- Source-truth admission proof remains fail-closed.
- Candidate-boundary inputs remain blocked and do not enter direct extraction.
- `core_risk.v1` does not call `_select_product_essence_values()`.
- Neutral risk-characteristic helpers are shared by product_essence and core_risk while preserving product_essence value shape.
- Proof-positive direct `core_risk.v1` suppresses candidate evidence, including direct missing.
- Accepted direct `core_risk.v1` emits four `required=False` `deferred_role` gaps for the deferred roles.
- Ambiguous risk-characteristic text fails closed with `ambiguous_table_or_locator`.
- Existing `data_extractor.py` fallback is exercised by tests without production `data_extractor.py` edits.
- Docs truth sync is bounded and does not claim parser replacement, full correctness, readiness, release, or complete core-risk source truth.

## Residual Risks

- Complete `core_risk.v1` source truth remains deferred to later independent gates for the four deferred roles.
- This work does not prove real-report correctness, parser replacement, full field correctness, golden/readiness, release, mark-ready, merge, push, or PR mutation.
- `_core_risk_status()` remains a binary `accepted | missing` model suitable only for this single-subvalue gate.
- Shared risk-characteristic label configuration affects both product_essence and core_risk; current tests prove no product_essence regression, but future semantic divergence requires a separate gate.

## Next Gate

After the accepted deepreview commit, the next entry point is:

`FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Ready-to-open-draft-PR Gate`

Release/readiness remains `NOT_READY`.
