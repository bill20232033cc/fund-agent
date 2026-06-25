# Evidence Confirm Default-on Policy Push/Update Draft PR Controller Judgment

## Gate

- Work unit: Evidence Confirm Productionization default-on policy.
- Gate: push/update draft PR controller judgment.
- Classification: heavy.
- Branch: `evidence-confirm-productionization`.
- Pushed head: `3c4fe064775a50c5e7b5fec58d5fce8ec03c39f7`.
- Draft PR: PR-40 `https://github.com/bill20232033cc/fund-agent/pull/40`.
- Artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-push-update-draft-pr-controller-judgment-20260623.md`.

## Authorization

User authorized exactly:

```text
同意执行 Push Gate：push 当前分支并更新 PR-40 body，不 mark ready、不
  merge、不 release。
```

This authorization covers only pushing the current branch and updating PR-40 body. It does not authorize mark-ready, merge, reviewer requests or release/readiness transition.

## Actions

```text
git push origin evidence-confirm-productionization
```

Result:

```text
af86b9b..3c4fe06  evidence-confirm-productionization -> evidence-confirm-productionization
```

```text
gh pr edit 40 --body-file <temporary body file>
```

Result: PR-40 body updated to describe the current default-on policy truth:

- product `fund-analysis analyze` defaults to repository-bounded Evidence Confirm with policy `warn`;
- product `fund-analysis analyze-annual-period` inherits the same `warn` policy through existing single-year `analyze()` delegation;
- product `fund-analysis checklist` remains Evidence Confirm `off`;
- `--evidence-confirm-policy off|warn|block` remains developer-only behind `--dev-override`;
- plain `--dev-override` keeps Evidence Confirm `off`.

No mark-ready, merge, reviewer request, release/readiness transition, live/PDF command, provider/LLM command or source fallback change was performed.

## Verification

```text
gh pr view 40 --json number,title,state,isDraft,headRefName,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,url,body
```

Observed:

- PR-40 is `OPEN`.
- PR-40 is still draft: `isDraft=true`.
- Head branch is `evidence-confirm-productionization`.
- Head OID is `3c4fe064775a50c5e7b5fec58d5fce8ec03c39f7`.
- Base branch is `evidence-confirm-anchor-audit-score`.
- PR body contains the current default-on policy truth and no longer claims "No default-on Evidence Confirm".
- CI `test` for head `3c4fe06` completed with `SUCCESS`.
- `mergeStateStatus` is `CLEAN`.

```text
git status --short --branch --untracked-files=all
```

Observed: local branch is aligned with `origin/evidence-confirm-productionization`; only known unrelated untracked residue remains.

## Residual Risks And Owners

| Residual | Disposition | Owner / Destination |
|---|---|---|
| PR-40 CI for head `3c4fe06` | closed in current gate | CI `test` completed with `SUCCESS`; merge state is `CLEAN` |
| Checklist Evidence Confirm CLI/support | deferred-with-owner | Service/CLI owner; separate checklist Evidence Confirm gate |
| Provider-backed/live semantic quality | deferred-with-owner | Evidence Confirm semantic owner; separate provider-backed semantic quality gate |
| Multi-sample live source/PDF coverage | deferred-with-owner | Evidence owner; separate multi-sample live evidence gate |
| Annual-period Evidence Confirm CLI summary display refinement | deferred-with-owner | UI/CLI owner; future UI/CLI residual gate |
| Annual-period developer-mode EC enablement | deferred-with-owner | Service/CLI owner; future annual-period developer-mode gate if needed |
| LLM-path EC dedicated test | deferred-with-owner | Service/LLM owner; future LLM-path EC or provider-backed semantic quality gate |
| Report-body Evidence Confirm rendering | deferred-with-owner | Renderer owner; future renderer gate |
| PR-40 mark-ready, merge and release transition | deferred-with-owner | Controller/release owner; separate explicit authorization and reviewed gate |

## Next Gate

`Evidence Confirm Productionization default-on policy PR Review Gate`

Start condition is satisfied: PR-40 CI for head `3c4fe06` completed with `SUCCESS` and merge state is `CLEAN`. PR review must use `deepreview`; do not mark ready, merge, request reviewers or claim release/readiness.

## Verdict

ACCEPT_PUSH_UPDATE_DRAFT_PR_READY_FOR_PR_REVIEW_GATE_NOT_READY
