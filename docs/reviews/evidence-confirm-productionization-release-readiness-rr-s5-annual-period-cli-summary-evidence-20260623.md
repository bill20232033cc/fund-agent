# Evidence Confirm Productionization Release/readiness RR-S5 Annual-period CLI Summary Evidence

## Verdict

`RR_S5_ANNUAL_PERIOD_EVIDENCE_CONFIRM_CLI_SUMMARY_PASS_NOT_READY`

Release/readiness remains `NOT_READY`.

## Scope

RR-S5 objective: make current-year Evidence Confirm inheritance visible in `fund-analysis analyze-annual-period` CLI output without changing the annual-period request contract, without adding annual-period LLM support, and without changing `annual_period_report.report_markdown`.

Changed files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `README.md`
- `tests/README.md`

No Service contract, renderer contract, provider, live source/PDF command, push, PR mutation, mark-ready, merge, request-reviewer action, or release transition was performed.

## Implementation Evidence

`fund_agent/ui/cli.py` now calls `_echo_evidence_confirm_summary(result.current_year_result)` immediately after `_echo_quality_gate_summary(result.current_year_result)` in `analyze_annual_period()`.

This uses the existing current-year `FundAnalysisResult.evidence_confirm_summary` emitted by the target-year `analyze()` delegation path. It does not introduce an annual-period-specific Evidence Confirm policy parameter, does not change `MultiYearAnnualAnalysisRequest`, and does not alter `annual_period_report.report_markdown`.

`tests/ui/test_cli.py` adds `test_analyze_annual_period_cli_prints_current_year_evidence_confirm_summary`, covering:

- safe summary fields appear in CLI output:
  - `evidence_confirm_status`
  - `evidence_confirm_policy`
  - `evidence_confirm_checked_facts`
  - `evidence_confirm_failed_facts`
  - `evidence_confirm_auditability_score`
- annual-period metadata and `annual_period_report.report_markdown` remain visible
- current-year report body is not printed as a second report body
- raw source excerpt, PDF path, parser payload, and provider payload are not leaked

`README.md` and `tests/README.md` were updated to describe the current behavior only.

## Validation

Focused CLI tests:

```text
uv run pytest tests/ui/test_cli.py::test_analyze_annual_period_cli_calls_multi_year_service tests/ui/test_cli.py::test_analyze_annual_period_cli_prints_current_year_evidence_confirm_summary -q
2 passed in 0.99s
```

UI and Service regression suite:

```text
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service.py -q
130 passed in 1.69s
```

Static check:

```text
uv run ruff check fund_agent/ui/cli.py fund_agent/services/fund_analysis_service.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py
All checks passed!
```

Whitespace diff check:

```text
git diff --check -- fund_agent/ui/cli.py fund_agent/services/fund_analysis_service.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py
PASS
```

## Boundary Assertions

- `analyze-annual-period` still does not accept `--use-llm`.
- `analyze-annual-period` still does not expose an annual-period-specific `--evidence-confirm-policy` option.
- The formal annual-period report body remains `result.annual_period_report.report_markdown`.
- Evidence Confirm is displayed as CLI safe summary only in this gate.
- No raw excerpt, PDF/cache path, parser JSON, provider payload, source adapter object, provider body, or API key is emitted by the new summary path.

## Residuals

- RR-S6 remains open for report-body Evidence Confirm rendering or explicit product deferral.
- RR-S7/RR-S8 remain open for docs/control/hygiene and local/remote readiness disposition.
- PR-40 remains draft/open; no push or PR mutation was authorized or performed in this gate.
- Release/readiness remains `NOT_READY`.
