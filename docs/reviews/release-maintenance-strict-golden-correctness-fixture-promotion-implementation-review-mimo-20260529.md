# Strict Golden Correctness / Fixture Promotion — Implementation Review (AgentMiMo)

日期：2026-05-29
角色：AgentMiMo implementation/evidence reviewer
Review target：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md` 及 `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-implementation-evidence-20260529.md`

## Verdict

**PASS_WITH_FINDINGS** — 2 medium findings、2 low findings。Decision artifact 整体结构完整、guardrails 正确、fixture manifest/schema 不变、无 promotion 执行。但存在 004194 P0 字段覆盖缺失的过度解读风险和 004393 P0/P1/P2 分类来源未显式引用的问题。

---

## Review Scope

已读取并交叉核验：

- Accepted plan：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md`
- DS re-review：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-rereview-ds-20260529.md`
- MiMo re-review：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-rereview-mimo-20260529.md`
- DS plan review：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-review-ds-20260529.md`
- MiMo plan review：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-review-mimo-20260529.md`
- Preflight JSON：`reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`
- Fixture manifest：`docs/reviews/fixture-promotion-state-manifest-20260529.json`
- Residual disposition manifest：`docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- Controller judgment：`docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md`
- Source score.json：004393、004194、006597
- Source quality_gate.json：004393、004194
- Source record_results：004393（150 records）、004194（150 records）

---

## 10 Rows 完整性验证

| fund/slot | preflight row | fixture manifest entry | residual manifest entry | decision table row | 一致性 |
|---|---|---|---|---|---|
| 004393 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 004194 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 006597 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 017641 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 096001 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 040046 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 019172 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 021539 | ✅ | ✅ | ✅ | ✅ | ✅ |
| FOF_SLOT | ✅ | ✅ | ✅ | ✅ | ✅ |
| 110020 | ✅ | ✅ | ✅ | ✅ | ✅ |

四份 artifact 对 10 个 entries 的 fund/slot + year 一致，blocker/owner/next_gate 无矛盾。FOF_SLOT source paths 为 null 符合预期。

---

## Source Score Correctness 数据验证

### 004393

| 字段 | Decision artifact 声称 | score.json 实际值 | 一致性 |
|---|---|---|---|
| `coverage_scope` | `partially_covered` | `partially_covered` | ✅ |
| `total_records` | 150 | 150 | ✅ |
| `comparable_records` | 9 | 9 | ✅ |
| `matched_records` | 9 | 9 | ✅ |
| `mismatched_records` | 0 | 0 | ✅ |
| `unavailable_records` | 141 | 141 | ✅ |

### 004194

| 字段 | Decision artifact 声称 | score.json 实际值 | 一致性 |
|---|---|---|---|
| `coverage_scope` | `covered` | `covered` | ✅ |
| `total_records` | 150 | 150 | ✅ |
| `comparable_records` | 5 | 5 | ✅ |
| `matched_records` | 5 | 5 | ✅ |
| `mismatched_records` | 0 | 0 | ✅ |
| `unavailable_records` | 145 | 145 | ✅ |

### 006597

| 字段 | Decision artifact 声称 | score.json 实际值 | 一致性 |
|---|---|---|---|
| `coverage_scope` | `not_configured` | `not_configured` | ✅ |
| `total_records` | 0 | 0 | ✅ |
| `comparable_records` | 0 | 0 | ✅ |
| `matched_records` | 0 | 0 | ✅ |
| `mismatched_records` | 0 | 0 | ✅ |
| `unavailable_records` | 0 | 0 | ✅ |

**Score-level 聚合数据全部准确。**

---

## Findings

### F1 — MEDIUM：004194 `promotion_prep_ready_candidate` 的 5 个 matched 字段全部为 P2 `index_profile`，无 P0 字段覆盖

**严重程度**：medium

**问题**：

Decision artifact 将 004194 标为 `promotion_prep_ready_candidate`，依据是 score-level `coverage_scope=covered`、5/5 matched、0 mismatch。但实际 record_results 显示 5 个 matched 字段全部来自 `index_profile`：

- `index_profile.benchmark_text`
- `index_profile.benchmark_identity_status`
- `index_profile.methodology_availability`
- `index_profile.constituents_availability`
- `index_profile.source_tier`

按 design.md §7.3 的 P0 字段定义（`basic_identity`、`classified_fund_type`、`benchmark`、`nav_benchmark_performance`、`fee_schedule`、`manager_strategy_text`），`index_profile` 不在 P0 列表中，属于 P2 或未分类字段。

这意味着 004194 的 `covered` 状态仅由 P2 字段的匹配支撑，而 P0 字段（`basic_identity`、`classified_fund_type`、`benchmark`、`nav_benchmark_performance`、`fee_schedule`、`manager_strategy_text`）全部在 145 个 unavailable records 中。Decision artifact 未报告此点。

**风险**：

004194 的 `covered` 语义可能被过度解读为"P0 字段已通过 correctness 验证"。实际上 P0 字段的 correctness 完全未经验证。Candidate rules（plan line 157-166）只要求 `coverage_scope=covered` 且 `mismatch=0`，未要求 P0 字段覆盖——这本身是 plan 的设计选择，但 decision artifact 应显式记录 matched 字段的优先级分布，让 controller 知情。

**与 004393 对比**：004393 作为 `conditional_candidate` 被要求提供 P0/P1/P2 breakdown（plan B3 的核心要求），但 004194 作为 `promotion_prep_ready_candidate` 却未被要求提供同等 breakdown。004393 的 9 个 matched 字段全部是 P0，反而比 004194 的 5 个 P2 matched 字段有更强的 P0 correctness 证据。

**建议**：

Decision artifact 的 004194 row 应增加一行记录：matched 字段清单及其优先级分类。Controller 在裁决 004194 的 `promotion_prep_ready_candidate` 时应知晓 P0 字段零覆盖的事实。如果 controller 认为 P0 覆盖是 promotion-prep 的必要条件，则 004194 应降级为 `conditional_candidate`。

---

### F2 — MEDIUM：004393 P0/P1/P2 breakdown 的分类来源未显式引用 `design.md` 或 `extraction_score.py` 的优先级定义

**严重程度**：medium

**问题**：

Decision artifact 的 004393 Partial Coverage Breakdown 声称：

- P0：11 total，9 comparable，2 unavailable（`manager_strategy_text.market_outlook`、`manager_strategy_text.strategy_summary`）
- P1：10 total，0 comparable，10 unavailable
- P2：0 total

实际 source data 验证：
- 9 matched 字段：`basic_identity`（5）、`benchmark.benchmark_name`（1）、`classified_fund_type.fund_type`（1）、`nav_benchmark_performance`（2）——这些确实属于 design.md §7.3 的 P0 字段组
- 2 unavailable P0：`manager_strategy_text.market_outlook`、`manager_strategy_text.strategy_summary`——source data 确认 status=unavailable
- P1 10 个 unavailable 字段：decision 列出的 `holder_structure`、`manager_alignment`、`product_profile`、`share_change` 子字段——source data 确认这些 status=unavailable

**数据一致性验证通过**，但 decision artifact 未引用分类来源。P0/P1/P2 优先级分类的权威来源是 `docs/design.md` §7.3-§7.4 还是 `fund_agent/fund/extraction_score.py` 中的 priority 映射？Implementation evidence 也未说明。

**风险**：

如果未来 priority 定义变更（例如 `index_profile` 从 P2 升为 P1），reviewer 无法追溯当前分类的依据。

**建议**：

Decision artifact 或 implementation evidence 应引用 P0/P1/P2 分类的来源文件和具体 section。

---

### F3 — LOW：`covered` + `unavailable_records=145` 的语义张力未在 decision artifact 中解释

**严重程度**：low

**问题**：

004194 的 score-level `coverage_scope=covered`，但 `unavailable_records=145`（96.7%）。004393 的 `coverage_scope=partially_covered`，`unavailable_records=141`（94%）。

两者的 unavailable 比例接近（96.7% vs 94%），但 coverage_scope 判定不同（`covered` vs `partially_covered`）。这说明 `coverage_scope` 的判定逻辑不是基于 unavailable 比例，而是基于 `comparable_records` 中的 matched/mismatched 比率——004194 的 5/5 全部 matched 所以 `covered`，004393 的 9/9 全部 matched 但因 `comparable_records < total_records` 的某个阈值而 `partially_covered`。

Decision artifact 未解释 `covered` 的语义：它只表示"所有 comparable records 均 matched"，不表示"大部分 records 已验证"。这对 controller 的裁决有直接影响。

**建议**：

Decision artifact 的 Strict Correctness Field Paths 节应增加一句说明：`covered` 仅表示 comparable records 中无 mismatch，不表示 total_records 的大部分已验证。

---

### F4 — LOW：006597 `needs_future_gate` 的 decision 与 manifest `promotion_blockers` 中 `strict_golden_not_configured` 的关系需确认

**严重程度**：low

**问题**：

Decision artifact 将 006597 标为 `needs_future_gate`，理由是 score-level `not_configured`。Fixture manifest 中 006597 的 `promotion_blockers` 包含 `strict_golden_not_configured`。Residual disposition manifest 中 006597 的 `current_blockers` 也包含 `strict_golden_not_configured`。

三者一致。但 fixture manifest 的 `blocking_reason` 还包含一句："bond_risk_evidence_missing is closed by accepted NAV-derived drawdown metric evidence, but fixture state remains absent and strict golden correctness remains unresolved." Decision artifact 在 `accepted_residuals` 列中写 "bond blocker is resolved context only"——这与 manifest 的 "closed" 语义一致。

**验证通过**。此 finding 仅确认 006597 的 bond blocker 解除 ≠ promotion 资格，decision artifact 正确处理。

---

## Guardrails 验证

| Guardrail | 要求 | 实际 | 状态 |
|---|---|---|---|
| `promotion_allowed=false` for every row | 所有 10 行 | fixture manifest 10 行全部 `promotion_allowed=false` | ✅ |
| No `fixture_state="promoted"` | 无 promoted 状态 | 无 promoted 或 `ready_for_future_promotion` | ✅ |
| No `fixture_state="promotion-prep-ready"` | schema 不变 | fixture manifest 未修改，`fixture_state` 只使用 `absent` / `deferred_from_v1` | ✅ |
| No golden answer / fixture mutation | 不改 golden | implementation evidence 确认无修改 | ✅ |
| No QDII probing | 不重启 | implementation evidence 确认 | ✅ |
| No FQ0-FQ6 weakening | 不弱化 | 无 quality gate 语义变更 | ✅ |
| No commit | 不提交 | implementation evidence 确认无 commit | ✅ |
| No JSON manifest modification | 不改 manifest | implementation evidence 确认无 JSON 修改 | ✅ |

**全部 guardrails 通过。**

---

## Docs-Only Validation 合理性

Implementation evidence 声明：本 gate 产出 Markdown-only evidence，不修改 Python runtime、CLI、preflight consumption、fixture manifest schema、score/quality/snapshot 行为，因此跳过 ruff/pytest。

**验证**：
- Decision artifact 是纯 Markdown ✅
- Implementation evidence 是纯 Markdown ✅
- 无 JSON manifest 被修改 ✅
- `fixture_state` schema 未变 ✅

**结论**：docs-only 不跑 ruff/pytest 合理。与 DS re-review 关注点 5 和 MiMo re-review F5 的裁决一致。

---

## 004393 / 004194 / 006597 Decision 逐项裁决建议

### 004393：`conditional_candidate_pending_partial_coverage_decision`

**裁决建议：合理，但需 controller 裁决。**

- P0/P1/P2 breakdown 数据与 source data 一致 ✅
- 9/150 partial coverage 足以触发 conditional 而非 automatic upgrade ✅
- P0 9/11 matched（2 个 `manager_strategy_text` unavailable）——P0 覆盖率 81.8%，风险可控
- P1 0/10 matched——P1 完全未验证
- P2 0/0——无 P2 字段
- `turnover_rate` warn owner 待定 ✅
- No automatic upgrade per plan stop conditions ✅

**残留风险**：P1 字段零覆盖。Controller 需裁决 P1 覆盖缺失是否阻断 conditional candidate。

### 004194：`promotion_prep_ready_candidate`

**裁决建议：需补充 P0 字段覆盖信息后由 controller 裁决。** 见 F1。

- 5/5 matched 且 0 mismatch ✅
- 但 5 个 matched 字段全部为 P2 `index_profile`，P0 字段零覆盖 ⚠️
- `tracking_error` P15 前置约束已标注 ✅
- `turnover_rate` warn owner 待定 ✅

**与 004393 对比**：004393 的 9 个 matched 字段全部是 P0（81.8% P0 覆盖率），但被标为 `conditional_candidate`；004194 的 5 个 matched 字段全部是 P2（0% P0 覆盖率），却被标为 `promotion_prep_ready_candidate`。这不是逻辑错误（plan 的 candidate rules 不要求 P0 覆盖），但语义上 004194 的 correctness 证据弱于 004393。

### 006597：`needs_future_gate`

**裁决建议：合理。**

- Bond blocker 解除仅作为 context，不作为 promotion 证据 ✅
- score-level `not_configured` 是 hard blocker ✅
- 需 rerun score with golden answer JSON ✅
- Fixture state 保持 `absent` ✅

---

## Residual Disposition / Fixture Manifest / Preflight Alignment

| 检查项 | 结论 |
|---|---|
| preflight `strict_golden_coverage` 与 fixture manifest `strict_golden_coverage` 一致 | ✅：004393/004194 `covered`，017641/QDII/110020 `fund_not_covered`，006597 `covered`，FOF `not_applicable` |
| fixture manifest `promotion_blockers` 与 preflight blockers 一致 | ✅ |
| residual disposition `promotion_allowed=false` 与 fixture manifest 一致 | ✅ |
| fixture manifest `fixture_state` 与 decision `fixture_state_after_gate` 一致 | ✅：004393/004194/006597 `absent`，deferred rows `deferred_from_v1` |
| controller judgment 的 next entry point 与本 gate 一致 | ✅：controller judgment 指向 `strict golden correctness / fixture promotion gate` |

---

## Summary

| ID | Severity | Finding | 建议 |
|---|---|---|---|
| F1 | MEDIUM | 004194 的 5 个 matched 字段全部为 P2 `index_profile`，P0 零覆盖，但被标为 `promotion_prep_ready_candidate`；004393 反而有 9 个 P0 matched 但被标为 `conditional_candidate` | Decision artifact 应记录 004194 matched 字段的优先级分布；controller 裁决是否需要 P0 覆盖作为 promotion-prep 必要条件 |
| F2 | MEDIUM | 004393 P0/P1/P2 breakdown 的分类来源未显式引用 design.md 或 extraction_score.py | Decision artifact 或 implementation evidence 应引用优先级分类的权威来源 |
| F3 | LOW | `covered` + `unavailable_records=145` 的语义张力未解释——`covered` 不等于"大部分已验证" | Decision artifact 应增加 `covered` 语义说明 |
| F4 | LOW | 006597 bond blocker 解除 ≠ promotion 资格的区分已正确处理 | 无需修改，仅确认 |

**Decision artifact 整体通过。Guardrails 全部满足。Fixture manifest/schema 不变。无 promotion 执行。无 ruff/pytest 需求。F1 需 controller 在裁决 004194 promotion-prep 资格时显式考虑 P0 字段覆盖问题。**

---

## Review Completion

Review 不修改 decision artifact、不修改 manifest、不执行 promotion、不提交。由 controller 裁决 F1（004194 P0 覆盖）和 F2（优先级来源引用）后决定是否需要 implementation worker 补充或修正。
