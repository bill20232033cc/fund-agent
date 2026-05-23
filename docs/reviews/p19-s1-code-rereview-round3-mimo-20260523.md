# P19-S1 Code Re-review Round 3 - MiMo

Date: 2026-05-23 01:03:57 +0800
Reviewed HEAD: `3ea3d80` (`fix: reject trimmed thermometer source dates`)
Role: one of P19-S1 code re-review round 3 reviewers.

## Scope

- P19-S1 self-owned 沪深300 index thermometer MVP only.
- Focused on the round-2 blocker: string date normalization must not truncate or trim; only exact `YYYY-MM-DD` strings are accepted.
- Re-checked prior accepted findings:
  - insufficient history sample fail-closed;
  - cache save failure still computes from fresh in-memory history;
  - Service source/cache/calculation failure domains remain split.
- Checked for scope expansion into `fund-analysis analyze`, all-A thermometer, or PB-only all-A thermometer.

## Verdict

PASS

## Findings

No blocking or non-blocking findings in this review scope.

## Evidence

### 1. Strict string-date contract is closed

`fund_agent/fund/data/thermometer_source.py:200-228` now handles date values as follows:

- `None` fails closed before normalization.
- `datetime` objects are accepted and converted with `value.date().isoformat()`.
- `date` objects are accepted and converted with `value.isoformat()`.
- All other values are converted with raw `str(value)` at line 219. There is no `strip()` and no slicing.
- `ISO_DATE_PATTERN.fullmatch(text)` at lines 222-223 validates the whole string against `^\d{4}-\d{2}-\d{2}$`.
- `datetime.strptime(text, "%Y-%m-%d")` at lines 224-227 rejects impossible dates such as `2026-02-30`.

This directly closes both prior failure modes: the earlier `text[:10]` truncation and the later `strip()` acceptance of leading/trailing whitespace.

Covered rejected examples in `tests/fund/data/test_thermometer_source.py:153-183`:

- `"2026-05-22T00:00:00"`
- `"2026-05-22 00:00:00"`
- `"2026-05-22abc"`
- `" 2026-05-22"`
- `"2026-05-22 "`
- `" 2026-05-22 "`

### 2. `date` / `datetime` object acceptance remains intentional

The implementation still accepts object-typed dates:

- `datetime` path: `fund_agent/fund/data/thermometer_source.py:215-216`
- `date` path: `fund_agent/fund/data/thermometer_source.py:217-218`

The test suite keeps the positive `date` object coverage in `tests/fund/data/test_thermometer_source.py:186-206`. I did not find a dedicated `datetime` object test in the current suite, but the code path is explicit and executes before the broader `date` branch, so `datetime(2026, 5, 22, ...)` will normalize to `2026-05-22`. This matches the requested contract that object-typed `date` / `datetime` values remain accepted while timestamp-shaped strings fail closed.

### 3. Prior accepted findings did not regress

- Sample insufficiency remains fail-closed: `fund_agent/fund/analysis/thermometer_calculator.py:45-48` raises `ThermometerCalculationError` when `len(history.points) < MIN_HISTORY_POINTS`, currently 30.
- Cache save failure still uses fresh history: `fund_agent/services/thermometer_service.py:204-208` catches only `OSError` from `cache.save(history)` and then calculates from the in-memory `history`.
- Failure domains remain split: `fund_agent/services/thermometer_service.py:189-203` catches only `ThermometerSourceError` around `load_index_history()` for stale-cache/unavailable fallback. Calculation contract errors occur outside that catch path and are not converted to unavailable.

### 4. No new scope expansion found

- Supported self-owned index symbols remain limited to `{"000300": "沪深300"}` in `fund_agent/fund/data/thermometer_source.py:19`.
- The production entry remains `fund-analysis thermometer --index`, routed through `fund_agent/ui/cli.py:245-292`.
- `rg` found production `ThermometerService` / `ThermometerRequest` usage only in `fund_agent/ui/cli.py`; I found no `fund-analysis analyze` integration, no all-A market thermometer implementation, and no PB-only all-A path.

## Residual Risks

- Live akshare availability and live upstream column drift were not validated in this review; this was a static/unit-focused re-review of HEAD.
- Cache load restores stored date strings without re-running the strict source date validator. This is not a new blocker for the source schema-drift fix, but manually edited or corrupted cache content can still rely on cache corruption handling rather than source schema validation.
- `datetime` object values intentionally drop the time component. That is consistent with the requested review contract, but it means object-typed timestamps are tolerated while timestamp-shaped strings are rejected.

## Validation Notes

Commands run:

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
```

Result: `60 passed in 0.50s`

```bash
.venv/bin/python -m ruff check fund_agent/fund/data/thermometer_source.py fund_agent/fund/analysis/thermometer_calculator.py fund_agent/fund/data/thermometer_cache.py fund_agent/services/thermometer_service.py tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py
```

Result: `All checks passed!`
