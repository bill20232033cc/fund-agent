# Docling Baseline Qualification Bounded EID-only Acquisition Plan - 2026-06-15

Status: `READY_FOR_PLAN_REVIEW_NOT_READY`
Gate: `Bounded EID-only Sample Acquisition Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Scope

This plan defines how to resolve Docling baseline qualification sample provenance gaps using only EID-controlled evidence.

This gate is planning-only. It does not execute EID/network/FDR/PDF acquisition, does not read PDF bodies, does not run `FundDocumentRepository`, does not run Docling conversion, does not run pdfplumber export, does not run provider/LLM/analyze/checklist/golden/readiness/release/PR commands, and does not change code/source policy/runtime behavior.

## 2. Source Of Truth

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/docling-baseline-qualification-acquisition-status-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-local-artifact-provenance-status-evidence-controller-judgment-20260615.md`

Accepted input from Gate 0A:

| Sample | Gate 0A disposition | Planning implication |
|---|---|---|
| S1 `004393 / 2025` | accepted tri-route representation seed | No acquisition needed. |
| S2 `004393 / 2024` | local EID candidate with provided SHA-256 | May proceed as accepted local candidate if controller accepts metadata-only threshold; no live acquisition needed by default. |
| S3 `004194 / 2024` | local EID candidate with hash gap | Needs controller decision: accept metadata threshold for candidate export planning, or include in bounded EID evidence for metadata/hash follow-up. |
| S4 `006597 / 2024` | provenance conflict: `_eid` filename vs CNINFO manual metadata / EID id unknown | Must not use local artifact as EID-controlled without follow-up; include in bounded EID-only acquisition or replacement decision. |
| S5 `017641 / 2024` | non-EID local metadata | Include in bounded EID-only acquisition or replacement decision. |
| S6 `110020 / 2024` | non-EID local metadata | Include in bounded EID-only acquisition or replacement decision. |

## 3. Non-goals And Forbidden Claims

Non-goals:

- No production parser replacement.
- No `FundDocumentRepository` behavior change.
- No source policy change.
- No non-EID fallback.
- No Docling runtime or conversion.
- No pdfplumber full representation export.
- No manual field correctness review.
- No `EvidenceAnchor` / source-kind schema change.
- No Service/UI/Host/renderer/quality-gate direct source/PDF/parser access.

Forbidden claims:

- S2-S6 are fully accepted active samples before controller closeout.
- EID acquisition has succeeded before execution evidence.
- PDF content/hash is verified unless the later execution gate explicitly performs hash verification.
- Field correctness/source truth/readiness/taxonomy compatibility/raw XML direct download is proven.

## 4. Acquisition Strategy

### 4.1 Default Controller Decisions

The recommended controller path is:

| Sample | Recommended status before live execution | Reason |
|---|---|---|
| S1 `004393 / 2025` | `accepted_seed_no_action` | Already accepted tri-route seed. |
| S2 `004393 / 2024` | `accept_metadata_only_local_eid_candidate_for_export_planning` | Manual metadata has EID URL/id plus SHA-256; local path is EID-labeled. Use only as candidate, not source truth. |
| S3 `004194 / 2024` | `accept_metadata_only_local_eid_candidate_with_hash_residual` or include in optional bounded metadata check | Manual metadata has EID URL/id; local path is EID-labeled; hash missing. Risk can be carried to later export planning or resolved with bounded EID evidence. |
| S4 `006597 / 2024` | `requires_bounded_eid_only_acquisition_or_replacement` | Provenance conflict; do not use local `_eid` filename as proof. |
| S5 `017641 / 2024` | `requires_bounded_eid_only_acquisition_or_replacement` | Current local/manual source is fund-company, not EID-controlled. |
| S6 `110020 / 2024` | `requires_bounded_eid_only_acquisition_or_replacement` | Current local/manual source is fund-company, not EID-controlled. |

### 4.2 Bounded EID-only Execution Target

If user/controller later authorizes the execution gate, the active bounded target set should be:

- Required: S4 `006597 / 2024`, S5 `017641 / 2024`, S6 `110020 / 2024`.
- Optional: S3 `004194 / 2024` only for hash/provenance refresh if controller does not accept hash-gap residual.
- Excluded by default: S1 and S2.

### 4.3 Allowed Official EID Request Families For Later Execution

Later execution may use only official EID endpoints already used by accepted source-policy/evidence chains or directly derivable from accepted manual EID URLs:

- EID annual-report search endpoint for fund reports, with explicit query params:
  - `fundCode=<fund_code>`
  - `reportYear=<report_year>`
  - annual-report report type, e.g. `FB010`/`FB010010` only if confirmed by accepted EID metadata for that endpoint family.
- EID PDF endpoint:
  - `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=<id>`
- EID HTML/XBRL render endpoint only for availability classification, not raw XML or PDF acquisition:
  - `http://eid.csrc.gov.cn/fund/disclose/instance_html_view.do?instanceid=<id>`

Later execution must record exact requested URL, HTTP status, redirect target if any, content type, content length, SHA-256 for downloaded PDF bytes if downloaded, and final classification.

### 4.4 Exact Identity Match Rules

Before any metadata row can be used for later active-sample planning, evidence must classify identity with the following rules:

| Field | Required treatment |
|---|---|
| `fund_code` | Must exactly equal requested sample fund code. Conflict => `eid_identity_mismatch`. |
| `report_year` | Must exactly equal requested report year. Conflict => `eid_identity_mismatch`. |
| `report_type` / `reportDesp` | Must be annual report. If report type is absent, classify `identity_partly_matched`, not `eid_acquired`. Conflict => `eid_identity_mismatch`. |
| `instanceid` / `uploadInfoId` / EID document id | Must be recorded when available. Missing id in metadata-only mode => `identity_partly_matched`; missing id in artifact-capture mode blocks capture. |
| `fund_name` / `fund_short_name` | If present, must not contradict the target fund identity. Conflict => `eid_identity_mismatch`. Missing name => `identity_partly_matched`. |
| `report_title` / `reportSendDate` | If present, record as supporting metadata. Conflict with target year/type => `eid_identity_mismatch`; missing value is a residual, not a pass proof. |

Artifact capture is forbidden unless the sample is at least exact on `fund_code`, `report_year`, annual-report type and EID document id.

## 5. Replacement Rules

If EID cannot supply S4-S6 under the bounded execution gate, the controller must not fall back to CNINFO, fund-company websites, Eastmoney, akshare or local non-EID PDFs.

Instead:

| Failure class | Meaning | Disposition |
|---|---|---|
| `eid_not_found` | EID search returns no exact annual report for fund/year. | Replace sample with same profile using EID-only candidate or mark profile `out_of_scope`. |
| `eid_identity_mismatch` | Returned fund code/name/year/report type conflicts. | Reject candidate; find profile-preserving replacement or mark blocked. |
| `eid_unavailable` | Network/server/access transient failure. | Stop execution; do not fallback. |
| `eid_schema_drift` | EID response shape cannot be interpreted safely. | Stop execution; fail closed. |
| `eid_integrity_error` | PDF content type/header/hash/write validation fails. | Stop execution; fail closed. |
| `auth_or_captcha` | Requires manual browser state, auth or captcha. | Stop execution; mark `blocked_not_ready`. |

Replacement must preserve sample role:

- S4 replacement: bond fund.
- S5 replacement: QDII fund.
- S6 replacement: index / ETF-linked fund.

Replacement selection itself must be a reviewed planning/evidence step. Do not silently substitute samples.

## 6. Planned Execution Artifact

If authorized later, evidence worker writes exactly one execution artifact:

`docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-evidence-20260615.md`

It must include:

- branch/status preflight;
- exact target sample list;
- exact official EID request URLs;
- HTTP status, content type, content length and redirect locations;
- matched metadata: fund code, fund name, fund id, report year, report type/description, send date, instance id/upload id;
- PDF byte-size and SHA-256 if PDF bytes are downloaded;
- local output path only if the gate authorizes writing downloaded artifacts;
- final per-sample classification:
  - `eid_acquired`;
  - `eid_metadata_matched_no_download`;
  - `eid_not_found`;
  - `eid_identity_mismatch`;
  - `eid_unavailable`;
  - `eid_schema_drift`;
  - `eid_integrity_error`;
  - `blocked_auth_or_captcha`;
  - `replace_required`;
- blocked claims and residuals;
- `git diff --check` result.

## 7. Execution Write Policy

The later execution gate has two possible modes. Controller must choose one before execution:

| Mode | Writes allowed | Use case |
|---|---|---|
| `metadata_only` | evidence artifact only; no PDF/cache writes | If the goal is only to prove EID existence/identity. |
| `artifact_capture` | evidence artifact plus explicit `cache/pdf/<fund>_<year>_annual_report_eid.pdf` writes for missing active samples | If the goal is to make samples available for later pdfplumber export planning. |

Default recommendation: `metadata_only` first if there is uncertainty about endpoint behavior. Use `artifact_capture` only after metadata match rules are accepted.

These modes are mutually exclusive at the gate level:

- `Bounded EID-only Sample Acquisition Metadata Evidence Gate` may request EID metadata and headers only. It must not download PDF bytes, compute PDF hashes from response bodies, or write cache files.
- `Bounded EID-only Sample Acquisition Artifact Capture Evidence Gate` requires separate explicit live/network/PDF write authorization and may download bytes only for samples that pass the exact identity match rules above.

## 8. Review Checklist

Reviewers must check:

- Does the plan preserve EID single-source/no-fallback?
- Does it avoid treating CNINFO/fund-company/manual metadata as acceptable sample source?
- Does it separate planning from live/network/PDF execution?
- Does it require exact identity matching before artifact capture?
- Does it keep S2/S3 as controller decisions rather than forcing unnecessary live work?
- Does it define replacement rules without fallback?
- Does it preserve `NOT_READY` and candidate-only Docling status?

## 9. Stop Conditions

Stop before execution if:

- any worker proposes CNINFO, fund-company, Eastmoney, akshare or local non-EID PDF fallback;
- annual report type code cannot be pinned to an accepted EID report family;
- a target sample cannot be matched by exact fund code, report year and annual report type;
- execution would require PDF body parsing, Docling conversion, pdfplumber export, provider/LLM or analysis commands;
- downloaded bytes cannot be integrity-checked when artifact capture is requested;
- the next gate would change `FundDocumentRepository` behavior or source policy.

## 10. Validation

Planning validation:

```text
git diff --check
```

## 11. Next Gate Recommendation

Immediate next gate:

`Bounded EID-only Sample Acquisition Plan Review Gate`

If accepted, route to one of:

1. `Bounded EID-only Sample Acquisition Metadata Evidence Gate` with later explicit live/network authorization; or
2. `Bounded EID-only Sample Acquisition Artifact Capture Evidence Gate` with later explicit live/network/PDF write authorization.

Do not proceed directly to pdfplumber export, Docling conversion, field correctness or production integration.

## 12. Final Verdict

`VERDICT: READY_FOR_PLAN_REVIEW_NOT_READY`
