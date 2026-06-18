# Docling Baseline Qualification Bounded EID-only Artifact Capture Plan - 2026-06-15

Status: `READY_FOR_PLAN_REVIEW_NOT_READY`
Gate: `Bounded EID-only Sample Acquisition Artifact Capture Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Plan a non-destructive artifact-capture evidence gate for S4/S5/S6 EID-controlled annual-report PDFs, using the metadata accepted in `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-controller-judgment-20260615.md`.

The goal is to make S4/S5/S6 available as EID-controlled local PDF artifacts for later representation/export comparison planning without overwriting existing provenance-conflicted cache files.

This plan does not execute PDF download.

## 2. Source Of Truth

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-controller-judgment-20260615.md`

Accepted metadata inputs:

| Sample | Fund/year | EID metadata status | Upload id | Fund short name |
|---|---|---|---:|---|
| S4 | `006597 / 2024` | `eid_metadata_matched_no_download` | `1253099` | `国泰利享中短债债券` |
| S5 | `017641 / 2024` | `eid_metadata_matched_no_download` | `1256369` | `摩根标普500指数发起式(QDII)` |
| S6 | `110020 / 2024` | `eid_metadata_matched_no_download` | `1249587` | `易方达沪深300ETF联接` |

## 3. Non-goals

- No PDF download in this planning gate.
- No overwrite of `cache/pdf/006597_2024_annual_report_eid.pdf`.
- No write to production-shaped `cache/pdf/<fund>_<year>_annual_report_eid.pdf` in the first capture evidence gate.
- No `FundDocumentRepository` execution.
- No Docling conversion.
- No pdfplumber export.
- No field correctness comparison.
- No production parser replacement.
- No source policy change.
- No non-EID fallback.
- No Service/UI/Host/renderer/quality-gate direct source/PDF/parser access.
- No provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands.

Forbidden claims:

- Artifact capture proves field correctness.
- Artifact capture proves Docling baseline qualification.
- Artifact capture proves source truth beyond accepted EID metadata and PDF integrity.
- Artifact capture changes production repository/cache behavior.
- Artifact capture makes release/readiness anything other than `NOT_READY`.

## 4. Current Cache Conflict

Metadata-only preflight observed an existing local file:

```text
cache/pdf/006597_2024_annual_report_eid.pdf
size=792928
mtime=May 29 05:51:59 2026
```

Prior provenance evidence classified this file as `EID-labeled filename only` with manual metadata conflict. The first artifact-capture execution gate must not overwrite or silently reuse this path.

Decision:

- Use a gate-owned staging directory under ignored `cache/`.
- Capture all S4/S5/S6 PDFs into staging, including S4.
- Do not write to `cache/pdf/` until a later cache promotion/replacement gate explicitly accepts the captured hashes and replacement policy.

## 5. Planned Write Set For Execution Gate

Execution gate may write only:

```text
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf
docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-evidence-20260615.md
```

The staging directory is under `cache/`, which is ignored by `.gitignore`. The durable tracked output is only the evidence artifact under `docs/reviews/`.

Execution gate must not write:

```text
cache/pdf/006597_2024_annual_report_eid.pdf
cache/pdf/017641_2024_annual_report_eid.pdf
cache/pdf/110020_2024_annual_report_eid.pdf
reports/representation-json/
reports/docling-route-a/
docs/design.md
docs/implementation-control.md
docs/current-startup-packet.md
source files
tests
```

## 6. Planned Official EID Requests

Execution gate may request only:

```text
GET http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1253099
GET http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1256369
GET http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1249587
```

Optional metadata re-check before each PDF request may use the same accepted metadata endpoints:

```text
POST http://eid.csrc.gov.cn/fund/disclose/validate_fund.do
GET http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do?aoData=<accepted annual-report metadata query>
```

No XBRL HTML render endpoint is needed for this gate.

## 7. Integrity And Identity Rules

For each sample, execution evidence must record:

- requested URL;
- final URL after redirects, if any;
- HTTP status;
- response content type;
- response content length header, if present;
- downloaded byte size;
- SHA-256 of downloaded bytes;
- first five bytes must equal `%PDF-`;
- staging path;
- metadata identity row used for the request.

Acceptance criteria for each captured PDF:

| Check | Required result |
|---|---|
| HTTP status | `200` |
| final domain | official EID domain |
| content type | exact `application/pdf` after stripping parameters |
| PDF magic bytes | starts with `%PDF-` |
| byte size | greater than 0 and recorded |
| SHA-256 | recorded |
| write path | exact staging path under `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/` |
| source identity | must match accepted metadata: fund code, year, report code `FB010010`, report description `年度报告`, upload id |

If a response fails integrity checks, the execution gate must stop and classify the sample as `eid_integrity_error`, not fallback.

## 8. Execution Evidence Artifact

Execution gate writes exactly one tracked evidence artifact:

`docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-evidence-20260615.md`

Minimum structure:

1. Scope
2. Source Of Truth
3. Preflight
4. Accepted Metadata Inputs
5. Capture Directory And Non-overwrite Policy
6. Request / Response Matrix
7. File Integrity Matrix
8. Staging Artifact Manifest
9. Blocked Proofs And Residuals
10. Validation
11. Final Classification

Per-sample final classification vocabulary:

- `eid_artifact_captured_staged`
- `eid_integrity_error`
- `eid_unavailable`
- `eid_identity_mismatch`
- `eid_schema_drift`
- `blocked_auth_or_captcha`

Whole-gate verdict vocabulary:

- `ALL_REQUIRED_EID_ARTIFACTS_CAPTURED_STAGED_NOT_READY`
- `PARTIAL_CAPTURE_BLOCKED_NOT_READY`
- `CAPTURE_FAILED_NOT_READY`

## 9. Required Commands For Execution Gate

Allowed command families:

```text
git branch --show-current
git status --short
git status --branch --short
mkdir -p cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf
curl or equivalent HTTP client for the three official EID PDF URLs only
shasum -a 256 on the three staged PDFs
stat on the three staged PDFs
xxd/head or equivalent first-byte check on the three staged PDFs
git diff --check
```

Constraints:

- Do not use `FundDocumentRepository` or `EidAnnualReportSource.fetch_annual_report_pdf()` for this evidence gate because those paths may reuse or overwrite `cache/pdf`.
- Direct official EID HTTP access is allowed only as an evidence-only staging exception for this gate. It does not change the production rule that annual-report access goes through `FundDocumentRepository`.
- Do not use production analyzer/checklist or parser commands.
- Do not use non-EID URLs.
- Do not use browser state, auth, captcha or manual download.

Execution command constraints:

- use explicit connect timeout and max-time values;
- use fail-on-HTTP-error behavior;
- use at most one bounded retry per URL, or explicitly record `retry=0`;
- write only to the exact staging paths listed in §5;
- if using temporary files, they must live under the same staging directory and must be removed or left with an `.incomplete` suffix recorded in evidence;
- do not write headers, raw response dumps or debug payloads outside the evidence artifact and staging directory.

## 10. Review Checklist

Reviewers must check:

- Does the plan avoid overwriting existing `cache/pdf/006597_2024_annual_report_eid.pdf`?
- Does the plan keep capture under an ignored gate-owned staging path?
- Does the plan use only accepted EID `uploadInfoId` values?
- Does the plan preserve EID single-source/no fallback?
- Does the plan avoid `FundDocumentRepository`, Docling, pdfplumber and production analyzer commands?
- Does it avoid field correctness, source truth, baseline and readiness claims?
- Does it define exact stop conditions and classifications?

## 11. Stop Conditions

Stop before execution if:

- any worker proposes writing directly to `cache/pdf/` in the first capture gate;
- any worker proposes deleting, moving, renaming, archiving or overwriting the existing S4 cache file;
- any worker proposes CNINFO, fund-company, Eastmoney, akshare or local non-EID fallback;
- any worker proposes Docling conversion or pdfplumber export in this capture gate;
- EID PDF response requires auth, captcha or browser state;
- EID redirects outside official EID domains;
- integrity checks fail for any sample;
- execution would require source/test/runtime behavior changes.

## 12. Next Gate Recommendation

Immediate next gate:

`Bounded EID-only Sample Acquisition Artifact Capture Plan Review Gate`

If accepted:

`Bounded EID-only Sample Acquisition Artifact Capture Evidence Gate`

After artifact-capture evidence is accepted, route to one of:

1. `EID Staged PDF Cache Promotion Planning Gate` if production-shaped `cache/pdf` paths are needed;
2. `Full Representation Export Planning Gate` if later export commands can consume explicit staged PDF paths without promotion.

Do not proceed directly to Docling conversion, pdfplumber export, field correctness, production integration or readiness.

## 13. Validation

Planning validation:

```text
git diff --check
```

## 14. Final Verdict

`VERDICT: READY_FOR_PLAN_REVIEW_NOT_READY`
