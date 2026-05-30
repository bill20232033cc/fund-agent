# 004393 Partial Coverage Decision Plan Review (AgentGLM)

日期：2026-05-29

角色：AgentGLM 独立 review worker。本文是 plan review artifact，不是 controller judgment，不启动 `$gateflow` / `/gateflow` / `phaseflow`，不修改代码、runtime、reports、manifests、golden files 或 control doc，不 commit、push、PR、merge、release、promote 或进入其它 gate。

---

## Review Scope

被审 plan artifact：`docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-20260529.md`

Review 来源：`AGENTS.md`、`docs/design.md` §7.3 / §7.4、`docs/implementation-control.md`、`docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`、`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md`、`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md`、`reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`、`docs/reviews/fixture-promotion-state-manifest-20260529.json`、`reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json`、`reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/snapshot.jsonl`、`reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/quality_gate.json`、`reports/golden-answers/golden-answer.json`。

---

## Verification Matrix

### 1. Field Counts

| Claim in plan | Verified value | Source | Match? |
|---|---|---|---|
| Score-wide `total_records=150` | `150` | `score.json` `correctness.total_records` | ✅ |
| Score-wide `comparable_records=9` | `9` | `score.json` `correctness.comparable_records` | ✅ |
| Score-wide `matched_records=9` | `9` | `score.json` `correctness.matched_records` | ✅ |
| Score-wide `mismatched_records=0` | `0` | `score.json` `correctness.mismatched_records` | ✅ |
| Score-wide `unavailable_records=141` | `141` | `score.json` `correctness.unavailable_records` | ✅ |
| Same-fund 004393 P0: `9 matched, 2 unavailable = 11 total` | Verified: 9 matched P0 + 2 unavailable P0 (`manager_strategy_text.strategy_summary`, `manager_strategy_text.market_outlook`) | `score.json` `record_results[]` filtered `fund_code=004393` | ✅ |
| Same-fund 004393 P1: `0 matched, 10 unavailable` | Verified: 0 matched P1 + 10 unavailable P1 (`product_profile.*` x3, `manager_alignment.*` x2, `holder_structure.*` x2, `share_change.*` x3) | `score.json` `record_results[]` | ✅ |

### 2. Priority Mapping

Plan says priority comes from `docs/design.md` §7.3. Verified:

- §7.3 P0 字段：`basic_identity`, `classified_fund_type`, `benchmark`, `nav_benchmark_performance`, `fee_schedule`, `manager_strategy_text`。9 matched rows 全部属于 P0 字段。✅
- §7.3 P1 字段：`product_profile`, `index_profile`, `tracking_error`, `turnover_rate`, `holder_structure`, `manager_alignment`, `holdings_snapshot`, `share_change`。10 unavailable rows 全部属于 P1 字段。✅
- P2 字段：`investor_return`, `nav_data`。004393 无 P2 golden rows。✅

### 3. P0 Mandatory Before Minimum v1

Plan says `manager_strategy_text.strategy_summary` 和 `manager_strategy_text.market_outlook` 是 P0 且 mandatory before minimum v1 promotion-prep。

- 二者均属于 §7.3 P0 字段 `manager_strategy_text`。✅
- 二者在 `golden-answer.json` 中存在 004393 期望值（`strategy_summary` 有完整策略文本，`market_outlook` 有完整市场展望文本），说明 golden answer 已 review 但 snapshot 未暴露为 comparable。✅
- 二者缺失原因是 `snapshot.jsonl` 中 `manager_strategy_text` 字段 `value_present=true`、`anchor_present=true` 但 `comparable_values={}`（空字典），即 projection gap。✅
- 结论：plan 正确判定这两个 P0 字段必须在未来 extractor projection gate 解决后才能进入 minimum v1 promotion-prep。✅

### 4. Missing Reason Attribution

Plan says missing reason 是 snapshot comparable projection gap，不是 value mismatch。

- `snapshot.jsonl` 验证：`manager_strategy_text` 记录 `value_present=true`, `anchor_present=true`, `comparable_values={}`。✅
- `score.json` `record_results` 中 `manager_strategy_text.strategy_summary` 和 `manager_strategy_text.market_outlook` status 为 `unavailable`，不是 `mismatch`。✅
- `quality_gate.json` FQ0 info 明确说"strict golden answer 部分字段超出 snapshot 可比合约"。✅
- 结论：plan 正确归因。✅

### 5. P1 Deferred Fields

Plan defers 10 P1 fields with owner "future fixture promotion or full-v1 coverage owner"。

- 10 个字段全部在 `score.json` 中 status=`unavailable`。✅
- 10 个字段全部属于 §7.3 P1 字段。✅
- 保守策略（defer P1）与 accepted controller judgment（`conditional_candidate_pending_partial_coverage_decision`）一致。✅
- Owner 赋值合理。✅

### 6. turnover_rate Handling

Plan says `turnover_rate` is outside current strict golden row set。

- `quality_gate.json` 确认 FQ2 warn for `turnover_rate` coverage/traceability，FQ2F warn for fund-level P1 failed field。✅
- `score.json` `record_results[]` 中 004393 无 `turnover_rate` comparable 或 unavailable row。✅
- `turnover_rate` 在 §7.3 为 P1 字段，但当前 score 的 correctness oracle 不包含 `turnover_rate` 的 004393 记录，因此 plan 正确将其归为 quality warning residual 而非 strict correctness comparable/unavailable row。✅
- Plan disposition `not_in_minimum_scope` 合理。✅

### 7. fixture_state and promotion_allowed

- `fixture-promotion-state-manifest-20260529.json` 确认 004393 `fixture_state=absent`, `promotion_allowed=false`。✅
- Plan 保持 `fixture_state=absent`, `promotion_allowed=false`，不改变。✅

### 8. Prohibited Files

Plan 禁止修改 `fund_agent/**`, `tests/**`, `scripts/**`, `reports/**`, golden answers, snapshots, manifests, `pyproject.toml`, `uv.lock`。这与 docs-only gate 性质一致，且与 `AGENTS.md` gate 分类规则和 `implementation-control.md` non-goals 一致。✅

### 9. Validation Matrix

Plan 只使用 `git diff --check` 和 `git diff --name-only` forbidden check，不运行 `ruff` / `pytest`。这对 docs-only gate 是合理的，因为没有 runtime 代码变更。✅

### 10. Next Gate Scope

Plan 的 next gate 是 `004393 P0 manager_strategy_text extractor projection / strict correctness rerun gate`。这个 gate 需要 runtime/snapshot projection 变更，但 plan 明确说"不授权"且"不命名 runtime files as allowed implementation targets"。Next gate 是独立 future gate，不 smuggle implementation 到当前 gate。✅

### 11. Conservative Default

Plan 默认 `reject_partial_coverage_for_minimum_v1_promotion_prep`。理由链：

- 9 matched 只证明已暴露 P0 子字段，不证明 `manager_strategy_text` 两个核心 P0。✅
- `coverage_scope=partially_covered` + FQ0 info 明确说 golden 超出 snapshot comparable contract。✅
- Root cause 是 projection gap 而非 mismatch，不能把 untested 子字段视为 correctness。✅
- `quality_gate.status=warn` + `fixture_state=absent` 保持 blocker。✅

保守默认与 accepted controller judgment 和 evidence 一致。✅

### 12. Fact Freeze Decision

Plan 说"no new reviewed fact freeze required"，因为 golden answer 已有 reviewed expected values。Stop conditions for future value changes 列出了 5 个具体触发条件。这与当前 golden answer 已存在 004393 的 21 条 reviewed records（包含 `manager_strategy_text` 两个子字段的期望值）一致。✅

---

## Findings

无 blocking findings。

无 non-blocking findings。

所有关键 claim 均由直接证据验证通过。

---

## Residual Risks

| Residual | Severity | Note |
|---|---|---|
| 未来 P0 projection gate 需要改变 snapshot projection 逻辑，可能涉及 extractor 或 snapshot service 代码变更 | info | Plan 已正确标注为 separate future gate，不授权于当前 gate |
| `turnover_rate` quality warn 仍缺少 owner timeline | info | Plan 记录为 quality residual with owner，但未绑定 timeline |
| Limited diagnostic-only alternative 依赖 controller 主动选择 | info | Plan 不推荐此选项作为默认，正确保守 |

---

## Conclusion

**PASS**

Plan `docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-20260529.md` is handoff-ready and evidence-based。Field counts verified correct; priority mapping uses §7.3; P0 mandatory fields correctly identified; missing reason correctly attributed to projection gap; P1 conservatively deferred; turnover_rate correctly outside strict golden row set; fixture_state absent preserved; prohibited file list comprehensive; validation matrix appropriate for docs-only gate; next gate minimal without smuggling implementation; conservative default well-justified.

---

Artifact: `docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-review-glm-20260529.md`
Conclusion: PASS
Self-check: pass
