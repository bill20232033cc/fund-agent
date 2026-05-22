# 基金行为教练 Agent —— 设计真源文档

> **版本**: v2.2
> **日期**: 2026-05-22
> **状态**: 已按 2026-05-22 设计更新输入融合，并按 P14 / P15 / P16 / post-P16 / thermometer self-owned direction 设计对齐裁决校正
> **变更摘要**: v2.2 统一温度计口径：当前公开页查询是过渡实现，长期应开发项目内自建温度计；自动映射 `valuation_state` 仍需独立规则设计
> **关联文档**: `docs/implementation-control.md`（实施总控）、`fund-agent-mvp-plan.md`（MVP 计划书）、`docs/fund-analysis-template-draft.md`（定性模板 v2）、`docs/audit-alignment.md`（审计机制对照研究）

⚠️ **重要声明**：本文档记录已接受的设计意图和当前实现事实。若本文档、实施总控和代码发生冲突，以当前代码事实与最新 control-doc reconciliation artifact 为准，并应及时回写本文档；不得长期保留“设计未来”口径冒充已实现状态。

---

## 1. 设计目标

### 1.1 北极星

**让普通基金投资者在买入前获得专业级的基金体检报告，避免追涨杀跌的行为亏损。**

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| 确定性 MVP 主链路 | 当前 `fund-analysis analyze` 不依赖 LLM 写作或外部 Dayu Host/Engine，由结构化抽取、确定性分析、模板渲染、程序审计和 quality gate 组成 |
| 好资产 + 好价格 + 长期持有 | 有知有行核心理念：分析报告回答"好不好"，检查清单回答"该不该买" |
| 证据可审计 | 每条断言必须关联到年报具体章节，计算必须可追溯 |
| 模板驱动而非自由生成 | MVP 阶段用模板填充，避免 LLM 幻觉；v2 引入 LLM 写作 |
| 分层解耦 | 当前主链路为 UI / Service / Fund Capability 三层；Host/Engine/Agent runtime 能力如后续需要，应在本项目内按边界内化实现 |
| 基金类型判断优先 | 必须先识别标准基金类型，再应用对应 `preferred_lens` 与 `ITEM_RULE` |

### 1.3 非目标

- 不做全市场横向比较（MVP 在精选基金池内做质量门控）
- 不做实时行为偏差检测（改为买入前检查清单）
- 不把当前有知有行公开页面抓取视为长期温度计真源（当前只读查询是过渡能力；后续应在本项目内开发自建温度计计算与数据契约）
- 不把温度计数值隐式自动映射为 `valuation_state`（映射阈值、适用范围、证据来源和缺失策略必须单独设计并通过 gate）
- 不做组合管理（v2 阶段）
- 不输出买卖建议或仓位比例
- 不把外部 Dayu Host/Engine/tool loop 作为主链路依赖或运行时接口（pyproject.toml 已移除 dayu-agent 依赖）

---

## 2. 系统架构

### 2.1 当前实现架构

```
UI（CLI / Typer）→ Service（用例编排）→ Fund Capability（基金领域知识）
```

| 层级 | 职责 | 实现 | 边界约束 |
|------|------|------|---------|
| **UI** | 采集输入、渲染结果、质量 gate 摘要输出 | `fund_agent/ui/cli.py`（Typer） | 只依赖 Service 层接口，不直接调用 Capability |
| **Service** | 用例编排、请求/响应模型、质量 gate 策略 | `fund_agent/services/`（7 个服务） | 可调用 Capability，不直接读取年报文件/PDF/缓存 |
| **Capability** | 基金领域知识、文档仓库、结构化抽取、分析引擎、模板渲染、审计规则、质量门控 | `fund_agent/fund/` | 理解基金类型、财报章节、投资规则、有知有行方法论 |
| **Config** | 静态默认路径常量 | `fund_agent/config/paths.py` | 不读取 prompt manifest、workspace config、环境变量或运行时配置 |

> **关键决策**：MVP 阶段采用纯 Python 确定性管线，不依赖 LLM。`pyproject.toml` 已移除 `dayu-agent` 依赖；Dayu-Agent 只作为方法论和历史审计研究参考，不作为安装依赖、运行时接口或后续外部 API 包装目标。后续如需要 runner、trace、ToolRegistry 等 runtime 能力，应在 `fund_agent` 内按项目边界内化实现。

> **目录事实裁决**：`fund_agent/config` 的存在不代表 prompt manifest、scene registry 或 Dayu config runtime 已接入；当前没有通用 Fund tool runtime。空目录、本地未跟踪草案或审计输入不能单独作为设计事实。

### 2.2 执行链路

```
CLI（Typer app）
  → FundAnalysisService.analyze(request)
    → FundDataExtractor.extract(fund_code, year)  # P1 结构化抽取
      → FundDocumentRepository.load_annual_report()  # 文档仓库
        → documents layer source orchestration and cache internals
      → extract_profile / extract_performance / ...  # 章节 extractor
      → FundNavDataAdapter.load_nav_data()  # 净值数据
    → run_quality_gate_for_bundle(bundle)  # 质量门控（可选，在 P2 分析之前）
    → judge_alpha_nature / calculate_r_abc / check_consistency / ...  # P2 分析计算
    → render_template_report(render_input)  # 模板渲染
    → run_programmatic_audit(audit_input)  # 程序审计
  → stdout 输出报告 Markdown
```

**Service 层服务清单**（7 个）：

| 服务 | 文件 | 职责 |
|------|------|------|
| `FundAnalysisService` | `fund_analysis_service.py` | 主分析用例编排（P1 抽取 → P2 分析 → 模板渲染 → 审计） |
| `ExtractionSnapshotService` | `extraction_snapshot_service.py` | 精选基金池字段级抽取快照 |
| `ExtractionScoreService` | `extraction_score_service.py` | 字段级 coverage / traceability / correctness 评分 |
| `QualityGateService` | `quality_gate_service.py` | 报告质量门控（FQ0-FQ6 规则） |
| `GoldenPrefillService` | `golden_prefill_service.py` | golden answer 预填底稿生成 |
| `GoldenAnswerService` | `golden_answer_service.py` | golden answer Markdown → JSON 转换 |
| `ThermometerService` | `thermometer_service.py` | 有知有行温度计数据查询 |

**Service 层关键类型**：

| 类型 | 说明 |
|------|------|
| `FinalJudgment` | `Literal["worth_holding", "needs_attention", "suggest_replace"]` |
| `FinalJudgmentDecision` | 最终判断选择结果，包含 `selected_judgment`（实际采用）、`derived_judgment`（系统派生）、`source`（来源：derived/developer_override）、冲突原因 |
| `AnalyzeMode` | `Literal["product", "developer_override"]` |
| `FundAnalysisDeveloperOverrides` | 开发覆盖参数（最终判断、股票仓位、实际风格等） |
| `QualityGatePolicy` | `Literal["off", "warn", "block"]` |

`quality_gate_policy=block` 是 `analyze` 默认策略；低质量或 not-run gate 以结构化异常阻断并由 CLI 返回退出码 2。当前没有 `ExecutionContract` / `AgentInput` / scene preparation 主链路。

### 2.3 核心契约

| 契约 | 方向 | 说明 |
|------|------|------|
| `FundAnalysisRequest` | UI → Service | 基金代码、年报年份、分析参数、质量 gate 策略；开发覆盖参数通过 `FundAnalysisDeveloperOverrides` 且只能在 `developer_override` mode 生效 |
| `FundAnalysisResult` | Service → UI | 报告 Markdown、最终判断选择契约、质量 gate 摘要、审计结果 |
| `ValuationState` | Service 类型 | `Literal["low", "fair", "high", "unavailable"]` |
| `MoneyHorizon` | Service 类型 | `Literal["long_enough", "uncertain", "too_short"]` |
| `StructuredFundDataBundle` | Capability 内部 | P1 结构化数据包，聚合结构化年报抽取字段与 `NavDataResult` |
| `FinalJudgmentDecision` | Capability → Service/renderer/audit | 根据检查清单、否决项、压力测试和质量 gate 派生；开发覆盖只改变 `selected`，冲突交给 R2 审计 |
| `TemplateRenderInput` | Service → Capability renderer | P1/P2 结构化结果、`FinalJudgmentDecision`、当前阶段说明 |
| `TemplateRenderResult` | Capability renderer → Service | 8 章 Markdown、程序审计输入、章节块、lens 应用计划 |
| `ProgrammaticAuditInput` / `ProgrammaticAuditResult` | Capability renderer ↔ Capability audit | 程序审计输入与结果，覆盖章节结构、证据、R=A+B-C、检查清单和 selected/derived/source 最终判断一致性 |
| `QualityGateResult` | Capability quality gate → Service/UI | `pass / warn / block`、issue 列表、JSON/Markdown 产物路径 |

**依赖注入模式**：Service 层通过 Protocol 定义依赖（如 `_FundDataExtractor`、`_AnnualReportRepository`），生产使用真实实现，测试注入 fake。

---

## 3. 定性分析模板

### 3.1 模板结构（8 章）

| 章 | 标题 | 核心问题 | 数据来源 |
|----|------|---------|---------|
| 0 | 投资要点概览 | 这是什么基金？好不好？ | 后续章节汇总 |
| 1 | 这只基金到底是什么产品 | 买的是什么？怎么赚钱？ | 年报§1/§2 |
| 2 | R=A+B-C 收益归因 | 钱是怎么赚到的？ | 年报§3 + 净值数据 |
| 3 | 基金经理画像与言行一致性 | 基金经理靠不靠谱？ | 年报§4（说）vs §8（做） |
| 4 | 投资者获得感 | 买了的人赚到钱了吗？ | 年报§3（2026新规）+ §10 |
| 5 | 当前阶段与关键变化 | 为什么偏偏是现在？ | 跨期年报对比 |
| 6 | 核心风险与否决项 | 什么情况下直接放弃？ | 年报§2/§9 + 天天基金 |
| 7 | 是否值得持有——最终判断 | 结论是什么？ | 后续章节汇总 |

### 3.2 CHAPTER_CONTRACT 机制

**代码实现**：`fund_agent/fund/template/contracts.py`

每个章节都有 `ChapterContract` dataclass，定义：

- `chapter_id`：章节编号（0-7）
- `title`：章节标题
- `narrative_mode`：叙事模式（封面→动作→验证 / 拆解→判断→成本 / ...）
- `must_answer`：必须回答的问题列表
- `must_not_cover`：禁止覆盖的内容
- `required_output_items`：必须输出的条目
- `preferred_lens`：按基金类型动态适配的分析视角（`Mapping[str, TemplateLensRule]`）

**机器契约清单**：`TemplateContractManifest` 聚合 8 章 `ChapterContract`，提供 `load_template_contract_manifest()` 和 `validate_template_contract_manifest()` 函数。

**preferred_lens 规则**：`TemplateLensRule` 包含 `fund_type`、`statements`、`facets_any`、`priority` 字段。通过 `resolve_preferred_lens(manifest, fund_type)` 获取当前基金类型的 lens 规则。

### 3.3 ITEM_RULE 机制

**代码实现**：`fund_agent/fund/template/item_rules.py`

条件型条目——某些内容只在特定条件下出现：

- `mode: optional`：有披露就写，无披露写"未披露"（`missing_behavior: render_unavailable`）
- `mode: conditional`：有披露就写，无披露**必须删除整段**（`missing_behavior: delete_segment`）
- `facets_any`：条件触发（如 `facets_any: [主动权益基金]`）
- `fund_types_any`：由 facets 确定性映射的标准基金类型（如 `("active_fund",)`）
- `segment_markers_any`：用于定位已渲染段落的唯一小节标记

**已实现的 ITEM_RULE**（4 条）：

| rule_id | 章节 | 条目 | 触发条件 |
|---------|------|------|---------|
| `chapter_1_index_constituents` | 1 | 指数编制规则与成分股 | 指数基金（含增强） |
| `chapter_1_manager_philosophy` | 1 | 基金经理投资哲学 | 主动基金 |
| `chapter_2_alpha_yearly_breakdown` | 2 | 超额收益分年度拆解 | 主动基金 + 指数增强 |
| `chapter_2_tracking_error_analysis` | 2 | 跟踪误差分析 | 指数基金 + 指数增强 |

**评估机制**：`evaluate_template_item_rules(fund_type, facets=())` 返回 `TemplateItemRuleDecision` 列表，每条包含 `triggered`、`status`（render/delete）、`reason`。

**ITEM_RULE 审计 API**：

| 函数/类型 | 说明 |
|-----------|------|
| `evaluate_template_item_rule(rule, fund_type, facets=())` | 单条 ITEM_RULE 评估，返回 `TemplateItemRuleDecision` |
| `TemplateItemRuleAuditContext` | 审计上下文：`Literal["identity_missing", "identity_present"]` |
| `rendered_segment_present(markdown, rule)` | 判断渲染后的 Markdown 是否包含某条 ITEM_RULE 的唯一段落标记 |

**评估结果验证**：renderer 在渲染后调用 `_validate_template_item_rule_decisions()`，确保：
- 触发的 conditional 规则（`status="render"`）在最终 Markdown 中有对应段落标记
- 未触发的 conditional 规则（`status="delete"`）在最终 Markdown 中无对应段落标记
- 缺证章节在证据附录中显式标注

### 3.4 preferred_lens 机制

**代码实现**：`fund_agent/fund/fund_type.py` + `fund_agent/fund/template/contracts.py`

按基金类型动态调整分析重点：

| 基金类型 | FundType 标识 | 优先分析视角 |
|---------|-------------|-------------|
| 宽基指数基金 | `index_fund` | 跟踪误差、费率、规模流动性 |
| 行业/主题指数基金 | `index_fund` | 跟踪误差、行业集中度 |
| 策略指数基金 | `index_fund` | 跟踪误差、策略纯度 |
| 指数增强基金 | `enhanced_index` | 超额收益来源、跟踪误差 |
| 主动权益基金 | `active_fund` | 超额收益稳定性、基金经理、言行一致性 |
| 债券基金 | `bond_fund` | 信用风险、久期、最大回撤 |
| QDII 基金 | `qdii_fund` | 汇率风险、境外市场暴露 |
| FOF 基金 | `fof_fund` | 子基金质量、双重收费 |

**preferred_lens 确定性应用**（P8）：

renderer 通过 Capability 层 `LensApplicationPlan` 消费 `preferred_lens`：

| 组件 | 说明 |
|------|------|
| `LensFocusLabels` | 标准基金类型的确定性关注点标签（`primary_focus`、`watch_variable_label`、`risk_focus_label`） |
| `LensChapterApplication` | 单章 lens 应用事实（`chapter_id`、`lens_key`、`used_default`、`primary_focus` 等） |
| `LensApplicationPlan` | 聚合 8 章 lens 应用事实，供 renderer 消费 |
| `build_lens_application_plan(fund_type, chapter_ids=(0,1,2,3,4,5,6,7))` | 构建 lens 应用计划 |

当前确定性应用范围：第 0 章"当前最值得盯住的变量"和第 1 章"看这类基金最先看什么"使用 normalized 关注点标签填充报告 slot。Quality gate 的 FQ5 证明模板契约适用性，不证明 renderer 已完整执行 lens 语义。

---

## 4. 分析引擎

### 4.1 R=A+B-C 计算器

**代码实现**：`fund_agent/fund/analysis/r_abc.py` + `fund_agent/fund/analysis/_ratios.py`

```
R（总收益）= 基金净值增长率
B（Beta）= 业绩基准收益率 × 股票仓位
A（Alpha）= R - B
C（Cost）= 管理费 + 托管费 + 换手率 × 0.3%
净超额 = A - C
```

**公开接口**：
- `calculate_r_abc(input: RabcInput) -> RabcAttribution`
- `calculate_r_abc_from_bundle(bundle: StructuredFundDataBundle) -> tuple[RabcAttribution, ...]`
- `calculate_r_abc_series(...) -> tuple[RabcAttribution, ...]`

**关键区分**：结构性超额（可持续的能力）vs 阶段性超额（风格顺风/运气）

| 特征 | 结构性超额 | 阶段性超额 |
|------|-----------|-----------|
| 多年度为正 | 4/5 年以上 | 集中在某 1-2 年 |
| 不同市场环境 | 牛熊都为正 | 仅在特定风格顺风时 |
| 来源可解释 | 选股/配置能力 | 无法解释 |

### 4.2 超额收益性质判断

**代码实现**：`fund_agent/fund/analysis/alpha_judge.py`

**公开接口**：`judge_alpha_nature(attributions) -> AlphaJudgment`

基于多年度 R=A+B-C 归因结果，判断超额收益是结构性还是阶段性。输出 `AlphaJudgment` 包含 `rule`（判断规则）、`observations`（逐年观察）。

### 4.3 言行一致性检验

**代码实现**：`fund_agent/fund/analysis/consistency_check.py`

交叉验证年报§4（"说"）和年报§8（"做"）：

| 维度 | §4 宣称 | §8 实际 | 信号 |
|------|--------|--------|------|
| 投资风格 | 风格定位 | 实际持仓风格 | 🟢/🟡/🔴 |
| 行业偏好 | 看好行业 | 重仓行业 | 🟢/🟡/🔴 |
| 仓位管理 | 仓位策略 | 实际仓位 | 🟢/🟡/🔴 |
| 换手水平 | 持有周期 | 换手率 | 🟢/🟡/🔴 |

**公开接口**：`check_consistency(input) -> ConsistencyCheckResult`

### 4.4 投资者获得感分析

**代码实现**：`fund_agent/fund/analysis/investor_return.py`

```
行为损益 = 投资者实际收益 - 基金产品收益
```

- 数据来源：年报§3（2026 新规要求披露加权平均投资者收益率）
- 备用方案：份额变动 × 净值变化估算

**公开接口**：
- `analyze_investor_experience(input) -> InvestorExperienceResult`
- `calculate_behavior_gap(input) -> BehaviorGapResult`
- `judge_fund_flow(input) -> FundFlowResult`

### 4.5 否决项检查

**代码实现**：`fund_agent/fund/analysis/risk_check.py`

| 风险项 | 否决条件 |
|--------|---------|
| 清盘风险 | 规模 < 5000 万 |
| 基金经理离职 | 管理本基金 < 6 个月 |
| 风格严重漂移 | 言行一致性检验 🔴 |
| 费率远超同类 | 总成本 > 同类 2 倍中位数 |
| 跟踪误差过大 | 指数基金 > 2% |

**公开接口**：`run_risk_checks(input) -> RiskCheckResult`

### 4.6 压力测试

**代码实现**：`fund_agent/fund/analysis/risk_check.py`（同上）

模拟 -20%/-40%/-60% 三个场景（借鉴 E大网格策略理念）。按基金类型使用差异化阈值。

**公开接口**：`run_stress_test(input) -> StressTestResult`

### 4.7 买入前检查清单

**代码实现**：`fund_agent/fund/analysis/checklist.py`

7 个问题，红/黄/绿灯判定：

| # | 问题 | 数据来源 |
|---|------|---------|
| 1 | 超额收益能覆盖成本吗？ | R=A+B-C |
| 2 | 基金经理跟我一条心吗？ | 年报§9 |
| 3 | 投资者真的赚到钱了吗？ | 年报§3 |
| 4 | 说的和做的一样吗？ | §4 vs §8 |
| 5 | 这只基金"不死"吗？ | 天天基金 |
| 6 | 当前估值处于什么位置？ | 温度计 |
| 7 | 这笔钱 3-4 年内不会用吗？ | 用户输入 |

**公开接口**：`run_checklist(input) -> ChecklistResult`

### 4.8 最终判断派生（P10）

**代码实现**：`fund_agent/fund/analysis/final_judgment.py`

最终判断由 Fund Capability policy 派生，不直接由用户输入或开发覆盖决定：

| 条件 | 派生判断 | 说明 |
|------|---------|------|
| 否决项存在、检查清单红灯、基础 -20% 压力场景越过用户承受能力 | `suggest_replace` | 必须建议替换 |
| 质量 gate block/not-run、黄灯/灰灯/数据不足、watch 项 | `needs_attention` | 需要关注 |
| 检查清单全绿、否决项通过、质量 gate pass/warn、压力测试未越界 | `worth_holding` | 值得持有 |
| 未命中更明确条件 | `needs_attention` | fail-safe 默认 |

**开发覆盖模式**（`developer_override`）：
- 只允许在 `AnalyzeMode.DEVELOPER_OVERRIDE` 下生效
- 覆盖只改变 `selected_judgment`，不改变 `derived_judgment`
- 覆盖与派生不一致时，记录 `conflict_reasons` 供 R2 审计使用

**公开接口**：
- `derive_final_judgment(checklist_result, risk_check_result, stress_test_result, quality_gate_status, ...) -> FinalJudgmentDecision`

---

## 5. 审计机制

### 5.1 三层审计架构

```
程序审计（P1/P2/P3/C2/L1/R1/R2 规则，已实现）
  → LLM 审计（证据充分性 + 内容合规性，v2）
    → 证据复核（年报 PDF 搜索验证，v2）
```

### 5.2 审计规则体系

**代码实现**：
- `fund_agent/fund/audit/audit_programmatic.py`—— 程序审计执行器
- `fund_agent/fund/audit/contract_rules.py`—— CHAPTER_CONTRACT C2 审计规则

| 规则码 | 含义 | 阻断级别 | MVP 阶段 | 代码位置 |
|--------|------|----------|---------|---------|
| P1 | 章节结构不匹配 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| P2 | 内容过短（<10字符） | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| P3 | 缺少"证据与出处"小节 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| C2 | 章节越界（展开禁止话题） | 阻断 | ✅ 实现 | `contract_rules.py` |
| L1 | R=A+B-C 计算错误 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| R1 | 检查清单规则错误 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| R2 | 判定与评分不一致 | 阻断 | ✅ 实现 | `audit_programmatic.py` |
| E1 | 证据锚点不精确 | 可复核 | ⬜ v2 | — |
| E2 | 证据与断言不匹配 | 可复核 | ⬜ v2 | — |
| E3 | 证据完全缺失 | 需重建 | ⬜ v2 | — |
| C1 | 内容违规（幻觉） | 阻断 | ⬜ v2 | — |
| L2 | 百分位计算错误 | 可复核 | ⬜ v2 | — |

**C2 审计实现细节**（`contract_rules.py`）：
- `ContractRequiredItemRule`：required_output_items 的字面 marker 规则（40+ 条）
- `ContractForbiddenContentRule`：must_not_cover 的字面禁止 marker 规则（9 条）
- `load_programmatic_contract_rules()`：加载并校验规则集合
- 规则通过 `validate_programmatic_contract_rules()` 与 CHAPTER_CONTRACT manifest 交叉校验

**公开接口**：`run_programmatic_audit(input: ProgrammaticAuditInput) -> ProgrammaticAuditResult`

### 5.3 修复闭环机制（v2）

借鉴 Dayu-Agent 的修复策略，根据违规严重程度选择修复粒度：

| 修复策略 | 触发条件 | 说明 |
|---------|---------|------|
| **none** | 审计通过 | 无需修复 |
| **patch** | E1/E2/C2 类违规 | 局部修补（删除断言/修正锚点/补充证据） |
| **regenerate** | P1/P2/P3/E3/C1 类违规 | 整章重建 |

> 详细对照分析见 `docs/audit-alignment.md`。

### 5.4 证据锚点格式

**代码实现**：`fund_agent/fund/extractors/models.py` —— `EvidenceAnchor` dataclass

| 数据类型 | 锚点格式 | source_kind |
|---------|---------|-------------|
| 年报数据 | `年报{年份}§{章节}表{编号}行{行号}` | `annual_report` |
| 外部 API | `外部数据(external_api)` | `external_api` |
| 计算结果 | `计算(derived)` | `derived` |

`EvidenceAnchor` 字段：`source_kind`、`document_year`、`section_id`、`page_number`、`table_id`、`row_locator`、`note`。

---

## 6. 数据源与文档仓库

### 6.1 文档仓库层

**代码实现**：`fund_agent/fund/documents/`

对基金文档的存取统一通过 `FundDocumentRepository`，禁止直接操作文件系统。

| 模块 | 文件 | 职责 |
|------|------|------|
| 仓库入口 | `repository.py` | `FundDocumentRepository` —— 对外唯一文档读取入口 |
| 数据模型 | `models.py` | `ParsedAnnualReport`、`ParsedTable`、`ReportSection`、`DocumentKey` 等 |
| 缓存层 | `cache.py` | `AnnualReportDocumentCache` —— PDF + parsed report 两级缓存，schema 版本控制 |
| 数据源 | `sources.py` | EID/证监会资本市场统一信息披露平台主源 + Eastmoney fallback 编排 |
| PDF 适配器 | `adapters/annual_report_pdf.py` | `AnnualReportPdfAdapter` —— PDF 下载 + 解析适配 |

**来源失败分类与 fallback 策略**（P8-S3）：

当 EID/证监会资本市场统一信息披露平台主源失败时，系统根据失败类别决定是否允许 fallback 到 Eastmoney 备用源：

| 失败类别 | 是否允许 fallback | 说明 |
|---------|------------------|------|
| `not_found` | 是 | 来源正常响应但没有目标基金/年份年报 |
| `unavailable` | 是 | 网络、超时、服务端或本地依赖临时不可用 |
| `schema_drift` | 否 | 官方来源响应结构、字段或附件形态偏离契约 |
| `identity_mismatch` | 否 | 返回候选与基金代码、基金 ID、年份或报告类型矛盾 |
| `integrity_error` | 否 | PDF Content-Type、文件头或写入内容完整性失败 |

**代码实现**：`fund_agent/fund/documents/sources.py`
- `AnnualReportSourceFailure`：记录失败类别、原始异常、上下文
- `AnnualReportSourceFallbackBlockedError`：当非 eligible 失败触发 fallback 时抛出，强制开发者显式处理

**缓存策略**：
- PDF 文件缓存：按 `cache/annual-reports/{fund_code}/{year}.pdf` 路径缓存
- Parsed report 缓存：JSON 格式，带 `PARSED_REPORT_SCHEMA_VERSION` 版本号
- 来源元数据：`AnnualReportSourceMetadata` 记录下载来源、URL、fallback 状态

### 6.2 结构化抽取层

**代码实现**：`fund_agent/fund/extractors/`

| 模块 | 文件 | 抽取内容 | 年报章节 |
|------|------|---------|---------|
| 基础画像 | `profile.py` | 基金名称、类型、费率、投资目标/范围/策略、风格定位、业绩基准、指数画像 `index_profile` | §1/§2 |
| 表现数据 | `performance.py` | 净值增长率、基准收益率、投资者收益率、直接披露跟踪误差 `tracking_error` | §3/§2 |
| 管理人 | `manager_ownership.py` | 管理人策略原文、换手率、基金经理持有、持有人结构 | §4/§8/§9 |
| 持仓变动 | `holdings_share_change.py` | 前十大重仓、行业分布、份额变动 | §8/§10 |
| 数据模型 | `models.py` | `EvidenceAnchor`、`ExtractedField[T]`、各抽取结果 dataclass | — |

**P1 数据 façade**：`fund_agent/fund/data_extractor.py`
- `FundDataExtractor`：编排文档仓库 + 净值适配器 + 章节 extractor
- `StructuredFundDataBundle`：聚合 profile、performance、manager、holdings、share change 和 nav 数据；当前包含 `index_profile` 与 `tracking_error` 结构化字段

**抽取模式**（`ExtractionMode`）：
- `direct`：直接从年报文本/表格提取
- `derived`：从多个字段计算得出
- `estimated`：数据缺失时按同类中位数估算
- `missing`：无法获取

### 6.3 外部数据

| 数据 | 来源 | 获取方式 | 代码位置 |
|------|------|---------|---------|
| 基金年报 PDF | EID/证监会资本市场统一信息披露平台主源 + Eastmoney fallback | httpx 下载 | `documents/sources.py` |
| 基金净值序列 | 天天基金 / akshare | API | `data/nav_data.py` |
| 温度计快照（当前） | 有知有行公开页面 | httpx + HTML 解析 | `data/thermometer.py` |
| 自建温度计（后续方向） | 项目内定义的数据源与计算口径 | 待设计；必须显式记录输入、公式、缓存、失败语义与证据来源 | 待后续 phase |
| 精选基金池 | 手动维护 CSV | 文件读取 | `extraction_snapshot.py` |

当前温度计能力通过 `ThermometerService` 与 `fund-analysis thermometer` CLI 暴露，只做有知有行公开页只读查询与缓存复用。这是过渡实现，不是长期设计终点。后续应开发项目内自建温度计能力，至少明确指数/市场覆盖范围、估值指标、分位数窗口、数据源可靠性、缓存策略、不可用状态和测试夹具。

即使自建温度计落地，也不得默认把温度计数值自动映射为买入前检查清单的 `valuation_state`，也不得静默参与 `fund-analysis analyze` 默认分析判断；映射规则必须单独设计，并保留用户显式输入优先级、缺失时灰灯/不可用语义和审计证据。

### 6.4 年报章节映射

| 年报章节 | 内容 | 用于 |
|---------|------|------|
| §1/§2 | 基金简介、费率、投资目标/范围/策略 | 第 1 章、第 2 章 |
| §3 | 净值、基准、投资者收益率 | 第 2 章、第 4 章 |
| §4 | 管理人报告（基金经理观点） | 第 3 章（"说"） |
| §8 | 投资组合报告（持仓、换手率） | 第 3 章（"做"） |
| §9 | 持有人结构、自购 | 第 3 章、第 6 章 |
| §10 | 份额变动 | 第 4 章 |

### 6.5 基金类型识别规则

**代码实现**：`fund_agent/fund/fund_type.py`

`FundType = Literal["index_fund", "active_fund", "bond_fund", "enhanced_index", "qdii_fund", "fof_fund"]`

识别基于年报 §1/§2 的稳定披露信息，按优先级执行：

1. **指数关键词**：名称含"指数"/"ETF"/"联接" → `index_fund`
2. **增强标识**：名称含"增强" → `enhanced_index`
3. **QDII 标识**：名称含"QDII"/"境外" → `qdii_fund`
4. **FOF 标识**：名称含"FOF"/"基金中基金" → `fof_fund`
5. **债券类别**：基金类别含"债券"/"中债" → `bond_fund`
6. **主动权益**：基金类别含"混合型"/"股票型" → `active_fund`

**公开接口**：`classify_fund_type(report: ParsedAnnualReport) -> FundTypeClassification`

### 6.6 错误处理与降级策略

| 失败场景 | 影响章节 | 处理策略 | 报告输出 |
|---------|---------|---------|---------|
| PDF 下载失败 | 全部 | 尝试 fallback 源 → 抛出异常 | Service 层捕获并报告 |
| 章节解析失败 | 特定章节 | extractor 返回 `extraction_mode="missing"` | 模板渲染写"未披露" |
| 关键数据缺失 | 第 2 章 | `extraction_mode="estimated"` + note 说明 | "换手率未披露，按同类中位数估算" |
| 2026 新规数据未披露 | 第 4 章 | 份额变动 × 净值变化估算 | "投资者收益率未披露，用份额变动估算" |
| 温度计获取失败 | 检查清单 | 使用过期缓存或返回 unavailable | "⚠️ 温度数据暂时不可用" |

---

## 7. 质量门控体系（P4）

### 7.1 三阶段质量管线

```
P4-S1: extraction_snapshot  —— 精选基金池字段级抽取快照
  → P4-S2: extraction_score  —— coverage / traceability / correctness 评分
    → P4-S3: quality_gate  —— FQ0-FQ6 质量规则门控
```

### 7.2 抽取快照（extraction_snapshot）

**代码实现**：`fund_agent/fund/extraction_snapshot.py`

- 读取精选基金池 CSV（`docs/code_20260519.csv`）
- 对每只基金调用 `FundDataExtractor.extract()`
- 将 `StructuredFundDataBundle` 拆成字段级 `SnapshotRecord`
- 输出 JSONL、错误明细和人工可读 summary

**字段顺序**（当前字段组）：`basic_identity` → `product_profile` → `benchmark` → `index_profile` → `fee_schedule` → `classified_fund_type` → `nav_benchmark_performance` → `investor_return` → `tracking_error` → `manager_strategy_text` → `turnover_rate` → `manager_alignment` → `holder_structure` → `holdings_snapshot` → `share_change` → `nav_data`

### 7.3 抽取评分（extraction_score）

**代码实现**：`fund_agent/fund/extraction_score.py`

对每个字段计算：
- **coverage**：`value_present=True` 的比例（阈值：pass ≥ 90%, watch ≥ 70%）
- **traceability**：`anchor_present=True` 的比例（阈值同上）
- **correctness**：与 golden answer 比对（match/mismatch/unavailable）

**字段优先级**：
| 优先级 | 字段 |
|--------|------|
| P0 | basic_identity, classified_fund_type, benchmark, nav_benchmark_performance, fee_schedule, manager_strategy_text |
| P1 | product_profile, index_profile, tracking_error, turnover_rate, holder_structure, manager_alignment, holdings_snapshot, share_change |
| P2 | investor_return, nav_data |

`index_profile` 和 `tracking_error` 是指数基金 / 指数增强基金的条件 P1 字段。非指数基金不把这两个字段纳入 coverage / traceability / fund quality 分母；未知或冲突基金类型保持保守处理。

### 7.4 质量门控规则（quality_gate）

**代码实现**：`fund_agent/fund/quality_gate.py`

| 规则码 | 含义 | 严重级别 | 说明 |
|--------|------|---------|------|
| FQ0 | 前置条件缺失 | info | score.json 缺少必要数据段，相关规则跳过 |
| FQ1 | 正确性/类别冲突 | block | 抽取值与 golden answer 冲突，或 App 类别与系统类型冲突 |
| FQ2 | 字段覆盖率/可追溯性未达标 | block/warn | P0 字段未达标阻断，P1 字段未达标警告 |
| FQ2F | 基金级评分失败 | block/warn | 单只基金整体 P0/P1 字段存在失败 |
| FQ3 | P0 证据锚点不足 | block | P0 字段 traceability < 90%，证据不可溯源 |
| FQ4 | snapshot 字段缺失率过高 | block/warn | 缺失率 ≥ 20% 警告，≥ 35% 阻断 |
| FQ5 | 模板契约（preferred_lens）不匹配 | block/info | mismatch 阻断，resolved/not_applicable 信息级 |
| FQ6 | 抽取流程完全失败 | block | 基金整个抽取流程异常 |

**质量 gate 集成**：`fund_agent/fund/quality_gate_integration.py`
- `run_quality_gate_for_bundle()`：将 `StructuredFundDataBundle` 转换为 snapshot → score → gate 产物
- 当前基金不在精选池时返回 `not_run_reason`，不伪造 App 类别

Golden Answer pipeline 由预填底稿、人工复核、strict JSON 构建和 correctness 比对组成。当前 quality gate 只消费可复核基准与结构化产物；基准覆盖不足时，应扩大 golden coverage 或降级为显式 residual risk，不能把少量 golden answer 误当全域正确性证明。`tracking_error` 生产 golden rows 只有在 reviewed direct observed disclosure evidence 被接受后才能添加。

### 7.5 ITEM_RULE 合规审计（P12）

**代码实现**：`fund_agent/fund/template/item_rules.py`

| 函数/类型 | 说明 |
|-----------|------|
| `TemplateItemRuleAuditContext` | 审计上下文：章节 ID、ITEM_RULE 定义、渲染后内容、证据锚点 |
| `evaluate_template_item_rule()` | 评估单条 ITEM_RULE 合规性 |
| `rendered_segment_present()` | 后渲染校验：检查渲染后内容是否包含 ITEM_RULE 要求的片段 |

**审计时机**：模板渲染完成后，对每章执行 ITEM_RULE 校验，确保 must_answer 问题被回答、must_not_cover 内容未出现。

### 7.6 Golden Answer 机制

**代码实现**：
- `fund_agent/fund/golden_prefill.py`—— 预填底稿生成
- `fund_agent/fund/golden_answer.py`—— Markdown → JSON 转换与校验

流程：`GoldenPrefillService`（自动预填）→ 人工复核 → `GoldenAnswerService`（转 JSON）→ `extraction_score`（correctness 比对）

---

## 8. 模板渲染

### 8.1 渲染器

**代码实现**：`fund_agent/fund/template/renderer.py`

`render_template_report(input: TemplateRenderInput) -> TemplateRenderResult`

渲染流程：
1. 校验最终判断（只允许 worth_holding / needs_attention / suggest_replace）
2. 收集证据锚点
3. 按章节 0-7 依次渲染（`_render_chapter_0` ~ `_render_chapter_7`）
4. 渲染证据附录（`## 证据与出处`）
5. 校验禁用词（"买入"/"卖出"/"仓位比例"/"收益预测"）
6. 切分章节块（`split_rendered_chapter_blocks`）
7. 构建程序审计输入

### 8.2 最终判断推导（P10）

**代码实现**：`fund_agent/fund/analysis/final_judgment.py`

`derive_final_judgment(...)` 从检查清单结果、风险检查结果、压力测试结果、质量门控状态，推导出最终判断：

| 判断值 | 含义 | 触发条件 |
|--------|------|----------|
| `worth_holding` | 值得持有 | 无否决项，检查清单通过，质量门控通过 |
| `needs_attention` | 需要关注 | 存在需要监控的风险信号，但未达替换标准 |
| `suggest_replace` | 建议替换 | 存在否决项，或检查清单未通过，或质量门控阻断 |

**开发者覆盖模式**：
- 允许开发者显式传入 `final_judgment_override` 覆盖推导结果
- 覆盖时记录 `FinalJudgmentSource.DEVELOPER_OVERRIDE` 和冲突信息
- 用于 R2 审计：检测开发者覆盖与程序推导的不一致

### 8.3 章节块切分

**代码实现**：`fund_agent/fund/template/chapter_blocks.py`

`split_rendered_chapter_blocks(report_markdown) -> tuple[RenderedChapterBlock, ...]`

按 `# {chapter_id}. {title}` 一级标题切分，校验章节完整性（0-7 必须全部存在、无重复、无乱序）。

---

## 9. 项目结构

以下结构用于说明当前主要模块边界，不作为逐文件 inventory；新增 helper、review artifact 和运行产物以代码与
`docs/implementation-control.md` 为准。

### 9.0 CLI 命令清单

| 命令 | 功能 | 当前状态 |
|------|------|----------|
| `fund-analysis analyze` | 主分析入口 | 已实现；默认运行 quality gate，低质量以结构化错误阻断 |
| `fund-analysis checklist` | 独立检查清单入口 | 占位；当前提示用户先使用 `analyze` 并以非零状态退出 |
| `fund-analysis thermometer` | 温度计查询 | 当前已实现有知有行公开页 read-only 查询；后续应迁移为项目内自建温度计口径；不自动映射估值状态 |
| `fund-analysis extraction-snapshot` | 精选基金池字段级抽取快照 | 已实现 |
| `fund-analysis extraction-score` | 字段级 coverage / traceability / correctness 评分 | 已实现 |
| `fund-analysis golden-prefill` | Golden answer 预填底稿 | 已实现 |
| `fund-analysis golden-build` | Golden answer Markdown 到 strict JSON 构建 | 已实现 |
| `fund-analysis quality-gate` | 对 score JSON 运行质量门控 | 已实现 |

```text
fund-agent/
├── fund_agent/
│   ├── __init__.py
│   ├── ui/                              # UI 层
│   │   ├── __init__.py
│   │   └── cli.py                       # Typer CLI 入口（analyze / checklist / thermometer）
│   ├── services/                        # Service 层（7 个服务）
│   │   ├── __init__.py                  # 公共导出（Request/Result/Service 类型）
│   │   ├── fund_analysis_service.py     # 主分析用例编排
│   │   ├── extraction_snapshot_service.py
│   │   ├── extraction_score_service.py
│   │   ├── quality_gate_service.py
│   │   ├── golden_prefill_service.py
│   │   ├── golden_answer_service.py
│   │   └── thermometer_service.py
│   ├── fund/                            # Capability 层
│   │   ├── __init__.py
│   │   ├── fund_type.py                 # 基金类型识别（FundType + classify_fund_type）
│   │   ├── data_extractor.py            # P1 结构化数据 façade（FundDataExtractor）
│   │   ├── extraction_snapshot.py       # P4-S1 抽取快照
│   │   ├── extraction_score.py          # P4-S2 抽取评分
│   │   ├── golden_answer.py             # golden answer Markdown → JSON
│   │   ├── golden_prefill.py            # golden answer 预填底稿
│   │   ├── quality_gate.py              # P4-S3 质量门控规则
│   │   ├── quality_gate_integration.py  # 单基金 quality gate 集成
│   │   ├── documents/                   # 文档仓库层
│   │   │   ├── __init__.py              # 导出 FundDocumentRepository
│   │   │   ├── repository.py            # 仓库入口（Protocol + 默认实现）
│   │   │   ├── models.py                # ParsedAnnualReport / ParsedTable / DocumentKey
│   │   │   ├── cache.py                 # PDF + parsed report 两级缓存
│   │   │   ├── sources.py               # 多源年报来源编排（EID 主源 + Eastmoney fallback）
│   │   │   └── adapters/
│   │   │       ├── __init__.py
│   │   │       └── annual_report_pdf.py # PDF 下载 + 解析适配器
│   │   ├── extractors/                  # 结构化抽取层
│   │   │   ├── __init__.py              # 导出 ExtractedField / EvidenceAnchor
│   │   │   ├── models.py                # EvidenceAnchor / ExtractedField[T] / 各 Result
│   │   │   ├── profile.py               # §1/§2 基础画像抽取
│   │   │   ├── performance.py           # §3 表现数据抽取
│   │   │   ├── manager_ownership.py     # §4/§8/§9 管理人抽取
│   │   │   └── holdings_share_change.py # §8/§10 持仓变动抽取
│   │   ├── analysis/                    # 分析引擎
│   │   │   ├── __init__.py              # 公共导出
│   │   │   ├── r_abc.py                 # R=A+B-C 收益归因
│   │   │   ├── alpha_judge.py           # 超额收益性质判断
│   │   │   ├── consistency_check.py     # 言行一致性检验
│   │   │   ├── investor_return.py       # 投资者获得感分析
│   │   │   ├── risk_check.py            # 否决项检查 + 压力测试
│   │   │   ├── checklist.py             # 7 问题检查清单
│   │   │   ├── final_judgment.py        # P10 最终判断推导（worth_holding/needs_attention/suggest_replace）
│   │   │   └── _ratios.py               # 内部比率计算工具
│   │   ├── audit/                       # 审计机制
│   │   │   ├── __init__.py              # 导出 run_programmatic_audit
│   │   │   ├── audit_programmatic.py    # 程序审计执行器（P1/P2/P3/L1/R1/R2）
│   │   │   └── contract_rules.py        # CHAPTER_CONTRACT C2 审计规则
│   │   ├── template/                    # 模板系统
│   │   │   ├── __init__.py              # 公共导出（lazy load renderer）
│   │   │   ├── contracts.py             # CHAPTER_CONTRACT 机器契约
│   │   │   ├── item_rules.py            # ITEM_RULE 机器契约
│   │   │   ├── lens_application.py      # P8 preferred_lens 应用计划
│   │   │   ├── renderer.py              # 8 章模板渲染器
│   │   │   └── chapter_blocks.py        # 章节块切分工具
│   │   ├── pdf/                         # PDF 基础设施
│   │   │   ├── __init__.py
│   │   │   ├── downloader.py            # PDF 下载
│   │   │   └── parser.py                # PDF 文本/表格解析（含章节目录定位）
│   │   ├── data/                        # 外部数据获取
│   │   │   ├── __init__.py
│   │   │   ├── nav_data.py              # 净值数据（天天基金/akshare）
│   │   │   └── thermometer.py           # 温度计（有知有行公开页面）
│   └── config/
│       ├── __init__.py
│       └── paths.py                     # P10 路径常量（DEFAULT_SELECTED_FUNDS_CSV 等）
├── scripts/
│   └── selected_funds_smoke.py          # 精选基金池冒烟测试
├── tests/                               # 测试
│   ├── fund/
│   │   ├── analysis/                    # 分析引擎测试（6 个文件）
│   │   ├── audit/                       # 审计测试
│   │   ├── documents/                   # 文档仓库测试
│   │   ├── extractors/                  # 抽取器测试（4 个文件）
│   │   ├── template/                    # 模板测试（3 个文件）
│   │   ├── pdf/                         # PDF 测试
│   │   ├── data/                        # 数据获取测试
│   │   ├── integration/                 # 集成测试
│   │   ├── test_extraction_snapshot.py
│   │   ├── test_extraction_score.py
│   │   ├── test_golden_answer.py
│   │   ├── test_golden_prefill.py
│   │   └── test_quality_gate.py
│   ├── services/                        # Service 层测试（5 个文件）
│   ├── ui/                              # UI 测试
│   ├── scripts/                         # 脚本测试
│   └── fixtures/                        # 测试固件
│       └── fund/
│           ├── extractors/              # 抽取器测试固件
│           └── pdf_sections/            # PDF 章节测试固件
├── reports/                             # 运行产物
│   └── golden-answers/                  # golden answer 产物
├── docs/                                # 设计文档
│   ├── design.md                        # 本文档（设计真源）
│   ├── implementation-control.md        # 实施总控
│   ├── implementation-control-p4.md     # P4 质量体系实施控制
│   ├── audit-alignment.md               # 审计机制对照研究
│   ├── fund-analysis-template-draft.md  # 定性模板 v2
│   ├── golden-answer-template.md        # golden answer 模板
│   ├── golden-answer-instructions.md    # golden answer 操作说明
│   └── reviews/                         # phaseflow / code review / controller judgment artifacts
├── pyproject.toml
├── uv.lock
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

### 9.1 Dayu-Agent 依赖状态（P9 更新）

| Dayu-Agent 模块 | pyproject.toml | 代码导入 | 说明 |
|---|---|---|---|
| `dayu-agent` 包 | ❌ 已移除 | ❌ 零导入 | P9: pyproject.toml 已移除 dayu-agent 依赖，MVP 纯 Python 实现 |
| Engine/Host/Prompting/Config | — | ❌ 未使用 | 计划 v2 LLM 写作阶段如需接入再重新评估 |
| 审计机制架构 | — | 🔧 借鉴 | audit→confirm→repair 三阶段架构参考，代码独立实现 |
| `dayu.fins` 分层 | — | 📐 参考 | Processor/Repository/Pipeline 分层思想，实现不适用 |

---

## 10. 设计决策记录

| 决策 | 选择 | 备选方案 | 理由 |
|------|------|---------|------|
| 架构模式 | 三层纯 Python（UI/Service/Capability） | 外部 Dayu Host/Engine 主链路 | MVP 不依赖 LLM，确定性管线更可靠；后续 runtime 能力如需要必须在本项目边界内化 |
| CLI 框架 | Typer | Click / argparse | 类型注解友好，与 FastAPI 生态一致 |
| 输出格式 | 8 章定性模板 | 一页纸报告 | 信息更完整，覆盖全链路 |
| 超额收益判断 | 区分结构性 vs 阶段性 | 仅计算 A=R-B | 第一性原理：可持续能力 vs 运气 |
| 检查清单位置 | 嵌入报告第 7 章 + 独立 checklist 模块 | 仅嵌入报告 | checklist 独立模块可复用，报告内通过 checklist_result 渲染 |
| PDF 解析 | pdfplumber | PyPDF2 | 表格提取能力更强 |
| 文档存取 | 统一仓库（FundDocumentRepository） | 直接文件操作 | 隔离 PDF/缓存细节，支持 Protocol 注入测试 |
| 数据缓存 | PDF 文件缓存 + parsed report JSON 缓存 | 仅文件缓存 | 避免重复解析，schema 版本控制支持缓存失效 |
| 年报来源 | EID/证监会资本市场统一信息披露平台主源 + Eastmoney fallback | Eastmoney 作为同级主源 | 官方来源优先；schema drift、identity mismatch、integrity error 必须 fail-closed |
| 审计策略 | MVP 程序审计（P1/P2/P3/C2/L1/R1/R2） | 三层全实现 | 降低复杂度，v2 引入 LLM 审计 |
| 质量门控 | FQ0-FQ6 规则 + golden answer correctness | 无质量门控 | 确保精选基金池抽取质量可量化追踪 |
| 温度计 | 当前保留有知有行公开页面 read-only 查询；后续开发项目内自建计算口径 | 永久依赖有知有行页面抓取 | 公开页抓取不是长期稳定真源；自建能力必须在项目边界内定义数据源、公式、缓存、失败语义和审计证据 |
| 依赖注入 | Protocol + 构造函数默认值 | 框架级 DI | 轻量级，不引入额外依赖，测试友好 |
| ITEM_RULE | 代码内硬编码 manifest | 外部 YAML 配置 | 规则数量少（4 条），代码内定义可获类型检查 |
| 模板渲染 | 纯 Python 函数 | Jinja2 / LLM | MVP 确定性管线，避免模板引擎或 LLM 幻觉 |
| Dayu-Agent 依赖 | P9 完全移除 | 保留声明但不使用 | 零导入证明无实际依赖，清理技术债 |
| 最终判断推导 | P10 程序化推导 + 开发者覆盖模式 | 纯人工判断 | 结构化输入 → 确定性输出，覆盖模式记录审计线索 |
| 来源失败分类 | P8-S3 五类失败 + fallback 资格判定 | 统一 fallback 策略 | 区分"可重试失败"与"契约违背"，防止错误传播 |
| ITEM_RULE 审计 | P12 后渲染校验（`rendered_segment_present`） | 仅前置校验 | 确保渲染后内容符合 ITEM_RULE 约束 |
| 跟踪误差披露 | P13/P14/P15 分阶段推进 | 可选且不可观测 | 指数基金核心指标；P13 建立结构化直接披露路径，P14 将其纳入指数/增强指数条件质量分母，P15 先获取 reviewed direct evidence，再决定是否进入 production golden |

## 11. Plan Review 设计边界检查

每个后续 plan review 必须显式检查：

- 是否违反 §1.3 非目标；
- 是否保持 UI / Service / Capability / Runtime / Engine 边界；
- 生产年报访问是否仍只通过 `FundDocumentRepository` / `FundDataExtractor`；
- 是否引入外部 Dayu runtime、LLM 写作、Evidence Confirm、计算型 tracking error、外部指数适配器或隐藏在 `extra_payload` 的显式参数；
- success signal 是否可验证，且不会激励在缺少直接证据时错误接受数据。
