# Golden Readiness Residual Disposition Plan — Re-Review (MiMo)

日期：2026-05-29

Reviewer：MiMo；planreview stance。Re-review worker，not controller。

Review target：`docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-20260529.md`

Prior review artifacts：
- `docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-review-mimo-20260529.md`
- `docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-review-ds-20260529.md`

## Scope

验证 prior MiMo F6（required-fix）和 F1/F2/F3/F7（warnings）是否已解决；同时检查 DS required fixes（017641 replacement_disposition、blocks_minimum_v1 入初始 schema）是否可见且正确。

## Evidence Read

- `AGENTS.md`
- `docs/design.md` (v2.2)
- `docs/implementation-control.md` (v2.1)
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`
- `docs/reviews/release-maintenance-golden-readiness-preflight-controller-judgment-20260529.md`
- `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md`
- `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md`
- Review target plan artifact (revised)
- Prior MiMo review artifact
- Prior DS review artifact

---

## Prior Finding Resolution Status

### MiMo F6 [block → resolved] — Schema `decision` enum 与 matrix 联合值不一致

**原问题**：QDII 四候选行 decision 写为 `defer_from_v1 / blocked_until_policy`，schema `decision` 是单一 enum string，无法存储联合值。

**当前 plan 状态**：

Schema constraints 第 197 行明确：

> `decision` must be a single primary enum value. Do not encode slash-combined values such as `defer_from_v1 / blocked_until_policy` or `defer_from_v1 / needs_candidate_gate`.

`policy_status` 字段记录 hard-stop 状态如 `blocked_until_qdii_policy_or_asset_class_fitness_gate`，`next_required_action` 记录 future gate 语义如 `needs_candidate_gate`。Disposition Output Matrix 中所有行的 `decision` 列均为单一值：`defer_from_v1`、`needs_fixture_promotion_gate` 或 `blocked_until_policy`。QDII 四候选（096001/040046/019172/021539）行的 `decision` 为 `defer_from_v1`，`policy_status` 为 `blocked_until_qdii_policy_or_asset_class_fitness_gate`。

**判定**：**resolved。** Schema 约束和 matrix 一致，联合语义通过 `decision` + `policy_status` + `next_required_action` 三个字段分离表达。

---

### MiMo F1 [warn → resolved] — `blocks_v1` 语义在 deferred 行上混淆

**原问题**：`blocks_v1` 在 schema 中是 boolean，但 plan 对 deferred 行使用条件式 `true until ...`，未定义 `blocks_v1=false` 的生效时机。

**当前 plan 状态**：

Schema constraints 第 205-206 行明确两个独立字段：

> `blocks_v1` remains `true` for full-v1 blockers unless a later controller judgment explicitly changes the full v1 scope or blocker contract.
> `blocks_minimum_v1` is part of the initial schema. Controller-proposed values: GLOBAL fixture `true`; 004393/004194/006597 `true`; QDII global `false` once deferred; 017641 `false`; ... FOF_SLOT `false`; 110020 `false`.

`blocks_v1` 是静态 boolean，只在后续 controller judgment 显式改变时才变更。`blocks_minimum_v1` 独立表达 minimum v1 的阻塞状态。两者不再混淆。

**判定**：**resolved。** 双字段设计消除了条件语义歧义。Controller judgment 显式改变 full v1 scope 时才修改 `blocks_v1`，不需要条件逻辑。

---

### MiMo F2 [warn → resolved] — Schema 示例只有一行 entry，未覆盖所有 disposition 类型

**原问题**：Schema 示例只含 `004393` 一个 `needs_fixture_promotion_gate` 条目，未展示 `defer_from_v1`、`blocked_until_policy`、`GLOBAL`、`FOF_SLOT` 等。

**当前 plan 状态**：

Schema 示例现含 GLOBAL 行（`needs_fixture_promotion_gate`）和 017641 行（`defer_from_v1`），展示了两种 primary decision 类型。Schema constraints 第 201-202 行定义了 `fund_or_slot` 接受 fund code string 或 `GLOBAL` / `FOF_SLOT` 特殊标识。`report_year` 接受 integer 或 `null`。`replacement_disposition` enum 为 `replace / exclude / null`。Disposition Output Matrix 展示了全部 12 行的完整编码方式。

**判定**：**resolved。** 示例 + constraints + matrix 三者组合提供了充分的编码指导。Implementer 可从 matrix 中任意行推导 JSON 编码。

---

### MiMo F3 [warn → resolved] — 006597 bond blocker invariant 回归检测依赖未明确

**原问题**：Plan 声明回归会 reclassify 006597，但未定义回归检测机制——由 fixture promotion gate 手动检查还是 preflight 自动检测。

**当前 plan 状态**：

Slice C 第 308 行明确：

> Before 006597 enters fixture candidacy, validate latest preflight/snapshot/score/quality artifacts and preserve the `bond_risk_evidence_missing` closed invariant.

How To Keep 006597 Bond Blocker Closed 第 248 行：

> Fixture promotion gate must validate latest preflight, snapshot, score, and quality artifacts for 006597 before treating it as a fixture candidate. The check must confirm latest artifacts still satisfy the invariant above; if the latest run is unavailable or stale, the gate must either rerun preflight or record a controller-accepted reason for using a later reviewed equivalent artifact set.

第 250 行：

> Any 006597 regression in score/quality/snapshot reclassifies 006597 as `fix_now` or `needs_evidence_gate`, not fixture candidate.

**判定**：**resolved。** Fixture promotion gate 有明确的 gate-level 约束：必须先验证 latest artifacts，不可使用 stale artifacts，回归时 reclassify 为 `fix_now` / `needs_evidence_gate`。

---

### MiMo F7 [warn → resolved] — 006597 `strict_golden_not_configured` blocker 处理路径未完全闭合

**原问题**：006597 行列出 `strict_golden_not_configured` blocker，但未明确此 blocker 如何影响 fixture promotion gate 路径。

**当前 plan 状态**：

§7 第 99 行增加 clarification 段落：

> `strict_golden_coverage=covered` 表示该基金代码存在于 golden answer manifest 的 fund-level coverage 中；`strict_golden_not_configured` 表示 score correctness 比对尚未配置或缺少同年 reviewed golden rows。两者是独立维度，006597 可同时为 fund-level covered 且仍被 strict golden correctness blocker 阻塞。

Disposition Output Matrix 006597 行的 `decision_reason` 写为 `immediate fixture candidate only if bond blocker remains closed; strict golden score correctness remains unresolved`，`next_required_action` 为 `latest preflight/snapshot/score/quality validation before fixture candidacy`。

**判定**：**resolved。** Coverage vs correctness 维度差异已显式说明，006597 fixture candidacy 条件明确要求 bond blocker 闭合 + latest artifact 验证。

---

### DS F1 [required-fix → resolved] — 017641 `replace` 未传播到 disposition matrix 与 JSON schema

**原问题**：017641 只记 `defer_from_v1`，未记录 prior controller judgment 的 `replace` 语义。

**当前 plan 状态**：

§3 Decision 3 第 71 行：`primary defer_from_v1，并通过 replacement_disposition=replace 保留 prior replace/not_promoted disposition`。

Schema constraints 第 203 行：`replacement_disposition enum：replace / exclude / null。replacement_disposition=replace preserves prior replacement disposition; that entry cannot become a v1 candidate again without a new controller judgment.`

Disposition Output Matrix 017641 行：`replacement_disposition` 列为 `replace`。

JSON schema 示例 017641 entry：`"replacement_disposition": "replace"`。

**判定**：**resolved。** `replace` 语义已通过 `replacement_disposition` 字段在 §3、matrix、schema 示例和 schema constraints 四处一致传播。

---

### DS F2 [required-fix → resolved] — `blocks_minimum_v1` 未纳入初始 schema

**原问题**：Plan 将 `blocks_minimum_v1` 推迟到 v1.1 schema，但本 gate 的 controller 接受 minimum v1 scope 后就需要该字段。

**当前 plan 状态**：

Schema constraints 第 206 行：`blocks_minimum_v1` is part of the initial schema. Controller-proposed values 列出所有 12 行的值。

JSON schema 示例含 `"blocks_minimum_v1": true`（GLOBAL）和 `"blocks_minimum_v1": false`（017641）。

Disposition Output Matrix 增加了 `blocks_minimum_v1` 列，所有行均有明确值：GLOBAL fixture `true`；004393/004194/006597 `true`；QDII global `false`；017641 `false`；096001/040046/019172/021539 `false`；FOF_SLOT `false`；110020 `false`。

**判定**：**resolved。** `blocks_minimum_v1` 已纳入初始 schema，controller 接受 minimum v1 scope 后可直接在 Slice B 中设置值，无需 schema revision。

---

### DS F3 [advisory → resolved] — 006597 coverage 维度说明缺失

**原问题**：`strict_golden_coverage=covered` 与 `strict_golden_not_configured` 容易混淆。

**当前 plan 状态**：§7 增加 clarification 段落说明两者是独立维度（同 MiMo F7 resolution）。

**判定**：**resolved。**

---

### DS F4 [advisory → resolved] — Fixture promotion state manifest 路径未预留

**原问题**：Plan 未为 fixture promotion state manifest 预留建议路径。

**当前 plan 状态**：Slice C 第 298-300 行建议路径约定 `docs/reviews/fixture-promotion-state-manifest-{YYYYMMDD}.json`，并注明最终路径由 fixture promotion gate plan 决定。

**判定**：**resolved。**

---

## Fresh Adversarial Pass

对 revised plan 做新一轮 adversarial 检查，聚焦 disposition schema、minimum-v1 语义、006597 closed invariant、promotion/FQ weakening。

### Check 1 — Disposition schema 是否足以表达所有裁决

Schema 字段覆盖：

| 需求 | 字段 | 状态 |
|---|---|---|
| primary decision | `decision` (single enum) | ✓ |
| decision 原因 | `decision_reason` | ✓ |
| policy hard-stop | `policy_status` | ✓ |
| future gate | `next_required_action` | ✓ |
| prior replacement | `replacement_disposition` | ✓ |
| full-v1 blocker | `blocks_v1` | ✓ |
| minimum-v1 blocker | `blocks_minimum_v1` | ✓ |
| promotion status | `promotion_allowed` | ✓ |
| evidence | `evidence_artifacts` | ✓ |
| owner | `owner` | ✓ |
| next gate | `next_gate` | ✓ |
| fund/slot id | `fund_or_slot` | ✓ |
| report year | `report_year` | ✓ |

全部 13 个语义维度均有对应字段。无联合值、无条件逻辑、无 v1.1 推迟。

### Check 2 — Minimum-v1 语义是否可执行

`blocks_minimum_v1` 值分配：

- 需要进入 minimum v1 fixture promotion 的行（004393/004194/006597 + GLOBAL fixture）：`true`。正确——这些行是 minimum v1 的前置。
- 被 defer 的行（QDII 全部/017641/FOF_SLOT/110020 + QDII global hard stop）：`false`。正确——deferred 行不阻塞 minimum v1。
- 语义一致：`blocks_v1=true` + `blocks_minimum_v1=false` 表示"阻塞 full v1 但不阻塞 minimum v1"。Implementer 可直接从两个 boolean 推导 gate 前置条件。

### Check 3 — 006597 closed invariant 是否可验证

Invariant 定义（第 237-243 行）完整列出五项条件。Required controls（第 246-251 行）要求 fixture promotion gate 在 006597 进入 candidacy 前验证 latest artifacts。第 250 行明确回归处理。第 249 行禁止使用 stale artifacts。第 251 行禁止弱化证据标准。

Invariant 可验证性：fixture promotion gate 的 worker 可逐项检查 five conditions against latest artifacts，任何一项不满足则不进入 promotion。

### Check 4 — 是否有 promotion 或 FQ weakening

- 全表 `promotion_allowed=false`。✓
- `promotion_manifest=false`（schema 示例）。✓
- §3 017641 明确 "不削弱 FQ0-FQ6"。✓
- Slice C 说明 fixture promotion state manifest "must not set `promotion_allowed=true`, alter golden answers, alter fixture contents, change FQ0-FQ6, or modify runtime/preflight behavior"。✓
- Validation Policy 三级验证策略正确。✓

### Check 5 — Disposition matrix 中 `n/a` vs `null` 的一致性

Matrix 使用 `n/a` 表示不适用字段（如 `policy_status: n/a`、`replacement_disposition: n/a`）。JSON schema 约束中这些字段应为 `null`。这是 Markdown 展示惯例 vs JSON 编码惯例的差异，不影响 schema 解析。JSON schema 示例中正确使用 `null`。

**判定**：无 finding。Markdown matrix 的 `n/a` 是人类可读的展示方式，JSON 中为 `null`，两者语义一致。

---

## Findings

无新 findings。所有 prior findings 均已 resolved。Fresh adversarial pass 未发现新问题。

---

## Open Questions

无。

---

## Residual Risks

| 风险 | 跟踪目标 |
|---|---|
| Fixture promotion gate 尚未执行，006597 invariant 验证依赖 gate worker 正确实现 | Slice C plan / fixture promotion gate |
| `blocks_v1` 和 `blocks_minimum_v1` 的最终 boolean 值取决于 controller judgment（Slice B），当前 plan 中 QDII/FOF/110020 的 `blocks_v1=true` 是初始值，controller 可能接受 minimum v1 后保持 `true` 不变 | Slice B controller judgment |
| Schema 示例只含 2 行（GLOBAL + 017641），implementer 需从 matrix 推导其余 10 行编码 | Slice A implementation |

以上均非 blocker，属于正常后续 gate 的实施细节。

---

## Self-Check

| 检查项 | 结论 |
|---|---|
| Prior MiMo F6 (block) 是否 resolved | ✓ |
| Prior MiMo F1 (warn) 是否 resolved | ✓ |
| Prior MiMo F2 (warn) 是否 resolved | ✓ |
| Prior MiMo F3 (warn) 是否 resolved | ✓ |
| Prior MiMo F7 (warn) 是否 resolved | ✓ |
| DS F1 (required-fix) 是否 resolved | ✓ |
| DS F2 (required-fix) 是否 resolved | ✓ |
| DS F3 (advisory) 是否 resolved | ✓ |
| DS F4 (advisory) 是否 resolved | ✓ |
| Fresh adversarial pass 是否有新 blocker | 无 |
| Disposition schema 是否完整 | 是（13 语义维度全覆盖） |
| Minimum-v1 语义是否可执行 | 是 |
| 006597 closed invariant 是否可验证 | 是 |
| 是否有 promotion/FQ weakening | 否 |
| 是否误把 deferred 当 ready | 否 |
| 结论是否与 evidence 一致 | 是 |

---

## Verdict

**accepted**

Revised plan 已解决 prior MiMo review 的全部 findings（F6 block + F1/F2/F3/F7 warnings）和 prior DS review 的全部 required fixes（017641 replacement_disposition、blocks_minimum_v1 入初始 schema）。

Disposition schema 现含 13 个字段，足以表达所有裁决维度；`decision` 为单一 enum、`policy_status` 和 `next_required_action` 分离 secondary 语义；`replacement_disposition` 保留 prior controller judgment 的 replace 语义；`blocks_v1` 和 `blocks_minimum_v1` 为独立 boolean，无条件逻辑。006597 bond blocker closed invariant 有完整的 gate-level 验证约束和回归处理路径。全表 `promotion_allowed=false`，无 promotion 或 FQ weakening。

Plan 可进入 Slice A implementation。
