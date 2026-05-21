# P9-S2 Quality Gate / Golden Coverage Calibration Plan — Review (MiMo)

- **Reviewer**: AgentMiMo
- **Date**: 2026-05-21
- **Artifact under review**: `docs/reviews/p9-s2-quality-gate-golden-coverage-plan-20260521.md`
- **Design source**: `docs/design.md`
- **Control source**: `docs/implementation-control.md`
- **Background**: `docs/reviews/post-p9-s1-follow-up-planning-20260521.md`

---

## Conclusion

**PASS_WITH_FINDINGS**

Plan direction is sound. The first-principles decision to separate membership contract from correctness oracle is correct and preserves P9-S1 fail-closed semantics. State model, default source, and non-goals are well-reasoned. No required fixes block implementation, but findings below should be addressed during implementation or in a follow-up plan revision.

---

## Findings

### F-01 [Medium] FQ0 语义重载：计划复用 FQ0 承载两种不同含义

**现状**：当前 `quality_gate.py` FQ0 已有两个触发场景：(a) `fund_quality` 缺失（FQ1/FQ4/FQ5 无法运行），(b) `correctness` 整体 `unavailable`/`not_implemented`。两者都是"子系统未接入"信号。

**计划意图**：将 `correctness_fund_not_covered`（golden 文件存在但当前基金无记录）也归入 FQ0/info。

**问题**：FQ0 当前语义是"子系统未接入"，而 `fund_not_covered` 是"子系统已接入但当前基金无标签"。将两者混为同一 rule code 会让 FQ0 的诊断含义变模糊——收到 FQ0 时无法区分是 golden 文件根本不存在，还是文件存在但该基金没覆盖。

**建议**：实现时在 FQ0 issue metadata 中区分 `reason`（如 `not_configured` vs `fund_not_covered` vs `field_not_comparable`），或者为 fund-not-covered 引入独立 info rule code（如 FQ0a）。不要求计划阶段决定，但实现时必须可区分。

### F-02 [Medium] 计划未覆盖 "golden 文件存在且基金有记录但 comparable_records=0" 边界

**现状**：当 `correctness.status="available"` 且 `comparable_records=0` 时，当前 FQ0 **不会触发**（因为 FQ0 只看 `status=="unavailable"`）。这是一个已知 gap。

**计划状态模型**：定义了 `correctness_fund_not_covered`（golden 文件存在但无该基金记录），但未显式覆盖"基金有记录但所有记录的子字段都不可比"这一边界。`correctness_field_not_comparable` 提到了 `partially_covered`，但 `comparable_records=0` + `status="available"` 的组合未被显式归类。

**建议**：在 Section 3 状态模型中增加显式说明：当 `correctness.status="available"` 且 `comparable_records=0` 时，应视为 `correctness_fund_not_covered`（或新增 `correctness_no_comparable_fields`），以 FQ0/info 处理。测试矩阵应增加此 case。

### F-03 [Low] gate_not_run 语义与 FQ0 的 fund_quality 缺失场景存在轻微矛盾

**计划 Section 3**：`gate_not_run` 定义为"CSV 缺失、CSV schema 无效、阻断性 CSV 校验错误、或基金不在精选池中"。

**现状 FQ0**：`fund_quality` 缺失时 FQ0 也会触发（info），但此时 quality gate **已经运行**（只是部分子规则未执行）。这与 `gate_not_run` 的"gate 无法执行"语义不完全一致。

**影响**：计划未改变 FQ0 对 `fund_quality` 的处理，所以这不是回归风险。但如果未来有人读计划的 `gate_not_run` 定义，可能会误解 FQ0 对 fund_quality 的 info 触发也属于 "gate not run"。

**建议**：无需修改计划，但实现时文档/注释应明确 `gate_not_run` 仅指 pre-gate 会员检查失败，不包括 gate 内部子规则跳过。

### F-04 [Low] 测试矩阵缺少 "golden 文件存在 + 基金有记录 + 所有字段不可比" case

**现状**：测试矩阵 `extraction score` 层有"golden fund present but all fields unavailable"case，期望为 `partially_covered` 或 `fund_not_comparable`，no block by itself。

**问题**：该 case 的期望值含糊（`partially_covered` 或 `fund_not_comparable`），且未说明 FQ0 是否应触发。当前代码中 `comparable_records=0` + `status="available"` 时 FQ0 不触发，而计划意图是应该触发。

**建议**：将此 case 的期望值收紧为明确单一值，并断言 FQ0/info 触发。

### F-05 [Low] correctness_required policy 机制未展开

**计划 Section 2**："Strict golden coverage becomes block only when a policy explicitly requires correctness coverage for a given fund/category and that fund/category is declared in-scope for strict coverage. P9-S2 should not expose this as a normal product-mode user option."

**问题**：这是一个正确的 forward-looking 声明，但 P9-S2 没有定义 `correctness_required` 的触发机制（配置文件？基金级 annotation？category-level policy？）。作为 planning artifact 这可以接受，但应明确这是后续 slice 的 responsibility，避免实现者在 P9-S2 中临时设计。

**建议**：在 Section 9 Non-Goals 中增加一条："Do not implement correctness_required policy mechanism; defer to a future slice."

### F-06 [Info] 默认 source CSV 重复 016492 问题已在 residual risks 中记录，确认无遗漏

计划 Section 10 已记录 `docs/code_20260519.csv` 重复 `016492` 为 human-owned residual risk。当前 validation 将 duplicate codes 视为 non-blocking。与 P5-S6 reconciliation 一致。无额外 action needed。

### F-07 [Info] covered subset 不作为 product source 的决策正确

计划 Section 4 决定不将 6-fund covered subset 作为 product 默认 source。推理正确：49 个 selected funds 会错误地变成 `gate_not_run`（它们是合法会员，只是缺 golden 标签）。covered subset 应仅作为 golden maintenance/reporting artifact。同意。

---

## Challenge-Specific Analysis

### Q1: selected-pool 成员缺 strict golden coverage 定义为 FQ0/info 是否会削弱 product fail-closed？

**结论：不会削弱。**

fail-closed 的核心边界是：(a) 基金必须在精选池中（membership），(b) gate 必须能运行（not_run vs pass/warn/block），(c) 用户不能绕过 block。计划保持了这三个边界不变。golden coverage 是 correctness oracle 的一部分，不是 membership contract 的一部分。将"没有人类标签"等同于"质量失败"会错误地阻断 49 个合法 selected funds，这才是真正的 usability 问题。

FQ0/info 确保缺失覆盖对用户可见（不是静默跳过），同时不阻断其他质量检查（coverage/traceability/fund_quality/App-category/template）的执行。这是正确的权衡。

### Q2: not_run vs correctness unavailable 状态边界是否清楚？

**结论：基本清楚，但有 F-02/F-03 中的边界 case 需要实现时注意。**

`gate_not_run` = pre-gate 会员检查失败（CSV 问题或基金不在池中）。`correctness_*` 系列 = gate 已运行，但 correctness oracle 的某个维度不可用。这两个维度正交，计划的 8 行状态表覆盖了主要路径。

### Q3: 默认 source 继续 docs/code_20260519.csv 是否合理？

**结论：合理。**

这是当前唯一的 selected-pool 定义。切换到 covered subset 会错误地阻断 49 个基金。CSV 的 duplicate 016492 已作为 human-owned residual risk 记录，不阻塞本 slice。

### Q4: covered subset 不作为 product source 是否正确？

**结论：正确。** 见 F-07。

### Q5: 测试矩阵是否足够？

**结论：基本足够，有 F-02/F-04 中的边界 case 需要补充。**

16 行测试矩阵覆盖了 extraction score / quality gate / quality gate integration / Service product / CLI / CLI-API guard 六层，是充分的。主要缺口是 `comparable_records=0` + `status="available"` 的边界。

### Q6: 是否需要 correctness_required policy 但不暴露给 product 用户？

**结论：计划正确地将其推迟到后续 slice。** 见 F-05。

---

## Summary

| Finding | Severity | Action |
|---------|----------|--------|
| F-01 FQ0 语义重载 | Medium | 实现时 metadata 区分 reason |
| F-02 comparable_records=0 边界未覆盖 | Medium | 状态模型补充，测试矩阵增加 |
| F-03 gate_not_run 与 FQ0 fund_quality 轻微矛盾 | Low | 实现时文档澄清 |
| F-04 测试矩阵 "all fields unavailable" 期望值含糊 | Low | 收紧期望值 |
| F-05 correctness_required 机制未展开 | Low | Non-Goals 补充一条 |
| F-06 CSV 重复 016492 已记录 | Info | 无 action |
| F-07 covered subset 不作 product source 正确 | Info | 无 action |
