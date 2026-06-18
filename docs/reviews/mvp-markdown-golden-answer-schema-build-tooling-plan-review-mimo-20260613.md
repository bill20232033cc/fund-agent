# MiMo Review - Markdown / Golden Answer Schema Build-tooling Plan

Date: 2026-06-13

Target:
`docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-plan-20260613.md`

Reviewer role: MiMo-style read-only plan review

Verdict: `ACCEPT_WITH_NONBLOCKING_RESIDUALS_NOT_READY`

## Scope

This was a read-only plan review. It did not modify source, tests, runtime
behavior, golden answers, fixture promotion state, release/readiness state, PR
state or cleanup state. It did not run live EID, network, PDF, FDR, provider,
LLM, analyze, checklist, golden-build, readiness, release, PR, push or merge
commands.

## Findings

| Severity | Finding | Evidence | Recommendation | Controller disposition |
|---|---|---|---|---|
| None | No blocker or required rewrite. | `docs/design.md` defines identity as `fund_code + report_year + field_name + sub_field`; current Markdown parser is legacy 2024; strict JSON loader already keys by fund/year/field/sub-field; plan covers legacy, cross-year, duplicate, metadata-error and preflight coverage paths. | Accept plan for controller judgment. | ACCEPT |
| Low | Slice B says preflight integration is optional while validation matrix requires preflight coverage. | Existing `tests/fund/test_golden_readiness_preflight.py` already covers year-not-covered and matching-year behavior; plan additionally suggests optional metadata-build integration. | Clarify in controller judgment that existing preflight year coverage must be preserved, while build-from-metadata preflight integration is required only if parser/build tests do not already prove the path sufficiently. | ACCEPT_WITH_CONTROLLER_AMENDMENT |

## Residuals / Deferred Items

| Item | Status |
|---|---|
| Legacy protection | Adequate; Markdown without metadata and legacy JSON without `report_year` stay 2024. |
| Allowed write set | Adequate; tracked `reports/golden-answers/*`, fixture promotion, source policy, readiness and release are excluded. |
| Duplicate fund-year blocks | Non-blocking ambiguity: implementation should either fail fast or document behavior if the same `fund_code/report_year` is split across headings without duplicate rows. |
| Readiness | Remains `NOT_READY`; plan does not authorize content edits, fixture promotion, source policy changes, readiness, release or PR. |
