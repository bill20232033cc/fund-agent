# DS implementation review: multi-year annual narrative writer/reporting

## Verdict

**ACCEPT**

The implementation faithfully executes the accepted plan under the amended controller judgment. All 10 locked plan decisions are met, Fund/Service/UI boundaries are preserved, `report_markdown` compatibility is locked by tests, CLI output is correct, and guardrails are in place. No source/test/runtime/design/control/startup file was modified by this review.

## Review Scope

- Gate: `multi-year annual narrative writer/reporting implementation gate`
- Classification: `heavy` — changes user-facing `analyze-annual-period` report body
- Accepted plan: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md`
- Controller judgment: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-controller-judgment-20260611-233310.md`
- Implementation evidence: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-implementation-evidence-20260612.md`
- Review focus: accepted write set, Fund/Service/UI boundary, `report_markdown` compatibility, CLI `annual_period_report` output, `quality_gate_status=not_available`, gap/fail-closed/writing guard tests, README current behavior

## Validation Executed

```text
uv run ruff check fund_agent/fund/template/annual_period_renderer.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
→ All checks passed!

uv run pytest tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
→ 115 passed in 1.33s

git diff --check
→ pass
```

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command was run.

## Findings

### F1 — Write set within accepted plan (PASS)

All changed files match the plan's allowed file list:

- `fund_agent/fund/template/annual_period_renderer.py` (new, plan Slice 1) — chooses MiMo-preferred template/ location, stays within Fund boundary
- `fund_agent/services/fund_analysis_service.py` (Slice 2) — wires renderer into `analyze_multi_year_annual()`
- `fund_agent/services/__init__.py` (Slice 2) — exports `AnnualPeriodReportRenderResult`
- `fund_agent/ui/cli.py` (Slice 3) — prints `result.annual_period_report.report_markdown`
- `tests/fund/test_annual_period_report.py` (new, Slice 1+4)
- `tests/services/test_fund_analysis_service.py` (Slice 2+4)
- `tests/ui/test_cli.py` (Slice 3+4)
- `README.md`, `fund_agent/README.md`, `fund_agent/fund/README.md`, `tests/README.md` (Slice 4)

No files outside the plan were modified or created. No source-policy, fallback, Eastmoney, fund-company/CDN, or CNINFO change was introduced.

### F2 — Fund/Service/UI boundary intact (PASS)

Renderer location `fund_agent/fund/template/` is within Agent layer Fund domain capability. Renderer consumes only typed in-memory inputs (`AnnualEvidenceBundle`, `current_year_report_markdown`, explicit `quality_gate_status`/`quality_gate_not_run_reason`). No repository, PDF/cache, source helper, downloader, provider, LLM, filesystem document corpus, Service, Host, or dayu import.

Service (`analyze_multi_year_annual()`) constructs `AnnualPeriodReportRenderInput` from `annual_bundle` (Fund-owned) and `current_year_result` (Service-owned) — correct layering. Service does not directly access repository/PDF/cache/source helper.

CLI accesses only `result.annual_period_report.report_markdown` — no direct Fund/Agent import.

No new boundary violation: UI→Service→Fund remains the only call chain for annual-period reporting.

### F3 — `report_markdown` compatibility preserved (PASS)

`MultiYearAnnualAnalysisResult.report_markdown` property (line 330) returns `self.current_year_result.report_markdown` — unchanged.

Test lock (line 1467 in `test_fund_analysis_service.py`):
```python
assert result.report_markdown == result.current_year_result.report_markdown
assert result.annual_period_report.report_markdown != result.report_markdown
```

The explicit `annual_period_report` field carries the formal annual-period report. The current-year `report_markdown` path is untouched. This matches controller judgment locked decision 1 and 2.

### F4 — CLI `annual_period_report` output correct (PASS)

CLI change: `typer.echo(result.report_markdown, nl=False)` → `typer.echo(result.annual_period_report.report_markdown, nl=False)`.

Metadata header (`canonical_years`, `available_years`, `gap_years`, `fail_closed_years`, `cross_year_fact_count`, `fallback_year_count`, `source[YYYY]`) is preserved via `_echo_multi_year_annual_summary()`.

CLI test now uses separate `_FakeResult(report_markdown="# current year report\n")` and `_FakeAnnualPeriodReport(report_markdown="# annual period report\n")`, then asserts:
- `# annual period report` appears in output
- `# current year report` does NOT appear

This proves CLI uses the explicit `annual_period_report.report_markdown` field, not `MultiYearAnnualAnalysisResult.report_markdown`. Matches controller judgment locked decision 3.

### F5 — Quality gate / gap / fail-closed guardrails sufficient (PASS)

**Quality gate absence**: `render_annual_period_report()` uses `input_data.quality_gate_status or QUALITY_GATE_STATUS_NOT_AVAILABLE`. When Service passes `None` (no quality gate result), renderer outputs `quality_gate_status=not_available` with bounded note "未提供质量门控状态，本报告不据此声明通过或 readiness。" Matches controller judgment locked decision 7.

**Gap rendering**: `_render_gap_section()` surfaces `gap_years`, `fail_closed_years`, individual `data_gap` entries with status/category/message. All-prior-years-gap path outputs `impact_status=insufficient_evidence`. Matches plan acceptance criterion.

**Fail-closed on empty input**: `_validate_render_input()` raises `ValueError` on empty `current_year_report_markdown`, invalid `fund_code`, invalid `target_year`, and mismatched `current_year_bundle` identity. Matches plan Slice 1 requirement.

### F6 — Wording guard comprehensive (PASS)

`validate_annual_period_report_wording()` enforces three levels:

1. **Forbidden phrases** (global, on `period_summary_markdown`): `买入金额`, `卖出时机`, `买入信号`, `卖出信号`, `仓位比例`, `收益预测`
2. **Direct trading advice** (global): regex on `建议/推荐/应当/应该/直接/立即/马上` + `买入/卖出/加仓/减仓`
3. **Unsupported causal** (section-specific, on `对当前判断的影响` only): regex on `必然/一定会/保证/确保/导致收益/带来收益/决定收益`

Test `test_annual_period_report_wording_guard_rejects_forbidden_impact_text` parametrizes over `("建议买入", "收益预测", "必然带来收益")` and asserts `ValueError` with "禁用措辞". Matches controller judgment locked decision 8.

### F7 — PDF/cache path redaction (PASS)

`_safe_text()` normalizes whitespace, then checks for `.pdf`, `cache/`, `\cache\`, and absolute paths (`/` or `~` prefix), returning `redacted_path`. Test `test_annual_period_report_redacts_raw_pdf_or_cache_paths` injects `"/tmp/cache/report.pdf"` in a fact's `values_by_year` and asserts the raw path is absent while `redacted_path` appears. Matches plan evidence wording requirement.

### F8 — Test coverage matches plan requirement (PASS)

| Plan test requirement | Test |
|---|---|
| Full five-year available renders coverage + cross-year facts | `test_annual_period_report_renders_full_years_and_cross_year_facts` |
| Partial gap/fail-closed renders gaps without over-claiming | `test_annual_period_report_renders_gap_and_fail_closed_without_overclaim` |
| All-prior-years-gap renders minimal + insufficient evidence | `test_annual_period_report_renders_all_prior_years_gap_as_insufficient` |
| Fallback count surfaced | Coverage table includes `fallback_year_count` in both render and test |
| Forbidden buy/sell wording absent | `test_annual_period_report_wording_guard_rejects_forbidden_impact_text` |
| Missing quality gate → `not_available` | Verified in all-prior-years-gap test and service test |
| Raw PDF/cache paths not rendered | `test_annual_period_report_redacts_raw_pdf_or_cache_paths` |
| Service contains both reports | `test_multi_year_annual_analysis_maps_service_request_to_fund_scope` |
| `report_markdown` compatibility | Same service test asserts equality |
| CLI uses explicit annual-period field | `test_analyze_annual_period_cli_calls_multi_year_service` |

### F9 — README/docs reflect current behavior without overstatement (PASS)

All four README changes:

- **`README.md`**: Updates `analyze-annual-period` description from "stdout 仍输出目标年份 8 章 Markdown 报告" to "CLI 会先在 stdout 输出可解析的多年证据 metadata header，再输出正式多年年报 Markdown 报告；报告正文包含年度覆盖与来源、跨年关键变化、对当前判断的影响、缺口与降级，并在末尾保留目标年份 8 章报告" — accurate. Updates "已实现" to "输出正式多年年报报告和内嵌目标年份 8 章报告" — accurate, no readiness/release claim.
- **`fund_agent/README.md`**: Adds "再用 Fund 层 annual-period renderer 生成正式多年年报报告" — accurate boundary description.
- **`fund_agent/fund/README.md`**: Adds renderer entry with input/output contract, `quality_gate_status=not_available` caveat, and boundary statement — accurate, matches code.
- **`tests/README.md`**: Adds test file entry with "只使用内存 bundle，不触发真实 EID、PDF、cache、provider、LLM、Service、Host 或 dayu" — accurate.

No README claims live/readiness/release status. No future-aspiration language.

### F10 — All 10 controller judgment locked decisions met (PASS)

| # | Locked Decision | Status |
|---|---|---|
| 1 | `report_markdown` remains target-year current report | PASS — property returns `current_year_result.report_markdown` |
| 2 | Distinct `annual_period_report` field exists | PASS — `MultiYearAnnualAnalysisResult.annual_period_report: AnnualPeriodReportRenderResult` |
| 3 | CLI keeps metadata header, prints annual-period report body | PASS — `_echo_multi_year_annual_summary()` + `result.annual_period_report.report_markdown` |
| 4 | Renderer consumes only in-memory typed inputs | PASS — `AnnualEvidenceBundle` + `current_year_report_markdown` + explicit QG |
| 5 | No repository/PDF/cache/source helper/downloader/provider/LLM/filesystem | PASS — import surface checked |
| 6 | Output includes coverage/source, cross-year facts, impact, gaps/degradation, current-year report | PASS — all 5 sections + current-year marker present |
| 7 | Missing QG → `quality_gate_status=not_available`, no pass/readiness claim | PASS — explicit in renderer and tests |
| 8 | Section-specific wording guard for impact section | PASS — `_impact_section()` extraction + `_UNSUPPORTED_CAUSAL_PATTERN` |
| 9 | No public chapter id beyond 0-7 | PASS — `# 多年年报分析` uses title, not chapter id |
| 10 | No source-policy/fallback/Eastmoney/fund-company/CDN/CNINFO change | PASS — diff checked, no such imports |

## Minor Observations

**O1 (INFO)**: `_render_source_row` renders `"unavailable | unavailable"` for both source and fallback columns when `source_provenance_by_year` has no entry for a year. This is only reachable for gap/fail-closed years (target year always has provenance per `AnnualEvidenceLoader`), so the output is semantically correct — a gap year indeed has no available source.

**O2 (INFO)**: `quality_gate_not_run_reason` is rendered only when `quality_gate_status != not_available`. When `quality_gate_status == not_available` (the common case for deterministic path without quality gate), the reason is suppressed in favor of the standard `quality_gate_note`. This is slightly narrower than the plan's wording but is safer: it avoids leaking internal reason strings when the status itself already says "not available."

**O3 (INFO)**: `_CURRENT_YEAR_REPORT_MARKER` (`<!-- current_year_report:start -->`) is emitted before the embedded current-year report. This marker is not currently consumed programmatically but serves as a stable separator for future parsing — consistent with the plan's "stable separator only" instruction.

## Residual Risk

| Risk | Severity | Owner |
|---|---|---|
| Additional controlled live samples | LOW — plan and controller explicitly defer | Controller / evidence owner |
| Release/readiness claim | NONE — explicitly not claimed | Release owner |
| Coverage measurement environment | LOW — deferred to separate hygiene gate | Coverage owner |
| `source_fund_id` structured-data identity extension | LOW — deferred | Fund/source identity owner |
| MiMo re-review channel residual from planning gate | INFO — does not affect implementation behavior | Controller / agent setup owner |

No new residuals were introduced by this implementation.

## Review Conclusion

The implementation is narrow, faithful to the accepted plan, and fully guarded. All 10 controller judgment locked decisions are met. Fund/Service/UI boundaries are preserved. The `report_markdown` compatibility contract is locked by tests. CLI output is correct. Wording, quality-gate, gap, and fail-closed guardrails are present and tested. README documentation reflects current behavior without overstating readiness.

Verdict: **ACCEPT**.
