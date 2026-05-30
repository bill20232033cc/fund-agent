# Controller Judgment: source provenance bounded evidence classification

> Controller: Codex
> Date: 2026-05-27
> Gate: `source provenance bounded evidence run`
> Latest accepted checkpoint before evidence run: `26e61f7 docs: accept source provenance evidence plan`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering evidence run | `source provenance bounded evidence classification plan accepted locally` |
| Next entry point entering evidence run | `source provenance bounded evidence run; must use init-agents / tmux multi-agent flow` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted artifacts |

## Decision

Accepted.

The bounded evidence run followed the accepted plan: it ran only the six public CLI commands for `110020` / 2024 and `017641` / 2024, wrote generated outputs only under ignored `reports/` directories, and tracked only the summary artifact. No source code, tests, `docs/design.md`, `docs/implementation-control.md`, renderer, FQ0-FQ6, default analyze/checklist behavior, source strategy, Host/Agent/dayu, baseline, golden, or fixture state was changed by the evidence worker.

Both rows remain outside the clean denominator. Public snapshot provenance shows `fallback_used=true`, `primary_failure_category=null`, `fallback_eligibility=unknown_public_metadata_absent`, and `source_provenance_status=incomplete` for both funds. Successful extraction, populated score output, and quality-gate completion were not used as fallback eligibility evidence.

## Evidence Summary

| Fund | Year | Public provenance terminal state | Quality status | Promotion disposition | Controller judgment |
|---|---:|---|---|---|---|
| `110020` | 2024 | `provenance_unknown_public_metadata_absent` | `warn` | `not_promoted` | Accepted. Non-blocking quality output does not prove fallback eligibility. |
| `017641` | 2024 | `provenance_unknown_public_metadata_absent` | `block` | `not_promoted` | Accepted. Quality block does not override provenance ordering because fallback eligibility was not publicly proven first. |

## Review Summary

| Reviewer | Artifact | Verdict | Controller disposition |
|---|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-review-mimo-20260527-061255.md` | `PASS` | Accepted. No material findings. |
| AgentGLM | `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-review-glm-20260527.md` | `PASS` | Accepted. No material findings. |

## Finding Disposition

No material findings were raised.

MiMo used a timestamped review artifact path instead of the originally suggested fixed path. This is a harmless review-output naming deviation because the artifact is present, scoped to the gate, and referenced explicitly in this controller judgment and control document. No re-review is required.

## Residual Risks

- Public metadata still does not expose `primary_failure_category`; fallback-backed rows therefore remain `provenance_unknown_public_metadata_absent`.
- `017641` has a real quality-gate `block` after public extraction, but this gate could not classify it as `quality_blocked_after_provenance` because public provenance did not first prove fallback eligibility.
- `110020` / `017641` remain excluded from clean baseline coverage and cannot enter golden/baseline corpus from this gate.
- Pure FOF coverage and bond positive-risk evidence residuals remain open.

## Next Entry Point

`source provenance primary-failure-category propagation design gate`

The next gate must be design/plan/review first. It may decide whether and how to persist or publicly project the repository primary failure category into source provenance outputs without weakening fail-closed fallback semantics or changing `FundDocumentRepository` source strategy. It must not directly promote index/QDII rows, mutate golden/baseline fixtures, alter FQ0-FQ6, or change renderer/default product behavior.
