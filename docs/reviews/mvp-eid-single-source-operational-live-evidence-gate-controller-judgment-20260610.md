# EID Single Source Operational Live Evidence Gate - Controller Judgment

## Verdict

`ACCEPTED`.

The gate accepts one bounded live EID acquisition proof for `004393 / 2024` through `FundDocumentRepository`.

## Evidence Chain

- Plan: `docs/reviews/mvp-eid-single-source-operational-live-evidence-gate-plan-20260610.md`
- Plan reviews:
  - `docs/reviews/mvp-eid-single-source-operational-live-evidence-gate-plan-review-ds-20260610.md`
  - `docs/reviews/mvp-eid-single-source-operational-live-evidence-gate-plan-review-mimo-20260610.md`
- Plan controller judgment: `docs/reviews/mvp-eid-single-source-operational-live-evidence-gate-plan-controller-judgment-20260610.md`
- Live evidence: `docs/reviews/mvp-eid-single-source-operational-live-evidence-gate-evidence-20260610.md`
- Evidence reviews:
  - `docs/reviews/mvp-eid-single-source-operational-live-evidence-gate-evidence-review-ds-20260610.md`
  - `docs/reviews/mvp-eid-single-source-operational-live-evidence-gate-evidence-review-mimo-20260610.md`

## Accepted Live Facts

For `004393 / 2024` only:

- live acquisition succeeded through `FundDocumentRepository.load_annual_report("004393", 2024, force_refresh=True)`;
- source metadata returned `source=eid`;
- `selected_source=eid`;
- `source_mode=single_source_only`;
- `fallback_enabled=false`;
- `fallback_used=false`;
- `primary_failure_category=None`;
- EID `upload_info_id=1248088`;
- EID `source_url=http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1248088`;
- PDF integrity evidence: `%PDF-` magic, `size_bytes=841826`, `sha256=bc6b0a1ae2f709f4cb4fa501f88ba9c19aa0f37d36758160577c57222e9860bf`;
- parser viability evidence: `raw_text_chars=66889`, `sections=8`, `tables=100`;
- temporary cache isolation avoided tracked workspace changes.

## Finding Disposition

Both evidence reviews returned `PASS`.

Non-blocking residuals:

- This proves only `004393 / 2024`, not all five small-golden rows.
- EID PDF content may change in a future live request; this is normal live evidence drift and does not invalidate the recorded hash.
- The downloaded PDF was not retained in review artifacts or tracked workspace files by design.

## Not Accepted By This Gate

This gate does not accept:

- all five small-golden rows;
- live EID failure branch coverage;
- extractor correctness;
- fixture projection;
- golden/readiness promotion;
- production report generation;
- provider / LLM behavior;
- fallback behavior;
- Eastmoney / fund-company / CNINFO source behavior.

## Final Boundary Check

Not performed:

- fallback invocation;
- Eastmoney / fund-company / CNINFO source use;
- extractor or `FundDataExtractor`;
- CLI `analyze` / `checklist`;
- Service / Host / UI / renderer / quality gate;
- provider / LLM / endpoint probe;
- fixture projection;
- golden/readiness promotion;
- source code, tests, config, runtime or budget changes;
- PR/push/merge/mark-ready.

## Next Entry

After checkpoint, valid next entries are:

1. Extend live EID evidence to additional rows, if separately authorized.
2. Return to queued row-shape contract decision gate.
3. Open a separate non-extractor phase.
