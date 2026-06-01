# MVP real-provider / LLM scoring artifact disposition gate

Date: 2026-05-31
Session reference: 019e7d70-0019-75c2-85c9-eff1f0764fb0
Branch: `codex/local-reconciliation`
Accepted baseline: `0e67389 gateflow: accept dayu host truth-source alignment`
Gate class: `standard`

## Scope

This gate classifies existing untracked residual artifacts. It does not modify runtime, code, tests, golden files, fixtures, scoring semantics, quality-gate semantics, release state, PR state, or external state.

The top-level `--help` file is absent and is not part of this disposition gate.

## Preflight

Commands run:

- `git branch --show-current`: `codex/local-reconciliation`
- `git status --short --untracked-files=all`: untracked residuals only
- `git diff --name-status`: no tracked dirty
- `git ls-files --others --exclude-standard`: bounded inventory source
- `git check-ignore -v` for report roots
- `rg` over truth/control docs and tracked review docs for raw report path references

Preflight result: continue. There is no tracked dirty at gate start.

## Ignore Coverage

Already ignored:

- `reports/extraction-snapshots/`
- `reports/quality-gate-runs/`
- `reports/scoring-runs/`
- `reports/smoke/`
- `reports/writing-runs/`
- `reports/data-source-runs/`

New scoped ignore recommended by this gate:

- `reports/mvp-local-acceptance/`
- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/`
- `reports/mvp-real-provider-smoke-rerun/`

Rationale: these roots contain repeatable raw command outputs, provider stdout/stderr, diagnostic JSON, exit codes, and smoke-run byproducts. They are not source-reviewed fixtures. Durable evidence must live in reviewed `docs/reviews/*.md` summaries, not raw provider or scoring payloads.

## Evidence Summary

The raw MVP provider/runtime directories are already summarized by review artifacts:

- `reports/mvp-local-acceptance/20260530/`: summarized by `docs/reviews/mvp-local-acceptance-real-provider-smoke-evidence-20260530.md` and its controller judgment.
- `reports/mvp-local-acceptance/20260530-rerun/`: summarized by `docs/reviews/mvp-local-acceptance-real-provider-smoke-rerun-evidence-20260530.md` and its controller judgment.
- `reports/mvp-local-acceptance/20260530-diagnostic/`: summarized by `docs/reviews/mvp-real-provider-audit-block-diagnostic-20260530.md` and its controller judgment.
- `reports/mvp-local-acceptance/20260531-auth-verification/`: summarized by `docs/reviews/mvp-provider-auth-config-verification-20260531.md` and its controller judgment.
- `reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/`: summarized by `docs/reviews/mvp-llm-writer-auditor-contract-hardening-controller-judgment-20260531.md`.
- `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/`: summarized by provider timeout hardening implementation evidence and controller judgment artifacts.
- `reports/mvp-local-acceptance/20260531-provider-timeout-rerun/`: summarized by `docs/reviews/mvp-real-provider-smoke-timeout-rerun-controller-judgment-20260531.md`.
- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/`: summarized by real-provider prompt-contract calibration artifacts.
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/`: summarized by writer prompt-contract diagnostic narrowing artifacts.
- `reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/`: summarized by writer marker syntax repair artifacts.
- `reports/mvp-local-acceptance/20260531-programmatic-audit-l1-calibration/`: summarized by programmatic audit L1 calibration artifacts.
- `reports/mvp-local-acceptance/20260531-provider-runtime-timeout-follow-up/`: summarized by provider runtime timeout follow-up artifacts.
- `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/`: summarized by independent body matrix evidence, reviews, and controller judgment.
- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/20260531/`: summarized by provider runtime budget / prompt-cost validation evidence, implementation evidence, deepreview, code reviews, and controller judgment.

Security-oriented scan over the MVP raw report roots found no `sk-*`, `Authorization: Bearer`, `Bearer ...`, explicit API key assignment, or `FUND_AGENT_LLM_API_KEY=...` pattern. A payload-field scan found only safe diagnostic metadata such as `contains_full_provider_response: false`, not full provider payloads.

The scan did not read or promote complete prompts, drafts, provider responses, or audit responses into this artifact.

## Disposition Table

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/reviews/mvp-artifact-disposition-20260531.md` | current-gate artifact | This gate output | Stage only with this gate's accepted checkpoint | Gateflow controller | artifact disposition accepted checkpoint | No |
| `docs/reviews/mvp-artifact-disposition-controller-judgment-20260531.md` | current-gate artifact | Controller decision for this gate | Stage only with this gate's accepted checkpoint | Gateflow controller | artifact disposition accepted checkpoint | No |
| `.gitignore` scoped MVP report additions | current-gate artifact | Prevents raw provider/runtime outputs from being source-reviewed | Stage only with this gate's accepted checkpoint | Gateflow controller | artifact disposition accepted checkpoint | No |
| `docs/reviews/mvp-*.md` | evidence-chain artifact | Contains plan, review, implementation evidence, validation evidence, and controller judgments for MVP LLM/provider gates | Do not bulk stage; promote through the owning accepted evidence checkpoint when needed | Gate owners / controller | evidence packaging or accepted checkpoint gate | No |
| `docs/reviews/release-maintenance-*.md` | evidence-chain artifact | Historical release-maintenance plans, reviews, evidence, and decisions | Leave untracked unless a release-maintenance evidence packaging gate accepts them | Release-maintenance owner | release-maintenance artifact packaging | No |
| `docs/reviews/repo-review-*.md` | research input / evidence-chain artifact | Repo review outputs outside the current gate | Leave untracked; promote only through explicit review artifact gate | Review owner | repo-review artifact packaging | No |
| `docs/reviews/workspace-ownership-reconciliation-20260531.md` | evidence-chain artifact | Baseline reconciliation used before this disposition gate | Preserve as reviewed evidence candidate; do not delete | Gateflow controller | accepted evidence checkpoint | No |
| `reports/mvp-local-acceptance/` | scratch/runtime output | Raw CLI/provider stdout, stderr, exit codes, diagnostic JSON, and quality byproducts summarized in `docs/reviews` | Add scoped ignore; leave on disk; do not commit raw files; deletion requires user authorization | Gateflow controller | optional cleanup authorization | No |
| `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/` | scratch/runtime output | Raw runtime-budget and prompt-cost validation byproducts summarized in `docs/reviews` | Add scoped ignore; leave on disk; do not commit raw files; deletion requires user authorization | Gateflow controller | optional cleanup authorization | No |
| `reports/mvp-real-provider-smoke-rerun/` | scratch/runtime output | Raw independent-body real-provider smoke byproducts summarized in `docs/reviews` | Add scoped ignore; leave on disk; do not commit raw files; deletion requires user authorization | Gateflow controller | optional cleanup authorization | No |
| `reports/scoring-runs/` | scratch/runtime output | Already ignored; referenced as generated scoring output, not durable fixture | Keep ignored; do not promote without explicit fixture/golden gate | Score/quality owner | fixture/golden promotion gate only | No |
| `reports/quality-gate-runs/` | scratch/runtime output | Already ignored; referenced as generated quality-gate output | Keep ignored; do not promote without explicit quality evidence gate | Quality owner | quality evidence packaging gate | No |
| `reports/extraction-snapshots/` | scratch/runtime output / candidate durable fixture only by separate gate | Already ignored; may contain regenerable extraction snapshots | Keep ignored; durable fixture promotion requires explicit fixture/golden gate | Data extraction owner | fixture/golden promotion gate only | No |
| `reviews/audit-report-2025-05-27.md` | research input / user-owned unknown | Top-level review artifact outside `docs/reviews`; ownership not established by this gate | Leave untracked; ask user before archive/delete/promote | User / original reviewer | user decision or review archive gate | No |
| `reviews/audit-report-2025-05-27-v2.md` | research input / user-owned unknown | Top-level review artifact outside `docs/reviews`; ownership not established by this gate | Leave untracked; ask user before archive/delete/promote | User / original reviewer | user decision or review archive gate | No |
| `docs/tmux-agent-memory-store.md` | user-owned unknown | Local agent memory store; explicitly excluded by prior gates | Leave untracked; ask user before archive/delete/promote | User / local automation owner | user decision | No |

## Deletion Authorization Boundary

This gate does not delete files.

If the user later wants cleanup, deletion must be separately authorized for exact paths. Candidate cleanup roots are:

- `reports/mvp-local-acceptance/`
- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/`
- `reports/mvp-real-provider-smoke-rerun/`
- `reports/scoring-runs/`
- `reports/quality-gate-runs/`
- `reports/extraction-snapshots/`

Before deletion, rerun a bounded secret/payload scan and confirm the durable `docs/reviews` evidence still carries the unique gate facts.

## Result

Later gates may proceed on a baseline where remaining visible dirty files are untracked evidence-chain artifacts or user-owned unknown residuals, provided each gate's preflight records them as out of scope. Raw MVP report roots should be hidden from ordinary status by the scoped `.gitignore` rules and must not be promoted as durable fixtures without an explicit review gate.
