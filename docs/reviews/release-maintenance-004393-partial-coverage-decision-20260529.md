# 004393 Partial Coverage Decision

日期：2026-05-29

角色：AgentCodex implementation/evidence worker。本文是 Slice 1 docs-only decision artifact，不是 controller judgment，不启动 `$gateflow` / `/gateflow` / `phaseflow`，不授权 commit、push、PR、merge、release、golden promotion、fixture promotion 或进入其它 gate。

## Scope / Guardrails

当前 sub gate：Track 1 / `004393 partial coverage decision / expansion gate`。

Gate classification：`heavy`，因为本决策影响 baseline / golden promotion readiness；但本 Slice 只写 docs/control-plane artifact。

Accepted plan commit：`60be50f`。

Accepted plan artifact：`docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-20260529.md`。

Accepted plan reviews：`docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-review-mimo-20260529.md`；`docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-review-glm-20260529.md`。

本 gate 只裁决 `004393 / 2024` 当前 partial strict correctness coverage 是否足以进入 future minimum v1 promotion-prep。它不修改 runtime code、tests、reports、manifests、golden answer、fixtures、score、quality gate、snapshot、README、`pyproject.toml`、`uv.lock` 或 `docs/implementation-control.md`。

执行边界来自 `AGENTS.md`：heavy gate 覆盖 baseline/golden promotion 等高影响事项；`docs/implementation-control.md` 是 controller 后续更新入口；`docs/design.md` 是当前设计真源。`docs/design.md` §7.3 将 `manager_strategy_text` 归为 P0，§7.4 规定 P0/P1 quality gate 语义，并明确基准覆盖不足时应扩大 golden coverage 或降级为显式 residual risk，不能把少量 golden answer 误当全域正确性证明。

## Evidence Freeze

本决策读取并冻结以下证据；若未来 artifact 改变，必须开新 gate 重新裁决：

| Area | Evidence |
|---|---|
| Execution and design truth | `AGENTS.md`; `docs/design.md` §7.3 / §7.4; `docs/implementation-control.md` |
| Accepted current route | `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`; `docs/reviews/release-maintenance-phase-roadmap-consolidation-controller-judgment-20260529.md` |
| Accepted strict correctness predecessor | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md`; `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` |
| Preflight state | `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`; `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md` |
| Control-plane manifests | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`; `docs/reviews/fixture-promotion-state-manifest-20260529.json` |
| Manifest controller judgments | `docs/reviews/release-maintenance-golden-readiness-residual-disposition-controller-judgment-20260529.md`; `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md` |
| 004393 strict correctness artifacts | `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/snapshot.jsonl`; `score.json`; `score.md`; `quality_gate.json`; `quality_gate.md`; `golden_set.json` |
| Reviewed expected facts | `reports/golden-answers/golden-answer.json` 004393 rows |
| Accepted plan chain | `docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-20260529.md`; MiMo / GLM plan reviews |

No source evidence contradicts the accepted plan.

## Current 004393 Score / Preflight / Fixture State

| Evidence | Current value | Source |
|---|---|---|
| Score-wide correctness | `coverage_scope=partially_covered`; `total_records=150`; `comparable_records=9`; `matched_records=9`; `mismatched_records=0`; `unavailable_records=141`; `accuracy_rate=1.0` | `score.json` / `score.md` |
| Same-fund 004393 strict golden rows | 21 rows in `reports/golden-answers/golden-answer.json`; score has 9 matched and 12 unavailable for `fund_code=004393` | `golden-answer.json`; `score.json` |
| Same-fund P0 coverage | 9 matched / 11 total; missing P0 rows are `manager_strategy_text.strategy_summary` and `manager_strategy_text.market_outlook` | `score.json`; `docs/design.md` §7.3 |
| Same-fund P1 coverage | 0 matched / 10 total; P1 unavailable rows are `product_profile.*`, `manager_alignment.*`, `holder_structure.*`, `share_change.*` | `score.json`; `docs/design.md` §7.3 |
| Missing reason | `snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。` | `score.json` |
| Snapshot projection state | `product_profile`, `manager_strategy_text`, `manager_alignment`, `holder_structure`, and `share_change` all have `value_present=true`, `anchor_present=true`, `comparable_values={}` | `snapshot.jsonl` |
| Quality gate | `status=warn`; issues are FQ2/FQ2F warn for `turnover_rate` and FQ0 info that strict golden fields exceed the snapshot comparable contract | `quality_gate.json`; `quality_gate.md` |
| Preflight | `overall_status=block`; `004393` readiness=`deferred_with_owner`, quality=`warn`, strict_golden=`covered`, fixture=`absent`, disposition=`include_for_later_review` | `golden_readiness_preflight.json` / `.md` |
| Fixture manifest | `fixture_state=absent`; `promotion_allowed=false`; blocker=`fixture_promotion_absent`; `blocks_minimum_v1=true` | `fixture-promotion-state-manifest-20260529.json` |
| Upstream controller state | `004393` is `conditional_candidate_pending_partial_coverage_decision`; next gate is partial coverage decision / strict golden fixture promotion review | strict golden correctness controller judgment |

## 9 Matched Fields Table

All 9 matched fields are P0 by `docs/design.md` §7.3.

| Field | Subfield | Priority | Score status | Evidence source |
|---|---|---|---|---|
| `basic_identity` | `fund_name` | P0 | match | `年报2024 §2 page-5 page-5-table-0 fund_name` |
| `basic_identity` | `fund_code` | P0 | match | `年报2024 §2 page-5 page-5-table-0 fund_code` |
| `basic_identity` | `management_company` | P0 | match | `年报2024 §2 page-5 page-5-table-0 management_company` |
| `basic_identity` | `custodian` | P0 | match | `年报2024 §2 page-5 page-5-table-0 custodian` |
| `basic_identity` | `inception_date` | P0 | match | `年报2024 §2 page-5 page-5-table-0 inception_date` |
| `benchmark` | `benchmark_name` | P0 | match | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `classified_fund_type` | `fund_type` | P0 | match | `年报2024 §2 page-5 page-5-table-0 fund_name` |
| `nav_benchmark_performance` | `nav_growth_rate` | P0 | match | `年报2024 §3 page-8 page-8-table-0 nav_growth_rate` |
| `nav_benchmark_performance` | `benchmark_return_rate` | P0 | match | `年报2024 §3 page-8 page-8-table-0 benchmark_return_rate` |

These matches prove only currently comparable P0 fields. They do not verify the two P0 `manager_strategy_text` subfields already present in reviewed golden answer.

## Unavailable P0 / P1 Field Disposition Matrix

| Field | Subfield | Priority | Minimum v1 strict correctness disposition | Missing cause |
|---|---|---|---|---|
| `manager_strategy_text` | `strategy_summary` | P0 | `needs_extractor_projection_gate` | Snapshot has `manager_strategy_text` value and anchor, but `comparable_values={}`; score says the golden subfield is not explicitly exposed. |
| `manager_strategy_text` | `market_outlook` | P0 | `needs_extractor_projection_gate` | Same projection gap; reviewed source anchor exists as `年报2024 §4 market_outlook`, but score cannot compare it. |
| `product_profile` | `investment_objective` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `product_profile` | `style_positioning` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `product_profile` | `investment_scope` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `manager_alignment` | `manager_holding` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `manager_alignment` | `employee_holding` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `holder_structure` | `institutional_holder` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `holder_structure` | `individual_holder` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `share_change` | `beginning_share` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `share_change` | `ending_share` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `share_change` | `net_change` | P1 | `defer_from_minimum_v1` | Snapshot has field-level value/anchor but no comparable subfield. |
| `turnover_rate` | not in current 004393 golden rows | P1 | `not_in_minimum_scope` for this decision | Quality gate warns coverage/traceability is 0%, but it is outside the current 004393 strict golden row set. |

P1 `defer_from_minimum_v1` means not mandatory for this minimum v1 strict-correctness decision by default. It is not a readiness claim; these rows remain full-v1 / future coverage owner residuals.

## Missing Cause Classification

Root cause：snapshot comparable projection gap.

Evidence chain:

- `score.json` marks the two P0 `manager_strategy_text` rows and ten P1 rows as `unavailable`, not `mismatch`.
- Every unavailable same-fund 004393 row uses the reason `snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。`
- `snapshot.jsonl` shows field-level `value_present=true` and `anchor_present=true` for affected field groups, but `comparable_values={}`.
- `quality_gate.md` FQ0 says current strict golden answer fields exceed the snapshot comparable contract and `coverage_scope=partially_covered`.

Therefore the issue is not disproven facts and not a normalization mismatch. It is that reviewed golden subfields are not projected into comparable snapshot values.

## Reviewed Fact Freeze Decision

No new fact freeze is required for this docs-only decision. The 004393 golden-answer rows already contain reviewed expected values and source anchors, including both P0 `manager_strategy_text.strategy_summary` and `manager_strategy_text.market_outlook`.

A future P0 projection gate may reuse the existing reviewed facts only if it exposes the existing values as comparable snapshot subfields without changing, splitting, summarizing, normalizing beyond current strict comparison semantics, rewording, or adding rows.

Future work must stop and require `needs_fact_freeze` if it needs to:

- change expected golden values;
- split or materially rewrite `manager_strategy_text` values;
- add new 004393 golden rows;
- change source anchors;
- resolve a conflict between extracted raw text and reviewed golden answer;
- alter the identity key semantics of `fund_code + report_year + field_name + sub_field`.

## Coverage Expansion Next Gate

Coverage expansion is required before 004393 can enter future minimum v1 promotion-prep, but it is not authorized in this gate.

Next gate：`004393 P0 manager_strategy_text extractor projection / strict correctness rerun gate`.

Minimum future gate content:

1. Expose reviewed `manager_strategy_text.strategy_summary` and `manager_strategy_text.market_outlook` as comparable snapshot subfields, if code ownership and tests support that route.
2. Rerun the necessary 004393 snapshot / score / quality artifacts under that future gate.
3. Review strict correctness output for the two P0 rows and any unintended regression.
4. Decide whether P1 rows stay deferred or need expansion before promotion-prep.

That future gate may need runtime or snapshot projection changes. This decision does not authorize them and does not name runtime files as allowed targets.

## Final Accepted Decision Candidate

Decision candidate for controller review:

| Key | Value |
|---|---|
| `decision` | `reject_partial_coverage_for_minimum_v1_promotion_prep` |
| `fund_code` | `004393` |
| `report_year` | `2024` |
| `fixture_state_after_gate` | `absent` |
| `promotion_allowed` | `false` |
| `minimum_v1_promotion_prep_ready` | `false` |
| `required_before_future_minimum_v1_promotion_prep` | P0 `manager_strategy_text.strategy_summary`; P0 `manager_strategy_text.market_outlook` |
| `required_p0_disposition` | `needs_extractor_projection_gate` |
| `default_p1_disposition` | `defer_from_minimum_v1` |
| `turnover_rate_disposition` | `not_in_minimum_scope` for this decision |
| `missing_cause` | `snapshot_comparable_projection_gap` |
| `fact_freeze_required_now` | `false` |
| `next_gate` | `004393 P0 manager_strategy_text extractor projection / strict correctness rerun gate` |

Rationale：9 matched rows prove only currently exposed P0 subfields. They do not verify two P0 `manager_strategy_text` rows that are already in reviewed golden answer and are mandatory by `docs/design.md` §7.3 priority before any future minimum v1 promotion-prep. Treating `9/150` score-wide comparable and P0 `9/11` as promotion-prep-ready would convert untested reviewed subfields into assumed correctness.

## Non-Goals And Forbidden Changes

This gate did not and must not:

- modify `docs/implementation-control.md`; controller will update it later if this decision is accepted;
- modify `fund_agent/**`, `tests/**`, `scripts/**`, `reports/**`, golden answers, golden fixtures, score, quality gate, snapshot, preflight outputs, manifests, `pyproject.toml`, `uv.lock`, README files, or unrelated untracked files;
- run or claim runtime validation;
- set `promotion_allowed=true`;
- change fixture state from `absent`;
- weaken FQ0-FQ6, strict golden correctness, score policy, or quality gate semantics;
- treat `turnover_rate` warning as current strict golden row evidence;
- restart QDII probing, enter FOF taxonomy, touch `004194` / `006597` follow-up scope, or begin release readiness;
- commit, push, PR, merge, release, promote, or enter another gate.

Self-check: pass for docs-only decision scope.
