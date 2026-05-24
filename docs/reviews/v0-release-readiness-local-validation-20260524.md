# V0 Release Readiness Local Validation

> Date: 2026-05-24  
> Branch: `codex/v0-release-readiness-plan`  
> Base: `origin/main` through merge commit `9deace0` plus local docs checkpoints  
> Plan: `docs/reviews/v0-release-readiness-plan-20260524.md`  
> Result: `blocked pending PR #17 integration / authorized external action`

## Scope

This validation covers the local, non-mutating part of v0 release readiness:

- refresh open PR state without mark-ready, merge, close, comment, reviewer, branch, or issue mutation;
- inspect main ruleset / branch protection metadata;
- audit README-supported v0 user paths;
- run the `004393` product smoke command under default block semantics;
- keep local `report.md` out of staging and commits.

## External State Refresh

Open PRs:

| PR | State | Draft | Head | Base | Merge state | CI | Readiness meaning |
|---:|---|---|---|---|---|---|---|
| #17 | open | yes | `codex/004393-quality-gate` @ `d16b5b` | `main` | `CLEAN` | `test` success | likely next external action is mark-ready / merge after user authorization |
| #15 | open | no | `baseline/p7-closure` @ `1bd9c1` | `main` | `DIRTY` | no checks in latest query | stale/conflicted; disposition needs explicit user authorization |

No external mutation was performed.

## Main Ruleset / Protection

`gh api repos/bill20232033cc/fund-agent/rulesets` returned active repository ruleset `protect-main` (`id=16789646`).

The detailed ruleset contains:

- `deletion`
- `non_fast_forward`
- `pull_request` with allowed merge methods `merge`, `squash`, `rebase`
- `required_linear_history`

Legacy branch protection endpoint for `main` returned `404 Branch not protected`, so current protection appears to be ruleset-based rather than legacy branch-protection based.

## README Supported Scope Audit

`README.md` is aligned with the v0 supported scope:

- 5-minute path: `fund-analysis analyze 004393 --report-year 2024`
- product default: `fund-analysis analyze` runs quality gate with default `block`
- report save example uses `report-004393.md`, not local `report.md`
- checklist entry exists: `fund-analysis checklist 004393 --report-year 2024`
- thermometer default and examples use self-owned `wind_all_a`
- release scope states real PDF/network pytest is not part of ordinary pytest and remains explicit smoke
- coverage policy states CI global `--cov-fail-under=50` and single-file >=80% as review target

No README edit is needed in this gate.

## `004393` Product Smoke

Command:

```bash
uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block
```

Result:

- exit code: `2`
- stderr summary:
  - `质量 gate 阻断报告输出`
  - `quality_gate_status: block`
  - `quality_gate_issues: 13`
  - `quality_gate_json: reports/quality-gate-runs/analyze-004393-2024-20260524T083027435045Z/quality_gate.json`
  - `quality_gate_md: reports/quality-gate-runs/analyze-004393-2024-20260524T083027435045Z/quality_gate.md`

Observed blocker categories from `quality_gate.md`:

- `FQ2/FQ3` block on P0 `fee_schedule` coverage / traceability.
- `FQ1` block on `basic_identity.management_company`, `basic_identity.custodian`, `basic_identity.inception_date`.
- `FQ1` block on benchmark-name conservative normalization.
- `FQ4` block because snapshot missing rate is `35.7%` above threshold `35.0%`.

Interpretation: this branch does not include PR #17's `004393` quality-gate fix, so the v0 smoke is blocked behind PR #17 integration. This gate must not weaken quality gate semantics or switch to `warn` to claim release readiness.

## PR #15 Disposition

PR #15 is open, non-draft, and now reports merge state `DIRTY`. It should be treated as stale/conflicted for v0 release readiness.

Allowed next choices require explicit user authorization:

- close as superseded/stale;
- comment with disposition and owner;
- keep open only if a human owner confirms it still represents unreplaced work.

## Local Artifact Policy

`report.md` remains untracked and must not be staged or committed. Generated quality-gate files under `reports/quality-gate-runs/...` are local runtime artifacts and are ignored by git.

## Release Checklist

| Item | Status | Evidence / next action |
|---|---|---|
| Current branch clean except local artifact | pass | `git status --short` shows only `?? report.md` before this artifact edit |
| Main ruleset present | pass | active `protect-main` repository ruleset |
| PR #17 ready for user decision | pending authorization | draft, mergeState `CLEAN`, CI `test` success |
| PR #15 disposition | pending authorization | open non-draft, mergeState `DIRTY` |
| README supported scope | pass | no edit needed |
| `004393` product smoke under block policy | blocked | exit `2`, quality gate `block`; blocked behind PR #17 integration |
| No quality-gate weakening | pass | no source/config/test/runtime behavior changed |
| No `report.md` commit | pass | not staged |

## Controller Judgment

V0 release readiness is not locally complete on this branch. The next practical step is an explicit user decision on PR #17:

1. authorize mark-ready / merge of PR #17, then refresh `main` and re-run the `004393` smoke; or
2. keep PR #17 draft and stop v0 release readiness at this blocked state.

PR #15 should also receive an explicit disposition decision, but it does not need to block PR #17 smoke integration if it is confirmed stale.
