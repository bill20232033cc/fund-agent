# Release Maintenance Slice C Controller Judgment — Layer Boundary Cleanup

## Scope

- Source finding: `docs/reviews/controller-judgment-repo-deepreview-20260523.md` Slice C.
- Handoff: `docs/reviews/release-maintenance-slice-c-layer-boundary-handoff-20260523.md`.
- Worker: implemented a focused boundary cleanup and added a static boundary regression test.

## Accepted Changes

- `fund_agent/ui/cli.py`
  - No longer imports thermometer result types from `fund_agent.fund.data.thermometer_types`.
  - Uses Service-facing exports from `fund_agent.services` for `ThermometerReading` and `ThermometerBatchResult`.
- `fund_agent/services/thermometer_service.py`
  - No longer imports `thermometer_cache.py` or `thermometer_source.py` concrete implementation modules directly for default construction.
  - Depends on `fund_agent.fund.data` public entrypoints and local Protocols for cache/source behavior.
- `fund_agent/fund/data/__init__.py`
  - Becomes the public Capability data entry for thermometer code classification, result types, source errors, and default source/cache factories.
- `tests/services/test_thermometer_service.py`
  - Adds an AST boundary regression test covering the forbidden UI/Service direct imports.
- `fund_agent/fund/README.md`
  - Documents `fund_agent/fund/data/__init__.py` as the public Service-facing thermometer data entry.

## Controller Verification

```bash
pytest tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
```

Result: `65 passed in 0.93s`.

```bash
ruff check fund_agent/ui/cli.py fund_agent/services/thermometer_service.py fund_agent/services/__init__.py fund_agent/fund/data/__init__.py tests/ui/test_cli.py tests/services/test_thermometer_service.py
```

Result: `All checks passed!`.

```bash
git diff --check
```

Result: passed.

## Judgment

Slice C is accepted. The patch preserves CLI output behavior while tightening the UI -> Service -> Capability boundary and adding a regression test that fails if the forbidden direct imports return.

## Residual Risk

Service still imports public Capability data symbols from `fund_agent.fund.data`, which is acceptable under current AGENTS.md boundaries. A fuller Application layer wrapper remains out of scope for this maintenance slice.
