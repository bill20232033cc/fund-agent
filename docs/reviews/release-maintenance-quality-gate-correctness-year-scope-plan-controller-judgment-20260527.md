# Gate 1 Plan Controller Judgment

> Date: 2026-05-27
> Gate: correctness report_year scope fix
> Plan: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-20260526.md`
> Review artifacts:
> - `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-review-mimo-20260527.md`
> - `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-review-glm-20260527.md`

## Verdict

**ACCEPTED FOR IMPLEMENTATION**

Both independent plan reviews returned `PASS_WITH_FINDINGS`. No finding blocks implementation, but several findings become mandatory implementation-review checks.

## Findings Disposition

| Reviewer | Finding | Disposition | Controller judgment |
|---|---|---|---|
| MiMo | `_snapshot_actual_index()` must extract `report_year` from each snapshot record | Accepted | Implementation must read the year from each record and key actual values by `(fund_code, report_year, field_name, sub_field)`. |
| MiMo | Current legacy golden set safely defaults to `2024` | Accepted | Current curated records are treated as legacy 2024 rows; this is a compatibility rule, not a new golden truth claim. |
| MiMo | `CORRECTNESS_COVERAGE_YEAR_NOT_COVERED` constant and quality gate handler required | Accepted | Implementation must add explicit constants and a FQ0/info handler; missing handler would be a runtime regression. |
| GLM F1 | `_correctness_coverage()` must be year-scoped | Accepted | This is mandatory. `fund_not_covered` means no fund-code golden at all; `year_not_covered` means fund-code golden exists but current report year is absent. |
| GLM F2 | Same `fund_code` may appear in multiple `GoldenAnswerFund` entries across years | Accepted | Loader and duplicate detection must allow different years and reject only duplicate `(fund_code, report_year, field_name, sub_field)`. |
| GLM F3 | Integration test must explicitly use a `report_year=2025` bundle | Accepted | Required focused integration test. |
| GLM F4 | Product smoke unrelated failure classes should be classified | Accepted | Closeout must separate correctness-year regressions from unrelated PDF/network/NAV/turnover/checklist-run-id failures. |
| GLM F5 | `quality_gate.py` must handle `year_not_covered` in available correctness coverage | Accepted | Required focused quality-gate test. |

## Implementation Handoff Requirements

The implementation agent must:

1. Keep the oracle identity at least `fund_code + report_year + field_name + sub_field`.
2. Preserve same-year mismatch as FQ1/block.
3. Convert wrong-year missing coverage into FQ0/info `year_not_covered`, with no mismatch rows and no FQ1 block.
4. Avoid Service/CLI/default analyze/checklist behavior changes unless a failing test proves a minimal explicit propagation fix is required.
5. Avoid renderer, report-writing audit, Host/Agent/dayu, `FundDocumentRepository`, source helper, NAV, turnover-rate, checklist run-id, and quality-gate policy changes.
6. Add tests for legacy golden compatibility, build serialization, duplicate identity, same-year mismatch, wrong-year coverage, quality gate FQ0/info, and single-bundle integration.

## Next Step

Proceed to Gate 1 implementation handoff to `AgentCodex` via tmux `$init-agents` workflow. Controller will review the returned diff, run focused validation, dispatch at least two code reviews, and only then update control state and commit.
