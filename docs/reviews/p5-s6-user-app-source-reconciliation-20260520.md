# P5-S6 User/App Source Reconciliation - 2026-05-20

## Verdict

BLOCKED ON HUMAN SOURCE CONFIRMATION.

P5-S6 is intentionally a human gate from the post-P4 backlog: verify whether the duplicate `016492` in `docs/code_20260519.csv` reflects the App source data or a local CSV transcription error.

## Current Facts

`docs/code_20260519.csv` contains two rows with code `016492`:

| CSV line | fund_name | fund_code | app_category |
|---:|---|---|---|
| 26 | 南方均衡成长混合A | 016492 | 国内股票类 |
| 35 | 易方达逆向投资混合A | 016492 | 国内股票类 |

Current code behavior:

- `validate_selected_fund_pool(...)` reports duplicate codes.
- `run_extraction_snapshot(...)` does not block duplicates; `summary.md` highlights duplicate codes.
- P4/P5 scoring and gate work can continue without silently rewriting the source CSV.

## Root Cause Status

Not determined.

The duplicate cannot be safely fixed from local code facts alone. The same fund code cannot identify two different fund names as a stable fund-pool truth, but choosing which row to edit or remove requires checking the App/source list.

## Required Human Decision

Please confirm one of:

1. `016492` belongs to `南方均衡成长混合A`; the `易方达逆向投资混合A` row should be corrected or removed.
2. `016492` belongs to `易方达逆向投资混合A`; the `南方均衡成长混合A` row should be corrected or removed.
3. Both fund names should remain, but one fund code is wrong; provide the corrected code.
4. Keep both rows exactly as-is because the duplicate reflects the current App source, accepting duplicate-code warnings in snapshot summaries.

## Controller Recommendation

Do not modify `docs/code_20260519.csv` until the source is confirmed. Continue to P5-S7 / aggregate readiness if the user accepts keeping RR-13 open as human-owned.

## Gate Decision

Current gate remains `P5-S6 user/App source reconciliation`.

Next automated gate after user decision or explicit deferral: `P5-S7 post-MVP infra validation plan/review`.
