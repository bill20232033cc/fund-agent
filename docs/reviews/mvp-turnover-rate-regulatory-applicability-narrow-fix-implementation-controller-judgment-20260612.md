# Controller Judgment - Turnover Rate Regulatory Applicability Narrow Fix Implementation

Date: 2026-06-12

Gate: `Turnover rate regulatory applicability narrow fix implementation gate`

Verdict: `ACCEPT_WITH_RESIDUALS_NOT_READY`

## Basis

- `AGENTS.md`: evidence must be source-traceable; root cause must be same-source; no source acquisition/fallback expansion without gate.
- `docs/current-startup-packet.md`: current active gate is the narrow turnover-rate regulatory applicability implementation gate.
- `docs/implementation-control.md`: accepted input is the quality warning identity evidence, regulatory applicability evidence, and narrow fix plan/controller judgment.
- `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-plan-controller-judgment-20260612.md`: accepted report-year cutoff and row-level non-annual metadata rules.
- Implementation evidence: `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-implementation-evidence-20260612.md`.
- DS review: `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-implementation-review-ds-20260612.md`.
- MiMo review/re-review: `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-implementation-review-mimo-20260612.md`.

## Judgment

The implementation is accepted for the current gate.

It changes scoring applicability only, leaves source acquisition and extractor behavior untouched, preserves `turnover_rate` as P1 for applicable rows, and excludes only non-applicable rows from `_scorable_records(...)`.

## Finding Disposition

| Finding | Disposition | Rationale |
|---|---|---|
| MiMo: `source_kind` was missing from explicit non-annual metadata keys | ACCEPT | Plan explicitly named `source_kind`; implementation now covers it with a known non-annual value allowlist. |
| MiMo: service FQ2F negative assertion used ineffective `field_name` | ACCEPT | Fund-level FQ2F has `field_name=None`; test now checks P1 FQ2F message content. |
| MiMo: invalid `report_year` fail-closed test missing | ACCEPT | Added regression test proving invalid year does not trigger exclusion. |
| DS: no blocking findings | ACCEPT | DS review aligns with validation and scope checks. |

## Accepted / Rejected / Residual Table

| Item | Status | Reason |
|---|---|---|
| pre-2026 turnover exclusion from field/fund/fund-quality scoring | ACCEPTED | Proven by targeted tests and shared `_scorable_records(...)` path. |
| 2026+ turnover missing remains P1 fail | ACCEPTED | Proven by targeted test. |
| explicit non-annual row metadata exclusion | ACCEPTED | Proven with `source_kind="quarterly_report"` and known-value allowlist. |
| invalid/missing year fail-closed exclusion | ACCEPTED | Invalid year remains P1 fail and produces no applicability decision. |
| replacement `ScoreApplicabilityIssue` for non-applicable turnover | REJECTED | Not needed; accepted behavior is no replacement issue for expected non-applicability. |
| source acquisition/fallback/extractor changes | REJECTED | Outside gate; no changes made. |
| release/readiness promotion | DEFERRED | This gate is not readiness proof; release/readiness remains `NOT_READY`. |

## Validation Accepted

```text
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py -q
122 passed in 1.12s

uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py tests/services/test_fund_analysis_service.py
All checks passed!

git diff --check
<no output>
```

## Residuals

| Residual | Owner | Next gate | Current blocker? |
|---|---|---|---|
| Release/readiness remains unproven | Release owner / controller | Release-readiness rollup | No for this gate; yes for release claim |
| Durable publication-date/template-version metadata absent from snapshot contract | Fund scoring owner | Future design/contract gate only if needed | No |
| Strict golden/readiness promotion not performed | Release/golden owner | Strict golden 2025 coverage / promotion planning gate | No for this gate |

## Next Entry

Recommended mainline next entry: `Strict golden 2025 coverage / promotion planning gate`.

Deferred entries:

- additional controlled-live sample evidence
- release-readiness rollup
- provider / LLM readiness
- source fallback / Eastmoney / CNINFO expansion
- cleanup / ignore / archive
