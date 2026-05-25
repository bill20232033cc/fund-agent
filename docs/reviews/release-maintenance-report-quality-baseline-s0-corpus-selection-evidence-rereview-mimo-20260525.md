# Release Maintenance Report-Quality Baseline S0 Corpus-Selection Evidence Re-Review (MiMo)

> Date: 2026-05-25
> Reviewer: AgentMiMo
> Gate: `report-quality-baseline S0 corpus-selection evidence`
> Review target: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md`（Codex 补丁后版本）
> Original review: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-review-mimo-20260525.md`
> Scope: Re-review only；不改文件，不 commit，不 push，不 PR。

## Verdict

**PASS**

Codex 补丁解决了原 review 的核心 material finding（F-1），并改进了两个技术描述准确性（async load_annual_report、DocumentKey repr）。原 F-3/F-4 minor findings 保留为 S1/S2 residual，不阻塞 controller judgment。

## Original Findings Disposition

### F-1 [Material] Fallback 记录缺少原始 failure category — 已解决

**原问题**: `110020`、`017641`、`017970` 三条 fallback 记录的 `source failure category` 为 `n/a`，违反 AGENTS.md 原始 failure category 必须保留的硬约束。

**补丁内容**:

1. `source failure category` 列从 `n/a` 改为 `unknown_upstream_failure_category`（lines 42, 45, 47）。
2. `repository verification status` 列新增说明："repository metadata only preserves fallback source/result, not original upstream failure category in this S0 probe"。
3. `017970` 行的 `source failure category` 改为 `data_gap; unknown_upstream_failure_category for fallback source`（line 47），同时标注了 fallback 上游失败类别未知。
4. Open Gaps 表（line 108）的 "Required next handling" 从被动建议升级为 S1 entry gate 前置条件："before durable baseline selection, source boundary / source reliability evidence must recover the original upstream failure category, or the fallback candidate must be excluded from the durable baseline corpus"。

**复核判定**: 已解决。S0 能做的最佳处理是：(a) 显式标记原始 failure category 未知而非静默 `n/a`；(b) 将恢复原始 category 或排除 fallback 候选提升为 S1 entry gate 前置条件。两者均已实现。原始 failure category 的实际恢复需要从 repository probe JSONL 中提取或重跑 source verification，这超出 S0 evidence scope。

### F-2 [Material] QDII-FOF classifier precedence — 不在 S0 补丁 scope 内

**原问题**: §6.5 基金类型识别规则未显式处理 QDII+FOF 混合类型。

**复核判定**: 未变更，也不需要在 S0 artifact 中解决。S0 artifact 正确记录了 observed behavior 和 `data_gap`。此问题属于 design.md §6.5 的独立 residual，应由 fund-type taxonomy gate 处理。原 review 建议 disposition 不变。

### F-3 [Minor] Review state transition 未覆盖异常/回退路径 — 保留

**复核判定**: 未变更。Forward transitions 定义完整，回退/terminal states 仍为 S1/S2 residual。不阻塞。

### F-4 [Minor] `rg` 验证命令 scope 过于宽泛 — 保留

**复核判定**: `rg` 命令新增了 `asyncio.run|unknown_upstream_failure_category|durable baseline selection` 三个关键词（line 116），scope 略有扩大但验证逻辑不变。仍未使用 `-c` 计数或上下文验证。Minor，不阻塞。

## Codex 额外改进（非 findings，但值得记录）

### 改进 1: async load_annual_report 描述

**位置**: Step Self-Check（line 32）

**变更**: 从 `FundDocumentRepository().load_annual_report(code, year, force_refresh=False)` 改为 "async repository access: the probe enters an async context through `asyncio.run(...)` and then awaits `FundDocumentRepository().load_annual_report(code, year, force_refresh=False)`"。

**评价**: 正确。`load_annual_report` 是 async 方法，原始描述省略了 async context 可能误导 reader 认为是同步调用。改进后技术描述准确。

### 改进 2: DocumentKey repr 格式化

**位置**: candidate table（lines 41-47）

**变更**: 所有 `DocumentKey(fund_code=004393, year=2024, annual_report)` 改为 `DocumentKey(fund_code="004393", year=2024, document_kind="annual_report")`。

**评价**: 正确。加了 fund_code 的字符串引号，`annual_report` 改为显式 `document_kind="annual_report"` 关键字参数。更贴近 dataclass 实际 repr。

## Residuals（继承自原 review，不变）

| # | Residual | Owner / Gate |
|---|---|---|
| 1 | Fallback 原始 failure category 需从 probe JSONL 恢复或 source verification 重跑 | S1 entry gate precondition |
| 2 | §6.5 QDII-FOF 混合类型分类策略需显式裁决 | 独立 fund-type taxonomy gate |
| 3 | Review state machine 需 terminal states（rejected / deferred / expired） | S1/S2 state machine 扩展 |
| 4 | `110020` 的 `fallback_used=True` + Eastmoney 来源是否符合 index_fund 首选策略 | S1 source gate |

## Required Fixes Before Controller Acceptance

无。

## Recommendation

**建议进入 controller judgment。**

Codex 补丁有效解决了 F-1 material finding，将 fallback 原始 failure category 从静默 `n/a` 改为显式 `unknown_upstream_failure_category` 并提升为 S1 entry gate 前置条件。技术描述改进（async、DocumentKey repr）增加了 artifact 准确性。原 minor findings（F-3、F-4）保留为 S1/S2 residual，不阻塞。F-2 不在 S0 scope 内，disposition 不变。S0 artifact 现在满足 controller judgment 条件。
