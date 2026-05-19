# P5-S1 Quality Gate Integration Implementation - 2026-05-20

## Summary

P5-S1 implementation is completed and ready for code review.

This slice connects the P4 quality gate to `fund-analysis analyze` without re-extracting annual report data and without moving fund-domain quality rules into UI or Service.

## Implemented

- Added Capability adapter `fund_agent/fund/quality_gate_integration.py`.
  - Reuses `build_snapshot_records(...)` on the already extracted `StructuredFundDataBundle`.
  - Writes single-fund `snapshot.jsonl`, `score.json`, `score.md`, `golden_set.json`, `quality_gate.json`, and `quality_gate.md`.
  - Returns `not_run_reason` when the fund is absent from the selected-fund CSV or the CSV is unavailable.
- Extended `FundAnalysisRequest` with explicit quality gate inputs:
  - `quality_gate_policy`
  - `quality_gate_source_csv`
  - `quality_gate_output_dir`
  - `quality_gate_run_id`
  - `quality_gate_golden_answer_path`
- Extended `FundAnalysisResult` with:
  - `quality_gate_result`
  - `quality_gate_not_run_reason`
- Added structured `QualityGateBlockedError`.
  - Carries `QualityGateResult`.
  - Used only when policy is `block` and gate status is `block`.
- Extended `fund-analysis analyze` CLI.
  - Adds explicit quality gate options.
  - Prints gate summaries to stderr.
  - On structured block, exits non-zero and prints gate artifact paths without printing a full report.
- Updated documentation:
  - `README.md`
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Boundary Judgment

- Capability owns snapshot/score/gate rules and bundle-to-gate conversion.
- Service orchestrates quality precheck and report generation.
- CLI only maps explicit parameters and renders stdout/stderr.
- The implementation does not place fund-domain rules in UI or programmatic audit.
- The implementation does not call `FundDataExtractor.extract(...)` a second time during `analyze`.

## Tests Added / Updated

- `tests/fund/test_quality_gate_integration.py`
  - adapter writes score/gate outputs from an existing bundle
  - fund absent from selected CSV returns not-run reason and does not write run artifacts
- `tests/services/test_fund_analysis_service.py`
  - `off`, `warn`, `block`, and not-run paths
  - structured `QualityGateBlockedError`
  - default run id avoids overwriting automatic output directories
  - extractor called once
- `tests/ui/test_cli.py`
  - new explicit analyze parameters
  - gate summary output
  - structured block output

## Validation

- `.venv/bin/python -m pytest tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q`: `19 passed`
- `.venv/bin/ruff check .`: passed
- `.venv/bin/python -m pytest tests/ -q`: `179 passed`
- `git diff --check`: passed

## Known Scope Exclusions

- P5-S2 FQ4/FQ5 and App category conflict rules remain deferred.
- P5-S3 wider correctness denominator remains deferred.
- `reports/quality-gate-runs/` is runtime output and should not be included in PR scope.

## Gate Decision

Current gate: `P5-S1 implementation completed`

Next gate: `P5-S1 code review`
