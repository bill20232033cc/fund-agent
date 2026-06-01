# MVP historical evidence-chain checkpoint disposition

Date: 2026-06-01
Gate: `MVP historical MVP evidence-chain checkpoint gate`
Branch: `codex/local-reconciliation`

## Scope

This gate only promotes remaining untracked `docs/reviews/mvp-*.md` historical evidence artifacts into a local accepted checkpoint.

It does not modify runtime, tests, raw reports, truth-source docs, release state, PR state, quality gates, score rules, golden files, fixtures, `docs/tmux-agent-memory-store.md`, top-level `reviews/`, `repo-review-*`, or `release-maintenance-*` artifacts.

## Preflight

- `git branch --show-current`: `codex/local-reconciliation`
- `git status --short`: untracked historical residuals only
- `git diff --name-status`: no tracked dirty
- `git diff --cached --name-status`: no staged dirty

## Inventory

Remaining untracked MVP evidence artifacts: 55 files.

Grouped by work unit:

| Work unit | Count | Category | Decision |
| --- | ---: | --- | --- |
| `mvp-independent-body-chapter-execution-*` | 7 | accepted MVP evidence-chain artifact | stage-current-gate |
| `mvp-llm-writer-auditor-contract-hardening-plan-*` side artifacts | 5 | accepted MVP evidence-chain artifact | stage-current-gate |
| `mvp-programmatic-audit-l1-calibration-*` | 7 | accepted MVP evidence-chain artifact | stage-current-gate |
| `mvp-provider-runtime-budget-prompt-cost-calibration-plan-20260531.md` | 1 | superseded/early plan evidence-chain artifact | stage-current-gate |
| `mvp-provider-runtime-timeout-follow-up-*` | 9 | accepted MVP evidence-chain artifact | stage-current-gate |
| `mvp-provider-runtime-timeout-hardening-*` side artifacts | 6 | accepted MVP evidence-chain artifact | stage-current-gate |
| `mvp-real-provider-smoke-prompt-contract-calibration-plan-*` side artifacts | 5 | accepted MVP evidence-chain artifact | stage-current-gate |
| `mvp-real-provider-smoke-timeout-rerun-controller-judgment-20260531.md` | 1 | accepted MVP evidence-chain artifact | stage-current-gate |
| `mvp-writer-marker-syntax-repair-*` | 7 | accepted MVP evidence-chain artifact | stage-current-gate |
| `mvp-writer-prompt-contract-diagnostic-narrowing-*` | 7 | accepted MVP evidence-chain artifact | stage-current-gate |

## Excluded Residuals

The following are intentionally excluded from this checkpoint:

- `docs/reviews/release-maintenance-*`
- `docs/reviews/overnight-release-maintenance-*`
- `docs/reviews/repo-review-*`
- `docs/reviews/workspace-ownership-reconciliation-20260531.md`
- `docs/tmux-agent-memory-store.md`
- `reviews/audit-report-2025-05-27*.md`

These remain user-owned unknown, research input, or non-MVP historical residuals and require a separate user decision or archive gate.

## Validation

Required before commit:

- `git diff --check`
- `git diff --cached --name-status`
- `git diff --cached --check`
- staged files limited to this artifact and `docs/reviews/mvp-*.md` remaining historical evidence artifacts.
