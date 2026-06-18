# MiMo-role Review: Turnover Rate Regulatory Applicability Narrow Fix Plan

Date: 2026-06-12

Review target:
`docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-plan-20260612.md`

Reviewer role: AgentMiMo-role

Verdict: `PASS_WITH_AMENDMENTS`

## Findings

| ID | Severity | Finding | Controller disposition |
| --- | --- | --- | --- |
| `MIMO-PLAN-001` | amendment | The turnover exclusion must be applied through shared `_scorable_records(...)` and verified across `score_snapshot_records`, `score_fund_records`, and `derive_fund_quality_records`. | Accepted and amended. |
| `MIMO-PLAN-002` | amendment | Add regression coverage proving pre-2026 turnover exclusion does not suppress unrelated P1 failures in the same active-fund record set. | Accepted and amended. |
| `MIMO-PLAN-003` | amendment | Add protection that existing bond/index applicability decisions remain unchanged after touching `_fund_field_applicability_decisions(...)`. | Accepted and amended. |

## Review Answers

- Plan is code-generation-ready and narrow enough.
- Report-year cutoff is acceptable as the first fix under the current snapshot
  contract.
- Plan preserves extractor/source/quality-gate semantics.
- Tests are sufficient after the added regression requirements.

## Final Recommendation

Accept the plan with amendments and proceed to
`Turnover rate regulatory applicability narrow fix implementation gate`.
