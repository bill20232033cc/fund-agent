# FundDisclosureDocument Non-active Facade/Processor Route Aggregate Deepreview Fix

## Gate

- Work unit: `FundDisclosureDocument Non-active Facade/Processor Route`
- Gate: `aggregate deepreview fix`
- Branch: `fund-processor-non-active-registry`
- Base context: PR-35 merge commit `29075bc505a63ded7f4d923b7b6d2c30001e9902`
- Fix artifact: `docs/reviews/funddisclosuredocument-non-active-facade-processor-route-aggregate-deepreview-fix-20260621-031620.md`

## Source Review

- Aggregate implementation review: `docs/reviews/code-review-20260621-031254.md`
- Finding fixed: `02-未修复-低-FDD 路由的 source_provenance 空值检查晚于 processor 执行`

## Fix

Changed `FundDataExtractor._extract_fund_disclosure_via_processor()` so `disclosure_intermediate.source_provenance is None` fails before registry resolution and before processor execution.

This keeps the same fail-closed user-visible outcome while moving the check to the earliest facade boundary where the explicit FDD route has enough information to reject unsafe input.

## Changed Files

- `fund_agent/fund/data_extractor.py`
  - Moved `source_provenance is None` check immediately after the explicit FDD dispatch key is built and before `self._processor_registry.resolve(dispatch_key)`.
- `tests/fund/test_data_extractor.py`
  - Strengthened `test_explicit_disclosure_missing_provenance_fails_closed()` to use `_RecordingRegistry`.
  - Added `registry.resolved_contexts == []` assertion proving missing provenance fails before registry resolution.

## Finding Status

- DS-02: `已修复`

Deferred/not-fixed findings from `docs/reviews/code-review-20260621-031254.md`:

- DS-01 `_blocked_result` duplicate helper drift risk: `deferred-with-owner`, owner `Fund Processor maintainability follow-up`; not a behavior defect in this route gate.
- DS-03 duplicated post-processing block in two processor route methods: `deferred-with-owner`, owner `FundDataExtractor maintainability follow-up`; not a behavior defect in this route gate.

## Validation

Passed:

```text
uv run pytest tests/fund/test_data_extractor.py -q
52 passed in 0.84s

uv run pytest tests/fund/processors tests/fund/test_data_extractor.py -q
285 passed in 1.00s

git diff --check
passed with no output
```

## Residual Risks

- Real-report correctness for non-active FDD source-truth extraction remains assigned to later evidence gates.
- Fund types outside the current `FundType` literal set remain assigned to a separate type-expansion gate.
- Helper consolidation and route post-processing extraction remain maintainability follow-up work, not blockers for this gate.

## Status

Fix is ready for targeted re-review.
