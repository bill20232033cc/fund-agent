# Controller Plan Re-Review - P5-S4 Snapshot Failure Accounting - 2026-05-20

## Verdict

PASS.

## Reviewed Patch

- `docs/reviews/p5-s4-snapshot-failure-accounting-plan-20260520.md`
- Prior review: `docs/reviews/p5-s4-plan-review-controller-20260520.md`

## Finding Closure

| Finding | Status | Evidence |
|---|---|---|
| P5-S4-PR1: writer should not accept `errors_path` | closed | Plan now keeps file parsing in `run_extraction_score(...)` and passes structured `failed_funds` to `write_extraction_score_records(...)`. |
| P5-S4-PR2: loader validation underspecified | closed | Plan now requires object JSONL rows, non-empty `fund_code`, optional field normalization, and fail-fast `ValueError` for malformed rows. |
| P5-S4-PR3: CLI/service docs must explain pairing | closed | Plan now requires CLI help and README to describe `--errors-path` as the `errors.jsonl` produced by `extraction-snapshot`. |

## Controller Judgment

The patched plan is implementation-ready. It preserves boundaries:

- Snapshot failure facts originate in Capability `SnapshotErrorRecord`.
- Score file entry parses optional `errors_path` explicitly.
- Score writer accepts structured failed rows and remains usable by bundle-based integration.
- Quality gate consumes only `score.json`.
- Service/CLI only forward explicit parameters and render status.

Next gate: `P5-S4 implementation`.
