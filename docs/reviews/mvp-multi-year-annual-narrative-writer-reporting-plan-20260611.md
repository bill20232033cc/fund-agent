# MVP multi-year annual narrative writer/reporting plan

## Worker Self-Check

- Gate: `multi-year annual narrative writer/reporting planning gate`.
- Classification: `standard` for planning; implementation should be classified `heavy` because it changes user-facing `analyze-annual-period` report output.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, accepted multi-year productization checkpoint `61ab780`, and accepted live evidence checkpoint `271a052`.
- Worker-channel residual: AgentCodex pane could not be used for this planning handoff after `/fast off` stalled on transport timeout; controller wrote this planning artifact directly under phaseflow controller allowlist and must obtain independent MiMo + DS review before acceptance.
- This artifact is planning only. It does not modify source/tests/runtime behavior and does not authorize implementation until reviewed and accepted.

## Current Facts

- `fund-analysis analyze-annual-period` is current code fact and calls Service `analyze_multi_year_annual()`.
- `MultiYearAnnualAnalysisResult.report_markdown` currently returns `current_year_result.report_markdown`; it is still a target-year single-year 8-chapter report body.
- CLI `_echo_multi_year_annual_summary()` emits machine-readable annual-period metadata before the report body, including canonical years, available/gap/fail-closed years, cross-year fact count, fallback count and source provenance by year.
- Fund `AnnualEvidenceBundle` already contains `cross_year_facts`, `available_years`, `gap_years`, `fail_closed_years`, source provenance, anchors, degradation summary and fallback summary.
- `ChapterFactProvider.project_annual_evidence()` / `project_annual_evidence_chapter_facts()` already project annual evidence facts into chapter id `5` under `annual_evidence.cross_year.*`.
- The deterministic template renderer currently renders Chapter 5 as largely insufficient-data prose and does not consume annual-period facts in a formal cross-year narrative.
- Controlled live evidence for `004393 / 2021-2025` is accepted as a single-sample EID single-source/no-fallback evidence fact; it does not imply release/readiness, golden promotion or all-fund live acceptance.

## Goal

Turn the accepted annual-period evidence bundle into a formal deterministic annual-period report output, so users no longer receive only:

1. a machine-readable annual evidence summary; and
2. a target-year single-year report body.

The product output should become a coherent annual-period report for `target_year + optional prior years`, while preserving current source policy, evidence anchoring, quality gate semantics and the existing single-year report path.

## Non-Goals

- No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands in implementation verification.
- No new annual-report source, fallback expansion, Eastmoney, fund-company/CDN, CNINFO or source-policy change.
- No provider/LLM writer and no `--use-llm` behavior change.
- No public chapter id expansion beyond `0-7`.
- No replacement of current-year `StructuredFundDataBundle` as canonical target-year structured truth.
- No raw PDF text, raw parsed full report text or raw five-year report body in prompts/artifacts.
- No score-loop, golden/readiness promotion, release/PR state, cleanup/ignore-rule or artifact disposition.
- No direct Service/UI/Host access to repository, PDF cache, source helpers or downloader internals.
- No use of `extra_payload` for explicit product/reporting parameters.

## Product Contract Decisions

Controller amendment after DS/MiMo plan review:

- `MultiYearAnnualAnalysisResult.report_markdown` must remain the target-year current report in this gate. This avoids a silent semantic break for existing consumers that treat the field as the current-year report.
- The annual-period report must be exposed through an explicit named field, preferably `annual_period_report: AnnualPeriodReportRenderResult`.
- The CLI `analyze-annual-period` command must consume `result.annual_period_report.report_markdown` for the user-facing annual-period report body after the existing metadata header.
- Any future change to `MultiYearAnnualAnalysisResult.report_markdown` semantics requires a separate compatibility/deprecation audit gate.

### Output shape

The implementation should keep the existing machine-readable annual-period summary available for evidence/debugging, but the primary stdout report body for `analyze-annual-period` should become a formal annual-period report rather than the target-year-only report.

Recommended shape:

```text
fund_code: ...
target_year: ...
canonical_years: ...
available_years: ...
gap_years: ...
fail_closed_years: ...
cross_year_fact_count: ...
fallback_year_count: ...
source[YYYY]: ...

# 多年年报分析（2021-2025）
...

## 当前年份报告

# 0. 投资要点概览
...
```

Rationale:

- preserve the current CLI metadata header so controlled evidence and downstream scripts can still parse provenance without reading raw report prose;
- add a formal annual-period narrative before or around the current-year report;
- do not invent public chapter ids outside `0-7`;
- keep current-year `# 0` to `# 7` report available as an embedded current-year section until a later reviewed gate redesigns public report taxonomy.

### New typed report result

Recommended Service result additions:

```python
@dataclass(frozen=True, slots=True)
class AnnualPeriodReportRenderResult:
    report_markdown: str
    period_summary_markdown: str
    current_year_report_markdown: str
    available_years: tuple[int, ...]
    gap_years: tuple[int, ...]
    fail_closed_years: tuple[int, ...]
    cross_year_fact_count: int
```

`MultiYearAnnualAnalysisResult` should gain an explicit field such as `annual_period_report: AnnualPeriodReportRenderResult`, or an equivalent named field that makes the annual-period report distinct from the target-year report.

Compatibility decision:

- `current_year_result.report_markdown` remains the target-year report.
- `MultiYearAnnualAnalysisResult.report_markdown` remains the target-year report in this gate.
- CLI must print `result.annual_period_report.report_markdown` for `analyze-annual-period` report body output.
- Tests must lock that `current_year_result.report_markdown` and `MultiYearAnnualAnalysisResult.report_markdown` still match, while `annual_period_report.report_markdown` contains the formal annual-period report.

## Rendering Contract

Add a deterministic renderer for the annual-period report. Recommended location:

- `fund_agent/fund/annual_period_report.py`, or
- `fund_agent/fund/template/annual_period_renderer.py` if local reviewer prefers all report rendering under `template/`.

The renderer must consume only in-memory typed inputs:

- `AnnualEvidenceBundle`;
- current-year report markdown or `TemplateRenderResult`;
- current-year checklist/final judgment/quality gate status only if passed explicitly by Service;
- no repository, PDF/cache/source helper, downloader, provider, LLM, filesystem document corpus or live command.

Minimum annual-period sections:

1. `# 多年年报分析（YYYY-YYYY）`
2. `## 年度覆盖与来源`
   - canonical years;
   - available/gap/fail-closed years;
   - source provenance summary by year;
   - fallback count;
   - explicit quality gate status line.
3. `## 跨年关键变化`
   - render each eligible `CrossYearDerivedFact` with `fact_type`, source years and value summary;
   - if categories are unavailable, show typed fact id and fact type rather than prose inference;
   - include evidence anchors or a precise "anchor not emitted" residual line.
4. `## 对当前判断的影响`
   - bounded deterministic language only;
   - no prediction, no buy/sell language, no unsupported causality;
   - if facts are insufficient, state insufficiency and next minimum validation question.
5. `## 缺口与降级`
   - list gap years and fail-closed years;
   - explain which cross-year claims were not made because evidence was missing or fail-closed.
6. `## 当前年份报告`
   - embed current-year 8-chapter report unchanged, or with a stable separator only.

Evidence wording requirements:

- numeric or year-level claims must cite source years and source field ids where available;
- if CLI/reporting cannot emit safe document identity, render `document_identity=not_emitted` rather than infer;
- cross-year facts must not be converted into stronger investment conclusions than their typed values support.
- quality gate context must never be silently omitted: if Service provides no quality gate status, render `quality_gate_status=not_available` and a bounded note that no pass/readiness claim is made from the annual-period report.
- the `对当前判断的影响` section must have a section-specific wording guard test that fails on buy/sell language, return prediction wording or unsupported causal phrasing.

## Implementation Slices

### Slice 1: Annual-period report renderer

Allowed files:

- new `fund_agent/fund/annual_period_report.py` or `fund_agent/fund/template/annual_period_renderer.py`;
- `tests/fund/test_annual_period_report.py` or local equivalent.

Implementation requirements:

- define typed render input/result dataclasses;
- render deterministic Markdown from `AnnualEvidenceBundle` plus current-year report markdown;
- include annual coverage/source table, cross-year fact section, impact section and gaps/degradation section;
- preserve current-year report text as a nested section without rewriting its content;
- fail closed on empty current-year report or invalid annual evidence bundle identity;
- do not parse raw PDF/report text to derive facts.

Tests:

- full five-year available bundle renders coverage table and cross-year facts;
- partial gap/fail-closed bundle renders gaps and does not over-claim;
- all-prior-years-gap bundle renders a minimal annual-period report and states cross-year evidence insufficiency;
- fallback count is surfaced and nonzero fallback is a visible caveat, not hidden;
- forbidden buy/sell wording is absent;
- missing quality gate context renders `quality_gate_status=not_available`;
- raw PDF/cache/source paths are not rendered.

### Slice 2: Service result assembly

Allowed files:

- `fund_agent/services/fund_analysis_service.py`;
- `fund_agent/services/__init__.py` if a new public type is exported;
- `tests/services/test_fund_analysis_service.py`.

Implementation requirements:

- after `AnnualEvidenceLoader.load(...)`, build the annual-period report result from the annual evidence bundle and current-year report;
- keep target-year `current_year_result` unchanged;
- expose explicit annual-period report field on `MultiYearAnnualAnalysisResult`;
- keep `MultiYearAnnualAnalysisResult.report_markdown` as the current-year report and test that this compatibility contract remains locked;
- do not let Service call repository/cache/PDF/source helper directly.

Tests:

- service result contains both current-year report and annual-period report;
- current-year report remains identical to `current_year_result.report_markdown`;
- `MultiYearAnnualAnalysisResult.report_markdown` remains identical to `current_year_result.report_markdown`;
- annual-period report includes cross-year summary when bundle has cross-year facts;
- annual-period report degrades when prior years are gaps/fail-closed;
- Service uses injected annual evidence loader only and no live/source helper.

### Slice 3: CLI reporting surface

Allowed files:

- `fund_agent/ui/cli.py`;
- `tests/ui/test_cli.py`.

Implementation requirements:

- `fund-analysis analyze-annual-period` should keep the current machine-readable annual-period summary header;
- stdout report body after the header should be `result.annual_period_report.report_markdown`;
- quality gate summary remains on stderr through existing `_echo_quality_gate_summary()`;
- no new CLI option is required for MVP unless reviewers decide a compatibility switch is necessary;
- do not run live CLI commands in tests.

Tests:

- fake service output proves CLI prints metadata header plus annual-period report;
- CLI no longer prints only target-year report for annual-period command;
- CLI test proves it uses the explicit annual-period report field rather than `MultiYearAnnualAnalysisResult.report_markdown`;
- options `--target-year`, `--start-year`, `--valuation-state`, `--quality-gate-policy`, `--force-refresh` remain accepted;
- `checklist`, single-year `analyze`, and `analyze --use-llm` outputs are unchanged.

### Slice 4: Programmatic guardrails and docs

Allowed files:

- targeted tests under `tests/fund/`, `tests/services/`, `tests/ui/`;
- README files triggered by actual source changes:
  - `README.md` if user-facing CLI output changes;
  - `fund_agent/README.md` if Service/Fund boundary explanation changes;
  - `fund_agent/fund/README.md` if a Fund renderer/module is added;
  - `tests/README.md` if new test layer/file is added.

Implementation requirements:

- add a deterministic wording guard for the annual-period report if not covered by existing template renderer guard;
- add a targeted guard for the `对当前判断的影响` section that catches buy/sell language, return prediction wording and unsupported causal phrasing;
- do not claim release/readiness or golden promotion;
- update docs only for current behavior after implementation, not future aspiration.

Validation for implementation gate:

```bash
uv run ruff check fund_agent/fund/annual_period_report.py fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
uv run pytest tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
git diff --check
```

If implementation chooses `fund_agent/fund/template/annual_period_renderer.py` instead of `fund_agent/fund/annual_period_report.py`, adjust the ruff target accordingly.

## Acceptance Criteria

The future implementation gate may be accepted only if:

- `analyze-annual-period` produces a formal annual-period report body, not only a target-year report plus metadata summary;
- current-year target report remains available and traceable;
- annual-period narrative is derived only from `AnnualEvidenceBundle` and explicit current-year analysis results;
- all cross-year claims cite typed facts/source years or degrade explicitly;
- EID single-source policy and repository boundary remain unchanged;
- no live/provider/LLM/golden/readiness/release command is run;
- deterministic tests cover full five-year, gap, fail-closed and no-cross-year-fact paths;
- user-facing README reflects the new `analyze-annual-period` output honestly.

## Review Request

MiMo and DS should review:

- whether output contract should change `MultiYearAnnualAnalysisResult.report_markdown` or keep it current-year-only with a separate annual-period field;
- whether the recommended renderer location respects Fund/Service/UI boundaries;
- whether the report sections are sufficient without creating public chapter ids beyond `0-7`;
- whether annual-period claims are bounded enough to avoid unsupported investment conclusions;
- whether implementation slices and validation are narrow enough for a no-live gate.

## Next Entries

Recommended next mainline after plan acceptance:

1. `multi-year annual narrative writer/reporting implementation gate`.

Deferred entries:

- additional controlled live annual-period samples;
- structured-data source identity extension;
- coverage measurement environment hygiene;
- runtime artifact disposition for `reports/live-evidence` and quality-gate outputs;
- release-readiness residual acceptance evidence.
