# Code Review - P5-S4 Snapshot Failure Accounting - 2026-05-20

## Verdict

PASS. No blocking findings.

## Scope Reviewed

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/services/extraction_score_service.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `tests/services/test_extraction_score_service.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Findings

No blocking findings.

## Checks

- `pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py -q`
  - `36 passed`
- `pytest tests/ -q`
  - `191 passed`
- `ruff check .`
  - passed
- `git diff --check`
  - passed

## Controller Notes

- `errors_path` is explicit and only parsed by `run_extraction_score(...)`.
- `write_extraction_score_records(...)` remains file-free and accepts structured `failed_funds`.
- `score.json` now always includes `failed_funds` for new outputs and remains compatible with older score files that omit it.
- `quality_gate.py` evaluates failed funds only through `score.json.failed_funds`, so it still consumes only score payloads and does not read `errors.jsonl`.
- Service and CLI changes are thin parameter forwarding.

## Residual Risk

No residual P5-S4 blocking risk. Failed extraction accounting now exists for explicit `--errors-path` use. The plan intentionally rejected auto-discovery of sibling `errors.jsonl`; callers must pass the path when scoring a snapshot run.

## Next Gate

P5-S4 acceptance / aggregate readiness.
