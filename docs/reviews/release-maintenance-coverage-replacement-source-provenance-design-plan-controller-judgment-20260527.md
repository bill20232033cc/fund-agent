# Controller Judgment: coverage replacement / source provenance design plan

> Controller: Codex
> Date: 2026-05-27
> Gate: `coverage replacement candidate selection or source provenance output design gate`
> Latest accepted checkpoint before gate: `e41c829 docs: accept index qdii recovery evidence`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this judgment | `index/QDII source recovery evidence accepted locally` |
| Reviewed plan gate | `coverage replacement candidate selection or source provenance output design gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted artifacts |

## Decision

Accepted.

The next safe path is an additive public-output source provenance contract, not replacement-candidate probing. The accepted evidence at `e41c829` shows public CLI runs for `110020` / 2024 and `017641` / 2024 can complete, but public outputs do not expose the original upstream source failure category. Successful downstream extraction is not direct evidence that fallback was eligible. Because no controller-approved replacement candidates exist, replacement probing would either be a no-op or violate the no ad hoc search / no direct PDF-cache-helper boundary.

The next implementation gate may design and implement only additive public provenance output. It must not change `FundDocumentRepository` source strategy, fallback eligibility decisions, source helpers, renderer, FQ0-FQ6, default Service/CLI behavior, Host/Agent/dayu, golden fixtures, baseline fixtures, or corpus promotion.

## Review Summary

| Reviewer | Initial verdict | Re-review verdict | Controller disposition |
|---|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | `PASS` | Accepted. Informational findings resolved in the revised plan. |
| AgentGLM | `PASS_WITH_FINDINGS` | `PASS` | Accepted. Medium provenance-category ambiguity finding resolved in the revised plan. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| `fallback_used=true` with missing `primary_failure_category` could be misread as eligible | GLM F1 / MiMo 5.3, 6.3 | Accepted and fixed | Plan now requires `fallback_eligibility="unknown_public_metadata_absent"`, not `eligible`, until a later accepted gate threads `AnnualReportSourceFailure.category` through metadata and public output. |
| Provenance projection ownership was underspecified | GLM F2 / MiMo 6.1 | Accepted and fixed | Plan now assigns pure projection ownership to `fund_agent/fund`; Service consumes the result and must not access source helpers. |
| `not_applicable` cross-field consistency needed a test | GLM F3 / MiMo 6.2 | Accepted and fixed | Future test scope now requires `source_provenance_status="not_applicable"` rows to have `fallback_eligibility="not_applicable"` and `fallback_used=false`. |
| Multi-source failure-chain category selection needed a rule | MiMo 5.1 | Accepted and fixed | Plan defers the concrete chain-selection rule to the implementation gate and requires conservative `unknown_public_metadata_absent` if public output cannot determine the applicable category. |
| `source_strategy` derivation should be explicit in implementation | MiMo 5.2 | Deferred to implementation gate | A constant such as `primary_then_fallback` is sufficient for v1, but exact derivation belongs in the implementation plan. |

## Accepted Plan Constraints

- Minimum public fields: `source_provenance_schema_version`, `source_strategy`, `resolved_source_name`, `fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, and `source_provenance_reason`.
- Conservative default: fallback-backed rows with missing category metadata are `unknown_public_metadata_absent`, not eligible.
- Fail-closed preservation: `schema_drift`, `identity_mismatch`, and `integrity_error` remain non-eligible even if downstream score or quality-gate succeeds.
- Implementation ownership: `fund_agent/fund` owns deterministic projection; Service/public output consumes projected fields.
- Replacement selection remains blocked until a controller-supplied or accepted-artifact-derived candidate exists.

## Validation

- Plan artifact written and revised.
- MiMo initial review: `PASS_WITH_FINDINGS`.
- GLM initial review: `PASS_WITH_FINDINGS`.
- MiMo targeted re-review: `PASS`.
- GLM targeted re-review: `PASS`.
- `git diff --check`: required before accepted commit.

## Residual Risks

- Current metadata may not persist `AnnualReportSourceFailure.category`; the implementation gate must not infer eligibility if category is unavailable.
- `017641` remains quality-gate `block`; provenance alone cannot make it baseline-ready.
- `110020` remains at most `warn`; provenance alone cannot promote it to golden or durable baseline.
- Pure FOF coverage, bond baseline-blocking, and reviewed-fact blockers remain separate residuals.

## Next Entry Point

`source provenance public-output implementation gate`

The next gate must start with Startup Packet replay and `$init-agents` / tmux multi-agent flow. It must first produce an implementation plan and pass plan review before code changes. It may only implement additive public provenance output under the accepted plan constraints above.
