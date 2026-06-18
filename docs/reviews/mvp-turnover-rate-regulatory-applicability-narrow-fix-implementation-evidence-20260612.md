# Turnover Rate Regulatory Applicability Narrow Fix Implementation Evidence

Date: 2026-06-12

Gate: `Turnover rate regulatory applicability narrow fix implementation gate`

Verdict: `IMPLEMENTED_PENDING_CONTROLLER_ACCEPTANCE`

## Inputs

- Control truth: `docs/implementation-control.md`
- Startup truth: `docs/current-startup-packet.md`
- Accepted plan: `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-plan-20260612.md`
- Plan controller judgment: `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-plan-controller-judgment-20260612.md`

## Scope

Allowed write set used:

- `fund_agent/fund/extraction_score.py`
- `tests/fund/test_extraction_score.py`
- `tests/services/test_fund_analysis_service.py`
- `docs/reviews/` implementation/review/controller artifacts
- `docs/current-startup-packet.md` and `docs/implementation-control.md` for control sync after acceptance

Explicitly not changed:

- extractor code
- source acquisition / repository / cache / downloader / FDR / fallback
- `fund_agent/fund/quality_gate.py`
- provider / LLM / live / golden / readiness / release / PR behavior
- README, because no public user or package documentation described turnover-rate scoring applicability semantics before this gate

## Implementation Summary

- Kept `turnover_rate` as a P1 field in `FIELD_PRIORITY_BY_NAME`.
- Added turnover-rate applicability constants:
  - `TURNOVER_RATE_DISCLOSURE_EFFECTIVE_REPORT_YEAR = 2026`
  - `TURNOVER_RATE_PRE_EFFECTIVE_REASON = "turnover_rate_pre_effective_report_year"`
  - `TURNOVER_RATE_NON_ANNUAL_REASON = "turnover_rate_non_annual_report"`
- Routed the exclusion through `_scorable_records(...)`, so the same denominator applies to:
  - `score_snapshot_records(...)`
  - `score_fund_records(...)`
  - `derive_fund_quality_records(...)`
- Excluded `turnover_rate` only when:
  - `report_year < 2026`; or
  - row-level report-kind metadata explicitly indicates a known non-annual report through `document_kind`, `report_type`, `report_kind`, or `source_kind`.
- Preserved fail-closed behavior:
  - `report_year >= 2026` remains applicable and missing values still fail P1.
  - missing/invalid `report_year` does not trigger exclusion.
  - unknown report-kind strings do not trigger exclusion.
- Added a `FieldApplicabilityDecision` for excluded turnover rows with:
  - `applicability_status="not_applicable_excluded"`
  - `denominator_effect="excluded_no_replacement_issue"`
  - `contract_id="turnover_rate_disclosure_applicability.v1"`
  - `replacement_issue_ids=()`
- Removed the prior practical blocker where field applicability decisions returned early when a fund had no `holdings_snapshot`; existing bond holdings decisions remain conditional on holdings records.

## Acceptance Criteria Evidence

| Criterion | Evidence | Result |
|---|---|---|
| pre-2026 `turnover_rate` no longer creates field-level P1 fail | `tests/fund/test_extraction_score.py::test_pre_2026_turnover_rate_is_excluded_from_p1_scoring_with_decision` asserts no `turnover_rate` field score | PASS |
| pre-2026 exclusion does not suppress unrelated applicable P1 failures | same test keeps `product_profile` as P1 fail and `benchmark` as P0 fail | PASS |
| 2026+ missing `turnover_rate` still fails P1 | `test_2026_turnover_rate_missing_still_fails_p1_scoring` | PASS |
| explicit non-annual metadata excludes `turnover_rate` | `test_explicit_non_annual_turnover_rate_is_excluded_even_after_2026` with `source_kind="quarterly_report"` | PASS |
| applicability decisions explain each exclusion | pre-2026 and non-annual tests assert reason codes | PASS |
| no replacement `ScoreApplicabilityIssue` for expected non-applicability | pre-2026 test asserts `derive_score_applicability_issues(records) == ()` | PASS |
| existing index/bond applicability unchanged | full target `tests/fund/test_extraction_score.py` and `tests/fund/test_quality_gate.py` passed | PASS |
| manually supplied failed turnover score rows still create quality warnings | `tests/fund/test_quality_gate.py::test_run_quality_gate_warns_turnover_only_p1_failure_without_fq4` passed; `quality_gate.py` unchanged | PASS |

## Validation

```text
$ uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py -q
........................................................................ [ 59%]
..................................................                       [100%]
122 passed in 1.12s
```

```text
$ uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py tests/services/test_fund_analysis_service.py
All checks passed!
```

```text
$ git diff --check
<no output>
```

## Residuals

| Residual | Disposition |
|---|---|
| Regulatory applicability evidence remains evidence-chain support, not release/readiness proof | accepted residual; release/readiness remains `NOT_READY` |
| Additional durable metadata such as publication-date or template-version is absent from current snapshot contract | deferred; current first fix intentionally uses `report_year` and explicit row-level report-kind metadata only |
| Broader strict golden promotion / readiness / additional live sample evidence | deferred to separate gates |

## Next Recommended Entry

`Strict golden 2025 coverage / promotion planning gate`
