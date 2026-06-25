# EC-P2W-2 Live Re-evidence After Pathway Status

- Gate: EC-P2W-2 authorized live re-evidence
- Work unit: Evidence Confirm productionization / EC-P2 repository-bounded live source/PDF pathway
- Sample: `004393/2025`
- Date: 2026-06-22

## Command

```text
uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh
```

## Result

- Exit code: `0`
- Safe JSON output:

```json
{
  "evidence_confirm_overall_status": "warn",
  "failure_categories": [],
  "field_correctness_proven": false,
  "issue_reasons": [],
  "pathway_status": "pass",
  "pathway_warning_reasons": [
    "v2_anchor_precision_warn_section_only_smoke"
  ],
  "projection_kind": "ec_p2_live_section_smoke",
  "reference_count": 1,
  "sample": "004393/2025",
  "source_metadata_admitted": true,
  "status": "fail"
}
```

## Interpretation

- Repository-bounded live source/PDF pathway is proven for this exact sample:
  - repository load returned admitted EID single-source/no-fallback metadata;
  - materializer built one annual-report reference;
  - V2 ran and produced the expected section-only E1 `anchor_precision` warning;
  - runner reported `pathway_status="pass"`.
- Strict V2 status remains intentionally not pass:
  - strict runner `status="fail"`;
  - `evidence_confirm_overall_status="warn"`;
  - `field_correctness_proven=false`.

## Non-Goals Preserved

- Does not prove field correctness.
- Does not prove semantic entailment.
- Does not promote golden/readiness/release.
- Does not integrate Service/UI/Host/renderer/quality gate.
- Does not change source fallback behavior.
- Does not prove additional samples.

## Next Gate

EC-P2 aggregate deepreview.

