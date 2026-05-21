# P11-S1 Control Doc Hygiene / Recovery Plan Review

- **Date**: 2026-05-21
- **Reviewer**: AgentGLM
- **Review target**: `docs/reviews/p11-s1-control-doc-hygiene-recovery-plan-20260521.md`
- **Review type**: Adversarial plan review
- **Input artifacts read**:
  - `AGENTS.md`
  - `docs/design.md`
  - `docs/implementation-control.md` (full, 1482 lines)
  - `docs/reviews/post-p10-follow-up-planning-20260521.md`

---

## Verdict: PASS_WITH_FINDINGS

P11-S1 plan 在核心目标（降低 phaseflow resume/handoff 成本）上设计合理，non-goals 边界清晰，artifact preservation 规则完整。发现 3 个 findings（1 MEDIUM、2 LOW），均不阻断但建议在 plan acceptance 前澄清或修订。

---

## Challenge 1: 是否真的降低 phaseflow resume/handoff 成本？

**判定：是，设计有效。**

Plan 的三层结构（Startup Packet → Phase History Index → Historical Evidence Archive）直接解决了当前 control doc 的核心痛点：新 controller 必须扫描 1482 行混合叙事才能确定当前 gate 和 next action。

Startup Packet（约 20 行表格 + 5 项 checklist）将 resume 必需信息压缩到一屏。Phase History Index 为历史 phase 提供导航表，避免扫描 archive。这是对当前问题的正确诊断和最小干预。

**风险点（已缓解）**：Plan 承认默认"keep history in same file"并只在"reviewers explicitly accept the tradeoff"时才拆分。这是正确的保守策略——拆分文件会引入"哪个文件是 truth"的歧义。

**F-1 (LOW)**：Startup Packet 的 controller resume checklist 第 5 项"If artifact references are touched, run the artifact existence check"是 good practice，但 plan 未说明这个 check 是在每次 resume 时都跑，还是只在 P11-S1 implementation 完成后跑一次。建议澄清：existence check 应作为 P11-S1 implementation 的 acceptance gate（一次性验证），而非每次 resume 的固定步骤。当前 control doc 已有 1482 行历史证据，每次 resume 跑 existence check 的成本不低且收益递减。

---

## Challenge 2: 是否保留 implementation-control 作为 control truth？

**判定：是，保留完整。**

Plan 的 Section 7（Design / Control Alignment Rules）明确声明：
- `docs/implementation-control.md` remains the control truth
- hygiene pass may reorganize but may not change design facts
- If control history contradicts `docs/design.md`, create reconciliation artifact first

Plan 的 File Ownership section 正确限定了只修改 `docs/implementation-control.md`，且默认不拆分到独立文件。如果未来拆分，`docs/implementation-control.md` 必须仍然 link to it from the startup packet。

**F-2 (MEDIUM)**：Plan 的 Section 3（Phase History Index）的 `Anchor` 列定义为"Link to the detailed same-file archive section"。但 plan 没有指定 anchor 的具体格式（Markdown heading anchor？行号？section ID？）。当前 `docs/implementation-control.md` 使用的是 `### P0: ...` / `### P1: ...` 等 heading，如果 archive 被重组为子 section（如 `### P0 Archive` / `### P1 Archive`），anchor 稳定性取决于 heading 唯一性。建议 plan 增加 anchor 格式约束：anchor 必须使用 phase-prefixed heading（如 `## Archive: P0` 或 `## P0 详细记录`），且每个 phase 的 archive heading 在文件内必须唯一。这不是阻断项，但如果 anchor 格式不一致，Phase History Index 的导航价值会打折扣。

---

## Challenge 3: 是否会丢 artifact paths / commit hashes / PR links / validation / residual owners？

**判定：不会丢失，preservation 规则完整。**

Plan 的 Section 5（Evidence Preservation Rules）列举了 14 类必须保留的字段：
- artifact paths, plan review paths, code review paths, controller judgment paths, re-review paths, implementation artifact paths, accepted local commit hashes, PR URLs, PR branch/head/merge commit, CI run IDs and status, validation commands and exact pass counts, residual risk IDs and owners, reviewer limitations

Plan 还明确声明：
- "If an old entry lacks one of these fields, do not invent it. Use `not recorded` only when the historical record truly lacks it."
- "Must not delete artifact paths, commits, PR links, validation results, or residual owners."

Section 6（Archive / Summarize Strategy）的 Level 3 规则："May remove duplicated prose only when the exact fact is retained in a table or archive entry." 这是最安全的 summarization 策略。

Section 8（Residual Risk Handling）保留了 active residual section 和历史 residual table。

**验证**：我对照了 `docs/implementation-control.md` 中的关键证据条目，确认 plan 的 preservation rules 覆盖了所有现有字段类型。P10 merge commit (`acc692c7e84c855398de86497b0d05f30b6f5ca5`)、PR #6 URL、Actions run ID `26234941272`、全量测试 pass count (`388 passed`)、RR-13 human-owned 标注、`docs/repo-audit-20260521.md` excluded 标注——这些在 plan 的 preservation rules 下都会保留。

---

## Challenge 4: 是否误开产品代码、Dayu runtime、Host/Engine/tool loop、LLM writing？

**判定：未误开，边界正确。**

Plan 的 Non-Goals section 明确排除：
- "Do not change source code, tests, config, CLI behavior, product behavior, Fund Capability logic, audit rules, quality gate behavior, renderer output, extraction logic, or runtime wiring."
- "Do not introduce Dayu runtime, Host, Engine, tool loop, prompt scene registry, or LLM writing."

File Ownership section 限定只修改 `docs/implementation-control.md`。Validation Plan section 明确"No pytest or ruff run is required for P11-S1 documentation-only implementation unless the implementation unexpectedly touches source, tests, or config. If that happens, the implementation is out of scope and should stop for controller review."

Section 7 的 design facts must-not-regress list 正确列出了 Dayu non-dependency 和 no prompt scene registry / Host session / Engine tool loop / LLM writing。

**对照 AGENTS.md**：Plan 未违反任何 AGENTS.md 模块边界规则——它不涉及 UI / Service / Runtime / Engine / Capability 的任何代码变更。

**对照 design.md**：Plan 不改变 design.md 的任何架构声明或产品行为描述。Plan 甚至明确要求"如果 control history contradicts `docs/design.md`，先建 reconciliation artifact"。

---

## Challenge 5: 是否正确保留 RR-13 human-owned 和 docs/repo-audit 排除？

**判定：正确保留。**

Plan 的 Non-Goals：
- "Do not auto-resolve RR-13 duplicate `016492`; it remains user/App-source owned."
- "Do not publish, commit, summarize as accepted evidence, or move `docs/repo-audit-20260521.md`."

Plan 的 Startup Packet open residuals 表包含：
- "RR-13 duplicate `016492` — User / App source"
- "`docs/repo-audit-20260521.md` — Controller / user"

Plan 的 Residual Risk Handling 表：
- "RR-13 duplicate `016492` | User / App source | Preserve as human-owned; do not modify CSV"
- "`docs/repo-audit-20260521.md` | Controller / user | Keep excluded unless later scope accepts publication"

这与 `post-p10-follow-up-planning-20260521.md` 的 accepted scope 完全一致。

我验证了 `docs/repo-audit-20260521.md` 确实存在于本地但未被 git 跟踪（git status 显示 `?? docs/repo-audit-20260521.md`），确认当前状态与 plan 描述一致。

---

## Additional Findings

**F-3 (LOW)**：Plan 的 Validation Plan section 的 manual review checklist 包含"The first 120 lines identify the current gate and next entry point."但 plan 未指定 Startup Packet 的硬性行数上限。当前 control doc 的 1.0 Current Snapshot section 约占 25 行（表格 + 一段叙述）。Plan 的 Startup Packet 设计（表格 + checklist + Active Gate Ledger）可能在实现后超过 120 行，尤其是 Active Gate Ledger 的 column count 较多时。建议 plan 增加一个硬约束："Startup Packet + Active Gate Ledger 合计不超过 80 行"，确保"一屏可读"目标不被 Ledger 膨胀稀释。这不是阻断项，但如果不约束，Active Gate Ledger 可能逐步退化成 mini-archive。

---

## Summary of Findings

| ID | Severity | Area | Summary | Recommendation |
|----|----------|------|---------|----------------|
| F-1 | LOW | Startup Packet | Artifact existence check 频率未澄清 | 澄清为 P11-S1 implementation acceptance gate（一次性），非每次 resume 固定步骤 |
| F-2 | MEDIUM | Phase History Index | Anchor 格式未约束 | 增加 anchor 格式约束：phase-prefixed heading，文件内唯一 |
| F-3 | LOW | Validation Plan | Startup Packet + Active Gate Ledger 行数无硬上限 | 增加硬约束：合计不超过 80 行 |

---

## Adversarial Failure Pass

| Attack vector | Result |
|---|---|
| Implementation 期间悄悄删除历史 artifact path | Section 5 preservation rules 阻断；existence check 捕获 |
| Summarization 丢失 commit hash 或 PR URL | Section 6 Level 3 规则：prose-only duplication 可删，exact fact 必须保留 |
| 误开产品代码变更 | Non-Goals + File Ownership + Validation Plan 三重守卫 |
| 误引入 Dayu runtime | Non-Goals + Section 7 design facts must-not-regress 双重守卫 |
| RR-13 被自动解决 | Non-Goals + Residual Risk Handling 双重守卫 |
| repo-audit 被意外提交 | Non-Goals 明确排除 + manual review checklist 包含检查项 |
| Archive anchor 失效导致 index 不可导航 | F-2 finding：建议增加 anchor 格式约束 |
| Active Gate Ledger 膨胀抵消 Startup Packet 收益 | F-3 finding：建议增加行数硬约束 |

---

## Conclusion

P11-S1 plan 正确诊断了当前 control doc 的核心问题（recovery cost），提出了最小干预方案（same-file restructure with three levels of detail），完整保留了 artifact preservation rules，严格守住 non-goals 边界（无产品代码、无 Dayu runtime、无 LLM writing），正确处理了 RR-13 human-owned 和 repo-audit 排除。

3 个 findings 均为澄清/约束性问题，不影响 plan 的核心正确性。建议在 acceptance 前处理 F-2（anchor 格式约束），F-1 和 F-3 可在 implementation 阶段处理。

**Verdict: PASS_WITH_FINDINGS** — plan 可进入下一 gate（acceptance），建议优先处理 F-2。

---

## Targeted Re-Review (2026-05-21)

- **Re-review trigger**: Plan revised to address F-1, F-2, F-3
- **Scope**: Only verify whether the three findings from the initial review are closed

### F-1 (LOW) — Artifact existence check frequency

**Status: CLOSED**

Plan 修订在多处明确澄清了 existence check 的定位：

- Section 1 Startup Packet checklist item 5（line 89）："Do not run the artifact existence check as a fixed resume step; it is a P11-S1 implementation acceptance gate after the hygiene edit changes references."
- Artifact Existence Check Recommendation（line 257）："This check is a one-time P11-S1 implementation acceptance gate, not a fixed action for every `phaseflow` resume."
- Validation Plan（line 294）："Run this artifact reference validation once before accepting the P11-S1 implementation. Do not add it to the routine resume checklist."
- Acceptance criterion 9（line 331）："Artifact existence checks are specified as a one-time implementation acceptance gate, not as routine resume work."

修订内容精确回应了 finding 的建议，无残留歧义。

### F-2 (MEDIUM) — Phase History Index anchor format

**Status: CLOSED**

Plan 修订新增了完整的 anchor format constraints 段落（lines 134-140）：

- "Archive sections must use phase-prefixed unique headings."
- "Use headings like `## Archive: P0`, `## Archive: P1`, ..., `## Archive: P11`."
- "Every archive heading must be unique within `docs/implementation-control.md`."
- "The `Phase History Index` anchor column must point to those exact archive headings."
- "If a phase needs sub-archives, use unique nested headings under the phase archive, for example `### Archive: P10 Draft PR Gate`; do not create a second `## Archive: P10`."

Acceptance criterion 5 和 manual review checklist 均已同步更新。Anchor 格式约束完整、无歧义，且覆盖了 sub-archive 边界情况。

### F-3 (LOW) — Startup Packet + Active Gate Ledger line limit

**Status: CLOSED**

Plan 修订新增了 80 行硬约束，出现在三处：

- Section 1 Startup Packet（line 65）："Hard size constraint: `Startup Packet` plus `Active Gate Ledger` should be no more than 80 lines in total."
- Section 2 Active Gate Ledger（line 114）："The ledger must stay compact enough to keep the combined `Startup Packet` + `Active Gate Ledger` under the 80-line limit. If a field would make the ledger sprawl, link to the phase history index or archive entry instead of adding prose."
- Acceptance criterion 6（line 328）和 manual review checklist（line 298）均已同步。

修订不仅增加了硬约束，还提供了 overflow 缓解策略（link to index/archive instead of adding prose），防止 Ledger 退化。

### Re-Review Verdict

All 3 findings **CLOSED**. Plan 已达到 code-generation-ready 状态，可进入 P11-S1 acceptance gate。

**Re-review Verdict: PASS** — plan accepted, no remaining findings.
