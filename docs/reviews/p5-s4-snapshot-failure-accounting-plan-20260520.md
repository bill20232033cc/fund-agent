# P5-S4 Snapshot Failure Accounting Plan - 2026-05-20

## Verdict

P5-S4 enters plan review.

This slice addresses the P5 backlog item “snapshot failure accounting”: a fund that fails extraction in `run_extraction_snapshot(...)` is currently recorded in `errors.jsonl`, but `run_extraction_score(...)` and `run_quality_gate(...)` only consume `snapshot.jsonl` / `score.json`. That means a fully failed fund can be invisible to the gate if callers do not manually inspect `errors.jsonl`.

Next gate: `P5-S4 plan review`.

## Inputs

- Design truth: `docs/design.md`
- Global control doc: `docs/implementation-control.md`
- P4/P5 control doc: `docs/implementation-control-p4.md`
- Post-P4 follow-up planning: `docs/reviews/post-p4-follow-up-planning-20260520.md`
- Current implementation:
  - `fund_agent/fund/extraction_snapshot.py`
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/quality_gate.py`
  - `fund_agent/fund/quality_gate_integration.py`

## First Principles

The quality gate must protect the user-facing report path from low-quality inputs. A complete extraction failure is stronger evidence than field-level missingness: the system has no structured data for that fund. Treating that failure as “not present in snapshot, therefore not evaluated” violates the P4 quality closure goal.

The root cause must remain data-same-source: use `SnapshotErrorRecord` written by the snapshot runner, not logs, Markdown summaries, shell output, or inferred missing rows.

## Current Facts

- `run_extraction_snapshot(...)` writes:
  - `snapshot.jsonl` for successful fund records.
  - `errors.jsonl` for failed funds, using `SnapshotErrorRecord`.
- `run_extraction_score(...)` currently takes `snapshot_path`, `source_csv`, `output_dir`, thresholds, and optional golden answer path. It does not read `errors.jsonl`.
- `write_extraction_score_records(...)` is used by the single-fund `quality_gate_integration` adapter and receives in-memory records. In that path an extractor failure occurs before a bundle exists, so this slice should not invent failed-fund rows there.
- `run_quality_gate(...)` only consumes `score.json`.

## Target Contract

### 1. Score payload adds `failed_funds`

`score.json` should include:

```json
"failed_funds": [
  {
    "fund_code": "000001",
    "fund_name": "失败基金",
    "app_category": "国内股票类",
    "report_year": 2024,
    "error_type": "RuntimeError",
    "error_message": "fixture failure"
  }
]
```

Rules:

- The input is parsed from `errors.jsonl` records produced by `run_extraction_snapshot(...)`.
- The public dataclass should be explicit, e.g. `FailedFundRow`.
- No exception stack, logs, or free-form summary parsing.
- `error_message` may be surfaced, but gate issue messages should not depend on matching exact exception text.

### 2. Score CLI/service explicitly accepts an optional errors path

Add an explicit parameter, not `extra_payload`:

- Capability file entry: `run_extraction_score(..., errors_path: Path | None = None)`
- Capability writer: `write_extraction_score_records(..., failed_funds: Sequence[FailedFundRow] = ())`
- Service request: `ExtractionScoreRequest(errors_path: Path | None = None)`
- CLI: `fund-analysis extraction-score --errors-path <path>`

Default behavior:

- If omitted, retain current behavior and output `failed_funds: []`.
- Do not silently auto-discover sibling `errors.jsonl` in this slice. Auto-discovery can create surprising coupling; the caller should pass the path produced by snapshot when they want failure accounting.
- `write_extraction_score_records(...)` must not read files. `run_extraction_score(...)` is responsible for parsing `errors_path` and passing structured `FailedFundRow` values to the writer.

### 3. Quality gate blocks failed funds

`run_quality_gate(...)` should evaluate `score.json.failed_funds`:

- If absent: old score compatibility, no issue.
- If present and not a list: `ValueError`.
- For each object: validate at least `fund_code` and emit a block issue.

Suggested rule:

- `rule_code="FQ6"`
- `severity="block"`
- `fund_code=<fund_code>`
- `message="基金 `<code>` 抽取流程失败，无法生成可靠报告；error_type=`...`"`

This is a fund-level blocking issue, independent of P0 field scores because no field rows exist for a totally failed fund.

### 4. Output/reporting updates

- `score.md` should add a short “Failed Funds” section.
- `quality_gate.json` already serializes issues generically; no schema change beyond issue rule code.
- `quality_gate.md` should naturally include the issue through existing issue table. If the table omits rule code/fund code, update minimally.

## Implementation Slices

1. `extraction_score.py`
   - Add `FailedFundRow`.
   - Add `load_snapshot_error_records(errors_path: Path)`.
   - Loader validation:
     - Ignore empty lines.
     - Require every non-empty line to be a JSON object.
     - Require non-empty `fund_code`.
     - Normalize optional `fund_name`, `app_category`, `report_year`, `error_type`, and `error_message` to `None` when absent.
     - Raise `ValueError` for malformed rows.
   - Add `failed_funds` to `ExtractionScoreResult`.
   - Extend `_score_json_payload(...)` and `_score_markdown(...)`.
   - Add `errors_path` explicit parameter to `run_extraction_score(...)`, defaulting to no failures.
   - Add `failed_funds` structured parameter to `write_extraction_score_records(...)`, defaulting to no failures.

2. Service / CLI
   - Extend `fund_agent/services/extraction_score_service.py` request and forwarding.
   - Extend `fund_agent/ui/cli.py extraction-score` with `--errors-path`.
   - CLI help and README must describe it as the `errors.jsonl` produced by `extraction-snapshot`.
   - Keep `quality_gate_integration.py` passing no failed funds, because it starts from an already available bundle.

3. `quality_gate.py`
   - Evaluate `failed_funds` from score payload.
   - Emit FQ6 block issue per failed fund.
   - Preserve old score compatibility when `failed_funds` is absent.

4. Tests / README
   - Add extraction score test: snapshot success + errors path failure produces `failed_funds`.
   - Add quality gate test: `failed_funds` produces block issue.
   - Add Service/CLI tests for explicit `errors_path` forwarding.
   - Update README, `fund_agent/fund/README.md`, and `tests/README.md`.

## Non-Goals

- Do not make failed funds appear as synthetic 14-field snapshot records.
- Do not infer failures from missing codes in the source CSV.
- Do not change `run_extraction_snapshot(...)` output format.
- Do not make `quality_gate_integration.py` handle extractor exceptions; Service already cannot build a bundle when extraction fails.
- Do not auto-discover `errors.jsonl` from `snapshot_path.parent`.

## Review Questions

1. Is explicit `--errors-path` preferable to auto-discovery for avoiding hidden coupling? Controller answer after review: yes, keep explicit.
2. Should FQ6 be a new rule code, or should failed funds reuse FQ2F? Controller answer after review: use FQ6 because it is not a field score failure.
3. Should `failed_funds` be required in new score schema? Controller answer after review: include it in all newly written score payloads as an empty list when no errors path is provided, while preserving compatibility for old score files that lack it.
4. Should `write_extraction_score_records(...)` accept a file path? Controller answer after review: no; it should accept structured `failed_funds` only.

## Validation Plan

- `pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py -q`
- `pytest tests/ -q`
- `ruff check .`
- `git diff --check`

## Gate Decision

Current gate advances from `P5-S4 plan review` to `P5-S4 plan patched after controller review`.

Next gate: `P5-S4 plan re-review`.
