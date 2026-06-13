# Provider/LLM Chapter 3 Bounded Live Re-evidence Worker-channel Disposition — DS Re-review

Date: 2026-06-14

Reviewer: AgentDS

Re-review trigger: target procodex artifact later appeared, correcting the original disposition's "artifact missing" premise.

Review targets:
- `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-procodex-20260614.md`
- `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-worker-channel-disposition-20260614.md`
- `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-worker-channel-controller-judgment-20260614.md`

Release/readiness: `NOT_READY`

## Verdict

PASS_WITH_FINDINGS

## Q1: Is ACCEPT_PERMISSION_APPROVAL_BLOCKER_NOT_READY supported by live_process_created=false and live_command_run_count=0?

**通过**。procodex artifact §4 直接支撑：

| Procodex field | Value | 含义 |
|---|---|---|
| `live_process_created` | `false` | OS 进程从未创建 |
| `live_command_run_count` | `0` | 授权命令执行次数为零 |
| `tool_error_class` | `CreateProcess` | 错误发生在工具层进程创建阶段 |
| `approval_result` | `permission_approval_review_timeout` | 权限审批超时 |
| Approval request attempts | `3` | 三次请求均未通过审批 |

分类 `ACCEPT_PERMISSION_APPROVAL_BLOCKER_NOT_READY` 比原始 disposition 的 `LIVE_EVIDENCE_INVALID_WORKER_CHANNEL_FAILURE_NOT_READY` 更精确：原始 disposition 只知道 artifact missing + stream disconnect，无法区分是 worker channel transport failure、permission approval timeout、还是 worker 逻辑错误。Procodex artifact 提供了具体分类依据，将 blocker 定位到 permission approval layer，而非 worker channel 或 application layer。

分类的后半部分 `NOT_READY` 与所有控制真源一致。

## Q2: Is it correct to reject provider runtime/completion/readiness/source-policy claims?

**通过**。`live_process_created=false` + `live_command_run_count=0` 意味着：

- 无 OS 进程 → 无 application runtime → 无 provider HTTP call
- 无 `reports/llm-runs/` manifest/summary → 无 chapter matrix，无 runtime diagnostic
- 无 source/provenance metadata

在此前提下，拒绝以下声明完全正确：
- provider readiness / provider attempt count / provider response classification
- LLM completion / LLM content quality
- Chapter 3 post-fix behavior
- Source policy / fallback status
- Release/readiness improvement

Controller judgment §4 的 REJECT 行均与 procodex artifact 的零执行事实一致。

## Q3: Is retry gate with preflight and exact original command boundary the right next entry?

**通过**。理由：

1. **Blocker 是 pre-execution 的**：permission approval timeout 发生在进程创建之前，不是 application/provider/LLM 层错误，不是 code bug，不是 provider unavailable，不是 source policy violation。没有需要修复的代码或配置。
2. **零运行时状态**：无进程创建 = 无残留进程、无 runtime artifact、无部分 provider 调用。原 command boundary 完全未被消费。
3. **Preflight checklist 充分**：controller judgment §5 的三条 preflight（no leftover process, no partial runtime artifact, clean git diff --check）覆盖了安全重试所需的全部前置条件。
4. **复用原 plan command boundary 正确**：`docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-20260613.md` 的 exact command、sample、stop conditions、redaction rules 均未被消费，无需修改。单独的 retry gate（非 continuation）正确地将重试视为新的 bounded attempt。

## Q4: Any stale statements?

**发现以下过期陈述**：

### S1 (medium) — 原始 disposition artifact 存在多条过期陈述

`docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-worker-channel-disposition-20260614.md` 写于 procodex artifact 出现之前，以下内容已过期：

| 位置 | 过期陈述 | 当前事实 |
|---|---|---|
| §2 | "required evidence artifact" absent | Procodex artifact 现已存在 |
| §3 fact 行 4 | "The worker did not produce the required evidence artifact" | 已产出，只是延迟出现 |
| §4 | "AgentCodex/procodex did not return the required artifact" | 已返回 |
| §4 | "stream disconnect after attempting the assigned command" | Procodex artifact 解释为 permission approval timeout；stream disconnect 与 approval timeout 的因果关系未被 controller judgment 显式调和 |
| §5 residual 行 2 | "Whether the worker's interrupted command reached provider/runtime" → UNKNOWN | Procodex artifact 证实 `live_command_run_count=0`，已确定未到达 provider/runtime |
| §6 verdict | `LIVE_EVIDENCE_INVALID_WORKER_CHANNEL_FAILURE_NOT_READY` | Controller 重新分类为 `ACCEPT_PERMISSION_APPROVAL_BLOCKER_NOT_READY` |

**影响**：原始 disposition 是 evidence chain 的一部分，但不是当前控制真源（controller judgment 已覆盖）。对于后续 evidence chain 重建，如果只读原始 disposition 而不读 controller judgment，会得到错误的 blocker 分类。建议在原始 disposition 顶部加一个 superseded notice，指向 controller judgment。

### S2 (minor) — 原始 DS review 和 MiMo review 基于过期前提

两份 review 均在 procodex artifact 出现前完成，其 Q1 回答基于 "artifact missing" 前提。Controller judgment 已将两者正确标注为 `PARTIALLY_SUPERSEDED_BY_LATE_ARTIFACT`。两份 review 中关于 "不推断 provider/LLM/readiness" 和 "不 overclaim" 的判断仍然有效（procodex artifact 进一步加固了这些判断），但关于 "worker channel failure" 的具体分类已被 controller judgment 的 `ACCEPT_PERMISSION_APPROVAL_BLOCKER_NOT_READY` 覆盖。

### S3 (minor) — Startup packet 和 Implementation control 的 next entry 尚未同步

- `docs/current-startup-packet.md` §2 next entry point: 仍为 `Provider/LLM Chapter 3 Bounded Live Re-evidence Gate`
- `docs/implementation-control.md` current gate / next entry: 同上

两者应同步为 `Provider/LLM Chapter 3 Bounded Live Re-evidence Retry Gate`。Controller judgment 未包含 control doc sync 命令，应在 retry gate 启动前由 controller 完成同步。

### S4 (minor) — "stream disconnect" 与 "permission approval timeout" 的因果链未调和

原始 disposition 记录 "stream disconnect after attempting the assigned command"，procodex artifact 记录 `approval_result=permission_approval_review_timeout`。两者可能一致（approval review timeout 导致 stream disconnect），但 controller judgment 未显式调和这两个描述。这不影响 blocker 分类的正确性，但 evidence chain 中存在轻微叙事不一致。建议 controller 在 retry gate plan 中简单注明两者关系，或接受此为 minor process residual。

## Accepted Corrected Facts

| Fact | DS disposition | Basis |
|---|---|---|
| Procodex artifact 现已存在并记录完整执行元数据 | ACCEPT | Artifact 可读，字段自洽 |
| `live_process_created=false`, `live_command_run_count=0` | ACCEPT | Procodex §4 |
| Permission approval timeout 是进程未创建的直接原因 | ACCEPT | Procodex §4 和 §7 |
| 无 runtime manifest/summary, 无 chapter matrix, 无 provider diagnostic | ACCEPT_WITH_SCOPE_LIMIT | 预期结果（进程未创建），procodex §5-§7 确认 |
| 不推断 provider/LLM/completion/readiness/source-policy | ACCEPT | 与 Q2 分析一致 |
| Retry gate with preflight + original command boundary | ACCEPT | 与 Q3 分析一致 |
| Controller judgment 正确覆盖原始 disposition | ACCEPT | Controller judgment §5 和 §6 |

## Findings

| ID | Severity | Description |
|---|---|---|
| S1 | medium | 原始 disposition artifact 含多条过期陈述（missing artifact, worker channel failure），未被标记为 superseded |
| S2 | minor | 原始 DS/MiMo review 基于过期前提，controller 已标注 PARTIALLY_SUPERSEDED，建议在 review artifact 顶部也加 notice |
| S3 | minor | Startup packet 和 implementation control 的 next entry 尚未同步到 retry gate |
| S4 | minor | "stream disconnect" 与 "permission approval timeout" 因果链未显式调和 |

## Required Amendments

1. **S1**：在原始 disposition artifact 顶部加 superseded notice，指向 controller judgment。或由 controller 在 control doc sync 时明确 disposition 的 evidence-chain-only 角色。
2. **S3**：在 retry gate 启动前将 `docs/current-startup-packet.md` 和 `docs/implementation-control.md` 的 next entry 同步为 `Provider/LLM Chapter 3 Bounded Live Re-evidence Retry Gate`。

S2 和 S4 为非阻塞建议，由 controller 决定是否处理。

## Recommended Controller Disposition

1. Accept `ACCEPT_PERMISSION_APPROVAL_BLOCKER_NOT_READY` as the corrected verdict。
2. Apply S1 amendment（标记原始 disposition 为 superseded）和 S3 amendment（同步 control docs）。
3. Route to `Provider/LLM Chapter 3 Bounded Live Re-evidence Retry Gate`，preflight checklist 按 controller judgment §5 执行。
4. 保留 `NOT_READY` 和 EID single-source/no-fallback。
