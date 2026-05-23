# P9-S1 Analyze Product Contract Plan Review — AgentMiMo

- **Reviewer**: AgentMiMo
- **Date**: 2026-05-21
- **Target**: `docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md`
- **References**: `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、`docs/reviews/post-p8-planning-20260521.md`、`fund_agent/services/fund_analysis_service.py`、`fund_agent/ui/cli.py`

---

## Findings

### F-1 [MEDIUM] Quality Gate Derive Rule #4 与执行流矛盾

**问题**：第 3.4 节派生规则 #4 写道"quality gate 为 `block`，但 dev `warn` 模式继续出报告"派生 `needs_attention`。但当前 `FundAnalysisService.analyze()` 的执行顺序是：quality gate 检查在 `checklist_result` 之前（第 276-280 行），且当 `quality_gate_policy=="block"` 且 gate status 为 block 时，Service 直接抛 `QualityGateBlockedError`，不会到达 `derive_final_judgment` 调用点。因此"quality gate block → needs_attention"这条规则在 product mode 和 developer override block 模式下都**不可能被触发**。只有 developer override `warn` 模式下，gate 不阻断、只产生 result 时，这条规则才有意义。

**证据**：`fund_agent/services/fund_analysis_service.py:276-280`（quality gate block 检查）；plan 第 3.4 节派生规则表第 4 行。

**为什么阻塞**：不阻塞实现，但会误导实现者认为 derive 函数需要处理 gate block 场景，实际上该场景在 derive 调用前已被 Service 拦截。建议在派生规则表中明确适用条件：此规则仅适用于 developer override `warn` 模式。

**建议修正**：派生规则 #4 改为"developer override `warn` 模式下 quality gate block 但继续出报告 → `needs_attention`"；product mode 下 gate block 由 Service 直接阻断，不进入派生。

---

### F-2 [MEDIUM] Developer Override 空对象语义未明确

**问题**：第 3.3 节校验规则写道"`mode=='developer_override'` 时允许 `developer_overrides` 为空；空对象表示只开启 dev mode 但不覆盖字段"。但未说明空 override 与 `final_judgment_override=None` 的关系。如果用户运行 `--dev-override` 且不传任何覆盖参数，`derive_final_judgment` 的 `override_judgment` 为 `None`，派生结果直接作为 selected judgment。这是正确行为，但 plan 没有显式说明这个 golden path。

**证据**：plan 第 3.3 节校验规则第 2 条。

**为什么阻塞**：不阻塞，但实现者可能对空 override 产生歧义。建议在第 3.3 节补充一句：空 override 下 `derive_final_judgment(override_judgment=None)` 的 selected judgment 等于 derived judgment，source 为 `"derived"`。

**建议修正**：在第 3.3 节校验规则后补充空 override 的预期行为说明。

---

### F-3 [MEDIUM] 派生规则优先级与去重未定义

**问题**：第 3.4 节派生规则表中，多个条件可能同时为真：

1. risk veto items 触发 `suggest_replace`。
2. checklist red 触发 `suggest_replace`。
3. minus_20 压力测试 beyond tolerance 触发 `suggest_replace`。

这三条可能同时成立（例如否决项导致 checklist 红灯，且压力测试也超过承受能力）。plan 没有说明 `reasons` 元组是累积所有触发原因还是只取最高优先级的首条。如果累积，`reasons` 会包含重复信息（否决项和红灯可能是同一件事）。

**证据**：plan 第 3.4 节派生规则表第 1-3 行。

**为什么阻塞**：不阻塞设计，但实现时需要明确。建议 `reasons` 累积所有触发原因（去重后），因为 R2 审计和 renderer 来源说明需要完整理由。

**建议修正**：在派生规则表后补充一句：`reasons` 累积所有触发的派生原因；当多个规则因同一底层事实触发时（如否决项同时导致红灯），应去重为单一 reason 并标注最高优先级 rule code。

---

### F-4 [MEDIUM] FinalJudgment 类型别名收口策略缺失

**问题**：plan 第 8.1 节风险条目 5 识别了 "`FinalJudgment` 类型别名漂移"风险，但没有给出具体收口策略。当前 `FinalJudgment` 在 `fund_agent/services/fund_analysis_service.py:41` 定义为 `TemplateFinalJudgment` 的别名。plan 提议在 `fund_agent/fund/analysis/final_judgment.py` 重新定义 `FinalJudgment`。这会导致两个模块各自定义同一类型，renderer/audit 各自引用可能漂移。

**证据**：`fund_agent/services/fund_analysis_service.py:41`（当前 `FinalJudgment = TemplateFinalJudgment`）；plan 第 5.1 节（新增 `FinalJudgment` 定义）。

**为什么阻塞**：不阻塞设计，但实现时如果多个模块各自定义 `FinalJudgment`，会导致类型不一致。建议明确收口：`FinalJudgment` 和 `FinalJudgmentSource` 定义在 `fund_agent/fund/analysis/final_judgment.py`，其他模块通过 import 消费，不重复定义。

**建议修正**：在第 5.7 节明确：`services/__init__.py` 从 Capability policy re-export `FinalJudgment`、`FinalJudgmentSource`、`FinalJudgmentDecision`，不保留 services 层独立定义。同步清理 `TemplateFinalJudgment` 的引用链。

---

### F-5 [LOW] `--money-horizon` 与 `--user-money-horizon-years` 互斥逻辑未说明

**问题**：plan 第 2.1 节将 `--money-horizon`（枚举）移入 developer override，保留 `--user-money-horizon-years`（年限）为 product 输入。但未说明如果两者同时提供时的行为。当前 `run_checklist(...)` 同时消费 `money_horizon` 和 `user_money_horizon_years`（`fund_analysis_service.py:326-328`）。如果 developer override 提供 `money_horizon` 且 product 提供 `user_money_horizon_years`，checklist 会同时使用两者，可能导致不一致。

**证据**：`fund_agent/services/fund_analysis_service.py:326-328`；plan 第 2.1 节 `--money-horizon` 行。

**为什么阻塞**：不阻塞设计，但实现时需要明确优先级或互斥逻辑。建议 product mode 只使用 `user_money_horizon_years`，developer override `money_horizon` 只在显式覆盖时生效且优先级高于年限推导。

**建议修正**：在第 3.3 节 `ResolvedAnalyzeContract` 说明中补充：product mode 下 `money_horizon=None`，只使用 `user_money_horizon_years`；developer override `money_horizon` 覆盖年限推导。

---

### F-6 [LOW] 文件实施顺序未指定依赖关系

**问题**：第 5 节按文件列出实施步骤，但未指定执行顺序和依赖关系。`final_judgment.py`（5.1）是 renderer（5.4）和 audit（5.5）的前置依赖，Service（5.3）依赖 final_judgment 和 renderer/audit 契约变更，CLI（5.6）依赖 Service 契约变更。

**证据**：plan 第 5 节。

**为什么阻塞**：不阻塞设计，但实施时如果顺序错误会导致中间态编译失败。建议补充实施顺序：5.1 → 5.2 → 5.4 + 5.5（可并行）→ 5.3 → 5.7 → 5.6 → 5.8 → 5.9。

**建议修正**：在第 5 节开头补充实施顺序和依赖说明。

---

### F-7 [LOW] 质量 Gate Product Block 与 Dev Warn/Off 设计合理但缺 edge case 说明

**问题**：第 3.6 节质量 gate 模式交互表设计合理：product 固定 block，developer override 可 warn/off。但未覆盖一个 edge case：developer override `quality_gate_policy="block"` 且 gate 阻断时，Service 行为与 product mode 一致（抛异常）。这意味着 developer override 只在 warn/off 时才有区别于 product 的行为。plan 没有显式说明 developer override block 等价于 product block。

**证据**：plan 第 3.6 节。

**为什么阻塞**：不阻塞，但补充说明可避免歧义。

**建议修正**：在第 3.6 节表格 `developer override` 行补充：`block` 行为与 product 一致，均以结构化异常退出码 2 阻断。

---

### F-8 [INFO] Module Boundary 合规性确认

**审查结论**：plan 未违反模块边界：

- `derive_final_judgment` 放在 `fund_agent/fund/analysis/final_judgment.py`（Capability 层），正确。
- Service 只做编排调用 `derive_final_judgment(...)`，不实现领域规则，正确。
- renderer 只消费 `FinalJudgmentDecision`，不重算 policy，正确。
- 未使用 `extra_payload`，所有参数显式声明，正确。
- 未绕过 `FundDocumentRepository`，未新增直接 PDF/cache 访问，正确。
- 未引入外部 Dayu runtime、LLM、Host/Engine、tool loop，正确。

---

### F-9 [INFO] Over-Engineering 评估

**审查结论**：plan 不过度设计。`ResolvedAnalyzeContract` 中间层增加了抽象，但它是必要的——Service 需要在 product/developer override 两种模式下统一消费 resolved 字段，避免在每个调用点重复 if/else 判断。`FinalJudgmentDecision` dataclass 聚合 selected/derived/source/override/reasons/conflict_reasons 是合理的，因为它是一个不可拆分的契约单元。迁移风险可控——旧测试只需补 `mode="developer_override"` 或 CLI `--dev-override`，不需要重写逻辑。

---

## Verdict

**PASS_WITH_REQUIRED_FIXES**

Plan 整体架构正确：final judgment 派生归属 Fund Capability、R2 审计覆盖 derived/override 冲突、quality gate product block 与 dev warn/off 分离合理、未违反模块边界或 extra_payload 禁令。F-1 需要在派生规则表中明确 quality gate block 规则的适用条件（仅 developer override warn 模式），避免实现者误解执行流。F-4 需要明确 FinalJudgment 类型别名收口策略，避免多处定义漂移。其余 findings 为建议性改进，不阻塞实施。
