# Docling Runtime Local Artifact / No-model-download Containment Proof Evidence Review (MiMo) - 2026-06-14

Status: `REVIEW_COMPLETE`
Reviewer role: AgentMiMo
Gate: `Docling Runtime Local Artifact / No-model-download Containment Proof Gate`
Review artifact under test: `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md`

## 1. Review Scope

This review evaluates whether the evidence artifact correctly proves or fails closed on Docling local artifact/no-model-download containment for layout/table stages before any conversion. Read-only scope per gate constraint.

Inputs read:

1. `AGENTS.md`
2. `docs/design.md` (sections relevant to Docling/current route)
3. `docs/current-startup-packet.md`
4. `docs/implementation-control.md` (first 200 lines + current gate section)
5. `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md`
6. `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md`

## 2. Verdict

```text
VERDICT: PASS
```

## 3. Review Findings

| # | Finding | Category | Severity | Disposition |
|---|---------|----------|----------|-------------|
| F1 | Evidence correctly identifies that `do_table_structure=False` bypasses table-structure execution but layout remains model-backed. The two-stage bypass is accurately described as partial. | Correctness | None (correct) | Accepted. Table bypass is partial; layout blocker is correctly identified as the remaining containment gap. |
| F2 | Local artifact inventory scanned `.venv` Docling/docling_ibm_models directories at maxdepth 10 for `*.onnx`, `*.safetensors`, `*.pt`, `*.pth`, `*.bin`, `*.ckpt`, `*.json` and found zero bundled layout/table weight/config artifacts. | Completeness | None (sufficient) | Accepted. The inventory depth and file-pattern coverage are sufficient to reject the claim that accepted local layout/table artifacts exist in the installed package. |
| F3 | RapidOCR residual files are correctly classified as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` and not accepted as layout/table containment proof. | Correctness | None (correct) | Accepted. OCR model residuals do not substitute for layout/table model artifacts. |
| F4 | Source-level analysis of `StandardPdfPipeline._init_models()` confirms layout model is always created; `BaseLayoutModel.__call__()` has no `enabled` pass-through; `PageAssembleModel` asserts `page.predictions.layout is not None`. This proves standard PDF pipeline cannot operate without layout. | Correctness | None (correct) | Accepted. The source chain `_init_models -> always creates layout_model -> no enabled bypass -> assembly requires layout` is a correct containment-blocker proof. |
| F5 | Guardrail assessment correctly rejects `enable_remote_services=False` and `allow_external_plugins=False` as sufficient containment proof. `enable_remote_services` only prevents configured remote service/API model calls, not HuggingFace artifact download for local model stages. | Correctness | None (correct) | Accepted. These guardrails do not prevent `snapshot_download()` for layout artifacts. |
| F6 | No EID HTTP, repository/FDR PDF acquisition, pdfplumber parser run, Docling conversion, provider/LLM, analyze/checklist, readiness/release/PR/push/merge, dependency install, or cache cleanup commands were executed. | Scope compliance | None (compliant) | Accepted. The command list and "intentionally not executed" section confirm full gate scope compliance. |
| F7 | Evidence preserves `NOT_READY` throughout and makes no claims of source truth, raw XML availability, field correctness, taxonomy compatibility, parser replacement, or `FundDocumentRepository` behavior change. | Boundary compliance | None (compliant) | Accepted. All blocked/retained proofs table entries correctly maintain NOT_READY status. |
| F8 | The `artifacts_path=None` default combined with `LayoutModel.__init__()` calling `download_hf_model()` -> `snapshot_download()` when `artifacts_path is None` is the key containment-blocker chain. Evidence correctly traces this through three source files. | Correctness | None (correct) | Accepted. This is the critical source-level proof that standard PDF layout will attempt remote download when no local artifact path is configured. |
| F9 | Evidence does not explore non-standard pipeline paths (e.g., custom pipeline subclassing, `EccentricPdfPipeline`, or manual model-free pipeline construction). The review scope was standard PDF pipeline only. | Scope limitation | Info | Non-blocking. The gate correctly scoped to the standard PDF pipeline. Non-standard paths would require separate authorization and are not needed to prove the current blocker. |

## 4. Accepted Facts

| Fact | Evidence basis | Reviewer disposition |
|---|---|---|
| Docling `2.93.0` / `docling_ibm_models` `3.13.2` installed and importable. | Local introspection output. | Accepted as local package fact. |
| `artifacts_path=None` is the default; no `artifacts_path` was configured or proven. | Source code `PipelineOptions` field default + local introspection `artifacts_path=None`. | Accepted. This is the root cause of the containment blocker. |
| `do_ocr=False` disables OCR execution. | Source code `StandardPdfPipeline._make_ocr_model(... enabled=self.pipeline_options.do_ocr ...)`. | Accepted as OCR-only bypass. |
| `do_table_structure=False` bypasses table-structure model execution. | Source code `BaseTableStructureModel.__call__()` yields pages unchanged when `enabled=False`. | Accepted as table-structure execution bypass. |
| Layout model is always created in `StandardPdfPipeline._init_models()` and has no `enabled` pass-through. | Source code analysis of `_init_models()` and `BaseLayoutModel`. | Accepted as layout containment blocker. |
| `PageAssembleModel` requires `page.predictions.layout is not None`. | Source code `PageAssembleModel.__call__()`. | Accepted as assembly dependency on layout. |
| `LayoutModel.download_models()` calls `download_hf_model()` which calls `huggingface_hub.snapshot_download()`. | Source code chain in `layout_model.py` -> `hf_model_download.py`. | Accepted. Remote download path exists when artifacts are missing. |
| No bundled layout/table weight/config artifact files found in `.venv` Docling package directories. | `find` at maxdepth 10 for `*.onnx`, `*.safetensors`, `*.pt`, `*.pth`, `*.bin`, `*.ckpt`, `*.json`. | Accepted. No local artifact proof. |
| RapidOCR residual files exist but are classified as not-promoted prior incident residual. | File inventory of `rapidocr/models/`. | Accepted. Not layout/table containment proof. |
| `socket_blocked_conversion_eligible=false` is correctly derived from the above facts. | Decision logic in evidence. | Accepted. Conversion correctly blocked. |

## 5. Blocked Claims Verification

| Claim | Evidence status | Reviewer verification |
|---|---|---|
| Layout no-model bypass | Blocked | Correct. No `do_layout=False` or equivalent switch exists in standard PDF pipeline. |
| Accepted local layout artifact | Blocked | Correct. `artifacts_path=None`, no bundled weights, `snapshot_download()` path exists. |
| Accepted local table artifact | Not needed if disabled; otherwise blocked | Correct. Table can be disabled, but default path downloads. |
| No-download containment for standard PDF | Blocked | Correct. Layout path remains model-backed. |
| Socket-blocked conversion eligibility | Blocked | Correct. Cannot convert without containment proof. |

## 6. Residual Verification

All residuals are correctly classified:

- `docling_layout_local_artifact_unproven` (blocking) - correct
- `docling_layout_no_model_bypass_unproven` (blocking) - correct
- `docling_table_artifact_unproven_if_enabled` (retained) - correct
- `docling_table_bypass_only_partial` (retained) - correct
- `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` (retained) - correct
- `socket_blocked_conversion_not_authorized` (blocking) - correct
- `same_report_comparison_not_reopened` (retained) - correct
- `not_raw_xml_download_proof` (retained) - correct
- `not_field_correctness_proof` (retained) - correct
- `not_taxonomy_compatibility_proof` (retained) - correct
- `not_source_truth` (retained) - correct
- `not_readiness_proof` (retained) - correct

## 7. Next Route Assessment

The evidence correctly concludes that the next step is NOT same-report comparison, production implementation, or Docling conversion. The two blocking residuals (`docling_layout_local_artifact_unproven`, `docling_layout_no_model_bypass_unproven`) must be resolved before any conversion gate.

Recommended next gate remains:

```text
Docling Runtime Local Artifact / No-model-download Containment Proof Gate (continued)
```

Minimum objectives for continuation:
- Either locate/accept a pre-downloaded `artifacts_path` containing the required layout repo folder with provenance and no-download proof;
- Or prove a source-supported standard PDF path that does not instantiate/execute model-backed layout (e.g., a non-standard pipeline or layout-disabled subclass);
- Or decide that the Docling standard PDF path is permanently blocked for no-model containment and route to alternative candidates (HTML render, pdfplumber-only, or hybrid).

The gate should remain **blocked** until one of these containment strategies is proven. Moving to a conversion gate without containment proof would violate the stop condition established by the prior controller judgment.

## 8. Control-doc Consistency

The evidence artifact is consistent with:
- `docs/current-startup-packet.md` active gate: `Docling Runtime Local Artifact / No-model-download Containment Proof Gate`
- `docs/implementation-control.md` current mainline: prove or fail closed before any conversion
- Prior controller judgment `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-controller-judgment-20260614.md` verdict: `ACCEPT_EVIDENCE_BLOCKED_READY_FOR_DOCLING_LOCAL_ARTIFACT_CONTAINMENT_PROOF_GATE_NOT_READY`
- `docs/design.md` boundary: Docling is only a future candidate, not current production parser; output is not fact truth

No inconsistency found between the evidence artifact and the control truth documents.

## 9. Summary

The evidence artifact is well-structured, correctly scoped, and accurately proves the containment blocker. The key finding is that `do_table_structure=False` successfully bypasses table-structure execution (partial bypass proven), but layout remains fully model-backed with no disable switch and no accepted local artifact. The `artifacts_path=None` -> `download_hf_model()` -> `snapshot_download()` chain is the definitive containment blocker. The local artifact inventory at maxdepth 10 is sufficient to reject any claim of existing bundled layout/table weights. All scope boundaries were respected and NOT_READY status is preserved throughout.

```text
review_artifact_path=docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-review-mimo-20260614.md
verdict=PASS
findings_count=9
blocking_findings=0
release_readiness=NOT_READY
```
