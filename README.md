# 基金分析 Agent

基于有知有行投资方法论（R = A + B - C）的智能基金分析系统。通过结构化模板从基金年报、招募说明书中提取关键信息，生成"值得持有 / 需要关注 / 建议替换"的判断框架。

## 核心理念

```
投资者收益 = Alpha（超额收益）+ Beta（市场收益）- Cost（成本）
```

- **好资产**：理解产品本质，买的是什么
- **好价格**：成本合理，超额收益可覆盖
- **长期持有**：基金经理靠谱，言行一致

## 快速开始

```bash
# 安装
pip install -e .

# 查看 CLI 帮助
fund-analysis --help

# 输出完整 8 章 Markdown 报告
fund-analysis analyze 110011 --report-year 2024
```

当前代码状态：

- CLI 使用 Typer，`fund-analysis --help` 可用，项目脚本入口为 `fund_agent.ui.cli:app`。
- `fund-analysis analyze FUND_CODE` 会通过 Service 层编排结构化抽取、P2 分析、模板渲染和程序审计，并把完整 Markdown 报告输出到 stdout。
- `fund-analysis checklist FUND_CODE` 独立命令尚未接入 Service，会以非零状态提示使用 `analyze`。

常用显式参数：

```bash
fund-analysis analyze 110011 \
  --report-year 2024 \
  --equity-position 80% \
  --actual-style 均衡 \
  --actual-equity-position 70% \
  --manager-tenure-months 24 \
  --peer-fee-median 1.00% \
  --investment-amount 10000 \
  --max-tolerable-loss-rate 50% \
  --valuation-state low \
  --user-money-horizon-years 4 \
  --final-judgment worth_holding
```

## 当前能力边界

- 已实现：
  - 样本基金基线记录：见 `docs/sample-funds.md`
  - 文档仓库入口：`FundDocumentRepository.load_annual_report(...)`
  - P1 结构化抽取 façade：`FundDataExtractor.extract(...)`
  - P2 分析能力：R=A+B-C、超额性质、言行一致性、投资者获得感、风险检查、压力测试、7 问题检查清单
  - 8 章 Markdown 模板渲染与程序审计
  - CLI 分析入口：`fund-analysis analyze`
- 尚未实现：
  - 温度计数据接入
  - 3 只样本基金端到端 CLI 矩阵
  - 独立 `fund-analysis checklist` Service 命令

## 分析框架

基金分析报告包含 8 个章节：

| 章节 | 核心问题 | 关键机制 |
|------|---------|---------|
| 第 0 章：投资要点概览 | 这是什么基金，好不好？ | 封面页，三段结构 |
| 第 1 章：产品本质 | 这只基金到底是什么？ | preferred_lens 按类型聚焦 |
| 第 2 章：R=A+B-C | 钱是怎么赚到的？ | 结构性 vs 阶段性超额 |
| 第 3 章：基金经理画像 | 基金经理靠不靠谱？ | 言行一致性交叉验证 |
| 第 4 章：投资者获得感 | 投资者真的赚到钱了吗？ | 行为损益估算 |
| 第 5 章：当前阶段 | 为什么偏偏是现在？ | 结构性 vs 阶段性变化 |
| 第 6 章：核心风险与否决项 | 什么情况下该放弃？ | 压力测试（E大策略） |
| 第 7 章：最终判断 | 是否值得持有？ | 三选一 + 阈值事件 |

## 项目结构（当前代码）

```
fund-agent/
├── fund_agent/                    # 核心代码包
│   ├── ui/                        # CLI 入口
│   │   └── cli.py
│   ├── services/                  # Service 层编排
│   ├── fund/                      # Capability 层（基金领域知识）
│   │   ├── documents/             # 年报仓库入口
│   │   ├── extractors/            # P1 章节抽取
│   │   ├── analysis/              # P2 分析能力
│   │   ├── audit/                 # 程序审计
│   │   ├── data/                  # 净值数据适配
│   │   └── template/              # 8 章模板渲染
│   └── config/                    # 配置
├── tests/                         # 测试
├── docs/                          # 设计文档
│   ├── design.md
│   └── implementation-control.md
├── pyproject.toml                 # 项目配置
└── README.md                      # 本文档
```

## 文档导航

| 文档 | 用途 | 读者 |
|------|------|------|
| [docs/design.md](docs/design.md) | 设计真源 | 开发者 |
| [docs/implementation-control.md](docs/implementation-control.md) | 实施进度 | 开发者 |
| [docs/audit-alignment.md](docs/audit-alignment.md) | 审计机制对照研究 | 开发者 |
| [docs/fund-analysis-template-draft.md](docs/fund-analysis-template-draft.md) | 基金分析模板 | AI Agent / 开发者 |
| [docs/fund-agent-mvp-plan.md](docs/fund-agent-mvp-plan.md) | MVP 计划 | 开发者 |
| [docs/sample-funds.md](docs/sample-funds.md) | 样本基金基线 | 开发者 |

## 支持的基金类型

| 类型 | preferred_lens 优先级 | 压力测试阈值 |
|------|----------------------|-------------|
| 宽基/行业/策略指数基金 | 跟踪误差 > 费率 > 规模 | -30% / -50% / -70% |
| 主动权益基金 | 基金经理 > 超额稳定性 > 言行一致 | -25% / -45% / -65% |
| 纯债/混合债基 | 信用风险 > 久期稳定性 > 回撤 | -5% / -10% / -20% |
| 指数增强基金 | 超额稳定性 > 跟踪误差 > 费率 | -25% / -45% / -60% |
| QDII 基金 | 费率 > 跟踪误差 > 汇率风险 | -35% / -55% / -75% |
| FOF 基金 | 配置策略 > 总费率 > 底层质量 | -20% / -40% / -55% |
