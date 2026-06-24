# Evidence Confirm Productionization EC-P2 Plan Controller Judgment

## Verdict

`ACCEPT_EC_P2_PLAN_READY_FOR_IMPLEMENTATION_NOT_READY`

## Scope

- Work unit: `Evidence Confirm Productionization Program`
- Slice: `EC-P2 Repository-bounded Live Source/PDF Evidence Gate`
- Gate classification: `heavy`
- Accepted plan: `docs/reviews/evidence-confirm-productionization-ec-p2-plan-20260622.md`
- Initial plan review: `docs/reviews/plan-review-20260622-160546.md`
- Targeted re-review: `docs/reviews/plan-review-20260622-160904.md`
- User authorization: `同意 EC-P2：sample 004393/2025，授权 repository-bounded live/PDF 命令。`

This judgment accepts the EC-P2 implementation plan only. It does not implement source code, run live/network/PDF/provider/LLM commands, instantiate `FundDocumentRepository`, push, mark PR-40 ready, merge, or change release/readiness.

## Decision

The EC-P2 plan is accepted after targeted fix/re-review.

The initial plan review failed because:

- the live command lacked an authorized `ChapterFactProjection` source even though the runner contract required one;
- the plan referenced `scripts/evidence_confirm_ec_p2_live_sample.py` without including it in the allowed write set or validation, and the existing import isolation test contradicted the planned `load_annual_report()` runner.

The amended plan fixes both blockers:

- The live command may build only an EC-P2 pathway-smoke projection from the loaded `ParsedAnnualReport.sections` after `FundDocumentRepository.load_annual_report("004393", 2025, force_refresh=True)` succeeds.
- The smoke projection is explicitly not product fact correctness, not field-family source truth, not semantic entailment, not golden/readiness evidence, and not authorized for Service/UI/renderer/quality-gate consumption.
- `scripts/evidence_confirm_ec_p2_live_sample.py` is now in the allowed write set and validation path.
- Import isolation is reframed from source-text absence of `"load_annual_report"` to the real boundary: no import-time repository instantiation, network, PDF/cache read, or repository method call.

## Finding Disposition

| Finding | Controller disposition |
|---|---|
| PR-1 live command lacks an authorized projection source | accepted; fixed by EC-P2 pathway-smoke projection sourced only from loaded `ParsedAnnualReport.sections` |
| PR-2 write set and import isolation test conflict with planned runner/script | accepted; fixed by adding script to allowed files/validation and updating import isolation test expectation |

## Validation

- Initial plan review conclusion: `fail` in `docs/reviews/plan-review-20260622-160546.md`.
- Targeted re-review conclusion: `pass` in `docs/reviews/plan-review-20260622-160904.md`.
- `git diff --check -- docs/reviews/evidence-confirm-productionization-ec-p2-plan-20260622.md docs/reviews/plan-review-20260622-160546.md docs/reviews/plan-review-20260622-160904.md` passed.

No live, network, PDF, provider, LLM, Service runtime, UI runtime, renderer, quality-gate runtime, PR external-state or release command was run in this planning checkpoint.

## Residual Owners

| Residual | Owner | Destination |
|---|---|---|
| EC-P2 live smoke projection does not prove field correctness | Evidence Confirm / Fund owner | EC-P3 or later source-truth/readiness gates |
| Semantic entailment remains unimplemented | Evidence Confirm semantic owner | EC-P4 / EC-P5 |
| Service/UI/renderer/quality-gate integration remains unimplemented | Service/UI/renderer/quality-gate owners | EC-P6 / EC-P7 / EC-P8 |
| Release/readiness remains unproven | Release/readiness owner | EC-P10 / EC-P11 |
| Multi-sample live matrix remains unproven | Evidence Confirm / source owner | EC-P2 follow-up only after single positive sample is accepted |

## Next Gate

`EC-P2 Repository-bounded Live Source/PDF Evidence Implementation Gate`

Allowed next implementation scope:

- Add EC-P2 repository runner/facade in `fund_agent/fund/evidence_confirm_sources.py`.
- Add fake repository and live-smoke projection tests in `tests/fund/test_evidence_confirm_sources.py`.
- Add authorized single-sample script `scripts/evidence_confirm_ec_p2_live_sample.py`.
- Update `fund_agent/fund/README.md` and `tests/README.md` for the new Fund/test surface.
- Write EC-P2 implementation evidence artifact under `docs/reviews/`.

Forbidden in implementation until the implementation/review gates accept it:

- live execution before no-live implementation and review acceptance;
- direct PDF/cache/source helper calls outside `FundDocumentRepository.load_annual_report()`;
- Service/UI/Host/renderer/quality-gate behavior changes;
- source fallback behavior changes;
- `EvidenceSourceKind` or public `EvidenceAnchor` expansion;
- semantic provider/LLM execution;
- multi-sample live matrix;
- PR mark-ready, merge, release/readiness claims.
