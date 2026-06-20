PLAN_READY_FOR_REVIEW

## Goal / Non-goal / Success Signal

Gate: `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction Planning Gate`.

Goal: implement only the `risk_characteristic_text` source-truth subvalue for `core_risk.v1`, with the smallest public value shape that is already accepted by current processor/bundle contracts.

Mandatory scope statement: this gate only implements `core_risk.v1` risk_characteristic_text. The four other `core_risk.v1` candidate roles, `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, and `concentration_risk`, remain candidate-only/deferred. Complete `core_risk.v1` source truth requires later independent gates.

First-principles judgment: Chapter 6 "core risk" is an analysis output, but this work unit is only a proof-positive disclosure fact extractor. A source-truth extractor may emit directly disclosed facts with public anchors; it must not infer risk severity, pressure-test conclusions, veto status, manager motive, future drawdown, final holding/replacement judgment, or any semantic risk decision.

Success signal:

- Proof-positive FDD content can emit `core_risk.v1` direct public value only when a stable disclosed risk-characteristic text is found.
- Direct public value shape is exactly:
  - `{"schema_version": "core_risk.v1", "risk_characteristic_text": <existing risk_characteristic_text.v1 dict>}`
- `risk_characteristic_text.v1` dict shape must match existing product/profile shape: `schema_version`, `fund_code`, `report_year`, `risk_characteristic_text`, `source_anchors`.
- Direct result has public `EvidenceAnchor(source_kind="annual_report", ...)`, `extraction_mode="direct"` when non-missing, `candidate_evidence=()`, and four contract-compatible deferred-role public gaps with `gap_code="deferred_role"` and `required=False`.
- Direct missing also has `candidate_evidence=()`, `status="missing"`, `value={}`, `anchors=()`, and `field_family_missing`.
- Proof-missing, proof-invalid, candidate-boundary, missing provenance, and failure-class paths remain fail-closed and never emit public values or anchors.
- Candidate selector semantics for `core_risk.v1` and other FDD families remain unchanged outside the proof-positive direct path.

Non-goals:

- No schema expansion in `contracts.py`, `EvidenceSourceKind`, public `EvidenceAnchor`, `StructuredFundDataBundle`, report evidence, template, renderer, Service/UI/Host, quality gate, repository/source/parser, FDR, Docling/pdfplumber/provider/LLM/live/readiness/release.
- No `StructuredFundDataBundle.core_risk` field.
- No direct extraction of `liquidation_status`, `scale_risk`, `tracking_error risk`, `style_drift`, `concentration_risk`, `pressure_test`, `max_drawdown`, `risk_level`, `veto`, or final recommendation.
- No promotion of candidate evidence, excerpts, Chapter 6 reasoning/output words, pressure-test vocabulary, or threshold interpretation into source truth.

## Current Code Facts

- `docs/design.md:5-8` states FDD source-truth direct extraction currently covers `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1`, and `current_stage.v1`; `core_risk.v1` remains unimplemented and candidate-only.
- `docs/design.md:674-678` states proof-positive FDD input is required; direct extraction result `candidate_evidence` is empty; `core_risk.v1` still remains public missing.
- `docs/implementation-control.md:10`, `docs/implementation-control.md:25-51`, and `docs/current-startup-packet.md:23-27` preserve no parser replacement, no upper-layer candidate consumption, no readiness/release, and no `core_risk.v1` implementation authorization outside a later gate.
- `fund_agent/fund/processors/contracts.py:32-39` already includes `core_risk.v1` in `FundFieldFamilyId`; `contracts.py:43-62` already includes proof/candidate gap codes needed for this plan.
- `contracts.py:188-260` defines `FundDisclosureSourceTruthAdmissionProof`; `fund_disclosure_processor.py:1072-1118` validates proof-positive admission and rejects missing/invalid proof, candidate boundary, failure class, and missing provenance.
- `fund_disclosure_processor.py:42-49` family order already includes `core_risk.v1`; `fund_disclosure_processor.py:51-58` maps it to chapter id `(6,)`.
- `fund_disclosure_processor.py:658-727` already defines `core_risk.v1` candidate roles: `risk_characteristic`, `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, and `concentration_risk`.
- `fund_disclosure_processor.py:980-1001` currently runs direct extraction only for the first five source-truth families. `core_risk.v1` is not direct-extracted.
- `fund_disclosure_processor.py:1028-1037` always selects `core_risk.v1` candidate evidence; `fund_disclosure_processor.py:1040-1069` then builds missing/candidate field families or existing direct family results.
- `fund_disclosure_processor.py:4008-4047` builds existing `risk_characteristic_text.v1` public shape inside `product_essence.v1`; `fund_disclosure_processor.py:4154-4172` builds its source anchor ref.
- `fund_agent/fund/processors/active_annual.py:31-35` shows existing `core_risk.v1` parsed-annual mapping includes several fields, but `data_extractor.py:708-755` currently projects only `core_risk.v1.value["risk_characteristic_text"]` as a fallback to `StructuredFundDataBundle.risk_characteristic_text`.
- `data_extractor.py:192-248` defines `StructuredFundDataBundle`; there is no `core_risk` field. `data_extractor.py:720-725` explicitly documents `core_risk.v1 -> only risk_characteristic_text fallback` and `current_stage.v1 -> no projection`.
- `tests/fund/processors/test_fund_disclosure_processor.py:6605-6670` proves current core-risk selector is candidate-only and public missing.
- `tests/fund/processors/test_fund_disclosure_processor.py:6671-7204` proves candidate boundary fields, no-match missing, blocked status, ordering/dedupe/limit, generic guard, cell self-guard, forbidden Chapter 6 output words, and S6-E token suppression.
- `tests/fund/test_data_extractor.py:720-851` and `tests/fund/test_data_extractor.py:880-987` include all-family marker processors; their current core-risk marker has no projected public bundle field except existing fallback behavior.

## Proposed Public Contract And Deferred Items

Gate-scope contract: this gate only admits `core_risk.v1.value["risk_characteristic_text"]` into direct source truth. The four other `core_risk.v1` roles remain candidate-only/deferred and must be visible on accepted direct results only as public gaps, not as public values or anchors.

Allowed public field-family contract:

- `core_risk.v1.value` may contain only:
  - `schema_version="core_risk.v1"`
  - `risk_characteristic_text=<risk_characteristic_text.v1 dict>`
- `risk_characteristic_text.v1` must be produced from directly disclosed FDD risk-characteristic text only, using existing annual-report anchors.
- `core_risk.v1.status`:
  - `accepted` only when `risk_characteristic_text` is emitted and no risk-characteristic ambiguity exists.
  - `missing` when no allowed direct value is emitted.
  - No `partial` in this minimal gate because there is exactly one allowed required subvalue. This binary `accepted | missing` status is a deliberate single-subvalue design; any later gate that adds another accepted source-truth subvalue must revisit `_core_risk_status()`.
- `core_risk.v1.extraction_mode`:
  - `direct` when accepted.
  - `missing` when missing.

Candidate role disposition:

- Promote to source-truth subvalue now:
  - `risk_characteristic`: allowed because it maps to existing `risk_characteristic_text.v1` public/bundle shape, already used by product/profile extractors and Chapter 6 availability.
- Keep candidate-only / deferred:
  - `liquidation_or_scale_risk`: current candidate role locates contract/scale/holder threshold text, but no accepted public subvalue exists for liquidation status or scale-risk status. Parsing threshold text into risk state would be semantic/legal judgment.
  - `tracking_error_or_deviation_risk`: direct tracking error already has existing `return_attribution.v1.tracking_error` ownership. Re-emitting it under `core_risk.v1` is not needed for the current bundle contract and would reopen index applicability / risk-interpretation semantics.
  - `turnover_or_style_drift_risk`: `turnover_rate` is owned by `manager_profile.v1`; style drift requires comparison or judgment. Candidate locator remains useful, but source-truth risk subvalue is deferred.
  - `concentration_risk`: `holdings_snapshot` is owned by `manager_profile.v1` / current-stage input reuse. Concentration risk needs threshold or comparative judgment and is not an accepted public subvalue in this FDD direct gate.

Deferred role public gap semantics:

- Accepted direct `core_risk.v1` results must include one `FundExtractionGap` per deferred role with `gap_code="deferred_role"` and `required=False`.
- Deferred-role gaps must be emitted for `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, and `concentration_risk`.
- These gaps communicate that the family is intentionally incomplete in this gate while remaining contract-compatible with public `accepted` status for the only required subvalue.
- Deferred-role gaps must not carry candidate evidence into the proof-positive direct route.

Facade projection:

- Do not add `StructuredFundDataBundle.core_risk`; it does not exist.
- Existing projection may be used only as currently implemented: if `product_essence.v1` does not provide `risk_characteristic_text` and `core_risk.v1.value["risk_characteristic_text"]` exists, `_active_processor_result_to_bundle()` may fill `StructuredFundDataBundle.risk_characteristic_text` with `note="fallback_from_core_risk.v1"`.
- If product essence already provides `risk_characteristic_text`, it remains the owning projection source and core-risk fallback must not override it.
- No projection for deferred candidate roles.

## Fail-closed Semantics

Proof-positive:

- `admit_disclosure_intermediate()` must pass.
- `source_truth_extraction_allowed` must be true.
- `FundDisclosureDocumentContentIntermediate` must be present.
- `_validate_source_truth_admission()` must return `None`.
- Only then may `_extract_core_risk_source_truth()` run.

Proof-missing:

- Missing `source_truth_admission` keeps public `core_risk.v1` missing and appends `source_truth_admission_missing`.
- Candidate evidence may remain present in this proof-missing path because the route is not direct source truth.

Proof-invalid:

- Mismatched proof identity or invalid proof type keeps public value and anchors empty and appends `source_truth_admission_invalid`.
- Candidate evidence may remain candidate-only; it must not satisfy public field status.

Proof-invalid at base admission:

- `source_provenance=None` or non-null `failure_class` follows current admission behavior and returns blocked/unsupported result before family direct extraction.

Candidate boundary:

- Non-null `candidate_boundary` remains `contract_status="blocked"` and cannot be bypassed by a proof object.
- Candidate evidence may remain present as candidate-only locator evidence, but public `value={}` and `anchors=()` stay unchanged.

Direct route candidate evidence:

- For proof-positive `core_risk.v1`, `candidate_evidence` must be `()` whether the direct extractor finds a value or returns direct missing.
- Reason: once the family is admitted into direct source-truth extraction, mixing candidate locator evidence with a direct result creates a false proof surface. Missing direct proof is a public source-truth extraction miss, not a candidate-only record.

## Implementation Slices

Slice 1: Wire core-risk direct route.

- Allowed file: `fund_agent/fund/processors/fund_disclosure_processor.py`.
- Add `core_risk_source_truth: FundFieldFamilyResult | None = None` in `_field_families_for_intermediate()`.
- When `source_truth_extraction_allowed and content_intermediate is not None`, call `_extract_core_risk_source_truth(content_intermediate, source_provenance, context)`.
- Set `core_risk_evidence = () if core_risk_source_truth is not None else _select_core_risk_candidate_evidence(intermediate)`.
- Extend family selection so `core_risk.v1` uses `core_risk_source_truth` when present.
- Preserve direct branches and candidate-evidence suppression for all previously implemented families.

Slice 2: Implement minimal core-risk direct extractor.

- Allowed file: `fund_agent/fund/processors/fund_disclosure_processor.py`.
- Add `_extract_core_risk_source_truth()`, `_select_core_risk_values()`, `_build_core_risk_value()`, `_core_risk_source_truth_gaps()`, `_core_risk_status()`, and `_core_risk_emitted_output_paths()`.
- Do not call `_select_product_essence_values()` from any `core_risk.v1` code path.
- Extract neutral shared risk-characteristic selector helpers used by both `product_essence.v1` and `core_risk.v1`:
  - `_collect_risk_characteristic_table_candidates(intermediate, context)`;
  - `_collect_risk_characteristic_paragraph_candidates(intermediate, context)`;
  - `_select_risk_characteristic_value(intermediate, context)`.
- The neutral selector helpers must collect only output path `risk_characteristic_text.risk_characteristic_text`; they must not collect product identity, product profile, benchmark, fee, tracking-error, turnover, holdings, holder-structure, or other product-essence values.
- `_select_core_risk_values()` call chain:
  - call only the neutral risk-characteristic collection/selection helpers;
  - return a family-neutral candidate type such as `_RiskCharacteristicValueCandidate`;
  - map ambiguity only for `risk_characteristic_text.risk_characteristic_text` to `core_risk.v1` ambiguity.
- `product_essence.v1` should be refactored to call the same neutral helpers for its existing risk-characteristic subvalue while retaining existing product-essence ownership for all other subvalues.
- Extract a small shared helper from existing product-essence code if needed:
  - `_build_risk_characteristic_text_value(selected_values, context) -> dict[str, object] | None`
  - Product essence and core risk should both call this helper.
  - The helper must produce the exact current shape from `fund_disclosure_processor.py:4040-4046`.
- Do not duplicate or rewrite product identity, benchmark, fee, tracking-error, turnover, holdings, holder-structure, or risk-judgment logic.
- Public anchors for `core_risk.v1` are deduped anchors of emitted `risk_characteristic_text` only.
- `_core_risk_source_truth_gaps()` must add four `required=False` `deferred_role` gaps on accepted direct results and must emit `ambiguous_table_or_locator` when the only required `risk_characteristic_text` path is ambiguous.

Slice 3: Processor tests.

- Allowed file: `tests/fund/processors/test_fund_disclosure_processor.py`.
- Add `_core_risk_source_truth_result()` helper analogous to existing family helpers.
- Required processor tests:
  - Positive: proof-positive risk-characteristic text emits `core_risk.v1` with exact keys `schema_version` and `risk_characteristic_text`; nested `risk_characteristic_text.v1` shape matches existing product/profile shape; anchors are public annual-report anchors; `candidate_evidence == ()`; gaps include exactly four `required=False` `deferred_role` entries for the deferred roles.
  - Direct missing: proof-positive content with no risk-characteristic disclosure returns missing, `value={}`, `anchors=()`, `candidate_evidence=()`, and `field_family_missing`.
  - Ambiguous direct text: proof-positive ambiguous `risk_characteristic_text` returns `status="missing"`, `value={}`, `anchors=()`, `gap_code="ambiguous_table_or_locator"`, and `candidate_evidence=()`.
  - Proof missing: no proof keeps public missing, retains candidate-only evidence if candidate tokens exist, and includes `source_truth_admission_missing`.
  - Proof invalid: mismatched proof keeps public missing/no anchors and includes `source_truth_admission_invalid`.
  - Candidate boundary: non-null `candidate_boundary` remains blocked, public `core_risk.v1` stays missing, candidate evidence remains candidate-only, and deferred role candidate evidence remains present when matching source text exists.
  - Candidate suppression: proof-positive direct route with risk candidate tokens does not include candidate evidence, including when no direct value is accepted.
  - Candidate boundary fields: existing candidate record invariants remain candidate_only / not_proven / not_ready.
  - Forbidden public keys: assert no `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, `concentration_risk`, `pressure_test`, `max_drawdown`, `veto`, `risk_level`, `risk_summary`, or `final_decision` appears in public value.
  - Non-interference: adding core-risk source-truth content does not change `current_stage.v1`, `investor_experience.v1`, `manager_profile.v1`, `return_attribution.v1`, or `product_essence.v1` signatures except where the same risk-characteristic source is already owned by product essence.

Slice 4: Facade projection tests.

- Allowed file: `tests/fund/test_data_extractor.py`.
- No production `data_extractor.py` edit is planned; current fallback already exists.
- This slice is the first activation verification for the existing `data_extractor.py:742-754` `core_risk.v1 -> risk_characteristic_text` fallback path; before this work, the path is effectively dead code because `core_risk.v1` cannot emit an accepted direct value.
- Required facade tests:
  - No `StructuredFundDataBundle.core_risk` attribute exists.
  - When FDD `product_essence.v1` lacks `risk_characteristic_text` but FDD `core_risk.v1` direct emits it, bundle `risk_characteristic_text` uses the existing fallback with `note="fallback_from_core_risk.v1"`.
  - When product essence also emits `risk_characteristic_text`, product essence remains the projection source and core-risk fallback does not override it.
  - Deferred roles do not project to bundle fields.
  - Existing current-stage no-projection behavior remains unchanged.

Slice 5: Docs sync in later implementation gate only.

- Allowed files in later implementation gate: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`.
- This planning gate must not edit those files.
- Docs sync after implementation should state:
  - `core_risk.v1` proof-positive FDD direct extraction exists only for `risk_characteristic_text`.
  - Other core-risk candidate roles remain candidate-only/deferred.
  - Complete `core_risk.v1` source truth remains deferred to later independent gates.
  - Accepted direct `core_risk.v1` results expose four `required=False` `deferred_role` gaps for the deferred roles.
  - Direct `candidate_evidence` is empty, including direct missing.
  - No `StructuredFundDataBundle.core_risk`; only existing `risk_characteristic_text` fallback is allowed.
  - No parser replacement, `EvidenceSourceKind` / `EvidenceAnchor` expansion, Service/UI/Host/renderer/quality-gate consumption, real-report correctness, golden/readiness, or release claim.

## Test Matrix

Processor tests:

| Case | Expected |
|---|---|
| proof-positive risk-characteristic text | `core_risk.v1.status == "accepted"`, `extraction_mode == "direct"`, exact minimal value shape, anchors non-empty, `candidate_evidence == ()` |
| proof-positive accepted deferred gaps | gaps include exactly four `required=False` `deferred_role` entries for `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, and `concentration_risk` |
| proof-positive no allowed direct value | missing, empty value/anchors, `field_family_missing`, `candidate_evidence == ()` |
| proof-positive ambiguous risk-characteristic text | missing, empty value/anchors, `ambiguous_table_or_locator`, `candidate_evidence == ()` |
| proof missing with candidate tokens | missing, empty value/anchors, candidate evidence remains candidate-only, `source_truth_admission_missing` |
| proof invalid | missing, empty value/anchors, `source_truth_admission_invalid` |
| missing provenance | result-level blocked, no direct family extraction |
| failure class | result-level blocked/unsupported per `FAILURE_CLASS_ADMISSION_MAP`, no direct family extraction |
| candidate boundary | `contract_status == "blocked"`, no public value/anchors, candidate evidence remains candidate-only, including deferred role candidate evidence when matching source text exists |
| candidate suppression | proof-positive route never carries `core_risk.v1.candidate_evidence` |
| forbidden keys | no semantic risk keys or deferred role keys in public value |
| non-interference | existing five source-truth families retain current behavior |

Facade tests:

| Case | Expected |
|---|---|
| core-risk fallback only | bundle `risk_characteristic_text` direct/fallback from `core_risk.v1`; no `bundle.core_risk` |
| product essence has risk text | product essence wins; core-risk fallback does not override |
| all-six-family marker processor | bundle ignores `current_stage.v1`; core-risk projects only `risk_characteristic_text` fallback if product risk text missing |
| candidate-only core risk | bundle does not consume candidate evidence |
| first core-risk fallback activation | test documents that `data_extractor.py:742-754` is first exercised by an accepted direct `core_risk.v1` value in this work |

## Validation Matrix

Allowed validation commands for later implementation gate:

- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q`
- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k "product_essence"`
- `uv run pytest tests/fund/test_data_extractor.py -q`
- `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py`
- `git diff --check -- fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md`

Forbidden validation commands:

- Any live/network/PDF/FDR/Docling/pdfplumber/provider/LLM/readiness/release/golden command.
- Any command that mutates PR state, pushes, commits, stages, resets, deletes, or cleans unrelated residue.

## Allowed / Forbidden Files And Modules

Allowed production code file:

- `fund_agent/fund/processors/fund_disclosure_processor.py`

Allowed test files:

- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`

Allowed docs files only in later implementation docs-sync slice:

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `fund_agent/fund/README.md`

Forbidden files/modules:

- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/processors/active_annual.py`
- `fund_agent/fund/data_extractor.py` production code, unless a review finds the existing documented fallback is broken and controller accepts a plan amendment.
- `docs/fund-analysis-template-draft.md`
- `fund_agent/fund/documents/**`, repository/source/cache/parser helpers, candidate document schema/projection, Docling/pdfplumber handlers.
- `fund_agent/services/**`, `fund_agent/ui/**`, `fund_agent/host/**`, `fund_agent/agent/**`, renderer, quality gate, report evidence, template, LLM/provider code.
- Any README or control/design docs during this planning-only gate.

## Residual Risks

- `core_risk.v1` remains a fact extractor, not a Chapter 6 risk analyzer. Owner: future semantic risk-analysis / pressure-test contract gate.
- `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, and `concentration_risk` remain candidate-only/deferred. Owner: future public contract gate if product needs these as structured risk facts.
- The status model is intentionally binary for this single-subvalue gate. Owner: later multi-subvalue `core_risk.v1` gate must redesign `_core_risk_status()` instead of treating current `accepted | missing` behavior as complete-family semantics.
- Existing facade has no `StructuredFundDataBundle.core_risk`; only `risk_characteristic_text` fallback is allowed. Owner: separate schema/public contract gate if a bundle-level core-risk object is needed.
- Direct extraction will not prove real-report correctness, parser replacement, field correctness, golden/readiness, or release. Owner: separate evidence/readiness gates.
- If implementation refactors shared risk-characteristic selector/value construction, reviewers must verify product_essence `risk_characteristic_text` output is byte/shape-compatible with current tests before accepting core-risk behavior. The implementation gate must run the focused `product_essence` validation command in addition to the full processor test file.
- Candidate-boundary behavior deliberately remains candidate-only. Candidate-boundary tests must verify deferred role candidate evidence remains present when matching source text exists, while public value and anchors remain empty.

## Stop Condition Status

This artifact is the only file written in this planning gate.

No code, tests, docs/control sync, validation command, commit, push, PR, review gate, implementation gate, cleanup, or external-state mutation is performed by this worker.
