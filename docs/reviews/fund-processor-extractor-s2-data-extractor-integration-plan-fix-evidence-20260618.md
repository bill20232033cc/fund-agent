# Fund Processor/Extractor S2 DataExtractor Integration Plan Fix Evidence

> Date: 2026-06-18
> Role: AgentDS plan fix worker
> Work unit: Fund Processor/Extractor S2 DataExtractor Integration Planning Gate
> Gate: S2 plan fix gate after plan review
> Artifact status: fix evidence only, not implementation

## Fix Summary

对 `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md` 实施了 6 项 controller 要求的 plan 修复。所有修复均限定在允许写入集内（plan artifact + 本 evidence artifact），未修改源文件、测试、control docs、design docs。

## Fix 1: core_risk.v1 与 current_stage.v1 投影规则澄清

**来源**: MiMo F1 (blocking) + DS Finding 5 (nonblocking, overlapping)

**修改**: 重写 `core_risk.v1` 投影规则，明确：
- 仅 `risk_characteristic_text` 可作为 fallback，触发条件为 `product_essence.v1` 同名字段 `extraction_mode == "missing"` 且 `core_risk.v1` 有 public value
- `holder_structure`、`turnover_rate`、`holdings_snapshot`、`tracking_error` 在 `core_risk.v1` 中为 informational/redundant，不得隐式合并到其他 bundle 字段
- 新增 `current_stage.v1` 条目，标注为 informational/redundant，S2 不单独从中投影 bundle 字段

**证据**: active_annual.py:170-189 确认 `core_risk.v1` 的 5 个字段全部与 primary family 重复；active_annual.py:156-169 确认 `current_stage.v1` 的 4 个字段也已由 primary family 拥有。

## Fix 2: processor.extract() 意外异常契约

**来源**: MiMo F2 (blocking)

**修改**: 在 Fail-closed Rules 中新增条目：
- `processor.extract()` 内部非预期异常必须向上抛出或由 implementation worker 显式转换为 typed fail-closed error
- 不得静默吞掉异常
- 不得 fallback 到 direct extractor path 为 active_fund 组装 bundle
- Repository failure 传播与 NAV 降级语义保持不变

**证据**: contracts.py:365-376 的 `FundProcessorProtocol.extract()` 协议已允许实现抛出 `ValueError`；active_annual.py:233-290 当前 `extract()` 实现已通过 `_blocked_result()` 处理已知 fail-closed 路径，但窄 extractor 的意外异常（TypeError/KeyError/AttributeError）当前未被显式捕获。本修复补充了该契约缺口。

## Fix 3: source_kind 派生规则

**来源**: DS Finding 1 (nonblocking) + MiMo F5 (nonblocking, overlapping)

**修改**: 将 dispatch key 构造中的 `source_kind=<public source kind>` 占位符替换为确定性静态值 `"annual_report"`，并明确：
- 不得从 candidate status 派生
- 不得从 `PublicSourceProvenance.selected_source` 或 fallback 状态派生
- 不得在 S2 production façade 中使用 candidate source kind

**证据**: contracts.py:104 定义 `source_kind: str` 无运行时验证；design.md evidence anchor 允许 `annual_report`、`external_api`、`derived`。S2 的 ParsedAnnualReport 年报生产路径属于 `annual_report`。

## Fix 4: active fund processor 归属验证测试策略

**来源**: DS Finding 6 (nonblocking)

**修改**: 增强必测清单中 active fund 测试条目，要求至少一个测试通过注入自定义 registry（返回已知特殊 marker 值的 processor）来证明 active 字段确实来自 processor 输出，而非仅因 direct extractor 值相等而通过。

**证据**: registry.py:65-100 的 `register()` 方法支持注入任意 processor；测试可通过注入 marker processor 验证 bundle 字段携带 marker 值而非 direct extractor 默认值。plan 原条目仅要求 "returns the same public bundle fields"，无法区分 processor 路径与 direct 路径。

## Fix 5: 非 active 非 bond 冒烟测试推荐

**来源**: DS Finding 7 (needs-more-evidence)

**修改**: 在必测清单中：
- 标注 bond fund 测试为必测
- 新增推荐条目：至少一种非 active 非 bond 类型（如 `index_fund`）的 direct path 冒烟测试；若 fixture 不足以支持则记录为 residual，不作为阻塞条件

**证据**: plan 第 137-153 行的 Non-active Fund Path 要求保留 index/enhanced/bond/qdii/fof/unclassified 五种类型的 direct path，但原必测清单仅覆盖 bond。本修复补齐了覆盖缺口。

## Fix 6: 约束保留验证

**验证项** (未修改，逐项确认):

| 约束 | 状态 | 证据位置 |
|------|------|----------|
| NOT_READY 边界 | 保持 | plan line 9, 26-31, 226-233, 235-243 |
| Candidate-only | 保持 | plan line 132-133, 159 |
| No parser replacement | 保持 | plan line 27, 176-190 (forbidden write set) |
| Exact write set | 保持 | plan line 163-190 |
| No-live 命令约束 | 保持 | plan line 217 |
| FundDocumentRepository 边界 | 保持 | plan line 19, 28-29, 56, 73 |
| NAV 降级语义 | 保持 | plan line 157 |
| Repository failure 传播 | 保持 | plan line 156 |

## Validation

```
$ git diff --check -- docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md
(no output — whitespace clean)

$ git diff --check -- docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-fix-evidence-20260618.md
(no output — whitespace clean)
```

Diff 确认仅修改 plan artifact 的 5 处位置，无意外变更，允许写入集外的零文件被修改。

## Stop Condition

本 fix gate 在此停止。不实现代码、不修改源文件/测试/control docs/design docs、不提交、不推送、不打开 PR、不进入 implementation。
