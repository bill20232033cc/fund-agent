# Plan Review: Post-Provenance Coverage Recovery Decision Plan

> Reviewer: AgentGLM (独立 plan reviewer)
> Date: 2026-05-27
> Target: `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-20260527.md`
> Truth sources: `AGENTS.md`; `docs/design.md` 当前设计章节; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
> Accepted artifacts verified:
> - `release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md`
> - `release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md`
> - `release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md`
> - `release-maintenance-bond-lens-score-applicability-implementation-controller-judgment-20260527.md`

## Verdict: **PASS_WITH_FINDINGS**

Plan 逻辑严密，事实断言与 accepted artifacts 同源一致，硬禁止全部遵守。两个 non-blocking finding 涉及 Candidate E 前置条件表述完整性和并行化可能性，不影响 gate 准入。

---

## Review Focus 1: 为什么不直接进入 golden answer corpus v1

**结论：理由充分，无遗漏前置条件。**

Plan 列出 Candidate E 的 5 条未满足前提（coverage 不足、FOF 未解、QDII quality-blocked、bond baseline-blocked、110020 未审查、无 fixture-promotion gate），逐条与 accepted evidence 同源验证：

| Plan 断言 | Evidence 验证 | 结果 |
|---|---|---|
| coverage 仅 3 个 clean candidate / 3 个 fund-type slot | small baseline v1 run controller judgment: "clean evaluated coverage is only three candidates / three fund-type slots, below the 5-10 representative target" | 一致 |
| pure FOF 是 data_gap / taxonomy residual | v1 run controller judgment: `007721` 和 `017970` 均为 `data_gap` / `taxonomy_pending` | 一致 |
| 017641 QDII quality-blocked | provenance rerun controller judgment: `017641` quality `block`, terminal_state `quality_blocked_after_provenance` | 一致 |
| 006597 bond baseline-blocked | bond-lens controller judgment: `baseline_blocking=true`, quality `warn` not `pass`, residual P1 gaps in holder_structure/share_change/turnover_rate | 一致 |
| 110020 仅为 review-eligible | provenance rerun controller judgment: terminal_state `provenance_eligible_for_next_review`, `not_promoted` | 一致 |
| 无 fixture-promotion gate | implementation-control.md Accepted Artifacts 中无任何 fixture-promotion controller judgment | 一致 |

**Finding F1 (non-blocking)**：Candidate E 前提列表未显式枚举 `004393`（active）和 `004194`（enhanced_index）各自到达 golden readiness 所需的具体证据补齐动作（如 004393 的 Chapter 3 turnover/style evidence gap、004194 的 tracking_error/turnover_rate evidence gap）。这些 gap 在 Evidence Table 中有记录，但在 Candidate E 的 "Unmet prerequisites" 中缺失，可能让后续 golden gate 遗漏这两个已 clean candidate 的剩余工作项。建议在修订时补充一行概述，不影响当前 gate 准入。

---

## Review Focus 2: 110020 / 017641 从 source blocker 转为 coverage/quality blocker 的分类

**结论：分类严谨，证据同源。**

两个样本的分类核心是 provenance rerun 后 quality gate 状态差异驱动：

| 样本 | Provenance 状态 | Quality 状态 | Blocking issues | Terminal state | 分类依据 |
|---|---|---|---|---|---|
| `110020` | `complete`, `eligible`, `unavailable` | `warn` | FQ2 warn turnover_rate, FQ2F warn P1, FQ0 info strict golden not configured | `provenance_eligible_for_next_review` | source 已解，quality 未 block → 可进入 coverage review |
| `017641` | `complete`, `eligible`, `unavailable` | `block` | FQ2/FQ3 block manager_strategy_text (P0), FQ2F block P0 | `quality_blocked_after_provenance` | source 已解，quality P0 block → 需 repair/replacement triage |

分类逻辑的关键区分点：
1. Source blocker 是否已解：provenance rerun evidence 确认两者 `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`，与 design.md §6.1 fallback 策略一致——`unavailable` 是允许 fallback 的失败类别。source blocker 确已解除。
2. Quality blocker 精确定位：`017641` 的 block 明确是 `manager_strategy_text` 字段 FQ2/FQ3 P0，不是泛化的 source 或 correctness 问题。provenance rerun artifact 第 49 行明确记录了 blocking issues 清单。
3. 两者的区分是 quality gate `warn` vs `block` 的二值差异，不是主观判断。

Plan 正确使用了 provenance rerun controller judgment 和 evidence rerun artifact 作为同源证据，没有引入间接推断。**无 finding。**

---

## Review Focus 3: 推荐 next gates 的顺序、scope 和 stop condition

**结论：顺序合理，scope 充分，stop condition 有效。有一个 non-blocking 观察。**

### 顺序合理性

Plan 推荐 110020 → 017641 的顺序，理由是：
- 两者直接消费 provenance rerun 新证据
- FOF 和 bond 未被 provenance rerun 改变，应延后

这个排序逻辑的隐含前提是"先消费已解锁证据，再处理未变 blocker"。这是保守但安全的策略。

**Finding F2 (non-blocking)**：Plan 未讨论 110020 gate 和 017641 gate 是否可以并行。两者处理不同 fund-type slot（index vs QDII），blocker 性质不同（quality warn review vs quality block triage），且消费不同的 quality gate issue 字段。并行化不会产生状态冲突。Plan 选择串行是安全的，但建议在 Handoff Recommendation 中注明"controller 可决定并行执行"以保留灵活性。不影响当前 gate 准入。

### 关于 FOF 和 bond 是否应优先

Plan 将 FOF（Candidate C）和 bond（Candidate D）列为"optional later gates"，理由是"not unlocked by the provenance rerun"。

验证这个判断：
- FOF：small baseline v1 run 确认 `007721` 和 `017970` 均为 QDII-FOF（系统分类为 `qdii_fund`），不是纯 FOF。Provenance rerun 没有改变它们的类型分类。要恢复 FOF 覆盖需要（a）找到纯 FOF 候选或（b）开 taxonomy design gate 重新定义 FOF/QDII-FOF 边界。两者都不依赖 provenance rerun 的成果。延后合理。
- Bond：bond-lens implementation 已被接受，`006597` 从 FQ4 block 降为 FQ4 warn + `bond_risk_evidence_missing.baseline_blocking=true`。下一步需要 positive `bond_risk_evidence.v1` 设计或 P1 residual triage。这确实是独立的 bond 领域路径，不依赖 provenance rerun。

Plan 的延后判断正确。先处理已解锁的 index/QDII slot，再回到 FOF/bond，是合理的优先级排序。

### Stop condition 充分性

110020 gate stop condition："Stop if plan attempts durable baseline/golden promotion, source strategy changes, or direct cache/PDF/source-helper inspection。"

017641 gate stop condition："Stop if plan weakens P0/FQ2/FQ3, implements extractor changes, or infers root cause without same-source evidence。"

这两个 stop condition 覆盖了：
- 禁止 promotion（与 Non-Goals 一致）
- 禁止 source/fallback 变更（与 AGENTS.md 硬约束一致）
- 禁止直接访问 cache/PDF（与 FundDocumentRepository 边界一致）
- 禁止 quality gate 弱化（与 FQ0-FQ6 不可变原则一致）
- 禁止 extractor 实现（与 plan-only scope 一致）
- 要求同源证据（与 AGENTS.md root cause 同源原则一致）

Stop condition 充分。**无 finding。**

---

## Review Focus 4: 硬禁止检查

逐项检查 plan 是否违反硬禁止：

| 硬禁止类别 | Plan 声明 | 验证结果 |
|---|---|---|
| 代码实现 | "Do not change source code" + scope 明确 "no code implementation" | 未违反 |
| renderer / FQ0-FQ6 | "Do not change current v0 renderer or 8-chapter output" + "Do not change FQ0-FQ6 quality gate behavior, thresholds, severity, or policy" | 未违反 |
| 默认 analyze/checklist | "Do not change Service/CLI defaults for analyze or checklist" | 未违反 |
| FundDocumentRepository / source strategy | "Do not change FundDocumentRepository, source strategy, source helper fallback semantics, cache behavior, PDF adapters, or downloaders" | 未违反 |
| Host / Agent / dayu | "Do not create Host/Agent packages, introduce dayu.host / dayu.engine, or build Dayu runtime integration" | 未违反 |
| baseline / golden / fixture promotion | "Do not promote any sample to durable baseline, clean denominator, fixture, or golden answer corpus" | 未违反 |
| GitHub mutation | "Do not run GitHub mutations, push, create PR, mark ready, merge, close PRs, delete branches, or commit" | 未违反 |

**全部硬禁止未被违反。无 finding。**

---

## Review Focus 5: Finding 汇总

| Finding ID | 类型 | 阻断级别 | 修订建议 |
|---|---|---|---|
| F1 | Candidate E 未显式枚举 `004393` 和 `004194` 的 golden readiness 剩余工作项 | non-blocking | 在 Candidate E "Unmet prerequisites" 中补充一行，概述两个已 clean candidate 的证据补齐需求（turnover/style evidence for active, tracking_error/turnover_rate for enhanced index） |
| F2 | 未讨论 110020 和 017641 两个 gate 是否可并行执行 | non-blocking | 在 Handoff Recommendation 中补充"controller 可根据资源情况决定两个 gate 串行或并行" |

---

## 附加验证

### Startup Packet Replay 一致性

Plan 的 Startup Packet 与 `docs/implementation-control.md` 一致：
- Current phase: `release maintenance` — 一致
- Current gate: `source provenance post-implementation bounded evidence rerun accepted locally` — 一致
- Next entry point: `post-provenance coverage recovery decision plan/review gate` — 一致

### Evidence Table 与 accepted artifacts 交叉校验

| Plan 表项 | Accepted artifact 验证点 | 一致性 |
|---|---|---|
| 110020: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `quality warn` | provenance rerun controller judgment 表 + evidence rerun 表 | 一致 |
| 017641: `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `quality block`, `manager_strategy_text` P0 | provenance rerun controller judgment 表 + evidence rerun 表 | 一致 |
| 004393: clean active candidate, quality warn, turnover/style gap | v1 run controller judgment: quality warn, candidate selection evidence | 一致 |
| 004194: clean enhanced-index candidate, quality warn, tracking_error/turnover_rate gaps | v1 run controller judgment: quality warn, correctness covered | 一致 |
| 006597: bond candidate, quality warn (not pass), `bond_risk_evidence_missing.baseline_blocking=true`, residual P1 | bond-lens controller judgment: quality warn, baseline_blocking=true, residual gaps | 一致 |
| FOF: data_gap / taxonomy_pending | v1 run controller judgment: `007721`/`017970` data_gap/taxonomy_pending | 一致 |

### Acceptance Matrix 完整性

两个推荐 gate 均具备：
- Required artifact 路径定义
- Required review（MiMo + GLM independent + controller judgment）
- Validation 条件
- Stop condition

可选延后 gate 的 deferral 理由明确且合理。

---

## Conclusion

**PASS_WITH_FINDINGS**

Plan 的事实断言全部与 accepted evidence 同源一致；110020/017641 的分类由 quality gate 状态差异精确驱动；next gate 排序逻辑合理；硬禁止全部遵守；stop condition 充分。两个 non-blocking finding（F1: Candidate E 前提完整性；F2: 并行化灵活性）均不影响 gate 准入，建议 controller 在接受时决定是否要求修订。
