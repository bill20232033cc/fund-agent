# P5-S7 Implementation - Post-MVP Infra Validation - 2026-05-20

## Verdict

P5-S7 implementation is complete.

This slice adds a read-only thermometer Service/CLI entry point and hardens the selected-funds live smoke command so true PDF/network/report-rendering validation is explicit and not masked by default quality gate blocking.

Next gate: `P5-S7 code review`.

## Implemented Changes

### Thermometer Service

Added `fund_agent/services/thermometer_service.py`.

Public contract:

- `ThermometerRequest(cache_dir: Path | None = None, force_refresh: bool = False)`
- `ThermometerService.run(request) -> ThermometerSnapshot`

Boundary decisions:

- Service coordinates `FundThermometerAdapter`.
- Service accepts an injected adapter factory Protocol for deterministic tests.
- Service does not parse thermometer HTML.
- Service does not map thermometer values to `low/fair/high`.
- Service does not mutate `FundAnalysisRequest` or checklist behavior.

### CLI

Added:

```bash
fund-analysis thermometer
fund-analysis thermometer --json
fund-analysis thermometer --force-refresh --cache-dir cache/thermometer
```

CLI behavior:

- Plain text output by default.
- JSON output with `--json`.
- `unavailable=True` is treated as data state and exits 0.
- Service validation/runtime exceptions exit 1.
- CLI only depends on Service exports; it does not import Capability thermometer types directly.

### Smoke Script

Updated `scripts/selected_funds_smoke.py` command builder to pass:

```bash
--quality-gate-policy warn
```

This keeps production `fund-analysis analyze` default `block` unchanged, while letting operational smoke observe the real PDF/network/report-rendering path even when quality gate issues are present.

### Docs

Updated:

- `README.md`
- `tests/README.md`
- `docs/implementation-control.md`
- `docs/implementation-control-p4.md`

Docs now distinguish:

- thermometer query vs automatic valuation-state mapping;
- deterministic pytest vs opt-in true PDF/network smoke;
- production `block` quality gate default vs smoke `warn` policy.

## Tests Added/Updated

Added:

- `tests/services/test_thermometer_service.py`

Updated:

- `tests/ui/test_cli.py`
- `tests/scripts/test_selected_funds_smoke.py`

Coverage:

- injected fake thermometer adapter avoids live network in Service tests;
- CLI plain text output;
- CLI JSON output for unavailable snapshots;
- CLI non-zero path for Service exceptions;
- smoke command builder includes `--quality-gate-policy warn`.

## Verification

- `.venv/bin/python -m pytest tests/fund/data/test_thermometer.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/scripts/test_selected_funds_smoke.py -q` -> `32 passed`
- `.venv/bin/python -m pytest tests/ -q` -> `200 passed`
- `.venv/bin/python -m ruff check .` -> passed
- `git diff --check` -> passed
- `.venv/bin/python -m fund_agent.ui.cli thermometer --json` -> exited 0 and returned a thermometer JSON snapshot

## Residual Risks

- RR-4 is closed for read-only Service/CLI access, but thermometer values still do not automatically drive `valuation_state`. That remains intentional until a same-source mapping rule is designed in Capability/checklist.
- RR-8 is closed for opt-in operational smoke command hardening, but live PDF/network execution remains environment-sensitive and should not enter ordinary pytest.
- P5-S6 duplicate `016492` remains human-owned and unchanged.
