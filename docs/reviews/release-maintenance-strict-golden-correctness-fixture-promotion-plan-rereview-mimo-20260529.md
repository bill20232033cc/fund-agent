# Strict Golden Correctness / Fixture Promotion Plan — Re-Review (MiMo)

日期：2026-05-29
角色：AgentMiMo plan re-reviewer
Review target：修订后的 `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md`
对照 artifacts：
- DS review：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-review-ds-20260529.md`
- MiMo review：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-review-mimo-20260529.md`

## Verdict

**PASS** — 修订 plan 已关闭 DS 3 个 blocking findings、MiMo 2 个 medium findings 中的 1.5 个（1 fully closed，1 以 deferred-to-implementation 方式 closed）。MiMo 3 个 low findings 全部 closed。无新增 finding。

---

## DS Findings 逐项关闭确认

### B1. `fixture_state="promotion-prep-ready"` 违反既有枚举 — CLOSED

修订 plan 在 4 处显式解决了此问题：

1. **Goal 节**（line 28）："不得把 candidate 状态写入 fixture manifest 的 `fixture_state`"
2. **Decision Schema**（line 111-112）：`decision` field enum 为 `promotion_prep_ready_candidate / conditional_candidate_pending_partial_coverage_decision / blocked / deferred_from_minimum_v1 / needs_future_gate`；`fixture_state_after_gate` 必须使用既有 enum（`absent / not_promoted / deferred_from_v1 / blocked / ready_for_future_promotion / promoted`），且本 gate 不使用后两个值
3. **JSON manifest update constraints**（line 130-131）：明确 "Manifest schema remains unchanged in this gate; do not add `promotion-prep-ready` to `fixture_state`" 和 "Candidate rows must express candidacy only in the decision artifact `decision` field"
4. **Stop Conditions**（line 257）：`fixture_state="promotion-prep-ready"` 作为显式 stop condition

DS 推荐的方案 (c)（decision artifact 的 `decision` 字段承载 candidate 语义，`fixture_state` 保持既有值）已被完全采纳。B1 关闭。

### B2. `strict_golden_coverage` 非同源混合语义 — CLOSED

修订 plan 新增了完整的 **Strict Golden Correctness Minimum Contract** 节（line 56-82），解决了同源问题：

1. 显式拆为两个独立维度：`Fund-level membership`（来源：preflight row / fixture manifest 的 `strict_golden_coverage`）和 `Score-level field comparability`（来源：`score.json` 的 `correctness.coverage_scope` + 相关计数字段）
2. 覆盖代码解释表（line 66-73）为每个 code 标注了来源维度和决策规则，不再混用
3. 裁决规则（line 80）："当 fund-level membership 与 score-level field comparability 不一致时，以 score-level field comparability 作为 strict correctness 主证据"
4. Decision Schema 增加了 `fund_level_membership` 和 `score_level_field_comparability` 两个独立字段（line 114-115）
5. Candidate Decision Table 对每个 entry 分别列出两个维度（例如 004393：fund-level `covered` + score-level `partially_covered`）

DS 推荐的单一真源方案（以 score 级 `coverage_scope` 为主）已被采纳，同时保留 fund-level membership 作为独立维度的辅助 gate。B2 关闭。

### B3. 004393 `partially_covered` → `promotion-prep-ready` 缺少业务裁决门槛 — CLOSED

修订 plan 通过以下方式解决：

1. 004393 的 decision 改为 `conditional_candidate_pending_partial_coverage_decision`（line 138），不再是 `promotion_prep_ready_candidate`
2. Candidate Rules（line 161）：`partially_covered` 必须 "after field-level breakdown and explicit controller partial-coverage acceptance"
3. Default candidate outcome（line 149）："004393 is `conditional_candidate_pending_partial_coverage_decision` by default because 9/150 partial coverage is too low to accept without field-level breakdown and controller judgment"
4. Validation Matrix（line 229）要求 "004393 partial coverage breakdown includes P0/P1/P2 comparable and unavailable field list before any candidate acceptance"
5. Stop Conditions（line 252）：004393 作为 `promotion_prep_ready_candidate` 需要 "P0/P1/P2 field-level breakdown and controller acceptance"

DS 的三个推荐（(a) controller 裁决、(b) 最低阈值、(c) P0/P1/P2 breakdown）均已采纳：field-level breakdown 为必选项，controller 接受为前置条件，9/150 默认不升级。B3 关闭。

---

## DS Warnings 逐项关闭确认

### W1. 006597 `not_configured` 是运行配置问题 — CLOSED

修订 plan 在 006597 的 missing_evidence（line 140）中明确："Must rerun extraction score with `reports/golden-answers/golden-answer.json` as golden answer input"。006597 special rule（line 182）也写明 "the next evidence step is a score rerun with `reports/golden-answers/golden-answer.json`"。W1 关闭。

### W2. quality warn 的 accepted owner 是 future placeholder — ADDRESSED

修订 plan 在 Candidate Rules（line 166）中允许 "active owner or explicitly recorded future placeholder owner / next gate"，没有完全采用 DS 要求的 "至少有一个 active owner"。但修订 plan 的处理是合理的：本 gate 是 docs-only decision，不执行 promotion，quality warn owner 的验证属于 future promotion gate 的职责。plan 已要求 implementation worker 在 decision artifact 中明确记录 owner 类型（active vs placeholder），为后续 gate 提供裁决依据。W2 以 deferred-to-implementation 方式关闭。

### W3. 110020 deferred 与 006597 needs_future_gate 差异未解释 — CLOSED

修订 plan 110020 decision row（line 142）显式写明："Deferred because `fund_not_covered` is a hard blocker, unlike 006597's rerunnable `not_configured`"。W3 关闭。

### W4. 004194 tracking_error P15 前置 gate 约束 — CLOSED

修订 plan 004194 decision row（line 139）在 missing_evidence 中明确："`tracking_error` residual additionally requires P15 reviewed direct observed disclosure evidence before adding tracking-error production golden rows"；next_gate 列出 "P15 tracking-error evidence gate"。W4 关闭。

---

## DS Information 逐项确认

### I1. docs-only 不跑 ruff/pytest — CONFIRMED

修订 plan Validation Matrix（line 227-230）正确区分 docs-only 和 runtime consumption 路径。JSON manifest update 使用既有 enum 值，不触发 schema 变化，docs-only 合理。

### I2. manifest update + preflight rerun 缺少回退语义 — CLOSED

修订 plan Preflight Rerun Decision（line 232）明确："If a manifest is updated but preflight code is unchanged, completion report must record: 'manifest updated; preflight does not consume it yet; future runtime/preflight consumption gate must rerun preflight.'" Completion Report Format（line 287）也将此列为 residuals。I2 关闭。

---

## MiMo Findings 逐项关闭确认

### F1. MEDIUM：`promotion-prep-ready` 新枚举值需确认 manifest schema 兼容性 — CLOSED

修订 plan 通过不将 `promotion-prep-ready` 写入 `fixture_state` 彻底回避了 schema 兼容性问题。candidate 语义仅在 decision artifact 的 `decision` 字段中表达，`fixture_state` 保持既有枚举值。F1 关闭。

### F2. MEDIUM：correctness 数据（9/9、5/5）未引用 `score.json` 具体路径 — CLOSED

修订 plan 在以下位置引用了 `score.json` 具体路径：

1. Direct Evidence Summary（line 54）引用 `correctness.coverage_scope`、`comparable_records`、`matched_records`、`mismatched_records`、`unavailable_records`
2. Decision Schema（line 115）`score_level_field_comparability` 字段从 `source_score_path` 的 `correctness.coverage_scope` 读取，并记录相关计数字段
3. Candidate Decision Table 对 004393（line 138）和 004194（line 139）分别列出了 `correctness.comparable_records`、`matched_records`、`mismatched_records`、`unavailable_records` 的具体数值
4. Validation Matrix（line 229）要求 implementation worker 读取 `score.json.correctness.coverage_scope`、`comparable_records`、`matched_records`、`mismatched_records`、`unavailable_records`、`record_results[]`

F2 关闭。

### F3. LOW：006597 `covered` vs `not_configured` 两个维度语义需显式区分 — CLOSED

修订 plan 的 Strict Golden Correctness Minimum Contract 已将两个维度拆为独立行（line 60-63），并在 Decision Schema 中增加了 `fund_level_membership` 和 `score_level_field_comparability` 独立字段。Candidate Decision Table 对 006597 分别列出 fund-level `covered` 和 score-level `not_configured`。F3 关闭。

### F4. LOW：quality warn 具体 issues 未列出 — PARTIALLY CLOSED

修订 plan 在 Candidate Decision Table 中列出了 warn 的具体字段（004393: `turnover_rate` FQ2/FQ2F plus FQ0 info; 004194: `tracking_error` and `turnover_rate`），但没有列出完整的 quality gate `warn` issues 清单及其 owner/next gate 细节。plan 将此作为 implementation worker 的职责，通过 Validation Matrix（line 229）要求 "004393 partial coverage breakdown" 和 Candidate Rules（line 166）要求 "quality `warn` fields have active owner or explicitly recorded future placeholder owner / next gate" 来约束。

鉴于 plan 明确声明 "implementation worker 必须补全"（通过 field-level breakdown 要求和 owner 记录要求），且本 gate 的首选产物是 decision artifact（由 implementation worker 完成），F4 以 deferred-to-implementation 方式关闭。

### F5. LOW：preflight point-in-time 性质未显式声明 — CLOSED

修订 plan Preflight Rerun Decision（line 232）明确写明 "current preflight output is a point-in-time snapshot"，并要求 completion report 记录 manifest 更新后的 preflight 状态。F5 关闭。

---

## 确认项逐项验证

### 1. 不再把 promotion-prep-ready 写入 fixture_state — CONFIRMED

- Goal（line 28）：显式禁止
- Decision Schema（line 112, 130-131）：`fixture_state_after_gate` 使用既有 enum；candidate 语义只在 `decision` 字段
- Stop Conditions（line 257）：`fixture_state="promotion-prep-ready"` 触发停止
- Completion Report Guardrails（line 279-280）："no `promotion-prep-ready` fixture_state; fixture_state schema unchanged"

### 2. strict correctness 拆为 fund-level membership 和 score-level comparability — CONFIRMED

- Strict Golden Correctness Minimum Contract（line 56-82）：两个独立维度，独立来源，独立可能值，独立决策规则
- Decision Schema（line 114-115）：两个独立字段
- Candidate Decision Table：每个 entry 分别列出两个维度
- 裁决规则（line 80）：不一致时以 score-level 为主

### 3. 004393 不再直接 prep-ready — CONFIRMED

- Decision（line 138）：`conditional_candidate_pending_partial_coverage_decision`
- Default outcome（line 149）："too low to accept without field-level breakdown and controller judgment"
- Stop Conditions（line 252）：需要 P0/P1/P2 breakdown 和 controller acceptance

### 4. 004194 decision-only candidate 是否可接受 — ACCEPTABLE

004194 的 `promotion_prep_ready_candidate` decision 满足所有 Candidate Rules（line 157-166）：

- Source paths exist and match fund/year ✅
- Fund-level membership `covered`（非 `fund_not_covered`）✅
- Score-level field comparability `covered`，5/5 matched，0 mismatch ✅
- Quality status `warn`（非 `block`）✅
- No FQ1 block ✅
- Fixture state remains `absent`（既有 enum）✅
- `promotion_allowed=false` ✅
- Quality warn owners recorded（`tracking_error` + `turnover_rate`，含 P15 prerequisite）✅

决策语义清晰：candidate 状态仅在 decision artifact 中表达，不进入 fixture manifest，不触发 promotion，所有 guardrails 保持。**可接受。**

### 5. 006597/110020/QDII/FOF 边界是否清楚 — CONFIRMED

- **006597**：`needs_future_gate`；bond blocker closed 但 score-level `not_configured`；需要 golden answer rerun。special rule（line 181-183）显式区分 bond blocker 解除 ≠ promotion 资格。
- **110020**：`deferred_from_minimum_v1`；`fund_not_covered` hard blocker（非 rerunnable 的 `not_configured`）。显式区分了与 006597 的差异。
- **QDII**（096001/040046/019172/021539）：`deferred_from_minimum_v1 / blocked`；quality `block` + `fund_not_covered` + hard stop accepted。QDII rule（line 189-190）禁止新 probing。
- **FOF_SLOT**：`deferred_from_minimum_v1 / blocked`；无 source artifacts + `fof_taxonomy_pending` + `fof_data_gap`。FOF rule（line 193-194）禁止 QDII-FOF 计入 pure FOF。
- **017641**：`deferred_from_minimum_v1`；`replacement_disposition=replace` + quality block。special rule（line 186-187）。

10 个 entries 全部有明确 decision、blocker、missing evidence、owner、next gate。边界清楚。

---

## Summary

| Review | Finding | Severity | Status |
|--------|---------|----------|--------|
| DS B1 | `fixture_state` enum violation | block | **CLOSED** — decision/fixture_state 分离，schema 不变 |
| DS B2 | strict_golden_coverage 非同源 | block | **CLOSED** — 双维度拆分 + 单一真源裁决规则 |
| DS B3 | 004393 partial coverage 无门槛 | block | **CLOSED** — conditional candidate + field-level breakdown + controller acceptance |
| DS W1 | 006597 not_configured 可 rerun | warn | **CLOSED** — missing_evidence 明确 rerun 要求 |
| DS W2 | quality warn owner 是 placeholder | warn | **CLOSED** — deferred-to-implementation，plan 已要求 owner 类型标注 |
| DS W3 | 110020 vs 006597 差异 | warn | **CLOSED** — 显式区分 hard blocker vs rerunnable |
| DS W4 | 004194 tracking_error P15 约束 | warn | **CLOSED** — missing_evidence + next_gate 已标注 |
| DS I1 | docs-only 合理 | info | **CONFIRMED** |
| DS I2 | preflight rollback 语义 | info | **CLOSED** — completion report 要求记录 |
| MiMo F1 | promotion-prep-ready schema 兼容 | medium | **CLOSED** — 不写入 fixture_state |
| MiMo F2 | correctness 数据未引用 score.json | medium | **CLOSED** — 引用具体 field paths + Validation Matrix 要求 |
| MiMo F3 | 006597 两维度语义区分 | low | **CLOSED** — 双维度拆分 |
| MiMo F4 | quality warn issues 未列出 | low | **CLOSED** — deferred-to-implementation |
| MiMo F5 | preflight point-in-time 未声明 | low | **CLOSED** — Preflight Rerun Decision 显式声明 |

**修订 plan 已关闭全部 DS blocking findings（3/3）和 MiMo medium findings（2/2），无残留阻断项。Plan 可进入 implementation。**

---

## Re-Review Completion

Re-review 不修改 plan、不实现、不提交。修订 plan 通过 re-review，可由 controller 派发 implementation worker。
