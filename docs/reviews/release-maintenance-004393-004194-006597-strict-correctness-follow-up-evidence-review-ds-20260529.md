# 004393 / 004194 / 006597 Strict Correctness Follow-up Evidence Review — AgentDS

Date: 2026-05-29

Role: AgentDS，independent evidence/code reviewer。不是 controller，不做实现。

## Verdict

**PASS**

Implementation evidence 在所有可验证维度上与 plan、controller judgment、accepted plan reviews、rerun score 输出一致。006597 same-fund unavailable=11 经 score.json 逐条验证为真，stop condition 正确触发，无人核验、无 golden/fixture/manifest/code 变更，全部 promotion_allowed=false。

## Truth Sources Verified

| Source | Path | Status |
|---|---|---|
| Implementation evidence | `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md` | Read & verified |
| Machine-readable decision | `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json` | Parsed, validated |
| Accepted plan | `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md` | Cross-referenced |
| Plan review (DS) | `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md` | PASS |
| Plan review (MiMo) | `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md` | PASS |
| Controller judgment | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` | Cross-referenced |
| 006597 rerun score | `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json` | Parsed, record-level verified |
| 006597 rerun golden set | `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/golden_set.json` | Parsed |
| Git diff (golden/fixture/manifest) | `git diff -- reports/golden-answers docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | Empty |
| Git diff (code/runtime) | `git diff -- fund_agent tests scripts pyproject.toml uv.lock` | Empty |

## Finding 1: 006597 same-fund unavailable=11 — Verified Real

**Verdict: PASS**

score.json `correctness.record_results[]` 中 fund_code=006597 共 20 条记录，逐条验证：

| Status | Count | Verified |
|---|---|---|
| match | 9 | field_name + sub_field + expected_value + actual_value 逐一存在且一致 |
| unavailable | 11 | 每条有 non-null expected_value、null actual_value、reason 说明 snapshot 未显式暴露 |
| mismatch | 0 | 确认无 mismatch 记录 |

9 条 matched 子字段：`fund_name`, `fund_code`, `management_company`, `custodian`, `inception_date`, `benchmark_name`, `fund_type`, `nav_growth_rate`, `benchmark_return_rate`

11 条 unavailable 子字段：`investment_objective`, `style_positioning`, `strategy_summary`, `market_outlook`, `manager_holding`, `employee_holding`, `institutional_holder`, `individual_holder`, `beginning_share`, `ending_share`, `net_change`

每个 unavailable 记录的 expected_value 均为 non-null 具体值（如 `investment_objective` expected="在严格控制风险的前提下，追求稳健的投资回报。"），actual_value=null，reason="snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。"。

evidence doc 中列出的 9 matched + 11 unavailable 字段名与 score.json 完全一致。

## Finding 2: Stop Condition — Correctly Triggered, Manual Review NOT Performed

**Verdict: PASS**

Decision JSON 字段验证：

- `stop_condition_triggered: true`
- `manual_field_review_required: true`
- `manual_field_review_performed: false`

Implementation evidence 明确声明：worker 未执行人工核验、未编辑 golden answer、未编辑 fixtures、未编辑 manifests、未执行 promotion、未修改代码。

git diff 验证确认：reports/golden-answers 目录无变更；fixture-promotion-state-manifest 无变更；golden-readiness-residual-disposition-manifest 无变更；fund_agent / tests / scripts / pyproject.toml / uv.lock 均无变更。

与 plan 的 result handling rule（line 102-103）和 stop condition（line 155）一致：unavailable_records > 0 时只检查 same-fund 006597 unavailable records，不跨基金检查，不编辑 golden answer。

## Finding 3: 004393 Decision — 符合 Controller Judgment

**Verdict: PASS**

Controller judgment: `conditional_candidate_pending_partial_coverage_decision`

Follow-up decision: `not_minimum_v1_promotion_prep_by_default`

这是 conservative downgrade（从 pending 到 not-by-default），不是 upgrade。decision reason 明确指出：partial strict correctness coverage（9/150 comparable, P0 9/11, P1 0/10）不被接受为 minimum v1 promotion-prep。

`promotion_allowed=false`，`fixture_state=absent`。与 plan line 82-87 的 required decision 一致。

## Finding 4: 004194 Decision — 符合 Controller Judgment

**Verdict: PASS**

Controller judgment: `conditional_candidate_pending_p0_coverage_decision`

Follow-up decision: `index_profile_only_candidate_not_full_fixture_ready`

同样是 conservative clarification（明确 five `index_profile.*` records matched 不等于 full fixture readiness）。P0 strict correctness coverage=0。

`promotion_allowed=false`，`fixture_state=absent`。与 plan line 91-95 的 required decision 一致。

## Finding 5: 006597 Decision — blocked_pending, Bond Blocker Correctly Handled

**Verdict: PASS**

006597 decision: `blocked_pending_same_fund_unavailable_field_review`

bond_blocker 状态验证：
- `state: closed`，`classification: resolved_context`
- `active_blocker: false`
- `used_as_promotion_evidence: false`

bond blocker 未被用作 promotion evidence 或 strict correctness 替代，与 plan stop condition（line 153）一致。

## Finding 6: promotion_allowed=false — All Rows Verified

**Verdict: PASS**

| Entity | Field | Value |
|---|---|---|
| Decision JSON top-level | `promotion_allowed` | false |
| Decision JSON top-level | `promotion_manifest` | false |
| Decision JSON top-level | `not_promotion_manifest` | true |
| 004393 decision | `promotion_allowed` | false |
| 004194 decision | `promotion_allowed` | false |
| 006597 decision | `promotion_allowed` | false |
| Score JSON record_results | records with `promotion_allowed` | 0 |

## Finding 7: JSON Parseability

**Verdict: PASS**

| File | `python -m json.tool` |
|---|---|
| score.json | PASS |
| decision JSON | PASS |
| golden_set.json | PASS |

## Finding 8: No FQ0-FQ6 Semantic Modifications

**Verdict: PASS**

- Quality-gate rerun 在 plan 中标记为 optional read-only consistency check，实际未执行（`reports/quality-gate-runs/strict-correctness-follow-up-006597-2024-20260529/quality_gate.json` 不存在）。
- 无 FQ 语义变更风险。score rerun 使用 public CLI，未修改代码；quality gate 未 rerun；无 FQ0-FQ6 policy 变更。

## Finding 9: Evidence Doc / Decision JSON Cross-Consistency

**Verdict: PASS**

| Claim in evidence.md | Verified in decision.json / score.json |
|---|---|
| correctness.status=available | decision.json strict_correctness.status=available |
| total=150, comparable=9, matched=9, mismatched=0, unavailable=141 | All match score.json correctness section |
| same-fund 006597: match=9, unavailable=11, mismatch=0 | Confirmed by record-level enumeration |
| 9 matched fields listed | Match score.json match records exactly |
| 11 unavailable fields listed | Match score.json unavailable records exactly |
| golden_answer_modified=false | decision.json confirms |
| code_modified=false | decision.json + git diff confirm |
| promotion_allowed=false all rows | decision.json confirms |
| bond_blocker closed, not promotion evidence | decision.json confirms |

## Findings Summary

| # | Category | Finding | Verdict |
|---|---|---|---|
| F1 | 006597 unavailable=11 | score.json record-level verification confirms 9 match + 11 unavailable | PASS |
| F2 | Stop condition | Triggered correctly; manual review NOT performed; no mutation | PASS |
| F3 | 004393 decision | not_minimum_v1_promotion_prep_by_default; aligns with controller judgment | PASS |
| F4 | 004194 decision | index_profile_only_candidate_not_full_fixture_ready; aligns with controller judgment | PASS |
| F5 | 006597 decision | blocked_pending_same_fund_unavailable_field_review; bond blocker not misused | PASS |
| F6 | promotion_allowed=false | All 3 funds + top-level + score.json verified | PASS |
| F7 | JSON parseability | score.json, decision.json, golden_set.json all valid | PASS |
| F8 | FQ0-FQ6 semantics | No quality gate rerun; no FQ semantic changes | PASS |
| F9 | Cross-consistency | Evidence doc, decision JSON, score JSON mutually consistent | PASS |

## Required Fixes

无。

## Observations

1. Quality-gate rerun 未执行（optional per plan）。这不影响 evidence 完整性，因为 plan 明确 quality-gate rerun 只是 read-only consistency check，不参与 decision 推导。
2. golden_set.json 包含 6 只基金（含 004393, 006597, 001548 等），其中 004194 不在 golden_set 中。这与 decision JSON 中 004194 的 source_golden_set_path 指向 `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/golden_set.json`（原始 snapshot 的 golden set）一致，因为 004194 未参与本次 rerun。
3. Score JSON 中 record_results 的 priority 字段为 null（P?），这不影响 correctness 计算，但未来若需要按 priority 分解 same-fund unavailable 字段分布，可考虑填充。
