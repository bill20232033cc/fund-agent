# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Planning Gate

## Gate Metadata

- Work unit: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction`
- Role: planning worker only
- Classification: heavy, because this changes a public field-family output path under the Processor/Extractor boundary.
- Artifact path: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
- Verdict: `PLAN_READY_FOR_REVIEW_NOT_READY`

## Goal / Motivation / Success Signal

Goal: implement exactly one new FDD source-truth direct extraction field family: `return_attribution.v1`.

Motivation: current control truth accepts Source-truth Field Extraction Slice A/B/C and proves only the admission mechanism plus proof-positive `product_essence.v1` direct extraction. `return_attribution.v1` currently has only S6-C candidate locator evidence; public output remains `status="missing"`, `value={}`, `anchors=()`. The next smallest useful step is to reuse the accepted admission proof gate and promote only proof-positive `return_attribution.v1` FDD content into public direct field-family output.

Success signal:

- Proof-positive FDD content with valid `FundDisclosureSourceTruthAdmissionProof`, valid `source_provenance`, `candidate_boundary is None`, and `failure_class is None` can produce `return_attribution.v1` with `extraction_mode="direct"`, non-empty public `value`, and public `EvidenceAnchor` entries.
- Missing/invalid proof, missing source provenance, non-empty failure class, candidate boundary, unstable locators, ambiguous duplicate values, or no allowed source fields all fail closed.
- Candidate-only `return_attribution.v1` behavior stays unchanged when proof is absent or invalid.
- No other field family gains source-truth extraction.
- Release/readiness remains `NOT_READY`.

## Non-goals / Scope Boundary

- Exactly one field family: `return_attribution.v1`.
- Do not implement `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1` source-truth extraction.
- Do not change `product_essence.v1` except for any minimal shared guard reuse required by this slice.
- Do not do parser replacement.
- Do not claim real-report field correctness, full correctness, golden/readiness, release, or production parser replacement.
- Do not change `FundDocumentRepository`, annual-report source policy, fallback policy, cache/PDF behavior, provider behavior, or source acquisition.
- Do not expand `EvidenceSourceKind`, `EvidenceAnchor`, processor contract schemas, candidate schema, or public source provenance schema.
- Do not let Service/UI/Host/renderer/quality gate/LLM prompt directly consume FDD candidate artifacts.
- Do not run live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference/provider/LLM commands.
- Do not touch unrelated dirty/untracked residue.

## Design / Control Alignment

Direct sources read for this plan:

- `AGENTS.md`: Fund document access remains repository-mediated; structured extraction must go through Fund Processor/Extractor; Service/UI/Host/renderer/quality gate must not consume parser/candidate internals directly.
- `docs/design.md` v2.29: Source-truth Slice A/B accepts positive admission proof; only proof-positive `product_essence.v1` is currently implemented; the other five FDD source-truth field families remain missing.
- `docs/implementation-control.md`: active gate is `FundDisclosureDocument Source-truth Field Extraction PR #29 Disposition Accepted`; next entry point is separate future gate only; no other field family/source/readiness transition is authorized without a future gate.
- `docs/current-startup-packet.md`: PR #28/#29 are merged; S6-C `return_attribution.v1` remains candidate evidence only; `candidate_boundary is None` is necessary but insufficient for source truth.
- `fund_agent/fund/README.md`: FDD source-truth direct extraction currently covers only `product_essence.v1`; `return_attribution.v1` remains missing.

Alignment decision:

- This plan opens the authorized separate future planning gate for `return_attribution.v1` only.
- It stays inside Agent/Fund layer `fund_agent/fund/processors/`.
- It reuses `FundDisclosureSourceTruthAdmissionProof`; it does not invent a weaker proof route.
- It preserves candidate-only evidence as internal evidence, not public source truth.

## First-principles Judgment And Direct Code Evidence

First-principles judgment:

1. Source truth is an admission state, not a locator state. `candidate_boundary is None` cannot prove repository-loaded identity, provenance, parser integrity, or failure absence.
2. A public field-family value requires field-specific extraction rules, public anchors, and fail-closed gaps. Candidate locator records are useful for finding possible source fields but cannot satisfy public anchor requirements.
3. The smallest correct implementation is to copy the already accepted pattern for `product_essence.v1`: validate proof once, route the single family to a field-specific source-truth extractor, suppress candidate evidence for that direct family, and leave all other families untouched.

Direct code evidence:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `FundDisclosureDocumentProcessor.extract()` performs supports check, identity check, `admit_disclosure_intermediate()`, source provenance/candidate boundary preservation, source-truth proof validation, field-family construction, contract status derivation, and anchor aggregation.
  - `_validate_source_truth_admission()` returns `source_truth_admission_missing` or `source_truth_admission_invalid`; it requires content intermediate, proof type, `candidate_boundary is None`, `failure_class is None`, non-null `source_provenance`, and dispatch/intermediate/proof identity equality.
  - `_field_families_for_intermediate()` currently only calls `_extract_product_essence_source_truth()` when `source_truth_extraction_allowed` is true; `return_attribution.v1` always uses `_select_return_attribution_candidate_evidence()` and then `_candidate_missing_field_family()`.
  - `_extract_product_essence_source_truth()` shows the accepted direct extraction pattern: select field-specific values, build exact public value shape, derive gaps/status, build public `EvidenceAnchor`, return `candidate_evidence=()`.
  - `_select_return_attribution_candidate_evidence()` and helpers currently only collect S6-C candidate records for roles `nav_benchmark_performance`, `fee_schedule`, and `tracking_error`.
  - `_candidate_missing_field_family()` preserves public `status="missing"`, `value={}`, `anchors=()`, and adds `candidate_only_not_source_truth`.
  - `_missing_field_family()` provides full missing behavior.
  - `_with_source_truth_admission_gap()` appends proof-missing/proof-invalid local gaps while keeping public missing shape.
- `fund_agent/fund/processors/active_annual.py`
  - `FIELD_FAMILY_MAPPINGS` defines existing public `return_attribution.v1` outputs: `nav_benchmark_performance`, `tracking_error`, and `fee_schedule`.
  - `_build_field_family_result()` establishes public family conventions: value contains `schema_version`, direct values, anchors, `field_family_partial` or `field_family_missing` gaps, and status derived from required fields.
- `fund_agent/fund/extractors/profile.py`
  - `_build_fee_schedule()` existing value shape is `{"management_fee": ..., "custody_fee": ...}`.
- `fund_agent/fund/extractors/performance.py`
  - `_build_nav_benchmark_performance()` existing value shape contains `nav_growth_rate` and `benchmark_return_rate`.
  - `_extract_tracking_error()` existing public type is `TrackingErrorValue`, with direct-disclosure provenance semantics.
- `fund_agent/fund/extractors/models.py`
  - `TrackingErrorValue` defines the public structured tracking-error value expected by downstream code.
- `fund_agent/fund/data_extractor.py`
  - `_bundle_from_processor_result()` already maps `return_attribution.v1` value keys to `fee_schedule`, `nav_benchmark_performance`, and `tracking_error`; no facade code change is required if FDD processor emits the existing keys.
- `tests/fund/processors/test_fund_disclosure_processor.py`
  - `test_source_truth_admission_requires_positive_proof`, `test_source_truth_admission_accepts_repository_loaded_identity_proof`, and related tests define source-truth admission guard behavior.
  - `test_product_essence_source_truth_extracts_exact_value_shape` and related tests define the direct extraction test pattern.
  - `test_return_attribution_selector_adds_candidate_evidence_only`, `test_return_attribution_selector_preserves_candidate_boundary_fields`, and `test_return_attribution_selector_preserves_candidate_boundary_blocked_status` prove current S6-C behavior is candidate-only.
- `tests/fund/test_data_extractor.py`
  - `test_explicit_disclosure_intermediate_routes_to_registry()` proves facade route already projects `return_attribution.v1` keys from a disclosure processor result.

## Affected Files / Modules

Implementation slice files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`

Facade regression slice file:

- `tests/fund/test_data_extractor.py`

Docs sync slice files:

- `fund_agent/fund/README.md`
- `docs/design.md`

No planned production changes outside `fund_agent/fund/processors/fund_disclosure_processor.py`.

## Contract / Schema / State-machine / Public-interface Changes

Public output behavior:

- Allowed change: for proof-positive FDD input only, `return_attribution.v1` may change from public `status="missing"`, `extraction_mode="missing"`, `value={}`, `anchors=()` to public `status="accepted"` or `status="partial"`, `extraction_mode="direct"`, non-empty `value`, and non-empty `anchors`.
- Not allowed: proof-missing, proof-invalid, candidate-boundary, failure-class, missing-provenance, non-content, unstable-locator, ambiguous, or no-match paths must not change public shape; they remain missing/blocked/unsupported according to existing admission behavior.

Value shape:

- Use the existing `return_attribution.v1` public family shape from `ActiveFundAnnualProcessor`.
- Top-level keys allowed in FDD direct output:
  - `schema_version`: `"return_attribution.v1"`
  - `nav_benchmark_performance`
  - `fee_schedule`
  - `tracking_error`
- No new public top-level key.
- No candidate-only fields in public `value`.

Anchors:

- Public `anchors` must be tuple of existing `EvidenceAnchor`.
- `source_kind` remains `"annual_report"`.
- `document_year` comes from dispatch context.
- `section_id`, `table_id`, `row_locator`, and `note` come from stable FDD locators.
- `page_number` remains `None` for FDD content when no page-level source-truth mapping exists.

Schemas not changed:

- Do not extend `EvidenceSourceKind`.
- Do not extend `EvidenceAnchor`.
- Do not extend `FundFieldFamilyId`, `FundFieldFamilyResult`, `FundProcessorResult`, `FundDisclosureDocumentContentIntermediate`, or `FundDisclosureSourceTruthAdmissionProof`.
- Do not change source provenance schema.

State machine:

- Existing base admission remains authoritative:
  - `source_provenance=None` => blocked by base admission.
  - non-empty `failure_class` => existing admission map result.
  - `candidate_boundary is not None` => blocked candidate path.
  - invalid dispatch/intermediate identity => blocked/unsupported.
- Existing source-truth guard remains authoritative:
  - proof missing/invalid => no public direct value or anchors.
  - proof valid => direct extractors may run.
- `_derive_contract_status()` remains unchanged:
  - one accepted/partial family plus missing families => processor `contract_status="partial"`.
  - all missing => `missing`.
  - blocked admission => `blocked`.

Upper layers:

- No Service/UI/Host/renderer/quality-gate code change.
- No LLM prompt/template direct consumption of candidate artifacts.
- Existing `FundDataExtractor` projection may receive the new FDD family value via the current processor result mapping; this is not a new upper-layer dependency on FDD candidate internals.

## Implementation Decisions

### Admission / Reuse Guard

- Reuse `source_truth_extraction_allowed` computed in `FundDisclosureDocumentProcessor.extract()`.
- Do not add a second proof mechanism.
- Do not treat `candidate_boundary is None` alone as source-truth proof.
- In `_field_families_for_intermediate()`, compute:
  - `product_essence_source_truth` as today.
  - `return_attribution_source_truth` only when `source_truth_extraction_allowed` and `content_intermediate is not None`.
- If `return_attribution_source_truth` is present, set its candidate evidence to `()`.
- If source-truth proof is missing/invalid, preserve current candidate selector behavior plus `_with_source_truth_admission_gap()`.

### Allowed Field Selection

`return_attribution.v1` direct extraction may use only stable FDD content for the three existing public output keys:

- `nav_benchmark_performance`
  - Allowed source: stable table/cell records.
  - Required facts for this subvalue: `nav_growth_rate` and `benchmark_return_rate`.
  - Matching labels:
    - NAV: `基金份额净值增长率`, `净值增长率`
    - Benchmark: `业绩比较基准收益率`, `基准收益率`
  - Value must contain a parseable percent literal.
  - Prefer same table and same `row_index` pair; if no unique pair exists, omit the subvalue and add a local gap.
  - Do not infer from benchmark name or standard deviation columns.
- `fee_schedule`
  - Allowed source: stable table/cell records, with paragraph fallback only for explicit `管理费率：...` / `托管费率：...` labeled text.
  - Allowed subkeys: `management_fee`, `custody_fee`.
  - Matching labels:
    - `management_fee`: `基金管理费`, `管理费率`, `管理费`
    - `custody_fee`: `基金托管费`, `托管费率`, `托管费`
  - Sales service fee remains candidate-only unless a later gate adds it to public mapping; current active annual public shape does not include it.
  - Value must contain explicit rate text, preferably percent literal or stable annual-rate text.
- `tracking_error`
  - Allowed source: stable table/cell records or explicit paragraph text with actual tracking-error disclosure.
  - Matching labels: `跟踪误差`, `年化跟踪误差`, `日均跟踪偏离度`, `日均偏离度`.
  - Must contain a parseable percent literal.
  - Must reject target/limit/planned/control-only context such as `目标`, `控制`, `不超过`, `力争`, `偏离度绝对值`.
  - Public value must be existing `TrackingErrorValue`, not a bare string.
  - Use direct-disclosure semantics:
    - `value`: Decimal ratio parsed from percent text.
    - `value_text`: percent text as disclosed.
    - `unit`: `"ratio"`.
    - `period_label`: row/heading/table context when available; fallback to `"annual_report_period"`.
    - `annualized`: true when text/label contains `年化`; otherwise false.
    - `source_type`: `"direct_disclosure"`.
    - `calculation_method`: `"disclosed"`.
    - `benchmark_identity_status`: `"missing"`.
    - `frequency`: `"annual_report_period"`.
    - provenance note: direct annual-report disclosure; no benchmark-return/stddev derivation.

### Value / Status / Gaps

- Add `_extract_return_attribution_source_truth()` parallel to `_extract_product_essence_source_truth()`.
- Add field-specific candidate/value helpers instead of generalizing all field families.
- Build value with `schema_version="return_attribution.v1"`.
- Status:
  - `accepted` if all three subvalues are present.
  - `partial` if at least one allowed subvalue is present.
  - `missing` if no allowed subvalue is present.
- Extraction mode:
  - `direct` for `accepted` or `partial`.
  - `missing` for `missing`.
- Gaps:
  - `field_family_missing` if no allowed public subvalue is formed.
  - `field_family_partial` for each missing required subvalue when at least one subvalue is present.
  - `ambiguous_table_or_locator` for duplicate/conflicting stable values.
- Result-level gaps remain empty for field-local missing/partial behavior.
- Public anchors include only emitted public subvalues, deduped by existing `_dedupe_anchors()`.

### Fail-closed Rules

- Skip unstable table/cell/paragraph locator.
- Skip cells whose value is just the label itself or generic header text.
- Omit a subvalue when multiple stable candidates for the same output path conflict.
- Omit `nav_benchmark_performance` unless both NAV and benchmark values are found in a unique same-row pair.
- Omit `tracking_error` when context is target/control/limit/benchmark-only/standard-deviation-only or the percent cannot be parsed.
- Never use S6-C candidate evidence as public value.
- Never add candidate evidence to a direct source-truth family.
- Never consume raw candidate JSON/Markdown/Docling/pdfplumber artifacts in implementation or tests.

## Implementation Slices

### Slice 1: Admission/reuse guard

- Objective: let `return_attribution.v1` enter direct extraction only through the existing source-truth proof guard.
- Allowed files/modules:
  - `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `tests/fund/processors/test_fund_disclosure_processor.py`
- Exact changes:
  - In `_field_families_for_intermediate()`, add local `return_attribution_source_truth: FundFieldFamilyResult | None`.
  - When `source_truth_extraction_allowed and content_intermediate is not None`, call `_extract_return_attribution_source_truth(content_intermediate, source_provenance, context)`.
  - Set `return_attribution_evidence = ()` when direct result is present; otherwise call `_select_return_attribution_candidate_evidence(intermediate)`.
  - In field-family tuple construction, return `return_attribution_source_truth` only for `family_id == "return_attribution.v1"` and non-None.
  - Keep `_with_source_truth_admission_gap()` applied to all families when `source_truth_gap_code` is non-None.
- Functions/classes/types:
  - `_field_families_for_intermediate`
  - new `_extract_return_attribution_source_truth`
  - existing `FundFieldFamilyResult`
- Data flow:
  - `extract()` -> base admission -> `_validate_source_truth_admission()` -> `_field_families_for_intermediate()` -> direct extractor or candidate selector.
- Error handling:
  - No exceptions for missing fields.
  - Existing base admission remains the only path for missing provenance/failure class/candidate boundary.
- Invariants:
  - Proof missing/invalid means no public `return_attribution.v1` value or anchors.
  - Direct family has `candidate_evidence=()`.
  - Other families stay unchanged.
- Non-goals:
  - No source-truth guard changes.
  - No contract schema changes.
- Tests:
  - Add `test_return_attribution_source_truth_requires_proof_even_when_candidate_boundary_none()`.
  - Add `test_return_attribution_source_truth_rejects_failure_class_at_base_admission()` if existing product test coverage is not enough to assert family-specific absence.
- Completion signal:
  - Proof-positive route reaches new direct extractor; proof-missing route keeps public missing and candidate evidence.
- Stop condition:
  - If this requires weakening `_validate_source_truth_admission()`, stop and return to plan review.

### Slice 2: Value extraction

- Objective: construct public `return_attribution.v1.value` from proof-positive FDD content.
- Allowed files/modules:
  - `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `tests/fund/processors/test_fund_disclosure_processor.py`
- Exact changes:
  - Add `_ReturnAttributionValueCandidate` dataclass with `output_path`, `value`, `anchor`, `source_field_path`, and optional `period_label`.
  - Add constants for allowed labels and required output fields:
    - `_RETURN_ATTRIBUTION_REQUIRED_TOP_LEVEL = ("nav_benchmark_performance", "fee_schedule", "tracking_error")`
    - `_RETURN_ATTRIBUTION_NAV_LABELS`
    - `_RETURN_ATTRIBUTION_BENCHMARK_LABELS`
    - `_RETURN_ATTRIBUTION_FEE_LABELS`
    - `_RETURN_ATTRIBUTION_TRACKING_ERROR_LABELS`
    - `_RETURN_ATTRIBUTION_GENERIC_CELL_TEXTS`
  - Add helpers:
    - `_select_return_attribution_values()`
    - `_collect_return_attribution_table_value_candidates()`
    - `_collect_return_attribution_paragraph_value_candidates()`
    - `_build_return_attribution_value()`
    - `_build_return_attribution_nav_benchmark_value()`
    - `_build_return_attribution_fee_schedule_value()`
    - `_build_return_attribution_tracking_error_value()`
    - `_return_attribution_emitted_output_paths()`
    - `_return_attribution_status()`
  - Use `TrackingErrorValue` from `fund_agent.fund.extractors.models` for `tracking_error`.
  - Use local percent parsing helpers if needed; keep them private and field-specific.
- Data flow:
  - Stable FDD cells/paragraphs -> value candidates -> conflict resolution -> exact public value -> anchors/gaps/status.
- Error handling:
  - Non-parseable percentages produce missing/partial gap, not exception.
  - Duplicate conflicting candidates produce `ambiguous_table_or_locator` and omit that output path.
- Invariants:
  - Public value has only `schema_version`, `nav_benchmark_performance`, `fee_schedule`, `tracking_error`.
  - `fee_schedule` only contains existing public subkeys `management_fee` and `custody_fee`.
  - `tracking_error` is `TrackingErrorValue`.
  - No derived computation from NAV/benchmark return into tracking error.
- Non-goals:
  - No investor return extraction.
  - No fee expansion to sales service fee.
  - No cross-year or NAV-series computation.
- Tests:
  - `test_return_attribution_source_truth_extracts_exact_value_shape()`: synthetic proof-positive content yields direct value with all three subvalues, public anchors, and `candidate_evidence == ()`.
  - `test_return_attribution_source_truth_partial_when_required_groups_missing()`: only fee/nav/tracking subset yields `partial` plus `field_family_partial`.
  - `test_return_attribution_source_truth_missing_keeps_family_missing()`: no allowed labels yields `missing`, `{}`, `()`, `candidate_evidence == ()`.
- Completion signal:
  - Focused processor tests prove accepted/partial/missing direct extraction behavior.
- Stop condition:
  - If existing FDD protocols lack enough stable fields to identify values without sibling inference, omit the affected subvalue and document residual rather than broadening protocol/schema.

### Slice 3: Anchor/gap behavior

- Objective: make public anchors and local gaps precise and fail-closed.
- Allowed files/modules:
  - `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `tests/fund/processors/test_fund_disclosure_processor.py`
- Exact changes:
  - Add `_return_attribution_cell_anchor()` and `_return_attribution_paragraph_anchor()` or a single field-specific anchor helper.
  - Row locators must include `field=<public_path>` and stable locator identity:
    - table/cell: `field=...; table_id=...; row=...; column=...; cell_id=...`
    - paragraph: `field=...; block_id=...`
  - Add `_return_attribution_source_truth_gaps(value, ambiguous_paths)`.
  - Deduplicate anchors with existing `_dedupe_anchors()`.
- Error handling:
  - Missing required groups become field-family local gaps.
  - Ambiguous duplicate candidate paths become local `ambiguous_table_or_locator` gaps.
- Invariants:
  - Non-missing family must have public anchors because `FundFieldFamilyResult.__post_init__()` enforces it.
  - Missing family must have local gaps.
  - Result-level gaps stay reserved for cross-family/admission failures.
- Non-goals:
  - No new `EvidenceAnchor` fields.
  - No source kind expansion.
- Tests:
  - `test_return_attribution_source_truth_ambiguous_duplicate_omits_conflicting_path()`.
  - `test_return_attribution_source_truth_skips_unstable_table_or_cell_locator()`.
  - `test_return_attribution_source_truth_rejects_tracking_error_target_or_limit_context()`.
  - Assert every public anchor uses `source_kind == "annual_report"`.
- Completion signal:
  - Ambiguity, instability, target-only tracking error, and no-match cases all fail closed.
- Stop condition:
  - If a planned anchor would require extending `EvidenceAnchor`, do not implement; keep the field missing and record residual.

### Slice 4: Facade/test/docs sync

- Objective: prove existing facade projection handles the new FDD `return_attribution.v1` direct output, then sync current facts in docs.
- Allowed files/modules:
  - `tests/fund/processors/test_fund_disclosure_processor.py`
  - `tests/fund/test_data_extractor.py`
  - `fund_agent/fund/README.md`
  - `docs/design.md`
- Exact changes:
  - Add/adjust processor tests in `tests/fund/processors/test_fund_disclosure_processor.py`.
  - Add a focused facade regression in `tests/fund/test_data_extractor.py` only if processor tests do not already prove bundle projection:
    - use existing explicit disclosure route fixture pattern.
    - assert FDD processor direct `return_attribution.v1` maps to `bundle.fee_schedule` and `bundle.nav_benchmark_performance`.
    - for active fund tracking error projection, assert current `_tracking_error_for_fund_type()` behavior explicitly; do not change it unless a failing test proves a boundary mismatch.
  - Update `fund_agent/fund/README.md` to say FDD source-truth direct extraction covers proof-positive `product_essence.v1` and `return_attribution.v1`; other four families remain missing.
  - Update `docs/design.md` current-state wording similarly after tests pass.
- Data flow:
  - FDD processor result -> existing `_bundle_from_processor_result()` -> `StructuredFundDataBundle` fields.
- Error handling:
  - If facade projection already handles marker values, no production facade code change is allowed.
  - If `tracking_error` active-fund post-processing intentionally marks non-index tracking error missing, record it as current facade behavior, not as a processor bug.
- Invariants:
  - Docs describe implemented code fact only after implementation tests pass.
  - Docs must preserve NOT_READY and no parser replacement wording.
- Non-goals:
  - No Service/UI/Host/renderer/quality-gate change.
  - No README/design update in this planning-only gate.
- Completion signal:
  - Focused tests pass and docs truth sync reflects exactly the implemented scope.
- Stop condition:
  - If docs would need to claim real-report correctness/readiness/source policy changes, stop and return to controller.

## Tests / Validation Commands And Expected Assertions

Required focused validation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Expected assertions:

- Existing source-truth admission tests still pass.
- Existing S6-C candidate-only tests still pass for proof-missing/invalid paths.
- New proof-positive `return_attribution.v1` tests prove direct public value and anchors.
- New negative tests prove fail-closed missing/partial/ambiguous/unstable/target-only behavior.

Facade regression if Slice 4 changes `tests/fund/test_data_extractor.py`:

```bash
uv run pytest tests/fund/test_data_extractor.py
```

Expected assertions:

- Explicit disclosure route still resolves `fund_disclosure_document.v1`.
- Existing projection maps `return_attribution.v1` keys without new facade code.
- No default production path begins parsing FDD when `disclosure_intermediate=None`.

Lint:

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
```

Expected assertion: ruff passes.

Whitespace/check:

```bash
git diff --check
```

Expected assertion: no whitespace errors.

Forbidden validation:

- No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference/provider/LLM commands.
- No release/readiness/golden promotion commands.

## Docs Decision

This plan does not modify docs outside this artifact.

Future implementation/docs slice must update:

- `fund_agent/fund/README.md`, because `fund_agent/fund/processors/fund_disclosure_processor.py` changes current Fund package behavior.
- `docs/design.md`, because current design truth must no longer say only `product_essence.v1` has FDD source-truth direct extraction after implementation is accepted.

Future docs wording must explicitly preserve:

- `return_attribution.v1` is implemented only for proof-positive FDD content.
- The other four FDD source-truth field families remain missing.
- Candidate evidence remains candidate_only / not_proven / NOT_READY.
- No parser replacement, EvidenceAnchor/EvidenceSourceKind expansion, Service/UI/Host/renderer/quality-gate consumption, golden/readiness, release, or real-report correctness claim.

## Risks / Open Questions / Residual Owner

Risks:

- FDD content protocols may not contain enough sibling/header information to safely extract all three `return_attribution.v1` subvalues. Owner: implementation worker; mitigation: emit partial/missing with local gaps, do not broaden schema in this gate.
- Tracking error direct disclosure is easy to confuse with target/control/benchmark-only text. Owner: implementation worker; mitigation: require percent plus actual-disclosure context and reject target/control/limit contexts.
- Downstream active-fund facade currently may treat `tracking_error` differently by fund type. Owner: implementation worker; mitigation: add facade test only for current projection behavior; do not change facade unless a direct boundary bug is proven.
- Docs may be over-updated to imply field correctness/readiness. Owner: docs sync worker; mitigation: update only current implemented scope and preserve NOT_READY.

Open questions:

- None blocking for plan review. The implementation can fail closed for any uncertain locator/value shape without new user decision.

Residual owner:

- Future gates own `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` source-truth extraction.
- Future evidence gates own real-report field correctness and readiness.
- Future architecture/source gates own parser replacement, source policy changes, and schema expansion.

## Completion Report Format

Implementation worker final report should include:

- Changed files.
- Slice(s) completed.
- Behavior summary for proof-positive and proof-missing paths.
- Tests/validation commands and results.
- Docs updated or explicitly deferred.
- Residual risks with owner.
- Verdict token: `IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY` or `IMPLEMENTATION_BLOCKED_NOT_READY`.

## Why This Is Not Over-designed

- It implements exactly one field family and reuses the existing admission proof, processor result, field-family, gap, and anchor contracts.
- It does not add a generic extraction framework for all remaining field families.
- It does not add schema fields, source kinds, repository behavior, parser routes, or upper-layer consumption.
- It uses field-specific helpers because `return_attribution.v1` has distinct numeric/rate/tracking-error fail-closed rules; a shared abstraction would hide the source-truth risk instead of reducing real duplication.
- It accepts partial/missing outcomes instead of forcing completeness from uncertain FDD locators.
- It leaves real-report correctness, readiness, and remaining families to separate gates.
