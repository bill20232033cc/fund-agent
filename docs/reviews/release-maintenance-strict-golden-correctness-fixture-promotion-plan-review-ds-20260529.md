# Strict Golden Correctness / Fixture Promotion Plan — Adversarial Plan Review (AgentDS)

日期：2026-05-29
角色：AgentDS plan reviewer
审查对象：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md`

## 前置阅读确认

已读取并交叉验证：

- `AGENTS.md`、`docs/design.md` (v2.2)、`docs/implementation-control.md` (v2.1)
- `reports/golden-readiness-preflight/.../golden_readiness_preflight.json` / `.md`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md`
- 相关 score artifacts：004393、004194、006597 的 `score.json`
- `fund_agent/fund/golden_readiness_preflight.py` — `_derive_strict_golden_coverage()` 和 `_derive_score_correctness_blockers()`
- `fund_agent/fund/extraction_score.py` — `_correctness_coverage()` 和 `coverage_scope` 常量
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md` — `fixture_state` enum 定义

## Overall Verdict

**PASS_WITH_FINDINGS** — 3 blocking、4 warning、1 info。

Plan 的结构、scope boundary、non-goals、stop conditions 和 validation matrix 整体完整。但存在 3 个必须在 implementation 前解决的 blocking findings，以及若干需要 controller 关注的 design 问题。

---

## Blocking Findings

### B1. `fixture_state="promotion-prep-ready"` 违反既有枚举，plan 未声明 schema change

**严重程度**：block

`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md` (line 173) 定义了 `fixture_state` 的完整枚举为 6 个值：

```
absent | not_promoted | deferred_from_v1 | blocked | ready_for_future_promotion | promoted
```

当前 accepted manifest (`fixture-promotion-state-manifest-20260529.json`) 的 implementation evidence 实际验证集合为：

```python
valid_states = {"absent", "not_promoted", "deferred_from_v1", "blocked"}
```

本 plan 提出 `fixture_state_after_gate` 使用 `promotion-prep-ready`（line 103），并在 Candidate Rules（line 146-155）中将其作为 promotion-prep candidate 的目标状态。

**`promotion-prep-ready` 不在既有 6 值枚举中。** 最接近的既有值是 `ready_for_future_promotion`，但该值在 fixture promotion state manifest plan 中被标注为 "Forbidden for all current rows"。

Plan 必须明确以下之一，否则 implementation worker 无法合法写入 manifest：

- (a) 声明这是一个 **schema change**，将 `promotion-prep-ready` 加入 `fixture_state` 枚举，并说明与 `ready_for_future_promotion` 的关系（替代？共存？语义差异？）；
- (b) 使用既有枚举值 `ready_for_future_promotion`（当前 forbidden），并解释为何本 gate 可以解除该 forbidden 约束；
- (c) 不使用 `fixture_state` 承载 promotion-prep-ready 语义，改为在 decision artifact 的 `decision` 字段中用 `promotion_prep_ready_candidate`（这是 plan 已在 decision schema 中定义的 enum 值），而 `fixture_state` 保持既有值不变。

**推荐 (c)**：decision artifact 的 `decision` 字段和 JSON manifest 的 `fixture_state` 是两个不同层级的字段。plan 已正确定义了 `decision` 的 enum（line 102: `promotion_prep_ready_candidate / blocked / deferred_from_minimum_v1 / needs_future_gate`），但没有区分 `decision`（docs-only decision artifact 的字段）和 `fixture_state`（JSON manifest 的 schema 字段）的语义边界。将 `promotion-prep-ready` 写入 JSON manifest 的 `fixture_state` 会直接违反既有 schema；但写入 decision Markdown artifact 的 `decision` 字段则不涉及 schema 冲突。

**Why**：JSON manifest 是 accepted control-plane artifact，有其 schema version 和 enum contract。未经显式 schema version bump 和 enum extension 声明就引入新值，会破坏 manifest consumer（当前虽无 runtime consumer，但 controller judgment、reviewer、future gate 都是 human consumer）的一致性预期。

**How to apply**：在 plan 中增加一节 "Fixture State Enum Alignment"，明确 decision artifact 的 `decision` enum 与 JSON manifest 的 `fixture_state` enum 的关系、以及本 gate 是否修改 JSON manifest schema。

---

### B2. `strict_golden_coverage` 判定非同源，plan 的 Candidate Decision Table 混合了两种语义

**严重程度**：block

经代码验证，`strict_golden_coverage` 在两个独立路径中以不同语义产出相似值：

| 来源 | 函数 | 判定依据 | 可能值 |
|---|---|---|---|
| Preflight | `_derive_strict_golden_coverage()` | golden answer JSON 的 `funds` 数组是否包含该 fund_code | `covered`, `fund_not_covered`, `not_configured`, `not_applicable` |
| Score | `_correctness_coverage()` | snapshot comparable_values 与 golden answer 的字段级比对 | `covered`, `partially_covered`, `fund_not_covered`, `year_not_covered`, `not_configured`, `no_comparable_fields` |

**关键差异**：
- Preflight **没有** `partially_covered` 输出（`RESERVED_STRICT_GOLDEN_CODES` 中保留了该 code 但从未触发）。
- Score 的 `covered` 要求所有 golden records 都可比对且全部 matched/mismatched；preflight 的 `covered` 只要求 fund_code 存在于 golden JSON。
- 两者可以给同一 fund 不同结论。004393 就是实例：preflight 说 `covered`，score 说 `partially_covered`（9/150 comparable，141 unavailable）。

**Plan 中的混合使用**：

Candidate Decision Table 对 004393 写的是 `score correctness available with 9/9 comparable matched, 0 mismatch, coverage partially_covered`——这里引用的是 score 级 `coverage_scope`。但对 004194 写的是 `coverage covered`——也是 score 级。对 006597 写的是 `source score correctness not_configured`——又是 score 级。

但 plan 的 Strict Golden Correctness Minimum Contract（line 60-72）定义的 coverage code 语义表混合了两种来源的语义：
- `covered` 的定义（line 62）提到 "score correctness 可使用同年同基金基准做部分比较"——这暗示 score 级语义；
- `not_configured` 的定义（line 63）提到 "score correctness 没有接入 strict golden answer JSON"——这是 score 级；
- `fund_not_covered` 的定义（line 64）提到 "不在 strict golden answer v1 fund-level coverage 中"——这是 preflight 级。

**同一个 decision 中，对 `covered` 的判定同时依赖两个不同来源，但这两个来源可能对同一 fund 给出矛盾结论。** 004393 的 preflight `covered` vs score `partially_covered` 就是具体矛盾。Plan 没有规定当两者矛盾时以谁为准。

**推荐**：plan 必须明确单一真源。建议以 **score 级 `coverage_scope`** 为 strict golden correctness 的真源（因为它反映字段级 comparability，直接对应 correctness oracle 的 `fund_code + report_year + field_name + sub_field` 契约），preflight 的 fund-level label 只作为快速分类辅助。或者，将两者映射为独立维度（fund-level membership vs field-level comparability），不在 decision 中混用同一组 label。

**Why**：`AGENTS.md` line 71 要求 "找问题的 root cause 一定要逻辑/数据同源，禁止使用间接证据"。当前 plan 的 strict golden correctness 判定在两个来源间切换，违反同源原则。

**How to apply**：在 Strict Golden Correctness Minimum Contract 中增加一个 "Source of Truth" 声明，明确每个 coverage code 从哪个 artifact（preflight JSON / score JSON）的哪个字段读取，以及当两个来源矛盾时的裁决规则。

---

### B3. 004393 `partially_covered` → `promotion-prep-ready` 的升级缺少业务裁决门槛

**严重程度**：block

004393 的 score 级 `coverage_scope` 是 `partially_covered`（9/150 comparable，141 unavailable）。Plan 将其推荐为 `promotion_prep_ready_candidate`，条件包括 "strict golden correctness is `covered` or accepted `partial_coverage` with no mismatch"（line 149）。

问题不在于 9/9 matched（这没问题），而在于 **141/150 unavailable** 意味着 golden answer 中 94% 的字段在 snapshot 中没有可比数据。这表示：

- 要么 golden answer 的字段覆盖远超当前 extractor 能力；
- 要么 snapshot 的 `comparable_values` 投影不完整；
- 要么 golden answer 包含大量当前 extractor 不产出的 sub_field。

无论哪种情况，**`partially_covered` 是一个程度问题，不是二元判断**。9/150（6% coverage）和 140/150（93% coverage）都叫 `partially_covered`，但它们的可信度完全不同。Plan 的 Candidate Rules 把 "accepted partial_coverage with no mismatch" 作为一个可接受条件，但没有定义 partial coverage 的最低可比字段数或可比比例阈值。

**这是业务裁决，不是纯技术判断。** 接受 6% 可比覆盖率的基金进入 promotion-prep-ready，意味着承认 "我们只能验证该基金 golden answer 的 6% 字段，其余 94% 的 correctness 未经证实"。这对 strict golden correctness gate 的语义是重大削弱。

**推荐**：
- (a) 由 controller 显式裁决 004393 的 9/150 partial coverage 是否可接受，并记录裁决理由；
- (b) 为 `partial_coverage` → `promotion-prep-ready` 设置最低可比字段数或可比比例阈值（如 ≥50% 或 ≥20 fields），低于阈值的自动归为 `needs_future_gate`；
- (c) 为 004393 单独记录：哪些 141 个 unavailable 字段是关键字段（P0 优先级），它们的缺失是否影响 promotion-prep 资格。

**Why**：`docs/design.md` §7.3 定义 P0 字段（basic_identity, classified_fund_type, benchmark, nav_benchmark_performance, fee_schedule, manager_strategy_text）为最高优先级。如果 004393 的 9 个可比字段覆盖了全部 P0，则风险可控；如果 P0 字段也在 unavailable 中，则 promotion-prep 资格应重新评估。

**How to apply**：在 Candidate Decision Table 中为 004393 增加一行 "partial coverage breakdown"：P0 可比数 / P0 总数、P1 可比数 / P1 总数、P2 可比数 / P2 总数。Controller judgment 基于此决定是否接受。

---

## Warnings

### W1. 006597 的双重信号未在 plan 中显式处理

**严重程度**：warn

006597 在 preflight 中呈现双重信号：
- `strict_golden_coverage: "covered"`（fund 在 golden JSON 中）
- blocker `strict_golden_not_configured`（score correctness 未接入 golden answer）

Plan 正确地将 006597 归为 `needs_future_gate` 而非 `promotion-prep-ready`，理由是 `not_configured`。但 plan 没有解释：如果 006597 的 score 用 golden answer 重新跑一次（即解决 `not_configured`），它是否可能立即成为 candidate？还是还有其他隐藏阻断？

当前 006597 score 的 `not_configured` 是因为那次 score run 的 `golden_answer_path` 为 null（bond risk evidence run 不需要 correctness 比对）。这是一个 **运行配置问题**，不是数据不可得问题。Plan 将 006597 与 110020、QDII 等归为不同的 decision category 是正确的，但应该在 missing evidence 中明确写 "需要以 golden answer JSON 为输入重新运行 extraction score，产出 correctness 结果后才能评估"。

**推荐**：在 006597 的 missing_evidence 列中明确此点。

---

### W2. quality `warn` 的 accepted owner 尚未存在

**严重程度**：warn

Plan 的 immediate promotion-prep candidate rule（line 154）要求 "quality warn fields have accepted owner / next gate"。004393 的 warn 来自 `turnover_rate` FQ2/FQ2F，004194 的 warn 来自 `tracking_error` 和 `turnover_rate`。

但这些 owner 目前被标注为 "future fixture promotion gate + baseline preflight owner"——这是一个 **future gate 占位符**，不是 accepted owner。Plan 没有区分：

- **active owner**：已 accepted 的 gate 或已指名的 reviewer 负责跟踪该 residual；
- **future placeholder**：尚未存在的 gate，只在 decision 中预留名字。

如果 "accepted owner" 允许是 future placeholder，则这个条件几乎没有过滤能力——任何 warn 都可以被 "future owner" 兜底接受。这削弱了 promotion-prep 的门槛。

**推荐**：区分 active owner 和 future placeholder；promotion-prep-ready 要求至少有一个已在 implementation-control.md Open Residuals 中注册的 active owner。

---

### W3. 110020 被归类为 `deferred_from_minimum_v1` 的决策一致性

**严重程度**：warn

Plan 将 110020 归为 `deferred_from_minimum_v1`（line 131），理由是 `fund_not_covered` + `not_configured` + `index_evidence_insufficient`。这与 residual disposition manifest 的 decision（`defer_from_v1`，`blocks_minimum_v1=false`）一致。

但 110020 的 quality 是 `warn`（不是 `block`），source provenance 是 `complete` + `eligible`，这点与 017641/QDII（quality `block`）不同。Plan 没有解释为什么 110020 不能像 004393/004194 一样进入 `needs_future_gate`（而非 `deferred_from_minimum_v1`）。

**推荐**：明确 110020 的归类理由——它被 deferred 是因为 `fund_not_covered`（不在 golden answer v1 中），这是一个 hard blocker，不同于 006597 的 `not_configured`（可通过 rerun 解决）。在 decision 中写清楚。

---

### W4. candidate decision table 中 004194 的 `tracking_error` warn 需注意 design.md 约束

**严重程度**：warn

`docs/design.md` §7.4 明确：
> `tracking_error` 生产 golden rows 只有在 reviewed direct observed disclosure evidence 被接受后才能添加。

004194 是 `enhanced_index`，其 quality gate warn 中包含 `tracking_error`。如果未来要将 004194 的 tracking_error 纳入 strict golden correctness 比对，必须先完成 P15 的 reviewed direct evidence gate。Plan 未提及此约束。

**推荐**：在 004194 的 accepted_residuals 中标注 tracking_error golden evidence 的前置 gate 约束。

---

## Information

### I1. docs-only 不跑 ruff/pytest 在此 gate 范围内合理

Plan 的 Validation Matrix 正确区分了 docs-only 和 runtime consumption 路径。当前本 gate 的推荐产物是 decision Markdown artifact，不修改 Python runtime、preflight 代码、score/quality/snapshot 行为。在只产出 Markdown 和可选 JSON manifest 更新的情况下，跳过 ruff/pytest 是合理的。

但有一个边界情况：如果 implementation 更新了 `fixture-promotion-state-manifest-20260529.json`，虽然 JSON 本身不参与 Python runtime，但 **preflight 代码中的 `_derive_fixture_promotion_blockers()` 或类似函数未来可能读取该 manifest**。如果本 gate 修改了 JSON schema（例如新增 `fixture_state` 值），而 preflight 代码中有针对 fixture_state 的枚举校验，则可能产生静默不兼容。

**推荐**：如果 JSON manifest schema 不变（即不回写 `promotion-prep-ready` 到 `fixture_state`），docs-only 不跑 ruff/pytest 完全合理。如果 schema 变化，至少需要校验 JSON parse 和既有的 preflight 枚举校验代码不抛异常。

---

### I2. manifest update 和 preflight rerun 条件覆盖了主要场景但缺少回退语义

Plan 的 Validation Matrix 和 Preflight Rerun Decision（line 215-217）覆盖了正常路径：

- docs-only → 不 rerun preflight
- runtime/preflight consumption 变更 → 需要 full ruff + full pytest + preflight rerun

缺少的场景：
- **manifest JSON 被更新但 preflight 代码未变**：当前 preflight 不消费 manifest，所以不需要 rerun。但如果 future gate 让 preflight 消费了 manifest 中的 `fixture_state`，那 manifest 更新就隐含了 preflight 输出的语义变化。Plan 没有要求记录 "manifest 已更新、preflight 已知但未消费" 的显式 residual。

**推荐**：如果 implementation 更新了 JSON manifest，在 completion report 中增加一条 residual："fixture promotion state manifest updated; preflight does not consume it yet; future gate that adds runtime consumption must rerun preflight."

---

## Boundary Check (per AGENTS.md / design.md)

| 检查项 | 结论 |
|---|---|
| 四层边界 UI → Service → Host → Agent | 通过。本 gate 不涉及 Host/Agent。 |
| 年报访问边界（FundDocumentRepository） | 通过。不读取 PDF/cache/source helper。 |
| Dayu Host/Agent 依赖 | 通过。未引入。 |
| 显式参数 / 禁止 extra_payload | 通过。 |
| score/quality/FQ0-FQ6 语义不变 | 通过。plan 明确禁止削弱。 |
| golden answer / promoted fixture 不变 | 通过。plan 明确禁止修改。 |
| QDII probing 不重启 | 通过。 |
| FOF QDII-FOF 不计入 pure FOF | 通过。 |
| pyproject.toml 工程基线 | 通过。docs-only 不需要额外依赖。 |

---

## Findings Summary

| ID | Severity | Finding | Recommendation |
|---|---|---|---|
| B1 | block | `fixture_state="promotion-prep-ready"` 不在既有 6 值枚举中 | 区分 decision artifact 的 `decision` enum 与 JSON manifest 的 `fixture_state` enum；或将新值加入 schema 并声明 schema change |
| B2 | block | `strict_golden_coverage` 的 preflight 判定和 score 判定非同源，plan 混合使用两种语义 | 明确单一真源（推荐 score 级 `coverage_scope`）；定义矛盾时的裁决规则 |
| B3 | block | 004393 的 9/150 (6%) partial coverage 升级为 promotion-prep-ready 是业务裁决，plan 未设最低阈值 | 由 controller 裁决；或设最低可比字段数/比例阈值；或分 P0/P1/P2 字段级 breakdown |
| W1 | warn | 006597 的 `not_configured` 是运行配置问题而非数据不可得，plan 未写明 rerun 即可解决 | 在 missing_evidence 中明确需要 rerun score with golden answer |
| W2 | warn | quality warn 的 owner 是 future placeholder，不是 accepted active owner | 区分 active owner 和 future placeholder；promotion-prep-ready 要求 active owner |
| W3 | warn | 110020 的 deferred 归类与 006597 的 needs_future_gate 的差异未解释 | 明确 110020 因 fund_not_covered（hard blocker）而非 not_configured（可 rerun）被 deferred |
| W4 | warn | 004194 tracking_error warn 受 design.md P15 golden evidence 前置 gate 约束 | 在 accepted_residuals 中标注 |
| I1 | info | docs-only 不跑 ruff/pytest 合理 | 若 JSON schema 不变则完全合理；若变则需要至少校验 |
| I2 | info | manifest update + preflight rerun 条件缺少回退语义 | 记录 "manifest updated but preflight not consuming it" 为显式 residual |

---

## Review Completion

Review 不修改 plan、不实现、不提交。由 controller 裁决 B1-B3 后决定是否进入 implementation。
