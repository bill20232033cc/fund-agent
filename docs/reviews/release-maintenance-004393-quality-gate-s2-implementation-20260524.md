# Release Maintenance 004393 Quality Gate S2 Implementation - 2026-05-24

## Gate

- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S2 - P1 Extraction And Benchmark Correctness`
- Current gate: `release-maintenance 004393 S2 P1 extraction and benchmark correctness implementation`
- Approved plan: `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
- Plan fix: `docs/reviews/release-maintenance-004393-quality-gate-plan-fix-20260524.md`
- Evidence: `docs/reviews/release-maintenance-004393-quality-gate-evidence-20260524.md`
- Evidence controller judgment: `docs/reviews/release-maintenance-004393-quality-gate-evidence-controller-judgment-20260524.md`
- S1 acceptance: `docs/reviews/release-maintenance-004393-quality-gate-s1-rereview-controller-judgment-20260524.md`

## Scope Boundaries

- No `fund_agent/host` or `fund_agent/agent` package was created.
- No Dayu Host/Agent dependency or runtime wiring was added.
- No golden answer, source CSV, config, runtime output, README, `docs/design.md`, `AGENTS.md`, or `docs/implementation-control.md` file was edited.
- No `turnover_rate` extractor, score, denominator, quality-gate applicability, schema, or derived proxy behavior was changed.
- No profile-derived identity was passed through `data_extractor.py`; share-class selection uses same-source §2 evidence inside `holdings_share_change.py`.
- Benchmark whitespace normalization is field-aware and applies only to `benchmark.benchmark_name` and `benchmark.benchmark_text` correctness comparison.

## Changed Files

- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `tests/fund/extractors/test_holdings_share_change.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `docs/reviews/release-maintenance-004393-quality-gate-s2-implementation-20260524.md`

`fund_agent/fund/quality_gate.py` was not changed. Quality-gate holdings coverage is claimed through score/fund_quality semantics: industry-only `holdings_snapshot` now remains visible as P1 missing in score output, and quality gate continues consuming those score rows.

## Implemented Plan Items

### Holdings Snapshot

- Added semantic detection for §8 all-stock investment details tables with stock code/name/quantity/fair-value/net-asset-ratio columns.
- Preserved existing output key `top_holdings`; all-stock details output the first 10 rows under that key.
- Added required machine-readable fields whenever `holdings_snapshot` is emitted:
  - `top_holdings_status`: `direct_top_ten`, `direct_all_stock_details`, or `missing`
  - `top_holdings_source`: `top_ten`, `all_stock_investment_details`, or `none`
  - `industry_distribution_status`: existing direct/missing status remains explicit
- Added snapshot comparable propagation for `top_holdings_status` and `top_holdings_source`.
- Updated score/fund_quality coverage so industry-only evidence with `top_holdings_status="missing"` does not satisfy stock-holdings coverage.

### Share Change

- Added adjacent split-table merge for §10 share-change header/data tables.
- Added same-source §2 A/C evidence extraction from the parsed §2 table/text.
- A/C column selection now requires direct §2 class evidence when no single value column or exact fund-code header exists.
- Missing §2 class evidence, non-adjacent split tables, or ambiguous class matches fail closed.
- No fund-code suffix heuristic was introduced.

### Benchmark Correctness

- Added correctness-only benchmark visual whitespace normalization for `benchmark.benchmark_name` and `benchmark.benchmark_text`.
- The normalization removes whitespace between adjacent Chinese characters only.
- Non-benchmark fields keep existing whitespace behavior.
- ASCII word spacing is preserved.

## Tests Added Or Updated

- Extractor tests cover:
  - top-ten status/source output;
  - all-stock-details as a stock-holdings source with first-10 rows;
  - industry-only output with `top_holdings_status="missing"`;
  - adjacent split share tables selecting A-class only with §2 evidence;
  - missing §2 evidence and non-adjacent split tables fail closed.
- Snapshot tests cover propagation of holdings status/source into `comparable_values`.
- Score tests cover:
  - industry-only holdings does not count as P1 stock-holdings coverage;
  - benchmark Chinese visual whitespace matches only for benchmark fields;
  - non-benchmark Chinese whitespace still mismatches;
  - ASCII benchmark word spacing remains significant.

## Validation

```bash
uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
```

Result: `76 passed`.

```bash
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
```

Result: passed.

```bash
git diff --check
```

Result: passed.

## Quality-Gate Holdings Coverage Claim

S2 claims quality-gate holdings coverage through `extraction_score.py` and `fund_quality` semantics, not through a direct `quality_gate.py` change:

- `holdings_snapshot.value_present=True` is not sufficient for score coverage when `top_holdings_status="missing"`.
- Industry-only evidence remains extractable and traceable, but it keeps `holdings_snapshot` missing for stock-holdings coverage.
- `quality_gate.py` already consumes field/fund score failures and therefore receives the corrected P1 status from score output.

## Residual Risks

- `ParsedTable` still has no physical parser-section metadata. S2 uses table semantics plus same-source §2 parsed evidence; it does not claim refreshed-source provenance or `fallback_used=false`.
- All-stock-details continuation across parser-split pages is limited to the first matching table in this slice. 004393 evidence has the first 10 rows in the first all-stock-details table, so this closes the current blocker without broader continuation redesign.
- Benchmark golden rows were not edited. This slice only prevents visual intra-Chinese whitespace from causing benchmark correctness mismatch.
- `turnover_rate disclosure applicability / quality gate denominator policy` remains a separate future Gateflow candidate.

## Completion

`ready_for_code_review: true`
