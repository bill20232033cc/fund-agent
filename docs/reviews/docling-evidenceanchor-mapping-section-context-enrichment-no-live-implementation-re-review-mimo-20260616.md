# Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Re-review — AgentMiMo

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Re-review Gate`
Reviewer: AgentMiMo
Date: 2026-06-16
Re-review basis: accepted fixes for DS finding 01 and MiMo finding 02

## Scope

- Mode: re-review of accepted fix set only
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: implementation review artifacts (DS + MiMo) and fix evidence
- Output file: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-re-review-mimo-20260616.md`
- Included scope:
  - `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` — fix verification for DS finding 01 and MiMo finding 02
  - `tests/fund/documents/test_docling_evidence_anchor_mapping.py` — fix test verification
  - `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-fix-evidence-20260616.md` — fix evidence claims
- Excluded scope: source acquisition, parser, repository/cache, production EvidenceAnchor, CHAPTER_CONTRACT, Service/Host/UI/renderer/quality gate, provider/LLM, README/design/control docs, readiness/release/PR/push/merge
- Parallel review coverage: 无

## Re-review Targets

### DS Finding 01: `_section_spans` 末 span 无上界

**Original defect**: `_section_spans` 对最后一个 span 设置 `end_page=None`；`_span_for_page` 中 `end_page=None` 条件永不为 True，末索引节吸收所有 >= start_page 的页码。若 §8 是最后一个被索引节（page 60），page 100+ 的附录内容会被错误分配到 §8。

**Fix verification**:

1. 新增 `_unindexed_section_boundary_pages` (L979-1002): 遍历所有 section nodes，跳过 TOC 和 child heading，对无法解析为唯一 §N 候选的节点提取其 page 作为 boundary page。
2. `_build_section_index` (L867) 调用此函数获取 `boundary_pages`，传入 `_section_spans`。
3. `_section_spans` (L1023-1024) 对每个 span 计算 `next_boundary = min((page for page in boundary_pages if page > start_page), default=None)`，然后 `next_start = _minimum_positive_page(next_stable_start, next_boundary)`。末 span 的 `end_page` 不再一定是 None，而是被最近的 boundary page 截断。

**代码走读**:

- `evidence_anchor_mapping.py:1021-1025`: 每个 span 的 `end_page` 由 `next_stable_start`（下一稳定章节起始页）和 `next_boundary`（大于当前 start_page 的最近未索引 section node 页码）中的较小值决定。
- `evidence_anchor_mapping.py:1023`: `min(..., default=None)` — 当 boundary_pages 中无大于 start_page 的页码时返回 None，不影响已有行为。
- `evidence_anchor_mapping.py:997-1001`: `_unindexed_section_boundary_pages` 正确排除 TOC 和 child heading，仅对真正无法归入稳定索引的正文 section node 提取边界页。

**测试覆盖**:

- `test_unsupported_section_node_closes_previous_stable_section_span` (L831-860): §8 在 page 60，"附录" 在 page 80。inside_table (page 62) 正确映射到 §8；outside_table (page 81) 正确阻断为 `missing_section_context`。验证了末 span 被 boundary page 截断。

**结论**: 修复正确。末 span 不再无条件吸收后续页码。boundary page 提取逻辑排除了 TOC 和 child heading，不会引入误截断。

### MiMo Finding 02: `_duplicate_sections` 仅比较页码未比较 node_id

**Original defect**: `_duplicate_sections` 使用 `top_level_pages = {entry.page for entry in entries if not entry.is_child_heading}`，仅比较页码集合大小。两个不同 node_id 的 body section node 在同一正页码时不会被标记为 duplicate，允许 page-based propagation。

**Fix verification**:

1. `_duplicate_sections` (L949-953) 改为 `top_level_node_ids = {entry.node_id for entry in entries if not entry.is_child_heading}`，检查 `len(top_level_node_ids) > 1`。

**代码走读**:

- `evidence_anchor_mapping.py:951`: `{entry.node_id for entry in entries if not entry.is_child_heading}` — 收集所有非 child heading 的 node_id。两个不同 node_id 的 section node 归一到同一 §N 时，即使页码相同也会被检测到。
- `evidence_anchor_mapping.py:952`: `len(top_level_node_ids) > 1` — 多个 distinct top-level node_id 触发 duplicate。
- 此改动同时保留了原有多页码场景的检测能力：不同 node_id 在不同页码时 `top_level_node_ids` 仍含多个元素。

**测试覆盖**:

- `test_duplicate_same_page_top_level_body_heading_blocks_page_based_propagation` (L699-722): 两个不同 `section_id`（`sec_8_a`、`sec_8_b`）的 §8 section node 均在 page 60，table 在 page 60。结果正确阻断为 `duplicate_section_heading`，table 未被映射。
- 既有测试 `test_duplicate_body_heading_blocks_page_based_propagation` (L673-696) 仍通过：不同页码（page 60、page 70）的重复章节仍正确阻断。

**结论**: 修复正确。从页码集合比较改为 node_id 集合比较，精确对齐计划语义 "If two distinct body section nodes normalize to the same annual section and cannot be proven to be the same source node or same selected body start, mark that section family as duplicate." 同页不同 node_id 现在正确 fail-closed。

## Validation Re-executed

```text
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
→ 36 passed in 0.38s

uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
→ All checks passed!

git diff --check
→ passed
```

Fix evidence 声称的 36 个测试全部通过（原 34 + 2 个 fix 新增测试）。ruff 和 git diff --check 均无报错。

## Findings

未发现实质性问题。两个 accepted findings 的 fix 实现正确、测试充分、验证通过。

## Open Questions

- 无。

## Residual Risk

- DS finding 01 的 boundary page 机制依赖 section node 的 `heading_text`/`heading_path` 不能被 `_section_candidates_from_texts` 解析为唯一 §N。若真实 Docling 输出中的附录/声明页 heading 碰巧命中关键词族（如"财务报表" → §7），则该页仍会被纳入 §7 的 span 而非截断。此为原始设计约束的已知边界，不属于 fix 引入的新风险。
- MiMo finding 02 的 fix 使用 `node_id` 做唯一性判断。若 Docling 对同一 section 生成多个具有相同 `section_id` 的 node（如分页 section），fix 不会误触发（同 node_id 不计入 top_level_node_ids）。此为正确行为。

## Final Verdict

```text
RE_REVIEW_PASS_NOT_READY
```

两个 accepted findings 的 fix 实现正确，新增测试覆盖了 fix 目标场景，36 个测试全部通过。release/readiness 维持 `NOT_READY`（fix gate 本身不改变 readiness 状态）。
