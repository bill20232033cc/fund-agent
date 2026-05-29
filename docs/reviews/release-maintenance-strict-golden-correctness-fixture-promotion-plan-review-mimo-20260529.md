# Strict Golden Correctness / Fixture Promotion Plan — Adversarial Review (MiMo)

日期：2026-05-29
角色：AgentMiMo plan reviewer
Review target：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md`

## Verdict

**PASS_WITH_FINDINGS**

Plan 整体框架正确，guardrails 完整，stop conditions 覆盖全面。但存在 2 个中等 finding 和 3 个低 finding，需要 controller 在 judgment 中显式裁决或要求 implementation worker 补证。

---

## Review Scope

已读取文件：

- `AGENTS.md`
- `docs/design.md`（v2.2）
- `docs/implementation-control.md`（v2.1）
- `reports/golden-readiness-preflight/.../golden_readiness_preflight.json`
- `reports/golden-readiness-preflight/.../golden_readiness_preflight.md`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json`
- `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/golden_set.json`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/golden_set.json`

---

## Finding 1 — MEDIUM：`fixture_state` 枚举值 `promotion-prep-ready` 引入新状态，需确认 manifest schema 兼容性

### 问题

Plan Decision Schema 允许 candidate rows 使用 `fixture_state="promotion-prep-ready"`，但当前 `fixture-promotion-state-manifest-20260529.json` 中所有 entry 的 `fixture_state` 只使用过以下值：

- `absent`（004393/004194/006597）
- `deferred_from_v1`（017641/096001/040046/019172/021539/FOF_SLOT/110020）

`promotion-prep-ready` 是本 gate 新引入的枚举值。同时 controller judgment 明确记录：

> no entry uses `fixture_state="promoted"` or `fixture_state="ready_for_future_promotion"`

这说明 controller 在上一个 gate 审查时排除了 `ready_for_future_promotion` 这个命名。Plan 使用的 `promotion-prep-ready` 与 `ready_for_future_promotion` 语义接近但命名不同。

### 风险

1. 下游消费者（未来 preflight 或 manifest parser）可能不认识新枚举值。
2. Plan 没有声明 manifest schema version 是否需要升级。

### 建议

Controller judgment 应显式接受 `promotion-prep-ready` 作为新增枚举值，并确认 manifest schema version 不需要升级（因为 `fixture-promotion-state.v1` 是开放式枚举）。或者要求 implementation worker 在 manifest 中新增 `accepted_fixture_states` 字段声明当前已用枚举。

---

## Finding 2 — MEDIUM：Plan 声称的 correctness 数据（9/9、5/5 matched）未在 evidence paths 中引用具体来源

### 问题

Plan Candidate Decision Table 声称：

- 004393："score correctness available with 9/9 comparable matched, 0 mismatch, coverage `partially_covered`"
- 004194："score correctness available with 5/5 comparable matched, 0 mismatch, coverage `covered`"

但 plan 的 `evidence_paths` 列表和 `source_score_golden_set_path` 指向的 `golden_set.json` 文件实际内容是**基金池选择记录**（fund selection records），不是 correctness comparison 结果。`golden_set.json` 包含的是 `fund_name`、`fund_code`、`app_category`、`selection_reason` 等字段，没有 match/mismatch 数据。

实际的 correctness 数据在 `score.json` 的 `correctness` section 中。Plan 引用了 `source_score_path`（指向 `score.json`），但没有在 Direct Evidence Summary 中明确说明 correctness 数据来自 `score.json` 的哪个 section，也没有引用具体字段路径。

### 风险

1. Reviewer 和 controller 无法快速验证 9/9 和 5/5 的具体含义（哪些字段可比、哪些不可比）。
2. `partially_covered` 和 `covered` 的区分依据不明确。

### 建议

Implementation worker 的 decision artifact 必须引用 `score.json` 中 correctness section 的具体路径（如 `score.correctness.comparable_fields`、`score.correctness.matched`、`score.correctness.mismatched`），并列出可比字段清单。不能只引用 `golden_set.json`。

---

## Finding 3 — LOW：006597 `strict_golden_coverage` 在 preflight 中为 `covered`，但 plan 引用 score 为 `not_configured`，需澄清两个维度的语义边界

### 问题

- Preflight Markdown 表格：006597 strict_golden = `covered`
- Fixture manifest：006597 `strict_golden_coverage` = `covered`
- 但 fixture manifest 的 `promotion_blockers` 包含 `strict_golden_not_configured`
- Plan 声称：006597 "source score correctness `not_configured`"

Plan 在 Strict Golden Correctness Minimum Contract 中定义了两个独立维度：

| 维度 | 含义 |
|------|------|
| `covered` | fund-level 覆盖当前 fund/year |
| `not_configured` | score correctness 没有接入 strict golden answer JSON |

Plan 正确区分了这两个维度：006597 在 fund-level coverage 中是 `covered`（存在同年 golden answer），但 score correctness 的实际比对功能是 `not_configured`（score 没有执行 correctness comparison）。

### 风险

如果 implementation worker 或未来 reviewer 不理解这个区分，可能误读 `covered` 为"correctness 已验证"。

### 建议

Decision artifact 应显式列出每个 candidate 的两个维度状态（fund-level coverage status + score correctness execution status），避免混淆。当前 plan 已经做到了这一点，但可以更显式。

---

## Finding 4 — LOW：quality `warn` 对 004393/004194 的具体 warning fields 未在 plan 中列出

### 问题

Plan 说 004393 quality `warn` for "turnover_rate FQ2/FQ2F plus FQ0 info"，004194 quality `warn` for "tracking_error and turnover_rate"。但 plan 没有引用 `quality_gate.json` 的具体 issue 列表。

按 plan 的 Candidate Rules，promotion-prep-ready 要求 "quality `warn` fields have accepted owner / next gate"。Plan 说 "Accept partial coverage risk and turnover-rate warn owner"，但没有具体说明哪些 warning fields 需要 owner。

### 建议

Decision artifact 应列出 004393 和 004194 的 quality gate `warn` issues 完整清单，并为每个 issue 标注 owner 和 next gate。这不阻断 plan acceptance，但 implementation 必须补全。

---

## Finding 5 — LOW：Plan 的 preflight rerun decision 理由充分但可更显式

### 问题

Plan 说 "not required for recommended docs/evidence-only gate, because current preflight does not consume residual/fixture manifests"。这是正确的——当前 preflight 是 read-only，不读取 manifest 文件。

但 plan 没有显式说明：如果 implementation 更新了 fixture manifest（将 004393/004194 从 `absent` 改为 `promotion-prep-ready`），preflight 输出的 `fixture_promotion_absent` blocker 是否会变为 stale。

### 风险

低。Preflight 是 point-in-time snapshot，manifest 更新不影响已生成的 preflight 输出。但未来如果 preflight 被改造为消费 manifest，需要重跑。

### 建议

Decision artifact 应记录 preflight 输出是 point-in-time，manifest 更新后 preflight 不自动刷新，下次 preflight 重跑时会反映新状态。

---

## 核心问题逐项裁决建议

### 1. 004393/004194 是否可标为 promotion-prep-ready candidate？

**建议：可以，但有条件。**

证据链完整：
- Source snapshot/score/quality paths 存在（已验证目录结构）
- strict golden coverage = `covered`（fixture manifest 确认）
- quality = `warn`（非 block）
- fixture state = `absent`（可变更为 candidate）
- promotion_allowed = `false`（保持不变）

但 implementation 必须：
1. 从 `score.json` 的 correctness section 提取并列出可比字段、matched/mismatched 数（不能依赖 `golden_set.json`）
2. 列出 quality gate `warn` issues 完整清单及 owner
3. 确认无 FQ1 mismatch（需要检查 `quality_gate.json` 中是否有 FQ1/block issue）

### 2. 006597 bond blocker resolved 但 strict correctness not_configured 是否应阻断 prep-ready？

**建议：是，plan 正确处理。**

Bond blocker 关闭只表示 bond risk evidence 已修复，不代表 strict golden correctness 已配置。Plan 正确将 006597 标为 `needs_future_gate` 而非 `promotion-prep-ready`。

### 3. 017641/QDII/FOF/110020 deferred/blocked 是否准确？

**建议：准确。**

- 017641：quality `block` + `fund_not_covered` + `replacement_disposition=replace` → deferred，正确
- QDII（096001/040046/019172/021539）：quality `block` + `fund_not_covered` + `qdii_coverage_blocked` → deferred，正确
- FOF_SLOT：无 source artifacts + `fof_taxonomy_pending` + `fof_data_gap` → deferred，正确
- 110020：`fund_not_covered` + `index_evidence_insufficient` + `reviewed_candidate_not_promoted` → deferred，正确

### 4. quality warn 是否被误当 ready？

**建议：未被误当 ready。**

Plan 明确说 "quality `warn` 只能进入 residual owner / accepted risk"，且 candidate rules 要求 "quality `warn` fields have accepted owner / next gate"。Warn 是 promotion-prep 的必要条件的一部分，不是充分条件。Plan 没有把 warn 当作 ready 证明。

### 5. 是否需要更新 fixture manifest 或重跑 preflight？

**建议：需要更新 fixture manifest（如果 controller 批准 candidate decision）。**

Plan 允许可选更新 manifest。如果 004393/004194 被接受为 candidate，manifest 应从 `absent` 更新为 `promotion-prep-ready`。不需要重跑 preflight。

### 6. 是否存在修改 golden fixture / promotion_allowed=true / FQ0-FQ6 弱化 / QDII probing / FOF 误分类风险？

**建议：不存在。**

Plan 的 guardrails 和 stop conditions 覆盖了所有这些风险：
- 不修改 golden answer JSON
- 所有 entry `promotion_allowed=false`
- 不削弱 FQ0-FQ6
- 不重启 QDII probing
- 不把 QDII-FOF 计为 pure FOF

---

## Manifest / Preflight / Residual Alignment 验证

Plan 要求 implementation worker 做只读 join。以下是我对 10 个 entries 的验证结果：

| fund/slot | preflight row 存在 | residual row 存在 | residual `promotion_allowed=false` | fixture row 存在 | fixture `promotion_allowed=false` | source paths 存在 | 一致性 |
|---|---|---|---|---|---|---|---|
| 004393 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 004194 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 006597 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 017641 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 096001 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 040046 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 019172 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 021539 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| FOF_SLOT | ✅ | ✅ | ✅ | ✅ | ✅ | null paths ✅ | ✅ |
| 110020 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

三份 manifest + preflight 对 10 个 entries 的 blocker/owner/next_gate 无矛盾。FOF_SLOT source paths 为 null 符合预期。

---

## Summary

| # | Severity | Finding | Resolution |
|---|----------|---------|------------|
| 1 | MEDIUM | `promotion-prep-ready` 是新枚举值，需 controller 显式接受 | Controller judgment 裁决 |
| 2 | MEDIUM | correctness 数据（9/9、5/5）未引用 `score.json` 具体路径，`golden_set.json` 不是 correctness comparison | Implementation 必须从 `score.json` 提取并引用 |
| 3 | LOW | 006597 `covered` vs `not_configured` 两个维度语义需显式区分 | Decision artifact 已区分，可更显式 |
| 4 | LOW | 004393/004194 quality warn 具体 issues 未列出 | Implementation 必须补全 |
| 5 | LOW | preflight point-in-time 性质未显式声明 | Decision artifact 补充说明 |

Plan 可以被接受进入 implementation，但 implementation worker 必须解决 Finding 1（等待 controller 裁决）和 Finding 2（必须从 `score.json` 提取 correctness 数据并引用具体路径）。
