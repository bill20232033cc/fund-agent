# DS-role Targeted Re-review - Bounded EID-only Acquisition Metadata Evidence - 2026-06-15

Artifact reviewed: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-20260615.md`
Role: DS-role targeted re-review worker
Scope: only the initial DS blocker about missing independent `fund_name / fund_short_name`

## Re-reviewed Finding

Initial blocker: the evidence artifact classified S4/S5/S6 as `eid_metadata_matched_no_download` without independent `fund_name / fund_short_name`, which did not align with accepted plan §4.4.

## Closure Assessment

Closed.

Re-reviewed revisions:

- §4 adds a supplemental field check explaining that the same `advanced_search_report.do` metadata endpoint was queried again to confirm row-level `fundShortName`, without requesting or downloading PDF bytes.
- §5 Evidence Matrix adds:
  - S4: `fundShortName=国泰利享中短债债券`, `organName=国泰`
  - S5: `fundShortName=摩根标普500指数发起式(QDII)`, `organName=摩根`
  - S6: `fundShortName=易方达沪深300ETF联接`, `organName=易方达`
- §7 Classification Rules Applied adds `fundShortName is present and does not contradict target fund identity`.
- The artifact still only claims `eid_metadata_matched_no_download`, not PDF acquisition, source truth, field correctness or readiness.

These revisions satisfy the accepted plan §4.4 identity field requirement for this metadata-only gate.

## Remaining Residuals

- PDF bytes/hash/integrity remain unproven.
- S3 hash gap remains an existing residual outside this re-review scope.
- `fundShortName` is metadata-level identity support, not fund fact truth or field correctness proof.

## Verdict

`PASS`
