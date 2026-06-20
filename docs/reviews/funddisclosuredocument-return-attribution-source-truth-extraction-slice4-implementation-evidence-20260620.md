# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Slice 4 Implementation Evidence

## Gate And Slice

- Work unit: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`
- Gate: `Implementation Gate - Slice 4: Facade/Test/Docs Sync`
- Role: implementation worker
- Accepted plan commit: `50b7837`
- Accepted Slice 1 commit: `cc7c628`
- Accepted Slice 2 commit: `3336c5e`
- Accepted Slice 3 commit: `ca05704`
- Verdict: `IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY`

## Changed Files

- `tests/fund/test_data_extractor.py`
- `docs/design.md`
- `fund_agent/fund/README.md`
- `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice4-implementation-evidence-20260620.md`

No production source file was changed in this slice.

## Behavior Summary

- Added a facade regression for `FundDataExtractor.extract(..., disclosure_intermediate=...)` using the default `FundDisclosureDocumentProcessor`.
- The regression constructs a proof-positive `FundDisclosureDocument` content stub with `FundDisclosureSourceTruthAdmissionProof`.
- The explicit FDD route projects proof-positive `return_attribution.v1` `fee_schedule` and `nav_benchmark_performance` into `StructuredFundDataBundle`.
- The regression verifies projected anchors are public `annual_report` `EvidenceAnchor` rows from direct source-truth extraction.
- `tracking_error` keeps the existing active-fund facade rule: non-index funds do not expose tracking error in the bundle and remain `missing` with note `非指数基金不适用跟踪误差`.
- The test does not import concrete candidate modules into `FundDataExtractor`; candidate evidence remains outside facade projection.
- `docs/design.md` and `fund_agent/fund/README.md` now state the current fact: proof-positive FDD source-truth direct extraction covers `product_essence.v1` and `return_attribution.v1`.
- The same docs preserve that `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain source-truth missing.

## Review Finding Disposition

- AgentDS initial review identified stale top-of-file `docs/design.md` status/summary text that still said only `product_essence.v1` had FDD source-truth direct extraction.
- The stale header text was corrected in this slice to match the detailed design sections and Fund README: `product_essence.v1` and `return_attribution.v1` are implemented; the other four families remain missing.
- Validation was rerun after the fix with the same passing results below.

## Tests And Validation

```text
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
170 passed in 0.92s
```

```text
uv run ruff check tests/fund/test_data_extractor.py
All checks passed!
```

```text
git diff --check -- tests/fund/test_data_extractor.py docs/design.md fund_agent/fund/README.md docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice4-implementation-evidence-20260620.md
PASS: no output
```

## Explicit Boundaries

- `NOT_READY` is preserved.
- No parser replacement is claimed or implemented.
- No production facade code was changed.
- No source/repository/fallback/cache/PDF/live/network/provider/LLM/manual-reference behavior was changed.
- No `EvidenceAnchor`, `EvidenceSourceKind`, processor contract, or public schema expansion.
- No other source-truth field family was implemented.
- No Service/UI/Host/renderer/quality-gate/LLM prompt consumption was added.
- Candidate evidence remains candidate-only / not_proven / NOT_READY and is not consumed as source truth.

## Residual Risks And Next Destination

- Real-report field correctness remains unproven; owner: later evidence gate.
- `tracking_error` source-truth exists inside `return_attribution.v1` processor output, but active-fund bundle projection still preserves the existing non-index not-applicable rule; owner: future facade semantics gate only if the product contract changes.
- Same-value duplicate disclosures from different stable locators remain accepted with the first locator; owner: future field-specific refinement gate if real-report evidence proves unsafe.
- The remaining four FDD source-truth families remain missing; owner: separate future gates.
- Aggregate deepreview / controller acceptance remains pending; owner: next review gate.

## Completion Status

Slice 4 implementation is ready for code review, while release/readiness remains `NOT_READY`.
