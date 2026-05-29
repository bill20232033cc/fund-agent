# Aggregate Deep Review: Strict Golden Correctness / Fixture Promotion Gate

| 字段 | 值 |
|---|---|
| **reviewer** | AgentGLM |
| **review_type** | aggregate_deepreview |
| **gate** | strict golden correctness / fixture promotion |
| **date** | 2026-05-29 |
| **scope** | 全链条 plan → review → rereview → decision → evidence → review → rereview → preflight → residual → fixture manifests |
| **artifacts_reviewed** | 11 份 gate chain 文档 + fixture-promotion-state-manifest + golden-readiness-residual-disposition-manifest + 3 份 score.json + extraction_score.py + design.md + implementation-control.md |
| **classification** | heavy (docs-only, read-only evidence gate) |

---

## 1. 总裁定

**VERDICT: PASS**

全链条自洽、守卫完整、无遗漏升级。所有用户指定检查点均已独立验证通过。004194 降级决策保守正确，004393 条件候选合理，006597 正确推迟至 future gate。未发现阻断性问题。

---

## 2. 用户指定检查点逐项验证

### 2.1 004393 — conditional partial coverage

| 声明 | 独立验证 | 结论 |
|---|---|---|
| decision = `conditional_candidate_pending_partial_coverage_decision` | decision 文档确认 | **PASS** |
| P0 部分覆盖：5/6 P0 字段 score pass，`fee_schedule` FAIL (0.0/0.0) | score.json 独立读取确认：basic_identity/classified_fund_type/benchmark/nav_benchmark_performance/manager_strategy_text pass，fee_schedule fail | **PASS** |
| P0 正确性 9/11 comparable (evidence manual analysis) | score.json correctness.status = "not_implemented"；9/11 来自 gate worker 手动分析而非自动化评分管线 | **PASS** (见 F1) |
| P1 大面积缺失：turnover_rate/holdings_snapshot FAIL | score.json 确认：turnover_rate 0.0/0.0, holdings_snapshot 0.0/0.0 | **PASS** |
| fixture_state = absent, promotion_allowed = false | manifest 独立验证 | **PASS** |

**结论**：004393 作为 `mandatory_known_failure_domestic_stock` 进入 golden set，P0 存在 `fee_schedule` 硬失败，P1 多字段缺失。conditional 候选定位准确，未升级至 prep-ready。

### 2.2 004194 — conditional P0 coverage

| 声明 | 独立验证 | 结论 |
|---|---|---|
| decision = `conditional_candidate_pending_p0_coverage_decision` (从 promotion_prep_ready_candidate 降级) | decision 文档确认；DS/MiMo rereview 均确认降级 | **PASS** |
| P0 score 全 pass (6/6) | score.json 确认：basic_identity/classified_fund_type/benchmark/nav_benchmark_performance/fee_schedule/manager_strategy_text 全 pass | **PASS** |
| P0 golden answer 正确性覆盖 = 0 (无 P0 字段参与 golden answer 比对) | score.json correctness: 5/5 matched 全部为 `index_profile` (P1) sub-fields，零 P0 字段有 golden answer 记录 | **PASS** |
| P1 failures: tracking_error 0.0/0.0, turnover_rate 0.0/0.0 | score.json 独立确认 | **PASS** |
| 降级语义合理性 | MiMo F1 指出语义倒挂（004393 有 9 P0 匹配却是 conditional，004194 零 P0 匹配却是 prep_ready_candidate）；降级消除倒挂 | **PASS** |

**结论**：004194 的 P0 字段 coverage score 全 pass，但 P0 层面无 golden answer 正确性验证（5/5 matched 全在 P1 index_profile）。降级为 conditional_candidate_pending_p0_coverage_decision 保守且正确。

### 2.3 006597 — needs score rerun with golden answer and bond blocker resolved context

| 声明 | 独立验证 | 结论 |
|---|---|---|
| decision = `needs_future_gate` | decision 文档确认 | **PASS** |
| P0 score 全 pass (6/6) | score.json 确认：所有 P0 字段 pass | **PASS** |
| P1 failures: turnover_rate/holder_structure/share_change | score.json 独立确认：三字段均为 0.0/0.0 | **PASS** |
| bond_risk_evidence 全 7 组 satisfied | score.json 确认 bond_risk_evidence 1.0/1.0 pass；manifest 确认 blocker closed_by_accepted_nav_derived_drawdown_metric_gate | **PASS** |
| correctness.status = unavailable, coverage_scope = not_configured | score.json 独立确认：无 golden answer JSON 配置 | **PASS** |
| 需要 score rerun with golden answer | 确认：当前 scoring run 未配置 golden answer，严格正确性无法验证 | **PASS** |

**结论**：006597 bond risk blocker 已关闭（7 组全 satisfied），但 strict golden correctness 因无 golden answer 配置而不可用。`needs_future_gate` 定位准确，前置条件为：(1) 配置 golden answer JSON；(2) 基于 bond blocker resolved context 重跑评分。

### 2.4 017641 / QDII / FOF / 110020 — deferred/blocked

| 条目 | fixture_state | promotion_allowed | blocker | 验证 |
|---|---|---|---|---|
| 017641 | deferred_from_v1 | false | fixture_promotion_absent | manifest 确认 |
| QDII (096001/040046/019172/021539) | deferred_from_v1 | false | fixture_promotion_absent + qdii_replacement_hard_stop (GLOBAL) | manifest 确认 |
| FOF_SLOT | deferred_from_v1 | false | fixture_promotion_absent | manifest 确认 |
| 110020 | deferred_from_v1 | false | fixture_promotion_absent | manifest 确认 |

**结论**：所有 deferred/blocked 条目 fixture_state 未变，promotion_allowed = false，QDII 全局硬拦截生效。**PASS**。

### 2.5 所有 promotion_allowed = false

独立验证范围：
- `fixture-promotion-state-manifest-20260529.json`：全部 10 条目 + 2 全局 blocker，promotion_allowed = false
- `golden-readiness-residual-disposition-manifest-20260529.json`：全部 12 条目，promotion_allowed = false
- `extraction_score.py` 及 `golden_readiness_preflight.py`：无代码路径设置 promotion_allowed = true
- `docs/implementation-control.md`：明确声明 "All entries keep promotion_allowed=false"

**结论**：**PASS**。代码/manifest/控制文档三方一致，零 promotion 授权。

### 2.6 fixture_state unchanged

- 004393/004194/006597：fixture_state = `absent`（gate 前后一致，未变更）
- 其余 7 条目：fixture_state = `deferred_from_v1`（未变更）
- Decision 文档明确声明 "no fixture manifest update"
- Git log 仅含 3 个 docs commit，无 manifest schema 变更

**结论**：**PASS**。

### 2.7 No golden promotion / golden fixture / runtime / manifest changes

Evidence 文档声明的 8 项 boundary 守卫逐项验证：

| 守卫 | 验证 |
|---|---|
| no golden answer modified | correctness.status 未变更（004393 not_implemented, 004194 available, 006597 unavailable）；golden_set.json 内容与 scoring run 原始产物一致 | **PASS** |
| no fixture modified | fixture_state 全部保持 absent/deferred_from_v1 | **PASS** |
| no score/quality/snapshot modified | score.json 为 scoring run 原始产物，未被 gate 改写 | **PASS** |
| no fixture manifest schema change | manifest schema = `fund-agent.fixture-promotion-state.v1`，无版本变更 | **PASS** |
| no promotion executed | promotion_allowed = false 全覆盖，无代码路径可执行 promotion | **PASS** |
| no QDII probing | QDII 全局硬拦截 qdii_replacement_hard_stop 生效 | **PASS** |
| no FOF taxonomy shortcut | FOF_SLOT fixture_state = deferred_from_v1，未触发分类捷径 | **PASS** |
| no Host/Agent/dayu | 全链条文档无 dayu-agent 运行时引用 | **PASS** |

### 2.8 Docs-only validation 合理性

- Gate 分类为 heavy (docs-only, read-only evidence)
- 无代码变更 → ruff/pytest 跳过合理
- 产物为 decision/evidence 文档 → markdown 校验即可
- DS L3 指出 "future gate regression conditions not declared"，已承认但不在当前 gate scope

**结论**：docs-only validation 在当前 gate scope 内合理。**PASS**。

---

## 3. 链条完整性审查

### 3.1 Review Chain Closure

| 阶段 | 产出 | Reviewer | 结论 | 阻断问题 |
|---|---|---|---|---|
| Plan | plan-20260529 | — | — | — |
| Plan Review (DS) | plan-review-ds | AgentDS | PASS_WITH_FINDINGS (B1-B3, W1-W4) | 3 blocking |
| Plan Review (MiMo) | plan-review-mimo | AgentMiMo | PASS_WITH_FINDINGS (F1-F5) | 2 medium |
| Plan Re-review (DS) | plan-rereview-ds | AgentDS | ALL B1-B3 CLOSED, W1-W4 ADDRESSED | 0 |
| Plan Re-review (MiMo) | plan-rereview-mimo | AgentMiMo | PASS, F1-F5 ALL CLOSED | 0 |
| Decision | decision-20260529 | AgentCodex | 10 rows, all promotion_allowed=false | — |
| Evidence | implementation-evidence-20260529 | AgentCodex | 8 项 boundary 守卫 | — |
| Impl Review (DS) | implementation-review-ds | AgentDS | PASS_WITH_FINDINGS (M1-M2, L1-L3, I1) | 0 blocking |
| Impl Review (MiMo) | implementation-review-mimo | AgentMiMo | PASS_WITH_FINDINGS (F1-F4) | 0 blocking |
| Impl Re-review (DS) | implementation-rereview-ds | AgentDS | PASS, M1-M2/L1-L3/I1 ALL CLOSED | 0 |
| Impl Re-review (GLM) | implementation-rereview-glm | AgentGLM | PASS, ALL PREVIOUS FINDINGS CLOSED | 0 |

**链条闭合状态**：所有 plan 阶段 B1-B3 已关闭，所有 implementation 阶段 M1-M2/F1-F4 已关闭。无遗留阻断。**PASS**。

### 3.2 关键决策演变追踪

| Fund | 初始分类 | 最终分类 | 降级原因 | 验证 |
|---|---|---|---|---|
| 004194 | promotion_prep_ready_candidate | conditional_candidate_pending_p0_coverage_decision | P0 golden answer 正确性覆盖为零；MiMo F1 语义倒挂 | 保守正确 |
| 004393 | conditional_candidate (P0 9/11) | conditional_candidate_pending_partial_coverage_decision | P0 有 fee_schedule 硬失败，P1 大面积缺失 | 合理 |
| 006597 | needs_future_gate | needs_future_gate (未变) | correctness unavailable，无 golden answer | 合理 |

---

## 4. Findings

### F1 (LOW): 004393 P0 comparable 分数来源歧义

Decision 文档中 004393 "P0 9/11 comparable" 来自 gate worker 手动分析（evidence extraction），而 score.json correctness.status = "not_implemented" 表明自动化评分管线未执行正确性比对。两个数据源（手动 vs 自动）的数字口径不完全对齐。

**影响**：不影响 gate decision（已定为 conditional），但 future gate 若引用 9/11 数字需明确标注来源为手动 evidence extraction 而非自动化评分。

**建议**：future gate 对 004393 启用自动化 correctness 评估，消除手动/自动口径差异。

### F2 (LOW): 006597 golden answer 未配置未作为显式前置条件

Decision 文档对 006597 的 next_gate 描述为 "needs_future_gate"，但未将 "配置 golden answer JSON" 列为显式前置条件。当前 006597 的 scoring run 配置为 coverage_scope = "not_configured"。

**影响**：future gate 执行者可能遗漏此前置条件。

**建议**：在 implementation-control.md 或 next gate plan 中明确列出 "006597 future gate 前置条件：(1) 配置 golden answer JSON for bond_fund scoring run；(2) 基于 bond blocker resolved context 重跑评分"。

### F3 (INFO): 三基金共享 P2 traceability 系统性缺口

004393/004194/006597 均有 `investor_return` (0.0/0.0) 和 `nav_data` (coverage=1.0, traceability=0.0) 失败。这不是基金特有问题而是系统性 traceability 缺口。

**影响**：不影响当前 gate decision（P2 为最低优先级），但应在 quality roadmap 中跟踪。

### F4 (INFO): 004194 covered 覆盖面极窄

004194 的 5/5 golden answer matched 仅覆盖 `index_profile` 的 5 个 sub-field（3.3% of 150 golden records）。P0/P2 层面零 golden answer 验证。current decision 正确反映此限制（conditional_candidate_pending_p0_coverage_decision），但 future gate 不应将 "5/5 matched" 等同于 "golden correctness verified"。

---

## 5. Positive Observations

1. **004194 降级决策链条完整**：Plan → DS/MiMo 发现语义倒挂 → Decision 降级 → DS/MiMo/GLM 确认关闭。多 reviewer 交叉验证有效。
2. **守卫边界严格**：8 项 boundary 守卫全部满足，无代码/manifest/scoring 变更。
3. **QDII 全局硬拦截**：qdii_replacement_hard_stop 作为 GLOBAL blocker 生效，正确阻止 QDII 类基金进入任何 promotion 路径。
4. **docs-only 边界自律**：Gate 未越界执行任何 runtime 操作，严格保持为只读 evidence gate。
5. **双维度模型（fund-level membership + score-level comparability）** 有效区分了 coverage 和 correctness 两个独立维度。

---

## 6. 总结

| 维度 | 结论 |
|---|---|
| 004393 conditional partial coverage | **VERIFIED** — P0 有 fee_schedule 硬失败，conditional 定位准确 |
| 004194 conditional P0 coverage | **VERIFIED** — P0 score pass 但 P0 golden answer 正确性为零，降级保守正确 |
| 006597 needs score rerun | **VERIFIED** — correctness unavailable，需 golden answer + bond blocker resolved context |
| 017641/QDII/FOF/110020 deferred/blocked | **VERIFIED** — fixture_state 未变，QDII 全局硬拦截生效 |
| All promotion_allowed = false | **VERIFIED** — 代码/manifest/控制文档三方一致 |
| fixture_state unchanged | **VERIFIED** — absent/deferred_from_v1 均未变更 |
| No golden/fixture/runtime/manifest changes | **VERIFIED** — 8 项 boundary 守卫全部满足 |
| docs-only validation | **VERIFIED** — 无代码变更，跳过 ruff/pytest 合理 |

**Final Verdict: PASS** — 全链条自洽，所有检查点独立验证通过，4 项 findings 均为 LOW/INFO 级别，无阻断。

---

*AgentGLM aggregate deepreview — 2026-05-29*
