# Controller Plan Review - P5-S4 Snapshot Failure Accounting - 2026-05-20

## Verdict

PASS WITH PATCHED REQUIREMENTS.

The plan correctly identifies the root cause: failed funds are written to `errors.jsonl` but are absent from `score.json`, so `quality_gate` cannot block them. The proposed fix keeps evidence data-same-source by consuming `SnapshotErrorRecord`, and it keeps the failure accounting in Capability / Service / CLI boundaries without moving quality logic into UI.

## Findings

### P5-S4-PR1 - `write_extraction_score_records(...)` should not accept `errors_path`

Severity: medium

The plan says to add `errors_path` to both `run_extraction_score(...)` and `write_extraction_score_records(...)`. That would blur two different entry points:

- `run_extraction_score(...)` is file-oriented and can parse `errors.jsonl`.
- `write_extraction_score_records(...)` is already an in-memory writer used by `quality_gate_integration.py` after Service has a bundle.

Patch requirement:

- Add `errors_path` only to `run_extraction_score(...)`.
- Add `failed_funds: Sequence[FailedFundRow] = ()` to `write_extraction_score_records(...)`.
- `run_extraction_score(...)` loads `errors_path` into `failed_funds` and passes the structured rows onward.
- `quality_gate_integration.py` remains unchanged or passes no failed rows.

Rationale:

This keeps explicit parameters while avoiding a lower-level writer unexpectedly reading files.

### P5-S4-PR2 - loader must reject non-object JSONL rows and missing fund code

Severity: medium

The plan says to add `load_snapshot_error_records(errors_path)`, but the validation contract is underspecified.

Patch requirement:

- Empty lines are ignored.
- Each non-empty line must be a JSON object.
- `fund_code` is required and non-empty.
- `fund_name`, `app_category`, `report_year`, `error_type`, and `error_message` are optional for old or hand-written fixtures, but the output row should normalize them to `None` when absent.
- A malformed `errors.jsonl` should fail fast with `ValueError`; otherwise gate consumers may trust partial accounting.

### P5-S4-PR3 - CLI/service docs must make `--errors-path` a pairing with snapshot output

Severity: low

The no-auto-discovery decision is accepted. The user-facing docs and CLI help need to make the expected usage obvious:

```bash
fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/<run-id>/snapshot.jsonl \
  --errors-path reports/extraction-snapshots/<run-id>/errors.jsonl
```

Patch requirement:

- Root README extraction-score example should include `--errors-path`.
- CLI option help should say it is the `errors.jsonl` produced by `extraction-snapshot`.

## Accepted Decisions

- Use new rule code `FQ6` for extraction failures.
- Emit block severity for every failed fund.
- Preserve old score compatibility when `failed_funds` is absent.
- Write `failed_funds: []` in all new score payloads when no errors path is supplied.
- Do not create synthetic 14-field snapshot rows.
- Do not infer failed funds by comparing source CSV codes to snapshot codes.

## Required Plan Patch

Update the plan with PR1/PR2/PR3 before implementation.

Next gate after patch: `P5-S4 plan re-review`.
