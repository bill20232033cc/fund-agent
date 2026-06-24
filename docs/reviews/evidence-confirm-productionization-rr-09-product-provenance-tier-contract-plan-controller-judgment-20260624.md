# RR-09 Product Provenance Tier Contract Plan Controller Judgment

Final token:

`ACCEPT_RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`

## Gate

Gate: `RR-09 Product Provenance Tier Contract Plan Controller Judgment Gate`.

Classification: `heavy`, because the accepted plan changes the product Evidence Confirm summary contract and quality-gate disposition semantics for provenance blockers.

This is a controller judgment / accepted plan checkpoint only. It does not change production code, tests, runtime behavior, quality-gate output, checklist support, report-body rendering, provider/LLM defaults, PR state, tag, release or readiness. It does not run live/PDF, repository/source-helper/parser, product CLI or provider/LLM commands.

## Reviewed Inputs

- Plan artifact: `docs/reviews/evidence-confirm-productionization-rr-09-product-provenance-tier-contract-plan-20260624.md`
- Initial plan review: `docs/reviews/plan-review-20260624-144929.md`
- Plan-fix artifact: `docs/reviews/evidence-confirm-productionization-rr-09-product-provenance-tier-contract-plan-fix-20260624.md`
- Targeted re-review: `docs/reviews/plan-review-20260624-150102.md`

## Decision

The fixed plan is accepted as code-generation-ready for no-live implementation.

Accepted rationale:

- The plan defines a bounded pragmatic provenance contract: `section` is the current minimum release floor, `table` and `row` are stronger tiers, and `cell` is reserved because the current reference model has no proof-bearing cell field.
- The plan keeps strict deterministic V2 value-match failure visible as `strict_precision_residual` only when claim provenance already exists.
- Pathway failure and claim-level missing provenance remain blockers.
- The plan separates summary v2 computation, ECQ mapping and CLI safe visibility into ordered implementation slices.
- The targeted re-review confirms prior finding `001` is fixed: S1 now includes transitive Service and semantic summary consumers, shared fake repository fixtures, and the invariant that `reference_build_result=None` plus V2 pass is not provenance pass.

## Accepted Implementation Scope

### Slice S1: Summary V2 Provenance Contract

Next executable gate: `RR-09 Product Provenance Tier Contract No-live Implementation Gate - Slice S1`.

Allowed files:

- `fund_agent/fund/evidence_confirm_production.py`
- `fund_agent/services/fund_analysis_service.py`
- `tests/fund/test_evidence_confirm_production.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/fund/test_evidence_confirm_semantic.py`

Required validation:

```bash
uv run pytest tests/fund/test_evidence_confirm_production.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py
```

Binding constraints:

- Upgrade summary schema to `evidence_confirm_production_summary.v2`.
- Add provenance status/tier/count fields and strict precision issue ids exactly as planned.
- Derive provenance only from repository run result, V2 dimensions and existing reference metadata.
- Do not read repository/PDF/cache/source-helper/parser/provider/LLM/report body from the summary helper.
- Do not emit `cell`.
- Do not treat `reference_build_result=None` plus V2 pass as provenance pass.

### Slice S2: ECQ And CLI Safe Visibility

Slice S2 is authorized only after S1 is implemented, reviewed and accepted.

Allowed files:

- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_quality_gate_integration.py`
- `tests/ui/test_cli.py`
- `fund_agent/fund/README.md`
- `docs/design.md`

Required validation:

```bash
uv run pytest tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py
```

Binding constraints:

- ECQ1 pathway failure remains `block`.
- ECQ2 provenance missing is `block`.
- ECQ2 strict precision residual follows Evidence Confirm policy: `warn` under product `warn`, `block` under `block`.
- CLI may print only safe provenance status/tier/count lines.
- No issue ids, raw excerpts, paths, source URLs, parser payloads, provider payloads or report body may be printed.

## Non-goals

- No live/PDF, repository/source-helper/parser or product CLI execution.
- No provider/LLM execution or provider-backed semantic default-on.
- No report-body Evidence Confirm rendering.
- No checklist Evidence Confirm support.
- No FDD default-on parsing or direct Docling/pdfplumber/EID HTML consumption outside Fund documents/Processor boundaries.
- No row/cell proof invention from section/table excerpts.
- No release, tag, PR external mutation or readiness claim.
- No weakening of deterministic V2, ECQ or quality-gate failure visibility.

## Residuals

| Residual | Disposition |
|---|---|
| Existing R1-R4 strict V2 value-match failures | Optional A6 strict-precision evidence path after contract implementation |
| B1 `017641 / 2024` product quality-gate block | Separate RR-09 B1 residual gate |
| Report-body sentence-level provenance | Existing RR-S6 deferred report-body gate |
| Checklist Evidence Confirm support | Existing RR-S4 deferred checklist gate |
| `cell` provenance tier | Future reference model gate only if proof-bearing cell metadata exists |
| Release/readiness | Remains `NOT_READY` |

## Validation

Controller/static checks only:

- Verified the accepted plan, plan review, plan-fix and targeted re-review chain.
- Verified targeted re-review conclusion is `pass`.
- Verified finding `001` final status is `已修复`.
- Verified next executable gate is no-live S1 implementation only.

No production tests were run because this gate is controller judgment only.

## Completion

Controller judgment accepts the fixed RR-09 product provenance tier contract plan and routes the next gate to:

`RR-09 Product Provenance Tier Contract No-live Implementation Gate - Slice S1`

Release/readiness remains `NOT_READY`.

Completion token:

`ACCEPT_RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`
