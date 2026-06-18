# Docling 架构重定位：从死循环到正确路线

> 日期：2026-06-17
> 性质：架构讨论纪要，供后续 gate/phase 决策参考
> 前提：已读 `docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md`、dayu-agent GitHub 仓库（`noho/dayu-agent`）Fins 包源码、当前 `docs/implementation-control.md`、`docs/reviews/docling-*` 全量 review 文件

---

## 1. 当前状态诊断

### 1.1 死循环证据

| 指标 | 数值 | 说明 |
|------|------|------|
| docling 相关 review 文件 | **367 个** | `docs/reviews/docling-*` |
| review 文件总行数 | **~47,000 行** | 仅 docling 相关 |
| representation JSON 单文件 | **2.4MB ~ 6.3MB** | 4 只基金 × 多种 parser |
| representation JSON 总量 | **~34MB** | 全量 dump |
| 当前 gate | `Docling Field Correctness Comparative Evidence Gate` | 仍在 "baseline qualification" |
| release/readiness | **NOT_READY** | 自始至终未变 |

### 1.2 死循环结构

```
Gate N: "验证 X 能力"
  → 发现 Y 未证明
    → Gate N+1: "验证 Y"
      → 发现 Z 未证明
        → Gate N+2: "验证 Z"
          → 发现 X 的新边界未覆盖
            → ...
```

从 `docs/implementation-control.md` 可以看到完整链条：

1. Representation Schema → 2. Locator Stability → 3. Field-Family Pilot → 4. Multi-Sample Expansion → 5. Same-Source Reference → 6. Cache Metadata → 7. Runtime Containment → 8. Full-Document Coverage → 9. EvidenceAnchor Mapping → 10. Section-Context Enrichment → 11. Source Truth Residual Closure → 12. Field Correctness Comparative Evidence → ...

每一步都产生 `plan → review (DS+MiMo) → evidence → controller judgment → re-evidence`，每步 5-10 个 review 文件。

### 1.3 Root Cause

**把 Docling 放错了架构位置。**

| 当前定位 | 问题 |
|----------|------|
| "有界 benchmark 候选" | 但 gate 链按"生产 parser 替代品"的完备性要求它 |
| "不作为生产依赖" | 但投入了 367 个 review 文件证明它的正确性 |
| "candidate-layer 表示能力" | 但 4.8MB 的 JSON 是全量 dump，不是按模板章节的结构化输入 |

**用生产级完备性标准去验证一个"研究输入"，导致永远验不完。**

---

## 2. dayu-agent Fins 架构的关键启示

### 2.1 Docling 在 dayu-agent 中的定位

dayu-agent 的 Fins 包里，Docling 只是一个**优先级 100 的通用 PDF 处理器**：

| 优先级 | 角色 | 处理器 |
|--------|------|--------|
| 200 | SEC 表单主路径 | `BsTenKFormProcessor`、`BsTwentyFFormProcessor` 等专项处理器 |
| 190 | SEC 表单回退 | edgartools 系列 |
| 120 | SEC 通用兜底 | `SecProcessor` |
| **100** | **文档格式通用** | **`FinsDoclingProcessor`（PDF）、`FinsMarkdownProcessor`** |
| 80 | HTML 通用 | `FinsBSProcessor` |

关键事实：
- Docling 在 download 阶段就把 PDF 转成 `_docling.json`，这是**一次性转换**，不是每次分析都跑
- 真正的结构化提取在 **Processor 层**，不在 Docling 层
- Processor 分派由 `source + form_type + media_type` 三键决定，不看 ticker、不看 market
- CN/HK 文档当前直接走通用 Docling 处理器，没有专项处理器——dayu-agent 自己也没有为 A 股做专项 extractor

### 2.2 dayu-agent 的两层分派机制

**第一层：ticker → pipeline（按 market 分派）**

```
NormalizedTicker.market == "US"            → SecPipeline
NormalizedTicker.market in {"HK", "CN"}    → CnPipeline
其它                                        → ValueError
```

**第二层：document → processor（按 source + form_type + media_type 分派）**

```
Source.supports(form_type, media_type) → ProcessorRegistry.create_with_fallback(...)
```

分派真源是 `ProcessorRegistry`，遍历所有注册 processor，按 priority 降序调用 `supports()`，取第一个实例化成功的。

### 2.3 核心设计原则

1. **Docling 是转换工具，不是提取工具**：PDF → `_docling.json` 是一次性转换，落盘复用
2. **Processor 负责结构化提取**：每个 Processor 理解自己要提取什么，返回 `SectionContent` 等强类型契约
3. **注册表驱动分派**：不硬编码 `if fund_type == ...`，而是按优先级注册、按条件匹配
4. **中间态可复用**：`_docling.json` 落盘后，后续分析不需要重新解析 PDF

---

## 3. fund-agent 应采用的正确架构

### 3.1 三层架构

```
                    FundDocumentRepository（仓储层）
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
           年报 PDF       季报 PDF       募集说明书 PDF
               │              │              │
               ▼              ▼              ▼
     Docling/pdfplumber（转换层，一次性，内部实现）
               │              │              │
               ▼              ▼              ▼
       _docling.json / _pdfplumber.json（中间态，落盘复用）
               │
               ▼
   ┌───────────┴───────────┐
   │   Processor 分派层     │  ← 按 fund_type + report_type + media_type
   │   （自制 Extractor）   │
   └───────────┬───────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 主动基金    指数基金    债券基金
 Extractor   Extractor   Extractor
    │          │          │
    ▼          ▼          ▼
 按模板章节提取结构化字段（这才是 "data warehouse"）
    │
    ▼
 8 章分析模板的结构化输入
```

### 3.2 Docling 的正确角色

- **转换工具**：PDF → Markdown/JSON，一次性执行，落盘复用
- **内部实现**：`FundDocumentRepository` 内部，Service/UI/Host/Renderer 不直接调用
- **不做 baseline representation**：Docling 输出是原材料，不是终点
- **不验证"整体正确性"**：验证粒度应该是单个 Extractor 提取的字段，不是 4.8MB 全量 JSON

### 3.3 Extractor 的设计（自制，学 dayu-agent Processor）

```python
# 类似 dayu-agent 的 ProcessorRegistry
class FundProcessorRegistry:
    """基金文档处理器注册表"""
    
    def register(self, processor_cls: type, priority: int):
        """注册处理器，按优先级排序"""
        ...
    
    def resolve(self, fund_type: str, report_type: str, media_type: str):
        """按三键分派，返回第一个 supports() 为 True 的处理器"""
        ...

class ActiveFundAnnualExtractor:
    """主动股票型基金年报提取器"""
    
    priority = 200
    
    def supports(self, fund_type: str, report_type: str, media_type: str) -> bool:
        return fund_type == "active_fund" and report_type == "annual" and media_type == "pdf"
    
    def extract(self, docling_json: dict) -> FundAnalysisData:
        """从 docling 中间态提取模板需要的结构化数据"""
        ...
```

### 3.4 按模板章节的字段族映射

| 模板章节 | 需要的字段族 | 来源年报章节 | Extractor 方法 |
|----------|-------------|-------------|----------------|
| §1 产品本质 | 基金类型、投资目标、比较基准 | 年报§投资目标 | `extract_product_essence()` |
| §2 收益归因 | 净值增长率、业绩比较基准、Alpha/Beta | 年报§主要财务指标 | `extract_return_attribution()` |
| §3 基金经理 | 从业年限、管理规模、持有本基金 | 年报§基金经理 | `extract_manager_profile()` |
| §4 投资者获得感 | 换手率、持有人结构、申赎数据 | 年报§基金份额持有人信息 | `extract_investor_experience()` |
| §5 当前阶段 | 规模变化、持仓变化 | 年报§投资组合 | `extract_current_stage()` |
| §6 核心风险 | 最大回撤、集中度、行业偏离 | 年报§投资组合/风险指标 | `extract_risk_profile()` |

### 3.5 验证方式的转变

| 维度 | 当前（死循环） | 正确路线 |
|------|--------------|----------|
| 验证对象 | Docling 输出（4.8MB JSON） | Extractor 提取的字段（几十 KB） |
| 对照物 | 另一个 parser 的输出 | 年报 PDF 中人工可读的数据 |
| 验证粒度 | 全量文档 representation | 单个字段族 |
| 完成标准 | "Docling baseline qualification" | "Extractors 覆盖全部 8 章模板" |
| 扩展方式 | 新增 gate 证明新边界 | 新增 Extractor 覆盖新基金类型 |

---

## 4. 实施路线建议

### 4.1 第一步：止血

- 将 Docling gate 链标记为 `DEFERRED`
- 367 个 review 文件归档到 `docs/archive/docling-benchmark-*`
- 更新 `docs/implementation-control.md`，明确 Docling 新定位

### 4.2 第二步：建立 Processor 注册表

- 创建 `fund_agent/fund/processors/` 模块
- 实现 `FundProcessorRegistry`（学 dayu-agent 的 `ProcessorRegistry`）
- 定义 `FundProcessorProtocol`（`supports()` + `extract()`）

### 4.3 第三步：实现第一个 Extractor

- 选**主动股票型基金年报**（最常见、数据最丰富）
- 只提取模板 §1-§6 需要的字段族
- 验证方式：对照 004393（富国天惠）年报 PDF 中的人工可读数据

### 4.4 第四步：扩展 Extractor 覆盖面

```
主动基金年报 → 主动基金季报 → 指数基金 → 债券基金 → QDII → FOF
```

每个 Extractor 只关心自己基金类型的特有字段。

### 4.5 第五步：数据仓库化

- Extractor 输出落盘为结构化 JSON（按基金代码 + 报告类型 + 年份）
- 多年数据累积形成 `workspace/portfolio/{fund_code}/structured/`
- 模板分析直接读取结构化数据，不再每次解析 PDF

---

## 5. 与当前 AGENTS.md / design.md 的对齐

### 5.1 需要更新的规则

- `AGENTS.md` 中"年报解析器（pdfplumber/Docling）属于 `FundDocumentRepository` 内部实现边界"——保持不变
- `AGENTS.md` 中"生产年报 PDF 访问必须经过 `FundDocumentRepository`"——保持不变
- 新增：**结构化数据提取必须通过 `FundProcessorRegistry`，禁止直接消费 Docling 原始输出**

### 5.2 需要更新的设计真源

- `docs/design.md` 中 Docling 相关章节：从"候选 baseline representation"更新为"通用 PDF 转换工具"
- 新增：Processor/Extractor 层的架构设计

### 5.3 四层架构的边界

- **UI**：渲染 Extractor 输出的结构化数据，不调用 Docling/Extractor
- **Service**：编排分析流程，调用 Host 执行 Agent
- **Host**：管理 session/run 生命周期
- **Agent**：消费 Extractor 输出的结构化数据，执行分析/LLM 写作

---

## 6. 一句话总结

**dayu-agent 用 Docling 做一次性 PDF 转换，用 Processor/Extractor 做结构化提取，用三键分派做路由。fund-agent 应该学这个架构，砍掉 367 个 review 文件的 gate 链，转而建设 Processor/Extractor 层，这才是通往"长期化数据仓库"的正确路径。**
