# Code Review

## Scope

- Mode: all repository
- Branch: `main`
- Base: 不适用（全仓模式）
- Output file: `docs/reviews/agentglm-repo-deepreview-20260523.md`
- Review date: 2026-05-23
- Included scope:
  - 生产代码：`fund_agent/`（UI / Service / Capability / Config 四层）
  - 测试代码：`tests/`
  - 关键设计文档：`AGENTS.md`、`CLAUDE.md`、`docs/design.md`、`docs/implementation-control.md`、`docs/fund-analysis-template-draft.md`
  - 项目配置：`pyproject.toml`
- Excluded scope:
  - `.venv/`（第三方依赖）
  - `cache/`（运行时缓存数据）
  - `zhixing-agent/`（历史研究参考，非生产依赖）
  - `docs/reviews/` 中的历史 review artifact（非生产代码）
  - `docs/20260430/`（历史研究笔记）
  - `.github/`、`.pytest_cache/`、`.ruff_cache/`（CI/缓存配置）
- Parallel review coverage: 无，主 reviewer 直接走读
- Covered areas:
  - UI 层：`fund_agent/ui/cli.py`（完整走读）
  - Service 层：`fund_agent/services/` 7 个服务（`fund_analysis_service.py`、`thermometer_service.py` 完整走读，其余 5 个服务按契约接口抽查）
  - Capability analysis 层：`r_abc.py`、`checklist.py`、`final_judgment.py`、`risk_check.py`、`valuation_state.py`、`thermometer_calculator.py`（完整走读）
  - Capability audit 层：`audit_programmatic.py`（完整走读）
  - Capability data 层：`thermometer.py`、`thermometer_source.py`、`thermometer_types.py`（完整走读）
  - Capability documents 层：`repository.py`、`sources.py`（完整走读）
  - Capability data_extractor façade：`data_extractor.py`（完整走读）
  - Config 层：`paths.py`（抽查）
- Partially covered areas:
  - Capability extractors：`profile.py`、`performance.py`、`holdings_share_change.py`、`manager_ownership.py`（按接口契约抽查，未逐行走读内部解析逻辑）
  - Capability template：`renderer.py`（前 100 行走读，渲染逻辑抽查）、`contracts.py`、`item_rules.py`、`lens_application.py`、`chapter_blocks.py`（按接口契约抽查）
  - Service 层其余 5 个服务：`extraction_snapshot_service.py`、`extraction_score_service.py`、`quality_gate_service.py`、`golden_prefill_service.py`、`golden_answer_service.py`（按公共契约抽查）
  - PDF 层：`downloader.py`、`parser.py`、`section_catalog.py`（未走读）
  - Capability documents cache 层：`cache.py`、`models.py`、`adapters/annual_report_pdf.py`（未走读）
- Not-covered areas:
  - `fund_agent/fund/pdf/`（PDF 下载和解析）
  - `fund_agent/fund/documents/cache.py`（文档缓存实现）
  - `fund_agent/fund/documents/adapters/annual_report_pdf.py`（PDF 适配器内部实现）
  - `scripts/`（辅助脚本）
  - `tests/` 内部实现细节（仅确认 537 passed 全绿）
  - `docs/` 中非关键文档（研究笔记、审计输入、更新草案等）

---

## Findings

### F-01-未修复-[中]-Service 层穿透 Capability data 层缓存和来源内部实现

- **入口/函数**: `ThermometerService.__init__`
- **文件(行号)**: `fund_agent/services/thermometer_service.py:24-25`、`fund_agent/services/thermometer_service.py:144-145`
- **输入场景**: `ThermometerService` 默认构造时的任何温度计查询调用
- **实际分支**: 默认工厂路径
- **预期行为**: Service 层通过 Protocol 接口或 Capability 公共入口依赖 Capability，不直接实例化 Capability data 层的内部缓存类和数据源类。AGENTS.md 模块边界规定 "Service 层不负责具体工具实现……可调用 Capability，不直接读取年报文件/PDF/缓存"。
- **实际行为**: `ThermometerService` 直接 `from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache` 和 `from fund_agent.fund.data.thermometer_source import AkshareIndexThermometerSource`，并在 `__init__` 中将它们作为默认值实例化。Service 层与 Capability data 层的具体缓存策略和数据源实现形成了紧耦合。
- **直接证据**:
  - `thermometer_service.py:24`: `from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache`
  - `thermometer_service.py:25`: `from fund_agent.fund.data.thermometer_source import AkshareIndexThermometerSource`
  - `thermometer_service.py:144`: `self._index_source = index_source or AkshareIndexThermometerSource()`
  - `thermometer_service.py:145`: `self._history_cache_factory = history_cache_factory or ThermometerHistoryCache`
- **影响**: 若 Capability data 层重构缓存格式（如从 JSON 迁移到 parquet）或更换数据源实现（如替换 akshare），Service 层需要同步修改 import 路径和默认实例化逻辑。当前 Service 已经定义了 `_IndexThermometerSource` 和 `_ThermometerHistoryCacheFactory` Protocol，但默认值绑定在具体实现上，破坏了 Protocol 带来的解耦。
- **建议改法和验证点**: 将默认实例化逻辑移到 Capability 层的公共工厂函数（如 `fund_agent.fund.data.make_default_index_source()` 和 `fund_agent.fund.data.make_default_history_cache_factory()`），Service 层只 import 工厂函数而不 import 具体类。验证点：确认 Service 层不再出现 `from fund_agent.fund.data.thermometer_cache import ...` 或 `from fund_agent.fund.data.thermometer_source import ...`。
- **修复风险（低）**: 纯粹的重构，不改变任何运行时行为；Protocol 接口已经就位，只需把默认值绑定从 Service 移到 Capability 工厂。
- **严重程度（中）**: 维护性问题。当前不导致运行时错误，但违反了 AGENTS.md 模块边界约束，增加了后续 Capability data 层独立演进的耦合成本。

---

### F-02-未修复-[低]-_load_index_batch 串行执行独立异步 I/O 操作

- **入口/函数**: `ThermometerService._load_index_batch`
- **文件(行号)**: `fund_agent/services/thermometer_service.py:187-189`
- **输入场景**: CLI 传入 `--index 000300,000905` 批量查询两个指数温度
- **实际分支**: 批量路径 `len(index_codes) > 1`
- **预期行为**: N 个独立指数温度计查询应并行发起，总延迟等于最慢单次查询延迟。
- **实际行为**: `[await self._load_index_reading(request, index_code) for index_code in index_codes]` 使用列表推导式串行 await，总延迟等于所有查询延迟之和。每个 `_load_index_reading` 可能涉及网络 I/O（akshare 数据源）或磁盘 I/O（JSON 缓存读写），批量查询时延迟线性增长。
- **直接证据**: `thermometer_service.py:187-189`:
  ```python
  readings = tuple(
      [await self._load_index_reading(request, index_code) for index_code in index_codes]
  )
  ```
- **影响**: 批量查询时延迟不必要地线性叠加。当前支持的最大批量为 2 个指数（沪深300 和中证500），实际影响有限；若后续扩展支持更多指数，影响会放大。
- **建议改法和验证点**: 替换为 `await asyncio.gather(*[self._load_index_reading(request, code) for code in index_codes])`，用 `asyncio.gather` 并行发起独立查询。验证点：确认批量查询两个指数时网络请求是并行的；现有测试不需要修改因为 mock 不测延迟。
- **修复风险（低）**: `asyncio.gather` 语义等价，不改变返回顺序；需注意 `_load_index_reading` 内部的 `cache.save` 是否有并发写入同一缓存文件的风险——当前每个指数有独立缓存文件，不存在冲突。
- **严重程度（低）**: 静态可证明的性能问题——N 个独立异步 I/O 操作串行执行而非并行。当前 N=2 影响有限，但属于可纠正的模式缺陷。

---

## Open Questions

- **OQ-01**: `fund_agent/fund/pdf/`（PDF 下载器、解析器、章节目录）未在本次 review 中走读。PDF 解析是 P1 结构化抽取的上游依赖，解析边界条件（空页、异常表格、中文编码）可能隐藏 correctness 问题。后续 review 应优先覆盖。
- **OQ-02**: `fund_agent/fund/documents/cache.py` 和 `fund_agent/fund/documents/adapters/annual_report_pdf.py` 未走读。文档缓存的 schema 版本管理和迁移安全性、PDF 适配器对异常年报的处理逻辑未验证。
- **OQ-03**: `fund_agent/fund/extractors/` 下的 5 个 extractor（profile、performance、holdings_share_change、manager_ownership、models）的内部解析逻辑未逐行走读。抽取器是 P1 数据质量的关键来源，特别是 `performance.py` 中的净值增长率和基准收益率解析对 R=A+B-C 计算有直接影响。
- **OQ-04**: `fund_agent/fund/template/renderer.py` 只走了前 100 行和接口契约，8 章模板填充的具体逻辑（特别是条件型段落的渲染和证据锚点的插入）未完整验证。

## Residual Risk

- **RR-01（测试覆盖缺口）**: 537 个测试全部通过，但测试主要覆盖 Capability analysis 层的计算逻辑、检查清单、审计规则和温度计计算。Service 层编排逻辑的集成测试依赖 mock/fake，未覆盖真实 PDF 下载和网络 I/O 的 failure paths（超时、重试耗尽、schema 漂移等）。PDF 解析和章节抽取的错误路径（异常 PDF 结构、缺失章节）测试覆盖程度未知。
- **RR-02（外部数据源依赖）**: 生产主链路依赖 akshare（温度计 PE/PB 数据）、EID/证监会披露平台（年报 PDF）、Eastmoney/天天基金（年报 PDF fallback）。这些外部数据源的可用性、schema 稳定性和响应格式变化不在代码控制范围内。当前代码已有 fail-closed 处理（温度计 unavailable、年报来源 fallback 阻断），但极端情况（如 akshare 接口返回合法但数值异常的数据）的防护依赖于 `_validate_values` 的正值检查，未覆盖所有数值异常场景。
- **RR-03（未走读区域）**: PDF 下载器/解析器、文档缓存、年报适配器、extractor 内部逻辑、template 渲染器完整逻辑这五个区域未在本次 review 中覆盖。这些区域是 P1 数据质量的直接决定因素，后续应安排专项 review。
