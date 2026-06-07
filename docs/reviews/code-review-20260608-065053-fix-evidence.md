# Aggregate Deepreview Fix Evidence - Agent Engine Slice E

Date: 2026-06-08

## Gate

- Gate: aggregate deepreview fix for `mvp internalized Agent engine Slice E`.
- Review artifact: `docs/reviews/code-review-20260608-065053.md`.
- Base: `main`.
- Scope: accepted aggregate review findings only; no live provider/network probes.

## Finding Closure

### F1 scheduler interruption classification

- Changed `fund_agent/agent/runner.py` to map Host cancellation and deadline interruption to precise Agent stop reasons: `scheduler_cancelled` and `scheduler_deadline_exceeded`.
- Changed `fund_agent/services/chapter_orchestrator.py` and `fund_agent/services/agent_bridge.py` so Service result stop reason and failure category preserve scheduler interruption instead of projecting it as `llm_exception`.
- Added/updated tests in `tests/agent/test_runner.py` and `tests/agent/test_service_bridge.py`.

### F2 report-quality nested primary IDs

- Changed `fund_agent/fund/report_quality_validation.py` so `scoring_ready` validation requires nested primary IDs:
  - `source_documents[].document_id`
  - `facts[].fact_id`
  - `evidence_anchors[].anchor_id`
  - `data_gaps[].gap_id`
  - `derived_calculations[].calculation_id`
- Added `tests/fund/test_report_quality_validation.py::test_scoring_ready_requires_nested_primary_ids`.

### F3 Host safe diagnostics sensitive values

- Changed `fund_agent/host/runtime.py` so safe diagnostics reject sensitive string values, not only sensitive keys.
- Added tests in `tests/host/test_runtime_state.py` and `tests/host/test_runtime_runner.py` to prove sensitive values fail before event sink exposure.

### F4 generated chapter IDs

- Changed `fund_agent/services/agent_bridge.py` so scheduler-only blocked tasks without attempts are excluded from `generated_chapter_ids`.
- Preserved provider-exception chapters as generated when they entered the writer/provider path by checking `exception_attempt_index`.
- Covered by existing Service chapter orchestration tests and updated Agent bridge cancellation test.

### F5 phase event timing

- Changed `fund_agent/agent/runner.py` to accept a Host-free phase recorder callback.
- Changed `fund_agent/services/agent_bridge.py` to translate Agent phase callbacks to Host phase events during writer/auditor/repair execution, removing post-run trace replay.
- Added `tests/agent/test_service_bridge.py::test_service_bridge_records_writer_phase_before_writer_returns` to prove writer `phase_started` reaches the Host event sink before writer returns.

### F6 pytest duplicate module basename

- Added package markers:
  - `tests/agent/__init__.py`
  - `tests/fund/template/__init__.py`
- Full pytest collection now succeeds.

### F7 startup packet Gate 5B contradiction

- Updated `docs/current-startup-packet.md` to state the accepted current fact precisely:
  - Slice E first no-live body-chapter mechanics are accepted.
  - Fuller production Agent tool-loop/retry/budget/ToolRegistry/live runtime expansion remains future work.

### F8 branch-wide diff-check hygiene

- Mechanically removed trailing whitespace and extra EOF blank lines from historical review artifacts reported by the aggregate branch diff-check.
- Before the accepted fix commit, `main...HEAD` still reflects the previous committed branch head and cannot include these working-tree whitespace fixes; the pre-commit closure check is `git diff --check main`.
- After the accepted fix commit, the controller must rerun `git diff --check main...HEAD` before declaring the accepted deepreview checkpoint closed.
- This was a whitespace-only artifact hygiene fix.

## Validation

- `uv run pytest tests/agent tests/services/test_chapter_orchestrator.py tests/host tests/fund/test_report_quality_validation.py`
  - Result: 171 passed.
- `uv run ruff check fund_agent/agent fund_agent/services fund_agent/host fund_agent/fund/report_quality_validation.py tests/agent tests/services tests/host tests/fund/test_report_quality_validation.py`
  - Result: passed.
- `uv run pytest`
  - Result: 1422 passed.
- `uv run ruff check`
  - Result: passed.
- `git diff --check main`
  - Result: passed.
- Pending accepted deepreview commit post-check: `git diff --check main...HEAD`.

## Residual Risk

- No accepted aggregate deepreview finding remains open in this fix evidence.
- No live provider evidence was collected in this gate by design; live `--use-llm` runtime remains outside this no-live aggregate fix scope.
