# Docling Runtime Local Artifact / No-model-download Containment Proof Controller Judgment - 2026-06-14

Status: `CONTROLLER_JUDGMENT_COMPLETE`
Gate: `Docling Runtime Local Artifact / No-model-download Containment Proof Gate`
Controller role: AgentController
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the local artifact / no-model-download containment proof gate for the installed Docling runtime.

The gate was allowed to inspect local package/source/artifact state and decide whether a later socket-blocked Docling conversion gate was eligible. It was not allowed to run EID HTTP, repository/FDR PDF acquisition, PDF body reads, pdfplumber, Docling conversion, provider/LLM, analyze/checklist, readiness/release/PR/push/merge commands, dependency install, production parser changes, cleanup or source policy changes.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- Prior setup evidence controller judgment: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md`
- Evidence artifact: `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md`
- DS review: `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-review-ds-20260614.md`
- MiMo review: `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-review-mimo-20260614.md`

## 3. Accepted Current Facts

| Fact | Controller disposition |
|---|---|
| Docling `2.93.0`, `docling_slim 2.93.0` and `docling_ibm_models 3.13.2` are installed and importable. | Accepted as local package fact only. |
| `do_ocr=False` disables OCR execution. | Accepted as OCR-only bypass; not sufficient for containment. |
| `do_table_structure=False` bypasses table-structure execution in the inspected standard PDF path. | Accepted as partial table bypass; not sufficient because layout remains model-backed. |
| Standard PDF pipeline stages include `preprocess -> ocr -> layout -> table -> assemble -> reading_order`. | Accepted. |
| Standard PDF pipeline creates and uses a model-backed layout stage; no accepted `do_layout=False` or equivalent layout-disable switch was found. | Accepted as the primary blocker. |
| Assembly depends on layout predictions. | Accepted; standard conversion cannot be treated as model-free when layout is unresolved. |
| `artifacts_path=None` plus Docling layout defaults lead to `download_hf_model()` / `huggingface_hub.snapshot_download()` for `docling-project/docling-layout-heron` when local artifacts are not supplied. | Accepted as no-download containment blocker. |
| No bundled Docling layout/table weight/config artifacts were observed under the inspected installed package directories. | Accepted as local inventory fact; not a global proof about every possible external artifact location. |
| RapidOCR residual files exist. | Accepted only as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`. |
| No conversion, network, EID, FDR/PDF, pdfplumber, provider/LLM, readiness/release/PR command was executed. | Accepted. |
| Release/readiness remains `NOT_READY`; no source truth, raw XML, field correctness, taxonomy compatibility or parser replacement claim was made. | Accepted. |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentDS | `PASS` | Accepted. No blocker finding. |
| AgentMiMo | `PASS` | Accepted. No blocker finding. |

Reviewer observations are accepted as non-blocking confirmations:

- table bypass is partial and does not remove layout containment risk;
- local package inventory is sufficient to reject current installed-package artifact proof;
- `enable_remote_services=False` and `allow_external_plugins=False` are insufficient against HuggingFace artifact lookup/download in local model stages;
- `socket_blocked_conversion_eligible=false` follows from the accepted blocker.

## 5. Blocked Claims

| Claim | Controller decision |
|---|---|
| Docling standard PDF conversion is no-download contained in the current local environment. | Rejected / blocked. |
| Current local install contains accepted Docling layout artifact proof. | Rejected / blocked. |
| A model-free standard Docling PDF path is proven. | Rejected / blocked. |
| Socket-blocked conversion is eligible now. | Rejected / blocked. |
| Docling can enter same-report quality comparison now. | Rejected / blocked. |
| Docling can replace or augment production parser now. | Rejected / blocked. |
| EID HTML render, raw XML, field correctness, taxonomy compatibility or source truth is affected by this gate. | Rejected. |
| Release/readiness can move from `NOT_READY`. | Rejected. |

## 6. Residuals

| Residual | Status | Next handling |
|---|---|---|
| `docling_layout_local_artifact_unproven` | blocking | Requires explicit user/controller decision to acquire, accept, and provenance-check local layout artifacts before any conversion. |
| `docling_layout_no_model_bypass_unproven` | blocking | Requires a separate research/design gate for a non-standard model-free Docling path, if pursued. |
| `docling_table_artifact_unproven_if_enabled` | retained | Table may remain disabled for a future experiment, but that reduces table reconstruction and does not solve layout. |
| `socket_blocked_conversion_not_authorized` | blocking | Conversion remains forbidden. |
| `same_report_comparison_not_reopened` | retained | Same-report comparison cannot include Docling until containment is accepted. |
| `eid_xbrl_html_render_candidate` | retained | Candidate route remains separate and is not upgraded or downgraded by Docling runtime evidence. |
| `not_raw_xml_download_proof` / `not_field_correctness_proof` / `not_taxonomy_compatibility_proof` / `not_source_truth` / `not_readiness_proof` | retained | No proof in this gate. |

## 7. Final Verdict

```text
VERDICT: ACCEPT_EVIDENCE_CONTAINMENT_NOT_PROVEN_BLOCKED_NOT_READY
```

Rationale:

- Evidence and both independent reviews support `CONTAINMENT_NOT_PROVEN_BLOCKED_NOT_READY`.
- The blocker is not a transient test failure; it is a source-backed containment constraint in the installed standard PDF pipeline.
- Continuing directly to conversion or same-report benchmark would violate the accepted stop condition.
- Repeating this gate without a new local artifact source or a new model-free path is low value and risks the same loop the current route is intended to avoid.

## 8. Next Recommended Gate

Recommended next gate:

```text
Docling Blocked Route Disposition And EID HTML Priority Reconciliation Gate
```

Purpose:

- formally mark the current Docling standard PDF route as blocked for no-download containment in this local environment;
- route Docling to a deferred candidate unless the user explicitly authorizes local model artifact acquisition/provenance or a non-standard model-free pipeline research gate;
- return the main structured-disclosure route to `eid_xbrl_html_render_candidate` and current pdfplumber/FundDocumentRepository boundaries without claiming field correctness, source truth or readiness;
- define the next evidence path that can proceed without Docling conversion.

Deferred entries:

- `Docling Local Model Artifact Acquisition / Provenance Gate` - requires explicit authorization because it may involve model artifact acquisition and provenance review.
- `Docling Non-standard Model-free Pipeline Research Gate` - design/research only unless later accepted.
- `Socket-blocked Docling Conversion Gate` - blocked until containment is accepted.
- `Same-report Route Quality Comparison Gate` - may proceed without Docling only if controller explicitly narrows comparison to EID HTML render candidate vs current pdfplumber/FundDocumentRepository evidence.
- Production parser implementation, parser replacement, source policy change, readiness/release/PR remain deferred.

## 9. Control-doc Update Recommendation

Update `docs/current-startup-packet.md` and `docs/implementation-control.md` to record:

- current Docling no-download containment proof is accepted as blocked;
- conversion and Docling same-report benchmark remain unauthorized;
- next mainline is `Docling Blocked Route Disposition And EID HTML Priority Reconciliation Gate`;
- release/readiness remains `NOT_READY`.
