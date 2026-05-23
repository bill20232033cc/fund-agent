# P19-S5 S5-2 Service, Cache Key, And Request Normalization Implementation — 2026-05-23

## Gate

- Work unit: P19-S5 all-A market thermometer
- Slice: S5-2 Service, Cache Key, And Request Normalization
- Role: AgentCodex implementation worker
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Approved plan: `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`
- S5-1 acceptance: `docs/reviews/p19-s5-s5-1-code-review-controller-judgment-20260523.md`

## Scope

Implemented only S5-2. No commit, no push, no PR, and no S5-3 CLI/docs work.

## Files Touched

- `fund_agent/services/thermometer_service.py`
- `fund_agent/fund/data/thermometer_cache.py`
- `tests/services/test_thermometer_service.py`
- `tests/fund/data/test_thermometer_cache.py`
- `docs/reviews/p19-s5-s5-2-service-cache-implementation-20260523.md`

## Implemented Items

- Changed Service default normalization so `ThermometerRequest()` materializes `wind_all_a`, making no-argument thermometer requests use the self-owned all-A pipeline instead of the transitional public-page adapter.
- Switched the default Service source to S5-1 `AkshareThermometerSource`, keeping Service free of akshare imports and source field knowledge.
- Updated Service normalization to accept exact `wind_all_a` or exact six ASCII digit codes, while rejecting other non-six-digit market-like tokens as malformed input.
- Replaced Service support checks with the S5-1 shared Capability classifier and display-name helper.
- Preserved unsupported well-formed six-digit code behavior as item-level unavailable, including cache-bypass prevention for forged `999999` cache files.
- Added all-A stale-cache fallback on source failure and all-A unavailable output without cache, with `index_code="wind_all_a"` and `index_name="万得全 A / 全 A 市场"`.
- Updated cache key routing to use the shared Capability classifier:
  - `cache/thermometer/market/wind_all_a_history.json`
  - `cache/thermometer/index/000300_history.json`
  - `cache/thermometer/index/000905_history.json`
- Made cache load return miss for unsupported codes and cache save fail closed for unsupported codes.
- Preserved calculation contract behavior: stale cache with insufficient samples still propagates calculation error instead of becoming unavailable.

## Tests Added Or Updated

- Default no-index request routes to `wind_all_a` source and does not call public-page adapter.
- Explicit `index_code="wind_all_a"` returns all-A reading.
- Batch request with `wind_all_a`, `000300`, `000905` preserves order and de-duplicates.
- Malformed non-six-digit tokens, including `wind_all_a1`, non-ASCII digits, and unsupported market-like strings, remain request errors.
- Unsupported `999999` cannot be served from forged fresh cache.
- All-A stale cache fallback works after source failure.
- All-A source failure without cache returns unavailable with all-A code/name and unavailable valuation candidate.
- All-A stale cache calculation error propagates.
- Cache tests assert all-A market namespace, index namespace preservation, unsupported cache load miss, and unsupported save rejection.

## Validation

```text
pytest tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py -q
33 passed in 0.72s
```

```text
pytest tests/services/test_fund_analysis_service.py -q
20 passed in 0.60s
```

```text
ruff check fund_agent/services/thermometer_service.py fund_agent/fund/data/thermometer_cache.py tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py
All checks passed!
```

```text
git diff --check
passed with no output
```

## Docs Decision

No README updates in this slice. S5-2 allowed files exclude README and CLI docs, and the accepted plan assigns user-facing CLI/docs synchronization to S5-3.

## Residual Risks

- CLI help/output still reflects pre-S5-3 wording and is intentionally left for S5-3.
- Public-page adapter remains present as transitional capability but is no longer the Service no-argument default after this slice.
- Legulegu retry constants from DS S5-1 residual were not changed; S5-2 covers the assigned Service degradation behavior through source failure to stale cache and source failure to unavailable tests.
- Active-fund/analyze all-A fallback remains out of scope and belongs to a later valuation-state integration gate.

## Completion Status

S5-2 implementation complete. Changes are intentionally left uncommitted for controller review.
