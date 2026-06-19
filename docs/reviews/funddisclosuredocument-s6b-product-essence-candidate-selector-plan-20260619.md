# FundDisclosureDocument S6-B Product Essence Candidate Selector Plan

## 1. Gate

- Gate: `FundDisclosureDocument S6-B Single-family Candidate Evidence Selector Planning Gate`
- Classification: `heavy` implementation gate, because it adds candidate selector behavior to a processor contract result.
- Accepted prerequisite: S6-A candidate evidence contract implementation accepted by `docs/reviews/funddisclosuredocument-s6a-candidate-evidence-contract-implementation-controller-judgment-20260619.md`.

## 2. Goal

Implement the first deterministic candidate evidence selector for exactly one field family:

`product_essence.v1`

The selector should populate `FundFieldFamilyResult.candidate_evidence` with candidate-only locator evidence from `FundDisclosureDocumentContentIntermediate`. It must not produce public structured values, public anchors, `partial` status, source truth, parser replacement, or facade-consumable facts.

## 3. Non-goals

- No selectors for `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1`.
- No final field extraction into `basic_identity`, `product_profile`, `benchmark`, or `risk_characteristic_text`.
- No `FundFieldFamilyResult.value` population from candidate evidence.
- No public `EvidenceAnchor` for candidate-only evidence.
- No `FundDataExtractor` projection changes.
- No change to admission helper semantics.
- No live/PDF/network/repository/source/cache behavior.
- No source truth, field correctness, parser replacement, golden/readiness, release, PR mutation, or unrelated cleanup.

## 4. Selector Mapping

The S6-B selector is a locator selector, not a semantic fact extractor.

Family: `product_essence.v1`

Allowed locator sources:

- `sections`
- `paragraph_blocks`
- `table_blocks`
- `table_blocks[*].cells`

Match groups:

| Group | Candidate text fields | Match tokens | Evidence role |
|---|---|---|---|
| product_identity | section heading, heading path, table heading/caption, row/column labels | `基金简介`, `基金基本情况`, `产品概况`, `基金产品资料概要`, `基金名称`, `基金代码` | product identity candidate |
| investment_scope | section heading, heading path, paragraph text, table heading/caption, row/column labels | `投资目标`, `投资范围`, `投资策略` | product profile candidate |
| benchmark | section heading, heading path, paragraph text, row/column labels, cell text | `业绩比较基准`, `比较基准` | benchmark candidate |
| risk_characteristic | section heading, heading path, paragraph text, row/column labels, cell text | `风险收益特征`, `风险特征` | risk characteristic candidate |

Normalization rule:

- Use existing normalized text fields when available.
- Also search raw text fields because some candidate fixtures may only preserve raw heading/cell text.
- Strip ASCII and full-width whitespace for token matching.
- Do not translate, infer synonyms, or use fuzzy matching in S6-B.

Ordering rule:

1. sections by tuple order
2. paragraph blocks by tuple order
3. table blocks by tuple order
4. cells by `(row_index, column_index)`

Deduplication rule:

- Deduplicate by exact `source_field_path`.
- Keep the first record for each path.

Limit rule:

- Keep at most `12` candidate records for `product_essence.v1`.
- Prefer evidence roles in this order: `product_identity`, `investment_scope`, `benchmark`, `risk_characteristic`.
- Within a role, preserve ordering rule.

Excerpt rule:

- Store at most `160` characters.
- For cells, excerpt is `cell_text_normalized` if non-empty, otherwise `cell_text`.
- For paragraphs, excerpt is `text_normalized` if non-empty, otherwise `text_raw`.
- For sections/tables, excerpt is the matched heading/caption string.

## 5. Result Semantics

When product essence candidate locators are found:

- `product_essence.v1.status` remains `missing`.
- `product_essence.v1.extraction_mode` remains `missing`.
- `product_essence.v1.value` remains `{}`.
- `product_essence.v1.anchors` remains `()`.
- `product_essence.v1.candidate_evidence` contains `FundCandidateEvidenceRecord` rows.
- local gap is `candidate_only_not_source_truth` with `source_boundary="candidate_only"`.
- result-level status remains governed by existing admission semantics:
  - concrete candidate-boundary input remains result-level `blocked`;
  - non-candidate test stubs may remain result-level `missing`.

When no product essence candidate locators are found:

- current `field_family_missing` behavior remains unchanged.
- `candidate_evidence == ()`.

All other field families remain current fully-gapped `missing` without candidate evidence.

## 6. Implementation Write Set

Allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`

Do not edit:

- `FundDataExtractor`
- `EvidenceAnchor`
- `FundFieldFamilyStatus`
- `FundProcessorContractStatus`
- source/repository/cache/live code

## 7. Required Tests

Add or update tests in `tests/fund/processors/test_fund_disclosure_processor.py`:

1. content-bearing intermediate with product identity section/table/cell yields product essence `candidate_evidence`.
2. product essence family remains `status="missing"`, `value={}`, `anchors=()`.
3. product essence local gap is `candidate_only_not_source_truth`.
4. candidate evidence records preserve candidate-only / not_proven / not_ready boundaries.
5. other five field families remain fully missing and have empty `candidate_evidence`.
6. no-content admission-only intermediate remains current six-family `field_family_missing` behavior.
7. nonmatching content-bearing intermediate yields no candidate evidence.
8. candidate-boundary input remains result-level `blocked`; candidate evidence does not change consumption status.
9. static import-boundary test still proves no concrete candidate, Docling, PDF/cache/source helper, network, provider, Service/UI/Host, renderer, or quality gate imports in `fund_disclosure_processor.py`.

## 8. Validation Matrix

Run after implementation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
git diff --check
```

If README/design are updated:

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

## 9. Acceptance Criteria

S6-B is accepted only if:

- exactly one field family selector is implemented: `product_essence.v1`;
- selector output is candidate evidence only;
- public `value` and `EvidenceAnchor` remain empty;
- `partial` / `accepted` are not used;
- facade projection remains unchanged;
- concrete candidate-boundary consumption remains blocked;
- release/readiness remains `NOT_READY`.

## 10. Next Gate After Acceptance

If S6-B is accepted, the next gate is:

`FundDisclosureDocument S6-C Product Essence Candidate Selector Implementation Gate`

No implementation is authorized until this plan passes adversarial plan review and controller judgment.
