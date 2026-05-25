# V0 Release Readiness Plan

> Date: 2026-05-24
> Branch: `codex/v0-release-readiness-plan`
> Work unit: release-maintenance candidate selection / plan
> Result: plan accepted locally

## Current State

- `release-maintenance coverage policy reconciliation` is accepted at local commit `750dea7`.
- Local worktree has an untracked empty `report.md`; it is a local artifact and must not be staged or committed.
- PR #17 is open draft: `https://github.com/bill20232033cc/fund-agent/pull/17`, head `codex/004393-quality-gate`, CI `test` success, merge state `CLEAN`.
- PR #15 is open non-draft: `https://github.com/bill20232033cc/fund-agent/pull/15`, head `baseline/p7-closure`, no checks in the latest query, merge state `UNKNOWN`.
- No PR mark-ready, merge, close, comment, reviewer request, branch deletion, or issue mutation is authorized in this plan.

## Goal

Prepare a v0 release-readiness gate that can be executed without blurring local repository readiness with external GitHub actions.

The release-readiness gate should answer five questions:

1. Are branch protection / main ruleset expectations known well enough to open or mark the release PR ready?
2. What is the required disposition for stale PR #15?
3. Does the root README accurately describe the current supported user path and non-goals?
4. Does the `004393` smoke command still prove the intended production path without weakening quality gate semantics?
5. What exact checklist must be complete before any v0 release PR is marked ready or merged?

## Scope

### Slice 1: External State Refresh

Refresh and record current state only:

- `gh pr view 17 --json number,title,isDraft,state,headRefName,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,url`
- `gh pr view 15 --json number,title,isDraft,state,headRefName,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,url`
- `gh pr list --state open --json number,title,isDraft,headRefName,baseRefName,updatedAt,url`
- Inspect branch protection / ruleset only if available as read-only metadata. If GitHub permissions are insufficient, record that as a release-readiness blocker or user-action item, not as a local code issue.

No external mutation is allowed in this slice.

### Slice 2: README Supported Scope Audit

Audit `README.md` against current implementation only:

- 5-minute path: `fund-analysis analyze 004393 --report-year 2024`.
- Current product mode default: quality gate `block`.
- Checklist entry: `fund-analysis checklist 004393 --report-year 2024`.
- Thermometer default: self-owned all-A `wind_all_a`.
- Smoke script boundaries: real PDF/network smoke is opt-in and uses `--dev-override --quality-gate-policy warn`.
- Non-goals: no trading advice, no future return forecast, no all-fund automatic valuation mapping.

If README is already aligned, produce an audit artifact without editing it. If drift is found, update only README lines that describe current user behavior.

### Slice 3: `004393` Smoke Confirmation

Use the least risky command first:

```bash
uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block
```

Expected success signal from the current PR #17 closeout: exit `0`, report renders, quality gate status is `warn`. If the command fails because PR #17 is not merged into this branch, record that the smoke is blocked behind PR #17 integration rather than changing source code in this gate.

Do not use `report.md` as output. If output capture is needed, use a timestamped ignored artifact path under `reports/` and do not stage it.

### Slice 4: PR #15 Disposition Plan

PR #15 appears stale relative to PR #16 and current main. The gate must classify it as one of:

- close as superseded by later merged work,
- keep open with an explicit rebase/review owner,
- convert into a tracked follow-up if it contains unique work not present on main.

Closing or commenting on PR #15 requires explicit user authorization.

### Slice 5: Release Checklist

Create a release-readiness checklist artifact covering:

- Local branch and base commit.
- Dirty worktree policy: `report.md` excluded.
- Validation commands run and results.
- README supported scope status.
- PR #17 status and required authorized action.
- PR #15 disposition and required authorized action.
- Remaining non-blocking residuals and owners.
- Explicit non-goals for the release gate.

## Required Guardrails

- Do not stage or commit `report.md`.
- Do not mark PR #17 ready, merge PR #17, close PR #15, comment on any PR, request reviewers, delete branches, or mutate issues without explicit user authorization.
- Do not create Host/Agent packages or add `dayu.host` / `dayu.engine` dependencies.
- Do not change CI coverage threshold in this release-readiness gate.
- Do not bypass `FundDocumentRepository` / `FundDataExtractor` for annual-report access.
- Do not weaken quality gate semantics to make a smoke command pass.

## Validation For This Plan

- `rg -n "V0 Release Readiness Plan|PR #17|PR #15|004393|report.md|mark-ready|quality gate|wind_all_a" docs/reviews/v0-release-readiness-plan-20260524.md`
- `git diff --check`

Full test suite is not required for this plan-only checkpoint.
