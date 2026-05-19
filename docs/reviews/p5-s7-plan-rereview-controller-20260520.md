# Controller Plan Re-review - P5-S7 Post-MVP Infra Validation - 2026-05-20

## Verdict

PASS.

The patched plan now gives implementation agents enough detail to proceed without redesign.

## Finding Closure

| Finding | Status | Controller judgment |
|---|---|---|
| P5-S7-PR1 injectable thermometer Service adapter/factory | closed | Plan now requires a Service injection point and fake adapter/factory tests, avoiding live network in Service/CLI tests. |
| P5-S7-PR2 explicit unavailable CLI behavior | closed | Plan now states unavailable snapshots exit 0, while validation/runtime exceptions exit non-zero. |
| P5-S7-PR3 smoke `--quality-gate-policy warn` | closed | Plan now requires smoke command builder to pass warn explicitly so PDF/network/report rendering remains observable. |
| P5-S7-PR4 thermometer JSON output | closed | Plan now requires `fund-analysis thermometer --json` and tests for available/unavailable snapshots. |

## Accepted Implementation Scope

P5-S7 implementation may proceed with:

- `ThermometerService` and `ThermometerRequest`.
- `fund-analysis thermometer` plain text and JSON output.
- Smoke command builder update to include `--quality-gate-policy warn`.
- README and tests README synchronization.

Explicitly excluded:

- No automatic mapping from thermometer values to `valuation_state`.
- No `--valuation-state auto`.
- No normal `pytest` dependency on live network/PDF.
- No auto-fix of duplicate `016492`.

## Required Verification

- `pytest tests/fund/data/test_thermometer.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/scripts/test_selected_funds_smoke.py -q`
- `pytest tests/ -q`
- `ruff check .`
- `git diff --check`

## Gate Decision

P5-S7 plan/review is accepted.

Next gate: `P5-S7 implementation`.
