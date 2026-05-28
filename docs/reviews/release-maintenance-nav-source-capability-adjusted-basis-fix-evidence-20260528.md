# NAV Source Capability / Adjusted Basis Fix Evidence

Date: 2026-05-28

Worker: Codex

Role: implementation/fix worker, not controller

Gate: `NAV source capability / adjusted basis evidence gate`

Assigned scope: artifact-only fix for accepted plan/evidence review findings.

## Worker Self-Check - Start

- Status: pass.
- Current role is specialist fix worker only. I did not start `$gateflow` / `/gateflow`, did not restart the plan, did not enter review, and did not commit / push / PR / merge / close out.
- Source of truth read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, target plan/evidence artifacts, DS review, GLM review, and Reviewer B artifact for `B-P1`.
- Scope boundary: allowed files only are the plan artifact, evidence artifact, and this fix evidence artifact. No production code, tests, score, quality gate, schema, golden fixture, blocker removal, release state, or unrelated files.
- Completion signal: accepted findings are reflected in artifact wording, conclusion remains `blocked_pending_source_adapter`, and verification is docs/artifact-only.

## Changed Files

- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-20260528.md`
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-evidence-20260528.md`
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-fix-evidence-20260528.md`

## Per-Finding Status

| Finding | Status | Fix |
|---|---|---|
| DS-F1 / B-P1 / GLM-F1 | fixed | Evidence now labels direct NAV SQLite inspection as `diagnostic-only`, `non-authoritative`, and not public adapter capability proof. Plan now states future production code and implementation paths must not copy direct SQLite reads as a Fund-layer adapter bypass. |
| DS-F2 | fixed | Plan now states raw NAV availability is proven by the public `FundNavDataAdapter.load_nav_data("006597")` smoke. SQLite inspection is explicitly separated as diagnostic-only evidence. |
| DS-F3 | fixed | Plan keeps the `_load_cached_sync()` metadata loss as future NAV adapter gate scope, requiring public adapter cache-hit metadata repair instead of direct SQLite access. |
| GLM-F2 | fixed | Plan adds `dividend_adjustment_status` as an explicit future gate decision point: it may be absorbed into `adjustment_basis` with documented semantics or exposed as an independent field. |

## Validation

Validation type: docs/artifact-only.

Commands / checks used:

```bash
rg -n "diagnostic-only|non-authoritative|FundNavDataAdapter\\.load_nav_data|dividend_adjustment_status|_load_cached_sync|blocked_pending_source_adapter" docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-20260528.md docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-evidence-20260528.md docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-fix-evidence-20260528.md
git status --short
```

The target plan/evidence artifacts are currently untracked in the workspace, so ordinary `git diff -- <path>` does not display a tracked-file diff for them. Scope was verified by `git status --short` plus direct `rg` checks against the three allowed paths.

`ruff` / `pytest` were not run because this fix changed only review artifacts under `docs/reviews/`; no Python code, tests, fixtures, score, quality gate, schema, or runtime behavior changed.

## Preservation Checks

- `capability_decision_recommendation = blocked_pending_source_adapter` remains unchanged.
- `drawdown_stress` blocker remains in place; no blocker解除 is claimed.
- No score, quality, snapshot schema, baseline, golden, FQ0-FQ6, renderer, Service/CLI, production adapter, Host/Agent/dayu, release, or PR state changed.
- Direct SQLite inspection remains recorded only as diagnostic non-boundary evidence and cannot be used as future source capability proof.

## Residual Risks

- Future NAV adapter gate still needs code and tests to expose origin source and retrieval timestamp through public adapter contracts; this fix only records the requirement.
- Future source provider selection still must prove adjusted / cumulative / total-return basis before any drawdown calculator or score/quality semantics change.
- Future derived evidence contract still needs source-kind-aware anchors and per-group provenance projection before `drawdown_stress` can be machine-checked.

## Worker Self-Check - Completion

- Status: pass.
- I changed only the three allowed artifact paths.
- I did not modify production code, tests, score, quality gate, schema, golden fixture, design/control truth, release / PR state, or unrelated untracked files.
- I did not commit, push, create PR, merge, close out the gate, or remove the blocker.
- Artifact conclusion remains fail-closed: current public adapter capability is insufficient for adjusted-basis drawdown evidence.
