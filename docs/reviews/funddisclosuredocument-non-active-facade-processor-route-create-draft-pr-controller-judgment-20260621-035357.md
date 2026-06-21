# FundDisclosureDocument Non-active Facade/Processor Route Create Draft PR Controller Judgment

## Gate

- Work unit: `FundDisclosureDocument Non-active Facade/Processor Route`
- Gate: `create draft PR`
- Branch: `fund-processor-non-active-registry`
- Base branch: `main`
- Head branch: `fund-processor-non-active-registry`
- Judgment artifact: `docs/reviews/funddisclosuredocument-non-active-facade-processor-route-create-draft-pr-controller-judgment-20260621-035357.md`

## PR Created

- PR: `36`
- URL: `https://github.com/bill20232033cc/fund-agent/pull/36`
- Title: `Fund Processor non-active registry and FDD route`
- State: `OPEN`
- Draft: `true`
- Author: `bill20232033cc`

## PR Body Summary

The draft PR body records:

- per-fund-type `ParsedAnnualReport` processors for index, enhanced index, bond, QDII and FOF funds
- per-fund-type `FundDisclosureDocument` processors for the current six `FundType` values
- explicit FDD facade routing by repository-loaded `ParsedAnnualReport` classification
- default `disclosure_intermediate=None` remains on the `ParsedAnnualReport` route
- no parser replacement, source policy change, upper-layer FDD consumption, real-report correctness, golden/readiness or release transition claim

## Current Check State

At creation time:

```text
test pending
https://github.com/bill20232033cc/fund-agent/actions/runs/27882131486/job/82511413013
```

`mergeStateStatus` reported by GitHub: `UNSTABLE`.

## Validation Before PR Creation

Ready gate validation had passed locally:

```text
uv run pytest tests/fund -q
1624 passed in 5.28s

uv run ruff check .
All checks passed!

git diff --check origin/main..HEAD
passed with no output
```

## Boundaries

- Draft PR only.
- No merge.
- No mark-ready-for-review.
- No request-reviewers.
- No branch deletion.
- No external issue changes.
- No unrelated untracked residue included.

## Status

Create draft PR gate accepted.

This artifact must be committed and pushed to PR-36 before PR review/draft-PR-pass gates.

Next entry point:

`FundDisclosureDocument Non-active Facade/Processor Route PR Review Gate`.
