# DS Plan Review: MVP Release-readiness Residual / Artifact Disposition Plan

日期：2026-06-12

Reviewer role：DS independent plan reviewer only。未参与 plan 编写，不充当 controller。

Review target：`docs/reviews/mvp-release-readiness-residual-artifact-disposition-plan-20260612.md`

Truth inputs used：

- `AGENTS.md`
- `docs/design.md` v2.18（§1–§2 当前架构/边界/裁决章节）
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-implementation-controller-judgment-20260612-002524.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-release-readiness-cleanliness-evidence-controller-judgment-20260611-153309.md`
- `docs/reviews/mvp-review-artifact-provenance-disposition-evidence-controller-judgment-20260611-160126.md`
- `docs/reviews/mvp-review-artifact-residual-acceptance-plan-controller-judgment-20260611-162326.md`

附加验证：

- `git status --short`（完整输出）
- `git status --branch --short`
- 精确 counts：`docs/reviews/` untracked（排除本 plan 后）、`docs/audit/`、`reports/live-evidence/`、`fund_agent/tools/`

---

## Verdict

`ACCEPT`

本 plan 保持 planning-only 范围，正确分离了 repo facts / truth-doc facts / prior judgment，Stage A 对 evidence worker 足够精确，allowed read/write sets 收窄且不含 source/test/runtime/truth-doc 修改，mainline entry 是单一路由且 deferred entries 保持 deferred，`NOT_READY` 在所有 stage 中保留。无 blocking finding。

---

## Blocking Findings

无。

---

## Non-blocking Findings

### N1 — Review/audit count delta from prior provenance manifest 未显式说明

- **Severity**：low
- **Evidence**：
  - Prior provenance controller judgment（20260611-160126）确认 manifest 覆盖 35 条 exact 路径：34 `docs/reviews/` + 1 `docs/audit/`。
  - 当前 `git status --short`（排除本 plan 后）显示 35 untracked `docs/reviews/` 路径 + 1 `docs/audit/` 文件 = 36 total。
  - Plan §3.1 列出 "35 exact `docs/reviews/*` paths" 和 `docs/audit/` 为独立 families，未说明 docs/reviews 从 34→35 的 delta（+1 path）。
- **Risk**：Stage A acceptance criteria 要求 "newly visible paths not present in the prior manifest are called out as new residue, not silently accepted"。若不显式标注 delta，evidence worker 可能遗漏那条新路径的分类。
- **Mitigation**：Stage A allowed read set 包含了 prior provenance evidence（含 34-path manifest），worker 可自行 cross-reference 找出 delta。Plan 无需修订即可执行。
- **Recommendation**：Controller 可在 handoff 中提醒 evidence worker 显式对比 prior manifest 并标注 new-vs-existing。

### N2 — Plan 自身未列入 Stage A allowed read set

- **Severity**：low
- **Evidence**：Stage A §5 allowed read set 列出 8 个 truth/evidence 文件，不含本 plan 自身。Evidence worker 执行 Stage A 需要读本 plan 才能知道 required output fields、classification values、acceptance criteria 和 validation matrix。
- **Risk**：形式上的 omission，实际执行时 worker 必然读 plan。不影响可执行性。
- **Recommendation**：无需修订；controller handoff 时自然包含。

### N3 — Classification taxonomy 与 prior provenance evidence 的分类名存在轻微 drift

- **Severity**：low
- **Evidence**：
  - Prior provenance evidence 使用：`REJECT_AS_RELEASE_EVIDENCE`、`DEFERRED_CANDIDATE`、`USER_OR_CONTROLLER_DECISION_REQUIRED`。
  - Stage A 要求使用：`KEEP_REJECTED_AS_RELEASE_EVIDENCE`、`DEFER_PROVENANCE_REQUIRED`、`USER_OR_CONTROLLER_DECISION_REQUIRED`、`ACCEPT_AS_NON_RELEASE_RESIDUAL`、`NEW_UNINDEXED_REVIEW_RESIDUE`。
  - `REJECT_AS_RELEASE_EVIDENCE` → `KEEP_REJECTED_AS_RELEASE_EVIDENCE` 和 `DEFERRED_CANDIDATE` → `DEFER_PROVENANCE_REQUIRED` 的语义桥接未在 plan 中显式文档化。
- **Risk**：Evidence worker 需自行判断 prior classification 到新 classification 的映射。Prior evidence 在 allowed read set 中，可桥接。
- **Recommendation**：Evidence worker 应在 evidence artifact 中显式记录每条路径的 `prior_classification`（来自 prior provenance manifest）和新的 `classification`，使桥接可审计。

### N4 — `status_seen` 字段值空间未定义

- **Severity**：low
- **Evidence**：Stage A required output fields 包含 `status_seen`，但 plan 未定义其允许值（如 `untracked`、`tracked`、`missing` 等）。
- **Risk**：Evidence worker 可能使用不一致的值，导致后续 reviewer 需要额外澄清。
- **Recommendation**：Evidence worker 应在 evidence artifact 开头定义 `status_seen` 的值空间。无需修订 plan。

### N5 — Stage B 允许的 metadata commands 表述偏模糊

- **Severity**：low
- **Evidence**：Stage B 允许 "path listing/counting commands that do not read file contents, if controller authorizes them in the handoff." 未列出 exact commands（对比 Stage A 列出了 `git status --short`、`git status --branch --short`、`git diff --check`）。
- **Risk**：Stage B 是 deferred gate，需单独授权后才执行。届时模糊性可由 controller handoff 消除。
- **Recommendation**：Controller 在授权 Stage B 执行时，应在 handoff 中列出 exact allowed metadata commands（如 `find reports/live-evidence -maxdepth 3 -type f`、`find reports/manual-llm-smoke -maxdepth 3 -type f`、`git status --short reports/`）。

### N6 — §3.3 prior judgment 摘要中存在少量 truth-doc fact 混入

- **Severity**：low
- **Evidence**：§3.3 下第二条摘要 "Current deterministic analyze-annual-period product path is accepted as code fact, including explicit annual_period_report" 本质上是 truth-doc fact（design.md / startup packet 均有记录），不是 controller judgment 的独立裁决。放在 §3.3 会轻微削弱 fact separation 的清晰度。
- **Risk**：不影响可执行性。不影响 fact separation 的主体结构（3.1/3.2/3.3 三层分离仍然清晰）。
- **Recommendation**：无需修订。

---

## Review Lens 逐项验证

### 1. Planning-only scope, no implementation/cleanup/live/PR/release drift

**Pass。** Plan §0 self-check 声明 "planning worker only"，§2 non-goals 显式禁止 source/test/runtime 修改、删除/移动/归档/清理、live 命令、PR/release 动作。§6 单独列出需独立授权的禁止事项。Stages A–D 的 allowed write sets 全部限定为 `docs/reviews/` 下的 evidence/review/judgment artifacts，不含任何 source/test/runtime/truth-doc 写入。

### 2. Fact separation: repo facts vs truth-doc facts vs prior reviewer/controller judgment

**Pass with N6 remark。** §3.1 严格基于 `git status` 输出，标注 "These are inventory facts only"。§3.2 显式引用 startup packet、implementation-control、design.md 的具体段落，每条标注来源。§3.3 正确摘要 5 个 prior controller judgment 的 verdict 和关键 residual。N6 记录的轻微混入不影响主体分离。

已验证的 repo facts 对照当前 `git status`：

| Plan claim | Current verification | Match |
|---|---|---|
| 35 `docs/reviews/*` untracked（pre-plan） | 35（36 total - 1 plan） | ✓ |
| `docs/audit/` untracked | 1 file | ✓ |
| `reports/live-evidence/` untracked | 3 files, new family | ✓ |
| `reports/manual-llm-smoke/` untracked | present | ✓ |
| `fund_agent/tools/` absent | `git status --short fund_agent/tools/` exit 0, no output | ✓ |
| Branch ahead 128 | `ahead 128` | ✓ |

### 3. Stage A exactness for evidence worker without redesign

**Pass with N1/N3/N4 remarks。** Stage A 提供了：

- 精确的 allowed read set（8 个文件）
- 精确的 metadata commands（3 条 git 命令）
- 精确的 allowed write set（2 类 artifact + reviews + judgment）
- 精确的 required output fields（10 个字段，含 exact `path`）
- 精确的 classification taxonomy（5 个值）
- 精确的 acceptance criteria（4 条）
- 精确的 validation matrix（3 条检查，含 expected assertion 和 failure handling）

Evidence worker 拿到 handoff 后可直接执行，不需 redesign classification 体系或字段语义。N1/N3/N4 的 minor ambiguities 均可通过 allowed read set 中的 prior evidence 和 worker 自身判断解决。

### 4. Allowed read/write sets and forbidden actions

**Pass with N2/N5 remarks。**

- Stage A allowed read：8 个文件，均为 truth docs + prior residue/provenance/acceptance evidence + controller judgments。不含 source/test/runtime/README/design-truth 写入权限。
- Stage A allowed write：`docs/reviews/mvp-review-artifact-residual-acceptance-evidence-20260612.md` + reviews + controller judgment。不含实现文件或 truth doc。
- Stage A forbidden：reading untracked content as truth、accepting rejected paths as release evidence、cleanup/archive/delete/move 等动作。与 §2 non-goals 和 §6 一致。
- Stages B–D 的 read/write sets 遵循同样收窄模式。

### 5. Mainline entry is one route, deferred entries stay deferred

**Pass。** §7 明确：

- Mainline：`Review-artifact residual acceptance evidence gate`
- Deferred：Runtime/live report、Research/user-owned/tooling、Ignore-rule policy、Archive/delete/cleanup、Controlled live annual-period narrative evidence、Release-readiness cleanliness re-evidence、PR/push/merge/mark-ready/release

Mainline 选择与 prior controller judgment（residual acceptance planning 20260611-162326）的 deferred routing 一致，也与当前 startup packet 的 "Next entry point: Planning worker for release-readiness residual/artifact disposition" 一致。Deferred entries 均标注了触发条件（"only if…"、"only after…"、"only with…"），不会意外提升。

### 6. NOT_READY preserved unless later direct evidence proves otherwise

**Pass。** NOT_READY 在 plan 中多处显式保留：

- §2 non-goals：禁止 "accepting release readiness, PR readiness, golden promotion, additional live samples or all-market acceptance"
- Stage A acceptance criteria："release/readiness remains `NOT_READY`"
- Stage B acceptance criteria："release/readiness remains `NOT_READY`"
- Stage D acceptance criteria："if unresolved blocker remains, result must stay `NOT_READY`"；"if no blockers remain, controller may decide whether a separate readiness gate is required before any readiness claim"
- §6 separate authorization：禁止 PR/push/merge/mark-ready 和 release-state changes

Plan 在任何 stage 都没有授权将 NOT_READY 翻转为 READY。Stage D 的 escape hatch（"controller may decide whether a separate readiness gate is required"）也要求在 cleanliness re-evidence pass 之后且需独立 gate，不是本 plan 范围内可触发。

---

## Controller Disposition Recommendation

**建议 controller 以 ACCEPT 接受本 plan 为 release-readiness residual/artifact disposition 的 controlling plan。**

Handoff 给 Stage A evidence worker 时建议附带以下提醒：

1. 显式对比 prior provenance manifest（34 `docs/reviews/` + 1 `docs/audit/`）与当前 status（35 + 1），在 evidence artifact 中标注 new-vs-existing delta。
2. 在 evidence artifact 开头定义 `status_seen` 的值空间。
3. 每条路径显式记录 `prior_classification`（来自 provenance evidence）和新的 `classification`，使 taxonomy bridge 可审计。
4. Stage B/C/D 的 exact metadata commands 由 controller 在各 stage handoff 时列出。

---

## Validation

```text
git status --short          → 无 unexpected tracked/source/test/runtime diff
git status --branch --short → feat/mvp-llm-incomplete-run-artifacts [ahead 128]
git diff --check            → pass（本 review artifact 写入后执行）
```

---

## Residuals

| Residual | Owner | Status |
|---|---|---|
| N1–N6 non-blocking findings | Controller / Stage A evidence worker | 在 handoff 或 evidence artifact 中处理；无需修订 plan |
| Plan 自身不在 Stage A allowed read set（N2） | Controller | Handoff 时自然包含 |
| Stage B exact metadata commands 待后续指定（N5） | Controller | Stage B 授权时列出 |

---

## Forbidden Actions Confirmed Not Performed

- 未修改 source/test/runtime/truth docs
- 未运行 live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release 命令
- 未 stage/commit/push/PR/merge/delete/move/archive/cleanup/ignore
- 仅写入本 DS review artifact
