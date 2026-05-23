# P19-S6 Production Validation and Comparison Plan（2026-05-23）

## 1. Gate / Role

- **Gate**: `P19-S6 production validation and comparison plan-review`
- **Branch**: `phase/p19-s6-production-validation`
- **Base**: `main` at `bbec908`
- **Design truth**: `docs/design.md` §11 and §12
- **Control truth**: `docs/implementation-control.md`
- **Selection input**: `docs/reviews/post-p19-next-phase-selection-20260523.md`
- **Planning handoff**: `docs/reviews/p19-s6-production-validation-planning-handoff-20260523.md`

This plan is code-generation-ready for implementation after review acceptance. It does not implement code.

## 2. Objective

Close the remaining P19 validation gap by proving the already-merged thermometer behavior is stable in realistic workflows without expanding scope.

P19-S6 validates:

- 3 sample fund CLI end-to-end reports still pass after automatic thermometer integration;
- exact supported benchmark identities (`000300`, `000905`) can use automatic thermometer valuation;
- unsupported, ambiguous, active, bond, QDII, FOF, and multi-index cases remain `unavailable`;
- `fund-analysis thermometer` default, single-index, and mixed-batch paths remain deterministic;
- live `akshare/Legulegu` smoke is available as an opt-in operational check, not normal CI;
- public-page thermometer remains comparison-only and never becomes production fallback.

## 3. Non-Goals

- Do not add new supported index codes.
- Do not retry P19-S4 source feasibility.
- Do not use 有知有行 public-page scraping as production source or fallback.
- Do not broaden automatic `valuation_state` mapping to active, bond, QDII, FOF, ambiguous, or multi-index benchmarks.
- Do not introduce Dayu Host/Engine/tool loop, LLM writing, Evidence Confirm, calculated tracking error, or external index adapters.
- Do not change annual-report repository access boundaries.
- Do not edit RR-13, selected-fund CSV rows, or excluded repo-audit artifacts.
- Do not put explicit parameters in `extra_payload`.

## 4. Implementation Slices

### Slice S6-1: Deterministic Analyze Validation Matrix

**Purpose**: prove `fund-analysis analyze` uses thermometer-derived valuation only when the P19-S3 exact identity contract allows it.

**Allowed files**:

- `tests/services/test_fund_analysis_service.py`
- `tests/fund/integration/test_p3_cli_e2e_matrix.py`
- optional helper-only changes in existing test modules if duplication becomes excessive

**Required tests**:

1. Add or extend Service-level tests using fake thermometer service/provider behavior:
   - `index_fund` with exact `benchmark_index_code="000300"` resolves to thermometer-derived `valuation_state`.
   - `enhanced_index` with exact `benchmark_index_code="000905"` resolves to thermometer-derived `valuation_state`.
   - unsupported exact code such as `399006` remains unavailable and does not call a supported-source path.
   - ambiguous or style-index benchmark text (`沪深300价值`, `中证500质量成长`) remains unavailable.
   - explicit request `valuation_state` still overrides automatic thermometer resolution.

2. Extend the existing 3 sample CLI e2e test or add a sibling P19-S6 test:
   - keep the existing explicit `--valuation-state fair` sample path unchanged as regression coverage;
   - add at least one auto-valuation CLI sample for exact `000300` or `000905` using a deterministic fake thermometer injected through `FundAnalysisService(..., thermometer_service=...)`;
   - the auto-valuation CLI sample must omit `--valuation-state`, record the fake `ThermometerRequest.index_code`, and assert the fake was called with the exact supported benchmark code;
   - add a negative CLI or Service assertion proving unsupported / ambiguous benchmark cases do not call the fake thermometer;
   - assert report contains thermometer disclaimer and external thermometer evidence when auto valuation is used;
   - assert all 8 chapters and programmatic audit still pass.

**Acceptance criteria**:

- Automatic mapping is positive only for exact supported benchmark identity.
- Unsupported or ambiguous identities remain `ValuationState.UNAVAILABLE`.
- Explicit CLI `--valuation-state` remains highest priority.
- No live network access is required.

### Slice S6-2: Deterministic Thermometer CLI Validation Matrix

**Purpose**: preserve user-visible thermometer CLI behavior after P19-S5.

**Allowed files**:

- `tests/ui/test_cli.py`
- `tests/services/test_thermometer_service.py`
- `tests/fund/data/test_thermometer_source.py`
- `tests/fund/data/test_thermometer_cache.py`

**Required tests**:

1. Keep or add tests for:
   - `fund-analysis thermometer --json` defaulting to `wind_all_a`;
   - `--index wind_all_a --json`;
   - `--index 000300 --json`;
   - `--index 000905 --json`;
   - `--index wind_all_a,000300,000905 --json`;
   - batch with unsupported-but-well-formed code returning partial unavailable;
   - malformed batch input exiting with validation error.

2. Assert JSON shape for batch output:
   - `requested_index_codes` order is preserved after de-duplication;
   - `result_count` matches readings;
   - `partial_unavailable` and `unavailable_count` are coherent;
   - each reading has `index_code`, `temperature`, `valuation_state_candidate`, `data_date`, and disclaimer when available.

**Acceptance criteria**:

- CLI tests are deterministic and fake external sources.
- No public-page adapter is used for the default thermometer command.
- Batch behavior remains exit-code 0 for partial unavailable but not for malformed input.

### Slice S6-3: Native Dependency Regression Guard

**Purpose**: prevent reintroducing concurrent `akshare/Legulegu/libmini_racer` entry paths.

**Allowed files**:

- `tests/fund/data/test_thermometer_source.py`
- optional `docs/reviews/p19-s6-production-validation-implementation-20260523.md`

**Required checks**:

1. Preserve existing P19-S5 sequential PE/PB tests.
2. Add a small regression test only if current tests do not already fail when PE/PB fetches are scheduled concurrently.
3. Document in the implementation artifact that:
   - index PE/PB fetch remains sequential;
   - all-A PE/PB fetch remains sequential;
   - batch Service iteration remains serial unless a future design explicitly makes source calls concurrency-safe.

**Acceptance criteria**:

- No new concurrency path is introduced.
- Existing sequential tests still pass.

### Slice S6-4: Public-Page Comparison Boundary

**Purpose**: decide whether directional comparison can be validated without adding production fallback or new public CLI/API.

**Allowed files**:

- `tests/fund/data/test_thermometer.py`
- optional new test helper inside existing test files
- `docs/reviews/p19-s6-production-validation-implementation-20260523.md`

**Required decision**:

Use the existing `FundThermometerAdapter` and parser tests as comparison-only coverage. Do not add a new CLI flag in P19-S6 unless a reviewer proves there is no internal test path to validate comparison boundaries.

**Required tests or documentation**:

- If current public-page parser/adapter tests already prove comparison-only availability, document that evidence and do not add duplicate tests.
- If a minimal test is added, it must use fixture HTML and assert only bucket/direction concepts, not exact parity.
- No test may route production `ThermometerService` fallback to public-page data.

**Acceptance criteria**:

- Public-page code remains internal/transitional.
- P19-S6 does not create a new production dependency on page scraping.
- Directional comparison remains non-blocking if page structure is unavailable.

### Slice S6-5: Optional Live Smoke Script / Docs

**Purpose**: make the user's manual smoke repeatable without making network availability a CI blocker.

**Allowed files**:

- `tests/README.md`
- root `README.md` only if adding user-facing optional smoke commands is necessary
- optional `docs/reviews/p19-s6-production-validation-live-smoke-20260523.md`

**Required live commands**:

```bash
fund-analysis thermometer --json
fund-analysis thermometer --index 000300 --json
fund-analysis thermometer --index wind_all_a,000300,000905 --json
fund-analysis thermometer --index wind_all_a,000300,000905 --force-refresh --json
```

**Rules**:

- These are opt-in operational checks.
- Do not run them in default CI.
- If run locally, record whether failures are source/network/native availability or deterministic contract failures.
- A live failure should not block implementation acceptance unless it reveals a Python-level contract regression that deterministic tests can reproduce.

### Slice S6-6: Documentation and Control Closeout

**Allowed files**:

- `docs/implementation-control.md`
- `tests/README.md`
- `fund_agent/fund/README.md` only if Fund capability behavior wording changes
- root `README.md` only if user command documentation changes
- `docs/reviews/p19-s6-production-validation-implementation-20260523.md`
- code review artifacts under `docs/reviews/`

**Required closeout updates**:

- Record exact tests added.
- Record targeted validation commands and results.
- Mark P19 exit criteria for 3 sample CLI e2e and comparison validation only when evidence exists.
- Keep P19-S4 unresolved source coverage deferred.
- Keep production `tracking_error` golden rows outside scope.

## 5. Review Requirements

Plan review must reject implementation if it:

- adds new supported index coverage;
- relies on live network smoke as normal CI;
- uses public-page data as fallback or production truth;
- weakens exact benchmark identity fail-closed behavior;
- broadens automatic valuation mapping beyond P19-S3 accepted types;
- introduces source access outside Service/Capability boundaries;
- creates external issue/PR comments or branch deletion without explicit user authorization.

## 6. Validation Commands

Minimum targeted validation after implementation:

```bash
pytest tests/fund/analysis/test_valuation_state.py tests/services/test_fund_analysis_service.py -q
pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q
pytest tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/fund/data/test_thermometer.py -q
ruff check fund_agent tests
git diff --check
```

Full validation before implementation acceptance:

```bash
pytest -q
```

Optional live smoke after deterministic validation:

```bash
fund-analysis thermometer --json
fund-analysis thermometer --index 000300 --json
fund-analysis thermometer --index wind_all_a,000300,000905 --json
fund-analysis thermometer --index wind_all_a,000300,000905 --force-refresh --json
```

## 7. Stop Conditions

Stop and return to controller if:

- a required analyze case cannot be modeled with deterministic fixtures;
- implementation needs new data sources;
- implementation needs a new public CLI flag;
- public-page comparison cannot be done without production fallback;
- live smoke exposes a native crash or non-recoverable process abort;
- source/test/doc changes exceed the allowed files above;
- any reviewer asks to mix P19-S6 with P19-S4 source expansion or E1-E3/Evidence Confirm.

## 8. Recommended Implementation Handoff

```text
Gate: P19-S6 implementation.

Use `docs/reviews/p19-s6-production-validation-plan-20260523.md` as the accepted plan.

Implement deterministic validation only:
- analyze exact supported / unsupported / explicit override matrix;
- CLI thermometer default, single, batch, partial unavailable, malformed input matrix;
- native dependency regression guard only if existing P19-S5 tests do not already cover it;
- public-page comparison only as fixture/internal comparison, never fallback;
- optional live-smoke documentation, not CI.

Do not add new supported indexes, public-page production fallback, new source adapters, Dayu runtime, LLM audit, Evidence Confirm, calculated tracking error, or external GitHub actions.
```
