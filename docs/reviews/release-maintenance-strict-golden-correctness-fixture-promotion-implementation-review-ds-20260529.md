# Strict Golden Correctness / Fixture Promotion — Implementation/Evidence Review (AgentDS)

日期：2026-05-29
角色：AgentDS implementation/evidence reviewer
审查对象：
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-implementation-evidence-20260529.md`

## 前置阅读

已读取并交叉验证：

- `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`
- accepted plan (`release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md`)
- DS plan review、MiMo plan review、DS re-review、MiMo re-review
- `reports/golden-readiness-preflight/.../golden_readiness_preflight.json`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md`
- 004393 / 004194 / 006597 / 017641 / 110020 / QDII rows 的 source score.json、quality_gate.json
- 004393 / 004194 score.json 的 `correctness.record_results[]` 完整字段级 breakdown

## Overall Verdict

**PASS_WITH_FINDINGS** — 2 medium、3 low、1 info。

Decision 和 evidence artifacts 对 plan 的忠实度很高：双维度拆分 (fund-level membership / score-level field comparability) 正确执行，`decision` / `fixture_state` 分层严格，10 个 entries 的 blocker / decision / missing_evidence / owner / next_gate 均符合 plan 规则。无 promotion、无 golden fixture mutation、无 schema change、无 runtime/module 修改。

发现 2 个 medium finding 涉及 `unavailable_records` 跨基金语义透明度和 `covered` 低绝对覆盖率的 future gate 风险；3 个 low finding 基本不影响 correctness，但值得 future gate 关注。

---

## 逐项验证

### 1. `score.json.correctness` 字段路径

Decision artifact 声明的字段路径：

| 路径 | 004393 实际存在 | 004194 实际存在 | 006597 实际存在 |
|---|---|---|---|
| `correctness.coverage_scope` | `partially_covered` ✅ | `covered` ✅ | `not_configured` ✅ |
| `correctness.total_records` | 150 ✅ | 150 ✅ | 0 ✅ |
| `correctness.comparable_records` | 9 ✅ | 5 ✅ | 0 ✅ |
| `correctness.matched_records` | 9 ✅ | 5 ✅ | 0 ✅ |
| `correctness.mismatched_records` | 0 ✅ | 0 ✅ | 0 ✅ |
| `correctness.unavailable_records` | 141 ✅ | 145 ✅ | 0 ✅ |
| `correctness.record_results[]` | 存在 ✅ | 存在 ✅ | `[]` ✅ |

所有字段路径真实存在，值匹配 decision table。006597 的 `golden_answer_path=null` 确认 `not_configured`。

### 2. 004393 Partial Coverage Breakdown

源数据验证（从 `score.json` → `correctness.record_results[]` 提取，仅 `fund_code=004393`）：

| priority | total | comparable | matched | mismatched | unavailable | 不可比字段 |
|---|---:|---:|---:|---:|---:|---|
| P0 | 11 | 9 | 9 | 0 | 2 | `manager_strategy_text` (market_outlook, strategy_summary) |
| P1 | 10 | 0 | 0 | 0 | 10 | `holder_structure`, `manager_alignment`, `product_profile`, `share_change` (共 10 个 sub_field) |
| P2 | 0 | 0 | 0 | 0 | 0 | — |

与 decision table §004393 Partial Coverage Breakdown 完全一致。9/150 (6%) 可比覆盖率已确认。

**关键观察**：P0 仅 `manager_strategy_text` 不可比（2 个 sub_field），其余 5 个 P0 字段（basic_identity、classified_fund_type、benchmark、nav_benchmark_performance、fee_schedule）的 9 个 sub_field 全部 matched。P1 全部 10 个 sub_field 不可比（覆盖率为 0%）。这验证了 plan 的 conditional_candidate 处置：P0 覆盖尚可但 P1 完全缺失，9/150 不足以自动升级。

### 3. 004194 `covered` vs `unavailable_records` 语义

源数据验证：

- `record_results[]` 中 `fund_code=004194` 的条目仅 5 条，均为 `status=match`
- 5 条 matched 字段全部属于 `index_profile.*`：`benchmark_text`、`benchmark_identity_status`、`methodology_availability`、`constituents_availability`、`source_tier`
- 剩余 145 条 `record_results[]` 均为 `fund_code=004393` 的跨基金 golden answer 记录，`status=unavailable`
- 004194 自身 **零条** intra-fund unavailable 记录——所有 5 条可比记录全部 matched

`unavailable_records=145` 作为 score-level 聚合值，包含了跨基金 golden answer 记录。Decision table 直接引用该数值，未区分跨基金 (145) 与基金内不可比 (0)。这不影响 decision（004194 `covered` + 5/5 matched 是准确的），但跨基金语义缺失可能误导 future reviewer（误以为 004194 自身有 145 个字段 missing）。详见 M1。

### 4. Quality Issues

Decision table §Quality Issues 的质量状态验证：

| fund | decision table 声称 | quality_gate.json 实际 | 一致 |
|---|---|---|---|
| 004393 | `warn`; P1 `turnover_rate` + FQ0 info | `warn`; FQ2 `turnover_rate` (0% cov) + FQ2F `turnover_rate` + FQ0 info | ✅ |
| 004194 | `warn`; P1 `tracking_error` + `turnover_rate` | `warn`; FQ2 `tracking_error` (0% cov) + FQ2 `turnover_rate` + FQ2F `tracking_error, turnover_rate` | ✅ |
| 006597 | `warn`; P1 `turnover_rate` + `holder_structure` + `share_change` | score.json field_scores 确认 3 个 P1 fail | ✅ |
| QDII rows | `block` | fixture manifest `quality_gate_status=block` | ✅ |
| FOF_SLOT | `not_evaluated` | 无 source artifacts | ✅ |
| 110020 | `warn` | fixture manifest `quality_gate_status=warn` | ✅ |

004194 的 `tracking_error` FQ2 warn（P1，coverage/traceability 均为 0.0）确认 design.md P15 约束适用：production golden rows 需要 reviewed direct observed disclosure evidence。

### 5. 006597 Rerun Requirement

源数据验证：

- `score.json.correctness.golden_answer_path`: `null`
- `score.json.correctness.coverage_scope`: `not_configured`
- `score.json.correctness.total_records`: `0`
- `reports/golden-answers/golden-answer.json` 文件存在（可 rerun）

Decision 正确判定 `needs_future_gate`，missing_evidence 明确要求 "rerun extraction score with golden answer JSON"。Bond blocker 已关闭（fixture manifest `resolved_context` 确认），但 score-level correctness 仍是 `not_configured`——正确。

### 6. QDII / FOF / 110020 Deferred

所有 deferred/blocked row 与 fixture manifest 和 residual disposition manifest 一致：

| fund/slot | decision | fixture manifest `fixture_state` | residual `decision` | 一致 |
|---|---|---|---|---|
| 017641 | `deferred_from_minimum_v1` | `deferred_from_v1` | `defer_from_v1` | ✅ |
| 096001 | `deferred_from_minimum_v1` | `deferred_from_v1` | `defer_from_v1` | ✅ |
| 040046 | `deferred_from_minimum_v1` | `deferred_from_v1` | `defer_from_v1` | ✅ |
| 019172 | `deferred_from_minimum_v1` | `deferred_from_v1` | `defer_from_v1` | ✅ |
| 021539 | `deferred_from_minimum_v1` | `deferred_from_v1` | `defer_from_v1` | ✅ |
| FOF_SLOT | `deferred_from_minimum_v1` | `deferred_from_v1` | `defer_from_v1` | ✅ |
| 110020 | `deferred_from_minimum_v1` | `deferred_from_v1` | `defer_from_v1` | ✅ |

无 QDII probing 重启、无 FOF taxonomy 例外、无 QDII-FOF 计入 pure FOF。

### 7. No Manifest / Schema / Golden Fixture / Runtime Changes

Implementation evidence §Boundary Confirmation 全部可验证：

- `git status` 仅显示 untracked `docs/reviews/` Markdown 文件，无 JSON manifest 变更
- 所有 10 个 fixture manifest entries `promotion_allowed=false`（未变）
- Fixture manifest schema version 仍是 `fund-agent.fixture-promotion-state.v1`
- `reports/golden-answers/` 未修改
- `reports/extraction-snapshots/`、`reports/scoring-runs/`、`reports/quality-gate-runs/` 未修改
- `fund_agent/` Python runtime 未修改
- 无 commit 产生

**确认**：本 gate 是严格的 docs-only implementation。

### 8. Docs-Only Validation

Implementation evidence 的验证策略正确：

- `git diff --check` 适用于 Markdown-only 产物（无 whitespace 错误）
- `python -m json.tool` 不适用（无 JSON 产出/修改）
- `ruff` / `pytest` 不适用（无 Python runtime 变更）
- Preflight rerun 不适用（preflight 代码未变，不消费 decision artifact）

与 plan Validation Matrix 一致。

---

## Findings

### M1 (MEDIUM): `unavailable_records` 跨基金语义未在 decision 中记录

**问题**：

004194 的 `unavailable_records=145` 和 004393 的 `unavailable_records=141` 是 score-level 聚合值，包含了 golden answer 中**所有 fund_code** 的记录。具体组成：

| fund | total | comparable (本基金) | 跨基金 unavailable | 本基金 intra-fund unavailable |
|---|---:|---:|---:|---:|
| 004393 | 150 | 9 | ~129 | ~12 (2 P0 + 10 P1) |
| 004194 | 150 | 5 | 145 (全为 fund_code=004393) | 0 |

004194 的 `record_results[]` 中 **全部 145 条** unavailable 记录的 `fund_code` 都是 `004393`（跨基金），而非 004194 自身字段不可比。004194 自身 5 条可比记录全部 matched，零条 intra-fund unavailable。

**影响**：decision table 直接引用 `unavailable_records=145`，future reviewer 可能误读为 "004194 有 145 个字段缺失"。这不改变 decision 结论（004194 `covered` / 5/5 matched 是准确的），但缺少跨基金语义说明降低了数字的可解释性。

**建议**：在 decision artifact 的 004194 row 或 evidence 中增加一行注释，说明 `unavailable_records` 的跨基金组成。

### M2 (MEDIUM): 004194 `covered` 仅覆盖 5 个 index_profile 子字段，future gate 不应理解为广义 correctness 验证

**问题**：

004194 score-level `coverage_scope=covered`（5/5 matched，3.3% 可比率）和 004393 `coverage_scope=partially_covered`（9/9 matched，6% 可比率）在绝对可比覆盖率上都极低。两者差异来自代码分类逻辑（全部可比记录 matched → `covered`；部分可比 → `partially_covered`），不代表 coverage breadth 有实质性差异。

004194 的 5 条 matched 记录全部是 `index_profile.benchmark_text`、`index_profile.benchmark_identity_status`、`index_profile.methodology_availability`、`index_profile.constituents_availability`、`index_profile.source_tier`——仅覆盖 enhanced_index 特有的 benchmark 跟踪字段。标准字段（basic_identity、fee_schedule、classified_fund_type 等）在 004194 的 score run 中因 snapshot 投影差异而全部不可比（状态为跨基金 `unavailable`，而非本基金可比场景）。

**影响**：decision 正确地将 004194 标为 `promotion_prep_ready_candidate`（满足 plan 的 candidate rules），但 "covered" 标签可能让 future gate 误以为 004194 的 strict golden correctness 已全面验证。实际上仅 5 个 index_profile 子字段可比——基金基本身份、费率、分类等标准字段的正确性尚未经过 golden answer 比对。

**建议**：
- (a) 在 decision artifact 中标注 004194 可比字段仅限于 `index_profile.*`，标准字段 (basic_identity, classified_fund_type, benchmark 非 index, fee_schedule 等) 当前不可比；
- (b) future strict golden fixture promotion review gate 在评估 004194 时应将其视为 "index_profile-only verified"，而非全局 correctness verified。

### L1 (LOW): 004393 P0 `manager_strategy_text` 不可比——与 017641 的 P0 block 可比较但不相同

004393 P0 中 `manager_strategy_text.market_outlook` 和 `manager_strategy_text.strategy_summary` 均不可比（snapshot 未暴露这两个子字段的 golden-comparable 数据）。017641 同样因 `manager_strategy_text` P0 block 被 deferred。差异在于：

- 004393：`manager_strategy_text` 的 market_outlook/strategy_summary 不可比，但该字段的其他子字段可能已可比（9 个 P0 可比记录包含 `manager_strategy_text` 的部分子字段）；quality 是 `warn` 而非 `block`
- 017641：`manager_strategy_text` 整体 P0 block（quality `block`），fund-level `fund_not_covered`

Decision 对 004393 的 conditional candidate 处置正确，但 future partial coverage decision gate 应明确：manager_strategy_text 的 2 个 P0 子字段不可比是否构成事实上的 P0 覆盖缺口。

### L2 (LOW): `promotion_prep_ready_candidate` decision 与 preflight 的 `fixture_promotion_absent` blocker 并存——语义边界已正确处理但值得记录

Preflight 的 GLOBAL blocker `fixture_promotion_absent` 对所有 entry 依然生效（004194/004393/006597 均在 preflight 中显示 `fixture_promotion_absent` blocker）。004194 的 `promotion_prep_ready_candidate` decision 是 docs-only 状态，不消除 preflight blocker。这两者语义边界：

- `promotion_prep_ready_candidate` = "如果 future gate 接受当前 evidence，该基金具备 promotion-prep 资格"
- `fixture_promotion_absent` = "尚未有 accepted fixture promotion 发生"

两者不矛盾——decision artifact 正确地在 `decision` 字段表达 candidate 语义而不写入 `fixture_state`。Implementation evidence 可以不额外处理，但 future gate 需要知道 preflight blocker 解除需要实际的 fixture promotion（非本 gate 范围）。

### L3 (LOW): implementation evidence 的 `ruff` / `pytest` 跳过的理由覆盖了当前 scope，但未提及 future gate 回归条件

Implementation evidence 声明 "ruff / pytest were not run because this gate produced Markdown-only evidence"。当前 scope 内正确。但如果 controller 后续要求更新 fixture manifest JSON（例如将 candidate decision 写回 manifest），则 future gate 的 implementation worker 需要知道回归条件：JSON 文件修改不触发 Python 行为变化，但 preflight 代码中的 fixture promotion blocker 派生逻辑如果 future 消费了 manifest，就需要 pytest 回归。

Plan 的 Preflight Rerun Decision 已覆盖此点（"future runtime/preflight consumption gate must rerun preflight"），implementation evidence 可引用该条款。

### I1 (INFO): 全部 10 entries plan compliance 确认

| plan rule | evidence |
|---|---|
| `decision` 与 `fixture_state` 分层 | decision artifact 只在 `decision` 字段使用新 enum 值；`fixture_state_after_gate` 全部使用既有 enum ✅ |
| `promotion_allowed=false` 全局不变 | 所有 10 entries ✅ |
| 双维度（fund-level / score-level）分别记录 | decision table 每行均有独立列 ✅ |
| score-level 为主证据，矛盾时 score 优先 | 004393 preflight `covered` vs score `partially_covered` → decision 使用 score 判定 ✅ |
| 004393 不自动升级 | `conditional_candidate_pending_partial_coverage_decision` ✅ |
| 004194 candidate 不等同 promotion | decision-only，`fixture_state=absent`，`promotion_allowed=false` ✅ |
| 006597 不标 ready | `needs_future_gate` ✅ |
| QDII 不重启 probing | 所有 QDII `deferred_from_minimum_v1` ✅ |
| FOF_SLOT 无 source artifacts | paths null ✅ |
| 110020 hard blocker `fund_not_covered` | `deferred_from_minimum_v1` ✅ |
| 无 QDII-FOF 计入 pure FOF | FOF_SLOT blocking_reason 明确排除 ✅ |
| Stop conditions 未触发 | 无 promotion、无 schema change、无 mismatch ❌ → 无 stop ✅ |

---

## Boundary Check

| 检查项 | 结论 |
|---|---|
| `score.json.correctness` 字段路径实际存在 | 通过。7 个字段路径全部在 3 个 score 文件中验证 |
| 004393 P0/P1/P2 breakdown 准确 | 通过。P0 9/11、P1 0/10、P2 0/0 |
| 004194 5/5 matched 字段确认 | 通过。全部为 index_profile.* sub_fields |
| 006597 `not_configured` 原因确认 | 通过。`golden_answer_path=null` |
| decision `↔` fixture_state 分层 | 通过。无 `promotion-prep-ready` 写入 fixture_state |
| fixture manifest schema 不变 | 通过。`schema_version` 仍为 `v1` |
| 全部 `promotion_allowed=false` | 通过。10 entries + GLOBAL blockers |
| golden answer / fixture 未修改 | 通过。git status 无相关修改 |
| score / quality / snapshot 未修改 | 通过 |
| preflight 未重跑 | 通过。不需重跑（docs-only） |
| QDII probing 未重启 | 通过 |
| FOF taxonomy 例外未引入 | 通过 |
| Host / Agent / dayu 未引入 | 通过 |
| ruff / pytest 跳过理由有效 | 通过。Markdown-only，无 Python runtime 变更 |
| 110020 vs 006597 差异处理 | 通过。`fund_not_covered` (hard blocker) vs `not_configured` (可 rerun) |
| 004194 tracking_error P15 约束 | 通过。decision table missing_evidence 已标注 |

---

## Findings Summary

| ID | Severity | Finding | Recommendation |
|---|---|---|---|
| M1 | MEDIUM | `unavailable_records` 数值包含跨基金 golden answer 记录，decision 未区分跨基金 vs 基金内不可比 | 在 decision 或 evidence 中标注跨基金组成 |
| M2 | MEDIUM | 004194 `covered` 仅覆盖 5 个 index_profile 子字段 (3.3%)，future gate 可能误读为广义 correctness 验证 | 标注可比字段仅限于 index_profile.*，标准字段当前不可比 |
| L1 | LOW | 004393 P0 `manager_strategy_text` 2 子字段不可比，与 017641 P0 block 可比较 | future gate 裁决 P0 覆盖缺口影响 |
| L2 | LOW | `promotion_prep_ready_candidate` 与 preflight `fixture_promotion_absent` 并存，边界正确但值得记录 | future gate 了解解除需要实际 fixture promotion |
| L3 | LOW | docs-only 跳过的回归条件在 plan 中有记录但 evidence 未引用 | evidence 可引用 plan 的 preflight rerun decision 条款 |
| I1 | INFO | 全部 10 entries plan compliance 确认 | 无需行动 |

---

## Review Completion

Review 不修改 decision/evidence artifacts、不实现、不提交。M1/M2 由 controller 裁决是否需要补证；L1-L3 不阻断 acceptance。

Decision 和 evidence artifacts 在结构完整性、plan compliance、数据准确性、boundary 约束方面均通过。可以进入 controller judgment。
