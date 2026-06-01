# Replacement / Exclusion Candidate Selection — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `replacement/exclusion candidate selection gate for QDII/index/FOF coverage`
> Decision artifact: `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `baseline coverage disposition decision plan accepted locally` |
| Startup Packet next entry point | `replacement/exclusion candidate selection gate for QDII/index/FOF coverage; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `b919e5e docs: accept baseline coverage disposition plan` |

This gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Disposition Matrix

| Slot / candidate | Accepted disposition | Owner | Revisit condition |
|---|---|---|---|
| Index / `110020` / 2024 | `include_for_later_review` | Future index reviewed-fact / index-evidence reviewer assigned by controller | After accepted index reviewed fact freeze / evidence sufficiency gate proves methodology, constituents, reviewed fact identity, and strict golden absence disposition. |
| QDII / `017641` / 2024 | `replace` | QDII replacement candidate selection owner assigned by controller | After accepted replacement candidate selection plan defines valid replacement criteria, source safety, stop conditions, and evidence commands. |
| FOF slot | `needs_taxonomy_gate` | FOF taxonomy / pure FOF candidate owner assigned by controller | After pure FOF entry contract / candidate path, or explicit `FOF deferred from golden v1` decision with owner and revisit trigger. |
| Active / `004393` / 2024 | `include_for_later_review` | Future baseline preflight owner | Only during a later durable baseline or golden preflight after all coverage and fixture-promotion prerequisites are met. |
| Enhanced-index / `004194` / 2024 | `include_for_later_review` | Future baseline preflight owner | Only during a later durable baseline or golden preflight after all coverage and fixture-promotion prerequisites are met. |
| Bond / `006597` / 2024 | `needs_evidence_gate` | Separate bond positive-risk evidence owner assigned by controller | After accepted positive bond-risk evidence contract or accepted bond exclusion/deferral decision resolves `bond_risk_evidence_missing.baseline_blocking=true`. |

No row is promoted to durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-review-mimo-20260527.md` | `PASS` |
| AgentDS | `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |

AgentGLM was initially assigned but did not produce a review artifact after follow-up; per user direction the second independent review was switched to AgentDS.

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS F1: next cursor name `QDII replacement candidate evidence gate` could imply skipping plan-before-evidence | **accepted; plan-first rename required** | The next entry point must be `QDII replacement candidate selection plan gate`; evidence CLI commands are not authorized until that plan is reviewed and accepted. |
| DS F2: disposition rows lack direct artifact cross-references | **deferred / documentation precision** | The matrix values are correct and reviewed; future disposition artifacts should cite controller judgment paths in-row where feasible. |
| DS F3: worker artifact requires explicit controller acceptance | **accepted and satisfied by this judgment** | This artifact and control-doc update provide the required controller acceptance before entering any next gate. |

No blocking finding remains. No re-review is required.

## Accepted Next Entry Point

`QDII replacement candidate selection plan gate`

Required next-gate constraints:

- Plan before evidence. Do not run replacement evidence CLI commands until a replacement selection/evidence plan is reviewed and accepted.
- Define valid QDII replacement criteria, candidate source, source-safety requirements, stop conditions, exact evidence commands, and no-promotion guardrails.
- Preserve `017641` as `replace` / `not_promoted`; do not convert it into extractor work or policy change.
- Preserve index, FOF, active/enhanced-index, and bond dispositions as accepted above.
- Do not enter golden corpus v1 or durable baseline fixture gate.

## Validation

- `git diff --check` passed before this judgment.
- This gate is docs/control/review only; no source or test code changed.

## Non-Goals Preserved

No new evidence, extraction/analyze/checklist/quality CLI, code, tests, renderer, FQ0-FQ6, Service/CLI, source strategy, `FundDocumentRepository`, source-helper, direct PDF/cache access, Host/Agent/dayu runtime, taxonomy implementation, extractor implementation, baseline/golden fixture promotion, GitHub mutation, push, PR, merge, or branch deletion occurred.
