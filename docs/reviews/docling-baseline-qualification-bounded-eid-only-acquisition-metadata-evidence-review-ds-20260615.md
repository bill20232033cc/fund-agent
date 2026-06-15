# DS-role Review - Bounded EID-only Acquisition Metadata Evidence - 2026-06-15

Artifact reviewed: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-20260615.md`
Role: DS-role evidence review worker
Review state: initial review before supplemental `fundShortName` evidence

## Findings

| Severity | Evidence | Recommendation | Blocking |
|---|---|---|---|
| High | Plan §4.4 requires `fund_name / fund_short_name`; if present it must not contradict target identity, and missing name routes to `identity_partly_matched`. The reviewed evidence recorded `fundCode`, `fundId`, `reportYear`, `reportCode/reportDesp`, `tableName`, `uploadInfoId`, `reportName`, and `reportSendDate`, but did not record an independent `fund_name / fund_short_name`, while classifying S4/S5/S6 as `eid_metadata_matched_no_download`. | Before controller closeout, either add EID metadata with fund name/short name and prove no contradiction, or downgrade S4/S5/S6 to `identity_partly_matched`. | Yes |
| Medium | The artifact confirms only `validate_fund.do` and `advanced_search_report.do` were used, and did not request PDF body/hash/cache write. | Preserve boundary; artifact capture must be a later gate. | No |
| Low | The artifact lists PDF-byte residuals, S3 hash gap, and control-doc lag, but did not list the fund-name identity gap. | If not supplemented, add it as residual/blocker. | Linked to High |

## Accepted Facts

- The artifact uses only EID metadata/search: `validate_fund.do` and `advanced_search_report.do`.
- The artifact states it did not download PDF body, request PDF endpoint, compute PDF hash, or write cache.
- It did not run `FundDocumentRepository`, Docling conversion, pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR.
- It did not reintroduce CNINFO, fund-company, Eastmoney or akshare fallback.
- It did not claim PDF acquisition, field correctness, source truth, Docling baseline proof or readiness proof.
- S4/S5/S6 all have EID metadata rows with fund code/year/type/table/upload id/report title/send date aligned to annual-report direction.

## Residuals

- S4/S5/S6 PDF bytes, PDF integrity, PDF hash and cache artifact capture remain unproven.
- S3 hash gap remains unhandled.
- S4/S5/S6 exact identity still needs independent fund name/short name or equivalent controller-accepted identity treatment.
- Control-doc lag can be handled after controller closeout.

## Verdict

`FAIL`

Reason: identity classification did not yet align with accepted plan §4.4 because independent `fund_name / fund_short_name` evidence was missing.
