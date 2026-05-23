# Post-P13 Follow-up Plan Re-Review — AgentMiMo（2026-05-22）

## Verdict

`PASS`

所有 6 个 findings 均已在修订后的 planning artifact 中闭环。无新增 blocker。

## Re-review Target

- `docs/reviews/post-p13-follow-up-planning-20260522.md`（修订版）

## Source Review

- `docs/reviews/post-p13-follow-up-plan-review-mimo-20260522.md`

## Findings Disposition

### F-1: "Quality denominator" 概念未定义 — CLOSED

**原文要求**: 明确"quality denominator"对应的具体代码机制。

**修订响应**: 新增独立 section "Quality Denominator Definition For P14-S1"（第 106-115 行），以表格形式显式列出三个实际机制：

| 机制 | P14-S1 scope | Explicitly not in scope |
|---|---|---|
| FQ2 priority / extraction score | 为两字段选择 priority behavior | 不新增 FQ rule family |
| Snapshot comparable values | 决定哪些子字段进入白名单 | 不把整块 nested value 直接放入 |
| Golden correctness | 决定是否新增 GoldenAnswerRecord | 不扩展 golden schema |

并以"不得继续使用'等价 denominator'绕开实际机制"收口。

**判定**: CLOSED。三个机制均有 current implementation 引用和 scope/in-scope 边界。

---

### F-2: FQ2 优先级分配未指定 — CLOSED

**原文要求**: 指定 FQ2 优先级和非指数基金 not_applicable 时的 gate 行为。

**修订响应**: Required Constraints #3 要求"消除 `UNMAPPED` 模糊性"，列出 P0/P1/P2/UNMAPPED/条件化 五种选择，并要求指定实现区域。Required Constraint #6 要求适用性矩阵覆盖全部 6 类基金。Required Constraint #7 要求二选一：扩展 `ExtractionMode` 增加 `not_applicable`，或保持 enum 不变并用 applicability matrix 排除。Exit criteria behavioral assertions 要求"non-index paths are excluded / not_applicable, not silently counted as FQ2 failures"。

**判定**: CLOSED。P14-S1 plan 必须在进入 implementation 前回答这些问题。

---

### F-3: 非指数基金路径 stop condition 不明确 — CLOSED

**原文要求**: 明确 not_applicable 路径在 FQ2/golden/comparable 中的处理策略。

**修订响应**: Required Constraints #6 和 #7 联合覆盖。#6 要求适用性矩阵明确每类基金的 expected denominator behavior；#7 要求在扩展 ExtractionMode 或保持 enum + applicability matrix 之间做出显式 trade-off 决策。Exit criteria 要求"active/bond/QDII/FOF non-index paths are excluded / not_applicable according to the selected semantics"。

**判定**: CLOSED。

---

### F-4: 缺少明确退出条件 / 正面验收标准 — CLOSED

**原文要求**: 添加退出条件。

**修订响应**: 新增独立 section "Required P14-S1 Plan Exit Criteria"（第 193-213 行），包含：
- Validation commands：7 类具体测试命令（snapshot、FQ2、golden、P3 matrix、quality gate、ruff、full suite）
- Baseline：不低于 P13 closeout 的 `424 passed`
- Behavioral assertions：8 条具体断言覆盖 index_fund disclosed、enhanced_index、non-index、missing、conflicting、comparable_values、golden match/mismatch/unavailable、full suite no regression

**判定**: CLOSED。Exit criteria 可直接验证。

---

### F-5: Fixture 策略缺乏现有基础设施衔接 — CLOSED

**原文要求**: 说明 fixture 策略与 P3 矩阵和 golden answer JSON 的衔接方式。

**修订响应**: Required Constraint #10 明确要求"基于现有 P3/sample matrix 和 golden answer JSON 说明 fixture 来源"。显式提到 `510300` 作为 index_fund disclosed tracking_error path 候选。要求 enhanced_index fixture 先证明已有覆盖或最小新增。Exit criteria 要求 `510300` 或其他显式选择的 index_fund fixture 覆盖 disclosed tracking_error 和 expected index_profile comparable sub-fields。

**判定**: CLOSED。

---

### F-6: Candidate Comparison 表对 "promote" 表述模糊 — CLOSED

**原文要求**: 区分 snapshot observability（已有）和 comparable/golden correctness（待建）。

**修订响应**:
- Candidate Comparison 表选中行已改为"`index_profile` / `tracking_error` comparable / golden / FQ2 coverage"（原为"Snapshot promotion"）
- Verdict 改为"补齐质量覆盖缺口"并明确"缺口不是'进入 snapshot'，而是...未进入 `COMPARABLE_SUB_FIELDS_BY_FIELD`、`GoldenAnswerRecord` / golden answer JSON correctness，且在 FQ2 `FIELD_PRIORITY_BY_NAME` 中仍可能落入 `UNMAPPED`"
- Explicit Out-of-scope 新增"泛化地把字段'提升进 snapshot'的表述；P13 已有 snapshot observability，P14-S1 只讨论明确选中的 comparable sub-fields、golden correctness 和 FQ2 priority"

**判定**: CLOSED。

---

## Summary

| Finding | Severity | Status |
|---|---|---|
| F-1 | HIGH | CLOSED |
| F-2 | HIGH | CLOSED |
| F-3 | MEDIUM | CLOSED |
| F-4 | MEDIUM | CLOSED |
| F-5 | LOW | CLOSED |
| F-6 | LOW | CLOSED |

## New Blockers

无。修订未引入新的 blocker。

## Recommended Next Action

Proceed to `P14-S1 index_profile / tracking_error quality-denominator plan-review`。
