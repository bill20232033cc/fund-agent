# P1-S8 Implementation Artifact

> 日期：2026-05-17
> gate：`P1-S8 implementation`
> slice：`P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵`
> 分支：`chore/reconcile-baseline`

## Scope / Non-Goals

### Scope

- 实现 `data_extractor.py` façade，聚合 P1 已接受 extractor。
- 实现 `fund_agent/fund/data/nav_data.py` 净值数据适配器与 `nav_cache`。
- 用 3 只样本基金的 12 项矩阵验证 P1 数据出口。

### Non-Goals

- 不触碰 UI / Service / Engine / Runtime / CLI。
- 不进入 `fund_agent/fund/analysis/**`。
- 不实现 P2 分析、判断或审计规则。
- 不在测试中依赖真实网络。

## Changed Files

- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data/__init__.py`
- `tests/fund/data/test_nav_data.py`
- `tests/fund/integration/test_p1_sample_matrix.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Implemented Items

1. 新增 `StructuredFundDataBundle`
   - 承载 P1 12 项结构化数据：
     - `basic_identity`
     - `product_profile`
     - `benchmark`
     - `fee_schedule`
     - `turnover_rate`
     - `nav_benchmark_performance`
     - `investor_return`
     - `share_change`
     - `manager_alignment`
     - `manager_strategy_text`
     - `holdings_snapshot`
     - `holder_structure`
   - 同时携带 `fund_code`、`report_year`、`nav_data`
2. 新增 `FundDataExtractor`
   - 只做 orchestration
   - 通过 repository 加载 `ParsedAnnualReport`
   - 通过 nav provider 加载净值数据
   - 聚合已接受 extractor 输出
   - 不直接读文件、不直接写缓存
3. 新增 `FundNavDataAdapter`
   - 支持注入 `fetcher`
   - 默认 fetcher 使用 akshare
   - 自身维护 `nav_cache` SQLite 表
   - `force_refresh=True` 会绕过缓存重新 fetch
4. 新增 P1 集成矩阵测试
   - `tests/fund/integration/test_p1_sample_matrix.py`
   - 使用 3 只样本基金：
     - `110011`
     - `510300`
     - `000171`
   - 12 项矩阵结果：`36/36`
5. 新增净值缓存测试
   - `tests/fund/data/test_nav_data.py`
   - 覆盖缓存命中与强制刷新

## Boundary Closure

- façade 只依赖 `FundDocumentRepository` 协议与 nav provider 协议，不直接打开文件或写缓存。
- 净值缓存写入只发生在 `FundNavDataAdapter` 内部。
- `structured_data` 当前以 `StructuredFundDataBundle` dataclass 冻结输出契约，SQLite 物化留待后续明确缓存治理需求时单独实现。

## Validation

执行命令：

```bash
.venv/bin/python -m pytest tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py -q
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py -q
```

结果：

```text
3 passed
32 passed
```

## Residual Risks

### Fixed Later Slice

- 当前 P1 样本矩阵使用 fake repository 和 fixture report 锁定 façade contract；真实 PDF 样本矩阵仍需在后续端到端验证中接入。
- `FundNavDataAdapter` 默认 akshare fetcher 已封装，但本轮测试不访问真实网络。

### Later Phase

- P2 才会消费 `StructuredFundDataBundle` 做 R=A+B-C、言行一致性和审计判断。

### User Decision

- 无。

## Completion Status

- `P1-S8` implementation completion signal：`reached`
- 判断依据：
  - façade 已输出 P1 12 项结构化数据
  - 净值适配器已具备独立缓存
  - 3 样本 36 格矩阵达到 `36/36`
  - P1 全量测试通过
