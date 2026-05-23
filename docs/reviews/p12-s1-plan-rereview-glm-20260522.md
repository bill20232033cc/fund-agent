# P12-S1 Plan Re-Review — AgentGLM（2026-05-22）

- **Reviewer**: AgentGLM（独立 plan re-reviewer）
- **Original review**: `docs/reviews/p12-s1-plan-review-glm-20260522.md`
- **Revised plan**: `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md`
- **Code baseline**: `79fb3e3`

---

## Verdict: **PASS**

修订计划逐条解决了初审全部 5 项 finding，无残留阻断项。

---

## Finding 1 (原 MEDIUM): missing-data 路径与 audit fail-closed — **已解决**

修订采用了初审推荐的 Route A，引入 `TemplateItemRuleAuditContext = Literal["identity_missing", "identity_present"]`：

- §4.1 明确定义了 renderer 在三种 identity 状态下的行为：identity 缺失 → `identity_missing` + 空决策；identity 存在且有效 → `identity_present` + 评估结果；identity 存在但无效 → `ValueError`。
- §4.3 显式采用 Route A 三分支逻辑：`identity_missing` + 空决策 → 跳过 issue；`identity_present` + 空决策 → C2 issue；`identity_present` + 非空 → 执行合规检查。
- §5 Slice 3 兼容性注释详细说明了现有直接构造 `ProgrammaticAuditInput` 的测试如何通过默认 `identity_missing` 避免大面积 fixture 修改。
- §8 验收标准 #8 显式要求两条路径都通过测试。

初审指出的三处语义张力已消除。

---

## Finding 2 (原 MEDIUM): 段落内容渲染规则 — **已解决**

修订计划补充了完整的段落格式规范：

- §4.2 明确规则："each segment is a heading followed by a fixed ordered set of `- key：value。` bullets, with no free prose paragraphs."
- §4.2 给出了四个段落的完整 Markdown 模板样例，包含具体 bullet key。
- §4.2 Evidence strategy 部分逐条规定了每个段落的证据使用边界（如 benchmark anchors 不证明成分股/编制方法）。
- §5 Slice 2 step 4 重申了固定格式约束。
- §8 验收标准 #6 明确禁止自由 prose 和推断值。

初审提出的三个具体疑问（段落格式、bullet 数量、证据行位置）均已回答。

---

## Finding 3 (原 LOW): 类型标注 — **已解决**

修订计划将所有 `tuple[TemplateItemRuleDecision, ...] | ()` 统一修正为 `tuple[TemplateItemRuleDecision, ...] = ()`，出现在 §4.1、§5 Slice 1 step 4、§5 Slice 3 step 1。有歧义的联合类型标注已消除。

---

## Finding 4 (原 LOW): audit marker 检查范围 — **已解决**

修订计划 §4.3 显式要求：

> Audit must match `decision.chapter_id` to the corresponding `RenderedChapterBlock` and inspect only that block's `body_markdown` through `rendered_segment_present(block.body_markdown, rule)`. It must not scan global `report_markdown` for ITEM_RULE markers.

§8 验收标准 #10 同步要求检查 `body_markdown` 而非全局 markdown。

---

## Finding 5 (原 LOW): tracking error 永久 data-insufficient — **已解决**

修订计划在多处显式标注 tracking error 为确定性占位：

- §4.2 表格：`deterministic data-insufficient placeholder until a tracking-error extractor exists`
- §4.2 Evidence strategy：`may cite benchmark/RABC anchors only to identify the relevant index context, not to prove tracking error`
- §6 Edge Cases `enhanced_index` 行和 `Tracking error data absent` 行
- §5 Slice 2 step 6 和 §8 验收标准 #12

---

## 新增内容评估

修订计划新增了初审未覆盖的以下内容，均合理：

1. **六基金类型表驱动测试矩阵**（§5 Slice 1 step 7、Slice 3 step 4）：不仅覆盖 active/index/enhanced，还覆盖 bond/qdii/fof 的全删除行为。这比初审建议的"至少一种非触发类型"更全面。

2. **`docs/implementation-control.md` 明确排除**（§9 Stop Conditions 最后一项）：防止实现 agent 擅自修改控制文档。这与 P11 的文档卫生精神一致。

3. **`item_rule_audit_context` 类型定义位置**（§5 Slice 1 step 3）：建议放在 `fund_agent/fund/template/item_rules.py` 而非 renderer 私有模块，确保 audit 和 renderer 共享同一类型定义。这是正确的边界选择。

---

## 总结

| Finding | 原 Severity | 状态 |
|---------|------------|------|
| 1. missing-data 与 audit fail-closed 冲突 | MEDIUM | 已解决（Route A） |
| 2. 段落渲染格式不具体 | MEDIUM | 已解决（固定模板 + evidence strategy） |
| 3. 类型标注歧义 | LOW | 已解决 |
| 4. audit marker 检查范围 | LOW | 已解决 |
| 5. tracking error 占位标注 | LOW | 已解决 |

无残留阻断项，计划可进入实现阶段。
