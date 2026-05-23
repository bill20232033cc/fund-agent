# P19-S5 Aggregate Deepreview Controller Judgment — 2026-05-23

## Scope

- Phase: P19 thermometer independent development
- Gate: P19-S5 aggregate deepreview / phase readiness review
- Design truth: `docs/design.md` v2.2 §11
- Control truth: `docs/implementation-control.md`
- Aggregate reviews:
  - `docs/reviews/p19-s5-aggregate-deepreview-ds-20260523.md`
  - `docs/reviews/p19-s5-aggregate-deepreview-glm-20260523.md`
- Included accepted commits:
  - `f4ee668` source feasibility acceptance
  - `c540334` implementation plan acceptance
  - `459038b` S5-1 capability source
  - `7a173ec` S5-1 bookkeeping
  - `5eb922c` S5-2 Service/cache
  - `ff9ff07` S5-2 bookkeeping
  - `355874b` S5-3 CLI/docs
  - `2ab9b33` S5-3 bookkeeping

## Controller Decision

Verdict: `ACCEPTED_AGGREGATE_REVIEW`

P19-S5 is accepted for ready-to-open-draft-PR reconciliation. GLM returned `PASS`; DS returned `PASS_WITH_FINDINGS` with four low-severity findings. None undermine the phase goal: all-A PE/PB source feasibility was proven, the Capability source contract uses the accepted `date` / `middlePETTM` / `middlePB` shape, Service/cache route no-index requests to `wind_all_a` without leaking source fields upward, CLI/docs expose all-A as the default thermometer path, and P19-S3 analyze behavior remains limited to exact supported index integration.

Based on `docs/design.md` §11 and first principles, the implementation now forms a coherent self-owned all-A thermometer slice across Capability, Service, cache, UI, tests, and documentation while preserving module boundaries and failure semantics.

## Findings Judgment

### DS F1 — Retry Budget Asymmetry

- Status: accepted non-blocking residual
- Owner: future production hardening
- Reasoning: All-A now has bounded retry and both index/all-A paths have stale-cache and unavailable degradation. Harmonizing retry policy is operational hardening, not required for correctness.

### DS F2 — Duplicate Date Handling Asymmetry

- Status: accepted non-blocking residual
- Owner: future Capability data-quality cleanup
- Reasoning: The index path last-wins behavior is pre-existing and was intentionally not changed in S5-1 to avoid widening scope. All-A uses stricter fail-closed semantics as required by the accepted source contract.

### DS F3 — Legacy Public-Page Adapter Path Is Unreachable

- Status: accepted non-blocking residual
- Owner: future transitional adapter cleanup
- Reasoning: S5-2/S5-3 intentionally changed the default CLI/Service path to self-owned all-A. The legacy adapter remains transitional/comparison code and should be removed or explicitly re-exposed only in a separate cleanup gate.

### DS F4 — All-A `asyncio.gather` Exception Wrapping

- Status: accepted non-blocking residual
- Owner: future async-hardening cleanup if the source is used in a true async runtime
- Reasoning: Current usage is synchronous through Service/CLI and normal source exceptions are wrapped at the fetcher layer. The remaining case is theoretical cancellation/async runtime behavior and not a current correctness blocker.

## Accepted Guarantees

- All-A source uses `akshare.stock_a_ttm_lyr()` + `akshare.stock_a_all_pb()` with exact `date`, `middlePETTM`, and `middlePB`.
- `wind_all_a` is a market code and cannot masquerade as a six-digit index.
- Source parsing is fail-closed for schema drift, invalid dates, invalid numerics, non-finite values, and conflicting duplicates.
- Service defaults no-index thermometer requests to `wind_all_a`; CLI does not hard-code the default route.
- Cache separates `market/wind_all_a_history.json` from `index/*.json` and unsupported cache files cannot bypass support checks.
- Source failure degrades through stale cache or unavailable output; calculation contract errors propagate.
- CLI/help/README docs expose all-A as default `fund-analysis thermometer` behavior.
- `fund-analysis analyze` is not expanded to all-A; exact `000300` / `000905` P19-S3 behavior remains the only automatic thermometer-to-valuation integration.

## Validation

Recorded across the accepted slice gates:

```text
pytest tests/fund/data/test_thermometer_source.py -q
37 passed

pytest tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py -q
33 passed

pytest tests/ui/test_cli.py -q
38 passed

pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
108 passed

pytest tests/services/test_fund_analysis_service.py -q
20 passed

ruff check required S5 files
All checks passed!

git diff --check
passed with no output
```

## Next Gate

Proceed to `P19-S5 ready-to-open-draft-PR reconciliation`.

The next controller step must reconcile the exact inclusion set, exclusion set, validation status, residual owners, and draft PR authorization boundary. It must not push or create a draft PR without explicit user authorization.
