# Provider/LLM Chapter 3 Bounded Live Re-evidence Worker-channel Disposition — DS Review

Date: 2026-06-14

Reviewer: AgentDS

Review target: `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-worker-channel-disposition-20260614.md`

Release/readiness: `NOT_READY`

## Verdict

PASS_WITH_FINDINGS

## Findings

### F1 (minor) — 重试 gate 缺少 worker 残留状态的前置检查

**位置**: §4 尾部与 §6 NEXT_ENTRY

**问题**: 当前 disposition 正确指出 "the controller must not treat the command boundary as cleanly unused"，但 `NEXT_ENTRY` 为 `Provider/LLM Chapter 3 Bounded Live Re-evidence Retry Gate` 时未显式要求 retry gate 的 plan 第一步是验证无残留进程、无 2026-06-14 毫秒级部分写入的 `reports/llm-runs/` artifact、及当前 git working tree 干净。

**严重度**: minor。当前 disposition 的推理链已隐含此要求，但未写入 next entry 的 precondition，可能导致 retry gate 开局跳过状态验证。

**建议**: 在 §4 或 §6 中增加一行 precondition："The retry gate plan must first verify no leftover `fund-analysis`/`uv` process, no partial `004393-2025-*` runtime artifact from 2026-06-14, and clean `git diff --check` before authorizing a new live command."

### F2 (minor) — 未回答 retry gate 是否复用原 plan 的 command boundary

**问题**: `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-20260613.md` 定义了一个 exact command、exact sample 和 stop conditions。当前 disposition 指示 retry gate，但未明确 retry gate 是直接复用原 plan 的 command boundary（相同 env/command/sample/stop conditions），还是需要一个新的 mini authorization。

**严重度**: minor。retry gate 计划阶段自然会回答此问题，但当前 disposition 作为 routing artifact，如果在这里给出方向可以减少 retry gate 的 plan ambiguity。

**建议**: 在 §4 或 residual 表中注明 retry gate 默认复用原 plan 的 command boundary（除非 controller 在 retry plan review 中明确修改），以降低 ambiguity。

## Accepted Facts

以下 disposition 中的事实判断经独立验证后接受：

| Fact | DS disposition | 备注 |
|---|---|---|
| No-live fix 在 `76df5ba` 仍为 accepted | ACCEPT | 交叉引用 `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-controller-judgment-20260614.md`，verdict 明确为 `ACCEPT_IMPLEMENTATION_NOT_READY` |
| 当前 gate 为 bounded live re-evidence，仅限 `004393 / 2025` Route C | ACCEPT | 与 startup packet §5 和 control doc current gate 一致 |
| Worker 未产出所需 evidence artifact | ACCEPT | 目标路径 absent，为可验证的文件系统事实 |
| 无可观察到的 2026-06-14 新 runtime artifact 目录 | ACCEPT_WITH_SCOPE_LIMIT | 安全路径检查，已正确标注 scope limit |
| 不推断 provider readiness / LLM completion / readiness | ACCEPT | 与 AGENTS.md "禁止使用间接证据" 原则一致，pane text 不等于 evidence |
| 拒绝 live completion proof 和 readiness 声明 | ACCEPT | 控制真源为 `NOT_READY` |

## Cross-check: 四个 Review Questions

### Q1: 是否正确地因 evidence artifact 缺失和 worker channel 断开而拒绝 live evidence？

**通过**。证据链完整：worker 被指派 → pane 报告 stream disconnect → target artifact absent → no new runtime directory → 无法接受 live evidence。逻辑无跳步，每个节点都有可验证的检查（路径 absent、process-name check、git diff --check）。

### Q2: 不从 pane text 推断 provider readiness / LLM completion / source fallback / readiness 是否正确？

**通过**。与 AGENTS.md "找问题的 root cause 一定要逻辑/数据同源，禁止使用间接证据" 一致。Pane text 是 worker channel 的间接产物，不是 provider/runtime 的直接 evidence artifact。Disposition 正确地在 residual 表中显式声明 "Do not infer success, failure class or provider readiness from pane text alone"。

### Q3: NEXT_ENTRY 为 separate bounded retry gate 是否合适？还是应为 NEED_MORE_CONTROLLER_EVIDENCE / BLOCKED？

**基本合适（见 F1/F2）**。根本原因是 worker channel transport failure（approval timeout + stream disconnect），不是 provider unavailable、code broken 或 policy violation。BLOCKED 暗示 permanent blocker，但这里没有证据表明 task 不可完成。NEED_MORE_CONTROLLER_EVIDENCE 可用于要求 controller 先收集更多证据再决策，但当前 controller 已有足够证据（missing artifact + idle worker + no new runtime dir）做出 disposition。Retry gate 是正确的 routing。

F1 和 F2 是对 retry gate 前置条件的补充建议，不影响 routing 方向的正确性。

### Q4: 是否有事实超出 safe metadata/path/process checks 而 overclaim？

**基本通过（一处小注意）**。接受的事实均在以下范围：
- 路径存在性检查（artifact absent）
- 进程状态检查（no active fund-analysis/uv）
- 引用已接受的 controller judgment（no-live fix at `76df5ba`）
- 控制真源引用（current gate, NOT_READY）

Fact 3 "AgentCodex/procodex was assigned the live evidence worker task" 是 process-level claim，basis 是 "Pane discovery, clear and handoff"。这不是 metadata/path check，而是 controller 对自身 handoff 行为的记录。可以接受，因为它是由 controller 直接执行的 handoff，属于可自我验证的过程事实。

## Required Amendments

无强制修改要求。F1 和 F2 为建议性 findings，由 controller 决定是否在 disposition 中吸收或推迟到 retry gate plan。

## Recommended Controller Disposition

1. 接受当前 disposition 的 verdict `LIVE_EVIDENCE_INVALID_WORKER_CHANNEL_FAILURE_NOT_READY` 和核心事实判断。
2. 考虑在 §4 或 §6 中吸收 F1 的 precondition（retry gate plan 第一步验证无残留）。
3. 考虑在 §4 或 residual 表中吸收 F2 的方向（retry gate 默认复用原 plan command boundary）。
4. 同步 `docs/current-startup-packet.md` 和 `docs/implementation-control.md` 到 retry gate next entry，保持 `NOT_READY`。
