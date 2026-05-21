# P12-S1 Plan Review — AgentGLM（2026-05-22）

- **Reviewer**: AgentGLM（独立 plan reviewer）
- **Plan artifact**: `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md`
- **Planning context**: `docs/reviews/post-p11-second-follow-up-planning-20260522.md`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Code baseline**: `79fb3e3`

---

## Verdict: **PASS_WITH_FINDINGS**

计划整体结构清晰，尊重确定性 MVP 边界，正确避免了 LLM/facet inference，模块边界和切片依赖关系合理。以下 5 项 finding 需要在实现前或实现中解决，其中 1 项 MEDIUM 可能影响现有测试兼容性。

---

## Finding 1: MEDIUM — missing-data 路径与 audit fail-closed 存在语义冲突

### 证据

Plan §4.1 说：

> If `basic_identity.value is None`, renderer may return no ITEM_RULE decision plan, matching the current missing-data path.

Plan §4.3 说：

> If decisions are absent while report Markdown/chapter blocks exist, audit should not silently pass ITEM_RULE compliance. Preferred implementation: add a C2 issue.

Plan §5 Slice 3 兼容性注释说：

> the fail-closed "missing ITEM_RULE decisions" check should trigger only when enough report/chapter input exists to claim C2 compliance.

三处表述存在逻辑张力。当前 missing-data 报告（`basic_identity.value is None`）会正常产生 8 章报告和 chapter_blocks。如果此时 `item_rule_decisions = ()`，audit 按 §4.3 应输出 C2 issue。但 `run_programmatic_audit()` 当前 `_issue()` 默认 severity 为 `blocker`，这意味着 missing-data 报告会从 C2 pass 变为 C2 fail，构成行为回归。

### 分析

这不是不可解决的问题，但 plan 应当显式裁决以下两条路线之一：

1. **路线 A**：C2 ITEM_RULE missing-decision 检查区分"identity 缺失"和"identity 存在但 renderer 未传递 decisions"。前者不触发 issue（因为 renderer 正确返回了空元组），后者触发 blocker issue。需要 audit 能区分这两种状态。
2. **路线 B**：所有 C2 ITEM_RULE missing-decision issue 一律为 `reviewable` severity，不阻断。renderer 路径验证由 `TemplateRenderResult.item_rule_decisions` 的 `ValueError` fail-closed 保证。

### 建议修复

推荐路线 A，与 plan 的 fail-closed 精神一致。具体做法：`ProgrammaticAuditInput` 增加 `item_rule_identity_missing: bool = False`，renderer 在 `basic_identity.value is None` 时设为 `True`。Audit 检查时：若 `item_rule_identity_missing is True`，跳过 ITEM_RULE missing-decision issue（等同于 lens plan 为 `None` 时 audit 不检查 lens 应用）。

如果选择路线 B，需在 plan 中声明这是有意降低 severity，并在实现中确保 `_issue()` 调用显式传 `severity="reviewable"`。

---

## Finding 2: MEDIUM — 条件型段落内容渲染规则不够具体

### 证据

Plan §4.2 对 `chapter_1_index_constituents` 说：

> Use benchmark/product profile evidence already available; if detailed constituents are absent, write `数据不足` with evidence line rather than invent constituents.

Plan §4.2 对 `chapter_1_manager_philosophy` 说：

> Use `manager_strategy_text` only as disclosed strategy source; if absent, write `未披露`/`数据不足` with evidence preservation.

### 分析

当前 renderer 的所有 chapter 内容都是 deterministic bullet-point 模板填充，使用 `_value_text()` / `_ratio_text()` / `_INSUFFICIENT_TEXT` 等固定模式。Plan 说了"用什么数据"和"缺数据怎么办"，但没说明"段落长什么样"。

具体疑问：

1. 段落是单行 bullet（`- 基金经理投资哲学：{text}`），还是独立 `####` 小节下包含多行内容？
2. 如果是 `####` 小节，正文结构是什么？需要几个固定 bullet？
3. 证据行是在小节内部追加独立 `> 📎 证据` 行，还是复用章节末尾已有的 evidence line？

Plan §4.2 明确要求 heading 格式为 `#### 指数编制规则与成分股` 等，且 §4.3 要求 audit 通过 `segment_markers_any` 检测这些 heading。因此段落必须至少包含 heading。但 heading 以下的正文结构未指定。

### 建议修复

Plan 不需要写出完整 Markdown 样例，但应补充以下规则：

1. 每个 ITEM_RULE 段落格式固定为 `#### {heading}\n- {item_title}：{deterministic content}`。
2. `{deterministic content}` 使用现有 `_value_text()` / `_INSUFFICIENT_TEXT` 模式，不自由生成 prose。
3. 证据行沿用章节末尾的 `_evidence_line()`，不在小节内独立追加（保持与现有章节结构一致）。如果小节确实携带独立 evidence anchor，则在小节内追加 `> 📎 证据` 行。

---

## Finding 3: LOW — `item_rule_decisions` 类型标注需澄清

### 证据

Plan §4.1 说：

> `TemplateRenderResult` should expose `item_rule_decisions: tuple[TemplateItemRuleDecision, ...] | ()`

### 分析

`tuple[TemplateItemRuleDecision, ...] | ()` 在 Python type 注解中含义不明确。`()` 是 `tuple[()]` 类型（空元组），不是 `tuple[TemplateItemRuleDecision, ...]` 的子类型。正确的标注应该是 `tuple[TemplateItemRuleDecision, ...]`，默认值为 `()`。

类似地，`ProgrammaticAuditInput.item_rule_decisions` 应为 `tuple[TemplateItemRuleDecision, ...] = ()`。

### 建议修复

统一为 `item_rule_decisions: tuple[TemplateItemRuleDecision, ...] = ()`。Plan §4.1 和 §5 Slice 3 应修正此标注。

---

## Finding 4: LOW — audit segment marker 检查范围应为 chapter block body

### 证据

Plan §4.3 说：

> For each decision with `status="render"`, exactly require that at least one configured `segment_markers_any` exists in the matching chapter block.

当前 `rendered_segment_present()` 实现是：

```python
return any(marker in markdown for marker in rule.segment_markers_any)
```

它接受完整 markdown 字符串。

### 分析

如果 audit 直接调用 `rendered_segment_present(report_markdown, rule)` 而非 `rendered_segment_present(block.body_markdown, rule)`，那么第 1 章的 marker 可能意外匹配到第 2 章的同名文本（虽然当前 heading 格式足够唯一，不太可能误匹配）。Plan 应显式要求 audit 按 `chapter_id` 匹配 block 后，只在对应 block 的 `body_markdown` 内检查 marker，而非全局检查。

### 建议修复

Plan §4.3 应补充："Audit 按 `decision.chapter_id` 匹配对应 `RenderedChapterBlock`，然后在该 block 的 `body_markdown` 中检查 `segment_markers_any`，不使用全局 report markdown。"

---

## Finding 5: LOW — `chapter_2_tracking_error_analysis` 对 index/enhanced 基金是永久 data-insufficient 段落

### 证据

Plan §4.2 说：

> Current P1/P2 does not provide tracking error, so render an explicit data-insufficient segment with benchmark/RABC evidence where available; do not calculate or infer tracking error.

### 分析

这意味着 `chapter_2_tracking_error_analysis` 段落对于 `index_fund` 和 `enhanced_index` 将始终渲染一个 heading + "数据不足" 的段落。Audit 会验证 marker 存在（render decision triggered → heading 必须出现），但内容永远是缺数据状态。

这不是 bug——plan 正确选择了不伪造数据——但应在 README 更新或 plan 边界条件中注明：tracking error 段落当前为确定性占位，待后续 P1 extractor 补充 tracking error 数据后才能输出实质内容。

### 建议修复

Plan §6 Edge Cases 的 `index_fund` / `enhanced_index` 行应注明：`跟踪误差分析` 段落当前为 data-insufficient 占位，不是完整的跟踪误差分析。

---

## 正面评估

以下方面 plan 处理得当：

1. **单一决策真源**：renderer 和 audit 消费同一份 `TemplateItemRuleDecision` 元组，避免"渲染按一套逻辑、审计按另一套逻辑"。这与 `rabc_attributions` / `checklist_result` 的现有模式一致。

2. **`_resolve_item_rule_decisions` 镜像 `_resolve_lens_application_plan`**：missing identity → 空决策，present identity 但 missing type → ValueError fail-closed。与现有 lens 解析路径行为完全对称。

3. **Facet 推断硬禁止**：`facets=()` 强制为空，renderer 不从 prose/fund name/category/benchmark 推断 facet。这正确遵守了 design.md §6.3 的"细分风格必须先形成单独设计 slice"约束。

4. **FQ5/quality gate 不变**：plan 正确区分了"模板契约适用性"（FQ5）和"渲染合规性"（programmatic audit C2），不扩大 FQ5 语义范围。

5. **Slice 依赖关系正确**：Slice 1（plumbing）→ Slice 2（segments）→ Slice 3（audit）→ Slice 4（docs）。Slice 3 可以在 Slice 1 完成后独立开始测试（用 mock decisions），不必等 Slice 2。

6. **bond/qdii/fof 行为**：四个 conditional ITEM_RULE 的 `fund_types_any` 均不包含这三种类型，因此所有 rule 的 status 为 `delete`，audit 验证 marker 不出现。当前 renderer 不产生这些段落，plan 只是让这个"不产生"变成可审计的。

7. **不违反 deterministic MVP 约束**：无 LLM、无 Host/Engine/tool loop、无 Dayu runtime、无 Service/UI/CLI 变更、无 `FundDocumentRepository` 边界突破。

---

## 总结

| # | Severity | Finding | 修复建议 |
|---|----------|---------|---------|
| 1 | MEDIUM | missing-data 路径与 audit fail-closed 语义冲突 | 区分 identity-missing 和 identity-present-but-decisions-empty 两种状态，前者不触发 C2 ITEM_RULE issue |
| 2 | MEDIUM | 段落内容渲染规则不够具体 | 补充固定格式规则：heading + deterministic bullet + evidence 模式 |
| 3 | LOW | 类型标注 `tuple[...] \| ()` 含义不明 | 统一为 `tuple[TemplateItemRuleDecision, ...] = ()` |
| 4 | LOW | audit marker 检查范围应为 block body | 显式要求按 chapter_id 匹配 block 后检查 body_markdown |
| 5 | LOW | tracking error 段落永久 data-insufficient | 在 edge case 表中注明为确定性占位 |

Finding 1 和 2 应在实现开始前由 plan 作者补充裁决。Finding 3-5 可在实现中直接处理。
