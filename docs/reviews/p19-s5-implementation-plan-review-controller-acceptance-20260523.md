# P19-S5 Implementation Plan Review Controller Acceptance — 2026-05-23

## Scope

- Phase: P19 thermometer independent development
- Gate: P19-S5 all-A market thermometer implementation plan/review
- Design truth: `docs/design.md` v2.2 §11
- Control truth: `docs/implementation-control.md`
- Plan: `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`
- Plan reviews: `docs/reviews/p19-s5-implementation-plan-review-ds-20260523.md`, `docs/reviews/p19-s5-implementation-plan-review-glm-20260523.md`
- Plan re-reviews: `docs/reviews/p19-s5-implementation-plan-rereview-ds-20260523.md`, `docs/reviews/p19-s5-implementation-plan-rereview-glm-20260523.md`

## Controller Decision

Verdict: `ACCEPTED PLAN`

The initial implementation plan was directionally correct but could not be handed to implementation until it closed the all-A fixture date-column error and made the source/service/cache architecture decisions explicit. The patched plan now freezes the all-A source shape to `date`, `middlePETTM`, and `middlePB`; separates no-arg all-A fetchers from symbol-based index fetchers through `AkshareAllAMarketThermometerSource` plus composite dispatch; materializes default `wind_all_a` routing in `_normalize_request()`; and requires a shared Capability classifier for source, cache, and Service.

Based on `docs/design.md` §11 and first principles, this is the right minimal implementation path: extend the existing self-owned thermometer pipeline without changing the calculator, without making UI or Service call akshare directly, without using Youzhiyouxing as production source, and without changing P19-S3 analyze behavior beyond exact supported-index integration.

## Accepted Review Findings

### F1 — All-A Fixture Date Column

- Status: fixed.
- Reasoning: all-A PE/PB akshare outputs use English `date`; using Chinese `日期` copied from index fixtures would make source tests false-positive.

### F2 — Source Adapter Architecture

- Status: fixed.
- Reasoning: separate all-A source plus composite dispatch avoids mixing no-arg all-A fetchers with symbol-based index fetchers and keeps `wind_all_a` from masquerading as a six-digit index.

### F3 — Service Normalization And Default Routing

- Status: fixed.
- Reasoning: `_normalize_request()` and `_normalize_index_codes()` now have explicit plan-level behavior for default all-A routing and exact `wind_all_a` acceptance.

### F4 — Cache / Service / Source Classifier Consistency

- Status: fixed.
- Reasoning: a shared Capability classifier prevents divergent `wind_all_a` handling across cache path, Service support checks, and source dispatch.

### F5 — Analyze Non-Regression

- Status: fixed.
- Reasoning: plan now requires `tests/services/test_fund_analysis_service.py` coverage proving P19-S3 exact `000300` integration does not fall through to default all-A.

## Implementation Constraints

Implementation must follow the accepted slices in order:

1. S5-1 Capability Source Contract
2. S5-2 Service, Cache Key, And Request Normalization
3. S5-3 CLI Output And Docs Sync

Controller will dispatch one slice at a time. Implementation agents must not modify `docs/design.md`, `docs/implementation-control.md`, P19-S4 source coverage, or `fund-analysis analyze` behavior outside the P19-S3 non-regression checks.

## Next Gate

Proceed to `P19-S5 implementation S5-1 Capability Source Contract`.

Do not start S5-2 or S5-3 until S5-1 has implementation artifact, validation, code review, and controller acceptance.
