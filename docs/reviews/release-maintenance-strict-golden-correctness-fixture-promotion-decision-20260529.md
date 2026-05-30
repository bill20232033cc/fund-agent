# Strict Golden Correctness / Fixture Promotion Decision

日期：2026-05-29

角色：AgentCodex implementation/evidence worker；不是 controller。本 artifact 只记录 docs-only decision evidence，不执行 promotion，不修改 golden answer / fixture / score / quality / snapshot / preflight / runtime，不提交。

## Scope

- 当前 gate：`strict golden correctness / fixture promotion gate`
- gate classification：`heavy`
- plan：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md`
- plan re-review：`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-rereview-mimo-20260529.md`；`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-rereview-ds-20260529.md`
- row universe：`docs/reviews/fixture-promotion-state-manifest-20260529.json` 的 10 个 entries

本 gate 不更新 fixture state manifest。Candidate 语义只写在本 decision artifact 的 `decision` 字段；所有 row 均保持 `promotion_allowed=false`，且 `fixture_state_after_gate` 只复述 accepted manifest 现状。

## Strict Correctness Field Paths

本 decision 使用两个独立维度，禁止把二者混作同一证据：

- fund-level membership：preflight row / fixture manifest 的 `strict_golden_coverage`
- score-level field comparability：各 `source_score_path` 的 `correctness.coverage_scope`、`correctness.total_records`、`correctness.comparable_records`、`correctness.matched_records`、`correctness.mismatched_records`、`correctness.unavailable_records`、`correctness.record_results[]`

当两个维度不一致时，score-level field comparability 是 strict correctness 主证据；fund-level `fund_not_covered` 仍是 hard blocker。

`coverage_scope=covered` 只表示当前 `comparable_records` 全部 matched 且无 mismatch，不表示 `total_records` 的大部分已验证；必须同时读取 `comparable_records`、`unavailable_records` 和 `record_results[]` 的 fund/field 分布。

## Decision Table

| fund_or_slot | year | decision | fixture_state_after_gate | promotion_allowed | fund_level_membership | score_level_field_comparability | quality_status | blockers | accepted_residuals / missing_evidence | owner | next_gate |
|---|---:|---|---|---|---|---|---|---|---|---|---|
| `004393` | 2024 | `conditional_candidate_pending_partial_coverage_decision` | `absent` | `false` | `covered` | `partially_covered`; `total_records=150`; `comparable_records=9`; `matched_records=9`; `mismatched_records=0`; `unavailable_records=141` | `warn` | `fixture_promotion_absent`; partial coverage not accepted | P0/P1/P2 breakdown below；no automatic upgrade；`turnover_rate` warn owner required | future fixture promotion gate | partial coverage decision / strict golden fixture promotion review gate |
| `004194` | 2024 | `conditional_candidate_pending_p0_coverage_decision` | `absent` | `false` | `covered` | `covered`; `total_records=150`; `comparable_records=5`; `matched_records=5`; `mismatched_records=0`; `unavailable_records=145`; comparable scope is index_profile-only; P0 strict correctness coverage is 0 | `warn` | `fixture_promotion_absent`; P0 strict correctness coverage not established | conditional candidate only；not promoted；`coverage_scope=covered` means 5/5 comparable records matched, not broad correctness coverage；tracking_error requires P15 reviewed direct observed disclosure before production golden rows；turnover_rate warn owner required | future fixture promotion gate + baseline preflight owner；P15 tracking-error evidence owner；P0 coverage decision owner | future strict golden fixture promotion review / P0 strict correctness coverage decision / P15 tracking-error evidence gate |
| `006597` | 2024 | `needs_future_gate` | `absent` | `false` | `covered` | `not_configured`; `total_records=0`; `comparable_records=0`; `matched_records=0`; `mismatched_records=0`; `unavailable_records=0` | `warn` | `strict_golden_not_configured`; `fixture_promotion_absent` | bond blocker is resolved context only；must rerun score with `reports/golden-answers/golden-answer.json` and then evaluate correctness coverage/matches | future fixture promotion gate + future baseline/golden preflight owner | strict golden correctness score rerun / fixture promotion gate |
| `017641` | 2024 | `deferred_from_minimum_v1` | `deferred_from_v1` | `false` | `fund_not_covered` | `not_configured` | `block` | `strict_golden_not_configured`; `quality_gate_block`; `strict_golden_fund_not_covered`; `fixture_promotion_absent` | source provenance complete but P0 `manager_strategy_text` blocks；accepted disposition remains replace / not promotion | future QDII diagnosis / replacement owner | QDII diagnosis or explicit deferred-from-v1 gate |
| `096001` | 2024 | `deferred_from_minimum_v1` | `deferred_from_v1` | `false` | `fund_not_covered` | `not_configured` | `block` | `strict_golden_not_configured`; `quality_gate_block`; `strict_golden_fund_not_covered`; `fixture_promotion_absent`; `qdii_coverage_blocked` | QDII hard stop；quality block after eligible provenance；no new probing | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate |
| `040046` | 2024 | `deferred_from_minimum_v1` | `deferred_from_v1` | `false` | `fund_not_covered` | `not_configured` | `block` | `strict_golden_not_configured`; `quality_gate_block`; `strict_golden_fund_not_covered`; `fixture_promotion_absent`; `qdii_coverage_blocked` | QDII hard stop；quality block after eligible provenance；no new probing | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate |
| `019172` | 2024 | `deferred_from_minimum_v1` | `deferred_from_v1` | `false` | `fund_not_covered` | `not_configured` | `block` | `strict_golden_not_configured`; `quality_gate_block`; `strict_golden_fund_not_covered`; `fixture_promotion_absent`; `qdii_coverage_blocked` | QDII hard stop；P0 `manager_strategy_text` blocks；no new probing | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate |
| `021539` | 2024 | `deferred_from_minimum_v1` | `deferred_from_v1` | `false` | `fund_not_covered` | `not_configured` | `block` | `strict_golden_not_configured`; `quality_gate_block`; `strict_golden_fund_not_covered`; `fixture_promotion_absent`; `qdii_coverage_blocked` | QDII hard stop；quality block after eligible provenance；no new probing | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate |
| `FOF_SLOT` | 2024 | `deferred_from_minimum_v1` | `deferred_from_v1` | `false` | `not_applicable` | `not_evaluated` | `not_evaluated` | `fof_taxonomy_pending`; `fof_data_gap` | source paths remain null；requires repository-verified pure FOF candidate；QDII-FOF cannot count | future FOF taxonomy / pure FOF candidate gate | pure FOF repository-verified candidate gate |
| `110020` | 2024 | `deferred_from_minimum_v1` | `deferred_from_v1` | `false` | `fund_not_covered` | `not_configured` | `warn` | `strict_golden_not_configured`; `strict_golden_fund_not_covered`; `fixture_promotion_absent`; `reviewed_candidate_not_promoted`; `index_evidence_insufficient` | hard blocker is fund-level `fund_not_covered`, unlike 006597 rerunnable `not_configured`; needs reviewed fact freeze, methodology / constituents evidence, strict golden fund-level coverage and score-level correctness | future index evidence sufficiency gate | index reviewed fact freeze / methodology / constituents evidence gate |

## 004393 Partial Coverage Breakdown

Source：`reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json` → `correctness.record_results[]`。

Priority classification source：`docs/design.md` §7.3 defines `extraction_score` field priorities and §7.4 defines quality-gate severity semantics for P0/P1 fields; the code implementation source named there is `fund_agent/fund/extraction_score.py`.

Score-wide result is `9/150` comparable. Row-scoped to `fund_code=004393`, the breakdown is:

| priority | total | comparable | matched | mismatched | unavailable | unavailable fields |
|---|---:|---:|---:|---:|---:|---|
| P0 | 11 | 9 | 9 | 0 | 2 | `manager_strategy_text.market_outlook`; `manager_strategy_text.strategy_summary` |
| P1 | 10 | 0 | 0 | 0 | 10 | `holder_structure.individual_holder`; `holder_structure.institutional_holder`; `manager_alignment.employee_holding`; `manager_alignment.manager_holding`; `product_profile.investment_objective`; `product_profile.investment_scope`; `product_profile.style_positioning`; `share_change.beginning_share`; `share_change.ending_share`; `share_change.net_change` |
| P2 | 0 | 0 | 0 | 0 | 0 | none |

Conclusion：004393 is not upgraded automatically. The row may only move beyond `conditional_candidate_pending_partial_coverage_decision` after controller accepts this partial coverage risk and records owner / next gate for the remaining P0/P1 unavailable fields.

## 004194 Covered Scope Breakdown

Source：`reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json` → `correctness.record_results[]`。

Priority classification source：same as above, `docs/design.md` §7.3 / §7.4 and the referenced `fund_agent/fund/extraction_score.py`. Under that source, `index_profile` is a conditional P1 field for index / enhanced-index funds, while P0 fields are `basic_identity`, `classified_fund_type`, `benchmark`, `nav_benchmark_performance`, `fee_schedule`, and `manager_strategy_text`.

Score-wide result is `5/150` comparable. Row-scoped to `fund_code=004194`, the breakdown is:

| priority | total | comparable | matched | mismatched | intra-fund unavailable | fields |
|---|---:|---:|---:|---:|---:|---|
| P0 | 0 | 0 | 0 | 0 | 0 | none comparable in this run |
| P1 | 5 | 5 | 5 | 0 | 0 | `index_profile.benchmark_text`; `index_profile.benchmark_identity_status`; `index_profile.methodology_availability`; `index_profile.constituents_availability`; `index_profile.source_tier` |
| P2 | 0 | 0 | 0 | 0 | 0 | none |

The score-level `unavailable_records=145` are all cross-fund `fund_code=004393` golden records in this score run, not 004194 intra-fund missing fields. Therefore 004194 has `intra_fund_unavailable=0`, but its strict correctness evidence covers only 5 `index_profile.*` fields and covers no P0 field. This is weaker than broad production golden readiness; the conservative decision is `conditional_candidate_pending_p0_coverage_decision`, not an unconditional `promotion_prep_ready_candidate`.

## Quality Issues

Source paths are each row's `source_quality_gate_path`.

- `004393`: status `warn`; issues are P1 `turnover_rate` coverage/traceability warn, fund-level P1 failed field summary for `turnover_rate`, and info that strict golden answer contains fields outside snapshot comparable contract.
- `004194`: status `warn`; issues are P1 `tracking_error` warn, P1 `turnover_rate` warn, and fund-level P1 failed field summary. `tracking_error` remains under the P15 direct-disclosure evidence constraint before production golden rows.
- `006597`: status `warn`; issues are P1 `turnover_rate`, `holder_structure`, `share_change`, fund-level P1 failed field summary, strict golden answer not configured info, and high snapshot missing-rate warn. No `bond_risk_evidence_missing` quality issue appears in the latest artifact.
- `017641`: status `block`; P0 `manager_strategy_text` coverage/traceability and evidence-anchor blockers, plus P1 `turnover_rate` / `holdings_snapshot` warns and high missing-rate warn.
- `096001`: status `block`; P0 `nav_benchmark_performance` coverage/traceability and evidence-anchor blockers, P1 warns for `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`, and missing-rate block.
- `040046`: status `block`; P1 warns for `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`, and missing-rate block.
- `019172`: status `block`; P0 `manager_strategy_text` coverage/traceability and evidence-anchor blockers, P1 warns for `turnover_rate`, `holdings_snapshot`, `share_change`, and missing-rate block.
- `021539`: status `block`; P1 warns for `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`, and missing-rate block.
- `FOF_SLOT`: no source quality artifact; status `not_evaluated`.
- `110020`: status `warn`; issues are P1 `turnover_rate` warn, fund-level P1 failed field summary, and strict golden answer not configured info.

## Evidence Paths

Common gate evidence:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-review-mimo-20260529.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-review-ds-20260529.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-rereview-mimo-20260529.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-rereview-ds-20260529.md`
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md`

Per-row source artifacts:

- `004393`: `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/snapshot.jsonl`; `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json`; `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/quality_gate.json`; `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/golden_set.json`
- `004194`: `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/snapshot.jsonl`; `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json`; `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/quality_gate.json`; `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/golden_set.json`
- `006597`: `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`; `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`; `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`
- `017641`: `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/snapshot.jsonl`; `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/score.json`; `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/quality_gate.json`; `reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527/golden_set.json`
- `096001`: `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/snapshot.jsonl`; `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/score.json`; `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/quality_gate.json`; `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/golden_set.json`
- `040046`: `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/snapshot.jsonl`; `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.json`; `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/quality_gate.json`; `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/golden_set.json`
- `019172`: `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/snapshot.jsonl`; `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/score.json`; `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/quality_gate.json`; `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/golden_set.json`
- `021539`: `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/snapshot.jsonl`; `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/score.json`; `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/quality_gate.json`; `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/golden_set.json`
- `FOF_SLOT`: no source artifacts; paths remain null in fixture manifest
- `110020`: `reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/snapshot.jsonl`; `reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/score.json`; `reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/quality_gate.json`; `reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/golden_set.json`

## Final Decision

- `004194` is a decision-only `conditional_candidate_pending_p0_coverage_decision`; `fixture_state_after_gate=absent`; `promotion_allowed=false`; no promotion is authorized. Its `coverage_scope=covered` only means the 5 comparable `index_profile.*` records all matched. It does not mean broad strict correctness coverage: P0 strict correctness coverage is 0, and the 145 unavailable records are cross-fund 004393 golden records rather than 004194 intra-fund unavailable fields.
- `004393` is `conditional_candidate_pending_partial_coverage_decision`; it has P0/P1/P2 breakdown but no automatic upgrade.
- `006597` is `needs_future_gate`; bond risk evidence blocker remains closed as resolved context, but score-level strict correctness is `not_configured` until a rerun with `reports/golden-answers/golden-answer.json`.
- `017641`, QDII rows, `FOF_SLOT`, and `110020` remain deferred/blocked for the reasons in the table.
- No runtime/preflight/manifest/schema/golden fixture/score/quality/snapshot change occurred.
