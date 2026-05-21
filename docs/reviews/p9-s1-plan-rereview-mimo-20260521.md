# P9-S1 Plan Re-Review — AgentMiMo

- **Reviewer**: AgentMiMo
- **Date**: 2026-05-21
- **Previous review**: `docs/reviews/p9-s1-plan-review-mimo-20260521.md`
- **Plan revision**: commit `1fa0e8a`
- **Scope**: 验证前次 required fixes 和关键建议是否闭环

---

## Previous Findings Closure

### F-1 [MEDIUM] Quality Gate Derive Rule #4 与执行流矛盾 — CLOSED

**修订内容**：

- `derive_final_judgment` 入口参数从 `quality_gate_result: QualityGateResult | None` 改为 `quality_gate_status: FinalJudgmentQualityGateStatus`，Service 在调用前归一化。
- 新增显式说明："product `block` 与 developer override `block` 下，若 gate not-run 或 block，Service 在 derive 前抛结构化异常，不会进入该函数。"
- 派生规则 #4 改为"`quality_gate_status=="block"` — 仅 developer override 且 `quality_gate_policy="warn"` 时可到达"。
- 派生规则 #5 改为"`quality_gate_status=="not_run"` — 仅 developer override `off/warn` 且策略允许继续时可到达"。
- 新增 quality gate 状态机表，明确 `block` + `status=block` 和 `block` + not-run 均抛异常、不调用 derive。
- 测试计划新增："product/block 和 developer override/block 的 gate block/not-run 不进入派生函数，由 Service 阻断。"

**结论**：派生规则与执行流的矛盾已消除。`FinalJudgmentQualityGateStatus` 作为归一化中间类型，让 derive 函数不反推 Service 执行流，架构更清晰。

---

### F-2 [MEDIUM] Developer Override 空对象语义 — CLOSED

**修订内容**：

- 校验规则新增：空 override 时 "`derive_final_judgment(override_judgment=None)` 必须返回 `selected_judgment == derived_judgment` 且 `source=="derived"`，不能因为进入 dev mode 就伪造 developer override source"。
- 测试计划新增："developer override 空对象不改变派生来源：无 final judgment override 时仍是 `source=="derived"`。"

**结论**：空 override 语义已明确。

---

### F-3 [MEDIUM] 派生规则优先级与去重 — CLOSED

**修订内容**：

- 派生规则表后新增："派生优先级按表格顺序执行：前三条 `suggest_replace` 规则优先于所有 `needs_attention` 规则，`worth_holding` 只在没有任何替换/关注信号时返回。"
- 去重规则："`reasons` 必须累积所有触发的派生原因；当多个规则来自同一底层事实时去重，只保留最高优先级 rule code 和一条面向用户可读的 reason，避免否决项和由否决项引出的红灯重复刷屏。"
- 测试计划新增："多条规则同时触发时 reasons 累积、去重并保留最高优先级。"

**结论**：优先级和去重策略已明确。

---

### F-4 [MEDIUM] FinalJudgment 类型别名收口 — CLOSED

**修订内容**：

- 第 3.4 节新增显式声明："`FinalJudgment`、`FinalJudgmentSource` 和 `FinalJudgmentDecision` 的单一定义点必须是 `fund_agent/fund/analysis/final_judgment.py`。renderer、audit、service 只能从该模块 import；`TemplateFinalJudgment`、audit 内部 `FinalJudgment` 或 service 层别名不得继续重复定义同一 `Literal`。"
- 第 5.1 节新增："该文件是 ... 的唯一类型定义点；其他模块只 import，不重复声明 Literal。"
- 第 5.4 节新增："删除 renderer 内 `TemplateFinalJudgment` Literal 定义，改为从 `fund_agent.fund.analysis.final_judgment` import。"
- 第 5.5 节新增："删除 audit 模块内 `FinalJudgment` Literal 定义，改为从 `fund_agent.fund.analysis.final_judgment` import。"
- 第 5.7 节明确：services re-export "必须从 `fund_agent.fund.analysis.final_judgment` re-export，不保留 services 层独立定义。"
- 第 8.1 节风险条目更新为收口声明。
- 测试计划新增 renderer 和 audit 的类型来源断言。

**结论**：类型收口策略已贯穿所有相关模块，无遗漏。

---

### F-5 [LOW] `--money-horizon` 与 `--user-money-horizon-years` 互斥 — CLOSED

**修订内容**：

- 第 3.2 节 product mode 固定策略新增："`money_horizon` 枚举在 product mode 始终为 `None`；若用户提供 `user_money_horizon_years`，Service 仍把年限传给 Capability `run_checklist(...)`。"
- 第 3.3 节校验规则新增："product mode 下 `money_horizon=None` ... developer override 下若显式提供 `money_horizon`，该枚举优先级高于 `user_money_horizon_years`，沿用 `run_checklist(...)` 当前'显式枚举优先'的语义。"

**结论**：互斥逻辑和优先级已明确。

---

### F-6 [LOW] 实施顺序 — CLOSED

**修订内容**：第 5 节开头新增 8 步实施顺序：final_judgment.py → __init__.py → renderer + audit（并行）→ service → services/__init__.py → cli → tests → docs。

**结论**：依赖关系已显式。

---

### F-7 [LOW] Quality Gate Dev Block 行为说明 — CLOSED

**修订内容**：

- 第 3.6 节表格 developer override 行更新为："`block` 行为与 product 一致"。
- 新增完整 quality gate 状态机表，覆盖所有 policy × gate result × not-run reason 组合。

**结论**：edge case 已覆盖。

---

## New Issues Check

修订未引入新的阻断项。以下变更值得确认但不构成问题：

- `FinalJudgmentQualityGateStatus` 新增类型简化了 derive 函数的输入契约，Service 承担归一化职责，derive 函数保持纯逻辑，架构合理。
- resolver 伪代码中 `overrides = request.developer_overrides or FundAnalysisDeveloperOverrides()` 正确处理空 override 路径。
- CLI 错误处理统一为 `typer.BadParameter` 而非 `Exit(2)`，与质量阻断的退出码 2 语义分离合理。

---

## Verdict

**PASS**

7 个前次 findings（2 required fixes + 5 建议）全部闭环。修订后的 plan 在质量 gate 执行流、类型收口、派生优先级/去重、money_horizon 优先级、实施顺序等关键点上均已显式定义，无剩余阻断项。计划可进入实施 gate。
