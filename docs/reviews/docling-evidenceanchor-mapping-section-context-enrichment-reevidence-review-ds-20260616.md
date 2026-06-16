# Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Review (DS) — 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Review Gate`
Reviewer role: AgentDS review worker
Release/readiness: `NOT_READY`

## Scope

- **Reviewed artifact**: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-20260616.md`
- **Referenced implementation**: `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- **Referenced controller judgment**: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-controller-judgment-20260616.md`
- **Mode**: evidence review, not code review
- **Excluded**: source, tests, control docs, design docs, reports, cache, live/network/PDF/FDR/provider/LLM/readiness/release

## Validation Reproduced

Independent re-run of the mapping against the four accepted candidate envelopes reproduced all claimed counts exactly:

| Metric | Evidence claim | Reproduced |
| --- | ---: | ---: |
| Total mapped | 9389 | 9389 |
| Total blocked | 14086 | 14086 |
| Mapped by type: heading/paragraph/table/cell | 69/219/154/8947 | 69/219/154/8947 |
| Blocked by reason: missing_section_context/duplicate_section_heading/unsupported_heading_number | 13209/424/453 | 13209/424/453 |
| Per-sample mapped/blocked (S1/S4/S5/S6) | 2074/820/5967/528 | 2074/820/5967/528 |

Candidate-only assertions verified: all 9389 mapped and 14086 blocked records carry `candidate_only=True`, `candidate_source="docling"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`. S1 full JSON correctly blocked by `ValueError: unsupported candidate representation schema_version`.

All arithmetic (block-type subtotals, reason-code subtotals, table/cell yield percentages, before/after deltas) is internally consistent and reproducible.

## Findings

### 01-未修复-中-S1-current-envelope 与 S1 full JSON 是不同的制品，证据未披露两者关系

- **入口/函数**: 证据制品 §2 输入表第17行和21行
- **文件(行号)**: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-20260616.md:17,21`
- **输入场景**: 证据将 S1-current-envelope（`004393_2025_docling_current_envelope.json`）作为已接受候选信封用于映射，将 S1-full-json（`004393_2025_docling_full.json`）标记为 residual。但两个文件并非同一份数据的不同版本——它们有完全不同的 JSON schema 和内部字段结构。
- **实际分支**: 证据 §2 仅说明 S1 full JSON 被 schema guard 阻断，未解释 S1-current-envelope 的来源或它与 full JSON 的关系。
- **预期行为**: 如果 S1-current-envelope 和 S1 full JSON 代表同一份年报的不同导出路径，证据应披露这种关系并说明映射结果是否可代表 S1 raw Docling 输出的预期表现。
- **实际行为**: 证据将两者独立列出但未解释 current envelope 的制品来源。Full JSON 的 sections 使用 `children/heading_id/level/text` 字段结构，current envelope 的 sections 使用 `section_id/heading_text/heading_level/heading_path` 字段结构——这是完全不同的 JSON schema。同时 full JSON 有 `pages/metadata/metrics/coverage_status` 等 envelope 没有的顶层键，而 envelope 有 `blocked_claims/fund_code/sample_id` 等 full JSON 没有的键。
- **直接证据**:
  - Full JSON: `schema_version=None`, 顶层键包含 `pages/metadata/metrics/coverage_status`, sections[0] 字段为 `children/heading_id/level/text`
  - Current envelope: `schema_version='candidate_annual_report_representation.v1'`, 顶层键包含 `blocked_claims/fund_code/sample_id`, sections[0] 字段为 `section_id/heading_text/heading_level/heading_path`
  - 两者 block 计数相同（25/670/95/3493）但内部结构完全不同
- **影响**: S1 贡献了 2074 条 mapped 记录（占 mapped 总量的 22.1%），其 48.43% 的映射收益率显著高于 S4（21.46%）和 S6（7.41%）。如果 S1-current-envelope 与 raw Docling 输出之间存在未披露的处理差异，则 S1 的映射结果可能不代表 S1 full JSON 修复 schema 后的实际表现。当前无法验证 S1 full JSON 投影后的映射结果是否与 current envelope 一致，因为 full JSON 被 schema guard 阻断。
- **建议改法和验证点**: 证据应增加一条 residual 或在 §2 中明确说明 S1-current-envelope 的生成路径（是否为 `representation_export` 输出、是否经过字段重映射），并标注 S1 结果依赖于不同于 S4/S5/S6 的制品链路。当 S1 full JSON 的 schema_version 问题修复后，应用相同的 current envelope 导出路径重新生成并对比。
- **修复风险（低）**: 仅涉及文档披露，不涉及代码修改。
- **严重程度（中）**: 不否定映射改进的事实，但影响对 S1 结果可代表性的判断。证据未过度声称（已正确标记 `NOT_READY` 和 candidate-only），但制品链路的透明度不足。

### 02-未修复-低-聚合收益率混合了两个有不同校验规则的 schema family

- **入口/函数**: 证据制品 §4 结果矩阵和 §5 表格/单元格收益率
- **文件(行号)**: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-20260616.md:50,70`
- **输入场景**: S1 使用 `S1_full` schema family，S4/S5/S6 使用 `S4_S5_S6_lightweight` schema family。两者的 `_validate_cell_parent_table()` 校验路径不同。
- **实际分支**: `evidence_anchor_mapping.py:572-579` — `S4_S5_S6_lightweight` 要求非 None cell_index 且检查 duplicate cell tuple；`S1_full` 仅要求跨页表格的 cell 有页码。S1_full 的单元格校验更宽松。
- **预期行为**: 聚合的 "46.23% table/cell yield" 和 "40.00% mapped yield" 应附带说明不同 schema family 的校验规则不同，直接聚合可能掩盖校验严格度差异对收益率的影响。
- **实际行为**: 证据 §4-§5 直接聚合四个样本，§10 的结论引用聚合数但未提及 schema family 差异。
- **直接证据**: `_validate_cell_parent_table()` 第572-579行对两个 schema family 施加了不同的阻断条件；S1 单元格收益率 51.65% vs S6 单元格收益率 8.33% 的差异中，部分可能源于校验规则不同而非文档结构差异。
- **影响**: 低——每样本明细已在矩阵中呈现，仔细阅读可发现差异。结论中的聚合数未误导，但缺少使用前提说明。
- **建议改法和验证点**: 在 §5 或 §10 增加一句说明：S1（S1_full schema）的单元格校验规则与 S4/S5/S6（S4_S5_S6_lightweight schema）不同，聚合收益率应结合每样本明细解读。
- **修复风险（低）**: 仅涉及文档补充。
- **严重程度（低）**: 不影响核心结论的正确性，属于披露完整性改进。

## Open Questions

1. S1-current-envelope 是通过什么导出路径生成的？它和 S1 full JSON 是否来自同一次 Docling 转换运行？
2. S6 的极低收益率（7.41% mapped，8.36% table/cell）是否反映 `missing_section_context=6209` 的根因是文档结构（如缺少清晰章节边界）还是映射逻辑对特定文档布局的系统性盲区？
3. S4/S5/S6 的 2433 个 text block 零 paragraph 映射——是这些文档的 text block 确实全部落在稳定章节 span 之外，还是存在未诊断的映射路径问题？

## Residual Risk

- **S1 制品链路风险**: S1-current-envelope 与 S1 full JSON 的内部结构不同，当 full JSON 的 schema_version 修复后，其映射结果可能不同于 current envelope。当前无法验证。
- **Schema family 聚合风险**: `S1_full` 和 `S4_S5_S6_lightweight` 的校验路径差异未在聚合收益率中体现。
- **S6 低收益未诊断**: 证据正确将其列为 residual，但未分析根因（文档结构 vs 映射逻辑盲区），后续 gate 可能需要针对性诊断。
- **paragraph 映射极低**: S4/S5/S6 零 paragraph 映射，总计 219/3103=7.06% text block 映射率。证据未将其作为独立 residual 列出。
- **测试仅覆盖合成 fixture**: 36 个测试全部使用构造的 `CandidateRepresentationDocument`，未包含真实制品回归测试。真实制品的映射正确性仅靠本次 re-evidence 的一次性验证。

## Final Verdict

```text
VERDICT: PASS_WITH_FINDINGS_NOT_READY
```

**理由**: 证据的核心声明（映射收益率从 0.43% 提升至 40.00%、table/cell 从零提升至 46.23%、所有记录保持 candidate-only、S1 full JSON 仍为 residual）经过独立复现验证，算术一致，candidate-only 断言全部成立。证据未过度声称 field correctness、source truth、baseline promotion 或 readiness。

Finding 01（S1-current-envelope 与 S1 full JSON 的结构差异未披露）是中等严重度的披露缺失，影响对 S1 结果可代表性的判断。Finding 02（schema family 混合聚合）是低严重度的披露改进点。两项均不否定映射改进的事实，也不构成 blocker。

证据的 5 项 residual 正确识别了主要遗留风险。Open Questions 中的 S1 制品链路、S6 根因和 paragraph 映射盲区建议在后续 gate 中处理。
