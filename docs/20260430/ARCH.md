# zhixing agent — 架构设计文档 (ARCH)

## 一、技术栈

| 层面 | 选型 | 理由 |
|------|------|------|
| 语言 | Python 3.11+ | 金融数据生态（AKShare/pandas）、dayu-agent 可借鉴、Docling 可用 |
| LLM | DeepSeek API (OpenAI-compatible SDK) | 中文能力强、性价比高、已有集成经验 |
| 财务数据 | AKShare（A 股）+ yfinance（美股） | 免费开源、无需 token、社区活跃 |
| 数据处理 | pandas, numpy | 财务计算标准工具 |
| 笔记解析 | python-frontmatter, markdown-it-py | 解析 YAML frontmatter + Markdown 正文 |
| 数据库 | SQLite（开发）→ PostgreSQL（部署） | 轻量起步，可扩展 |
| CLI | typer | 类型安全的命令行框架 |
| Web API | FastAPI | 异步、类型安全、自动文档生成 |
| 渲染 | pandoc → HTML/PDF | 报告输出多格式 |

### 为什么选 Python 而不是 JavaScript

| 因素 | Python | JavaScript |
|------|--------|-----------|
| AKShare / Tushare | 原生支持 | 无 |
| Docling（PDF 解析） | 原生支持 | 无 |
| edgartools（SEC 财报） | 原生支持 | 无 |
| pandas / numpy（财务计算） | 原生生态 | DanfoJS（弱很多） |
| DCF / 估值计算 | scipy, numpy | 需手写 |
| dayu-agent 代码可直接借鉴 | 是 | 否 |

5 个"原生支持"对比 JS 的可迁移经验，Python 是正确选择。

---

## 二、架构概览

借鉴 dayu-agent 的 4 层架构，精简为 3 层：

```
┌─────────────────────────────────────────────────┐
│                  UI Layer                        │
│          CLI (typer) / Web API (FastAPI)         │
├─────────────────────────────────────────────────┤
│               Service Layer                      │
│    Scene Engine · Analysis Orchestrator          │
│    Note Insight Extractor · Report Generator     │
├─────────────────────────────────────────────────┤
│               Engine Layer                       │
│    AsyncAgent · ToolRegistry · PromptBuilder     │
│    ContextBudget · DataCache                     │
├─────────────────────────────────────────────────┤
│                  Tools                           │
│  note_reader · financial_data · screener         │
│  valuation · report_writer                       │
└─────────────────────────────────────────────────┘
```

---

## 三、目录结构

```
zhixing-agent/
├── zhixing/
│   ├── __init__.py
│   ├── cli.py                  — CLI 入口 (typer)
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── agent.py            — AsyncAgent 主循环
│   │   ├── tool_registry.py    — 工具注册与分发
│   │   ├── prompt_builder.py   — Prompt 组装（Scene → System + User prompt）
│   │   └── context_budget.py   — 上下文预算治理
│   ├── scenes/
│   │   ├── __init__.py
│   │   ├── base.py             — Scene 基类
│   │   ├── screening.py        — Phase 0: 标的筛选
│   │   ├── qualitative.py      — Phase 1: 定性分析
│   │   ├── quantitative.py     — Phase 2: 定量分析
│   │   ├── valuation.py        — Phase 3: 估值定价
│   │   ├── decision.py         — Phase 4: 投资决策
│   │   └── tracking.py         — Phase 5: 持仓追踪
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── note_reader.py      — 读取 Obsidian/flomo/NoNotes 笔记
│   │   ├── insight_extractor.py— 从笔记中提取投资洞见
│   │   ├── financial_data.py   — AKShare/yfinance 财务数据获取
│   │   ├── screener.py         — 量化筛选器
│   │   ├── valuation.py        — DCF + 相对估值计算
│   │   └── report_writer.py    — 报告生成
│   ├── data/
│   │   ├── cache.py            — SQLite 数据缓存层
│   │   └── schema.py           — 数据模型定义
│   └── render/
│       └── renderer.py         — Markdown → HTML/PDF 渲染
├── templates/
│   ├── qualitative.md          — 定性分析模板
│   ├── quantitative.md         — 定量分析模板
│   ├── valuation.md            — 估值模板
│   ├── buy_plan.md             — 买入计划模板
│   └── tracking.md             — 持仓追踪模板
├── workspace/                   — 用户工作区（分析产出）
│   ├── watchlist/
│   ├── analysis/
│   └── portfolio/
├── tests/
├── docs/
│   ├── PRD.md
│   ├── ARCH.md
│   ├── RESEARCH.md             — 研究文档
│   └── DEV_PLAN.md             — 开发计划
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

---

## 四、核心模块设计

### 4.1 AsyncAgent 引擎

借鉴 dayu-agent 的引擎设计，精简实现：

```python
# zhixing/engine/agent.py — 核心循环（伪代码）
class AsyncAgent:
    """精简版 Agent 主循环"""

    async def run(self, scene: Scene, user_input: str) -> AgentResult:
        messages = self.prompt_builder.build(scene, user_input)

        for iteration in range(scene.max_iterations):
            response = await self.llm_runner.call(messages)

            if response.has_tool_calls:
                results = await self.tool_registry.execute_batch(response.tool_calls)
                messages.append(response.to_message())
                messages.extend(results.to_messages())

                if self.context_budget.should_compress(messages):
                    messages = self.context_budget.compress(messages)
            else:
                # 最终回答
                return AgentResult(answer=response.content, iterations=iteration)

        return AgentResult(answer="达到最大迭代次数", iterations=scene.max_iterations)
```

**与 dayu-agent 的差异**：
- dayu-agent 的引擎处理财报解析（上万行代码），zhixing 只需处理结构化财务数据
- 不需要 PDF/HTML 解析管线，数据直接从 AKShare/yfinance 获取
- 引擎核心预计 200-400 行代码

### 4.2 Scene 机制

每个分析场景（Scene）定义：

```python
@dataclass
class Scene:
    name: str                    # 场景名称
    description: str             # 场景描述
    system_prompt_template: str  # System prompt 模板路径
    allowed_tools: list[str]     # 允许使用的工具白名单
    max_iterations: int          # 最大迭代次数
    required_outputs: list[str]  # 必须产出的内容
    next_scene: str | None       # 完成后跳转的下一个场景
```

场景编排：

```python
SCENE_FLOW = {
    "screening":    Scene(name="screening",    allowed_tools=["screener", "financial_data"],  max_iterations=5,  next_scene="qualitative"),
    "qualitative":  Scene(name="qualitative",  allowed_tools=["note_reader", "insight_extractor", "financial_data"], max_iterations=15, next_scene="quantitative"),
    "quantitative": Scene(name="quantitative", allowed_tools=["financial_data", "screener"],   max_iterations=10, next_scene="valuation"),
    "valuation":    Scene(name="valuation",    allowed_tools=["valuation", "financial_data"],  max_iterations=8,  next_scene="decision"),
    "decision":     Scene(name="decision",     allowed_tools=["financial_data", "note_reader"],max_iterations=5,  next_scene=None),
    "tracking":     Scene(name="tracking",     allowed_tools=["financial_data", "note_reader"],max_iterations=8,  next_scene=None),
}
```

### 4.3 上下文预算治理

借鉴 dayu-agent 和 Claude Code 的实践：

```python
class ContextBudget:
    max_tokens: int = 80000      # 保守上限（DeepSeek V4 支持 128K，留余量）
    compress_threshold: float = 0.7  # 70% 时触发压缩

    def should_compress(self, messages: list) -> bool:
        return self.estimate_tokens(messages) > self.max_tokens * self.compress_threshold

    def compress(self, messages: list) -> list:
        # 保留策略：
        # 1. System prompt（永远保留）
        # 2. 最近 3 轮完整保留
        # 3. 更早的工具输出替换为摘要
        # 4. Pinned state（关键数据点）永远保留
        ...
```

### 4.4 笔记洞见提取

zhixing agent 的独有创新点：

```python
class InsightExtractor:
    """从用户笔记中提取投资相关洞见"""

    async def extract(self, notes: list[Note], ticker: str) -> list[Insight]:
        # 1. 按相关性筛选（提到标的、行业、竞争对手的笔记）
        relevant = self._filter_relevant(notes, ticker)

        # 2. 调用 LLM 提取结构化洞见
        insights = await self._llm_extract(relevant, ticker)

        # 3. 分类到分析维度
        #    - 商业模式洞见
        #    - 护城河洞见
        #    - 管理层洞见
        #    - 行业洞见
        #    - 情感倾向（看多/看空/中性）

        # 4. 每个洞见标注来源笔记（可追溯）
        return insights

@dataclass
class Insight:
    content: str          # 洞见内容
    category: str         # 所属分析维度
    sentiment: str        # bullish / bearish / neutral
    source_note: str      # 来源笔记路径
    source_excerpt: str   # 原文摘录
    timestamp: datetime   # 笔记时间
```

---

## 五、数据模型

### 5.1 财务数据（标准化 Schema）

```python
@dataclass
class FinancialData:
    ticker: str
    market: str              # "A" / "US" / "HK"
    year: int
    quarter: int | None      # None = 年报

    # 利润表
    revenue: float
    gross_profit: float
    operating_income: float
    net_income: float
    eps: float

    # 资产负债表
    total_assets: float
    total_debt: float
    shareholders_equity: float
    cash: float
    goodwill: float

    # 现金流量表
    operating_cash_flow: float
    free_cash_flow: float
    capex: float

    # 关键比率（计算得出）
    roe: float               # 净资产收益率
    roic: float              # 投入资本回报率
    debt_to_equity: float    # 资产负债率
    gross_margin: float      # 毛利率
    operating_margin: float  # 经营利润率
    fcf_yield: float         # 自由现金流收益率
```

### 5.2 分析报告

```python
@dataclass
class AnalysisReport:
    ticker: str
    market: str
    date: datetime
    scenes_completed: list[str]

    # 各场景产出
    screening_result: dict | None
    qualitative_analysis: str | None      # Markdown
    quantitative_analysis: str | None     # Markdown
    valuation_result: dict | None         # DCF 参数 + 结果
    decision: str | None                  # Markdown 投资备忘录

    # 元数据
    insights_used: list[Insight]          # 引用的笔记洞见
    data_sources: list[str]               # 使用的数据源
    token_usage: int                      # 总 token 消耗
```

---

## 六、关键设计决策

### 6.1 模板驱动 > 自由对话

每个 Scene 的 System Prompt 包含完整的分析模板章节。LLM 的任务是逐章节填充，而非自由发挥。

**为什么**：dayu-agent 的实践证明，模板驱动的输出质量远高于自由对话。自由对话容易产生泛泛而谈的"卖方报告"，模板驱动能产出有决策价值的"买方分析"。

### 6.2 不碰 PDF/HTML 财报解析

MVP 阶段只使用 AKShare/yfinance 的结构化数据。PDF 解析是 dayu-agent 花了 2 万行代码才搞定的领域，不重复造轮子。

**未来**：如果需要更深入的财报数据，可以考虑调用 dayu-agent 处理过的数据作为输入。

### 6.3 笔记 = 差异化护城河

个人投资笔记是 zhixing agent 独有的数据维度。将笔记洞见与结构化分析框架融合，是其他工具做不到的。

### 6.4 每个结论可追溯

dayu-agent 的核心理念："让数据有置信度，让投资结论可审计、可追踪"。

- 财务数据结论 → 标注 AKShare/yfinance 数据源和时间点
- 定性分析观点 → 标注来源（财报原文/新闻/用户笔记）
- 笔记洞见 → 标注来源笔记路径和原文摘录
