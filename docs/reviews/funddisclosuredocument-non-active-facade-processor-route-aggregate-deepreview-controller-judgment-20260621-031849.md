# FundDisclosureDocument Non-active Facade/Processor Route Aggregate Deepreview Controller Judgment

## Gate

- Work unit: `FundDisclosureDocument Non-active Facade/Processor Route`
- Gate: `aggregate deepreview`
- Branch: `fund-processor-non-active-registry`
- Base: `29075bc505a63ded7f4d923b7b6d2c30001e9902`
- HEAD at review start: `c30d325`
- Judgment artifact: `docs/reviews/funddisclosuredocument-non-active-facade-processor-route-aggregate-deepreview-controller-judgment-20260621-031849.md`

## Reviewed Artifacts

- AgentDS aggregate review: `docs/reviews/code-review-20260621-031254.md`
- AgentMiMo aggregate review: `docs/reviews/code-review-20260621-031335.md`
- Fix artifact: `docs/reviews/funddisclosuredocument-non-active-facade-processor-route-aggregate-deepreview-fix-20260621-031620.md`
- AgentDS targeted re-review: `docs/reviews/code-review-20260621-031710.md`
- AgentMiMo targeted re-review: `docs/reviews/code-review-20260621-031737.md`

## Findings And Decisions

| Finding | Source | Decision | Final status |
| --- | --- | --- | --- |
| DS-01 `_blocked_result` duplicate helper signature drift risk | `code-review-20260621-031254.md` | `deferred-with-owner` | deferred to `Fund Processor maintainability follow-up` |
| DS-02 FDD route source_provenance None check runs after processor execution | `code-review-20260621-031254.md` | `accepted` | `已修复` |
| DS-03 duplicated post-processing code in parsed/FDD processor facade routes | `code-review-20260621-031254.md` | `deferred-with-owner` | deferred to `FundDataExtractor maintainability follow-up` |

AgentMiMo aggregate review found no substantive issues.

## Fix Summary

Accepted finding DS-02 was fixed by moving `disclosure_intermediate.source_provenance is None` validation in `FundDataExtractor._extract_fund_disclosure_via_processor()` before registry resolution and processor execution.

Regression coverage was strengthened in `tests/fund/test_data_extractor.py::test_explicit_disclosure_missing_provenance_fails_closed` by using `_RecordingRegistry` and asserting `registry.resolved_contexts == []`.

## Re-review Result

- AgentDS targeted re-review verdict: DS-02 `已修复`.
- AgentMiMo targeted re-review verdict: `已修复`.

No accepted findings remain open.

## Validation

Passed after fix:

```text
uv run pytest tests/fund/test_data_extractor.py -q
52 passed in 0.84s

uv run pytest tests/fund/processors tests/fund/test_data_extractor.py -q
285 passed in 1.00s

uv run pytest tests/fund -q
1624 passed in 5.48s

uv run ruff check .
All checks passed!

git diff --check
passed with no output
```

## Residual Risks

- Real-report correctness for non-active FDD source-truth extraction remains assigned to later evidence gates.
- Fund types outside the current `FundType` literal set remain assigned to a separate type-expansion gate.
- DS-01 helper consolidation is deferred to `Fund Processor maintainability follow-up`.
- DS-03 facade post-processing extraction is deferred to `FundDataExtractor maintainability follow-up`.
- Per-fund-type semantic specialization beyond shared processor behavior remains assigned to later type-specific extraction/evidence gates.

All residual risks are classified and non-blocking for this aggregate deepreview gate.

## Controller Judgment

Accepted.

The aggregate deepreview gate is complete. The next entry point is:

`FundDisclosureDocument Non-active Facade/Processor Route Accepted Deepreview Commit Gate`.
