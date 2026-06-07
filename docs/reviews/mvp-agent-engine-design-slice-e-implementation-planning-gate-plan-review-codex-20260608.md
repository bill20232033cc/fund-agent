# MVP Agent Engine Design Slice E Implementation Planning Gate Plan Review - Codex

## Findings

### 1-未修复-高-E5 把 code review / controller judgment / control sync 放进 implementation 授权范围

- **位置**: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:205-224`, `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:331-343`
- **问题类型**: 范围漂移 / 过宽授权 / Gate 流程边界
- **当前写法**: E5 的 allowed files 包含 `docs/reviews/mvp-agent-engine-design-slice-e-code-review-*.md`、`docs/reviews/mvp-agent-engine-design-slice-e-controller-judgment-20260608.md`、`docs/current-startup-packet.md` 和 `docs/implementation-control.md`；Controller option 又允许 implementation "proceed exactly through E1-E5"。
- **反例/失败场景**: Controller 接受该 plan 后，implementation worker 可按字面范围创建 code review artifact、controller judgment artifact，或在 review/controller acceptance 前把 Agent package 写入 control truth。这样会把 reviewer/controller 职责并入 implementation worker，并让 control docs 先于 accepted implementation 记录当前事实。
- **为什么有问题**: `AGENTS.md` 将 standard gate 定义为需要验证矩阵、独立 review、controller judgment、必要文档更新和 local accepted commit；这些动作属于顺序化 gate 生命周期，不应由 implementation slice 的 allowed files 一次性授权。当前 control truth 也只授权 Slice E planning-only，明确要求 plan/review/controller judgment 后才可进入 implementation；同一原则应继续适用于 implementation 后的 code review 和 controller judgment。
- **直接证据**:
  - Plan E5 allowed files: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:205-216`
  - Plan controller option: `PLAN_ACCEPTED_IMPLEMENTATION_AUTHORIZED` 可执行 E1-E5: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:331-343`
  - `AGENTS.md` standard gate 需要 independent review 和 controller judgment: `AGENTS.md:55`
  - 当前 next entry 仅为 planning-only，implementation 需 plan/review/controller judgment 后显式授权: `docs/current-startup-packet.md:21-22`, `docs/implementation-control.md:70-72`
- **影响**: 实施 Agent 可能越权写 review/judgment/control truth；controller 无法区分 implementation evidence、review disposition 和 accepted checkpoint；后续恢复入口可能把未 review 的 Agent runtime 写成当前事实。
- **建议改法和验证点**:
  - 将 E5 拆成三个边界：implementation worker 只允许写 implementation evidence、Agent README / package map / tests README 中由代码变更触发的文档；code review artifacts 只允许 reviewer 写；controller judgment 和 control docs 只允许 controller 在 code review 后写。
  - Controller decision option 应改为 implementation may proceed through E1-E4 plus implementation-evidence/doc updates, then stop for code review/controller judgment。
  - Stop condition 增加：implementation worker must not write code-review, controller-judgment, current-startup-packet or implementation-control unless a separate controller role explicitly authorizes control sync。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 高

### 2-未修复-中-Host cancel/deadline 迁移缺少 normalized scheduler contract 和等价测试

- **位置**: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:131-166`, `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:168-203`, `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:271-304`
- **问题类型**: 架构边界 / 不可直接实施 / 状态机漏洞 / 测试缺口
- **当前写法**: E3 只说 Host interruption 可作为 already-normalized Agent scheduler event/status 进入 repair policy，并禁止 repair policy / tool adapters import 或 inspect Host context/state；但未定义该 normalized event/status 的字段、归属、runner 何时检查、如何映射为 Agent terminal，E4 和 No-Live Validation Matrix 也没有 cancel/deadline 等价测试。
- **反例/失败场景**: 当前 Service `ChapterOrchestrator` 在章节和 writer/auditor phase 边界接收 `HostRunContext` 并调用 cancel/deadline 检查。迁移 body execution 到 Agent runner 时，如果 implementation worker按 plan 最小实现：
  - 可能让 Agent runner 直接 import `HostRunContext`，破坏 Agent/Host 边界；
  - 或完全不传递 cancel/deadline，导致 Host timeout/cancel 不再在 body chapter phase 边界生效；
  - 或把 interruption 当 content repair 输入，错误消耗 repair budget。
- **为什么有问题**: `AGENTS.md` 固定 Host 负责 run lifecycle、timeout、cancel，Agent 负责 runner/tool loop/repair/tool execution；Slice C judgment 已要求 Host interruption 在进入 repair policy 前由 Agent scheduling normalized。Slice E 是 code-generation-ready implementation plan，必须给 implementation worker 一个具体 contract 和 no-live test，否则迁移当前 execution mechanics 时只能重新设计或冒跨层依赖风险。
- **直接证据**:
  - Plan E3 normalized interruption 只有原则，无字段/terminal/test: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:155-157`
  - Plan E4 迁移 Service body execution，但未描述 Host cancel/deadline bridge: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:180-192`
  - Plan validation matrix 未覆盖 Host cancel/deadline: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md:271-304`
  - 当前 code fact: `ChapterOrchestrator` 直接接收 `HostRunContext` 并在 phase 边界检查 cancel/deadline: `fund_agent/services/chapter_orchestrator.py:642-650`, `fund_agent/services/chapter_orchestrator.py:683`, `fund_agent/services/chapter_orchestrator.py:1379-1394`
  - Slice C judgment follow-up: repair policy 只能消费 Agent scheduling normalized signal: `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-controller-judgment-20260608.md:74-79`
  - `AGENTS.md` Host/Agent 职责边界: `AGENTS.md:109-119`, `AGENTS.md:131-136`
- **影响**: Agent runner migration 可能弱化 Host lifecycle behavior，或引入 Agent 对 Host runtime 的直接依赖；no-live parity tests 即使通过章节内容矩阵，也不能证明 cancellation/deadline 语义未退化。
- **建议改法和验证点**:
  - 在 E1/E3 增加 Agent-owned scheduler interruption dataclass 或 literal contract，例如 `AgentSchedulerInterruption(status, reason, phase, chapter_id, attempt_index)`，明确它由 Service bridge 从 Host context 结果转译，不把 `HostRunContext` 传入 Agent contracts / repair / tools。
  - 在 E3/E4 增加 no-live tests：cancel before first chapter、deadline between writer and auditor、interruption does not consume content repair budget、Agent package does not import `fund_agent.host`。
  - 明确 terminal/readiness mapping：interrupted run must fail closed and cannot produce complete report markdown。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 中

## Verdict

`BLOCKED`

当前 plan 方向与 Slices A-D 的主体设计相容，但还不能授权 implementation。必须先修正 E5 角色/文件授权边界，并补齐 Host cancel/deadline normalized scheduler contract 与 no-live equivalence tests。修正后可重新 review；若这些点收敛，implementation 可在 controller judgment 后被授权，但约束应限定为：只改明确实现文件、只跑本地 no-live tests/ruff/diff-check、不写 code review/controller judgment/control truth、不运行 live/provider/network/probe，不改变 provider/default/runtime/budget、score-loop、multi-year、golden/readiness、quality gate、public chapter ids、stdout/final judgment。

## Reviewed Target And Scope

- Target plan: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md`
- Review artifact: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-codex-20260608.md`
- Review timestamp from local clock: `20260608-015952 CST`
- Scope: plan review only; no source, test, target plan, control doc or README edits; no live `--use-llm`; no provider readiness, curl, DNS, socket, endpoint or network probe; no `fund_agent/agent` creation; no commit/PR/push/external comment.

## Context Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- Slice A judgment: `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md`
- Slice B judgment: `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-controller-judgment-20260608.md`
- Slice C judgment: `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-controller-judgment-20260608.md`
- Slice D judgment: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-controller-judgment-20260608.md`
- Current code facts inspected only for local enum/boundary evidence: `fund_agent/services/chapter_orchestrator.py`, `fund_agent/services/final_chapter_assembler.py`, existing service tests search results.

## Assumptions Tested

- Whether allowed files are narrow enough for implementation worker authorization.
- Whether implementation sequencing preserves plan -> implementation evidence -> code review -> controller judgment -> control sync.
- Whether Service/Host/Agent/Fund ownership remains enforceable after body execution migration.
- Whether terminal mapping covers current `ChapterRunStopReason` and `ChapterFailureCategory` and preserves `llm_exception + code_bug`.
- Whether no-live validation is sufficient for body outcome parity, ToolTrace safety and final assembly readiness.
- Whether provider/runtime retry remains separate from Agent content repair budget.
- Whether hidden Agent retry remains forbidden and observable through attempt/repair/tool ledgers.

## Non-Blocking Observations

- Terminal mapping appears to enumerate every current `ChapterRunStopReason` literal in `fund_agent/services/chapter_orchestrator.py:53-77`, and includes all current `ChapterFailureCategory` literals in `fund_agent/services/chapter_orchestrator.py:105-113`.
- The plan correctly preserves Slice D's `llm_exception + code_bug -> blocked_internal_code_bug` distinction and does not collapse it into provider/runtime.
- The plan covers duplicate body chapter rows and accepted source id uniqueness in E4 and the no-live matrix; this matches current final assembly fail-closed behavior in `fund_agent/services/final_chapter_assembler.py:443-456`.
- ToolTrace serialization constraints are materially aligned with Slice A/B judgments: no prompt, draft, raw provider/audit payload, provider request/body, key/header/token, model or base URL; `request_id` is scalar allowlist-only.

## Residual Risks And Tracking Destination

- After plan revision, implementation review should re-check that Agent ToolTrace cannot serialize `ToolCallResult` payloads containing fact values, draft markdown or unsafe anchor prose.
- After plan revision, implementation review should re-check that `llm_exception` with provider-unclassified exceptions remains code-bug fail-closed and never consumes content repair budget.
- Tracking destination: revised Slice E plan and subsequent Slice E code review artifacts.

## Validation Commands

Executed before writing review:

```text
git branch --show-current
git status --short
date '+%Y%m%d-%H%M%S %Z'
```

Executed after writing review:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-codex-20260608.md
```

Result: exit `0`; no whitespace errors.

Supplemental new-file check:

```text
git diff --check --no-index -- /dev/null docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-codex-20260608.md
```

Result: exit `1` because the new file differs from `/dev/null`; no whitespace errors emitted.
