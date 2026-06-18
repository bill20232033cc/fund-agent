# Code Review

## Scope

- Mode: current changes (implementation review gate)
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: `main`
- Output file: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-review-mimo-20260616.md`
- Included scope:
  - `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` (new, 1435 lines)
  - `tests/fund/documents/test_docling_evidence_anchor_mapping.py` (new, 922 lines, 34 tests)
  - `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-evidence-20260616.md`
- Excluded scope: source acquisition, parser, repository, production EvidenceAnchor, CHAPTER_CONTRACT, Service, Host, UI, renderer, quality gate, provider/LLM, README, design docs, control docs, reports, readiness, release, PR, push, merge
- Parallel review coverage: 无
- Review basis:
  - `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md`
  - `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-controller-judgment-20260616.md`

## Findings

### 01-未修复-低-公共单块 API 每次调用重建 SectionIndex

- **入口/函数**: `map_candidate_locator_to_anchor_candidate()` (line 241)
- **文件(行号)**: `evidence_anchor_mapping.py:268`
- **输入场景**: 调用方对同一文档的多个 block 逐个调用公共单块 API
- **实际分支**: 每次调用执行 `_build_section_index(document)` (line 268)
- **预期行为**: 计划要求 "Build an internal frozen SectionIndex or equivalent private structure once in `map_candidate_document_anchor_candidates()` and pass it through internal helper calls." 批处理函数 `map_candidate_document_anchor_candidates()` 正确地在 line 192 构建一次并传递；但公共单块 API 没有复用机制。
- **实际行为**: 公共 API 每次调用重新构建 `_SectionIndex`，包含遍历所有 section nodes、分组、去重检查、单调性检查和 span 构建。对同一文档 N 个 block 逐个调用时复杂度为 O(N * S)，S 为 section 节点数。
- **直接证据**: `evidence_anchor_mapping.py:268` — `section_index=_build_section_index(document)` 在每次公共单块调用时执行；`_build_section_index` (line 845) 遍历 `document.sections` 并执行完整的索引构建流程。
- **影响**: 性能影响。不影响正确性。公共 API 签名保持不变（满足计划约束），但调用方可能不知道应优先使用批处理函数。
- **建议改法和验证点**: 1) 在模块文档中明确推荐 `map_candidate_document_anchor_candidates()` 用于批量场景；或 2) 在后续 gate 中考虑为公共 API 增加可选 `section_index` 参数（需 controller 授权签名变更）。验证：确认批处理函数只构建一次索引（已满足）。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 02-未修复-低-_duplicate_sections 仅比较页码未比较 node_id

- **入口/函数**: `_duplicate_sections()` (line 935)
- **文件(行号)**: `evidence_anchor_mapping.py:949-953`
- **输入场景**: 两个不同 body section node 规范化为同一年报章节且恰好在同一正页码
- **实际分支**: `top_level_pages = {entry.page for entry in entries if not entry.is_child_heading}`; `len(top_level_pages) > 1` 为 False
- **预期行为**: 计划要求 "If two distinct body section nodes normalize to the same annual section and cannot be proven to be the same source node or same selected body start, mark that section family as duplicate." 当两个不同 body 节点在同一正页码时，实现按 "same selected body start" 视为安全。
- **实际行为**: 实现仅比较 `entry.page` 集合大小，未显式检查 `entry.node_id` 是否相同。两个不同 node_id 的 body 条目在同一正页码时不会被标记为 duplicate。当前 `_section_index_entries` 中每个 entry 携带了 `node_id` 字段（line 908），但 `_duplicate_sections` 未使用。
- **直接证据**: `evidence_anchor_mapping.py:950-951` — `top_level_pages = {entry.page ...}` 仅提取页码集合；未使用 `entry.node_id` 做同源节点判断。
- **影响**: 边界情况。两个不同 body 节点恰好在同一正页码时不会被标记为 duplicate，允许 page-based propagation。在实际年报中，不同 body section node 出现在同一页码的概率较低。不影响已通过的测试。
- **建议改法和验证点**: 若需完全对齐计划语义，可将 `_duplicate_sections` 改为：当 `len(top_level_pages) > 1` 或 `len(unique_node_ids) > 1`（同一正页码但不同 node_id）时标记为 duplicate。验证：添加合成测试用两个不同 node_id 的 body 节点在同一正页码，确认行为符合预期。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- 无。实现与计划/控制器裁决对齐，两个 findings 均为低严重程度，不阻塞 gate 推进。

## Residual Risk

- Table/cell yield on accepted real artifacts 仍未验证（需 re-evidence gate）。
- Field correctness 未证明。
- Source truth 未证明。
- S1 full JSON current-envelope mismatch 仍 deferred。
- Runtime/cache/cost baseline suitability 未证明。
- `_is_child_section_heading` 对 `CandidateSectionNode` 的 `heading_path` 依赖假设 heading_path 中的值是原始标题文本（非规范化后的 section_id）。若 heading_path 包含 `§8` 而非 `8.4 投资组合报告`，该节点不会被识别为 child heading。当前合成测试覆盖了标准 case，但未覆盖 heading_path 格式变异。
- `_section_candidate_from_document_section` 的 fallback 路径（line 787-802）未被直接测试覆盖。该路径在 block 的 `section_id` 匹配唯一 document section 且不在 `_SectionIndex` 中时触发。

## Test Adequacy

34 tests pass, ruff clean, `git diff --check` clean。

覆盖的 plan 要求 case：
- 数字标题 positive: `2.1 基金基本情况` → §2, `§ 2` → §2, `２．１` → §2, `8.4 报告期末按行业分类的股票投资组合` → §8
- 未授权数字标题: `8.3 任意无关文本`, `11.1`, `二、`, `（二）`, `第八节`, `2、` → `unsupported_heading_number`
- TOC 排除: TOC 节点不作为正文 span 起点
- 不安全 TOC/body 模糊: 无 TOC 信号时重复章节 → `duplicate_section_heading`
- 重复正文标题: → `duplicate_section_heading`
- 跨章节单调违规: → `section_order_not_monotonic`
- 同章节子标题不破坏单调性
- page-based table 继承: page 62 → §8
- 半开区间边界: page 60 → §8 (not §3)
- 缺页码: → `missing_section_context`
- 跨章节多页表格: → `section_span_crosses_multiple_sections`
- cell 仅继承父表章节: row_label/column_header 中的 §2/§9 不覆盖
- 封面/报告标题: → `missing_section_context`
- S1 full JSON schema mismatch: `ValueError`

未直接覆盖但通过间接路径验证：
- explicit `§` token 路径跳过 keyword family 验证（通过 § 2 positive test 间接覆盖）
- `map_candidate_locator_to_anchor_candidate` 公共单块 API（通过 test_s1_cell_can_resolve_parent_by_unique_bbox_containment 间接覆盖）

## Plan/Controller Alignment Checklist

| Focus area | Status | Evidence |
| --- | --- | --- |
| Candidate-only boundary | PASS | `__post_init__` guards on all dataclasses; note field asserts |
| Public API stability | PASS | `map_candidate_locator_to_anchor_candidates` and `map_candidate_locator_to_anchor_candidate` signatures unchanged |
| Numeric heading closed-family guard | PASS | `_section_candidate_from_numeric_heading` validates 1..10 + keyword family |
| TOC exclusion and duplicate fail-closed | PASS | `_is_toc_section` + `_duplicate_sections` |
| Inter-section monotonic and same-section child | PASS | `_non_monotonic_sections` + `_is_child_section_heading` |
| SectionIndex built once and private | PASS | Built in `map_candidate_document_anchor_candidates` line 192; passed through private `_map_candidate_locator_to_anchor_candidate` |
| Page propagation and half-open spans | PASS | `_SectionSpan` with `end_page`; `_span_for_page` uses `page >= span.end_page` |
| Table/cell parent inheritance only | PASS | `_map_cell` resolves section from parent table; `_cell_row_locator` uses labels for locator only |
| Blocked reason taxonomy | PASS | All 7 new codes present: `missing_section_context`, `unstable_section_context`, `duplicate_section_heading`, `section_order_not_monotonic`, `section_span_crosses_multiple_sections`, `unsupported_heading_number`, plus existing codes |
| Test adequacy | PASS | 34 tests cover all plan-required positive and negative cases |
| No production EvidenceAnchor/source truth/readiness | PASS | `candidate_only=True`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"` enforced |

## Final Verdict

```text
PASS_WITH_FINDINGS_NOT_READY
```
