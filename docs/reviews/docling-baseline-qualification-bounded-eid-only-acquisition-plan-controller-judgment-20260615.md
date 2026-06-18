# Docling Baseline Qualification Bounded EID-only Acquisition Plan Controller Judgment - 2026-06-15

Gate: `Bounded EID-only Sample Acquisition Planning Gate`
Role: controller
Readiness state: `NOT_READY`

## 1. Scope

This judgment closes the bounded EID-only acquisition planning gate. It accepts the plan and routes the next gate, but does not execute live/network/PDF/FDR acquisition.

This judgment does not authorize EID/network/FDR/PDF acquisition, PDF body reads, PDF downloads, PDF hash computation from response bodies, cache writes, `FundDocumentRepository` execution, Docling conversion, pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, production parser replacement, source policy change, non-EID fallback, push or PR.

## 2. Artifacts Reviewed

- Plan: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-plan-20260615.md`
- DS review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-plan-review-ds-20260615.md`
- MiMo review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-plan-review-mimo-20260615.md`
- Prior controller judgment: `docs/reviews/docling-baseline-qualification-local-artifact-provenance-status-evidence-controller-judgment-20260615.md`
- Current control docs: `docs/current-startup-packet.md`, `docs/implementation-control.md`

## 3. Accepted Plan Facts

| Fact | Controller disposition |
|---|---|
| S1 requires no acquisition. | ACCEPT |
| S2 can be carried as metadata-only local EID candidate for later export planning, without source-truth or field-correctness claim. | ACCEPT_WITH_RESIDUAL |
| S3 can be carried as metadata-only local EID candidate with hash residual, or included in optional bounded metadata evidence. | ACCEPT_WITH_RESIDUAL |
| S4 cannot be accepted from `_eid` filename because manual metadata points to CNINFO and EID id is unknown. | ACCEPT |
| S5/S6 cannot use current local non-EID PDFs; they require EID-only metadata evidence and possibly replacement. | ACCEPT |
| Non-EID fallback is forbidden. | ACCEPT |
| Replacement is profile-preserving and must be reviewed; no silent substitution. | ACCEPT |
| Metadata-only and artifact-capture modes are mutually exclusive. | ACCEPT_WITH_BINDING_AMENDMENT |
| Exact identity match rules must be satisfied before artifact capture. | ACCEPT_WITH_BINDING_AMENDMENT |

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| Plan preserves planning-only boundary. | DS / MiMo | ACCEPT | Closed. |
| Plan preserves EID single-source/no-fallback. | DS / MiMo | ACCEPT | Closed. |
| S2/S3/S4/S5/S6 routing is correct. | DS / MiMo | ACCEPT | Closed. |
| Exact identity match should be formalized. | DS | ACCEPT_AS_REQUIRED_FIX | Closed by plan §4.4. |
| `metadata_only` and `artifact_capture` should be mutually exclusive. | DS / MiMo | ACCEPT_AS_REQUIRED_FIX | Closed by plan §7. |
| Next gate should prefer metadata-only; artifact capture requires separate explicit authorization. | MiMo | ACCEPT_AS_BINDING_AMENDMENT | Applied in next gate decision. |

No blocking finding remains.

## 5. Blocked Claims

The following remain blocked:

- EID acquisition succeeded;
- S4-S6 are accepted EID-controlled active samples;
- PDF bytes/hash/content are verified;
- local non-EID PDFs are acceptable;
- any CNINFO/fund-company/Eastmoney/akshare fallback is allowed;
- pdfplumber export may proceed;
- Docling conversion may proceed;
- field correctness/source truth/taxonomy/raw XML/readiness is proven;
- production parser or repository behavior may change.

## 6. Next Gate

Primary next gate:

`Bounded EID-only Sample Acquisition Metadata Evidence Gate`

Purpose:

- metadata-only EID lookup for required target set S4/S5/S6 and optional S3;
- classify each target as `eid_metadata_matched_no_download`, `identity_partly_matched`, `eid_not_found`, `eid_identity_mismatch`, `eid_unavailable`, `eid_schema_drift`, `blocked_auth_or_captcha`, or `replace_required`;
- preserve no-fallback and `NOT_READY`;
- produce evidence for deciding whether artifact-capture execution is needed or whether replacement planning is required.

Allowed only after explicit live/network authorization:

- official EID metadata/search requests;
- HTTP status/content-type/content-length/redirect metadata;
- no PDF body download;
- no PDF hash from response bodies;
- no cache writes.

Still not authorized:

- `Artifact Capture Evidence Gate`;
- PDF download/write/hash;
- pdfplumber export;
- Docling conversion;
- field correctness comparison;
- production integration.

## 7. Validation

Required validation:

```text
git diff --check
```

Controller result: passed after plan, reviews and this judgment were written.

## 8. Final Verdict

`VERDICT: ACCEPT_PLAN_READY_FOR_BOUNDED_EID_ONLY_METADATA_EVIDENCE_GATE_NOT_READY`
