# Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Controller Judgment - 2026-06-14

Status: `CONTROLLER_JUDGMENT_COMPLETE`
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Gate`
Controller role: AgentController
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the evidence gate opened after the accepted plan:

- Plan: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`
- Plan controller judgment: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-controller-judgment-20260614.md`

The gate was allowed to collect bounded evidence for `004393 / 安信企业价值优选混合A`, preferred year `2025`, but only after proving Docling runtime containment. The gate was not allowed to implement code, install dependencies, replace parsers, change `FundDocumentRepository`, change source policy, run provider/LLM/readiness/release/PR commands, or promote any route to source truth.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- Evidence artifact: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md`
- DS review: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-review-ds-20260614.md`
- MiMo review: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-review-mimo-20260614.md`

## 3. Accepted Current Facts

| Fact | Controller disposition |
|---|---|
| Primary sample is `004393 / 安信企业价值优选混合A`, preferred year `2025`, fallback years `2024/2023/2022` only if needed. | Accepted as sample-selection fact only. |
| Local `基金年报/` filenames for 2022-2025 were observed. | Accepted only as user-owned filename inventory; not source truth, not repository proof, not PDF body evidence. |
| Docling `2.93.0` is installed and importable. | Accepted as local package fact. |
| `PdfPipelineOptions(do_ocr=False)` is configurable. | Accepted, but insufficient for containment. |
| Visible Docling layout/table stages still expose model-backed paths: `docling-project/docling-layout-heron`, empty `model_path`, `artifacts_path=None`, default `do_table_structure=True`, `TableFormerMode.ACCURATE`. | Accepted as the current containment blocker. |
| `enable_remote_services=False` and `allow_external_plugins=False` are visible guardrails. | Accepted, but rejected as sufficient proof that model artifacts cannot be fetched or required. |
| RapidOCR residual model files exist in `.venv`. | Accepted only as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`. |
| No EID HTTP, repository/FDR PDF acquisition, pdfplumber parser run, Docling conversion, provider/LLM, readiness/release/PR command was executed. | Accepted. |
| `eid_xbrl_html_render_candidate` remains candidate classification only. | Accepted; not raw XML, not raw XBRL instance truth, not source truth. |
| No field correctness, taxonomy compatibility, source-truth, parser replacement or readiness proof exists from this gate. | Accepted. |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentDS | `PASS` | Accepted. No blocker finding. |
| AgentMiMo | `PASS_WITH_FINDINGS` | Accepted with non-blocking info findings. |

MiMo findings:

| Finding | Controller disposition |
|---|---|
| Evidence read one additional implicit input, `same-report-document-representation-quality-comparison-evidence-20260614.md`. | Accepted as non-blocking. It was already referenced by the plan context and did not expand implementation or runtime scope. |
| RapidOCR residual list mixes `.onnx`, `.pth` and dictionary files under one residual label. | Accepted as non-blocking. The unified label is conservative because no residual file is promoted as accepted containment proof. |
| Import introspection did not record elapsed time/module-load counts. | Accepted as non-blocking. The plan only required conversion elapsed if conversion was allowed; conversion was not allowed. |

## 5. Blocked Claims

The following claims remain explicitly blocked:

| Claim | Status |
|---|---|
| Docling runtime containment is proven. | Blocked. |
| Docling can be safely converted under no-download/no-network conditions. | Blocked. |
| Same-report route comparison among EID HTML render, current pdfplumber and Docling is available for `004393 / 2025`. | Blocked. |
| EID HTML render identity is discovered for `004393 / 2025`. | Not attempted after containment block. |
| `FundDocumentRepository` PDF ownership is proven for `004393 / 2025` in this gate. | Not attempted after containment block. |
| HTML render is raw XML or raw XBRL instance truth. | Rejected. |
| Field correctness is proven. | Rejected. |
| Taxonomy/schemaRef compatibility is proven. | Rejected. |
| Any candidate route is source truth. | Rejected. |
| Release/readiness is improved to ready. | Rejected; remains `NOT_READY`. |

## 6. Final Verdict

```text
VERDICT: ACCEPT_EVIDENCE_BLOCKED_READY_FOR_DOCLING_LOCAL_ARTIFACT_CONTAINMENT_PROOF_GATE_NOT_READY
```

Rationale:

- The evidence worker followed the accepted stop order: C0/C1 containment before EID discovery, repository PDF acquisition, parser runs or Docling conversion.
- C0/C1 evidence is sufficient to prove a blocker, not sufficient to prove containment.
- DS and MiMo reviews do not identify any blocking defect in the evidence artifact.
- The correct next step is not same-report comparison or production implementation; it is a narrower local artifact/no-model-download containment proof gate.

## 7. Next Entry

Recommended next gate:

```text
Docling Runtime Local Artifact / No-model-download Containment Proof Gate
```

Minimum objective:

- identify the exact Docling standard PDF stages required for text-native annual-report conversion;
- prove accepted local artifacts for layout/table stages, or configure and justify a no-model path that disables or bypasses model-backed stages;
- pin artifact-path and accelerator/device behavior where needed;
- allow conversion only after containment proof, and only in a subprocess with conversion-phase socket blocking;
- keep RapidOCR residual files classified as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` unless a later gate proves a clean accepted model artifact setup.

Deferred entries:

- official EID HTML render discovery for `004393 / 2025`;
- repository-bounded PDF ownership proof for `004393 / 2025`;
- current pdfplumber parser evidence;
- Docling conversion evidence;
- same-report route quality comparison;
- candidate source design update;
- parser adapter implementation;
- production integration;
- readiness/release/PR.

## 8. Control-doc Update Recommendation

Update `docs/current-startup-packet.md` and `docs/implementation-control.md` to set the active gate to `Docling Runtime Local Artifact / No-model-download Containment Proof Gate`, preserving:

- release/readiness = `NOT_READY`;
- no production parser replacement;
- no `FundDocumentRepository` behavior change;
- no Service/UI/Host/renderer/quality-gate direct parser/XBRL/HTML/PDF access;
- no source fallback expansion;
- no field correctness, taxonomy, raw XML, source truth or readiness claim.
