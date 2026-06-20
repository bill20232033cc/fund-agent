# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Planning Gate

## Gate Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Role: AgentCodex planning worker only
- Classification: `standard` feature slice inside Fund layer Processor/Extractor boundary
- Artifact path: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- Verdict: `CODE_GENERATION_READY`
- Preflight observed in this planning pass:
  - `git branch --show-current` -> `funddisclosure-return-attribution-source-truth`
  - `git status --short` shows unrelated untracked files only; this plan ignores them and does not stage, modify, delete, or classify them.

## 1. Goal / Motivation / Success Signal

Goal: implement exactly one new proof-positive FDD source-truth direct extraction field family: `manager_profile.v1`.

Motivation: design/control truth says `product_essence.v1` and `return_attribution.v1` already have proof-positive FDD source-truth direct extraction, while `manager_profile.v1` remains public `missing`. S6-D accepted only candidate-only locator evidence for manager roster, strategy/outlook, turnover, manager/employee holding, and holdings snapshot; it did not prove source truth or field correctness.

Success signal:

- Proof-positive `FundDisclosureDocumentContentIntermediate` with valid `FundDisclosureSourceTruthAdmissionProof`, valid `source_provenance`, `candidate_boundary is None`, and `failure_class is None` can emit `manager_profile.v1` public field-family output with `extraction_mode="direct"`, non-empty existing-shape public `value`, and public `EvidenceAnchor` entries.
- Missing proof, invalid proof, candidate-boundary input, non-empty `failure_class`, missing `source_provenance`, non-content input, ambiguous/conflicting locator values, unstable locators, candidate-only evidence, or no allowed source field fails closed to public `status="missing"`, `value={}`, `anchors=()` or field-local `partial` only when at least one allowed subvalue is proven.
- No field family other than `manager_profile.v1` changes behavior.
- Candidate evidence remains `candidate_only / not_proven / NOT_READY`.
- No parser replacement, real-report correctness, golden/readiness, release, or repository/source behavior claim is made.

## 2. Non-goals / Scope Boundary

- Exactly one family: `manager_profile.v1`.
- Do not implement source-truth extraction for `investor_experience.v1`, `current_stage.v1`, `core_risk.v1`, or any other family.
- Do not change `product_essence.v1` or `return_attribution.v1` direct extraction semantics.
- Do not change S6-D candidate selector semantics except suppressing `manager_profile.v1` candidate evidence on proof-positive direct route.
- Do not consume S6-D candidate evidence as source truth.
- Do not expand `EvidenceSourceKind`, public `EvidenceAnchor`, processor contracts, source provenance schema, repository/source policy, fallback behavior, cache/PDF behavior, provider/LLM behavior, Service/UI/Host/renderer/quality-gate behavior, or LLM prompt/template direct consumption.
- Do not run live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM commands.
- Do not claim Chapter 3 manager quality, consistency, motivation, current-stage judgment, risk causality, investor experience, field correctness, full coverage, parser replacement, readiness, or release.
- Do not modify control docs, PR state, branch state, git index, or unrelated untracked residue.

## 3. Design / Control / Code Evidence

Direct evidence read:

- `AGENTS.md:27-32` defines required read order; `AGENTS.md:75-80` requires repository-mediated document access and Fund Processor/Extractor boundary; `AGENTS.md:91-141` fixes `UI -> Service -> Host -> Agent` boundaries; `AGENTS.md:147-162` requires Chinese docstrings, flat helper functions, and maintainable boundaries.
- `docs/design.md:5-8` states S6-D is candidate-only and current source-truth direct extraction covers only `product_essence.v1` and `return_attribution.v1`; `manager_profile.v1` remains unimplemented. `docs/design.md:660-678` states FDD is Processor/Extractor input, candidate evidence is not source truth, proof-positive admission is required, and other FDD source-truth families remain future independent gates.
- `docs/implementation-control.md:10` and `docs/implementation-control.md:50-53` set the current next entry point to `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Planning Gate` and forbid other families, parser replacement, upper-layer consumption, readiness, or release.
- `docs/current-startup-packet.md:22-28` and `docs/current-startup-packet.md:63` repeat that PR #30 is merged, next entry is `manager_profile.v1`, and remaining families are not proven.
- S6-D plan `docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-plan-20260619.md` defines accepted candidate locator roles, ordering, dedupe, guard, and public-missing semantics.
- S6-D evidence `docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-implementation-evidence-20260619.md` proves current selector behavior: candidate records only in `candidate_evidence`; public `status="missing"`, `value={}`, `anchors=()`; `not_proven` and `NOT_READY` preserved.
- Return-attribution source-truth plan `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md` and controller judgment `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-controller-judgment-20260620.md` establish the reusable direct extraction pattern: proof-positive guard, single family, no schema expansion, existing public value shape, direct anchors, fail-closed ambiguity, candidate suppression on direct route.
- `fund_agent/fund/processors/fund_disclosure_processor.py:737-818` currently routes only `product_essence.v1` and `return_attribution.v1` into direct extraction when `source_truth_extraction_allowed`; `manager_profile.v1` always uses `_select_manager_profile_candidate_evidence()`.
- `fund_agent/fund/processors/fund_disclosure_processor.py:821-850` validates proof type, `candidate_boundary`, `failure_class`, `source_provenance`, and dispatch identity before source-truth direct extraction.
- `fund_agent/fund/processors/fund_disclosure_processor.py:910-937` shows the accepted direct extractor shape for `return_attribution.v1`: select values, build value, build gaps/status, dedupe anchors, return `candidate_evidence=()`.
- `fund_agent/fund/processors/fund_disclosure_processor.py:3151-3520` contains S6-D `manager_profile.v1` candidate-only selector and guard context rules.
- `fund_agent/fund/processors/active_annual.py:113-137` defines existing `manager_profile.v1` public top-level fields: `portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, `holdings_snapshot`.
- `fund_agent/fund/data_extractor.py:708-793` already projects `manager_profile.v1` from processor result into `StructuredFundDataBundle` fields; no facade production code change is needed if FDD processor emits those existing keys.
- `fund_agent/fund/extractors/models.py:641-668` documents current manager and holdings extracted fields as `ExtractedField[dict[str, object]]`.
- `tests/fund/processors/test_fund_disclosure_processor.py` already has source-truth proof guard tests, product/return direct extraction tests, S6-D candidate-only tests, and candidate-boundary fail-closed tests.
- `tests/fund/test_data_extractor.py` already has generic processor-to-bundle projection coverage for `manager_profile.v1` and explicit FDD facade route coverage.

First-principles judgment:

1. Source truth is a positive admission state, not a locator match. `candidate_boundary is None` and S6-D candidate records are insufficient.
2. `manager_profile.v1` can be implemented without contract expansion because existing public fields and `StructuredFundDataBundle` projection already exist.
3. The smallest correct slice is a field-family-local direct extractor inside `FundDisclosureDocumentProcessor`, using only current FDD content protocol fields and existing public value shapes.

## 4. Exact Public Value Shape

`manager_profile.v1` direct output may contain only these top-level keys:

- `schema_version`: exactly `"manager_profile.v1"`.
- `portfolio_managers`: existing portfolio-manager tenure-list shape.
- `manager_strategy_text`: existing strategy/outlook dict shape.
- `turnover_rate`: existing turnover dict shape.
- `manager_alignment`: existing manager/employee holding dict shape.
- `holdings_snapshot`: existing holdings snapshot dict shape.

Do not add new top-level keys. Do not include candidate metadata in public `value`.

Allowed subkeys in this gate:

- `portfolio_managers`
  - Shape:
    - `schema_version`: `"portfolio_manager_tenure_list.v1"`
    - `fund_code`: context fund code
    - `report_year`: context document year
    - `portfolio_managers`: list of manager entries
  - Entry shape:
    - `name`: disclosed manager name
    - `role`: disclosed role, must include or normalize to `基金经理`
    - `start_date`: disclosed start date text when present
    - `end_date`: disclosed end date text only when present and non-empty
    - `source_anchor`: dict with `section_id`, `section_title`, `page_number=None`, `table_id`, `row_locator="portfolio_manager:<name>"`
  - Deferred: resume, education, securities experience years, prior employers, manager quality, tenure calculation, current/on-duty judgment beyond disclosed date fields.
- `manager_strategy_text`
  - Shape: `{"strategy_summary": str | None, "market_outlook": str | None}`
  - Emit when at least one of the two subkeys is non-empty.
  - Deferred: style classification, consistency judgment, market forecast validity, current-stage implication.
- `turnover_rate`
  - Shape: `{"turnover_rate": str, "turnover_basis": str | None}`
  - Emit only when an actual disclosed turnover percentage is found.
  - Deferred: turnover quality judgment, risk classification, historical comparison, regulatory applicability, candidate/golden correctness.
- `manager_alignment`
  - Shape: `{"manager_holding": str | None, "employee_holding": str | None, "judgment": None}`
  - Emit when at least one disclosed manager or employee holding value/range is found.
  - `judgment` must remain `None`; no motivation or利益一致性 inference in this gate.
- `holdings_snapshot`
  - Shape may include only:
    - `top_holdings`: list[dict[str, str]] | None
    - `top_holdings_status`: `"direct_top_ten"` or `"missing"`
    - `top_holdings_source`: `"top_ten"` or `"none"`
    - `industry_distribution`: list[dict[str, str]] | None
    - `industry_distribution_status`: `"direct"` or `"missing"`
  - Row dict keys preserve disclosed Chinese column headers from FDD table cells.
  - Deferred: holding concentration judgment, style drift, core risk use, current-stage use, all-stock-details fallback, target-fund holdings, bond holdings, QDII/FOF-specific holdings.

Status rules:

- `accepted`: all five top-level subvalues are emitted.
- `partial`: at least one but fewer than five top-level subvalues are emitted.
- `missing`: no allowed subvalue is emitted.
- `extraction_mode`: `"direct"` for `accepted`/`partial`, `"missing"` for `missing`.
- `candidate_evidence`: always `()` on proof-positive direct route, including direct-route missing.

## 5. Source Selection Rules

All source selection must read only current `FundDisclosureDocumentContentIntermediate` protocol fields:

- `sections`
- `paragraph_blocks`
- `table_blocks`
- `table_blocks[*].cells`

All emitted values require stable source locators:

- Section/table/paragraph/cell `locator_stability` must be `"stable"` if present.
- Table and cell values must preserve `source_field_path` formats already used by S6-D:
  - `sections[{section_index}]`
  - `paragraph_blocks[{paragraph_index}]`
  - `table_blocks[{table_index}]`
  - `table_blocks[{table_index}].cells[{cell_index}]`
- Cell scan order sorts by `(row_index, column_index)` while `source_field_path` preserves the original tuple index.

### 5.1 Manager Roster / `portfolio_managers`

Allowed source:

- Stable table rows under table/section/heading path containing `基金经理简介`, `基金管理人及基金经理情况`, `基金经理情况`, or `主要人员情况`.
- Stable cells with column/header/row context for `姓名`, `职务`, `任职日期`, `任职时间`, `聘任日期`, `起始日期`, `离任日期`, `离任时间`, or `终止日期`, but generic header tokens must retain S6-D source-level guard context containing `基金经理` or `管理人`.

Selection:

- Group cells by `(table_index, row_index)`.
- Header resolution uses `column_header_path`, `row_label_path`, and nearby table heading/caption/path; do not infer columns by position alone unless header text is present in the same row/header path.
- A manager entry requires a non-empty `name` and a row/role context containing `基金经理`; `start_date` is optional but, when absent, the field still emits only if `name` and role are stable.
- If a row has no manager name or only generic headers, skip it.
- Same manager row repeated with identical entry value: keep first locator.
- Same manager name with conflicting role/date values: omit that entry and add `ambiguous_table_or_locator` for `portfolio_managers`.

### 5.2 Strategy / Manager Commentary / `manager_strategy_text`

Allowed source:

- Stable paragraph blocks whose `heading_path`, `text_normalized`, or `text_raw` is under:
  - `报告期内基金投资策略和运作分析`
  - `投资策略和运作分析`
  - `投资策略`
  - `运作分析`
  - `管理人对宏观经济、证券市场及行业走势的简要展望`
  - `后市展望`
  - `市场展望`

Selection:

- `strategy_summary`: concatenate stable paragraph texts under strategy/operation headings in document order.
- `market_outlook`: concatenate stable paragraph texts under outlook headings in document order.
- Skip table/cell strategy candidate records for source-truth value; those remain locator evidence only when proof is missing.
- Do not parse or classify style, market prediction, manager skill, or current-stage impact.
- If the same subkey has multiple identical paragraph groups, keep first; if two disjoint groups conflict by heading lineage or duplicate heading reset, omit the subkey and add `ambiguous_table_or_locator`.

### 5.3 Turnover / `turnover_rate`

Allowed source:

- Stable table/cell rows or explicit paragraphs containing `换手率`, `股票换手率`, `报告期内股票换手率`, `换手率口径`, or `换手率计算口径`.

Selection:

- `turnover_rate` requires a parseable disclosed percent literal from a row/paragraph whose label/context contains turnover-rate tokens.
- `turnover_basis` may be filled from explicit basis/口径 text in the same row/table/paragraph context.
- Basis-only disclosure must not emit `turnover_rate`; it may only support a partial local diagnostic gap.
- Reject standalone `交易`, `买入`, `卖出`, `股票`, or broad holding/portfolio table labels.
- Multiple identical turnover rates: keep first locator. Conflicting turnover rates: omit `turnover_rate` and add `ambiguous_table_or_locator`.

### 5.4 Manager / Employee Holding Alignment / `manager_alignment`

Allowed source:

- Stable section/paragraph/table/cell sources containing:
  - `基金经理持有本基金`
  - `基金经理持有份额`
  - `本基金基金经理持有本开放式基金`
  - `基金管理人所有从业人员持有本基金`
  - `从业人员持有本基金`
  - guarded generic `基金经理持有`, `从业人员持有`, or `持有本基金`

Selection:

- `manager_holding`: disclosed manager holding value/range/text from manager-labeled row/paragraph.
- `employee_holding`: disclosed employee holding value/range/text from employee/从业人员/基金管理人-labeled row/paragraph.
- `judgment`: always `None`.
- Generic `持有本基金` requires S6-D guard context containing `基金经理`, `从业人员`, or `基金管理人`.
- Multiple identical values: keep first locator. Conflicting manager or employee values: omit the conflicting subkey and add `ambiguous_table_or_locator`.
- Do not infer manager motivation or interests alignment.

### 5.5 Holdings Snapshot / `holdings_snapshot`

Allowed source only if owned by `manager_profile.v1` in this gate:

- Stable table rows under headings/captions/path containing:
  - `报告期末按行业分类的股票投资组合`
  - `期末按行业分类的股票投资组合`
  - `报告期末按公允价值占基金资产净值比例大小排序的前十名股票投资明细`
  - `前十名股票投资明细`
  - `报告期末基金资产组合情况`

Selection:

- `top_holdings`: up to 10 disclosed rows from the `前十名股票投资明细` table; preserve disclosed Chinese column headers and cell text.
- `top_holdings_status`: `"direct_top_ten"` when `top_holdings` is emitted, otherwise `"missing"`.
- `top_holdings_source`: `"top_ten"` when `top_holdings` is emitted, otherwise `"none"`.
- `industry_distribution`: disclosed industry rows from industry-classification table; preserve disclosed Chinese column headers and cell text.
- `industry_distribution_status`: `"direct"` when `industry_distribution` is emitted, otherwise `"missing"`.
- Do not emit concentration, style drift, core risk, current-stage, share-change, target-fund, or bond-holding conclusions.
- Conflicting duplicate rows for the same stock/industry key cause the conflicting row group to be omitted with `ambiguous_table_or_locator`; identical duplicate rows keep first locator.

## 6. Ambiguity And Fail-closed Taxonomy

Use existing `FundExtractionGapCode` only. Do not add taxonomy.

- `field_family_missing`: no allowed `manager_profile.v1` subvalue is emitted.
- `field_family_partial`: at least one subvalue is emitted and one or more of the five allowed top-level subvalues is missing.
- `ambiguous_table_or_locator`: multiple stable locators produce conflicting values for the same output path or row identity.
- `evidence_anchor_missing`: a helper produced a value candidate without a valid public `EvidenceAnchor`; implementation should prefer omitting the value before this gap becomes necessary.
- `candidate_only_not_source_truth`: proof missing/invalid path preserves current candidate-only evidence and appends source-truth admission gap.
- `source_truth_admission_missing` / `source_truth_admission_invalid`: inherited from existing proof guard.
- Base admission failures (`source_provenance=None`, non-empty `failure_class`, identity mismatch, unsupported input) stay in existing processor admission behavior.

Same-value/multi-locator behavior:

- Same output path + same normalized value across multiple stable locators: keep the first locator and do not add ambiguity.
- Same output path + conflicting normalized values: omit that output path and add one `ambiguous_table_or_locator` gap with `source_field_path` equal to the output path.
- Multi-row list fields:
  - Identical row identity and identical row value: keep first.
  - Identical row identity and conflicting row value: omit that row and add `ambiguous_table_or_locator`.
  - Distinct row identities: include in source order.

Proof and boundary fail-closed behavior:

- `source_truth_extraction_allowed` must remain the only direct route switch.
- Proof-positive direct route suppresses `manager_profile.v1.candidate_evidence` even when no direct value is found.
- Proof-missing or proof-invalid route keeps current S6-D candidate-only behavior and public missing shape.
- Candidate-boundary route remains blocked by existing admission semantics and must not be upgraded by any proof object.

## 7. Anchor Construction And Gap Semantics

Construct public anchors using existing `EvidenceAnchor` only:

- `source_kind="annual_report"`
- `document_year=context.document_year`
- `section_id`: from section/paragraph/table/cell section field
- `page_number=None` for FDD content unless current protocol already exposes proven page number; do not expand schema.
- `table_id`: table/cell table id when table-backed, else `None`
- `row_locator`: stable field-specific string
- `note`: truncated disclosed text/value via existing `_truncate`

Required row locator formats:

- Portfolio manager row: `field=portfolio_managers; table_id={table_id}; row={row_index}; manager={name}`
- Strategy paragraph: `field=manager_strategy_text.{strategy_summary|market_outlook}; block_id={block_id}`
- Turnover cell/paragraph: `field=turnover_rate.{turnover_rate|turnover_basis}; table_id={table_id}; row={row_index}; column={column_index}` or `field=turnover_rate.{...}; block_id={block_id}`
- Alignment cell/paragraph: `field=manager_alignment.{manager_holding|employee_holding}; table_id={table_id}; row={row_index}; column={column_index}` or `field=manager_alignment.{...}; block_id={block_id}`
- Holdings row: `field=holdings_snapshot.{top_holdings|industry_distribution}; table_id={table_id}; row={row_index}`

Anchor rules:

- Public `anchors` includes only anchors for emitted public subvalues.
- Deduplicate by existing `_dedupe_anchors()`.
- Do not create anchors for missing/deferred subkeys.
- Do not use candidate locator records as public anchors.

Gap rules:

- Direct-route `missing`: `value={}`, `anchors=()`, `candidate_evidence=()`, one `field_family_missing` gap.
- Direct-route `partial`: `value` contains `schema_version` plus emitted subvalues only; one `field_family_partial` gap per missing allowed top-level subvalue; ambiguity gaps are additive.
- Direct-route `accepted`: no gaps unless non-required duplicate rows were skipped; if any ambiguity gap is present, status must be `partial`, not `accepted`.

## 8. Facade Projection Decision

No `FundDataExtractor` production code change is planned.

Reason:

- `fund_agent/fund/data_extractor.py:708-793` already maps `manager_profile.v1` to `portfolio_managers`, `turnover_rate`, `manager_alignment`, `manager_strategy_text`, and `holdings_snapshot`.
- `_field_from_family()` already returns missing `ExtractedField` when a top-level key is absent or `None`.
- Therefore, if FDD processor emits existing top-level keys with existing dict shapes, `StructuredFundDataBundle` projection is already supported.

Planned facade work is tests only:

- Add or update an explicit FDD facade regression proving proof-positive `manager_profile.v1` values project to:
  - `bundle.portfolio_managers`
  - `bundle.turnover_rate`
  - `bundle.manager_alignment`
  - `bundle.manager_strategy_text`
  - `bundle.holdings_snapshot`
- Add negative facade regression proving proof-missing/candidate-only `manager_profile.v1` remains missing in bundle and does not consume candidate evidence.

Do not add new bundle fields. Do not route `current_stage.v1` or `core_risk.v1` through these values in this gate.

## 9. Affected Files / Modules And Forbidden Files

Future implementation allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`
- `docs/design.md`
- `fund_agent/fund/README.md`
- Implementation evidence artifact under `docs/reviews/` for the later implementation gate

Forbidden files/modules:

- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/data_extractor.py` production code
- `fund_agent/fund/extractors/**` production code
- `fund_agent/fund/documents/**`
- `fund_agent/services/**`, `fund_agent/service/**`, `fund_agent/ui/**`, `fund_agent/host/**`, `fund_agent/agent/**`
- renderer, quality gate, repository/source/cache/live/network/provider/LLM code
- root README or unrelated package README unless implementation unexpectedly changes user-facing commands or broader architecture, which this plan forbids
- control docs: `docs/implementation-control.md`, `docs/current-startup-packet.md`
- git state, branches, PR, external state, unrelated untracked files

## 10. Implementation Slices

### Slice 1: Direct Route / Admission Guard Skeleton

Objective: route exactly `manager_profile.v1` into a direct extractor only when existing source-truth admission allows it.

Allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`

Exact changes:

- Add local `manager_profile_source_truth: FundFieldFamilyResult | None` in `_field_families_for_intermediate()`.
- When `source_truth_extraction_allowed and content_intermediate is not None`, call new `_extract_manager_profile_source_truth(content_intermediate, source_provenance, context)`.
- Set `manager_profile_evidence = ()` when direct result is present; otherwise keep `_select_manager_profile_candidate_evidence(intermediate)`.
- In field-family construction, return `manager_profile_source_truth` only for `family_id == "manager_profile.v1"` and non-None.
- Add `_extract_manager_profile_source_truth()` skeleton returning missing direct-route shape (`field_family_missing`, `candidate_evidence=()`).
- Do not alter `_validate_source_truth_admission()`.

Tests:

- `test_manager_profile_source_truth_route_suppresses_candidate_evidence`
- `test_manager_profile_source_truth_requires_proof_even_when_candidate_boundary_none`
- `test_manager_profile_source_truth_rejects_base_admission_invalid_paths`
- `test_manager_profile_source_truth_candidate_boundary_remains_blocked`

Validation command:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Expected assertions:

- Proof-positive route has `candidate_evidence == ()`.
- Proof-missing route keeps S6-D candidate evidence plus `source_truth_admission_missing`.
- Base admission invalid routes do not emit field families.
- Candidate boundary remains blocked and public missing.

Completion signal: direct skeleton exists, no public values yet, all existing candidate-only tests still pass.

Stop condition: any admission behavior change outside `manager_profile.v1` or any source-truth proof weakening.

### Slice 2: Manager Roster, Strategy, Turnover Values

Objective: emit the first three allowed `manager_profile.v1` top-level subvalues from stable proof-positive FDD content.

Allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`

Exact changes:

- Add private module-level helpers:
  - `_select_manager_profile_values(...)`
  - `_select_manager_profile_portfolio_managers(...)`
  - `_select_manager_profile_strategy_text(...)`
  - `_select_manager_profile_turnover_rate(...)`
  - `_build_manager_profile_value(...)`
  - `_manager_profile_status(...)`
  - `_manager_profile_source_truth_gaps(...)`
  - `_manager_profile_emitted_output_paths(...)`
- Add small private candidate dataclass only if needed, e.g. `_ManagerProfileValueCandidate`, with `output_path`, `value`, `anchor`, `source_field_path`.
- Implement source rules from sections 5.1-5.3.
- Build anchors using section/paragraph/table/cell public `EvidenceAnchor`, `source_kind="annual_report"`, `page_number=None`.
- Omit ambiguous conflicting subvalues; do not raise.

Tests:

- `test_manager_profile_source_truth_extracts_roster_strategy_turnover_shape`
- `test_manager_profile_source_truth_partial_when_required_groups_missing`
- `test_manager_profile_source_truth_missing_when_no_allowed_labels`
- `test_manager_profile_source_truth_ambiguous_duplicate_omits_conflicting_value`
- `test_manager_profile_source_truth_skips_unstable_locator`
- Existing S6-D candidate tests must remain unchanged.

Validation command:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Expected assertions:

- `value["schema_version"] == "manager_profile.v1"`.
- `portfolio_managers` matches existing tenure-list shape.
- `manager_strategy_text` includes only `strategy_summary` / `market_outlook`.
- `turnover_rate` includes only `turnover_rate` / `turnover_basis`.
- Public anchors exist only for emitted values.
- Missing subvalues produce `field_family_partial`, not inferred values.

Completion signal: proof-positive FDD can emit three subvalues without candidate evidence.

Stop condition: implementation needs new contract/schema, new source kind, or source fields not present in current FDD protocol.

### Slice 3: Alignment, Holdings Snapshot, Anchor/Gap Hardening

Objective: add remaining two allowed subvalues and complete fail-closed taxonomy.

Allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`

Exact changes:

- Add helpers:
  - `_select_manager_profile_alignment(...)`
  - `_select_manager_profile_holdings_snapshot(...)`
  - row grouping and duplicate/ambiguity helpers shared only inside manager-profile source-truth extraction.
- Implement source rules from sections 5.4-5.5.
- Ensure `manager_alignment["judgment"] is None`.
- Ensure holdings snapshot does not emit concentration/style/current-stage/core-risk/share-change data.
- Ensure direct-route missing uses `value={}`, not `{"schema_version": ...}`.
- Ensure direct-route emitted values do not include missing top-level keys with `None`; absence plus gaps is the missing signal.

Tests:

- `test_manager_profile_source_truth_extracts_alignment_without_judgment`
- `test_manager_profile_source_truth_extracts_holdings_snapshot_without_risk_or_stage_fields`
- `test_manager_profile_source_truth_rejects_generic_holding_without_guard_context`
- `test_manager_profile_source_truth_same_value_multi_locator_keeps_first_anchor`
- `test_manager_profile_source_truth_conflicting_holdings_row_is_ambiguous`
- `test_manager_profile_source_truth_accepted_when_all_allowed_groups_present`

Validation command:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Expected assertions:

- All five allowed top-level subvalues present -> `status="accepted"`, `extraction_mode="direct"`, no gaps.
- Partial values -> `status="partial"` with `field_family_partial`.
- Conflicts -> `ambiguous_table_or_locator`; no conflicting value emitted.
- Candidate boundary and proof invalid paths remain public missing.

Completion signal: manager_profile direct extraction is field-family complete for this gate.

Stop condition: implementation would need semantic judgments, real-report manual verification, parser replacement, or public schema expansion.

### Slice 4: Facade Regression, Docs Sync, Evidence Artifact

Objective: prove existing facade projection works and sync current facts after implementation.

Allowed files:

- `tests/fund/test_data_extractor.py`
- `docs/design.md`
- `fund_agent/fund/README.md`
- implementation evidence artifact under `docs/reviews/`

Exact changes:

- Add facade regression using explicit FDD route and proof-positive source-truth manager-profile values.
- Assert bundle fields:
  - `portfolio_managers`
  - `turnover_rate`
  - `manager_alignment`
  - `manager_strategy_text`
  - `holdings_snapshot`
- Add negative facade regression for proof-missing/candidate-only FDD route preserving missing bundle fields.
- Update `docs/design.md` only to state current implemented fact after code passes: `manager_profile.v1` proof-positive FDD source-truth direct extraction exists; other three families remain unimplemented; candidate evidence remains `not_proven / NOT_READY`.
- Update `fund_agent/fund/README.md` only for Fund package current behavior; no release/readiness or real-report correctness claim.
- Do not update control docs in implementation worker slice unless controller separately authorizes.

Validation commands:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
git diff --check
git diff --check -- docs/design.md fund_agent/fund/README.md
```

Expected assertions:

- Focused processor and facade tests pass.
- Existing parsed annual manager/holdings extractor tests still pass, proving existing public shape expectations were not broken.
- Ruff passes for touched code/test files.
- Diff check passes.
- Docs wording preserves `NOT_READY`, no parser replacement, no source/readiness/release expansion, no other family implemented.

Completion signal: implementation evidence artifact records changed files, validation outputs, docs decision, residual risks, and stop confirmation.

Stop condition: any facade production code change appears necessary; that would require controller decision because this plan assumes existing projection is sufficient.

## 11. Docs Sync Decision

Implementation changes current facts, so docs sync is required after tests pass:

- `docs/design.md`: update current-state summary and Processor/Extractor section to add `manager_profile.v1` as proof-positive FDD source-truth direct extraction; keep `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` unimplemented; preserve candidate-only/not_proven/NOT_READY boundaries.
- `fund_agent/fund/README.md`: update Fund package current Processor/Extractor behavior only.

No docs sync in this planning-only gate beyond this plan artifact.

No root `README.md`, `fund_agent/README.md`, control docs, startup packet, release docs, PR docs, or external state updates are planned for implementation.

## 12. Residual Risks And Owners

- Real-report correctness: assigned to future evidence gate. This no-live/unit plan does not prove real annual-report field correctness.
- Cross-parser representation correctness: assigned to future candidate/source evidence owner. This plan does not qualify Docling/FDD full representation.
- Holdings snapshot shape breadth: assigned to future field-family refinement gate. This gate only implements active-fund top holdings and industry distribution subset.
- Manager tenure normalization: assigned to future refinement gate. This gate preserves disclosed date text; no tenure duration or current-manager inference.
- `manager_alignment.judgment`: assigned to future analysis/template gate. This gate leaves `judgment=None`.
- Facade production code: owner implementation worker. If existing `data_extractor` projection proves insufficient, stop and return to controller; do not patch facade production code under this plan.
- Docs/control sync after implementation: implementation worker may update `docs/design.md` and `fund_agent/fund/README.md`; controller owns control-doc entry after accepted implementation/review.

No residual blocks code-generation-ready planning.

## 13. Why This Is Not Over-designed

- It reuses the existing `FundDisclosureSourceTruthAdmissionProof` gate instead of inventing a second proof mechanism.
- It reuses existing `manager_profile.v1` public top-level fields and `StructuredFundDataBundle` projection instead of adding schema.
- It keeps all logic local to `FundDisclosureDocumentProcessor` and focused tests.
- It implements only field extraction from proof-positive content, not semantic manager analysis.
- It treats `turnover_rate` and `holdings_snapshot` only as existing `manager_profile.v1` fields for Chapter 3 and does not generalize them into `core_risk.v1` or `current_stage.v1`.
- It keeps candidate evidence candidate-only when proof is missing or invalid.
- It defers real-report correctness, parser replacement, broader holdings shapes, and readiness to later gates with explicit owners.

## 14. Completion Report Format For Implementation Worker

Later implementation worker should report:

- artifact path for implementation evidence
- verdict: implementation complete or blocked
- changed files
- validation commands and results
- docs sync performed or not performed with reason
- residual risks and owners
- stop confirmation: no commit, push, PR, merge, mark-ready, external state, unrelated cleanup, or next gate action unless separately authorized
