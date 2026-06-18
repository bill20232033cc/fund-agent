# Docling Baseline Qualification Local Artifact Provenance Status Evidence Controller Judgment - 2026-06-15

Gate: `Docling Baseline Qualification Local Artifact Provenance Status Evidence Gate`
Role: controller
Readiness state: `NOT_READY`

## 1. Scope

This judgment closes Gate 0A for Docling baseline qualification. It accepts metadata-only local artifact provenance/status evidence and decides the next gate.

This judgment does not authorize Docling conversion, EID acquisition, live/network/PDF/FDR, pdfplumber export, manual reference review, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, production parser replacement, `FundDocumentRepository` behavior change, source policy change, non-EID fallback, field correctness claim, source-truth claim, raw XML/XBRL claim, taxonomy compatibility claim, push or PR.

## 2. Artifacts Reviewed

- Evidence: `docs/reviews/docling-baseline-qualification-local-artifact-provenance-status-evidence-20260615.md`
- DS backup review: `docs/reviews/docling-baseline-qualification-local-artifact-provenance-status-evidence-review-ds-20260615.md`
- MiMo review: `docs/reviews/docling-baseline-qualification-local-artifact-provenance-status-evidence-review-mimo-20260615.md`
- Accepted plan judgment: `docs/reviews/docling-baseline-qualification-acquisition-status-plan-controller-judgment-20260615.md`
- Current control docs: `docs/current-startup-packet.md`, `docs/implementation-control.md`

Process note: the originally assigned DS channel returned a completed status without review body. Controller treated that as a review-channel residual and obtained an independent DS-backup review before accepting this gate.

## 3. Accepted Evidence Facts

| Sample | Controller disposition | Accepted scope |
|---|---|---|
| S1 `004393 / 2025` | ACCEPT | Accepted tri-route representation seed: Docling, pdfplumber and EID HTML render full JSONs exist and remain representation evidence only. |
| S2 `004393 / 2024` | ACCEPT_AS_LOCAL_EID_CANDIDATE_FOR_NEXT_DECISION | Local EID-labeled PDF/parsed cache, manual EID URL/id and provided SHA-256 metadata align. No PDF body/hash verification occurred in this gate. |
| S3 `004194 / 2024` | ACCEPT_AS_LOCAL_EID_CANDIDATE_WITH_HASH_GAP | Local EID-labeled PDF/parsed cache and manual EID URL/id align, but no hash is provided. Controller decision or follow-up provenance evidence is required before active use. |
| S4 `006597 / 2024` | ACCEPT_PROVENANCE_CONFLICT | Local filename has `_eid`, but accepted manual metadata points to CNINFO and states EID document id unknown. Filename alone is not EID provenance. |
| S5 `017641 / 2024` | ACCEPT_NON_EID_LOCAL_METADATA | Local PDF and manual metadata are fund-company source, not EID-controlled. |
| S6 `110020 / 2024` | ACCEPT_NON_EID_LOCAL_METADATA | Local PDF and manual metadata are fund-company source, not EID-controlled. |

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| Evidence is metadata-only; no PDF body/parser/repository/live/conversion/export commands. | DS backup / MiMo | ACCEPT | Closed. |
| Local file visibility is not accepted provenance. | DS backup / MiMo | ACCEPT | Closed. |
| S4 `_eid` filename conflicts with manual CNINFO/EID-id-unknown metadata. | DS backup / MiMo | ACCEPT | Closed; S4 cannot be accepted as EID-controlled from filename. |
| S5/S6 must go to bounded EID-only acquisition or replacement. | DS backup / MiMo | ACCEPT | Closed. |
| No fallback, field correctness, source truth or readiness claim is made. | DS backup / MiMo | ACCEPT | Closed. |
| Next gate should be controller decision/review before acquisition/export/conversion. | DS backup / MiMo | ACCEPT | Closed. |

No blocking finding remains.

## 5. Blocked Claims

The following remain blocked:

- S2-S6 are accepted baseline qualification active samples;
- S4 local `_eid` filename proves EID provenance;
- S5/S6 local PDFs are usable under EID single-source policy;
- non-EID fallback is allowed;
- pdfplumber full representation JSON exists for S2-S6;
- Docling full representation JSON exists for S2-S6;
- EID HTML render is available for S2-S6;
- field correctness is proven;
- source truth is proven;
- raw XML / raw XBRL direct download is proven;
- taxonomy compatibility is proven;
- readiness/release/PR readiness.

## 6. Residuals

| Residual | Owner | Next handling |
|---|---|---|
| S2 provenance has metadata alignment but still no current-gate PDF body/hash verification. | Controller / Fund documents source owner | Can be accepted as local EID candidate for later pdfplumber export planning if controller accepts metadata-only threshold, or verified in a follow-up provenance gate. |
| S3 hash is missing. | Controller / Fund documents source owner | Decide whether EID URL/id plus `_eid` local cache is enough for candidate export planning, or require bounded hash/provenance evidence. |
| S4 provenance conflict. | Controller / Fund documents source owner | Do not use local artifact as EID-controlled unless a follow-up controller provenance decision resolves conflict; otherwise bounded EID-only acquisition or replacement. |
| S5/S6 non-EID metadata. | Controller / Fund documents source owner | Bounded EID-only acquisition or profile-preserving replacement. |
| Original DS channel produced no body. | Controller / agent channel owner | Process residual; independent DS-backup and MiMo reviews are accepted. |
| `AGENTS.md` remains modified but rejected by rules-sync review. | Rules owner / controller | Separate rules-sync rewrite gate; do not stage current diff. |

## 7. Next Gate

Primary next gate:

`Bounded EID-only Sample Acquisition Planning Gate`

Purpose:

- decide how to resolve S4-S6 and any controller-selected S2/S3 provenance gap without non-EID fallback;
- define exact sample rows, official EID lookup/download metadata, allowed live/network boundaries if execution is later authorized, stop rules and replacement criteria;
- preserve current `NOT_READY` and candidate-only Docling status.

This next gate is planning-only. It must not execute live/network/PDF/FDR acquisition unless a later bounded evidence execution gate is explicitly opened.

Deferred until after sample provenance is resolved:

- pdfplumber full representation export planning/execution for active samples;
- Docling conversion/runtime containment for S2-S6;
- same-report reference fact coverage;
- EID HTML render availability evidence for S2-S6;
- field correctness comparison;
- production integration.

## 8. Validation

Required validation:

```text
git diff --check
```

Controller result: passed after evidence, reviews and this judgment were written.

## 9. Final Verdict

`VERDICT: ACCEPT_LOCAL_ARTIFACT_STATUS_WITH_PROVENANCE_GAPS_READY_FOR_BOUNDED_EID_ONLY_ACQUISITION_PLANNING_NOT_READY`
