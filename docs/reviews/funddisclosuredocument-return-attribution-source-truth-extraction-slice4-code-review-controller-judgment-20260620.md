# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Slice 4 Code Review Controller Judgment

## Verdict

`ACCEPT_SLICE4_READY_FOR_AGGREGATE_DEEPREVIEW_NOT_READY`

## Scope

- Work unit: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`
- Gate: `Implementation Gate - Slice 4: Facade/Test/Docs Sync`
- Classification: `heavy`
- Controller role: accept or reject Slice 4 after implementation evidence, code review, and targeted re-review
- Accepted plan commit: `50b7837`
- Accepted Slice 1 commit: `cc7c628`
- Accepted Slice 2 commit: `3336c5e`
- Accepted Slice 3 commit: `ca05704`

## Inputs Reviewed

- Implementation evidence: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice4-implementation-evidence-20260620.md`
- AgentDS code review: `docs/reviews/code-review-20260620-ds-return-attribution-source-truth-slice4.md`
- AgentMiMo code review: `docs/reviews/code-review-20260620-mimo-return-attribution-source-truth-slice4.md`
- AgentDS targeted re-review: `docs/reviews/code-review-20260620-ds-return-attribution-source-truth-slice4-rereview.md`
- AgentMiMo targeted re-review: `docs/reviews/code-review-20260620-mimo-return-attribution-source-truth-slice4-rereview.md`
- Changed test: `tests/fund/test_data_extractor.py`
- Changed docs: `docs/design.md`, `fund_agent/fund/README.md`

## Controller Decision

Slice 4 is accepted.

The implementation adds a facade regression that uses the default `FundDisclosureDocumentProcessor`, a proof-positive `FundDisclosureSourceTruthAdmissionProof`, and the explicit `FundDataExtractor.extract(..., disclosure_intermediate=...)` route to verify `return_attribution.v1` projection into `StructuredFundDataBundle`.

Accepted facade behavior:

- `fee_schedule` projects as direct source-truth bundle value.
- `nav_benchmark_performance` projects as direct source-truth bundle value.
- `tracking_error` remains missing at the active-fund bundle layer under the existing non-index rule.
- Public anchors for projected fields are `annual_report` `EvidenceAnchor` rows from direct extraction.
- Candidate evidence is not consumed as facade source truth.

The initial AgentDS review found stale top-of-file `docs/design.md` status/summary wording. That finding was fixed in this slice and both targeted re-reviews returned `TARGETED_REREVIEW_PASS_NOT_READY`.

## Validation Accepted

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

- Real-report field correctness remains unproven; this slice uses synthetic proof-positive no-live fixtures.
- `tracking_error` source-truth can exist inside processor output, but active-fund bundle projection preserves the existing non-index not-applicable rule.
- Same-value duplicate disclosures from different stable locators still accept the first locator; owner is a future field-specific refinement gate only if real-report evidence proves unsafe.
- `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain missing for FDD source-truth direct extraction.
- Aggregate deepreview remains pending.

## Hard Boundaries Preserved

- No production source code was changed in Slice 4.
- No parser replacement.
- No public schema expansion for `EvidenceAnchor`, `EvidenceSourceKind`, `FundFieldFamilyResult`, or processor result contracts.
- No source/repository/fallback/cache/PDF/live/network/provider/LLM/manual-reference behavior change.
- No Service/UI/Host/renderer/quality-gate/LLM prompt consumption of FDD candidate artifacts.
- No other field-family source-truth extraction beyond `return_attribution.v1`.
- No release/readiness transition.

## Next Entry Point

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Aggregate Deepreview Gate`

The next gate may review the accepted plan plus Slices 1-4 as an aggregate local work unit. It must not expand to other field families, parser replacement, source/repository changes, live evidence, PR mutation, readiness, or release.
