# Fixture Promotion State Manifest Plan — Re-Review (DS)

日期：2026-05-29
角色：AgentDS re-review worker；不是 controller
Re-review target：`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md`（修订版）
Prior DS review：`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-ds-20260529.md`
Prior MiMo review：`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-mimo-20260529.md`
Output artifact：`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-rereview-ds-20260529.md`

## Re-Review Purpose

验证修订版 plan 是否正确修复了 controller accepted 的 4 个 findings：
DS Finding 1（fixture_state 推导规则不完整）、DS Finding 2（blocker conflict stop 条件模糊）、DS Finding 3（blocking_reason 无填充规则）、MiMo Finding 1（006597 quality_gate 路径错误 + 缺少文件存在性校验）。

同时检查修订是否引入新的 material issue。

## Accepted Fixes Verification

### Fix 1: Deterministic `fixture_state` Derivation Rules (DS Finding 1)

- **原问题**: `fixture_state` 推导规则不完整，implementation agent 无法在 `absent` vs `not_promoted` vs `blocked` vs `deferred_from_v1` 之间确定性选择。
- **修订位置**: Manifest Semantics > Deterministic `fixture_state` derivation rules（lines 209–216）
- **修订内容**:
  1. `decision="needs_fixture_promotion_gate"` + preflight `fixture_promotion_state="absent"` → `absent`
  2. `decision="defer_from_v1"` → `deferred_from_v1`
  3. `quality_gate_block` 保留在 promotion_blockers/blocking_reason 中，但不得将 deferred row 变为 `ready_for_future_promotion`
  4–5. `ready_for_future_promotion` 和 `promoted` 对所有当前 row 禁止
  6. 未来出现未覆盖的 decision/state 组合 → stop
- **验证**: 6 条规则覆盖了当前 10 个 row 的全部两种情况（3 个 absent + 7 个 deferred_from_v1），对未来未知组合 fail-closed。每条规则产出的 fixture_state 是唯一确定的。
- **结论**: ✅ 已修复。推导规则现在确定且 fail-closed。

### Fix 2: Concrete Blocker Reconciliation Stop Conditions (DS Finding 2)

- **原问题**: "if preflight and residual blocker sets conflict materially" 中 "materially" 未定义，implementation agent 需要自行做 policy 判断。
- **修订位置**: Consuming The 12-Entry Residual Disposition Manifest > Concrete blocker reconciliation stop conditions（lines 256–264）
- **修订内容**:
  - preflight `severity="block"` blocker 不在 residual `current_blockers` → stop
  - residual `current_blockers` 项不在 preflight `blockers[]` → stop（global/policy-only 例外）
  - global/policy-only 例外限定为 `qdii_replacement_hard_stop`、top-level `fixture_promotion_absent`、`policy_status`、`replacement_disposition`，且不得插入 fund-row reconciliation 除非已在该 row 的 preflight blockers 中
  - fund code / slot id / year 不匹配 → stop
  - join key 重复或缺失 → stop
  - `006597` 有 `bond_risk_evidence_missing` → stop
  - warning-only 差异 → 记录但不 stop
- **验证**: 每个 stop 条件具体、可机械执行，不需要 agent 做 "materiality" 判断。例外列表封闭且 scope 清晰。当前 10 row 数据无冲突（经 DS 首次 review 逐行比对确认）。
- **结论**: ✅ 已修复。"materially" 歧义已消除，所有 stop 条件可机械判定。

### Fix 3: `blocking_reason` Generation Rule (DS Finding 3)

- **原问题**: `blocking_reason` 定义为 "Human-readable explanation" 但没有构造规则，不同 row 的详略和风格可能不一致。
- **修订位置**: Consuming The 12-Entry Residual Disposition Manifest > Blocking reason construction（lines 273–282）
- **修订内容**:
  1. 从 residual manifest `decision_reason` 开始
  2. 追加每个 preflight blocker message 的简明摘要，保留 blocker code
  3–7. 为 006597、017641、QDII rows、FOF_SLOT、110020 分别给出显式的附加上下文要求
  8. implementation evidence 必须记录该生成规则，并提供每 row 生成的 `blocking_reason` 或 row 级摘要证明规则被遵循
- **验证**: 规则给出了明确的起点（decision_reason）、追加内容（preflight blocker messages + codes）和特殊上下文的显式措辞要求。10 个 row 每 row 都有对应的特殊规则（006597 / 017641 / QDII / FOF_SLOT / 110020 / 默认 rule 1+2）。
- **结论**: ✅ 已修复。构造规则具体到可被 implementation agent 机械执行、被 reviewer 逐 row 验证。

### Fix 4: 006597 `quality_gate` Path Correction + Source Path Existence Validation (MiMo Finding 1)

- **原问题**: plan example JSON 和 Bond Evidence Handling 节中 006597 `source_quality_gate_path` 指向 `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`，该路径文件不存在。正确路径为 `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`。plan 的 self-check 也未包含文件存在性校验。
- **修订位置**:
  - Schema > Entry object fields example（line 162）: 已改为 `reports/quality-gate-runs/...`
  - 006597 Bond Evidence Handling（lines 325–326）: 已改为正确路径，并显式标注 "must remain exactly ... do not substitute the extraction-snapshot directory quality gate path"
  - Fail-closed join conditions（line 251）: 新增 "If any non-null source_snapshot_path, source_score_path, or source_quality_gate_path does not exist on disk, stop"
  - Validation checklist（line 391）: 新增 "every non-null source_snapshot_path, source_score_path, and source_quality_gate_path exists on disk"
- **磁盘验证**: `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json` 存在；`reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/` 目录仅有 `snapshot.jsonl`、`summary.md`、`errors.jsonl`，无 `quality_gate.json`。
- **结论**: ✅ 已修复。路径已更正为磁盘存在的正确路径；文件存在性校验已加入 fail-closed join conditions 和 validation checklist。

## New Issues Search

对修订版 plan 逐节检查是否引入新的 material issue：

### 检查 blocker reconciliation 例外列表的完整性

新增的例外列表（line 259–260）包含 `fixture_promotion_absent` 作为 global/policy-only 例外。当前 `needs_fixture_promotion_gate` 的 3 个 fund row（004393/004194/006597）在 preflight blockers 和 residual current_blockers 中均有 `fixture_promotion_absent`，因此不会触发 stop。例外列表的闭合性合理：`fixture_promotion_absent` 是系统级状态，即使未来某 row 的 residual 有此 blocker 而 preflight 报告方式不同，不应导致 spurious stop。

### 检查 fixture_state 推导规则与 Required Current Row Mapping 的一致性

推导规则（lines 209–216）产出：3 个 `absent` + 7 个 `deferred_from_v1`。Row mapping 表（lines 286–297）产出完全一致。无矛盾。

### 检查 006597 bond blocker 处理的一致性

修订版在以下位置一致地排除了 `bond_risk_evidence_missing`：
- Row mapping 表（line 290）：仅列 `strict golden not configured` + `fixture state absent`
- Bond Evidence Handling（line 320）：显式要求 "Do not include bond_risk_evidence_missing in promotion_blockers"
- Fail-closed 条件（line 254, 263）：两处 stop condition 覆盖 bond blocker regression
- Validation checklist（line 393）：显式校验 006597 不列 `bond_risk_evidence_missing`

无矛盾。

### 检查 FOF_SLOT null path 处理

Fail-closed 条件（line 252）："If FOF_SLOT has non-null source snapshot/score/quality paths, stop" — 与 row mapping（line 296：source paths must be null）一致。

### 检查 scope boundary 一致性

Plan 在以下位置一致声明 JSON/evidence-only scope：
- Revision Notes（line 27）
- Classification And Scope（lines 67–70）
- Future Preflight Consumption Decision（lines 358–373）
- Parser / Validation Test Decision（lines 377–397）

无 scope creep。

### 检查是否有新的 unspecified behavior

- `fixture_state` derivation rule 6（line 216）："If a future source row has a different decision/state combination, implementation must stop" — 对当前 10 row 不触发，对未来情况 fail-closed。合理。
- `not_promoted` 和 `blocked` enum values 在当前 manifest 中不使用（lines 303–305），但保留在 schema 中供未来使用。修订版未删改这些语义，与 schema 完整性一致。

## Architecture Boundary Review

修订未改变 plan 的架构边界。Scope 仍为 `docs/reviews` JSON/evidence only。无新代码、runtime、preflight、Host/Agent/dayu 边界变更。四层边界安全。

## Best-Practice Review

修订遵循 fail-closed 惯例：每个不确定情况（未知 decision/state 组合、blocker mismatch、path missing）都 stop 而非继续。新增的 `blocking_reason` 构造规则使 manifest 的 reviewability 显著提升。

## Overengineering Review

新增规则（derivation rules、stop conditions、blocking_reason construction）均为填补原 plan gap 所需，无过度抽象或预留。

## Overcoupling Review

修订未引入新的耦合。Manifest JSON 与 preflight / residual disposition 之间仍为单向引用。

## Residual Risks

| Risk | Likelihood | Impact | Suggested tracking |
|------|-----------|--------|-------------------|
| `fixture_state` derivation rules 仅覆盖 `needs_fixture_promotion_gate` 和 `defer_from_v1` 两种 decision；未来若出现新 decision 类型，rule 6 fail-closed 会 stop | 中 | 低：stop 是安全默认行为，不会产出错误 manifest | 未来 gate plan 需显式扩展 derivation table |
| `blocking_reason` 生成依赖 implementation agent 忠实执行 rule 1–8；若某 row 的 preflight blocker message 为空或过长，生成结果可能不一致 | 低 | 低：evidence artifact 记录生成规则和结果，review 可发现偏差 | implementation evidence 需逐 row 展示 blocking_reason 与 rule 的对应 |
| `fixture_promotion_absent` 在 blocker reconciliation 例外列表中；若未来有 row 的 residual 包含此 blocker 但 preflight 报告方式完全改变，可能被静默豁免而非 stop | 低 | 低：该例外有合理语义基础（系统级状态） | 未来 gate 如需收紧，可缩小例外列表 |

## Open Questions

无 blocking open question。

Plan 自述 "No blocking open question"（line 503–504），与当前修订状态一致。

## Conclusion

**Verdict: `accepted`**

4 个 controller accepted findings 全部验证通过：

- DS Finding 1 ✅ — 6 条确定性 `fixture_state` derivation rules，fail-closed
- DS Finding 2 ✅ — 具体 blocker reconciliation stop conditions，消除 "materially" 歧义
- DS Finding 3 ✅ — `blocking_reason` 8 步构造规则，逐 row 可执行
- MiMo Finding 1 ✅ — 006597 quality_gate 路径已更正，磁盘验证通过；source path 文件存在性校验已加入 fail-closed conditions 和 validation checklist

修订版 plan 未引入新的 material issue。Plan 对 scope boundary、schema semantics、12-entry residual manifest consumption、006597 bond 处理、QDII/FOF/110020 处置、stop conditions 和 validation strategy 的覆盖完整。Plan 已达到 code-generation-ready 状态，可安全交给 implementation agent。

## Reviewer Self-Check

- [x] Reviewed target、scope、source of truth、assumptions tested 已写清
- [x] 4 个 accepted fixes 逐一验证，有具体 plan line 引用和证据
- [x] New issues search 覆盖了 blocker reconciliation 例外列表、fixture_state 一致性、006597 bond blocker 一致性、FOF_SLOT null path、scope boundary
- [x] Findings 是 evidence-based、adversarial、可执行的，无 style/nit/speculation
- [x] Open questions、residual risks、tracking destination 与 findings 分开
- [x] Conclusion 为 `accepted`
- [x] Output path 匹配用户指定路径
