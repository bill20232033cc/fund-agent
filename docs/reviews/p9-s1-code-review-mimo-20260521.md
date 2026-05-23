# P9-S1 Code Review — AgentMiMo

- **Date**: 2026-05-21
- **Reviewer**: AgentMiMo
- **Scope**: workspace uncommitted changes (19 files, +913/-258)
- **Plan**: `docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md` (commit `1fa0e8a`)
- **Implementation artifact**: `docs/reviews/p9-s1-implementation-20260521.md`

## Verdict

**PASS_WITH_FINDINGS**

实现整体符合 accepted plan 的契约、模块边界和 fail-closed 要求。无阻断级发现。

## Review Checklist

### 1. Product analyze 最小输入

**PASS.** `FundAnalysisRequest` (`fund_analysis_service.py:117-141`) 根字段仅含 `fund_code`、`report_year`、`investment_amount`、`max_tolerable_loss_rate`、`valuation_state`、`user_money_horizon_years`、`force_refresh`、`mode`、`developer_overrides`。所有开发夹具字段（`equity_position`、`actual_style`、`money_horizon`、`current_stage`、`final_judgment` 等）均不在根部。CLI `analyze 110011` 构造 product mode request，`developer_overrides is None`。

### 2. Dev-only 参数必须 --dev-override

**PASS.** `_has_developer_override_options()` (`cli.py:602-673`) 检查全部 14 个 dev 参数；`_build_developer_overrides()` (`cli.py:676-761`) 在 `provided_options and not dev_override` 时抛 `typer.BadParameter`。`quality_gate_policy` 通过 `!= "block"` 默认值检测。测试 `test_analyze_cli_rejects_dev_options_without_dev_override` 和 `test_analyze_cli_rejects_quality_gate_policy_without_dev_override` 覆盖。

### 3. Service quality gate block/not_run 在 derive 前阻断

**PASS.** `analyze()` (`fund_analysis_service.py:335-339`) 在 `derive_final_judgment` 之前检查 `quality_gate_policy == "block"`，`quality_gate_result is None` 时抛 `QualityGateNotRunBlockedError`，`status == GATE_STATUS_BLOCK` 时抛 `QualityGateBlockedError`。`_resolve_final_judgment_quality_gate_status()` 归一化 pass/warn/block/not_run 后才传入 derive。quality gate 状态机与 plan §3.6 一致。

### 4. FinalJudgment 单一定义点

**PASS.** `FinalJudgment`、`FinalJudgmentSource`、`FinalJudgmentQualityGateStatus`、`FinalJudgmentDecision` 定义于 `fund_agent/fund/analysis/final_judgment.py:16-55`。renderer (`renderer.py:18`)、audit (`audit_programmatic.py:15`)、service (`fund_analysis_service.py:19`)、CLI (`cli.py:22`) 均从该模块 import。renderer 和 audit 模块内无重复 `Literal` 定义。`services/__init__.py` re-export 而非独立定义。

### 5. Renderer/audit selected/derived/source 和 R2 冲突

**PASS.**
- `TemplateRenderInput` (`renderer.py:79`) 使用 `final_judgment_decision: FinalJudgmentDecision` 单一契约字段，无平行 loose 字段。
- renderer 第 7 章 (`renderer.py:545-546`) 渲染 `decision.selected_judgment` 和来源说明（`_final_judgment_source_text`）。
- `ProgrammaticAuditInput` (`audit_programmatic.py:104-106`) 接收 `final_judgment`、`derived_final_judgment`、`final_judgment_source` 三字段。
- R2 审计 (`audit_programmatic.py:596-620`)：derived source 下 selected != derived 直接 fail；developer_override source 下冲突 fail。
- renderer 填入 audit input (`renderer.py:137-145`) 正确映射 selected/derived/source。

### 6. FundDocumentRepository/extra_payload/模块边界

**PASS.**
- 未引入 `extra_payload` 或 dict 类型兜底。
- 所有文档访问仍通过 `FundDataExtractor` / `FundDocumentRepository`。
- `derive_final_judgment` 位于 Capability 层 (`final_judgment.py`)，不读取 UI/Service/文档仓库。
- Service 只编排，不实现领域规则。

### 7. 测试覆盖

**PASS.** 计划要求的测试场景均有对应覆盖：

| 计划要求 | 测试位置 |
|---|---|
| risk veto → suggest_replace | `test_final_judgment.py:140` |
| checklist red → suggest_replace | `test_final_judgment.py:165` |
| minus_20 beyond → suggest_replace | `test_final_judgment.py:179` |
| gate block/not_run → needs_attention | `test_final_judgment.py:193` |
| yellow/gray/watch → needs_attention | `test_final_judgment.py:216` |
| all green pass → worth_holding | `test_final_judgment.py:231` |
| reasons 累积去重 | `test_final_judgment.py:245` |
| override 选择 + 冲突记录 | `test_final_judgment.py:262` |
| product request 最小路径 | `test_fund_analysis_service.py:268` |
| product mode 固定 block | `test_fund_analysis_service.py:383` |
| warn 策略保留报告 | `test_fund_analysis_service.py:349` |
| block 策略阻断 | `test_fund_analysis_service.py:383` |
| CLI 默认 product request | `test_cli.py:548` |
| dev 参数未配 --dev-override | `test_cli.py:573` |
| quality gate policy 未配 --dev-override | `test_cli.py:598` |
| CLI structured gate block | `test_cli.py:623` |
| renderer 用 FinalJudgmentDecision | `test_renderer.py:1046` |
| 非法 final judgment fail closed | `test_renderer.py:1009` |
| R2 要求 derived/source | `test_audit_programmatic.py:683,713` |
| derived source 冲突 | `test_audit_programmatic.py:857` |
| developer override 冲突 | `test_audit_programmatic.py:883` |

## Findings

### F1 — INFO: `_audit_final_judgment` 防御分支不可达

- **文件**: `fund_agent/fund/audit/audit_programmatic.py:613`
- **严重度**: INFO（不阻断）
- **描述**: `elif final_judgment_source not in {"derived", "developer_override", None}` 分支中，`None` 已在 `_audit_required_inputs` 前置检查中阻断，而 `FinalJudgmentSource` Literal 只有 `"derived"` 和 `"developer_override"` 两个值，因此该 `elif` 永远不会命中。不影响功能正确性，仅为 dead code。
- **建议**: 可选移除 `None` 或整个 `elif` 分支；不阻断本次合入。

### F2 — INFO: CLI 测试未覆盖 product mode 真实 Service 路径

- **文件**: `tests/ui/test_cli.py:548`
- **严重度**: INFO（不阻断）
- **描述**: `test_analyze_cli_default_product_request` 使用 `_FakeService` 验证 CLI 构造的 request 字段正确，但未验证 product mode 固定 `quality_gate_policy="block"` 在真实 Service 中的行为。该路径已由 `test_fund_analysis_service.py` 中的 block 策略测试覆盖，CLI 层不需重复。
- **建议**: 当前覆盖充分；如有后续 CLI-Serivce 集成测试需求可补充。

### F3 — INFO: 计划中部分 CLI 测试场景由组合覆盖而非独立测试

- **文件**: `tests/ui/test_cli.py`
- **严重度**: INFO（不阻断）
- **描述**: 计划 §6.1 要求的 `--dev-override --equity-position 80% --final-judgment-override worth_holding --quality-gate-policy warn` 构造 nested override 场景，在 `test_analyze_cli_calls_service_and_prints_report` (line 437) 中已覆盖（传入 `--dev-override --equity-position 80% --final-judgment worth_holding --quality-gate-policy warn`）。非独立测试但覆盖完整。
- **建议**: 无需额外测试。

## Module Boundary Compliance

| 边界约束 | 状态 |
|---|---|
| UI 不承载基金领域判断 | PASS — CLI 只解析、构造 request、调用 Service、输出 |
| Service 不实现基金领域规则 | PASS — 只编排抽取/gate/分析/渲染/审计 |
| Fund Capability 拥有类型/检查/风险/压力/判断/模板/审计 | PASS — `final_judgment.py` 位于 `fund/analysis/` |
| 文档访问只经 FundDocumentRepository | PASS — 未新增直接文件访问 |
| 不使用 extra_payload | PASS |
| 不引入外部 Dayu runtime/LLM/Host/Engine | PASS |
| valuation_state 仍是显式输入或缺省 unavailable | PASS |

## Conclusion

P9-S1 implementation 正确实现了 accepted plan 的全部核心契约：

1. `FinalJudgment` 类型族单一定义于 Capability 层，全链路 import 无重复 Literal。
2. product mode 最小输入 `analyze 110011`，开发参数必须显式 `--dev-override`。
3. quality gate block/not_run 在 derive 前阻断，状态机与 plan §3.6 一致。
4. renderer 消费不可拆分的 `FinalJudgmentDecision`，audit R2 能检测 derived 和 developer_override 冲突。
5. 无 `extra_payload`、无绕过 `FundDocumentRepository`、无外部 runtime 引入。
6. 测试覆盖 plan §6 要求的全部场景，88 targeted + 365 full suite 通过。

3 个 INFO 级发现均为代码质量观察，不影响功能正确性或契约合规性。
