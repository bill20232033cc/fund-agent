# P19-S1 Code Re-review Controller Judgment（2026-05-23）

## Verdict

`BLOCKED_FIXED_PENDING_REREVIEW`

Two independent re-reviews both returned `BLOCKED` on the same accepted finding:

- `docs/reviews/p19-s1-code-rereview-mimo-20260523.md`
- `docs/reviews/p19-s1-code-rereview-glm-20260523.md`

The blocker is accepted. The previous fix still validated only the first 10 characters of string dates, so timestamp-like or suffixed strings could pass as strict ISO dates. Based on `docs/design.md` v2.2 and P19-S1 failure semantics, external source schema drift must fail closed instead of being silently normalized.

## Blocking Finding Judgment

| Finding | Source | Judgment | Handling |
|---|---|---|---|
| String date normalization still accepts suffixed non-strict ISO values after `text[:10]` | MiMo / GLM | Accepted | `_normalize_date()` now validates the full string with `ISO_DATE_PATTERN.fullmatch(text)` and `datetime.strptime(text, "%Y-%m-%d")`; no truncation remains. |

## Fix Summary

Files changed after re-review:

- `fund_agent/fund/data/thermometer_source.py`
- `tests/fund/data/test_thermometer_source.py`

The added regression tests reject:

- `2026-05-22T00:00:00`
- `2026-05-22 00:00:00`
- `2026-05-22abc`

The existing `date` object normalization path remains accepted and tested.

## Validation

```text
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
57 passed

.venv/bin/python -m ruff check fund_agent tests
All checks passed

git diff --check
passed
```

## Next Gate

`P19-S1 code re-review round 2`

The next re-review should focus on the accepted blocking finding and verify that strict string date handling is now complete, while confirming the prior accepted findings remain fixed.
