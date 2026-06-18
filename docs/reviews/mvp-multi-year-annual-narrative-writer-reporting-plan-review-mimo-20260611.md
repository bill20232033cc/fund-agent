# Plan review: multi-year annual narrative writer/reporting

## Reviewer

AgentMiMo, independent plan reviewer.

## Gate

`multi-year annual narrative writer/reporting planning gate`.

## Verdict

`ACCEPT`

## Truth Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- Plan: `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md`
- Prior controller judgment: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-controller-judgment-20260611-231045.md`
- Prior controller judgment: `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-controller-judgment-20260611-175745.md`

## Focus Question Assessment

### 1. Does the plan correctly target the real product gap?

**Yes.** Current `analyze-annual-period` stdout is a machine-readable metadata header (canonical years, available/gap/fail-closed years, cross-year fact count, fallback count, source provenance by year) followed by a target-year single-year 8-chapter report body. The plan correctly identifies this as a metadata summary + target-year report, not a formal annual-period report. The proposed output shape preserves the metadata header, adds a formal annual-period narrative (coverage/source, cross-year changes, impact, gaps/degradation), and embeds the current-year report as a nested section. This is the correct product gap.

### 2. Does the renderer/result contract preserve Fund/Service/UI boundaries?

**Yes.** The plan specifies:

- Renderer location in `fund_agent/fund/` (Fund layer), consuming only in-memory typed inputs (`AnnualEvidenceBundle`, current-year report markdown, explicit quality gate status).
- Explicit prohibition: "no repository, PDF/cache/source helper, downloader, provider, LLM, filesystem document corpus or live command."
- Service assembles result from injected annual evidence loader; does not call repository/cache/PDF/source helper directly.
- CLI prints metadata header + report body; does not access Fund internals.
- No `extra_payload` for explicit product/reporting parameters.

This respects the `UI -> Service -> Host -> Agent` boundary. Fund owns domain rendering, Service owns orchestration, UI owns display.

### 3. Is the output contract acceptable?

**Yes.** The plan:

- Preserves the machine-readable metadata header for evidence/debugging.
- Adds formal annual-period narrative without inventing public chapter ids outside `0-7`.
- Embeds current-year `# 0` to `# 7` report unchanged.
- Defers full report taxonomy redesign to a later reviewed gate.

### 4. Are claims bounded enough?

**Yes.** The plan specifies:

- "bounded deterministic language only"
- "no prediction, no buy/sell language, no unsupported causality"
- "if facts are insufficient, state insufficiency and next minimum validation question"
- Cross-year facts must cite typed facts/source years or degrade explicitly
- "cross-year facts must not be converted into stronger investment conclusions than their typed values support"

### 5. Are slices and validation sufficient for a no-live gate?

**Yes.** Four implementation slices with clear allowed files, implementation requirements, and test requirements. Validation commands are deterministic: `ruff check`, `pytest`, `git diff --check`. No live/provider/LLM commands required.

## Findings

### F1: `MultiYearAnnualAnalysisResult.report_markdown` compatibility decision needs test lock (non-blocking)

The plan (line 98) says: "`MultiYearAnnualAnalysisResult.report_markdown` may be changed to return the annual-period report because this method backs the user-facing `analyze-annual-period` product output. If changed, tests must explicitly lock the new behavior."

The compatibility decision is acknowledged but left open. Slice 2 tests should explicitly lock whichever choice is made. If `report_markdown` changes to return annual-period report, existing tests that assert on `report_markdown` content must be updated. If it stays as current-year, Slice 3 CLI tests must verify the new annual-period report is printed.

**Disposition:** non-blocking; Slice 2 already has "decide and test whether `MultiYearAnnualAnalysisResult.report_markdown` returns annual-period report or remains current-year report" as an explicit requirement.

### F2: Renderer location preference is unresolved (non-blocking)

The plan (line 104-106) offers two locations: `fund_agent/fund/annual_period_report.py` or `fund_agent/fund/template/annual_period_renderer.py`. The plan says "if local reviewer prefers all report rendering under `template/`."

The existing deterministic renderer lives in `fund_agent/fund/template/renderer.py`. Placing the annual-period renderer under `template/` would be consistent with the existing rendering module boundary. However, the plan correctly adjusts ruff targets if either location is chosen, so this is a preference, not a blocker.

**Disposition:** non-blocking; recommend `fund_agent/fund/template/annual_period_renderer.py` for consistency with existing renderer location, but either is acceptable.

### F3: "Quality gate caveat if provided" is underspecified (non-blocking)

The plan (line 123) mentions "quality gate caveat if provided" in the annual coverage section. It is unclear what this means: does the renderer receive the full `QualityGateResult`, or just a status string, or a boolean "has caveat"? The plan should clarify the input contract for this field.

**Disposition:** non-blocking; implementation can resolve this by passing quality gate status as a simple string or omitting it if not available. The annual-period report renderer should not depend on full quality gate internals.

### F4: Slice 4 wording guard is vague (non-blocking)

The plan (line 229) says: "add a minimal deterministic wording guard for the annual-period report if not covered by existing template renderer guard." It is unclear what specific wording is being guarded against, or what form the guard takes (regex, allowlist, blocklist).

**Disposition:** non-blocking; the existing renderer already guards against buy/sell wording and unsupported causality. The annual-period renderer can reuse the same guard pattern. Implementation should define the specific guard in the slice.

### F5: No explicit test for "all prior years are gaps" edge case (non-blocking)

The plan (line 165-168) lists test requirements for Slice 1: full five-year, partial gap/fail-closed, nonzero fallback, forbidden wording, no raw PDF paths. However, it does not explicitly list a test for the case where all prior years are gaps (only target year available). This is a boundary case where the annual-period report would have a minimal cross-year section.

**Disposition:** non-blocking; the "partial gap/fail-closed bundle" test implicitly covers this, but an explicit all-gaps test would strengthen coverage.

### F6: Cross-year fact data shape is not re-specified in plan (non-blocking)

The plan references `CrossYearDerivedFact` (line 126) but does not re-specify its fields. This is acceptable because the type is already defined in `fund_agent/fund/annual_evidence.py` from the accepted productization implementation at `61ab780`. The renderer should import and consume the existing type.

**Disposition:** non-blocking; the existing type is sufficient.

## Accepted Residuals

| Residual | Owner | Next handling |
|---|---|---|
| `MultiYearAnnualAnalysisResult.report_markdown` compatibility decision | Implementation owner | Resolve in Slice 2; lock choice with explicit tests |
| Renderer location under `fund_agent/fund/` vs `fund_agent/fund/template/` | Implementation owner | Choose one; adjust ruff targets per plan |
| Coverage measurement for new modules | Controller / coverage owner | Single-file coverage remains unmeasured in local environment; deterministic functional tests are the acceptance gate |
| No live implementation verification | Controller | Plan explicitly excludes live commands; implementation gate uses deterministic validation only |
| Current-year `source_fund_id` still deferred | Fund/source identity owner | Remains deferred from productization gate; does not block annual-period report |

## Validation Performed (static only)

- Read all truth inputs listed above.
- Verified plan non-goals align with `AGENTS.md` §1.3 non-goals and `docs/implementation-control.md` non-goal reminder.
- Verified plan boundaries align with `AGENTS.md` §2 module boundaries (UI/Service/Host/Agent).
- Verified plan rendering contract prohibits repository/PDF/source access outside Fund, consistent with `AGENTS.md` §2.1 hard constraints.
- Verified plan preserves EID single-source policy, consistent with `docs/design.md` §6.1 and `docs/current-startup-packet.md` §3.
- Verified plan does not introduce public chapter ids beyond `0-7`, consistent with `docs/design.md` §3.2.
- Verified plan slices are compatible with no-live deterministic validation.
- Verified plan acceptance criteria are checkable without live commands.
- Cross-checked plan output shape against existing `AnnualEvidenceBundle` fields from productization implementation at `61ab780`.
- Cross-checked plan rendering sections against existing Chapter 5 cross-year fact projection from `ChapterFactProvider.project_annual_evidence()`.

## Explicit Statement

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands were run in this review. No source/test/runtime file was edited. No design/control/startup docs were modified. No stage/commit/push/PR/delete/move/archive/clean actions were taken.
