# Release Maintenance: Post-Provenance Coverage Recovery Decision Plan

> Worker: AgentCodex planning worker, not controller  
> Date: 2026-05-27  
> Gate: `post-provenance coverage recovery decision plan/review gate`  
> Scope: plan artifact only; no implementation, no promotion, no `docs/implementation-control.md` update

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate from Startup Packet | `source provenance post-implementation bounded evidence rerun accepted locally` |
| Current requested gate | `post-provenance coverage recovery decision plan/review gate` |
| Next entry point | plan/review decision gate; must use Startup Packet replay and `$init-agents` / tmux multi-agent flow |
| Latest checkpoint | `source provenance post-implementation bounded evidence rerun local accepted commit; use latest branch HEAD for exact hash` |
| Current truth sources replayed | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted artifacts listed below |
| Accepted artifacts used | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md`; `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md` |

Current allowed scope:

- Reconcile accepted source provenance rerun evidence with small baseline corpus v1 coverage needs.
- Decide, through plan/review/controller judgment, whether `110020` should enter a later reviewed coverage-candidate gate.
- Decide whether `017641` should enter a later `manager_strategy_text` extraction / quality triage gate or remain replacement-bound.
- Identify which residual blockers still prevent `golden answer corpus v1`.
- Produce reviewable artifacts under `docs/reviews/`.

Current forbidden scope:

- No code implementation.
- No renderer, FQ0-FQ6, Service/CLI default `analyze` / `checklist`, Host/Agent/dayu, `FundDocumentRepository`, source strategy, source-helper fallback semantics, extractor logic, `fund_type.py`, fixture, baseline, or golden corpus changes.
- No direct PDF/cache/source-helper inspection.
- No durable baseline, clean denominator, fixture, report-quality corpus, or golden promotion.
- No GitHub mutation, push, PR, merge, branch deletion, or commit.

## Reconciliation

This gate should not enter user-facing long-term `golden answer corpus v1` directly.

The accepted small baseline corpus v1 run was evidence-only. It evaluated eight candidate rows across seven unique fund codes, but accepted only three clean evaluated fund-type slots (`004393` active, `004194` enhanced index, `006597` bond), kept index/QDII fallback rows excluded, kept FOF attempts as data-gap / taxonomy residuals, and explicitly concluded that `golden answer corpus v1` entry conditions were not satisfied.

The accepted post-implementation source provenance rerun changes the index/QDII source picture but does not itself promote either sample. `110020` and `017641` now expose public complete source provenance with `primary_failure_category=unavailable` and `fallback_eligibility=eligible`; that resolves the previous unknown-fallback-source blocker. It does not resolve quality, fund-type coverage, reviewed-fact freeze, fixture promotion, or golden-corpus readiness. `110020` becomes review-eligible because quality is `warn`; `017641` remains quality-blocked because `manager_strategy_text` is a P0 block.

Therefore the next needed unit is a post-provenance coverage recovery decision gate: a narrow decision gate that converts newly accepted provenance evidence into ordered next gates, without treating review eligibility as promotion.

## Evidence Table

| Sample | Accepted current state | Accepted quality / blocker | Terminal state | Promotion disposition | Source artifact |
|---|---|---|---|---|---|
| `110020` / 2024 | Source provenance complete; `fallback_used=true`; `primary_failure_category=unavailable`; `fallback_eligibility=eligible`; public row consistency passed. | Quality gate `warn`; public notes cite `turnover_rate` P1 warn and strict golden not configured. | `provenance_eligible_for_next_review` | `not_promoted` | source provenance rerun artifact + controller judgment |
| `017641` / 2024 | Source provenance complete; `fallback_used=true`; `primary_failure_category=unavailable`; `fallback_eligibility=eligible`; public row consistency passed. | Quality gate `block`; public notes cite `manager_strategy_text` FQ2/FQ3 P0 block, plus P1 warnings. | `quality_blocked_after_provenance` | `not_promoted` | source provenance rerun artifact + controller judgment |
| `004393` / 2024 | Clean evaluated active-fund candidate; repository path and public smoke/snapshot/score/gate succeeded. | Quality gate `warn`; active Chapter 3 turnover/style evidence gap remains a reviewed-fact / wording risk. | clean candidate, not `scoring_ready` | not durable baseline / not golden | small baseline corpus v1 run controller judgment |
| `004194` / 2024 | Clean evaluated enhanced-index candidate; comparable golden rows matched in the run. | Quality gate `warn`; `tracking_error`, `turnover_rate`, and methodology / constituent evidence remain gaps. | clean candidate, not `scoring_ready` | not durable baseline / not golden | small baseline corpus v1 run controller judgment |
| `006597` / 2024 | Clean evaluated bond candidate; later accepted bond-lens applicability work moved the equity-shaped holdings false blocker to an explicit replacement issue path. | Current accepted state after bond-lens implementation: quality `warn`, not `pass`; `bond_risk_evidence_missing.baseline_blocking=true`; residual `holder_structure`, `share_change`, and `turnover_rate` remain. | evidence candidate with baseline-blocking residuals | not durable baseline / not golden | accepted baseline/bond-lens controller judgments |
| Small-sample FOF data gaps (`007721` / 2024, `017970` / 2024) | Kept visible as data-gap / taxonomy-pending attempts; `017970` also had fallback-blocked history before provenance work. | Cannot count QDII-FOF as pure FOF without a taxonomy gate; no accepted pure `fof_fund` repository-verified candidate exists. | `data_gap` / `taxonomy_pending` residual | not durable baseline / not golden | small baseline corpus v1 run controller judgment |

## Decision Candidates

### Candidate A: `110020 reviewed coverage candidate decision gate`

Purpose: decide whether `110020` / 2024 should become an index slot coverage candidate for a later baseline/golden preflight.

Entry conditions:

- Accepted provenance tuple remains public and complete: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`.
- Accepted quality state remains `warn`, not `block`.
- The gate is plan/review first and treats `110020` as candidate review, not promotion.

Forbidden:

- No durable baseline / golden / fixture promotion.
- No source strategy, fallback semantics, FQ0-FQ6, renderer, Service/CLI, Host/Agent/dayu, or extractor changes.
- No direct cache/PDF/source-helper inspection.

Validation evidence:

- Reuse accepted public provenance rerun artifact.
- If controller authorizes evidence collection later, only public CLI paths and ignored run outputs are allowed.
- Artifact must record unresolved `turnover_rate` / strict-golden-not-configured implications before any baseline decision.

### Candidate B: `017641 manager_strategy_text extraction/quality triage gate`

Purpose: decide whether QDII coverage should proceed by fixing / classifying the `manager_strategy_text` P0 quality block for `017641` / 2024 or by replacing the candidate.

Entry conditions:

- Accepted provenance tuple remains complete and eligible, so source is no longer the blocker.
- The accepted quality blocker is explicitly `manager_strategy_text` FQ2/FQ3 P0, not a generic source or correctness issue.
- Gate starts with plan/review; implementation is not authorized until a later accepted implementation plan.

Forbidden:

- No extractor implementation in this decision plan.
- No quality-gate weakening or P0 reclassification to make the row pass.
- No QDII subtype redesign or `fund_type.py` changes unless a later taxonomy/design gate accepts them.

Validation evidence:

- Use accepted public quality output identifying `manager_strategy_text`.
- Plan must separate possible outcomes: extraction bug, disclosure absence / accepted data gap, QDII policy issue, or replacement.
- Stop before implementation if public evidence cannot distinguish root cause with logic/data同源 proof.

### Candidate C: `pure FOF coverage/taxonomy gate`

Purpose: recover FOF representative coverage without falsely counting QDII-FOF attempts as pure FOF.

Entry conditions:

- Controller decides FOF coverage is the next dominant blocker after source-provenance recovery.
- Either approved pure FOF candidates exist for repository-safe probing, or the gate is explicitly a taxonomy / precedence design gate.

Forbidden:

- Do not count `007721` or `017970` as pure FOF coverage solely from prior QDII-FOF attempts.
- Do not alter `fund_type.py` or taxonomy behavior without a dedicated reviewed design/implementation gate.
- Do not promote any FOF row to fixtures/golden.

Validation evidence:

- Accepted small baseline artifact for current FOF data-gap state.
- For future probing, public repository paths only and tracked summary artifact only.

### Candidate D: `bond positive-risk evidence or remaining baseline-blocking residual gate`

Purpose: decide whether bond coverage should continue by adding positive `bond_risk_evidence.v1` evidence input / contract, or by resolving remaining `006597` P1 gaps.

Entry conditions:

- Use accepted bond-lens implementation judgment: `006597` is `warn`, not `pass`, and still baseline-blocked by `bond_risk_evidence_missing.baseline_blocking=true`.
- Candidate gate must decide between positive bond-risk evidence design and residual evidence triage; it must not merely suppress equity holdings fields.

Forbidden:

- No weakening of quality thresholds or silent N/A treatment.
- No golden route while `baseline_blocking=true` persists.
- No direct PDF/cache/source-helper access.

Validation evidence:

- Accepted bond-lens implementation evidence showing applicable denominator and explicit replacement issue.
- Future gate must prove `006597` improves by adding/reviewing bond-risk evidence, not by hiding missing evidence.

### Candidate E: `golden answer corpus v1 entry gate`

Purpose: eventually promote reviewed, representative, source-safe, quality-accepted samples into golden answer corpus v1.

Current status: not ready.

Unmet prerequisites:

- Coverage is still below the 5-10 representative target.
- Pure FOF coverage is unresolved.
- `017641` QDII is quality-blocked.
- `006597` bond remains baseline-blocked by missing positive bond-risk evidence and residual P1 gaps.
- `110020` is only review-eligible and not yet reviewed for baseline suitability.
- No separate fixture-promotion gate has accepted durable artifacts.

Forbidden:

- Do not enter golden corpus from this gate.
- Do not promote any local scoring, writing, source, snapshot, or quality outputs as durable fixtures.

Validation evidence required before future entry:

- Reviewed candidate matrix with source-safe provenance, quality `pass` or accepted `warn`, fund-type coverage, reviewed facts, baseline-blocking residuals resolved or explicitly accepted, and separate fixture/golden promotion controller judgment.

## Recommended Minimal Next Step

Recommend two small decision gates, in this order:

1. `110020 reviewed coverage candidate decision gate`
2. `017641 manager_strategy_text extraction/quality triage gate`

Why this is minimal:

- These two gates directly consume the new accepted provenance evidence and avoid reopening already-settled source propagation work.
- `110020` is the only newly source-recovered row that is quality `warn`, so it is the smallest path to recover the missing index slot without changing production behavior.
- `017641` is the paired QDII row whose source blocker is now resolved but whose quality blocker is precise and P0; triaging it decides whether QDII coverage should be repair-first or replacement-first.
- FOF and bond remain real blockers, but neither was changed by the post-provenance rerun. They should stay as parallel residual gates after the newly unlocked source decisions are made.

Why this does not break the product path:

- Both recommended gates are plan/review decision gates.
- They do not alter `fund-analysis analyze`, `fund-analysis checklist`, renderer output, FQ0-FQ6 semantics, source fallback semantics, or repository behavior.
- They use accepted public CLI evidence and review artifacts as inputs, not private cache/PDF/source-helper inspection.
- Every row remains `not_promoted` until a later dedicated baseline/golden promotion gate.

## Acceptance Matrix

| Recommended gate | Required artifact | Required review | Validation | Stop condition |
|---|---|---|---|---|
| `110020 reviewed coverage candidate decision gate` | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-20260527.md` | MiMo + GLM independent plan reviews and controller judgment | Reconcile accepted provenance-complete eligible state with quality `warn`; list unresolved P1/golden/fact-review gaps; prove no promotion | Stop if plan attempts durable baseline/golden promotion, source strategy changes, or direct cache/PDF/source-helper inspection |
| `017641 manager_strategy_text extraction/quality triage gate` | `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-20260527.md` | MiMo + GLM independent plan reviews and controller judgment | Classify next action from accepted public quality evidence: extraction bug, data gap, policy/taxonomy issue, or replacement path | Stop if plan weakens P0/FQ2/FQ3, implements extractor changes, or infers root cause without same-source evidence |

Optional later gates, not recommended as the immediate next step:

| Later gate | Why deferred |
|---|---|
| `pure FOF coverage/taxonomy gate` | Required before golden, but not unlocked by the provenance rerun; needs approved pure FOF candidates or taxonomy design scope. |
| `bond positive-risk evidence or remaining baseline-blocking residual gate` | Required before golden, but current accepted evidence already says it is a separate bond-risk / P1 residual path. |
| `golden answer corpus v1 entry gate` | Blocked by coverage, FOF, QDII quality, bond baseline-blocking residuals, candidate review, and fixture-promotion prerequisites. |

## Explicit Non-Goals

- Do not change source code.
- Do not change current v0 renderer or 8-chapter output.
- Do not change FQ0-FQ6 quality gate behavior, thresholds, severity, or policy.
- Do not change Service/CLI defaults for `analyze` or `checklist`.
- Do not change `FundDocumentRepository`, source strategy, source helper fallback semantics, cache behavior, PDF adapters, or downloaders.
- Do not create Host/Agent packages, introduce `dayu.host` / `dayu.engine`, or build Dayu runtime integration.
- Do not change extractors, `fund_type.py`, golden answers, baseline fixtures, durable corpus files, or report-quality fixtures.
- Do not promote any sample to durable baseline, clean denominator, fixture, or golden answer corpus.
- Do not run GitHub mutations, push, create PR, mark ready, merge, close PRs, delete branches, or commit.

## Handoff Recommendation

Controller should route this artifact to independent plan review. If accepted, the next controller-owned entry should be `110020 reviewed coverage candidate decision gate`, with `017641 manager_strategy_text extraction/quality triage gate` either immediately following or run as a second narrow planning gate under the same no-promotion discipline.
