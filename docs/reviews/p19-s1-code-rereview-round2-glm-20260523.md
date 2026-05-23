# P19-S1 Code Re-review Round 2 - Reviewer 2

Date: 2026-05-23
Reviewed HEAD: `d7ae07f`
Scope: P19-S1 self-owned CSI 300 thermometer MVP only.

## Verdict

`BLOCKED`

The previous timestamp / suffix examples are fixed, but the strict date-string contract is still not fully closed. `_normalize_date()` strips string values before validating, so raw strings with leading or trailing whitespace are accepted even though they are not complete strict `YYYY-MM-DD` strings.

## Findings

### F1 - Date schema drift still accepts leading/trailing characters

Severity: Blocking

Evidence:

- `fund_agent/fund/data/thermometer_source.py:219-223` converts every non-`date`/`datetime` value with `str(value).strip()` before `ISO_DATE_PATTERN.fullmatch(text)`.
- Because validation runs after `strip()`, values such as `" 2026-05-22 "` pass and normalize to `"2026-05-22"`.
- Direct reproduction on current HEAD:

```bash
.venv/bin/python -c 'from fund_agent.fund.data.thermometer_source import _normalize_date; print(_normalize_date(" 2026-05-22 "))'
```

Observed output:

```text
2026-05-22
```

What can go wrong:

The accepted finding required schema drift to fail closed. A raw string containing leading/trailing characters is not a complete strict `YYYY-MM-DD` payload; accepting it silently weakens the data-source schema boundary in the same way as the prior `text[:10]` truncation, just through whitespace normalization instead of slicing.

Suggested fix:

For string inputs, validate the original string value without trimming. If non-string objects are intentionally supported through `str(value)`, apply the same no-trim rule to the stringified value, or narrow accepted non-string types to explicit `date` / `datetime` only. Add regression tests for `" 2026-05-22"` and `"2026-05-22 "`.

## Non-blocking Checks Passed

- Timestamp / time suffix regression examples are covered by `tests/fund/data/test_thermometer_source.py:153-176`: `"2026-05-22T00:00:00"`, `"2026-05-22 00:00:00"`, and `"2026-05-22abc"` now expect `ThermometerSourceError`.
- `date` objects remain accepted by `tests/fund/data/test_thermometer_source.py:179-205`; the implementation also accepts `datetime` objects through `value.date().isoformat()` at `fund_agent/fund/data/thermometer_source.py:215-216`.
- Sample-size fail-closed remains in place at `fund_agent/fund/analysis/thermometer_calculator.py:45-48`.
- Service failure domains remain split:
  - Source fallback only catches `ThermometerSourceError` at `fund_agent/services/thermometer_service.py:189-203`.
  - Cache save failure catches only `OSError` and computes from fresh in-memory history at `fund_agent/services/thermometer_service.py:204-208`.
  - Calculation contract errors are not wrapped by the source-unavailable path.
- Scope remains constrained: self-owned thermometer is routed only through `fund-analysis thermometer --index` at `fund_agent/ui/cli.py:245-292`; `fund-analysis analyze` does not call `ThermometerService`, and `AkshareIndexThermometerSource` supports only `000300`.

## Residual Risks

- The current cache format stores date strings without revalidating strict date format on load. This is not a new blocker for the round-2 source-fix review, but stale or manually edited cache content can still enter the calculator if it has valid PE/PB values and enough points.
- `datetime` values are intentionally accepted and normalized to dates. This is consistent with the requested review item, but it means upstream object-typed timestamp columns are tolerated while timestamp-shaped strings fail closed.

## Validation Notes

Commands run:

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
.venv/bin/python -m ruff check fund_agent tests
.venv/bin/python -c 'from fund_agent.fund.data.thermometer_source import _normalize_date; print(_normalize_date(" 2026-05-22 "))'
```

Results:

- Targeted P19-S1 test set: `57 passed in 0.50s`
- Ruff: `All checks passed!`
- Manual adversarial reproduction: leading/trailing whitespace date string was accepted, which keeps the strict date blocker open.

