# FundDisclosureDocument S6-C Return Attribution Candidate Selector Implementation Evidence

## Gate

- Gate: `FundDisclosureDocument S6-C Return Attribution Candidate Selector Implementation Gate`
- Role: implementation worker
- Scope: exactly one new field-family selector, `return_attribution.v1`
- Stop condition: implementation + tests + evidence artifact only

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-s6c-return-attribution-candidate-selector-implementation-evidence-20260619.md`

## Behavior Summary

- Added deterministic candidate-only locator selection for `return_attribution.v1`.
- Match groups are limited to:
  - `nav_benchmark_performance`: NAV/benchmark performance locator tokens.
  - `fee_schedule`: management fee, custody fee, and sales service fee locator tokens.
  - `tracking_error`: tracking-error locator tokens.
- Did not add broad or interpretive standalone tokens: `超额收益`, `Alpha`, `阿尔法`, `收益归因`, `Beta`, `贝塔`, `成本`, `收益`, `费用`.
- Source paths remain exact:
  - `sections[{i}]`
  - `paragraph_blocks[{i}]`
  - `table_blocks[{i}]`
  - `table_blocks[{table_index}].cells[{cell_index}]`
- Cell scan order is sorted by `(row_index, column_index)` while `cell_index` remains the original enumerate index.
- Deduplication is only within `return_attribution.v1` by exact `source_field_path`; `product_essence.v1` keeps its own evidence set.
- `return_attribution.v1` candidate evidence is capped at 12 records and excerpts are capped at 160 characters.
- `product_essence.v1` S6-B selector functions and source path behavior were not refactored.

## Public Contract Boundary

- `return_attribution.v1.status` remains `missing`.
- `return_attribution.v1.extraction_mode` remains `missing`.
- `return_attribution.v1.value` remains `{}`.
- `return_attribution.v1.anchors` remains `()`.
- Candidate records remain:
  - `candidate_only=True`
  - `source_boundary="candidate_only"`
  - `field_correctness_status="not_proven"`
  - `source_truth_status="not_proven"`
  - `parser_replacement_authorized=False`
  - `readiness_status="not_ready"`
- Candidate excerpts are locator previews only. They are not parsed or copied into public field values.

## Explicit Non-Readiness

This implementation does not prove source truth, field correctness, parser replacement, full coverage, golden/readiness, release, or upper-layer consumption. Release/readiness remains `NOT_READY`.

## Validation

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Result: passed, `48 passed in 0.53s`.

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
```

Result: passed, `All checks passed!`.

```bash
git diff --check
```

Result: passed, no output.

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Result: passed, no output.

## Residuals

- `return_attribution.v1` remains locator-only and candidate-only. Typed extraction for NAV/benchmark performance, fee schedule, tracking error, alpha, beta, cost, or excess return remains a later gate.
- Other remaining field-family selectors are still not implemented unless already accepted by prior S6-B/S6-C gates.
- No PR, push, merge, commit, cleanup, release, readiness, source truth, parser replacement, Service/UI/Host/renderer/quality gate, repository/source/cache/live, provider, or LLM action was performed.
