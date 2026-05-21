# P11-S1 Plan Review (MiMo)

- **Date**: 2026-05-21
- **Reviewer**: AgentMiMo
- **Target plan**: `docs/reviews/p11-s1-control-doc-hygiene-recovery-plan-20260521.md`
- **Review scope**: Plan only, no implementation changes
- **Inputs read**:
  - `AGENTS.md`
  - `docs/design.md`
  - `docs/implementation-control.md` (1481 lines, full read)
  - `docs/reviews/post-p10-follow-up-planning-20260521.md`
  - `docs/reviews/p11-s1-control-doc-hygiene-recovery-plan-20260521.md`

---

## Verdict

**PASS_WITH_FINDINGS**

P11-S1 plan is documentation-only, correctly scoped, and preserves all required gate evidence categories. The startup packet + active gate ledger + phase history index design will reduce phaseflow resume/handoff cost. No blocking findings. Two informational findings noted below.

---

## Review Challenge Analysis

### 1. 是否真的降低 phaseflow resume/handoff 成本

**结论：是。**

当前 `docs/implementation-control.md` 共 1481 行，§1.0 Current Snapshot 仅 10 行但紧接其后是密集的 gate 历史记录（§1.3 约 400+ 行）。Resume agent 必须扫描大段混合叙事才能定位当前状态和下一步动作。

计划的 Startup Packet（表格 + 5 步 resume checklist）+ Active Gate Ledger（仅 2 行）+ Phase History Index（导航表，不重复详情）形成三层降噪结构：
- 第一层：当前 gate、下一 entry point、open residuals（< 30 行）
- 第二层：仅 active/previous gate 的 artifact/commit/validation（< 10 行）
- 第三层：P0-P11 导航索引，指向详细 archive section

这与 post-P10 planning 的诊断一致："startup requires scanning a long mixed narrative"，fix 是 "make the first screen answer what should the next controller do now"。

### 2. 是否保留 implementation-control 作为 control truth

**结论：是。**

计划明确：
- §7 Design/Control Alignment Rules 第 2 条："`docs/implementation-control.md` remains the control truth for phase state, gates, artifacts, commits, validation, residual risks, and next entry point"
- §6 Archive/Summarize Strategy Level 3："Must not delete artifact paths, commits, PR links, validation results, or residual owners"
- 默认 archive 在 same file，不拆分（除非 reviewer 显式接受）

### 3. 是否会丢 artifact paths/commit hashes/PR links/validation/residual owners

**结论：不会丢，但有 INFO 级提醒。**

Evidence Preservation Rules（§5）列出 13 类 immutable fields，覆盖：
- artifact paths (plan review, code review, controller judgment, re-review, implementation)
- accepted local commit hashes
- PR URLs, branch/head/merge commit
- CI run IDs and status
- validation commands and exact pass counts
- residual risk IDs and owners

计划还规定："If an old entry lacks one of these fields, do not invent it. Use `not recorded` only when the historical record truly lacks it."

**Finding #1 (INFO)**：Artifact Existence Check（§末）只覆盖 file-backed `docs/reviews/...` 路径。PR URLs（如 `https://github.com/bill20232033cc/fund-agent/pull/6`）、commit hashes（如 `acc692c`）和 CI run IDs（如 `26234941272`）作为字符串保留，不做自动验证。计划已承认这点："External PR URLs, GitHub Actions run IDs, branch names, and commit hashes are not file paths. They should be preserved as strings and reviewed manually for obvious truncation." 这是合理的设计选择，但实现时应确保这些字符串在 reorganization 过程中不被意外截断或丢失。

### 4. 是否误开产品代码、Dayu runtime、Host/Engine/tool loop、LLM writing

**结论：没有。**

Non-Goals 第 1 条明确排除：source code, tests, config, CLI behavior, product behavior, Fund Capability logic, audit rules, quality gate behavior, renderer output, extraction logic, runtime wiring。

Non-Goals 第 6 条明确排除：Dayu runtime, Host, Engine, tool loop, prompt scene registry, LLM writing。

File Ownership 节明确限定："Implementation should modify only documentation-control files: `docs/implementation-control.md`"。

### 5. 是否正确保留 RR-13 human-owned 和 docs/repo-audit 排除

**结论：是。**

- Non-Goals 第 4 条："Do not auto-resolve RR-13 duplicate `016492`; it remains user/App-source owned."
- Non-Goals 第 5 条："Do not publish, commit, summarize as accepted evidence, or move `docs/repo-audit-20260521.md`."
- Active Residuals 表（§8）保留 RR-13 和 repo-audit 为 separate entries with explicit owners.
- Startup Packet 的 Open residuals 行包含 "RR-13 duplicate `016492`, excluded `docs/repo-audit-20260521.md`"。
- Implementation Step #10："Do not touch `docs/repo-audit-20260521.md`."

---

## Findings

### Finding #1: PR URL / commit hash / CI run ID 验证范围

| 属性 | 值 |
|------|-----|
| Severity | INFO |
| Evidence | 计划 §末 Artifact Existence Check Recommendation |
| Description | 自动 existence check 只覆盖 file-backed paths；PR URLs、commit hashes、CI run IDs 依赖 manual review |
| Risk | 低：当前 control doc 中这些字段格式稳定，且计划已要求 "reviewed manually for obvious truncation" |
| Recommendation | 实现时可在 Phase History Index 的 PR/commit 列做一次 grep 交叉检查，确认所有历史 PR URL 和 merge commit hash 在 reorganization 后仍完整保留 |

### Finding #2: 120 行 target 与当前 1481 行的张力

| 属性 | 值 |
|------|-----|
| Severity | INFO |
| Evidence | Validation Plan "The first 120 lines identify the current gate and next entry point"；当前文件 1481 行 |
| Description | 计划要求前 120 行完成 startup packet + active gate ledger + phase history index。当前 1481 行中有约 440 行 gate 历史在 §1.3，约 500+ 行 slice 状态在 §1.3 和 §2，约 340 行状态更新日志在 §7。要压缩到前 120 行覆盖当前状态，需要将大量历史内容下沉到 archive section |
| Risk | 低：这是文档重组的正常目标，不是设计缺陷。但如果 Phase History Index 行数过多（P0-P11 共 12 phase + 多个 post-phase follow-up），120 行可能偏紧 |
| Recommendation | 实现时优先保证 Startup Packet + Active Gate Ledger 在前 60 行内，Phase History Index 可以在 60-150 行范围内，不必严格限制在 120 行。关键是 "one short read" 而非精确行数 |

---

## Conclusion

P11-S1 plan 正确诊断了当前 phaseflow resume 成本问题，提出的三层降噪结构（startup packet → active gate ledger → phase history index）能在不丢失历史证据的前提下显著降低 handoff 成本。所有 non-goals 对齐 AGENTS.md 硬约束和 post-P10 planning 的范围定义。Evidence Preservation Rules 覆盖全部 13 类 gate 证据字段。RR-13 和 repo-audit 的排除处理正确。计划不引入任何产品代码、Dayu runtime 或 LLM writing scope。

两个 INFO finding 均不阻塞计划接受，可在实现阶段作为 checklist 输入。

**Initial Verdict: PASS_WITH_FINDINGS**

---

## Targeted Re-Review (2026-05-21)

- **Trigger**: Plan updated after initial review; re-review requested for three specific findings
- **Re-review scope**: Verify three finding closures only

### Re-Review Check 1: Artifact Existence Check as P11-S1 Acceptance Gate

**Status: CLOSED**

Plan now explicitly scopes the existence check as a one-time implementation acceptance gate, not a routine resume action:

- Resume checklist step 5 (line 89): "Do not run the artifact existence check as a fixed resume step; it is a P11-S1 implementation acceptance gate after the hygiene edit changes references."
- Artifact Existence Check section (lines 256-257): "This check is a one-time P11-S1 implementation acceptance gate, not a fixed action for every `phaseflow` resume."
- Validation Plan (line 294): "Run this artifact reference validation once before accepting the P11-S1 implementation. Do not add it to the routine resume checklist."

### Re-Review Check 2: Phase History Index Anchor with Phase-Prefixed Unique Headings

**Status: CLOSED**

Plan now specifies anchor format constraints (lines 136-140):

- "Archive sections must use phase-prefixed unique headings."
- "Use headings like `## Archive: P0`, `## Archive: P1`, ..., `## Archive: P11`."
- "Every archive heading must be unique within `docs/implementation-control.md`."
- "If a phase needs sub-archives, use unique nested headings under the phase archive, for example `### Archive: P10 Draft PR Gate`; do not create a second `## Archive: P10`."

Validation manual review checklist (line 300) and acceptance criteria (line 329) both reference this constraint.

### Re-Review Check 3: Startup Packet + Active Gate Ledger ≤80 Lines

**Status: CLOSED**

Plan now states an explicit hard size constraint (line 65): "`Startup Packet` plus `Active Gate Ledger` should be no more than 80 lines in total."

Reinforced in:
- Active Gate Ledger (line 114): "The ledger must stay compact enough to keep the combined `Startup Packet` + `Active Gate Ledger` under the 80-line limit."
- Manual review checklist (line 298): "`Startup Packet` plus `Active Gate Ledger` are no more than 80 lines total."
- Acceptance criteria (line 328): "`Startup Packet` plus `Active Gate Ledger` stay within the 80-line limit."

---

## Targeted Re-Review Conclusion

All three initial findings are closed in the updated plan. The artifact existence check is correctly scoped as a one-time P11-S1 acceptance gate. Phase History Index anchors have explicit phase-prefixed unique heading format. The first-screen recovery constraint is a clear 80-line limit with reinforcement in four separate plan sections.

**Re-Review Verdict: PASS**
