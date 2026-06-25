# Atomic Source Fact Store / Composite Analysis View Split Plan Fix

## Gate

- Work unit: `Atomic Source Fact Store / Composite Analysis View Split`
- Gate: Implementation Plan Fix Gate
- Reviewed plan: `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md`
- Review artifact: `docs/reviews/plan-review-20260625-125326.md`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-plan-fix-20260625-125650.md`
- Verdict: `ATOMIC_SOURCE_FACT_STORE_COMPOSITE_VIEW_SPLIT_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`

## Scope

This gate fixes the implementation plan only. It does not implement production code, tests, README, design/control/startup packet updates, live/PDF evidence, product CLI evidence, provider/LLM execution, remote state changes, tag, release, or readiness.

Changed files:

- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-plan-fix-20260625-125650.md`

## Fixes

### F1 - atomic facts 承载位置不明确

Status: `已修复`

Plan changes:

- Added a canonical output surface section.
- Set `FundProcessorResult.source_facts` as the only Processor output truth surface.
- Set `StructuredFundDataBundle.source_facts` as a facade mirror of the processor store.
- Set `ChapterFactProjection.source_facts` as the writing/audit projection mirror.
- Explicitly prohibited adding atomic fact payloads to `FundFieldFamilyResult`.
- Updated public contract impact, S1 tests, S1 stop conditions and reviewer checklist.

### F2 - default parsed annual 可能从 composite dict 反推子字段

Status: `已修复`

Plan changes:

- Split the old S2 into `S2A - Default parsed annual extractor child fact split` and `S2B - Default parsed annual processor atomic emission`.
- Added legacy extractor modules to S2A scope: `profile.py`, `performance.py`, `manager_ownership.py`, and their result models if owned in the same package.
- Required child-level extractor output before Processor assembly.
- Required no-fabrication tests proving child facts are tied to child-level extractor match evidence, not dict keys.
- Updated S2B so processor emission consumes S2A child-level outputs and stops if it would infer child paths from old composite dicts.

### F3 - ChapterFactProvider / Evidence Confirm bridge contract missing

Status: `已修复`

Plan changes:

- Added chapter/audit bridge contract fields:
  - `ChapterFactEntry.source_fact_ids`
  - `ChapterFactEntry.derived_view_id`
  - `ChapterFactProjection.source_facts`
  - `ChapterFactProjection.derived_views`
- Required Evidence Confirm to resolve migrated-family values and anchors through the bridge ids and projection store.
- Prohibited Evidence Confirm from rediscovering atomic mappings from dict keys, `field_path`, top-level `source_field_id`, row locator text, or free-form locators.
- Updated S4/S5 tests and reviewer checklist.

## Validation

Static checks only:

- `rg` was used to verify the fixed plan now contains the canonical source-fact surfaces, S2A/S2B split, and chapter/audit bridge terms.
- `git diff --check` is required before re-review.

No production tests, live/PDF, product CLI, provider/LLM, network, push, PR mutation, tag, release, or readiness command was run.

## Residual Risks

- The plan still intentionally routes actual code changes to later implementation slices.
- `fund_disclosure_processor.py` size and responsibility concentration remain later refactor risk, not a blocker for this plan fix.
- Strict V2 live/PDF evidence, B1 `017641 / 2024`, and release/readiness remain later exact authorization gates.

## Completion

Ready for plan re-review.

ATOMIC_SOURCE_FACT_STORE_COMPOSITE_VIEW_SPLIT_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY
