# FundDisclosureDocument S6-F Core Risk Candidate Selector Plan

## 1. Gate And Recommendation

- Gate: `FundDisclosureDocument S6-F Single-family Candidate Evidence Selector Planning Gate`
- Work unit: `Docling architecture reorientation / Fund Processor-Extractor route`
- Worker role: planning worker only; no implementation, source/test/design/control edit, commit, push, PR, merge, cleanup, or controller judgment.
- Selected field family: `core_risk.v1`
- Verdict: proceed with exactly one selector for `core_risk.v1`.

Rationale from first principles:

- Current control truth says S6-F must choose and plan exactly one remaining unimplemented field family selector, currently `current_stage.v1` or `core_risk.v1`, while preserving candidate-only / not_proven / NOT_READY boundaries.
- The user has selected `core_risk.v1`; this plan treats that selection as the planning input and does not re-open field-family choice.
- `core_risk.v1` maps to template Chapter 6, "核心风险与否决项", but this gate is not allowed to answer Chapter 6. It may only locate risk-related disclosure candidates for a later extractor/evidence gate.
- Current `ActiveFundAnnualProcessor` maps `core_risk.v1` to five existing field surfaces: `profile.risk_characteristic_text`, `manager_ownership.holder_structure`, `manager_ownership.turnover_rate`, `holdings_share_change.holdings_snapshot`, and `performance.tracking_error`.
- Those five surfaces overlap accepted S6-B/S6-C/S6-D/S6-E selectors. The correct S6-F design is family-local candidate evidence with strict source-level guards, not cross-family semantic reuse or selector mutation.
- `current_stage.v1` remains unimplemented. This plan does not introduce a selector for it.

Chapter 6 risk-judgment boundary:

- `core_risk.v1` candidate evidence locates disclosure that may later support risk analysis.
- It must not infer one-vote veto, risk causality, risk level, structural vs cyclical risk, pressure-test conclusion, final holding/replacement judgment, or "most fatal risk".
- Candidate evidence remains `candidate-only`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `readiness_status="not_ready"`.

## 2. Exact Non-goals

- No selector for `current_stage.v1`.
- No modification to accepted S6-B `product_essence.v1`, S6-C `return_attribution.v1`, S6-D `manager_profile.v1`, or S6-E `investor_experience.v1` semantics.
- No final field extraction into `risk_characteristic_text`, `holder_structure`, `turnover_rate`, `holdings_snapshot`, `tracking_error`, scale, liquidation status, concentration, drawdown, pressure-test output, veto status, or risk score.
- No parsing of candidate excerpts into numeric values, thresholds, ratio comparisons, risk labels, or conclusions.
- No `FundFieldFamilyResult.value` population from candidate evidence.
- No public `EvidenceAnchor` creation and no `FundFieldFamilyResult.anchors` population from candidate evidence.
- No `partial`, `accepted`, `satisfied`, `direct`, `derived`, or `estimated` status/mode from candidate evidence.
- No `FundDataExtractor`, facade projection, `StructuredFundDataBundle`, renderer, quality gate, Service, UI, Host, Agent runner, repository, source, cache, live/network, PDF, Docling conversion, pdfplumber export, provider, or LLM change.
- No contract/schema expansion in `contracts.py`; the S6-A candidate evidence contract is sufficient.
- No `EvidenceSourceKind` or public `EvidenceAnchor.source_kind` expansion.
- No source truth, field correctness, parser replacement, golden, readiness, release, PR state, or upper-layer consumption claim.
- No cleanup, deletion, staging, or classification of unrelated untracked residuals.

## 3. Selector Contract

The S6-F selector is a deterministic locator selector, not a value extractor and not a Chapter 6 risk analyzer.

Family:

- `core_risk.v1`

Mapping to current `ActiveFundAnnualProcessor` field surface, as locator roles only:

| Locator role | Current processor field surface | Template chapter | Meaning in this gate |
|---|---|---|---|
| `risk_characteristic` | `profile.risk_characteristic_text` | 6 | Locator for product risk-characteristic disclosure only. |
| `liquidation_or_scale_risk` | `manager_ownership.holder_structure` | 6 | Locator for liquidation / minimum-holder / minimum-asset-value disclosure only. |
| `tracking_error_or_deviation_risk` | `performance.tracking_error` | 6 | Locator for tracking-error or tracking-deviation disclosure only. |
| `turnover_or_style_drift_risk` | `manager_ownership.turnover_rate` | 6 | Locator for turnover or explicitly disclosed strategy/style-change risk disclosure only. |
| `concentration_risk` | `holdings_share_change.holdings_snapshot` | 6 | Locator for holdings / industry / top-position concentration disclosure only. |

Allowed input protocol:

- `FundDisclosureDocumentContentIntermediate` only after existing admission and identity checks pass.
- If the intermediate is only `FundDisclosureDocumentIntermediate` and not content-bearing, `core_risk.v1` remains `field_family_missing`.

Allowed locator sources:

- `sections`
- `paragraph_blocks`
- `table_blocks`
- `table_blocks[*].cells`

Allowed candidate source fields:

- Section fields: `heading_text_normalized`, `heading_text_raw`, `heading_path`
- Paragraph fields: `text_normalized`, `text_raw`, `heading_path`
- Table fields: `heading_text`, `table_caption_or_nearby_heading`, `heading_path`
- Cell fields: `cell_text_normalized`, `cell_text`, `row_label_path`, `column_header_path`, `heading_path`

Match groups:

| Role | Strong tokens | Generic tokens requiring source-level guard | Guard tokens | Evidence role |
|---|---|---|---|---|
| `risk_characteristic` | `风险收益特征`, `风险特征`, `基金风险收益特征`, `产品风险收益特征` | `风险`, `收益` | `风险收益特征`, `风险特征`, `基金产品资料概要`, `基金简介` | locator for risk-characteristic disclosure candidate |
| `liquidation_or_scale_risk` | `基金资产净值低于五千万元`, `基金资产净值低于5000万元`, `基金份额持有人数量不满二百人`, `基金份额持有人数量不满200人`, `连续二十个工作日`, `连续20个工作日`, `基金合同终止事由`, `基金合同自动终止`, `基金财产清算` | `规模`, `清盘`, `持有人`, `基金资产净值` | `基金合同终止`, `基金财产清算`, `连续二十个工作日`, `连续20个工作日`, `五千万元`, `5000万元`, `二百人`, `200人`, `基金份额持有人数量` | locator for liquidation / scale-risk disclosure candidate |
| `tracking_error_or_deviation_risk` | `跟踪误差`, `年化跟踪误差`, `日均跟踪偏离度`, `日均偏离度`, `跟踪偏离度` | `跟踪`, `偏离` | `跟踪误差`, `跟踪偏离度`, `业绩比较基准`, `标的指数`, `指数基金`, `指数增强` | locator for tracking-error / deviation disclosure candidate |
| `turnover_or_style_drift_risk` | `换手率`, `股票换手率`, `报告期内股票换手率`, `换手率口径`, `换手率计算口径`, `投资风格发生重大变化`, `投资策略发生重大变化`, `风格漂移` | `换手`, `风格`, `漂移`, `策略变化` | `换手率`, `投资策略`, `投资风格`, `报告期内基金投资策略和运作分析`, `运作分析`, `重大变化` | locator for turnover / explicitly disclosed style-drift risk candidate |
| `concentration_risk` | `持仓集中度`, `报告期末按行业分类的股票投资组合`, `期末按行业分类的股票投资组合`, `报告期末按公允价值占基金资产净值比例大小排序的前十名股票投资明细`, `前十名股票投资明细`, `报告期末基金资产组合情况` | `持仓`, `集中`, `行业集中`, `前十名` | `股票投资组合`, `资产组合情况`, `公允价值占基金资产净值比例`, `前十名股票投资明细`, `行业分类`, `持仓集中度` | locator for concentration disclosure candidate |

Forbidden standalone tokens:

- Do not match `风险`, `收益`, `持仓`, `规模`, `清盘`, `压力`, `回撤`, `换手`, `集中`, `跟踪`, `偏离`, `风格`, `漂移`, `持有人`, or `基金资产净值` without the role-specific source-level guard above.
- Do not add `压力测试`, `最大回撤`, `否决`, `一票否决`, `最致命`, `需要替换`, `值得持有`, or `风险等级` as match tokens for this gate. Those are Chapter 6 reasoning/output concepts, not locator-only disclosure surfaces.
- Do not add S6-E share-flow-only tokens such as `基金份额变动`, `申购`, `赎回`, `净申购`, `净赎回`, `收益分配`, `分红`, or `红利` to `core_risk.v1`.
- Do not add S6-C return/fee tokens such as `净值增长率`, `业绩比较基准收益率`, `管理费`, `托管费`, or `销售服务费` to `core_risk.v1`, except `业绩比较基准` may appear only as a guard token for tracking-error/deviation context and must not itself produce a record.

Guard rule:

- Strong tokens may match directly because they are already role-specific disclosure phrases.
- Generic tokens may match only when the same source-level guard context contains at least one guard token for that role.
- For sections and tables, guard context is the same source text tuple used for matching: heading text, caption, and heading path.
- For paragraphs, guard context is `text_normalized`, `text_raw`, and `heading_path`.
- For cells, guard context must be parent table `heading_text`, parent `table_caption_or_nearby_heading`, parent `heading_path`, cell `row_label_path`, cell `column_header_path`, and cell `heading_path`.
- Core-risk cell generic guard context must be role-invariant across all five roles and must never include `cell_text` or `cell_text_normalized`.
- Do not copy the S6-E `_investor_experience_cell_guard_context()` default branch for core-risk cells, because that branch can include same-cell text in the guard context.
- Strong tokens may still match directly from `cell_text` / `cell_text_normalized`; only broad generic-token guards are forbidden from being satisfied by the same cell text.
- For cells, generic tokens must not pass solely because the same cell text contains both a broad token and a guard-looking token; this prevents `风险` / `规模` / `持仓` / `换手` self-guarding inside arbitrary cells.
- A generic token in one source must not pass because another section/table/paragraph elsewhere contains a guard token.

Overlap handling:

- S6-B `product_essence.v1` already owns risk-characteristic locator evidence. S6-F may produce family-local `risk_characteristic` records from the same source paths, but must not change S6-B token set, order, limit, gap semantics, or tests.
- S6-C `return_attribution.v1` already owns `tracking_error` locator evidence. S6-F may produce family-local `tracking_error_or_deviation_risk` records from the same source paths, but must not change S6-C return/performance/fee semantics.
- S6-D `manager_profile.v1` already owns `turnover_rate` and `holdings_snapshot` locator evidence. S6-F may produce family-local `turnover_or_style_drift_risk` and `concentration_risk` records from the same source paths, but must not change S6-D manager-profile semantics.
- S6-E `investor_experience.v1` already owns holder/share-change/subscription/redemption/distribution locators. S6-F may use holder/minimum-holder context only for `liquidation_or_scale_risk`; it must not capture share-flow or distribution tokens and must not change S6-E semantics.
- Cross-family dedupe is forbidden. Each accepted field family keeps its own candidate evidence set and local dedupe by `source_field_path`.

## 4. Source Path, Ordering, Dedupe, Limit, Excerpt

Source path formats must remain exact and stable:

- Section record: `sections[{section_index}]`
- Paragraph record: `paragraph_blocks[{paragraph_index}]`
- Table record: `table_blocks[{table_index}]`
- Cell record: `table_blocks[{table_index}].cells[{cell_index}]`

For cell records:

- `cell_index` is the original tuple index from `enumerate(table.cells)`.
- Cell scan order is sorted by `(row_index, column_index)`, while `source_field_path` preserves the original tuple index.

Ordering rule:

1. Iterate roles in this order: `risk_characteristic`, `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, `concentration_risk`.
2. Within each role, scan sources in this order: sections, paragraph blocks, table blocks, table cells.
3. Sections, paragraphs, and tables preserve tuple order.
4. Cells are sorted by `(row_index, column_index)`.

Dedupe rule:

- Deduplicate within `core_risk.v1` by exact `source_field_path`.
- Keep the first record for a path according to the ordering rule.
- Do not deduplicate across `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1`, and `core_risk.v1`; each field family owns its own candidate evidence set.

Limit rule:

- Add `_CORE_RISK_CANDIDATE_LIMIT = 16`.
- Keep at most 16 records for `core_risk.v1`.
- If more than 16 candidate records exist, preserve the ordering rule and truncate after 16.

Excerpt rule:

- Reuse `_CANDIDATE_EXCERPT_LIMIT = 160`.
- Section/table excerpt: first non-empty normalized/raw heading, caption, or heading-path text used for matching.
- Paragraph excerpt: `text_normalized` if non-empty, otherwise `text_raw`.
- Cell excerpt: `cell_text_normalized` if non-empty, otherwise `cell_text`.
- Excerpt is a candidate locator preview only; it is not source truth and must not be parsed as a field value, threshold comparison, risk classification, pressure-test result, or final judgment.

Candidate evidence fields:

- `field_family_id="core_risk.v1"`
- `source_boundary="candidate_only"`
- `candidate_only=True`
- `field_correctness_status="not_proven"`
- `source_truth_status="not_proven"`
- `parser_replacement_authorized=False`
- `readiness_status="not_ready"`
- `row_locator` format must mirror S6-B/S6-C/S6-D/S6-E: `role={role}; locator=...`

## 5. Implementation Design For Later Gate

The later implementation gate should keep the behavior change local to `FundDisclosureDocumentProcessor`.

Required processor behavior:

- Add `_CORE_RISK_MATCH_GROUPS` with role configs matching this plan.
- Add `_CORE_RISK_CANDIDATE_LIMIT = 16`.
- Add `_select_core_risk_candidate_evidence()` as the core-risk wrapper.
- In `_field_families_for_intermediate()`, select:
  - existing `product_essence.v1` candidate evidence;
  - existing `return_attribution.v1` candidate evidence;
  - existing `manager_profile.v1` candidate evidence;
  - existing `investor_experience.v1` candidate evidence;
  - new `core_risk.v1` candidate evidence.
- Do not add a sixth nested conditional expression inside `_field_families_for_intermediate()`.
- Implement family selection with a local `candidate_evidence_by_family` mapping or equivalent local mapping structure keyed by field-family id, then iterate `_FAMILY_ORDER` and choose:
  - `_candidate_missing_field_family(family_id, source_provenance, candidate_evidence)` when mapped evidence is non-empty;
  - `_missing_field_family(family_id, source_provenance)` when mapped evidence is empty or absent.
- The mapping must include only implemented candidate selectors. `current_stage.v1` must be absent from the mapping or mapped to empty evidence, so it stays `field_family_missing`.
- This restructuring must not change S6-B/S6-C/S6-D/S6-E selector semantics, family order, source path order, gap semantics, `value == {}`, `anchors == ()`, limits, or row locators.
- For `core_risk.v1` with non-empty candidate evidence:
  - return `_candidate_missing_field_family("core_risk.v1", source_provenance, core_risk_evidence)`.
- For `core_risk.v1` with empty candidate evidence:
  - keep existing `_missing_field_family("core_risk.v1", source_provenance)`.
- `current_stage.v1` stays fully missing with no candidate evidence.

Required result semantics:

- `core_risk.v1.status == "missing"`
- `core_risk.v1.extraction_mode == "missing"`
- `core_risk.v1.value == {}`
- `core_risk.v1.anchors == ()`
- `core_risk.v1.gaps[0].gap_code == "candidate_only_not_source_truth"` only when candidate evidence exists.
- `core_risk.v1.gaps[0].gap_code == "field_family_missing"` when no candidate evidence exists.
- Overall result-level candidate-boundary status remains existing admission behavior:
  - concrete candidate-boundary input remains `contract_status="blocked"`;
  - non-candidate content stubs may remain `contract_status="missing"`.
- Other accepted field families remain governed only by their own S6-B/S6-C/S6-D/S6-E matching content.

Required helper structure:

- This gate must not refactor S6-B/S6-C/S6-D/S6-E traversal helpers into shared guarded-scanning helpers.
- Add core-risk-local private helpers only, such as `_matches_guarded_core_risk_source()` and `_core_risk_cell_guard_context()`.
- Keep existing S6-B/S6-C/S6-D/S6-E traversal helpers unchanged except for call-site-neutral coexistence with the new `_field_families_for_intermediate()` local mapping.
- `_core_risk_cell_guard_context()` must return only parent table heading/caption/path and row/column/heading path context; it must not return `cell_text` or `cell_text_normalized` for any role.
- `_matches_guarded_core_risk_source()` must keep strong-token-first behavior and only allow generic-token matches with same-source role-specific guard context.
- Do not copy S6-E cell-guard default behavior into core-risk helpers.
- Do not add nested functions/classes.
- Do not import candidate document concrete classes, Docling, PDF/source/cache helpers, repository helpers, Service/UI/Host, renderer, quality gate, provider, LLM, or network modules.
- Update the `_field_families_for_intermediate()` docstring from S6-B/S6-C/S6-D wording to S6-B/S6-C/S6-D/S6-E/S6-F current wording if implementation changes that function.

## 6. Allowed And Forbidden Write Set

Current planning worker allowed write set:

- `docs/reviews/funddisclosuredocument-s6f-core-risk-candidate-selector-plan-20260619.md`

Current planning worker forbidden write set:

- Every file except the plan artifact above.
- No source, test, docs/design, docs/control, README, implementation evidence, commit, push, PR, merge, stage, cleanup, or residual disposition.

Future implementation gate allowed write set, only after plan review and controller judgment:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-s6f-core-risk-candidate-selector-implementation-evidence-20260619.md`

Future implementation gate forbidden write set:

- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/data_extractor.py` or any `FundDataExtractor` implementation file
- `fund_agent/fund/extractors/**`
- `fund_agent/fund/documents/**`
- `fund_agent/service/**`
- `fund_agent/host/**`
- `fund_agent/agent/**`
- renderer, quality gate, repository, source, cache, live/network, provider, PR, release, or unrelated residual files

## 7. Required Tests

Add or update focused tests in `tests/fund/processors/test_fund_disclosure_processor.py` during the future implementation gate:

1. `test_core_risk_selector_adds_candidate_evidence_only`
   - Content-bearing intermediate with risk-characteristic, liquidation/scale, tracking-error/deviation, turnover/style-change, and concentration locator text yields `core_risk.v1.candidate_evidence`.
   - Assert role set contains exactly `role=risk_characteristic`, `role=liquidation_or_scale_risk`, `role=tracking_error_or_deviation_risk`, `role=turnover_or_style_drift_risk`, and `role=concentration_risk`.
   - Assert `status="missing"`, `extraction_mode="missing"`, `value == {}`, `anchors == ()`, and local gap `candidate_only_not_source_truth`.

2. `test_core_risk_selector_preserves_candidate_boundary_fields`
   - Every core-risk candidate record has `field_family_id == "core_risk.v1"`, `candidate_only=True`, `source_boundary="candidate_only"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, and `readiness_status="not_ready"`.
   - Assert no `source_field_path`, excerpt, numeric-looking text, threshold, or role is copied into `family.value`.

3. `test_core_risk_selector_keeps_current_stage_without_candidate_evidence`
   - With only core-risk matching content, `current_stage.v1` remains `field_family_missing` with empty `candidate_evidence`.
   - Existing `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1`, and `investor_experience.v1` remain governed only by their own S6-B/S6-C/S6-D/S6-E matching content.

4. `test_core_risk_selector_no_match_keeps_field_family_missing`
   - Neutral content produces no core-risk evidence and preserves `field_family_missing`.

5. `test_core_risk_selector_preserves_candidate_boundary_blocked_status`
   - Candidate-boundary input with core-risk candidate evidence still returns result-level `contract_status="blocked"`.
   - Assert `result.candidate_boundary is boundary`, `family.candidate_evidence` is non-empty, and `family.value == {}` / `family.anchors == ()`.

6. `test_core_risk_selector_orders_dedupes_limits_and_truncates`
   - Construct more than 16 candidate paths across all five roles.
   - Assert role order, source order, exact `source_field_path`, first-record-wins dedupe by path, 16-record limit, and `len(record.excerpt) <= 160`.
   - Include out-of-order cells and assert scan order uses `(row_index, column_index)` while `source_field_path` keeps original tuple index.

7. `test_core_risk_selector_requires_context_for_generic_tokens`
   - Generic `风险` / `收益` without risk-characteristic context must not produce `risk_characteristic` evidence.
   - Generic `规模` / `清盘` / `持有人` / `基金资产净值` without liquidation/minimum-holder/minimum-asset-value context must not produce `liquidation_or_scale_risk` evidence.
   - Generic `跟踪` / `偏离` without tracking-error/deviation context must not produce `tracking_error_or_deviation_risk` evidence.
   - Generic `换手` / `风格` / `漂移` / `策略变化` without turnover or explicit investment-style/strategy-change context must not produce `turnover_or_style_drift_risk` evidence.
   - Generic `持仓` / `集中` / `行业集中` / `前十名` without holdings-snapshot / industry / top-position context must not produce `concentration_risk` evidence.

8. `test_core_risk_selector_allows_generic_tokens_with_source_context`
   - Generic tokens above must produce candidate evidence when same source-level guard context contains the required guard token for that role.
   - Assert produced records use the expected `role=...` row locator prefix.

9. `test_core_risk_selector_blocks_cell_self_guard_for_broad_tokens`
   - A cell whose `cell_text` contains both a broad token and a guard-looking token must not pass if parent table heading/caption, row/column labels, and heading path lack the role-specific guard.
   - A sibling cell or unrelated table with a guard token must not authorize the generic cell.
   - A cell may pass only when parent table context, row/column labels, or heading path provide the role-specific guard.

10. `test_core_risk_selector_does_not_capture_reasoning_or_output_tokens`
    - Content containing only Chapter 6 reasoning/output words such as `压力测试`, `最大回撤`, `否决`, `一票否决`, `最致命`, `需要替换`, `值得持有`, or `风险等级` must not produce `core_risk.v1` evidence.
    - Mixed content containing a forbidden reasoning/output token plus a legal strong token must produce evidence only from the legal strong token and expected role.
    - Assert the forbidden token alone does not create an extra record, role, row locator, or source path.

11. `test_core_risk_selector_does_not_capture_investor_experience_owned_tokens`
    - Content containing only S6-E-owned share-flow/distribution tokens such as `基金份额变动`, `申购`, `赎回`, `净申购`, `净赎回`, `收益分配`, `分红`, or `红利` must not produce `core_risk.v1` evidence.

12. `test_core_risk_selector_preserves_overlap_family_semantics`
    - Build a baseline fixture that produces S6-B/S6-C/S6-D/S6-E candidate evidence from their existing selectors without S6-F-only content.
    - Build a second fixture by adding S6-F core-risk content to the baseline fixture.
    - Compare each existing S6-B/S6-C/S6-D/S6-E family between the baseline result and S6-F-added result.
    - Assert existing family record count, exact `source_field_path` order, gap semantics, `value == {}`, and `anchors == ()` remain unchanged.
    - The comparative fixture must cover S6-B, S6-C, S6-D, and S6-E; if implementation scope must be narrowed, it must at minimum cover S6-D plus one additional overlapping family and record the uncovered families as residual risk.

Existing regression tests that must keep passing, with expectation updates only where S6-F makes old wording stale:

- All S6-A candidate evidence contract tests.
- All S6-B product essence selector tests.
- All S6-C return attribution selector tests.
- All S6-D manager profile selector tests.
- All S6-E investor experience selector tests.
- `test_extract_admits_candidate_boundary_but_returns_blocked`
- `test_extract_satisfied_returns_fully_gapped_result`
- `test_extract_satisfied_result_preserves_source_provenance`
- `test_extract_satisfied_result_candidate_boundary_none`
- `test_extract_candidate_boundary_result_preserves_candidate_boundary`
- `test_processor_does_not_import_forbidden_boundaries`

## 8. Validation Matrix

Planning-worker artifact validation:

```bash
git diff --check -- docs/reviews/funddisclosuredocument-s6f-core-risk-candidate-selector-plan-20260619.md
```

Future implementation gate must run:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
git diff --check
```

Docs diff-check if `fund_agent/fund/README.md` and `docs/design.md` are updated:

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Expected validation assertions:

- Focused pytest passes and includes S6-A/S6-B/S6-C/S6-D/S6-E regression coverage plus new S6-F tests.
- Ruff passes for touched code/test files.
- `git diff --check` passes.
- README/design wording, if touched, states current behavior only and does not claim source truth, parser replacement, field correctness, readiness, release, risk conclusion, pressure-test conclusion, final judgment, or upper-layer consumption.

## 9. Acceptance Criteria

S6-F plan acceptance requires:

- Exactly one field family is selected: `core_risk.v1`.
- The plan is code-generation-ready: implementation path, role mapping, tokens, source-level guards, source fields, source paths, order, dedupe, limit, excerpt, write set, tests, validation, and result semantics are explicit.
- The plan explicitly distinguishes risk-disclosure locator evidence from Chapter 6 risk judgment.
- The plan blocks broad standalone tokens including `风险`, `收益`, `持仓`, `规模`, `清盘`, `压力`, `回撤`, `换手`, `集中`, and `跟踪`.
- The plan explains overlap handling with S6-B risk-characteristic, S6-C tracking-error, S6-D turnover/holdings, and S6-E holder/share-change evidence without changing accepted selector semantics.
- Candidate evidence remains `candidate-only`, `not_proven`, and `not_ready`.
- Public `value` and public `EvidenceAnchor` remain empty.
- No `partial`, `accepted`, `satisfied`, `direct`, `derived`, or `estimated` state is introduced by candidate evidence.
- `current_stage.v1` remains unimplemented and receives no candidate evidence.
- `FundDataExtractor`, repository/source/cache/live behavior, public schema, and upper layers remain unchanged.
- Existing S6-A/S6-B/S6-C/S6-D/S6-E behavior is preserved by regression tests.
- Release/readiness remains `NOT_READY`.

Future S6-F implementation acceptance additionally requires:

- Focused pytest passes.
- Ruff passes for touched code/test files.
- `git diff --check` passes.
- Fund README/design sync, if touched, preserves candidate-only wording, current production boundaries, and no-risk-judgment wording.
- Implementation evidence artifact records exact changed files, validation results, docs decision, residual risks, and final `NOT_READY` boundary.

## 10. Residual Risks / Open Questions

- Token false positives remain possible because locator matching does not prove semantic field correctness. Owner: later field-extraction/source-truth gate; S6-F mitigates by keeping public status `missing`.
- `risk_characteristic` overlaps S6-B `product_essence.v1`. Owner: S6-F implementation must keep family-local dedupe and preserve S6-B tests unchanged except stale wording.
- `tracking_error_or_deviation_risk` overlaps S6-C `return_attribution.v1`. Owner: S6-F implementation must avoid non-tracking return/fee tokens and preserve S6-C tests.
- `turnover_or_style_drift_risk` and `concentration_risk` overlap S6-D `manager_profile.v1`. Owner: S6-F implementation must preserve S6-D row locators, limits, and semantics while producing only family-local core-risk locators.
- `liquidation_or_scale_risk` can overlap S6-E holder-structure evidence and Chapter 6 scale/liquidation reasoning. Owner: S6-F implementation must require liquidation/minimum-holder/minimum-asset-value source context and must not capture share-flow or distribution tokens.
- Current parsed annual `core_risk.v1` mapping does not include `profile.basic_identity`, so scale/liquidation locator design may remain under-covered if content only appears in basic-identity or fund-summary sections. Owner: later implementation evidence or field-family extraction design; this plan stays inside current code facts and candidate locator boundaries.
- The selector does not prove pressure-test input sufficiency. Owner: later Chapter 6 extraction/analysis gate; S6-F must not produce pressure-test results.
- Candidate excerpts can contain numeric-looking text such as percentages, net assets, holder counts, turnover values, tracking errors, or concentration ratios. Owner: S6-F implementation must keep excerpts out of `value` and `anchors`; tests must assert no value leak.
- Refactoring traversal helpers could regress S6-B/S6-C/S6-D/S6-E selectors. Owner: S6-F implementation test suite; existing selector tests must remain passing.
- The selector does not prove comparator correctness against repository-loaded PDF, Docling, EID HTML render, or pdfplumber. Owner: deferred evidence/source-truth gates; release/readiness stays `NOT_READY`.

No implementation is authorized by this planning-worker artifact alone.
