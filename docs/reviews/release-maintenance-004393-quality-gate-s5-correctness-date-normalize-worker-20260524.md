# Release Maintenance 004393 S5 Correctness Date Normalize Worker

## Scope

- Worker role: Gateflow specialist worker.
- Branch: `codex/checklist-host-engine-design`.
- Current gate: release maintenance 004393 S5 end-to-end quality gate verification.
- Objective: fix the correctness normalize false mismatch where `basic_identity.inception_date` expected `2022 年 8 月 8 日` and actual `2022年8月8日` should compare equal.

## Changes

- Updated `fund_agent/fund/extraction_score.py`.
  - Added field-scoped normalization for `basic_identity.inception_date`.
  - Only complete Chinese date strings matching `YYYY 年 M 月 D 日` shape remove internal visual whitespace.
  - Existing benchmark-only intra-Chinese visual whitespace normalization remains unchanged.
- Updated `tests/fund/test_extraction_score.py`.
  - Added coverage that spaced and unspaced Chinese dates compare equal.
  - Added coverage that non-date strings are not over-normalized by the date rule.

## Validation

- `uv run pytest tests/fund/test_extraction_score.py -q`
  - Result: `36 passed`.
- `uv run pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q`
  - Result: `26 passed`.
- `uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py`
  - Result: passed.
- `uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block`
  - Result: no FQ1 correctness block for `basic_identity.inception_date`.
  - Latest generated quality gate run: `reports/quality-gate-runs/analyze-004393-2024-20260524T015408658643Z`.
  - Evidence from `score.json`: `basic_identity.inception_date` row is `match`; normalized expected and actual are both `2022年8月8日`; correctness mismatch count is `0`.
  - Remaining command exit: failed later with `分析失败：报告包含禁用投资建议措辞：买入`.

## Residual Risk

- The 004393 smoke still fails after quality gate due to a downstream report audit banned-word issue. That is outside this worker scope.
- The date normalization intentionally does not parse alternate date formats or partial dates; it only handles complete Chinese年月日 visual spacing differences needed by S5.
