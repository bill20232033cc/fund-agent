# Post-P13 Follow-up Plan Re-review — AgentGLM（2026-05-22）

## Verdict

`PASS`

原始 4 个 finding（F1-F4）全部关闭。修订未引入新 blocker。

## Review Target

- `docs/reviews/post-p13-follow-up-planning-20260522.md`（修订版）

## Source Review

- `docs/reviews/post-p13-follow-up-plan-review-glm-20260522.md`

## Finding Closure Assessment

### F1（Medium）：UNMAPPED priority 未显式命名 → CLOSED

修订响应：

- Verdict 段落显式点名"FQ2 `FIELD_PRIORITY_BY_NAME` / `ExtractionScore` 中仍可能落入 `UNMAPPED` 或未定义优先级"。
- "Quality Denominator Definition" 表 FQ2 行要求"必须为 `index_profile` / `tracking_error` 选择 priority behavior，消除 implementation plan 中的 `UNMAPPED` 模糊性"。
- 约束 #3"FQ2 priority 决策"要求"必须消除 `index_profile` / `tracking_error` 的 `UNMAPPED` 模糊性"，并列出四种选项（P0/P1/P2/继续 UNMAPPED 且显式排除/按基金类型条件化）。条件化路径显式列出实现区域：`FIELD_PRIORITY_BY_NAME`、`_evaluate_field_score`、`_build_score_row`、`_missing_fields_by_priority`。

结论：UNMAPPED 被显式命名、被要求消除、实现路径被精确指向。F1 关闭。

### F2（Medium）：ExtractionMode `missing` 与 `not_applicable` 合并风险 → CLOSED

修订响应：

- 新增约束 #7"非指数与 not_applicable 语义"：显式引用当前 `ExtractionMode` 枚举值，要求二选一裁决——(a) 扩展 `ExtractionMode` 增加 `not_applicable`，或 (b) 保持 enum 不变用 `classified_fund_type` / applicability matrix 排除非适用字段。
- 约束 #7 同时要求写清 trade-off："扩 enum 会触及 extractor/model/consumer/test 面，保持 enum 则要防止 non-index missing 被 FQ2 误计为质量失败"。

结论：二选一裁决 + trade-off 分析的要求完全覆盖 F2 的 required change。F2 关闭。

### F3（Low）：条件化 priority 实现复杂度未显式提及 → CLOSED

修订响应：

- 约束 #3 条件化路径要求"必须说明实现区域是 `FIELD_PRIORITY_BY_NAME`、`_evaluate_field_score` / `_build_score_row` / `_missing_fields_by_priority` 或等价 scoring logic，而不是只改文案"。
- 比原始要求更进一步：不仅点名了函数，还排除了"只改文案"的逃避路径。

结论：实现复杂度已被显式提及并精确指向代码位置。F3 关闭。

### F4（Low）：enhanced_index fixture 可用性需确认 → CLOSED

修订响应：

- 约束 #10"Fixture 策略"：明确"enhanced_index fixture 当前不能假设已存在，plan 必须先证明已有 fixture 覆盖 enhanced_index，或最小新增一个 deterministic fixture"。
- Exit criteria behavioral assertions："enhanced_index applicable path is covered by an existing fixture or by a minimal new deterministic fixture"。

结论：enhanced_index fixture 可用性被明确要求确认，不存在假设已有的漏洞。F4 关闭。

## New Blocker Check

修订版主要新增了以下内容：

- "Quality Denominator Definition For P14-S1" 三机制表（FQ2、comparable、golden correctness），每个机制绑定代码位置和 scope/exclusion 边界。
- 约束从 10 条扩展到 16 条，新增 FQ2 priority 决策、comparable sub-fields 决策、golden correctness 决策、非指数 not_applicable 语义、缺失与冲突语义、validation / exit criteria、required behavior assertions 共 7 条。
- "Required P14-S1 Plan Exit Criteria" 新增独立段落，列出验证命令、行为断言和 baseline 要求。

逐项检查：

| 新增内容 | 是否引入 scope creep | 是否违反设计约束 | 是否引入新 blocker |
|----------|---------------------|-----------------|-------------------|
| 三机制表 | 否。只引用已有代码机制 | 否。绑定到实际代码位置 | 否 |
| 约束 #3-#7（FQ2/comparable/golden/applicability/ExtractionMode） | 否。只消费已有字段 | 否。保持 Fund Capability ownership | 否 |
| 约束 #8-#16 | 否。是现有约束的精确化 | 否。保持所有设计边界 | 否 |
| Exit criteria 段落 | 否。只列验证命令和断言 | 否 | 否 |

**结论：无新增 blocker。**

## Summary

F1-F4 全部关闭，修订质量高——每个 finding 都被精确响应，且新增内容（三机制表、扩展约束、exit criteria）进一步加强了 P14-S1 plan handoff 的确定性。Verdict: `PASS`。

**不修改生产代码，不提交，不 push，不创建 PR。**
