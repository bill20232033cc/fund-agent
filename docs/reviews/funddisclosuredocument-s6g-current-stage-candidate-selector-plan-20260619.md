# FundDisclosureDocument S6-G Current Stage Candidate Selector Plan

## 1. Goal / Motivation / Success Signal

- Gate: `FundDisclosureDocument S6-G Current Stage Candidate Selector Planning Gate`
- Work unit: `Docling architecture reorientation / Fund Processor-Extractor route`
- Worker role: planning worker only; no implementation, review, source/test/design/control edit beyond this artifact, commit, stage, push, PR, merge, or residual cleanup.
- Selected field family: `current_stage.v1`
- Recommendation: proceed with exactly one candidate-only locator selector for `current_stage.v1`.

Goal:

- Produce a code-generation-ready plan for adding deterministic `current_stage.v1` candidate-only locator evidence inside `FundDisclosureDocumentProcessor`.
- Keep public field-family result fail-closed: `status="missing"`, `extraction_mode="missing"`, `value={}`, `anchors=()`.
- Preserve existing S6-B/S6-C/S6-D/S6-E/S6-F selector semantics, source order, row locators, limits, gap semantics, public value/anchor emptiness, and candidate-only boundaries.

Motivation:

- `docs/fund-analysis-template-draft.md` Chapter 5 defines `当前阶段与关键变化` as an independent chapter with `current_stage` audit focus.
- Current `fund_agent/fund/processors/active_annual.py` already maps `current_stage.v1` to parsed-route surfaces:
  - `profile.basic_identity`
  - `holdings_share_change.share_change`
  - `holdings_share_change.holdings_snapshot`
  - `manager_ownership.portfolio_managers`
- Current `fund_agent/fund/processors/fund_disclosure_processor.py` already includes `current_stage.v1` in `_FAMILY_ORDER` and `_CHAPTER_IDS["current_stage.v1"] = (5,)`, but `candidate_evidence_by_family` does not include it, so it remains `field_family_missing`.
- S6-F was accepted with `core_risk.v1` candidate evidence while public values stayed missing; S6-G should apply the same boundary discipline to Chapter 5, not promote candidate evidence into source truth or readiness.

Success signal:

- Later implementation can add `current_stage.v1` candidate evidence without redesigning roles, tokens, ordering, guard behavior, row locator schema, source paths, tests, write set, or boundaries.
- `current_stage.v1` gains internal candidate records only when Chapter 5 current-stage / key-change disclosure is found.
- Existing accepted families remain behaviorally unchanged.
- Overall release/readiness remains `NOT_READY`.

## 2. First-principles Judgment

Why planning is valid:

- Chapter 5 asks for current phase and key changes, not for a final investment decision. A locator selector can safely identify disclosed change/stage candidates without deciding whether those changes alter the investment thesis.
- Existing processor contract already supports candidate-only records through `FundCandidateEvidenceRecord` and `_candidate_missing_field_family()`.
- `current_stage.v1` is already a known family and chapter mapping in both parsed-route and FundDisclosureDocument processor code; the missing piece is only a local selector and mapping entry.
- The S6-A through S6-F accepted chain established that candidate evidence can be useful as locator evidence while staying `candidate_only`, `not_proven`, and `not_ready`.

Why this is not direct implementation:

- Current gate is explicitly a heavy planning gate. It must decide scope, selector semantics, token boundaries, overlap rules, tests, and future write set before code is touched.
- Chapter 5 has high overlap with prior families: product identity, share changes, holdings snapshots, portfolio manager changes, and risk/market/valuation language. Implementing without a plan would force the implementation worker to invent token ownership and guard rules.
- The previous blocked S6 broad plan showed that multi-family or under-specified field extraction is not code-generation-ready. S6-G must stay single-family and locator-only.

Why this is not source truth / readiness:

- Candidate records are only locator candidates from `FundDisclosureDocumentContentIntermediate`; they do not compare against repository-loaded PDF excerpts, reviewed golden answers, Docling/EID HTML render correctness, or manual source truth.
- Candidate excerpt text is not parsed into stage classification, change impact, tracking variable, threshold, or final conclusion.
- No public `EvidenceAnchor`, `StructuredFundDataBundle` value, renderer input, quality gate input, Service/UI/Host/Agent consumption, parser replacement, golden/readiness, PR readiness, or release state changes are authorized.
- `field_correctness_status` and `source_truth_status` remain `not_proven`; `readiness_status` remains `not_ready`; project release/readiness remains `NOT_READY`.

No over-design:

- The plan adds one family-local selector and one mapping entry.
- It does not introduce shared traversal refactors, new schemas, new contracts, new public source kinds, new extractor/facade routes, or cross-family semantic reuse.

## 3. Non-goals / Hard Boundaries

Current planning worker non-goals:

- Do not implement code.
- Do not edit source, tests, README, `docs/design.md`, control docs, implementation evidence, review artifacts, or residual files.
- Do not run implementation tests, ruff, live/network/PDF/provider/LLM commands, Docling conversion, pdfplumber export, repository loading, manual reference review, PR mutation, stage, commit, push, merge, or cleanup.

Future implementation hard boundaries:

- Do not connect candidate evidence to facade/upstream/direct upper-layer consumption.
- Do not modify `contracts.py`, `FundDataExtractor`, extractors, documents repository/source/cache, Service, UI, Host, Agent runner, renderer, quality gate, LLM prompt, provider, or live/network behavior.
- Do not expand `EvidenceAnchor`, `EvidenceSourceKind`, public source provenance schema, failure taxonomy, or public field-family contract.
- Do not populate `FundFieldFamilyResult.value`, `FundFieldFamilyResult.anchors`, `StructuredFundDataBundle`, chapter facts, reports, final judgments, or quality gate decisions from candidate evidence.
- Do not claim source truth, field correctness, parser replacement, full coverage, golden/readiness, release readiness, PR readiness, or production parser behavior changes.
- Do not clean or classify unrelated residuals.
- Do not add selector evidence for any family other than `current_stage.v1`.
- Do not change accepted S6-B/S6-C/S6-D/S6-E/S6-F selector behavior.

Forbidden Chapter 5 reasoning/output concepts:

- Do not use `为什么偏偏是现在`, `下一步最小验证问题`, `接下来最该跟踪`, `变化是否改变前文判断`, `未改变`, `需要重新评估`, `推翻前文判断`, `值得持有`, `需要关注`, `建议替换`, `买入`, `卖出`, or final action labels as locator tokens.
- Do not use market forecast or valuation-external-truth tokens such as `市场走势`, `未来收益`, `估值温度计`, `温度计`, `估值百分位`, `估值分位`, `低估`, `高估`, `便宜`, `昂贵`, or external macro/market prediction wording.
- Do not use Chapter 6 risk-output tokens such as `压力测试`, `核心风险`, `否决`, `一票否决`, `最致命`, `风险等级`, or `清盘风险` as current-stage locator tokens.

## 4. Design / Control Alignment

AGENTS alignment:

- Keeps all document/candidate handling inside Agent-layer `fund_agent/fund`.
- Does not bypass `FundDocumentRepository` or expose parser/source/cache helpers to Service/UI/Host/renderer/quality gate.
- Keeps Docling/pdfplumber/EID HTML render as internal candidate or research input only.
- Does not place explicit parameters in `extra_payload`.
- Preserves evidence traceability by keeping candidate locator metadata explicit and fail-closed.

`docs/design.md` alignment:

- Current design says S6-A introduced internal candidate evidence, S6-B through S6-F added candidate locator selectors, and all candidate evidence remains public `missing`, not source truth, not field correctness, not parser replacement, and not readiness.
- S6-G should update design only after implementation acceptance, and only as current fact wording for `current_stage.v1` candidate locator evidence.

`docs/implementation-control.md` / `docs/current-startup-packet.md` alignment:

- Current active gate is `FundDisclosureDocument S6-G Current Stage Candidate Selector Planning Gate`.
- Gate classification is heavy planning gate.
- S6-F is accepted; next substantive work may only plan `current_stage.v1` candidate-only locator selector while preserving `candidate_only` / `not_proven` / `NOT_READY`.
- This plan does not implement code or mutate control docs.

S6-F controller judgment alignment:

- S6-F accepted `core_risk.v1` candidate locator evidence with public `missing` / `value={}` / `anchors=()`.
- S6-F explicitly left `current_stage.v1` unimplemented.
- S6-G follows the accepted boundary pattern but must not copy S6-F risk tokens or Chapter 6 semantics.

## 5. Affected Files / Future Allowed Write Set

Current planning worker allowed write set:

- `docs/reviews/funddisclosuredocument-s6g-current-stage-candidate-selector-plan-20260619.md`

Current planning worker forbidden write set:

- Every other file.

Future implementation gate allowed write set, only after plan review and controller acceptance:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-s6g-current-stage-candidate-selector-implementation-evidence-20260619.md`

Conditional control docs:

- `docs/implementation-control.md` and `docs/current-startup-packet.md` are not future implementation-worker files for this selector.
- If control docs need S6-G closeout wording, only controller closeout may write them in a separate controller-authorized gate.

Future implementation forbidden write set:

- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extractors/**`
- `fund_agent/fund/documents/**`
- `fund_agent/service/**` or `fund_agent/services/**`
- `fund_agent/host/**`
- `fund_agent/agent/**`
- renderer, quality gate, repository, source, cache, live/network/provider/LLM files
- unrelated docs, residuals, PR metadata, release artifacts

## 6. Selector Design

Selector identity:

- Function: `_select_current_stage_candidate_evidence()`
- Family: `current_stage.v1`
- Limit: `_CURRENT_STAGE_CANDIDATE_LIMIT = 16`
- Excerpt limit: reuse `_CANDIDATE_EXCERPT_LIMIT = 160`
- Result wrapper: `_candidate_missing_field_family("current_stage.v1", source_provenance, current_stage_evidence)` only when evidence is non-empty.

Allowed input:

- Only `FundDisclosureDocumentContentIntermediate` after existing admission and identity checks.
- Non-content `FundDisclosureDocumentIntermediate` returns no `current_stage.v1` candidate evidence and remains `field_family_missing`.

Allowed locator sources:

- `sections`
- `paragraph_blocks`
- `table_blocks`
- `table_blocks[*].cells`

Allowed source fields:

- Section: `heading_text_normalized`, `heading_text_raw`, `heading_path`
- Paragraph: `text_normalized`, `text_raw`, `heading_path`
- Table: `heading_text`, `table_caption_or_nearby_heading`, `heading_path`
- Cell: `cell_text_normalized`, `cell_text`, `row_label_path`, `column_header_path`, `heading_path`

Source path stability:

- Section record: `sections[{section_index}]`
- Paragraph record: `paragraph_blocks[{paragraph_index}]`
- Table record: `table_blocks[{table_index}]`
- Cell record: `table_blocks[{table_index}].cells[{cell_index}]`
- `cell_index` is the original tuple index from `enumerate(table.cells)`.
- Cell scan order is sorted by `(row_index, column_index)`, while `source_field_path` preserves the original tuple index.

Role order:

1. `stage_status`
2. `manager_change`
3. `share_scale_change`
4. `holding_strategy_change`

Source order inside each role:

1. sections
2. paragraph blocks
3. table blocks
4. table cells

Dedupe:

- Deduplicate within `current_stage.v1` by exact `source_field_path`.
- First record wins according to role/source/order scan.
- Do not deduplicate across S6-B/S6-C/S6-D/S6-E/S6-F; each field family owns its candidate evidence independently.

Row locator schema:

- Section: `role={role}; locator=section_id={section.section_id}`
- Paragraph: `role={role}; locator=block_id={paragraph.block_id}`
- Table: `role={role}; locator=table_id={table.table_id}`
- Cell: `role={role}; locator=table_id={cell.table_id}; row={cell.row_index}; column={cell.column_index}`

Candidate evidence fixed fields:

- `field_family_id="current_stage.v1"`
- `source_boundary="candidate_only"`
- `candidate_only=True`
- `field_correctness_status="not_proven"`
- `source_truth_status="not_proven"`
- `parser_replacement_authorized=False`
- `readiness_status="not_ready"`

Excerpt:

- Section/table excerpt: first non-empty normalized/raw heading, caption, or heading path text used for matching.
- Paragraph excerpt: `text_normalized` if non-empty, otherwise `text_raw`.
- Cell excerpt: `cell_text_normalized` if non-empty, otherwise `cell_text`.
- Excerpt is only a locator preview. It must not be parsed as stage, change impact, scale trend, manager-change conclusion, strategy-change conclusion, market forecast, valuation signal, risk conclusion, tracking variable, or final judgment.

## 7. Token / Guard Table

The selector must use Chapter 5 current-stage / key-change disclosure tokens only.

| Role | Strong tokens | Generic tokens requiring source-level guard | Guard tokens | Meaning |
|---|---|---|---|---|
| `stage_status` | `当前阶段`, `所处阶段`, `运作阶段`, `建仓期`, `稳定期`, `膨胀期`, `萎缩期`, `转型期`, `基金运作情况`, `报告期内基金运作` | `阶段`, `状态`, `运作` | `当前阶段`, `所处阶段`, `关键变化`, `基金运作情况`, `报告期内基金投资策略和运作分析`, `报告期内基金运作` | Locator for directly disclosed current-stage / operating-stage context. |
| `manager_change` | `基金经理变更`, `基金经理变动`, `基金经理发生变化`, `新任基金经理`, `基金经理离任`, `离任基金经理`, `基金经理任职`, `基金经理聘任` | `变更`, `变动`, `任职`, `离任`, `聘任` | `基金经理`, `投资经理`, `主要人员情况`, `基金管理人及基金经理情况`, `基金经理情况` | Locator for manager-change disclosure, not manager biography. |
| `share_scale_change` | `基金份额变动`, `份额变动`, `基金份额总额变动`, `报告期期初基金份额总额`, `报告期期末基金份额总额`, `期初基金份额总额`, `期末基金份额总额`, `规模变化`, `规模波动`, `规模剧变`, `大额申购`, `大额赎回`, `净申购`, `净赎回` | `份额`, `规模`, `申购`, `赎回`, `净申购`, `净赎回` | `基金份额变动`, `基金份额总额变动`, `期初基金份额总额`, `期末基金份额总额`, `规模变化`, `规模波动`, `大额申购`, `大额赎回` | Locator for scale/share-flow changes relevant to Chapter 5. |
| `holding_strategy_change` | `投资策略调整`, `策略调整`, `投资策略发生重大变化`, `投资风格发生重大变化`, `资产配置变化`, `持仓结构变化`, `行业配置变化`, `仓位变化`, `前十大重仓股变化`, `投资组合重大变动`, `报告期内基金投资策略和运作分析` | `策略`, `持仓`, `配置`, `仓位`, `行业`, `重仓`, `变化`, `调整`, `变动` | `投资策略`, `投资组合`, `资产配置`, `持仓结构`, `行业配置`, `运作分析`, `重大变化` | Locator for disclosed strategy/holding/portfolio changes. |

Forbidden standalone or owned tokens:

- Product identity only: `基金简介`, `基金基本情况`, `产品概况`, `基金名称`, `基金代码`, `风险收益特征`, `业绩比较基准` must not by themselves create `current_stage.v1` evidence.
- Portfolio manager biography only: `基金经理简介`, `姓名`, `职务`, `职责`, `岗位` must not by themselves create `current_stage.v1` evidence.
- Investor-experience only: `持有人户数`, `户均持有份额`, `机构投资者持有`, `个人投资者持有`, `收益分配`, `分红`, `红利`, `投资者实际收益`, `投资者获得感` must not by themselves create `current_stage.v1` evidence.
- Return/fee only: `净值增长率`, `业绩比较基准收益率`, `管理费`, `托管费`, `销售服务费`, `跟踪误差`, `跟踪偏离度` must not by themselves create `current_stage.v1` evidence.
- Core-risk only: `风险`, `核心风险`, `清盘`, `清盘风险`, `压力测试`, `最大回撤`, `否决`, `一票否决`, `最致命`, `风险等级`, `需要替换`, `值得持有` must not create `current_stage.v1` evidence.
- Market / valuation external-truth tokens: `市场走势`, `未来收益`, `宏观预测`, `估值温度计`, `温度计`, `估值百分位`, `估值分位`, `低估`, `高估`, `便宜`, `昂贵` must not create `current_stage.v1` evidence.

Guard rule:

- Strong tokens may match directly because they are already role-specific Chapter 5 disclosure phrases.
- Generic tokens may match only when the same source-level guard context contains at least one role-specific guard token.
- For sections and tables, guard context is the same source text tuple used for matching.
- For paragraphs, guard context is `text_normalized`, `text_raw`, and `heading_path`.
- For cells, guard context must be parent table `heading_text`, parent `table_caption_or_nearby_heading`, parent `heading_path`, cell `row_label_path`, cell `column_header_path`, and cell `heading_path`.
- Cell generic guard must be role-invariant and fail-closed: do not include `cell_text` or `cell_text_normalized` in the guard context.
- Do not copy S6-E same-cell default guard behavior. Same-cell self-guard is not allowed for broad generic tokens unless a later review finds direct code evidence that requires it; current plan gives no such exception.
- Strong tokens may still match directly from `cell_text` / `cell_text_normalized`.
- A generic token in one source must not pass because another section/table/paragraph/sibling cell contains a guard token.

## 8. Overlap Handling

S6-B `product_essence.v1` overlap:

- `current_stage.v1` must not capture product identity only.
- `profile.basic_identity` is a parsed-route input surface for Chapter 5, but in FundDisclosureDocument candidate selection it is only relevant when source text contains stage/change context.
- Product essence selector tokens, order, limit, gap semantics, row locator, `value`, and `anchors` must remain unchanged.

S6-C `return_attribution.v1` overlap:

- Fee changes are mentioned by Chapter 5 preferred lens, but current parsed-route `current_stage.v1` mapping does not include `profile.fee_schedule`; S6-G must not capture fee schedule tokens.
- Tracking error/performance/fee tokens remain S6-C-owned unless explicitly embedded in a Chapter 5 legal strong phrase in this plan, which currently does not include them.
- Under-coverage of fee-adjustment current-stage evidence is a residual for later field-family mapping or Chapter 5 extraction design.

S6-D `manager_profile.v1` overlap:

- `current_stage.v1` may capture manager-change disclosure (`基金经理变更`, `离任`, `新任`, `聘任`) because current parsed-route Chapter 5 maps to `manager_ownership.portfolio_managers`.
- It must not capture ordinary manager profile or biography table labels (`基金经理简介`, `姓名`, `职务`) without change context.
- S6-D manager-profile selector behavior must remain unchanged.

S6-E `investor_experience.v1` overlap:

- `current_stage.v1` may capture share/scale change disclosure because Chapter 5 asks for size, share and large subscription/redemption changes.
- It must not capture investor-return, holder-structure, distribution, dividend, or investor-experience tokens as current-stage evidence.
- S6-E share-flow/distribution selector behavior must remain unchanged.

S6-F `core_risk.v1` overlap:

- `current_stage.v1` must not capture risk conclusions, risk labels, pressure-test words, liquidation risk, or final action wording.
- If a disclosure fact later needs to be translated into a risk or veto item, that belongs to Chapter 6 / later extraction or analysis gates, not this locator selector.
- S6-F core-risk selector behavior must remain unchanged.

## 9. Future Implementation Shape

Required processor changes:

- Add `_CURRENT_STAGE_CANDIDATE_LIMIT = 16`.
- Add `_CURRENT_STAGE_MATCH_GROUPS` matching the role/token/guard table above.
- Add `_select_current_stage_candidate_evidence()`.
- Add current-stage-local helpers only, following the existing family-local pattern:
  - `_extend_current_stage_section_records()`
  - `_extend_current_stage_paragraph_records()`
  - `_extend_current_stage_table_records()`
  - `_extend_current_stage_cell_records()`
  - `_matches_guarded_current_stage_source()`
  - `_current_stage_cell_guard_context()`
- `_current_stage_cell_guard_context()` must follow the S6-F `_core_risk_cell_guard_context()` role-invariant pattern. Its inclusion tuple is exactly `(table.heading_text, table.table_caption_or_nearby_heading, *table.heading_path, *cell.row_label_path, *cell.column_header_path, *cell.heading_path)`, and it must always exclude `cell_text` and `cell_text_normalized`.
- Add no nested functions or classes.
- Do not refactor S6-B/S6-C/S6-D/S6-E/S6-F helpers into shared traversal helpers in this gate.
- Do not import candidate document concrete classes, Docling, PDF/source/cache helpers, repository helpers, Service/UI/Host, renderer, quality gate, provider, LLM, or network modules.

Required `_field_families_for_intermediate()` shape:

- Keep the current mapping style; do not restore nested ternary logic.
- Add:
  - `current_stage_evidence = _select_current_stage_candidate_evidence(intermediate)`
  - `"current_stage.v1": current_stage_evidence` to `candidate_evidence_by_family`
- Keep existing entries unchanged:
  - `"product_essence.v1": product_essence_evidence`
  - `"return_attribution.v1": return_attribution_evidence`
  - `"manager_profile.v1": manager_profile_evidence`
  - `"investor_experience.v1": investor_experience_evidence`
  - `"core_risk.v1": core_risk_evidence`
- Continue iterating `_FAMILY_ORDER` and using:
  - `_candidate_missing_field_family(family_id, source_provenance, candidate_evidence_by_family[family_id])` when mapped evidence is non-empty.
  - `_missing_field_family(family_id, source_provenance)` when mapped evidence is empty or absent.
- Adding `current_stage.v1` to the mapping must not alter S6-B/S6-C/S6-D/S6-E/S6-F evidence selection or result semantics.
- Update `_field_families_for_intermediate()` docstring to mention S6-B/S6-C/S6-D/S6-E/S6-F/S6-G current wording.

Required result semantics:

- With `current_stage.v1` candidate evidence:
  - `status == "missing"`
  - `extraction_mode == "missing"`
  - `value == {}`
  - `anchors == ()`
  - `gaps[0].gap_code == "candidate_only_not_source_truth"`
  - `candidate_evidence` non-empty and fixed to `current_stage.v1`.
- With no `current_stage.v1` candidate evidence:
  - `candidate_evidence == ()`
  - `gaps[0].gap_code == "field_family_missing"`
- Result-level candidate-boundary behavior remains existing admission behavior:
  - candidate-boundary content input remains `contract_status="blocked"`;
  - non-candidate content stubs may remain `contract_status="missing"`.

## 10. Required Tests

Add focused tests in `tests/fund/processors/test_fund_disclosure_processor.py`.

1. `test_current_stage_selector_adds_candidate_evidence_only`
   - Build content-bearing intermediate with `stage_status`, `manager_change`, `share_scale_change`, and `holding_strategy_change` matches.
   - Assert role set contains exactly those four roles.
   - Assert `status="missing"`, `extraction_mode="missing"`, `value == {}`, `anchors == ()`, and gap `candidate_only_not_source_truth`.

2. `test_current_stage_selector_preserves_candidate_boundary_fields`
   - Assert every record has `field_family_id == "current_stage.v1"`, `candidate_only=True`, `source_boundary="candidate_only"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, and `readiness_status="not_ready"`.
   - Assert no excerpt, source path, role, or numeric-looking text is copied into `family.value`.

3. `test_current_stage_selector_no_match_keeps_field_family_missing`
   - Neutral sections/paragraphs/tables/cells produce no current-stage evidence.
   - Assert gap remains `field_family_missing`.

4. `test_current_stage_selector_preserves_candidate_boundary_blocked_status`
   - Candidate-boundary content with legal current-stage evidence still returns result-level `contract_status="blocked"`.
   - Assert `result.candidate_boundary is boundary`, candidate evidence exists, and public `value` / `anchors` remain empty.

5. `test_current_stage_selector_orders_dedupes_limits_and_truncates`
   - Construct more than 16 candidates across all four roles and all four source types.
   - Assert role order, source order, exact `source_field_path`, first-record-wins dedupe by path, 16-record limit, and `len(record.excerpt) <= 160`.
   - Include out-of-order cells and assert scan order uses `(row_index, column_index)` while `source_field_path` keeps original tuple index.

6. `test_current_stage_selector_requires_context_for_generic_tokens`
   - Generic `阶段` / `状态` / `运作` without stage context does not match.
   - Generic `变更` / `变动` / `任职` / `离任` / `聘任` without manager context does not match.
   - Generic `份额` / `规模` / `申购` / `赎回` without share-scale-change context does not match.
   - Generic `策略` / `持仓` / `配置` / `仓位` / `行业` / `重仓` / `变化` / `调整` / `变动` without holding-strategy-change context does not match.

7. `test_current_stage_selector_allows_generic_tokens_with_source_context`
   - Same generic tokens produce evidence when the same source-level guard context contains the required guard token.
   - Assert produced records use expected `role=...` row locator prefixes.

8. `test_current_stage_selector_blocks_cell_self_guard_for_broad_tokens`
   - A cell whose `cell_text` contains both a broad generic token and a guard-looking token must not pass when parent table heading/caption/path and row/column labels lack role-specific guard.
   - A sibling cell or unrelated table with a guard token must not authorize the generic cell.
   - A cell may pass only when parent table context, row/column labels, or heading path provide the guard.
   - Strong tokens in `cell_text` may still match directly.

9. `test_current_stage_selector_blocks_chapter5_reasoning_output_tokens`
   - Content containing only Chapter 5 reasoning/output words (`为什么偏偏是现在`, `下一步最小验证问题`, `接下来最该跟踪`, `变化是否改变前文判断`, `未改变`, `需要重新评估`, `推翻前文判断`) does not produce evidence.
   - Mixed content containing forbidden reasoning wording plus a legal strong disclosure token produces evidence only from the legal role/source, with no extra record for forbidden wording.

10. `test_current_stage_selector_blocks_chapter6_risk_tokens`
    - Content containing only S6-F/Chapter 6 risk tokens (`风险`, `核心风险`, `清盘风险`, `压力测试`, `最大回撤`, `否决`, `一票否决`, `风险等级`, `需要替换`, `值得持有`) does not produce `current_stage.v1` evidence.
    - Existing `core_risk.v1` behavior must remain covered by its own tests.

11. `test_current_stage_selector_blocks_market_and_valuation_external_tokens`
    - Content containing only `市场走势`, `未来收益`, `估值温度计`, `温度计`, `估值百分位`, `低估`, `高估`, `便宜`, or `昂贵` does not produce current-stage evidence.

12. `test_current_stage_selector_blocks_product_identity_only_overlap`
    - Product identity-only content (`基金简介`, `基金基本情况`, `产品概况`, `基金名称`, `基金代码`, `风险收益特征`, `业绩比较基准`) does not produce current-stage evidence.
    - S6-B `product_essence.v1` selector behavior remains unchanged.

13. `test_current_stage_selector_blocks_manager_biography_only_overlap`
    - Manager biography-only content (`基金经理简介`, `姓名`, `职务`, `职责`, `岗位`) does not produce current-stage evidence.
    - Legal manager-change phrases produce `manager_change`.
    - S6-D `manager_profile.v1` selector behavior remains unchanged.

14. `test_current_stage_selector_blocks_investor_experience_only_overlap`
    - Holder structure / distribution / investor-return-only content does not produce current-stage evidence.
    - Legal share/scale-change phrases produce `share_scale_change`.
    - S6-E `investor_experience.v1` selector behavior remains unchanged.

15. `test_current_stage_selector_blocks_return_fee_only_overlap`
    - NAV, benchmark-return, tracking-error, and fee-only content does not produce current-stage evidence.
    - S6-C `return_attribution.v1` selector behavior remains unchanged.

16. `test_current_stage_selector_preserves_overlap_family_semantics`
    - Build a baseline fixture that produces S6-B/S6-C/S6-D/S6-E/S6-F candidate evidence.
    - The baseline fixture must include S6-E `share_change` strong-token content such as `基金份额变动`, `基金份额总额变动`, `报告期期初基金份额总额`, or `报告期期末基金份额总额`.
    - The overlap case must at minimum cover the same source token class used by S6-E `share_change` and S6-G `share_scale_change`, then compare that S6-E record count, exact `source_field_path` order, gap codes, public `value`, and public `anchors` remain unchanged.
    - Build a second fixture by adding S6-G current-stage legal content.
    - Compare each existing family signature: record count, exact path order, gap codes, public `value`, and public `anchors`.
    - Assert `current_stage.v1` has candidate evidence only in the second fixture.

17. Comparative regression for existing families:
    - Existing S6-A/S6-B/S6-C/S6-D/S6-E/S6-F tests must keep passing.
    - Existing admission and forbidden-boundary tests must keep passing:
      - `test_extract_admits_candidate_boundary_but_returns_blocked`
      - `test_extract_satisfied_returns_fully_gapped_result`
      - `test_extract_satisfied_result_preserves_source_provenance`
      - `test_extract_satisfied_result_candidate_boundary_none`
      - `test_extract_candidate_boundary_result_preserves_candidate_boundary`
      - `test_processor_does_not_import_forbidden_boundaries`

## 11. Validation Commands

Planning-worker validation:

```bash
git diff --check -- docs/reviews/funddisclosuredocument-s6g-current-stage-candidate-selector-plan-20260619.md
```

Future implementation gate validation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
git diff --check
```

Future docs validation if `fund_agent/fund/README.md` and `docs/design.md` are updated:

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Expected validation assertions:

- Focused pytest passes and includes S6-A through S6-F regression coverage plus new S6-G tests.
- Ruff passes for touched code/test files.
- `git diff --check` passes.
- README/design wording, if touched, states current behavior only and does not claim source truth, parser replacement, field correctness, readiness, release, Chapter 5 conclusion, final judgment, or upper-layer consumption.

## 12. Residual Risks With Owner / Destination

- Token-based locator false positives remain possible. Owner: later field-extraction/source-truth evidence gate. Destination: keep `current_stage.v1` public `missing` and candidate-only.
- Fee-adjustment current-stage evidence is under-covered because current parsed-route `current_stage.v1` mapping does not include `profile.fee_schedule`, and fee tokens are S6-C-owned. Owner: later Chapter 5 field-family mapping gate. Destination: separate plan if fee-adjustment locator becomes required.
- Market environment changes are under-covered because this plan forbids market-prediction and valuation-external-truth tokens. Owner: later Chapter 5 analysis/evidence design gate. Destination: separate reviewed gate with explicit source-truth rules.
- Generic stage/change language can be broad. Owner: S6-G implementation. Destination: source-level guard tests and cell self-guard negative tests.
- Manager-change locator overlaps S6-D manager profile. Owner: S6-G implementation. Destination: overlap regression tests preserving S6-D signatures.
- Share/scale-change locator overlaps S6-E investor experience. Owner: S6-G implementation. Destination: overlap regression tests preserving S6-E signatures and blocking holder/distribution-only tokens.
- Holding/strategy-change locator overlaps S6-D holdings/strategy text and S6-F risk/style-drift terms. Owner: S6-G implementation. Destination: overlap regression tests plus Chapter 6 risk token negatives.
- Candidate excerpts may include numeric-looking text such as share totals, subscription/redemption amounts, scale, or dates. Owner: S6-G implementation. Destination: tests asserting no public `value` or `anchors` leak.
- No repository-loaded PDF, Docling, EID HTML render, pdfplumber, live/network, provider, LLM, or manual comparison is run here. Owner: deferred source-truth/readiness gates. Destination: release/readiness remains `NOT_READY`.

No unclassified residual risk blocks this planning artifact because all residuals are assigned to later gates or the future implementation test suite.

## 13. Completion Report Format

Future implementation evidence artifact must report:

- Gate and worker role.
- Changed files.
- Implemented selector roles, role order, source order, dedupe rule, limit, excerpt rule, and row locator schema.
- Explicit statement that public `current_stage.v1` remains `missing`, `value={}`, and `anchors=()`.
- Explicit statement that S6-B/S6-C/S6-D/S6-E/S6-F semantics were not changed.
- Validation commands and exact results.
- Docs decision for `fund_agent/fund/README.md` and `docs/design.md`.
- Residual risks with owner/destination.
- Final boundary: `current_stage.v1` candidate evidence remains `candidate_only` / `not_proven` / `not_ready`; release/readiness remains `NOT_READY`.

Suggested final report wording:

```text
S6-G current_stage.v1 candidate selector implementation completed.
Changed files: ...
Validation:
- uv run pytest tests/fund/processors/test_fund_disclosure_processor.py: ...
- uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py: ...
- git diff --check: ...
Boundary: public current_stage.v1 remains missing/value={}/anchors=(); candidate evidence is candidate_only/not_proven/not_ready; no source truth, parser replacement, upper-layer consumption, readiness or release claim.
Residuals: ...
```

No implementation is authorized by this planning-worker artifact alone.
