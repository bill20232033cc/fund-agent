# Fund Processor/Extractor Architecture Planning Gate — Truth-Doc Sync Review

> Reviewer: AgentMiMo
> Date: 2026-06-17
> Gate: Fund Processor/Extractor Architecture Planning Gate (heavy, docs/planning only)
> Review type: truth-doc sync review, read-only, no implementation

---

## Review Inputs

| Document | Role |
|---|---|
| `AGENTS.md` | 规则真源 |
| `docs/docling-architecture-reorientation-20260617.md` | 架构讨论输入（非自动事实真源） |
| `docs/design.md` v2.19 | 设计真源 |
| `docs/implementation-control.md` v2.8-control-compressed | 实施总控 |
| `docs/current-startup-packet.md` | 短恢复入口 |
| `fund_agent/README.md` | 开发手册总览（secondary） |
| `fund_agent/fund/README.md` | Fund 包开发手册（secondary） |

---

## Verdict

**TRUTH_SYNC_REVIEW_PASS_NOT_READY**

四份真源/控制文档在当前 phase、current gate、非目标、候选证据身份和 NOT_READY 边界上基本一致。未发现阻断级不一致。4 条信息级 findings 均不要求本轮修改。

---

## Findings

### F1 [INFO] 讨论纪要统计值未独立验证，但设计真源已正确限定为"输入"

**文件/行号**: `docs/docling-architecture-reorientation-20260617.md:13-20`; `docs/design.md` v2.19 变更摘要

**证据**: 讨论纪要 §1.1 声称"docling 相关 review 文件 367 个"、"总行数 ~47,000 行"、"representation JSON 总量 ~34MB"。这些数字未标注计算方法或数据源。设计真源 v2.19 变更摘要明确声明："不把该讨论纪要中的统计值、归档建议或未实现代码写成当前事实。"

**影响**: 无当前阻断影响。若后续文档引用这些数字作为事实依据，需要先独立验证。

**建议裁决**: 保持当前设计真源的"输入限定"表述，不修改。若后续 gate 需要引用具体数字，应独立计算。

### F2 [INFO] 讨论纪要的实施路线建议未被任何 gate 接受，设计真源已正确隔离

**文件/行号**: `docs/docling-architecture-reorientation-20260617.md:196-226`（§4 实施路线建议）

**证据**: 讨论纪要 §4 提出五步实施路线（止血 → 建立 Processor 注册表 → 实现第一个 Extractor → 扩展覆盖 → 数据仓库化），包括具体动作如"将 Docling gate 链标记为 DEFERRED"、"367 个 review 文件归档到 `docs/archive/`"、"创建 `fund_agent/fund/processors/` 模块"。这些是建议，不是已接受事实。

设计真源 v2.19 变更摘要正确处理："当前修订接受 `docs/docling-architecture-reorientation-20260617.md` 作为架构重定位输入，但不把该讨论纪要中的统计值、归档建议或未实现代码写成当前事实。"

**影响**: 无当前阻断影响。设计真源的隔离措施充分。

**建议裁决**: 保持现状。后续如果需要执行归档或创建模块，必须进入独立 reviewed gate。

### F3 [INFO] 讨论纪要引用的 dayu-agent Processor/Registry 机制已在多处正确标注为参考而非实现

**文件/行号**: `docs/docling-architecture-reorientation-20260617.md:56-98`（§2 dayu-agent Fins 架构）; `docs/design.md:672`（Processor/Extractor 分派决策）; `AGENTS.md:83`（Dayu 硬约束）

**证据**: 讨论纪要详细描述了 dayu-agent Fins 的 `ProcessorRegistry`、`source + form_type + media_type` 三键分派和 `_docling.json` 一次性转换机制。设计真源在 §6.1 和 §10 设计决策记录中正确引用为"借鉴 dayu-agent Fins 的 Processor/Registry 思路"并标注"必须在本项目内实现，不直接依赖 `dayu-agent` runtime"。AGENTS.md 硬约束也明确"禁止把 `dayu-agent` 作为生产 runtime 直接依赖"。

**影响**: 无。三处引用口径一致。

**建议裁决**: 无需修改。

### F4 [INFO] 四份文档对当前 gate 命名存在微小措辞差异

**文件/行号**: `docs/current-startup-packet.md:23` 使用 "Fund Processor/Extractor Architecture Planning Gate"; `docs/implementation-control.md:49` 使用 "Fund Processor/Extractor Architecture Planning Gate"; `docs/docling-architecture-reorientation-20260617.md:252` 使用 "FundProcessorRegistry / Extractor Architecture Planning Gate"

**证据**: 讨论纪要 §5.1 使用 "FundProcessorRegistry / Extractor Architecture Planning Gate"，而 startup packet 和 implementation-control 统一使用 "Fund Processor/Extractor Architecture Planning Gate"。差异仅为命名风格（前者更具体到实现类名），语义一致。

**影响**: 无。不造成 gate 身份混淆。

**建议裁决**: 无需修改。后续 gate 命名应以 `docs/implementation-control.md` 为准。

---

## Consistency Matrix

| 检查项 | AGENTS.md | design.md | implementation-control.md | current-startup-packet.md | 讨论纪要 | README (secondary) | 一致？ |
|---|---|---|---|---|---|---|---|
| 当前 phase | N/A | v2.19 变更摘要 | §开头: Docling reorientation / Fund Processor-Extractor route | §2: same | N/A (input) | N/A | YES |
| 当前 active gate | N/A | N/A | §Current Gate: Fund Processor/Extractor Architecture Planning Gate, heavy | §2: same | N/A | N/A | YES |
| 非目标/NOT_READY | N/A | 多处 "NOT_READY" | §开头 + 多处 "NOT_READY" | §2: "NOT_READY" | §1: "NOT_READY" | N/A | YES |
| Docling 候选身份 | 硬约束 §79 | §6.1 candidate-only | §Current Truth Guardrails | §2 Current Docling evidence | N/A (input) | fund/README:75-77 | YES |
| Processor/Extractor 边界 | 硬约束 §79 | §6.1 已接受未来设计 | §Current Truth Guardrails:40 | §2: current gate input | §3-4 (建议) | fund/README:35 | YES |
| 不得直接消费 parser 产物 | 硬约束 §79 | §6.1 多处 | §Current Truth Guardrails:43 | §2 Non-goal Reminder | §3.2 | fund/README:77 | YES |
| EID single-source policy | 硬约束 §79 | §6.1 | §Current Truth Guardrails:37 | §2: same | N/A | fund/README:73 | YES |
| UI→Service→Host→Agent 四层 | §92-141 | §2.1 | §Current Truth Guardrails:30 | §2: same | §5.3 | README:5-8 | YES |
| release/readiness 状态 | N/A | 多处 NOT_READY | 多处 NOT_READY | §2: NOT_READY | §1: NOT_READY | N/A | YES |
| 不得执行 live/source 命令 | N/A | §1.3 + §12 | §Non-goal Reminder | §4 + §5 Non-goal | N/A | N/A | YES |

---

## Scope Boundary Check

| 边界约束 | 是否违反？ | 证据 |
|---|---|---|
| 讨论纪要只作为输入，不自动成为真源 | 否 | design.md v2.19 变更摘要显式限定 |
| 不得声称 source truth / full field correctness | 否 | 四份文档均保持 candidate-only / not_proven 措辞 |
| 不得授权 live/source acquisition 命令 | 否 | startup packet §4 + §5 显式禁止 |
| 不得把 Docling/HTML render 当 raw XML/source truth | 否 | AGENTS.md 硬约束 + control doc guardrails |
| Processor/Extractor 设计限定在 Fund 层边界 | 否 | design.md §6.1 明确 "属于 Agent 层 fund_agent/fund" |
| 不得越过 UI → Service → Host → Agent 边界 | 否 | 讨论纪要 §5.3 正确声明四层边界 |
| README 与真源一致 | 否（无不一致） | fund/README 正确引用 Processor/Extractor 边界和 candidate harness |

---

## Blocking Open Questions

无。

---

## Residual Risks

| Risk | Severity | Mitigation |
|---|---|---|
| 讨论纪要统计值（367 文件、47K 行、34MB）若被后续文档引用可能传播未验证数据 | Low | 设计真源已限定为输入；后续引用应独立验证 |
| 讨论纪要 §4 实施路线五步建议若被误解为已接受计划可能导致未授权实施 | Low | 设计真源已隔离；实施必须进入独立 reviewed gate |
| 当前 gate 尚无 accepted implementation plan artifact | Info | 这是正常的 gate 入口状态；下一步应由 planning worker 产出 plan |

---

## Conclusion

四份真源/控制文档在 Docling 架构重定位后的当前 phase、current gate、非目标、候选证据身份和 NOT_READY 边界上保持一致。讨论纪要 `docs/docling-architecture-reorientation-20260617.md` 被正确处理为架构重定位输入而非自动事实真源。Processor/Extractor 未来设计正确限定在 Fund 层 `fund_agent/fund` 边界内，未越过 UI → Service → Host → Agent 四层架构。README secondary 检查未发现不一致。release/readiness 保持 `NOT_READY`。

本轮无阻断 findings，gate 可继续推进到 planning worker 阶段。
