# 110020 Reviewed Coverage Candidate Decision Plan — Controller Judgment

> Controller: Codex  
> Date: 2026-05-27  
> Gate: `110020 reviewed coverage candidate decision gate`  
> Latest prior accepted checkpoint: `188f150 docs: accept post provenance recovery plan`

## Startup Alignment

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `110020 reviewed coverage candidate decision gate` |
| Startup Packet next entry point | `110020 reviewed coverage candidate decision gate` |
| Switch from Startup Packet? | No. This judgment completes the current Startup Packet next entry point. |

## Evidence Reviewed

| Purpose | Artifact |
|---|---|
| Plan | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-20260527.md` |
| Initial review: MiMo | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-review-mimo-20260527.md` |
| Initial review: GLM | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-review-glm-20260527.md` |
| Targeted re-review: MiMo | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-rereview-mimo-20260527.md` |
| Targeted re-review: GLM | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-rereview-glm-20260527.md` |
| Prior recovery decision | `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-controller-judgment-20260527.md` |

## Decision

Accepted.

`110020` / 2024 is accepted only as input to a later public-only reviewed coverage candidate evidence gate. This is not a durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus promotion.

Accepted current state for `110020` / 2024:

| Field | Accepted state |
|---|---|
| `fund_type_slot` | `index_fund` |
| `source_strategy` | `primary_then_fallback` |
| `resolved_source_name` | `eastmoney` |
| `source_provenance_status` | `complete` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `quality_gate_status` | `warn` |
| `terminal_state` | `provenance_eligible_for_next_review` |
| `promotion_disposition` | `not_promoted` |

The next gate may run only the reviewed public evidence matrix specified in the accepted plan, with generated outputs remaining ignored and one tracked summary artifact under `docs/reviews/`.

## Finding Judgments

| Finding | Source | Judgment | Handling |
|---|---|---|---|
| M1: missing index-lens evidence sufficiency definition | MiMo | accepted and fixed | Plan now requires independent `index_evidence_assessment` for `index_profile`, `tracking_error`, and benchmark-methodology / constituents / tracking evidence. |
| M2: strict golden not configured needs disposition | MiMo | accepted and fixed | Plan now carries strict golden absence as residual: correctness cannot be reviewed until same-year golden coverage exists. |
| M3: stop conditions too narrow | MiMo | accepted and fixed | Plan now stops on new P0/P1 warnings, source/provenance tuple regression, source strategy / resolved source changes, reviewer `BLOCK`, or insufficient reviews without explicit controller risk acceptance. |
| L1: fund type not explicit | MiMo | accepted and fixed | Plan now records `fund_type_slot=index_fund`. |
| L2: reviewer `BLOCK` handling unclear | MiMo | accepted and fixed | Plan now requires halt until fixed and re-reviewed on any reviewer `BLOCK`. |
| F1: index-specific evidence assessment should be independent | GLM | accepted and fixed | Plan now adds an independent index evidence assessment step and artifact requirement. |
| F2: `--source-csv` identity should be recorded | GLM | accepted and fixed | Plan now requires CSV identity/version note and records current observed CSV state. |

Both targeted re-reviews returned `PASS`; no blocking/material finding remains open.

## Accepted Next Gate

`110020 reviewed coverage candidate evidence gate`

The next evidence gate must:

- Use only public CLI commands from the accepted plan.
- Keep generated outputs under ignored `reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/`.
- Write only `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-20260527.md` as tracked evidence summary.
- Include an independent `index_evidence_assessment`.
- Keep `promotion_disposition=not_promoted`.
- Stop on any provenance regression, quality `block`, new P0/P1 warnings beyond accepted warning set, reviewer `BLOCK`, direct PDF/cache/source-helper access, or any attempt to promote.

## Validation

- Initial plan review: MiMo `PASS_WITH_FINDINGS`.
- Initial plan review: GLM `PASS_WITH_FINDINGS`.
- Targeted re-review: MiMo `PASS`.
- Targeted re-review: GLM `PASS`.
- `git diff --check`: passed.

## Residual Risks

- `110020` still lacks same-year strict golden coverage and reviewed-fact freeze.
- `turnover_rate` remains P1 warn and must be carried forward.
- Index-lens evidence sufficiency is not proven until the next evidence gate.
- Broader corpus blockers remain: `017641` QDII `manager_strategy_text` quality block, pure FOF taxonomy/data gap, bond positive-risk evidence, and future fixture/golden promotion gates.
