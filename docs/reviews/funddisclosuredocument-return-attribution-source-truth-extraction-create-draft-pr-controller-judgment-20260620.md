# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Create Draft PR Controller Judgment

## Verdict

`ACCEPT_CREATE_DRAFT_PR_READY_FOR_PR_REVIEW_NOT_READY`

## Scope

- Work unit: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`
- Gate: `Create Draft PR Gate`
- Classification: `standard external-state bookkeeping`
- Branch: `funddisclosure-return-attribution-source-truth`
- Base: `main`
- Local/upstream head before PR creation: `5ab675d`

## Preflight Facts

```text
git status --branch --short
## funddisclosure-return-attribution-source-truth...origin/funddisclosure-return-attribution-source-truth
?? docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md
?? docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md
?? docs/next-development-phaseflow.md
?? docs/tmux-agent-memory-store.md
?? scripts/claude_mimo_simple.py
?? scripts/review-artifact.sh
```

```text
git rev-parse --short HEAD
5ab675d
```

```text
git rev-parse --short @{u}
5ab675d
```

```text
gh pr list --state open --head funddisclosure-return-attribution-source-truth --json number,state,title,headRefName,baseRefName,url,isDraft --limit 10
[]
```

`git diff --check origin/main...HEAD` exited successfully.

## Action Taken

Created draft PR:

- PR: `#30`
- URL: `https://github.com/bill20232033cc/fund-agent/pull/30`
- Title: `FundDisclosureDocument return_attribution source-truth extraction`
- Head: `funddisclosure-return-attribution-source-truth`
- Base: `main`
- Draft: `true`

## Post-action Facts

```json
{
  "baseRefName": "main",
  "headRefName": "funddisclosure-return-attribution-source-truth",
  "headRefOid": "5ab675d52b779e5deefa9551bf05f97058f72b7c",
  "isDraft": true,
  "mergeStateStatus": "UNSTABLE",
  "number": 30,
  "state": "OPEN",
  "title": "FundDisclosureDocument return_attribution source-truth extraction",
  "url": "https://github.com/bill20232033cc/fund-agent/pull/30"
}
```

CI `test` was queued at PR creation time.

## Controller Decision

Accept draft PR creation.

PR #30 is the external review surface for the accepted `return_attribution.v1` source-truth direct extraction work unit. It remains draft/open and must go through PR review before any mark-ready or merge decision.

This controller judgment and control/startup sync are local create-draft-PR bookkeeping and should be pushed to the PR branch before PR review.

## Next Entry Point

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction PR Review Gate`

The PR review gate must use `deepreview`, review PR #30 against `main`, and preserve all `NOT_READY` boundaries.

## Boundaries Preserved

- PR was created as draft.
- No PR was marked ready.
- No merge, rebase, reset or force-push was performed.
- No readiness/release transition.
- No other field-family extraction.
- No parser replacement.
- No `EvidenceAnchor` / `EvidenceSourceKind` expansion.
- No source/repository, live/provider/PDF, Docling conversion, pdfplumber export, manual reference review, or upper-layer consumption work.
