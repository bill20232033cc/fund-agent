# P9-S1 Analyze Product Contract Plan - 2026-05-21

## 1. Scope And Constraints

本计划只定义 `fund-analysis analyze` 产品契约加固的 code-generation-ready implementation plan，不包含本次实施代码。

必须保持的边界：

- UI 只解析输入、调用 Service、输出报告或结构化错误，不承载基金领域判断。
- Service 只编排抽取、quality gate、分析、模板渲染和审计，不实现基金领域规则。
- Fund Capability 拥有基金类型、检查清单、风险、压力测试、最终判断派生、模板和审计规则。
- 年报生产访问仍只经过 `FundDocumentRepository`，本 slice 不新增任何直接 PDF/cache/filesystem 访问。
- 不使用 `extra_payload` 传递显式参数。
- 不引入外部 Dayu runtime、LLM、Host、Engine、tool loop 或 prompt scene registry。
- 不在本 slice 自动从温度计推导估值状态；`valuation_state` 仍是显式用户输入或缺省 `unavailable`。

## 2. Current Contract Inventory

### 2.1 CLI Current State

`fund_agent/ui/cli.py::analyze` 当前把以下参数全部暴露在同一个普通用户命令路径：

| 当前 CLI 参数 | 当前默认 | 当前用途 | P9-S1 判定 |
|---|---:|---|---|
| `fund_code` | 必填 | 基金代码 | 保留为 product 必填 |
| `--report-year` | `2024` | 年报年份 | 保留为 product 可选 |
| `--equity-position` | `None` | R=A+B-C 股票仓位 | 移入 developer override |
| `--actual-style` | `None` | 言行一致性实际风格 | 移入 developer override |
| `--actual-equity-position` | `None` | 言行一致性实际股票仓位 | 移入 developer override |
| `--manager-tenure-months` | `None` | 否决项经理任期 | 移入 developer override；后续应由 Capability 派生/抽取 |
| `--peer-fee-median` | `None` | 否决项同类费率 | 移入 developer override；后续应由数据源/Capability 提供 |
| `--tracking-error` | `None` | 指数基金跟踪误差 | 移入 developer override；后续应由 NAV/benchmark Capability 派生 |
| `--investment-amount` | `10000` | 压力测试本金 | 保留为 product 可选用户输入 |
| `--max-tolerable-loss-rate` | `None` | 用户最大可承受亏损 | 保留为 product 可选用户输入 |
| `--valuation-state` | `unavailable` | 检查清单估值状态 | 保留为 product 可选用户输入，直到温度计映射另行设计 |
| `--money-horizon` | `None` | 资金期限枚举 | 移入 developer override；product 使用年限输入 |
| `--user-money-horizon-years` | `None` | 用户资金不用年限 | 保留为 product 可选用户输入 |
| `--current-stage` | `None` | 第 5 章当前阶段文本 | 移入 developer override；product 缺失时渲染数据不足 |
| `--final-judgment` | `needs_attention` | 第 7 章最终判断与 R2 输入 | 从 product 移除，改为 Capability 派生；developer override 仅作显式覆盖 |
| `--force-refresh` | `False` | 刷新底层数据 | 保留为 product 可选操作参数 |
| quality gate 参数组 | `block` / 默认路径 | 输入质量 gate | product 固定 `block`；`warn/off/source/output/run/golden` 移入 developer override |

### 2.2 Service Current State

`FundAnalysisRequest` 当前是扁平 dataclass，包含：

- 用户事实：`fund_code`、`report_year`、`investment_amount`、`max_tolerable_loss_rate`、`valuation_state`、`money_horizon`、`user_money_horizon_years`。
- 开发/夹具事实：`equity_position`、`actual_style`、`actual_equity_position`、`manager_tenure_months`、`peer_fee_median`、`tracking_error`、`current_stage`。
- 结论输入：`final_judgment`，当前默认 `needs_attention`。
- 运行控制：`force_refresh`、`quality_gate_policy`、`quality_gate_source_csv`、`quality_gate_output_dir`、`quality_gate_run_id`、`quality_gate_golden_answer_path`。

`FundAnalysisService.analyze()` 当前把这些字段直接传入 Capability：

- `request.equity_position` → `calculate_r_abc_from_bundle(...)`
- `request.actual_style` / `request.actual_equity_position` → `check_consistency(...)`
- `request.manager_tenure_months` / `peer_fee_median` / `tracking_error` → `run_risk_checks(...)`
- `request.investment_amount` / `max_tolerable_loss_rate` → `run_stress_test(...)`
- `request.valuation_state` / `money_horizon` / `user_money_horizon_years` → `run_checklist(...)`
- `request.final_judgment` / `current_stage` → `TemplateRenderInput(...)`

### 2.3 Template And Audit Current State

- `TemplateRenderInput.final_judgment` 必填，renderer 在第 0 章和第 7 章渲染该值，并把它放入 `ProgrammaticAuditInput.final_judgment`。
- `ProgrammaticAuditInput.final_judgment` 当前被 `_audit_required_inputs()` 视为 R2 必需输入。
- R2 当前只检查：
  - 有红灯检查项时，最终判断必须是 `suggest_replace`。
  - 检查清单全绿时，最终判断不应是 `suggest_replace`。
- 当前 R2 不知道判断是用户输入、开发覆盖还是系统派生，也无法识别“派生应为 `needs_attention` 但 override 强行 `worth_holding`”这类冲突。

### 2.4 Existing System-Derived Inputs And Gaps

P1/P2 已能从 `StructuredFundDataBundle` 或 Capability 分析得到：

- 基金类型、基金规模、基金名称、基准、费率、换手率、NAV/benchmark、投资者收益、份额变化、经理/从业人员持有披露、持仓和行业分布。
- R=A+B-C 在缺少股票仓位时会返回 `missing`，不会静默假设。
- 言行一致性在缺少实际风格/实际股票仓位时部分维度返回 `insufficient_data`。
- 否决项在缺少经理任期、同类费率、跟踪误差时对应项返回 `insufficient_data`。
- 压力测试缺少最大可承受亏损时仍输出场景浮亏，但不判断承受能力。
- 检查清单缺少估值或资金期限时输出灰灯。

P9-S1 不应为了“看起来完整”把这些缺口重新推给普通用户；product mode 应允许这些项以 `missing/insufficient_data/gray` 进入报告和最终判断派生。

## 3. Target Contract Proposal

### 3.1 Mode Decision

采用单一命令、显式模式开关：

- 默认 `fund-analysis analyze` 是 product mode。
- 通过 `--dev-override` 进入 developer override mode。

选择该方案而不是新增独立 `analyze-dev` 子命令的原因：

- 保持当前用户入口和测试入口不分裂，避免两个命令长期漂移。
- Service 可以通过 `mode` 和嵌套 override 对象统一执行 fail-closed 校验。
- 旧 smoke/manual comparison 命令只需补 `--dev-override`，不需要迁移到另一套命令实现。

UI 帮助文本必须把 product 成功路径放在主描述中；developer override 参数放入“开发覆盖/夹具”帮助分组，并且任何 developer 参数在未传 `--dev-override` 时必须失败，不允许静默生效。

### 3.2 Product Mode Inputs

product mode 的最小成功路径：

```bash
fund-analysis analyze 110011
```

product mode 保留的用户/操作输入：

| 字段 | CLI | Service 请求字段 | 必填 | 说明 |
|---|---|---|---|---|
| 基金代码 | `fund_code` | `fund_code` | 是 | 6 位数字，Service 继续校验 |
| 年报年份 | `--report-year` | `report_year` | 否，默认 2024 | 用户可选择披露年份 |
| 投入金额 | `--investment-amount` | `investment_amount` | 否，默认 10000 | 用户自有金额；压力测试需要本金 |
| 最大可承受亏损 | `--max-tolerable-loss-rate` | `max_tolerable_loss_rate` | 否 | 用户自有风险承受输入；缺失时只显示浮亏 |
| 估值状态 | `--valuation-state` | `valuation_state` | 否，默认 `unavailable` | 暂不自动接温度计映射 |
| 资金不用年限 | `--user-money-horizon-years` | `user_money_horizon_years` | 否 | product 优先暴露年限，不暴露枚举 |
| 强制刷新 | `--force-refresh` | `force_refresh` | 否 | 操作参数，不含领域逻辑 |

product mode 固定策略：

- `mode="product"`。
- `developer_overrides=None`。
- `quality_gate_policy="block"`。
- 使用默认 `quality_gate_source_csv` 和默认 golden answer 路径；不向普通用户暴露 `off/warn` 或 gate 文件路径。
- 不接受 `final_judgment` 输入；最终判断由 Capability policy 派生。

### 3.3 Developer Override Inputs

新增显式 dataclass：

```python
@dataclass(frozen=True, slots=True)
class FundAnalysisDeveloperOverrides:
    """开发覆盖参数，只能在 developer_override mode 使用。"""

    equity_position: Decimal | str | int | float | None = None
    actual_style: str | None = None
    actual_equity_position: Decimal | str | int | float | None = None
    manager_tenure_months: int | None = None
    peer_fee_median: Decimal | str | int | float | None = None
    tracking_error: Decimal | str | int | float | None = None
    money_horizon: MoneyHorizon | None = None
    current_stage: str | None = None
    final_judgment_override: TemplateFinalJudgment | None = None
    quality_gate_policy: QualityGatePolicy | None = None
    quality_gate_source_csv: Path | None = None
    quality_gate_output_dir: Path | None = None
    quality_gate_run_id: str | None = None
    quality_gate_golden_answer_path: Path | None = None
```

`FundAnalysisRequest` 改为：

```python
AnalyzeMode = Literal["product", "developer_override"]

@dataclass(frozen=True, slots=True)
class FundAnalysisRequest:
    fund_code: str
    report_year: int = 2024
    investment_amount: Decimal | str | int | float = Decimal("10000")
    max_tolerable_loss_rate: Decimal | str | int | float | None = None
    valuation_state: ValuationState = "unavailable"
    user_money_horizon_years: Decimal | str | int | float | None = None
    force_refresh: bool = False
    mode: AnalyzeMode = "product"
    developer_overrides: FundAnalysisDeveloperOverrides | None = None
```

Service 内部通过 resolver 得到有效运行配置，不在请求根部保留历史开发字段：

```python
@dataclass(frozen=True, slots=True)
class ResolvedAnalyzeContract:
    mode: AnalyzeMode
    equity_position: Decimal | str | int | float | None
    actual_style: str | None
    actual_equity_position: Decimal | str | int | float | None
    manager_tenure_months: int | None
    peer_fee_median: Decimal | str | int | float | None
    tracking_error: Decimal | str | int | float | None
    money_horizon: MoneyHorizon | None
    current_stage: str | None
    final_judgment_override: TemplateFinalJudgment | None
    quality_gate_policy: QualityGatePolicy
    quality_gate_source_csv: Path | None
    quality_gate_output_dir: Path | None
    quality_gate_run_id: str | None
    quality_gate_golden_answer_path: Path | None
```

校验规则：

- `mode=="product"` 且 `developer_overrides is not None` 必须抛 `ValueError`。
- `mode=="developer_override"` 时允许 `developer_overrides` 为空；空对象表示只开启 dev mode 但不覆盖字段。
- `quality_gate_policy="off"` 或 `"warn"` 只能经 developer override 生效。
- `final_judgment_override` 只能经 developer override 生效。
- 不提供 `extra_payload` 或 dict 类型兜底。

### 3.4 Final Judgment Derivation Policy

新增 Fund Capability policy 模块，建议路径：

`fund_agent/fund/analysis/final_judgment.py`

建议契约：

```python
FinalJudgment = Literal["worth_holding", "needs_attention", "suggest_replace"]
FinalJudgmentSource = Literal["derived", "developer_override"]

@dataclass(frozen=True, slots=True)
class FinalJudgmentDecision:
    selected_judgment: FinalJudgment
    derived_judgment: FinalJudgment
    source: FinalJudgmentSource
    override_judgment: FinalJudgment | None
    reasons: tuple[str, ...]
    conflict_reasons: tuple[str, ...]
```

入口：

```python
def derive_final_judgment(
    *,
    checklist_result: ChecklistResult,
    risk_check_result: RiskCheckResult,
    stress_test_result: StressTestResult,
    quality_gate_result: QualityGateResult | None,
    quality_gate_not_run_reason: str | None,
    override_judgment: FinalJudgment | None = None,
) -> FinalJudgmentDecision:
    ...
```

派生规则首版：

| 条件 | derived judgment | 理由 |
|---|---|---|
| 任一 `risk_check_result.veto_items` | `suggest_replace` | 模板第 6 章否决项优先 |
| 任一 checklist 红灯 | `suggest_replace` | 检查清单第 7 章红灯优先 |
| `minus_20` 压力场景 `capacity_status=="beyond_tolerance"` | `suggest_replace` | 用户承受能力与基础压力场景冲突 |
| quality gate 为 `block`，但 dev `warn` 模式继续出报告 | `needs_attention` | 数据质量不足，不把质量问题误判为基金应替换 |
| quality gate 未运行且策略允许继续 | `needs_attention` | 缺少质量证明 |
| 任一 risk watch/insufficient、checklist yellow/gray、压力测试 near/beyond 但未触发上方否决 | `needs_attention` | 存在需要最小验证的问题 |
| checklist 全绿、risk 全 pass、quality gate pass 或 policy off、压力测试不越过用户承受能力 | `worth_holding` | 仅表示“当前证据下值得持有”，不是买入建议 |
| 其他未覆盖状态 | `needs_attention` | fail-safe 默认 |

override 语义：

- 无 override：`selected_judgment == derived_judgment`，`source="derived"`。
- 有 override：`selected_judgment == override_judgment`，`source="developer_override"`，同时保留 `derived_judgment`。
- policy 不在派生函数里直接抛出 override 冲突；冲突交给 R2 审计阻断，保证 developer smoke 可以构造冲突测试。

### 3.5 R2 Audit Contract

`ProgrammaticAuditInput` 增加显式派生判断字段，不依赖 UI：

```python
final_judgment: FinalJudgment | None = None
derived_final_judgment: FinalJudgment | None = None
final_judgment_source: FinalJudgmentSource | None = None
```

R2 更新为：

- 继续要求 `final_judgment` 存在；缺失仍 fail。
- product/derived 路径要求 `derived_final_judgment` 和 `final_judgment` 相等。
- developer override 路径如果 `final_judgment != derived_final_judgment`，必须按 `conflict_reasons` 或 audit 规则触发 R2 blocker。
- 保留现有 checklist 红灯/全绿一致性规则，避免 derived policy 回归时被漏检。

renderer 只渲染 `selected_judgment` 和可选的“判断来源：系统派生/开发覆盖”短文本；不在 renderer 内重算 policy。

### 3.6 Quality Gate Mode Interaction

| 模式 | 默认策略 | 可否 `warn/off` | 行为 |
|---|---|---|---|
| product | `block` | 否 | gate not-run 或 block 均以结构化异常退出码 2 阻断 |
| developer override | `block`，可覆盖 | 是 | `warn` 返回报告并携带 gate result；`off` 返回报告并记录 not-run reason=`policy=off` |

quality gate 结果只作为最终判断派生的输入之一；Service 仍在 product `block` 下先阻断，不生成报告。

## 4. Migration Strategy

1. 先新增 nested request/override 和 final judgment policy，保持 Service 内部可从 product request 跑通。
2. 再更新 renderer/audit input 以携带 selected/derived/source，不改变 8 章 Markdown 章节结构。
3. 再更新 CLI：默认 product path 最小输入；历史开发参数仍存在但必须配 `--dev-override`。
4. 更新 tests/smoke：需要旧确定性字段的测试统一补 `mode="developer_override"` 或 CLI `--dev-override`。
5. 更新 README/design 文档：只把 product success path 作为用户手册成功路径；developer override 写在开发手册或测试手册。

不做静默兼容：

- 旧代码中直接构造 `FundAnalysisRequest(equity_position=...)` 应改为 `developer_overrides=FundAnalysisDeveloperOverrides(...)`。
- 旧 CLI 使用 `--final-judgment` 时，必须同时传 `--dev-override`；推荐新名 `--final-judgment-override`，可保留 `--final-judgment` 作为隐藏别名一个开发周期。

## 5. File-By-File Implementation Steps

### 5.1 `fund_agent/fund/analysis/final_judgment.py`（新增）

- 定义 `FinalJudgment`、`FinalJudgmentSource`、`FinalJudgmentDecision`。
- 实现 `derive_final_judgment(...)`。
- 用模块级常量定义 rule codes/reason 文本，避免魔法字符串散落。
- docstring 必须引用模板第 7 章和检查清单第 7 问。
- 不读取文档仓库、PDF、cache、UI 或 Service。

### 5.2 `fund_agent/fund/analysis/__init__.py`

- 导出 `FinalJudgmentDecision`、`derive_final_judgment` 和类型别名。
- 保持 Capability public import 风格与现有分析模块一致。

### 5.3 `fund_agent/services/fund_analysis_service.py`

- 新增 `AnalyzeMode`、`FundAnalysisDeveloperOverrides`、`ResolvedAnalyzeContract`。
- 收窄 `FundAnalysisRequest` 根字段到 product inputs。
- 增加 `_resolve_analyze_contract(request)`：
  - product 下填充 dev 字段为 `None`。
  - product 下固定 `quality_gate_policy="block"`、默认 source/golden 路径。
  - developer override 下读取 override quality gate 参数，缺省仍使用当前默认。
- `_validate_request()` 增加 mode/override 互斥校验。
- `analyze()` 改为先解析 `resolved_contract`，后续调用全部使用 resolved 字段。
- 在 `checklist_result` 之后调用 `derive_final_judgment(...)`，传入 quality gate result/not-run reason 和 override。
- `TemplateRenderInput` 改传 final judgment decision 或 selected/derived/source 字段。
- `FundAnalysisResult` 增加 `final_judgment_decision`，便于测试和 CLI 观察，不影响 `report_markdown` property。
- 保持 `FundDataExtractor` 作为唯一生产文档入口，不新增任何直接文件访问。

### 5.4 `fund_agent/fund/template/renderer.py`

两种可接受实现，优先选择 A：

- A：`TemplateRenderInput` 增加 `final_judgment_decision: FinalJudgmentDecision`，删除单独 `final_judgment`。
- B：为降低改动，保留 `final_judgment`，新增 `derived_final_judgment`、`final_judgment_source`。

推荐 A，因为最终判断的 selected/derived/source 是一个不可拆分契约。

具体修改：

- 第 0 章和第 7 章使用 `decision.selected_judgment`。
- 第 7 章增加一句来源说明：
  - derived：`判断来源：系统根据检查清单、否决项、压力测试与质量 gate 派生。`
  - developer override：`判断来源：开发覆盖；系统派生判断为 ...。`
- `ProgrammaticAuditInput` 填入 selected、derived、source。
- `_validate_final_judgment()` 校验 selected 和 derived 都在允许集合。
- 不改变章节标题、证据附录标题或 CHAPTER_CONTRACT 结构。

### 5.5 `fund_agent/fund/audit/audit_programmatic.py`

- `ProgrammaticAuditInput` 增加：
  - `derived_final_judgment: FinalJudgment | None`
  - `final_judgment_source: FinalJudgmentSource | None`
- `_audit_required_inputs()`：
  - `final_judgment` 缺失仍 R2 fail。
  - `derived_final_judgment` 缺失也 R2 fail。
  - `final_judgment_source` 缺失也 R2 fail。
- `_audit_final_judgment()`：
  - 保留现有红灯/全绿规则。
  - 当 `final_judgment_source=="derived"` 时，`final_judgment != derived_final_judgment` 直接 R2 fail。
  - 当 `final_judgment_source=="developer_override"` 且二者不同，R2 fail，message 明确“开发覆盖与系统派生判断冲突”。
  - 非法 source 值 R2 fail。

### 5.6 `fund_agent/ui/cli.py`

- `analyze()` 新增 `--dev-override` boolean。
- product 参数保留：
  - `fund_code`
  - `--report-year`
  - `--investment-amount`
  - `--max-tolerable-loss-rate`
  - `--valuation-state`
  - `--user-money-horizon-years`
  - `--force-refresh`
- developer override 参数保留但放入 dev help panel：
  - `--equity-position`
  - `--actual-style`
  - `--actual-equity-position`
  - `--manager-tenure-months`
  - `--peer-fee-median`
  - `--tracking-error`
  - `--money-horizon`
  - `--current-stage`
  - `--final-judgment-override`，可带隐藏别名 `--final-judgment`
  - quality gate policy/source/output/run/golden 参数
- 新增 `_has_developer_override_options(...)` 和 `_build_developer_overrides(...)` 模块级 helper。
- 若传任一 dev 参数但未传 `--dev-override`，抛 `typer.BadParameter` 或输出 stderr 后 `Exit(2)`，message 指向 `--dev-override`。
- 构造 `FundAnalysisRequest(mode=..., developer_overrides=...)`。
- 删除普通用户路径对 `_final_judgment(...)` 的调用，只在 override helper 内使用。

### 5.7 `fund_agent/services/__init__.py`

- 导出 `AnalyzeMode`、`FundAnalysisDeveloperOverrides`。
- 如 `FinalJudgment` 继续从 services re-export，确保来源与 Capability policy 一致，避免 renderer/audit 各自定义漂移。

### 5.8 Tests

按第 6 节执行。

### 5.9 Documentation

按第 7 节执行。

## 6. Test Plan

### 6.1 New Focused Tests

`tests/fund/analysis/test_final_judgment.py`：

- risk veto 派生 `suggest_replace`。
- checklist red 派生 `suggest_replace`。
- `minus_20` 压力超过用户承受能力派生 `suggest_replace`。
- quality gate block 在 dev warn 路径派生 `needs_attention`。
- yellow/gray/insufficient 数据派生 `needs_attention`。
- 全绿、risk pass、quality pass 派生 `worth_holding`。
- override 选择 override judgment，同时保留 derived judgment 和 source。

`tests/services/test_fund_analysis_service.py`：

- `FundAnalysisRequest(fund_code="110011", quality gate off 不可用)` 改为最小 product request；用 fake extractor 验证可出报告，`final_judgment_decision.source=="derived"`。
- product request 不再需要 `equity_position` 等字段；R=A+B-C 可为 missing，报告仍可审计通过。
- product mode 固定 block，不能通过请求关闭 quality gate。
- developer override request 传入旧字段后仍能 computed R=A+B-C 并通过审计。
- developer override final judgment 与 derived 冲突时，程序审计失败并由 Service 抛 `ValueError`。
- warn/off quality gate 只在 developer override 生效。

`tests/ui/test_cli.py`：

- 默认 `analyze 110011` 构造 product request，`developer_overrides is None`。
- `--equity-position 80%` 未配 `--dev-override` 返回 exit 2。
- `--dev-override --equity-position 80% --final-judgment-override worth_holding --quality-gate-policy warn` 构造 nested override。
- `--quality-gate-policy off` 未配 `--dev-override` 返回 exit 2。
- product help/smoke 不需要 `--final-judgment`。

`tests/fund/template/test_renderer.py`：

- renderer 用 `FinalJudgmentDecision` 渲染 selected judgment。
- developer override 来源说明出现，且 `audit_input` 携带 selected/derived/source。
- 非法 selected 或 derived judgment 仍 fail closed。

`tests/fund/audit/test_audit_programmatic.py`：

- R2 要求 `derived_final_judgment` 和 `final_judgment_source`。
- derived source 下 selected/derived 不一致 fail。
- developer override source 下 selected/derived 不一致 fail。
- 保留红灯与全绿现有一致性测试。

### 6.2 Updated Existing Tests

- 所有直接构造旧 `FundAnalysisRequest(equity_position=..., final_judgment=...)` 的测试改为 nested `FundAnalysisDeveloperOverrides`。
- 旧 CLI 测试中验证 flat field 的断言改为检查 `last_request.developer_overrides`。
- P3 CLI e2e/smoke 如果需要确定性 computed R=A+B-C，应补 `--dev-override`。

### 6.3 Verification Commands

Targeted：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_final_judgment.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check
```

Full suite expectation：

```bash
.venv/bin/python -m pytest -q
```

若 full suite 失败，只能接受与本 slice 无关且有明确 root cause 的环境性失败；否则必须修复。

## 7. Documentation Updates

需要在实现和测试通过后同步：

- `README.md`：更新用户手册成功路径，只展示 `fund-analysis analyze 110011` 和少量 product 可选项；删除或移出普通用户 `--final-judgment`、`--equity-position` 等参数。
- `fund_agent/README.md`：更新 UI / Service / Fund Capability 边界，说明 analyze 有 product mode 和 developer override mode，最终判断由 Capability policy 派生。
- `fund_agent/fund/README.md`：新增最终判断派生 policy、R2 审计输入、developer override 冲突审计说明。
- `docs/design.md`：更新核心契约表中 `FundAnalysisRequest`，不再把 R=A+B-C/言行一致性/风险字段描述为普通用户显式输入；补充 final judgment derived policy。
- `tests/README.md`：若新增 final judgment policy 测试分层，补充测试约定。

不更新：

- 不写“未来将支持自动温度计估值映射”作为已实现能力。
- 不把 developer override 写进根 README 的 5 分钟用户成功路径。

## 8. Risks And Non-Goals

### 8.1 Risks

- **报告信息更常出现灰灯/数据不足**：这是 product contract 的正确结果，不应回退为要求普通用户补开发字段。风险通过最终判断默认 `needs_attention` 和下一步最小验证问题缓解。
- **final judgment policy 可能过严或过松**：首版规则必须用表驱动和测试锁定，后续根据真实样本再调阈值。
- **quality gate block 与 fund judgment 混淆**：policy 明确把数据质量 block 解释为 `needs_attention`，不直接等价为 `suggest_replace`。
- **旧 smoke 命令失败**：迁移要求旧手工命令补 `--dev-override`，并在 README/tests 中给出新写法。
- **类型别名漂移**：`FinalJudgment` 不应在 renderer、audit、service 多处重复定义；实现时收口到 Capability policy 或显式 re-export。

### 8.2 Non-Goals

- 不实现股票仓位、经理任期、同类费率、跟踪误差的新增 extractor。
- 不实现跨期当前阶段自动判断。
- 不实现温度计到估值状态的自动映射。
- 不改变 CHAPTER_CONTRACT 章节结构。
- 不引入 LLM 写作、外部 Dayu runtime、Host/Engine/tool loop。
- 不改变 `FundDocumentRepository` 的文档访问边界。

## 9. Review Checklist For MiMo/DS/GLM

Reviewers 请逐项检查：

- product mode 是否只需要最小输入，且不再暴露 `final_judgment` 为普通用户主路径输入。
- developer override 是否必须显式 `--dev-override`，且与 product success path 分离。
- `FundAnalysisRequest` 是否没有把显式参数塞进 `extra_payload` 或 dict 兜底。
- final judgment 派生是否在 Fund Capability，而不是 UI；Service 是否只做编排。
- R2 是否能同时审计 derived judgment 和 developer override 冲突。
- quality gate 在 product mode 是否保持 block fail-closed，warn/off 是否仅限 developer override。
- Service/UI/renderer/audit 是否没有直接访问 PDF、cache、下载 helper 或绕过 `FundDocumentRepository`。
- 是否没有引入外部 Dayu runtime、LLM、Host、Engine、tool loop 或 prompt scene registry。
- 测试是否覆盖 product minimal path、dev override path、final judgment policy、R2 conflict、CLI gating。
- README/design/doc 更新是否只描述当前实现，不把后续自动派生能力写成已完成事实。
