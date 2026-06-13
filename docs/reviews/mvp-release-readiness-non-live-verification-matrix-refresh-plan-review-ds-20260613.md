# DS Review: Release-readiness Non-live Verification Matrix Refresh Plan

Date: 2026-06-13

Reviewed artifact:
`docs/reviews/mvp-release-readiness-non-live-verification-matrix-refresh-plan-20260613.md`

Verdict: `PASS_WITH_FINDINGS`

## Findings

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| F1 | Non-blocking | V13 only asserted nested `funds[0].records`; it did not also assert top-level `records` and `record_count` for `004393 / 2025`. The loader mainly consumes `funds`, so this is not an execution blocker, but the plan target is generated JSON row-scope and the flat record surface is part of that output. | V13 in the plan; generated JSON contains both nested and flat records. | Before controller acceptance, extend V13 to check `payload["records"]` for `004393 / 2025` identities/count and consistency with nested records. |
| F2 | Non-blocking | V13/V14 are long `python -c` one-liners. They are read-only and boundary-acceptable, but shell quoting and future auditability are weaker than a short script body. V14 also uses private `_load_fixture_promotion_states`, which is acceptable for bounded evidence but not a long-term public contract. | V13/V14 in the plan. | Do not block. Record that the one-liners are accepted only as bounded evidence commands. |

## Scope Checks

| Check | Result |
|---|---|
| V11-V15 cover latest accepted facts | PASS. V11 covers year-aware golden identity and `year_not_covered`; V12/V14 cover manifest JSON and exact `(fund_code, report_year)` parser identity; V13 covers row-scope and negative fee/turnover/skipped assertions; V15 covers exact-year, wrong-year, legacy, duplicate, unknown-field and wrong-identity fail-closed behavior. |
| Planning-only boundary | PASS. Non-goals, forbidden commands/paths and allowed writes prohibit source/tests/runtime/golden/manifest/fixture/design/README edits and live/provider/LLM/analyze/checklist/readiness/release/PR/push/merge/cleanup. |
| Allowed commands | PASS. No direct live/provider/LLM/analyze/checklist/readiness/release/PR external-state command is authorized. Static `rg` patterns mention those terms only as search strings. |
| Readiness posture | PASS. Plan preserves `NOT_READY` and does not overclaim readiness. |

## Residuals

- Release/readiness, PR/push/merge/mark-ready and external state remain unauthorized.
- Live/provider/LLM/analyze/checklist commands remain separate reviewed gates.
- Fee rows, `turnover_rate`, skipped/deferred rows and other fund/year scope remain residual.
- V13 flat-record consistency should be handled as a non-blocking amendment.

## Recommendation

Accept as `PASS_WITH_FINDINGS` after recording F1/F2 as non-blocking amendments
or accepted risks. The next entry should be exactly:

`Release-readiness Non-live Verification Matrix Refresh Evidence Gate`

This review did not modify files and did not run live/provider/LLM/analyze/
checklist/readiness/release/PR/push/merge/cleanup commands.
