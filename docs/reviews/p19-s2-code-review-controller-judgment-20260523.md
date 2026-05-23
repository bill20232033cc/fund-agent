# P19-S2 Code Review Controller Judgment（2026-05-23）

## Verdict

`BLOCKED_FIXED_PENDING_REREVIEW`

Two independent code reviews returned:

- `docs/reviews/p19-s2-code-review-mimo-20260523.md`: `PASS`
- `docs/reviews/p19-s2-code-review-glm-20260523.md`: `BLOCKED`

The blocking finding is accepted. A well-formed unsupported index must remain item-level unavailable even if a local fresh cache file exists. Support coverage is part of the current self-owned thermometer contract and must be checked before cache reuse.

## Accepted Finding

| Finding | Source | Judgment | Handling |
|---|---|---|---|
| Unsupported well-formed index can become available when fresh cache exists | GLM | Accepted | Added Capability/data `is_supported_index_code()` and made `ThermometerService` return `ThermometerUnavailable` before fresh/stale cache lookup for unsupported codes. |

## Fix Summary

Files changed after code review:

- `fund_agent/fund/data/thermometer_source.py`
- `fund_agent/services/thermometer_service.py`
- `tests/services/test_thermometer_service.py`
- `tests/ui/test_cli.py`

Added regression coverage:

- Service batch `("000300", "999999")` with a fresh `999999_history.json` still returns `999999` as unavailable and does not call source for `999999`.
- CLI `fund-analysis thermometer --index 000300,999999 --json --cache-dir <dir>` exits 0 and reports the unsupported item unavailable even when `999999_history.json` exists.

## Validation

```text
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
81 passed

.venv/bin/python -m ruff check fund_agent tests
All checks passed

git diff --check
passed
```

## Next Gate

`P19-S2 code re-review`

Re-review should focus on the accepted cache-bypass support-check blocker and confirm no P19-S2 scope regression occurred.
