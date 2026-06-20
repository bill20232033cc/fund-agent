# 基金分析 Agent 项目 CodeWiki

> 本文档基于 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md` 和仓库代码综合分析生成。
> 版本: v1.0 | 日期: 2026-06-20

---

## 一、项目概述

### 1.1 北极星目标

**让普通基金投资者在买入前获得专业级的基金体检报告，避免追涨杀跌的行为亏损。**

### 1.2 核心方法论

本项目基于**有知有行投资方法论 R = A + B - C**：

```
R（投资者收益）= Alpha（超额收益）+ Beta（市场收益）- Cost（费用损耗）
```

分析框架：**产品本质 → 收益归因 → 基金经理画像 → 投资者获得感 → 当前阶段 → 核心风险 → 最终判断**

---

## 二、架构设计

### 2.1 四层目标架构

```
UI → Service → Host → Agent
```

| 层级 | 职责 | 代码位置 | 边界约束 |
|------|------|---------|---------|
| **UI** | 用户交互界面、报告渲染 | `fund_agent/ui/cli.py` | 只依赖 Service 接口，不直接调用 Host/Agent |
| **Service** | 业务用例编排、场景定义、prompt 组装 | `fund_agent/services/` | 调用 Host 执行 Agent；当前可直调 fund 公开能力 |
| **Host** | session/run 生命周期、并发、超时、取消 | `fund_agent/host/` | 实现必须内化 Dayu Host 能力，不直接依赖 dayu.host |
| **Agent** | tool loop、基金领域能力、审计规则 | `fund_agent/fund/` + `fund_agent/agent/` | 实现必须内化 Dayu Engine 能力 |

### 2.2 关键设计决策

#### ✅ 已实现
- **确定性 MVP 主链路**：`fund-analysis analyze` / `checklist` 不依赖 LLM，由结构化抽取、确定性分析、模板渲染、程序审计组成
- **显式 opt-in LLM 路径**：`--use-llm` 是用户显式选择的 Route C 路径
- **FundProcessorRegistry**：S2 已实现，active fund annual `ParsedAnnualReport` 默认 facade 投影 `StructuredFundDataBundle`
- **FundDisclosureDocument facade route**：S5 已实现显式 opt-in 路径
- **Source-truth direct extraction**：`product_essence.v1` 与 `return_attribution.v1` 已实现 proof-positive FDD source-truth extraction
- **Multi-year annual analysis**：已实现 deterministic `analyze-annual-period` 产品路径

#### ⚠️ 待实现
- **Full production Agent tool-loop/runtime expansion**
- **Host durable session/resume/memory/outbox**
- **LLM 分章写作 / write-audit-repair 闭环**
- **Evidence Confirm（证据复核层）**

### 2.3 目录结构

```
fund_agent/
├── ui/                    # UI 层（Typer CLI）
│   └── cli.py            # 命令行入口
├── services/              # Service 层（业务用例编排）
│   ├── fund_analysis_service.py      # 主分析服务
│   ├── quality_gate_service.py       # 质量门控服务
│   ├── thermometer_service.py        # 温度计服务
│   ├── chapter_orchestrator.py       # 章节编排器
│   └── ...
├── host/                  # Host 层（生命周期治理）
│   └── runtime.py         # 进程内 Host runtime runner
├── agent/                 # Agent 层（执行内核）
│   ├── runner.py          # Agent body runner
│   ├── tools.py           # 工具定义
│   └── contracts.py       # Agent 契约
└── fund/                  # Fund 层（基金领域能力）
    ├── analysis/          # 分析引擎（R=A+B-C、超额收益、言行一致性等）
    ├── audit/             # 审计机制（程序审计、契约规则）
    ├── data/              # 数据层（净值、温度计、NAV）
    ├── documents/         # 文档层（年报解析、来源编排）
    ├── extractors/        # 字段提取器
    ├── processors/        # Processor/Extractor 架构
    ├── template/          # 模板系统（CHAPTER_CONTRACT、preferred_lens）
    └── quality_gate.py    # 质量门控
```

---

## 三、业务流程

### 3.1 主分析流程（确定性路径）

```
CLI（Typer app）
  → FundAnalysisService.analyze(request)
    → FundDataExtractor.extract(fund_code, year)  # P1 结构化抽取
      → FundDocumentRepository.load_annual_report()  # 文档仓库入口
        → documents layer source orchestration
      → extract_profile / extract_performance / ...  # 章节 extractor
      → FundNavDataAdapter.load_nav_data()  # 净值数据
    → judge_alpha_nature / calculate_r_abc / ...  # P2 分析计算
    → run_quality_gate_for_bundle(bundle)  # 质量门控
    → render_template_report(render_input)  # 模板渲染
    → run_programmatic_audit(audit_input)  # 程序审计
  → stdout 输出报告 Markdown
```

### 3.2 八章分析模板结构

| 章 | 标题 | 核心问题 | 数据来源 |
|----|------|---------|---------|
| 0 | 投资要点概览 | 这是什么基金？好不好？ | 后续章节汇总 |
| 1 | 这只基金到底是什么产品 | 买的是什么？怎么赚钱？ | 年报§1/§2 |
| 2 | R=A+B-C 收益归因 | 钱是怎么赚到的？ | 年报§3 + 净值数据 |
| 3 | 基金经理画像与言行一致性 | 基金经理靠不靠谱？ | 年报§4 vs §8 |
| 4 | 投资者获得感 | 买了的人赚到钱了吗？ | 年报§3 + §10 |
| 5 | 当前阶段与关键变化 | 为什么偏偏是现在？ | 跨期年报对比 |
| 6 | 核心风险与否决项 | 什么情况下直接放弃？ | 年报§2/§9 |
| 7 | 是否值得持有——最终判断 | 结论是什么？ | 后续章节汇总 |

### 3.3 CHAPTER_CONTRACT 机制

每个章节通过 `ChapterContract` 定义：
- `must_answer`：必须回答的问题列表
- `must_not_cover`：禁止覆盖的内容
- `required_output_items`：必须输出的条目
- `preferred_lens`：按基金类型的分析视角

**真源位置**：`docs/fund-analysis-template-draft.md` 的 `TEMPLATE_CONTRACT_MANIFEST_JSON` 是唯一 authored truth source。

### 3.4 三层审计架构

```
程序审计（P1/P2/P3/C2/L1/R1/R2）✅ 已实现
  → LLM 审计（E1/E2/E3/C1/L2）⬜ v2
    → 证据复核（年报 PDF 搜索验证）⬜ v2
```

| 规则码 | 含义 | MVP 实现 |
|--------|------|---------|
| P1 | 章节结构不匹配 | ✅ |
| P2 | 内容过短（<10字符） | ✅ |
| P3 | 缺少证据小节 | ✅ |
| C2 | 章节越界（展开禁止话题） | ✅ |
| L1 | R=A+B-C 计算错误 | ✅ |
| R1 | 检查清单规则错误 | ✅ |
| R2 | 判定与评分不一致 | ✅ |

---

## 四、技术选型分析

### 4.1 核心技术栈

| 类别 | 选型 | 理由 |
|------|------|------|
| 语言 | Python >= 3.11 | 现代类型注解支持，项目统一要求 |
| CLI | Typer | 简洁的 CLI 框架 |
| 数据验证 | Pydantic / dataclass | 类型安全 |
| 并发 | asyncio | 异步 I/O 支持 |
| PDF 解析 | CSRC EID + Docling (候选) | 官方来源为主，Docling 为候选 evidence harness |

### 4.2 文档来源策略

| 来源 | 角色 | 优先级 |
|------|------|--------|
| CSRC EID（证监会电子化信息披露平台） | 主来源 | 1 |
| 天天基金 | fallback（仅 not_found/unavailable） | 2 |
| 基金公司官网 | fallback（仅 not_found/unavailable） | 3 |
| Docling | 候选 evidence harness / research input | deferred |

### 4.3 年报来源 fallback 策略

| 失败类别 | 含义 | 是否允许 fallback |
|---------|------|------------------|
| `not_found` | 正常响应但没有目标年报 | ✅ |
| `unavailable` | 网络/超时/临时不可用 | ✅ |
| `schema_drift` | 响应结构偏离契约 | ❌ fail-closed |
| `identity_mismatch` | 返回候选与基金信息矛盾 | ❌ fail-closed |
| `integrity_error` | PDF 完整性失败 | ❌ fail-closed |

---

## 五、基本功能模块

### 5.1 文档层（fund_agent/fund/documents/）

| 模块 | 职责 | 关键类 |
|------|------|--------|
| `repository.py` | 统一文档仓库入口 | `FundDocumentRepository` |
| `sources.py` | 来源编排与 fallback | `SourceOrchestrator` |
| `cache.py` | 文档缓存管理 | `DocumentCache` |
| `candidates/` | FundDisclosureDocument 结构 | `FundDisclosureDocument` |

### 5.2 提取层（fund_agent/fund/extractors/）

| 提取器 | 提取字段 |
|--------|---------|
| `profile.py` | 基金概况、类型、管理规模 |
| `performance.py` | 业绩表现、净值增长 |
| `manager_ownership.py` | 基金经理持有本基金 |
| `holdings_share_change.py` | 份额变动、持有人结构 |

### 5.3 分析层（fund_agent/fund/analysis/）

| 模块 | 功能 |
|------|------|
| `r_abc.py` | R=A+B-C 收益归因计算 |
| `alpha_judge.py` | 超额收益性质判断（结构性 vs 阶段性） |
| `consistency_check.py` | 言行一致性检验 |
| `investor_return.py` | 投资者获得感分析 |
| `risk_check.py` | 否决项检查、压力测试 |
| `checklist.py` | 7 问题买入前检查清单 |
| `final_judgment.py` | 最终判断派生 |

### 5.4 模板层（fund_agent/fund/template/）

| 模块 | 职责 |
|------|------|
| `contracts.py` | CHAPTER_CONTRACT 解析与验证 |
| `typed_contracts.py` | 类型化契约投影 |
| `renderer.py` | 8 章模板渲染 |
| `lens_application.py` | preferred_lens 确定性应用 |
| `item_rules.py` | ITEM_RULE 条件型条目规则 |

### 5.5 审计层（fund_agent/fund/audit/）

| 模块 | 职责 |
|------|------|
| `audit_programmatic.py` | 程序审计执行器 |
| `contract_rules.py` | CHAPTER_CONTRACT C2 审计规则 |

### 5.6 质量门控（fund_agent/fund/quality_gate.py）

FQ0-FQ6 规则体系，对应 FDD 字段级 coverage / traceability / correctness 评估。

---

## 六、使用场景与命令

### 6.1 CLI 命令

```bash
# 主分析命令（确定性路径）
fund-analysis analyze <基金代码> [--year <年份>]

# 买入前检查清单
fund-analysis checklist <基金代码> [--year <年份>]

# 多年年报分析
fund-analysis analyze-annual-period <基金代码> --target-year <年份> [--max-years 5]

# LLM 增强分析（opt-in）
fund-analysis analyze <基金代码> --use-llm

# 字段级质量评估
fund-analysis score <基金代码> [--year <年份>]

# 温度计查询
fund-analysis thermometer <基金代码>

# 精选基金池处理
fund-analysis batch <CSV路径> [--workers <并发数>]
```

### 6.2 Python API

```python
from fund_agent.services import FundAnalysisService
from fund_agent.fund import FundDataExtractor

# 直接抽取
extractor = FundDataExtractor()
bundle = await extractor.extract("004393", 2024)

# Service 用例编排
service = FundAnalysisService()
result = await service.analyze("004393", year=2024)
print(result.report_markdown)
```

---

## 七、真源文档一致性分析

### 7.1 ✅ 一致部分

| 设计决策 | 文档描述 | 代码实现 | 状态 |
|---------|---------|---------|------|
| 四层架构边界 | `UI → Service → Host → Agent` | `fund_agent/ui/`, `services/`, `host/`, `fund/` | ✅ 一致 |
| 默认主链路 | 确定性 analyze/checklist | `FundAnalysisService.analyze()` | ✅ 一致 |
| 文档仓库入口 | `FundDocumentRepository` | `fund_agent/fund/documents/repository.py` | ✅ 一致 |
| CHAPTER_CONTRACT | `docs/fund-analysis-template-draft.md` JSON | `fund_agent/fund/template/contracts.py` | ✅ 一致 |
| 审计规则 | P1/P2/P3/C2/L1/R1/R2 | `fund_agent/fund/audit/audit_programmatic.py` | ✅ 一致 |
| R=A+B-C | 公式定义与计算 | `fund_agent/fund/analysis/r_abc.py` | ✅ 一致 |
| Multi-year | `analyze-annual-period` | `AnnualEvidenceLoader`, `AnnualPeriodRenderer` | ✅ 一致 |
| Source-truth | product_essence / return_attribution | `FundDisclosureDocument` facade | ✅ 一致 |

### 7.2 ⚠️ 存在差异部分

| 设计文档描述 | 实际情况 | 建议 |
|------------|---------|------|
| `docs/design.md` v2.29 提到 `fund_agent/host/README.md` | 当前 `fund_agent/host/` 存在但 README 较简 | 补充完善 Host 包文档 |
| `fund_agent/fund/README.md` 应描述 Fund 作为 Agent 层能力包定位 | 当前 README 内容较基础 | 同步 `docs/design.md` 最新设计 |
| 模板章节 5 "跨期年报对比" 应支持多年 | 当前 `annual_period_renderer.py` 已实现 | 文档待同步 |

### 7.3 📋 一致性建议

1. **补充 `fund_agent/host/README.md`**：描述 Host 层架构、进程内 runner、生命周期治理
2. **更新 `fund_agent/fund/README.md`**：同步 S5/S6 实现状态、FundDisclosureDocument facade
3. **同步 `docs/design.md` 最新 v2.29 状态**：当前 design.md 版本标注为 v2.29，需验证代码对应

---

## 八、开发路线与后续规划

### 8.1 当前已完成（截至 2026-06-20）

| Gate | 状态 | 说明 |
|------|------|------|
| S1 Processor/Extractor 架构 | ✅ 已合并 | `FundProcessorRegistry` |
| S2 DataExtractor Integration | ✅ 已合并 | active fund 默认 facade |
| S5 FundDisclosureDocument facade | ✅ 已合并 | opt-in 路径 |
| S6-A ~ S6-G Candidate Evidence | ✅ 已实现 | 6 个字段族 locator selector |
| Source-truth Slice A/B/C | ✅ 已实现 | product_essence / return_attribution |
| Multi-year annual analysis | ✅ 已实现 | `analyze-annual-period` |
| --use-llm Route C | ✅ 最小实现 | Host + Agent body runner |

### 8.2 进行中（Active Gate）

| Gate | 说明 |
|------|------|
| `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction` | PR #30 review 刚通过，等待 follow-up push |

### 8.3 待处理（Deferred Gates）

| 类别 | Gate | 说明 |
|------|------|------|
| **Stabilization** | Chapter 2/3/5/6 further stabilization | LLM writer 章节级修复 |
| **Runtime** | Full Agent tool-loop/runtime expansion | 完整 tool loop / retry / budget |
| **Runtime** | Host durable session/resume/memory/outbox | 持久化会话 |
| **Quality** | Chapter repair budget calibration | 修复预算校准 |
| **Quality** | Evidence Confirm | 证据复核层 |
| **Route** | Multi-period disclosure LLM route | 半年报/季报 LLM 分析 |
| **Source** | Fallback/source expansion design | Eastmoney/CNINFO 扩展 |
| **Release** | Release-readiness gate | 发布就绪评估 |

### 8.4 Phaseflow Queue（长跑道）

```
1. CSRC EID XBRL HTML Render 评估
2. FundDisclosureDocument Candidate Source Design
3. Fund Processor/Extractor S1-S6 实现
4. Source-truth Field Extraction（当前进度）
5. LLM 分章写作 / write-audit-repair 闭环
6. Host durable session / memory
7. Full production Agent tool-loop
8. Evidence Confirm 层
```

---

## 九、关键文件索引

| 文件 | 用途 |
|------|------|
| [AGENTS.md](file:///workspace/AGENTS.md) | 最高优先级执行规则 |
| [docs/design.md](file:///workspace/docs/design.md) | 设计真源（v2.29） |
| [docs/implementation-control.md](file:///workspace/docs/implementation-control.md) | 实施总控 |
| [docs/fund-analysis-template-draft.md](file:///workspace/docs/fund-analysis-template-draft.md) | 分析模板 |
| [fund_agent/services/fund_analysis_service.py](file:///workspace/fund_agent/services/fund_analysis_service.py) | 主分析 Service |
| [fund_agent/fund/documents/repository.py](file:///workspace/fund_agent/fund/documents/repository.py) | 文档仓库 |
| [fund_agent/fund/analysis/r_abc.py](file:///workspace/fund_agent/fund/analysis/r_abc.py) | R=A+B-C 计算器 |
| [fund_agent/fund/audit/audit_programmatic.py](file:///workspace/fund_agent/fund/audit/audit_programmatic.py) | 程序审计 |
| [fund_agent/fund/template/contracts.py](file:///workspace/fund_agent/fund/template/contracts.py) | CHAPTER_CONTRACT |
| [fund_agent/fund/analysis/checklist.py](file:///workspace/fund_agent/fund/analysis/checklist.py) | 检查清单 |
| [fund_agent/fund/analysis/final_judgment.py](file:///workspace/fund_agent/fund/analysis/final_judgment.py) | 最终判断 |

---

## 十、附录

### 10.1 设计原则速查

| 原则 | 描述 |
|------|------|
| 第一性原理 | 从原始需求出发，动机和目标不清晰时停下来讨论 |
| 证据可溯源 | 所有数值判断必须标注年报章节，禁止"根据经验" |
| 禁止买卖建议 | 只输出"值得持有/需要关注/建议替换" |
| 基金类型优先 | 先识别 index/active/bond/QDII/FOF，再应用 preferred_lens |
| 显式参数 | 所有参数必须在 typed request/contract/config 中声明 |

### 10.2 非目标（不可做）

- ❌ 直接输出"买入""卖出"建议
- ❌ 预测未来收益或市场走势
- ❌ 超出公开披露信息的因果推断
- ❌ 基金经理动机猜测
- ❌ 直接依赖 `dayu-agent` 作为生产 runtime
- ❌ 把 Docling 作为生产 parser 替代（当前是 candidate evidence harness）

---

*本 CodeWiki 由代码分析和真源文档综合生成，反映截至 2026-06-20 的项目状态。*
