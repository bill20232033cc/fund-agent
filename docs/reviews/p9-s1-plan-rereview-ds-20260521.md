# P9-S1 Analyze Product Contract Plan — Targeted Re-Review (AgentDS)

**审查对象**: `docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md`（修订版，commit `1fa0e8a`）
**前置审查**: `docs/reviews/p9-s1-plan-review-ds-20260521.md`（初版审查，verdict PASS_WITH_REQUIRED_FIXES）
**审查日期**: 2026-05-21
**审查人**: AgentDS（独立 reviewer）
**审查范围**: 仅验证初版审查的 2 项 required fixes 和 5 项 important/low clarity 是否在修订版中闭环

---

## Required Fixes — 逐项验证

### F1: CLI dev 参数未配 --dev-override 统一 typer.BadParameter

**初版问题**: "抛 `typer.BadParameter` 或输出 stderr 后 `Exit(2)`" 未选定
**修订版变更**（第 5.6 节）:
> "统一抛 `typer.BadParameter`，message 指向 `--dev-override` 并列出误传的 dev 参数。选择 `BadParameter` 的理由：这是 CLI 参数用法错误，不是 quality gate 或数据质量阻断；Typer 会生成标准非零退出并保留参数定位，避免与退出码 2 的质量阻断语义混淆。"

测试计划同步更新（第 6.1 节）：
> "`--equity-position 80%` 未配 `--dev-override` 触发 Typer `BadParameter`，错误信息指向 `--dev-override`"
> "`--quality-gate-policy off` 未配 `--dev-override` 触发 Typer `BadParameter`"

**判定**: ✅ **CLOSED**。方案已锁定，理由充分（语义区分：参数用法错误 vs 质量阻断），测试预期已同步。

---

### F2: TemplateRenderInput 锁定唯一 FinalJudgmentDecision 方案

**初版问题**: "两种可接受实现"（A 替换 vs B 保留并新增），未锁定
**修订版变更**（第 5.4 节）:
> "锁定唯一方案：`TemplateRenderInput` 增加 `final_judgment_decision: FinalJudgmentDecision`，删除单独 `final_judgment` 字段。最终判断的 selected/derived/source 是一个不可拆分契约，不允许保留平行的 loose 字段方案。"

配套变更：
- 第 5.4 节新增："删除 renderer 内 `TemplateFinalJudgment` Literal 定义，改为从 `fund_agent.fund.analysis.final_judgment` import"
- 第 6.1 节测试预期："renderer 不再定义 `TemplateFinalJudgment`，只 import Capability policy 类型"

**判定**: ✅ **CLOSED**。方案 A 已锁定为唯一实现路径，历史兼容方案已删除。renderer 类型定义漂移风险已消除。

---

## Important Clarity — 逐项验证

### F3: money_horizon 在 product mode 始终为 None 的语义

**初版问题**: 计划未显式声明 product mode 下 `money_horizon=None` 对 checklist 第 7 问的影响
**修订版变更**:
- 第 3.2 节新增：
> "`money_horizon` 枚举在 product mode 始终为 `None`；若用户提供 `user_money_horizon_years`，Service 仍把年限传给 Capability `run_checklist(...)`，由检查清单模块按现有规则派生第 7 问信号。若年限缺失，第 7 问保持 gray / `insufficient_data`。"

- 第 3.3 节新增：
> "product mode 下 `money_horizon=None`，只把 `user_money_horizon_years` 交给 Capability 检查清单；developer override 下若显式提供 `money_horizon`，该枚举优先级高于 `user_money_horizon_years`，沿用 `run_checklist(...)` 当前"显式枚举优先"的语义。"

**判定**: ✅ **CLOSED**。语义已显式文档化：product mode 不做 `user_money_horizon_years` → `money_horizon` 枚举派生，依赖 checklist 模块现有规则处理。实现者不会误以为需要写映射逻辑。

---

### F4: quality gate warn/block/not_run 状态机

**初版问题**: `warn + gate block` 与 `not_run` 在派生逻辑中可能混淆
**修订版变更**:
- 第 3.4 节新增 `FinalJudgmentQualityGateStatus` 枚举：
```python
FinalJudgmentQualityGateStatus = Literal["pass", "warn", "block", "not_run"]
```
- `derive_final_judgment()` 签名从 `quality_gate_result: QualityGateResult | None` 改为 `quality_gate_status: FinalJudgmentQualityGateStatus`，由 Service 在调用前归一化。
- 新增归一化规则：
  - `pass/warn/block`：已运行，取 `quality_gate_result.status`
  - `not_run`：未运行（dev override `off` 的 `policy=off`，或 dev override `warn` 下 source/golden 缺失）
  - product `block` 和 dev `block` 下 gate not-run 或 block 时 Service 抛异常，不进入派生
- 第 3.6 节新增完整状态机表（6 行，覆盖 policy × gate result × not-run reason × Service 行为 × 传入派生），消除所有分支歧义。
- 第 6.1 节测试预期新增：
  - "product/block 和 developer override/block 的 gate block/not-run 不进入派生函数，由 Service 阻断"
  - "developer override `block` 与 product `block` 行为一致"

**判定**: ✅ **CLOSED**。状态机完整、可测试；归一化将 Service 执行流与 Capability 派生函数解耦；`FinalJudgmentQualityGateStatus` 消除 `None` 的二义性。

---

## Low Priority — 逐项验证

### F5: quality gate block 行仅适用 dev override

**初版问题**: 派生表中未标注仅 dev override 可到达
**修订版变更**（第 3.4 节）:
> "`quality_gate_status=="block"` | `needs_attention` | 仅 developer override 且 `quality_gate_policy="warn"` 时可到达"

**判定**: ✅ **CLOSED**。条件约束已显式标注。

---

### F6: resolver pseudocode

**初版问题**: `_resolve_analyze_contract()` 仅 bullet points，无伪代码
**修订版变更**（第 5.3 节）:
- 新增完整伪代码（~50 行），覆盖 product 和 developer override 两条路径
- 覆盖所有 `ResolvedAnalyzeContract` 字段映射
- 包含 `None` sentinel 歧义说明："如果实现需要表达'dev override 下显式关闭 source/golden 路径'，不得用 `None` 同时表示'未提供'和'显式关闭'；应新增 typed sentinel"

**判定**: ✅ **CLOSED**。伪代码精确、完整，可直接翻译为实现代码。

---

### F7: 类型别名单一定义点

**初版问题**: 计划在 8.1 节识别了漂移风险但未给出具体收口约束
**修订版变更**:
- 第 3.4 节新增：
> "`FinalJudgment`、`FinalJudgmentSource` 和 `FinalJudgmentDecision` 的单一定义点必须是 `fund_agent/fund/analysis/final_judgment.py`。renderer、audit、service 只能从该模块 import；`TemplateFinalJudgment`、audit 内部 `FinalJudgment` 或 service 层别名不得继续重复定义同一 `Literal`。"

- 第 5.1 节："该文件是 `FinalJudgment`、`FinalJudgmentSource`、`FinalJudgmentDecision` 的唯一类型定义点"
- 第 5.4 节："删除 renderer 内 `TemplateFinalJudgment` Literal 定义"
- 第 5.5 节："删除 audit 模块内 `FinalJudgment` Literal 定义"
- 第 5.7 节："必须从 `fund_agent.fund.analysis.final_judgment` re-export，不保留 services 层独立定义"
- 第 6.1 节对应测试预期已更新
- 第 8.1 节风险描述收窄为单一句子

**判定**: ✅ **CLOSED**。单一定义点约束已写入 plan 主体、文件级 implementation steps 和测试预期三层；不依赖事后 review 发现。

---

## 修订版新增内容审查

修订版额外引入了以下值得肯定的改进：

- **第 5 节实施顺序**：按依赖关系排列 8 步实施顺序，renderer 与 audit 可并行改，避免顺序错误。
- **派生优先级与去重**：明确了 `suggest_replace` 规则优先于 `needs_attention`；`reasons` 累积去重保留最高优先级 rule code。
- **dev override 空对象语义**：明确 `developer_overrides=None` 或空对象时 `source=="derived"`，不因进入 dev mode 伪造 override source。
- **`final_judgment_override` 类型收口**：从 `TemplateFinalJudgment` 改为 `FinalJudgment`，与单一定义点一致。

未发现修订引入新的歧义或冲突。

---

## Verdict: PASS

所有 2 项 required fixes 和 5 项 important/low clarity 均已闭环。修订版在以下维度达到 code-generation-ready 精度：

- CLI 错误处理语义锁定且理由充分
- 模板渲染输入方案唯一，无历史包袱
- `money_horizon` 产品语义显式文档化
- quality gate 状态机完整、可测试
- resolver 有完整伪代码
- 类型别名单一定义点约束写入所有相关模块

**无剩余阻断项。** 计划可进入 P9-S1 implementation gate。
