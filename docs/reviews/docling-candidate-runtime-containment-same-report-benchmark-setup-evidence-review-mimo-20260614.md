# Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Gate — MiMo Evidence Review

Date: 2026-06-14
Reviewer: AgentMiMo
Artifact reviewed: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md`
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Gate`

## Verdict

```text
VERDICT: PASS_WITH_FINDINGS
```

## Findings Table

| # | Severity | Finding | Evidence Location | Disposition |
|---|---|---|---|---|
| F1 | info | Section 2 Inputs Reviewed 列出 7 项，比 plan §4 要求的 6 项多了一项 `same-report-document-representation-quality-comparison-evidence-20260614.md`。该文件是 plan §4 Direct Evidence Inputs 的隐含前提（plan §2 引用了它），多读不违反 boundary，但 evidence 未说明为什么补充读取该文件。 | Section 2, item 7 | accepted; non-blocking |
| F2 | info | RapidOCR residual files 列表中出现 `.pth` 文件（`ch_PP-OCRv4_det_mobile.pth` 等）以及 `ppocrv5_dict.txt`，但 classification 仍使用统一标签 `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`。`.pth` 权重与 `.onnx` 推理模型混合存在可能值得细化记录，但不影响 containment verdict。 | Section 4, residual files list | accepted; non-blocking |
| F3 | info | Section 12 Performance And Runtime Side Effects 未记录 Docling import introspection 的 elapsed time 或 import 触发的内部 module 加载数量。plan §10 要求 Performance 列有 `conversion elapsed only if contained`，但 import introspection 本身未计时。不影响 containment verdict。 | Section 12 | accepted; non-blocking |

## Accepted Facts

| # | Fact | Source |
|---|---|---|
| A1 | Primary sample correctly selected as `004393 / 安信企业价值优选混合A`, preferred year `2025`, fallback years `2024, 2023, 2022`. Matches plan §6 Sample Matrix. | Section 1, Section 3 |
| A2 | Local `基金年报/` PDF filename inventory correctly classified as `identity_partly_matched_local_candidate_only` / `candidate_inventory_only`, not source truth, not body-read. | Section 3, Section 6, Section 7 |
| A3 | Docling version `2.93.0` confirmed installed and importable through project `uv run python`. | Section 4 C0 |
| A4 | `PdfPipelineOptions.do_ocr=False` is configurable. | Section 4 C0 |
| A5 | C0/C1 containment correctly identified as `blocked`: layout stage has `repo_id=docling-project/docling-layout-heron`, `model_path=''`, `artifacts_path=None`; default table structure enabled with `TableFormerMode.ACCURATE`; no accepted local artifact proof. | Section 4 C1 |
| A6 | `enable_remote_services=False` and `allow_external_plugins=False` observed but correctly noted as insufficient proof against model-artifact lookup/download inside local stages. | Section 4 C1 |
| A7 | RapidOCR residual model files from prior boundary incident exist and are correctly classified as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`. | Section 4 |
| A8 | No EID HTTP request, repository PDF acquisition, pdfplumber execution, Docling conversion, provider/LLM command, readiness/release/PR action was executed. | Section 2, Sections 5-12 |
| A9 | `eid_xbrl_html_render_candidate` label correctly preserved throughout; not called raw XBRL, raw XML, source truth, field correctness proof or taxonomy proof. | Section 5 |
| A10 | Verdict `DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY` correctly matches one of the plan §11 allowed verdicts. | Section 15 |
| A11 | Release/readiness remains `NOT_READY`. | Section 1, Section 13, Section 15 |
| A12 | No production source/test/runtime file modified. No cache or parser output written. No dependency installation attempted. | Section 12 |

## Residuals

| Residual | Status | Owner |
|---|---|---|
| `docling_runtime_containment_unproven` | blocking | Evidence worker / controller |
| `layout_model_remote_repo_visible` | blocking | Evidence worker / controller |
| `table_structure_model_path_unproven` | blocking | Evidence worker / controller |
| `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED` | retained | Evidence worker / controller |
| `004393_eid_html_render_identity_unproven` | retained | Evidence worker / controller |
| `004393_fdr_pdf_ownership_unproven` | retained | Evidence worker / controller |
| `same_report_tri_route_comparison_unproven` | retained | Evidence worker / controller |
| `not_raw_xml_download_proof` | retained | Evidence worker / controller |
| `not_field_correctness_proof` | retained | Evidence worker / controller |
| `not_taxonomy_compatibility_proof` | retained | Evidence worker / controller |
| `not_source_truth` | retained | Evidence worker / controller |
| `not_readiness_proof` | retained | Evidence worker / controller |

## Review Focus Checklist

| # | Focus | Result |
|---|---|---|
| 1 | Evidence 是否正确使用 004393 / 安信企业价值优选混合A 作为 primary sample，但未把本地 PDF filename inventory 当 source truth | **PASS** — A1, A2 |
| 2 | C0/C1 containment 是否足以支持 verdict DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY | **PASS** — A5, A6, A7; layout/table model stages unproven local, residual files not promoted |
| 3 | 是否正确停止在 containment blocker，未运行 EID HTTP、FDR/PDF、pdfplumber、Docling conversion、provider/LLM、readiness/release/PR | **PASS** — A8, A12 |
| 4 | 是否正确保留 eid_xbrl_html_render_candidate，不叫 raw XBRL/raw XML truth | **PASS** — A9 |
| 5 | 是否没有 field correctness、taxonomy compatibility、source truth、parser replacement、readiness claim | **PASS** — A9, A11; all claims correctly absent |
| 6 | Next gate recommendation 是否合理 | **PASS** — `Docling Runtime Local Artifact / No-model-download Containment Proof Gate` is logical next step to resolve C0/C1 blocker |
| 7 | 是否存在 blocker finding 或只需要 controller amendments | **No blocker findings** — only info-level observations (F1-F3), all accepted |

## Recommendation

Evidence artifact 正确执行了 plan 要求的 bounded containment 检查，正确在 C0/C1 blocker 处停止，正确保持所有 non-goals 和 boundary constraints。三个 info-level findings 均为非阻断性观察，不需要 controller amendment。

Next gate `Docling Runtime Local Artifact / No-model-download Containment Proof Gate` 是合理的后续入口：必须先证明 Docling layout/table stages 的本地 artifacts 或禁用/绕过路径，才能进入 same-report benchmark comparison。

```text
artifact_path=docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-review-mimo-20260614.md
verdict=PASS_WITH_FINDINGS
blocking_findings=0
info_findings=3
git_diff_check=not_applicable_review_only
release_readiness=NOT_READY
```
