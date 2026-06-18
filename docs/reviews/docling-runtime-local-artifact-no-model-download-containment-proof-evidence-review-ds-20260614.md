# Docling Runtime Local Artifact / No-model-download Containment Proof Evidence Review (DS) - 2026-06-15

Status: `REVIEW_COMPLETE`
Role: AgentDS review; not controller; not evidence worker
Review target: `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md`

## 1. Review Scope

This review assesses only whether the evidence artifact under test supports its own verdict `CONTAINMENT_NOT_PROVEN_BLOCKED_NOT_READY` and whether it meets the review focus items specified by the gate. The review does not re-execute commands, re-inspect local packages, or run any conversion/network/EID/FDR/PDF/pdfplumber/provider/LLM/readiness/release/PR/push/merge command.

Inputs read:
- `AGENTS.md`
- `docs/design.md` (Docling/current route sections only)
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md`
- `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md`

## 2. Final Verdict

```text
VERDICT: PASS
```

## 3. Findings Table

| # | Finding | Severity | Disposition |
|---|---|---|---|
| F1 | Evidence correctly proves table bypass (`do_table_structure=False`) is partial: `BaseTableStructureModel.__call__()` yields pages unchanged when disabled, but this does not disable layout. | Info | Accepted. The partial-bypass classification is source-backed. |
| F2 | Evidence correctly proves layout remains model-backed: `StandardPdfPipeline._init_models()` always creates `self.layout_model`; no `do_layout`/`enabled` switch exists on `BaseLayoutModel`; `PageAssembleModel` requires `page.predictions.layout`. | Info | Accepted. The layout-blocker reasoning is sound. |
| F3 | Evidence correctly proves `artifacts_path=None` leads to `download_hf_model()` → `huggingface_hub.snapshot_download()` for the layout model path `docling-project/docling-layout-heron`. | Info | Accepted. The remote-download path is source-backed. |
| F4 | Evidence correctly classifies RapidOCR residual files as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` and does not treat them as layout/table containment proof. | Info | Accepted. The residual classification is conservative and correct. |
| F5 | Evidence correctly proves `force_backend_text=True` does not bypass layout: the standard pipeline still initializes and executes layout, and assembly requires `page.predictions.layout`. | Info | Accepted. `force_backend_text` is a text-detection option, not a layout-disable switch. |
| F6 | Evidence correctly inventories local package artifact files (no `.onnx`, `.safetensors`, `.pt`, `.pth`, `.bin`, `.ckpt` in Docling package dirs) and rejects accepted local artifact proof. | Info | Accepted. The inventory is thorough and the conclusion follows. |
| F7 | Evidence correctly preserves `NOT_READY` and does not claim source truth, raw XML availability, field correctness, taxonomy compatibility, or parser replacement. | Info | Accepted. All scope boundaries are respected. |
| F8 | Evidence correctly records that no conversion, EID HTTP, repository/FDR PDF acquisition, PDF body read, pdfplumber run, provider/LLM, analyze/checklist, readiness/release/PR/push/merge command was executed. | Info | Accepted. Command log and intentionally-not-executed list are complete. |
| F9 | Evidence correctly rejects socket-blocked conversion eligibility because containment is not proven. | Info | Accepted. The decision follows from the blocking findings. |
| F10 | Evidence artifact reads two additional files beyond the explicit six-input list: `docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md` (the setup evidence) and local Docling package source files. | Non-blocking | Accepted. The setup evidence is the immediate predecessor artifact and reading it is appropriate context. Package source inspection is the core evidence-gathering method for this gate. Neither expands implementation or runtime scope. |

## 4. Accepted Facts

| Fact | Review disposition |
|---|---|
| Docling 2.93.0 is installed and importable (`docling_version=2.93.0`, `docling_slim_version=2.93.0`, `docling_ibm_models_version=3.13.2`). | Accepted as local package fact. |
| `do_ocr=False` disables OCR model execution but does not affect layout. | Accepted. OCR bypass is correct but insufficient. |
| `do_table_structure=False` causes `BaseTableStructureModel.__call__()` to yield pages unchanged. | Accepted. Table-structure bypass is correct for the configured path but does not affect layout. |
| Standard PDF pipeline stages: `preprocess -> ocr -> layout -> table -> assemble -> reading_order`. | Accepted. Source-backed. |
| Layout model path: `docling-project/docling-layout-heron`, `revision=main`, `model_path=''`, `artifacts_path=None`. | Accepted from local introspection. |
| When `artifacts_path=None`, `LayoutModel.__init__()` calls `self.download_models()` which calls `download_hf_model()` which calls `huggingface_hub.snapshot_download()`. | Accepted. Source-backed from `layout_model.py`, `base_factory.py`, `hf_model_download.py`. |
| No `do_layout=False` or layout disable switch exists in the standard PDF pipeline path inspected. | Accepted. Source-backed. |
| `PageAssembleModel.__call__()` requires `page.predictions.layout is not None`. | Accepted. Source-backed. |
| No bundled Docling layout/table weight/config artifacts (`.onnx`, `.safetensors`, `.pt`, `.pth`, `.bin`, `.ckpt`) were observed under `.venv` Docling package dirs. | Accepted as local artifact inventory fact. |
| `enable_remote_services=False` prevents remote service/API model calls but does not disable HuggingFace artifact lookup/download. | Accepted. The guardrail is correctly classified as insufficient. |
| RapidOCR residual files exist but are not accepted as Docling layout/table containment proof. | Accepted. Conservative classification. |
| No conversion, EID HTTP, repository/FDR PDF acquisition, PDF body read, pdfplumber, provider/LLM, analyze/checklist, readiness/release/PR/push/merge command was executed. | Accepted. Verified against command log. |
| Release/readiness remains `NOT_READY`. No source truth, raw XML, field correctness, taxonomy compatibility, or parser replacement claim is made. | Accepted. Scope boundaries respected. |

## 5. Blocked Claims (Reviewed and Confirmed)

| Claim | Review disposition |
|---|---|
| Layout no-model bypass | Confirmed blocked. Source evidence is sufficient. |
| Accepted local layout artifact | Confirmed blocked. No artifact root found; `artifacts_path=None` leads to remote download. |
| Accepted local table artifact (if enabled) | Confirmed blocked for default path. Not needed if `do_table_structure=False` is accepted, but that is only a partial bypass. |
| No-download containment for standard PDF conversion | Confirmed blocked. Layout path remains model-backed. |
| Socket-blocked conversion gate eligibility | Confirmed blocked. Conversion would violate current gate stop condition. |
| RapidOCR as accepted containment | Confirmed rejected. Correctly classified as residual. |

## 6. Residuals

| Residual | Review disposition |
|---|---|
| `docling_layout_local_artifact_unproven` | Retained as blocking. Correctly identifies that a later gate needs explicit accepted `artifacts_path` with provenance. |
| `docling_layout_no_model_bypass_unproven` | Retained as blocking. Correctly identifies that no source-supported layout-disable path exists in the standard pipeline. |
| `docling_table_artifact_unproven_if_enabled` | Retained. Correct conditional. |
| `docling_table_bypass_only_partial` | Retained. Correctly notes that disabling tables reduces reconstruction quality and does not solve layout. |
| `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` | Retained. Correct conservative classification. |
| `socket_blocked_conversion_not_authorized` | Retained. Correctly blocks conversion until containment proof. |
| `same_report_comparison_not_reopened` | Retained. No comparison was attempted. |
| `not_raw_xml_download_proof` | Retained. Correct scope preservation. |
| `not_field_correctness_proof` | Retained. Correct scope preservation. |
| `not_taxonomy_compatibility_proof` | Retained. Correct scope preservation. |
| `not_source_truth` | Retained. Correct scope preservation. |
| `not_readiness_proof` | Retained. Correct scope preservation. |

## 7. Review Rationale

The evidence artifact is methodical and complete within its declared scope. It correctly:

1. **Proves the blocker**: The standard PDF pipeline always instantiates and executes a model-backed layout stage. No `do_layout` disable switch exists. `artifacts_path=None` leads to `huggingface_hub.snapshot_download()` for `docling-project/docling-layout-heron`. `PageAssembleModel` depends on layout predictions. No bundled layout weights/config were found in the installed package directories.

2. **Correctly classifies partial bypasses**: `do_ocr=False` and `do_table_structure=False` are valid bypasses for their respective stages, but they do not remove the layout blocker. `force_backend_text=True` is a text-detection option, not a layout bypass.

3. **Respects all scope boundaries**: No conversion was run. No forbidden command was executed. `NOT_READY` is preserved throughout. No source truth, raw XML, field correctness, taxonomy compatibility, or parser replacement claims are made.

4. **Maintains proper residual classification**: RapidOCR files remain classified as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`. All residuals carry appropriate status and next-step guidance.

The source-code analysis chain (lines 177-233 of the evidence) is the strongest section: it traces from `StandardPdfPipeline` through `_init_models()`, `BaseLayoutModel`, `LayoutModel.__init__()`, `download_models()`, `download_hf_model()`, and `hf_model_download.py` to establish the remote-download path. The table-model analysis covers three alternative table paths (TableFormer v1, TableStructureModelV2, GraniteVision) and correctly notes all are model-backed when not disabled.

No blocking defect, omission, or overclaim was found.

## 8. Recommendation

The evidence artifact is sound. The verdict `CONTAINMENT_NOT_PROVEN_BLOCKED_NOT_READY` is fully supported. The gate should remain blocked.

Next route options:
- A later gate could attempt to configure an explicit `artifacts_path` with pre-downloaded layout model artifacts and prove no-download behavior.
- A later gate could explore a non-standard Docling pipeline path that does not use model-backed layout (if one exists and is documented).
- The route could remain blocked indefinitely if neither option proves viable, keeping Docling as a deferred benchmark candidate only.

No conversion should be authorized until accepted local layout artifact proof or a verified no-model layout path is established in a subsequent gate.

Completion status:

```text
artifact_path=docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-review-ds-20260614.md
verdict=PASS
```
