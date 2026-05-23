# P19-S1 Code Re-review Round 2 - MiMo（2026-05-23）

## Scope

- Reviewed HEAD: `d7ae07f` (`fix: enforce strict thermometer source dates`)
- Review role: one of P19-S1 code re-review round 2 reviewers.
- Requested focus:
  - Close prior blocker in `_normalize_date()`.
  - Confirm added regression tests for timestamp, space-separated time, trailing characters.
  - Re-check previously accepted findings: insufficient sample fail-closed, cache save failure uses fresh history, Service failure domains remain split.
  - Confirm no scope expansion beyond self-owned 沪深300 index thermometer MVP.

## Verdict

PASS

## Findings

No blocking or non-blocking findings in this review scope.

## Evidence

### 1. Prior blocker is closed

`fund_agent/fund/data/thermometer_source.py:200` now normalizes dates without truncating strings:

- `datetime` objects are accepted and converted via `value.date().isoformat()` (`:215-216`).
- `date` objects are accepted and converted via `value.isoformat()` (`:217-218`).
- String-like values are stripped, then validated with `ISO_DATE_PATTERN.fullmatch(text)` against the complete string (`:219-223`).
- Valid-looking strings are also checked with `datetime.strptime(text, "%Y-%m-%d")` (`:224-227`), so impossible dates fail closed.

This closes the previous `text[:10]` bug. Inputs like `"2026-05-22T00:00:00"`, `"2026-05-22 00:00:00"`, and `"2026-05-22abc"` no longer share an accepted first-10-character path because no substring is used before validation.

### 2. Regression tests cover the three rejected examples

`tests/fund/data/test_thermometer_source.py:153-176` parameterizes:

- `"2026-05-22T00:00:00"`
- `"2026-05-22 00:00:00"`
- `"2026-05-22abc"`

Each case flows through `AkshareIndexThermometerSource.load_index_history("000300")` and asserts `ThermometerSourceError` with `match="ISO"`. `tests/fund/data/test_thermometer_source.py:179-199` keeps the positive `date` object case.

### 3. Previously accepted findings did not regress

- Insufficient sample fail-closed: `fund_agent/fund/analysis/thermometer_calculator.py` keeps `MIN_HISTORY_POINTS = 30` and raises `ThermometerCalculationError` when `len(history.points) < MIN_HISTORY_POINTS`.
- Cache save failure uses fresh history: `fund_agent/services/thermometer_service.py` catches only `OSError` around `cache.save(history)` and then computes from the in-memory `history`.
- Service failure domains remain split: `ThermometerService._load_index_reading()` catches only `ThermometerSourceError` around `load_index_history()` for stale-cache/unavailable fallback. Calculation contract errors are outside that catch path and propagate.

### 4. Scope remains within P19-S1

- `SUPPORTED_INDEX_SYMBOLS` remains `{"000300": "沪深300"}`.
- The new self-owned path is still entered through `ThermometerRequest.index_code` / `fund-analysis thermometer --index`.
- I found no new `fund-analysis analyze` integration, no all-A implementation, and no PB-only all-A thermometer path in the reviewed HEAD.

## Residual Risks

- This review did not hit live akshare. It verifies strict local schema handling and unit/service behavior, not live upstream availability or live column drift.
- `datetime` object acceptance intentionally converts to date and drops time. That is consistent with the current request, which requires date/datetime objects to remain accepted while string timestamps fail closed.
- Cache write failure handling only treats `OSError` as non-fatal. That matches the accepted finding being fixed; other unexpected cache serialization/programming errors still propagate.

## Validation Notes

Commands run:

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
```

Result: `57 passed in 0.50s`

```bash
.venv/bin/python -m ruff check fund_agent/fund/data/thermometer_source.py tests/fund/data/test_thermometer_source.py fund_agent/fund/analysis/thermometer_calculator.py fund_agent/services/thermometer_service.py tests/services/test_thermometer_service.py
```

Result: `All checks passed!`
