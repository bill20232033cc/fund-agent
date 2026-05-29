# Plan Review: MVP truth pivot and context compaction gate

> **Reviewer**: MiMo
> **Date**: 2026-05-30
> **Plan artifact**: `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md`
> **Review type**: adversarial plan review
> **Verdict**: **PASS_WITH_NON_BLOCKING**

---

## Verdict rationale

Plan is structurally sound, correctly scoped to docs-only, and preserves all hard constraints. No blocking findings. Three non-blocking findings and two observations that the implementation agent should address during execution.

---

## Findings

### F1 [LOW] Current Accepted Artifacts 处置未显式指定

**Location**: Plan §6, "Required Current Accepted Artifacts section"

**Issue**: Plan 要求 implementation-control.md 新版只保留"short table with only the artifacts needed to resume the MVP pivot"，但未显式说明当前 control doc 中 ~40+ release-maintenance artifacts（§6 Current Accepted Artifacts 表）的处置方式。Plan 只说"Include links to the existing release-maintenance roadmap / closeout / residual disposition artifacts only as evidence-chain summaries, not active gate truth"，但实现 agent 需要判断哪些归入 Historical Evidence Index、哪些保留为摘要链接、哪些完全省略。

**Risk**: 实现 agent 可能做出不一致的裁剪，或过度保留导致 control doc 仍然冗长。

**Suggested fix**: 在 plan §6 中补充一句："将现有 release-maintenance artifacts 全量索引移入 `docs/archive/` 或 Historical Evidence Index，在 Current Accepted Artifacts 表中只保留本 pivot gate 的 artifacts 和 roadmap consolidation / overnight closeout 两个摘要链接。"

---

### F2 [LOW] Release-maintenance closeout ledger 行的措辞约束

**Location**: Plan §6, "Required Recent Active Gate Ledger"

**Issue**: Plan 要求"Keep only a compact ledger of this pivot gate plus a single summarized row for release-maintenance closeout"，并要求"The ledger must not imply release maintenance is the current phase after this gate"。但当前 control doc 的 Recent Active Gate Ledger 有 20+ 行详细记录（从 source provenance 到 fixture promotion state manifest），实现 agent 需要将它们压缩为一行。Plan 未提供这一行的示例措辞。

**Risk**: 压缩后的一行可能遗漏关键状态（如 `promotion_allowed=false` 仍然生效），或措辞模糊导致后续 agent 误以为 release-maintenance 已完结。

**Suggested fix**: 在 plan §6 中提供示例行，如：

| Gate | Status | Summary |
|---|---|---|
| release-maintenance consolidation + overnight closeout | accepted locally | All promotion_allowed=false; 004393/004194/006597 fixture_state=absent; QDII/FOF/110020 deferred; Host/Agent/dayu deferred. Full ledger: Historical Evidence Index. |

---

### F3 [INFO] Validation plan 不覆盖 docs-only 范围确认

**Location**: Plan §11

**Issue**: Plan 的 validation plan 包含 `git diff --check` 和 path-existence checks，并说明"docs-only rationale for not running full ruff/pytest"。这是正确的。但 plan 未要求实现 agent 验证"only allowed docs were changed"——即 `git diff --name-only` 输出只包含 §5 列出的文件。这是 controller judgment artifact 的关键输入。

**Suggested fix**: 在 §11 中增加一条 validation command:

```bash
git diff --name-only  # must only show docs/implementation-control.md, docs/design.md, docs/current-startup-packet.md, docs/reviews/*
```

---

## Observations

### O1 Plan 与当前 source truth 的一致性

- Plan §2 正确识别了 AGENTS.md、docs/design.md、docs/implementation-control.md、docs/fund-analysis-template-draft.md 作为 source truths。
- Plan §3 non-goals 完整覆盖了 AGENTS.md 的硬约束：不改 runtime/schema/score/snapshot/quality/golden/fixtures、不 promotion、不改 AGENTS.md/template。
- Plan §4 Route C 描述与 docs/design.md §5.4 "章节级写作审计闭环（已接受的未来设计）"一致，且正确标注为"accepted future design, not current implementation"。
- Plan §6 Current Truth Guardrails 与 AGENTS.md 的四层边界、Dayu Host/Agent 纪律、显式参数要求一致。

### O2 Plan 的 scope 正确性

- Plan 只修改 3 个 docs 文件 + 2 个 reviews artifacts，不触及 runtime、tests、pyproject.toml 或任何代码文件。
- Plan 不修改 AGENTS.md、docs/fund-analysis-template-draft.md。
- Plan 不创建 fund_agent/host 或 fund_agent/agent 包。
- Plan 不引入 dayu.host 或 dayu.engine 依赖。
- Plan 不改变 golden fixtures、promotion state 或 quality gate 语义。
- Plan 正确识别当前 branch `codex/local-reconciliation` 和 untracked artifacts 的存在，并明确要求不处理它们。

---

## Checklist

| Check | Result |
|---|---|
| Route C is not described as implemented | PASS: Plan §4 repeatedly states "accepted future design" and "not currently implemented" |
| Active control plane no longer points at 006597 extractor gate | PASS: Plan §6 specifies new next entry = "MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate" |
| Golden/strict/QDII/FOF/110020/fixture promotion are residuals, not deleted | PASS: Plan §6 Open Residuals preserves all as residual, explicitly not blocking MVP |
| Long release-maintenance history is linked/summarized, not embedded | PASS: Plan §6 requires links only, not embedded ledgers |
| docs/current-startup-packet.md is short enough | PASS: Plan §8 targets 100-150 lines |
| UI -> Service -> Host -> Agent boundary intact | PASS: Plan §4 and §6 reaffirm this boundary |
| Host/Agent/dayu deferred to Gate 5 | PASS: Plan §4 Gate 5 is the only step for dayu integration |
| No unrelated untracked artifact referenced as evidence | PASS: Plan §3 and §6 explicitly exclude untracked files |
| AGENTS.md not modified | PASS: Not in §5 files-to-modify list |
| Template not modified | PASS: Not in §5 files-to-modify list |
| No promotion/fixture/golden changes | PASS: Plan §3 and §6 prohibit these |

---

## Severity summary

| Severity | Count |
|---|---|
| BLOCKING | 0 |
| LOW | 2 |
| INFO | 1 |

---

*Review artifact produced by MiMo as Gateflow plan reviewer. No plan, control doc, design doc, startup packet, AGENTS.md, or template was modified.*
