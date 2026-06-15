# DS-role Review - Bounded EID-only Artifact Capture Plan - 2026-06-15

Artifact reviewed: `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-plan-20260615.md`
Role: DS-role plan review worker

## Findings

| Severity | Evidence | Recommendation | Blocking |
|---|---|---|---|
| Low | §9 allows direct `curl or equivalent HTTP client` for the three official EID PDF URLs while explicitly avoiding `FundDocumentRepository` to prevent reuse/overwrite of `cache/pdf`. This fits the evidence-only staging objective, but must not be generalized into production document access. | Controller closeout should state that direct EID HTTP capture is evidence-only staging and does not alter the production `FundDocumentRepository` boundary. | No |
| Low | §8 defines per-sample classifications but initially did not define whole-gate verdict tokens. | Evidence worker should report both per-sample classification and a whole-gate verdict such as `ALL_REQUIRED_EID_ARTIFACTS_CAPTURED_STAGED_NOT_READY` or `PARTIAL_CAPTURE_BLOCKED_NOT_READY`. | No |

## Accepted Facts

- The plan explicitly does not overwrite existing `cache/pdf/006597_2024_annual_report_eid.pdf`.
- The staging path is `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/`, not production-shaped `cache/pdf/`, and is under ignored `cache/`.
- The plan uses only accepted EID `uploadInfoId` values: `1253099`, `1256369`, `1249587`.
- The plan avoids `FundDocumentRepository`, Docling, pdfplumber and production analyzer/checklist commands.
- The plan preserves EID single-source/no fallback and forbids CNINFO, fund-company, Eastmoney, akshare and local non-EID fallback.
- It preserves `NOT_READY` and avoids field correctness, source truth, baseline and readiness claims.
- Stop conditions cover old-cache overwrite, non-EID fallback, cross-domain redirect, auth/captcha, integrity failure, Docling/pdfplumber scope creep and source/test/runtime behavior changes.

## Residuals

- Staged PDFs, even if captured, prove only EID-controlled local artifact bytes plus basic integrity; they do not prove field correctness, source truth, Docling baseline or readiness.
- Staged-to-production cache promotion remains a separate gate.
- Full representation export from staged paths remains a separate gate.

## Verdict

`PASS_WITH_RESIDUALS`

## Controller-applied Non-blocking Amendments

After this review, the plan was amended to:

- state direct EID HTTP capture is evidence-only staging and does not alter the `FundDocumentRepository` production boundary;
- add whole-gate verdict vocabulary;
- add exact command constraints for timeout, fail-on-HTTP-error behavior, bounded retry, staging-only writes and partial-file handling.
