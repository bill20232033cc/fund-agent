# Drawdown Stress NAV-Derived Metric Implementation Plan — Rereview (GLM)

日期：2026-05-29
角色：plan rereview worker only。不做实现、修复、commit、push、PR、merge、release、golden promotion。
Gate：`drawdown_stress NAV-derived metric contract / implementation gate`
Gate classification：`heavy`

---

## 0. Rereview 范围

本 rereview 验证 updated plan 对 controller disposition 指定修复项的落实情况。

Inputs：
- Updated plan：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md`
- GLM 初审：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-glm-20260529.md`
- MiMo 初审：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-mimo-20260529.md`

Controller disposition：
- MiMo 01 → accepted as required plan fix
- MiMo 02-04、GLM N1-N5 → non-blocking，fold where cheap

---

## 1. Plan Fix Notes 是否存在

**Confirmed。**

Updated plan 第 9-17 行新增 `## Plan Fix Notes`，列出 5 项修复：

1. MiMo 01 修复：`quantitative_derived` 必须 paired with `derived_metric`
2. MiMo 02 折叠：repository vs helper `minimum_records` 语义澄清
3. MiMo 03 / GLM N3 折叠：derived anchor snapshot stop condition
4. GLM N4 折叠：score regression test
5. Slice 4 / evidence 边界收紧

Plan Fix Notes 覆盖了 controller disposition 的全部要求。

---

## 2. Validator Contract 是否精确防止 accepted + quantitative_derived + 非 derived_metric

**Confirmed。**

Updated plan § Contract / Projection Into bond_risk_evidence.v1，第 188 行新增：

> `_validate_bond_risk_status_strength()` 必须额外强制：只要 `strength=="quantitative_derived"`，`measurement_kind` 必须等于 `"derived_metric"`；`status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="actual_metric"`、`"actual_exposure"` 或其他 measurement kind 必须 fail validation。

该约束精确覆盖了 MiMo 01 的要求：
- 正向：`accepted + quantitative_derived + derived_metric` 通过
- 反向：`accepted + quantitative_derived + actual_metric` 被拒绝
- 反向：`accepted + quantitative_derived + actual_exposure` 被拒绝
- 反向：`accepted + quantitative_derived + 任何其他 measurement_kind` 被拒绝

该约束独立于现有的 `accepted → strength ∈ accepted_set` 检查，形成双重防护。Implementation worker 必须在 `_validate_bond_risk_status_strength()` 的 `accepted` 分支内新增一个条件：`if strength == "quantitative_derived" and measurement_kind != "derived_metric": raise`。

---

## 3. Required Reject Test 是否存在

**Confirmed。**

Updated plan § Required Tests #9，第 449-451 行新增 reject test：

> `validate_bond_risk_evidence_value()` rejects `status="accepted"`, `strength="quantitative_derived"`, `measurement_kind="actual_metric"`; equivalent non-`derived_metric` measurement kinds must not pass as accepted derived metrics.

该测试要求：
- 构建 `status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="actual_metric"` 的 record
- 验证 `validate_bond_risk_evidence_value()` 抛出 validation error
- 等价地覆盖其他非 `derived_metric` measurement_kind

与 MiMo 01 要求的验证点完全匹配。

---

## 4. Repository minimum_records vs Metric Helper minimum_records 是否清晰且有测试

**Confirmed。**

Updated plan 在三处澄清了两者区别：

**§ Core Decisions #3 Period，第 133 行：**

> repository `minimum_records` 是 full-series early sanity check，只证明 source 返回的整体 series 不是空壳；metric helper 的 `minimum_records` 是 period-filtered final check，必须独立执行，不能因为 repository 已传 `minimum_records=30` 就跳过。

**§ Formula 步骤 3，第 143 行：**

> 若过滤后记录数 `< minimum_records`，fail-closed `insufficient_records`；这里的 `minimum_records` 指 period-filtered records 数量，不是 repository 对 full series 做的 early sanity check。

**§ Required Tests #2，第 425 行：**

> full series has `>=30` records but period-filtered records have `<30` records must fail closed in the metric helper; this proves repository `minimum_records` and metric helper `minimum_records` are independent checks.

三处形成完整闭环：定义、算法步骤、测试。完全折叠 MiMo 02。

---

## 5. Derived Anchor Snapshot Stop Condition 和 Score Regression Test 是否存在

**Confirmed。**

**Derived anchor stop condition** 出现在三处：

1. § Anchor / Provenance Format，第 255 行：
   > if snapshot projection assumes `source_kind="annual_report"` or rejects `section_id="derived:nav"`, stop for controller instead of changing schema or weakening projection semantics.

2. Slice 2 stop condition，第 531 行：
   > if snapshot validator rejects derived anchor shape, stop for controller rather than weakening anchor validation.

3. Slice 4 stop condition，第 565 行：
   > If snapshot projection assumes annual-report source_kind or rejects `derived:nav`, stop for controller unless the needed production change is a narrow projection compatibility fix with tests and no schema change.

第三处还补充了"narrow compatibility fix"例外路径：如果 snapshot 只需小幅适配（不改变 schema），可以继续但必须有测试覆盖。这比初审的 stop condition 更精确，合理。

**Score regression test** 出现在两处：

1. § Required Tests #8，第 447 行：
   > regression failure path: when the other six groups are satisfied but `drawdown_stress` is the only weak/missing/ambiguous/absent group, `derive_score_applicability_issues()` must still emit `bond_risk_evidence_missing` with `missing_evidence_groups=("drawdown_stress",)`。

2. Slice 4 changes，第 561 行：
   > Add score regression test that drawdown-only unsatisfied groups still produce `bond_risk_evidence_missing`.

完全折叠 GLM N4（初审建议增加的 regression test）。

---

## 6. 是否有新 scope expansion / score/quality/golden weakening / changed core decisions

**Confirmed：无。**

逐项检查：

| 检查项 | 结果 |
|--------|------|
| Core Decision 1（max drawdown alone） | 未变 |
| Core Decision 2（006597/A only） | 未变 |
| Core Decision 3（2024 annual period） | 未变，增加了 minimum_records 澄清 |
| Core Decision 4（formula） | 未变，步骤 3 增加 minimum_records 语义注释 |
| Core Decision 5（volatility non-goal） | 未变 |
| Data Boundary | 未变 |
| Contract Extension | 增加 validator 约束（strengthening，非 weakening） |
| Non-Goals | 未变 |
| Allowed production files | 未变 |
| Disallowed files | 未变 |
| Score policy / FQ0-FQ6 | 未变 |
| Golden / baseline / fixture | 未变 |

新增内容全部是：clarification text、validator strengthening constraint、additional test requirements、tighter stop conditions。没有 scope expansion 或语义弱化。

Slice 4 对 `extraction_snapshot.py` 和 `extraction_score.py` 的条件允许语言也从 "only if needed / only if tests reveal" 收紧为更精确的 "only if tests prove derived anchors cannot be projected without a narrow source_kind/section handling fix" 和 "only if tests prove already-satisfied groups are not recognized because of an implementation bug"，并且 completion report 格式要求 implementation worker 逐项说明任何 production 修改的原因。这折叠了 GLM N5。

---

## 7. Findings 关闭验证

### MiMo Findings

| # | 严重度 | 初审内容 | Updated plan 处置 | 关闭状态 |
|---|--------|---------|-------------------|---------|
| 01 | 中 | `quantitative_derived` + 非 `derived_metric` 未被 validator 拦截 | § Contract Extension 第 188 行新增强制约束 + § Tests #9 新增 reject test | **Closed** |
| 02 | 低 | repository vs helper 双重 minimum_records 语义差异 | § Period 第 133 行澄清 + § Formula 步骤 3 第 143 行注释 + § Tests #2 第 425 行独立测试 | **Closed** |
| 03 | 低 | Slice 4 snapshot 修改边界未明确 | § Anchor 第 255 行 stop condition + Slice 2/4 stop conditions + Slice 4 收紧的条件允许语言 | **Closed** |
| 04 | 低 | real smoke force_refresh 缓存影响 | 保持为 residual；plan Residual Risks 未变 | **Closed（non-blocking，保持 residual）** |

### GLM Findings

| # | 严重度 | 初审内容 | Updated plan 处置 | 关闭状态 |
|---|--------|---------|-------------------|---------|
| N1 | LOW | `minimum_period_records` vs `minimum_records` 命名 | § Formula 步骤 3 第 143 行明确 "这里的 minimum_records 指 period-filtered records" | **Closed** |
| N2 | LOW | na_reason 前缀模式 | 未显式折叠；plan § Fail-Closed Behavior 的 na_reason 已使用 `drawdown_` 前缀 | **Closed（plan 已隐式采用）** |
| N3 | LOW | `_build_group_anchors()` derived 分支需独立测试 | § Anchor 第 255 行 stop condition + Slice 4 第 565 行 narrow fix 例外 | **Closed** |
| N4 | LOW | 缺少 score regression test | § Tests #8 第 447 行 + Slice 4 第 561 行 | **Closed** |
| N5 | LOW | extraction_snapshot/score 条件允许偏宽 | Slice 4 第 556-557 行收紧 + completion report 第 597 行逐项说明要求 | **Closed** |

---

## 8. Verdict

**accepted**

Updated plan 正确落实了 controller disposition 的全部要求：

1. Plan Fix Notes 存在且完整覆盖 disposition 项。
2. Validator contract 精确防止 `accepted + quantitative_derived + 非 derived_metric`——新增独立的 measurement_kind 约束。
3. Reject test 明确要求验证 `actual_metric` 和等价非 `derived_metric` measurement kinds 被拒绝。
4. Repository full-series `minimum_records` 与 metric helper period-filtered `minimum_records` 的语义区别在三处澄清，且有独立 fail-closed 测试。
5. Derived anchor snapshot stop condition 出现三处（anchor convention、Slice 2、Slice 4），score regression test 出现两处（Tests #8、Slice 4）。
6. 无 scope expansion、无 score/quality/golden weakening、core decisions 未变。
7. MiMo 01-04 全部关闭（01 required fix，02-04 folded），GLM N1-N5 全部关闭。

Plan 达到 code-generation-ready 状态，可交由 implementation worker 执行。

---

## 9. 文件路径

| 文件 | 路径 |
|---|---|
| 本 rereview | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-glm-20260529.md` |
| Updated plan | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md` |
| GLM 初审 | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-glm-20260529.md` |
| MiMo 初审 | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-mimo-20260529.md` |
