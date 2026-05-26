# Controller Judgment: source provenance post-implementation bounded evidence rerun plan

> Controller: Codex
> Date: 2026-05-27
> Gate: `source provenance post-implementation bounded evidence rerun plan/review gate`
> Latest accepted checkpoint before gate: `f88a3aa feat: persist annual report fallback failure category`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this plan | `source provenance primary-failure-category propagation implementation accepted locally` |
| Reviewed gate | `source provenance post-implementation bounded evidence rerun plan/review gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted artifacts |

## Decision

Accepted.

The plan safely defines a bounded public evidence rerun for `110020` / 2024 and `017641` / 2024. It uses only public CLI commands, requires `extraction-snapshot --force-refresh` through the public path to avoid old cached metadata masking the new `primary_failure_category`, and forbids manual cache deletion, private cache/source/PDF inspection, code changes, source strategy changes, FQ0-FQ6 changes, renderer changes, default CLI changes, Host/Agent/dayu work, and baseline/golden/clean-denominator promotion.

Every row remains `promotion_disposition=not_promoted` in this gate.

## Review Summary

| Reviewer | Artifact | Verdict | Controller disposition |
|---|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-plan-review-mimo-20260527.md` | `PASS` | Accepted. No material findings. |
| AgentGLM | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-plan-review-glm-20260527.md` | `PASS` | Accepted. No material findings. |

## Accepted Evidence Scope

- Funds: `110020` / 2024 and `017641` / 2024 only.
- Commands: `fund-analysis extraction-snapshot --force-refresh`, `fund-analysis extraction-score`, and `fund-analysis quality-gate`.
- Run ids:
  - `source-provenance-rerun-110020-2024-20260527`
  - `source-provenance-rerun-017641-2024-20260527`
- Generated output root: ignored `reports/extraction-snapshots/<run_id>/`.
- Tracked summary artifact: `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md`.
- Classification may use only public snapshot provenance fields and public quality outputs.

## Finding Disposition

No material findings were raised.

## Residual Risks

- `--force-refresh` may produce a different source path than the prior cached run if the external primary source state changed. This is acceptable because classification is based only on public output from this run.
- If public metadata still lacks `primary_failure_category`, classification remains `provenance_unknown_public_metadata_absent`; no inference is allowed.
- This evidence gate still cannot promote either sample to durable baseline, golden, fixture, or clean denominator.

## Next Entry Point

`source provenance post-implementation bounded evidence rerun`

The next worker may run the exact accepted commands, write the tracked summary artifact, and stop for independent evidence review. It must not commit, push, create a PR, mutate GitHub state, modify code/docs/control, inspect private cache/source/PDF internals, or promote any corpus state.
