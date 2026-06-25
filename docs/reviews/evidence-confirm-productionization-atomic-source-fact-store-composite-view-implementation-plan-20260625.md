# Atomic Source Fact Store / Composite Analysis View Split Implementation Plan

## Gate

- Work unit: `Atomic Source Fact Store / Composite Analysis View Split`
- Gate: Implementation Plan Gate
- Role: planning worker only
- Classification: `heavy`
- Artifact: `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md`
- Verdict: `ATOMIC_SOURCE_FACT_STORE_COMPOSITE_VIEW_SPLIT_IMPLEMENTATION_PLAN_READY_FOR_REVIEW_NOT_READY`

## Scope Boundary

This plan is based only on the accepted repo review and design-sync/control artifacts listed in the task. It does not introduce new direct code inspection facts.

Goal: migrate extraction truth from opaque composite dict fields to atomic source facts, while preserving `StructuredFundDataBundle` as the migration compatibility view.

Motivation: source facts such as `fee_schedule.management_fee`, `nav_benchmark_performance.nav_growth_rate`, `manager_strategy_text.strategy_summary`, and `manager_alignment.manager_holding` are independently disclosed and independently auditable. Combining sibling values into one top-level dict makes provenance, gaps, Evidence Confirm, and chapter facts reason about composites instead of the disclosed facts.

Success signal:

- default parsed annual processor path emits canonical atomic fact ids for directly proven child facts;
- explicit `FundDisclosureDocument` source-truth route preserves selected child output paths as atomic source facts before assembling compatibility views;
- `StructuredFundDataBundle` remains usable by existing consumers, but is documented and tested as a derived compatibility view, not extraction truth;
- `ChapterFactProvider` can project chapter facts from atomic facts or explicit derived views with dependency fact ids;
- Evidence Confirm V2 material/value matching defaults to atomic facts and only accepts derived view provenance through child fact dependencies;
- default parsed annual child facts are emitted only after the legacy extractor/result model exposes child-level `ExtractedField` or atomic fact records; processor wrappers must not infer child facts from composite dict keys;
- no live/PDF, product CLI, provider/LLM, release/readiness, PR state, tag, merge, or readiness claim is performed by this implementation work unit.

## Current Accepted Facts

The following are accepted current code facts from `docs/reviews/repo-review-20260625-120726.md` and `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-design-truth-sync-20260625.md`:

- Current `StructuredFundDataBundle` exposes `fee_schedule`, `nav_benchmark_performance`, `manager_alignment`, and `manager_strategy_text` as composite dict fields.
- Default parsed annual processing currently scopes anchors to top-level `source_field_path=<field>` for those composites; it does not emit direct child provenance such as `source_field_path=fee_schedule.management_fee` on the default production path.
- Explicit `FundDisclosureDocument` source-truth route already selects some atomic child output paths, then rebuilds them into composite `FundFieldFamilyResult.value` and projects those composites into `StructuredFundDataBundle`.
- `ChapterFactProvider` currently projects from `StructuredFundDataBundle`, maps source ids at top-level composite granularity, and records facts with values that may be entire dicts.
- Evidence Confirm currently flattens composite dict values for material tokens and value diagnostics; that makes one sibling fact inherit the audit burden of unrelated sibling values.
- Existing tests currently encode composite dict values and top-level-only `source_field_path` as expected behavior; those assertions must be split into extraction-truth tests and compatibility-view tests.
- Release/readiness remains `NOT_READY`; strict V2 live/PDF re-evidence and B1 `017641 / 2024` manager strategy residuals remain separate follow-up gates.

## Target Contract

### Canonical atomic fact id

Use the existing processor output path shape as the canonical stable fact id:

- `fee_schedule.management_fee`
- `fee_schedule.custody_fee`
- `nav_benchmark_performance.nav_growth_rate`
- `nav_benchmark_performance.benchmark_return_rate`
- `manager_strategy_text.strategy_summary`
- `manager_strategy_text.market_outlook`
- `manager_alignment.manager_holding`
- `manager_alignment.employee_holding`

Do not prefix canonical ids with `structured.`. If chapter facts need a display/source namespace, derive it as `structured.<fact_id>` at projection time only.

### New Fund-owned types

Add a Fund-layer module `fund_agent/fund/source_facts.py` with:

- `AtomicSourceFact`
  - `fact_id: str`
  - `family_id: str`
  - `value: object | None`
  - `status: str`
  - `extraction_mode: str`
  - `anchors: tuple[EvidenceAnchor, ...]`
  - `provenance: object | None`
  - `gaps: tuple[str, ...]`
  - `source_field_path: str`
  - `dependency_metadata: FactDependencyMetadata`
- `FactDependencyMetadata`
  - `dependency_fact_ids: tuple[str, ...]`
  - `dependency_policy: str`
  - `derived_from_view_id: str | None`
  - `notes: tuple[str, ...]`
- `AtomicSourceFactStore`
  - immutable mapping by `fact_id`
  - `get_required(fact_id)`
  - `get_optional(fact_id)`
  - `by_family(family_id)`
  - `merge_strict(other)` with duplicate-id equality guard
- `CompositeAnalysisView`
  - `view_id: str`
  - `value: object | None`
  - `status: str`
  - `anchors: tuple[EvidenceAnchor, ...]`
  - `gaps: tuple[str, ...]`
  - `dependency_fact_ids: tuple[str, ...]`

### Canonical output surface and data flow

Atomic source facts have exactly one primary production surface:

- `FundProcessorResult.source_facts: AtomicSourceFactStore = empty_atomic_source_fact_store()`

Compatibility mirrors are allowed only in these two places:

- `StructuredFundDataBundle.source_facts` carries the same store returned by `FundProcessorResult.source_facts` for facade consumers;
- `ChapterFactProjection.source_facts` carries the same store for writing/audit projection, together with a derived view registry.

Do not add atomic fact payloads to `FundFieldFamilyResult`. `FundFieldFamilyResult.value` remains the legacy field-family compatibility value. If a field-family result needs to identify its derived inputs, use `CompositeAnalysisView.dependency_fact_ids` and `ChapterFactEntry.source_fact_ids`, not a second source-fact store inside `FundFieldFamilyResult`.

The migration data flow is fixed:

1. Processor or extractor emits atomic source facts into `FundProcessorResult.source_facts`.
2. Derived view assembler builds `CompositeAnalysisView` objects and the existing `FundFieldFamilyResult.value` / `StructuredFundDataBundle` `ExtractedField` values from that store.
3. `FundDataExtractor` copies the processor store to `StructuredFundDataBundle.source_facts` without rewriting ids or anchors.
4. `ChapterFactProvider` projects `ChapterFactEntry` records from either one `source_fact_id` or one `derived_view_id`.
5. Evidence Confirm consumes the `ChapterFactEntry` ids and resolves values/provenance through `ChapterFactProjection.source_facts` and derived views. It must not rediscover atomic ids by flattening dict values.

### Chapter and audit bridge contract

Additive chapter projection fields:

- `ChapterFactEntry.source_fact_ids: tuple[str, ...] = ()`
- `ChapterFactEntry.derived_view_id: str | None = None`
- `ChapterFactProjection.source_facts: AtomicSourceFactStore = empty_atomic_source_fact_store()`
- `ChapterFactProjection.derived_views: tuple[CompositeAnalysisView, ...] = ()`

Bridge invariants:

- Atomic chapter facts have exactly one `source_fact_id` and no `derived_view_id`.
- Derived chapter facts have one `derived_view_id` and list their child `source_fact_ids` through the matching `CompositeAnalysisView.dependency_fact_ids`.
- Legacy facts for non-migrated fields keep both fields empty and follow existing value/materialization behavior.
- Evidence Confirm must use these ids as the only migrated-family bridge. It must not rebuild atomic mappings from `field_path`, `source_field_id`, row locator text, or dict keys.

Contract invariants:

- `fact_id == source_field_path` for source facts.
- Atomic facts have no sibling dependencies; their `dependency_fact_ids` is empty.
- Derived composite views must list child `dependency_fact_ids`.
- A derived view may be `accepted` only if all required child facts for that view satisfy its assembly policy; otherwise it is `partial` or `missing`.
- Anchors on atomic facts must be copied only from directly proven source anchors. Do not infer child anchors from composite dict shape.
- Missing child provenance must produce a gap/status, not a fabricated child `source_field_path`.

## Public Contract Impact

This is an additive migration, not removal:

- Keep `StructuredFundDataBundle` public fields and current field names during this work unit.
- Add `FundProcessorResult.source_facts` as the primary source-fact output surface.
- Add `StructuredFundDataBundle.source_facts` as a trailing defaulted field that carries the processor store for facade consumers without requiring positional construction changes.
- Add `ChapterFactEntry.source_fact_ids`, `ChapterFactEntry.derived_view_id`, `ChapterFactProjection.source_facts`, and `ChapterFactProjection.derived_views` as trailing defaulted compatibility fields.
- Keep existing composite fields as `CompositeAnalysisView`-assembled compatibility values.
- Keep `FundFieldFamilyResult.value` available for existing family result consumers, but no longer treat it as extraction truth for the migrated families.
- Do not add a second source-fact store to `FundFieldFamilyResult`.
- Do not change CLI output, renderer output, report body, checklist Evidence Confirm default, provider default, release policy, or quality-gate policy in this work unit.

## Implementation Slices

### S1 - Atomic contract and compatibility view primitives

Allowed modules:

- `fund_agent/fund/source_facts.py`
- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/data_extractor.py`
- focused tests under `tests/fund/`

Changes:

- Introduce the atomic source fact dataclasses and store.
- Add `FundProcessorResult.source_facts` as the only Processor output truth surface for atomic facts.
- Add `StructuredFundDataBundle.source_facts` as a compatibility mirror copied from `FundProcessorResult.source_facts`.
- Do not add atomic payloads to `FundFieldFamilyResult`; keep it as legacy field-family compatibility.
- Add a pure assembler helper that builds `CompositeAnalysisView` and legacy `ExtractedField[dict]` values from atomic facts for the four migrated families.
- Add duplicate fact id and missing dependency fail-closed behavior.

Tests:

- atomic fact id, status, source_field_path, anchors, provenance, gaps, extraction_mode, dependency metadata contract tests;
- processor result exposes source facts only through `FundProcessorResult.source_facts`;
- compatibility construction test proving existing composite fields remain available;
- frozen/slots constructor compatibility test proving existing positional/keyword construction remains valid after defaulted trailing fields;
- duplicate fact id rejection test;
- missing dependency produces partial/missing view, not fabricated data.

Stop condition:

- Stop if adding the store requires removing or renaming existing public bundle fields, or if implementation needs to place a second atomic store inside `FundFieldFamilyResult`.

### S2A - Default parsed annual extractor child fact split

Allowed modules:

- `fund_agent/fund/extractors/profile.py`
- `fund_agent/fund/extractors/performance.py`
- `fund_agent/fund/extractors/manager_ownership.py`
- extractor result models in the same package if those modules currently own their result dataclasses
- focused extractor tests under `tests/fund/`

Changes:

- Split legacy extractor outputs for the migrated composites into child-level facts before Processor assembly.
- For fee data, expose independently proven `fee_schedule.management_fee` and `fee_schedule.custody_fee`.
- For return attribution, expose independently proven `nav_benchmark_performance.nav_growth_rate` and `nav_benchmark_performance.benchmark_return_rate`.
- For manager text, expose independently proven `manager_strategy_text.strategy_summary` and `manager_strategy_text.market_outlook`.
- For manager alignment, expose independently proven `manager_alignment.manager_holding` and `manager_alignment.employee_holding`.
- Preserve existing composite extractor result values only as derived compatibility output.
- Do not create a child atomic fact from a dict key unless the extractor can attach the child value to its own matched source anchor or explicit missing gap.

Tests:

- each child-level output has its own value, extraction mode, anchors, status/gap, and canonical path when directly matched;
- missing child values produce explicit missing/partial state and no fabricated anchor;
- old composite extractor outputs remain available as compatibility values assembled from children.

Stop condition:

- Stop if a child path can only be inferred from the old composite dict and cannot be tied to child-level extractor match evidence.

### S2B - Default parsed annual processor atomic emission

Allowed modules:

- `fund_agent/fund/processors/active_annual.py`
- shared parsed annual processor helpers if the repository already centralizes them
- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- focused processor tests under `tests/fund/processors/`

Changes:

- Consume S2A child-level extractor outputs and emit them into `FundProcessorResult.source_facts`.
- Preserve child paths already known by parsed annual extractor outputs as atomic fact ids.
- Emit atomic facts for direct child facts in `fee_schedule`, `nav_benchmark_performance`, `manager_strategy_text`, and `manager_alignment` only when S2A supplied child-level evidence.
- Assemble the existing top-level `StructuredFundDataBundle` composite fields from emitted atomic facts.
- Replace top-level-only source-field-path expectations with no-fabrication expectations:
  - child path is present only when the extractor directly identified that child;
  - child path is absent and gap/status is explicit when not directly proven.

Tests:

- default parsed annual path emits `fee_schedule.management_fee` and sibling ids when directly matched;
- anchor `source_field_path` matches canonical fact id for directly matched child facts;
- compatibility bundle still returns the old top-level dict value;
- no child anchor is created from dict shape alone.

Stop condition:

- Stop if a child path would be inferred from the old composite dict rather than from S2A child extractor output or accepted source route metadata.

### S3 - Explicit FundDisclosureDocument source-truth route atomic preservation

Allowed modules:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- processor contract helpers introduced in S1
- `fund_agent/fund/data_extractor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`

Changes:

- In source-truth direct extraction, preserve selected output paths as `AtomicSourceFact` records before family value assembly.
- Keep candidate-only evidence out of atomic source facts unless proof-positive source-truth admission is present.
- Build `return_attribution.v1` and `manager_profile.v1` compatibility composite values from atomic facts rather than rebuilding from parallel selector state.
- Ensure direct route `candidate_evidence=()` semantics remain unchanged for proof-positive source-truth output.

Tests:

- FDD source-truth route emits the same canonical ids as default parsed annual where the same child fact exists;
- proof-positive child path becomes atomic fact with direct anchors/provenance;
- candidate-only/not_proven child evidence does not become an atomic source fact;
- existing `StructuredFundDataBundle` projections remain compatible for migrated fields.

Stop condition:

- Stop if the implementation requires default-on FDD parsing, parser JSON consumption outside Fund boundaries, or treating fixture-only child anchors as live/source readiness proof.

### S4 - ChapterFactProvider projection from atomic facts and derived views

Allowed modules:

- `fund_agent/fund/chapter_facts.py`
- `fund_agent/fund/source_facts.py`
- focused chapter fact tests under `tests/fund/`

Changes:

- Add projection support from `StructuredFundDataBundle.source_facts`.
- Add trailing defaulted bridge fields to `ChapterFactEntry` and `ChapterFactProjection` exactly as defined in the target contract.
- For migrated families, chapter facts should reference one atomic fact id when the chapter needs one fact, or an explicit `CompositeAnalysisView.view_id` with `dependency_fact_ids` when the chapter needs a derived bundle.
- Preserve legacy projection for non-migrated fields.
- Record `field_path` as `AtomicSourceFact.<fact_id>` for atomic facts and `CompositeAnalysisView.<view_id>` for derived views.
- Carry `ChapterFactProjection.source_facts` and `ChapterFactProjection.derived_views` forward so Evidence Confirm can resolve the same ids that the writer sees.

Tests:

- cost chapter can project `fee_schedule.management_fee` without inheriting `custody_fee`;
- return attribution can project NAV and benchmark as separate facts;
- manager profile can project `strategy_summary` and `market_outlook` separately;
- derived view facts carry dependency ids and do not hide missing child gaps.
- legacy projection with an empty `source_facts` store still preserves existing non-migrated field behavior.

Stop condition:

- Stop if chapter projection would silently flatten a composite dict for migrated families.

### S5 - Evidence Confirm atomic audit behavior

Allowed modules:

- `fund_agent/fund/evidence_confirm.py`
- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/evidence_confirm_value_diagnostics.py`
- `fund_agent/fund/source_facts.py`
- focused Evidence Confirm tests under `tests/fund/`

Changes:

- Make migrated-family audit materialization resolve values and anchors through `ChapterFactEntry.source_fact_ids`, `ChapterFactEntry.derived_view_id`, `ChapterFactProjection.source_facts`, and `ChapterFactProjection.derived_views`.
- For derived composite views, validate provenance through dependency facts:
  - all required child facts must have section-or-better provenance for derived view provenance pass;
  - strict row/value precision residuals remain visible and policy-governed;
  - missing child provenance is not converted to `not_run`.
- For legacy facts with no bridge ids, keep existing `fact.value` / row-locator materialization behavior.
- Keep V2/ECQ/quality-gate policy semantics unchanged except for the source material unit becoming atomic where available.
- Do not let Evidence Confirm rediscover atomic mappings from dict keys, `field_path`, top-level `source_field_id`, or free-form row locator parsing.

Tests:

- value diagnostics for `fee_schedule.management_fee` use only the management fee value;
- derived `fee_schedule` view provenance fails or degrades when one required child lacks provenance;
- no-fabrication test for `source_field_path` with missing child anchor;
- Evidence Confirm uses the same fact id as `ChapterFactEntry.source_fact_ids` for migrated atomic facts;
- legacy no-bridge path still returns existing Evidence Confirm summary behavior;
- migration regression for existing Evidence Confirm summaries where no atomic facts are available.

Stop condition:

- Stop if Evidence Confirm behavior change would alter CLI/report/quality-gate policy semantics beyond the atomic materialization unit.

### S6 - Migration regression and docs-control decision

Allowed modules:

- tests touched by prior slices
- `fund_agent/fund/README.md` only if implementation changes Fund developer-facing current behavior
- `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md` only in a separate controller truth-sync gate, not inside the implementation slice unless explicitly authorized

Changes:

- Reclassify existing composite tests as compatibility-view tests.
- Add migration regression tests proving old consumers still receive `StructuredFundDataBundle` fields.
- Record uncovered live/PDF/release residuals in implementation evidence.

Tests:

- atomic contract suite;
- compatibility view suite;
- no-fabrication provenance suite;
- migration regression suite across default parsed annual and explicit FDD source-truth route.

Stop condition:

- Stop before README/design/control edits if the current gate authorization does not include docs sync.

## Validation Matrix For Future Implementation

No commands are run in this planning gate except static artifact checks. Future implementation should run focused no-live validation only, for example:

- `uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py -q`
- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_production.py tests/fund/test_evidence_confirm_semantic.py -q`
- `uv run pytest tests/fund/test_quality_gate_integration.py -q`
- focused chapter fact tests once test filenames are confirmed by implementation worker
- focused ruff for changed Python files
- `git diff --check`

Do not run live/PDF, product CLI, repository source-helper, parser download, provider/LLM, network, CI, push, PR mutation, tag, release, or readiness commands in this implementation work unit unless a later gate explicitly authorizes them.

## Residual Routing

- Strict V2 live/PDF re-evidence: required after no-live atomic migration if release scope still depends on row/value precision. Route to a separate exact live/PDF authorization gate; do not run in implementation.
- Release/readiness: remains `NOT_READY` until separate release-boundary evidence accepts source/PDF, semantic, Service/UI/renderer/quality-gate integration, external PR state, and residual disposition.
- B1 `017641 / 2024` `manager_strategy_text`: route to a post-implementation runtime product CLI re-evidence or narrower source-fact correctness gate. Atomic migration may improve traceability, but does not itself prove the QDII sample or remove the residual.
- Checklist Evidence Confirm, report-body rendering, provider-backed semantic default, FDD default-on parsing, tag, release, mark-ready, merge, and reviewer requests remain separate gates.

## Non-goals

- Do not remove `StructuredFundDataBundle`.
- Do not rename existing public bundle fields.
- Do not make FDD default-on.
- Do not consume Docling, pdfplumber JSON, EID HTML render, PDF cache, source helper, or parser artifacts outside Fund documents / Processor / Extractor boundaries.
- Do not change UI, Service orchestration, Host runtime, renderer output, checklist Evidence Confirm default, provider default, quality-gate policy, CLI output, PR state, tag, release, or readiness.
- Do not treat fixture-level FDD child anchors as live/PDF source-truth proof.
- Do not claim strict V2, B1 `017641 / 2024`, or release/readiness pass.

## Reviewer Checklist

- Does every migrated source value have a stable canonical fact id equal to its source field path?
- Is `FundProcessorResult.source_facts` the only Processor output truth surface for atomic facts?
- Does `StructuredFundDataBundle.source_facts` only mirror the processor store rather than creating a second store?
- Does the plan avoid adding atomic payloads to `FundFieldFamilyResult`?
- Are atomic facts emitted only from directly proven matcher/source-truth paths?
- Does default parsed annual migration split legacy extractor outputs before processor assembly, rather than deriving child facts from composite dict keys?
- Are composite values assembled as derived compatibility views with dependency fact ids?
- Does `StructuredFundDataBundle` compatibility remain intact for existing consumers?
- Does default parsed annual processing preserve child provenance where directly known?
- Does explicit FDD source-truth output preserve child output paths before family assembly?
- Do `ChapterFactEntry` and `ChapterFactProjection` expose the bridge ids/store needed by Evidence Confirm?
- Does `ChapterFactProvider` avoid flattening migrated composite dicts as audit facts?
- Does Evidence Confirm audit atomic fact values by default and evaluate derived provenance through dependencies?
- Does Evidence Confirm consume `ChapterFactEntry.source_fact_ids` / `derived_view_id` instead of rediscovering atomic mappings from dicts or locators?
- Do tests separate atomic extraction truth from compatibility view behavior?
- Are no-fabrication provenance cases covered?
- Are live/PDF, product CLI, provider/LLM, release/readiness, and PR external actions absent from implementation validation?

## Acceptance Criteria

- Plan review finds no blocking ambiguity in fact id naming, module ownership, slice order, public contract impact, or test scope.
- Plan review confirms F1/F2/F3 from `docs/reviews/plan-review-20260625-125326.md` are fixed or no longer blocking.
- Future implementation can proceed slice-by-slice without inventing a new contract.
- Current production behavior is not claimed changed by this planning gate.
- Release/readiness remains `NOT_READY`.

## Completion Report Format

Future implementation evidence must report:

- changed files by slice;
- atomic ids implemented;
- compatibility behavior preserved;
- focused tests and results;
- skipped validations with reasons;
- residual routing for strict V2 live/PDF, release/readiness, and B1 `017641 / 2024`;
- final token ending in `NOT_READY`.

ATOMIC_SOURCE_FACT_STORE_COMPOSITE_VIEW_SPLIT_IMPLEMENTATION_PLAN_READY_FOR_REVIEW_NOT_READY
