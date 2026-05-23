# Release Maintenance Next Candidate Plan - 2026-05-24

## Goal / Motivation

为下一轮 release-maintenance 本地 work unit 选择一个可进入 plan review 的最小候选，并给出 plan-review-ready 决策计划。本 work unit 是 document-only boundary decision，不授权代码生成、Host/Agent 实现、依赖修改或包结构变更。

当前 gate 是 `release maintenance quality gate final judgment contract accepted locally`。Startup Packet 的下一入口是 `ready for push authorization or next release-maintenance candidate selection`。本 artifact 只负责候选选择和下一 work unit 计划，不执行 push / PR / merge，不改 source / test / config / README / control_doc / design_doc，不创建 `fund_agent/host` 或 `fund_agent/agent` 占位包。

第一性原理判断：当前代码的确定性生产主链路已经可运行，Host/Agent 尚未有具体 session/run/cancel/resume/outbox 或 runner/tool-loop/ToolTrace 需求。直接进入 Host/Agent dependency gate 会在没有真实用例时引入生产依赖；直接创建 Host/Agent 包会制造空框架。最合理的下一步是先做一个窄化的 **Host/Agent boundary decision planning gate**：只产出决策记录、验收矩阵和后续落地 gate 的进入条件，不落地通用执行包，不声明 `dayu.host` / `dayu.engine` 依赖。

## Non-Goals / Scope

- 不启动 `/gateflow` 或 `$gateflow`。
- 不从旧 plan 重新开始，不重排当前 gate。
- 不读取或引用被 Startup Packet 明确排除的旧 repo-audit 文档。
- 不把 `docs/reviews/` 或 implementation-control archive 中旧六层、Application、Runtime/Engine 口径作为当前架构依据。
- 不创建 `fund_agent/host` 或 `fund_agent/agent` 占位包。
- 不修改 `pyproject.toml`、`uv.lock`、source、test、config、README、`docs/design.md`、`docs/implementation-control.md`。
- 不引入 Host 调度、Agent tool loop、LLM 写作、Evidence Confirm、外部指数适配器或计算型 tracking error。
- 不把显式业务参数放入 `extra_payload` / `extra_payloads`。
- 不执行 push、PR、merge、分支删除、外部评论、issue/PR mutation。

## Direct Evidence

- `AGENTS.md`：目标架构固定为 `UI -> Service -> Host -> Agent`；Host 管理 session/run/并发/timeout/cancel/resume/memory/outbox/事件投递，且必须使用 `dayu.host`；Agent 管理 tool loop/runner/ToolRegistry/ToolTrace/context budget/tool execution，且必须使用 `dayu.engine`。
- `AGENTS.md`：当前确定性过渡路径可由 Service 调用 `fund_agent/fund` 公开能力；禁止通过零散外部 Dayu API 绕过四层边界；显式参数不得塞入 `extra_payload`。
- `docs/implementation-control.md` Startup Packet：当前 gate 为 `release maintenance quality gate final judgment contract accepted locally`；当前 phase 为 `release maintenance`；未开独立 Host/Agent gate 前不得创建占位 `fund_agent/host` 或 `fund_agent/agent` 包。
- `docs/implementation-control.md` Startup Packet：Next release-maintenance candidates 只有两个：`Host/Agent boundary decision` 与 `Host/Agent dependency gate`。
- `docs/implementation-control.md` Startup Packet：Host/Agent dependency gate 的 scope guard 是“仅当 Host 或 Agent 执行内核落地时，通过独立 gate 修改依赖、契约、事件流和测试”。
- `docs/design.md` §1.3：不在当前确定性 `analyze` / `checklist` 主链路中临时拼接 Host、tool loop 或 LLM 写作；进入 Agent 化路径前必须完成四层契约、依赖声明、事件流、ToolTrace、失败语义和测试 gate。
- `docs/design.md` §2.1：当前 CLI 走 UI -> Service，Service 直接调用 `fund_agent/fund` 公开能力；任何 session/run/cancel/resume/outbox 能力进入 Host 并使用 `dayu.host`；任何 tool loop/runner/ToolRegistry/ToolTrace/context budget 能力进入 Agent 并使用 `dayu.engine`。
- `docs/design.md` §2.2：当前没有 `HostRun` / `AgentInput` / scene preparation 主链路；没有明确 session/run/tool-loop 需求前，不应空造 Host 或 Agent 包，也不应引入未使用的 `dayu.host` / `dayu.engine` 依赖。
- `docs/design.md` §12：后续 plan review 必须检查四层边界、生产年报访问、禁止误拼接 Host/tool loop/LLM/Evidence Confirm/`extra_payload`、pyproject 工程基线、License/repo hygiene、Dayu 四层真源和可验证 success signal。
- 当前代码事实：`find fund_agent -maxdepth 2 -type d` 未列出 `fund_agent/host` 或 `fund_agent/agent`；`pyproject.toml` 当前生产依赖未声明 `dayu.host` 或 `dayu.engine`。
- `docs/design.md` §9.1 + 当前 `pyproject.toml` 是本地 Dayu-Agent 工程吸收基线：Python `>=3.11`，setuptools 构建，PEP 621 元数据，显式 dependencies，`test` / `dev` 可选依赖，pytest/ruff/black 配置入口，包发现排除 tests/docs/reports/scripts/workspace/cache；当前没有 `[tool.setuptools.package-data]`，因为 `fund_agent` 包内尚无需要分发的非 Python 资源。
- 外部 `dayu-agent` `pyproject.toml` 不属于本地既有事实；未来 dependency gate 如需对照外部 `dayu-agent`，必须记录精确 URL、commit/revision、获取时间、摘要内容或完整片段，以及该外部内容与本地 `docs/design.md` §9.1 / `pyproject.toml` 的差异。

## Candidate Comparison

| Candidate | Benefit | Risk | Fit Now | Decision |
|---|---|---|---|---|
| Host/Agent boundary decision | 关闭当前“Host/Agent 是否、何时、以何种最小用例落地”的边界债；为后续 dependency gate 提供进入条件；不必触碰生产代码 | 如果范围过大，容易退化为空架构设计或重新引入历史六层 / Runtime/Engine 口径 | 高。当前已有四层真源，但缺少一个可执行的下一步落地判定矩阵 | 选中，但必须窄化为文档化 planning/decision work unit |
| Host/Agent dependency gate | 可在真实 Host/Agent 落地前声明依赖、事件流和测试 | 当前没有具体 Host session/run 或 Agent tool-loop 需求；现在改依赖会违反“不引入未使用依赖”的工程基线 | 低。应依赖 boundary decision 的输出触发 | 不选中；作为后续条件 gate |

## Selected Work Unit

**Release-maintenance Host/Agent boundary decision, no package/dependency implementation.**

本 work unit 只生成一个新的 review artifact，建议路径：

`docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`

该 artifact 的目标不是实现 Host/Agent，而是给 controller 和后续 plan review 一个可执行决策：

1. 当前是否继续保持 UI -> Service -> `fund_agent/fund` 确定性过渡路径。
2. 何种具体需求才允许打开 Host implementation gate。
3. 何种具体需求才允许打开 Agent execution/tool-loop gate。
4. dependency gate 是否仍保持 blocked-until-needed。
5. 后续任何实现 gate 的最小契约、测试、文档和 stop conditions。

Required artifact section skeleton:

- `## Gate / Scope`
- `## Direct Evidence`
- `## Current-State Decision`
- `## Host Gate Entry Criteria`
- `## Agent Execution Gate Entry Criteria`
- `## Dependency Gate Status`
- `## Future Gate Skeletons`
- `## Validation Plan`
- `## Review Checklist`
- `## Stop Conditions`
- `## Decision Absorption Path`
- `## Completion Report Format`
- `## Handoff Status`

## Affected Files / Modules

本计划允许的下一 work unit 修改范围：

| Path | Change Type | Reason |
|---|---|---|
| `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Add only | 记录边界决策、证据、候选比较、进入条件、后续 gates |

本计划明确不允许修改：

| Path / Area | Reason |
|---|---|
| `fund_agent/host/` | 未开独立 Host implementation gate 前不得创建占位包 |
| `fund_agent/agent/` | 未开独立 Agent execution/tool-loop gate 前不得创建占位包 |
| `fund_agent/**` | 本 work unit 是边界决策，不改变运行时行为 |
| `tests/**` | 无生产代码行为变化；只允许在后续 implementation gate 中新增测试 |
| `pyproject.toml` / `uv.lock` | dependency gate 未触发；不声明未使用的 `dayu.host` / `dayu.engine` |
| `README.md` / package READMEs | 没有用户入口或包行为变化；如 controller 要求同步，只能在独立 docs gate 中处理 |
| `docs/design.md` / `docs/implementation-control.md` | 本 work unit 是 review artifact，不改真源或 control_doc |

## Public Contract / Schema / State-Machine / Dependency Changes

- Public contract changes: none.
- Schema changes: none.
- State-machine changes: none.
- Dependency changes: none.
- CLI behavior changes: none.
- Report/render/audit behavior changes: none.

Future gates may introduce these changes only after controller approval:

| Future Gate | Allowed Change Only If Triggered |
|---|---|
| Host implementation gate | Add `fund_agent/host` backed by `dayu.host`; define session/run lifecycle, timeout/cancel/resume/memory/outbox/event contracts and tests |
| Agent execution/tool-loop gate | Add `fund_agent/agent` backed by `dayu.engine`; define runner/tool loop/ToolRegistry/ToolTrace/context budget/failure semantics and tests |
| Host/Agent dependency gate | Modify `pyproject.toml` / `uv.lock` only when implementation imports `dayu.host` or `dayu.engine` in production code |

## Implementation Slices

Validation note:

- All `rg` commands in this plan are programmatic existence checks only. They prove required terms or guardrails are present in the artifact; they do not prove the decision is semantically correct. Semantic correctness, boundary fit, and evidence quality are covered by the plan review / re-review gates.

### Slice 1 - Evidence and Current-State Matrix

Allowed files:

- `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`

Exact changes:

- Add direct evidence table with citations to `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, current `pyproject.toml`, and directory fact that `fund_agent/host` / `fund_agent/agent` do not exist.
- Record current production path as UI -> Service -> `fund_agent/fund`.
- Record disallowed historical inputs: six-layer, Application, Runtime/Engine language in archive/review files.

Tests / validation:

- `rg -n "UI -> Service -> Host -> Agent|dayu.host|dayu.engine|extra_payload|pyproject|fund_agent/host|fund_agent/agent" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`
- `git diff --check -- docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`

### Slice 2 - Decision Matrix and Entry Criteria

Allowed files:

- `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`

Exact changes:

- Define “keep deterministic transition path” as the default decision unless a concrete lifecycle/tool-loop need exists.
- Define Host gate triggers:
  - real multi-run/session lifecycle need;
  - cancel/resume/timeout/memory/outbox/event-delivery requirement;
  - Service contract that cannot be expressed as current deterministic function orchestration.
- Define Agent execution gate triggers:
  - real runner/tool-loop need;
  - ToolRegistry / ToolTrace / context budget requirement;
  - LLM audit or Evidence Confirm execution requiring traceable tool execution.
- Define dependency gate trigger:
  - production implementation imports `dayu.host` and/or `dayu.engine`;
  - dependency bounds and package-data impact have been checked against the local baseline: `docs/design.md` §9.1 plus current `pyproject.toml`;
  - any external `dayu-agent` `pyproject.toml` comparison records URL, commit/revision, fetched content/provenance, and delta from the local baseline.

Tests / validation:

- Confirm artifact states `Host/Agent dependency gate remains blocked until implementation imports require it`.
- Confirm artifact states `no fund_agent/host or fund_agent/agent placeholder package`.
- Confirm artifact states `no explicit parameters in extra_payload`.
- `rg -n "dependency gate remains blocked|blocked until implementation imports|no fund_agent/host|no fund_agent/agent|extra_payload|local baseline|docs/design.md.*9\\.1|external dayu-agent|URL|commit|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`

### Slice 3 - Future Gate Skeletons

Allowed files:

- `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`

Exact changes:

- Add three future gate templates:
  - `Host implementation gate` with allowed files, contract requirements, test categories, README triggers.
  - `Agent execution/tool-loop gate` with allowed files, contract requirements, test categories, README triggers.
  - `Dependency gate` with `pyproject.toml`, `uv.lock`, import smoke, `uv lock --check`, package discovery, package-data checks, and local/external baseline provenance.
- Include explicit stop conditions for each future gate.
- Dependency gate command set must include, where applicable:
  - `rg -n "dayu" pyproject.toml`
  - `uv lock --check`
  - `rg -n "tool\\.setuptools\\.(packages\\.find|package-data)|include-package-data" pyproject.toml`
  - package discovery/import smoke checks for any newly introduced `fund_agent/host` or `fund_agent/agent` package.

Tests / validation:

- `rg -n "Host implementation gate|Agent execution/tool-loop gate|Dependency gate|Stop Conditions" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`
- `rg -n "rg -n .*dayu.*pyproject\\.toml|uv lock --check|tool\\.setuptools\\.packages\\.find|tool\\.setuptools\\.package-data|package discovery|package-data|URL|commit|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`
- `git diff --check -- docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`

### Slice 4 - Completion Summary

Allowed files:

- `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`

Exact changes:

- Add `Handoff status: ready for plan review` only if no blocking question remains.
- Add completion report format for the implementer.
- Add `Decision absorption path` describing how an accepted decision is recorded: controller records it in control tracking, or opens a separate docs/control update only if the accepted decision changes current truth.
- Add suggested next gate for controller: `release-maintenance Host/Agent boundary decision plan review`.

Tests / validation:

- Ensure no forbidden files changed:
  - `git diff --name-only`
  - Expected: only `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` for the next work unit.

## Docs Decision

For the selected next work unit, no README/design/control updates are part of scope.

Reason:

- It changes no runtime behavior, public CLI, package boundary, dependency graph, or current design truth.
- It records a review/decision artifact under `docs/reviews/`, which is the appropriate place for gate-local planning evidence.
- If the controller later accepts the decision and asks to update Startup Packet or design/control truth, that must be a separate controller-authorized docs/control update.

## Review Gates

Recommended next gate:

`release-maintenance Host/Agent boundary decision plan review`

Review checklist:

- Confirms current truth uses Dayu four-layer `UI -> Service -> Host -> Agent`.
- Confirms Host, if landed, must use `dayu.host`.
- Confirms Agent execution/tool-loop, if landed, must use `dayu.engine`.
- Confirms no `fund_agent/host` or `fund_agent/agent` package is created before an implementation gate.
- Confirms dependency gate remains conditional, not immediate.
- Confirms no source/test/config/README/design/control files are changed by the boundary decision artifact.
- Confirms no explicit parameter is hidden in `extra_payload` / `extra_payloads`.
- Confirms any future package/dependency change checks current `dayu-agent` pyproject baseline and local `pyproject.toml` constraints.
- Confirms production annual-report access remains through `FundDocumentRepository` / `FundDataExtractor` only.
- Confirms License/repo hygiene is preserved and not weakened by test or metadata relaxation.
- Confirms no historical six-layer/Application/Runtime/Engine wording is used as current architecture basis.

## Stop Conditions

Stop and return to controller if any of these occur:

- A reviewer asks to implement Host or Agent package in the same gate.
- A reviewer asks to add `dayu.host` / `dayu.engine` dependency without a concrete implementation import and test plan.
- A reviewer asks to revive six-layer, Application façade, Runtime/Engine naming, or old archive architecture as current truth.
- A concrete Host/session/run or Agent/tool-loop requirement is introduced that changes scope beyond a decision artifact.
- Any implementation plan requires modifying `fund_agent/**`, `tests/**`, `pyproject.toml`, `uv.lock`, README, `docs/design.md`, or `docs/implementation-control.md`.
- Any plan proposes `extra_payload` / `extra_payloads` for explicit business parameters.

Stop report format:

- Triggered condition:
- Context / evidence:
- Suggested scope adjustment:
- User decision required: yes / no

## Risks / Open Questions

Risks:

- Over-scoping the boundary decision into an architecture rewrite would violate the current release-maintenance maintenance posture.
- Premature dependency declaration would weaken the absorbed Dayu pyproject baseline by adding unused runtime dependencies.
- Creating empty packages would make the repository appear more Agentized than current code facts support.
- A purely documentary decision may be seen as insufficient unless it produces concrete future gate entry criteria; the selected work unit avoids this by requiring explicit gate skeletons and stop conditions.

Open questions:

- No blocking question for controller at this planning level.
- Non-blocking future question: which concrete product need should trigger the first real Host/Agent implementation gate: LLM audit/Evidence Confirm, asynchronous run lifecycle, or tool trace observability?

## Completion Report Format

When the selected next work unit is completed, report:

- Artifact path:
- Decision:
- Future gates opened / blocked:
- Files changed:
- Validation run: list each command, expected assertion, exit code or observed pass signal, and any skipped validation with reason.
- Decision absorption path:
- Blocking questions:
- Recommended next gate:

## Handoff Status

Handoff status: ready for plan review.
