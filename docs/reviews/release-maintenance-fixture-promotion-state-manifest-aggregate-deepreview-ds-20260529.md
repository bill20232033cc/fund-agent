# Fixture Promotion State Manifest — Aggregate Deepreview (DS)

日期：2026-05-29
角色：AgentDS aggregate deepreview worker；不是 controller

## Reviewed Artifacts

| Role | Artifact | Verdict |
|---|---|---|
| Plan | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md` | 修订版经 MiMo/DS re-review accepted |
| Plan review (MiMo, initial) | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-mimo-20260529.md` | accepted-with-required-fixes |
| Plan review (DS, initial) | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-ds-20260529.md` | pass-with-risks |
| Plan re-review (MiMo) | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-rereview-mimo-20260529.md` | accepted |
| Plan re-review (DS) | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-rereview-ds-20260529.md` | accepted |
| Implementation manifest | `docs/reviews/fixture-promotion-state-manifest-20260529.json` | — |
| Implementation evidence | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-evidence-20260529.md` | — |
| Implementation review (MiMo) | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-review-mimo-20260529.md` | accepted |
| Implementation review (DS) | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-review-ds-20260529.md` | accepted |

Source of truth consumed：`AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、preflight JSON、12-entry residual disposition manifest。

## 1. Gate Objective

Gate objective：产出 accepted machine-readable fixture promotion state manifest，描述所有 fund/slot 的当前 fixture promotion state，明确 `promotion_allowed=false`、阻塞原因、owner、next gate 和证据来源。不执行 promotion、不修改 golden fixtures、不改变 runtime 行为。

**结论：gate objective satisfied。**

- Manifest JSON 存在且通过 `python -m json.tool` 校验。
- Schema version `fund-agent.fixture-promotion-state.v1`，`promotion_manifest=false`。
- 2 global blockers + 10 fund/slot entries，与 preflight（10 rows）和 residual manifest（12 entries：2 GLOBAL + 10 fund/slot）完全对齐。
- 全部 12 条记录 `promotion_allowed=false`，无 `promoted` 或 `ready_for_future_promotion`。
- 两份独立 implementation review 均为 `accepted`，零 findings。

## 2. No Golden Promotion

逐条检查 manifest 所有 entry 和 global blocker：
- 全部 `promotion_allowed=false` ✅
- `promotion_manifest=false` ✅
- `promotion_allowed_default=false` ✅
- 无 `fixture_state=promoted` ✅
- 无 `fixture_state=ready_for_future_promotion` ✅

**结论：无 golden promotion 发生。**

## 3. No Golden Fixture Changes

Implementation evidence 确认 scope 为 docs/reviews JSON/evidence only。未修改任何 golden answer fixture、golden corpus fixture、promoted fixture 或 golden prefill/preflight 产物。未修改 `fund_agent/fund/golden_answer.py`、`golden_prefill.py` 或任何 golden 相关代码。`git diff --stat HEAD` 无已跟踪文件变更。

**结论：无 golden fixture 变更。**

## 4. No FQ0-FQ6 Weakening

Manifest 不改变 quality gate 规则、score policy、snapshot generation 或 FQ0-FQ6 语义。各 entry 的 `promotion_blockers` 如实反映了 preflight 报告的 quality gate 状态（如 QDII row 的 `quality_gate_block`），但未修改 gate 判断逻辑。Quality gate 相关的 blocker 是观测记录，不是语义变更。

**结论：FQ0-FQ6 语义未削弱。**

## 5. Manifest Machine-Readable and Complete

### 5.1 JSON 结构

- 有效 JSON，`python -m json.tool` 通过。
- Top-level 包含全部 required 字段：`schema_version`、`accepted_as_of`、`source_preflight_run_id`、`source_residual_disposition_manifest`、`promotion_manifest`、`promotion_allowed_default`、`source_artifacts`、`global_blockers`、`entries`。
- `global_blockers` 含 2 条记录，均有 `scope=GLOBAL`、`year=null`、`promotion_allowed=false`。
- `entries` 含 10 条记录，所有 fund row 有 `fund_code`、`slot=null`，`FOF_SLOT` 有 `fund_code=null`、`slot=FOF_SLOT`。

### 5.2 Required 字段完整性（逐 entry）

每条 entry 均包含 plan 要求的全部 required 字段：`fund_code`/`slot`、`year`、`fixture_state`、`promotion_allowed`、`promotion_blockers`（非空）、`blocking_reason`（非空）、`decision`、`owner`、`next_gate`、`evidence_artifacts`、`source_snapshot_path`、`source_score_path`、`source_quality_gate_path`。全部通过。

### 5.3 Source Path 磁盘存在性

所有 36 个非 null source path 均通过 `Path.exists()` 验证。FOF_SLOT 的 4 个 source path 均为 null（符合 plan 要求）。006597 的 `source_quality_gate_path` 指向正确的 `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`（非 extraction-snapshots 目录）。

### 5.4 fixture_state 推导规则遵循

Plan 的 6 条确定性推导规则全部正确执行：
- Rule 1（`needs_fixture_promotion_gate` → `absent`）：004393、004194、006597 ✅
- Rule 2（`defer_from_v1` → `deferred_from_v1`）：017641、096001、040046、019172、021539、FOF_SLOT、110020 ✅
- Rule 4（禁止 `ready_for_future_promotion`）：全部 10 row ✅
- Rule 5（禁止 `promoted`）：全部 10 row ✅

### 5.5 Blocker Reconciliation

Preflight `severity=block` blockers 与 manifest `promotion_blockers` 逐行比对，完全一致。无缺失、无多余、无冲突。Global/policy-only 例外（`fixture_promotion_absent`、`qdii_replacement_hard_stop`）正确处理。

### 5.6 blocking_reason 构造规则

Plan 的 8 步构造规则全部遵循：
- 每条以 residual `decision_reason` 语义开头 ✅
- 每条包含 preflight blocker code + 中文描述 ✅
- 006597：含 bond resolved 上下文 ✅
- 017641：含 `replacement_disposition=replace` ✅
- QDII rows：含 hard-stop 上下文，无新 probing 暗示 ✅
- FOF_SLOT：含 pure FOF taxonomy/data-gap、QDII-FOF 不可计数 ✅
- 110020：含 reviewed-candidate-not-promoted + methodology/constituents insufficiency ✅
- Evidence markdown 记录了生成规则 ✅

**结论：manifest machine-readable 且完整。**

## 6. 006597 Bond Blocker Resolved but Fixture Absent

Manifest 正确处理了 006597 的双重事实：

- `promotion_blockers` 不含 `bond_risk_evidence_missing` ✅
- `promotion_blockers` 含 `strict_golden_not_configured` + `fixture_promotion_absent` ✅
- `resolved_context` 记录 `bond_risk_evidence_missing` 已由 accepted NAV-derived drawdown metric gate 关闭 ✅
- `fixture_state=absent` ✅（bond 问题解决不意味着 fixture 就绪）
- `blocking_reason` 显式说明 "bond_risk_evidence_missing is closed ... but fixture state remains absent and strict golden correctness remains unresolved" ✅
- `source_quality_gate_path` 指向正确的 `reports/quality-gate-runs/...` 路径，且文件存在 ✅
- Plan 要求的 stop condition（若 006597 当前 blocker 含 `bond_risk_evidence_missing` 则 stop）未被触发，因为 regression 未发生 ✅

**结论：006597 bond blocker resolved 但 fixture absent 正确处理。**

## 7. QDII / FOF / 110020 Deferred/Blocked Not Ready

### QDII rows（096001、040046、019172、021539）

- 全部 `fixture_state=deferred_from_v1` ✅
- 全部 `promotion_allowed=false` ✅
- 全部含 `qdii_coverage_blocked` blocker ✅
- 全部 `blocks_minimum_v1=false`（不阻塞 minimum v1，但阻塞 full v1）✅
- `blocking_reason` 含 QDII hard-stop 上下文但无新 probing 暗示 ✅

### 017641

- `fixture_state=deferred_from_v1` ✅
- `replacement_disposition=replace` 保留在 `blocking_reason` 中 ✅
- `blocks_minimum_v1=false` ✅

### FOF_SLOT

- `fixture_state=deferred_from_v1` ✅
- 全部 source path 为 null ✅
- `promotion_blockers` 含 `fof_taxonomy_pending` + `fof_data_gap` ✅
- `blocking_reason` 含 "QDII-FOF cannot count as pure FOF" ✅

### 110020

- `fixture_state=deferred_from_v1` ✅
- `promotion_blockers` 含 `reviewed_candidate_not_promoted` + `index_evidence_insufficient` ✅
- 方法论/成分股/reviewed fact freeze 不足已记录 ✅

**结论：QDII/FOF/110020 全部 deferred/blocked，无一 ready。**

## 8. Control Doc Update Pending

`docs/implementation-control.md` 当前仍显示：
- Current gate: `golden readiness residual disposition gate accepted local validation`
- Next entry point: `fixture promotion state manifest gate`

Manifest gate 的 accepted artifacts、decision summary、active gate ledger entry 尚未写入 control doc。该更新属于 controller 在最终 judgment 后的独立操作，不属于本 aggregate deepreview 或 manifest implementation 的范围。

**状态：已知待办，不影响 manifest 的正确性或本 gate 的 acceptance。**

## 9. Cross-Artifact Consistency Check

### 9.1 Plan → Implementation 一致性

| Plan 要求 | Implementation | 一致 |
|---|---|---|
| Schema version `fund-agent.fixture-promotion-state.v1` | 正确 | ✅ |
| 2 global blockers + 10 entries | 正确 | ✅ |
| `fixture_state` derivation rules (6 rules) | 全部遵循 | ✅ |
| Blocker reconciliation stop conditions | 全部通过（无冲突触发） | ✅ |
| `blocking_reason` construction rules (8 steps) | 全部遵循 | ✅ |
| 006597 quality_gate path 正确 | `reports/quality-gate-runs/...` | ✅ |
| Source path 文件存在性校验 | 全部 36 个非 null path 存在 | ✅ |
| No promotion/golden/FQ/score/quality changes | 仅 docs/reviews 新文件 | ✅ |

### 9.2 Preflight → Manifest 一致性

- 10 preflight rows → 10 manifest entries ✅
- Preflight `blockers[]` (severity=block) → manifest `promotion_blockers` 逐行一致 ✅
- Preflight static disposition source paths → manifest source paths 一致 ✅
- Preflight `fixture_promotion_state=absent` → manifest `fixture_state=absent` 对 004393/004194/006597 ✅

### 9.3 Residual Manifest → Manifest 一致性

- 12 residual entries → 2 global_blockers + 10 entries ✅
- Residual `decision` → manifest `decision` 逐行一致 ✅
- Residual `blocks_v1` / `blocks_minimum_v1` → manifest 对应字段一致 ✅
- Residual `current_blockers` → manifest `promotion_blockers` 一致（含 global/policy-only 例外处理）✅

### 9.4 MiMo Review ↔ DS Review 一致性

两份 implementation review 结论均为 `accepted`，零 findings。检查清单覆盖的验证点高度一致（schema、counts、states、006597 bond、FOF null paths、source path existence、QDII/110020 deferred）。无 reviewer 之间的结论冲突。

## 10. Adversarial Failure Pass

| 攻击面 | 测试方法 | 结果 |
|---|---|---|
| 是否有 row 被标记为 promoted？ | grep manifest | 无 ✅ |
| 是否有 row promotion_allowed=true？ | 逐行检查 | 无 ✅ |
| 006597 是否误含 bond_risk_evidence_missing？ | 直接读取 | 无 ✅ |
| 006597 quality_gate 路径是否指向错误目录？ | 比对 plan + 磁盘验证 | 正确 ✅ |
| FOF_SLOT 是否有非 null source path？ | 逐字段检查 | 全部 null ✅ |
| 是否有 fund row 缺少 source path？ | 9 个 fund row 逐一检查 | 全部有非 null path ✅ |
| 是否有 source path 指向不存在文件？ | Path.exists() 全量验证 | 全部存在 ✅ |
| QDII row 的 blocking_reason 是否暗示新 probing？ | 全文搜索 | 无 ✅ |
| 是否有 deferred row 被标记为 ready？ | fixture_state 检查 | 无 ✅ |
| 是否有未授权的代码/runtime/control doc 变更？ | git diff | 无 ✅ |
| Blocker reconciliation 是否有遗漏或多余？ | preflight ↔ manifest 逐行比对 | 完全一致 ✅ |
| Residual manifest 12 entries 是否正确 split？ | 2 GLOBAL → global_blockers, 10 fund/slot → entries | 正确 ✅ |

全部 12 项 adversarial 检查通过，零假阳性、零漏报。

## 11. Architecture Boundary

- Manifest 为纯 control-plane state ledger，不引用 runtime/Service/Agent 代码 ✅
- 无 preflight parser 消费 manifest（符合 plan recommended first scope）✅
- 无 promotion/golden mutation 操作 ✅
- 无 QDII probing / FOF taxonomy work / 110020 evidence work ✅
- 仅 `docs/reviews/` 下两个新文件（JSON + evidence md），未修改已跟踪文件 ✅
- 四层边界（UI → Service → Host → Agent）未触及 ✅

## 12. Plan Review Fix Loop Completeness

Plan phase 的 4 个 controller accepted findings 修复闭环完整：

| Finding | 来源 | 修复 | Re-review 验证 |
|---|---|---|---|
| 006597 quality_gate 路径错误 + 文件存在性校验缺失 | MiMo #1 | 路径更正为 `reports/quality-gate-runs/...`；fail-closed join 条件新增 source path 存在性检查 | MiMo re-review: ✅ DS re-review: ✅ |
| fixture_state 推导规则不完整 | DS #1 | 6 条确定性推导规则 | MiMo re-review: ✅ DS re-review: ✅ |
| "conflict materially" 未定义 | DS #2 | 具体 blocker reconciliation stop conditions 替代模糊措辞 | MiMo re-review: ✅ DS re-review: ✅ |
| blocking_reason 无填充规则 | DS #3 | 8 步构造规则 | MiMo re-review: ✅ DS re-review: ✅ |

所有修复在 revised plan 中正确落地，implementation 忠实执行。

## 13. Findings

### Finding 1 — 低 — Manifest 含 plan schema 未显式列出的 provenance 字段

- **位置**: manifest JSON 全部 10 entry，字段 `source_static_promotion_state` 和 `preflight_fixture_promotion_state`
- **性质**: 这两个字段不在 plan 的 required 或 optional/recommended 字段列表中。它们的语义来自 preflight static disposition manifest 的 `promotion_state` 和 preflight row 的 `fixture_promotion_state`。
- **实际影响**: 无。这两个字段是 provenance/audit trail，不改变 `fixture_state`、`promotion_allowed` 或任何 policy 判断。两份 implementation review 均已接受，未将其标记为 issue。
- **建议**: Controller 可在 judgment 中明确这些 provenance 字段是否接受为 manifest schema 的一部分。若接受，无需修改；若要求严格对齐 plan schema，可移入 evidence markdown 或标记为 optional provenance annex。
- **严重程度**: 低

### Finding 2 — 信息级 — Control doc 尚未更新

- **位置**: `docs/implementation-control.md`
- **性质**: Current gate 仍为 `golden readiness residual disposition gate accepted local validation`，Next entry point 仍为 `fixture promotion state manifest gate`。Manifest gate 的 accepted artifacts、decision summary、active gate ledger 均未写入。
- **实际影响**: 无——这是 controller judgment 后的独立操作，不属于 manifest implementation scope。Plan 也未要求 implementation worker 更新 control doc。
- **建议**: Controller 在最终 judgment 后将本 gate 的 accepted artifacts 和 decision summary 写入 control doc，并将 Next entry point 推进到下一个 gate。
- **严重程度**: 信息级（已知待办）

## 14. Residual Risks

| Risk | Severity | Tracking |
|---|---|---|
| Manifest 未被 runtime/preflight 消费 | 低 | 符合 plan recommended first scope；未来如需消费需独立 implementation gate |
| `fixture_state` derivation rules 仅覆盖 `needs_fixture_promotion_gate` 和 `defer_from_v1` 两种 decision | 低 | Rule 6 fail-closed；未来新 decision 类型会 stop 而非产出错误 manifest |
| 006597 bond blocker regression 检测依赖手动检查 | 低 | Current manifest gate 已验证无 regression；未来 gate 若重新运行 006597 snapshot/score/quality，需显式重新验证 |
| Control doc 未更新 | 低 | Controller judgment 后的标准操作 |

## 15. Conclusion

**Verdict: `accepted`**

Gate objective satisfied on all primary dimensions:

- **Manifest 产出**: machine-readable JSON 存在，schema 正确，2 global blockers + 10 entries 完整。
- **No golden promotion**: 全部 `promotion_allowed=false`，无 `promoted` 或 `ready_for_future_promotion`。
- **No golden fixture changes**: 未修改任何 golden answer/corpus/prefill/preflight fixture。
- **No FQ0-FQ6 weakening**: quality gate 语义未变更，blocker 仅为观测记录。
- **006597 正确**: bond blocker resolved 记录在 `resolved_context`，`fixture_state=absent`，`promotion_blockers` 不含 `bond_risk_evidence_missing`。
- **QDII/FOF/110020 正确**: 全部 `deferred_from_v1`，无一 ready。
- **Plan → Implementation 忠实执行**: 6 条 fixture_state 推导规则、8 步 blocking_reason 构造规则、blocker reconciliation stop conditions、source path 存在性等全部遵循。
- **两份独立 implementation review 均 accepted**，零 findings。

Low-severity Finding 1（额外 provenance 字段）不影响 correctness 或 safety，controller 可自行决定是否要求严格对齐 plan schema。信息级 Finding 2（control doc 待更新）是 controller judgment 后的标准后续操作。

Manifest 和 evidence artifact 可安全进入 controller judgment。

## Reviewer Self-Check

- [x] 全部 gate artifacts（plan、4 plan reviews、manifest JSON、evidence、2 implementation reviews）已读取
- [x] Gate objective、no promotion、no golden changes、no FQ weakening、manifest completeness、006597、QDII/FOF/110020 逐项验证
- [x] Cross-artifact consistency（plan→implementation、preflight→manifest、residual→manifest、MiMo↔DS reviews）全部检查
- [x] Adversarial failure pass 覆盖 12 项，零假阳性
- [x] Plan review fix loop completeness 验证
- [x] Findings 与 residual risks 分开，严重程度明确
- [x] Architecture boundary 安全
- [x] Conclusion 为 `accepted`
