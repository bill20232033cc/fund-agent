# P19-S5 S5-3 CLI Output And Docs Sync Implementation

## Gate

- Work unit: P19-S5 all-A market thermometer
- Current gate: S5-3 CLI Output And Docs Sync implementation
- Role: AgentCodex implementation worker
- Approved plan: `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`
- Controller input: `docs/reviews/p19-s5-s5-2-code-review-controller-judgment-20260523.md`

## Scope

Implemented only S5-3. No changes were made to Service internals, valuation-state mapping, renderer, audit, design doc, control doc, source/cache internals, or PR/commit state.

## Files Touched

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p19-s5-s5-3-cli-docs-implementation-20260523.md`

`fund_agent/README.md` was not changed because this slice did not alter layering text or architecture boundaries.

## Implementation Summary

- Updated `fund-analysis thermometer --index` help to mention `wind_all_a`, `000300`, and `000905`.
- Updated `--force-refresh` help from public-page refresh wording to self-owned thermometer history data wording.
- Kept CLI no-argument request forwarding as `ThermometerRequest(index_code=None, index_codes=None)` so Service owns default all-A routing.
- Updated CLI tests so no-argument `thermometer --json` emits an all-A `ThermometerReading` payload through fake Service while asserting request fields remain `None`.
- Added CLI tests for:
  - `--index wind_all_a --json`
  - `--index wind_all_a,000300 --json` order preservation
  - malformed `--index wind_all_a,abc` exit 2
  - default all-A plain output including `index_code`, `index_name`, `source`, `temperature`, PE/PB percentiles, valuation candidate, and disclaimer
  - all-A unavailable JSON output
  - help text for all-A and self-owned history refresh wording
- Retained existing explicit `000300`, `000300,000905`, partial unavailable, unsupported well-formed code, malformed input, and service-error CLI coverage.
- Updated root README so all-A is the default thermometer CLI path and public-page snapshot is documented only as transitional/non-default.
- Updated Fund README to describe P19-S5 all-A coverage and market/index cache namespace.
- Updated tests README to describe all-A source/cache/service/CLI test coverage and no-live-network expectations.

## Validation

```text
pytest tests/ui/test_cli.py -q
38 passed in 0.81s
```

```text
pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
108 passed in 0.70s
```

```text
pytest tests/services/test_fund_analysis_service.py -q
20 passed in 0.44s
```

```text
ruff check fund_agent/fund/data/thermometer_source.py fund_agent/fund/data/thermometer_cache.py fund_agent/services/thermometer_service.py fund_agent/ui/cli.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py
All checks passed!
```

```text
git diff --check
passed
```

## Docs Decisions

- Root README now treats `fund-analysis thermometer` as the self-owned all-A default.
- Public-page adapter wording was retained only as transitional/comparison capability, not as the default CLI path.
- The README explicitly states `analyze` automatic valuation remains limited to exact supported-index behavior for `000300` and `000905`; it does not claim all-A is used by `analyze`.
- No `fund_agent/README.md` update was needed because Service/UI/Capability layer boundaries did not change in S5-3.

## Residual Risks

- No S5-3 blocker remains.
- Public-page adapter tests remain in their existing Capability test file, but the default CLI path no longer exercises public-page snapshot output. This is intentional per S5-3 scope.
- Existing untracked documents in the worktree were present before this slice and were not modified.

## Stop Status

S5-3 implementation is complete and left uncommitted as requested. No push, PR, commit, or aggregate review was performed.
