# P19-S1 Code Re-review Round 2 Controller Judgment（2026-05-23）

## Verdict

`BLOCKED_FIXED_PENDING_REREVIEW`

Round 2 produced split reviewer results:

- `docs/reviews/p19-s1-code-rereview-round2-mimo-20260523.md`: `PASS`
- `docs/reviews/p19-s1-code-rereview-round2-glm-20260523.md`: `BLOCKED`

The blocking finding is accepted because it has a direct reproduction: string dates were validated after `strip()`, so raw values with leading or trailing whitespace were silently normalized into valid dates. P19-S1 requires fail-closed handling for source schema drift; a raw string date must be exactly `YYYY-MM-DD`.

## Blocking Finding Judgment

| Finding | Source | Judgment | Handling |
|---|---|---|---|
| Date schema drift still accepts leading/trailing whitespace | GLM | Accepted | `_normalize_date()` now validates `str(value)` without `strip()`; regression tests reject leading, trailing, and surrounding whitespace. |

## Fix Summary

Files changed after round 2:

- `fund_agent/fund/data/thermometer_source.py`
- `tests/fund/data/test_thermometer_source.py`

The strict date tests now reject:

- `2026-05-22T00:00:00`
- `2026-05-22 00:00:00`
- `2026-05-22abc`
- ` 2026-05-22`
- `2026-05-22 `
- ` 2026-05-22 `

`date` and `datetime` object inputs remain explicitly accepted and normalized.

## Validation

```text
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
60 passed

.venv/bin/python -m ruff check fund_agent tests
All checks passed

git diff --check
passed

.venv/bin/python -c '... _normalize_date whitespace rejection ...'
rejected ' 2026-05-22'
rejected '2026-05-22 '
rejected ' 2026-05-22 '
```

## Next Gate

`P19-S1 code re-review round 3`

Round 3 should verify that the full strict string-date contract is now closed: no truncation, no trimming, only exact `YYYY-MM-DD` strings, while `date` and `datetime` objects remain accepted.
