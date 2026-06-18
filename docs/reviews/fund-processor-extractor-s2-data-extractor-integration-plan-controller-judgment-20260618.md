# Fund Processor/Extractor S2 DataExtractor Integration Plan Controller Judgment

> Date: 2026-06-18
> Role: phaseflow controller
> Work unit: Fund Processor/Extractor S2 DataExtractor Integration
> Gate: S2 plan review / fix / re-review controller judgment
> Classification: standard planning gate closeout

## Verdict

ACCEPT_PLAN_READY_FOR_IMPLEMENTATION_GATE_NOT_READY

The fixed S2 plan is accepted for the next implementation gate. This judgment does not implement code, does not authorize parser replacement, does not claim source truth, full field correctness, golden promotion, release readiness, or production readiness.

## Accepted Artifacts

- Plan: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md`
- Initial DS review: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-review-ds-20260618.md`
- Initial MiMo review: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-review-mimo-20260618.md`
- Plan fix evidence: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-fix-evidence-20260618.md`
- DS re-review: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-rereview-ds-20260618.md`
- MiMo re-review: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-rereview-mimo-20260618.md`

## Review Disposition

| Finding | Controller disposition | Reason |
|---|---|---|
| MiMo F1: `core_risk.v1` fallback projection under-specified | accepted; fixed | Plan now states only `risk_characteristic_text` may fallback from `core_risk.v1`; other `core_risk.v1` fields are informational/redundant and must not be merged into bundle fields. |
| MiMo F2: `processor.extract()` unexpected exception contract under-specified | accepted; fixed | Plan now requires unexpected exceptions to propagate or be explicitly converted to typed fail-closed errors, never swallowed, and never fallback to direct active-fund extraction. |
| MiMo F3: `current_stage.v1` projection implicit | accepted; fixed | Plan now marks `current_stage.v1` informational/redundant for S2 bundle projection. |
| MiMo F4: unclassified fund direct-path residual | accepted residual | Existing behavior remains direct legacy path; S2 does not promote unclassified inputs to processor path. |
| MiMo/DS source_kind derivation finding | accepted; fixed | Plan now uses deterministic `source_kind="annual_report"` for S2 ParsedAnnualReport production path. |
| DS active-field attribution test finding | accepted; fixed | Plan now requires injected/custom registry marker proof that active fields come from processor output or registry path. |
| DS non-active non-bond test coverage finding | accepted residual with mitigation | Plan recommends at least one non-active non-bond direct-path smoke test where fixtures allow; otherwise implementation evidence must record the residual. |
| DS tracking-error facade overlay note | accepted residual | Implementation evidence should record that `_tracking_error_for_fund_type()` intentionally post-processes processor output at the facade boundary. |
| DS anchor allocation strategy note | accepted residual | S2 plan defaults to using `FundFieldFamilyResult.anchors`; future field-level anchor filtering remains out of scope. |

## Controller Judgment

The fixed plan is code-generation-ready for the S2 implementation gate because:

- It preserves the `FundDocumentRepository` boundary and does not add direct parser/candidate consumption outside Fund Processor/Extractor ownership.
- It keeps S2 limited to active fund annual `ParsedAnnualReport` integration through `FundProcessorRegistry`.
- It preserves non-active fund behavior via explicit direct legacy residual path.
- It blocks silent active-fund fallback when registry resolution or processor extraction fails.
- It preserves repository failure propagation, NAV degradation, bond evidence semantics, source provenance projection, `NOT_READY`, candidate-only, and no parser replacement boundaries.
- It provides an exact implementation write set and validation matrix.

## Next Gate

Proceed to S2 implementation gate with the exact write set and stop condition in the accepted plan:

- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md` only if implementation changes documented Fund package current behavior
- `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md`

Implementation must not touch control docs, design docs, repository/source/candidate internals, Service/Host/Agent/render/quality paths, untracked residue, PR/release state, or live/source/provider/LLM/readiness commands.

## Residual Risks

| Residual | Owner | Destination |
|---|---|---|
| Bootstrap profile extraction is duplicated in memory for active fund classification and processor extraction. | S3 planning owner | Future precomputed extraction context or classifier processor gate. |
| `index_profile` remains projected from bootstrap profile extraction. | S3 planning owner | Future processor field-family coverage gate. |
| Non-active fund processors are not implemented. | Future Fund Processor owner | Separate processor implementation gates per fund type. |
| Candidate intermediates remain unauthorized for production facade. | Fund documents / processor owner | Separate source-truth/correctness gate before any production consumption. |
| Field-family anchor allocation remains family-level in S2. | S2 implementation/review owner | Implementation evidence and code review; future field-level anchor refinement if needed. |

Release/readiness remains `NOT_READY`.
