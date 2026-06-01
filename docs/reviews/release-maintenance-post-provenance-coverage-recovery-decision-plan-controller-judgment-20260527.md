# Post-Provenance Coverage Recovery Decision Plan — Controller Judgment

> Controller: Codex  
> Date: 2026-05-27  
> Gate: `post-provenance coverage recovery decision plan/review gate`  
> Latest prior accepted checkpoint: `41b808c docs: reconcile design truth findings`

## Startup Reconciliation

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `docs-only truth reconciliation accepted locally` |
| Next entry point from Startup Packet | `post-provenance coverage recovery decision plan/review gate` |
| Current cursor | Resume after accepted docs-only truth reconciliation; do not restart roadmap Gate 1 |

Roadmap gates already accepted and not to be rerun:

| Roadmap gate | Cursor judgment |
|---|---|
| 1. correctness report_year scope fix | accepted; cite existing controller judgment and validation evidence |
| 2. core analyze/checklist reliability hardening | accepted; cite existing controller judgment and validation evidence |
| 3. active-fund Chapter 3 renderer minimal integration | accepted; design truth reconciled as current implemented scoped behavior |
| 4. small baseline corpus v1 | accepted as evidence run only; no durable baseline / golden promotion |

Roadmap Gate 5 `golden answer corpus v1` is not ready. Current blockers remain coverage, FOF/taxonomy, QDII quality, bond baseline-blocking residuals, reviewed-fact readiness, and fixture-promotion gate absence.

## Evidence Reviewed

| Purpose | Artifact |
|---|---|
| Plan | `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-20260527.md` |
| Review: MiMo | `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-review-mimo-20260527.md` |
| Review: GLM | `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-review-glm-20260527.md` |
| Prior source-provenance rerun controller judgment | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` |
| Docs-only truth reconciliation | `docs/reviews/release-maintenance-docs-truth-reconciliation-20260527.md` |

## Decision

Accepted with non-blocking refinements.

The plan correctly avoids entering `golden answer corpus v1` directly and chooses the next cursor from accepted current evidence: `110020` is source-provenance complete and quality `warn`, so it may enter a reviewed coverage-candidate decision gate; `017641` is source-provenance complete but quality `block` on `manager_strategy_text`, so it needs a separate extraction/quality triage gate before any QDII baseline use.

The plan artifact was produced before the docs-only truth reconciliation gate, but its next-entry conclusion remains valid after reconciliation. The docs-only gate changed design-truth wording for active-fund Chapter 3 and final judgment quality-gate semantics; it did not change the accepted provenance evidence, sample terminal states, or post-provenance coverage blockers.

## Review Finding Judgments

| Finding | Source | Judgment | Controller handling |
|---|---|---|---|
| Candidate E should explicitly include `004393` and `004194` golden-readiness residuals | GLM F1, non-blocking | accepted | Future golden-entry and candidate-review gates must carry `004393` active Chapter 3 turnover/style evidence residual and `004194` enhanced-index `tracking_error` / `turnover_rate` / methodology evidence residual. No plan rewrite required for this decision gate. |
| `110020` and `017641` gates could run in parallel because scopes do not overlap | GLM F2, non-blocking | accepted | Controller may run the two gates in parallel only if separate artifacts, separate reviewer handoffs, and non-overlapping implementation scopes are maintained. The safer default cursor remains `110020` first, then `017641`, unless concurrency improves throughput without weakening review. |
| MiMo PASS with low observations on explicit artifact paths for Candidate A / bond references | MiMo observations | accepted as guidance | Future gate artifacts should cite exact accepted artifact paths, especially for provenance and bond-lens evidence. |

No blocking or material finding remains open.

## Accepted Next Cursor

Primary next entry point:

1. `110020 reviewed coverage candidate decision gate`

Secondary allowed gate, either immediately after or in parallel if scoped separately:

2. `017641 manager_strategy_text extraction/quality triage gate`

Both gates must remain plan/review first, must keep all samples `not_promoted`, and must not enter golden answer corpus v1.

## Stop Conditions For Next Cursor

- Stop if any plan attempts durable baseline, fixture, clean-denominator, or golden promotion.
- Stop if any plan changes source strategy, `FundDocumentRepository`, source-helper fallback semantics, renderer, Service/CLI defaults, FQ0-FQ6, Host/Agent/dayu, or product behavior.
- Stop if `017641` triage weakens P0/FQ2/FQ3 or infers root cause without same-source evidence.
- Stop if current truth-source conflict reappears; enter docs-only reconciliation before implementation.

## Validation

- Plan review: MiMo `PASS`.
- Plan review: GLM `PASS_WITH_FINDINGS`; both findings are non-blocking and accepted above.
- `git diff --check`: passed.

## Next Entry Point

`110020 reviewed coverage candidate decision gate`

Controller may also prepare `017641 manager_strategy_text extraction/quality triage gate` as an adjacent narrow planning gate, but neither gate may promote samples or implement code without its own accepted plan/review.
