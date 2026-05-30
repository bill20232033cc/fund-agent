# Controller Judgment: Baseline Coverage / Source Recovery / Taxonomy + Bond Triage Plan

> Date: 2026-05-27
> Controller: Codex
> Gate: `baseline coverage / source recovery / taxonomy + bond extraction triage plan/review`
> Plan: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-20260527.md`
> Reviews:
> - `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-review-mimo-20260527.md`
> - `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-review-glm-20260527.md`
> Re-reviews:
> - `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-rereview-mimo-20260527.md`
> - `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-rereview-glm-20260527.md`
> Verdict: **ACCEPTED FOR SUBGATE 1 EVIDENCE-ONLY TRIAGE**

## Startup Reconciliation

The Startup Packet says the current phase is `release maintenance`, the current gate is `small baseline corpus v1 accepted locally`, and the next entry point is `baseline coverage / source recovery / taxonomy + bond extraction triage plan/review`.

The latest accepted checkpoint before this plan is `297f5cb`. Gate 4 proved small baseline corpus v1 is accepted as evidence but is not eligible for `golden answer corpus v1`.

## Findings Judgment

| Finding | Judgment | Controller rationale |
|---|---|---|
| MiMo M1: no-direct-PDF field-existence investigation path | Accepted; resolved | The revised plan now enumerates allowed evidence, forbidden evidence, and `needs-more-evidence` fallback when existing public/tracked evidence cannot prove field existence. |
| MiMo M2: `investor_return` omitted from bond triage | Accepted; resolved | The revised plan adds `investor_return` to Problem C, the triage checklist, and stop conditions; it may not be treated as not-applicable for bond funds without an accepted design/template decision. |
| GLM F3: replacement-candidate dependency may stall Subgate 1 | Accepted; resolved | The revised plan splits Subgate 1 into Track 1A bond triage and Track 1B coverage probing; Track 1B may close as `not_run_no_approved_candidates` without blocking Track 1A. |
| GLM info findings: Gate 4 reconciliation, subgate decomposition, fallback, FOF, bond triage, scope, verifier, golden criteria | Accepted | These findings confirm the plan aligns with current truth and keeps implementation gated behind same-source evidence. |

## Authorized Next Work

Authorize **Subgate 1 evidence-only triage** only.

Allowed:

- Track 1A: classify `006597` / 2024 bond missing fields from existing public CLI outputs, current scratch evidence, tracked extractor tests/fixtures if already present, accepted design/template rules, and newly generated public CLI snapshot/score/quality-gate outputs.
- Track 1B: probe index/QDII/FOF replacement candidates only if the controller supplies or approves candidate codes; otherwise close as `not_run_no_approved_candidates`.
- write one tracked evidence artifact under `docs/reviews/`;
- keep bulk outputs under ignored scratch paths;
- run `git diff --check`.

Forbidden:

- implementation changes;
- direct production PDF reads, cache inspection, concrete source adapter/helper/downloader calls, or ad hoc parsing of production annual-report files outside public paths;
- renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, `FundDocumentRepository`, source fallback semantics, extractors, fixtures, golden corpus, package config, or GitHub mutation;
- classifying `investor_return` as bond-fund not-applicable without an accepted design/template decision;
- counting QDII-FOF as pure FOF without a taxonomy gate;
- promoting any candidate to durable baseline or golden corpus.

## Evidence Artifact Requirements

The Subgate 1 evidence artifact must include:

- `006597` field-level classification for at least `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`, `investor_return`, and `nav_data` anchor status;
- allowed evidence source used for each classification;
- whether each classification points to score applicability, extractor/anchor/projection, bond-lens contract, or `needs-more-evidence`;
- Track 1B status: replacement candidates probed with command evidence, or `not_run_no_approved_candidates`;
- explicit next recommendation: Slice 2A, 2B, 2C, 2D, more evidence, or no-op;
- `git diff --check` result.

## Verdict

The plan is accepted. Proceed to Subgate 1 evidence-only triage; do not implement until that evidence is reviewed and a later controller judgment authorizes a narrower implementation slice.
