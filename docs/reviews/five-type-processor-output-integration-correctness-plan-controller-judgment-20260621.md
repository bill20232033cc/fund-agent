# Five-type ProcessorRegistry + Extractor Output Integration Correctness Plan Controller Judgment - 2026-06-21

## Verdict

`ACCEPT_PLAN_READY_FOR_TESTS_ONLY_IMPLEMENTATION_NOT_READY`

## Scope

This judgment accepts the plan for connecting five-type small golden set retained-excerpt evidence to the merged ProcessorRegistry facade and extractor-output repository.

It does not implement the tests, change production behavior, add FOF coverage, promote golden/readiness, or mutate remote PR state.

## Accepted Plan Chain

- Plan: `docs/reviews/five-type-processor-output-integration-correctness-plan-20260621-140119.md`
- Initial plan review: `docs/reviews/plan-review-20260621-140156.md`
- Targeted re-review: `docs/reviews/plan-review-20260621-140313.md`

## Controller Amendments

- Implementation must be tests-only unless failing evidence proves a production defect.
- The oracle/report builder must be shared between existing row-field correctness tests and the new integration test.
- The implementation must cover exactly the five accepted fund types: active, index, enhanced index, bond, QDII.
- FOF remains deferred and must not be satisfied by QDII-FOF.
- No live/network/PDF/FundDocumentRepository real IO/provider/fallback is authorized.
- Extractor-output persistence must be explicit repository usage with `tmp_path`, not an implicit side effect of `FundDataExtractor.extract()`.

## Finding Disposition

| Finding | Status |
|---|---|
| `001` new helper may diverge from existing row-field oracle builder | `已修复` |

## Next Entry

`Five-type ProcessorRegistry + Extractor Output Integration Correctness Tests-only Implementation Gate`.

Release/readiness remains `NOT_READY`.
