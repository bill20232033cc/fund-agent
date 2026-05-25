# Release Maintenance Report-Quality Baseline S0 Corpus-Selection Evidence Review (MiMo)

> Date: 2026-05-25
> Reviewer: AgentMiMo
> Gate: `report-quality-baseline S0 corpus-selection evidence`
> Review target: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md`
> Truth sources: `AGENTS.md`; `docs/design.md` v2.2 §5.4, §5.4.2, §5.4.3, §6.5; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted Fact/Evidence plan and controller judgment artifacts.
> Scope: Review only; no file modification, commit, push, or PR.

## Verdict

**PASS_WITH_FINDINGS**

Artifact 满足 S0 全部必备字段、FundDocumentRepository boundary 约束、FOF data_gap 记录要求、review state transition 定义和非目标声明。无阻塞性 blocker。有 2 个 material finding 和 2 个 minor finding 需要在 controller judgment 前处理或记录 disposition。

## Findings

### F-1 [Material] Fallback 记录缺少原始 failure category — 违反 AGENTS.md 硬约束

**位置**: candidate table 行 `110020`、`017641`、`017970`（lines 42, 45, 47）

**问题**: `110020`、`017641`、`017970` 三条记录的 source metadata 均标注 `fallback_used=True`，但 `source failure category` 列为 `n/a`。

**对照 truth source**: `AGENTS.md` 明确规定：

> fallback 成功时必须保留 `metadata.fallback_used=True`。
> fallback 被阻断时必须保留来源、失败类别、错误信息和原始异常 cause。

当前 artifact 的 Open Gaps 表（line 108）承认了这个问题并建议 "S1/source gate should preserve original failure categories when selecting durable corpus"，但这不足以替代 S0 证据本身的完整性。S0 的职责是记录 corpus identity verification evidence；如果 fallback 发生了，原始上游失败类别（`not_found` 还是 `unavailable`）必须在 S0 evidence 中可追溯，否则 S1 无法判断该 fallback 是否符合 fail-open 条件。

**影响**: S1 若基于这些记录进入 scoring schema 设计，将无法验证 fallback 合规性。这不是 S1 blocker（因为 S1 尚未开始），但 evidence artifact 本身的完整性存在缺口。

**建议 disposition**: Controller 可以选择：
- (a) 接受 S0 但要求补充原始 failure category 到 candidate table 或 Open Gaps 表作为 S0 补丁；
- (b) 接受 S0 但将此记录为 S1 entry gate 的前置验证项，要求 S1 启动前先从 repository probe JSONL 中提取并补充。

---

### F-2 [Material] QDII-FOF classifier precedence 问题未在 design.md 中显式记录

**位置**: FOF Attempt Result（lines 49-61）和 Open Gaps 表第一行（line 106）

**问题**: Artifact 正确观察到 §6.5 基金类型识别规则中 QDII 优先级（第 3 步）高于 FOF（第 4 步），导致 "QDII-FOF" 基金被分类为 `qdii_fund` 而非 `fof_fund`。Artifact 将此记录为 `data_gap` 并提出两个解决路径：找纯 FOF 或开 taxonomy/precedence 设计 gate。

但 `docs/design.md` §6.5 的规则表未显式说明当名称同时包含 "QDII" 和 "FOF" 时应如何处理。当前按优先级链自然走 QDII，但设计文档既没有将此标注为已知行为也没有标注为待裁决。如果后续有人读 §6.5 并按 "名称含 FOF → fof_fund" 理解，会产生与当前 classifier 行为的矛盾。

**影响**: 不阻塞 S0/S1，但会导致后续 contributor 或 reviewer 对 FOF 覆盖产生误解。

**建议 disposition**: 此问题超出 S0 artifact 职责范围。Controller 应记录为 design.md §6.5 的独立 residual，在下一个 fund-type taxonomy gate 中显式裁决 QDII-FOF 混合类型的分类策略。S0 artifact 本身的记录是充分的。

---

### F-3 [Minor] Review state transition 未覆盖异常/回退路径

**位置**: Review State Transition Contract（lines 65-71）

**问题**: 6 个状态的 forward transition 都定义了 trigger、actor 和 minimum evidence，但没有定义：
- 若 `repository_verified` 后发现 identity mismatch，是否回退到 `candidate` 或标记为 `rejected`？
- 若 `fact_prefill_reviewed` 时 reviewer reject 了整条记录，是回到 `repository_verified` 还是标记为 `deferred`？
- 是否存在 terminal state（如 `rejected`、`deferred`、`expired`）？

**影响**: Minor。当前 S0 只有 `candidate` 和 `repository_verified` 两个状态的记录，回退场景在 S0 阶段不太可能发生。但 S1/S2 扩展时需要补全。

**建议 disposition**: 接受 S0，将此记录为 S1/S2 state machine 扩展的 residual。

---

### F-4 [Minor] `rg` 验证命令的 scope 可能过于宽泛

**位置**: Validation（lines 116-118）

**问题**: `rg` 命令用 `|` 连接了大量关键词（`fund type slot|repository verification status|review state|source failure category|ignored run path|fof_fund|data_gap|candidate|repository_verified|...`），但没有用 `-c`（count）或具体 expected match 数量来验证。只要文件中出现任何一个关键词就算 passed。

**影响**: Minor。这是一个文档级 validation 的精度问题，不影响 artifact 正确性。验证命令证明了必要术语存在，但未验证它们出现在正确的上下文中（如表头 vs 正文）。

**建议 disposition**: 接受 S0。S1 可考虑更精确的验证策略。

---

## Open Questions / Residuals

| # | Question | Owner / Gate |
|---|---|---|
| 1 | Fallback 记录的原始 failure category 应从 repository-probe.jsonl 中提取并补充到何处？ | S0 patch 或 S1 entry gate |
| 2 | §6.5 QDII-FOF 混合类型分类策略是否需要在 design.md 中显式裁决？ | 独立 fund-type taxonomy gate |
| 3 | Review state machine 是否需要 terminal states（rejected / deferred / expired）？ | S1/S2 state machine 扩展 |
| 4 | `110020`（index_fund）的 `fallback_used=True` 来源是 Eastmoney fallback，这是否符合 index_fund 的首选来源策略？ | S1 source gate |

## Required Fixes Before Controller Acceptance

无阻塞性 required fix。

F-1 是最接近 required fix 的 finding，但因为 S1 尚未启动且 Open Gaps 表已记录了该问题，controller 可以在 judgment 中选择接受 + 记录 disposition 而非要求 S0 重新产出。

## Recommendation

**建议进入 controller judgment。**

Artifact 满足 S0 全部 deliverable：7 条候选记录覆盖 6 个 fund type slot（FOF 为 data_gap）、全部 S0 必备字段完整、FundDocumentRepository boundary 未被违反、review state transition 定义完整（含 trigger/actor/minimum evidence）、非目标声明与 control doc 一致。Findings 均可通过 controller disposition 处理，无需退回 S0 重新产出。
