# 基金行为教练 Agent —— 设计真源文档

> **版本**: v1.1
> **日期**: 2026-05-21
> **状态**: 已按 P7 / repo-level deepreview 后代码事实对齐
> **关联文档**: `docs/implementation-control.md`（实施总控）、`fund-agent-mvp-plan.md`（MVP 计划书）、`fund-analysis-template-draft.md`（定性模板 v2）、`docs/audit-alignment.md`（审计机制对照研究）

⚠️ **重要声明**：本文档记录已接受的设计意图和当前实现事实。若本文档、实施总控和代码发生冲突，以当前代码事实与最新 control-doc reconciliation artifact 为准，并应及时回写本文档；不得长期保留“设计未来”口径冒充已实现状态。

---

## 1. 设计目标

### 1.1 北极星

**让普通基金投资者在买入前获得专业级的基金体检报告，避免追涨杀跌的行为亏损。**

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| 宿主强约束下的 LLM in the loop | 借鉴 Dayu-Agent：Host 拥有执行生命周期，Agent 只在边界内执行 |
| 好资产 + 好价格 + 长期持有 | 有知有行核心理念：分析报告回答"好不好"，检查清单回答"该不该买" |
| 证据可审计 | 每条断言必须关联到年报具体章节，计算必须可追溯 |
| 模板驱动而非自由生成 | MVP 阶段用模板填充，避免 LLM 幻觉；v2 引入 LLM 写作 |
| 分层解耦 | UI / Service / Host / Agent 四层架构，层间通过稳定契约协同 |

### 1.3 非目标

- 不做全市场横向比较（v2 在严选基金池内做）
- 不做实时行为偏差检测（改为买入前检查清单）
- 不做温度计自建（MVP 使用缓存数据）
- 不做组合管理（v2 阶段）
- 不输出买卖建议或仓位比例

---

## 2. 系统架构

### 2.1 当前实现架构

```
UI（CLI）→ Service（用例编排）→ Fund Capability（基金领域能力）
```

| 层级 | 职责 | 当前实现 |
|------|------|----------|
| **UI** | 采集输入、渲染结果、CLI 退出码 | `fund_agent/ui/cli.py` |
| **Service** | 用例编排、参数校验、调用 Capability、组合报告与 quality gate | `fund_agent/services/*.py` |
| **Capability** | 基金文档仓库、提取、分析、模板、审计、quality gate、外部数据 adapter | `fund_agent/fund/` |
| **Host/Engine** | v2 候选托管执行层；当前未接入主链路 | `dayu-agent` 依赖存在，但 `fund-analysis analyze` 不经过 `dayu.host` / `dayu.engine` |

> **当前边界（2026-05-21）**：`fund-analysis analyze` 直接通过 `FundAnalysisService` 编排 `fund_agent/fund` Capability。Dayu 仍作为 Host/Engine/Prompting/Config 的架构参考和后续接入候选；当前代码没有自建或接入通用 tool loop / Host session / Agent runtime。

### 2.2 执行链路

```
fund-analysis CLI → FundAnalysisService → FundDataExtractor → FundDocumentRepository
  → P1 extractors → P2 analysis → template renderer → programmatic audit
  → optional quality gate → CLI stdout/stderr
```

- `FundDocumentRepository` 是基金文档唯一生产入口；Service/UI 不直接读取 PDF、cache 或年报文件。
- 年报 PDF 来源顺序：EID/证监会资本市场统一信息披露平台主源，Eastmoney/akshare fallback。
- `quality_gate_policy=block` 是 `analyze` 默认策略；低质量或 not-run gate 以结构化异常阻断并由 CLI 返回退出码 2。
- 当前没有 `ExecutionContract` / `AgentInput` / scene preparation 主链路。

### 2.3 核心契约

| 契约 | 方向 | 说明 |
|------|------|------|
| `FundAnalysisRequest` | UI → Service | 显式基金代码、年报年份、R=A+B-C 输入、言行一致性输入、风险/压力测试输入、quality gate 参数 |
| `StructuredFundDataBundle` | Capability → Service | P1 结构化数据包，聚合 profile/performance/manager/holdings/nav 数据 |
| `TemplateRenderInput` | Service → Capability renderer | P1/P2 结构化结果、最终判断、当前阶段说明 |
| `TemplateRenderResult` | Capability renderer → Service | 8 章 Markdown、程序审计输入、章节块 |
| `QualityGateResult` | Capability quality gate → Service/UI | `pass / warn / block`、issue 列表、JSON/Markdown 产物路径 |

---

## 3. 定性分析模板

### 3.1 模板结构（8 章）

| 章 | 标题 | 核心问题 | 数据来源 |
|----|------|---------|---------|
| 0 | 投资要点概览 | 这是什么基金？好不好？ | 后续章节汇总 |
| 1 | 这只基金到底是什么产品 | 买的是什么？怎么赚钱？ | 招募说明书 + 年报§2 |
| 2 | R=A+B-C 收益归因 | 钱是怎么赚到的？ | 年报§3 + 净值数据 |
| 3 | 基金经理画像与言行一致性 | 基金经理靠不靠谱？ | 年报§4（说）vs §8（做） |
| 4 | 投资者获得感 | 买了的人赚到钱了吗？ | 年报§3（2026新规）+ §10 |
| 5 | 当前阶段与关键变化 | 为什么偏偏是现在？ | 跨期年报对比 |
| 6 | 核心风险与否决项 | 什么情况下直接放弃？ | 年报§2/§9 + 天天基金 |
| 7 | 是否值得持有——最终判断 | 结论是什么？ | 后续章节汇总 |

### 3.2 CHAPTER_CONTRACT 机制

每个章节都有 `CHAPTER_CONTRACT`，定义：

- `narrative_mode`：叙事模式（封面→动作→验证 / 拆解→判断→成本 / ...）
- `must_answer`：必须回答的问题列表
- `must_not_cover`：禁止覆盖的内容
- `required_output_items`：必须输出的条目
- `preferred_lens`：按基金类型动态适配的分析视角

`must_answer` 由 Capability 层 `ContractAuditCoverageManifest` 逐条声明审计覆盖路由。当前覆盖类型包括 `covered_by_required_item`、`programmatic_marker`、`structured_data_availability`、`llm_semantic_audit`、`evidence_confirm` 和 `narrative_guidance`；其中只有 `covered_by_required_item` 和 `programmatic_marker` 属于 MVP C2 的确定性可证明子集，其余类型只作为后续 LLM / evidence / quality gate 的显式路由。

### 3.3 ITEM_RULE 机制

条件型条目——某些内容只在特定条件下出现：

- `mode: optional`：有披露就写，无披露写"未披露"
- `mode: conditional`：有披露就写，无披露**必须删除整段**
- `facets_any`：条件触发（如 `facets_any: [主动权益基金]`）

### 3.4 preferred_lens 机制

按基金类型动态调整分析重点：

| 基金类型 | 优先分析视角 |
|---------|-------------|
| 指数基金 | 跟踪误差、费率、规模流动性 |
| 主动权益基金 | 超额收益稳定性、基金经理、言行一致性 |
| 债券基金 | 信用风险、久期、最大回撤 |
| 指数增强基金 | 超额收益来源、跟踪误差 |
| QDII 基金 | 海外市场/汇率风险、跟踪或管理能力、成本 |
| FOF 基金 | 底层基金配置、双重费率、组合分散度 |

---

## 4. 分析引擎

### 4.1 R=A+B-C 计算器

```
R（总收益）= 基金净值增长率
B（Beta）= 业绩基准收益率 × 股票仓位
A（Alpha）= R - B
C（Cost）= 管理费 + 托管费 + 换手率 × 0.3%
净超额 = A - C
```

**关键区分**：结构性超额（可持续的能力）vs 阶段性超额（风格顺风/运气）

| 特征 | 结构性超额 | 阶段性超额 |
|------|-----------|-----------|
| 多年度为正 | 4/5 年以上 | 集中在某 1-2 年 |
| 不同市场环境 | 牛熊都为正 | 仅在特定风格顺风时 |
| 来源可解释 | 选股/配置能力 | 无法解释 |

### 4.2 言行一致性检验

交叉验证年报§4（"说"）和年报§8（"做"）：

| 维度 | §4 宣称 | §8 实际 | 信号 |
|------|--------|--------|------|
| 投资风格 | 风格定位 | 实际持仓风格 | 🟢/🟡/🔴 |
| 行业偏好 | 看好行业 | 重仓行业 | 🟢/🟡/🔴 |
| 仓位管理 | 仓位策略 | 实际仓位 | 🟢/🟡/🔴 |
| 换手水平 | 持有周期 | 换手率 | 🟢/🟡/🔴 |

### 4.3 投资者获得感分析

```
行为损益 = 投资者实际收益 - 基金产品收益
```

- 数据来源：年报§3（2026 新规要求披露加权平均投资者收益率）
- 备用方案：份额变动 × 净值变化估算

### 4.4 否决项检查

| 风险项 | 否决条件 |
|--------|---------|
| 清盘风险 | 规模 < 5000 万 |
| 基金经理离职 | 管理本基金 < 6 个月 |
| 风格严重漂移 | 言行一致性检验 🔴 |
| 费率远超同类 | 总成本 > 同类 2 倍中位数 |
| 跟踪误差过大 | 指数基金 > 2% |

### 4.5 压力测试

模拟 -20%/-40%/-60% 三个场景（借鉴 E大网格策略理念）。

### 4.6 买入前检查清单（独立模块）

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

---

## 5. 审计机制

### 5.1 三层审计架构

```
程序审计（P/E/C/L/R 规则，无需 LLM）
  → LLM 审计（证据充分性 + 内容合规性，v2）
    → 证据复核（年报 PDF 搜索验证，v2）
```

### 5.2 审计规则体系

| 规则码 | 含义 | 阻断级别 | MVP 阶段 | 来源 |
|--------|------|----------|---------|------|
| P1 | 章节结构不匹配 | 阻断 | ✅ 实现 | 沿用 Dayu-Agent |
| P2 | 内容过短（<10字符） | 阻断 | ✅ 实现 | 沿用 Dayu-Agent |
| P3 | 缺少"证据与出处"小节或章节内最小证据行 | 阻断 | ✅ 实现 | 沿用 Dayu-Agent |
| E1 | 证据锚点不精确 | 可复核 | ⬜ v2 | 沿用 Dayu-Agent |
| E2 | 证据与断言不匹配 | 可复核 | ⬜ v2 | 沿用 Dayu-Agent |
| E3 | 证据完全缺失 | 需重建 | ⬜ v2 | 沿用 Dayu-Agent |
| C1 | 内容违规（幻觉） | 阻断 | ⬜ v2 | 沿用 Dayu-Agent |
| C2 | 章节契约越界 / 禁止话题 | 阻断（确定性子集）/ 低优先级（语义子集） | ✅ 确定性子集；语义判断 v2 | 沿用 Dayu-Agent |
| L1 | R=A+B-C 计算错误 | 阻断 | ✅ 实现 | 🆕 基金专属 |
| L2 | 百分位计算错误 | 可复核 | ⬜ v2 | 🆕 基金专属 |
| R1 | 检查清单规则错误 | 阻断 | ✅ 实现 | 🆕 基金专属 |
| R2 | 判定与评分不一致 | 阻断 | ✅ 实现 | 🆕 基金专属 |

MVP 的 C2 只覆盖确定性 `CHAPTER_CONTRACT` 子集：章节块与契约元数据一致、`required_output_items` 显式 marker 存在、`must_answer` 独立程序 marker 存在、`must_not_cover` 显式禁止 marker 不出现。`must_answer` 的非程序化 coverage 只记录审计路由，不表示 C2 已证明语义质量；语义型章节越界、幻觉判断、证据与断言匹配和修复合同仍属于 v2。

### 5.3 修复闭环机制（v2）

借鉴 Dayu-Agent 的修复策略，根据违规严重程度选择修复粒度：

| 修复策略 | 触发条件 | 说明 |
|---------|---------|------|
| **none** | 审计通过 | 无需修复 |
| **patch** | E1/E2/C2/S 类违规 | 局部修补（删除断言/修正锚点/补充证据） |
| **regenerate** | P1/P2/P3/E3/C1 类违规 | 整章重建 |

**修复合同（RepairContract）**：结构复用 Dayu-Agent，包含 `missing_evidence_slots`、`offending_claim_spans`、`remediation_actions`、`repair_strategy`、`retry_scope`。

**Patch 粒度**：substring / line / bullet / paragraph（直接复用）。

**处置模式**：delete_claim / rewrite_with_existing_evidence / anchor_fix_only（直接复用）。

**锚点重写**：对 `supported_but_anchor_too_coarse` 状态执行证据行修正，适配为基金年报锚点格式。

> 详细对照分析见 `docs/audit-alignment.md`。

### 5.4 证据锚点格式

| 数据类型 | 锚点格式 |
|---------|---------|
| 年报数据 | `年报{年份}§{章节}表{编号}行{行号}` |
| 招募说明书 | `招募说明书第{页}页` |
| 温度计 | `温度计{日期}` |
| 净值数据 | `净值{日期}来源{平台}` |
| 计算结果 | `计算:{公式}输入:{来源}` |

---

## 6. 数据源

### 6.1 主要数据源

| 数据 | 来源 | 获取方式 |
|------|------|---------|
| 基金年报 PDF | 证监会资本市场统一信息披露平台 EID；天天基金 / Eastmoney fallback | 统一文档仓库接口下载 |
| 基金净值序列 | 天天基金 / akshare | API |
| 基金基本信息 | 天天基金 | API |
| 温度计数据 | 有知有行 | 爬虫（24h 缓存） |
| 严选基金池 | 有知有行 App | 手动维护 |

#### 温度计数据源详细说明

**数据来源**：有知有行 App/网站的市场温度数据

**数据项**：
- 全市场温度（沪深A股整体估值温度）
- 指数温度（沪深300、中证500、创业板指等主要指数）
- 更新时间（用于判断数据新鲜度）

**当前获取策略**：

- `fund_agent/fund/data/thermometer.py` 提供 `FundThermometerAdapter`。
- `fund_agent/services/thermometer_service.py` 提供 read-only Service。
- `fund-analysis thermometer` 提供 plain / JSON 查询入口。
- 缓存命中、新鲜度、stale fallback 和 unavailable 状态由 Capability data adapter 管理。
- 当前不会把温度计结果自动映射为 `analyze --valuation-state`；报告仍要求显式传入估值状态。

**异常处理**：
- 爬取失败时，优先使用 stale cache；无缓存时返回 `unavailable`。
- CLI 查询温度计时，`unavailable` 正常退出并明确展示状态。
- `analyze` 检查清单第 6 题仍消费显式 `valuation_state`，不从温度计自动推断。

**风险**：有知有行页面结构变更可能导致爬取失败，需预留适配时间

### 6.2 年报章节映射

| 年报章节 | 内容 | 用于 |
|---------|------|------|
| §1/§2 | 基金简介、费率 | 第 1 章、第 2 章 |
| §3 | 净值、基准、投资者收益率 | 第 2 章、第 4 章 |
| §4 | 管理人报告（基金经理观点） | 第 3 章（"说"） |
| §8 | 投资组合报告（持仓、换手率） | 第 3 章（"做"） |
| §9 | 持有人结构、自购 | 第 3 章、第 6 章 |
| §10 | 份额变动 | 第 4 章 |

### 6.3 基金类型识别规则

基金类型决定 `preferred_lens` 的应用，识别优先级如下：

| 识别来源 | 优先级 | 规则 | 示例 |
|---------|--------|------|------|
| 招募说明书"基金类别" | 1 | 直接映射 | "股票型"→主动权益基金 |
| 基金名称关键词 | 2 | 正则匹配 | "沪深300"→宽基指数基金 |
| 业绩基准 | 3 | 基准指数判断 | 基准含"中证红利"→策略指数基金 |
| 持仓特征 | 4 | 股票仓位+集中度 | 股票仓位>80%+前十大>50%→主动基金 |

**类型判定规则（按优先级执行）**：

```
IF 招募说明书.基金类别 == "指数型":
    IF 基金名称含"增强": → 指数增强基金
    ELSE IF 基金名称含"行业"或"主题": → 行业/主题指数基金
    ELSE IF 基金名称含"红利"或"低波"或"价值"或"质量": → 策略指数基金
    ELSE: → 宽基指数基金
ELSE IF 招募说明书.基金类别 == "QDII": → QDII基金
ELSE IF 招募说明书.基金类别 == "FOF": → FOF基金
ELSE IF 招募说明书.投资范围.债券占比 > 80%: → 纯债基金
ELSE IF 招募说明书.投资范围.股票占比 < 40%: → 偏债混合基金
ELSE IF 招募说明书.投资范围.股票占比 40-60%: → 二级债基/混合债基
ELSE: # 主动权益基金，进一步细分风格
    IF 持仓.价值股占比 > 成长股占比: → 主动权益基金（价值风格）
    ELSE IF 持仓.成长股占比 > 价值股占比: → 主动权益基金（成长风格）
    ELSE: → 主动权益基金（均衡风格）
```

**风格判断指标**（基于年报§8持仓）：
- 价值股：低PE、低PB、高股息率（参考中证价值指数成分股）
- 成长股：高营收增长、高研发投入（参考中证成长指数成分股）
- 当价值股/成长股占比差 < 20% 时，判定为均衡风格

### 6.4 错误处理与降级策略

**数据获取失败时的处理策略**：

| 失败场景 | 影响章节 | 处理策略 | 报告输出 |
|---------|---------|---------|---------|
| PDF下载失败 | 全部 | 尝试缓存→提示用户手动上传 | "无法获取年报，请上传PDF或稍后重试" |
| 章节解析失败 | 特定章节 | 标记为"数据获取失败"，继续其他章节 | 该章节显示"⚠️ 数据获取失败" |
| 关键数据缺失 | 第2章(R=A+B-C) | 使用估算值并标注 | "换手率未披露，按同类中位数估算" |
| 2026新规数据未披露 | 第4章(获得感) | 使用份额变动估算 | "投资者收益率未披露，用份额变动估算" |
| 温度计爬取失败 | 检查清单 | 使用过期缓存或提示手动确认 | "⚠️ 温度数据暂时不可用" |

**关键数据缺失的估算规则**：

```python
# 伪代码：关键数据缺失时的估算策略
class DataFallback:
    def get_turnover_rate(self, fund_code):
        """换手率缺失时，按同类中位数估算"""
        try:
            return extract_from_pdf(fund_code, "§8")
        except DataNotFound:
            fund_type = classify_fund_type(fund_code)
            median = get_peer_median(fund_type, "turnover_rate")
            return {
                "value": median,
                "source": "估算",
                "note": f"年报未披露，按{fund_type}同类中位数估算"
            }
    
    def get_investor_return(self, fund_code):
        """投资者收益率缺失时（2026新规前），用份额变动估算"""
        try:
            return extract_from_pdf(fund_code, "§3")
        except DataNotFound:
            # 用份额变动 × 净值变化估算
            shares_change = get_shares_change(fund_code)
            nav_change = get_nav_change(fund_code)
            estimated = calculate_behavioral_return(shares_change, nav_change)
            return {
                "value": estimated,
                "source": "估算",
                "note": "2026新规数据未披露，用份额变动估算"
            }
```

**报告生成降级策略**：

```
IF 关键章节(第1/2/6章)数据缺失:
    → 生成"数据不完整报告"，明确标注缺失项
    → 不输出最终判断(第7章)
    → 提示用户"关键数据缺失，建议手动核实后决策"
ELSE IF 非关键章节(第3/4/5章)数据缺失:
    → 正常生成报告
    → 缺失章节标注"⚠️ 数据获取失败"
    → 最终判断基于可用数据
```

---

## 7. 当前项目结构

```
fund-agent/
├── fund_agent/
│   ├── ui/                        # UI 层
│   │   ├── cli.py
│   ├── services/                  # Service 层
│   │   ├── fund_analysis_service.py
│   │   ├── extraction_snapshot_service.py
│   │   ├── extraction_score_service.py
│   │   ├── golden_answer_service.py
│   │   ├── golden_prefill_service.py
│   │   ├── quality_gate_service.py
│   │   └── thermometer_service.py
│   ├── fund/                      # Capability 层
│   │   ├── documents/             # 统一年报仓库、来源编排、cache、metadata
│   │   │   ├── repository.py
│   │   │   ├── sources.py
│   │   │   ├── cache.py
│   │   │   ├── models.py
│   │   │   └── adapters/
│   │   ├── extractors/            # P1 结构化抽取
│   │   │   ├── profile.py
│   │   │   ├── performance.py
│   │   │   ├── manager_ownership.py
│   │   │   └── holdings_share_change.py
│   │   ├── analysis/              # 分析引擎
│   │   │   ├── r_abc.py           # R=A+B-C 收益归因
│   │   │   ├── alpha_judge.py     # 超额收益性质判断
│   │   │   ├── consistency_check.py  # 言行一致性检验
│   │   │   ├── investor_return.py # 投资者获得感分析
│   │   │   ├── risk_check.py      # 否决项检查 + 压力测试
│   │   │   └── checklist.py       # 7问题检查清单
│   │   ├── audit/                 # 程序审计
│   │   │   ├── audit_programmatic.py  # 程序化审计
│   │   │   └── contract_rules.py
│   │   ├── template/              # CHAPTER_CONTRACT / ITEM_RULE / renderer
│   │   │   ├── contracts.py
│   │   │   ├── item_rules.py
│   │   │   ├── chapter_blocks.py
│   │   │   └── renderer.py
│   │   ├── pdf/                   # documents 内部 PDF helper
│   │   │   ├── downloader.py
│   │   │   ├── parser.py
│   │   │   └── section_catalog.py
│   │   └── data/                  # 外部数据获取
│   │       ├── nav_data.py        # 净值数据（天天基金/akshare）
│   │       └── thermometer.py     # 温度计（有知有行）
│   └── config/                    # 配置包和 prompts 目录
├── tests/
├── cache/
├── docs/
│   ├── design.md                  # 本文档（设计真源）
│   └── implementation-control.md  # 实施总控
├── pyproject.toml                 # 依赖 dayu-agent
└── README.md
```

### 7.1 Dayu-Agent 模块状态

| Dayu-Agent 模块 | 当前状态 | 说明 |
|---|---|---|
| `dayu.engine` | 后续候选 | 当前 CLI/Service 主链路未接入 tool loop、runner、trace 或 ToolRegistry |
| `dayu.host` | 后续候选 | 当前未接入 Host session/run 生命周期 |
| `dayu.contracts` | 后续候选 | 当前未使用 ExecutionContract / AppEvent 作为主链路契约 |
| `dayu.prompting` | 后续候选 | 当前模板契约在 `fund_agent/fund/template` typed manifest 中维护 |
| `dayu.config` | 依赖候选 | 当前配置包存在，但主链路不依赖 dayu config 装配 |
| 审计机制 | 架构借鉴 | 当前已实现 deterministic programmatic audit；LLM audit / Evidence Confirm 后续再接 |

---

## 8. 设计决策记录

| 决策 | 选择 | 备选方案 | 理由 |
|------|------|---------|------|
| 架构模式 | 四层架构，Engine/Host 直接依赖 dayu-agent | 全部自建 | 复用 dayu-agent 的 Engine/Host/Prompting/Config，减少 60-70% 基础设施工作量 |
| 输出格式 | 8 章定性模板 | 一页纸报告 | 信息更完整，覆盖全链路 |
| 超额收益判断 | 区分结构性 vs 阶段性 | 仅计算 A=R-B | 第一性原理：可持续能力 vs 运气 |
| 检查清单位置 | 独立模块 | 嵌入报告 | 检查清单是行为干预工具，不是分析工具 |
| PDF 解析 | pdfplumber | PyPDF2 | 表格提取能力更强 |
| 数据缓存 | SQLite + 文件缓存 | 仅文件缓存 | 支持结构化查询和增量更新 |
| 审计策略 | MVP 仅程序审计 | 三层全实现 | 降低复杂度，v2 引入 LLM 审计 |
| 温度计 | 爬虫 + 24h 缓存 | 自建计算 | 数据源依赖有知有行，自建留到 v3 |
| 工具注册 | dayu toolset registrar 模式 | 自建工具框架 | 与 dayu.engine 无缝集成，获得 trace/截断/续读能力 |
| Prompt 资产 | dayu scene/task/base 三层结构 | 自建模板系统 | 复用条件渲染、context slot、CHAPTER_CONTRACT 解析机制 |
