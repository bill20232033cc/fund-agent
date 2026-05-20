# P7 Aggregate Readiness Reconciliation - 2026-05-20

## Scope

- Phase: P7 annual report source migration
- Design source: `docs/design.md`
- Control doc: `docs/implementation-control-p4.md`
- Current gate: `P7 aggregate readiness reconciliation`

## Verdict

P7 is ready for aggregate deepreview.

All planned P7 slices from `docs/reviews/post-p6-follow-up-planning-20260520.md` have been completed, reviewed, accepted, committed, and pushed to `origin/main`.

## Slice Status

| Slice | Status | Accepted artifacts | Commit |
|---|---|---|---|
| P7-S1 EID source research spike | Accepted | `docs/reviews/p7-s1-eid-source-research-spike-plan-20260520.md`, `docs/reviews/plan-review-20260520-210548.md` | `3f281e3` |
| P7-S2 document repository source abstraction | Accepted after fix | `docs/reviews/p7-s2-implementation-20260520.md`, `docs/reviews/p7-s2-code-review-controller-judgment-20260520.md` | `eb39877` |
| P7-S3 EID primary implementation | Accepted | `docs/reviews/p7-s3-implementation-20260520.md`, `docs/reviews/p7-s3-code-review-controller-judgment-20260520.md` | `f727ca7` |
| P7-S4 source metadata hardening | Accepted | `docs/reviews/p7-s4-implementation-20260520.md`, `docs/reviews/p7-s4-code-review-controller-judgment-20260520.md` | `707d89f` |

## Readiness Evidence

- Design alignment:
  - EID/证监会资本市场电子化信息披露平台 is now the documented public-fund annual report primary source.
  - Eastmoney/akshare remains explicit fallback.
  - 巨潮 is not used as public-fund annual report primary source.
  - Annual report access remains behind Fund Capability document repository boundaries.
- Source acquisition:
  - `EidAnnualReportSource` validates fund code, searches annual report metadata, downloads PDF, and validates `Content-Type` plus `%PDF-`.
  - default order is EID primary -> Eastmoney/akshare fallback.
  - mismatch/schema errors stop fallback; not-found/unavailable errors can fallback.
- Metadata/provenance:
  - `ParsedAnnualReport.metadata` now carries source metadata and cache provenance.
  - `documents.source_metadata_json` persists source metadata in the PDF cache row.
  - legacy parsed payloads and legacy documents rows remain compatible.
  - metadata travels through per-call `AnnualReportPdfFetchResult`, not adapter-wide mutable state.
- Verification at latest accepted commit:
  - P7-S4 source metadata focused tests: `55 passed`
  - full suite: `290 passed`
  - `ruff check .`: passed
  - `git diff --check`: passed

## Residual Risks

| Risk | Owner / Destination | Status |
|---|---|---|
| Live EID schema can drift from mocked fixture shape | Future data-source operational hardening / Evidence Confirm phase | Tracked; current code fails closed on schema mismatch |
| `source_metadata_json` corruption by manual SQLite edits can raise during cache read | Future cache robustness hardening if needed | Non-blocking; code-controlled writes are valid |
| New source names require updating `AnnualReportSourceName` and deserialization validation | Future source expansion slice | Non-blocking |
| P7 did not add report/UI display of source provenance | Future UX/report provenance slice if needed | Non-goal for P7 |

## Next Gate

Proceed to `P7 aggregate deepreview`.

Aggregate review should focus on cross-slice behavior rather than isolated tests:

- whether source abstraction, EID primary, fallback categories, and metadata persistence compose correctly;
- whether cache behavior can hide stale or wrong-source PDFs;
- whether provenance remains inside Fund Capability without Service/UI source awareness;
- whether legacy cache compatibility is robust enough for existing users;
- whether public model/export choices are coherent for downstream Capability consumers.
