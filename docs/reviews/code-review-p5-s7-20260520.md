# Controller Code Review - P5-S7 Post-MVP Infra Validation - 2026-05-20

## Verdict

PASS.

No blocking finding found.

## Scope Reviewed

- `fund_agent/services/thermometer_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `scripts/selected_funds_smoke.py`
- `tests/services/test_thermometer_service.py`
- `tests/ui/test_cli.py`
- `tests/scripts/test_selected_funds_smoke.py`
- `README.md`
- `tests/README.md`
- `docs/reviews/p5-s7-post-mvp-infra-validation-plan-20260520.md`

## Review Checks

### 1. Layer boundaries

PASS.

- Thermometer parsing and cache behavior remain in Capability data layer.
- Service only coordinates `FundThermometerAdapter` through an injectable factory.
- CLI calls `ThermometerService` and formats returned data.
- CLI no longer imports Capability thermometer types directly.
- No `analyze` valuation-state injection was added.

### 2. Deterministic tests avoid live network

PASS.

- Service tests inject a fake adapter factory.
- CLI tests inject fake Services.
- Existing adapter tests still use fake fetchers or local HTML.
- Smoke script tests only inspect command construction and CSV facts.

### 3. Unavailable thermometer semantics

PASS.

`FundThermometerAdapter` already models upstream unavailable as data. CLI mirrors that by exiting 0 when a snapshot has `unavailable=True`; unexpected Service exceptions exit 1.

### 4. Smoke command semantics

PASS.

`scripts/selected_funds_smoke.py` now explicitly adds `--quality-gate-policy warn`. This is appropriate for operational smoke because the target signal is whether the true PDF/network/report path is observable. Production `fund-analysis analyze` still defaults to block.

### 5. Documentation sync

PASS.

README and tests README describe the current behavior:

- `fund-analysis thermometer` exists.
- thermometer does not auto-map to `--valuation-state`.
- real PDF/network smoke remains opt-in with `--run`.
- smoke uses quality gate warn policy.

## Verification

- `.venv/bin/python -m pytest tests/fund/data/test_thermometer.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/scripts/test_selected_funds_smoke.py -q` -> `32 passed`
- `.venv/bin/python -m pytest tests/ -q` -> `200 passed`
- `.venv/bin/python -m ruff check .` -> passed
- `git diff --check` -> passed

## Residual Risk

Live smoke was not run as a required acceptance gate. That is acceptable for P5-S7 because the accepted plan keeps live network/PDF as explicit operational validation, not deterministic CI.

## Gate Decision

P5-S7 code review is accepted.

Next gate: `P5 aggregate readiness reconciliation`.
