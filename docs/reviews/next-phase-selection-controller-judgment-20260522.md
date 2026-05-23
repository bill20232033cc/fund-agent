# Next Phase Selection Controller Judgment（2026-05-22）

## Verdict

`ACCEPTED_WITH_REQUIRED_P13_S1_CONSTRAINTS`

Controller 接受 `docs/reviews/next-phase-selection-20260522.md` 的推荐：下一 gate 进入 `P13-S1 tracking-error / index-data source contract plan-review`。

该 gate 仍是 planning/design，不允许直接 implementation。

## Basis

- 当前总控状态为 `maintenance-ready`，下一入口为 `next phase selection`。
- P12 已关闭在 `main`，post-P12 release lane 已通过 maintenance closeout。
- 设计真源仍要求确定性 MVP 主链路、Fund Capability ownership、生产年报访问经 `FundDocumentRepository`、不引入 Dayu Host/Engine/tool loop。
- index / enhanced-index 的 `preferred_lens` 明确把 tracking error 作为核心分析变量；当前 renderer 仍存在用户可见的 `数据不足` gap。
- E1-E3 / Evidence Confirm 属于后续审计架构 phase；repo-hygiene 和 RR-13 均不应混入 P13 数据能力。

## Review Disposition

| Review artifact | Verdict | Controller disposition |
|---|---|---|
| `docs/reviews/next-phase-selection-plan-review-mimo-20260522.md` | `pass-with-risks` | accepted; 风险不阻断 selection，但必须进入 P13-S1 plan 的必答约束 |
| `docs/reviews/next-phase-selection-plan-review-glm-20260522.md` | `PASS` | accepted; 3 个 finding 均为 P13-S1 plan-review 约束，不阻断 selection |

## Required P13-S1 Constraints

P13-S1 plan 必须先回答以下问题，否则不得进入 implementation：

1. `tracking_error` 的权威来源是年报/招募说明书直接披露、Fund Capability 计算，还是 developer override；如果从 service-level override 迁移到 Capability extraction，必须定义冲突优先级和迁移路径。
2. 跟踪误差如果需要从基金/指数时间序列计算，必须先定义指数序列来源、identity、cache、failure taxonomy 和 provenance；不得把外部指数序列 adapter 暗含进一个过宽 implementation slice。
3. `index methodology` 和 `constituents` 必须按可用性分级：只有现有 `FundDocumentRepository` 路径或已设计的新 source contract 能提供时才替换 `数据不足`，否则保留 missing / insufficient-data 行为。
4. P13-S1 plan 必须给出正面接受标准，不只列拒绝条件。至少包括 slice 输入/输出、边界规则、独立可交付性、stop conditions 和 targeted validation。
5. 纯指数基金 fixture 策略必须明确：使用真实样本文档还是人工构造 fixture，以及如何覆盖 index / enhanced-index / missing-data 路径。

## Non-Goals Preserved

- 不修改 source、tests、README、`docs/design.md`、`docs/implementation-control.md` 或 `docs/repo-audit-20260521.md` 作为 selection gate 的一部分。
- 不自动修复 RR-13 duplicate `016492`。
- 不引入 Dayu runtime、LLM writing、Evidence Confirm 或 E1-E3 执行。
- 不让 Service/UI/renderer/quality gate 直接调用具体文档来源、PDF cache 或下载 helper。

## Next Gate

Proceed to:

```text
P13-S1 tracking-error / index-data source contract plan-review
```

Required planning artifact:

```text
docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md
```
