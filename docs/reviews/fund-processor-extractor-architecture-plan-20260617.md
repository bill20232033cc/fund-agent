# Fund Processor/Extractor Architecture Planning Gate

> Date: 2026-06-17
> Role: planning worker only
> Work unit: Fund Processor/Extractor Architecture Planning Gate
> Classification: heavy architecture planning, docs/planning only
> Artifact status: handoff-ready, code-generation-ready, not implementation

## Verdict

PLAN_READY_FOR_REVIEW_NOT_READY

本计划可进入 review gate；不得据此直接实现、切换生产 parser、声明 source truth、声明 full field correctness、推进 readiness/release/PR，或执行 live/source/PDF/FDR/Docling/provider/LLM/analyze/checklist/golden/readiness/release 命令。

## Scope And Non-goals

Scope:

- 规划 Fund 层 `FundProcessorRegistry` / `FundProcessorProtocol` / concrete Extractor 架构。
- 规划 dispatch key、registry priority、allowed input intermediate kinds、字段族输出契约、EvidenceAnchor/provenance/fail-closed gap semantics。
- 规划与当前 `FundDataExtractor`、`ParsedAnnualReport`、现有窄 extractor、Docling/pdfplumber/EID HTML candidate internals 的迁移关系。
- 规划首个 no-live implementation slice、exact allowed files/modules、测试矩阵、README/docs sync、禁止命令。

Non-goals:

- 不实现代码，不修改 control docs，不提交 commit。
- 不替换生产 parser，不改变 EID single-source policy、fallback、source acquisition、provider/runtime/config、repair budget、quality gate、golden/readiness/release/PR 状态。
- 不允许 Service/UI/Host/renderer/quality gate/LLM prompt/模板直接消费 Docling、pdfplumber full JSON、EID HTML render、PDF cache 或 parser helper。
- 不声明 Docling/EID HTML/pdfplumber source truth、full field correctness、taxonomy compatibility、baseline/golden promotion 或 release readiness。
- 不执行 live/network/PDF/FDR/Docling conversion/provider/LLM/analyze/checklist/golden/readiness/release 命令。

## Direct Truth And Code Evidence

Execution and truth hierarchy:

- `AGENTS.md:7-9` states `AGENTS.md` is the repository's authoritative execution entry; `AGENTS.md:29-32` orders required truth reads.
- `AGENTS.md:38-42` requires `docs/design.md` to distinguish current implementation, accepted future design, and candidate/research input.
- `AGENTS.md:54-57` classifies architecture/public contract/source policy/readiness-impacting work as heavy.
- `AGENTS.md:75-79` requires production annual-report PDF access through `FundDocumentRepository` and structured fund field extraction through a Fund-layer Processor/Extractor boundary.
- `AGENTS.md:83` makes Dayu a reference and capability source, not production runtime dependency.
- `AGENTS.md:91-141` fixes the target boundary as `UI -> Service -> Host -> Agent`; Fund domain extraction/audit/template logic belongs to Agent-layer `fund_agent/fund`.
- `AGENTS.md:224-232` requires fund-type identification, `preferred_lens`, 8-chapter template analysis, audit, and traceable evidence anchors.

Current gate and NOT_READY boundary:

- `docs/current-startup-packet.md:22-27` sets current phase/gate, scope, candidate-only Docling evidence, and says no implementation plan artifact has been accepted yet.
- `docs/implementation-control.md:24-43` records current truth guardrails: current mainline no longer continues Docling full-representation retry; Processor/Extractor remains future direction; parser outputs cannot be consumed outside Fund documents/Future Processor boundary.
- `docs/implementation-control.md:49-52` defines the active gate and binding constraints, including no production parser replacement, no source policy change, no source-truth/readiness claim, and NOT_READY.
- `docs/current-startup-packet.md:63-66` names the next entry point and keeps production integration/parser replacement/live/source acquisition deferred.

Design truth:

- `docs/design.md:648-657` says document access is unified through `FundDocumentRepository`; current document models are `ParsedAnnualReport`, `ParsedTable`, `ReportSection`, `DocumentKey`.
- `docs/design.md:660-668` states current production parser path is `pdfplumber -> ParsedAnnualReport -> self-owned extractor -> EvidenceAnchor / CHAPTER_CONTRACT / audit / report`, while Docling/pdfplumber/EID HTML are internal intermediate or benchmark inputs, not fact truth.
- `docs/design.md:664-666` explicitly marks `docs/docling-architecture-reorientation-20260617.md` as architecture discussion/research input, not code fact, readiness conclusion, or archive authorization.
- `docs/design.md:672-676` accepts future `FundProcessorRegistry` / `FundProcessorProtocol` / concrete Extractor design, owned by `fund_agent/fund`, dispatched by `fund_type + report_type + media_type/intermediate_kind`, and not directly dependent on `dayu-agent`.
- `docs/design.md:680-690` keeps EID HTML render as candidate input only; HTML/Docling/raw text/PDF parser outputs must go through extractor/EvidenceAnchor/fail-closed projection before reaching CHAPTER_CONTRACT, audit, or reports.
- `docs/design.md:694-719` preserves current EID single-source source policy, current cache/provenance behavior, and fail-closed classes.
- `docs/design.md:746-760` documents current `FundDataExtractor` as the P1 data facade and current `ExtractionMode` values.
- `docs/design.md:1004-1051` shows current `fund_agent/fund` package ownership and existing `data_extractor.py`, `documents/`, `extractors/`, `audit/`, and `template/` layout.
- `docs/design.md:1147-1149` records the design decision: current problem should converge on Processor/Extractor field-family output, not parser full JSON correctness.

Template field need:

- `docs/fund-analysis-template-draft.md:6-22` defines `TEMPLATE_CONTRACT_MANIFEST_JSON` and public chapters 0-7.
- `docs/fund-analysis-template-draft.md:480-522` shows Chapter 2 required output items and fail-closed missing-evidence behavior for returns, benchmark, cost, and R=A+B-C closure.
- `docs/fund-analysis-template-draft.md:592-620` shows Chapter 3 manager-profile field needs, including manager information, strategy, behavior, consistency, style stability, and manager holding.
- `docs/fund-analysis-template-draft.md:791-935` and `docs/fund-analysis-template-draft.md:1082-1107` require investor experience, current stage, core risk, veto items, and next minimum verification question.

Current implementation:

- `fund_agent/fund/documents/repository.py:295-324` exposes `FundDocumentRepository.load_annual_report()` and returns `ParsedAnnualReport` without exposing local PDF paths.
- `fund_agent/fund/documents/repository.py:350-419` shows repository-owned PDF/cache/parser orchestration; callers should not own parser/cache details.
- `fund_agent/fund/documents/models.py:28-75` defines source metadata including selected source, source mode, fallback, and failure category; `fund_agent/fund/documents/models.py:292-420` defines reference metadata result for metadata-only checks.
- `fund_agent/fund/data_extractor.py:240-345` currently loads annual report through repository, loads NAV separately, calls narrow extractors directly, classifies fund type from `basic_identity`, and returns `StructuredFundDataBundle`.
- `fund_agent/fund/data_extractor.py:405-431` intentionally degrades only NAV provider failures to `nav_unavailable`; `fund_agent/fund/data_extractor.py:291-295` leaves repository/year-report failures unmasked.
- `fund_agent/fund/extractors/models.py:87-108` defines current `EvidenceAnchor`; `fund_agent/fund/extractors/models.py:496-545` defines `ExtractedField`, `ProfileExtractionResult`, and `PerformanceExtractionResult`; `fund_agent/fund/extractors/models.py:641-668` defines manager and holdings extraction result shapes.
- `fund_agent/fund/extractors/bond_risk_evidence.py:1-5` states the extractor consumes already-loaded `ParsedAnnualReport` and does not access repository, PDF cache, or source helper.
- `fund_agent/fund/documents/candidates/representation_models.py:1-6` makes candidate representation internal to Fund documents and non-exported to Service/UI/Host/renderer/quality gate.
- `fund_agent/fund/documents/candidates/representation_models.py:21-27` limits candidate source kinds to `docling_pdf_candidate`, `pdfplumber_pdf_candidate`, and `eid_xbrl_html_render_candidate`.
- `fund_agent/fund/documents/candidates/representation_models.py:72-112` forces candidate status, field correctness, source truth, taxonomy compatibility, and production parser replacement to remain non-proof/not-authorized.
- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py:1-7` maps candidate internals to EvidenceAnchor-like fields without importing production `EvidenceAnchor`, without repository/PDF/Docling calls, and fail-closes ambiguous section mapping.
- `tests/fund/test_data_extractor.py:31-75` uses a fake repository for no-live extraction tests; `tests/fund/test_data_extractor.py:201-260` verifies NAV failure is degraded while repository failure is not masked.
- `tests/fund/documents/test_docling_no_consumption_guards.py:8-22` guards Service/UI/Host/template/audit/extractors/quality paths from importing Docling/candidates/PDF adapter/cache.
- `tests/fund/documents/test_candidate_representation_models.py:16-33` verifies candidate source kinds are closed; `tests/fund/documents/test_candidate_representation_models.py:73-94` rejects proof/parser-replacement claims.

Truth-sync review inputs:

- `docs/reviews/fund-processor-extractor-truth-sync-review-ds-20260617.md:12-18` concludes PASS_NOT_READY with no material contradiction.
- `docs/reviews/fund-processor-extractor-truth-sync-review-ds-20260617.md:24-50` accepts wording/discoverability risk that discussion input might be misread as truth source; this is a residual to preserve in the plan.
- `docs/reviews/fund-processor-extractor-truth-sync-review-ds-20260617.md:110-118` confirms discussion statistics, archive suggestions, and unimplemented code sketches did not leak as current truth.
- `docs/reviews/fund-processor-extractor-truth-sync-review-mimo-20260617.md:24-28` concludes PASS_NOT_READY; `docs/reviews/fund-processor-extractor-truth-sync-review-mimo-20260617.md:34-54` says discussion statistics and implementation-roadmap suggestions are input, not accepted facts.

## First-principles Problem Statement

The real problem is not "which parser has the most complete full-document JSON." The report writer and audit path need stable, typed, chapter-relevant fund facts with provenance and explicit gaps. A full representation can be large and still unusable for CHAPTER_CONTRACT if it does not answer the next template action: what field family was extracted, from which report section/table/row, under which source identity, with what confidence/status, and what should happen when the field is missing or ambiguous.

Therefore:

- `FundDocumentRepository` owns source access, parser/cache orchestration, and internal intermediate construction.
- Docling/pdfplumber/EID HTML render remain internal/candidate inputs because they are document conversion or representation routes, not domain field extraction contracts.
- `FundProcessorRegistry` must be the Fund-owned domain routing boundary that selects the appropriate Processor/Extractor for `fund_type`, `report_type`, and `intermediate_kind`.
- Processor/Extractor output, not parser output, becomes the only candidate to feed chapter facts, EvidenceAnchor validation, fail-closed gaps, audit, and report generation.
- A processor result can be accepted for a narrow field family without implying parser replacement, full-document correctness, source truth, golden promotion, or readiness.

This is not extra abstraction for its own sake. Current code already has hidden routing in `FundDataExtractor.extract()` and multiple narrow extractors. The missing boundary is a typed, testable, registry-driven contract that prevents new parser routes from leaking upward and prevents each future extractor from inventing its own output/gap/provenance language.

## Proposed Architecture

### Layering

Target data flow:

```text
FundDocumentRepository
  -> controlled document intermediate
     - current: ParsedAnnualReport
     - future/candidate: FundDisclosureDocument, docling_json_candidate, pdfplumber_json_candidate, eid_html_render_candidate
  -> FundProcessorRegistry.resolve(dispatch_key)
  -> FundProcessorProtocol.extract(input)
  -> FundProcessorResult
  -> chapter fact projection / StructuredFundDataBundle adapter / audit / renderer
```

The registry and processors belong under Agent-layer `fund_agent/fund`. Service, UI, Host, renderer, quality gate, LLM prompt, and template code must only see processor outputs or existing Fund public facades, not parser/candidate internals.

### FundProcessorRegistry

Future module ownership:

- `fund_agent/fund/processors/registry.py`: registry implementation.
- `fund_agent/fund/processors/contracts.py`: protocol, dispatch key, input contract, output contract, status enums.
- `fund_agent/fund/processors/active_annual.py`: first concrete processor that wraps current narrow extractor functions for active annual reports.
- `fund_agent/fund/processors/__init__.py`: public exports only; no candidate internals exported.

Registry behavior:

- `register(processor_cls, priority)` validates unique processor id and integer priority.
- `resolve(context)` sorts registered processors by priority descending, then stable registration order.
- `supports(context)` is called with a typed `FundProcessorDispatchKey`.
- First supported processor wins.
- No fallback processor may silently turn `schema_drift`, `identity_mismatch`, `integrity_error`, unsupported intermediate, or ambiguous fund type into success.
- If no processor supports the context, return/raise a typed `unsupported_processor` fail-closed result instead of using a generic parser output.

### Processor Protocol

Minimum protocol:

```python
class FundProcessorProtocol(Protocol):
    processor_id: ClassVar[str]
    priority: ClassVar[int]
    output_schema_version: ClassVar[str]

    def supports(self, context: FundProcessorDispatchKey) -> bool: ...
    def extract(self, input: FundProcessorInput) -> FundProcessorResult: ...
```

Contract rules:

- `supports()` may inspect only dispatch metadata, not raw parser body content.
- `extract()` consumes one controlled intermediate and returns field families plus gaps.
- `extract()` must not call `FundDocumentRepository`, PDF cache, source helpers, Docling conversion, network, provider/LLM, Service/Host/UI, renderer, or quality gate.
- Processor classes must have Chinese module/class/function docstrings and cite template chapter numbers in fund-analysis code, matching `AGENTS.md:147-150`.
- Explicit parameters only; no `extra_payload`.

### Dispatch Keys

`FundProcessorDispatchKey` fields:

- `fund_type`: one of current `FundType` values: `index_fund`, `active_fund`, `bond_fund`, `enhanced_index`, `qdii_fund`, `fof_fund`.
- `report_type`: initially `annual_report`; future values require separate gate.
- `intermediate_kind`: closed set:
  - `parsed_annual_report.v1` for current `ParsedAnnualReport`.
  - `fund_disclosure_document.v1` for future accepted Fund documents object.
  - `docling_pdf_candidate.v1` for candidate harness only.
  - `pdfplumber_pdf_candidate.v1` for candidate harness only.
  - `eid_xbrl_html_render_candidate.v1` for candidate harness only.
- `source_kind`: public provenance/source kind when available, e.g. `annual_report`, `derived`, candidate source kinds only inside Fund documents/processors tests.
- `document_year`: positive int.
- `fund_code`: six-digit string.
- `processor_goal`: initially `template_chapters_1_6_minimum_field_families`.

Dispatch invariants:

- `fund_type` must be determined before processor resolution. If not classifiable, return `fund_type_missing_or_ambiguous`.
- Candidate intermediate kinds do not authorize parser replacement and must carry `candidate_only=true`, `field_correctness_status=not_proven`, and `source_truth_status=not_proven` in provenance/gap notes.
- `report_type != annual_report` is unsupported in first slice.

### Input Intermediate Contract

`FundProcessorInput` fields:

- `context: FundProcessorDispatchKey`
- `intermediate: ParsedAnnualReport | FutureFundDisclosureDocument | CandidateRepresentationDocument`
- `reference_metadata: AnnualReportReferenceMetadata | None`
- `candidate_status: CandidateRepresentationStatus | None`
- `source_provenance: PublicSourceProvenance | None`

Allowed first-slice input:

- Only `ParsedAnnualReport` with `intermediate_kind="parsed_annual_report.v1"`.

Allowed future candidate inputs:

- Candidate documents are allowed only inside `fund_agent/fund/documents` and `fund_agent/fund/processors` tests or candidate evidence harness.
- Candidate inputs cannot be exported to Service/UI/Host/renderer/quality gate and cannot be used as production fact truth without later source-truth/correctness gate.

### Output Field-family Contracts

`FundProcessorResult` fields:

- `processor_id`
- `output_schema_version`
- `fund_code`
- `report_year`
- `fund_type`
- `report_type`
- `input_intermediate_kind`
- `field_families: tuple[FundFieldFamilyResult, ...]`
- `gaps: tuple[FundExtractionGap, ...]` for cross-cutting gaps only, such as unsupported dispatch, unsafe source provenance, or candidate boundary blocks that cannot be attributed to one field family.
- `anchors: tuple[EvidenceAnchor, ...]`
- `source_provenance`
- `candidate_boundary: CandidateBoundaryStatus | None`
- `contract_status: satisfied | partial | missing | unsupported | blocked`

`FundFieldFamilyResult` fields:

- `field_family_id`: closed IDs aligned to template needs:
  - `product_essence.v1` for Chapter 1 product type, objective, scope, benchmark, style/risk text.
  - `return_attribution.v1` for Chapter 2 NAV growth, benchmark return, alpha/excess return, cost.
  - `manager_profile.v1` for Chapter 3 manager identity, tenure, strategy text, behavior, consistency inputs, holding.
  - `investor_experience.v1` for Chapter 4 holder structure, investor return, share change, redemption/subscription pressure.
  - `current_stage.v1` for Chapter 5 scale/share/holding/manager/strategy changes.
  - `core_risk.v1` for Chapter 6 risk characteristic, concentration, style drift, turnover, drawdown, veto items, next minimum verification question input.
- `chapter_ids`: tuple of public chapter IDs.
- `value`: typed dataclass or dict with schema version.
- `status`: `accepted`, `partial`, `missing`, `not_applicable`, `blocked`.
- `extraction_mode`: current modes `direct`, `derived`, `estimated`, `missing`, plus accepted planned mode `not_applicable`.
- `anchors`: tuple of `EvidenceAnchor`.
- `gaps`: tuple of `FundExtractionGap`.
- `source_provenance`.

Do not force all six field families into `StructuredFundDataBundle` in the first implementation. The first slice may return `FundProcessorResult` directly and wrap existing narrow extractors, then a later migration slice can adapt the result into `StructuredFundDataBundle`.

`ExtractionMode.not_applicable` rule:

- S1 may extend `ExtractionMode` with `not_applicable`.
- `not_applicable` is valid only when a field family is categorically inapplicable to the fund type or report type.
- `not_applicable` must never be used as a synonym for missing evidence, unsupported parser output, ambiguous locator, or extractor weakness; those cases must emit `missing`, `partial`, `field_family_missing`, or `field_family_partial`.

### EvidenceAnchor And Provenance Model

Keep current production `EvidenceAnchor` as the public anchor object for accepted processor outputs:

- `source_kind`: initially current `annual_report`, `external_api`, `derived`. Candidate source kinds may appear only in candidate boundary metadata or candidate-only notes, not as public production `EvidenceAnchor.source_kind` unless a later schema gate extends it.
- `document_year`, `section_id`, `page_number`, `table_id`, `row_locator`, `note` remain required anchor coordinates where applicable.
- Every non-missing `FundFieldFamilyResult` must include at least one anchor or explicitly be `derived` with source-anchor lineage.
- Candidate-to-anchor mappings can mirror EvidenceAnchor semantic fields but must retain `candidate_only`, `field_correctness_status=not_proven`, and `source_truth_status=not_proven`.

Provenance:

- Source provenance is copied from `ParsedAnnualReport.metadata.source` through current `project_public_source_provenance()`.
- Processor output must not invent source policy. It can report `source_provenance_status`, `fallback_enabled`, `fallback_used`, `selected_source`, and `source_mode` only from repository metadata/projection.
- For derived NAV metrics, keep derived anchor pattern like current bond risk drawdown path: `source_kind="derived"`, `section_id="derived:nav"`, stable metric locator, and note containing input source/query/period/record-count lineage.

### Fail-closed Gap Semantics

`FundExtractionGap` fields:

- `gap_code`: closed machine code.
- `field_family_id`
- `required_output_item_ids`: template item IDs when available.
- `severity`: `block`, `render_evidence_gap`, `render_minimum_verification_question`, `info`.
- `reason`: human-readable Chinese reason.
- `source_boundary`: `annual_report`, `derived_nav`, `candidate_only`, `unsupported_intermediate`, `unsupported_fund_type`, `ambiguous_locator`, `source_provenance_unsafe`.
- `next_minimum_verification_question`: optional string.
- `anchors`: anchors that explain partial evidence; empty for true absence.

Required gap codes for first implementation:

- `fund_type_missing_or_ambiguous`
- `unsupported_report_type`
- `unsupported_intermediate_kind`
- `unsupported_fund_type_processor`
- `field_family_missing`
- `field_family_partial`
- `evidence_anchor_missing`
- `candidate_only_not_source_truth`
- `source_provenance_unsafe`
- `derived_metric_unavailable`
- `ambiguous_table_or_locator`

Fail-closed rules:

- Missing required evidence never becomes a value by heuristic.
- Candidate-only evidence can support a candidate field-family result only with explicit non-proof status.
- Unsupported or ambiguous inputs return blocked/missing results, not generic parser dumps.
- Processor result cannot weaken current repository fail-closed behavior. Repository failures still propagate before processor execution unless a later gate explicitly designs a typed source failure result.
- Field-family-local gaps stay on `FundFieldFamilyResult.gaps`; `FundProcessorResult.gaps` is reserved for cross-cutting gaps not attributable to a single field family.

### Relationship To Existing FundDataExtractor And Narrow Extractors

Current `FundDataExtractor` remains the production facade for existing analyze/checklist callers. It already does three jobs:

1. Load `ParsedAnnualReport` through `FundDocumentRepository`.
2. Load/derive NAV data through typed NAV provider/repository.
3. Directly call narrow extractors and assemble `StructuredFundDataBundle`.

Planned migration:

- Slice 1: add registry/contracts and an active annual processor that wraps existing narrow extractors. Do not wire it into default `FundDataExtractor.extract()`.
- Slice 2: add optional constructor-injected registry behind `FundDataExtractor`, gated by explicit parameter or internal test-only adapter; default production path remains current direct extractor calls.
- Slice 3: once reviewed, replace direct extractor orchestration with registry result adaptation inside `FundDataExtractor` without changing public Service/UI/Host/renderer behavior.
- Slice 4+: add candidate intermediate processors and non-active fund-type processors only after separate planning/review gates.

Existing narrow extractors are not discarded:

- `extract_profile()` maps to `product_essence.v1`.
- `extract_performance()` maps to `return_attribution.v1`.
- `extract_manager_ownership()` maps to `manager_profile.v1` and parts of `investor_experience.v1`.
- `extract_holdings_share_change()` maps to `current_stage.v1`, holdings-related `manager_profile.v1`, and `investor_experience.v1`.
- `extract_bond_risk_evidence()` remains bond-specific and should not be forced into active-fund first slice except as a pattern for group-level evidence contracts.

S1 field-level mapping requirement:

- `fund_agent/fund/processors/active_annual.py` must include a module-level mapping table in its docstring or adjacent constant comments before the implementation code.
- The mapping table must list every S1-consumed extractor output field/path and map it to `field_family_id`, field-family field name, public chapter ID, extraction mode, required/optional status, and fallback gap code.
- No extractor output field may populate a `FundFieldFamilyResult.value` unless it is listed in this table.
- If a field-family field has no listed extractor output mapping, or the listed extractor output is absent/ambiguous, S1 must emit `field_family_partial` or `field_family_missing`; it must not reach into parser internals, candidate representations, raw full JSON, PDF cache, source helpers, or heuristics to fill the value.

## First Implementation Slice Proposal

Slice id: `S1_ACTIVE_ANNUAL_PROCESSOR_CONTRACTS_NO_LIVE`

Objective:

- Create the Processor/Extractor contract and registry.
- Implement a first `ActiveFundAnnualProcessor` that consumes current `ParsedAnnualReport` and wraps existing narrow extractors into six field-family results for template Chapters 1-6.
- Keep production behavior unchanged by not default-wiring `FundDataExtractor.extract()` to the registry.

Exact allowed files/modules for future implementation gate:

- Add `fund_agent/fund/processors/__init__.py`
- Add `fund_agent/fund/processors/contracts.py`
- Add `fund_agent/fund/processors/registry.py`
- Add `fund_agent/fund/processors/active_annual.py`
- Add `tests/fund/processors/__init__.py`
- Add `tests/fund/processors/test_registry.py`
- Add `tests/fund/processors/test_active_annual_processor.py`
- Required update `fund_agent/fund/README.md` because S1 modifies `fund_agent/fund/` by adding the Processor/Extractor package; document the current implemented Processor/Extractor boundary and preserve Docling/candidate non-proof boundaries.
- Optionally update `tests/README.md` only if new test layer commands/conventions are added.

Explicitly not allowed in S1:

- No modification to `FundDataExtractor.extract()` default behavior.
- No Service/UI/Host/renderer/quality gate imports or behavior changes.
- No `FundDocumentRepository` source policy, cache, PDF adapter, source helper, fallback, or source metadata changes.
- No Docling conversion, no candidate projection expansion, no parser full JSON consumption in production paths.
- No provider/LLM/analyze/checklist/golden/readiness/release/PR commands.
- No schema change to public `EvidenceAnchor.source_kind` unless a review explicitly accepts it before implementation.

Implementation details for S1:

- `contracts.py` defines closed Literals/dataclasses:
  - `FundProcessorDispatchKey`
  - `FundProcessorInput`
  - `FundFieldFamilyResult`
  - `FundExtractionGap`
  - `FundProcessorResult`
  - `FundProcessorProtocol`
  - status/intermediate/family/gap Literals.
- `registry.py` defines:
  - `FundProcessorRegistry.register(processor_cls, priority=None)`
  - `FundProcessorRegistry.resolve(context)`
  - `FundProcessorRegistry.create_default()` only if it registers processors without side effects.
- `active_annual.py` defines:
  - `ActiveFundAnnualProcessor.processor_id = "active_fund_annual.parsed_annual_report.v1"`
  - `supports()` only for `fund_type="active_fund"`, `report_type="annual_report"`, `intermediate_kind="parsed_annual_report.v1"`.
  - `extract()` validates `ParsedAnnualReport`, calls existing narrow extractors, maps outputs into field families, projects public provenance, and emits missing/partial gaps.
  - A field-level mapping table from extractor output field/path to field family and field-family field, with `field_family_partial` / `field_family_missing` behavior for missing mappings.
- S1 output can be parallel to `StructuredFundDataBundle`; it need not replace it.

`create_default()` side-effect definition:

- Forbidden side effects: any call to `FundDocumentRepository`, PDF cache, PDF adapter, source helper, Docling conversion, network, provider/LLM, analyze/checklist/golden/readiness/release command, or filesystem read/write.
- Pure imports of processor classes and already-pure narrow extractor functions are acceptable if import time performs no repository, cache, source, Docling, network, provider, or filesystem access.

Migration boundary:

- S1 is additive and no-live.
- Existing `FundDataExtractor` and CLI/product flows continue unchanged.
- Any production behavior switch must be a later implementation gate with direct tests proving output equivalence or accepted diffs.

Completion signal for S1:

- Registry tests prove priority ordering, first-supported wins, no supported processor fail-closes, and no raw parser fallback.
- Processor tests prove active annual parsed-report input returns expected field-family IDs, anchors/gaps, source provenance, and no candidate/proof/readiness claims.
- Processor tests include one synthetic happy-path `ParsedAnnualReport` fixture that exercises all six field families with non-missing results through the documented field-level mapping table.
- Static boundary tests prove guarded paths still do not import candidate internals, Docling, PDF adapter/cache, or processor internals from Service/UI/Host.

## Test And Validation Matrix

Planning gate validation:

- Read-only inspection only.
- Optional: `git diff --check -- docs/reviews/fund-processor-extractor-architecture-plan-20260617.md`
- Do not run pytest in this planning gate.

Future implementation S1 no-live tests:

| Test family | Target | Expected assertions |
|---|---|---|
| Unit: registry | `tests/fund/processors/test_registry.py` | priority descending, stable tie order, first `supports()` wins, unsupported context returns typed fail-closed result/error |
| Unit: dispatch key | `tests/fund/processors/test_registry.py` | invalid fund code/year/report type/intermediate kind rejected; no `extra_payload` |
| Unit: active processor | `tests/fund/processors/test_active_annual_processor.py` | `ParsedAnnualReport` fixture produces field families `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` |
| Unit: active processor happy path | `tests/fund/processors/test_active_annual_processor.py` | one synthetic no-live fixture covers all six field families with non-missing results and verifies the documented extractor-output-to-field-family mapping |
| Contract: field family | `tests/fund/processors/test_active_annual_processor.py` | every non-missing field family has anchors or derived lineage; every missing required field has `FundExtractionGap` |
| Contract: field mapping gaps | `tests/fund/processors/test_active_annual_processor.py` | unmapped or absent required field-family fields produce local `field_family_partial` or `field_family_missing` gaps, not heuristic values or result-level duplicates |
| Contract: provenance | `tests/fund/processors/test_active_annual_processor.py` | source provenance is projected from report metadata; no invented fallback/source policy |
| Boundary: no source access | `tests/fund/processors/test_active_annual_processor.py` plus AST guard | processor does not call repository/PDF/cache/source helper/network/Docling/provider/LLM |
| Boundary: guarded consumers | extend existing AST guard only if needed | Service/UI/Host/template/audit/quality/renderer do not import candidates, Docling, PDF adapter/cache, or concrete processor internals |
| Fixture strategy | synthetic `ParsedAnnualReport` with sections/tables | no live, no FDR, no PDF parsing, no Docling conversion; include one happy-path fixture covering all six field families; fixtures are text/table objects like current extractor tests |
| Negative/fail-closed | unsupported fund type/intermediate/report type | no generic parser dump, no silent success, explicit gap/error |
| Candidate boundary | candidate status objects if used | `candidate_only=true`, `field_correctness_status=not_proven`, `source_truth_status=not_proven`, no parser replacement claim |

Future allowed validation commands for S1, subject to implementation gate authorization:

- `uv run pytest tests/fund/processors/test_registry.py`
- `uv run pytest tests/fund/processors/test_active_annual_processor.py`
- `uv run pytest tests/fund/documents/test_docling_no_consumption_guards.py`
- `uv run pytest tests/fund/test_data_extractor.py` only if later slice touches facade integration.
- `uv run ruff check fund_agent/fund/processors tests/fund/processors`
- `git diff --check -- <approved files>`

Forbidden commands for this planning gate and for S1 unless separately authorized:

- Any live/network/source acquisition command.
- Any PDF/FDR/Docling conversion/export command.
- Any provider/LLM command.
- `fund-analysis analyze`, `fund-analysis checklist`, golden, readiness, release, PR, push, or external-state commands.
- Full pytest if not explicitly authorized by implementation gate.

README/docs sync:

- If S1 adds `fund_agent/fund/processors`, update `fund_agent/fund/README.md` to document the Fund package's Processor/Extractor boundary as current implemented contract, while preserving Docling/candidate non-proof boundary.
- If S1 adds a new test directory convention, update `tests/README.md`.
- Do not update `docs/design.md` or `docs/implementation-control.md` during S1 unless controller explicitly authorizes a truth/control sync gate.

## Review Residual Disposition

| Input | Finding | Disposition | Owner / destination |
|---|---|---|---|
| DS review Finding 1 | `implementation-control.md:9` wording may imply discussion doc itself entered truth sync | Accepted residual, non-blocking for this plan. This plan explicitly states discussion doc is input, not truth source. | Controller / later control-doc wording cleanup gate |
| DS review Finding 2 | startup packet gate input list does not label discussion doc as non-truth | Accepted residual, non-blocking. This plan uses `docs/docling-architecture-reorientation-20260617.md` only as architecture discussion input. | Controller / later startup-packet wording cleanup gate |
| DS review Finding 3 | `AGENTS.md` lacks current phase/gate pointer | Accepted discoverability residual, non-blocking. Mandatory read order and current control docs mitigate. | Controller / later rules-doc discoverability gate if desired |
| DS review Finding 4 | future 0-10 chapter audit wording risk | Deferred, outside Processor/Extractor S1. | Future template/audit design gate |
| DS review Finding 5 | README terminology drift from canonical `FundProcessorRegistry` | Accepted low residual; S1 README sync should use canonical name if docs are touched. | S1 implementation worker only if README update is in approved write set |
| AgentDS planreview F1 | Chapter 4-6 field-family mapping from existing narrow extractors is underspecified | Accepted and fixed in this plan. S1 `active_annual.py` must include a field-level mapping table from extractor output field/path to field family and field-family field; missing mappings produce `field_family_partial` or `field_family_missing`. | S1 implementation worker |
| AgentDS planreview F2 | `ExtractionMode.not_applicable` forward dependency | Accepted and fixed in this plan. S1 may extend `ExtractionMode` with `not_applicable` only for categorically inapplicable field families; never use it as a synonym for missing evidence. | S1 implementation worker |
| AgentDS planreview F3 | S1 README update optional vs mandatory | Accepted and fixed in this plan. `fund_agent/fund/README.md` update is required for S1 because S1 modifies `fund_agent/fund/`. | S1 implementation worker |
| AgentDS planreview F4 | `create_default()` side-effect ambiguity | Accepted and fixed in this plan. Side effects exclude repository/PDF cache/source helper/Docling/network/provider/filesystem calls; pure imports are allowed. | S1 implementation worker |
| AgentDS planreview F5 | Synthetic fixture structure not specified | Accepted and fixed in this plan. S1 tests require one synthetic happy-path fixture covering all six field families. | S1 implementation worker |
| AgentDS planreview F6 | Result-level gaps vs per-field-family gaps relationship unspecified | Accepted and fixed in this plan. Result-level gaps are cross-cutting-only; field-family gaps stay local. | S1 implementation worker |
| MiMo F1 | discussion statistics unverified | Accepted non-blocking. This plan does not rely on unverified statistics as facts. | Future evidence worker if statistics are needed |
| MiMo F2 | discussion roadmap suggestions not accepted | Accepted. This plan does not authorize archive actions or full roadmap implementation. | Future implementation gates |
| MiMo F3 | Dayu Processor/Registry is reference only | Accepted and enforced. | S1 implementation worker |
| MiMo F4 | gate naming minor drift | Non-blocking; canonical gate name here follows control doc. | None |

## Residual Risks And Follow-up Gates

Residual risks:

- Field-family contracts may still be too broad for a single implementation slice. Mitigation: S1 may emit six families using existing extractor outputs, but no downstream integration is authorized.
- `ExtractionMode.not_applicable` extension is accepted for S1 only under the categorical-inapplicability constraint; misuse as missing evidence remains a review risk.
- Public `EvidenceAnchor.source_kind` currently excludes candidate kinds. Candidate provenance should remain in boundary metadata unless a separate schema gate extends it.
- `FundDataExtractor` integration may require careful equivalence tests because current behavior includes NAV degradation and source failure propagation. S1 avoids default wiring.
- Active fund first slice may expose gaps in existing narrow extractors for Chapter 4-6 fields. Missing/partial gaps are acceptable; S1 must follow the documented `active_annual.py` field-level mapping table and must not backfill by parser dump, candidate truth claim, or heuristic values.
- Candidate intermediates such as `FundDisclosureDocument` and EID HTML render remain not production truth; adding them requires separate candidate schema/processor gates.

Follow-up gates:

1. `S1_ACTIVE_ANNUAL_PROCESSOR_CONTRACTS_NO_LIVE` implementation gate.
2. S1 code review/re-review gate.
3. Optional `FundDataExtractor Registry Integration No-live Planning Gate` for constructor-injected/default-off integration.
4. `StructuredFundDataBundle Adapter Migration Gate` only after registry output is reviewed.
5. Separate processor gates for index/enhanced/bond/QDII/FOF and for candidate intermediates.
6. Separate truth/control doc sync gate if controller wants DS wording/discoverability residuals corrected.

## Stop Condition

Current planning worker must stop after writing this single artifact and optional `git diff --check` for this artifact. No implementation, commit, push, PR, live/source/PDF/FDR/Docling/provider/LLM/analyze/checklist/golden/readiness/release commands are authorized.

## Completion Report Format

Use exactly:

```text
Verdict token: PLAN_READY_FOR_REVIEW_NOT_READY
Artifact path: docs/reviews/fund-processor-extractor-architecture-plan-20260617.md
Blocking open questions: <none or list>
Residual risks: <short list>
```

## Blocking Open Questions

None for plan review. Open design choices are classified as residual risks/follow-up gates above and do not block review of this architecture plan.
