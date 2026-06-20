# FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Planning Gate

## Gate Metadata

- Work unit: `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction`
- Gate: Planning Gate
- Role: AgentCodex planning worker only
- Classification: `heavy` for this plan, because the implementation will change proof-positive public field-family output and facade-visible bundle projection behavior inside the Fund Processor/Extractor boundary.
- Artifact path: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- Verdict: `PLAN_READY_FOR_REVIEW`
- Plan Fix Gate note: amended after controller acceptance of DS finding 1/2/3 and MiMo finding 004/005; MiMo 001/002/003/006 remain documented scope limitations and do not change this plan.
- Branch / stack note: current local branch is `funddisclosure-investor-experience-source-truth`, HEAD `57c992f70dd6b7c43b799508bd69f37cf1b3cd02`, stacked on PR-31 accepted review head parent `285fac019704519087b7ac528374998e9935ef5f`. This planning gate does not push, create/update PR, mark ready, merge, or mutate PR-31 / remote state.
- Preflight observed: `git branch --show-current` -> `funddisclosure-investor-experience-source-truth`; `git status --short` shows unrelated untracked files only. This plan ignores them and does not stage, delete, classify, or modify them.

## 1. Goal / Motivation / Success Signal

Goal: produce a code-generation-ready implementation plan for exactly one new proof-positive FDD source-truth direct extraction family: `investor_experience.v1`.

Motivation:

- Design truth says proof-positive FDD source-truth direct extraction currently covers `product_essence.v1`, `return_attribution.v1`, and `manager_profile.v1`.
- `investor_experience.v1` currently has S6-E candidate-only locator evidence for investor return, holder structure, share change, subscription/redemption, and income distribution; public field family remains `status="missing"`, `value={}`, `anchors=()`.
- Existing public/bundle shape already has exactly three investor-experience outputs: `investor_return`, `holder_structure`, and `share_change`. The smallest correct step is to emit only those three existing public subvalues from proof-positive FDD content.

Success signal:

- Proof-positive `FundDisclosureDocumentContentIntermediate` with valid `FundDisclosureSourceTruthAdmissionProof`, valid `source_provenance`, `candidate_boundary is None`, and `failure_class is None` can emit `investor_experience.v1` public value with existing top-level keys only, `extraction_mode="direct"` for non-missing output, and public `EvidenceAnchor` entries.
- Missing proof, invalid proof, candidate-boundary input, non-empty `failure_class`, missing `source_provenance`, non-content input, unstable locators, ambiguous/conflicting values, no allowed source value, or content that only matches candidate-only non-public roles fails closed.
- Proof-positive direct route suppresses `investor_experience.v1` candidate evidence, including direct-route missing.
- Proof-missing / proof-invalid route preserves current candidate-only public missing behavior and appends the source-truth admission gap.
- `current_stage.v1` and `core_risk.v1` remain current behavior: no source-truth direct extraction; candidate/missing behavior unchanged.

## 2. Non-goals / Hard Boundaries

- Exactly one field family: `investor_experience.v1`.
- No `current_stage.v1` or `core_risk.v1` implementation.
- No change to `product_essence.v1`, `return_attribution.v1`, or `manager_profile.v1` source-truth semantics.
- No parser replacement, real-report correctness, field correctness, golden/readiness, release, mark-ready, merge, push, or PR mutation.
- No `FundDocumentRepository`, source, fallback, cache, PDF, Docling, pdfplumber, live/network, provider, or LLM work.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion.
- No processor contract/schema expansion unless an existing type already requires local typing; do not add a new public schema.
- No Service/UI/Host/renderer/quality-gate direct consumption of FDD candidate JSON.
- No direct public value for S6-E candidate-only roles `subscription_redemption` or `income_distribution`; they remain candidate locator roles only because no existing public/bundle top-level subvalue exists for them.
- No inference about investor behavior, behavior loss, investor satisfaction, profitability ratio, current stage, risk causality, market timing, or final holding/replacement judgment.
- No unrelated cleanup, residue disposition, commit, push, PR, review, or next gate entry from this planning worker.

## 3. Evidence Read And Alignment

Truth sources:

- `docs/design.md` says only proof-positive, non-candidate-boundary, provenance-valid, failure-free FDD input can produce source-truth public field values; `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain unimplemented for FDD source-truth direct extraction.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` keep candidate evidence as `candidate_only / not_proven / NOT_READY` and do not authorize other field-family parallel implementation, parser replacement, upper-layer candidate consumption, readiness, or release.
- S6-E plan and implementation evidence establish the current investor-experience selector as locator-only, public missing, with roles `investor_return`, `holder_structure`, `share_change`, `subscription_redemption`, and `income_distribution`.
- Current branch HEAD is the stacked local planning branch based on the accepted manager-profile source-truth checkpoint.

Code evidence:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `_field_families_for_intermediate()` currently direct-extracts `product_essence.v1`, `return_attribution.v1`, and `manager_profile.v1` only.
  - `investor_experience.v1` always calls `_select_investor_experience_candidate_evidence()` and then `_candidate_missing_field_family()` when records exist.
  - `_validate_source_truth_admission()` is the only direct-route proof gate and already checks proof type, candidate boundary, failure class, source provenance, and dispatch/intermediate/proof identity equality.
  - `_extract_return_attribution_source_truth()` and `_extract_manager_profile_source_truth()` are the reusable source-truth direct extraction patterns: select values, build public value, build gaps/status, dedupe public anchors, return `candidate_evidence=()`.
  - `_candidate_missing_field_family()` and `_with_source_truth_admission_gap()` preserve proof-missing/candidate-boundary public missing semantics.
- `fund_agent/fund/data_extractor.py`
  - `_active_processor_result_to_bundle()` already projects `investor_experience.v1` to `investor_return`, `holder_structure`, and `share_change`; no production facade code change is expected if the processor emits the existing keys.
- Existing public extractor shapes:
  - `performance._build_investor_return()` uses `investor_return_rate`, `disclosure_status`, and `fallback_status`.
  - `manager_ownership._build_holder_structure()` uses `institutional_holder` and `individual_holder`.
  - `holdings_share_change._extract_share_change()` uses `beginning_share`, `ending_share`, `net_change`, `share_class_column`, and `share_class_selection_reason`.
- `tests/fund/processors/test_fund_disclosure_processor.py` already has source-truth proof guard tests, return/manager direct extraction tests, and investor-experience candidate-only tests.
- `tests/fund/test_data_extractor.py` already has projection scaffolding for `investor_experience.v1` and explicit FDD facade projection tests for return attribution and manager profile.

First-principles judgment:

1. Source truth is a positive admission state plus field-specific extraction proof, not a candidate locator match.
2. The public value must be limited to existing public/bundle keys; otherwise this gate would be a schema/public contract expansion.
3. Candidate roles without existing public shape must stay candidate-only even when direct route is active.
4. The correct implementation surface is a field-family-local direct extractor in `FundDisclosureDocumentProcessor`, plus focused processor and facade regression tests.

## 4. Approved Public Value Shape

`investor_experience.v1.value` may contain only:

- `schema_version`: exactly `"investor_experience.v1"`.
- `investor_return`: existing public/bundle field shape.
- `holder_structure`: existing public/bundle field shape.
- `share_change`: existing public/bundle field shape.

No other top-level keys are allowed. In particular, do not add:

- `subscription_redemption`
- `income_distribution`
- `profitable_investor_ratio`
- `behavior_loss`
- `investor_satisfaction`
- `holder_behavior`
- `dividend_distribution`
- `cash_flow`

Allowed subvalue shapes:

- `investor_return`
  - direct disclosure:
    - `investor_return_rate`: disclosed text value
    - `disclosure_status`: `"direct"`
    - `fallback_status`: `"not_needed"`
  - estimated disclosure:
    - `investor_return_rate`: disclosed text value
    - `disclosure_status`: `"estimated"`
    - `fallback_status`: `"estimated_disclosure_in_section"`
  - Do not emit the existing parsed-annual fallback missing shape inside family `value`; if no proof-positive return value exists, omit top-level `investor_return`.
- `holder_structure`
  - `institutional_holder`: disclosed text value or `None`
  - `individual_holder`: disclosed text value or `None`
  - Emit this top-level subvalue only when at least one side has a stable disclosed value.
- `share_change`
  - `beginning_share`: disclosed text value or `None`
  - `ending_share`: disclosed text value or `None`
  - `net_change`: disclosed text value, safely calculated from beginning/ending when both are parseable, or `None`
  - `share_class_column`: selected column/header text
  - `share_class_selection_reason`: existing reason string, limited to `"single_value_column"` or `"fund_code_header_match"` in this FDD direct slice.
  - Do not add申购/赎回 subkeys. If a table has only申购/赎回 rows but cannot form the existing share-change shape, omit `share_change`.

Family status:

- `accepted`: all three top-level subvalues are emitted and no ambiguity gap remains.
- `partial`: at least one but fewer than three top-level subvalues are emitted, or at least one top-level subvalue was omitted due to ambiguity while another subvalue was emitted.
- `missing`: no approved top-level subvalue is emitted.
- `extraction_mode`: `"direct"` for `accepted` / `partial`, `"missing"` for `missing`.
- `candidate_evidence`: always `()` on proof-positive direct route, including direct-route `missing`.

## 5. Source Selection Rules

Common rules:

- Read only `FundDisclosureDocumentContentIntermediate` protocol fields: `sections`, `paragraph_blocks`, `table_blocks`, and `table_blocks[*].cells`.
- Require stable locators for emitted values. If a block exposes `locator_stability` and it is not `"stable"`, skip it.
- Use existing public `EvidenceAnchor` only:
  - `source_kind="annual_report"`
  - `document_year=context.document_year`
  - `section_id` from source section/table/cell
  - `page_number=None`
  - `table_id` from table/cell when applicable
  - `row_locator` starts with `field={output_path}; ...`
  - `note` is a truncated source value/context preview
- Cell scan order sorts by `(row_index, column_index)` while source path preserves original tuple index.
- Same output path + same normalized value across multiple stable locators: keep first anchor.
- Same output path + conflicting normalized values: omit that output path and add `ambiguous_table_or_locator`.

### 5.1 `investor_return`

Allowed labels:

- direct: `加权平均投资者收益率`, `投资者收益率`, `投资者实际收益`
- estimated: `加权平均投资者收益率（估算）`, `投资者收益率（估算）`, `估算投资者收益率`

Allowed sources:

- Stable paragraph text with explicit label/value pattern.
- Stable table/cell row or column context where label and value are in the same row/cell context.

Selection:

- Require an explicit disclosed value text, preferably a percent literal. Do not derive from NAV, benchmark, holder structure, share change, or external data.
- Paragraph extraction requires a label token plus a valid percent value in the same paragraph block. The value must appear after the label or within the immediate label/value phrase around the label; a label-only paragraph is not enough.
- If the paragraph contains negated or unavailable wording near the matched label, including `未披露`, `未提供`, `无法取得`, `不适用`, or `无`, omit `investor_return` for that paragraph even if the label token matches.
- Table/cell extraction similarly requires the label and value to be in the same row/cell context and must not accept label-only or unavailable cells.
- Direct labels take precedence over estimated labels.
- If direct and estimated both exist with different values, select direct and do not add ambiguity.
- If multiple direct values conflict, omit `investor_return` and add `ambiguous_table_or_locator` with `source_field_path="investor_return"`.
- If multiple estimated values exist and their normalized values conflict, apply the same ambiguity rule as direct conflicts: omit `investor_return` and add `ambiguous_table_or_locator` with `source_field_path="investor_return"`.
- Do not emit盈利投资者占比 or行为损益 as public value in this gate; no existing public/bundle shape exists for them.

### 5.2 `holder_structure`

Allowed labels:

- institutional side: `机构投资者`, `机构投资者持有`, `机构投资者持有比例`, `机构投资者持有份额`
- individual side: `个人投资者`, `个人投资者持有`, `个人投资者持有比例`, `个人投资者持有份额`
- table/section guard: `基金份额持有人信息`, `基金份额持有人结构`, `基金份额持有人情况`, `持有人结构`

Allowed sources:

- Stable paragraph text with explicit institutional/individual label/value pattern.
- Stable table rows under holder-structure table/heading context.

Selection:

- Emit `holder_structure` when at least one side is found.
- Preserve text values as disclosed; do not normalize into ratios or infer missing side.
- If one side is missing, keep that side as `None` and let family status/gaps carry partiality.
- Reject empty or placeholder values before conflict resolution. Invalid holder side values include empty string, whitespace-only text, `无`, `不适用`, `-`, `—`, and `未披露`.
- A rejected placeholder side remains `None`; it must not be emitted as a public value and must not by itself make `holder_structure` present.
- Conflicting values for the same side omit that side and add `ambiguous_table_or_locator` with `source_field_path="holder_structure.institutional_holder"` or `holder_structure.individual_holder`.
- Do not use generic `持有人`, `户数`, or `基金份额` without holder-structure guard context.

### 5.3 `share_change`

Allowed labels:

- beginning: `期初基金份额总额`, `报告期期初基金份额总额`, `期初份额`
- ending: `期末基金份额总额`, `报告期期末基金份额总额`, `期末份额`
- net: `净变动`, `本期申购赎回净额`
- table guard: `基金份额变动`, `份额变动`, `基金份额总额变动`

Allowed sources:

- Stable table rows under a share-change table/heading context.
- Paragraph fallback is not allowed for `share_change` source-truth value in this slice because the existing public value shape depends on a selected share-class/value column.

Selection:

- Determine the value column only by existing public reasons:
  - one non-label value column -> `share_class_selection_reason="single_value_column"`
  - header/path exact current fund code match -> `share_class_selection_reason="fund_code_header_match"`
- Build column header text from the FDD table protocol, not from a non-existent table-level header field:
  - group cells by `column_index`
  - for each column, collect every non-empty string from `cell.column_header_path` in source scan order
  - trim whitespace, drop duplicates while preserving first occurrence, and join the remaining parts with ` / ` to form the column header text
  - if a column has no usable `column_header_path`, use the non-empty cell text from header-like rows only when the implementation can identify those rows from row/column header metadata; otherwise treat the column header as empty
- Exclude label columns before applying value-column selection. A column is a label column when its aggregated header text or stable row-label-like cells are dominated by label tokens such as `项目`, `项目名称`, `份额类别`, `类别`, `基金份额`, `基金份额项目`, `变动项目`, `期初`, `期末`, `申购`, `赎回`, or when the column mostly contains allowed row labels (`期初基金份额总额`, `报告期期初基金份额总额`, `期初份额`, `期末基金份额总额`, `报告期期末基金份额总额`, `期末份额`, `净变动`, `本期申购赎回净额`) instead of numeric values.
- A value column must contain at least one stable beginning/ending/net row value after label-column exclusion. Columns containing only labels, placeholders, or empty cells are not value columns.
- `fund_code_header_match` requires exact match against `context.fund_code` after trimming whitespace and removing internal whitespace from both sides. Substring, prefix, suffix, fuzzy, fund-name, or share-class-name matches are not allowed.
- If multiple value columns cannot be resolved by these rules, omit `share_change` and add `ambiguous_table_or_locator`.
- Fill `beginning_share`, `ending_share`, and `net_change` from the selected value column.
- If `net_change` is absent but beginning/ending are parseable numeric text, calculate `ending - beginning` with `Decimal` arithmetic aligned with the existing `_calculate_net_change` semantics in `holdings_share_change.py`; preserve stable text formatting by using a deterministic decimal string derived from the computed `Decimal` without scientific notation and without adding presentation units. Otherwise `net_change=None`.
- Emit `share_change` only when beginning, ending, or net exists and a stable value column was selected.
-申购/赎回 rows can help identify the table as share-change context, but do not become new public subkeys.

## 6. Candidate Suppression / Proof-missing Semantics

Direct route active:

- In `_field_families_for_intermediate()`, add `investor_experience_source_truth`.
- When `source_truth_extraction_allowed and content_intermediate is not None`, call `_extract_investor_experience_source_truth(...)`.
- If the direct extractor returns a family result, `investor_experience_evidence` must be `()`.
- Direct-route missing due to no allowed public subvalue still returns `candidate_evidence=()`, `status="missing"`, `value={}`, `anchors=()`, and `field_family_missing`.

Proof missing / invalid:

- Do not call the direct extractor.
- Keep `_select_investor_experience_candidate_evidence(intermediate)` exactly as the current S6-E candidate selector.
- If candidate records exist, return `_candidate_missing_field_family("investor_experience.v1", source_provenance, investor_experience_evidence)`.
- `_with_source_truth_admission_gap()` then appends `source_truth_admission_missing` or `source_truth_admission_invalid`, while preserving public `value={}`, `anchors=()`, `status="missing"`, and candidate records.

Candidate boundary / base admission blocked:

- `candidate_boundary is not None` remains blocked by existing admission/proof behavior.
- Candidate evidence may still be present for blocked candidate-boundary input as current tests allow, but it must not produce public value or anchors.

Remaining families:

- `current_stage.v1` and `core_risk.v1` remain unchanged. Their existing candidate selectors may still populate candidate evidence when matching candidate content exists; `investor_experience.v1` direct-route suppression must not clear, suppress, or otherwise alter their candidate evidence. They must not enter source-truth direct extraction.

## 7. Implementation Slices

### Slice 1: Processor direct extractor

Allowed file:

- `fund_agent/fund/processors/fund_disclosure_processor.py`

Required changes:

- Add dataclass:
  - `_InvestorExperienceValueCandidate`
    - `output_path: str`
    - `value: object`
    - `anchor: EvidenceAnchor`
    - `source_field_path: str`
- Add constants:
  - `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL = ("investor_return", "holder_structure", "share_change")`
  - label tuples for investor-return, holder-structure, and share-change source-truth selection; reuse current S6-E token constants only where they are narrower than or equal to this plan.
- Add in `_field_families_for_intermediate()`:
  - local `investor_experience_source_truth: FundFieldFamilyResult | None = None`
  - call `_extract_investor_experience_source_truth()` under the same guard as return/manager
  - suppress `_select_investor_experience_candidate_evidence()` when direct result is present
  - return direct result for `family_id == "investor_experience.v1"` when present
- Add helpers:
  - `_extract_investor_experience_source_truth(intermediate, source_provenance, context) -> FundFieldFamilyResult`
  - `_select_investor_experience_values(intermediate, context) -> tuple[dict[str, _InvestorExperienceValueCandidate], set[str]]`
  - `_select_investor_experience_return(intermediate, context, ambiguous_paths) -> _InvestorExperienceValueCandidate | None`
  - `_select_investor_experience_holder_structure(intermediate, context, ambiguous_paths) -> _InvestorExperienceValueCandidate | None`
  - `_select_investor_experience_share_change(intermediate, context, ambiguous_paths) -> _InvestorExperienceValueCandidate | None`
  - `_build_investor_experience_value(selected_values) -> dict[str, object]`
  - `_investor_experience_emitted_output_paths(value, selected_values) -> tuple[str, ...]`
  - `_investor_experience_source_truth_gaps(value, ambiguous_paths) -> tuple[FundExtractionGap, ...]`
  - `_investor_experience_status(value, ambiguous_paths) -> str`
  - small source-local helpers for cell value/context, anchor construction, duplicate resolution, and share-change column selection.
- Do not refactor accepted S6-B/S6-C/S6-D/S6-E/S6-F/S6-G candidate selector traversal unless a local helper is required and tests prove no behavior change.

Required exact semantics:

- Public non-missing result:
  - `field_family_id="investor_experience.v1"`
  - `chapter_ids=(4,)`
  - `extraction_mode="direct"`
  - `candidate_evidence=()`
  - anchors deduped from emitted output paths only
- Public missing direct-route result:
  - `value={}`
  - `status="missing"`
  - `extraction_mode="missing"`
  - `anchors=()`
  - `candidate_evidence=()`
  - gap `field_family_missing` with `source_boundary="annual_report"`
- Partial result:
  - emit available top-level subvalues only
  - missing required top-level subvalues get `field_family_partial` gaps
  - ambiguity gaps use `ambiguous_table_or_locator`

### Slice 2: Processor tests

Allowed file:

- `tests/fund/processors/test_fund_disclosure_processor.py`

Add focused tests:

- `test_investor_experience_source_truth_route_suppresses_candidate_evidence`
  - proof-positive content contains S6-E candidate match plus no public value; result is direct-route missing with empty candidate evidence.
- `test_investor_experience_source_truth_requires_proof_even_when_candidate_boundary_none`
  - same content without proof keeps candidate-only missing plus `source_truth_admission_missing`.
- `test_investor_experience_source_truth_rejects_base_admission_invalid_paths`
  - missing provenance and non-empty failure class do not emit public value.
- `test_investor_experience_source_truth_candidate_boundary_remains_blocked`
  - candidate boundary blocks direct route and preserves public missing.
- `test_investor_experience_source_truth_extracts_exact_value_shape`
  - proof-positive content emits only `schema_version`, `investor_return`, `holder_structure`, `share_change`; candidate evidence empty; anchors non-empty.
- `test_investor_experience_source_truth_estimated_investor_return_only`
  - proof-positive content with only an estimated investor-return label emits `investor_return.disclosure_status="estimated"` and `fallback_status="estimated_disclosure_in_section"`.
- `test_investor_experience_source_truth_estimated_investor_return_conflict_omits_value`
  - multiple estimated-only investor-return matches with different normalized percent values omit `investor_return` and add `ambiguous_table_or_locator`.
- `test_investor_experience_source_truth_investor_return_paragraph_requires_label_value_pattern`
  - paragraph extraction requires a matched label plus same-paragraph valid percent value after/near the label; label-only text, no-value text, or negated/unavailable wording omits `investor_return`.
- `test_investor_experience_source_truth_holder_structure_filters_placeholder_values`
  - holder side values `无`, `不适用`, `-`, `—`, `未披露`, or empty text remain `None` and no invalid placeholder value is emitted publicly.
- `test_investor_experience_source_truth_partial_when_required_groups_missing`
  - one or two top-level subvalues produce `partial` with `field_family_partial`.
- `test_investor_experience_source_truth_missing_when_no_allowed_public_labels`
  - proof-positive content with only `收益分配` or only `申购赎回` locator content remains direct-route missing; no candidate evidence.
- `test_investor_experience_source_truth_ambiguous_duplicate_omits_conflicting_value`
  - conflicting values for one output path omit that top-level subvalue and add `ambiguous_table_or_locator`.
- `test_investor_experience_source_truth_share_change_excludes_label_column`
  - a share-change table with a label column and one numeric value column excludes the label column and emits values from the value column only.
- `test_investor_experience_source_truth_share_change_selects_single_value_column`
  - a table with exactly one non-label value column emits `share_class_selection_reason="single_value_column"`.
- `test_investor_experience_source_truth_share_change_selects_exact_fund_code_column`
  - a multi-value-column table selects the column whose aggregated `column_header_path` exactly matches `context.fund_code` after whitespace normalization and emits `share_class_selection_reason="fund_code_header_match"`.
- `test_investor_experience_source_truth_share_change_rejects_ambiguous_share_class_columns`
  - multi-column share table without exact fund-code or single-column selection omits `share_change`.
- `test_investor_experience_source_truth_share_change_calculates_net_change`
  - beginning and ending values with absent net row compute `net_change` via Decimal arithmetic aligned with `_calculate_net_change` and emit deterministic decimal text.
- `test_investor_experience_source_truth_does_not_populate_stage_or_risk`
  - proof-positive investor content does not alter `current_stage.v1` or `core_risk.v1` source-truth behavior, and investor direct-route candidate suppression does not clear their existing candidate evidence when matching stage/risk candidate content is present.

Keep existing S6-E candidate-only tests unchanged unless direct-route helper fixtures require local fixture reuse.

### Slice 3: Facade regression tests

Allowed file:

- `tests/fund/test_data_extractor.py`

Decision: add tests, no production facade code expected.

Rationale:

- `_active_processor_result_to_bundle()` already maps `investor_experience.v1` to `investor_return`, `holder_structure`, and `share_change`.
- Existing return/manager FDD facade tests show this route should be regression-protected when a new direct family becomes proof-positive.

Add tests:

- `test_explicit_disclosure_source_truth_investor_experience_projects_to_bundle`
  - proof-positive FDD intermediate with investor_return, holder_structure, and share_change content projects to bundle fields with `extraction_mode="direct"`, non-empty values, and annual-report anchors.
- `test_explicit_disclosure_candidate_only_investor_experience_stays_missing`
  - same content without proof leaves `bundle.investor_return`, `bundle.holder_structure`, and `bundle.share_change` missing with empty anchors.

Do not change facade production code unless tests reveal a projection bug in existing generic family-to-field mapping. If production code changes become necessary, stop and route back to controller because this plan assumes no facade implementation change.

### Slice 4: Docs / evidence sync for future implementation gate

Allowed files after implementation review authorization, not in this planning gate:

- `fund_agent/fund/README.md`
- `docs/design.md`
- future implementation evidence artifact under `docs/reviews/`

Docs decision:

- Update docs only after tests pass.
- State only current code fact: proof-positive `investor_experience.v1` direct extraction covers existing `investor_return`, `holder_structure`, and `share_change` shapes.
- Preserve that `subscription_redemption` and `income_distribution` are not public source-truth subvalues.
- Preserve `current_stage.v1` and `core_risk.v1` as not source-truth implemented.
- Preserve `NOT_READY`, no parser replacement, no real-report correctness, no `EvidenceSourceKind` expansion, and no upper-layer candidate JSON consumption.

## 8. Allowed / Forbidden Files

Current planning gate allowed write set:

- `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`

Current planning gate forbidden write set:

- Every file except the plan artifact above.
- No source, tests, README, design/control docs, existing review artifacts, git index, commit, push, PR, or remote state.

Future implementation gate allowed files, only after plan review/controller authorization:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- one implementation evidence artifact under `docs/reviews/`

Future implementation gate forbidden files/modules:

- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/data_extractor.py` unless facade regression proves existing projection bug and controller explicitly accepts scope change
- `fund_agent/fund/extractors/**`
- `fund_agent/fund/documents/**`
- `fund_agent/services/**`
- `fund_agent/ui/**`
- `fund_agent/host/**`
- `fund_agent/agent/**`
- renderer, quality gate, repository/source/cache/PDF/Docling/pdfplumber/provider/LLM/live/network modules
- PR/control/release artifacts except the explicitly authorized implementation evidence artifact

## 9. Validation Commands For Future Implementation

Focused validation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Facade regression:

```bash
uv run pytest tests/fund/test_data_extractor.py -k "disclosure_source_truth_investor_experience or disclosure_candidate_only_investor_experience"
```

Lint:

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
```

Diff hygiene:

```bash
git diff --check
```

Optional broader processor regression if time budget allows:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
```

Do not run live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference/provider/LLM commands.

## 10. Residual Risks / Open Questions

Residual risks:

- FDD source-truth direct extraction remains no-live fixture-backed unless a later evidence gate authorizes real-report validation; no real-report correctness or readiness claim follows from this plan.
- `investor_return` source labels may differ across reports; this slice intentionally accepts only explicit existing-shape disclosures and otherwise fails closed.
- `share_change` column selection is intentionally narrower than parsed annual extractor behavior because this gate cannot rely on full parsed-report §2 share-class evidence unless it is explicitly present in FDD content and separately reviewed.
- `subscription_redemption` and `income_distribution` may be useful Chapter 4 evidence later, but no public/bundle top-level shape exists now; adding them needs a separate schema/public contract gate.

Blocking open questions:

- None for code generation. The plan is code-generation-ready under the stated boundaries.
