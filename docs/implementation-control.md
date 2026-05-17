# 基金行为教练 Agent —— 实施总控文档

> **版本**: v1.0
> **日期**: 2026-05-16
> **设计真源**: `docs/design.md`
> **MVP 计划书**: `fund-agent-mvp-plan.md`
> **定性模板**: `fund-analysis-template-draft.md`

---

## 1. 总览

### 1.1 Phase 列表

| Phase | 名称 | 周期 | 状态 | 依赖 |
|-------|------|------|------|------|
| P0 | 环境搭建与架构骨架 | Week 1 | ✅ done | 无 |
| P1 | 数据层（PDF 下载 + 解析 + 提取） | Week 2-3 | ✅ done | P0 |
| P2 | 分析引擎（R=A+B-C + 检验 + 审计） | Week 3-4 | 🟡 in progress | P1 |
| P3 | CLI 入口 + 整合测试 + 验证 | Week 4-5 | ⬜ pending | P2 |

### 1.2 里程碑

| 里程碑 | 目标日期 | 关联 Phase | 验收标准 |
|--------|---------|-----------|---------|
| M1: 架构就绪 | Week 1 结束 | P0 | 四层骨架可运行，样本基金 PDF 可下载解析 |
| M2: 数据管道可用 | Week 3 中 | P1 | 12 项关键数据提取准确率 > 90% |
| M3: 分析引擎可用 | Week 4 中 | P2 | R=A+B-C 计算正确，言行一致性检验输出信号 |
| M4: MVP 交付 | Week 5 结束 | P3 | `fund-analysis <code>` 输出完整 8 章报告 |

### 1.3 当前 Gate 与基线裁决（2026-05-17）

- 当前分支：`chore/reconcile-baseline`
- 当前 gate：`P2-S1 implementation + review`
- 下一 gate：`P2-S1 implementation + review`
- 当前裁决：
  - P0 维持 `done`。已验证 `dayu` 依赖可导入、`fund-agent` 处于 editable install、`fund-analysis --help` 可用、样本基金 `110011` 年报可下载、`pdfplumber` 可提取全文文本和表格。
  - P1 已完成并通过 aggregate review。
  - P2 进入 `in progress`。
  - `P1-S1 文档访问契约收口` 已完成：对外唯一仓库入口收口为 `FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`，公共契约已迁入 `fund_agent/fund/documents/*`，`fund_agent/fund/pdf/*` 降为仓库内部 helper / adapter。
  - `P1-S2 章节定位修复与 §3 冻结` 已完成：
    - `§3` root cause 已直接关闭，不是基金代码特判
    - 章节规则已迁出到 `fund_agent/fund/pdf/section_catalog.py`
    - 目录过滤已从单一 `"..."` 升级为可复用规则表
    - `110011/2024` 的正文 `§3` 已由 fixture + test 稳定覆盖
  - `P1-S3 两级缓存与仓库内解析物化` 已完成：
    - raw PDF 元信息缓存与 parsed report 物化缓存均已落在 `documents` 层内部
    - repository 已优先命中缓存，避免重复下载 / 重复全文解析
    - `force_refresh=True` 已正确穿透 parsed report 与已记录的 PDF 路径
    - 本 slice 未创建 `structured_data` 表，也未冻结其 schema
  - `P1-S4 基础画像与基金类型识别` 已完成：
    - `fund_agent/fund/fund_type.py` 已承载稳定的基金类型识别输出 `classified_fund_type` / `classification_basis`
    - `fund_agent/fund/extractors/profile.py` 已落地 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule`
    - 基金类型识别已显式先于通用字段构造执行，并由测试锁定
    - 费率、基准、规模、经理信息均已带 `EvidenceAnchor`
  - `P1-S5 §3 表现提取与投资者收益 fallback` 已完成：
    - `fund_agent/fund/extractors/performance.py` 已落地 `nav_benchmark_performance` 与 `investor_return`
    - `investor_return` 已稳定区分 `direct / estimated / missing`
    - `§3` 直接披露与估算披露命中均带 `EvidenceAnchor`
    - 未披露路径不再静默返回空字符串，而是显式标记 `missing`
    - `nav_benchmark_performance` 在部分命中时不再伪装成完整 `direct`
  - `P1-S6 管理人文本、换手率、利益一致性与持有人结构` 已完成：
    - `fund_agent/fund/extractors/manager_ownership.py` 已落地 `manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure`
    - `§4/§8/§9` 命中字段均带 `EvidenceAnchor`
    - `manager_alignment` 仅输出原始披露，未引入利益一致性判断
    - 未披露路径显式标记 `missing`
  - `P1-S7 持仓快照与份额变动` 已完成：
    - `fund_agent/fund/extractors/holdings_share_change.py` 已落地 `holdings_snapshot` 与 `share_change`
    - 前十大重仓与份额变动可结构化输出
    - 行业分布未披露时显式标记 `missing`
    - 表格命中路径均带页码、表 ID 和行定位
  - `P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵` 已完成：
    - `fund_agent/fund/data_extractor.py` 已落地 `FundDataExtractor` 与 `StructuredFundDataBundle`
    - `fund_agent/fund/data/nav_data.py` 已落地 `FundNavDataAdapter` 与 `nav_cache`
    - 3 只样本基金 12 项矩阵达到 `36/36`
    - P1 全量测试当前通过
- 下一 entry point：
  - 进入 `P2-S1 implementation + review`
  - 优先目标是实现 R=A+B-C 计算模块
- 当前 artifact：
  - plan: `docs/reviews/p1-plan-2026-05-17.md`
  - plan review: `docs/reviews/p1-plan-review-2026-05-17.md`
  - `P1-S1`:
    - baseline reconciliation: `docs/reviews/p1-s1-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s1-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s1-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s1-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s1-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s1-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s1-rereview-mimo-2026-05-17.md`
      - `docs/reviews/p1-s1-rereview-glm-2026-05-17.md`
      - controller confirmation: `docs/reviews/p1-s1-rereview-controller-2026-05-17.md`
    - accepted slice commit: `e772dae`
  - `P1-S2`:
    - baseline reconciliation: `docs/reviews/p1-s2-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s2-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s2-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s2-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s2-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `c3bd264`
  - `P1-S3`:
    - baseline reconciliation: `docs/reviews/p1-s3-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s3-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s3-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s3-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s3-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `d92eef7`
  - `P1-S4`:
    - baseline reconciliation: `docs/reviews/p1-s4-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s4-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s4-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s4-code-review-glm-2026-05-17.md`
      - `docs/reviews/p1-s4-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s4-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s4-rereview-glm-2026-05-17.md`
      - `docs/reviews/p1-s4-rereview-controller-2026-05-17.md`
    - accepted slice commit: `22a1a7a`
  - `P1-S5`:
    - baseline reconciliation: `docs/reviews/p1-s5-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s5-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s5-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s5-code-review-glm-2026-05-17.md`
      - `docs/reviews/p1-s5-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s5-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s5-rereview-controller-2026-05-17.md`
    - accepted slice commit: `8102944`
  - `P1-S6`:
    - baseline reconciliation: `docs/reviews/p1-s6-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s6-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s6-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `18566f9`
  - `P1-S7`:
    - baseline reconciliation: `docs/reviews/p1-s7-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s7-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s7-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `3167754`
  - `P1-S8`:
    - baseline reconciliation: `docs/reviews/p1-s8-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s8-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s8-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `d398bc2`
  - `P1 aggregate review`: `docs/reviews/p1-aggregate-review-2026-05-17.md`
  - baseline commit: `9956c45`

---

## 2. Phase 详细定义

### P0: 环境搭建与架构骨架

**目标**

完成开发环境搭建，建立四层架构骨架，验证数据提取可行性。

**进入条件**

- [x] 设计真源文档 `docs/design.md` 已冻结
- [x] 实施总控文档 `docs/implementation-control.md` 已创建
- [x] Python 3.11+ 可用

**退出条件**

- [x] `dayu-agent` 包可正常安装且 import 通过（`dayu.engine`、`dayu.host`、`dayu.config`）
- [x] 四层架构目录结构就位（ui/services/fund/config）
- [x] `pyproject.toml` 配置完成且 `pip install -e .` 无报错
- [x] 选定 3-5 只样本基金并记录分析基准
- [x] 能从巨潮资讯网下载至少 1 只样本基金的年报 PDF
- [x] 能用 pdfplumber 提取 PDF 文本和表格
- [x] `fund-analysis` CLI 命令可运行且输出帮助信息

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P0-S1 | 安装 dayu-agent 依赖，验证 Engine/Host/Config 可用 | `python -c "from dayu.engine import AsyncAgent; from dayu.host import Host"` 通过 |
| P0-S2 | 创建项目骨架目录结构（ui/services/fund/config） | `ls fund_agent/` 输出符合 design.md |
| P0-S3 | 编写 `pyproject.toml`（含 dayu-agent 依赖 + pdfplumber 等） | `pip install -e .` 无报错 |
| P0-S4 | 选定样本基金（从有知有行严选基金池） | 记录基金代码和手动分析结果 |
| P0-S5 | 实现 `fund/pdf/downloader.py` 基础版 | 能下载巨潮网年报 PDF |
| P0-S6 | 实现 `fund/pdf/parser.py` 基础版 | 能读取 PDF 文本和表格 |
| P0-S7 | 编写 CLI 入口（`fund-analysis` 命令） | `fund-analysis --help` 输出帮助信息 |

**验证要求**

- P0-S4：下载 3 只不同类型基金的年报 PDF，确认均可获取
- P0-S5：对 1 只基金年报执行 pdfplumber 提取，确认能读取 §2/§3/§4/§8/§9/§10 的文本

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 巨潮网反爬 | 低 | 改用东方财富 akshare API + pdf.dfcfw.com | ✅ 已缓解：改用 akshare + eastmoney PDF |
| pdfplumber 对中文 PDF 支持差 | 中 | 备选 PyPDF2 + pdfminer.six | ✅ 已验证：中文提取正常，70K 字文本可提取 |

**当前实现裁决（2026-05-17）**

- 已验证 `fund-agent==0.1.0` 以 editable install 方式安装在当前虚拟环境中，`fund-analysis --help` 可直接运行。
- 已验证样本基金基线存在：`docs/sample-funds.md` 已记录主动权益、指数、债券三类样本。
- 已验证样本年报下载与解析链路：`110011` 的 2024 年年报可下载，且可提取约 70K 字全文与 99 个表格。
- 当前未把 `pip install -e .` 的重放网络波动记为代码阻塞；下载 `dayu-agent` wheel 时可能受 GitHub 可达性影响。

---

### P1: 数据层（PDF 下载 + 解析 + 提取）

**目标**

完成 PDF 下载、解析和数据提取功能，能从基金年报中提取 12 项关键数据。

**进入条件**

- [x] P0 退出条件全部满足
- [x] 样本基金 PDF 已下载到本地

**退出条件**

- [ ] `fund/pdf/downloader.py` 能下载任意基金年报 PDF（输入基金代码）
- [ ] `fund/pdf/parser.py` 能解析 PDF 并提取文本和表格
- [ ] `fund/data_extractor.py` 能提取 12 项关键数据（准确率 > 90%）
- [ ] `fund/pdf/cache.py` 两级缓存（文件 + SQLite）可用
- [ ] 对 3 只样本基金的数据提取结果与人工核对一致

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P1-S1 | 文档访问契约收口 | `FundDocumentRepository.load_annual_report(...)` 成为唯一公开入口 |
| P1-S2 | 章节定位修复与 `§3` 冻结 | `110011/2024` 年报稳定命中 `§3` 正文 |
| P1-S3 | 两级缓存与仓库内解析物化 | 重复加载同一年报不重复下载/不重复全文解析 |
| P1-S4 | 基础画像与基金类型识别 | 3 只样本都输出 `classified_fund_type` 与 `classification_basis` |
| P1-S5 | `§3` 表现提取与投资者收益 fallback | 净值增长率、基准收益率、投资者收益三态输出 |
| P1-S6 | 管理人文本、换手率、利益一致性与持有人结构 | `§4/§8/§9` 直接披露字段可结构化提取 |
| P1-S7 | 持仓快照与份额变动 | 前十大重仓、份额期初/期末/净变动可回归 |
| P1-S8 | façade 集成、净值数据适配器与 P1 验收矩阵 | 3 只样本 36 格矩阵至少 `33/36` 通过 |

**验证要求**

- 对 3 只样本基金（指数/主动/债券各 1 只）执行全量数据提取
- 每只基金提取 12 项数据，与人工核对准确率 > 90%
- 缓存命中时提取时间 < 1 秒

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 不同基金公司年报格式差异大 | 高 | 设计兜底策略：解析失败显示"数据获取失败" | ⬜ 待验证 |
| 2026 新规"投资者收益率"尚未落地 | 中 | 先用份额变动估算，新规落地后切换 | ⬜ 待验证 |
| akshare API 不稳定 | 中 | 备选天天基金直接 API | ⬜ 待验证 |

**当前实现基线（2026-05-17）**

- 已有 `fund_agent/fund/pdf/downloader.py` 原型，可通过 akshare 查找公告并下载样本基金 `110011` 的 2024 年年报。
- 已有 `fund_agent/fund/pdf/parser.py` 原型，可提取全文文本、表格，并提供 `locate_sections()` / `extract_section()` 的初版章节定位能力。
- 当前章节定位尚不稳定：在样本基金 `110011` 上仅定位到 `§1/§2/§4/§5/§8/§9/§10`，漏掉 `§3`，还不能支撑后续 12 项结构化提取。
- 结构化数据提取模块、SQLite 缓存层和测试套件尚未落地。

**P1-S1 当前状态（2026-05-17）**

- `P1-S1 文档访问契约收口`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/documents/*` 已承载稳定公共契约与唯一仓库入口
  - `FundDocumentRepository.load_annual_report(...)` 不再向上层暴露本地 `Path`
  - `fund_agent/fund/pdf/downloader.py` 已明确降级为内部 helper，并去除目标年份缺失时的 silent fallback
  - downloader / adapter 中的同步阻塞调用已通过 `asyncio.to_thread(...)` 隔离
  - 相关测试命令 ` .venv/bin/python -m pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py ` 当前通过（`11 passed`）
- 当前 residual risks：
  - `P1-S2` owner：`parser.py` 章节定位原型仍未稳定，`§3` 漏识别尚未关闭
  - `P1-S3` owner：缓存根路径策略与 SQLite 物化尚未落地
  - 后续 phase owner：当前只支持 `annual_report`，未扩展到其它文档类型

**P1-S2 当前状态（2026-05-17）**

- `P1-S2 章节定位修复与 §3 冻结`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/pdf/section_catalog.py` 已承载 `§1/§2/§3/§4/§5/§8/§9/§10` 的标题规则和目录信号规则
  - `fund_agent/fund/pdf/parser.py` 已从硬编码字典改为消费配置化 catalog
  - `tests/fixtures/fund/pdf_sections/110011_2024_excerpt.txt` 已固定“目录行 + 正文行同名”的 `§3` 事实
  - `tests/fund/pdf/test_parser.py` 已覆盖：
    - 正文 `§3` 命中
    - 目录误判回归
    - `§1/§2/§3/§4/§8/§9/§10` 偏移单调递增
  - 验证命令 `.venv/bin/python -m pytest tests/fund/pdf/test_parser.py -q` 当前通过（`3 passed`）
- 当前 residual risks：
  - `P1-S3` owner：负向/边界测试仍偏少，可在缓存阶段一并补强
  - 后续样本回归 owner：`§5` 当前规则已存在，但 fixture 尚未覆盖
  - 后续样本回归 owner：`§3` 模式仍使用 `.*` 贪婪通配，需由更多样本决定是否收窄

**P1-S3 当前状态（2026-05-17）**

- `P1-S3 两级缓存与仓库内解析物化`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/documents/cache.py` 已提供 `AnnualReportDocumentCache`
  - `documents` 表与 `parsed_reports` 表已在 `documents` 层内部落地
  - parsed report 已物化到 `cache/documents/parsed_reports/*.json`
  - repository 已支持：
    - parsed report 缓存命中
    - 已记录 PDF 路径复用
    - `force_refresh=True` 穿透 parsed report 与 PDF 路径缓存
  - `tests/fund/documents/test_cache.py` 与 `tests/fund/documents/test_repository.py` 已覆盖缓存最小闭环
  - 验证命令 `.venv/bin/python -m pytest tests/fund/documents -q` 当前通过（`10 passed`）
- 当前 residual risks：
  - 后续性能优化 owner：缓存 `initialize()` 每次操作都会重复执行，当前正确但不够高效
  - 后续性能优化 owner：默认缓存实例不做复用，当前单仓库场景无正确性风险
  - 后续缓存治理 owner：缓存根目录仍使用相对路径，后续若要统一根路径策略再单独裁决

**P1-S4 当前状态（2026-05-17）**

- `P1-S4 基础画像与基金类型识别`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/fund_type.py` 已提供 6 类标准基金类型标签和 `FundTypeClassification`
  - `fund_agent/fund/extractors/models.py` 已提供 `EvidenceAnchor`、`ExtractedField`、`ProfileExtractionResult`
  - `fund_agent/fund/extractors/profile.py` 已落地：
    - `basic_identity`
    - `product_profile`
    - `benchmark`
    - `fee_schedule`
  - `extract_profile(report)` 已显式先调用 `classify_fund_type(report)`，再构造通用画像字段
  - `basic_identity.value` 已稳定包含：
    - `classified_fund_type`
    - `classification_basis`
  - `tests/fund/extractors/test_profile.py` 已覆盖：
    - 分类先于通用字段构造
    - 主动权益 / 增强指数 / 债券三类样本识别
    - 费率、基准、规模、经理 anchor 存在
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q` 当前通过（`4 passed`）
- 当前 residual risks：
  - 后续 extractor refactor owner：`fund_type.py` 与 `profile.py` 之间仍有部分字段 pattern 重复定义
  - 后续样本回归 owner：`index_fund` / `qdii_fund` / `fof_fund` 仍缺 fixture 与测试覆盖
  - 后续可维护性优化 owner：`_build_basic_identity()` 当前使用列表索引映射字段，后续若继续扩字段建议改为按名字组织

**P1-S5 当前状态（2026-05-17）**

- `P1-S5 §3 表现提取与投资者收益 fallback`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `PerformanceExtractionResult`
  - `fund_agent/fund/extractors/performance.py` 已落地：
    - `nav_benchmark_performance`
    - `investor_return`
  - `investor_return` 当前已稳定区分：
    - `direct`
    - `estimated`
    - `missing`
  - `tests/fund/extractors/test_performance.py` 已覆盖：
    - 净值增长率 / 基准收益率提取与 anchor
    - 投资者收益率直接披露路径
    - 投资者收益率估算披露路径
    - 投资者收益率未披露时显式 `missing`
    - `nav_benchmark_performance` 部分命中时显式保留 `missing`
  - `tests/fixtures/fund/extractors/performance/` 已固定最小 `§3` 文本夹具
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q` 当前通过（`5 passed`）
- 当前 residual risks：
  - 后续 fallback owner：当前 `estimated` 仅覆盖 `§3` 中显式标记“估算”的披露，不包含依赖 `§10` 或净值序列的后续 fallback
  - 后续集成测试 owner：`§3` 整体缺失路径仍需在真实样本矩阵或单独 fixture 中补强
  - 后续样本回归 owner：当前以最小文本夹具锁定三态输出，真实样本覆盖仍需在 `P1-S8` 验收矩阵阶段继续扩展

**P1-S6 当前状态（2026-05-17）**

- `P1-S6 管理人文本、换手率、利益一致性与持有人结构`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `ManagerOwnershipExtractionResult`
  - `fund_agent/fund/extractors/manager_ownership.py` 已落地：
    - `manager_strategy_text`
    - `turnover_rate`
    - `manager_alignment`
    - `holder_structure`
  - `manager_alignment.value["judgment"]` 当前固定为 `None`，确保 P1 只输出原始披露
  - `tests/fund/extractors/test_manager_ownership.py` 已覆盖：
    - 完整披露路径
    - 未披露 `missing` 路径
    - 部分披露路径
    - 换手率口径命中但数值缺失路径
    - 换手率与持有人信息 anchor
  - `tests/fixtures/fund/extractors/manager_ownership/` 已固定最小 `§4/§8/§9` 文本夹具
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_manager_ownership.py -q` 当前通过（`4 passed`）
- 当前 residual risks：
  - 后续样本回归 owner：真实年报 `§4/§8/§9` 可能使用表格或不同字段名称，需在 `P1-S8` 验收矩阵阶段继续扩展
  - 后续估算 owner：换手率未披露时的同类中位数估算尚未接入，当前只能显式返回 `missing`

**P1-S7 当前状态（2026-05-17）**

- `P1-S7 持仓快照与份额变动`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `HoldingsShareChangeExtractionResult`
  - `fund_agent/fund/extractors/holdings_share_change.py` 已落地：
    - `holdings_snapshot`
    - `share_change`
  - `tests/fund/extractors/test_holdings_share_change.py` 已覆盖：
    - 前十大重仓表
    - 行业分布表
    - 份额变动表
    - 行业分布缺失路径
    - 表格整体缺失路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_holdings_share_change.py -q` 当前通过（`3 passed`）
- 当前 residual risks：
  - 后续样本回归 owner：真实年报表头差异仍需在 `P1-S8` 验收矩阵阶段继续扩展
  - 后续 schema owner：当前表格行按原表头输出，最终标准字段名需在 façade 集成前裁决

**P1-S8 当前状态（2026-05-17）**

- `P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/data_extractor.py` 已落地：
    - `StructuredFundDataBundle`
    - `FundDataExtractor`
  - `fund_agent/fund/data/nav_data.py` 已落地：
    - `FundNavDataAdapter`
    - `NavDataResult`
    - `nav_cache` SQLite 表
  - `tests/fund/integration/test_p1_sample_matrix.py` 已覆盖 3 只样本基金 12 项矩阵，当前结果 `36/36`
  - `tests/fund/data/test_nav_data.py` 已覆盖净值缓存命中和强制刷新
  - 验证命令 `.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py -q` 当前通过（`32 passed`）
- 当前 residual risks：
  - 后续端到端 owner：当前 P1 矩阵使用 fake repository 和 fixture report，真实 PDF 样本矩阵需在端到端验证中继续扩展
  - 后续网络验证 owner：默认 akshare fetcher 已封装，本轮测试未访问真实网络

---

### P2: 分析引擎（R=A+B-C + 检验 + 审计）

**目标**

完成收益归因计算、言行一致性检验、投资者获得感分析、否决项检查、程序审计功能。

**进入条件**

- [ ] P1 退出条件全部满足
- [ ] 12 项关键数据可从缓存获取

**退出条件**

- [ ] `fund/analysis/r_abc.py` 能计算近 1/3/5 年 R=A+B-C 归因
- [ ] `fund/analysis/alpha_judge.py` 能区分结构性 vs 阶段性超额
- [ ] `fund/analysis/consistency_check.py` 能输出言行一致性 4 维度信号
- [ ] `fund/analysis/investor_return.py` 能计算行为损益
- [ ] `fund/analysis/risk_check.py` 能执行 5 项否决检查 + 压力测试
- [ ] `fund/analysis/checklist.py` 能输出 7 问题红/黄/绿灯
- [ ] `fund/audit/audit_programmatic.py` 能执行 P1/P2/P3/L1/R1/R2 规则检查
- [ ] `fund/template/renderer.py` 能将数据填充到定性模板 v2

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P2-S1 | 实现 R=A+B-C 计算模块 | 对样本基金计算，与手动计算一致 |
| P2-S2 | 实现超额收益性质判断 | 对已知基金判断结果合理 |
| P2-S3 | 实现言行一致性检验 | 对样本基金输出 4 维度信号 |
| P2-S4 | 实现投资者获得感分析 | 计算行为损益 + 资金流向判断 |
| P2-S5 | 实现否决项检查 | 5 项否决条件检查正确 |
| P2-S6 | 实现压力测试 | 模拟 -20%/-40%/-60% 场景 |
| P2-S7 | 实现检查清单引擎 | 7 问题输出红/黄/绿灯 |
| P2-S8 | 实现程序审计（P1/P2/P3/L1/R1/R2） | 能检测到故意注入的错误 |
| P2-S9 | 实现模板渲染器 | 输出 8 章报告 Markdown |
| P2-S10 | 实现证据锚点标注 | 每个数据标注来源 |

**验证要求**

- R=A+B-C 计算结果与手动计算误差 < 0.01%
- 程序审计能检测到以下注入错误：
  - 章节缺失（P1）
  - 关键字段为空（P2）
  - R=A+B-C 计算不闭合（L1）
  - 检查清单信号与规则不一致（R1）
- 模板渲染输出包含 8 章完整内容

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 业绩基准计算复杂（多指数加权） | 中 | MVP 先用简化计算，v2 精确实现 | ⬜ 待验证 |
| 超额收益性质判断主观性强 | 中 | MVP 用规则引擎（多年度为正 + 不同环境），v2 引入 LLM | ⬜ 待验证 |

---

### P3: CLI 入口 + 整合测试 + 验证

**目标**

完成 CLI 入口封装，整合所有功能，实现端到端验证。

**进入条件**

- [ ] P2 退出条件全部满足
- [ ] 单只基金分析可本地运行

**退出条件**

- [ ] `fund-analysis <fund_code>` 命令可用
- [ ] 输出完整 8 章分析报告（Markdown 格式）
- [ ] 报告通过程序审计
- [ ] 3 只样本基金端到端测试通过
- [ ] 单只基金分析时间 < 30 秒（不含 PDF 下载）
- [ ] 包含 README.md（安装 + 使用说明）
- [ ] 单元测试覆盖率 > 50%

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P3-S1 | CLI 入口封装（argparse） | `fund-analysis 110011` 输出报告 |
| P3-S2 | 温度计数据爬取（有知有行） | 能获取全市场和指数温度 |
| P3-S3 | 端到端整合测试 | 3 只样本基金完整流程 |
| P3-S4 | 程序审计集成 | 报告通过 P1/P2/P3/L1/R1/R2 |
| P3-S5 | 证据锚点集成 | 每个数据标注来源 |
| P3-S6 | 编写 README.md | 包含安装、使用、示例 |
| P3-S7 | 编写单元测试 | pytest 覆盖率 > 50% |
| P3-S8 | 性能优化 | 单只基金 < 30 秒 |

**验证要求**

- 端到端测试：输入 3 只样本基金代码，输出 3 份完整报告
- 每份报告包含 8 章内容 + 证据锚点
- 程序审计全部通过
- `pytest` 覆盖率 > 50%

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 有知有行页面结构变更 | 中 | 异常处理 + 24h 缓存 | ⬜ 待验证 |
| 整合测试发现数据层 bug | 高 | 预留 2 天 buffer | ⬜ 待验证 |

---

## 3. 依赖关系

```
P0（环境搭建）
  └── P1（数据层）
        └── P2（分析引擎）
              └── P3（整合测试）
```

- 所有 Phase 串行执行，无并行 Phase
- P1 内部的 Slice 可部分并行（P1-S4~P1-S7 在 P1-S3 被接受后可并行）
- P2 内部的 Slice 可部分并行（P2-S1~S7 与 P2-S8~S10 可并行）

---

## 4. 阻塞问题追踪

| ID | 问题 | 影响 Phase | 状态 | 决议 |
|----|------|-----------|------|------|
| BQ-1 | 巨潮网反爬策略未知 | P0/P1 | ✅ closed | 已改用 akshare + eastmoney PDF，无需直接访问巨潮 |
| BQ-2 | 2026 新规"投资者收益率"披露时间表 | P2 | ⬜ open | P1 已提供 `investor_return` 三态和 `share_change` 输入，P2 再实现行为损益 |
| BQ-3 | 有知有行温度数据页面结构 | P3 | ⬜ open | P3-S2 验证后关闭 |
| BQ-4 | akshare 基金净值 API 稳定性 | P1/P3 | 🟡 partially closed | P1-S8 已封装可注入 fetcher 与 `nav_cache`，真实网络验证移交 P3 |
| BQ-5 | 当前章节定位规则无法稳定识别 `§3` 正文 | P1 | ✅ closed | 已由 P1-S2 章节定位修复与 `§3` 冻结关闭 |

---

## 5. 残余风险追踪

| ID | 风险 | Phase | 缓解状态 | 需要人类裁决？ |
|----|------|-------|---------|--------------|
| RR-1 | PDF 格式不统一导致解析失败 | P1 | 已设计兜底策略 | 否 |
| RR-2 | 超额收益性质判断主观性强 | P2 | MVP 用规则引擎 | 否 |
| RR-3 | 审计规则过严导致频繁阻断 | P2 | MVP 仅启用程序审计 | 否 |
| RR-4 | 温度计爬虫被封锁 | P3 | 24h 缓存 + 异常处理 | 是（如被封锁需人工确认） |
| RR-5 | `dayu-agent` wheel 下载受 GitHub 可达性影响 | P0/P1 | 当前虚拟环境已安装，可继续开发；新环境安装待镜像化或替代分发方案 | 否 |

---

## 6. 后续迭代（非 MVP 范围）

### v2（Week 6-9）

| 功能 | 说明 |
|------|------|
| 严选基金池内横向比较 | 同类型基金择优 |
| LLM 审计 | 证据充分性（E1/E2/E3）+ 内容合规性（C1/C2） |
| 证据复核 | 对 E1/E2 类违规执行二次确认（supported/confirmed_missing） |
| 修复闭环 | patch（局部修补）+ regenerate（整章重建）+ 锚点重写 |
| LLM 写作 | 从模板填充升级为 LLM 生成差异化分析 |

### v3（Week 10-13）

| 功能 | 说明 |
|------|------|
| 组合管理 | 再平衡引擎 + 目标市值策略 |
| 温度计自建 | AKShare + 自行计算 PE/PB 百分位 |
| Web UI | FastAPI + 前端 |
| 微信入口 | 微信消息适配 |

---

## 7. 状态更新日志

| 日期 | Phase | 状态变更 | 备注 |
|------|-------|---------|------|
| 2026-05-16 | 全部 | 创建 | 初始版本 |
| 2026-05-17 | P0 | ✅ done | 全部退出条件满足；项目更名为 fund-agent；数据源改用 akshare + eastmoney |
| 2026-05-17 | P1 | 🟡 in progress | 完成 Git 基线初始化与 baseline reconciliation；下一 gate 为 P1 plan |
| 2026-05-17 | P1 | 🟡 in progress | P1 计划通过 re-review；accepted artifacts 为 `docs/reviews/p1-plan-2026-05-17.md`、`docs/reviews/p1-plan-review-2026-05-17.md`；下一 gate 为 `P1-S1 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S5` code review / fix / re-review 已收口，accepted slice commit=`8102944`；下一 gate 为 `P1-S6 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` implementation 已完成，`§4/§8/§9` 管理人/持有人 extractor 与测试已落地；当前 gate 维持 `P1-S6 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` controller review 已通过；下一 gate 为 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` 已接受，accepted commit 为 `18566f9`；下一 gate 为 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` implementation 已完成，`§8/§10` 持仓/份额 extractor 与测试已落地；当前 gate 维持 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` controller review 已通过；下一 gate 为 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` 已接受，accepted commit 为 `3167754`；下一 gate 为 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` implementation 已完成，façade、净值适配器与 `36/36` 样本矩阵已落地；当前 gate 维持 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` controller review 已通过；下一 gate 为 `P1 aggregate review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` 已接受，accepted commit 为 `d398bc2`；下一 gate 为 `P1 aggregate review` |
| 2026-05-17 | P1 | ✅ done | P1 aggregate review 通过，artifact 为 `docs/reviews/p1-aggregate-review-2026-05-17.md`；下一 gate 为 `P2-S1 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | 进入 `P2-S1 implementation + review`，优先实现 R=A+B-C 计算模块 |
