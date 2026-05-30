# Controller Judgment: bond-lens contract + baseline coverage recovery plan

> Controller: Codex
> Date: 2026-05-27
> Target plan: `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-20260527.md`
> Reviews: `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-review-mimo-20260527.md`, `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-review-glm-20260527.md`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this judgment | `share_change focused implementation accepted locally` |
| Next entry point reviewed | `bond-lens contract design + baseline coverage recovery plan/review` |
| Latest accepted checkpoint before this judgment | `5f07019` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, current accepted artifacts |

## Decision

Accepted.

The plan is accepted as a design/plan gate. It does not authorize source-code implementation by itself. The next safe entry is a narrow `bond-lens score applicability design` gate, followed by a separate implementation gate only if plan/review accepts exact file scope and validation.

The accepted plan makes the key first-principles decision: equity-shaped `holdings_snapshot` coverage is not an appropriate P1 requirement for `bond_fund`, but bond risk evidence cannot be silently marked N/A. The future contract must be fund-type-dependent and must replace equity holdings semantics with explicit bond-risk evidence, issue taxonomy, and failure behavior.

## Review Summary

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS` | Accepted. No material findings; no re-review required. |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted with non-blocking refinements below; no re-review required because findings do not change current plan scope. |

## Finding Disposition

| Finding | Reviewer severity | Controller status | Judgment |
|---|---:|---|---|
| F1: Chapter 2 bond preferred-lens gap not addressed | Informational | Deferred | This is a separate chapter-contract/template-lens concern. Current plan is scoped to `holdings_snapshot` score applicability and baseline coverage recovery. Record as future bond-lens template/contract residual; do not expand this gate. |
| F2: Convertibility / equity exposure missing from bond evidence groups | Low | Accepted as next-gate refinement | Before implementation, the bond-risk evidence design should explicitly include convertible-bond / equity-exposure evidence for secondary-bond or mixed-bond facets. This strengthens the contract without changing the plan's narrow gate sequencing. |
| F3: No taxonomy code for unknown/conflicted fund type | Informational | Deferred | The current plan already fails closed for unknown/conflicted types. Add a dedicated taxonomy code only if later output consumers need it. |
| F4: Gate C constant placement file scope | Informational | Accepted as scope guard | Future implementation should prefer the local `extraction_score.py` constant pattern. If `fund_type.py` or another module is needed, the implementation plan must explicitly expand allowed files before coding. |
| F5: FQ4 denominator effect for 006597 not explicitly computed | Informational | Accepted as validation requirement | Future implementation must compute/report the denominator effect and prove `006597` does not improve only by suppressing equity evidence without a replacement bond-risk issue. |

## Accepted Plan Boundaries

Allowed next:

- Design the exact bond-fund score-applicability contract for replacing equity-shaped `holdings_snapshot`.
- Keep index/QDII source recovery and pure FOF coverage as evidence/planning gates; do not weaken fallback semantics or count QDII-FOF as pure FOF.
- Keep `turnover_rate` and `holder_structure` as `needs_more_evidence`.
- Keep `investor_return` and `nav_data` as future score/evidence-contract work.

Forbidden until a later accepted implementation plan:

- Renderer changes.
- FQ0-FQ6 semantic weakening, threshold changes, or severity downgrades.
- Service/CLI default behavior changes.
- Host/Agent package creation or Dayu runtime integration.
- `FundDocumentRepository` source strategy, source-helper fallback, downloader, cache, or direct PDF access changes.
- Extractor logic changes.
- Golden corpus, durable baseline, or fixture promotion.
- Explicit parameter tunneling through `extra_payload`.
- GitHub mutation.

## Verifier Matrix

| Verifier | Result |
|---|---|
| Plan artifact | present at `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-20260527.md` |
| Plan review: MiMo | `PASS`, no material findings |
| Plan review: GLM | `PASS_WITH_FINDINGS`, no blocking/material findings |
| Controller judgment | accepted with non-blocking refinements |
| `git diff --check` | passed in plan artifact; controller rerun required before checkpoint commit |

## Next Entry Point

`bond-lens score applicability design gate`

Entry conditions:

- Start with Startup Packet replay.
- Use `$init-agents` / tmux multi-agent flow.
- Plan/review only first; no source/test implementation until accepted.
- Design must explicitly include convertible-bond / equity-exposure handling and FQ4 denominator validation requirement from this judgment.
