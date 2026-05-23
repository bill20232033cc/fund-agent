# P19-S2 Code Re-review - MiMo - 2026-05-23

Review time: 2026-05-23 01:48:38 CST

Scope: current `HEAD` including `0a0045c fix: enforce thermometer supported index before cache`, focused on the prior blocker "well-formed unsupported index can be bypassed by fresh cache" and P19-S2 scope regression checks.

## Verdict: PASS

No blocker found. The prior blocker is fixed on the real Service/CLI path: supported-index coverage is checked before any index history cache read, so a fresh cache file for a well-formed unsupported code cannot produce an available reading.

## Findings

No blocking or non-blocking findings.

## Evidence Reviewed

- `fund_agent/services/thermometer_service.py:163` normalizes the request before dispatch, preserving a single Service-owned validation path.
- `fund_agent/services/thermometer_service.py:216` checks `is_supported_index_code(index_code)` before constructing `ThermometerHistoryCache` at `fund_agent/services/thermometer_service.py:223` and before `cache.load(index_code)` at `fund_agent/services/thermometer_service.py:225`. This directly closes the fresh-cache bypass.
- `fund_agent/services/thermometer_service.py:217` returns `ThermometerUnavailable(...).to_reading()` for unsupported but well-formed codes, so batch item-level unavailable remains exit-0-compatible.
- `fund_agent/services/thermometer_service.py:296` to `fund_agent/services/thermometer_service.py:301` keeps `index_code` and `index_codes` mutually exclusive and routes both through `_normalize_index_codes`.
- `fund_agent/services/thermometer_service.py:305` to `fund_agent/services/thermometer_service.py:335` rejects malformed codes, empty items, empty batches, and duplicate-normalizes by preserve-order de-duplication.
- `fund_agent/fund/data/thermometer_source.py:19` declares only `000300` and `000905` as supported; `fund_agent/fund/data/thermometer_source.py:28` to `fund_agent/fund/data/thermometer_source.py:41` exposes the support predicate in the Capability data layer.
- `fund_agent/ui/cli.py:275` to `fund_agent/ui/cli.py:292` catches `ValueError` as exit 2 and unexpected exceptions as exit 1.
- `fund_agent/ui/cli.py:928` to `fund_agent/ui/cli.py:945` only splits CLI `--index` and leaves malformed shape validation to Service, preserving the UI thinness boundary.
- `fund_agent/ui/cli.py:804` to `fund_agent/ui/cli.py:807` and `fund_agent/ui/cli.py:835` to `fund_agent/ui/cli.py:858` serialize single and batch thermometer results without changing analyze behavior.
- `fund_agent/ui/cli.py:93` to `fund_agent/ui/cli.py:205` still takes `--valuation-state` explicitly for `analyze`; no automatic thermometer-to-analyze integration was added.
- Diff scope from `0a4c3d2..HEAD` under `fund_agent/` is limited to `fund_agent/fund/README.md`, `fund_agent/fund/data/__init__.py`, `fund_agent/fund/data/thermometer_source.py`, `fund_agent/fund/data/thermometer_types.py`, `fund_agent/services/thermometer_service.py`, and `fund_agent/ui/cli.py`; no `fund_analysis_service.py`, renderer, Engine, all-A, or no-index public-page adapter implementation file was changed.
- `README.md:165` to `README.md:174` documents current supported `000300`/`000905`, batch behavior, unsupported item unavailable exit 0, malformed exit 2, and no automatic `analyze --valuation-state` mapping.
- `fund_agent/fund/README.md:307` to `fund_agent/fund/README.md:314` keeps P19-S1/S2 self-owned thermometer inside Fund data/cache/calculator and records no public-page fallback and no analyze integration.

## Verification Commands

```bash
git status --short
git log --oneline -5
git show --stat --oneline 8ddad68
git show --stat --oneline 0a0045c
rg -n "thermometer|index.*000300|000905|supported index|supported_index|unsupported" fund_agent tests docs README.md
nl -ba fund_agent/fund/data/thermometer_source.py | sed -n '1,260p'
nl -ba fund_agent/services/thermometer_service.py | sed -n '1,420p'
nl -ba fund_agent/ui/cli.py | sed -n '245,430p'
nl -ba fund_agent/ui/cli.py | sed -n '780,975p'
nl -ba fund_agent/fund/data/thermometer_cache.py | sed -n '1,220p'
nl -ba fund_agent/fund/data/thermometer_types.py | sed -n '1,220p'
nl -ba tests/services/test_thermometer_service.py | sed -n '1,620p'
nl -ba tests/ui/test_cli.py | sed -n '938,1260p'
nl -ba tests/fund/data/test_thermometer_source.py | sed -n '1,280p'
.venv/bin/python -m pytest tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer_source.py -q
rg -n "ThermometerService|thermometer|--index|valuation_state|ValuationState|FundThermometerAdapter|load_thermometer|index_codes" fund_agent/services fund_agent/ui fund_agent/fund | head -n 200
git diff --name-only 0a4c3d2..HEAD -- fund_agent | sort
git diff --stat 0a4c3d2..HEAD
```

Target test result:

```text
60 passed in 0.64s
```

## Residual Risks

- I did not run the full repository test suite; coverage was limited to the P19-S2 thermometer source, Service, and CLI paths relevant to this re-review.
- The supported-index predicate is duplicated conceptually with `SUPPORTED_INDEX_SYMBOLS`/`INDEX_NAMES`; current code uses the same module-level map, so this is not a present correctness issue, but future support expansion should keep the single map as the source of truth.
- Live akshare behavior for `000905` was not exercised in this re-review; tests verify symbol mapping and schema behavior with injected fetchers, which is appropriate for deterministic unit coverage.
