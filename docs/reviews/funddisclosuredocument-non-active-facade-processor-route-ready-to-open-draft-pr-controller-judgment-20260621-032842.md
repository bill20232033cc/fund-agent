# FundDisclosureDocument Non-active Facade/Processor Route Ready-to-open-draft-PR Controller Judgment

## Gate

- Work unit: `FundDisclosureDocument Non-active Facade/Processor Route`
- Gate: `ready-to-open-draft-PR`
- Branch: `fund-processor-non-active-registry`
- Base: `origin/main` at PR-35 merge commit `29075bc505a63ded7f4d923b7b6d2c30001e9902`
- HEAD at judgment: `0aee81c`
- Judgment artifact: `docs/reviews/funddisclosuredocument-non-active-facade-processor-route-ready-to-open-draft-pr-controller-judgment-20260621-032842.md`

## Branch Contents

Branch is ahead of `origin/main` by two accepted gate commits:

```text
0aee81c gateflow: accept deepreview for funddisclosure non-active route
c30d325 gateflow: accept funddisclosure non-active route
```

The branch diff contains the intended work unit scope:

- non-active `ParsedAnnualReport` registry integration dependency
- six-type explicit `fund_disclosure_document.v1` processor/facade route
- tests for registry, processor supports and facade dispatch
- docs/control updates
- implementation evidence, code review artifacts, aggregate deepreview artifacts, fix/re-review artifacts and controller judgments

Unrelated untracked residue remains outside the branch and is intentionally excluded.

## Gate Checklist

| Requirement | Evidence | Status |
| --- | --- | --- |
| Branch contains intended commits only | `git log --oneline origin/main..HEAD` shows `c30d325` and `0aee81c` | passed |
| Accepted slice commit exists | `c30d325 gateflow: accept funddisclosure non-active route` | passed |
| Aggregate deepreview completed | `docs/reviews/funddisclosuredocument-non-active-facade-processor-route-aggregate-deepreview-controller-judgment-20260621-031849.md` | passed |
| Accepted findings fixed and re-reviewed | DS-02 fixed and re-reviewed in `code-review-20260621-031710.md` / `code-review-20260621-031737.md` | passed |
| Accepted deepreview commit exists | `0aee81c gateflow: accept deepreview for funddisclosure non-active route` | passed |
| Tests and static checks passed | See Validation | passed |
| Docs decision complete | `docs/design.md`, `fund_agent/fund/README.md`, `tests/README.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md` updated | passed |
| Residual risks classified | See Residual Risks | passed |
| Draft PR summary can match real code | See Draft PR Summary | passed |

## Validation

Passed at this gate:

```text
uv run pytest tests/fund -q
1624 passed in 5.28s

uv run ruff check .
All checks passed!

git diff --check origin/main..HEAD
passed with no output
```

Prior accepted validations also passed:

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/processors/test_registry.py tests/fund/test_data_extractor.py -q
260 passed

uv run pytest tests/fund/processors tests/fund/test_data_extractor.py -q
285 passed
```

## Draft PR Summary

Title:

```text
Fund Processor non-active registry and FDD route
```

Body:

```text
## Summary

- register per-fund-type ParsedAnnualReport processors for index, enhanced index, bond, QDII and FOF funds
- add per-fund-type FundDisclosureDocument processors for the current six FundType values
- route explicit FundDisclosureDocument facade calls by the repository-loaded ParsedAnnualReport classification
- keep disclosure_intermediate=None on the default ParsedAnnualReport route and preserve FDD candidate/source-truth boundaries

## Validation

- uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/processors/test_registry.py tests/fund/test_data_extractor.py -q
- uv run pytest tests/fund/processors tests/fund/test_data_extractor.py -q
- uv run pytest tests/fund -q
- uv run ruff check .
- git diff --check origin/main..HEAD

## Boundaries

- no parser replacement
- no source policy change
- no Service/UI/Host/renderer/quality-gate direct FDD consumption
- no real-report correctness, golden/readiness or release transition claim
```

## Residual Risks

- Real-report correctness for non-active FDD source-truth extraction remains assigned to later evidence gates.
- Fund types outside the current `FundType` literal set remain assigned to a separate type-expansion gate.
- DS-01 helper consolidation is deferred to `Fund Processor maintainability follow-up`.
- DS-03 facade post-processing extraction is deferred to `FundDataExtractor maintainability follow-up`.
- Per-fund-type semantic specialization beyond shared processor behavior remains assigned to later type-specific extraction/evidence gates.

All residual risks are classified and non-blocking for draft PR creation.

## Controller Judgment

Accepted.

This branch is ready for the push gate and draft PR creation flow. The next entry point is:

`FundDisclosureDocument Non-active Facade/Processor Route Push Gate`.
