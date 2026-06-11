# Release-readiness Cleanliness Gate Plan

日期：2026-06-11

角色：planning worker

Gate：`Release-readiness cleanliness gate`

分类：`heavy`

状态：planning artifact only。本文档不声明 release readiness，不进入 implementation/evidence，不清理 residue，不修改外部 release/PR 状态。

## 1. 当前事实与前提审查

当前控制真源为 `docs/implementation-control.md`，短启动入口为 `docs/current-startup-packet.md`。两者均指向：

- Branch：`feat/mvp-llm-incomplete-run-artifacts`。
- Active gate：`Release-readiness cleanliness gate`。
- Accepted input：Runtime artifact disposition / ignore-rule implementation evidence `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-implementation-evidence-20260611.md`，controller judgment `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-implementation-controller-judgment-20260611-150616.md`，accepted checkpoint `6bef193`。
- Control sync checkpoint：`b841ae4`。

第一性原理判断：release-readiness cleanliness 不能靠“已有 residue 被记录过”自动成立。上一个 gate 只接受了非破坏性的 inventory / owner / next-gate evidence；它明确没有接受 cleanup、`.gitignore` 修改、archive、delete、promotion、stage、PR/release 状态变更或 readiness claim。

因此，本 gate 在以下条件满足前不能 claim release readiness：

1. 当前可见 blocker residue 已被清理、忽略、归档、提升，或被 controller 明确接受为 release-readiness residual；
2. 每个 material residual 都有 owner、next gate 和不作为 release evidence 的边界；
3. 禁止命令和外部状态动作均未发生；
4. MiMo 与 DS 独立 plan review 后，由 controller judgment 裁决是否允许进入 evidence/implementation。

PR 22 相关文本若出现在 pane 或旧上下文，只能视为 residue。它不是 AgentMiMo 或 AgentDS 不可用的证据。当前 gate 必须按 MiMo 与 DS 可用来设计 review 要求。

## 2. 本计划的当前允许范围

本 planning worker 只允许写入：

- `docs/reviews/mvp-release-readiness-cleanliness-plan-20260611.md`

本计划不允许：

- 修改 source、tests、runtime behavior、README、`docs/design.md`、`.gitignore`、reports、PDF corpus 或 residue files；
- 删除、移动、archive、clean、ignore、promote、stage、commit、push、PR、mark-ready、merge 或改变外部 release 状态；
- 运行 live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands；
- 创建 review artifact 或 controller artifact。

## 3. Planning-only checks 与 future evidence checks 分离

### 3.1 Planning-only checks

本计划阶段只允许使用已接受 artifact 和只读文档事实：

| Check | Evidence source | 当前结论 |
|---|---|---|
| Gate identity | `docs/implementation-control.md`、`docs/current-startup-packet.md` | Active gate 是 `Release-readiness cleanliness gate`，classification 是 `heavy` |
| Accepted prior disposition | `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-implementation-evidence-20260611.md` | prior gate 只做 non-destructive disposition evidence |
| Controller accepted facts | `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-implementation-controller-judgment-20260611-150616.md` | residue remains visible；no readiness accepted |
| Prior residue grouping | `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` | residue groups 已有早期分类，但后续 `6bef193` evidence 是当前更近 accepted input |
| Design boundary | `docs/design.md` | current default path 仍是 deterministic analyze/checklist；`--use-llm` 是 explicit opt-in fail-closed；release/golden/readiness promotion 仍需独立 gate |

Planning 阶段不得把历史 readiness 或 PR 文本当成当前 proof。

### 3.2 Future implementation/evidence checks

只有当本 plan 经 MiMo review、DS review 和 controller judgment 接受后，future evidence worker 才可运行以下本地、非 live、非 destructive 命令。命令输出必须记录到 evidence artifact，不得自动推进 readiness。

| Purpose | Allowed local evidence command / artifact | Prohibited expansion |
|---|---|---|
| Confirm branch and worktree state | `git branch --show-current`; `git status --branch --short`; `git status --short` | 不 stage、不 commit、不 checkout、不 reset |
| Confirm no tracked/staged drift caused by this gate | `git diff --check`; `git diff --name-only`; `git diff --cached --name-only` | 不修复 whitespace，不格式化，不改 tracked files |
| Inventory untracked review artifacts | `git status --short docs/reviews`; `git ls-files docs/reviews`; metadata-only file count if needed | 不 bulk-read untracked review contents as truth |
| Verify closed source-like residue remains closed | `git status --short fund_agent/tools` | 不 recreate/import/promote `fund_agent/tools` |
| Metadata-only inventory for known residue groups | bounded `find <known-path> -maxdepth N -type f -exec ls -l {} +` for `docs/audit/`, `reports/manual-llm-smoke/`, `reviews/`, `基金年报/` only if path exists | 不读 PDF/report contents，不调用 PDF/FDR/helper/source commands |
| Verify `.gitignore` unchanged if no ignore gate is accepted | `git ls-files -s .gitignore`; `stat` metadata if needed | 不编辑 `.gitignore` |
| Verify no release evidence misuse | Future evidence artifact cross-references accepted disposition paths only | 不把 untracked residue、manual smoke reports 或 PDFs 当 release proof |
| Review process evidence | MiMo plan review artifact, DS plan review artifact, controller judgment artifact | 不以 old PR pane text 替代 reviewer output |

`uv run pytest`、`uv run ruff` 或 CLI smoke 不属于本 cleanliness planning 的最小 future evidence set；若 controller 要把 code-health release validation 并入 readiness，必须另开 release validation gate 或在 controller judgment 中显式扩展命令矩阵。当前 plan 不授权 `fund-analysis analyze/checklist/golden/readiness` 相关命令。

Future artifact names containing `<HHMMSS>` use `<HHMMSS>` only as a placeholder. When those artifacts are actually created, the placeholder must be replaced with the actual runtime timestamp.

## 4. Acceptance criteria to verifier matrix

| Acceptance criterion | Direct evidence required | Allowed verifier | Pass condition | Failure classification |
|---|---|---|---|---|
| A1 gate identity is current | Control truth and startup packet agree on active gate/classification/next entry | `docs/implementation-control.md`; `docs/current-startup-packet.md` | Both identify `Release-readiness cleanliness gate` and no readiness claim | Blocker if control truth diverges |
| A2 prior disposition accepted but not readiness | Runtime artifact disposition judgment states no cleanup/readiness accepted | Prior controller judgment and evidence artifact | `ACCEPT_WITH_RESIDUALS`; residue remains blocker | Blocker if plan treats prior gate as readiness pass |
| A3 no tracked/staged drift in current gate | Git diff/status evidence | `git diff --check`; `git diff --name-only`; `git diff --cached --name-only` | No tracked/staged files except exact future accepted write set | Blocker |
| A4 known residue groups are classified | Current inventory table maps every visible group to blocker/material residual/non-blocking residual/blocking question | `git status --short`; bounded metadata inventory; accepted disposition evidence | No unclassified visible residue remains | Blocker |
| A5 arbitrary residue is not release proof | Evidence artifact lists proof sources and excludes untracked residue as proof/source truth/fixture/release evidence | Future evidence artifact | Every proof path is tracked or accepted by exact provenance | Blocker |
| A6 blocker residue is resolved or accepted as residual | Controller judgment explicitly resolves each blocker by cleanup/ignore/archive/promotion or accepts residual owner/next gate | Future controller judgment | No unresolved blocker remains before readiness claim | Blocker |
| A7 `.gitignore` status is explicit | Either unchanged with rationale, or separate accepted ignore-rule gate exists | `.gitignore` blob/status evidence; optional future ignore-rule artifact only if authorized | No implicit ignore-rule claim | Material residual if deferred; blocker if plan claims ignored state without evidence |
| A8 user-owned / destructive paths are not touched without authorization | Evidence artifact records no delete/move/archive/cleanup and no content reads for user-owned unknowns | Future evidence artifact; metadata-only commands | `基金年报/` and similar user-owned paths untouched unless separately authorized | Blocking question if disposition requires user decision |
| A9 review gate is complete | Independent MiMo and DS plan reviews, then controller judgment | Review artifact paths and controller judgment | Both reviews present and controller accepts/accepts with amendments | Blocker if missing; PR 22 residue cannot substitute |
| A10 forbidden actions did not occur | Negative evidence section | Future evidence artifact | No live/provider/EID/PDF/FDR/analyze/checklist/golden/readiness/release/external-state actions | Blocker |

Minimum formal acceptance standard：A1-A10 must pass, or every failing item must be explicitly accepted as residual with owner, next gate, and rationale. Without that, this gate may produce evidence but cannot claim release readiness.

## 5. Known residue classification

Classification uses the current accepted disposition evidence at `6bef193`, with earlier `693638b` residue disposition used only as supporting history.

| Path / group | Current classification for release-readiness cleanliness | Evidence basis | Required future disposition |
|---|---|---|---|
| Accepted current-gate artifacts from prior disposition gate | Non-blocking residual | Prior controller judgment accepted exact evidence/review/judgment set | No action unless path-level correction is needed |
| Other untracked `docs/reviews/*.md` / `*.json` | Blocker | `6bef193` evidence: yes until classified, accepted as residual, or cleaned under authorization | Exact path-level provenance, accepted residual, or authorized cleanup/promotion |
| `docs/audit/` | Blocker until classified; likely material residual after controller acceptance | Deepreview input is evidence-chain only and cannot override truth docs | Review-artifact disposition gate or accepted residual owner |
| `docs/learning-roadmap.md` | Material residual; blocker to readiness claim until accepted residual/disposition | Research input, not control truth | Accept as non-release residual or route to research-doc disposition gate |
| `docs/next-development-phaseflow.md` | Material residual; blocker if used as control truth | Planning/research input, not `docs/implementation-control.md` | Accept as non-release residual or route to phaseflow planning disposition |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | Blocking question if cited as current design; otherwise material residual | Candidate design cannot override `docs/design.md` | Design-truth-sync gate if used; otherwise accepted research residual |
| `docs/tmux-agent-memory-store.md` | Material residual | Ops/research note; archive needs exact gate | Accept residual or route to ops artifact disposition |
| `reports/manual-llm-smoke/` | Blocker | Runtime/live evidence residue; not accepted as release proof | Runtime evidence disposition gate, accepted residual, ignore-rule gate, or authorized cleanup |
| `reviews/` | Blocker | Obsolete duplicate / external review residue outside canonical `docs/reviews/` | Artifact disposition gate; archive/delete requires authorization |
| `scripts/claude_mimo_simple.py` | Material residual; blocker if imported, promoted, or used as proof | Scratch helper/tooling residue | Tooling residue disposition or accepted non-release residual |
| `基金年报/` | Blocking question | User-owned unknown / local PDF corpus; production PDF access must go through `FundDocumentRepository`; deletion/ignore/move needs explicit decision | User/controller decision: accepted local-data residual, scoped ignore, move/archive, or delete authorization |
| `定性分析模板.md` | Material residual; blocker if cited as template truth | User/research input; canonical template remains `docs/fund-analysis-template-draft.md` | Accept residual or route to template research disposition |
| `fund_agent/tools` exact source-like residue | Non-blocking residual, closed for exact prior case | Prior evidence: `git status --short fund_agent/tools` empty; control doc records closure at `11040bd` | No action unless it reappears |
| `.gitignore` candidate patterns | Material residual, not implemented | Prior evidence deferred patterns; no `.gitignore` edit occurred | Separate ignore-rule gate if controller wants durable ignore behavior |
| PR 22 pane/context text | Non-blocking residue | User instruction and current control truth: old PR text is residue only | Do not use as reviewer availability evidence or release proof |

Evidence authority note：current classification authority is checkpoint `6bef193` and the current control truth. Earlier `693638b` / control-compression residue evidence is supporting history only; it cannot override `6bef193` or the current control surface.

Current blocker conclusion：this gate cannot claim release readiness while blocker groups remain unresolved or not explicitly accepted as residuals by controller judgment.

## 6. Future write set

This plan authorizes no implementation writes by itself. If accepted by review/controller judgment, the exact future write set is:

### 6.1 Plan review and controller judgment write set

- `docs/reviews/mvp-release-readiness-cleanliness-plan-review-mimo-20260611.md`
- `docs/reviews/mvp-release-readiness-cleanliness-plan-review-ds-20260611.md`
- `docs/reviews/mvp-release-readiness-cleanliness-plan-controller-judgment-20260611-<HHMMSS>.md`

These are reviewer/controller artifacts only. They must not modify source, tests, runtime behavior, `.gitignore`, reports, PDFs or existing residue files.

### 6.2 Future evidence gate write set, only after plan acceptance

- `docs/reviews/mvp-release-readiness-cleanliness-evidence-20260611.md`
- `docs/reviews/mvp-release-readiness-cleanliness-evidence-review-mimo-20260611-<HHMMSS>.md`
- `docs/reviews/mvp-release-readiness-cleanliness-evidence-review-ds-20260611-<HHMMSS>.md`
- `docs/reviews/mvp-release-readiness-cleanliness-evidence-controller-judgment-20260611-<HHMMSS>.md`

### 6.3 Controller status sync write set, only after evidence acceptance

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Controller status sync may record accepted evidence, residual owners, next entry point and accepted checkpoint. It must not claim release readiness unless A1-A10 pass or unresolved items are explicitly accepted as residuals.

No `.gitignore`, source, tests, README, `docs/design.md`, report, PDF, archive, cleanup, promotion, stage, commit, push or PR write is included in this plan. Any such action requires a new accepted plan or explicit controller/user authorization with exact paths.

## 7. Review requirements

Required sequence:

1. AgentMiMo independent plan review.
2. AgentDS independent plan review.
3. Controller judgment that reconciles both reviews, accepted amendments, residual owners and whether future evidence worker may proceed.

MiMo and DS are usable for this gate. PR 22 pane text, old PR context, stale tmux output or historical review-channel residue must not be treated as MiMo/DS unavailability evidence. If a reviewer actually fails during this gate, the controller must record fresh, direct failure evidence and decide reroute separately.

## 8. Stop conditions

Stop and report instead of proceeding if:

- next action would modify source, tests, runtime behavior, README, `docs/design.md`, `.gitignore`, reports, PDF corpus or existing residue files;
- next action would delete, move, archive, clean, ignore, promote, stage, commit, push, PR, mark-ready, merge or mutate external release state;
- next action would run live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands;
- current inventory reveals a new source-like or tracked-diff residue outside the exact write set;
- future evidence inventory discovers any visible residue group not covered by §5; evidence worker must stop and report rather than classifying opportunistically;
- a residue group requires destructive cleanup or user-owned path disposition, especially `基金年报/`, without explicit user/controller authorization;
- MiMo or DS review is missing and controller has not explicitly accepted a reviewer-risk residual based on fresh direct evidence;
- any plan/review/controller artifact attempts to use untracked residue as source truth, fixture, product scope, release evidence or readiness proof.

## 9. Non-goals

- No release readiness claim.
- No PR readiness claim.
- No release, merge, mark-ready, request-reviewer, external comment or GitHub mutation.
- No cleanup, archive, delete, move, ignore-rule implementation, `.gitignore` edit, or promotion.
- No functional code/test/runtime behavior change.
- No provider/default/runtime budget/config/retry/fallback/source-policy change.
- No live provider, EID, PDF, FDR, FundDocumentRepository, helper, extractor, analyze, checklist, golden, readiness, score-loop or release command.
- No Host durable runtime, Agent full tool-loop/runtime expansion, dayu production dependency, fixture promotion, golden promotion or quality gate semantic change.
- No direct filesystem use of PDF corpus as production proof.

## 10. Recommended next handoff

Handoff target：AgentMiMo and AgentDS plan reviewers.

Review prompt should ask only:

- Does this plan preserve the heavy release-readiness boundary without claiming readiness?
- Is the verifier matrix sufficient and limited to allowed local evidence?
- Are blocker/material residual/non-blocking residual/blocking question classifications consistent with accepted disposition evidence?
- Is the future write set exact enough to prevent cleanup, `.gitignore`, source/test, PR or release drift?
- Are MiMo/DS availability and PR 22 residue handled correctly?

After both reviews, controller judgment must either accept the plan, accept with exact amendments, or reject with blocking findings. No evidence worker should proceed before controller judgment.
