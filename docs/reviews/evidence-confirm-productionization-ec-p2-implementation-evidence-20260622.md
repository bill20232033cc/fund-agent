# EC-P2 Implementation Evidence - repository-bounded runner

Date: 2026-06-22

## Scope Implemented

- Added `run_repository_bounded_evidence_confirm()` in `fund_agent/fund/evidence_confirm_sources.py`.
- Added explicit request/result/provenance/issue dataclasses for EC-P2 repository-bounded Evidence Confirm.
- Runner boundary:
  - accepts injected repository or creates default `FundDocumentRepository` lazily inside runner;
  - requires async `load_annual_report`;
  - calls `load_annual_report(fund_code, report_year, force_refresh=...)`;
  - can build live smoke projection through a post-load `projection_factory` inside the runner boundary;
  - does not call PDF/cache/source helper, Service, Host, renderer, quality gate, provider or LLM;
  - reuses the existing annual-report reference materializer and V2 Evidence Confirm.
- Added fail-closed source failure classification:
  - `not_found`
  - `unavailable`
  - `schema_drift`
  - `identity_mismatch`
  - `integrity_error`
  - `ambiguous_repository_failure`
- Added `scripts/evidence_confirm_ec_p2_live_sample.py` for the authorized `004393/2025` sample command surface.
  - The script is hard-limited to `004393/2025`.
  - It builds only `projection_kind="ec_p2_live_section_smoke"`.
  - It outputs safe scalar JSON only.
  - It sets `field_correctness_proven=false`.

## Tests Added / Updated

- `tests/fund/test_evidence_confirm_sources.py`
  - positive fake repository runner path and exact `load_annual_report` call args;
  - poison fake repository methods proving no PDF/parser helper is touched;
  - invalid repository shape fail-closed;
  - negative provenance stops before proof-positive reference/V2;
  - materializer failures propagate to runner issues;
  - V2 value mismatch fails the runner;
  - repository exception category mapping;
  - ambiguous generic repository error classification;
  - runner post-load `projection_factory`;
  - live-sample section smoke projection helper positive/negative tests;
  - live-sample repository failure safe JSON payload;
  - import isolation no longer asserts source text lacks `load_annual_report`; it asserts import does not instantiate repository or call load.

## Local Validation

All validation below is no-live and uses fake reports/repositories.

```text
uv run pytest tests/fund/test_evidence_confirm_sources.py -q
37 passed in 0.87s
```

```text
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
84 passed in 0.86s
```

```text
uv run ruff check fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py
All checks passed!
```

```text
git diff --check -- fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py fund_agent/fund/README.md tests/README.md
PASS
```

## Not Executed

- Did not execute the authorized live/PDF command yet:
  - `uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh`

Reason: EC-P2 still needs code review / re-review acceptance before live execution.

## Non-Goals Preserved

- No Service/UI/Host/renderer/quality-gate integration.
- No semantic field correctness claim.
- No source-truth family productionization claim.
- No golden/readiness/release claim.
- No PR external state change.

## Next Gate

EC-P2 code review of the local implementation slice.
