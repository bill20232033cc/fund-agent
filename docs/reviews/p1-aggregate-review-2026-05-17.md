# P1 Aggregate Review

> 日期：2026-05-17
> Controller：Codex
> Phase：P1 数据层（PDF 下载 + 解析 + 提取）
> 当前分支：`chore/reconcile-baseline`

## 1. Review Scope

P1 覆盖以下 accepted slices：

- `P1-S1` 文档访问契约收口
- `P1-S2` 章节定位修复与 `§3` 冻结
- `P1-S3` 两级缓存与仓库内解析物化
- `P1-S4` 基础画像与基金类型识别
- `P1-S5` `§3` 表现提取与投资者收益 fallback
- `P1-S6` 管理人文本、换手率、利益一致性与持有人结构
- `P1-S7` 持仓快照与份额变动
- `P1-S8` façade 集成、净值数据适配器与 P1 验收矩阵

## 2. Accepted Commits

- `P1-S1`: `e772dae`
- `P1-S2`: `c3bd264`
- `P1-S3`: `d92eef7`
- `P1-S4`: `22a1a7a`
- `P1-S5`: `8102944`
- `P1-S6`: `18566f9`
- `P1-S7`: `3167754`
- `P1-S8`: `d398bc2`

## 3. Contract Review

### 文档访问

- 对外统一入口为 `FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`
- 上层不直接消费本地 PDF `Path`
- `fund_agent/fund/pdf/**` 维持底层 helper / adapter 定位

### 结构化数据

- 当前 `StructuredFundDataBundle` 已聚合 P1 12 项数据：
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
- `FundDataExtractor` 只做 orchestration，不直接读文件、不直接写缓存。
- `FundNavDataAdapter` 独立负责净值数据和 `nav_cache`。

### 边界检查

- 未引入 UI / Service / Engine / Runtime / CLI 改动。
- 未进入 `fund_agent/fund/analysis/**`。
- P1 extractor 只输出原始披露或 missing/estimated 状态，不做 P2 分析判断。

## 4. Validation

执行命令：

```bash
.venv/bin/python -m pytest -q
```

结果：

```text
38 passed
```

P1-S8 样本矩阵：

```text
3 只样本基金 × 12 项结构化数据 = 36/36
```

## 5. Residual Risks

### R1-真实 PDF 样本矩阵仍需端到端验证

- **状态**：deferred
- **Owner / Destination**：P3 end-to-end validation
- **说明**：P1-S8 使用 fake repository 锁定 façade contract，真实 PDF 下载、解析、提取链路应在端到端验证中跑完整样本。

### R2-真实年报格式异构仍需扩展样本

- **状态**：deferred
- **Owner / Destination**：P3 / later extractor hardening
- **说明**：当前各 extractor 以最小 fixture 锁定状态机、anchor 和边界，真实年报中的表格差异、字段命名差异仍需持续扩展回归。

### R3-akshare 真实网络稳定性未在单测中验证

- **状态**：deferred
- **Owner / Destination**：P3 external integration validation
- **说明**：P1 已封装可注入 fetcher 和 `nav_cache`，单测不依赖真实网络；真实网络验证移交端到端阶段。

### R4-`structured_data` 未 SQLite 物化

- **状态**：accepted residual
- **Owner / Destination**：later cache governance
- **说明**：当前已通过 `StructuredFundDataBundle` 冻结数据出口。SQLite 物化需要额外缓存失效策略，本阶段不为未来设计预写表。

## 6. Conclusion

- `P1 aggregate review` 结论：`pass`
- P1 可标记为 `done`
- 下一 gate：`P2-S1 implementation + review`
