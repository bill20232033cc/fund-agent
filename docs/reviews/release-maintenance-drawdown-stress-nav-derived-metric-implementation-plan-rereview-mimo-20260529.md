# Drawdown Stress NAV-Derived Metric Implementation Plan Rereview — MiMo

日期：2026-05-29

角色：plan rereview worker only。不实施、不 commit、不 push、不 PR、不 merge。

## Reviewed Target

更新后的 plan：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md`

## Inputs

| 用途 | Artifact |
|---|---|
| 更新后 plan | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md` |
| MiMo 初次 review | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-mimo-20260529.md` |
| GLM 初次 review | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-glm-20260529.md` |

## Controller Disposition

- MiMo finding 01 accepted as required plan fix：`quantitative_derived` must require `derived_metric`；validator must reject `quantitative_derived` paired with `actual_metric`/`actual_exposure`/other measurement kinds；test required。
- MiMo findings 02-04 and GLM LOW N1-N5 non-blocking but should be folded where cheap。

## Rereview Tasks

### 1. Plan Fix Notes 是否存在

**通过。**

更新后 plan 第 9-18 行包含 `## Plan Fix Notes`，明确列出 5 项修复/折叠：

1. 修复 MiMo finding 01：`quantitative_derived` 必须要求 `derived_metric`。
2. 折叠 MiMo 02：repository `minimum_records` 与 metric helper `minimum_records` 独立性澄清。
3. 折叠 MiMo 03 / GLM N3：derived anchor projection snapshot 假设 stop condition。
4. 折叠 GLM N4 / controller 要求：回归测试要求。
5. 收紧 Slice 4 / evidence 边界：production `extraction_snapshot.py` / `extraction_score.py` 修改必须逐项说明。

### 2. Validator Contract 是否精确防止 accepted + quantitative_derived + non-derived_metric

**通过。**

更新后 plan Contract Extension 段（第 187-188 行）新增关键约束：

> `_validate_bond_risk_status_strength()` 必须额外强制：只要 `strength=="quantitative_derived"`，`measurement_kind` 必须等于 `"derived_metric"`；`status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="actual_metric"`、`"actual_exposure"` 或其他 measurement kind 必须 fail validation。

这精确覆盖了初次 review finding 01 的反例：`accepted + quantitative_derived + actual_metric` 必须被拒绝。约束粒度正确——不要求 `derived_metric` 只能搭配 `quantitative_derived`（因为未来可能有其他 derived strength），只要求 `quantitative_derived` 必须搭配 `derived_metric`。

### 3. Required Reject Test 是否存在

**通过。**

更新后 plan Tests 段（第 449-451 行）test 9 明确包含：

> `validate_bond_risk_evidence_value()` rejects `status="accepted"`, `strength="quantitative_derived"`, `measurement_kind="actual_metric"`; equivalent non-`derived_metric` measurement kinds must not pass as accepted derived metrics.

### 4. Repository vs Metric Helper minimum_records 是否清晰且有测试

**通过。**

更新后 plan 有三处强化：

1. **Core Decisions #3 Implementation invariant**（第 133 行）：明确 "repository `minimum_records` 是 full-series early sanity check，只证明 source 返回的整体 series 不是空壳；metric helper 的 `minimum_records` 是 period-filtered final check，必须独立执行，不能因为 repository 已传 `minimum_records=30` 就跳过。"
2. **Formula 步骤 3**（第 143 行）："这里的 `minimum_records` 指 period-filtered records 数量，不是 repository 对 full series 做的 early sanity check。"
3. **Tests #2**（第 425-426 行）："full series has `>=30` records but period-filtered records have `<30` records must fail closed in the metric helper; this proves repository `minimum_records` and metric helper `minimum_records` are independent checks."

三处一致，语义清晰，测试覆盖独立性证明。

### 5. Derived Anchor / Snapshot Stop Condition 和 Score Regression Test 是否存在

**通过。**

**Snapshot stop condition**：Anchor / Provenance Format 段（第 255 行）新增：

> Implementation must first prove this with tests; if snapshot projection assumes `source_kind="annual_report"` or rejects `section_id="derived:nav"`, stop for controller instead of changing schema or weakening projection semantics.

Slice 4 stop condition（第 565 行）进一步强化：

> If snapshot projection assumes annual-report source_kind or rejects `derived:nav`, stop for controller unless the needed production change is a narrow projection compatibility fix with tests and no schema change.

**Score regression test**：Tests #8（第 447 行）新增回归测试：

> regression failure path: when the other six groups are satisfied but `drawdown_stress` is the only weak/missing/ambiguous/absent group, `derive_score_applicability_issues()` must still emit `bond_risk_evidence_missing` with `missing_evidence_groups=("drawdown_stress",)`。

这直接覆盖 GLM N4 和 controller 要求。

### 6. 是否有新的 scope expansion / score/quality/golden weakening / core decision 变更

**通过。**

逐项核对：

- **Non-Goals**：未新增、未删除、未弱化。volatility 仍为 non-goal。
- **Core Decisions**：5 个核心决策（metric、share class、period、formula、volatility）均未变更。
- **Data Boundary**：未扩展——仍只消费 `FundNavRepository.load_nav_series()`。
- **Contract Extension**：只增加了 `quantitative_derived → derived_metric` 约束（修复），未新增其他 enum 值或 schema 变更。
- **Allowed / Disallowed files**：未扩展。`extraction_snapshot.py` / `extraction_score.py` 的条件允许语言从 "only if needed" 收紧为 "only if tests prove ... narrow source_kind/section handling fix"。
- **Score/Quality Gate 语义**：无变化。plan 仍明确 "不修改 score policy、quality gate FQ0-FQ6"。
- **Golden fixtures**：无变化。
- **Slice 结构**：5 个 slice 目标、依赖和 stop condition 未变更，只在 Slice 4 增加了 regression test 和 stop condition 细化。

### 7. GLM LOW Findings 折叠验证

| GLM Finding | 折叠状态 |
|---|---|
| N1: `minimum_period_records` vs `minimum_records` 命名 | 已折叠——Formula 步骤 3 和 Core Decisions #3 明确使用 `minimum_records` 作为函数参数名，并注释 period-filtered 语义 |
| N2: `na_reason` 前缀模式 | 非阻断——Fail-Closed Behavior 表已使用一致的 `drawdown_` 前缀 |
| N3: `_build_group_anchors()` 测试覆盖 | 已折叠——Slice 4 stop condition 要求独立测试 |
| N4: regression test | 已折叠——Tests #8 新增明确回归测试 |
| N5: `extraction_snapshot.py` / `extraction_score.py` 条件允许语言 | 已折叠——Plan Fix Notes 和 Slice 4 收紧了条件允许语言 |

## Rereview Self-Check

- [x] 更新后 plan 包含 Plan Fix Notes
- [x] validator contract 精确防止 accepted + quantitative_derived + non-derived_metric
- [x] required reject test 存在
- [x] repository vs metric helper minimum_records 清晰且有测试
- [x] derived anchor/snapshot stop condition 和 score regression test 存在
- [x] 无新 scope expansion / score/quality/golden weakening / core decision 变更
- [x] 结论只能是 `accepted` / `still changes required` / `blocked`

## Conclusion

**accepted**

Controller disposition 的所有 required fixes 和 recommended folds 均已在更新后 plan 中落实：

1. MiMo finding 01 的 validator 约束和 reject test 精确到位。
2. Repository vs metric helper `minimum_records` 独立性在三处一致澄清并有测试覆盖。
3. Snapshot stop condition 防止 implementation worker 在遇到 `source_kind` 假设问题时绕过 controller。
4. Score regression test 证明 `drawdown_stress` 仍是唯一未满足组时 blocker 不会意外消失。
5. 无 scope expansion、无 score/quality/golden weakening、无 core decision 变更。
6. 所有 GLM LOW findings 均已合理折叠。

更新后 plan 达到 code-generation-ready 状态，可交由 implementation worker 执行。
