# FundDisclosureDocument Source-truth Field Extraction Plan

## Gate

- Work unit: `FundDisclosureDocument Source-truth Field Extraction`
- Work unit type: feature / architecture-sensitive extractor contract change
- Gate: `plan`
- Branch: `funddisclosure-source-truth-field-extraction-plan`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`

## Goal

Implement the first source-truth field extraction slice for the explicit `FundDisclosureDocument` processor route.

The first implementation slice must convert only one field family, `product_essence.v1`, from the current FDD `missing + candidate_only_not_source_truth` shape into public source-truth field output when the FDD intermediate is non-candidate, admitted, identity-safe, provenance-safe, and provides stable section/table/cell/paragraph locators.

## Motivation

S6-A through S6-G completed candidate-only locator selection for six field families, but the accepted boundary is explicit: candidate locator evidence is still `candidate_only / not_proven / NOT_READY`, public field families remain `missing`, and candidate evidence must not be consumed by Service/UI/Host/renderer/quality gate or LLM prompt.

The next useful step is not another locator selector. It is a narrow extractor/source-truth slice that proves the Processor/Extractor boundary can promote a non-candidate FDD intermediate into public `EvidenceAnchor`-backed fields while preserving fail-closed behavior for candidate and unsafe inputs.

## Success Signal

- For non-candidate admitted `FundDisclosureDocumentContentIntermediate` inputs, `FundDisclosureDocumentProcessor` can extract `product_essence.v1` fields with:
  - `status="partial"` or `status="accepted"` according to required-field coverage.
  - `extraction_mode="direct"`.
  - non-empty public `EvidenceAnchor` values using `source_kind="annual_report"`.
  - source provenance preserved from the intermediate.
  - no candidate evidence in the promoted field output.
- For candidate-boundary inputs, behavior remains fail-closed and does not return a usable bundle.
- For admitted but insufficient non-candidate FDD inputs, `product_essence.v1` remains `missing` with classified local gaps.
- Other field families remain current-state `missing`.
- Default `FundDataExtractor.extract()` without `disclosure_intermediate` still uses the active parsed annual report route.

## Non-goals

- No code implementation in this planning gate.
- No direct Service/UI/Host/renderer/quality-gate consumption of FDD or candidate artifacts.
- No promotion of candidate-only locator evidence to source truth.
- No parser replacement and no `EvidenceSourceKind` expansion.
- No Docling baseline qualification retry, source-truth residual closure retry, or full representation correctness proof.
- No final Chapter 5 judgment, LLM prompt consumption, golden/readiness/release transition, or default production route switch.
- No non-active fund processor implementation.
- No extraction for `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1` in the first implementation slice.

## Design Alignment

- `AGENTS.md` requires structured fund field extraction to pass through Fund layer Processor/Extractor boundaries.
- `docs/design.md` says Docling/pdfplumber/EID HTML render/FDD are only Fund documents internals or Processor/Extractor inputs; facts must pass through Extractor, `EvidenceAnchor`, and fail-closed classification before entering CHAPTER_CONTRACT/reporting.
- `docs/design.md` current S6 state says S6-B through S6-G only provide candidate-only locator evidence; public field family values remain missing and do not prove source truth.
- `FundProcessorResult` / `FundFieldFamilyResult` already require non-missing field families to carry public `EvidenceAnchor`.
- `EvidenceAnchor.source_kind` is currently limited to `annual_report`, `external_api`, and `derived`; this slice must use `annual_report`, not invent a candidate source kind.

## First-principles Judgment

This work unit is valid because the current system has a clear gap between locator discovery and source-truth extraction:

- Locator selectors can find plausible places in FDD content.
- Public field-family output still cannot use those locators because candidate evidence is not source truth.
- The correct bridge is not to relax the candidate boundary, but to define a non-candidate FDD extractor path that emits public fields only when source identity, provenance, locator stability, and required-field coverage are sufficient.

The narrowest useful slice is `product_essence.v1` because it maps to template Chapter 1 and has existing active parsed route fields: `basic_identity`, `product_profile`, `risk_characteristic_text`, and `benchmark`.

## Direct Code Evidence

- `fund_agent/fund/processors/contracts.py`
  - Defines `FundDisclosureDocumentContentIntermediate` with sections, paragraph blocks and table blocks.
  - Defines `FundCandidateEvidenceRecord` as `candidate_only=True`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`.
  - Requires non-missing `FundFieldFamilyResult` to have public `EvidenceAnchor`.
- `fund_agent/fund/processors/fund_disclosure_processor.py`
  - Supports exact `active_fund + annual_report + fund_disclosure_document.v1`.
  - Currently admits safe non-candidate FDD inputs but returns all six field families as missing.
  - Current S6 locator helpers populate candidate evidence but keep public value and anchors empty.
- `fund_agent/fund/data_extractor.py`
  - Default path without `disclosure_intermediate` still resolves `parsed_annual_report.v1`.
  - Explicit FDD path routes through registry and fail-closes on candidate boundary, unsafe provenance, failure classes, identity mismatch and unsupported fund type.
- `tests/fund/test_data_extractor.py`
  - Covers default parsed route preservation.
  - Covers explicit FDD route through registry.
  - Covers candidate boundary fail-closed behavior.
  - Covers admitted non-candidate FDD current missing bundle behavior.

## Affected Files / Modules

Implementation slice A should be limited to:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `fund_agent/fund/processors/contracts.py` only if a new local gap code is strictly required.
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py` only for facade-level regression of explicit FDD route.
- `fund_agent/fund/README.md` only if implementation changes current package behavior wording.
- `docs/design.md` only after implementation is accepted, to sync current facts.

No other files are authorized by the first implementation slice.

## Contract / Schema Decisions

### Public EvidenceAnchor

Promoted FDD fields must emit public anchors with:

- `source_kind="annual_report"`
- `document_year=context.document_year`
- `section_id`: stable annual-report section id from FDD section/block/cell context.
- `page_number`: `None` unless the FDD protocol exposes stable page number in an accepted prior gate; do not infer from unavailable data.
- `table_id`: table id for table-derived fields, otherwise `None`.
- `row_locator`: stable row/cell/block locator string derived from FDD locator identity.
- `note`: bounded excerpt or locator note; must not include candidate proof wording.

### Product Essence Fields

`product_essence.v1` first slice should target these output fields:

- `basic_identity`
- `product_profile`
- `risk_characteristic_text`
- `benchmark`

The extractor should prefer table/cell values for identity-like key/value fields and paragraph/section text for descriptive fields.

### Status Rules

- `accepted`: all required product essence fields are extracted with anchors.
- `partial`: at least one required product essence field is extracted with anchors, but not all.
- `missing`: no required product essence field can be extracted.
- `blocked`: reserved for admission/identity/provenance/input-level failures, not ordinary absent fields.

### Gap Rules

Use existing gap codes when possible:

- `field_family_missing`
- `field_family_partial`
- `evidence_anchor_missing`
- `ambiguous_table_or_locator`

Only add a new `FundExtractionGapCode` if the implementation cannot express a stable failure with existing codes.

## Implementation Decisions

1. Add internal source-truth extraction helpers under `fund_disclosure_processor.py`.
   Keep them private and module-local until a second field family proves shared abstraction pressure.

2. Require non-candidate admitted FDD inputs.
   If `intermediate.candidate_boundary is not None`, keep current fail-closed behavior through admission/facade tests; do not attempt extraction.

3. Use section/table/cell/paragraph locators, not raw parser identity.
   The extractor consumes only `FundDisclosureDocumentContentIntermediate` protocol fields.

4. Keep the first extractor deterministic and lexical.
   It may use the already accepted product-essence section/table/cell role vocabulary as a starting point, but output fields must be direct source fields with public anchors, not candidate evidence records.

5. Preserve all existing S6 candidate locator behavior.
   Candidate evidence can still be attached to missing field families for candidate/internal diagnostics, but not to promoted source-truth outputs.

6. Do not change `FundDataExtractor.extract()` routing semantics.
   It already admits explicit FDD route and protects default route. The first slice should only change the result produced by `FundDisclosureDocumentProcessor` for safe non-candidate FDD input.

## Implementation Slices

### Slice A - Product Essence Source-truth Extraction

Objective:
Implement `product_essence.v1` direct extraction for safe non-candidate FDD intermediates.

Allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `fund_agent/fund/processors/contracts.py` only if required by a new gap code
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`

Expected behavior:

- Safe non-candidate FDD fixtures can produce `product_essence.v1` public value and anchors.
- Candidate-boundary fixtures still fail closed.
- Unsafe/missing provenance and failure classes still fail closed.
- Other five field families remain missing.

Validation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py fund_agent/fund/processors/contracts.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
git diff --check
```

Completion signal:
All listed tests pass, ruff passes, diff check passes, and implementation evidence records exact changed files plus residual risks.

### Slice B - Documentation Sync After Accepted Implementation

Objective:
After Slice A implementation and review acceptance, sync docs to current facts.

Allowed files:

- `docs/design.md`
- `fund_agent/fund/README.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- one implementation evidence artifact under `docs/reviews/`

Expected behavior:

- Docs say only `product_essence.v1` has non-candidate FDD source-truth extraction.
- Docs continue to say candidate evidence is not source truth.
- Docs continue to say readiness/release remains `NOT_READY`.

## Tests / Validation Matrix

Required no-live tests:

- Positive non-candidate FDD product essence extraction:
  - `status in {"partial", "accepted"}`
  - `extraction_mode="direct"`
  - `anchors` non-empty
  - every anchor has `source_kind="annual_report"`
  - `candidate_evidence == ()` for the promoted field family
- Candidate boundary remains blocked:
  - current `test_explicit_disclosure_candidate_boundary_fails_closed` still passes.
- Default parsed annual route remains unchanged:
  - current default active route test still passes.
- Non-active explicit FDD remains fail-closed:
  - current non-active explicit FDD test still passes.
- Missing/ambiguous product essence fields produce classified missing/partial gaps.
- Other field families remain missing in Slice A.

## Docs Decision

Docs must not be updated before code is accepted. After implementation acceptance, sync only current facts:

- `docs/design.md`: update Fund Processor/Extractor section to say FDD non-candidate `product_essence.v1` source-truth extraction is implemented if Slice A is accepted.
- `fund_agent/fund/README.md`: update Fund package current implementation summary.
- `docs/implementation-control.md` and `docs/current-startup-packet.md`: update gate status and residual ownership.

## Risks / Open Questions

| Risk | Disposition |
|---|---|
| FDD content protocol lacks page number | Accept `page_number=None`; do not infer unsupported page data. |
| Existing candidate locators are lexical and not field correctness proof | Do not reuse candidate evidence as public source truth; only safe non-candidate FDD path can promote direct fields. |
| Over-broad lexical matching may produce false positives | Keep Slice A fixtures focused; classify ambiguous matches as `ambiguous_table_or_locator` rather than promoted values. |
| Six field families are too broad for one slice | Only `product_essence.v1` is in Slice A; others are later work units/slices after review. |
| Public `EvidenceSourceKind` lacks FDD-specific source kind | Use `annual_report`; do not expand source kind in this gate. |

No blocking open question remains for plan review. The plan is intentionally narrow and code-generation-ready for Slice A.

## Residual Risks / Owners

| Residual | Owner / Destination |
|---|---|
| `return_attribution.v1` FDD source-truth extraction | Future field-family implementation slice after Slice A review. |
| `manager_profile.v1` FDD source-truth extraction | Future field-family implementation slice after Slice A review. |
| `investor_experience.v1` FDD source-truth extraction | Future field-family implementation slice after Slice A review. |
| `current_stage.v1` FDD source-truth extraction | Future field-family implementation slice after Slice A review. |
| `core_risk.v1` FDD source-truth extraction | Future field-family implementation slice after Slice A review. |
| Non-active fund FDD processors | Future fund-type-specific processor planning gate. |
| Readiness/release | Future explicit readiness/release gate. |

## Completion Report Format

Implementation worker must report:

- changed files;
- exact tests and outputs;
- behavior changes by field family;
- retained fail-closed behavior;
- residual risks and owners;
- confirmation that no Service/UI/Host/renderer/quality-gate consumption was added.
