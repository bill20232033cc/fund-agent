# Docling EvidenceAnchor Mapping Section-context Enrichment Plan Review (AgentMiMo) - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Plan Review Gate`
Role: AgentMiMo review worker
Release/readiness: `NOT_READY`

## Reviewed Target

`docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md`

## Scope

Adversarial review of the section-context enrichment plan, focusing on: candidate-only boundary, write set narrowness, deterministic section normalization closure, table/cell propagation safety, fail-closed behavior for duplicate/out-of-order/cross-section cases, S1 full JSON disposition, and test/evidence sufficiency.

## Assumptions Tested

1. Plan stays inside Fund documents candidate internals.
2. Exact later write set is narrow and excludes production surfaces.
3. Section normalization is closed and deterministic.
4. Table/cell propagation uses stable section index and structural parent-table resolution.
5. Duplicate/unstable heading behavior is fail-closed.
6. S1 full JSON mismatch is not silently bypassed.
7. Tests can prove table/cell yield without claiming field correctness or readiness.

## Source Documents Read

| Document | Purpose |
| --- | --- |
| Plan artifact | Review target |
| `AGENTS.md` | Execution rules, candidate isolation, fail-closed constraints |
| `docs/design.md` | Design truth: Docling is candidate-layer only |
| `docs/implementation-control.md` | Current gate and binding constraints |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-controller-judgment-20260616.md` | Prior gate verdict and residuals |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` | Accepted evidence facts |
| `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` | Current implementation |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | Current tests |

## Findings

### 01-未修复-高-Slice 1 未显式闭合 numeric heading 关键词族校验

- **位置**: Slice 1: Section Token Normalization
- **问题类型**: 不可直接实施
- **当前写法**: Plan 声称"Numeric headings map to an annual section only when the top-level number is `1..10` and the normalized heading text matches the closed keyword family for that section"。
- **反例/失败场景**: 现有 `_section_candidates_from_texts()` 在 `_ANNUAL_SECTION_PATTERN` 命中时直接 `candidates.add()` 并 `continue`，跳过关键词族校验。例如 heading `15.3 某随机标题` 不会误匹配（top-level 15 超出 1..10），但 `8.3 任意无关文本` 会直接映射为 `§8`，无需匹配关键词族。Plan 未指出这是需要修改的现有代码行为，implementation agent 可能认为当前逻辑已满足要求。
- **为什么有问题**: Plan 的 "closed keyword family" 约束是 section normalization 确定性的核心保证。如果 numeric heading 只要 top-level 在 1..10 就通过，任何 `8.xxx` 格式的非年报标题（如附录编号、表格编号）都会被错误映射，破坏 closed/auditable 语义。
- **直接证据**: `evidence_anchor_mapping.py:596-601` — `_section_candidates_from_texts` 中 pattern match 后 `continue` 跳过 keyword family check。Plan Slice 1 第3点："Extract annual-report numeric prefixes second, but only for top-level `1..10` and only when the remaining heading text matches the closed section keyword family"。
- **影响**: 实施 Agent 可能不修改现有 `_section_candidates_from_texts` 逻辑，导致 false-positive section mapping 增加，破坏 fail-closed 语义。
- **建议改法和验证点**: Plan 应显式标注 `_section_candidates_from_texts()` 的 `continue` 语句需要移除或改为 fallthrough 到 keyword family check。新增测试：`8.3 任意无关文本` 应 blocked，`8.4 报告期末按行业分类的股票投资组合` 应映射为 `§8`。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 高

### 02-未修复-中-新增 fail-closed reason codes 缺少对应测试规格

- **位置**: Slice 5: Blocked Reason Taxonomy, Tests and Validation Commands
- **问题类型**: 测试缺口
- **当前写法**: Slice 5 新增 6 个 blocked reason codes（`duplicate_section_heading`, `section_order_not_monotonic`, `section_span_crosses_multiple_sections`, `unsupported_heading_number` 等）。Tests 章节列出了 `duplicate same-section headings block propagation` 和 `out-of-order section nodes block propagation` 两条测试意图。
- **反例/失败场景**: Plan 未为 `section_order_not_monotonic`、`unsupported_heading_number`、`duplicate_section_heading` 提供具体的 synthetic test fixture 规格（输入 section node 结构、预期 reason code）。Implementation agent 可能只写 happy-path 测试或用模糊 assertion。
- **为什么有问题**: 这些 reason codes 是 fail-closed 行为的可审计证据。如果测试只验证 reason code 存在而不验证触发条件的精确边界（如"两个 section node normalize 到同一 §X 但 section_id 不同"触发 `duplicate_section_heading`），则无法证明 fail-closed 是确定性的。
- **直接证据**: Plan Tests 章节列出了 9 条测试意图，但只有 2 条涉及新增 fail-closed codes。现有测试 `test_docling_evidence_anchor_mapping.py` 不覆盖任何新增 reason codes。
- **影响**: Implementation agent 可能产出只覆盖 happy-path 的测试套件，新增 fail-closed reason codes 成为 untested dead code。
- **建议改法和验证点**: 为每个新增 reason code 至少提供一个 synthetic test case 的输入/输出规格。特别是：(1) `duplicate_section_heading` — 两个 section node 都 normalize 到 `§8` 但 section_id 不同；(2) `section_order_not_monotonic` — `§8` 出现在 `§3` 之前；(3) `unsupported_heading_number` — heading 如 `11.1 xxx` top-level 超出 1..10。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 03-未修复-中-Slice 2 section index 构建规则缺少 page-based propagation 边界测试

- **位置**: Slice 2: Stable Section Index, Slice 3: Section Propagation
- **问题类型**: 测试缺口
- **当前写法**: Slice 2 定义了 section span 计算规则（page start 到下一 stable section start 的前一页）。Slice 3 定义了 page-based nearest previous section propagation 和 cross-section span blocking。
- **反例/失败场景**: Plan 未为以下关键场景提供 test fixture 规格：(1) table 的 page range 跨两个 stable section span 时 blocked 为 `section_span_crosses_multiple_sections`；(2) block 无 page number 且无 explicit section context 时 blocked 为 `missing_section_context`；(3) table pages 全部落在一个 stable section span 内时正确继承。
- **为什么有问题**: Slice 2/3 是 table/cell yield 从零到非零的关键路径。如果 implementation agent 只测试 heading normalization（Slice 1）而不精确测试 section index + propagation 逻辑，则 table/cell yield 可能通过非确定性手段（如 fallback to heading_path keyword match）实现，而非 plan 设计的 page-based propagation。
- **直接证据**: Plan Tests 章节列出了 `table without own heading path inherits nearest stable section by page span` 和 `table spanning two stable section spans blocks` 两条意图，但未给出具体 fixture 结构。现有测试不涉及 section index 或 page-based propagation。
- **影响**: Table/cell yield 可能通过意外路径实现，re-evidence 无法区分"正确 propagation"和"keyword match fallback"。
- **建议改法和验证点**: 为 page-based propagation 提供最小 synthetic fixture：2 个 section nodes（§3 page 10, §8 page 60）、1 个 table（page 62，无 heading_path）、1 个 table（page 58-62，跨 §5/§8 边界）。前者应映射为 §8，后者应 blocked。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 04-未修复-低-_section_candidates_from_block 包含 cell 行为规格但 plan 禁止该路径

- **位置**: Slice 4: Cell Section Inheritance From Parent Table Only
- **问题类型**: 过度耦合 / 代码残留
- **当前写法**: Plan 明确规定"Cells must inherit annual-report section context from their resolved parent table. Do not infer annual-report section from `row_label_path`, `column_header_path` or cell text"。
- **反例/失败场景**: 现有 `_section_candidates_from_block()` 的 `CandidateTableCell` 分支（line 550-551）从 `row_label_path` 和 `column_header_path` 提取 section candidates。当前 `_map_cell` 不调用 `_resolve_section_id`，所以该分支对 cell 是 dead code。但如果未来重构引入新调用路径，cell label 中的 `§` token（如 `row_label_path=["§8 股票A"]`）会产生 false section candidate。
- **为什么有问题**: Plan 声称 cell section 来源唯一（parent table），但未要求 implementation agent 清理 `_section_candidates_from_block` 中的 cell 分支。这不是当前 bug，但是 latent risk。
- **直接证据**: `evidence_anchor_mapping.py:550-551` — cell 分支从 `row_label_path`/`column_header_path` 提取。Plan Slice 4："Do not infer annual-report section from `row_label_path`, `column_header_path` or cell text"。
- **影响**: 低。当前代码路径安全（`_map_cell` 不走 `_resolve_section_id`），但代码与 plan 声称的 invariant 不完全一致。
- **建议改法和验证点**: 可接受为 defer-candidate。Implementation agent 可选择：(A) 移除 cell 分支；(B) 在 cell 分支加注释标注 dead code 且受 Slice 4 约束；(C) 加测试证明 cell 不从 label 推断 section。推荐 (C) 作为最低验证。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Findings Summary Table

| # | 严重程度 | 位置 | 简述 |
| --- | --- | --- | --- |
| 01 | 高 | Slice 1 | numeric heading 关键词族校验未闭合，plan 未标注需修改现有代码 |
| 02 | 中 | Slice 5 / Tests | 新增 fail-closed reason codes 缺少对应 synthetic test 规格 |
| 03 | 中 | Slice 2/3 / Tests | page-based section propagation 缺少边界测试 fixture 规格 |
| 04 | 低 | Slice 4 | cell 分支 dead code 与 plan invariant 不完全一致 |

## Open Questions

| # | Question | Why it matters |
| --- | --- | --- |
| O1 | Slice 2 要求"positive page start"，但现有 `_resolve_section_id` 不检查 page positivity。Plan 是否要求在 section index 构建时过滤 page=None 的 section nodes？ | Implementation agent 可能不过滤，导致 section span 计算包含无 page 的 node。 |
| O2 | Slice 1 alias additions（§2: 基金基本情况, §8: 报告期末按行业分类的股票投资组合 等）是否应作为新的 keyword families 加入 `_SECTION_KEYWORD_FAMILIES`，还是作为独立 alias dict？ | 影响 implementation agent 的具体代码位置选择。 |

## Residual Risks

| Risk | Severity | Tracking destination |
| --- | --- | --- |
| Numeric heading false-positive mapping if keyword family check not closed | 高 | Implementation gate — requires explicit code change callout |
| Section index construction untested on real artifact shapes | 中 | Re-evidence gate |
| Page-based propagation correctness unproven until re-evidence | 中 | Re-evidence gate |
| S1 full JSON remains blocked; separate gate needed for regeneration/export | 低 | Deferred gate per plan Slice 6 |
| Table/cell yield does not prove field correctness | 低 | Future comparative correctness gate |

## Plan Review Conclusion

**pass-with-risks**

Plan 的整体设计合理：candidate-only 边界清晰、write set 窄、fail-closed 原则一致、S1 full JSON disposition 正确、re-evidence 设计可操作。主要风险是 Finding 01（numeric heading 关键词族校验未闭合）可能导致 implementation agent 不修改现有 `_section_candidates_from_texts` 逻辑，从而引入 false-positive section mapping。Findings 02/03 是测试覆盖缺口，可在 implementation gate 补充。Finding 04 是 latent dead code risk，可接受为 defer。

Controller 应在 implementation gate 前确认 Finding 01 的修复要求，并在 implementation gate 验收时检查新增 fail-closed reason codes 的测试覆盖。

## Final Verdict

```text
PASS_WITH_FINDINGS_NOT_READY
```
