# Implementation review: multi-year annual narrative writer/reporting

## Verdict

`ACCEPT`

Implementation matches the accepted plan contract, stays within the allowed write set, preserves Fund/Service/UI boundaries and `report_markdown` compatibility, and passes deterministic validation.

## Gate

`multi-year annual narrative writer/reporting implementation gate`

Classification: `heavy`.

Reviewed artifacts:

- Accepted plan: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md`
- Controller judgment: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-controller-judgment-20260611-233310.md`
- Evidence: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-implementation-evidence-20260612.md`
- Workspace diff: current branch `feat/mvp-llm-incomplete-run-artifacts` against HEAD

## Accepted Write Set Check

| Plan allowed file | Present in diff | Verdict |
|---|---|---|
| `fund_agent/fund/template/annual_period_renderer.py` (new) | YES | OK |
| `tests/fund/test_annual_period_report.py` (new) | YES | OK |
| `fund_agent/services/fund_analysis_service.py` | YES | OK |
| `fund_agent/services/__init__.py` | YES | OK |
| `fund_agent/ui/cli.py` | YES | OK |
| `tests/services/test_fund_analysis_service.py` | YES | OK |
| `tests/ui/test_cli.py` | YES | OK |
| `README.md` | YES | OK |
| `fund_agent/README.md` | YES | OK |
| `fund_agent/fund/README.md` | YES | OK |
| `tests/README.md` | YES | OK |

No out-of-scope source/test/runtime/design/control/startup files were modified. Write set is clean.

## Contract Verification

### C1: `report_markdown` compatibility

Plan requirement: `MultiYearAnnualAnalysisResult.report_markdown` must remain the target-year current report.

Evidence: `tests/services/test_fund_analysis_service.py:1467` asserts `result.report_markdown == result.current_year_result.report_markdown`. The CLI test's `_FakeMultiYearResult.report_markdown` property also delegates to `current_year_result.report_markdown`. `MultiYearAnnualAnalysisResult` does not override `report_markdown`; the field name on the new `AnnualPeriodReportRenderResult` is distinct.

Status: **PASS** — no silent semantic break.

### C2: Explicit annual-period report field

Plan requirement: A distinct `annual_period_report` field carries the formal annual-period report.

Evidence: `MultiYearAnnualAnalysisResult` gained `annual_period_report: AnnualPeriodReportRenderResult` at `fund_analysis_service.py:308`. Service assembles it from renderer output at `fund_analysis_service.py:803-814`. Exported in `services/__init__.py`.

Status: **PASS**.

### C3: CLI consumes explicit annual-period report field

Plan requirement: CLI `analyze-annual-period` prints `result.annual_period_report.report_markdown` after metadata header.

Evidence: `cli.py:1067` changed from `typer.echo(result.report_markdown, nl=False)` to `typer.echo(result.annual_period_report.report_markdown, nl=False)`. CLI test asserts `"# annual period report"` is in output and `"# current year report"` is NOT in output.

Status: **PASS**.

### C4: `quality_gate_status=not_available` when absent

Plan requirement: Missing quality-gate context renders `quality_gate_status=not_available` and cannot imply pass/readiness.

Evidence: Renderer defaults to `QUALITY_GATE_STATUS_NOT_AVAILABLE` when `input_data.quality_gate_status` is falsy (`annual_period_renderer.py:98`). Coverage section appends a bounded no-readiness note when status equals `not_available` (`annual_period_renderer.py:230-231`). Service passes `quality_gate_status` from `current_year_result.quality_gate_result.status` or `None` (`fund_analysis_service.py:808-812`). Renderer test `test_annual_period_report_renders_all_prior_years_gap_as_insufficient` asserts `quality_gate_status=not_available` and `不据此声明通过或 readiness` in output. Service test asserts `quality_gate_status=not_available` in `annual_period_report.report_markdown`.

Status: **PASS**.

### C5: All-prior-years-gap degrade path

Plan requirement: All-prior-years-gap bundle must render minimal annual-period report and state cross-year evidence insufficiency.

Evidence: `test_annual_period_report_renders_all_prior_years_gap_as_insufficient` constructs a bundle with `available_years=(2025,)` and `gap_years=(2024,2023,2022,2021)`. Asserts `跨年事实：insufficient_evidence`, `impact_status=insufficient_evidence`, and `quality_gate_status=not_available`. Service test also asserts `impact_status=insufficient_evidence` when all prior years are gaps.

Status: **PASS**.

### C6: Wording guard — buy/sell, prediction, causality

Plan requirement: Section-specific wording guard for `对当前判断的影响` that catches buy/sell language, return prediction wording and unsupported causal phrasing.

Evidence: Renderer defines `_FORBIDDEN_ANNUAL_PERIOD_PHRASES` (6 phrases), `_DIRECT_TRADING_ADVICE_PATTERN` (regex for 建议/推荐/应当/应该/直接/立即/马上 + 买入/卖出/加仓/减仓), and `_UNSUPPORTED_CAUSAL_PATTERN` (regex for 必然/一定会/保证/确保/导致收益/带来收益/决定收益). `validate_annual_period_report_wording()` applies all three checks, with the causal pattern scoped to the impact section only. `render_annual_period_report()` calls `validate_annual_period_report_wording(period_summary)` before composing the final report. Parametrized test covers `建议买入`, `收益预测`, and `必然带来收益`.

Status: **PASS**.

### C7: Raw PDF/cache paths not rendered

Plan requirement: Raw PDF/cache/source paths must be redacted.

Evidence: `_safe_text()` detects `.pdf`, `cache/`, `\cache\` substrings and paths starting with `/` or `~`, returning `redacted_path`. Test `test_annual_period_report_redacts_raw_pdf_or_cache_paths` asserts `/tmp/cache/report.pdf` absent and `redacted_path` present.

Status: **PASS**.

### C8: Renderer boundary — no repository/PDF/cache/provider/LLM access

Plan requirement: Renderer must consume only in-memory typed inputs.

Evidence: `annual_period_renderer.py` imports only `fund_agent.fund.annual_evidence` and standard library modules. No import of repository, PDF cache, source helper, downloader, provider, LLM, or filesystem document corpus. All inputs come through `AnnualPeriodReportRenderInput` dataclass.

Status: **PASS**.

### C9: Service boundary

Plan requirement: Service must not call repository/cache/PDF/source helper directly for annual-period report.

Evidence: `fund_analysis_service.py:803-814` calls `render_annual_period_report()` with an `AnnualPeriodReportRenderInput` constructed from in-memory `annual_bundle`, `current_year_result.report_markdown`, and quality gate fields. No repository or source helper is invoked in the annual-period report assembly path.

Status: **PASS**.

### C10: Annual-period report sections

Plan requirement: Minimum sections — title, coverage/source, cross-year facts, impact, gaps/degradation, current-year report.

Evidence: Renderer produces five sections via `_render_title`, `_render_coverage_section`, `_render_cross_year_fact_section`, `_render_impact_section`, `_render_gap_section`, plus `## 当前年份报告` with embedded current-year report behind stable marker.

Status: **PASS**.

### C11: No public chapter id expansion beyond 0-7

Plan requirement: No new public chapter ids.

Evidence: Renderer does not introduce chapter ids. The `## 当前年份报告` section embeds the existing current-year report unchanged.

Status: **PASS**.

### C12: Empty current-year report fail-closed

Plan requirement: Fail closed on empty current-year report.

Evidence: `_validate_render_input` raises `ValueError("current_year_report_markdown 不能为空")` when report is empty. Test `test_annual_period_report_fails_closed_on_empty_current_year_report` covers this.

Status: **PASS**.

## Validation Re-Run

```text
uv run ruff check fund_agent/fund/template/annual_period_renderer.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Result: All checks passed.

```text
uv run pytest tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
```

Result: 115 passed in 1.10s.

```text
git diff --check
```

Result: pass.

## Findings

| Finding | Severity | Disposition |
|---|---|---|
| No findings | — | — |

All 12 contract checks pass. No scope boundary violations, no out-of-scope file modifications, no missing guardrails.

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Additional controlled live annual-period samples | Controller / evidence owner | Separate controlled live gate only if explicitly authorized |
| Release/readiness claim | Release owner | Still not claimed; requires separate readiness gate |
| Coverage measurement | Coverage owner | Deferred environment/coverage hygiene gate |
| `source_fund_id` current-year structured-data identity extension | Fund/source identity owner | Deferred structured-data source identity extension gate |
| MiMo targeted re-review channel residual from planning gate | Controller / agent setup owner | Does not affect implementation behavior; recorded in controller judgment |

## Verdict

`ACCEPT`

Implementation stays within the accepted plan write set, preserves Fund/Service/UI boundaries, locks `report_markdown` current-year compatibility, consumes the explicit `annual_period_report` field in CLI, applies wording/quality-gate/gap/fail-closed/redaction guardrails with deterministic test coverage, and updates README to reflect current behavior without overstating live/readiness/release status.
