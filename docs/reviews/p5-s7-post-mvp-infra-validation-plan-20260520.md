# P5-S7 Post-MVP Infra Validation Plan - 2026-05-20

## Verdict

P5-S7 enters plan review.

This slice closes the post-MVP infrastructure validation backlog around:

- RR-4: thermometer Service/CLI integration.
- RR-8: true PDF/network smoke automation.

The target is not to make live external data part of deterministic tests. The target is to expose explicit, auditable operational entry points while keeping normal `pytest` and report generation stable.

Next gate: `P5-S7 plan review`.

## Inputs

- Design truth: `docs/design.md`
- Global control doc: `docs/implementation-control.md`
- P4/P5 control doc: `docs/implementation-control-p4.md`
- Post-P4 planning: `docs/reviews/post-p4-follow-up-planning-20260520.md`
- Current code:
  - `fund_agent/fund/data/thermometer.py`
  - `fund_agent/services/fund_analysis_service.py`
  - `fund_agent/ui/cli.py`
  - `scripts/selected_funds_smoke.py`
  - `tests/fund/data/test_thermometer.py`
  - `tests/scripts/test_selected_funds_smoke.py`

## Current Facts

### Thermometer

- `FundThermometerAdapter` already exists in Capability data layer.
- It fetches public pages, parses market/index/macro thermometer data, writes `cache/thermometer/thermometer.json`, reuses 24h fresh cache, falls back to 7-day stale cache, and returns `unavailable=True` when no data is available.
- The adapter intentionally does not write thermometer values into report conclusions.
- `FundAnalysisRequest.valuation_state` is still explicit `low/fair/high/unavailable`.
- `fund-analysis analyze` exposes `--valuation-state`, but there is no thermometer CLI or Service entry point.

### Real PDF/network smoke

- `scripts/selected_funds_smoke.py` already validates `docs/code_20260519.csv`, samples funds, and builds `fund-analysis analyze` commands.
- The script defaults to dry-run and only touches true PDF/network path when `--run` is explicitly passed.
- Smoke output is written under `reports/smoke`.
- Current normal tests cover script planning, not live network/PDF execution.
- `docs/code_20260519.csv` still contains duplicate `016492`; P5-S6 records this as human-owned and not auto-fixed.

## First-Principles Boundary

External live data has two very different roles:

1. It can be queried and recorded as evidence-like operational context.
2. It must not silently mutate deterministic analysis behavior unless the mapping contract is explicit and tested.

For P5-S7, thermometer data should become visible through a Service/CLI boundary, but it should not automatically convert into checklist `valuation_state`. The project has no same-source rule that maps a market temperature number to `low/fair/high`, and doing so inside `analyze` would be an implicit investment-judgment rule.

True PDF/network smoke should remain opt-in. Network availability, upstream page layout, PDF download latency, and source-site throttling are not deterministic correctness signals for ordinary unit/integration tests.

## Target Contract

### 1. Thermometer Service/CLI entry point

Add a thin Service layer wrapper around `FundThermometerAdapter`.

Proposed public objects:

- `ThermometerRequest`
  - `cache_dir: Path | None`
  - `force_refresh: bool`
- `ThermometerService.run(request: ThermometerRequest) -> ThermometerSnapshot`

`ThermometerService` must accept an injectable adapter or factory Protocol in `__init__`.
Production defaults may construct `FundThermometerAdapter(cache_dir)`, but tests must inject a fake adapter/factory so Service and CLI tests never hit live network.

Service responsibilities:

- Coordinate Capability adapter invocation.
- Validate explicit request fields.
- Not parse thermometer HTML itself.
- Not decide `valuation_state`.
- Not read or write report artifacts.

CLI command:

```bash
fund-analysis thermometer
fund-analysis thermometer --force-refresh
fund-analysis thermometer --cache-dir cache/thermometer
fund-analysis thermometer --json
```

CLI output should be concise and machine-readable enough for smoke use:

- source
- cached
- stale
- unavailable
- unavailable_reason
- as_of_date/as_of_text
- market temperature and valuation band if present
- index count and macro fields if present

Plain text remains the default. `--json` is required for automation and must cover both available and unavailable snapshots in tests.

CLI exit behavior:

- If Service returns `ThermometerSnapshot(unavailable=True)`, exit 0 and print unavailable fields.
- If Service raises validation or unexpected runtime error, exit non-zero.

### 2. No automatic `analyze` valuation injection

Do not add `--valuation-state auto` in this slice.

Reasons:

- Mapping thermometer value to `low/fair/high` is a domain rule and must be defined in Capability/checklist design before Service can use it.
- Current checklist contract requires caller-provided explicit valuation state.
- Silent automatic valuation would make report behavior depend on live data and cache freshness.

P5-S7 may document a manual workflow:

1. Run `fund-analysis thermometer`.
2. Human/operator decides explicit `--valuation-state`.
3. Run `fund-analysis analyze ... --valuation-state <low|fair|high|unavailable>`.

### 3. Real PDF/network smoke automation remains explicit opt-in

Keep `scripts/selected_funds_smoke.py` as the operational smoke entry point.

Required hardening:

- README/tests docs must state dry-run vs `--run` behavior.
- The script must keep printing planned commands before execution.
- The script must keep recording stdout/stderr and `results.jsonl`.
- The default command should not use `--force-refresh`; force refresh must stay explicit.
- Duplicate `016492` should be visible in dry-run summary but not auto-fixed.
- Smoke commands must pass `--quality-gate-policy warn` explicitly. This keeps production `analyze` default unchanged while making the operational smoke observe the PDF/network/report-rendering path even when quality gate issues are present.

## Implementation Slices

### Slice A: Thermometer Service and CLI

Files:

- `fund_agent/services/thermometer_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_thermometer_service.py`
- `tests/ui/test_cli.py`

Acceptance:

- Service with fake fetcher/cache can return an available snapshot.
- Service tests use an injected fake adapter/factory and never hit live network.
- Service validates cache path shape if needed.
- CLI command calls `ThermometerService.run(...)`.
- CLI unavailable path exits successfully and prints `unavailable: true` unless the Service raises an unexpected exception.
- CLI `--json` prints parseable JSON for available and unavailable snapshots.
- No changes to `FundAnalysisRequest.valuation_state`.
- No changes to `run_checklist(...)` valuation semantics.

### Slice B: Smoke workflow documentation/reconciliation

Files:

- `README.md`
- `tests/README.md`
- `scripts/selected_funds_smoke.py`
- `tests/scripts/test_selected_funds_smoke.py`
- optional review artifact documenting whether a live smoke was run.

Acceptance:

- Docs distinguish deterministic tests from true network/PDF smoke.
- Docs provide dry-run and live-run commands.
- P5-S7 control docs record that live smoke is opt-in operational validation, not normal CI.
- Smoke command builder includes explicit `--quality-gate-policy warn`.

### Slice C: Optional live smoke run

Command, only if explicitly authorized or already intended by user:

```bash
.venv/bin/python scripts/selected_funds_smoke.py \
  --code 004393 \
  --run \
  --output-dir reports/smoke/p5-s7-004393
```

Acceptance:

- `reports/smoke/p5-s7-004393/results.jsonl` records command status.
- stdout/stderr files are preserved.
- If upstream network/PDF fails, record it as environment/upstream failure, not as deterministic code failure unless same-source stderr points to project code.

## Non-Goals

- Do not map thermometer temperature to checklist `valuation_state`.
- Do not make live network/PDF smoke part of ordinary `pytest`.
- Do not fix `docs/code_20260519.csv` duplicate `016492` without user/App source confirmation.
- Do not rebuild thermometer algorithm.
- Do not add LLM audit or evidence-confirm integration.
- Do not make Service read thermometer cache files directly.

## Review Questions

1. Is a read-only thermometer Service/CLI enough to close RR-4 for P5-S7?
2. Should the CLI return success for unavailable thermometer data? Controller plan review answer: yes, unavailable is a data state, not a wrapper failure.
3. Should smoke command default include `--quality-gate-policy warn` to avoid report blocking masking PDF/network failures? Controller plan review answer: yes, explicitly for smoke only.
4. Does P5-S7 require a live smoke run now, or is an opt-in operational command plus docs enough for this gate?

## Validation Plan

- `pytest tests/fund/data/test_thermometer.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/scripts/test_selected_funds_smoke.py -q`
- `pytest tests/ -q`
- `ruff check .`
- `git diff --check`

Live smoke, if authorized:

- `.venv/bin/python scripts/selected_funds_smoke.py --code 004393 --run --output-dir reports/smoke/p5-s7-004393`

## Gate Decision

Current gate advances from `P5-S7 post-MVP infra validation plan/review` to `P5-S7 plan review`.

Next gate: `P5-S7 plan review`.
