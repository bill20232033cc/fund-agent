# Runtime/Engine Boundary Decision Plan Review - Controller Judgment

Date: 2026-05-23

## Reviewed Plan

`docs/reviews/release-maintenance-runtime-engine-boundary-decision-plan-20260523.md`

## Independent Reviews

- `docs/reviews/release-maintenance-runtime-engine-boundary-decision-plan-review-ds-20260523.md`
- `docs/reviews/release-maintenance-runtime-engine-boundary-decision-plan-review-glm-20260523.md`

Both reviews conclude `pass-with-risks` and report no blockers.

## Controller Decision

Accepted.

The best current decision is to **not create `fund_agent/runtime` or `fund_agent/engine` placeholder packages now**. Runtime and Engine remain valid target boundaries, but implementation must be triggered by concrete runtime/tool-loop requirements rather than directory completeness.

This is accepted because the direct evidence is aligned:

- `docs/design.md` says current production path is UI -> Application -> Service -> Capability and that Runtime / Engine are not wired.
- `docs/implementation-control.md` records Runtime/Engine as remaining boundary debt and warns against empty framework creation without concrete runner/tool-loop demand.
- `fund_agent/README.md` lists current package boundaries without Runtime/Engine and states external Dayu Host/Engine/Prompting are not current mainline facts.
- The filesystem has no `fund_agent/runtime` or `fund_agent/engine` directories.

## Finding Disposition

| Finding | Source | Disposition | Controller Rationale |
|---|---|---|---|
| `docs/design.md` project tree lists non-existent `runtime/` and `engine/` directories | DS M1 / M3, GLM M1 | Accepted as Slice 1 implementation constraint | A current-layout tree should not visually imply target packages exist. Slice 1 must remove or clearly separate the target-only entries and add prose that absence is intentional until a concrete runtime/tool-loop gate. |
| Local `AGENTS.md` conflict diff has four-layer / external Dayu runtime wording | DS M2, GLM M2 | Accepted as residual, not in scope | User-provided `AGENTS.md` remains authoritative for this session. The local file must not be staged or edited without explicit user decision. This must stay recorded before any push or Runtime/Engine implementation gate. |
| Optional Slice 2 validation commands use placeholders | DS M4 | Accepted as non-blocking | Slice 2 is optional and only executes if reviewers require static guards. Concrete commands can be specified if that slice is later selected. |

## Accepted Next Slice

Proceed with Slice 1 docs-only alignment:

- `docs/design.md`: make the §9 project tree reflect current filesystem facts; document Runtime / Engine as intentionally absent target boundaries until concrete triggers.
- `docs/implementation-control.md`: record accepted plan, reviews, controller judgment, defer decision, and next entry point.
- `fund_agent/README.md`: clarify current production path vs six-layer target boundary, and that absence of Runtime/Engine packages is intentional.

Non-scope:

- No production code changes.
- No test changes unless a later static guard slice is explicitly selected.
- No `fund_agent/runtime` or `fund_agent/engine` package creation.
- No external Dayu runtime dependency.
- No local `AGENTS.md` staging or edits.
- No push / PR / external action.

## Validation Required For Slice 1

- `git diff --check docs/design.md docs/implementation-control.md fund_agent/README.md`
- Conflict scan for external Dayu runtime and four-layer target wording across the touched docs.
- `git diff --cached --name-status` before commit must exclude `AGENTS.md` and unrelated deletions.
