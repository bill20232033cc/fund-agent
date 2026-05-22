# P19 温度计独立开发技术方案

> **日期**: 2026-05-22
> **状态**: 待 plan review
> **关联**: design.md §11（新增）、implementation-control.md P19（新增）

---

## 1. 背景与决策

### 1.1 决策

温度计功能独立开发，不依赖有知有行页面抓取。

### 1.2 理由

- 有知有行页面结构可能随时变化，抓取方案不可靠
- 独立开发可完全掌控数据质量和计算逻辑
- 可扩展至有知有行未覆盖的指数和资产类别

---

## 2. 有知有行温度计方法论研究

### 2.1 数据来源

根据有知有行官方说明（[来源](https://youzhiyouxing.cn/materials/172)）：

| 要素 | 有知有行做法 |
|------|-------------|
| **样本空间** | A 股所有上市公司 |
| **参考指数** | 万得全 A（Wind 全 A） |
| **计算指标** | PE（市盈率）+ PB（市净率）综合 |
| **加权方式** | **等权**（非市值加权） |
| **考察周期** | 包含**两轮完整牛熊周期**（动态窗口） |
| **温度区间** | 低估 0°~30°、中估 30°~70°、高估 70°~100° |

### 2.2 核心算法（逆向工程）

基于有知有行公开描述，温度计算逻辑为：

```
步骤 1: 获取 A 股所有上市公司当日 PE 和 PB
步骤 2: 对所有公司 PE 取等权中位数 → 全市场 PE 中位数
步骤 3: 对所有公司 PB 取等权中位数 → 全市场 PB 中位数
步骤 4: 计算 PE 中位数在历史周期中的分位数 → PE 温度
步骤 5: 计算 PB 中位数在历史周期中的分位数 → PB 温度
步骤 6: 综合温度 = (PE 温度 + PB 温度) / 2
步骤 7: 映射为估值状态：≤30% → low, 30%~70% → fair, ≥70% → high
```

### 2.3 关键设计决策

| 决策点 | 有知有行选择 | 我们的复现策略 |
|--------|-------------|---------------|
| 样本空间 | A 股所有上市公司 | **复现**：使用全 A 股样本 |
| 加权方式 | 等权 | **复现**：使用等权中位数 |
| 考察周期 | 两轮完整牛熊周期 | **复现**：动态窗口（约 10-15 年） |
| 综合方式 | PE + PB 各 50% | **复现**：等权平均 |
| 分位数计算 | 未公开具体算法 | 使用标准百分位排名 |

### 2.4 数据来源选择

| 数据源 | 用途 | 获取方式 | 可行性 |
|--------|------|----------|--------|
| **akshare** | 全 A 股 PE/PB 日频数据 | `ak.stock_a_lg_indicator()` 或类似接口 | ✅ 免费、开源、已作为项目依赖 |
| **中证指数官方** | 指数级 PE/PB（宽基/行业） | CSIndex API | ✅ 免费，需申请 |
| **东方财富** | 个股 PE/PB | akshare 封装 | ✅ 已有 fallback 经验 |

**推荐方案**：以 akshare 为主数据源，中证指数官方为指数级数据补充源。

---

## 3. 精选基金池指数覆盖分析

### 3.1 已知精选基金池信息

根据 design.md 和 README，精选基金池（`docs/code_20260519.csv`）包含 56 条记录、55 个唯一基金代码，覆盖以下基金类别：

| 类别 | 说明 |
|------|------|
| 宽基指数基金 | 沪深300、中证500、创业板指、科创50 等 |
| 行业指数基金 | 消费、医药、科技 等 |
| 策略指数基金 | 红利、低波动 等 |
| 主动权益基金 | 混合型、股票型 |
| 债券基金 | 纯债、二级债基 |
| QDII 基金 | 境外市场 |
| FOF 基金 | 基金中基金 |

### 3.2 温度计需要覆盖的指数

基于有知有行精选基金池的典型构成，温度计需要支持以下指数：

#### 宽基指数（必须支持）

| 指数 | 代码 | 用途 | 优先级 |
|------|------|------|--------|
| 万得全 A | Wind 全 A | 全市场温度（核心） | P0 |
| 沪深 300 | 000300 | 大盘蓝筹 | P0 |
| 中证 500 | 000905 | 中盘成长 | P0 |
| 创业板指 | 399006 | 成长板块 | P1 |
| 科创 50 | 000688 | 科技创新 | P1 |

#### 行业指数（建议支持）

| 指数 | 代码 | 用途 | 优先级 |
|------|------|------|--------|
| 中证消费 | 000932 | 消费行业 | P1 |
| 中证医药 | 000933 | 医药行业 | P1 |
| 国证食品饮料 | 399396 | 食品饮料 | P2 |
| 中证科技 | 931087 | 科技行业 | P2 |

#### 策略指数（建议支持）

| 指数 | 代码 | 用途 | 优先级 |
|------|------|------|--------|
| 中证红利 | 000922 | 红利策略 | P1 |
| 中证低波动 | H30269 | 低波策略 | P2 |

### 3.3 覆盖范围决策

| 阶段 | 覆盖范围 | 说明 |
|------|----------|------|
| **P19 MVP** | 万得全 A + 沪深300 + 中证500 | 覆盖全市场 + 两大核心宽基 |
| **P19 扩展** | + 创业板指 + 科创50 + 中证红利 + 中证消费 + 中证医药 | 覆盖精选基金池主要指数 |
| **后续 Phase** | + 其他行业/策略指数 | 按需扩展 |

---

## 4. 技术架构设计

### 4.1 模块边界

```
UI 层（CLI）
  → ThermometerService（Service 层）
    → ThermometerCalculator（Capability 层 - 计算引擎）
    → ThermometerDataSource（Capability 层 - 数据获取）
    → ThermometerCache（Capability 层 - 缓存）
```

| 层级 | 模块 | 职责 |
|------|------|------|
| UI | `cli.py` | `fund-analysis thermometer` 命令入口 |
| Service | `ThermometerService` | 编排数据获取 → 计算 → 缓存 → 输出 |
| Capability | `ThermometerCalculator` | PE/PB 分位数计算、温度综合、估值状态映射 |
| Capability | `ThermometerDataSource` | 从 akshare/中证指数获取 PE/PB 数据 |
| Capability | `ThermometerCache` | 历史数据缓存、增量更新 |

### 4.2 核心接口设计

```python
@dataclass(frozen=True)
class ThermometerReading:
    """单次温度计读数"""
    index_code: str           # 指数代码（如 "000300"）
    index_name: str           # 指数名称（如 "沪深300"）
    pe_percentile: float      # PE 分位数（0-100）
    pb_percentile: float      # PB 分位数（0-100）
    temperature: float        # 综合温度（0-100）
    valuation_state: ValuationState  # low / fair / high
    data_date: date           # 数据日期
    lookback_start: date      # 回溯期起始日
    lookback_years: float     # 回溯期年数

@dataclass(frozen=True)
class ThermometerBatchResult:
    """批量温度计结果"""
    readings: tuple[ThermometerReading, ...]
    computed_at: datetime
    data_source: str          # "akshare" / "csindex" / "cache"

class ThermometerCalculator(Protocol):
    """温度计计算引擎协议"""
    def calculate(self, index_code: str, ...) -> ThermometerReading: ...
    def calculate_batch(self, index_codes: tuple[str, ...], ...) -> ThermometerBatchResult: ...

class ThermometerDataSource(Protocol):
    """温度计数据源协议"""
    def fetch_pe_pb_history(self, index_code: str, lookback_years: float) -> PePbHistory: ...
```

### 4.3 计算流程

```
1. ThermometerDataSource.fetch_pe_pb_history(index_code, lookback_years)
   → 获取指数/全市场历史 PE/PB 序列

2. ThermometerCalculator._compute_percentile(current_value, history)
   → 计算当前值在历史序列中的百分位排名

3. ThermometerCalculator._compute_temperature(pe_percentile, pb_percentile)
   → 综合温度 = (PE 分位 + PB 分位) / 2

4. ThermometerCalculator._map_valuation_state(temperature)
   → ≤30 → low, 30~70 → fair, ≥70 → high

5. ThermometerCache.save(reading)
   → 缓存结果，支持增量更新
```

### 4.4 缓存策略

| 缓存类型 | 路径 | 更新频率 | 说明 |
|----------|------|----------|------|
| 原始数据缓存 | `cache/thermometer/{index_code}/pe_pb_history.parquet` | 日更增量 | PE/PB 历史序列 |
| 计算结果缓存 | `cache/thermometer/{index_code}/reading.json` | 日更 | 最新温度读数 |
| 全市场数据缓存 | `cache/thermometer/wind_all_a/pe_pb_history.parquet` | 日更增量 | 万得全 A 等权 PE/PB |

---

## 5. 与现有系统的集成

### 5.1 CLI 集成

```bash
# 查询全市场温度
fund-analysis thermometer

# 查询指定指数温度
fund-analysis thermometer --index 000300
fund-analysis thermometer --index 000300,000905,399006

# 强制刷新
fund-analysis thermometer --force-refresh

# JSON 输出（供程序消费）
fund-analysis thermometer --json
```

### 5.2 analyze 自动集成

```bash
# 自动获取温度并映射为 valuation-state
fund-analysis analyze 004393 --report-year 2024
# → 自动调用 ThermometerService 获取对应指数温度
# → 映射为 --valuation-state low/fair/high
# → 无需手动传入 --valuation-state
```

### 5.3 与 Quality Gate 集成

温度计数据不直接参与 quality gate，但 `valuation_state` 作为分析输入影响最终判断：
- `low` → 倾向 `worth_holding`
- `high` → 倾向 `needs_attention` 或 `suggest_replace`

---

## 6. 数据源技术细节

### 6.1 akshare 数据获取

```python
# 全市场等权 PE/PB（核心）
# akshare 提供 A 股市场整体估值指标
import akshare as ak

# 方案 A：通过个股数据聚合
df = ak.stock_zh_a_spot_em()  # 全 A 股实时行情（含 PE/PB）
pe_median = df["市盈率-动态"].median()  # 等权中位数
pb_median = df["市净率"].median()

# 方案 B：通过指数估值接口（如果 akshare 提供）
# 需要验证 akshare 是否有全市场等权估值接口
```

### 6.2 中证指数数据获取

```python
# 中证指数官方 API
# https://www.csindex.com.cn/zh-CN/indices/index-detail/000300
# 提供 PE/PB 等估值指标的历史数据

# 或通过 akshare 封装
import akshare as ak
df = ak.index_value_hist_funddb(symbol="沪深300")  # 历史估值
```

### 6.3 历史数据回填

| 数据 | 所需历史长度 | 来源 | 预估数据量 |
|------|-------------|------|-----------|
| 万得全 A PE/PB | ~10-15 年（两轮牛熊） | akshare 个股聚合 | ~5000 只 × 15 年 × 250 交易日 |
| 沪深300 PE/PB | ~10-15 年 | 中证指数 / akshare | ~15 年 × 250 交易日 |
| 中证500 PE/PB | ~10-15 年 | 中证指数 / akshare | ~15 年 × 250 交易日 |

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| akshare 接口变更 | 数据获取失败 | 封装 DataSource Protocol，支持多源切换 |
| 全市场 PE/PB 计算量大 | 首次运行慢 | 增量缓存 + parquet 格式 |
| 等权 vs 市值加权差异 | 与有知有行结果不完全一致 | 文档明确标注"方法论复现，非精确复制" |
| 历史数据缺失 | 分位数计算偏差 | 标注有效数据起始日，不足时扩大回溯期 |
| 有知有行未公开精确算法 | 无法 100% 复现 | 以公开描述为准，接受合理偏差 |

---

## 8. 与有知有行结果的对比验证

### 8.1 验证方法

| 验证项 | 方法 | 通过标准 |
|--------|------|----------|
| 全市场温度方向 | 与有知有行页面对比 | 低估/中估/高估方向一致 |
| 温度数值偏差 | 与有知有行页面对比 | 偏差 ≤ 10° |
| 宽基指数温度 | 与有知有行页面对比 | 方向一致 |

### 8.2 不追求精确复现

有知有行明确表示"出于保密的要求"，未公开精确算法。我们的目标是：

> **方法论复现，方向一致，数值合理偏差可接受。**

在报告和 CLI 输出中应明确标注：

```
⚠️ 本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。
计算方法：全市场等权 PE/PB 中位数历史分位数综合。
与有知有行官方温度计可能存在合理偏差。
```

---

## 9. 实施分阶段计划

### Phase P19-S1: 全市场温度计 MVP

**目标**：实现万得全 A 全市场温度计算

**Exit Criteria**：
- [ ] 全市场 PE/PB 等权中位数计算通过单元测试
- [ ] 历史分位数计算正确（使用已知数据验证）
- [ ] CLI `fund-analysis thermometer` 输出全市场温度
- [ ] 缓存机制工作正常（首次计算后，二次读取走缓存）
- [ ] 与有知有行页面方向对比验证通过

### Phase P19-S2: 宽基指数温度计

**目标**：扩展至沪深300、中证500

**Exit Criteria**：
- [ ] 沪深300、中证500 温度计算通过单元测试
- [ ] CLI 支持指定指数查询
- [ ] 与有知有行页面方向对比验证通过

### Phase P19-S3: analyze 自动集成

**目标**：`fund-analysis analyze` 自动获取温度并映射 valuation-state

**Exit Criteria**：
- [ ] analyze 自动调用温度计获取对应指数温度
- [ ] 温度映射为 `ValuationState`（low/fair/high）
- [ ] 3 只样本基金端到端测试通过
- [ ] 程序审计 P1/P2/P3/C2/L1/R1/R2 全部通过

### Phase P19-S4: 扩展指数覆盖

**目标**：扩展至创业板指、科创50、中证红利、中证消费、中证医药

**Exit Criteria**：
- [ ] 5 个扩展指数温度计算通过单元测试
- [ ] CLI 支持批量查询
- [ ] 与有知有行页面方向对比验证通过
