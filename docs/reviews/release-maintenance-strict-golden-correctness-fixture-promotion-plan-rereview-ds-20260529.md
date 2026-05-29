# Strict Golden Correctness / Fixture Promotion Plan — Re-Review (AgentDS)

日期：2026-05-29
角色：AgentDS plan re-reviewer
审查对象：修订后的 `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md`
参考：原始 DS review（B1-B3, W1-W4）、MiMo review（Finding 1-5）

## Re-Review Scope

本次 re-review 只验证修订 plan 是否关闭了原始 DS review 的 3 个 blocking findings (B1-B3) 和 4 个 warnings (W1-W4)，以及用户指定的 5 个关注点：

1. `fixture_state` enum/schema 不变
2. strict correctness 真源同源且字段路径明确
3. 004393 partial coverage 不直接升级
4. 004194 candidate 不等同 promotion
5. docs-only validation 合理

不新增发现、不重复 MiMo findings、不评估 implementation。

---

## B1 关闭验证：`fixture_state` 枚举边界

**原始 finding**：plan 提出 `fixture_state_after_gate` 使用 `promotion-prep-ready`，不在既有 6 值枚举中。

**修订 plan 的处置**：

| 位置 | 内容 | 效果 |
|---|---|---|
| Goal (line 28) | "不得把 candidate 状态写入 fixture manifest 的 `fixture_state`" | 硬约束 |
| Decision Schema `fixture_state_after_gate` (line 112) | 列出完整 6 值枚举，明确 "本 gate 不使用 `ready_for_future_promotion` 或 `promoted`" | 枚举闭合 |
| JSON manifest update constraints (line 130-131) | "Manifest schema remains unchanged in this gate；do not add `promotion-prep-ready` to `fixture_state`" | schema 不变 |
| Candidate rules (line 164) | "fixture state remains an existing fixture manifest enum value; candidacy is not encoded in `fixture_state`" | 分层明确 |
| Stop conditions (line 257) | `fixture_state="promotion-prep-ready"` 列入 stop | 阻断违规 |
| Candidate Decision Table 004393 (line 138) | "Fixture state remains `absent`" | 实例一致 |
| Candidate Decision Table 004194 (line 139) | "fixture state remains `absent`" | 实例一致 |

**裁决**：B1 **已关闭**。修订 plan 将 `decision`（Markdown artifact 的决策枚举）与 `fixture_state`（JSON manifest 的 schema 枚举）严格分层。`decision` 可使用 `promotion_prep_ready_candidate` / `conditional_candidate_pending_partial_coverage_decision` 等新值；`fixture_state` 只使用既有枚举且本 gate 不新增任何值。Manifest schema 不变。Stop condition 将 `fixture_state="promotion-prep-ready"` 列为硬阻断。

**关注点 1 验证通过**：`fixture_state` enum 和 schema 均不变。

---

## B2 关闭验证：strict correctness 真源同源

**原始 finding**：`strict_golden_coverage` 在 preflight（fund-level membership）和 score（field-level comparability）中以不同语义产出相似值，plan 混合使用两种语义，未定义矛盾时裁决规则。

**修订 plan 的处置**：

| 位置 | 内容 | 效果 |
|---|---|---|
| Strict Golden Correctness Minimum Contract (lines 60-63) | 拆为两个独立维度表：Fund-level membership（来源 preflight `strict_golden_coverage`）和 Score-level field comparability（来源 `score.json` → `correctness.coverage_scope` + comparable/matched/mismatched/unavailable records） | 双维度、双来源、字段路径明确 |
| Coverage code interpretation (lines 67-73) | 每个 code 标注所属 source dimension | 不再混用 |
| Additional rules (line 80) | "当 fund-level membership 与 score-level field comparability 不一致时，以 score-level field comparability 作为 strict correctness 主证据" | 裁决规则明确 |
| Additional rules (line 81) | "`strict_golden_coverage=covered` 与 `strict_golden_not_configured` 可同时出现于不同来源维度；必须在 decision artifact 中分别列出" | 006597 双重信号有处理规则 |
| Decision Schema (lines 114-115) | `fund_level_membership` 和 `score_level_field_comparability` 作为独立字段 | decision artifact 强制分别记录 |

**裁决**：B2 **已关闭**。修订 plan 建立了双维度真源模型，每个维度有明确 source field path，冲突裁决规则明确（score-level 优先），decision artifact schema 强制分别记录两个维度。

**关注点 2 验证通过**：strict correctness 真源同源（以 score-level field comparability 为主证据），字段路径明确（`score.json.correctness.coverage_scope` + `comparable_records` / `matched_records` / `mismatched_records` / `unavailable_records` / `record_results[]`）。

---

## B3 关闭验证：004393 partial coverage 升级门槛

**原始 finding**：004393 的 9/150 (6%) partial coverage 被推荐为 `promotion-prep-ready`，缺少最低可比字段数或比例阈值，且未区分 P0/P1/P2 字段级 breakdown。

**修订 plan 的处置**：

| 位置 | 内容 | 效果 |
|---|---|---|
| Coverage code interpretation (line 73) | "`partially_covered` 不得自动升级为 promotion-prep candidate；必须提供字段级 breakdown，特别是 P0/P1/P2 可比覆盖，且由 controller 接受 partial coverage decision。004393 当前默认不 ready。" | 默认阻断 |
| Candidate Decision Table 004393 (line 138) | decision = `conditional_candidate_pending_partial_coverage_decision`；"not promotion-prep-ready unless this gate also produces field-level breakdown and controller explicitly accepts" | 降级 |
| Missing evidence (line 138) | "P0 comparable/total, P1 comparable/total, P2 comparable/total, and list of unavailable P0 fields" | 证据要求具体 |
| Candidate Rules (line 161) | "`partially_covered` only after field-level breakdown and explicit controller partial-coverage acceptance" | 升级条件 |
| Default outcome (line 149) | "004393 is conditional... because 9/150 partial coverage is too low to accept without field-level breakdown and controller judgment" | 9/150 明确认定为不足 |
| Stop conditions (line 251) | 004393 被标为 `promotion_prep_ready_candidate` 而无 breakdown + controller acceptance → stop | 阻断违规 |
| Validation Matrix (line 229) | "004393 partial coverage breakdown includes P0/P1/P2 comparable and unavailable field list before any candidate acceptance" | 验证要求 |
| Review Requirements (line 239) | controller 必须显式裁决 004393 conditional decision | 裁决门禁 |

**裁决**：B3 **已关闭**。修订 plan 将 004393 从 `promotion_prep_ready_candidate` 降级为 `conditional_candidate_pending_partial_coverage_decision`，要求 P0/P1/P2 字段级 breakdown，9/150 明确认定为不足以自动升级，stop condition 阻断无 breakdown 的升级。

**关注点 3 验证通过**：004393 partial coverage 不直接升级，必须先产出 field-level breakdown 并经 controller 显式接受。

---

## W1-W4 关闭验证

### W1: 006597 双重信号

**原始 finding**：`covered` + `not_configured` 同时出现，plan 未解释 rerun 即可解决。

**修订 plan 的处置**：
- Decision table (line 140)："Must rerun extraction score with `reports/golden-answers/golden-answer.json` as golden answer input"
- 006597 special rule (line 182)："The next evidence step is a score rerun"
- Default outcome (line 151)："strong future candidate input because bond blocker is closed, but current source score correctness is `not_configured`"

**裁决**：W1 **已处理**。明确 006597 是配置问题（可 rerun 解决），不是数据不可得问题（不同于 110020 的 `fund_not_covered`）。

### W2: quality warn owner

**原始 finding**：owner 是 future placeholder，不是 active owner。

**修订 plan 的处置**：
- Candidate rule (line 166)：明确允许 "active owner or explicitly recorded future placeholder owner / next gate"

**裁决**：W2 **已处理**。修订 plan 显式接受 future placeholder owner 在本 gate 范围内可接受。鉴于本 gate 不执行 promotion（`promotion_allowed=false`），且 owner 赋值在下一 gate 完成，此处理合理。

### W3: 110020 归类理由

**原始 finding**：110020 deferred vs 006597 needs_future_gate 的差异未解释。

**修订 plan 的处置**：
- Decision table 110020 (line 142)："Deferred because `fund_not_covered` is a hard blocker, unlike 006597's rerunnable `not_configured`"

**裁决**：W3 **已处理**。差异解释明确：`fund_not_covered`（hard blocker，基金不在 golden answer 中）vs `not_configured`（可 rerun 解决）。

### W4: 004194 tracking_error 的 design.md 约束

**原始 finding**：未提及 tracking_error 需要 P15 reviewed direct evidence 前置 gate。

**修订 plan 的处置**：
- Decision table 004194 (line 139)："`tracking_error` residual additionally requires P15 reviewed direct observed disclosure evidence before adding tracking-error production golden rows"

**裁决**：W4 **已处理**。P15 前置约束已显式标注。

---

## 用户指定关注点验证

### 关注点 4: 004194 candidate 不等同 promotion

**验证**：

| 约束 | 位置 | 状态 |
|---|---|---|
| `promotion_allowed=false` | Decision table (line 139)、global rule (line 113) | 不变 |
| fixture_state 保持 `absent` | Decision table (line 139) | 不变 |
| decision 仅写于 Markdown artifact | Goal (line 28)、JSON constraints (line 131) | 分层 |
| "not promoted" | Decision table (line 139) | 显式声明 |

**通过**。004194 的 `promotion_prep_ready_candidate` 仅在 decision artifact 的 `decision` 字段中表达，不写入 manifest `fixture_state`，`promotion_allowed` 恒为 false，不触发 promotion。

### 关注点 5: docs-only validation 合理

**验证**：

| 条件 | 状态 |
|---|---|
| 推荐产物是 decision Markdown | 确认（line 97-99） |
| 不修改 Python runtime | 确认（non-goals, line 42） |
| 不修改 preflight 代码 | 确认 |
| JSON manifest 更新是可选的 | 确认（line 100-103） |
| 若 JSON schema 不变，不跑 ruff/pytest | 确认（Validation Matrix, line 230-231） |
| Preflight rerun 条件明确 | 确认（line 232） |

**通过**。docs-only 路径的 validation 策略合理。若 JSON manifest 被更新但 schema 不变（本 gate 的约束），不跑 ruff/pytest 是合理的。若未来 preflight 消费 manifest，需 rerun——这一点已在 Validation Matrix 的 preflight rerun decision 中记录。

---

## MiMo Findings 与本 gate 修订的关系

MiMo 的 Finding 1（`promotion-prep-ready` 枚举兼容性）已被修订 plan 通过分层解决，与 B1 关闭一致。

MiMo 的 Finding 2（correctness 数据未引用 score.json 具体路径）已在修订 plan 的 Strict Golden Correctness Minimum Contract 中通过明确字段路径解决（`score.json.correctness.coverage_scope` 等）。

MiMo 的 Finding 3-5（LOW）不影响 plan acceptance，留给 implementation worker 处理。

---

## Re-Review Verdict

**B1-B3 全部关闭。W1-W4 全部处理。5 个用户关注点全部验证通过。**

修订 plan 可以进入 implementation。

### 关闭确认表

| ID | Severity | Finding | Status |
|---|---|---|---|
| B1 | block | `fixture_state` 枚举违规 | **CLOSED** — `decision`/`fixture_state` 分层，schema 不变 |
| B2 | block | strict correctness 非同源 | **CLOSED** — 双维度、双来源、字段路径明确、裁决规则 |
| B3 | block | 004393 6% coverage 无门槛升级 | **CLOSED** — 降级为 conditional，要求 P0/P1/P2 breakdown |
| W1 | warn | 006597 双重信号 | **ADDRESSED** — rerun 路径明确 |
| W2 | warn | quality warn owner 占位符 | **ADDRESSED** — 显式接受 future placeholder |
| W3 | warn | 110020 归类理由 | **ADDRESSED** — fund_not_covered vs not_configured 差异说明 |
| W4 | warn | tracking_error P15 约束 | **ADDRESSED** — P15 前置约束已标注 |

### 残留风险（非 blocking）

1. 004393 的 `conditional_candidate_pending_partial_coverage_decision` 依赖 implementation worker 产出 field-level breakdown 和 controller 裁决——如果 breakdown 显示 P0 字段大量 unavailable，controller 可能拒绝 conditional candidate，004393 退回 blocked。这是 plan 的设计意图，不是缺陷。

2. 004194 的 quality warn owner（tracking_error / turnover_rate）仍是 future placeholder——plan 已显式接受此状态，但 future gate 必须兑现 owner assignment。

3. 006597 的 score rerun 依赖 golden answer JSON 可用——当前 `reports/golden-answers/golden-answer.json` 存在，但 rerun 可能揭示新的 mismatch 或 coverage 问题。Plan 正确将其归为 `needs_future_gate`。

---

Re-review 不修改 plan、不实现、不提交。
