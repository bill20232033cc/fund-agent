# FundDisclosureDocument S6-C Return Attribution Candidate Selector Plan Draft

## 1. Gate And Recommendation

- Gate: `FundDisclosureDocument S6-C Single-family Candidate Evidence Selector Planning Gate`
- Worker role: planning worker only; no implementation, commit, push, PR, merge, cleanup, or controller judgment.
- Recommended field family: `return_attribution.v1`
- Verdict: recommend proceeding with exactly one selector for `return_attribution.v1`.

Rationale:

- `return_attribution.v1` maps directly to template Chapter 2 `R = A + B - C` and the current processor mapping surface: `performance.nav_benchmark_performance`, `performance.tracking_error`, and `profile.fee_schedule`.
- The candidate document content protocol already exposes section, paragraph, table, and cell locators. Return/performance/fee/tracking-error disclosures usually have stable headings, row labels, column headers, or table captions, so a locator-only selector can be implemented without semantic extraction.
- This field family is lower interpretation risk than `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1`: it can select candidate rows/tables by disclosed labels without inferring manager behavior, investor experience, current cycle stage, or risk causality.
- It extends S6-B with the next most mechanical table/cell-heavy family while preserving `candidate-only`, `not_proven`, and `NOT_READY`.

## 2. Exact Non-goals

- No selector for `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1`.
- No final field extraction into `fee_schedule`, `nav_benchmark_performance`, `tracking_error`, alpha, beta, cost, excess return, or any structured Chapter 2 fact.
- No `FundFieldFamilyResult.value` population from candidate evidence.
- No public `EvidenceAnchor` creation or `FundFieldFamilyResult.anchors` population.
- No `partial`, `accepted`, `satisfied`, `direct`, `derived`, or `estimated` status/mode from candidate evidence.
- No `FundDataExtractor`, facade projection, `StructuredFundDataBundle`, renderer, quality gate, Service, UI, Host, Agent runner, repository, source, cache, live/network, PDF, Docling conversion, pdfplumber export, provider, or LLM change.
- No contract/schema expansion in `contracts.py`; S6-A candidate evidence contract is sufficient.
- No `EvidenceSourceKind` / public `EvidenceAnchor.source_kind` expansion.
- No source truth, field correctness, parser replacement, golden, readiness, release, or PR state claim.
- No cleanup, deletion, staging, or classification of unrelated untracked residuals.

## 3. Selector Contract

The S6-C selector is a deterministic locator selector, not a value extractor.

Family:

- `return_attribution.v1`

Allowed input protocol:

- `FundDisclosureDocumentContentIntermediate` only after existing admission and identity checks pass.
- If the intermediate is only `FundDisclosureDocumentIntermediate` and not content-bearing, the family remains current `field_family_missing`.

Allowed locator sources:

- `sections`
- `paragraph_blocks`
- `table_blocks`
- `table_blocks[*].cells`

Match groups:

| Role | Candidate text fields | Match tokens | Evidence role |
|---|---|---|---|
| `nav_benchmark_performance` | section heading, heading path, paragraph text, table heading/caption, row/column labels, cell text | `基金份额净值增长率`, `净值增长率`, `基金净值表现`, `业绩比较基准收益率`, `基准收益率`, `业绩比较基准` | locator for NAV growth and benchmark return candidate |
| `fee_schedule` | section heading, heading path, paragraph text, table heading/caption, row/column labels, cell text | `基金管理费`, `管理费率`, `管理费`, `基金托管费`, `托管费率`, `托管费`, `销售服务费率`, `销售服务费` | locator for cost / fee candidate |
| `tracking_error` | section heading, heading path, paragraph text, table heading/caption, row/column labels, cell text | `跟踪误差`, `年化跟踪误差`, `日均跟踪偏离度`, `日均偏离度` | locator for tracking-error candidate |

Do not add broad or interpretive tokens in S6-C:

- Do not add `超额收益`, `Alpha`, `阿尔法`, `收益归因`, `Beta`, `贝塔`, `成本`, `收益`, or `费用` as standalone tokens.
- Reason: these terms either require semantic interpretation or are too broad for a locator-only gate.

## 4. Source Path, Ordering, Dedupe, Limit, Excerpt

Source path formats must be exact and stable:

- Section record: `sections[{section_index}]`
- Paragraph record: `paragraph_blocks[{paragraph_index}]`
- Table record: `table_blocks[{table_index}]`
- Cell record: `table_blocks[{table_index}].cells[{cell_index}]`

For cell records:

- `cell_index` is the original tuple index from `enumerate(table.cells)`.
- Cell scan order is sorted by `(row_index, column_index)`, while source path still preserves the original tuple index.

Ordering rule:

1. Iterate match roles in this order: `nav_benchmark_performance`, `fee_schedule`, `tracking_error`.
2. Within each role, scan sources in this order: sections, paragraph blocks, table blocks, table cells.
3. Sections, paragraphs, and tables preserve tuple order.
4. Cells are sorted by `(row_index, column_index)`.

Dedupe rule:

- Deduplicate within `return_attribution.v1` by exact `source_field_path`.
- Keep the first record for a path according to the ordering rule.
- Do not deduplicate across `product_essence.v1` and `return_attribution.v1`; each field family owns its own candidate evidence set.

Limit rule:

- Add `_RETURN_ATTRIBUTION_CANDIDATE_LIMIT = 12`.
- Keep at most 12 records for `return_attribution.v1`.
- If more than 12 candidate records exist, preserve the ordering rule and truncate after 12.

Excerpt rule:

- Keep `_CANDIDATE_EXCERPT_LIMIT = 160`.
- Section/table excerpt: first non-empty normalized/raw heading, caption, or heading-path text used for matching.
- Paragraph excerpt: `text_normalized` if non-empty, otherwise `text_raw`.
- Cell excerpt: `cell_text_normalized` if non-empty, otherwise `cell_text`.
- Excerpt is a candidate locator preview only; it is not source truth and must not be parsed as a field value.

Candidate evidence fields:

- `field_family_id="return_attribution.v1"`
- `source_boundary="candidate_only"`
- `candidate_only=True`
- `field_correctness_status="not_proven"`
- `source_truth_status="not_proven"`
- `parser_replacement_authorized=False`
- `readiness_status="not_ready"`
- `row_locator` format should mirror S6-B: `role={role}; locator=...`

## 5. Implementation Design For Later Gate

The later implementation gate should keep the change local to `FundDisclosureDocumentProcessor`.

Required processor behavior:

- In `_field_families_for_intermediate()`, select both:
  - existing `product_essence.v1` candidate evidence;
  - new `return_attribution.v1` candidate evidence.
- For `return_attribution.v1` with non-empty candidate evidence:
  - return `_candidate_missing_field_family("return_attribution.v1", source_provenance, return_evidence)`.
- For `return_attribution.v1` with empty candidate evidence:
  - keep existing `_missing_field_family("return_attribution.v1", source_provenance)`.
- All remaining families stay fully missing unless they already have an accepted selector.

Required result semantics:

- `return_attribution.v1.status == "missing"`
- `return_attribution.v1.extraction_mode == "missing"`
- `return_attribution.v1.value == {}`
- `return_attribution.v1.anchors == ()`
- `return_attribution.v1.gaps[0].gap_code == "candidate_only_not_source_truth"` only when candidate evidence exists.
- `return_attribution.v1.gaps[0].gap_code == "field_family_missing"` when no candidate evidence exists.
- Overall result-level candidate-boundary status remains existing admission behavior:
  - concrete candidate-boundary input remains `contract_status="blocked"`;
  - non-candidate content stubs may remain `contract_status="missing"`.

Recommended helper structure:

- Add `_RETURN_ATTRIBUTION_MATCH_GROUPS`.
- Add `_RETURN_ATTRIBUTION_CANDIDATE_LIMIT`.
- Refactor S6-B product selector and S6-C return selector through a shared private helper:
  - `_select_candidate_evidence(intermediate, field_family_id, match_groups, limit)`
  - `_extend_candidate_section_records(...)`
  - `_extend_candidate_paragraph_records(...)`
  - `_extend_candidate_table_records(...)`
  - `_extend_candidate_cell_records(...)`
- Keep `_select_product_essence_candidate_evidence()` as a thin wrapper to preserve S6-B readability and regression isolation.
- Add `_select_return_attribution_candidate_evidence()` as a thin wrapper for S6-C.
- Do not add nested functions/classes.
- Do not import candidate document concrete classes, Docling, PDF/source/cache helpers, repository helpers, Service/UI/Host, renderer, quality gate, provider, or network modules.

## 6. Allowed Write Set

Current planning worker write set:

- `docs/reviews/funddisclosuredocument-s6c-return-attribution-candidate-selector-plan-20260619.md`

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

1. `test_return_attribution_selector_adds_candidate_evidence_only`
   - Content-bearing intermediate with return/performance/fee/tracking-error locator text yields `return_attribution.v1.candidate_evidence`.
   - Assert `status="missing"`, `extraction_mode="missing"`, `value == {}`, `anchors == ()`, and local gap `candidate_only_not_source_truth`.

2. `test_return_attribution_selector_preserves_candidate_boundary_fields`
   - Every return candidate record has `candidate_only=True`, `source_boundary="candidate_only"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, and `readiness_status="not_ready"`.

3. `test_return_attribution_selector_keeps_other_unimplemented_families_without_candidate_evidence`
   - With return-attribution matching content, `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain `field_family_missing` with empty `candidate_evidence`.
   - `product_essence.v1` remains governed only by S6-B matching content.

4. `test_return_attribution_selector_no_match_keeps_field_family_missing`
   - Neutral content produces no return-attribution evidence and preserves `field_family_missing`.

5. `test_return_attribution_selector_preserves_candidate_boundary_blocked_status`
   - Candidate-boundary input with return candidate evidence still returns result-level `contract_status="blocked"`.

6. `test_return_attribution_selector_orders_dedupes_limits_and_truncates`
   - Construct more than 12 candidate paths.
   - Assert role order, source order, exact `source_field_path`, first-record-wins dedupe, 12-record limit, and `excerpt` length <= 160.

7. Existing S6-A tests must keep passing:
   - admission protocol remains content-free;
   - candidate evidence rejects source-truth/readiness escape;
   - candidate evidence does not satisfy partial anchor requirement.

8. Existing S6-B product essence tests must keep passing unchanged.

9. Existing static import-boundary test, if present in this file, must continue proving no forbidden imports in `fund_disclosure_processor.py`.

## 8. Validation Matrix

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

Planning-worker artifact validation:

```bash
git diff --check -- docs/reviews/funddisclosuredocument-s6c-return-attribution-candidate-selector-plan-20260619.md
```

## 9. Acceptance Criteria

S6-C plan acceptance requires:

- Exactly one remaining field family is selected: `return_attribution.v1`.
- The plan is code-generation-ready: implementation path, source paths, token mapping, order, dedupe, limit, excerpt, write set, tests, validation, and result semantics are explicit.
- Candidate evidence remains `candidate-only`, `not_proven`, and `not_ready`.
- Public `value` and public `EvidenceAnchor` remain empty.
- No `partial` / `accepted` / `satisfied` state is introduced by candidate evidence.
- `FundDataExtractor`, repository/source/cache/live behavior, public schema, and upper layers remain unchanged.
- Existing S6-A/S6-B behavior is preserved by regression tests.
- Release/readiness remains `NOT_READY`.

Future S6-C implementation acceptance additionally requires:

- Focused pytest passes.
- Ruff passes for touched code/test files.
- `git diff --check` passes.
- Fund README/design sync, if touched, states current behavior only and does not claim source truth, parser replacement, readiness, or release.

## 10. Residual Risks

- Token false positives remain possible because substring matching does not prove semantic field correctness. Owner: later field-extraction/source-truth gate; S6-C mitigates by keeping public status `missing`.
- `tracking_error` may be absent or not applicable for non-index-like active funds. Owner: later typed extraction and fund-type-specific applicability gate; S6-C only records locators.
- Candidate excerpts can contain numeric-looking text. Owner: S6-C implementation must keep excerpts out of `value` and `anchors`; tests must assert no value leak.
- Refactoring S6-B helper code could regress product essence behavior. Owner: S6-C implementation test suite; existing S6-B tests must remain unchanged and pass.
- The selector does not prove comparator correctness against repository-loaded PDF, Docling, EID HTML render, or pdfplumber. Owner: deferred evidence/source-truth gates; release/readiness stays `NOT_READY`.

## 11. Next Gate

If this plan passes adversarial plan review and controller judgment, the next gate should be:

`FundDisclosureDocument S6-C Return Attribution Candidate Selector Implementation Gate`

No implementation is authorized by this planning-worker draft alone.
