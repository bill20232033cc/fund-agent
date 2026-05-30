# 004194 P0 Coverage / Index Profile-Only Fixture Decision

日期：2026-05-29

角色：AgentCodex implementation/evidence worker。本文是 Slice 1 docs-only decision artifact，不是 controller judgment，不启动 `$gateflow` / `/gateflow` / `phaseflow`，不授权 commit、push、PR、merge、release、golden promotion、fixture promotion 或进入其它 gate。

## Scope / Guardrails

当前 sub gate：Track 1 / `004194 P0 coverage or index_profile-only fixture decision gate`。

Gate classification：`heavy`。原因是本决策影响 baseline / golden / fixture promotion readiness；但本 Slice 只写 docs/control-plane artifact。

Accepted plan commit：`214eaa4`。

Accepted plan artifact：`docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md`。

Accepted plan reviews：`docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-review-mimo-20260529.md`；`docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-review-glm-20260529.md`。MiMo verdict 为 `PASS`；GLM verdict 为 `PASS_WITH_FINDINGS`。本 artifact 接受 GLM F1 作为措辞约束：不得写成 P16-S2 添加或接受 golden rows；精确 provenance 是 P16-S1 接受 `index_profile` benchmark-context concept，P16-S2 在 golden-row edits 前被阻断，现有 004194 golden-answer `index_profile` rows 通过当前 scoring 验证。

本 gate 只裁决 `004194 / 2024` 在当前 strict golden correctness 证据下能否进入 full fixture promotion-prep，或是否只能作为 `index_profile-only` bounded diagnostic / specialized candidate。它不修改 runtime code、tests、reports、manifests、golden answer、fixtures、score、quality gate、snapshot、README、`pyproject.toml`、`uv.lock` 或 `docs/implementation-control.md`。

执行边界来自 `AGENTS.md`：baseline/golden promotion 属于 high-impact heavy gate；当前架构边界仍是 `UI -> Service -> Host -> Agent`，当前确定性路径为 UI -> Service -> `fund_agent/fund`；年报生产访问必须经过 `FundDocumentRepository`；不得用少量可比 golden rows 证明全域正确性。`docs/design.md` §7.3 将 P0 字段定义为 `basic_identity`, `classified_fund_type`, `benchmark`, `nav_benchmark_performance`, `fee_schedule`, `manager_strategy_text`，并将 `index_profile` 与 `tracking_error` 定义为指数 / 指数增强基金条件 P1。`docs/design.md` §7.4 明确基准覆盖不足时应扩大 golden coverage 或降级为显式 residual risk，且 `tracking_error` 生产 golden rows 只有在 reviewed direct observed disclosure evidence 被接受后才能添加。

## Evidence Freeze

本决策读取并冻结以下证据；若未来 artifact、score、golden answer 或 manifest 改变，必须开新 gate 重新裁决：

| Area | Evidence |
|---|---|
| Execution and design truth | `AGENTS.md`; `docs/design.md` §7.3 / §7.4; `docs/implementation-control.md` |
| Accepted current route | `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`; `docs/reviews/release-maintenance-phase-roadmap-consolidation-controller-judgment-20260529.md` |
| Previous route state | `docs/reviews/release-maintenance-004393-partial-coverage-decision-controller-judgment-20260529.md` |
| Accepted strict correctness predecessor | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md`; `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` |
| Current accepted plan chain | `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md`; MiMo / GLM plan reviews |
| Preflight state | `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`; `.md` |
| Control-plane manifests | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`; `docs/reviews/fixture-promotion-state-manifest-20260529.json` |
| 004194 strict correctness artifacts | `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/snapshot.jsonl`; `score.json`; `score.md`; `quality_gate.json`; `quality_gate.md`; `golden_set.json` |
| Reviewed expected rows | `reports/golden-answers/golden-answer.json` 004194 rows |
| P15 / P16 provenance | `docs/reviews/p15-s1a-code-review-controller-judgment-20260522.md`; `docs/reviews/p15-s1a-tracking-error-source-contract-evidence-acquisition-plan-20260522.md`; `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md`; `docs/reviews/p16-s2-code-review-controller-judgment-20260522.md`; `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md` |

No source evidence contradicts the accepted plan. The controlling evidence supports a conservative docs-only decision: no full fixture readiness, no promotion, and no `tracking_error` production golden rows.

## Current 004194 Score / Preflight / Fixture State

| Evidence | Current value | Source |
|---|---|---|
| Fund / year | `004194 / 2024` | `snapshot.jsonl`; preflight JSON |
| Fund name | `招商中证1000指数增强A` | preflight JSON |
| App category | `国内股票类` | preflight JSON |
| Classified fund type | `enhanced_index` | `snapshot.jsonl`; preflight JSON |
| Score correctness | `coverage_scope=covered`; `total_records=150`; `comparable_records=5`; `matched_records=5`; `mismatched_records=0`; `unavailable_records=145` | `score.json`; `score.md` |
| Same-fund comparable rows | Exactly five rows, all `index_profile.*`, all `status=match` | `score.json`; `score.md` |
| Same-fund P0 strict correctness coverage | `0` comparable P0 rows; no 004194 P0 golden rows exist in current strict golden scope | `score.json`; `reports/golden-answers/golden-answer.json`; `docs/design.md` §7.3 |
| Golden-answer 004194 rows | Exactly five rows: `benchmark_text`, `benchmark_identity_status`, `methodology_availability`, `constituents_availability`, `source_tier` under `index_profile` | `reports/golden-answers/golden-answer.json` |
| Snapshot `index_profile` | `value_present=true`; `anchor_present=true`; comparable values contain the five scalar rows; note says benchmark context only and not methodology / constituents evidence | `snapshot.jsonl` |
| Snapshot P0-capable fields | `basic_identity`, `benchmark`, `classified_fund_type`, `nav_benchmark_performance`, `fee_schedule`, and `manager_strategy_text` are not verified by 004194 golden rows in this run | `snapshot.jsonl`; `score.json`; `golden-answer.json` |
| Snapshot `tracking_error` | `extraction_mode=missing`; `value_present=false`; `anchor_present=false`; note=`tracking_error_unparseable` | `snapshot.jsonl` |
| Snapshot `turnover_rate` | `extraction_mode=missing`; `value_present=false`; `anchor_present=false`; note=`§8 未披露可规则化抽取的换手率` | `snapshot.jsonl` |
| Quality gate | `status=warn`; issues are FQ2 warn for P1 `tracking_error`, FQ2 warn for P1 `turnover_rate`, and FQ2F fund-level P1 failed fields; no FQ1 mismatch/block | `quality_gate.json`; `quality_gate.md` |
| Preflight | `overall_status=block`; 004194 readiness=`deferred_with_owner`; `quality_gate_status=warn`; `strict_golden_coverage=covered`; `fixture_promotion_state=absent`; blocker=`fixture_promotion_absent` | preflight JSON / MD |
| Fixture manifest | `fixture_state=absent`; `promotion_allowed=false`; `blocks_minimum_v1=true`; `blocks_v1=true` | `fixture-promotion-state-manifest-20260529.json` |
| Upstream route state | 004194 was `conditional_candidate_pending_p0_coverage_decision`; next gate was P0 strict correctness coverage decision / P15 tracking-error evidence gate | strict correctness controller judgment |

The score-level `unavailable_records=145` are unavailable records from the broader golden-answer scope, not 004194 intra-fund missing P0 rows. The key 004194 blocker is different: current 004194 strict correctness coverage contains no P0 golden rows.

## 5 Matched Index Profile Rows Table

All five matched rows are conditional P1 `index_profile` rows by `docs/design.md` §7.3 because 004194 is an `enhanced_index` fund.

| Field | Subfield | Priority | Expected value | Score status | Evidence source |
|---|---|---|---|---|---|
| `index_profile` | `benchmark_text` | conditional P1 | `中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%` | match | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `benchmark_identity_status` | conditional P1 | `composite` | match | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `methodology_availability` | conditional P1 | `benchmark_only` | match | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `constituents_availability` | conditional P1 | `benchmark_only` | match | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `index_profile` | `source_tier` | conditional P1 | `benchmark_context` | match | `年报2024 §2 page-5 page-5-table-1 benchmark` |

These rows validate only benchmark-context `index_profile` scalar behavior. `methodology_availability=benchmark_only` and `constituents_availability=benchmark_only` are absence / limitation markers, not proof of index methodology detail or constituents detail.

## P0 Coverage Decision

Decision：P0 strict correctness coverage is `0`, and full 004194 fixture promotion-prep is blocked.

Rationale:

- `docs/design.md` §7.3 defines P0 fields as `basic_identity`, `classified_fund_type`, `benchmark`, `nav_benchmark_performance`, `fee_schedule`, and `manager_strategy_text`.
- `reports/golden-answers/golden-answer.json` has exactly five 004194 rows, all `index_profile.*`; it has no 004194 P0 rows.
- `score.json` confirms the only 004194 comparable records are those same five `index_profile.*` rows.
- A full fixture would imply correctness coverage for product identity, benchmark, fund type, NAV/benchmark performance, fees, manager strategy text, and downstream full-report readiness. Current strict scoring verifies none of those P0 rows for 004194.

Therefore:

| Decision field | Value |
|---|---|
| `minimum_v1_full_fixture_promotion_prep_ready` | `false` |
| `fixture_state_after_gate` | `absent` |
| `promotion_allowed` | `false` |
| `promotion_manifest` | `false` |
| `minimum_v1_full_fixture_promotion_prep_blocker` | `P0 strict correctness coverage=0` |

`coverage_scope=covered` must be interpreted narrowly: it means the five comparable rows matched. It does not mean 004194 has broad correctness coverage or fixture readiness.

## Index Profile-Only Candidate Limitations

`index_profile_only_specialized_candidate_allowed=true` only as a bounded diagnostic / specialized candidate. It is not a full fixture, not promotion-prep-ready, and not ready for future promotion.

Allowed scope:

- Candidate name must remain `index_profile-only`, `diagnostic`, or `specialized`.
- It covers exactly five rows: `index_profile.benchmark_text`, `index_profile.benchmark_identity_status`, `index_profile.methodology_availability`, `index_profile.constituents_availability`, `index_profile.source_tier`.
- It is scoped to benchmark-context evidence from annual report §2, page-5 table-1.
- It may validate current extractor / golden correctness behavior for the five scalar benchmark-context rows only.
- It preserves `fixture_state=absent`, `promotion_allowed=false`, and `promotion_manifest=false`.

Explicit limitations:

- It does not satisfy P0 strict correctness.
- It does not satisfy `tracking_error`.
- It does not prove methodology detail, constituents detail, performance, cost, manager, turnover, holdings, shareholder, or final judgment readiness.
- It does not modify preflight, fixture manifest, residual manifest, score, quality gate, snapshot projection, golden-answer JSON, or reports.
- It does not authorize a minimum-v1 full fixture promotion-prep decision.

P16 provenance must remain precise: P16-S1 accepted the `index_profile` benchmark-context concept and evidence classification; P16-S2 was blocked before golden-row edits; the current five 004194 golden-answer rows are existing rows verified by current scoring, not rows newly added or accepted by P16-S2.

## Tracking Error / P15 Decision

Decision：`tracking_error_production_golden_allowed=false` until P15-style reviewed direct observed disclosure evidence is accepted.

Evidence:

- `docs/design.md` §7.4 states that `tracking_error` production golden rows can only be added after reviewed direct observed disclosure evidence is accepted.
- P15-S1A controller judgment accepted `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` for the reviewed evidence path and kept production `tracking_error` golden rows blocked.
- P16-S1 evidence for the five enhanced-index candidates, including `004194`, classified `004194` as `blocked_no_direct_tracking_error`: available mentions were target/limit text or manager narrative, not observed tracking-error values.
- Current 004194 snapshot has `tracking_error` missing with `note=tracking_error_unparseable` and no anchor.
- Current quality gate warns on P1 `tracking_error`.

Implications:

- No `tracking_error` production row may be added from target/limit text, manager narrative, benchmark-only text, standard-deviation-only text, ambiguous text, unparseable text, or calculated values.
- The current five `index_profile` rows do not require accepted `tracking_error` evidence to remain matched, but their existence cannot weaken the P15 prerequisite.
- Future `tracking_error` work must first produce reviewed direct observed disclosure evidence with complete source anchors before any separate golden implementation gate.

## Field Disposition Matrix

Disposition categories:

- `fix_now`：只允许本 gate 的 docs-only decision artifact 和 implementation evidence artifact。
- `defer_from_minimum_v1`：当前 minimum-v1 diagnostic candidate 不要求；仍是 full-v1 / future coverage residual。
- `needs_fact_freeze`：添加 golden rows 或改变 expected values 前需要 reviewed expected facts。
- `needs_extractor_projection_gate`：需要 future runtime / snapshot / golden-scoring implementation gate；本 gate 不授权。
- `not_in_minimum_scope`：不属于本 004194 decision 的 minimum scope。

| Area / field | Current evidence | Disposition | Owner | Next gate |
|---|---|---|---|---|
| Decision artifact wording | Need to encode conservative 004194 decision and GLM F1 P16 provenance constraint | `fix_now` | 004194 decision worker | docs-only decision artifact |
| Implementation evidence artifact | Need to prove read-only evidence, diff boundary, and self-checks | `fix_now` | 004194 decision worker | docs-only evidence artifact |
| `index_profile.*` five scalar rows | 5/5 matched; benchmark-context only | `defer_from_minimum_v1` for full fixture; allowed as specialized diagnostic candidate | future fixture / baseline owner | future fixture promotion-prep only after controller accepts bounded role |
| P0 strict correctness coverage | 0 comparable P0 rows in current 004194 golden scope | `needs_fact_freeze` before adding rows; then possible `needs_extractor_projection_gate` if snapshot projection gaps appear | future P0 golden coverage owner | 004194 P0 golden row fact-freeze / strict correctness expansion gate |
| `basic_identity.*` P0 | Snapshot comparable values exist; no current 004194 P0 golden rows | `needs_fact_freeze` | future P0 golden coverage owner | P0 golden coverage expansion gate |
| `benchmark.benchmark_name` P0 | Snapshot comparable value exists; no current 004194 benchmark P0 golden row | `needs_fact_freeze` | future P0 golden coverage owner | P0 golden coverage expansion gate |
| `classified_fund_type.fund_type` P0 | Snapshot comparable value `enhanced_index`; no current 004194 P0 golden row | `needs_fact_freeze` | future P0 golden coverage owner | P0 golden coverage expansion gate |
| `nav_benchmark_performance.*` P0 | Snapshot comparable values exist; no current 004194 P0 golden rows | `needs_fact_freeze` | future P0 golden coverage owner | P0 golden coverage expansion gate |
| `fee_schedule` P0 | Snapshot field is present / anchored but no comparable P0 golden row in current scope | `needs_fact_freeze`, then `needs_extractor_projection_gate` only if expected subfields are not projected | future P0 fee owner | P0 fact-freeze / projection gate |
| `manager_strategy_text.*` P0 | Snapshot field present / anchored but `comparable_values={}`; no current 004194 golden rows | `needs_fact_freeze` plus likely `needs_extractor_projection_gate` | future P0 manager strategy owner | P0 manager strategy fact-freeze / projection gate |
| `tracking_error` conditional P1 | Quality warn; snapshot missing with `tracking_error_unparseable`; P15/P16 direct disclosure not accepted | `needs_fact_freeze` only if direct observed disclosure is found; otherwise blocked for production rows and `defer_from_minimum_v1` for current diagnostic candidate | P15/P17 tracking-error evidence owner | P15 direct observed disclosure evidence gate / extractor ambiguity gate |
| `turnover_rate` P1 | Quality warn; snapshot missing | `defer_from_minimum_v1` | future quality coverage owner | turnover-rate evidence / extractor gate |
| Methodology / constituents detail beyond benchmark-only | Current rows only say `benchmark_only` | `not_in_minimum_scope` | future index evidence owner | methodology / constituents evidence gate |
| Performance / cost / manager / holdings / shareholder / final judgment readiness | Not verified by the five index_profile rows | `not_in_minimum_scope` for this diagnostic candidate; blocked for full fixture readiness | future full fixture owner | full fixture promotion-prep gate only after P0 expansion and reviews |
| Fixture manifest state | Current `absent`, `promotion_allowed=false`, `blocks_minimum_v1=true` | `not_in_minimum_scope` for worker mutation; preserve as evidence only | future fixture promotion gate | future promotion-prep gate |

## Final Accepted Decision Candidate

Decision candidate for controller review:

| Key | Value |
|---|---|
| `decision` | `index_profile_only_candidate_not_full_fixture_ready` |
| `fund_code` | `004194` |
| `report_year` | `2024` |
| `minimum_v1_full_fixture_promotion_prep_ready` | `false` |
| `index_profile_only_specialized_candidate_allowed` | `true`, only as bounded diagnostic / specialized candidate |
| `fixture_state_after_gate` | `absent` |
| `promotion_allowed` | `false` |
| `promotion_manifest` | `false` |
| `tracking_error_production_golden_allowed` | `false` until P15-style reviewed direct observed disclosure evidence is accepted |
| `tracking_error_production_golden_blocked_inputs` | target/limit text; manager narrative; benchmark-only text; standard-deviation-only text; ambiguous text; unparseable text; calculated values |
| `p0_strict_correctness_coverage` | `0` |
| `current_matched_rows` | exactly five `index_profile.*` benchmark-context scalar rows |
| `full_fixture_blocker` | no 004194 P0 strict correctness rows in current golden scope |
| `fixture_state_after_gate` | `absent` |
| `next_gate` | `006597 same-fund unavailable field review or strict correctness rerun`; 004194 residuals route to future P0 expansion / P15 tracking-error evidence gates |

Rationale：the five matched `index_profile` rows are useful and verified, but they are conditional P1 benchmark-context rows only. They do not establish P0 correctness or full-report readiness. Full fixture promotion-prep remains blocked by P0 strict correctness coverage `0`.

## Non-Goals / Forbidden Changes

This gate did not and must not:

- modify `docs/implementation-control.md`; controller will update it later if accepted;
- modify `fund_agent/**`, `tests/**`, `scripts/**`, `reports/**`, golden answers, golden fixtures, score, quality gate, snapshot, preflight outputs, manifests, `pyproject.toml`, `uv.lock`, README files, `docs/design.md`, or unrelated untracked files;
- run or claim runtime validation, score reruns, snapshot regeneration, golden-build, ruff, or pytest;
- set `promotion_allowed=true`;
- change fixture state from `absent`;
- create or modify a promotion manifest;
- weaken FQ0-FQ6, strict golden correctness, score policy, quality gate semantics, final judgment, renderer, Service/UI, Host/Agent/dayu, external source strategy, or `FundDocumentRepository` boundary;
- add `tracking_error` golden rows or infer `tracking_error` from target/limit, narrative, benchmark-only, standard deviation, ambiguous, unparseable, or calculated text;
- call the current five `index_profile` rows P0 coverage, full fixture readiness, final judgment readiness, methodology detail, constituents detail, performance, cost, manager, holdings, shareholder, or turnover readiness;
- restart QDII probing, enter FOF taxonomy, touch `110020` / `017641`, rerun `006597`, or begin release readiness;
- commit, push, PR, merge, release, promote, or enter another gate.

Self-check: pass for docs-only decision scope.
