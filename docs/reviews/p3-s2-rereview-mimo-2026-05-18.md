# P3-S2 Re-Review — MiMo

> **Reviewer**: MiMo
> **Date**: 2026-05-18
> **Gate**: P3-S2 re-review
> **Scope**: Verify accepted fix for GLM F3 / MiMo INFO F3 only
> **Fix artifact**: `docs/reviews/p3-s2-fix-2026-05-18.md`

---

## Verified Changes

### 1. Degree preference ordering

`_parse_market_temperature` at `thermometer.py:338` now calls `_degree_after_heading` before `_decimal_after_labels`. This ensures degree-marked values (e.g., `70℃`) are preferred over nearby non-temperature numbers (e.g., `统计样本 1234 只基金`). **Correct.**

### 2. Celsius sign support

`_degree_after_heading` at `thermometer.py:618` regex changed from `°` only to `(?:°|℃)`, accepting both U+00B0 and U+2103. **Correct.**

### 3. New test

`test_parse_thermometer_pages_prefers_degree_market_value_over_nearby_number` at `test_thermometer.py:387–412` constructs HTML with a distractor number (`1234`) before the degree-marked value (`70℃`) and asserts the parser returns `70`. **Correct and sufficient.**

---

## Verdict

**PASS**

The fix correctly addresses GLM F3 and MiMo INFO F3. No remaining blockers for the scoped finding.
