# EC-P2 Live Sample Evidence

Date: 2026-06-22

## Command

```text
uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh
```

## Authorization Boundary

- User authorized EC-P2 sample `004393/2025`.
- Command is repository-bounded and uses `FundDocumentRepository.load_annual_report("004393", 2025, force_refresh=True)` through the EC-P2 runner boundary.
- No provider/LLM command was run.
- No Service/UI/Host/renderer/quality-gate command was run.

## Result

Exit code: `0`

Safe JSON output:

```json
{
  "evidence_confirm_overall_status": "warn",
  "failure_categories": [],
  "field_correctness_proven": false,
  "issue_reasons": [],
  "projection_kind": "ec_p2_live_section_smoke",
  "reference_count": 1,
  "sample": "004393/2025",
  "source_metadata_admitted": true,
  "status": "fail"
}
```

## Accepted Facts

- Repository-bounded command completed with exit code `0`.
- Output stayed within safe scalar JSON; no excerpt, PDF path or source URL was emitted.
- EID single-source/no-fallback metadata admission is positive for the loaded sample:
  - `source_metadata_admitted=true`
- The live section-smoke projection produced one materialized annual-report reference:
  - `reference_count=1`
- Field correctness remains explicitly unproven:
  - `field_correctness_proven=false`

## Negative / Not-Ready Facts

- Runner aggregate status is not pass:
  - `status="fail"`
- V2 Evidence Confirm status is not pass:
  - `evidence_confirm_overall_status="warn"`
- This live result cannot be used as readiness, release, golden, semantic entailment or source-truth family proof.

## Controller Interpretation

The EC-P2 live command proves the repository-bounded pathway can load the authorized sample, admit same-source metadata, materialize one annual-report reference and emit safe JSON. It does not prove EC-P2 success because the runner aggregate status remains `fail` due to V2 `warn`.

## Next Gate Candidate

EC-P2 live warning disposition / fix planning:

- determine whether V2 `warn` is expected and acceptable for section-smoke pathway evidence, or
- adjust smoke projection / runner aggregation semantics under a reviewed plan, then rerun bounded no-live tests before any further live execution.
