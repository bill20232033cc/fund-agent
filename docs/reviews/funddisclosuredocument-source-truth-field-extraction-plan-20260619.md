# FundDisclosureDocument Source-truth Field Extraction Plan

## Gate

- Work unit: `FundDisclosureDocument Source-truth Field Extraction`
- Work unit type: feature / architecture-sensitive extractor contract change
- Gate: `plan-fix`
- Branch: `funddisclosure-source-truth-field-extraction-plan`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Plan review to close: `docs/reviews/plan-review-20260619-221202.md`
- Controller judgment: `docs/reviews/funddisclosuredocument-source-truth-field-extraction-plan-review-controller-judgment-20260619.md`

## Goal

Make the explicit `FundDisclosureDocument` processor route code-generation-ready for the first source-truth field extraction path without promoting candidate evidence.

The implementation must be split into two ordered slices:

1. **Slice A - Source-truth admission proof contract.** Add a positive proof contract for source-truth FDD inputs. `candidate_boundary is None` is necessary but never sufficient. Inputs without positive proof must fail closed and must not emit public field values.
2. **Slice B - Product essence direct extraction.** Only after Slice A proof is present and valid, extract `product_essence.v1` public values from stable FDD table/cell/paragraph locators.

The original field-extraction goal is therefore not downgraded to a prototype, but its first implementation step is a proof/admission contract. Product extraction is explicitly downstream of that proof.

## Motivation

S6-A through S6-G completed candidate-only locator selection for six field families. The accepted boundary is unchanged: candidate locator evidence is still `candidate_only / not_proven / NOT_READY`, public field families remain `missing`, and candidate evidence must not be consumed by Service/UI/Host/renderer/quality gate or LLM prompt.

The next useful step is not another locator selector and not a blind promotion of non-candidate stubs. It is a narrow positive-admission contract followed by one field-family extractor that proves the Processor/Extractor boundary can emit public `EvidenceAnchor`-backed fields only from an admitted source-truth FDD intermediate.

## Success Signal

- Slice A adds an explicit source-truth admission proof contract and processor guard.
- `candidate_boundary is None` without valid source-truth proof yields fail-closed output:
  - no public field-family `value`;
  - no public `EvidenceAnchor`;
  - local/result gap uses the new source-truth-proof failure code defined below.
- A candidate-boundary input remains `blocked` and never emits public field values.
- Only an input with both `candidate_boundary is None` and valid positive source-truth proof may reach Slice B extraction.
- Slice B extracts only `product_essence.v1` with:
  - exact `value` shape defined in this plan;
  - `extraction_mode="direct"`;
  - non-empty public `EvidenceAnchor` values using `source_kind="annual_report"`;
  - `candidate_evidence == ()` for the promoted field family;
  - other field families still current-state `missing`.
- Default `FundDataExtractor.extract()` without `disclosure_intermediate` still uses the active parsed annual report route.

## Non-goals

- No code implementation in this planning gate.
- No direct Service/UI/Host/renderer/quality-gate consumption of FDD or candidate artifacts.
- No promotion of candidate-only locator evidence to source truth.
- No parser replacement and no `EvidenceSourceKind` expansion.
- No Docling baseline qualification retry, source-truth residual closure retry, or full representation correctness proof.
- No final Chapter 5 judgment, LLM prompt consumption, golden/readiness/release transition, or default production route switch.
- No non-active fund processor implementation.
- No extraction for `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1` in this work unit.
- No sibling-cell/table traversal API beyond the current `FundDisclosureCellLike` fields.

## Design Alignment

- `AGENTS.md` requires structured fund field extraction to pass through Fund layer Processor/Extractor boundaries.
- `docs/design.md` says Docling/pdfplumber/EID HTML render/FDD are only Fund documents internals or Processor/Extractor inputs; facts must pass through Extractor, `EvidenceAnchor`, and fail-closed classification before entering CHAPTER_CONTRACT/reporting.
- `docs/design.md` current S6 state says S6-B through S6-G only provide candidate-only locator evidence; public field family values remain missing and do not prove source truth.
- `FundFieldFamilyResult` requires non-missing field families to carry public `EvidenceAnchor`.
- `EvidenceAnchor.source_kind` is currently limited to existing public source kinds; this work unit must use `annual_report`, not invent an FDD or candidate source kind.

## Direct Code Evidence

- `fund_agent/fund/processors/contracts.py`
  - `FundDisclosureDocumentIntermediate` currently has `candidate_boundary` but no positive source-truth proof field.
  - `CandidateBoundaryStatus` only blocks candidate promotion; it does not prove source truth.
  - `FundDisclosureDocumentContentIntermediate` exposes sections, paragraph blocks and table blocks, but no source-truth admission proof.
  - `FundFieldFamilyResult.value` is `dict[str, object]`, so this plan must define the exact `product_essence.v1.value` shape.
- `fund_agent/fund/processors/fund_disclosure_processor.py`
  - Supports exact `active_fund + annual_report + fund_disclosure_document.v1`.
  - Current admitted FDD inputs still return all six public field families as `missing`, optionally with candidate evidence.
  - Current candidate selector helpers must remain candidate-only and must not be reused as public source truth.
- `tests/fund/processors/test_fund_disclosure_processor.py`
  - `_ContentIntermediateStub` defaults to `candidate_boundary=None`, but it is only a test object and currently does not prove repository-mediated source truth.
  - Existing candidate-selector tests assert public value/anchor stay empty; new source-truth tests must distinguish proof-positive fixtures from proof-missing fixtures.

## Affected Files / Modules

Implementation Slice A is allowed to touch:

- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py` only if facade-level regression needs the new proof fixture.

Implementation Slice B is allowed to touch:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py` only for explicit FDD route projection regression.

Documentation sync is after accepted implementation/review only:

- `docs/design.md`
- `fund_agent/fund/README.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- one implementation evidence artifact under `docs/reviews/`

No other files are authorized by this plan.

## Slice A Contract - Positive Source-truth Admission Proof

### New Contract Type

Add a frozen dataclass in `fund_agent/fund/processors/contracts.py`:

```python
@dataclass(frozen=True, slots=True)
class FundDisclosureSourceTruthAdmissionProof:
    proof_kind: Literal["repository_loaded_annual_report_identity.v1"]
    source_boundary: Literal["annual_report"]
    fund_code: str
    report_year: int
    document_kind: Literal["annual_report"]
    intermediate_kind: Literal["fund_disclosure_document.v1"]
    source_kind: Literal["annual_report"]
    repository_identity_verified: Literal[True]
    source_provenance_verified: Literal[True]
    locator_identity_verified: Literal[True]
    parser_integrity_verified: Literal[True]
    producer: Literal["FundDocumentRepository"]
```

Validation rules:

- `fund_code` must be 6 digits.
- `report_year` must be positive.
- `repository_identity_verified`, `source_provenance_verified`, `locator_identity_verified`, and `parser_integrity_verified` must all be `True`.
- `proof_kind`, `source_boundary`, `document_kind`, `intermediate_kind`, `source_kind`, and `producer` accept only the literal values above.
- The proof does not authorize parser replacement, readiness, or candidate promotion.

### Protocol Extension

Extend `FundDisclosureDocumentContentIntermediate` with:

```python
source_truth_admission: FundDisclosureSourceTruthAdmissionProof | None
```

Only content intermediates can carry source-truth proof because field extraction needs section/table/paragraph locator identity. The base `FundDisclosureDocumentIntermediate` admission protocol remains content-free for existing S6 candidate/admission tests.

### Processor Admission Rule

Add a private helper in `fund_disclosure_processor.py`, for example `_validate_source_truth_admission(intermediate, context)`.

The helper returns positive only if all conditions hold:

- `isinstance(intermediate, FundDisclosureDocumentContentIntermediate)`;
- `intermediate.candidate_boundary is None`;
- `intermediate.failure_class is None`;
- `intermediate.source_provenance is not None`;
- `intermediate.source_truth_admission is not None`;
- proof identity equals dispatch identity:
  - `proof.fund_code == context.fund_code == intermediate.fund_code`;
  - `proof.report_year == context.document_year == intermediate.report_year`;
  - `proof.document_kind == context.report_type == intermediate.document_kind`;
  - `proof.intermediate_kind == context.intermediate_kind == intermediate.intermediate_kind`;
  - `proof.source_kind == context.source_kind == "annual_report"`;
- all proof booleans are true as validated by the dataclass.

Failure behavior:

- Candidate-boundary inputs keep existing `candidate_boundary_blocked` behavior.
- Proof-missing or proof-invalid non-candidate inputs must not call product extraction.
- Proof-missing or proof-invalid non-candidate inputs return public field families as `missing`, with no public anchors and no public values.
- Add exact internal contract values in `contracts.py`:
  - `FundExtractionGapCode`: `source_truth_admission_missing`
  - `FundExtractionGapCode`: `source_truth_admission_invalid`
  - `FundExtractionSourceBoundary`: `source_truth_unverified`
- Missing proof gap:
  - `gap_code="source_truth_admission_missing"`
  - `message="FundDisclosureDocument source-truth admission proof is missing"`
  - `source_boundary="source_truth_unverified"`
- Invalid proof gap:
  - `gap_code="source_truth_admission_invalid"`
  - `message="FundDisclosureDocument source-truth admission proof is invalid"`
  - `source_boundary="source_truth_unverified"`

This is an internal processor/fail-closed gap. It is not an `EvidenceSourceKind` expansion.

## Slice B Contract - product_essence.v1 Value Schema

`product_essence.v1.value` must be a `dict[str, object]` with only these top-level keys:

- `basic_identity`
- `product_profile`
- `benchmark`
- `risk_characteristic_text`

Unavailable top-level fields must be omitted, not included with `None`, so `_field_from_family()` projects missing fields as `ExtractedField(value=None, extraction_mode="missing")`.

### `basic_identity` Shape

Required to include this top-level value:

- `fund_name: str`
- `fund_code: str`

Optional keys, present with `str | None` values:

- `fund_category`
- `fund_scale`
- `fund_manager`
- `management_company`
- `custodian`
- `inception_date`

Required classification keys:

- `classified_fund_type: Literal["active_fund"]`
- `classification_basis: tuple[str, ...]`

Exact construction:

- `fund_code` must come from an anchored FDD cell value matching the dispatch `context.fund_code`; if a candidate value conflicts with dispatch identity, omit `basic_identity` and add `ambiguous_table_or_locator`.
- `classified_fund_type` must come from `context.fund_type`, not from lexical inference.
- `classification_basis` must be `("dispatch_key.fund_type=active_fund",)`.

### `product_profile` Shape

Required to include this top-level value:

- At least one of `investment_objective`, `investment_scope`, or `investment_strategy` is a non-empty string.

Keys and types:

- `investment_objective: str | None`
- `style_positioning: str | None`
- `investment_scope: str | None`
- `investment_strategy: str | None`

Exact construction:

- `style_positioning` must only be filled from an explicit `style_positioning` / `投资风格` / `产品定位` label in FDD content.
- Do not derive `style_positioning` from investment objective in this FDD source-truth slice.

### `benchmark` Shape

Required to include this top-level value:

- `benchmark_text: str`

No other benchmark keys are allowed in Slice B.

### `risk_characteristic_text` Shape

Required to include this top-level value:

- `schema_version: Literal["risk_characteristic_text.v1"]`
- `fund_code: str`
- `report_year: int`
- `risk_characteristic_text: str`
- `source_anchors: list[dict[str, object]]`

`source_anchors` entries must contain exactly:

- `section_id: str | None`
- `page_number: None`
- `table_id: str | None`
- `row_locator: str | None`

`fund_code` and `report_year` must equal dispatch context values.

### Field-family Status

- `accepted`: all four top-level values are present: `basic_identity`, `product_profile`, `benchmark`, `risk_characteristic_text`.
- `partial`: at least one top-level value is present, but not all four.
- `missing`: no top-level value is present.
- `blocked`: admission/identity/provenance/input-level failures only; not ordinary absent fields.

`FundFieldFamilyResult.anchors` must contain at least one public anchor for every emitted top-level value. The family anchor tuple can be the stable deduplicated union of anchors used by included top-level values.

## Slice B Extraction Rules

### Label Map

Only these labels are in scope:

| Output path | Labels |
|---|---|
| `basic_identity.fund_name` | `基金名称`, `基金简称` |
| `basic_identity.fund_code` | `基金主代码`, `基金代码` |
| `basic_identity.fund_category` | `基金类别`, `基金类型` |
| `basic_identity.fund_scale` | `基金规模`, `基金资产净值` |
| `basic_identity.fund_manager` | `基金经理` |
| `basic_identity.management_company` | `基金管理人` |
| `basic_identity.custodian` | `基金托管人` |
| `basic_identity.inception_date` | `基金合同生效日`, `成立日期` |
| `product_profile.investment_objective` | `投资目标` |
| `product_profile.investment_scope` | `投资范围` |
| `product_profile.investment_strategy` | `投资策略` |
| `product_profile.style_positioning` | `投资风格`, `产品定位`, `风格定位` |
| `benchmark.benchmark_text` | `业绩比较基准`, `比较基准` |
| `risk_characteristic_text.risk_characteristic_text` | `风险收益特征`, `基金风险收益特征` |

### Table/cell Rule

The current `FundDisclosureCellLike` exposes one cell and its locator context; it does not expose sibling lookup. Slice B must not read sibling cells.

A table cell is a value candidate only when all rules hold:

- table and cell `locator_stability == "stable"`;
- the output path label matches `cell.row_label_path` first, otherwise `cell.column_header_path`;
- `cell.cell_text_normalized` is non-empty; fallback to `cell.cell_text` only when normalized text is empty;
- the selected cell text is not exactly one of the matched labels and not one of `项目`, `指标`, `名称`, `内容`, `说明`;
- for `basic_identity.fund_code`, selected text must equal `context.fund_code`;
- source path is exactly `table_blocks[{table_index}].cells[{cell_index}]` using tuple order after sorting cells by `(row_index, column_index)` only for iteration.

Table/cell priority:

1. Use table/cell candidates before paragraph fallback for every output path.
2. If exactly one normalized value exists for an output path, use it.
3. If multiple candidates have the same normalized value, deduplicate and use the first stable locator as the primary anchor.
4. If multiple different normalized values exist for the same output path at the same priority, omit that output path and add `ambiguous_table_or_locator`.

### Paragraph Fallback Rule

Paragraph fallback is allowed only for:

- `product_profile.investment_objective`
- `product_profile.investment_scope`
- `product_profile.investment_strategy`
- `product_profile.style_positioning`
- `benchmark.benchmark_text`
- `risk_characteristic_text.risk_characteristic_text`

Paragraph fallback is not allowed for `basic_identity.*`.

A paragraph is a value candidate only when:

- paragraph `locator_stability == "stable"`;
- either its `heading_path` contains the output label, or its `text_normalized` starts with `{label}:`, `{label}：`, or `{label} `;
- extracted value is the text after the label separator, or the whole paragraph text when the heading path supplies the label;
- extracted value is non-empty and is not just the label itself.

If table/cell produced an unambiguous value for an output path, paragraph fallback for that path is ignored. If table/cell produced no value, paragraph fallback follows the same duplicate/ambiguity rule as table/cell.

### Anchor Rule

Every emitted output path must have an `EvidenceAnchor`:

- `source_kind="annual_report"`
- `document_year=context.document_year`
- `section_id` from `cell.section_anchor`, `table.section_id`, or `paragraph.section_id`
- `page_number=None`
- `table_id` from the table/cell when applicable, otherwise `None`
- `row_locator`:
  - table/cell: `field=<output_path>; table_id=<table_id>; row=<row_index>; column=<column_index>; cell_id=<cell_id>`
  - paragraph: `field=<output_path>; block_id=<block_id>`
- `note`: bounded source excerpt, not candidate/proof wording

Candidate evidence records must not be copied into public anchors.

### Missing And Ambiguity Behavior

- Missing optional subfields do not create gaps.
- Missing required top-level requirements create `field_family_partial` when at least one top-level value exists.
- If no top-level value exists, `product_essence.v1` is `missing` with `field_family_missing`.
- Ambiguous duplicate values for a required output path create `ambiguous_table_or_locator`; the ambiguous path is omitted.
- If ambiguity removes all top-level values, family status is `missing`; otherwise `partial`.

## Implementation Decisions

1. Preserve existing admission and identity checks before source-truth proof validation.
2. Add the source-truth proof dataclass and protocol property before any extraction helper is implemented.
3. Add a private extraction helper only for `product_essence.v1` after proof validation passes.
4. Keep existing S6 candidate locator helpers unchanged for candidate/missing diagnostic output.
5. Do not use candidate evidence as extraction input.
6. Do not change default `FundDataExtractor.extract()` routing semantics.
7. Keep extraction deterministic and lexical; no LLM, provider, PDF, Docling, repository, network, or filesystem reads inside the processor.

## Implementation Slices

### Slice A - Source-truth Admission Proof Contract

Objective:
Add the positive source-truth admission proof contract and fail-closed guard.

Allowed files:

- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py` only if explicit facade regression needs the proof fixture.

Expected behavior:

- Existing candidate-boundary tests still pass.
- Existing candidate selector tests keep public `value == {}` and `anchors == ()`.
- A non-candidate FDD content stub without `source_truth_admission` produces no public values and records `source_truth_admission_missing` or the exact fallback gap code chosen in this slice.
- A proof-positive FDD content stub reaches the extraction decision point but may still return `missing` until Slice B.

Required tests:

- `test_source_truth_admission_requires_positive_proof`
  - fixture: `_ContentIntermediateStub(candidate_boundary=None, source_truth_admission=None)`
  - assert: `product_essence.v1.value == {}`, `anchors == ()`, no public value, `source_truth_admission_missing` gap present.
- `test_source_truth_admission_rejects_identity_mismatch`
  - fixture: proof `fund_code` or `report_year` differs from dispatch context.
  - assert: no public value/anchors; `source_truth_admission_invalid` gap present.
- `test_source_truth_admission_accepts_repository_loaded_identity_proof`
  - fixture: proof fields match dispatch/intermediate identity and all booleans are true.
  - assert: helper/admission path recognizes proof-positive state; if Slice B not yet implemented, public family may remain missing.
- Existing `test_product_essence_selector_preserves_candidate_boundary_blocked_status` continues to assert candidate input remains `blocked`.

Validation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
uv run ruff check fund_agent/fund/processors/contracts.py fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
git diff --check
```

### Slice B - Product Essence Source-truth Extraction

Objective:
Implement `product_essence.v1` direct extraction for proof-positive FDD intermediates only.

Allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py` only for explicit FDD route projection regression.

Expected behavior:

- Proof-positive fixtures can produce `product_essence.v1` public value and anchors.
- Proof-missing fixtures still fail closed with no public values.
- Candidate-boundary fixtures still fail closed.
- Unsafe/missing provenance and failure classes still fail closed.
- Other five field families remain missing.

Required tests:

- `test_product_essence_source_truth_extracts_exact_value_shape`
  - fixture cells:
    - `row_label_path=("基金名称",)`, `cell_text_normalized="测试主动基金"`
    - `row_label_path=("基金主代码",)`, `cell_text_normalized="004393"`
    - `row_label_path=("基金管理人",)`, `cell_text_normalized="测试基金管理有限公司"`
    - `row_label_path=("基金托管人",)`, `cell_text_normalized="测试托管银行"`
    - `row_label_path=("业绩比较基准",)`, `cell_text_normalized="沪深300指数收益率*80%+中债综合指数收益率*20%"`
    - `row_label_path=("风险收益特征",)`, `cell_text_normalized="本基金属于主动权益基金，风险收益水平较高。"`
  - fixture paragraph: heading/path or label for `投资目标`.
  - assert exact top-level keys are `basic_identity`, `product_profile`, `benchmark`, `risk_characteristic_text`.
  - assert exact nested required values and `classified_fund_type == "active_fund"`.
  - assert `candidate_evidence == ()`, `extraction_mode == "direct"`, `anchors` non-empty and every anchor `source_kind == "annual_report"`.
- `test_product_essence_source_truth_requires_proof_even_when_candidate_boundary_none`
  - same content as positive fixture, but no proof.
  - assert no public value/anchors and `source_truth_admission_missing` gap present.
- `test_product_essence_source_truth_ambiguous_duplicate_omits_conflicting_path`
  - two stable `基金名称` cells with different normalized values.
  - assert `basic_identity` omitted, gap `ambiguous_table_or_locator`, no unanchored fallback.
- `test_product_essence_source_truth_paragraph_fallback_for_descriptive_fields`
  - no table value for `投资范围`; paragraph text starts `投资范围：...`.
  - assert `product_profile.investment_scope` extracted with paragraph anchor.
- `test_product_essence_source_truth_missing_keeps_family_missing`
  - proof-positive content has no allowed labels.
  - assert `status == "missing"`, `value == {}`, `anchors == ()`, `field_family_missing`.
- `test_product_essence_source_truth_partial_when_required_groups_missing`
  - proof-positive content includes only fund name/code.
  - assert `status == "partial"`, `basic_identity` present, missing required groups reflected by `field_family_partial`.
- Existing default parsed annual route and non-active explicit FDD fail-closed tests must still pass.

Validation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
git diff --check
```

Completion signal:
All listed tests pass, ruff passes, diff check passes, and implementation evidence records exact changed files plus residual risks.

### Slice C - Documentation Sync After Accepted Implementation

Objective:
After Slice A/B implementation and review acceptance, sync docs to current facts.

Allowed files:

- `docs/design.md`
- `fund_agent/fund/README.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- one implementation evidence artifact under `docs/reviews/`

Expected behavior:

- Docs say only proof-positive `FundDisclosureDocument` inputs can produce source-truth field values.
- Docs say only `product_essence.v1` has FDD source-truth extraction, if Slice B is accepted.
- Docs continue to say candidate evidence is not source truth.
- Docs continue to say readiness/release remains `NOT_READY`.

## Tests / Validation Matrix

| Requirement | Test coverage |
|---|---|
| `candidate_boundary=None` is not proof | proof-missing fixture with extractable content returns no public value/anchor |
| Positive proof required | proof-positive fixture reaches extraction and can emit values |
| Identity mismatch fails closed | proof fund/year/kind mismatch test |
| Candidate boundary remains blocked | existing candidate-boundary tests plus regression |
| Exact `product_essence.v1.value` shape | positive exact-shape assertion |
| Table/cell key/value extraction | row_label/key cell fixtures for identity, benchmark, risk |
| No sibling lookup | fixture with label-only cell and unlabelled sibling must not extract sibling value |
| Paragraph fallback | descriptive paragraph fallback fixture |
| Duplicate ambiguity | conflicting duplicate values omitted with `ambiguous_table_or_locator` |
| Missing behavior | proof-positive no-label fixture remains `missing` |
| Partial behavior | only one top-level value yields `partial` with `field_family_partial` |
| Other field families unchanged | assert five other families remain `missing` |
| Default parsed route unchanged | existing default active route tests |
| Non-active explicit FDD unchanged | existing non-active explicit route fail-closed tests |

## Docs Decision

Docs must not be updated before code is accepted. After implementation acceptance, sync only current facts:

- `docs/design.md`: update Fund Processor/Extractor section to say source-truth FDD extraction requires positive admission proof; if Slice B is accepted, only `product_essence.v1` is implemented.
- `fund_agent/fund/README.md`: update Fund package current implementation summary.
- `docs/implementation-control.md` and `docs/current-startup-packet.md`: update gate status and residual ownership.

## Risks / Open Questions

| Risk | Disposition |
|---|---|
| Current FDD content protocol lacks positive proof | Closed by Slice A proof contract before extraction. |
| No accepted live/non-candidate FDD producer may exist yet | Acceptable; implementation tests can use proof-positive fixtures, while production callers without proof fail closed. |
| FDD content protocol lacks page number | Accept `page_number=None`; do not infer unsupported page data. |
| Candidate locators are lexical and not field correctness proof | Do not reuse candidate evidence as public source truth. |
| Over-broad lexical matching may produce false positives | Use exact label map, stable locators, no sibling lookup, and ambiguity fail-closed rules. |
| Six field families are too broad for one slice | Only `product_essence.v1` is in Slice B; others are later work units/slices after review. |
| Public `EvidenceSourceKind` lacks FDD-specific source kind | Use `annual_report`; do not expand source kind in this gate. |

No blocking open question remains for implementation planning after this fix. The implementation order is proof first, extraction second.

## Residual Risks / Owners

| Residual | Owner / Destination |
|---|---|
| Real production FDD producer that can create `FundDisclosureSourceTruthAdmissionProof` | Future Fund documents / repository-mediated producer gate. |
| `return_attribution.v1` FDD source-truth extraction | Future field-family implementation slice after product essence review. |
| `manager_profile.v1` FDD source-truth extraction | Future field-family implementation slice after product essence review. |
| `investor_experience.v1` FDD source-truth extraction | Future field-family implementation slice after product essence review. |
| `current_stage.v1` FDD source-truth extraction | Future field-family implementation slice after product essence review. |
| `core_risk.v1` FDD source-truth extraction | Future field-family implementation slice after product essence review. |
| Non-active fund FDD processors | Future fund-type-specific processor planning gate. |
| Readiness/release | Future explicit readiness/release gate. |

## Completion Report Format

Implementation worker must report:

- changed files;
- exact tests and outputs;
- behavior changes by slice and field family;
- source-truth proof behavior;
- retained fail-closed behavior;
- residual risks and owners;
- confirmation that no Service/UI/Host/renderer/quality-gate consumption was added.
