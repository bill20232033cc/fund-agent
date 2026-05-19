# P5-S4 Snapshot Failure Accounting Implementation - 2026-05-20

## Scope

Implemented failed-fund accounting from P4 snapshot errors into score and quality gate outputs.

The root issue was that `run_extraction_snapshot(...)` recorded complete extraction failures in `errors.jsonl`, while `run_extraction_score(...)` and `run_quality_gate(...)` only consumed `snapshot.jsonl` / `score.json`. A fully failed fund could therefore be absent from gate evaluation.

## Code Changes

- `fund_agent/fund/extraction_score.py`
  - Added `FailedFundRow`.
  - Added `load_snapshot_error_records(errors_path)`.
  - Added `ExtractionScoreResult.failed_funds`.
  - Added explicit `run_extraction_score(..., errors_path=None)`.
  - Kept `write_extraction_score_records(...)` file-free; it accepts structured `failed_funds`.
  - `score.json` now always includes `failed_funds`, defaulting to `[]`.
  - `score.md` now includes a `Failed Funds` section.

- `fund_agent/fund/quality_gate.py`
  - Evaluates `score.json.failed_funds` when present.
  - Emits `FQ6/block` per failed fund.
  - Preserves old `score.json` compatibility when `failed_funds` is absent.

- `fund_agent/services/extraction_score_service.py`
  - Added explicit `ExtractionScoreRequest.errors_path`.
  - Validates `.jsonl` suffix and forwards to Capability.

- `fund_agent/ui/cli.py`
  - Added `fund-analysis extraction-score --errors-path`.

- Docs/tests
  - Updated `README.md`, `fund_agent/fund/README.md`, and `tests/README.md`.
  - Added tests for `failed_funds`, malformed errors rows, FQ6, Service forwarding, and CLI forwarding.

## Verification

- `pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py -q`
  - `36 passed`
- `pytest tests/ -q`
  - `191 passed`
- `ruff check .`
  - passed
- `git diff --check`
  - passed

## Controller Judgment

P5-S4 implementation satisfies the accepted plan:

- failure facts originate from `errors.jsonl` / `SnapshotErrorRecord`;
- score entry uses an explicit `errors_path` parameter;
- lower-level score writer remains file-free;
- quality gate consumes only `score.json`;
- Service and UI only forward explicit parameters.

Next gate: `P5-S4 code review`.
