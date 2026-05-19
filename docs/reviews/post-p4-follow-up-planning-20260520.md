# Post-P4 Follow-up Planning - 2026-05-20

## Verdict

Post-P4 follow-up planning is accepted.

P4 已经完成并合入 `main`。下一阶段不应继续扩展更多 extractor 作为第一优先级，而应先把 P4 建立的质量闭环接入用户实际会调用的 `analyze` 主链路。否则系统已经知道某些输入质量不可用，但用户仍可能通过正常报告入口获得未被质量 gate 保护的报告。

下一 gate：`P5-S1 quality gate integration plan/review`。

## Inputs

- Design truth: `docs/design.md`
- Global control doc: `docs/implementation-control.md`
- P4 control doc: `docs/implementation-control-p4.md`
- P4 readiness reconciliation: `docs/reviews/p4-readiness-reconciliation-20260520.md`
- P4 design/control/code reconciliation: `docs/reviews/p4-design-control-code-reconciliation-20260519.md`
- P4 PR review controller judgment: `docs/reviews/pr-3-review-controller-judgment-20260520.md`

## First Principles

基金分析报告的风险不是“字段少”，而是“字段质量低但报告形式完整”。P4 已经证明 snapshot / score / quality gate 可以度量并阻断低质量输入；post-P4 的第一优先级必须是让这个阻断能力进入报告主路径，而不是停留在独立 CLI 或离线 artifact。

设计边界裁决：

- Capability 继续负责 snapshot、score、quality gate、correctness、preferred_lens 和审计规则。
- Service 只负责编排质量预检与报告生成，不承载基金领域规则。
- CLI 只暴露显式参数和渲染状态，不直接判断基金质量。
- `analyze` 集成不得绕过统一文档仓库接口，不得直接读取 PDF/cache 文件。
- 所有输入必须显式声明；禁止把 `fund_code`、`report_year`、`source_csv`、`golden_answer_path`、gate policy 等显式参数塞进 `extra_payload`。

## P5 Candidate Backlog

| Slice | Priority | Owner | Scope | Acceptance signal |
|---|---:|---|---|---|
| P5-S1 | P0 | `quality gate integration slice` | 把 P4 quality gate 接入 `analyze` 主链路，至少保证报告生成前后能显式产出 gate 状态，并能按策略阻断或标记低质量输入 | `fund-analysis analyze` 不再静默绕过 quality gate；Service 返回值携带 gate 结果；blocking gate 可阻断报告输出或输出明确 blocked 状态 |
| P5-S2 | P1 | `quality gate rules slice` | 补齐 P4-R9：FQ1 App 类别冲突分支、FQ4 数据不足比例、FQ5 preferred_lens mismatch | 新规则在 `score.json` / `quality_gate.json` 中有稳定 schema、规则码和测试 |
| P5-S3 | P1 | `snapshot sub-field exposure slice` | 扩大 correctness 可比字段，优先暴露 P0 子字段，如 `fee_schedule`、`benchmark`、`product_profile`、`basic_identity` 的可比子项 | correctness denominator 不再只有 `classified_fund_type.fund_type`；skipped/unavailable 仍不进分母 |
| P5-S4 | P1 | `snapshot failure accounting slice` | 完全失败基金进入 fund-level accounting，避免只落在 `errors.jsonl` 后被 gate 忽略 | `fund_scores` 或独立 `failed_funds` 能被 quality gate 消费并触发 block |
| P5-S5 | P2 | `share_change hardening slice` | 明确多份额列选择策略，按基金代码/份额类别选择 A/C 份额对应列 | `share_change` 对多份额表不再依赖偶然列顺序，测试覆盖 A/C 份额 |
| P5-S6 | Human | user/App source reconciliation | 核对精选基金池 CSV 中 `016492` 重复的真实来源 | 用户裁决后更新源 CSV 或记录保留重复的业务原因 |
| P5-S7 | P3 | `post-MVP infra validation` | 温度计 Service/CLI 接入与真实 PDF/network smoke 自动化 | 不阻塞 P5-S1；作为 post-MVP infra validation 继续追踪 |

## P5-S1 Plan Requirements

P5-S1 进入实现前必须先形成 plan/review artifact，至少回答：

1. `analyze` 的质量 gate 策略是 `off / warn / block` 还是更窄的显式选项；默认策略必须避免静默绕过。
2. Service 如何复用或生成 score/gate 输入，避免重复下载 PDF 或绕过 `FundDocumentRepository`。
3. gate blocked 时 CLI 和 Service 返回值如何表达，不输出“形式完整但质量不可用”的报告。
4. 没有 `source_csv`、App 类别或 golden answer 时，哪些规则可运行，哪些规则应明确 `not_run / unavailable`。
5. `quality_gate.json` 与现有 `ProgrammaticAuditResult` 的关系：P5-S1 只做质量预检编排，不把质量 gate 混入模板审计规则。

## Deferred But Tracked

| Risk | Decision |
|---|---|
| RR-13 / P4-R1: `016492` duplicate | 需要用户核对 App 源数据；不阻塞 P5-S1 |
| RR-15 / P4-R8: quality gate not attached to `analyze` | 升级为 P5-S1 blocking focus |
| RR-16: narrow correctness denominator | P5-S3 负责，不阻塞 P5-S1 plan |
| RR-4: thermometer Service/CLI integration | 后移到 P5-S7 / post-MVP infra validation |
| RR-8: true PDF/network smoke | 后移到 P5-S7 / post-MVP infra validation |

## Gate Decision

当前 gate 从 `post-P4 follow-up planning` 推进为 `post-P4 follow-up planning accepted`。

下一步进入 `P5-S1 quality gate integration plan/review`。在 plan 通过前，不应直接实现 `analyze` 集成代码。
