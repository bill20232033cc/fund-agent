# P19-S5 S5-1 Code Review Controller Judgment — 2026-05-23

## Scope

- Phase: P19 thermometer independent development
- Gate: P19-S5 S5-1 Capability Source Contract implementation/code review
- Design truth: `docs/design.md` v2.2 §11
- Control truth: `docs/implementation-control.md`
- Implementation artifact: `docs/reviews/p19-s5-s5-1-capability-source-implementation-20260523.md`
- Code reviews: `docs/reviews/p19-s5-s5-1-code-review-ds-20260523.md`, `docs/reviews/p19-s5-s5-1-code-review-glm-20260523.md`
- Reviewed files:
  - `fund_agent/fund/data/thermometer_source.py`
  - `tests/fund/data/test_thermometer_source.py`

## Controller Decision

Verdict: `ACCEPTED`

S5-1 is accepted. The implementation stays inside the Capability source-contract slice, adds a first-class all-A market source for `wind_all_a`, keeps the existing symbol-based index source separate, and exposes a shared classifier so later Service/cache work does not invent a divergent support check. The all-A source uses the accepted `akshare.stock_a_ttm_lyr()` / `akshare.stock_a_all_pb()` contract with exact `date`, `middlePETTM`, and `middlePB` fields, strict date and value parsing, duplicate conflict fail-closed behavior, and PE/PB common-date intersection without imputation.

Based on `docs/design.md` §11 and first principles, this is the minimal correct source-layer step: it makes the verified all-A data contract consumable by the self-owned thermometer pipeline without changing Service routing, cache keys, CLI defaults, public-page transitional behavior, or `fund-analysis analyze` integration.

## Review Finding Judgment

### DS F1 — Retry Attempts And Backoff Differ From Suggested Plan Constants

- Reviewer severity: low
- Controller status: accepted as non-blocking residual
- Decision: no S5-1 fix required

The accepted implementation plan listed `SOURCE_RETRY_ATTEMPTS = 3` and `SOURCE_RETRY_BACKOFF_SECONDS = 0.2` as suggested constants, not as a hard source-contract acceptance criterion. Current source behavior still performs a bounded retry, preserves exception cause, and fails closed into `ThermometerSourceError`; GLM independently judged this acceptable for S5-1. The remaining product risk is not incorrect data, but a potentially earlier transition to stale cache or unavailable during consecutive transient source failures.

This residual is assigned to S5-2 validation: Service/cache tests must cover source failure with stale all-A cache and source failure without cache returning unavailable all-A output. Future production hardening may raise the retry budget or add backoff if Legulegu availability data warrants it.

## Accepted Guarantees

- S5-1 did not modify Service, cache, CLI, README, `docs/design.md`, `docs/implementation-control.md`, P19-S4, renderer, audit, or analyze behavior before controller bookkeeping.
- `wind_all_a` is classified as a market code, not as a six-digit index.
- All-A PE/PB parsing fails closed on Chinese `日期`, missing required fields, non-strict dates, bool, non-numeric values, NaN, Infinity, and conflicting duplicate dates.
- Empty or non-positive all-A rows are dropped only within the source contract; empty valid common dates fail closed.
- Existing `000300` and `000905` index source behavior is preserved.
- The implementation report, DS review, and GLM review agree there are no blocking correctness, stability, or scope findings.

## Validation

Recorded by implementation worker and reviewers:

```text
pytest tests/fund/data/test_thermometer_source.py -q
37 passed

ruff check fund_agent/fund/data/thermometer_source.py tests/fund/data/test_thermometer_source.py
All checks passed!

git diff --check
passed with no output
```

Controller will rerun the focused validation before creating the accepted local commit.

## Next Gate

Proceed to `P19-S5 S5-2 Service, Cache Key, And Request Normalization implementation`.

S5-2 must keep source field knowledge out of Service, share the Capability classifier across Service/cache/source checks, route default no-index requests to `wind_all_a`, namespace all-A cache outside `index/`, and prove all-A stale-cache/unavailable degradation behavior.
