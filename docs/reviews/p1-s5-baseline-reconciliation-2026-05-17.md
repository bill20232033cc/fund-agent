# P1-S5 基线对账裁决

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S5 `§3` 表现提取与投资者收益 fallback
> 分支：`chore/reconcile-baseline`
> 当前 gate：`P1-S5 implementation + review`
> 上一 accepted slice commit：`22a1a7a` (`gateflow: accept P1 P1-S4`)

## 1. 触发原因

- `docs/implementation-control.md` 当前 next entry point 已切到 `P1-S5 implementation + review`。
- `docs/reviews/p1-plan-2026-05-17.md` 第 8.2 节要求 `P1-S5` 先落地：
  - `nav_benchmark_performance`
  - `investor_return`
- 同时必须满足：
  - `110011` 的 `§3` 能提取净值增长率与业绩基准收益率
  - 投资者收益率若未披露，必须返回 `estimated` 或 `missing`
  - 所有数值字段都带 anchor 或明确 `derived` 来源

## 2. 当前工作树状态

当前 `git status --short` 仅剩无关未跟踪项：

```text
?? docs/reviews/code-review-20260517-0727.md
?? scripts/
```

裁决：

- 这两项不纳入 `P1-S5` 范围
- 当前可以安全基于 `HEAD=9ba4ea3` 继续推进

## 3. 代码基线事实

### 3.1 当前 fund capability 现状

当前 `fund_agent/fund/` 中与 `P1-S5` 直接相关的稳定事实：

- 已有：
  - `fund_agent/fund/extractors/models.py`
  - `fund_agent/fund/extractors/profile.py`
  - `fund_agent/fund/fund_type.py`
  - `fund_agent/fund/documents/models.py`
- 当前**没有**：
  - `fund_agent/fund/extractors/performance.py`
  - `nav_benchmark_performance` / `investor_return` 对应结果模型

### 3.2 当前测试现状

当前 `tests/fund/` 中：

- 已有：
  - `tests/fund/pdf/test_parser.py`
  - `tests/fund/extractors/test_profile.py`
- 当前**没有**：
  - `tests/fund/extractors/test_performance.py`
  - `tests/fixtures/fund/extractors/performance/**`

### 3.3 当前稳定输入与边界

当前稳定输入已存在：

- `FundDocumentRepository.load_annual_report(...)`
- 返回 `ParsedAnnualReport`
  - `key`
  - `raw_text`
  - `sections`
  - `tables`
- `ParsedAnnualReport.get_section_text("§3")`

这意味着 `P1-S5` 不需要再碰：

- `documents/` 公共契约
- `parser.py` / `section_catalog.py` 的章节定位语义
- repository 公开签名

## 4. 需求与约束裁决

### 4.1 设计与计划约束

按已接受 plan：

- `P1-S5` 只允许新增：
  - `nav_benchmark_performance`
  - `investor_return`
- 当前 slice 必须区分三种状态：
  - `direct`
  - `estimated`
  - `missing`
- 若估算逻辑需要 P2 的分析公式或投资结论，必须停止

### 4.2 AGENTS 硬约束

- `AGENTS.md` 明确要求：
  - 证据必须可溯源
  - root cause 必须逻辑/数据同源，不能用间接证据
  - 基金文档访问必须通过统一仓库接口，不直接操作文件系统
- 因此 `P1-S5` 不能：
  - 直接重新解析 PDF 或操作本地文件
  - 把 `§10` fallback 混进本轮最小实现，除非当前 `§3` 直接缺失且仍可仅凭当前输入构造明确 `estimated`
  - 用“经验上通常如此”填充投资者收益率

## 5. 范围裁决

### 5.1 Allowed files/modules

按已接受 plan，`P1-S5` 允许文件为：

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/performance.py`
- `tests/fund/extractors/test_performance.py`
- `tests/fixtures/fund/extractors/performance/**`

### 5.2 当前最小必要实现范围

controller 裁决本轮最小必要落地为：

- `fund_agent/fund/extractors/models.py`
  - 补充 `PerformanceExtractionResult`
- `fund_agent/fund/extractors/performance.py`
  - 只基于 `§3` 做表现字段抽取
  - 至少输出：
    - `nav_benchmark_performance`
    - `investor_return`
  - `investor_return` 必须区分：
    - 直接披露 `direct`
    - 当前仅能说明“未披露，待后续 fallback”时 `missing`
- `tests/fund/extractors/test_performance.py`
  - 覆盖：
    - `110011` 风格的 `§3` 直接提取净值增长率与业绩基准收益率
    - 投资者收益率直接披露路径
    - 投资者收益率未披露时不允许静默空字符串，必须 `missing`
- `tests/fixtures/fund/extractors/performance/**`
  - 至少覆盖：
    - 一只带投资者收益率披露的最小 `§3` 样本
    - 一只不带投资者收益率披露的最小 `§3` 样本

### 5.3 当前不建议触碰

- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/documents/**`
- `fund_agent/fund/pdf/**`
- `fund_agent/fund/data/nav_data.py`
- `tests/fund/pdf/**`
- 任何 `§4/§8/§9/§10` 提取逻辑

## 6. Root Cause 裁决

`P1-S5` 当前要解决的不是“多加两个字段”这么浅的问题，而是：

1. 当前 extractor 数据模型还没有 `§3` 表现结果容器
   - 无法让 `nav_benchmark_performance` / `investor_return` 成为稳定输出
2. 当前 capability 层还没有 `§3` extractor
   - 无法把净值增长率、基准收益率和投资者收益率做成带证据的结果
3. 当前还没有针对“披露 / 未披露”两类 `§3` 样本的 fixture/test
   - 无法锁定 `direct / missing` 状态机

## 7. 当前结论

- baseline reconciliation 结论：`pass`
- `P1-S5` 可以直接进入 implementation
- controller 对本轮的额外约束：
  - 不接受越界修改 `documents/**`、`pdf/**`、`data_extractor.py`
  - 不接受只抽值不带 anchor
  - 不接受把“未披露”静默表达为空字符串或 `None` 且不标状态
  - 不接受提前实现依赖 `§10` 的复杂 fallback 公式

## 8. 后续执行约束

- `AgentCodex` 负责：
  - 只在 `P1-S5` 允许文件内完成实现
  - 输出 durable implementation artifact
  - 不 commit、不 push、不进入下一 gate
- `AgentMiMo` 与 `AgentGLM` 负责：
  - 独立 code review / re-review
  - 重点检查是否严格留在 `§3` 边界、三态是否清晰、是否有 anchor、是否未越界到 `documents/pdf/data_extractor`
- controller 负责：
  - 对 findings 做 accepted / deferred / rejected 裁决
  - 必要时继续 `fix -> re-review`
  - 通过后再更新 `docs/implementation-control.md`
