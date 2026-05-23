# P19 Phase 定义（供 implementation-control.md 使用）

> **日期**: 2026-05-22
> **技术方案**: `p19-thermometer-technical-proposal.md`
> **Design 变更**: `design-md-v22-changes.md`

---

## Phase P19: 温度计独立开发

### Goal

独立实现温度计功能，基于有知有行公开方法论复现，不依赖有知有行页面抓取。P19-S1/S2 先交付项目内自建指数温度计和 CLI 读数；P19-S3 才允许在独立 gate 中为 `fund-analysis analyze` 提供估值状态（low/fair/high/unavailable）自动判断能力。全 A 市场温度计保留为目标，但必须等待全 A PE 历史来源验证后进入 P19-S5 / all-A PE source gate。

### Design Truth Update

- design.md §1.3 非目标调整：移除"不做温度计自建"，新增 §11 温度计设计
- design.md §6.3 外部数据表更新：温度计数据源从有知有行页面改为 akshare + 中证指数
- design.md §10 设计决策记录新增 4 条温度计相关决策
- design.md 版本 v2.1 → v2.2

### Entry Criteria

- [ ] P18 已合入 main（或决定并行开发）
- [ ] design.md 已更新至 v2.2（§1.3、§6.3、§10、§11）
- [ ] `p19-thermometer-technical-proposal.md` 已通过 plan review
- [x] akshare 数据可用性裁决完成：全 A PB 已有可用候选；全 A PE 历史未找到可验证来源；P19-S1 scope 改为沪深 300 指数温度计 MVP

### Exit Criteria（可验证）

#### P19 整体

- [ ] 沪深300、中证500 温度计算通过单元测试
- [ ] CLI `fund-analysis thermometer --index 000300` 输出沪深300温度
- [ ] CLI `fund-analysis thermometer --index 000300,000905` 输出批量指数温度
- [ ] CLI `fund-analysis thermometer --json` 输出结构化 JSON
- [ ] P19-S3 后，`fund-analysis analyze` 自动获取支持指数温度并映射为 `valuation_state`，且用户显式输入优先
- [ ] 3 只样本基金 CLI 端到端测试通过
- [ ] 程序审计 P1/P2/P3/C2/L1/R1/R2 全部通过
- [ ] 全量测试套件通过（`pytest -q`）
- [ ] ruff 检查通过
- [ ] 与有知有行页面温度方向对比验证通过（低估/中估/高估方向一致）

#### P19-S1 沪深300指数温度计 MVP

- [ ] `ThermometerDataSource` Protocol 定义完成
- [ ] 沪深300 PE/PB 历史数据获取实现并通过 fixture 测试
- [ ] `ThermometerCalculator` PE/PB 分位数和综合温度计算通过测试
- [ ] 历史分位数计算正确（使用已知 fixture 数据验证）
- [ ] `ThermometerReading` dataclass 定义完成
- [ ] 缓存机制工作正常（parquet 格式或接受的替代格式，增量更新）
- [ ] CLI `fund-analysis thermometer --index 000300` 输出沪深300温度
- [ ] 数据源失败时输出 `unavailable`，不 fallback 到有知有行页面抓取

#### P19-S2 宽基指数温度计

- [ ] 中证500 PE/PB 历史数据获取实现
- [ ] 指数级温度计算通过单元测试
- [ ] CLI 支持指定指数查询（`--index 000300`）
- [ ] CLI 支持批量查询（`--index 000300,000905`）

#### P19-S3 analyze 自动集成

- [ ] `fund-analysis analyze` 自动调用温度计获取对应指数温度
- [ ] 指数基金 → 使用跟踪指数温度
- [ ] 主动基金 → 使用业绩基准对应指数温度
- [ ] 温度不可用 → `ValuationState.UNAVAILABLE`
- [ ] 检查清单第 6 题自动填充估值状态
- [ ] 3 只样本基金端到端测试通过

#### P19-S4 扩展指数覆盖

- [ ] 创业板指、科创50、中证红利、中证消费、中证医药 温度计算通过测试
- [ ] CLI 批量查询覆盖所有支持的指数

#### P19-S5 全 A 市场温度计

- [ ] 全 A PE 历史来源通过验证，包含字段、历史覆盖、缺失规则和使用许可
- [ ] 全 A PB `stock_a_all_pb()` 字段语义已冻结为 fixture
- [ ] 全 A PE/PB 历史数据获取实现并通过测试
- [ ] CLI `fund-analysis thermometer` 默认输出全 A 市场温度
- [ ] 与有知有行页面温度方向对比验证通过

### Hard Constraints（明确不做）

- 不依赖有知有行页面抓取
- 不引入付费数据源（除非显式授权）
- 不追求与有知有行温度计数值精确一致
- 不提供短期择时信号
- 不支持非 A 股市场温度计算
- 不修改现有 Service/Capability 分层边界
- 不引入 Dayu Host/Engine/tool loop
- 不修改现有分析引擎逻辑（R=A+B-C、检查清单等）
- CLI 和报告输出必须包含免责标注

### Dependencies

| 依赖 | 说明 |
|------|------|
| akshare | 全 A PB、分市场 PE/PB、宽基指数 PE/PB 候选数据源（项目已有依赖）；全 A PE 历史仍需验证 |
| pandas | 数据处理（项目已有依赖） |
| pyarrow 或 fastparquet | parquet 缓存格式（需新增依赖） |

### Open Residuals

| 风险 | Owner | 处理方式 |
|------|-------|----------|
| akshare 全 A 股 PE/PB 接口稳定性 | Capability | 全 A PB 可走 `stock_a_all_pb()`；全 A PE 历史未找到可验证来源；全 A 市场温度计移至 P19-S5 / all-A PE source gate |
| 等权计算与有知有行结果偏差 | P19-S1 验证 | 文档标注"方法论复现"，方向一致即可 |
| 历史数据首次下载耗时长 | P19-S1/S5 | 指数温度计低成本；全 A 若逐股重建必须另行接受耗时、存储量和增量策略 |
| akshare / 乐咕乐股访问抖动 | P19-S1/S2 | Protocol 封装、fixture 测试、retry/cache/unavailable 语义；禁止 fallback 到有知有行页面抓取 |

### Non-goal Reminder

- 不引入 LLM 写作、Host、Engine、tool loop
- 不修改现有审计规则
- 不扩展至 QDII 或债券基金温度

### Resume Checklist

- 确认当前 gate 和 next entry point
- P18 已合入 main 或决定并行
- design.md 已更新至 v2.2
- P19-S1 已改为沪深300指数温度计 MVP；全 A 市场温度计等待 P19-S5 / all-A PE source gate
- 不修改外部 GitHub 状态（PR/issue）除非显式授权
- 保持确定性 MVP 边界
