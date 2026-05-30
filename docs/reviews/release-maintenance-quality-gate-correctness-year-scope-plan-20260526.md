# Quality Gate Correctness Report-Year Scope Plan

## Gate Context

- Current phase: `release maintenance`
- Current gate at startup: `renderer minimal integration implementation accepted locally`
- Next entry point: `quality gate correctness report-year scope plan/review; must use init-agents / multi-agent flow`
- Goal: fix strict golden-answer correctness identity so cross-year analysis cannot compare a current snapshot against a different report year's golden answer.
- Non-goal: do not change renderer, report-writing audit, Host/Agent packages, Dayu runtime, `FundDocumentRepository`, PDF/cache/source helpers, NAV behavior, checklist run-id naming, or FQ0-FQ6 block/warn policy semantics.

## Direct Evidence

The current code path is fund-code scoped, not report-year scoped:

- `reports/golden-answers/golden-answer.json` stores curated rows for `004393` whose `source` anchors are `年报2024 ...`; the JSON has `fund_code`, `field_name`, `sub_field`, `expected_value`, `confidence`, and `source`, but no structured `report_year`.
- `fund_agent/fund/golden_answer.py` defines `GoldenAnswerRecord` and `GoldenAnswerFund` without `report_year`.
- `load_golden_answer_json()` uses duplicate keys `(fund_code, field_name, sub_field)`.
- `fund_agent/fund/extraction_score.py` builds the correctness actual index in `_snapshot_actual_index()` with key `(fund_code, field_name, sub_field)`.
- `_compare_golden_record()` looks up that same fund-only key.
- `fund_agent/fund/extraction_snapshot.py` already writes `SnapshotRecord.report_year`, so the missing year scope is in golden/correctness comparison, not in snapshot generation.

This directly explains the manual failure: `004393 / 2025` snapshot can hit `004393 / 2024` golden rows for `nav_benchmark_performance.nav_growth_rate` and `benchmark_return_rate`, producing an FQ1 mismatch even when the 2025 extraction may be correct for the 2025 annual report.

## First-Principles Oracle Identity

A correctness oracle row is only valid for the disclosure document it was reviewed against. The minimum identity is:

```text
fund_code + report_year + field_name + sub_field
```

`fund_code` alone is insufficient because the same fund's annual-report facts legitimately change across years. `field_name + sub_field` is still required because the oracle compares scalar subfields, not the whole fund document.

## Implementation Plan

### Files To Modify

- `fund_agent/fund/golden_answer.py`
  - Add `report_year: int` to `GoldenAnswerFund` and `GoldenAnswerRecord`.
  - Keep loading existing v1 JSON compatible by defaulting missing `report_year` to `2024` for current curated legacy rows.
  - Make duplicate detection use `(fund_code, report_year, field_name, sub_field)`.
  - Make `build_golden_answer_json()` emit `report_year` at fund and record level using the current default year.

- `fund_agent/fund/extraction_score.py`
  - Add `report_year` to `CorrectnessRecordResult`.
  - Change `_snapshot_actual_index()` to key by `(fund_code, report_year, field_name, sub_field)`.
  - Change `_compare_golden_record()` to look up the year-scoped key.
  - Add `year_not_covered` coverage reason/scope for the case where the fund code exists in golden answers but the current report year does not.
  - Preserve `fund_not_covered`, `no_comparable_fields`, `partially_covered`, `covered`, and mismatch behavior for same-year data.

- `fund_agent/fund/quality_gate.py`
  - Accept `coverage_scope="year_not_covered"` for available correctness summaries.
  - Emit FQ0/info for year-not-covered, not FQ1/block.
  - Keep explicit same-year mismatch as FQ1/block.

- Tests:
  - `tests/fund/test_golden_answer.py`
  - `tests/fund/test_extraction_score.py`
  - `tests/fund/test_quality_gate.py`
  - `tests/fund/test_quality_gate_integration.py`
  - Service/CLI tests only if output/request contract changes are observable there. The current plan should not require Service/CLI changes.

- Documentation:
  - `fund_agent/fund/README.md`: correctness oracle is scoped by report year.
  - `tests/README.md`: score/golden/quality-gate tests must cover report-year identity.
  - `README.md`: user-facing score/correctness description should mention same-year golden comparison.
  - `docs/implementation-control.md`: update current gate, accepted artifacts, residuals, and next entry point after implementation acceptance.

### Compatibility Strategy

- Existing curated golden rows are treated as report year `2024` because their accepted sources are `年报2024 ...` and the current reviewed golden file was built for the 2024 baseline.
- Missing `report_year` in legacy strict JSON does not fail closed in this gate; it is upgraded in memory to `2024`.
- New build output should include structured `report_year` so future files are not dependent on source-string inference.
- Missing current-year golden coverage is an explicit coverage gap:
  - `coverage_scope = "year_not_covered"`
  - `coverage_reason = "year_not_covered"`
  - severity remains `FQ0/info`
  - no mismatch rows enter the blocker path for the wrong year.

### Non-Changes

- No quality gate policy weakening: same-year correctness mismatch still triggers FQ1/block.
- No turnover-rate policy change.
- No checklist/analyze artifact naming change.
- No renderer/report-writing audit change.
- No product default analyze/checklist control-flow change.
- No Host/Agent/dayu/source-helper/FundDocumentRepository change.

## Test Matrix

- Golden schema:
  - legacy JSON without `report_year` loads with `report_year=2024`.
  - build output includes `report_year` at fund and record level.
  - duplicate rows with same `fund_code + report_year + field/subfield` are rejected.

- Correctness compare:
  - `004393 / 2024` snapshot against `004393 / 2024` golden still compares normally.
  - `004393 / 2024` same-year mismatched scalar remains `mismatch`.
  - `004393 / 2025` snapshot against only `004393 / 2024` golden returns `year_not_covered`, `comparable_records=0`, `mismatched_records=0`.
  - field not comparable remains `no_comparable_fields`.
  - fund not present in golden remains `fund_not_covered`.

- Quality gate:
  - available correctness with `year_not_covered` produces FQ0/info and does not block.
  - available correctness with same-year mismatch still produces FQ1/block.

- Integration:
  - `run_quality_gate_for_bundle()` with a 2025 bundle and only 2024 golden returns a gate result with FQ0/info year-not-covered, not an FQ1 mismatch block, assuming no unrelated field failure.

## Acceptance Commands

Focused:

```bash
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
uv run ruff check fund_agent/fund/golden_answer.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py
```

Product smoke:

```bash
uv run fund-analysis analyze 004393 --report-year 2024
uv run fund-analysis checklist 004393 --report-year 2024
uv run fund-analysis analyze 004393 --report-year 2025
uv run fund-analysis checklist 004393 --report-year 2025
```

Full:

```bash
uv run ruff check .
uv run pytest -q
git diff --check
```

## Expected Acceptance

- 2024 analyze/checklist remains warn or stricter with direct same-year evidence, but not silently weakened.
- 2025 analyze/checklist no longer uses 2024 golden rows to trigger FQ1 mismatch block.
- If no 2025 golden exists, the score/gate output reports `year_not_covered` or equivalent explicit coverage metadata.
- `turnover_rate` missing remains warn/non-blocking under current semantics.
- Checklist run-id naming confusion remains a P3 residual for the later reliability hardening gate.

## Residuals After This Gate

- Future golden-build UX may need an explicit `--report-year` parameter; this gate avoids CLI changes unless review proves they are required.
- Existing curated `reports/golden-answers/golden-answer.json` may remain legacy-compatible or be migrated in a later golden maintenance gate; the runtime fix must not depend on editing hundreds of curated rows.
- Multi-year golden files beyond 2024 need a reviewed golden-coverage expansion gate.
- Core analyze/checklist reliability hardening is queued next: NAV unavailable degradation, pre-2026 turnover-rate wording/quality expectations, and checklist/analyze artifact naming.
