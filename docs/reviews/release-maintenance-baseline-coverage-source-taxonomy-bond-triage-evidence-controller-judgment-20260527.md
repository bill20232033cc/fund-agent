# Controller Judgment: Baseline Coverage / Source Recovery / Taxonomy + Bond Triage Evidence

> Date: 2026-05-27
> Controller: Codex
> Gate: `baseline coverage / source recovery / taxonomy + bond extraction triage`
> Evidence: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-20260527.md`
> Reviews:
> - `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-review-mimo-20260527.md`
> - `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-review-glm-20260527.md`
> Verdict: **ACCEPTED LOCALLY**

## Evidence Judgment

Subgate 1 evidence is accepted. The run stayed within the authorized public-output path: `extraction-snapshot`, `extraction-score`, `quality-gate`, accepted artifacts, tracked code context, and `git diff --check`. It did not use direct production PDF reads, cache inspection, source helpers, downloaders, or ad hoc annual-report parsing.

Track 1B is accepted as `not_run_no_approved_candidates` because the controller did not provide replacement candidates for index/QDII/FOF probing.

## Field Classification Judgment

| Field | Accepted classification | Controller judgment |
|---|---|---|
| `turnover_rate` | `needs_more_evidence` | Public CLI evidence shows no extracted value and no anchor, but cannot prove source absence or bond applicability. No implementation authorized. |
| `holder_structure` | `needs_more_evidence` | Public CLI evidence cannot distinguish disclosure absence from extractor limitation. No implementation authorized. |
| `holdings_snapshot` | `bond_lens_contract_gap` | Current score expects equity-shaped stock/industry holdings while `006597` is `bond_fund`; this needs a bond-lens evidence contract before code changes. |
| `share_change` | `extractor_gap` | Public snapshot note gives a concrete root cause: §10 has multiple share columns and current rules cannot reliably select the corresponding share class. This is the only field ready for a narrow implementation plan. |
| `investor_return` | `score_contract_gap` | It is not equity-only and should not be marked bond N/A. The current gap is fallback/projection contract work, not the immediate P1 blocker. |
| `nav_data` anchor status | `score_contract_gap` | NAV data exists through external cache, but annual-report anchor semantics do not apply. This belongs to future external evidence provenance / source-contract work. |

## Reviewer Findings Judgment

AgentMiMo returned `PASS`; AgentGLM returned `PASS`. All findings were informational and are accepted:

- `share_change` is the most actionable narrow extractor gap;
- `holdings_snapshot` has broader bond-lens contract implications;
- quality gate `block` is intentionally preserved and must not be weakened;
- no artifact correction, rerun, or closeout blocker exists.

## Next Entry Point

Proceed to `share_change focused implementation plan + bond-lens contract design choice plan/review`.

Allowed next scope:

- plan/review only first;
- define a narrow `share_change` implementation plan from the observed share-class selection ambiguity;
- decide whether `holdings_snapshot` needs a bond-lens CHAPTER_CONTRACT / score-applicability design gate before implementation;
- keep `turnover_rate` and `holder_structure` evidence-only until a reviewed source or policy proves applicability;
- keep `investor_return` and `nav_data` in future score/evidence-contract work.

Forbidden:

- no implementation before plan review and controller judgment;
- no renderer/FQ0-FQ6 weakening/Service/CLI default/Host/Agent/dayu/source fallback/direct PDF/cache/helper/golden corpus changes;
- no durable baseline promotion.

## Validation

- Subgate 1 commands completed and are recorded in the evidence artifact.
- AgentMiMo evidence review verdict: `PASS`.
- AgentGLM evidence review verdict: `PASS`.
- `git diff --check`: passed.
