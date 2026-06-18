# Docling Baseline Qualification Bounded EID-only Artifact Capture Plan Controller Judgment - 2026-06-15

Gate: `Bounded EID-only Sample Acquisition Artifact Capture Planning Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the artifact-capture planning gate for S4/S5/S6 EID-controlled annual-report PDFs.

This judgment does not execute PDF download, does not authorize writes to production-shaped `cache/pdf`, does not authorize overwriting the existing S4 cache file, does not run `FundDocumentRepository`, Docling, pdfplumber, analyzer/checklist, provider/LLM, golden/readiness/release/PR/push/merge commands, and does not change source policy or production behavior.

## 2. Artifacts Reviewed

- Plan: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-plan-20260615.md`
- DS-role review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-plan-review-ds-20260615.md`
- MiMo-role review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-plan-review-mimo-20260615.md`
- Metadata evidence controller judgment: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-controller-judgment-20260615.md`
- Current truth docs: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## 3. Accepted Plan Decisions

| Decision | Controller disposition | Reason |
|---|---|---|
| Use gate-owned staging path `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/`. | ACCEPT | Avoids reuse/overwrite of provenance-conflicted production-shaped cache paths while keeping binary artifacts under ignored `cache/`. |
| Do not write to `cache/pdf/` in the first artifact-capture evidence gate. | ACCEPT | S4 `cache/pdf/006597_2024_annual_report_eid.pdf` already exists with provenance conflict; direct overwrite would destroy evidence context. |
| Capture all required samples S4/S5/S6 into staging, including S4. | ACCEPT | Produces comparable EID-controlled staged bytes for all required missing samples. |
| Use only accepted EID `uploadInfoId` values `1253099`, `1256369`, `1249587`. | ACCEPT | These were accepted by metadata evidence as exact EID annual-report metadata matches. |
| Avoid `FundDocumentRepository` and `EidAnnualReportSource.fetch_annual_report_pdf()` for the evidence command. | ACCEPT_WITH_BOUNDARY_NOTE | This is an evidence-only staging exception to prevent cache reuse/overwrite; it does not change the production rule that annual-report access goes through `FundDocumentRepository`. |
| Require `application/pdf`, `%PDF-`, byte size and SHA-256 integrity evidence. | ACCEPT | Matches current EID source integrity expectations without invoking production cache path. |
| Preserve `NOT_READY`. | ACCEPT | Artifact capture is not field correctness, Docling baseline, production integration or release/readiness proof. |

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| Direct EID HTTP must be explicitly limited to evidence-only staging and not production access. | DS-role review | ACCEPT_AS_NONBLOCKING_AMENDMENT | Plan amended in §9. |
| Evidence gate needs whole-gate verdict tokens. | DS-role review | ACCEPT_AS_NONBLOCKING_AMENDMENT | Plan amended in §8. |
| HTTP command details should specify timeout, fail-on-error, retry and partial-file handling. | MiMo-role review | ACCEPT_AS_NONBLOCKING_AMENDMENT | Plan amended in §9. |

No blocking finding remains.

## 5. Rejected Or Deferred Claims

| Claim | Disposition | Reason |
|---|---|---|
| Artifact-capture plan authorizes immediate PDF download. | REJECT | Next gate is evidence execution; this plan only defines boundaries. |
| Artifact-capture plan authorizes overwrite/promotion to `cache/pdf`. | REJECT | First capture gate is staging-only; promotion requires later gate. |
| Direct EID HTTP can become normal production document access. | REJECT | Direct HTTP is accepted only for this evidence-only staging gate; production remains `FundDocumentRepository` boundary. |
| Captured PDFs would prove field correctness/source truth/Docling baseline/readiness. | REJECT | Captured PDFs only prove EID metadata-linked bytes and basic integrity. |
| Non-EID fallback can be used if EID download fails. | REJECT | EID single-source/no fallback remains binding. |
| S3 hash gap is resolved by this plan. | DEFER | This plan handles required S4/S5/S6 only. |

## 6. Next Gate

Primary next gate:

`Bounded EID-only Sample Acquisition Artifact Capture Evidence Gate`

Allowed in that gate:

- create `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/`;
- request only:
  - `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1253099`
  - `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1256369`
  - `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1249587`
- write only the three staged PDFs and one tracked evidence artifact;
- record status, final URL, content type, bytes, SHA-256 and `%PDF-` check;
- classify per-sample and whole-gate verdict.

Still not authorized:

- writing to `cache/pdf/`;
- deleting/moving/renaming/archiving/overwriting existing cache files;
- Docling conversion;
- pdfplumber export;
- source/test/runtime behavior change;
- field correctness comparison;
- production integration;
- readiness/release/PR/push/merge.

## 7. Validation

```text
git diff --check
passed
```

## 8. Final Verdict

`VERDICT: ACCEPT_PLAN_READY_FOR_STAGED_ARTIFACT_CAPTURE_EVIDENCE_NOT_READY`
