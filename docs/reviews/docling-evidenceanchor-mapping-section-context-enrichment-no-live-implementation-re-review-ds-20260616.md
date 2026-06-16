# Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Re-review — AgentDS

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Re-review Gate`
Re-reviewer: AgentDS
Date: 2026-06-16
Release/readiness: `NOT_READY`

## Scope

- **Mode**: re-review (accepted fixes only)
- **Branch**: `feat/mvp-llm-incomplete-run-artifacts`
- **Output file**: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-re-review-ds-20260616.md`
- **Re-reviewed fixes**:
  - DS finding 01: last stable span unbounded → `_unindexed_section_boundary_pages` + `boundary_pages` in `_section_spans`
  - MiMo finding 02: same-page distinct top-level duplicate not detected → `top_level_node_ids` in `_duplicate_sections`
- **Included scope**:
  - `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` (fix lines only)
  - `tests/fund/documents/test_docling_evidence_anchor_mapping.py` (new tests for fixes)
  - `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-fix-evidence-20260616.md` (fix evidence claims)
- **Excluded scope**: all non-fix code, deferred/rejected findings, re-evidence gate artifacts
- **Parallel review coverage**: 无

## Validation

```text
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
→ 36 passed in 0.44s

uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
→ All checks passed!

git diff --check
→ passed
```

## Fix 01 Re-review: Last Stable Span Unbounded

### Fix trace

原始问题：`_section_spans` (L978-996 at time of DS review) 对最后一个稳定章节 span 设置 `end_page=None`，`_span_for_page` 中 `span.end_page is not None and page >= span.end_page` 对 None end_page 永不为 True，末 span 吸收所有 >= start_page 的页码。

修复方式：
- 新增 `_unindexed_section_boundary_pages` (L979-1002)：遍历全部 section node，过滤 TOC 和 child heading，对无法唯一归入 §1–§10 的 section node 提取其页码作为边界页。
- `_build_section_index` L867 调用 `boundary_pages = _unindexed_section_boundary_pages(document.sections)`，L868 传入 `_section_spans(selected_pages, boundary_pages)`。
- `_section_spans` (L1005-1026) 新增 L1023-1024：对每个 span 取 `next_boundary = min((page for page in boundary_pages if page > start_page), default=None)`，`next_start = _minimum_positive_page(next_stable_start, next_boundary)`。
- `_minimum_positive_page` (L1029-1047)：取两个可选正页码中的较小者。

### 链路走读

测试 case `test_unsupported_section_node_closes_previous_stable_section_span` (L831-860)：

- sections: §8 (page 60), "附录" (page 80)
- "附录" → `_section_candidates_from_texts(["appendix", "附录"])` → candidates=() → len != 1 → boundary_pages={80}
- §8 span: start_page=60, next_stable_start=None, next_boundary=80, next_start=80, end_page=80
- §8 span = [60, 80)
- Table page 62 → `_span_for_page`: page ≥ 60, page < 80 → §8 ✅
- Table page 81 → `_span_for_page`: page ≥ 60, page ≥ 80 → skip; no more spans → None → `missing_section_context` ✅

### Adversarial check

**边界页位于两个稳定章节之间**：例如 §3 (page 10)、未识别 "管理人报告" (page 30)、§8 (page 60)。

- boundary_pages={30}
- §3 span: [10, 30), §8 span: [60, None)
- 页码 35 的 block → `_span_for_page`: §3 page 35 ≥ 30 → skip; §8 page 35 < 60 → skip; 无更多 span → None → `missing_section_context`

此行为比原始实现更保守：原始代码中 §3 span [10, 60) 会吸收页码 35。边界页关闭前一 span 后，下一稳定 span 尚未开始，中间内容被阻断。

**评估**：fail-closed，不产生错误映射。计划要求无法一一映射时阻断，此行为符合设计哲学。但需注意：若真实文档中边界页对应的未支持章节实际是前序章节的子内容（非独立边界），阻断率会高于必要水平。此风险需要在 re-evidence gate 的真实 artifact 上验证。

**边界页位于首稳定章节之前**：例如 "封面" (page 1)、§2 (page 5)。boundary_pages={1}，但 1 不大于 §2 的 start_page 5，next_boundary=None，不影响 §2 span。封面页码 1 → `_span_for_page` 全部 skip → `missing_section_context` ✅。

### Fix verdict: PASS

修复正确解决了末稳定 span 无上界的问题。`_unindexed_section_boundary_pages` + `boundary_pages` + `_minimum_positive_page` 机制在末稳定章节后被未索引 section node 截断时正确关闭 span。中间 gap 区域的 fail-closed 阻断是合理保守行为。

---

## Fix 02 Re-review: Same-page Distinct Top-level Duplicate

### Fix trace

原始问题：`_duplicate_sections` (L949-953 at time of MiMo review) 使用 `top_level_pages = {entry.page for entry in entries if not entry.is_child_heading}` 比较页码集合，两个不同 node_id 的 body 条目在同一页码时不会被标记为 duplicate。

修复方式：
- L951: `top_level_node_ids = {entry.node_id for entry in entries if not entry.is_child_heading}` — 改用 node_id 集合
- L952: `if len(top_level_node_ids) > 1:` — 不同 node_id 即标记 duplicate，无论页码是否相同

### 链路走读

测试 case `test_duplicate_same_page_top_level_body_heading_blocks_page_based_propagation` (L699-722)：

- sections: sec_8_a (page 60), sec_8_b (page 60)
- 两者均被 `_section_index_entries` 归一为 §8，is_child_heading=False
- top_level_node_ids = {"sec_8_a", "sec_8_b"} → len > 1 → duplicate_sections = {"§8"} ✅
- `safety_reason_for_section("§8")` → "duplicate_section_heading" → page propagation 被阻断 ✅

### Adversarial check

**同 node 多次出现**：同一 section node 不可在 `_section_index_entries` 中生成多个条目（迭代一次生成至多一个条目）。即使发生，top_level_node_ids 只有 1 个元素 → 不触发 duplicate。无危害。

**Child heading 仍正确排除**：`test_same_section_child_nodes_do_not_break_monotonic_ordering` (L751-776) — sec_8_child 的 heading_text "8.4 报告期末按行业分类的股票投资组合" 含 "." → is_child_heading=True → 不进入 top_level_node_ids → 不触发 duplicate ✅。

**node_id 一致性**：`_SectionIndexEntry.node_id` 在 L908 赋值为 `section.section_id`，即 `CandidateSectionNode.section_id`，是候选表示中该 section 节点的唯一标识。不同 body section node 必有不同 section_id，正确区分 distinct source。

### Fix verdict: PASS

修复正确将对 duplicate 的判断从页码比较改为 node_id 比较。两个 distinct 顶层 body section node 归一为同一 §N 时，无论页码是否相同均被标记为 duplicate_section_heading，fail-closed 阻断。

---

## Findings

未发现新的实质性问题。两个 accepted fix 均正确实现，测试覆盖了修复的核心场景。

## Open Questions

- 无

## Residual Risk

- **Fix 01 中间 gap 阻断率**：边界页关闭前一稳定 span 后，若与下一稳定 span 之间存在 gap，gap 内内容被阻断为 `missing_section_context`。在真实文档中未识别 section node 密集分布时可能产生高于预期的阻断率。需 re-evidence gate 真实 artifact 验证。
- 所有其他 DS review 和 MiMo review 的 residual risk 仍然有效（field correctness、source truth、S1 full JSON、真实 artifact table/cell yield 等）。

## Final Verdict

```text
RE_REVIEW_PASS_NOT_READY
```

两个 controller-accepted fix 均正确实现并经过测试验证。36 测试全部通过，ruff 和 git diff --check 无报错。release/readiness 维持 `NOT_READY`。
