# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Planning Gate`
Role: controller judgment only
Verdict: `ACCEPT_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`
Release/readiness: `NOT_READY`

## Accepted Artifacts

- Plan: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
- DS plan review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-review-ds-20260617.md`
- Plan fix evidence: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix-evidence-20260617.md`
- DS re-review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-rereview-ds-20260617.md`
- MiMo plan review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-review-mimo-20260617.md`
- Plan fix2 evidence: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix2-evidence-20260617.md`
- MiMo re-review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-rereview-mimo-20260617.md`

## Controller Decision

The plan is accepted for the next local no-live implementation gate.

Accepted implementation scope is limited to:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md`

The accepted implementation target is the raw legacy v1 helper path in `_enrich_reference_bundle_contexts()`. The implementation may add deterministic candidate helper enrichment for:

- table-local row hierarchy derivation for explicit §8 portfolio asset composition rows;
- benchmark semantic context derivation for raw legacy text spans.

The implementation must not use evidence-wrapper v2 prefill as the solution, must not overwrite already enriched v2 bundles, and must not expand production parser, source retrieval, Service/UI/Host/renderer/quality-gate paths.

## Finding Disposition

DS initial review findings:

- F-DS-P1 `_row_primary_label` undefined: fixed. The plan now defines last non-empty stripped `row_label_path` element as the only positive row label identity.
- F-DS-P2 context label priority undefined: fixed. Priority is `context_label > heading_path > raw_text`, with explicit fail-closed conflict handling.
- F-DS-P3 raw prefix delimiter ambiguity: fixed. The plan specifies delimiter-aware prefix parsing.
- F-DS-P4 missing heading-path benchmark positive test: fixed.
- F-DS-P5 nonexistent `_enrich_share_period_contexts()` example: fixed; optional local refactor only.
- F-DS-P6 row-index gaps ambiguity: fixed; integer gaps remain comparable, while missing/non-integer/duplicated identity fails closed.

DS re-review verdict: `PASS`; blocking findings: 0.

MiMo initial review findings:

- F1 `其中：普通股` positive stock-closure mismatch: fixed. The accepted plan no longer treats `其中：普通股` as positive proof for `stock_investment_amount` in this gate and explicitly prohibits `FIELD_RULES` expansion.
- F2 top-level asset row boundary list: accepted as non-blocking conservative residual.
- F3 `_enrich_share_period_contexts()` ambiguity: clarified as non-blocking; default is preserving existing inline behavior.
- F4 S5-F032 depends on actual table structure: accepted as non-blocking implementation/evidence residual.

MiMo re-review verdict: `PASS`; blocking findings: 0.

## Accepted Residuals

- DS F-DS-R1: `heading_path` internal benchmark/investment-objective conflict is not explicitly covered by a dedicated test. Current accepted behavior is fail-closed to `unknown`; this is non-blocking for implementation.
- The next implementation may reduce candidate residuals, but it must not claim source truth acceptance. Any later closure count still requires a separate no-live re-evidence gate.
- All rows remain `source_truth_status=not_proven` until a separate source-truth gate is accepted.

## Boundary Guardrails

This accepted plan does not authorize:

- Docling baseline promotion;
- parser replacement;
- production source truth acceptance;
- full field correctness proof;
- release readiness, PR readiness, or golden-set readiness;
- live/network/provider/LLM commands;
- direct PDF/cache/source-helper access;
- `FIELD_RULES` expansion for `普通股`.

The next gate must preserve:

- `NOT_READY`;
- `candidate_only=true`;
- `source_truth_status=not_proven`;
- candidate-helper-only scope.

## Next Gate

Next gate:

`Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Implementation Gate`

Implementation worker stop condition:

- write only the accepted implementation files listed above;
- run `uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py`;
- write the implementation evidence artifact;
- stop for code review.

## Self-check

Current gate is planning acceptance. Controller has read the updated plan, DS/MiMo reviews, both fix evidence artifacts, and both re-review artifacts. Both independent re-reviews are `PASS` with zero blocking findings. Scope is candidate helper only, and unrelated untracked workspace artifacts are excluded from this checkpoint.
