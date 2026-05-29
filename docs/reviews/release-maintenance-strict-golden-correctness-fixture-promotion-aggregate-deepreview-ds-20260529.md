# Strict Golden Correctness / Fixture Promotion Gate — Aggregate Deepreview (AgentDS)

日期：2026-05-29
角色：AgentDS aggregate deepreview worker
审查范围：plan → plan reviews (DS/MiMo) → plan rereviews (DS/MiMo) → decision → implementation evidence → implementation reviews (DS/MiMo) → implementation rereviews (DS/GLM) → manifests (fixture/residual/preflight)
Gate classification：`heavy`

## 前置阅读

已读取并全量交叉核验：

- `AGENTS.md`、`docs/design.md` (v2.2)、`docs/implementation-control.md` (v2.1)
- fixture promotion state manifest (`fixture-promotion-state-manifest-20260529.json`)
- golden readiness residual disposition manifest (`golden-readiness-residual-disposition-manifest-20260529.json`)
- preflight JSON/Markdown (`golden_readiness_preflight.json/.md`)
- fixture manifest controller judgment
- 全部 13 个本 gate artifact（plan、2 plan reviews、2 plan rereviews、decision、implementation evidence、2 implementation reviews、2 implementation rereviews、本 aggregate deepreview）
- 10 entries 的 source score.json / quality_gate.json（004393/004194/006597/017641/096001/040046/019172/021539/110020）
- 004393 与 004194 的 `correctness.record_results[]` 完整字段级数据

---

## 1. Accepted Decision 目标满足度

### 1.1 本 gate 目标回顾

Plan 定义的目标：形成 accepted decision——哪些 fund/slot 可进入 future promotion-prep candidate 决策路径，哪些继续 blocked/deferred，每项缺什么证据、owner 和 next_gate。Candidate 语义只写于 decision artifact 的 `decision` 字段，不写入 fixture manifest `fixture_state`，所有 row `promotion_allowed=false`。

### 1.2 Decision 最终状态

| fund/slot | decision | fixture_state | key evidence |
|---|---|---|---|
| `004393` | `conditional_candidate_pending_partial_coverage_decision` | `absent` | P0 9/11 matched (81.8%), P1 0/10, overall 9/150 (6%) |
| `004194` | `conditional_candidate_pending_p0_coverage_decision` | `absent` | P0 0/0, 5/5 `index_profile.*` matched, overall 5/150 (3.3%) |
| `006597` | `needs_future_gate` | `absent` | bond blocker closed; score `not_configured`; needs rerun with golden answer |
| `017641` | `deferred_from_minimum_v1` | `deferred_from_v1` | QDII, quality `block`, `fund_not_covered` |
| `096001` | `deferred_from_minimum_v1` | `deferred_from_v1` | QDII, quality `block`, `fund_not_covered` |
| `040046` | `deferred_from_minimum_v1` | `deferred_from_v1` | QDII, quality `block`, `fund_not_covered` |
| `019172` | `deferred_from_minimum_v1` | `deferred_from_v1` | QDII, quality `block`, `fund_not_covered` |
| `021539` | `deferred_from_minimum_v1` | `deferred_from_v1` | QDII, quality `block`, `fund_not_covered` |
| `FOF_SLOT` | `deferred_from_minimum_v1` | `deferred_from_v1` | no source artifacts, `not_applicable` |
| `110020` | `deferred_from_minimum_v1` | `deferred_from_v1` | `fund_not_covered`, `index_evidence_insufficient` |

**目标满足度：通过。** 10 entries 均有明确 decision、blocker、missing evidence、owner、next gate。Candidate 语义严格限制在 decision artifact 的 `decision` 字段，`fixture_state_after_gate` 全部使用既有枚举（`absent` / `deferred_from_v1`），无 `promotion-prep-ready` 写入 manifest。所有 row `promotion_allowed=false`。

---

## 2. 逐项状态正确性验证

### 2.1 004393 — 状态正确 ✅

**Preflight**：`strict_golden_coverage=covered`（fund-level membership），`readiness=deferred_with_owner`

**Score**：`coverage_scope=partially_covered`，`total_records=150`，`comparable_records=9`，`matched_records=9`，`mismatched_records=0`，`unavailable_records=141`

**P0/P1/P2 breakdown**（已独立验证 `record_results[]`）：
- P0：11 total，9 comparable/matched，2 unavailable（`manager_strategy_text.market_outlook`、`manager_strategy_text.strategy_summary`）。P0 覆盖率 81.8%。
- P1：10 total，0 comparable，10 unavailable。P1 覆盖率 0%。
- P2：0 total。

**Quality**：`warn`（`turnover_rate` FQ2/FQ2F + FQ0 info），非 block。

**Decision 正确性**：`conditional_candidate_pending_partial_coverage_decision` 是正确的。9/150 (6%) 可比覆盖率太低，不能自动升级。但 P0 覆盖尚可（81.8%），值得 future gate 进一步评估。Plan B3 的核心要求（不自动升级、需 P0/P1/P2 breakdown、controller 裁决）已全部满足。

### 2.2 004194 — 状态正确，降级合理 ✅

**Preflight**：`strict_golden_coverage=covered`（fund-level membership），`readiness=deferred_with_owner`

**Score**：`coverage_scope=covered`，`total_records=150`，`comparable_records=5`，`matched_records=5`，`mismatched_records=0`，`unavailable_records=145`

**关键发现（本 deepreview 确认）**：
- 5 个 matched 字段全部属于 `index_profile.*`（`benchmark_text`、`benchmark_identity_status`、`methodology_availability`、`constituents_availability`、`source_tier`），按 `docs/design.md` §7.3 为 conditional P1（仅适用于 index/enhanced-index 基金）。
- P0 strict correctness coverage = **0**。`basic_identity`、`classified_fund_type`、`benchmark`（非 index_profile）、`nav_benchmark_performance`、`fee_schedule`、`manager_strategy_text` 全部不在 comparable records 中。
- `unavailable_records=145` 全部为跨基金 `fund_code=004393` golden records，004194 自身 intra-fund unavailable = **0**。已在 decision artifact §004194 Covered Scope Breakdown 中显式标注。

**降级轨迹**：
- Plan 初始推荐：`promotion_prep_ready_candidate`（最强的 candidate）
- MiMo implementation review F1 发现 P0 零覆盖，建议降级
- DS implementation review M2 发现 5 fields 仅限 `index_profile.*`
- Decision 最终：`conditional_candidate_pending_p0_coverage_decision`
- DS rereview 确认降级合理："conservative 且正确"
- GLM rereview 确认："降级语义正确，P0 零覆盖事实已透明记录"

**Decision 正确性**：`conditional_candidate_pending_p0_coverage_decision` 是正确的。`coverage_scope=covered` 仅表示 5/5 comparable matched，不表示 P0 字段经过 correctness 验证。降级后与 004393 同属 `conditional_candidate_pending_*` 层级，消除了语义倒挂。

**Future gate 警示**：004194 的 strict golden correctness 仅覆盖 index_profile 子字段。标准字段（basic_identity、fee_schedule 等）的 golden correctness 尚未建立。future gate 不应将 004194 的 `covered` 理解为广义 correctness 验证。

### 2.3 006597 — 状态正确 ✅

**Preflight**：`strict_golden_coverage=covered`（fund-level membership，fund 在 golden JSON 中）

**Score**：`coverage_scope=not_configured`，`total_records=0`。原因是 score run 的 `golden_answer_path=null`（bond risk evidence run 不需要 correctness 比对）。

**Bond blocker**：已关闭（fixture manifest `resolved_context` 确认，quality gate 无 `bond_risk_evidence_missing`）。仅作为 resolved context，不作为 promotion 证据。

**Decision 正确性**：`needs_future_gate` 是正确的。`not_configured` 是运行配置问题（可通过 rerun score with `reports/golden-answers/golden-answer.json` 解决），不是数据不可得问题。与 110020 的 `fund_not_covered`（hard blocker）有本质区别。Plan 的 006597 special rule 和 decision 的 missing_evidence 均正确反映了这一点。

**注意**：006597 的 bond blocker 关闭来自 drawdown metric gate 的 accepted evidence。004393 和 004194 没有 bond risk evidence 需求（非债券基金），因此 bond blocker 上下文不适用于它们——这一点在决策链中保持正确。

### 2.4 017641 — 状态正确 ✅

QDII 基金。`fund_not_covered`（不在 golden answer v1 fund-level coverage 中）。Quality `block`（P0 `manager_strategy_text`）。Prior disposition `replace`。

**Decision 正确性**：`deferred_from_minimum_v1` 是正确的。source provenance 完整（eligible fallback），但 P0 block + fund_not_covered 双重阻断。Replacement disposition 保持不变。Plan 的 017641 special rule 正确处理。

### 2.5 QDII 四行（096001/040046/019172/021539）— 状态正确 ✅

全部 `fund_not_covered` + quality `block` + `qdii_coverage_blocked`。

**Decision 正确性**：全部 `deferred_from_minimum_v1`。QDII hard stop 已 accepted，无新 probing，无 evidence run 重启。Plan 的 QDII rule 和 control doc 的 `qdii_replacement_hard_stop` global blocker 均保持一致。

### 2.6 FOF_SLOT — 状态正确 ✅

无 source snapshot/score/quality artifacts（paths null）。`strict_golden_coverage=not_applicable`。Blockers: `fof_taxonomy_pending`、`fof_data_gap`。

**Decision 正确性**：`deferred_from_minimum_v1`。需要 repository-verified pure FOF candidate。QDII-FOF 不计入 pure FOF。Plan 的 FOF rule 正确处理。

### 2.7 110020 — 状态正确 ✅

`fund_not_covered`（hard blocker——基金不在 golden answer v1 中）。Quality `warn`（非 block）。`index_evidence_insufficient`。

**Decision 正确性**：`deferred_from_minimum_v1`。区分于 006597 的 `not_configured`（可 rerun）：110020 的 `fund_not_covered` 是 hard blocker，因为基金本身不在 golden answer JSON 的 fund-level coverage 中。这是 fixable（future methodology/constituents/reviewed fact freeze gate 可能将 110020 加入 golden answer），但不是 rerunnable（不能通过 rerun score 解决）。Plan W3 和 decision 均正确区分。

---

## 3. Guardrails 验证：无 Promotion / 无修改

### 3.1 Promotion

| 检查项 | 要求 | 实际 | 状态 |
|---|---|---|---|
| 全部 entry `promotion_allowed=false` | 10 entries | fixture manifest 10 entries 全部 `promotion_allowed=false` | ✅ |
| 无 `fixture_state="promoted"` | 禁止 | manifest 无此值 | ✅ |
| 无 `fixture_state="ready_for_future_promotion"` | 禁止 | manifest 无此值 | ✅ |
| 无 `fixture_state="promotion-prep-ready"` | 禁止写入 manifest | manifest `fixture_state` 仅使用 `absent` / `deferred_from_v1` | ✅ |
| Candidate 语义仅存于 decision artifact | 分层 | `decision` 字段使用新 enum，`fixture_state` 使用既有 enum | ✅ |
| Global `promotion_allowed_default=false` | 全局 | fixture manifest top-level 确认 | ✅ |
| `promotion_manifest=false` | 全局 | fixture manifest top-level 确认 | ✅ |

### 3.2 Golden Fixture / Manifest / Schema / Runtime / Score / Quality / Snapshot

| 检查项 | 状态 |
|---|---|
| `reports/golden-answers/` 未修改 | ✅ — git status 无相关变更 |
| fixture manifest JSON 未修改 | ✅ — git status 无 JSON 变更；manifest schema_version 仍为 `v1` |
| fixture manifest schema 未变 | ✅ — 无新增 `fixture_state` 值，无新增字段 |
| residual disposition manifest 未修改 | ✅ |
| preflight 未重跑 | ✅ — docs-only gate，不需要 |
| Python runtime 未修改 | ✅ — `fund_agent/` 无变更 |
| score artifacts 未修改 | ✅ — `reports/extraction-snapshots/` 和 `reports/scoring-runs/` 无变更 |
| quality gate artifacts 未修改 | ✅ — `reports/quality-gate-runs/` 无变更 |
| snapshot artifacts 未修改 | ✅ |
| FQ0-FQ6 语义未弱化 | ✅ |
| QDII probing 未重启 | ✅ |
| FOF taxonomy 例外未引入 | ✅ |
| QDII-FOF 未计入 pure FOF | ✅ |
| Host / Agent / dayu 未引入 | ✅ |
| 无 commit 产生 | ✅ — 所有产物均为 untracked Markdown |
| 无 PR/push/merge/release | ✅ |

**结论：全部 guardrails 通过。本 gate 是严格的 docs-only implementation，未触及任何生产路径、数据产物、schema 或 runtime。**

---

## 4. 验证策略足够性评估

### 4.1 Review 覆盖

| 阶段 | Reviewer | Verdict | 关键发现 |
|---|---|---|---|
| Plan review | DS | PASS_WITH_FINDINGS (3B/4W/2I) | B1 fixture_state enum, B2 non-homogeneous source, B3 004393 threshold |
| Plan review | MiMo | PASS_WITH_FINDINGS (2M/3L) | F1 promotion-prep-ready enum, F2 correctness data path |
| Plan rereview | DS | B1-B3 CLOSED, W1-W4 ADDRESSED | 5 user concerns verified |
| Plan rereview | MiMo | PASS | All DS/MiMo findings closed |
| Implementation review | DS | PASS_WITH_FINDINGS (2M/3L/1I) | M1 cross-fund unavailable, M2 004194 index_profile scope |
| Implementation review | MiMo | PASS_WITH_FINDINGS (2M/2L) | F1 004194 P0=0, F2 priority source citation |
| Implementation rereview | DS | PASS | M1/M2/F1/F2/F3 all closed |
| Implementation rereview | GLM | PASS | All findings closed |

**Review 密度**：8 份独立 review/rereview，覆盖 plan 和 implementation 两个阶段。4 个 reviewer（DS、MiMo、DS rereview、GLM rereview），满足 AGENTS.md heavy gate 的 "至少两份独立 review" 要求，且超出最低要求。

### 4.2 Review Quality

- **B1 (fixture_state enum violation)** 被 DS plan review 在 implementation 前捕获，避免了 schema 破坏。修订 plan 通过严格分层（decision enum vs fixture_state enum）彻底解决。
- **M2/F1 (004194 P0=0)** 被 DS 和 MiMo implementation review 独立发现，导致 decision 从 `promotion_prep_ready_candidate` 降级为 `conditional_candidate_pending_p0_coverage_decision`。这是 review 链的核心价值——plan 只看到 `coverage_scope=covered`，未下钻到 matched 字段的优先级分布。
- **M1 (cross-fund unavailable)** 是数据语义透明度问题，不影响 decision 正确性，但提升了对 future reviewer 的可解释性。
- **F2 (priority source citation)** 确保 future auditability。

### 4.3 自行验证

本 aggregate deepreview 独立核验了：
- 10 entries 在 preflight ↔ residual manifest ↔ fixture manifest ↔ decision 之间的一致性（全部一致）
- 004393 P0/P1/P2 breakdown 与 source `record_results[]` 的一致性（准确）
- 004194 5 matched 字段与 source `record_results[]` 的一致性（准确，全部为 `index_profile.*`）
- 006597 `not_configured` 原因（`golden_answer_path=null`，确认）
- Quality status 与 source quality_gate.json 的一致性（全部匹配）
- `promotion_allowed=false` 全局一致性（fixture manifest 10 entries + 2 global blockers 全部 false）
- Ruff/pytest 跳过理由的合理性（docs-only，无 Python runtime 变更，符合 plan Validation Matrix）

### 4.4 验证策略结论

**足够。** 8 份 review + 本 aggregate deepreview 形成了密集的 adversarial review 网。B1/B2/B3 在 plan 阶段被捕获，M1/M2/F1/F2 在 implementation 阶段被捕获，全部在 acceptance 前关闭。无遗漏的 blocking finding。

---

## 5. Remaining Residuals 和 Next Gates 清晰度

### 5.1 Immediate Next Gates

| Priority | Gate | Owner | 前置条件 |
|---|---|---|---|
| 1 | 004393 partial coverage decision gate | future fixture promotion gate + controller | 本 gate 的 P0/P1/P2 breakdown 已被接受；controller 裁决 partial coverage 是否可接受 |
| 2 | 004194 P0 strict correctness coverage decision gate | future fixture promotion gate + P0 coverage decision owner | P0=0 的事实已记录；future gate 决定是否需要 P0 覆盖作为 promotion 前提 |
| 3 | 006597 strict golden correctness score rerun | future fixture promotion gate + baseline/golden preflight owner | 以 `reports/golden-answers/golden-answer.json` 为输入 rerun score；产出 `coverage_scope` 和 match 结果 |
| 4 | 004194 P15 tracking-error evidence gate | P15 tracking-error evidence owner | `docs/design.md` §7.4 要求 reviewed direct observed disclosure evidence 才能添加 tracking_error golden rows |
| 5 | 110020 index reviewed fact freeze / methodology / constituents evidence gate | future index evidence sufficiency gate | 硬阻断是 `fund_not_covered`；需先解决 golden answer coverage 再评估 score correctness |
| 6 | QDII diagnosis or explicit deferred-from-v1 disposition gate | future QDII diagnosis owner | 当前 hard stop；QDII probing 不重启 |
| 7 | Pure FOF repository-verified candidate gate | future FOF taxonomy owner | QDII-FOF 不可计入 |

### 5.2 Long-Running Residuals（从 control doc Open Residuals 继承）

| Residual | 本 gate 影响 |
|---|---|
| QDII hard stop | 不变。4 QDII rows + 017641 保持 deferred |
| Golden answer corpus v1 blocked | 不变。`overall_status=block`，`ready_count=0` |
| Fixture promotion state manifest not promotion | 不变。本 gate 未更新 manifest，所有 `promotion_allowed=false` |
| Tracked residual disposition manifest not runtime-consumed | 不变。本 gate 未引入 runtime consumption |
| `006597` remaining quality warnings (turnover/holder/share_change) | 不变。非 bond-risk，属于 future readiness gate |

### 5.3 清晰度评估

**清晰。** 每个 entry 的 next gate、owner、missing evidence 在 decision table 中显式记录。本 gate 正确地将 004393 和 004194 置于 `conditional_candidate_pending_*` 状态——它们不再是简单的 blocked，但也不能自动进入 promotion-prep。Future gate 有足够信息做出进一步裁决。

---

## 6. Adversarial Failure Pass

### 6.1 假设 adversary 试图利用本 gate 的产物进行非授权 promotion

**攻击面**：将 decision artifact 的 `promotion_prep_ready_candidate` 误解为 promotion 授权，或利用 `coverage_scope=covered` 声称 004194 的 correctness 已验证。

**防御**：
- Decision artifact 的 `decision` 字段与 fixture manifest 的 `fixture_state` 严格分层——candidate 语义不在 manifest 中
- 004194 已降级为 `conditional_candidate_pending_p0_coverage_decision`，不再是 `promotion_prep_ready_candidate`
- Decision §Strict Correctness Field Paths 显式声明 `covered` 只表示 comparable records matched，不表示大部分 total_records 已验证
- 所有 entry `promotion_allowed=false`，manifest `promotion_manifest=false`，manifest `promotion_allowed_default=false`
- Control doc §Next Entry Point 明确："It must not enter promotion unless a separate promotion gate is explicitly authorized"

**结论：攻击面已被有效关闭。**

### 6.2 假设 adversary 试图利用 `coverage_scope` 的歧义

**攻击面**：将 preflight `strict_golden_coverage=covered`（fund-level membership）与 score `coverage_scope=covered`（field-level comparability）混用，声称 006597 的 strict correctness 已满足。

**防御**：
- Plan B2 建立了双维度真源模型：fund-level membership（来源 preflight）和 score-level field comparability（来源 score.json）
- 裁决规则：不一致时以 score-level 为主
- Decision table 每行显式列出 `fund_level_membership` 和 `score_level_field_comparability` 两个独立列
- 006597：fund-level `covered` + score-level `not_configured` → `needs_future_gate`，不是 candidate

**结论：双重语义攻击面已被双维度拆分和显式裁决规则关闭。**

---

## 7. 项目指令检查

按 `AGENTS.md` 和 `docs/design.md` 的约束逐项检查：

| 约束 | 状态 |
|---|---|
| 四层边界 UI → Service → Host → Agent | ✅ 未涉及 Host/Agent |
| 年报访问边界（FundDocumentRepository） | ✅ 未访问 PDF/cache |
| Dayu Host/Agent 依赖 | ✅ 未引入 |
| 显式参数 / 禁止 extra_payload | ✅ 不适用（docs-only） |
| 逻辑/数据同源（AGENTS.md line 71） | ✅ 双维度拆分明确了每个 code 的 source field path |
| score/quality/FQ0-FQ6 语义不变 | ✅ 未修改任何代码或产物 |
| golden answer / promoted fixture 不变 | ✅ |
| QDII probing 不重启 | ✅ |
| FOF QDII-FOF 不计入 pure FOF | ✅ |
| Gate 分类（heavy） | ✅ 正确分类并遵循 heavy 流程（多份独立 review + controller judgment） |
| `fixture_state` 不引入 `promotion-prep-ready` | ✅ schema 不变，enum 不变 |
| 不把 deferred row 改为 ready | ✅ |
| 不把 quality warn 当 ready 证明 | ✅ warn 只进入 residual owner / accepted risk |
| 基金类型判断优先 | ✅ index/enhanced_index 区分体现在 004194 的 conditional P1 处理中 |

---

## 8. 过度耦合检查

| 检查项 | 状态 |
|---|---|
| Decision artifact 是否依赖 fixture manifest 的特定 schema version？ | 只读依赖 `v1`，不修改 schema ✅ |
| Candidate decision 是否被 preflight 消费？ | 否。当前 preflight 不读取 decision artifact ✅ |
| 004194 降级是否影响其他 entry 的 decision？ | 否。每个 entry 独立评估 ✅ |
| `unavailable_records` 跨基金语义是否耦合了 004393 和 004194 的评估？ | 已在 decision 中显式拆分。004194 的 145 unavailable 全部跨基金，004194 intra-fund=0 ✅ |
| 本 gate 的产物是否被 future gate 强依赖（不可逆）？ | 否。产物为 docs-only Markdown，future gate 可重新评估 ✅ |

---

## 9. 综合裁决

### 9.1 Accepted Decision 满足目标

**满足。** 10 entries 的 decision、evidence、missing evidence、owner、next gate 完整且正确。Candidate 语义严格分层，无 promotion 授权。控制 doc 的 Next Entry Point 要求已满足。

### 9.2 状态正确性

**全部正确。** 004393/004194/006597/017641/QDII/FOF/110020 的状态与 source score/quality/preflight/manifest 一致。004194 的降级（`promotion_prep_ready_candidate` → `conditional_candidate_pending_p0_coverage_decision`）是 review 链的核心纠正，消除了 P0=0 的隐藏风险。

### 9.3 No Promotion / No Modification

**确认。** 无 promotion、无 golden fixture 修改、无 manifest/schema/runtime/score/quality/snapshot 修改。所有产物为 untracked Markdown。

### 9.4 验证策略

**足够。** 8 份 review + aggregate deepreview，覆盖 plan 和 implementation 两个阶段，所有 blocking/medium finding 均在 acceptance 前关闭。

### 9.5 Residuals / Next Gates

**清楚。** 7 个 immediate next gate 和 5 个 long-running residual 均有明确 owner 和前置条件。

### 9.6 Adversarial / 项目指令 / 过度耦合

**全部通过。** 无攻击面、无指令违规、无过度耦合。

---

## 10. 无新 Finding

本 aggregate deepreview 未发现新的 blocking、medium 或 low finding。所有在先 review 已捕获的问题均已关闭。

## 11. 建议的 Controller 裁决项

Controller 在 acceptance 前应显式裁决：

1. **004393 `conditional_candidate_pending_partial_coverage_decision`**：接受 P0 81.8% / P1 0% / overall 6% 的 partial coverage 状态，并确认 next gate（partial coverage decision gate）的 scope
2. **004194 `conditional_candidate_pending_p0_coverage_decision`**：确认 P0=0 的降级处置正确，确认 future gate 需评估 P0 strict correctness coverage 是否作为 promotion 前提
3. **006597 `needs_future_gate`**：确认 score rerun with golden answer JSON 为下一步
4. **Deferred rows**（017641/QDII/FOF/110020）：确认 deferred 状态不变
5. **Control doc 同步**：是否需要将本 gate 的 decision artifact 加入 `docs/implementation-control.md` 的 Current Accepted Artifacts

---

## Review Completion

本 aggregate deepreview 不修改任何文件（本 artifact 除外）。由 controller 做最终裁决。

产出路径：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-aggregate-deepreview-ds-20260529.md`
