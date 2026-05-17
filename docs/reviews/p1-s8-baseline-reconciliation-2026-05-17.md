# P1-S8 基线对账裁决

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵
> 分支：`chore/reconcile-baseline`
> 当前 gate：`P1-S8 implementation + review`
> 上一 accepted slice commit：`3167754` (`gateflow: accept P1 P1-S7`)

## 1. 当前入口

- `docs/implementation-control.md` 当前 gate 已推进到 `P1-S8 implementation + review`。
- `docs/reviews/p1-plan-2026-05-17.md` 要求本 slice：
  - 实现 `data_extractor.py` façade
  - 接入 `fund_agent/fund/data/nav_data.py`
  - 收口 `structured_data` 缓存
  - 跑完 3 只样本基金 36 格矩阵，至少 `33/36` 通过

## 2. 当前基线事实

- 已有稳定文档入口：
  - `FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`
- 已有 extractor：
  - `extract_profile(report)`
  - `extract_performance(report)`
  - `extract_manager_ownership(report)`
  - `extract_holdings_share_change(report)`
- 当前尚未存在：
  - `fund_agent/fund/data_extractor.py`
  - `fund_agent/fund/data/nav_data.py`
  - `StructuredFundDataBundle`
  - `tests/fund/integration/test_p1_sample_matrix.py`

## 3. 范围裁决

### Allowed files/modules

- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/extractors/**`
- `tests/fund/integration/test_p1_sample_matrix.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

### 禁止触碰

- UI / Service / Engine / Runtime / CLI
- `fund_agent/fund/analysis/**`
- `docs/design.md`

## 4. 输出契约裁决

- `data_extractor.py`
  - 只做 orchestration
  - 不直接读文件
  - 不直接写缓存
  - 通过 `FundDocumentRepository` 读取年报
  - 聚合已接受 extractor 输出为 `StructuredFundDataBundle`
- `nav_data.py`
  - 提供可注入 fetcher 的净值数据适配器
  - 自身负责 `nav_cache` SQLite 表
  - 测试不得依赖真实网络
- P1 验收矩阵
  - 以 3 只样本基金为行，12 项结构化数据为列
  - 本 slice 使用 fake repository / fixture report 锁定 36 格至少 `33/36` 可用

## 5. Root Cause 裁决

`P1-S8` 当前要关闭的是 extractor 已分散落地但尚未形成稳定 P1 数据出口的问题：

1. 上层仍无法通过单一 façade 获取 12 项结构化数据。
2. 净值数据尚未有 capability 层适配器与缓存边界。
3. P1 的 36 格验收矩阵尚未自动化，无法对前序 slice 做整体回归。

## 6. 当前结论

- baseline reconciliation 结论：`pass`
- `P1-S8` 可以进入 implementation
- 若实现需要反改 `P1-S1 ~ P1-S3` 已冻结契约，必须停止并重新裁决。
