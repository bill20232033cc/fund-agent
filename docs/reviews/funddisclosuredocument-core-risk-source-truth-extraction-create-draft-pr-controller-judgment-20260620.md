# FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Create Draft PR Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`
- Gate: Create Draft PR Gate
- Branch: `funddisclosure-core-risk-source-truth`
- Draft PR: `https://github.com/bill20232033cc/fund-agent/pull/34`
- PR number: `34`
- Base: `funddisclosure-current-stage-source-truth`
- Head: `funddisclosure-core-risk-source-truth`
- PR head at creation/update check: `cca789bdb141ac16c54d1eb3c8b92fa167e0656e`
- Artifact path: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-create-draft-pr-controller-judgment-20260620.md`

## Verdict

`ACCEPT_CREATE_DRAFT_PR_NOT_READY`

Draft PR 34 was created with the intended stacked base/head.

## PR Body Correction

The initial `gh pr create --body` invocation used a double-quoted body and shell-expanded Markdown backtick spans before PR creation returned. The controller immediately inspected PR 34, found the body corrupted, and corrected it with `gh pr edit 34 --body` using single-quoted body text.

The corrected PR body now states:

- only `core_risk.v1.risk_characteristic_text` is implemented;
- complete `core_risk.v1` source truth remains out of scope;
- four deferred roles remain candidate-only/deferred and appear only as `required=False` `deferred_role` gaps;
- no parser replacement, schema expansion, upper-layer consumption, readiness, release, mark-ready, or merge is claimed;
- local validation and gate evidence artifacts are listed.

## Current PR State

- Draft: true
- Merge state: `UNSTABLE`
- CI `test`: in progress at first post-create check

## Scope Boundary

This gate does not mark PR 34 ready, merge any PR, claim readiness/release, or expand source-truth scope beyond `core_risk.v1.risk_characteristic_text`.

## Next Gate

`FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Gate`

Release/readiness remains `NOT_READY`.
