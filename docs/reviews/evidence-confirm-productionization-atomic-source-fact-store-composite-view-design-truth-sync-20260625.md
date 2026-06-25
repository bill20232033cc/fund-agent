# Atomic Source Fact Store / Composite Analysis View Split Design Truth Sync

## Gate

- Work unit: `Atomic Source Fact Store / Composite Analysis View Split`
- Gate: Design Truth Sync Gate
- Classification: `heavy`
- Verdict: `ATOMIC_SOURCE_FACT_STORE_COMPOSITE_VIEW_SPLIT_DESIGN_TRUTH_SYNC_ACCEPTED_NOT_READY`
- Artifact: `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-design-truth-sync-20260625.md`

## Scope

This gate accepts the architecture direction from `docs/reviews/repo-review-20260625-120726.md` and synchronizes design/control truth only.

Changed files:

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-design-truth-sync-20260625.md`

No production code, tests, README, live/PDF command, provider/LLM command, product CLI command, remote GitHub state, tag, release, or readiness claim is authorized or performed by this gate.

## Current Code Facts

The current implemented extraction path still uses composite public extraction values:

- `StructuredFundDataBundle.fee_schedule`
- `StructuredFundDataBundle.nav_benchmark_performance`
- `StructuredFundDataBundle.manager_alignment`
- `StructuredFundDataBundle.manager_strategy_text`

The default parsed annual processor currently adds only top-level `source_field_path=<field>` locators for these fields. It does not emit direct subfield provenance such as `source_field_path=fee_schedule.management_fee` on the default production path.

The explicit `FundDisclosureDocument` source-truth route has child output path information for some fields, but still reassembles selected values into composite `FundFieldFamilyResult.value` and then projects those values into `StructuredFundDataBundle`.

Chapter facts and Evidence Confirm currently consume `StructuredFundDataBundle` top-level fields. As a result, composite dict values are flattened for audit tokens, and strict row/value precision cannot naturally audit one independent source value without additional narrowing logic.

## Accepted Design Direction

The extraction truth should move to atomic source facts:

- each source-disclosed scalar/text fact has its own stable fact id;
- each atomic fact owns its value, extraction status, extraction mode, anchors, provenance, and gaps;
- examples include `fee_schedule.management_fee`, `fee_schedule.custody_fee`, `nav_benchmark_performance.nav_growth_rate`, `nav_benchmark_performance.benchmark_return_rate`, `manager_strategy_text.strategy_summary`, `manager_strategy_text.market_outlook`, `manager_alignment.manager_holding`, and `manager_alignment.employee_holding`.

Composite fields are accepted only as derived analysis views:

- `fee_schedule`
- `nav_benchmark_performance`
- `manager_strategy_text`
- `manager_alignment`

These views may be used by templates, deterministic renderers, LLM prompts, and compatibility adapters, but they are not the source-of-truth extraction objects after the future implementation gate.

Evidence Confirm should default to auditing atomic source facts. Derived composite views should carry dependency fact ids and inherit provenance from their child facts, rather than being audited as opaque dict values.

## Non-goals

- Do not remove `StructuredFundDataBundle` in this gate.
- Do not change `FundDataExtractor.extract()` runtime behavior.
- Do not change `FundFieldFamilyResult` schema in this gate.
- Do not change Evidence Confirm V2, ECQ, quality-gate, report-body, checklist, renderer, provider/LLM, or CLI behavior.
- Do not consume parser JSON, Docling JSON, PDF cache, source helper, or external document sources outside the Fund documents / Processor boundary.
- Do not claim release readiness.

## Next Plan Gate

Next entry point:

`Atomic Source Fact Store / Composite Analysis View Split Implementation Plan Gate`

The implementation plan must be code-generation-ready and include:

1. atomic fact contract and stable fact id naming;
2. migration boundary for `StructuredFundDataBundle` as compatibility / analysis view;
3. parsed annual processor adoption path;
4. FDD source-truth route adoption path;
5. `ChapterFactProvider` projection changes;
6. Evidence Confirm atomic-fact audit behavior;
7. tests that distinguish extraction truth from derived composite views;
8. residual routing for live/PDF strict precision evidence and release/readiness.

## Validation

Static validation only:

- design/control docs are updated with explicit current-state vs accepted-future-state labels;
- release/readiness remains `NOT_READY`;
- live/PDF, product CLI, provider/LLM, remote, tag, and release actions remain out of scope.

## Residual Risks

- The implementation migration is high impact because current production code and tests still depend on composite `StructuredFundDataBundle` fields.
- Atomic fact id naming remains an implementation-plan decision.
- Whether to keep `StructuredFundDataBundle` long term or replace it with a new analysis-view contract remains an implementation-plan decision.
- Real-report child-level provenance must be re-evidenced after implementation; current FDD fixture-level child paths are not sufficient release proof.
