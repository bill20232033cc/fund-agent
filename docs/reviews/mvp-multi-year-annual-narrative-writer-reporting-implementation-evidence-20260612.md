# Implementation evidence: multi-year annual narrative writer/reporting

## Gate

`multi-year annual narrative writer/reporting implementation gate`

Classification: `heavy`, because this implementation changes the user-facing `fund-analysis analyze-annual-period` report body.

Accepted plan:

- `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md`
- Controller judgment: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-controller-judgment-20260611-233310.md`
- Planning checkpoint: `8682859`

## Scope Confirmation

Implemented only deterministic annual-period narrative/reporting behavior. No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command was run.

No source acquisition policy was changed. Eastmoney, fund-company/CDN, CNINFO and fallback behavior were not introduced.

## Changed Files

Source:

- `fund_agent/fund/template/annual_period_renderer.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`

Tests:

- `tests/fund/test_annual_period_report.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`

README/docs triggered by source/test changes:

- `README.md`
- `fund_agent/README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Implementation Summary

- Added Fund-owned `annual_period_report.v1` renderer under `fund_agent/fund/template/annual_period_renderer.py`.
- Renderer consumes only in-memory `AnnualEvidenceBundle`, current-year report Markdown and explicit quality-gate inputs.
- Renderer outputs deterministic Markdown sections:
  - `年度覆盖与来源`
  - `跨年关键变化`
  - `对当前判断的影响`
  - `缺口与降级`
  - `当前年份报告`
- Renderer preserves current-year report text behind a stable marker and does not rewrite current-year 8章内容.
- Renderer emits `quality_gate_status=not_available` when quality-gate context is absent and states that no pass/readiness claim is made.
- Renderer includes a wording guard for annual-period summary and section-specific impact wording: no direct buy/sell language, return prediction wording or unsupported causal phrasing.
- Renderer redacts raw PDF/cache/path-like values from rendered fact payloads.
- `MultiYearAnnualAnalysisResult.report_markdown` remains the current-year report.
- `MultiYearAnnualAnalysisResult.annual_period_report` now carries the formal annual-period report.
- CLI `analyze-annual-period` keeps the existing metadata header and prints `result.annual_period_report.report_markdown` after it.

## Contract Decisions Verified

| Contract | Evidence |
|---|---|
| `report_markdown` compatibility remains current-year | `tests/services/test_fund_analysis_service.py` asserts `result.report_markdown == result.current_year_result.report_markdown` |
| Explicit annual-period report field exists | `MultiYearAnnualAnalysisResult.annual_period_report` and Service assembly |
| CLI consumes explicit annual-period report field | `tests/ui/test_cli.py` asserts annual-period output appears and current-year fake output does not |
| Missing quality-gate context is explicit | renderer and Service tests assert `quality_gate_status=not_available` |
| All-prior-years-gap path degrades | `tests/fund/test_annual_period_report.py` covers all prior years as gaps and emits `insufficient_evidence` |
| Forbidden wording guard exists | renderer test rejects `建议买入`, `收益预测`, and unsupported causal text |
| Raw PDF/cache paths are not rendered | renderer test asserts raw `/tmp/cache/report.pdf` is absent and `redacted_path` is present |

## Validation

Executed:

```text
uv run ruff check fund_agent/fund/template/annual_period_renderer.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Result:

```text
All checks passed!
```

Executed:

```text
uv run pytest tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
```

Result:

```text
115 passed in 1.04s
```

Executed:

```text
git diff --check
```

Result: pass.

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Additional controlled live samples | Controller / evidence owner | Separate controlled live gate only if explicitly authorized |
| Release/readiness claim | Release owner | Still not claimed; requires separate readiness gate |
| Coverage measurement | Coverage owner | Deferred environment/coverage hygiene gate |
| `source_fund_id` current-year structured-data identity extension | Fund/source identity owner | Deferred structured-data source identity extension gate |
| MiMo targeted re-review channel residual from planning gate | Controller / agent setup owner | Does not affect implementation behavior; record in review/controller judgment if still relevant |

## Next Review Request

MiMo and DS should review:

- whether the implementation stays within the accepted plan and write set;
- whether Fund/Service/UI boundaries remain intact;
- whether `report_markdown` compatibility is preserved;
- whether CLI now prints the annual-period report body after metadata header;
- whether wording/quality-gate/gap/fail-closed guardrails are sufficient;
- whether README/test docs describe current behavior without overstating live/readiness/release status.
