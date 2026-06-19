# FundDisclosureDocument S6-E Investor Experience Candidate Selector Plan

## 1. Gate And Recommendation

- Gate: `FundDisclosureDocument S6-E Investor Experience Candidate Selector Planning Gate`
- Work unit: `Docling architecture reorientation / Fund Processor-Extractor route`
- Worker role: planning worker only; no implementation, source/test/design/control edit, commit, push, PR, merge, cleanup, or controller judgment.
- Recommended field family: `investor_experience.v1`
- Verdict: proceed with exactly one selector for `investor_experience.v1`.

Rationale from first principles:

- The current accepted state already has candidate-only locator selectors for `product_essence.v1`, `return_attribution.v1`, and `manager_profile.v1`. S6-D implementation controller judgment leaves exactly three remaining choices for S6-E: `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1`.
- `investor_experience.v1` is the next lowest-risk locator-only family because its current `ActiveFundAnnualProcessor` mapping has a narrow primary surface: `performance.investor_return`, `manager_ownership.holder_structure`, and `holdings_share_change.share_change`.
- `current_stage.v1` is less suitable for this gate because its current mapping is compositional and mostly redundant over other primary families: `profile.basic_identity`, `holdings_share_change.share_change`, `holdings_share_change.holdings_snapshot`, and `manager_ownership.portfolio_managers`. Selecting it now would likely re-label already-owned product, holdings, and manager locators as a stage conclusion.
- `core_risk.v1` is less suitable because it is risk-judgment oriented and overlaps heavily with other accepted or primary surfaces: `profile.risk_characteristic_text`, `manager_ownership.holder_structure`, `manager_ownership.turnover_rate`, `holdings_share_change.holdings_snapshot`, and `performance.tracking_error`. A locator-only selector could easily be mistaken for risk causality or final risk evidence.
- `investor_experience.v1` still has overlap risk with return attribution and manager/profile tables, but it can be bounded by investor-specific, holder-structure, share-change, subscription/redemption, and distribution locator roles. This is narrower than selecting a current-stage or core-risk family that inherently asks for synthesis.
- The selector remains candidate-only locator evidence. It does not infer actual investor return, behavior loss, investor trading behavior, current stage, risk causality, field correctness, source truth, parser replacement, readiness, release, or upper-layer consumption.

## 2. Exact Non-goals

- No selector for `current_stage.v1` or `core_risk.v1`.
- No modification to accepted S6-B `product_essence.v1`, S6-C `return_attribution.v1`, or S6-D `manager_profile.v1` semantics.
- No final field extraction into `investor_return`, `holder_structure`, `share_change`, subscription/redemption metrics, distribution metrics, weighted average investor return, profitable investor ratio, behavior loss, fund-holder behavior, or any Chapter 4 conclusion.
- No parsing of candidate excerpts into numeric values.
- No `FundFieldFamilyResult.value` population from candidate evidence.
- No public `EvidenceAnchor` creation and no `FundFieldFamilyResult.anchors` population from candidate evidence.
- No `partial`, `accepted`, `satisfied`, `direct`, `derived`, or `estimated` status/mode from candidate evidence.
- No `FundDataExtractor`, facade projection, `StructuredFundDataBundle`, renderer, quality gate, Service, UI, Host, Agent runner, repository, source, cache, live/network, PDF, Docling conversion, pdfplumber export, provider, or LLM change.
- No contract/schema expansion in `contracts.py`; the S6-A candidate evidence contract is sufficient.
- No `EvidenceSourceKind` or public `EvidenceAnchor.source_kind` expansion.
- No source truth, field correctness, parser replacement, golden, readiness, release, PR state, or upper-layer consumption claim.
- No cleanup, deletion, staging, or classification of unrelated untracked residuals.

## 3. Selector Contract

The S6-E selector is a deterministic locator selector, not a value extractor.

Family:

- `investor_experience.v1`

Mapping to current `ActiveFundAnnualProcessor` field surface, as locator roles only:

| Locator role | Current processor field surface | Template chapter | Meaning in this gate |
|---|---|---|---|
| `investor_return` | `performance.investor_return` | 4 | Locator for investor-return / investor-experience disclosure only. |
| `holder_structure` | `manager_ownership.holder_structure` | 4 | Locator for fund-holder structure disclosure only. |
| `share_change` | `holdings_share_change.share_change` | 4 | Locator for share-change disclosure only. |
| `subscription_redemption` | `holdings_share_change.share_change` | 4 | Locator for申购/赎回 rows or paragraphs inside share-change disclosure only. |
| `income_distribution` | `performance.investor_return` | 4 | Locator for dividend / income distribution context only; no new public field is added. |

Allowed input protocol:

- `FundDisclosureDocumentContentIntermediate` only after existing admission and identity checks pass.
- If the intermediate is only `FundDisclosureDocumentIntermediate` and not content-bearing, `investor_experience.v1` remains `field_family_missing`.

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

| Role | Strong tokens | Generic tokens requiring guard | Guard tokens | Evidence role |
|---|---|---|---|---|
| `investor_return` | `投资者实际收益`, `加权平均投资者收益率`, `盈利投资者占比`, `投资者回报`, `投资者获得感`, `行为损益` | `实际收益`, `盈利占比` | `投资者`, `持有人`, `基金份额持有人` | locator for investor-return / experience disclosure candidate |
| `holder_structure` | `基金份额持有人信息`, `基金份额持有人结构`, `基金份额持有人情况`, `持有人户数`, `户均持有份额`, `机构投资者持有`, `个人投资者持有` | `机构投资者`, `个人投资者`, `持有人`, `户数` | `基金份额持有人`, `持有人结构`, `持有人信息`, `持有人情况` | locator for holder-structure disclosure candidate |
| `share_change` | `基金份额变动`, `份额变动`, `基金份额总额变动`, `报告期期初基金份额总额`, `报告期期末基金份额总额`, `期初基金份额总额`, `期末基金份额总额` | `期初份额`, `期末份额`, `份额总额` | `基金份额`, `份额变动`, `基金份额总额变动` | locator for share-change disclosure candidate |
| `subscription_redemption` | `基金总申购份额`, `基金总赎回份额`, `总申购份额`, `总赎回份额`, `本期申购`, `本期赎回`, `申购赎回` | `申购`, `赎回`, `净申购`, `净赎回` | `份额`, `基金份额`, `份额变动`, `基金总申购`, `基金总赎回` | locator for subscription / redemption disclosure candidate |
| `income_distribution` | `基金收益分配`, `收益分配`, `利润分配`, `收益分配情况`, `基金利润分配`, `每10份基金份额分红数` | `分红`, `红利` | `收益分配`, `利润分配`, `基金份额`, `分配` | locator for dividend / income distribution disclosure candidate |

Do not add broad or interpretive tokens in S6-E:

- Do not add `收益`, `投资者`, `份额`, `持有人`, `申购`, `赎回`, `分红`, `上涨`, `下跌`, `追涨`, `抄底`, `体验`, `获得感`, `行为`, `亏损`, or `盈利` as standalone unguarded tokens.
- Do not add `净值增长率`, `业绩比较基准`, `基准收益率`, `跟踪误差`, `管理费`, `托管费`, `换手率`, `基金经理`, or `持仓` as investor-experience tokens. These are already owned by S6-C/S6-D or by future non-S6-E families.
- Reason: these terms either belong to accepted selector surfaces, require semantic judgment, or are too broad for a locator-only gate.

Guard rule:

- Strong tokens may match directly.
- Generic tokens may match only when the same source-level guard context also contains at least one guard token for that role.
- For section and table records, guard context is the same source text tuple used for matching: headings, captions, and heading path.
- For paragraph records, guard context is `text_normalized`, `text_raw`, and `heading_path`.
- For cell records, guard context is parent table `heading_text`, `table_caption_or_nearby_heading`, parent `heading_path`, cell `row_label_path`, cell `column_header_path`, cell `cell_text_normalized`, cell `cell_text`, and cell `heading_path`.
- A generic token in a cell must not pass only because a different table elsewhere has a guard token.

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

1. Iterate roles in this order: `investor_return`, `holder_structure`, `share_change`, `subscription_redemption`, `income_distribution`.
2. Within each role, scan sources in this order: sections, paragraph blocks, table blocks, table cells.
3. Sections, paragraphs, and tables preserve tuple order.
4. Cells are sorted by `(row_index, column_index)`.

Dedupe rule:

- Deduplicate within `investor_experience.v1` by exact `source_field_path`.
- Keep the first record for a path according to the ordering rule.
- Do not deduplicate across `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1`, and `investor_experience.v1`; each field family owns its own candidate evidence set.

Limit rule:

- Add `_INVESTOR_EXPERIENCE_CANDIDATE_LIMIT = 16`.
- Keep at most 16 records for `investor_experience.v1`.
- If more than 16 candidate records exist, preserve the ordering rule and truncate after 16.

Excerpt rule:

- Reuse `_CANDIDATE_EXCERPT_LIMIT = 160`.
- Section/table excerpt: first non-empty normalized/raw heading, caption, or heading-path text used for matching.
- Paragraph excerpt: `text_normalized` if non-empty, otherwise `text_raw`.
- Cell excerpt: `cell_text_normalized` if non-empty, otherwise `cell_text`.
- Excerpt is a candidate locator preview only; it is not source truth and must not be parsed as a field value.

Candidate evidence fields:

- `field_family_id="investor_experience.v1"`
- `source_boundary="candidate_only"`
- `candidate_only=True`
- `field_correctness_status="not_proven"`
- `source_truth_status="not_proven"`
- `parser_replacement_authorized=False`
- `readiness_status="not_ready"`
- `row_locator` format must mirror S6-B/S6-C/S6-D: `role={role}; locator=...`

## 5. Implementation Design For Later Gate

The later implementation gate should keep the change local to `FundDisclosureDocumentProcessor`.

Required processor behavior:

- Add `_INVESTOR_EXPERIENCE_MATCH_GROUPS` with role configs matching this plan.
- Add `_INVESTOR_EXPERIENCE_CANDIDATE_LIMIT = 16`.
- Add `_select_investor_experience_candidate_evidence()` as the investor-experience wrapper.
- In `_field_families_for_intermediate()`, select:
  - existing `product_essence.v1` candidate evidence;
  - existing `return_attribution.v1` candidate evidence;
  - existing `manager_profile.v1` candidate evidence;
  - new `investor_experience.v1` candidate evidence.
- For `investor_experience.v1` with non-empty candidate evidence:
  - return `_candidate_missing_field_family("investor_experience.v1", source_provenance, investor_experience_evidence)`.
- For `investor_experience.v1` with empty candidate evidence:
  - keep existing `_missing_field_family("investor_experience.v1", source_provenance)`.
- `current_stage.v1` and `core_risk.v1` stay fully missing with no candidate evidence.

Required result semantics:

- `investor_experience.v1.status == "missing"`
- `investor_experience.v1.extraction_mode == "missing"`
- `investor_experience.v1.value == {}`
- `investor_experience.v1.anchors == ()`
- `investor_experience.v1.gaps[0].gap_code == "candidate_only_not_source_truth"` only when candidate evidence exists.
- `investor_experience.v1.gaps[0].gap_code == "field_family_missing"` when no candidate evidence exists.
- Overall result-level candidate-boundary status remains existing admission behavior:
  - concrete candidate-boundary input remains `contract_status="blocked"`;
  - non-candidate content stubs may remain `contract_status="missing"`.
- Other accepted field families remain governed only by their own S6-B/S6-C/S6-D matching content.

Required helper structure:

- The implementation may introduce small private shared helper functions for guarded source scanning, token matching, record construction, and limit handling if needed to avoid a fourth copy of traversal logic.
- Any shared helper must preserve existing S6-B/S6-C/S6-D order, paths, excerpts, limits, row locators, guard behavior, and tests.
- Do not add nested functions/classes.
- Do not import candidate document concrete classes, Docling, PDF/source/cache helpers, repository helpers, Service/UI/Host, renderer, quality gate, provider, LLM, or network modules.

## 6. Allowed And Forbidden Write Set

Current planning worker allowed write set:

- `docs/reviews/funddisclosuredocument-s6e-investor-experience-candidate-selector-plan-20260619.md`

Current planning worker forbidden write set:

- Every file except the plan artifact above.
- No source, test, docs/design, docs/control, README, implementation evidence, commit, push, PR, merge, stage, cleanup, or residual disposition.

Future implementation gate allowed write set, only after plan review and controller judgment:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-s6e-investor-experience-candidate-selector-implementation-evidence-20260619.md`

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

1. `test_investor_experience_selector_adds_candidate_evidence_only`
   - Content-bearing intermediate with investor-return, holder-structure, share-change, subscription/redemption, and income-distribution locator text yields `investor_experience.v1.candidate_evidence`.
   - Assert role set contains exactly `role=investor_return`, `role=holder_structure`, `role=share_change`, `role=subscription_redemption`, and `role=income_distribution`.
   - Assert `status="missing"`, `extraction_mode="missing"`, `value == {}`, `anchors == ()`, and local gap `candidate_only_not_source_truth`.

2. `test_investor_experience_selector_preserves_candidate_boundary_fields`
   - Every investor-experience candidate record has `field_family_id == "investor_experience.v1"`, `candidate_only=True`, `source_boundary="candidate_only"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, and `readiness_status="not_ready"`.
   - Assert no `source_field_path` is copied into `family.value`.

3. `test_investor_experience_selector_keeps_other_families_without_candidate_evidence`
   - With only investor-experience matching content, `current_stage.v1` and `core_risk.v1` remain `field_family_missing` with empty `candidate_evidence`.
   - `product_essence.v1`, `return_attribution.v1`, and `manager_profile.v1` remain governed only by their own S6-B/S6-C/S6-D matching content; investor-experience tokens must not populate those families.

4. `test_investor_experience_selector_no_match_keeps_field_family_missing`
   - Neutral content produces no investor-experience evidence and preserves `field_family_missing`.

5. `test_investor_experience_selector_preserves_candidate_boundary_blocked_status`
   - Candidate-boundary input with investor-experience candidate evidence still returns result-level `contract_status="blocked"`.
   - Assert `result.candidate_boundary is boundary`, `family.candidate_evidence` is non-empty, and `family.value == {}` / `family.anchors == ()`.

6. `test_investor_experience_selector_orders_dedupes_limits_and_truncates`
   - Construct more than 16 candidate paths across all five roles.
   - Assert role order, source order, exact `source_field_path`, first-record-wins dedupe by path, 16-record limit, and `len(record.excerpt) <= 160`.
   - Include out-of-order cells and assert scan order uses `(row_index, column_index)` while `source_field_path` keeps original tuple index.

7. `test_investor_experience_selector_requires_context_for_generic_tokens`
   - Generic `实际收益` without `投资者` / `持有人` / `基金份额持有人` context must not produce `investor_return` evidence.
   - Generic `机构投资者` / `个人投资者` / `持有人` / `户数` without holder-structure context must not produce `holder_structure` evidence.
   - Generic `期初份额` / `期末份额` / `份额总额` without fund-share context must not produce `share_change` evidence.
   - Generic `申购` / `赎回` / `净申购` / `净赎回` without fund-share/share-change context must not produce `subscription_redemption` evidence.
   - Generic `分红` / `红利` without distribution or fund-share context must not produce `income_distribution` evidence.

8. `test_investor_experience_selector_allows_generic_tokens_with_context`
   - Generic tokens above must produce candidate evidence when same source-level guard context contains the required guard token for that role.
   - Assert produced records use the expected `role=...` row locator prefix.

9. `test_investor_experience_selector_does_not_capture_return_or_manager_owned_tokens`
   - Content containing only S6-C/S6-D-owned tokens such as `净值增长率`, `业绩比较基准`, `跟踪误差`, `管理费`, `换手率`, `基金经理`, and `前十名股票投资明细` must not produce `investor_experience.v1` evidence.
   - Existing S6-C/S6-D families may still match their own tokens if those tests intentionally include them; this test should assert only that investor experience stays empty for those tokens.

Existing regression tests that must keep passing, with expectation updates only where S6-E makes the old wording stale:

- `test_candidate_evidence_record_rejects_unsafe_boundary_fields`
- `test_candidate_evidence_record_requires_locator_identity`
- `test_missing_field_family_can_carry_candidate_evidence_without_value_leak`
- `test_candidate_evidence_does_not_satisfy_partial_anchor_requirement`
- `test_product_essence_selector_adds_candidate_evidence_only`
- `test_product_essence_selector_leaves_other_families_without_candidate_evidence`
- `test_product_essence_selector_no_match_keeps_field_family_missing`
- `test_product_essence_selector_preserves_candidate_boundary_blocked_status`
- `test_return_attribution_selector_adds_candidate_evidence_only`
- `test_return_attribution_selector_preserves_candidate_boundary_fields`
- `test_return_attribution_selector_keeps_other_unimplemented_families_without_candidate_evidence`
- `test_return_attribution_selector_no_match_keeps_field_family_missing`
- `test_return_attribution_selector_preserves_candidate_boundary_blocked_status`
- `test_return_attribution_selector_orders_dedupes_limits_and_truncates`
- `test_manager_profile_selector_adds_candidate_evidence_only`
- `test_manager_profile_selector_preserves_candidate_boundary_fields`
- `test_manager_profile_selector_keeps_other_remaining_families_without_candidate_evidence`
- `test_manager_profile_selector_no_match_keeps_field_family_missing`
- `test_manager_profile_selector_preserves_candidate_boundary_blocked_status`
- `test_manager_profile_selector_orders_dedupes_limits_and_truncates`
- `test_manager_profile_selector_requires_context_for_generic_roster_and_holding_tokens`
- `test_manager_profile_selector_allows_generic_tokens_with_context`
- `test_extract_admits_candidate_boundary_but_returns_blocked`
- `test_extract_satisfied_returns_fully_gapped_result`
- `test_extract_satisfied_result_preserves_source_provenance`
- `test_extract_satisfied_result_candidate_boundary_none`
- `test_extract_candidate_boundary_result_preserves_candidate_boundary`
- `test_processor_does_not_import_forbidden_boundaries`

## 8. Validation Matrix

Planning-worker artifact validation:

```bash
git diff --check -- docs/reviews/funddisclosuredocument-s6e-investor-experience-candidate-selector-plan-20260619.md
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

- Focused pytest passes and includes S6-A/S6-B/S6-C/S6-D regression coverage plus new S6-E tests.
- Ruff passes for touched code/test files.
- `git diff --check` passes.
- README/design wording, if touched, states current behavior only and does not claim source truth, parser replacement, field correctness, readiness, release, or upper-layer consumption.

## 9. Acceptance Criteria

S6-E plan acceptance requires:

- Exactly one remaining field family is selected: `investor_experience.v1`.
- The plan explains why `investor_experience.v1` is a safer next locator-only selector than `current_stage.v1` and `core_risk.v1`.
- The plan is code-generation-ready: implementation path, role mapping, tokens, guards, source fields, source paths, order, dedupe, limit, excerpt, write set, tests, validation, and result semantics are explicit.
- Candidate evidence remains `candidate-only`, `not_proven`, and `not_ready`.
- Public `value` and public `EvidenceAnchor` remain empty.
- No `partial`, `accepted`, `satisfied`, `direct`, `derived`, or `estimated` state is introduced by candidate evidence.
- `FundDataExtractor`, repository/source/cache/live behavior, public schema, and upper layers remain unchanged.
- Existing S6-A/S6-B/S6-C/S6-D behavior is preserved by regression tests.
- Release/readiness remains `NOT_READY`.

Future S6-E implementation acceptance additionally requires:

- Focused pytest passes.
- Ruff passes for touched code/test files.
- `git diff --check` passes.
- Fund README/design sync, if touched, preserves candidate-only wording and current production boundaries.
- Implementation evidence artifact records exact changed files, validation results, docs decision, residual risks, and final `NOT_READY` boundary.

## 10. Residual Risks

- Token false positives remain possible because locator matching does not prove semantic field correctness. Owner: later field-extraction/source-truth gate; S6-E mitigates by keeping public status `missing`.
- `investor_return` locators may overlap conceptually with S6-C return attribution. Owner: S6-E implementation must avoid S6-C-owned standalone performance/fee/tracking-error tokens and test the negative case.
- `holder_structure` locators may overlap with future `core_risk.v1` informational risk surfaces. Owner: future core-risk selector planning; S6-E records only investor-experience locators and does not infer risk.
- `share_change` and `subscription_redemption` locators may overlap with future `current_stage.v1`. Owner: future current-stage selector planning; S6-E records only share-flow locators and does not infer stage.
- `income_distribution` is not a distinct current `ActiveFundAnnualProcessor` public field. Owner: later field-family extraction design; S6-E treats it only as Chapter 4 investor-experience context under locator evidence.
- Candidate excerpts can contain numeric-looking text such as percentages, shares, dividends,申购/赎回 quantities, or holder counts. Owner: S6-E implementation must keep excerpts out of `value` and `anchors`; tests must assert no value leak.
- Refactoring traversal helpers could regress S6-B/S6-C/S6-D selectors. Owner: S6-E implementation test suite; existing S6-B/S6-C/S6-D tests must remain unchanged except for wording that explicitly references still-unimplemented families.
- The selector does not prove comparator correctness against repository-loaded PDF, Docling, EID HTML render, or pdfplumber. Owner: deferred evidence/source-truth gates; release/readiness stays `NOT_READY`.

## 11. Next Gate

If this plan passes adversarial plan review and controller judgment, the next gate should be:

`FundDisclosureDocument S6-E Investor Experience Candidate Selector Implementation Gate`

No implementation is authorized by this planning-worker artifact alone.
