# Controller Judgment: baseline coverage recovery decision plan

> Controller: Codex
> Date: 2026-05-27
> Gate: `baseline coverage recovery decision gate`
> Latest accepted checkpoint before gate: `5812a1e`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this judgment | `bond-lens score applicability implementation accepted locally` |
| Reviewed next entry | `baseline coverage recovery decision gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, current accepted artifacts |

## Decision

Accepted.

The next safe gate is `index/QDII source recovery and replacement decision gate`.

This is accepted because the dominant blocker for moving toward a representative small baseline is still source-safe coverage, not fixture promotion or more work on a single bond sample. `006597` has improved from the equity-shaped `holdings_snapshot` false blocker to a quality-gate `warn`, but it remains baseline-blocked by `bond_risk_evidence_missing.baseline_blocking=true` and other residual P1 gaps. Index and QDII rows remain source-blocked with unknown upstream fallback category, so the next minimal step is to decide a repository-safe recovery/replacement path for those slots.

## Review Summary

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | Accepted. Informational findings noted; no re-review required. |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted after targeted patch. Medium/low process findings fixed; targeted re-review `PASS`. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| `extraction-snapshot` is not lightweight | MiMo F1 | Accepted as guard | Future evidence gate must treat it as real repository access, not a read-only probe, and must remain within accepted evidence scope. |
| Golden exclusion condition could be sharper | MiMo F2 | Deferred | Conservative condition is acceptable. Future golden gate should distinguish already-classified residuals from `needs_more_evidence` residuals. |
| 006597 state change could be clearer | MiMo F3 | Accepted | Plan already records current `warn`; controller judgment records the block-to-warn transition explicitly. |
| closeout omitted review + controller judgment | GLM F1 | Accepted and fixed | Plan now explicitly requires MiMo review, GLM review, and controller judgment before next gate authorization. |
| next gate lacked plan-before-evidence guard | GLM F2 | Accepted and fixed | Plan now states the next gate must produce its own plan artifact and pass MiMo + GLM review + controller judgment before any evidence run. |
| sequencing readability | GLM F3 | Accepted and fixed | Plan now notes source recovery and later bond positive-risk evidence are complementary. |

## Accepted Next Gate Boundaries

The next gate may plan `110020` / `017641` recovery or replacement only under these constraints:

- Use repository-safe public/product paths only; no direct PDF/cache/source-helper access.
- Preserve source fallback fail-closed semantics: only `not_found` / `unavailable` may be fallback-eligible.
- Treat `schema_drift`, `identity_mismatch`, and `integrity_error` as fail-closed.
- Do not count QDII-FOF as pure FOF without a taxonomy gate.
- Do not promote durable baseline or golden artifacts.
- Do not modify renderer, FQ0-FQ6 policy, Service/CLI, Host/Agent/dayu, source strategy, extractors, `fund_type.py`, golden/baseline fixtures, or GitHub state.

## Validation

- `git diff --check`: passed.
- MiMo plan review: `PASS_WITH_FINDINGS`.
- GLM plan review: `PASS_WITH_FINDINGS`.
- GLM targeted re-review: `PASS`.

## Residual Risks

- `006597` remains baseline-blocked by `bond_risk_evidence_missing.baseline_blocking=true` and still has `holder_structure`, `share_change`, and `turnover_rate` residuals.
- Pure FOF coverage remains unresolved; QDII-FOF cannot count as pure FOF without taxonomy review.
- Golden corpus v1 remains blocked until source, fund-type, baseline-blocking, and reviewed-fact conditions are satisfied.

## Next Entry Point

`index/QDII source recovery and replacement decision gate`

The next gate must start with Startup Packet replay and `$init-agents` / tmux multi-agent flow. It must be plan-before-evidence: no source recovery evidence run or candidate replacement probing may start until the next gate has its own accepted plan/review/controller judgment.
