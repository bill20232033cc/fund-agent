# Release Maintenance Aggregate Deepreview Controller Judgment - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `release-maintenance aggregate deepreview`
- Branch: `codex/checklist-host-engine-design`
- Review range: `origin/main..HEAD`
- Review artifacts:
  - `docs/reviews/release-maintenance-aggregate-deepreview-mimo-20260524.md`
  - `docs/reviews/release-maintenance-aggregate-deepreview-glm-20260524.md`
- Controller conclusion: `fix required for accepted low findings`

## Review Summary

| Reviewer | Conclusion | Findings | Blocking Questions |
|---|---|---:|---|
| MiMo | `PASS_WITH_FINDINGS` | 2 low/cosmetic | 0 |
| GLM | `PASS_WITH_FINDINGS` | 3 low, 4 informational | 0 |

Both reviewers found no blocker, no high-severity correctness issue, and no violation of the current Dayu four-layer guardrails:

- no placeholder `fund_agent/host` or `fund_agent/agent` packages;
- no `dayu.host` / `dayu.engine` dependency before an explicit Host/Agent gate;
- no actual `extra_payload` parameter smuggling;
- current deterministic path remains UI -> Service -> `fund_agent/fund`.

Controller evidence check found that GLM F2 was narrower than the actual evidence: `rg -n "Capability|Fund Capability" fund_agent` shows multiple current source docstrings in `fund_agent/fund` still using old Capability-layer terminology. Because `AGENTS.md` and `docs/design.md` now define `fund_agent/fund` as the Agent-layer fund domain capability package, the current fix should clean the source-facing architecture terminology consistently, not only the single public data entrypoint.

## Controller Finding Decisions

### RM-AGG-C1-deferred-low-ci-coverage-threshold

- **Sources**: GLM F1; MiMo verification note.
- **Decision**: deferred.
- **Reason**: Based on the current release-maintenance scope, the 50% CI threshold is an intentionally conservative floor already accepted in Slice D, while actual validation remains 91.94% coverage. Raising the CI policy now is a separate hardening decision and not required to prove this Host/Agent boundary decision branch is ready.
- **Owner / destination**: future release-maintenance CI hardening.
- **Blocking status**: non-blocking for `ready-to-open-draft-PR`.

### RM-AGG-C2-accepted-low-source-terminology-cleanup

- **Sources**: GLM F2 plus controller evidence check.
- **Decision**: accepted.
- **Reason**: Based on the current design truth, current source docstrings must not keep presenting `fund_agent/fund` as a standalone `Capability` layer. That old term weakens the four-layer boundary and can mislead future agents during plan/review.
- **Required fix**: In current source comments/docstrings, replace architecture-level `Capability` / `Fund Capability` wording with `Agent 层基金能力`, `基金领域能力`, or another precise current-term equivalent. Keep this scoped to current source-facing wording; do not rewrite historical review artifacts or control archive history. Do not change runtime behavior, imports, public APIs, tests, dependencies, package layout, `docs/design.md`, or `README` files unless a touched source docstring creates a direct doc mismatch.
- **Minimum evidence**: `rg -n "Capability|Fund Capability" fund_agent` should no longer show current source architecture docstrings that describe `fund_agent/fund` as a `Capability` layer. If an occurrence remains because it is part of a historical identifier, explicit external terminology, or accepted runtime value, document why in the fix artifact.

### RM-AGG-C3-accepted-low-checklist-result-type-annotation

- **Sources**: MiMo F2, GLM F3.
- **Decision**: accepted.
- **Reason**: The CLI helper already documents `FundChecklistResult`; using a real type annotation is the simplest current best practice and removes an unnecessary `no-untyped-def` suppression.
- **Required fix**: Import/export use should stay through `fund_agent.services`; annotate `_echo_checklist_result(result: FundChecklistResult) -> None` in `fund_agent/ui/cli.py` and remove the `# type: ignore[no-untyped-def]` suppression.

### RM-AGG-C4-rejected-stale-section-count-note

- **Source**: MiMo F1.
- **Decision**: rejected as already closed / stale evidence.
- **Reason**: The Host/Agent boundary decision code-review loop already accepted and fixed HABC-C1, and both targeted re-reviews marked it fixed. Controller evidence before the accepted slice checkpoint confirmed only `13 required sections` remains in the implementation artifact. No current action is needed.

### RM-AGG-C5-informational-observations

- **Sources**: GLM F4, F5, F6, F7.
- **Decision**: accepted as informational evidence, not defects.
- **Reason**: These observations support readiness of the lockfile change, historical document cleanup, review artifact trail, and Chapter 0 renderer implementation. They do not require fix work.

## Required Fix Scope

Dispatch a fix worker for RM-AGG-C2 and RM-AGG-C3 only.

Allowed files:

- `fund_agent/fund/**/*.py` for source docstring/comment terminology cleanup;
- `fund_agent/config/paths.py` only if `rg` shows a current source docstring with old `Fund Capability` wording;
- `fund_agent/ui/cli.py` for the `_echo_checklist_result` type annotation;
- `docs/reviews/release-maintenance-aggregate-deepreview-fix-20260524.md` as the fix artifact.

Non-goals:

- no Host/Agent package creation;
- no `dayu.host` / `dayu.engine` dependency declaration;
- no behavior, API, test fixture, golden data, README, design-doc, control-doc, CI threshold, or lockfile change;
- no cleanup of historical `docs/reviews/` artifacts or implementation-control archive wording.

Validation expected from the fix worker:

- `rg -n "Capability|Fund Capability" fund_agent`
- `uv run ruff check fund_agent/fund fund_agent/config/paths.py fund_agent/ui/cli.py`
- focused CLI/type-adjacent tests if the worker identifies a relevant existing test file;
- `git diff --check`

## Residual Risks

| ID | Status | Owner / Destination |
|---|---|---|
| RR-AGG-1 CI coverage threshold may be too low for long-term regression prevention | deferred | future release-maintenance CI hardening |
| RR-AGG-2 historical `Capability` wording remains in archive/control history | accepted non-current evidence | no action; historical records are not current architecture truth |

## Next Gate

Dispatch the aggregate fix worker. After the fix artifact exists and validation passes, request targeted aggregate re-review from MiMo and GLM. If both re-reviews pass and no new blocker appears, update `docs/implementation-control.md`, create the accepted deepreview local checkpoint, and stop at `ready-to-open-draft-PR` for user authorization before any push or draft PR action.
