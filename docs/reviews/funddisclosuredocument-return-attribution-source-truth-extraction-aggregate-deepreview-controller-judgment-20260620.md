# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Aggregate Deepreview Controller Judgment

## Verdict

`ACCEPT_AGGREGATE_DEEPREVIEW_READY_FOR_READY_TO_OPEN_DRAFT_PR_NOT_READY`

## Scope

- Work unit: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`
- Gate: `Aggregate Deepreview Gate`
- Classification: `heavy`
- Reviewed range: `50b7837..HEAD` at local head `9bef25f`
- Aggregate artifact: `docs/reviews/code-review-20260620-080325.md`

## Inputs Reviewed

- Accepted plan: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
- Slice 1 controller judgment: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice1-code-review-controller-judgment-20260620.md`
- Slice 2 controller judgment: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice2-code-review-controller-judgment-20260620.md`
- Slice 3 controller judgment: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice3-code-review-controller-judgment-20260620.md`
- Slice 4 controller judgment: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice4-code-review-controller-judgment-20260620.md`
- Aggregate deepreview: `docs/reviews/code-review-20260620-080325.md`

## Controller Decision

Aggregate deepreview is accepted.

The aggregate review walked the explicit FDD facade path, source-truth admission path, `return_attribution.v1` extraction selectors, anchor/gap construction, bundle projection, and docs sync. It reported no substantive findings.

Accepted work-unit facts:

- proof-positive `return_attribution.v1` FDD input can emit public direct source-truth field-family values;
- direct `return_attribution.v1` route suppresses `candidate_evidence`;
- explicit FDD facade projects proof-positive fee and NAV/benchmark values into `StructuredFundDataBundle`;
- active-fund `tracking_error` continues to follow the existing non-index missing rule at bundle projection;
- `docs/design.md` and `fund_agent/fund/README.md` now consistently state `product_essence.v1` and `return_attribution.v1` are the currently implemented FDD source-truth direct extraction families.

## Validation Accepted

Latest Slice 4 controller validation remains the accepted deterministic check:

```text
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
170 passed
```

```text
uv run ruff check tests/fund/test_data_extractor.py
All checks passed!
```

```text
git diff --check
PASS: no output
```

## Accepted Residuals

- Real-report field correctness remains unproven.
- Same-value duplicate disclosures from different stable locators still accept the first locator unless future evidence proves unsafe.
- `tracking_error` bundle projection remains governed by the current non-index missing rule.
- `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain missing for FDD source-truth direct extraction.
- Release/readiness remains `NOT_READY`.

## Hard Boundaries Preserved

- No parser replacement.
- No source/repository/fallback/cache/PDF/live/network/provider/LLM/manual-reference behavior change.
- No `EvidenceAnchor`, `EvidenceSourceKind`, processor contract, or public schema expansion.
- No Service/UI/Host/renderer/quality-gate/LLM prompt consumption of FDD candidate artifacts.
- No other field-family source-truth extraction beyond `return_attribution.v1`.
- No PR mutation, mark-ready, merge, release, or readiness transition in this gate.

## Next Entry Point

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Ready-to-open-draft-PR Gate`

The next gate may inspect branch/remote/PR state and decide whether a draft PR surface exists or must be created. It must not mark ready, merge, claim readiness, run live/provider/PDF/parser replacement work, or expand field-family extraction.
