# Post-P12 Planning（2026-05-22）

- **Role**: AgentCodex planning specialist
- **Gate**: `post-P12 planning`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **P12 closeout**: `docs/reviews/p12-main-branch-closeout-20260522.md`
- **P12 aggregate judgment**: `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md`
- **Output only**: 本 artifact 只规划下一阶段；不改 source/test/README/control doc，不 commit、不 push、不建 PR。

## 1. Goal / Motivation

选择 P12 closed-on-main 后的下一条最小、最直接、风险收益最高的 phase/work unit，或建议进入 release/maintenance closeout。

推荐选择：**release/maintenance closeout and main-branch readiness reconciliation**。

理由：P12 已关闭 ITEM_RULE deterministic compliance，aggregate review 双 PASS，full suite `403 passed`。当前剩余项中，真实 tracking-error/index methodology/constituents 抽取和 E1-E3/Evidence Confirm 都是新的产品/审计能力，scope 与风险明显高于一个 follow-up closeout；RR-13 需要 user/App source truth；`docs/repo-audit-20260521.md` 是旧 baseline 的未跟踪候选输入，不应在没有新 repo-hygiene scope 的情况下发布。最短安全路径是先做 main-branch readiness / maintenance closeout，把当前 release lane 的状态、残余项和 untracked repo-audit 处置口径收口，再由后续 phase 明确选择是否进入 P13 产品能力。

## 2. Direct Evidence

- `docs/implementation-control.md` Startup Packet：Current gate 为 `P12 closed on main`，Next entry point 为 `post-P12 planning`，Product baseline 为 `P10 release-readiness merged; P11 control-doc recovery accepted; P12 closed on main`。
- `docs/reviews/p12-main-branch-closeout-20260522.md` 裁决 `CLOSED_ON_MAIN`：P12 commits 已在 `main`，不适用 retroactive draft PR gate；正确路径是 main-branch closeout artifact + control-doc reconciliation。
- `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md` 裁决 `ACCEPTED`：MiMo/GLM aggregate review 均 `PASS`，无 blocking 或 non-blocking findings；controller 验证 targeted `83 passed`、adjacent `43 passed`、ruff passed、diff check passed、full suite `403 passed`。
- `docs/reviews/p12-aggregate-deepreview-controller-judgment-20260522.md` accepted facts：P12-S1/S2 已完成 renderer-produced ITEM_RULE decisions/context、chapter-scoped C2 verification、multi-anchor provenance display；FQ5/quality gate semantics 未扩张；未跨 Service/UI/CLI/Engine/runtime/documents/source repository/Dayu 边界。
- `docs/design.md` 仍定义当前主链路为 deterministic UI -> Service -> Fund Capability；LLM audit / Evidence Confirm 是 v2；Dayu Host/Engine/tool loop 不是当前生产依赖。
- `docs/design.md` 与 `AGENTS.md` 均要求生产年报访问经 `FundDocumentRepository`；因此任何 tracking-error/index methodology/constituents 真数据能力都必须作为 Fund Capability documents/extractor/analysis 契约设计，不能让 Service/UI 直接读内部来源。
- `docs/implementation-control.md` Active Residuals：RR-13 duplicate `016492` human-owned；`docs/repo-audit-20260521.md` excluded unless later scope explicitly accepts publication；P12 evidence/extractor follow-ups deferred。
- `docs/repo-audit-20260521.md` 是 P8-era 仓库审核输入。部分事实已被 P10/P11/P12 后续工作覆盖或过时；仍 open 的 repo/doc hygiene candidates 包括 D-1 `docs/design.md` 项目结构树、D-8/C-5 `fund/tools` 目录事实核对、C-9 `docs/reviews/` 目录膨胀。这些不阻塞 maintenance closeout，但必须作为 future repo-hygiene residual，而不能被记为已覆盖。

## 3. Candidate Comparison

| Candidate | Product / safety value | Scope / risk | Boundary fit | Decision |
|---|---:|---:|---:|---|
| Release/maintenance closeout and main-branch readiness | 中到高：把 P12 closed-on-main 后的 release lane、residual owners、repo-audit exclusion 和 next entry 收口 | 低：docs-only reconciliation / validation evidence | 高 | **Selected** |
| P13 real tracking-error/index methodology/constituents extractor/calculation | 高：填充当前指数相关 `数据不足` placeholders | 高：需新增数据源、schema、cache、计算口径、source fallback、tests | 可行但必须在 Fund Capability 内设计 | Defer to future P13 product phase |
| Evidence sufficiency / E1-E3 audit or Evidence Confirm | 高：解决证据与断言匹配 | 高：设计上属于 v2 audit layer，可能引入 LLM/Evidence Confirm/repair contract | 需重新设计边界，不能借 Dayu runtime | Defer to future audit architecture phase |
| Repo/doc hygiene incl. `docs/repo-audit-20260521.md` publication | 中：可降低未跟踪输入噪音 | 中：repo-audit baseline 旧，发布可能制造历史事实混淆 | 可作为 docs-only phase | Defer; closeout explicitly keeps repo-audit untracked/excluded |
| RR-13 duplicate `016492` | 中：精选池源数据身份冲突 | 高：必须用户/App source 决策，代码不能推断 | 不适合作为 agent-only implementation | Keep human-owned |
| Product-safety micro-slice: audit noise cleanup for chapter-mismatched ITEM_RULE | 低：当前已 fail-closed | 低 | 可行但收益弱 | Defer |
| Product-safety micro-slice: long-anchor truncation/grouping | 低：当前无 real large anchor set | 中：需要 Markdown UX contract | 可行但 premature | Defer |
| Product-safety micro-slice: future ITEM_RULE dispatch abstraction | 低到中：只有新增规则时有收益 | 中：当前无新增 ITEM_RULE pressure | 可行但 premature | Defer |

## 4. Recommended Next Gate

Proceed to:

```text
release/maintenance closeout and main-branch readiness reconciliation
```

This is a docs-only/controller reconciliation work unit, not a source implementation phase. It should confirm the current `main` branch is release/maintenance-ready after P12, record that `docs/repo-audit-20260521.md` remains excluded/untracked, and explicitly defer product-expansion candidates to future phases.

Recommended artifact path for the next gate:

```text
docs/reviews/post-p12-release-maintenance-closeout-20260522.md
```

After that closeout passes review, the controller may either:

- stop the current release lane as `maintenance-ready`, or
- open a new planning gate for a real P13 product phase, with fresh scope and branch handling.

## 5. Non-goals

- Do not reopen P12 unless a new production or aggregate regression is discovered.
- Do not implement real tracking-error, index methodology, constituents extraction, daily NAV/index series, or new document source.
- Do not implement E1/E2/E3, LLM audit, Evidence Confirm, RepairContract, LLM writing, Host, Engine, tool loop, prompt scene registry, or Dayu runtime.
- Do not modify Service/UI/CLI or let them directly read document repository internals.
- Do not modify `FundDocumentRepository`, PDF/cache helpers, source fallback taxonomy, source repository internals, or quality gate semantics.
- Do not auto-resolve RR-13 duplicate `016492`.
- Do not publish, stage, edit, or delete `docs/repo-audit-20260521.md` in this selected closeout unless the user separately authorizes deletion/disposal.
- Do not add release publishing automation, version tags, changelog, or time-sensitive release notes.

## 6. Scope / Allowed Files

For this planning artifact:

- Allowed file: `docs/reviews/post-p12-planning-20260522.md` only.

For the recommended next closeout gate:

- Allowed files:
  - `docs/reviews/post-p12-release-maintenance-closeout-20260522.md`
  - optional review/controller judgment artifacts under `docs/reviews/`
  - `docs/implementation-control.md`
- Required `docs/implementation-control.md` updates:
  - update Startup Packet for the new accepted post-P12 planning artifact;
  - add an Active Gate Ledger row for `post-P12 planning`;
  - update Current gate / Next entry point after closeout acceptance;
  - keep residual owner table consistent with the closeout artifact.
- Disallowed files:
  - source code under `fund_agent/`
  - tests under `tests/`
  - README files unless a concrete stale statement is discovered during review
  - `docs/design.md`
  - `docs/repo-audit-20260521.md`
  - RR-13 source data such as selected-fund CSV rows

Closeout should not stage or publish the untracked repo-audit file. If the controller wants it removed from the filesystem, that is a separate destructive local cleanup decision requiring explicit user approval.

Minimum `maintenance-ready` acceptance criteria:

- current branch is `main`;
- no tracked uncommitted source/test/doc changes exist except allowed closeout artifacts and `docs/implementation-control.md`;
- `pytest`, `ruff check fund_agent tests`, and `git diff --check HEAD` pass;
- `git diff --name-only HEAD` contains only allowed closeout files;
- all residuals have explicit owner/destination;
- `docs/implementation-control.md` Startup Packet, Active Gate Ledger, and Next entry point match the actual closeout status.

## 7. Closeout Steps

### Step 1: Main-branch readiness evidence

Objective: prove the current branch is coherent after P12 closeout.

Required checks:

```bash
git branch --show-current
git status --short
git log --oneline -10
git diff --name-only HEAD
pytest
ruff check fund_agent tests
git diff --check HEAD
```

Expected:

- branch is `main`;
- no tracked source/test/doc changes are pending for the closeout gate;
- `git diff --name-only HEAD` lists only allowed closeout files;
- `docs/repo-audit-20260521.md` may remain untracked and excluded;
- full suite remains at current baseline or higher (`403 passed` was P12 closeout baseline);
- ruff and diff check pass.

### Step 2: Repo-audit disposition record

Objective: explicitly decide current handling of `docs/repo-audit-20260521.md` without publishing it.

Required content in closeout artifact:

- It is an older P8-era audit input, not a current accepted project artifact.
- Current control doc already marks it excluded unless future scope explicitly accepts publication.
- Its suggestions must be split by status:
  - partially covered by later work: items that P10/P11/P12 already reconciled or made obsolete;
  - still open repo/doc hygiene candidates: D-1 `docs/design.md` project structure tree, D-8/C-5 `fund/tools` directory fact check, C-9 `docs/reviews/` directory growth;
  - out of current scope: product or historical observations not relevant to maintenance closeout.
- Open repo/doc hygiene candidates do not block maintenance closeout, but must appear in residual tracking with future repo-hygiene ownership.
- It remains untracked/excluded. No deletion is performed without user approval.

### Step 3: Residual owner reconciliation

Objective: preserve all remaining work with owner/destination.

Required residual table:

- real tracking-error extraction/calculation -> future Fund Capability extractor/calculation phase;
- real index methodology / constituents extraction -> future documents/extractor phase through `FundDocumentRepository`;
- E1/E2/E3 / Evidence Confirm -> future audit architecture phase;
- long-anchor truncation/grouping -> future evidence-display UX slice only when real large anchor sets appear;
- future ITEM_RULE expansion -> future rule-addition slice;
- chapter-mismatch duplicate C2 noise -> future maintainability cleanup if issue volume becomes material;
- RR-13 duplicate `016492` -> user/App source; if still unresolved before the next product phase, make it an explicit blocking input to that phase's planning instead of letting an agent auto-fix it;
- repo-audit disposition -> controller/user; keep excluded unless future repo-hygiene phase owns it.

### Step 4: Next-lane recommendation

Objective: avoid accidentally starting a high-scope product phase from stale residuals.

Required recommendation:

- Current release lane can stop at maintenance-ready if validation passes.
- If the user wants a product phase next, the safest P13 candidate is not immediate implementation; first gate should be a dedicated P13 design/plan for tracking-error/index-data capability with explicit source contracts.
- Evidence Confirm / E1-E3 should be a separate audit architecture phase, not mixed with data extraction.

## 8. Validation / Review Gates

Plan review criteria for this artifact:

- Does the recommendation correctly avoid reopening P12?
- Does it compare all required candidates and preserve owners for deferred residuals?
- Does it keep repo-audit untracked/excluded unless explicitly scoped?
- Does it avoid Service/UI direct document-source access and Dayu/LLM runtime expansion?
- Are closeout allowed files and validation commands concrete enough for controller execution?

Recommended closeout review:

- One reviewer is sufficient for docs-only closeout if no source/test/control changes are made.
- If `docs/implementation-control.md` is updated during closeout, use at least one independent review to verify Active Gate Ledger / Startup Packet consistency.
- If any source/test/README change becomes necessary, stop this closeout and open a proper gated implementation plan.

Validation commands for the next closeout gate:

```bash
git status --short
git diff --name-only HEAD
pytest
ruff check fund_agent tests
git diff --check HEAD
```

Expected assertions:

- No tracked source/test/README changes.
- `git diff --name-only HEAD` lists only allowed files: closeout artifacts under `docs/reviews/` and `docs/implementation-control.md`.
- `docs/repo-audit-20260521.md` is not staged or published.
- P12 artifacts remain referenced in control truth.
- Full suite, ruff, and diff check must pass. If `pytest`, `ruff`, or diff check fails, closeout must stop; it may continue only if the controller explicitly confirms the failure is unrelated to closeout scope and records that confirmation in the closeout artifact.

## 9. Residual Tracking / Owners

| Residual | Decision | Owner / destination |
|---|---|---|
| Real tracking-error extraction/calculation | Defer; too large for maintenance closeout | Future P13 Fund Capability extractor/calculation design |
| Real index methodology / constituents extraction | Defer; requires new document/source design | Future P13 documents/extractor design through `FundDocumentRepository` |
| Evidence sufficiency / E1-E3 / Evidence Confirm | Defer; v2 audit architecture | Future audit architecture phase |
| Long-anchor truncation/grouping | Defer until real large anchor sets exist | Future evidence-display UX slice |
| Future ITEM_RULE expansion | Defer until new manifest entries exist | Future rule-addition slice |
| Chapter-mismatch duplicate C2 noise | Defer; fail-closed today | Future maintainability cleanup |
| RR-13 duplicate `016492` | Keep human-owned; if unresolved before the next product phase, treat as explicit blocking input to that phase planning | User / App source |
| `docs/repo-audit-20260521.md` | Keep excluded/untracked | Controller / user; future repo-hygiene phase may explicitly publish, archive, or delete with approval |
| Repo/doc hygiene suggestions from repo-audit | Defer; D-1 project structure tree, D-8/C-5 `fund/tools` fact check, and C-9 reviews directory growth remain open candidates | Future repo-hygiene phase if selected |

## 10. Open Questions

No questions block closeout execution.

Non-blocking choices for controller:

- Which concrete Next entry point to write into `docs/implementation-control.md` after closeout acceptance: stop as `maintenance-ready`, or enter a new phase planning gate.
- Whether the user wants to delete the local untracked `docs/repo-audit-20260521.md`; deletion is outside this plan and should require explicit approval.
- Whether the next product lane should be P13 tracking-error/index-data design or an audit architecture phase; this plan recommends deciding only after maintenance closeout.

## 10.1 Plan Review Response / Finding Disposition

| Finding | Source | Disposition | Plan update |
|---|---|---|---|
| repo-audit 建议状态描述不准确 | MiMo #1 | accepted | §2、§7 Step 2、§9 现在明确区分已覆盖项与仍 open 的 repo/doc hygiene candidates，并点名 D-1、D-8/C-5、C-9。 |
| allowed files 缺少 control doc Active Gate Ledger 更新 | MiMo #2 | accepted | §6 将 `docs/implementation-control.md` 升级为 required allowed file，并列出 Startup Packet、Active Gate Ledger、Current gate / Next entry point、residual owner table 更新要求。 |
| `maintenance-ready` 状态无定义 | MiMo #3 | accepted | §6 新增 minimum `maintenance-ready` acceptance criteria。 |
| validation 缺少 `git diff --name-only` 检查 | MiMo #4 | accepted | §7 和 §8 增加 `git diff --name-only HEAD`，并要求输出只包含 allowed files。 |
| RR-13 缺少用户不响应时的升级路径 | MiMo #5 | accepted | §7 Step 3 和 §9 现在要求如果 RR-13 在下一次产品 phase 前仍未裁决，应作为该 phase planning 的显式 blocking input，而不是 agent 自动修复。 |
| validation assertion 允许 unrelated failure 继续 | GLM F1 | accepted | §8 改为 pytest/ruff/diff check 失败必须 stop；只有 controller 显式确认 unrelated 并记录后才能继续。 |
| “No blocking open questions” 措辞可能误导 | GLM F2 | accepted | §10 改为“没有阻断 closeout 执行的问题”，并移除 control-doc 是否更新的混淆口径，改为选择具体 Next entry point。 |

## 11. Controller Handoff

Recommended controller prompt for the next gate:

```text
Gate: release/maintenance closeout and main-branch readiness reconciliation.

Use `docs/reviews/post-p12-planning-20260522.md` as the accepted planning input.

Task:
- Create `docs/reviews/post-p12-release-maintenance-closeout-20260522.md`.
- Update `docs/implementation-control.md` Startup Packet, Active Gate Ledger, Current gate / Next entry point, and residual owner table after closeout acceptance.
- Do not change source/test/README/design/repo-audit.
- Verify current `main` readiness with `git status --short`, `git diff --name-only HEAD`, `pytest`, `ruff check fund_agent tests`, and `git diff --check HEAD`.
- Assert `git diff --name-only HEAD` contains only allowed closeout files.
- Record that P12 is closed on main and no retroactive PR gate applies.
- Keep `docs/repo-audit-20260521.md` untracked/excluded unless user separately authorizes publication or deletion.
- Record open repo/doc hygiene residuals from repo-audit: D-1 project structure tree, D-8/C-5 `fund/tools` fact check, C-9 reviews directory growth.
- Carry all residuals forward with explicit owners.
- Recommend either stopping the release lane as maintenance-ready or opening a new P13 design/plan gate.

Stop if validation fails, if tracked source/test changes are required, if repo-audit disposition requires deletion/publication, or if RR-13 source data would need automatic modification.
```

Completion report format for closeout:

```markdown
## Closeout Report

- Gate:
- Artifact:
- Branch/status:
- Validation:
- Repo-audit disposition:
- Residual owner table:
- Recommended next entry point:
- Blocking open questions:
```
