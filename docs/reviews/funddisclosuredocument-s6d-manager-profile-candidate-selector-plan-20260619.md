# FundDisclosureDocument S6-D Manager Profile Candidate Selector Plan

## 1. Gate And Recommendation

- Gate: `FundDisclosureDocument S6-D Single-family Candidate Evidence Selector Planning Gate`
- Worker role: planning worker only; no implementation, commit, push, PR, merge, cleanup, or controller judgment.
- Recommended field family: `manager_profile.v1`
- Verdict: proceed with exactly one selector for `manager_profile.v1`.

Rationale:

- Current accepted state already has S6-B `product_essence.v1` and S6-C `return_attribution.v1`; the remaining families are `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1`.
- `manager_profile.v1` maps directly to template Chapter 3 and to the current `ActiveFundAnnualProcessor` mapping surface: `manager_ownership.portfolio_managers`, `manager_ownership.manager_strategy_text`, `manager_ownership.turnover_rate`, `manager_ownership.manager_alignment`, and `holdings_share_change.holdings_snapshot`.
- The existing extractor code already treats the source surface as locator-heavy disclosure from annual report `§4`, `§8`, and `§9`: manager roster headings/tables, strategy/outlook headings, turnover disclosure, manager/employee holding disclosure, and holdings snapshot tables.
- `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` are more compositional: they reuse performance, holder structure, share change, holdings, manager roster, risk text, turnover, and tracking error, and are more likely to imply current state or risk judgment. They are less suitable than `manager_profile.v1` as the next locator-only single-family selector.
- This plan keeps the selector at candidate-only locator level. It does not infer manager quality, consistency, motivation, investor experience, current stage, risk causality, field correctness, source truth, parser replacement, readiness, or release.

## 2. Exact Non-goals

- No selector for `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1`.
- No modification to accepted S6-B `product_essence.v1` or S6-C `return_attribution.v1` semantics.
- No final field extraction into `portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, `holdings_snapshot`, manager tenure, investment style, holding amount, turnover value, holding concentration, or manager consistency.
- No `FundFieldFamilyResult.value` population from candidate evidence.
- No public `EvidenceAnchor` creation and no `FundFieldFamilyResult.anchors` population from candidate evidence.
- No `partial`, `accepted`, `satisfied`, `direct`, `derived`, or `estimated` status/mode from candidate evidence.
- No `FundDataExtractor`, facade projection, `StructuredFundDataBundle`, renderer, quality gate, Service, UI, Host, Agent runner, repository, source, cache, live/network, PDF, Docling conversion, pdfplumber export, provider, or LLM change.
- No contract/schema expansion in `contracts.py`; the S6-A candidate evidence contract is sufficient.
- No `EvidenceSourceKind` or public `EvidenceAnchor.source_kind` expansion.
- No source truth, field correctness, parser replacement, golden, readiness, release, PR state, or upper-layer consumption claim.
- No cleanup, deletion, staging, or classification of unrelated untracked residuals.

## 3. Selector Contract

The S6-D selector is a deterministic locator selector, not a value extractor.

Family:

- `manager_profile.v1`

Allowed input protocol:

- `FundDisclosureDocumentContentIntermediate` only after existing admission and identity checks pass.
- If the intermediate is only `FundDisclosureDocumentIntermediate` and not content-bearing, `manager_profile.v1` remains `field_family_missing`.

Allowed locator sources:

- `sections`
- `paragraph_blocks`
- `table_blocks`
- `table_blocks[*].cells`

Candidate source fields:

- Section fields: `heading_text_normalized`, `heading_text_raw`, `heading_path`
- Paragraph fields: `text_normalized`, `text_raw`, `heading_path`
- Table fields: `heading_text`, `table_caption_or_nearby_heading`, `heading_path`
- Cell fields: `cell_text_normalized`, `cell_text`, `row_label_path`, `column_header_path`, `heading_path`

Match groups:

| Role | Candidate text fields | Match tokens | Guard | Evidence role |
|---|---|---|---|---|
| `portfolio_managers` | section/table heading, heading path, row/column labels, cell text | `基金经理简介`, `基金管理人及基金经理情况`, `基金经理情况`, `主要人员情况`, `姓名`, `职务`, `职责`, `岗位`, `任职日期`, `任职时间`, `聘任日期`, `起始日期`, `离任日期`, `离任时间`, `终止日期` | Generic header tokens (`姓名`, `职务`, `职责`, `岗位`, date tokens) require same source heading path, table heading/caption, or section heading to include `基金经理` or `管理人`; title tokens need no extra guard. | locator for manager roster / tenure table candidate |
| `manager_strategy_text` | section heading, heading path, paragraph text, table heading/caption, row/column labels, cell text | `报告期内基金投资策略和运作分析`, `投资策略和运作分析`, `投资策略`, `运作分析`, `管理人对宏观经济、证券市场及行业走势的简要展望`, `后市展望`, `市场展望` | No value parsing; text block location only. | locator for manager strategy / outlook disclosure candidate |
| `turnover_rate` | section heading, heading path, paragraph text, table heading/caption, row/column labels, cell text | `换手率`, `股票换手率`, `报告期内股票换手率`, `换手率口径`, `换手率计算口径` | Do not match standalone `交易`, `买入`, `卖出`, or `股票` tokens. | locator for turnover behavior candidate |
| `manager_alignment` | section heading, heading path, paragraph text, table heading/caption, row/column labels, cell text | `基金经理持有本基金`, `基金经理持有份额`, `本基金基金经理持有本开放式基金`, `基金经理持有`, `基金管理人所有从业人员持有本基金`, `从业人员持有本基金`, `从业人员持有`, `持有本基金` | `持有本基金` requires same source text or heading path to include `基金经理`, `从业人员`, or `基金管理人`. | locator for manager/employee holding alignment candidate |
| `holdings_snapshot` | section heading, heading path, paragraph text, table heading/caption, row/column labels, cell text | `报告期末按行业分类的股票投资组合`, `期末按行业分类的股票投资组合`, `报告期末按公允价值占基金资产净值比例大小排序的前十名股票投资明细`, `前十名股票投资明细`, `报告期末基金资产组合情况`, `持仓集中度` | Do not infer concentration or style; locator only. | locator for actual holdings behavior candidate |

Do not add broad or interpretive tokens in S6-D:

- Do not add `靠谱`, `能力`, `风格稳定`, `言行一致`, `漂移`, `动机`, `价值`, `成长`, `持仓`, `配置`, `风险`, or `收益` as standalone tokens.
- Reason: these terms either require semantic judgment or are too broad for a locator-only gate.

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

1. Iterate roles in this order: `portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, `holdings_snapshot`.
2. Within each role, scan sources in this order: sections, paragraph blocks, table blocks, table cells.
3. Sections, paragraphs, and tables preserve tuple order.
4. Cells are sorted by `(row_index, column_index)`.

Dedupe rule:

- Deduplicate within `manager_profile.v1` by exact `source_field_path`.
- Keep the first record for a path according to the ordering rule.
- Do not deduplicate across `product_essence.v1`, `return_attribution.v1`, and `manager_profile.v1`; each field family owns its own candidate evidence set.

Limit rule:

- Add `_MANAGER_PROFILE_CANDIDATE_LIMIT = 16`.
- Keep at most 16 records for `manager_profile.v1`.
- If more than 16 candidate records exist, preserve the ordering rule and truncate after 16.

Excerpt rule:

- Keep existing `_CANDIDATE_EXCERPT_LIMIT = 160`.
- Section/table excerpt: first non-empty normalized/raw heading, caption, or heading-path text used for matching.
- Paragraph excerpt: `text_normalized` if non-empty, otherwise `text_raw`.
- Cell excerpt: `cell_text_normalized` if non-empty, otherwise `cell_text`.
- Excerpt is a candidate locator preview only; it is not source truth and must not be parsed as a field value.

Candidate evidence fields:

- `field_family_id="manager_profile.v1"`
- `source_boundary="candidate_only"`
- `candidate_only=True`
- `field_correctness_status="not_proven"`
- `source_truth_status="not_proven"`
- `parser_replacement_authorized=False`
- `readiness_status="not_ready"`
- `row_locator` format should mirror S6-B/S6-C: `role={role}; locator=...`

## 5. Implementation Design For Later Gate

The later implementation gate should keep the change local to `FundDisclosureDocumentProcessor`.

Required processor behavior:

- In `_field_families_for_intermediate()`, select:
  - existing `product_essence.v1` candidate evidence;
  - existing `return_attribution.v1` candidate evidence;
  - new `manager_profile.v1` candidate evidence.
- For `manager_profile.v1` with non-empty candidate evidence:
  - return `_candidate_missing_field_family("manager_profile.v1", source_provenance, manager_profile_evidence)`.
- For `manager_profile.v1` with empty candidate evidence:
  - keep existing `_missing_field_family("manager_profile.v1", source_provenance)`.
- `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` stay fully missing.

Required result semantics:

- `manager_profile.v1.status == "missing"`
- `manager_profile.v1.extraction_mode == "missing"`
- `manager_profile.v1.value == {}`
- `manager_profile.v1.anchors == ()`
- `manager_profile.v1.gaps[0].gap_code == "candidate_only_not_source_truth"` only when candidate evidence exists.
- `manager_profile.v1.gaps[0].gap_code == "field_family_missing"` when no candidate evidence exists.
- Overall result-level candidate-boundary status remains existing admission behavior:
  - concrete candidate-boundary input remains `contract_status="blocked"`;
  - non-candidate content stubs may remain `contract_status="missing"`.

Required helper structure:

- Add `_MANAGER_PROFILE_MATCH_GROUPS` with role configs matching this plan.
- Add `_MANAGER_PROFILE_CANDIDATE_LIMIT`.
- Add `_select_manager_profile_candidate_evidence()` as the manager-profile wrapper.
- The implementation may introduce small private shared helper functions for source scanning, token matching, guard evaluation, record construction, and limit handling if needed to avoid a third copy of S6-B/S6-C traversal logic. Any shared helper must preserve existing S6-B/S6-C order, paths, excerpts, limits, and tests.
- Do not add nested functions/classes.
- Do not import candidate document concrete classes, Docling, PDF/source/cache helpers, repository helpers, Service/UI/Host, renderer, quality gate, provider, LLM, or network modules.

## 6. Allowed And Forbidden Write Set

Current planning worker allowed write set:

- `docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-plan-20260619.md`

Current planning worker forbidden write set:

- Every file except the plan artifact above.
- No commit, push, PR, merge, stage, cleanup, or residual disposition.

Future implementation gate allowed write set, only after plan review and controller judgment:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`

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

1. `test_manager_profile_selector_adds_candidate_evidence_only`
   - Content-bearing intermediate with §4 manager roster, §4 strategy/outlook, §8 turnover/holdings, and §9 manager holding locator text yields `manager_profile.v1.candidate_evidence`.
   - Assert `status="missing"`, `extraction_mode="missing"`, `value == {}`, `anchors == ()`, and local gap `candidate_only_not_source_truth`.

2. `test_manager_profile_selector_preserves_candidate_boundary_fields`
   - Every manager profile candidate record has `candidate_only=True`, `source_boundary="candidate_only"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, and `readiness_status="not_ready"`.

3. `test_manager_profile_selector_keeps_other_remaining_families_without_candidate_evidence`
   - With manager-profile matching content, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain `field_family_missing` with empty `candidate_evidence`.
   - `product_essence.v1` and `return_attribution.v1` remain governed only by their own S6-B/S6-C matching content.

4. `test_manager_profile_selector_no_match_keeps_field_family_missing`
   - Neutral content produces no manager-profile evidence and preserves `field_family_missing`.

5. `test_manager_profile_selector_preserves_candidate_boundary_blocked_status`
   - Candidate-boundary input with manager profile candidate evidence still returns result-level `contract_status="blocked"`.

6. `test_manager_profile_selector_orders_dedupes_limits_and_truncates`
   - Construct more than 16 candidate paths.
   - Assert role order, source order, exact `source_field_path`, first-record-wins dedupe, 16-record limit, and `excerpt` length <= 160.

7. `test_manager_profile_selector_requires_context_for_generic_roster_and_holding_tokens`
   - Generic `姓名` / `职务` / `任职日期` content without `基金经理` or `管理人` context must not produce `portfolio_managers` evidence.
   - Generic `持有本基金` content without `基金经理` / `从业人员` / `基金管理人` context must not produce `manager_alignment` evidence.

8. Existing S6-A tests must keep passing:
   - admission protocol remains content-free;
   - candidate evidence rejects source-truth/readiness escape;
   - candidate evidence does not satisfy partial anchor requirement.

9. Existing S6-B and S6-C selector tests must keep passing unchanged.

10. Existing static import-boundary test, if present in this file, must continue proving no forbidden imports in `fund_disclosure_processor.py`.

## 8. Validation Matrix

Planning-worker artifact validation:

```bash
git diff --check -- docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-plan-20260619.md
```

Future implementation gate must run:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
git diff --check
```

If `fund_agent/fund/README.md` and `docs/design.md` are updated:

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Expected assertions:

- Focused pytest passes and includes S6-A/S6-B/S6-C regression coverage.
- Ruff passes for touched code/test files.
- `git diff --check` passes.
- README/design wording, if touched, states current behavior only and does not claim source truth, parser replacement, readiness, release, or upper-layer consumption.

## 9. Acceptance Criteria

S6-D plan acceptance requires:

- Exactly one remaining field family is selected: `manager_profile.v1`.
- The plan is code-generation-ready: implementation path, roles, token mapping, guards, source fields, source paths, order, dedupe, limit, excerpt, write set, tests, validation, and result semantics are explicit.
- Candidate evidence remains `candidate-only`, `not_proven`, and `not_ready`.
- Public `value` and public `EvidenceAnchor` remain empty.
- No `partial`, `accepted`, `satisfied`, `direct`, `derived`, or `estimated` state is introduced by candidate evidence.
- `FundDataExtractor`, repository/source/cache/live behavior, public schema, and upper layers remain unchanged.
- Existing S6-A/S6-B/S6-C behavior is preserved by regression tests.
- Release/readiness remains `NOT_READY`.

Future S6-D implementation acceptance additionally requires:

- Focused pytest passes.
- Ruff passes for touched code/test files.
- `git diff --check` passes.
- Fund README/design sync, if touched, preserves candidate-only wording and current production boundaries.

## 10. Residual Risks

- Token false positives remain possible because locator matching does not prove semantic field correctness. Owner: later field-extraction/source-truth gate; S6-D mitigates by keeping public status `missing`.
- Manager roster generic headers such as `姓名` and `职务` are broad. Owner: S6-D implementation must enforce the context guard and test negative cases.
- `holdings_snapshot` locators overlap with current-stage and core-risk future selectors. Owner: later field-family selector gates; S6-D records only manager behavior locators and does not infer risk/current-stage conclusions.
- `turnover_rate` is behavior/cost-adjacent and may overlap future core-risk selectors. Owner: later selector design; S6-D keeps family-local dedupe and no cross-family dedupe.
- Candidate excerpts can contain numeric-looking text such as dates, shares, percentages, or turnover values. Owner: S6-D implementation must keep excerpts out of `value` and `anchors`; tests must assert no value leak.
- Refactoring traversal helpers could regress S6-B/S6-C selectors. Owner: S6-D implementation test suite; existing S6-B/S6-C tests must remain unchanged and pass.
- The selector does not prove comparator correctness against repository-loaded PDF, Docling, EID HTML render, or pdfplumber. Owner: deferred evidence/source-truth gates; release/readiness stays `NOT_READY`.

## 11. Next Gate

If this plan passes adversarial plan review and controller judgment, the next gate should be:

`FundDisclosureDocument S6-D Manager Profile Candidate Selector Implementation Gate`

No implementation is authorized by this planning-worker artifact alone.
