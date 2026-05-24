# Release Maintenance Next Candidate Plan Fix - 2026-05-24

## Gate

- Source plan: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`
- Source reviews:
  - `docs/reviews/release-maintenance-next-candidate-plan-review-mimo-20260524.md`
  - `docs/reviews/release-maintenance-next-candidate-plan-review-glm-20260524.md`
- Controller judgment: `docs/reviews/release-maintenance-next-candidate-plan-review-controller-judgment-20260524.md`
- Fix scope: document-only plan fix; no implementation, dependency, source, test, config, README, design, or control-doc changes.

## Changed Files

- Modified: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`
- Added: `docs/reviews/release-maintenance-next-candidate-plan-fix-20260524.md`

## Per-Finding Status

| Finding | Status | Fix Summary |
|---|---|---|
| C1 dayu-agent pyproject baseline | Fixed | Clarified local baseline as `docs/design.md` §9.1 plus current `pyproject.toml`; external `dayu-agent` pyproject now requires URL/commit/revision/content provenance; future dependency gate command set includes `rg -n "dayu" pyproject.toml`, `uv lock --check`, setuptools package discovery/package-data checks, and package import smoke checks where applicable. |
| C2 decision artifact skeleton | Fixed | Added required section skeleton for `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`. |
| C3 rg validation limits | Fixed | Added validation note that `rg` commands are existence checks only and semantic correctness is covered by plan review / re-review gates. |
| C4 decision absorption path | Fixed | Added Decision absorption path requirement to Slice 4 and the completion report format. |
| C5 stop-condition report format | Fixed | Added stop report format: triggered condition, context/evidence, suggested scope adjustment, user decision required. |
| C6 code-generation-ready wording | Fixed | Replaced the goal wording with `plan-review-ready 决策计划` and explicitly stated the work unit is document-only. |
| C7 Slice 2 executable rg command | Fixed | Added Slice 2 `rg` validation command covering dependency gate blocked status, no placeholder packages, `extra_payload`, and baseline provenance. |
| C8 validation pass criteria | Fixed | Expanded `Validation run` completion field to require command, expected assertion, exit code or observed pass signal, and skipped validation reason. |
| C9 review checklist completeness | Fixed | Added checklist items for annual-report access through `FundDocumentRepository` / `FundDataExtractor` and License/repo hygiene. |

## Validation

Validation run:

- `git diff --check` — pass, exit code 0, no whitespace errors reported.
- `rg -n "plan-review-ready|document-only|local baseline|docs/design.md.*9\\.1|external dayu-agent|URL|commit|provenance|uv lock --check|tool\\.setuptools\\.(packages\\.find|package-data)|Validation note|existence checks|semantic correctness|Decision absorption path|Stop report format|FundDocumentRepository|FundDataExtractor|License/repo hygiene" docs/reviews/release-maintenance-next-candidate-plan-20260524.md` — pass, exit code 0, required fix terms found.
- `rg -n "dependency gate remains blocked|blocked until implementation imports|no fund_agent/host|no fund_agent/agent|extra_payload|local baseline|docs/design.md.*9\\.1|external dayu-agent|URL|commit|provenance" docs/reviews/release-maintenance-next-candidate-plan-20260524.md` — pass, exit code 0, Slice 2 validation terms found.
- `rg -n "dayu" pyproject.toml` — expected no-match signal, exit code 1, confirming current `pyproject.toml` still has no Dayu dependency text.
- `rg -n "tool\\.setuptools\\.(packages\\.find|package-data)|include-package-data" pyproject.toml` — pass, exit code 0, package discovery entry found; no package-data entry is currently present, matching the plan's baseline statement.
- `uv lock --check` — pass, exit code 0, lockfile is current.

## Residual Risks

- The `rg` validations remain existence checks; semantic correctness intentionally remains a re-review responsibility.
- `uv lock --check` may depend on local `uv` availability and lockfile state; any failure should be reported as validation evidence, not worked around in this document-only gate.
- No external `dayu-agent` pyproject was fetched in this fix, because the plan only needs to define provenance requirements for a future dependency gate.

## Handoff Status

Handoff status: ready for re-review against C1-C9 accepted findings.
