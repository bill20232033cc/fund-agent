# P19-S2 Code Re-review Controller Judgment（2026-05-23）

## Verdict

`PASS_ACCEPTED`

Two independent re-reviews passed:

- `docs/reviews/p19-s2-code-rereview-mimo-20260523.md`: `PASS`
- `docs/reviews/p19-s2-code-rereview-glm-20260523.md`: `PASS`

The prior accepted blocker is closed. Well-formed unsupported index codes are rejected as item-level unavailable before any fresh or stale cache lookup, so a local cache file cannot turn an unsupported code into an available thermometer reading.

## Judgment

| Topic | Judgment | Reason |
|---|---|---|
| Unsupported index cache bypass | Accepted as fixed | `ThermometerService` now checks Capability/data support coverage before constructing or reading `ThermometerHistoryCache`. This directly serves the P19-S2 contract that unsupported well-formed codes remain unavailable with CLI exit 0. |
| Service/Capability boundary | Accepted | Support truth is exposed from `fund_agent/fund/data/thermometer_source.py`, while UI only parses the CLI option and delegates semantic validation to Service/Capability. |
| P19-S2 scope | Accepted | Re-reviews found no automatic `fund-analysis analyze` integration, no all-A implementation, no public-page no-index adapter change, and no Dayu/parquet/extra_payload expansion. |
| Test coverage | Accepted for P19-S2 | Regression tests cover service and CLI cache-bypass behavior for batch requests; static path review confirms the same pre-cache guard covers single and stale-cache paths. |

## Accepted Commit

- `0a0045c` — `fix: enforce thermometer supported index before cache`

## Validation

Controller validation before re-review:

```text
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
81 passed

.venv/bin/python -m ruff check fund_agent tests
All checks passed

git diff --check
passed
```

Independent re-review validation:

- MiMo: `60 passed` on targeted source/service/CLI tests.
- GLM: `81 passed`; targeted ruff checks passed.

## Residual Risks

- Live akshare availability and upstream schema stability remain external-data risks; current deterministic tests use fixtures and fail-closed schema checks.
- Full all-A market thermometer remains deferred to P19-S5 / all-A PE source gate because all-A PE historical source has not been verified.
- Automatic thermometer-to-`valuation_state` integration remains out of P19-S1/S2 and must enter P19-S3 as a separate plan/review gate with user explicit input priority, unavailable semantics, and audit evidence.

## Next Gate

`P19-S3 thermometer-to-valuation_state integration plan/review`
