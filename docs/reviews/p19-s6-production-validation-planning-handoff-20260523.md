# P19-S6 Production Validation Planning Handoff（2026-05-23）

## 1. Gate / Role

- **Current branch**: `phase/p19-s6-production-validation`
- **Base**: `main` at `bbec908`
- **Current gate**: `P19-S6 production validation and comparison plan-review`
- **Design truth**: `docs/design.md` §11 and §12
- **Control truth**: `docs/implementation-control.md`
- **Selection input**: `docs/reviews/post-p19-next-phase-selection-20260523.md`

This handoff is controller work. It defines the planning task and guardrails for a planning specialist. It does not implement code, tests, README changes, or product behavior.

## 2. Planning Task

Create:

```text
docs/reviews/p19-s6-production-validation-plan-20260523.md
```

The plan must be code-generation-ready and must define exact implementation slices, file ownership, test commands, live-smoke boundaries, stop conditions, and documentation/control update triggers for P19-S6.

## 3. Objective

Close the remaining P19 validation gap without expanding thermometer scope.

The plan should prove that the already-merged thermometer capability is stable and observable in realistic workflows:

- deterministic `fund-analysis analyze` behavior for supported and unsupported benchmark identities;
- deterministic CLI coverage for the thermometer batch/default paths;
- optional live smoke for `akshare/Legulegu` availability and native dependency risk;
- public-page comparison only as a non-production directional signal;
- no new index coverage, no production fallback to public-page scraping, and no broadened automatic valuation mapping.

## 4. Required Plan Slices

### Slice A: Deterministic Analyze Integration Matrix

The plan must identify exact tests and fixtures for:

- supported exact benchmark identity `000300`;
- supported exact benchmark identity `000905`;
- unsupported / ambiguous benchmark identity that must remain `unavailable`;
- explicit user `--valuation-state` override taking precedence over automatic thermometer output.

The plan must preserve the P19-S3 contract: active, bond, QDII, FOF, multiple-equity-index, ambiguous, and derived benchmark cases must not silently use thermometer readings.

### Slice B: Thermometer CLI Validation Matrix

The plan must cover:

- default no-index command routes to `wind_all_a`;
- single-index commands for `000300`, `000905`, and `wind_all_a`;
- mixed batch `wind_all_a,000300,000905`;
- unsupported-but-well-formed code returning unavailable in batch;
- malformed input still exits with a validation error.

The plan must distinguish deterministic tests from live smoke.

### Slice C: Optional Live Smoke Contract

The plan must define opt-in commands for live validation, at minimum:

```bash
fund-analysis thermometer --json
fund-analysis thermometer --index 000300 --json
fund-analysis thermometer --index wind_all_a,000300,000905 --json
```

Live smoke must not become a normal CI blocker unless explicitly opted in. Source/network failures should be recorded as environment or upstream availability evidence, not as deterministic correctness failures.

### Slice D: Public-Page Comparison Boundary

The plan must decide whether P19-S6 uses the existing `FundThermometerAdapter` only through tests or through a small internal comparison helper.

Hard boundaries:

- public-page data is not production truth;
- public-page data is not fallback;
- comparison is directional or bucket-level only;
- exact value parity is not a success criterion.

If no stable public-page comparison can be done without adding public CLI/API surface, the plan should explicitly defer this part and record it as non-blocking.

### Slice E: Native Dependency Regression Guard

The plan must include a review/check that no new concurrent `akshare/Legulegu/libmini_racer` entry path is introduced.

It should reference the existing sequential PE/PB tests added in P19-S5 and decide whether additional regression tests are needed.

### Slice F: Documentation / Control Sync

The plan must define when to update:

- `docs/implementation-control.md`;
- `tests/README.md`;
- root `README.md` only if user-visible commands or workflow text changes;
- `fund_agent/fund/README.md` only if Fund capability behavior or validation boundaries change.

## 5. Non-Goals

- Do not add new supported indexes.
- Do not retry P19-S4 exact-index source feasibility.
- Do not use public-page scraping as production source or fallback.
- Do not broaden automatic `valuation_state` mapping.
- Do not introduce Dayu Host/Engine/tool loop, LLM writing, Evidence Confirm, calculated tracking error, or external index adapters.
- Do not edit source CSVs, RR-13, or excluded repo-audit artifacts.
- Do not put explicit parameters in `extra_payload`.

## 6. Required Review Criteria

Plan review must reject the plan if it:

- mixes deterministic tests with live smoke in normal CI;
- expands supported index coverage without a source gate;
- weakens exact benchmark identity fail-closed behavior;
- uses public-page data as production truth or fallback;
- requires Service/UI direct access to Capability internals or concrete source adapters;
- lacks explicit validation commands;
- lacks exact allowed file scope for implementation.

## 7. Expected Validation In Plan

The plan should include targeted commands such as:

```bash
pytest tests/fund/analysis/test_valuation_state.py tests/services/test_fund_analysis_service.py -q
pytest tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py -q
ruff check fund_agent tests
git diff --check
```

The plan should also state whether full `pytest -q` is required before implementation acceptance.

## 8. Stop Conditions

Stop and return to controller if:

- the plan requires new production data sources;
- the plan requires public-page data as fallback;
- the plan requires new user-facing CLI flags;
- deterministic fixture coverage cannot represent the required analyze cases;
- implementation would need to touch unrelated modules or previous excluded artifacts.
