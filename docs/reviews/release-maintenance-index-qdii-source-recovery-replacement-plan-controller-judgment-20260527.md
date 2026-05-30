# Controller Judgment: index/QDII source recovery and replacement plan

> Controller: Codex
> Date: 2026-05-27
> Gate: `index/QDII source recovery and replacement decision gate`
> Latest accepted checkpoint before gate: `1a28919`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this judgment | `baseline coverage recovery decision plan accepted locally` |
| Reviewed next entry | `index/QDII source recovery and replacement decision gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, current accepted artifacts |

## Decision

Accepted.

The plan authorizes the next gate to run a bounded evidence step for `110020` / 2024 and `017641` / 2024 only after Startup Packet replay. The evidence step may use public Fund CLI paths that internally use `FundDocumentRepository`, but it may not directly access PDF/cache/source helpers or modify source strategy.

The accepted terminal states are:

- `recovered_eligible`
- `recovered_fail_closed`
- `unrecoverable_safe_path`
- `repository_run_failed`
- `not_run_no_approved_candidates`
- `replacement_verified`
- `excluded`

Rows remain outside the clean denominator unless an eligible upstream failure category is recovered or a controller-approved / accepted-artifact-derived replacement candidate is verified.

## Review Summary

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS` | Accepted. Informational findings do not require plan change. |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted. Low finding about `excluded` terminal state definition patched; no re-review required per reviewer. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| `extraction-snapshot` may not expose original failure category | MiMo F1 / GLM F1 | Accepted as stop-path guard | If public CLI output does not expose category, classify `unrecoverable_safe_path`; do not use indirect symptoms or direct helper access. |
| cache artifact output specificity | MiMo F2 | Deferred | Evidence closeout must note any generated ignored cache/report paths and must not track large outputs. |
| downstream path if both rows unrecoverable | MiMo F3 | Deferred | Controller will decide next gate after evidence closeout; plan correctly stops/excludes rather than repeated probing. |
| `excluded` terminal state not defined | GLM F2 | Accepted and fixed | Plan now defines `excluded` as an intentional outside-clean-denominator state with recorded reason after Subgate A/B analysis. |

## Accepted Evidence Gate Boundaries

Allowed after this judgment:

- Run bounded public CLI evidence for `110020` and `017641` through existing Fund paths.
- Keep generated outputs in scratch / ignored `reports/...`.
- Write a tracked summary artifact under `docs/reviews/`.
- Classify each candidate into one accepted terminal state.

Forbidden:

- Direct PDF/cache/source-helper/downloader access.
- Source strategy, source helper, `FundDocumentRepository`, extractor, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, `fund_type.py`, golden, or baseline fixture changes.
- Ad hoc web/search replacement candidate discovery.
- Durable baseline/golden promotion.
- GitHub mutation.

## Required Validation For Evidence Gate

- Public CLI command status and output paths for each candidate.
- Per-candidate terminal state and direct evidence path.
- Explicit source fallback category if recovered.
- `git diff --check`.
- MiMo review, GLM review, and controller judgment before any later gate treats a row as clean evidence.

## Next Entry Point

`index/QDII source recovery evidence gate`

The next gate may run evidence only within the accepted boundaries above. If public outputs cannot recover the original upstream failure category and no approved replacement exists, the correct result is exclusion / `not_run_no_approved_candidates`, not repeated probing.
