# P9-S1 Analyze Product Contract Plan — Independent Review (AgentDS)

**审查对象**: `docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md`
**审查日期**: 2026-05-21
**审查人**: AgentDS（独立 reviewer，不参与本 slice planning/implementation）
**依据文件**: `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、`docs/reviews/post-p8-planning-20260521.md`、当前代码基线 `fund_agent/services/fund_analysis_service.py`、`fund_agent/ui/cli.py`、`fund_agent/fund/audit/audit_programmatic.py`、`fund_agent/fund/template/renderer.py`

---

## Findings

### F1: CLI 非法 dev 参数错误响应未选定 — BLOCKING

**段落**: 第 5.6 节
**引用**: "若传任一 dev 参数但未传 `--dev-override`，抛 `typer.BadParameter` 或输出 stderr 后 `Exit(2)`"

**证据**:
- `typer.BadParameter` 是 Typer 的内置参数校验异常，会在 `--help` 风格输出中高亮具体参数，向用户提示"哪个参数非法"。
- `Exit(2)` 是当前 quality gate block 的统一退出码（`fund_agent/ui/cli.py:184,189`），语义是"数据/质量不足以生成报告"。
- 两种行为差异显著：`BadParameter` 有参数定位但退出码由 Typer 控制；`Exit(2)` 退出码确定但参数定位需自行构造消息。

**为什么阻塞**: code-generation-ready plan 不应在 CLI 错误处理上留"或"选择。实现者必须知道该写 `raise typer.BadParameter(...)` 还是 `typer.echo(..., err=True); raise typer.Exit(2)`，否则两个实现者可能写出不同行为。

**建议修正**: 选定一种。推荐 `typer.BadParameter` 当只有单个 dev 参数被误传时（更好的 UX），`Exit(2)` 当多个 dev 参数同时被误传时（统一退出码）。或者一律用 `typer.BadParameter`，因为 Typer 本身会将其转为非零退出码。

---

### F2: TemplateRenderInput 方案 A/B 未决 — BLOCKING

**段落**: 第 5.4 节
**引用**: "两种可接受实现，优先选择 A……推荐 A，因为最终判断的 selected/derived/source 是一个不可拆分契约。"

**证据**:
- 方案 A：`TemplateRenderInput` 增加 `final_judgment_decision: FinalJudgmentDecision`，删除单独 `final_judgment`。
- 方案 B：保留 `final_judgment`，新增 `derived_final_judgment`、`final_judgment_source`。
- 两种方案对 `ProgrammaticAuditInput` 的构造方式不同：A 直接拆解 `FinalJudgmentDecision` 字段；B 仍可独立传值。
- 当前 renderer 在 `TemplateRenderInput` 中使用 `final_judgment: TemplateFinalJudgment`（`renderer.py:80`），第 0/7 章和 `audit_input` 均消费该字段。

**为什么阻塞**: "两种可接受"意味着实现者可在 A 与 B 间自行选择。如果实现者选 B，未来重构者可能认为"既然推荐 A，当前 B 是历史包袱"，导致二次迁移。code-generation-ready 计划必须锁定唯一方案。

**建议修正**: 删除 B，只保留 A。如果担心 A 改动面大，在 plan 中把 A 拆为两步：第一步新增 `final_judgment_decision`，第二步删除 `final_judgment` 字段。但最终交付必须只含 A。

---

### F3: `money_horizon` 在 product mode 始终为 None 的语义未显式说明 — IMPORTANT

**段落**: 第 3.2、3.3、3.4 节
**引用**:
- 第 3.2 节：`--money-horizon` "移入 developer override；product 使用年限输入"
- 第 3.3 节：`FundAnalysisDeveloperOverrides.money_horizon` 仅经 dev override 生效
- 第 3.2 节：`--user-money-horizon-years` 保留为 product 可选输入

**证据**:
- 当前 Service 调用 `run_checklist(..., money_horizon=request.money_horizon, user_money_horizon_years=request.user_money_horizon_years)`（`fund_analysis_service.py:327-328`）。
- `money_horizon` 和 `user_money_horizon_years` 是两个独立参数传入 checklist。计划后 product mode 中 `money_horizon` 始终 `None`，`user_money_horizon_years` 可能非空。
- 计划没有说明 checklist 问题 7 在 product mode 下是否总是返回 gray，或是否应从 `user_money_horizon_years` 派生 `money_horizon`。

**为什么重要但不阻塞**: 计划在 2.4 节已声明 "product mode 应允许这些项以 `missing/insufficient_data/gray` 进入报告"，所以 question 7 返回 gray 在 product mode 是预期行为，不是 bug。但计划没有显式写出"在 product mode，即使 `user_money_horizon_years` 有值，`money_horizon` 仍是 None，question 7 始终 gray"。缺少这句话，未来实现者可能误以为需要做派生。

**建议修正**: 在第 3.2 节或 3.3 节显式加一句："product mode 下 `money_horizon` 始终为 `None`，checklist 第 7 问始终为 gray / `insufficient_data`；`user_money_horizon_years` 作为显式用户事实注入报告但不参与 checklist 信号计算。"

---

### F4: Quality gate `warn` 路径下 `quality_gate_result` 与 `not_run_reason` 共存行为未定义 — IMPORTANT

**段落**: 第 3.6 节
**引用**: "warn 返回报告并携带 gate result；off 返回报告并记录 not-run reason=`policy=off`"

**证据**:
- 当前 `_run_quality_gate_if_enabled()`（`fund_analysis_service.py:423`）在 `policy="off"` 时返回 `(None, "policy=off")`。
- 计划第 3.6 节表：dev override `warn` 路径时 gate 实际运行且可能返回 block/warn/pass，`off` 路径不运行。
- 但当 dev override 设置 `quality_gate_policy="warn"` 且 gate 实际结果为 `block` 时，`FundAnalysisResult` 中同时有 `quality_gate_result`（非空，status=block）和 `quality_gate_not_run_reason`（应为 None）。这个组合在计划中没有明确。
- 后续 `derive_final_judgment()` 需要区分 "gate ran and blocked" vs "gate not run"，如果仅靠 `quality_gate_result is None` 判断，`warn + gate blocked` 可能被误认为 "gate not run"。

**为什么重要但不阻塞**: 当前代码中只有 `policy="off"` 时 `quality_gate_result` 为 `None` 且 `not_run_reason` 非空；`warn`/`block` 时 gate 实际运行。但派生逻辑需要区分三种状态：(1) gate ran → pass, (2) gate ran → block, (3) gate not run。代码就绪计划应明确状态机。

**建议修正**: 在 3.4 节 `derive_final_judgment()` 的 prose 说明中加一条：`quality_gate_status` 三元枚举 `pass / block / not_run`，由 Service 在调用派生前从 `(quality_gate_result, quality_gate_not_run_reason)` 决议。派生表第一列从 "quality gate 为 block" 改为使用该枚举。

---

### F5: 最终判断派生中 "quality gate 为 block 但 dev warn 模式继续出报告" 的条件行仅适用 dev override — LOW

**段落**: 第 3.4 节派生表
**引用**: "quality gate 为 `block`，但 dev `warn` 模式继续出报告 | `needs_attention`"

**证据**: product mode 默认 `quality_gate_policy="block"`，如果 gate 返回 block，Service 在调用 `derive_final_judgment()` 之前就已经 `raise QualityGateBlockedError`，不可能到达派生逻辑。因此该行**仅在 developer override + `quality_gate_policy="warn"` 时才会被触发**。

**为什么不阻塞**: 逻辑是正确的——product mode 永远不会执行到这一行。但表中未标注这一约束，可能误导读者认为 product mode 也可能走到这个分支。

**建议修正**: 在该行加脚注：`（仅 developer override 且 quality_gate_policy="warn" 时可到达；product mode block 策略下 Service 已先行阻断。）`

---

### F6: `_resolve_analyze_contract()` 伪代码缺失 — LOW

**段落**: 第 5.3 节
**引用**: "增加 `_resolve_analyze_contract(request)`：product 下填充 dev 字段为 `None`……developer override 下读取 override quality gate 参数"

**证据**: 其他关键函数如 `derive_final_judgment()` 给了完整签名和 prose 规则，但 resolver 只有 bullet points。实现者需要从 bullets 自己推导字段映射关系（如 `request.equity_position` 在 product 时置 None、在 dev override 且 `developer_overrides.equity_position is not None` 时读取后者）。

**为什么不阻塞**: bullet points 已足够精确（"product 下填充 dev 字段为 None"），只是粒度不及其他部分。当前信息可支撑实现。

**建议修正**: 补充简短 pseudo-code 或字段映射表，与 3.3 节 `ResolvedAnalyzeContract` 的字段一一对应。

---

### F7: 类型别名漂移收口方案缺乏具体约束 — LOW

**段落**: 第 5.7 节、第 8.1 节
**引用**: "类型别名漂移：`FinalJudgment` 不应在 renderer、audit、service 多处重复定义；实现时收口到 Capability policy 或显式 re-export。"

**证据**: 当前 `FinalJudgment` 在三处独立定义：
- `renderer.py:37`: `TemplateFinalJudgment`
- `audit_programmatic.py:32`: `FinalJudgment`
- `fund_analysis_service.py:41`: `FinalJudgment = TemplateFinalJudgment`

计划在第 5.1 节新增 `fund_agent/fund/analysis/final_judgment.py` 定义 `FinalJudgment`。但 5.7 节只说"确保来源与 Capability policy 一致"，没有明确说"删除 renderer 模块的 `TemplateFinalJudgment` 和 audit 模块的 `FinalJudgment`，统一 import 自 `fund_agent.fund.analysis.final_judgment`"。

**为什么不阻塞**: 风险已在 8.1 节识别，实现时 review 可检查。

**建议修正**: 在 5.7 节加一条：renderer 的 `TemplateFinalJudgment` 和 audit 的 `FinalJudgment` 应改为 `from fund_agent.fund.analysis.final_judgment import FinalJudgment`，禁止模块内重复定义 Literal。

---

### 已确认无问题的方面

以下计划主张经审查确认正确，无需修正：

- **final judgment 派生在 Fund Capability**：计划将 `derive_final_judgment()` 放在 `fund_agent/fund/analysis/final_judgment.py`，符合 AGENTS.md "任何理解基金类型、投资规则、有知有行方法论"的归属规则。Service 仅编排调用。✅
- **developer override 隔离**：`--dev-override` 显式切换 + 未传时 dev 参数报错。product 路径无法静默注入开发字段。✅
- **R2 能审计 override/derived 冲突**：新增 `derived_final_judgment` 和 `final_judgment_source` 字段，R2 对 `source="developer_override"` 且 selected≠derived 触发 fail。✅
- **quality gate product block vs dev warn/off**：product 固定 block（Service 先阻断），warn/off 仅经 `FundAnalysisDeveloperOverrides` 生效。✅
- **不违反 extra_payload 禁令**：所有参数显式声明在 typed dataclass 中，无 dict 兜底。✅
- **不绕过 FundDocumentRepository**：Service 仅通过 `FundDataExtractor` 进入 Capability，无 PDF/cache/filesystem 直接访问。✅
- **不引入外部 Dayu/LLM/Host/Engine/tool loop**：non-goals 和约束明确排除。✅
- **迁移策略合理**：5 步渐进式迁移，不做静默兼容。✅
- **测试覆盖充分**：覆盖 product minimal path、dev override path、policy 派生、R2 冲突、CLI gating。✅

---

## Verdict: PASS_WITH_REQUIRED_FIXES

**过关条件**: F1（CLI 错误响应选定）和 F2（TemplateRenderInput 方案锁定）必须在计划修订版中修正，才能进入 P9-S1 implementation gate。

**建议**: F3、F4 虽不阻塞 implementation gate，但强烈建议在修订版中一并补充。F5-F7 可留到 implementation 时通过 code review 确保不漂移。

**不构成 FAIL 的理由**: 计划在核心架构决策上正确——final judgment 派生在 Capability、product/dev 模式分离、R2 冲突审计、quality gate 策略分层、模块边界保持——仅有两处 implementation-ready 精度的缺口（F1/F2），修复成本低，不推翻整体方向。
