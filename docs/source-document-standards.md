# 真源文档规范

本文档是 `AGENTS.md` 中“真源文档规范”的可读版。执行约束以 `AGENTS.md` 为准。

## 目标

真源文档必须降低恢复任务和设计裁决的认知负担，而不是把所有历史记录堆在一起。当前仓库的真源入口分为三层：

| 文档 | 职责 |
|---|---|
| `AGENTS.md` | Agent 执行规则、模块边界和文档规范的唯一权威入口 |
| `docs/design.md` | 当前代码设计真源；记录当前事实、稳定边界和已接受但未实现的未来设计 |
| `docs/implementation-control.md` | 当前 phase / gate 总控；记录 Startup Packet、next entry point、accepted artifacts 和 residual owner |

## `docs/design.md` 规范

`docs/design.md` 可以包含未来设计，但必须显式标注状态。

允许：

- 当前已实现的代码事实。
- 已经 gate 裁决接受、但尚未实现的未来设计。
- 当前非目标、触发未来 gate 的条件、禁止事项和边界约束。

禁止：

- 把未实现能力写成当前实现。
- 把研究文档、外部项目机制、旧架构或本地草案直接写成当前设计事实。
- 用“未来会做”的散文替代可裁决的设计状态、契约和非目标。

推荐每个涉及未来能力的章节都写清：

```text
状态：当前已实现 / 已接受的未来设计 / 候选
当前代码事实：
未来设计边界：
非目标：
进入实现 gate 的触发条件：
```

## `docs/implementation-control.md` 规范

`docs/implementation-control.md` 应保持为控制面入口，不应继续膨胀成完整审计账本。

前部必须保留：

- Startup Packet。
- Current Truth Guardrails。
- Current phase / current gate / next entry point。
- 当前 gate 相关 accepted artifacts。
- Open residuals 和 owner。
- Non-goal reminder。
- 最近 Active Gate Ledger。

应迁出：

- 旧 phase 的全量日志。
- superseded 架构叙述。
- 长 PR / commit / review 记录。
- 已关闭 gate 的详细过程。
- 只用于证据保全的历史材料。

迁出目标：

- `docs/reviews/`：单个 plan、review、controller judgment、implementation report。
- `docs/archive/`：历史总账、旧 phase 长记录、已 superseded 的控制记录。

`docs/implementation-control.md` 对迁出内容只保留索引，例如：

```text
Historical evidence archive:
- P0-P12 detailed history: docs/archive/implementation-control-history-p0-p12.md
- P13-P19 detailed history: docs/archive/implementation-control-history-p13-p19.md
```

## 有效信息判定

在 `docs/implementation-control.md` 中：

- Startup Packet 和当前 gate 是当前控制真源。
- Active Gate Ledger 的最近 gate 是当前恢复依据。
- archive / historical section 是证据链，不是当前架构依据。
- 与 Startup Packet 或 `docs/design.md` 冲突的历史内容自动降级为 superseded evidence。

## 语言规范

- 中文为主。
- gate id、artifact path、commit hash、命令、类型名可以保留英文。
- 裁决、边界、风险、禁止事项和恢复说明应使用中文。
