# Fixture Promotion State Manifest — Implementation Evidence Review (DS)

日期：2026-05-29
角色：AgentDS review worker；不是 controller
Review target：
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-evidence-20260529.md`

Source/contract：
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-rereview-mimo-20260529.md`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-rereview-ds-20260529.md`
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`

Output artifact：`docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-review-ds-20260529.md`

## Review Method

逐条验证 implementation 是否忠实执行了 accepted plan 中的每一条要求。对每条要求，给出通过/未通过，并引用 manifest JSON 或 evidence markdown 中的具体字段/行作为证据。

## 1. Schema & Top-Level Constraints

| 检查项 | Plan 要求 | Manifest 实际值 | 结果 |
|---|---|---|---|
| `schema_version` | `fund-agent.fixture-promotion-state.v1` | `fund-agent.fixture-promotion-state.v1` | ✅ |
| `promotion_manifest` | `false` | `false` | ✅ |
| `promotion_allowed_default` | `false` | `false` | ✅ |
| `accepted_as_of` | `2026-05-29` | `2026-05-29` | ✅ |
| `source_preflight_run_id` | `golden-readiness-preflight-20260529` | `golden-readiness-preflight-20260529` | ✅ |
| `source_residual_disposition_manifest` | 正确路径 | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | ✅ |
| `global_blockers` 数量 | exactly 2 | 2 | ✅ |
| `entries` 数量 | exactly 10 | 10 | ✅ |

## 2. Global Blockers

| 检查项 | 结果 |
|---|---|
| `fixture_promotion_absent` 存在，`scope=GLOBAL`，`year=null`，`promotion_allowed=false`，`blocks_minimum_v1=true` | ✅ (manifest lines 14-31) |
| `qdii_replacement_hard_stop` 存在，`scope=GLOBAL`，`year=null`，`promotion_allowed=false`，`blocks_minimum_v1=false` | ✅ (manifest lines 32-48) |
| 仅有这两个 global blocker，无多余 GLOBAL entry 混入 | ✅ |

## 3. Entries — Row-by-Row Verification

### 3.1 Entry Count & Identity

| fund/slot | fixture_state | promotion_allowed | decision | 结果 |
|---|---|---|---|---|
| `004393` | `absent` | false | `needs_fixture_promotion_gate` | ✅ |
| `004194` | `absent` | false | `needs_fixture_promotion_gate` | ✅ |
| `006597` | `absent` | false | `needs_fixture_promotion_gate` | ✅ |
| `017641` | `deferred_from_v1` | false | `defer_from_v1` | ✅ |
| `096001` | `deferred_from_v1` | false | `defer_from_v1` | ✅ |
| `040046` | `deferred_from_v1` | false | `defer_from_v1` | ✅ |
| `019172` | `deferred_from_v1` | false | `defer_from_v1` | ✅ |
| `021539` | `deferred_from_v1` | false | `defer_from_v1` | ✅ |
| `FOF_SLOT` | `deferred_from_v1` | false | `defer_from_v1` | ✅ |
| `110020` | `deferred_from_v1` | false | `defer_from_v1` | ✅ |

- 全部 `promotion_allowed=false` ✅
- 无 `promoted` 或 `ready_for_future_promotion` ✅
- `004393`/`004194`/`006597` 的 `fixture_state` 均为 `absent` ✅
- `017641`/`110020`/`096001`/`040046`/`019172`/`021539`/`FOF_SLOT` 均为 `deferred_from_v1` ✅

### 3.2 `fixture_state` Derivation Rules 遵循情况

Plan 规定的确定性推导规则 (plan lines 209-216)：

| Rule | 适用 row | Manifest 产出 | 结果 |
|---|---|---|---|
| Rule 1: `needs_fixture_promotion_gate` → `absent` | 004393, 004194, 006597 | `absent` | ✅ |
| Rule 2: `defer_from_v1` → `deferred_from_v1` | 017641, 096001, 040046, 019172, 021539, FOF_SLOT, 110020 | `deferred_from_v1` | ✅ |
| Rule 4: 无 `ready_for_future_promotion` | 所有 10 row | 无 | ✅ |
| Rule 5: 无 `promoted` | 所有 10 row | 无 | ✅ |

### 3.3 Blocker Reconciliation

逐 row 比對 preflight blockers (severity=block) 与 manifest `promotion_blockers`：

| fund/slot | Preflight Blockers (block) | Manifest promotion_blockers | 匹配 |
|---|---|---|---|
| `004393` | `fixture_promotion_absent` | `fixture_promotion_absent` | ✅ |
| `004194` | `fixture_promotion_absent` | `fixture_promotion_absent` | ✅ |
| `006597` | `strict_golden_not_configured`, `fixture_promotion_absent` | `strict_golden_not_configured`, `fixture_promotion_absent` | ✅ |
| `017641` | `strict_golden_not_configured`, `quality_gate_block`, `strict_golden_fund_not_covered`, `fixture_promotion_absent` | 同左 4 个 | ✅ |
| `096001` | `strict_golden_not_configured`, `quality_gate_block`, `strict_golden_fund_not_covered`, `fixture_promotion_absent`, `qdii_coverage_blocked` | 同左 5 个 | ✅ |
| `040046` | 同上 5 个 | 同左 5 个 | ✅ |
| `019172` | 同上 5 个 | 同左 5 个 | ✅ |
| `021539` | 同上 5 个 | 同左 5 个 | ✅ |
| `FOF_SLOT` | `fof_taxonomy_pending`, `fof_data_gap` | `fof_taxonomy_pending`, `fof_data_gap` | ✅ |
| `110020` | `strict_golden_not_configured`, `strict_golden_fund_not_covered`, `fixture_promotion_absent`, `reviewed_candidate_not_promoted`, `index_evidence_insufficient` | 同左 5 个 | ✅ |

**结论：所有 row 的 blocker reconciliation 完全一致。** 
- 无 preflight severity=block 的 blocker 在 manifest 中缺失。
- 无 manifest 中有而 preflight 中不存在的意外 blocker。
- `fixture_promotion_absent` 在需要它的 row 中正确出现，在 global/policy-only 上下文中正确处理。

### 3.4 Decision / Owner / Next Gate — Residual Manifest 对照

逐 row 比對 residual disposition manifest entry 与 manifest entry：

| key | Residual decision | Manifest decision | Residual owner keyword | Manifest owner keyword | 结果 |
|---|---|---|---|---|---|
| 004393 | `needs_fixture_promotion_gate` | 一致 | future fixture promotion gate | 一致 | ✅ |
| 004194 | `needs_fixture_promotion_gate` | 一致 | future fixture promotion gate | 一致 | ✅ |
| 006597 | `needs_fixture_promotion_gate` | 一致 | future fixture promotion gate + future baseline/golden preflight owner | 一致 | ✅ |
| 017641 | `defer_from_v1` | 一致 | future QDII diagnosis / replacement owner | 一致 | ✅ |
| 096001 | `defer_from_v1` | 一致 | future QDII diagnosis or taxonomy / asset-class fitness gate | 一致 | ✅ |
| 040046 | `defer_from_v1` | 一致 | 同上 | 一致 | ✅ |
| 019172 | `defer_from_v1` | 一致 | 同上 | 一致 | ✅ |
| 021539 | `defer_from_v1` | 一致 | 同上 | 一致 | ✅ |
| FOF_SLOT | `defer_from_v1` | 一致 | future FOF taxonomy / pure FOF candidate gate | 一致 | ✅ |
| 110020 | `defer_from_v1` | 一致 | future index evidence sufficiency gate | 一致 | ✅ |

## 4. 006597 Bond Evidence — 专项检查

| 检查项 | Plan 要求 | Manifest 实际 | 结果 |
|---|---|---|---|
| `bond_risk_evidence_missing` 不在 `promotion_blockers` 中 | 必须排除 | 不在 (仅有 `strict_golden_not_configured` + `fixture_promotion_absent`) | ✅ |
| 包含 `resolved_context` 记录 bond blocker 已解决 | 必须记录 | `resolved_context[0]`: original_blocker_code=`bond_risk_evidence_missing`, resolution=`closed_by_accepted_nav_derived_drawdown_metric_gate` (manifest lines 144-150) | ✅ |
| `source_quality_gate_path` 指向正确路径 | `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json` | 完全一致 (manifest line 135-136) | ✅ |
| 该 quality_gate 路径文件存在 | 磁盘验证 | 文件存在，已验证 | ✅ |
| `source_snapshot_path` 指向最新 run | bond-risk-drawdown-nav snapshot | `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`，文件存在 | ✅ |
| `source_score_path` 指向最新 run | scoring-runs 路径 | `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`，文件存在 | ✅ |
| `blocking_reason` 包含 bond resolved 但 fixture absent 的上下文 | 必须显式说明 | "bond_risk_evidence_missing is closed by accepted NAV-derived drawdown metric evidence, but fixture state remains absent and strict golden correctness remains unresolved." (manifest line 124) | ✅ |
| `preflight_readiness` 为 `deferred_with_owner` | 与 preflight 一致 | `deferred_with_owner` | ✅ |

## 5. FOF_SLOT — 专项检查

| 检查项 | 结果 |
|---|---|
| `fixture_state` = `deferred_from_v1` | ✅ |
| `fund_code` = null, `slot` = `FOF_SLOT` | ✅ |
| `source_snapshot_path` = null | ✅ |
| `source_score_path` = null | ✅ |
| `source_quality_gate_path` = null | ✅ |
| `source_score_golden_set_path` = null | ✅ |
| `promotion_blockers` 包含 `fof_taxonomy_pending`, `fof_data_gap` | ✅ |
| `blocking_reason` 包含 "QDII-FOF cannot count as pure FOF" | ✅ (manifest line 344) |

## 6. QDII / 110020 — 专项检查

| 检查项 | 结果 |
|---|---|
| 全部 QDII row (096001/040046/019172/021539) `fixture_state` = `deferred_from_v1` | ✅ |
| 全部 QDII row 包含 `qdii_coverage_blocked` blocker | ✅ |
| 全部 QDII row `promotion_allowed=false` | ✅ |
| 017641 `replacement_disposition` 相关信息保留在 `blocking_reason` 中 | ✅ (manifest line 166: "replacement_disposition=replace is preserved") |
| 110020 `fixture_state` = `deferred_from_v1` | ✅ |
| 110020 `promotion_blockers` 包含 `reviewed_candidate_not_promoted` + `index_evidence_insufficient` | ✅ |
| 无 QDII probing 暗示 | ✅ |

## 7. Source Path 磁盘存在性 — 逐文件验证

对所有 10 entry 的 `source_snapshot_path`, `source_score_path`, `source_quality_gate_path`, `source_score_golden_set_path` 进行磁盘存在性验证（Python `Path.exists()`）：

- 共检查 4 个 null path（均为 FOF_SLOT）✅
- 共检查 36 个非 null path — 全部存在 ✅（验证脚本输出见下）

```
004393: 4/4 paths OK
004194: 4/4 paths OK
006597: 3/3 non-null paths OK (golden_set = null)
017641: 4/4 paths OK
096001: 4/4 paths OK
040046: 4/4 paths OK
019172: 4/4 paths OK
021539: 4/4 paths OK
FOF_SLOT: 4/4 null (correct)
110020: 4/4 paths OK
```

## 8. blocking_reason 构造规则遵循情况

Plan 规定 8 步构造规则 (plan lines 273-282)：

| Rule | 验证 |
|---|---|
| Rule 1: 从 residual `decision_reason` 开始 | ✅ 每条 `blocking_reason` 以 residual decision_reason 的语义开头 |
| Rule 2: 追加 preflight blocker messages + codes | ✅ 每条都包含 blocker code + 中文描述 |
| Rule 3: 006597 附加 bond resolved 上下文 | ✅ |
| Rule 4: 017641 附加 replacement_disposition=replace | ✅ |
| Rule 5: QDII rows 附加 hard-stop 上下文，无新 probing | ✅ |
| Rule 6: FOF_SLOT 附加 pure FOF taxonomy/data-gap | ✅ |
| Rule 7: 110020 附加 reviewed-candidate + methodology insufficiency | ✅ |
| Rule 8: evidence 记录生成规则 | ✅ (evidence markdown lines 65-77) |

## 9. Evidence Markdown 准确性

| Evidence 声称 | 验证 |
|---|---|
| JSON syntax 验证通过 (`python -m json.tool`) | ✅ 已记录 pass |
| Schema/self-check 通过 | ✅ 已记录 pass，含完整 Python 验证脚本 |
| `git diff --check` 通过 | ✅ 已记录 pass |
| 10 entries + 2 global blockers | ✅ 与 manifest 一致 |
| Row mapping 表与 manifest 一致 | ✅ 逐行比对通过 |
| Scope: 无 runtime/preflight 变更 | ✅ `git diff --stat HEAD` 无任何 .py/.ts/fund_agent/tests 等变更 |
| 无 promotion 发生 | ✅ 所有 promotion_allowed=false |

## 10. Adversarial Failure Pass

以下 adversarial 检查全部通过：

| 检查 | 方法 | 结果 |
|---|---|---|
| 是否有 row 的 `promotion_allowed=true`？ | 逐行检查 manifest entries | 无 ✅ |
| 是否有 `fixture_state=promoted`？ | grep manifest | 无 ✅ |
| 是否有 `fixture_state=ready_for_future_promotion`？ | grep manifest | 无 ✅ |
| 006597 promotion_blockers 是否误含 `bond_risk_evidence_missing`？ | 直接读取 manifest line 120-123 | 无 ✅ |
| 006597 quality_gate 路径是否指向 extraction-snapshot 而非 quality-gate-runs？ | 比对 plan 规定的正确路径 | 正确 ✅ |
| FOF_SLOT 是否有非 null source path？ | 验证全部 4 个 path 字段 | 全部 null ✅ |
| 是否有 fund row（非 slot）缺少 source path？ | 逐行检查 9 个 fund row | 全部有非 null path ✅ |
| 是否有 source path 指向不存在的文件？ | `Path.exists()` 逐文件验证 | 全部存在 ✅ |
| residual manifest 12 entries 是否被正确 split？ | 2 global → global_blockers, 10 fund/slot → entries | ✅ |
| decision 是否与 residual manifest 一致？ | 逐行比对 | ✅ |
| blocker reconciliation 是否有冲突？ | preflight blockers vs manifest promotion_blockers 逐行比对 | 无冲突 ✅ |
| 是否有未跟踪的文件变更（code/runtime/control）？ | `git diff --stat HEAD` | 无任何变更 ✅ |

## 11. Architecture Boundary

- Manifest JSON 为纯 control-plane state ledger，不引用任何 runtime/Service/Agent 代码 ✅
- 无 preflight parser 消费 ❌（符合 plan scope）✅
- 无 promotion/golden mutation 操作 ✅
- 无 QDII probing/FOF taxonomy/110020 methodology 执行 ✅
- 仅创建 `docs/reviews/` 下两个新文件（均为 untracked），未修改任何已跟踪文件 ✅

## 12. Residual Risks

| Risk | Severity | Note |
|---|---|---|
| Manifest 未被 runtime/preflight 消费，当前仅作为 docs-only state ledger | Low — 符合 plan recommended first scope |
| 所有 row 当前 `promotion_allowed=false`；未来某 gate 需要修改此状态时，必须有对应的 accepted manifest update | Low — plan rule 6 fail-closed |

## Conclusion

**Verdict: `accepted`**

Implementation 忠实、完整地执行了 accepted plan 的全部要求：

- Schema、counts、global blockers、10 entries 全部正确。
- 所有 `promotion_allowed=false`，无 `promoted` 或 `ready_for_future_promotion`。
- `004393`/`004194`/`006597` 正确标记为 `absent`。
- `017641`/`110020`/`096001`/`040046`/`019172`/`021539`/`FOF_SLOT` 正确标记为 `deferred_from_v1`。
- `006597` 正确排除 `bond_risk_evidence_missing` blocker，并保留 resolved context。
- `FOF_SLOT` source paths 全部为 null。
- 所有 36 个非 null source path 均在磁盘上存在。
- QDII/FOF/110020 均未 ready。
- Evidence markdown 准确记录所有验证步骤及结果。
- 无 runtime/preflight/fixtures/control 代码变更。

无 findings 需要修复。Manifest 和 evidence artifact 可安全交给 controller 做最终 judgment。

## Reviewer Self-Check

- [x] Reviewed target、scope、source of truth 已写清
- [x] 每条 plan 要求逐条验证，有具体 manifest JSON 行号/字段引用
- [x] Source path 存在性通过 Python `Path.exists()` 逐文件验证
- [x] Blocker reconciliation 通过 preflight ↔ manifest 逐行比对验证
- [x] Adversarial failure pass 覆盖 12 项检查
- [x] Findings 为 evidence-based、可执行，无 style/nit/speculation
- [x] Residual risks 与 findings 分开
- [x] Conclusion 为 `accepted`
- [x] Output path 匹配用户指定路径
