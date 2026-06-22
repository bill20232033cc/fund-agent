# Evidence Confirm Productionization Program Plan Controller Judgment

## Verdict

`ACCEPT_PLAN_READY_FOR_EC_P1A_IMPLEMENTATION_NOT_READY`

## Scope

- Work unit: `Evidence Confirm Productionization Program`
- Branch: `evidence-confirm-productionization`
- Gate classification: `heavy`
- Accepted plan: `docs/reviews/evidence-confirm-productionization-program-plan-20260622.md`
- Initial plan review: `docs/reviews/plan-review-20260622-133033.md`
- Targeted re-review: `docs/reviews/plan-review-20260622-134537.md`

This judgment accepts the program plan only. It does not implement source code, run live/network/PDF/provider/LLM commands, push, mutate PR-39, mark ready, merge, or change release/readiness.

## Decision

The amended plan is accepted as the controlling plan for the Evidence Confirm productionization program. The original plan review failed because EC-P1 assumed locator structures that current code does not provide:

- `ParsedTable` has no `table_id`.
- `ReportSection` has no paragraph/page text structure.
- `ParsedTable.rows` has no row-level identifiers.

The amended plan fixes those blockers by narrowing the first implementation gate to `EC-P1A ParsedAnnualReport Locator-contract No-live Materializer Gate`:

- `table_id` supports only the compatibility format `page-{page_number}-table-{table_index}` and otherwise fails closed.
- `row_locator` supports only zero-based `row-N` and otherwise fails closed.
- section excerpts use `ParsedAnnualReport.get_section_text(section_id)` with a fixed character bound and no paragraph/page slicing.
- `source_truth_status` defaults to `not_proven`; proven references require explicit request proof and source-admission checks.
- richer table IDs, row labels, paragraph/page windows, merged-cell reconstruction and live structure behavior are deferred to later gates.

## Finding Disposition

| Finding | Controller disposition |
|---|---|
| F1 `ParsedTable` lacks `table_id` | accepted, fixed by compatibility table-id regex plus fail-closed unsupported format |
| F2 `ReportSection` lacks paragraph/page structure | accepted, fixed by bounded `get_section_text()` section excerpt only |
| F3 `row_locator` mapping unspecified | accepted, fixed by exact zero-based `row-N` contract |
| F4 EC-P8 extension point unspecified | accepted, fixed by optional `evidence_confirm_summary` parameter on `run_quality_gate_for_bundle()`; no `score.json` mutation in EC-P8 |
| F5 EC-P1 structural edge tests missing | accepted, fixed by required tests for empty sections/tables, unsupported locators, out-of-range rows, empty excerpts and header/row mismatch |
| F6 Service request contract ambiguous | accepted, fixed by `FundAnalysisDeveloperOverrides.evidence_confirm_policy` opt-in for EC-P6; product default remains off |
| F7 Semantic protocol location ambiguous | accepted, fixed by placing `EvidenceEntailmentClient` protocol in Fund layer |

## Validation

- Plan review conclusion: `FAIL` in `docs/reviews/plan-review-20260622-133033.md`.
- Plan fix re-review conclusion: `PASS` in `docs/reviews/plan-review-20260622-134537.md`.
- `git diff --check -- docs/reviews/evidence-confirm-productionization-program-plan-20260622.md docs/reviews/plan-review-20260622-133033.md docs/reviews/plan-review-20260622-134537.md` passed.

No live, network, PDF, provider, LLM, Service runtime, UI runtime, quality-gate runtime, PR or release command was run in this planning checkpoint.

## Residual Owners

| Residual | Owner | Destination |
|---|---|---|
| Compatibility `page-{page}-table-{index}` table id may not cover live structures | Fund documents / Evidence Confirm owner | EC-P2 live source/PDF evidence gate |
| Current extractor `row_locator` values may not use zero-based `row-N` | Evidence Confirm owner | EC-P1A implementation must fail closed; richer locators deferred |
| Fixed section excerpt bound may truncate long-section evidence | Evidence Confirm owner | EC-P2 live evidence and later documents-model gate if needed |
| Semantic entailment remains unimplemented | Evidence Confirm semantic owner | EC-P4 / EC-P5 |
| Service/UI/renderer/quality-gate integration remains unimplemented | Service/UI/renderer/quality-gate owners | EC-P6 / EC-P7 / EC-P8 |
| Release/readiness remains unproven | Release/readiness owner | EC-P10 / EC-P11 |

## Next Gate

`EC-P1A ParsedAnnualReport Locator-contract No-live Materializer Implementation Gate`

Allowed next implementation scope:

- Add `fund_agent/fund/evidence_confirm_sources.py`.
- Add `tests/fund/test_evidence_confirm_sources.py`.
- Update `fund_agent/fund/README.md` and `tests/README.md` only if triggered by the new Fund/test surface.
- Preserve existing `evidence_confirm.v1` and `evidence_confirm.v2` behavior.

Forbidden in EC-P1A:

- live/network/PDF/provider/LLM commands;
- `FundDocumentRepository` instantiation;
- Service/UI/Host/renderer/quality-gate behavior changes;
- `EvidenceSourceKind` or public `EvidenceAnchor` expansion;
- source fallback behavior changes;
- PR ready/merge/release/readiness claims.
