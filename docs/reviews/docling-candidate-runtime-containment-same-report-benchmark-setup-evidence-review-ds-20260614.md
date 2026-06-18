# Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Review — AgentDS — 2026-06-14

Status: `REVIEW_COMPLETE`
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Gate`
Reviewer: AgentDS (evidence review worker, read-only)
Evidence under review: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md`
Plan artifact: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`
Controller judgment: `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-controller-judgment-20260614.md`

## 1. Scope

This review is evidence-only, read-only, and bounded by the seven review focuses prescribed by the controller. It does not authorize any implementation, live command, network access, PDF read, parser execution, Docling conversion, provider/LLM call, readiness/release/PR action, stage, or commit.

## 2. Inputs Reviewed

- `AGENTS.md`
- `docs/design.md` (partial, architecture/current-state sections)
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-20260614.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-plan-controller-judgment-20260614.md`
- `docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md`

## 3. Review Matrix

| Focus | Question | Verdict | Evidence |
|---|---|---|---|
| F1 | 是否正确使用 004393 作为 primary sample，未把本地 PDF filename inventory 当 source truth？ | PASS | Evidence §3 正确设置 A1=004393/2025；本地 PDF 文件列表归类为 `identity_partly_matched_local_candidate_only`，明确标注 no body read / not source truth；§6 声明 local file as source truth forbidden/not used。 |
| F2 | C0/C1 containment 是否足以支持 verdict DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY？ | PASS | C0 记录了 version、do_ocr、do_table_structure、layout model repo_id、table mode、artifacts_path=None、enable_remote_services=False；C1 证明 layout model 有 remote repo_id 且 model_path 为空，table structure 默认启用且无 local-only proof，RapidOCR 残留在案。阻断理由充分，verdict 正确。 |
| F3 | 是否正确停止在 containment blocker？ | PASS | §5 EID HTML render `not_attempted_after_containment_block`；§6 FDR/PDF `not_attempted_after_containment_block`；§4 C0/C1 未执行 convert；§12 无安装/网络/转换/provider/LLM。所有 prohibited 操作均未执行。 |
| F4 | 是否正确保留 eid_xbrl_html_render_candidate，不叫 raw XBRL/raw XML truth？ | PASS | §5 显式声明 `eid_xbrl_html_render_candidate=not_discovered_for_004393_in_this_gate`、`not_raw_xml`、`not_source_truth`、`not_field_correctness_proof`、`not_taxonomy_proof`。 |
| F5 | 是否没有 field correctness / taxonomy / source truth / parser replacement / readiness claim？ | PASS | §13 列出 `not_raw_xml_download_proof`、`not_field_correctness_proof`、`not_taxonomy_compatibility_proof`、`not_source_truth`、`not_readiness_proof` 均为 retained；§1 声明 readiness=NOT_READY；全文无以上任何声明。 |
| F6 | Next gate recommendation 是否合理？ | PASS | 推荐 `Docling Runtime Local Artifact / No-model-download Containment Proof Gate`，聚焦 layout/table model local artifact proof 或 no-model bypass，保留 socket-blocking 和 residual 分类。推荐精确对应 blocker，不扩大 scope，不跳过 EID HTML render discovery 等 deferred gate。无需改写。 |
| F7 | 是否存在 blocker finding 或只需要 controller amendments？ | PASS | 无 blocker finding。Evidence 在 plan 约束内完整执行，C0/C1 证据充分，stop condition 正确触发，所有 non-goal 保持。不需要 controller amendments。 |

## 4. Findings

| # | Class | Severity | Description | Disposition |
|---|---|---|---|---|
| DS-F1 | observation | info | C0 options introspection 覆盖面完整：除 do_ocr 外还检查了 do_table_structure、layout_options、table_structure_options、artifacts_path、enable_remote_services、allow_external_plugins、accelerator_options、picture_classification/description、code_formula/chart 等所有可见 model-backed stage。 | 正面确认，无需行动。 |
| DS-F2 | observation | info | RapidOCR 残留文件分类严格遵循 plan 要求：`DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`，8 个文件全量列出，未被当作 self-contained proof。 | 正面确认，无需行动。 |
| DS-F3 | observation | info | Evidence 在 `not_attempted_after_containment_block` 状态下仍然正确保留了完整的 blocked proofs and residuals 表（§13），使后续 gate 可直接消费当前状态，不丢失上下文。 | 正面确认，无需行动。 |
| DS-F4 | observation | info | Next gate recommendation 末尾显式声明了 deferred gates 列表（EID HTML render discovery、repository PDF、pdfplumber、Docling conversion、source design、parser adapter、production integration、readiness/release、PR、fallback），防止 scope creep。 | 正面确认，无需行动。 |

## 5. Accepted Facts

1. Docling 2.93.0 已安装、可导入，但 C0/C1 无法证明 layout/table 模型阶段为 local-only。
2. `layout_options.model_spec.repo_id=docling-project/docling-layout-heron`、`model_path=''`、`artifacts_path=None` 构成当前阻断证据。
3. `do_table_structure=True`，`TableFormerMode.ACCURATE`，无 local-only proof。
4. `enable_remote_services=False` 和 `allow_external_plugins=False` 不构成 model fetch 防护证明。
5. RapidOCR 残留文件存在，分类为 `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`。
6. 所有 EID HTTP、FDR/PDF、pdfplumber、Docling conversion、provider/LLM 操作均未执行。
7. `eid_xbrl_html_render_candidate` 保持候选分类，未声明为 raw XML/source truth/taxonomy proof。
8. 无 field correctness、taxonomy compatibility、source truth、parser replacement、readiness 声明。
9. Release/readiness 保持 `NOT_READY`。

## 6. Residuals

| Residual | Status | Owner |
|---|---|---|
| `docling_runtime_containment_unproven` | retained; next gate input | Evidence worker / controller |
| `004393_eid_html_render_identity_unproven` | retained; deferred after containment | Evidence worker / controller |
| `004393_fdr_pdf_ownership_unproven` | retained; deferred | Evidence worker / controller |
| `same_report_tri_route_comparison_unproven` | retained; deferred | Evidence worker / controller |

## 7. Verdict

```text
VERDICT: PASS
```

Rationale:

- F1–F7 全部 PASS，无 blocker finding，无 controller amendment 需求。
- Evidence 正确使用 004393 作为 primary sample，本地 PDF filename inventory 未当作 source truth。
- C0/C1 containment 证据充分支持 `DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY`。
- 所有操作在 containment blocker 处正确停止，未执行 EID HTTP、FDR/PDF、pdfplumber、Docling conversion、provider/LLM、readiness/release/PR。
- `eid_xbrl_html_render_candidate` 分类正确保留，未越界声明。
- 无 field correctness、taxonomy、source truth、parser replacement、readiness claim。
- Next gate recommendation 精确、合理，无需改写。

## 8. Recommendation

Controller 可接受此 evidence artifact 并推进到 next gate `Docling Runtime Local Artifact / No-model-download Containment Proof Gate`。Evidence artifact 本身无需修改。

Completion status:

```text
Self-check: pass
artifact_path=docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-review-ds-20260614.md
verdict=PASS
release_readiness=NOT_READY
```
