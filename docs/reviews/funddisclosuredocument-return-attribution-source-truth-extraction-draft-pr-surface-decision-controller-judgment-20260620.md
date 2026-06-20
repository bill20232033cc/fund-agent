# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Draft-PR Surface Decision Controller Judgment

## Verdict

`ACCEPT_NEW_BRANCH_SURFACE_READY_FOR_BRANCH_PREPARATION_NOT_READY`

## Scope

- Work unit: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`
- Gate: `Draft-PR Surface Decision Gate`
- Classification: `standard external-state decision`
- Current branch: `funddisclosure-source-truth-field-extraction-plan`
- Current local head: `a15c90c`

## Facts Checked

Current branch is ahead of its upstream by 10 accepted local commits:

```text
## funddisclosure-source-truth-field-extraction-plan...origin/funddisclosure-source-truth-field-extraction-plan [ahead 10]
```

Existing same-branch PR surfaces are merged, not open:

- PR #28: `MERGED`
- PR #29: `MERGED`

Candidate new branch availability:

```text
git branch --list funddisclosure-return-attribution-source-truth
<no output>
```

```text
git branch -r --list origin/funddisclosure-return-attribution-source-truth
<no output>
```

```text
gh pr list --state open --head funddisclosure-return-attribution-source-truth --json number,state,title,headRefName,baseRefName,url,isDraft --limit 10
[]
```

## Controller Decision

Use a clean new branch for the return-attribution source-truth work unit:

`funddisclosure-return-attribution-source-truth`

Rationale:

- the current branch name is already tied to merged PR surfaces #28/#29;
- current local head is ahead of upstream by accepted work-unit commits;
- the candidate branch name is locally and remotely unused;
- no open PR exists for the candidate branch.

Do not push or create a PR in this decision gate.

## Next Entry Point

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction New Branch Preparation Gate`

That gate may create local branch `funddisclosure-return-attribution-source-truth` from current accepted local head after rechecking cleanliness and branch availability. Push and PR creation remain separate future gates.

## Boundaries Preserved

- No branch creation in this gate.
- No push.
- No PR creation/mutation.
- No mark-ready or merge.
- No readiness/release transition.
- No other field-family extraction, parser replacement, source/repository, live/provider/PDF, or upper-layer consumption work.
