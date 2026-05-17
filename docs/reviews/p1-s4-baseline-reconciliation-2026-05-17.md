# P1-S4 基线对账裁决

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S4 基础画像与基金类型识别
> 分支：`chore/reconcile-baseline`
> 当前 gate：`P1-S4 implementation + review`
> 上一 accepted slice commit：`d92eef7` (`gateflow: accept P1 P1-S3`)

## 1. 触发原因

- `docs/implementation-control.md` 当前 next entry point 已切到 `P1-S4 implementation + review`。
- `docs/reviews/p1-plan-2026-05-17.md` 第 8.2 节要求 `P1-S4` 先落地：
  - `basic_identity`
  - `product_profile`
  - `benchmark`
  - `fee_schedule`
- 同时必须让 `classified_fund_type` 成为 P1 的稳定输出，并满足 `AGENTS.md` 的“基金类型判断优先于通用分析”。

## 2. 当前工作树状态

当前 `git status --short` 仅剩无关未跟踪项：

```text
?? docs/reviews/code-review-20260517-0727.md
?? scripts/
```

裁决：

- 这两项不纳入 `P1-S4` 范围
- 当前可以安全基于 `HEAD=4dcbf4f` 继续推进

## 3. 代码基线事实

### 3.1 当前 fund capability 现状

当前 `fund_agent/fund/` 目录中：

- 已有：
  - `documents/`
  - `pdf/`
  - `analysis/`
  - `audit/`
  - `data/`
  - `template/`
- 但当前**没有**：
  - `fund_agent/fund/fund_type.py`
  - `fund_agent/fund/extractors/`

### 3.2 当前测试现状

当前 `tests/fund/` 中：

- 已有：
  - `tests/fund/documents/`
  - `tests/fund/pdf/`
- 但当前**没有**：
  - `tests/fund/extractors/test_profile.py`
  - `tests/fixtures/fund/extractors/profile/**`

### 3.3 当前稳定输入与边界

当前稳定输入已存在：

- `FundDocumentRepository.load_annual_report(...)`
- 返回 `ParsedAnnualReport`
  - `key`
  - `raw_text`
  - `sections`
  - `tables`

这意味着 `P1-S4` 不需要再碰：

- `documents/` 公共契约
- `parser.py` 章节定位语义
- repository 公开签名

## 4. 需求与约束裁决

### 4.1 设计与计划约束

按已接受 plan：

- `basic_identity.value` 内必须包含：
  - `classified_fund_type`
  - `classification_basis`
- 当前 slice 只输出供后续消费的数据：
  - 不做 preferred_lens 应用
  - 不做任何基金好坏判断

### 4.2 AGENTS 硬约束

- `AGENTS.md` 明确要求：
  - 基金类型判断优先于通用分析
  - 证据必须可溯源
- 因此 `P1-S4` 不能先写 profile 抽取再补分类；
  - 必须先定义基金类型识别与分类依据输出
  - 再让 `basic_identity` / `product_profile` / `benchmark` / `fee_schedule` 依赖该结果

## 5. 范围裁决

### 5.1 Allowed files/modules

按已接受 plan，`P1-S4` 允许文件为：

- `fund_agent/fund/fund_type.py`
- `fund_agent/fund/extractors/__init__.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fixtures/fund/extractors/profile/**`

### 5.2 当前最小必要实现范围

controller 裁决本轮最小必要落地为：

- `fund_agent/fund/fund_type.py`
  - 至少产出：
    - `classified_fund_type`
    - `classification_basis`
  - 不能做基金代码特判
- `fund_agent/fund/extractors/models.py`
  - 至少落地：
    - `EvidenceAnchor`
    - `ExtractedField`
    - `basic_identity / product_profile / benchmark / fee_schedule` 相关最小数据结构
- `fund_agent/fund/extractors/profile.py`
  - 只抽 `§1/§2` 当前需要的四类输出
  - 不进入 `data_extractor.py`
- `tests/fund/extractors/test_profile.py`
  - 覆盖：
    - 基金类型先于通用抽取输出
    - `classified_fund_type` 与 `classification_basis` 存在
    - 费率、基准、规模、经理信息带 anchor
- `tests/fixtures/fund/extractors/profile/**`
  - 至少覆盖 3 只样本基金里与 `§1/§2` 相关的最小事实片段

### 5.3 当前不建议触碰

- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/documents/**`
- `fund_agent/fund/pdf/**`
- `fund_agent/fund/data/nav_data.py`
- 任何 `§3/§4/§8/§9/§10` 提取逻辑

## 6. Root Cause 裁决

`P1-S4` 当前要解决的不是“缺少几个字段”这么浅的问题，而是：

1. 当前 capability 层还没有基金类型识别模块
   - 无法满足“基金类型判断优先”的硬约束
2. 当前还没有 extractor 数据模型
   - 无法把 `EvidenceAnchor`、`ExtractedField` 变成稳定输出
3. 当前还没有 profile extractor 与 fixture/test
   - `§1/§2` 相关字段无法形成可重复回归

## 7. 当前结论

- baseline reconciliation 结论：`pass`
- `P1-S4` 可以直接进入 implementation
- controller 对本轮的额外约束：
  - 不接受基金代码级分类特判
  - 不接受只返回分类标签、不返回 `classification_basis`
  - 不接受只抽值不带 anchor
  - 不接受提前把 `P1-S5` 的 `§3` 表现提取混进来

## 8. 后续执行约束

- `AgentCodex` 负责：
  - 只在 `P1-S4` 允许文件内完成实现
  - 输出 durable implementation artifact
  - 不 commit、不 push、不进入下一 gate
- `AgentMiMo` 与 `AgentGLM` 负责：
  - 独立 code review / re-review
  - 重点检查是否真的先做基金类型识别、是否无代码特判、是否有 anchor、是否没越到 `data_extractor.py`
- controller 负责：
  - 对 findings 做 accepted / deferred / rejected 裁决
  - 必要时继续 `fix -> re-review`
  - 通过后再更新 `docs/implementation-control.md`
