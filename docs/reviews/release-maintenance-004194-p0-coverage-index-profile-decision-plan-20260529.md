# 004194 P0 Coverage / Index Profile-Only Fixture Decision Plan

日期：2026-05-29

角色：AgentCodex planning worker。本文是 handoff-ready plan artifact，不是 controller judgment；不启动 `$gateflow` / `/gateflow` / `phaseflow`，不提交、不 push、不 PR、不 merge、不 release、不 promotion，不进入其它 gate。

## Goal

为 `004194 / 2024` 在当前 strict golden correctness 结果下形成保守决策计划：

- 判断 `P0 strict correctness coverage=0` 是否阻断 full fixture promotion-prep。
- 判断 5 条 `index_profile.*` matched row 是否可作为 `index_profile-only` 专项候选，并定义明确限制。
- 判断 `tracking_error` direct observed disclosure / P15 evidence 是否是 production `tracking_error` golden rows 前置条件。
- 判断 minimum v1 是否必须扩展 P0 golden coverage，或是否可接受一个非 full fixture 的专项诊断候选。
- 保持 `fixture_state=absent`、`promotion_allowed=false`、`promotion_manifest=false`，不修改 runtime、tests、reports、golden、score、quality、snapshot projection、manifests 或 control doc。

## Non-Goals

- 不修改 `fund_agent/**`、`tests/**`、`scripts/**`、`reports/**`、golden answer JSON、golden fixtures、score policy、quality gate、snapshot projection、manifests、README 或 `docs/implementation-control.md`。
- 不新增或重跑 004194 snapshot / score / quality / golden artifacts。
- 不把 `coverage_scope=covered` 解释为 broad correctness coverage。
- 不把 `index_profile-only` 候选标为 full fixture promotion-prep-ready。
- 不新增 `tracking_error` golden rows，不改变 P15/P16 已接受裁决。
- 不设置 `promotion_allowed=true`。
- 不改变 FQ0-FQ6、final judgment、renderer、Service/UI、Host/Agent/dayu、来源策略或 `FundDocumentRepository` 边界。
- 不处理 `006597`、QDII、FOF、`017641`、`110020`，也不重开 `004393`。

## Truth Sources

| Source | Usage |
|---|---|
| `AGENTS.md` | heavy gate 分类、四层边界、禁止 promotion / release / external mutation、证据可溯源 |
| `docs/design.md` §7.3 / §7.4 | P0/P1/P2 字段优先级；`index_profile` / `tracking_error` 是指数和增强指数条件 P1；FQ0-FQ6 语义 |
| `docs/design.md` index / enhanced-index sections | `enhanced_index` preferred lens：增强来源、超额稳定性、跟踪约束；第 2/3/5 章 core |
| `docs/implementation-control.md` | 当前 phase、next entry、accepted artifacts、non-goals、residual owners |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` | Route 1 顺序：004393 后进入 004194 P0 / index_profile-only 决策 |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-controller-judgment-20260529.md` | roadmap accepted；004194 仍 blocking minimum v1，fixture/promotion 未进入 |
| `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md` | 已接受前置裁决的 004194 breakdown：5 条 `index_profile.*`，P0 coverage 0 |
| `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` | controller 已降级为 `conditional_candidate_pending_p0_coverage_decision` |
| `docs/reviews/release-maintenance-004393-partial-coverage-decision-controller-judgment-20260529.md` | 前一 gate state：004393 不进入 minimum v1 promotion-prep；下一入口为 004194 |
| preflight JSON/MD | `overall_status=block`；004194 `deferred_with_owner`、quality `warn`、fixture `absent` |
| residual / fixture manifests | 004194 `fixture_state=absent`、`promotion_allowed=false`、`blocks_minimum_v1=true` |
| `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/*` | 004194 snapshot / score / quality / golden_set direct evidence |
| `reports/golden-answers/golden-answer.json` 004194 rows | reviewed expected rows：仅 5 条 `index_profile` scalar rows |
| P15 / P16 tracking-error/index-profile artifacts | P15/P16 accepted state：`tracking_error` production golden blocked without direct observed disclosure；P16 accepted only `index_profile` benchmark-context rows |

## Direct Evidence Table

| Evidence | Current value |
|---|---|
| Fund / year / type | `004194 / 2024`; `classified_fund_type=enhanced_index`; App category `国内股票类` |
| Score correctness | `coverage_scope=covered`; `total_records=150`; `comparable_records=5`; `matched_records=5`; `mismatched_records=0`; `unavailable_records=145` |
| Same-fund matched rows | Exactly 5 rows: `index_profile.benchmark_text`, `benchmark_identity_status`, `methodology_availability`, `constituents_availability`, `source_tier` |
| Same-fund P0 correctness rows | 0 comparable, 0 matched, 0 unavailable in the 004194 row set because no 004194 P0 golden rows exist in current strict golden scope |
| Golden-answer 004194 rows | Exactly the five `index_profile` rows above; source anchor `年报2024 §2 page-5 page-5-table-1 benchmark` |
| Snapshot `index_profile` | `value_present=true`, `anchor_present=true`, `comparable_values` contains the five scalar rows; note says benchmark context only and not methodology / constituents evidence |
| Snapshot P0-capable fields | Snapshot exposes P0-like comparable values for `basic_identity`, `benchmark`, `classified_fund_type`, `nav_benchmark_performance`, but current golden answer has no 004194 P0 rows, so strict correctness cannot score them |
| Snapshot `tracking_error` | `extraction_mode=missing`, `value_present=false`, `anchor_present=false`, note `tracking_error_unparseable` |
| Snapshot `turnover_rate` | `extraction_mode=missing`, `value_present=false`, `anchor_present=false`, note `§8 未披露可规则化抽取的换手率` |
| Quality gate | `status=warn`; FQ2 warn for P1 `tracking_error` and `turnover_rate`; FQ2F warn for fund-level P1 failed fields |
| Preflight | `overall_status=block`; 004194 readiness `deferred_with_owner`; `strict_golden_coverage=covered`; `fixture_promotion_state=absent`; blocker `fixture_promotion_absent`; warning `quality_gate_warn` |
| Fixture manifest | 004194 `fixture_state=absent`; `promotion_allowed=false`; blocker `fixture_promotion_absent`; `blocks_minimum_v1=true`; `blocks_v1=true` |
| P15/P16 state | P16 accepted `index_profile` benchmark-context golden rows; `tracking_error` remained blocked for all five enhanced-index candidates without direct observed disclosure |

## Proposed Conservative Decision

Conservative decision: **do not mark 004194 as full fixture promotion-prep-ready**.

Required decision fields for future implementation artifact:

| Field | Value |
|---|---|
| `decision` | `index_profile_only_candidate_not_full_fixture_ready` |
| `minimum_v1_full_fixture_promotion_prep_ready` | `false` |
| `index_profile_only_specialized_candidate_allowed` | `true`, only under limitations below |
| `fixture_state_after_gate` | `absent` |
| `promotion_allowed` | `false` |
| `promotion_manifest` | `false` |
| `tracking_error_production_golden_allowed` | `false` until P15-style reviewed direct observed disclosure evidence is accepted |
| `next_gate` | `006597 same-fund unavailable field review or strict correctness rerun`, while 004194 residuals route to future P0 expansion / P15 tracking-error evidence gates |

### Required Answers

`P0 coverage=0` **blocks full fixture promotion-prep**. It is not a data mismatch; it is absence of current 004194 P0 golden rows in strict correctness scope. A full fixture would imply correctness of P0 fields such as identity, benchmark, fund type, NAV/benchmark performance, fee schedule, and manager strategy text, but none of those are currently verified by 004194 strict golden rows.

`index_profile-only` specialized candidate is acceptable **only as a bounded diagnostic / specialized fixture candidate**, not as full fund fixture readiness. It may validate only the five current scalar benchmark-context `index_profile` rows. It must not be used to prove P0, `tracking_error`, methodology, constituents, performance, cost, manager, turnover, holdings, shareholder, or final-judgment readiness.

`tracking_error` direct disclosure availability / P15 evidence is **required before production `tracking_error` golden rows**. It is not required to preserve the existing five `index_profile` rows, but quality warning ownership must stay active and no `tracking_error` production row may be added from target/limit, manager narrative, benchmark-only text, standard-deviation-only text, ambiguous text, or unparseable text.

P0 golden coverage expansion is **required before any full 004194 fixture promotion-prep**. It is **not required** only if the controller explicitly accepts a non-full, `index_profile-only` diagnostic candidate for minimum-v1 bookkeeping. That candidate cannot satisfy full minimum-v1 fixture readiness by itself.

## Index Profile-Only Candidate Limitations

An `index_profile-only` specialized candidate is allowed only if all conditions are recorded:

- It is named as `index_profile-only`, `diagnostic`, or `specialized`; never `full fixture`, `promotion-prep-ready`, `ready_for_future_promotion`, or `promoted`.
- It covers exactly five rows: `benchmark_text`, `benchmark_identity_status`, `methodology_availability`, `constituents_availability`, `source_tier`.
- It is scoped to benchmark-context evidence from annual report §2, page-5 table-1.
- `methodology_availability=benchmark_only` and `constituents_availability=benchmark_only` must be interpreted as absence of direct methodology / constituent evidence, not as proof of methodology or constituents.
- It does not satisfy `tracking_error`; current snapshot remains `tracking_error_unparseable`.
- It does not satisfy P0 strict correctness.
- It does not change preflight, fixture manifest, residual manifest, score, quality gate, snapshot projection, or golden-answer JSON.
- It keeps `fixture_state=absent` and `promotion_allowed=false`.

## Field Disposition Matrix

Disposition categories:

- `fix_now`: allowed only for the docs-only decision artifact and implementation evidence in this gate.
- `defer_from_minimum_v1`: not required for minimum-v1 diagnostic candidate; remains tracked for full v1 or future quality work.
- `needs_fact_freeze`: requires reviewed expected values before golden or extractor projection work.
- `needs_extractor_projection_gate`: requires future runtime/snapshot/golden-scoring implementation gate; not authorized here.
- `not_in_minimum_scope`: outside this 004194 decision.

| Area / field | Current evidence | Disposition | Owner | Next gate |
|---|---|---|---|---|
| Decision artifact wording | Needs to encode 004194 conservative decision and limitations | `fix_now` | 004194 decision worker | docs-only decision artifact |
| Implementation evidence artifact | Needs to prove source reads, diff boundary, self-checks | `fix_now` | 004194 decision worker | docs-only evidence artifact |
| `index_profile.*` five scalar rows | 5/5 matched, benchmark-context only | `defer_from_minimum_v1` for full fixture; allowed as specialized diagnostic candidate | future fixture / baseline owner | future fixture promotion-prep only after controller accepts bounded role |
| P0 strict correctness coverage | 0 comparable rows in 004194 golden scope | `needs_fact_freeze` before adding rows; then `needs_extractor_projection_gate` if snapshot projection gaps appear | future P0 golden coverage owner | 004194 P0 golden row fact-freeze / strict correctness expansion gate |
| `basic_identity.*` P0 | Snapshot comparable values exist; no 004194 golden rows in current scope | `needs_fact_freeze` | future P0 golden coverage owner | P0 golden coverage expansion gate |
| `benchmark.benchmark_name` P0 | Snapshot comparable value exists; no current 004194 benchmark golden row | `needs_fact_freeze` | future P0 golden coverage owner | P0 golden coverage expansion gate |
| `classified_fund_type.fund_type` P0 | Snapshot comparable value `enhanced_index`; no current 004194 P0 golden row | `needs_fact_freeze` | future P0 golden coverage owner | P0 golden coverage expansion gate |
| `nav_benchmark_performance.*` P0 | Snapshot comparable values exist; no current 004194 golden rows | `needs_fact_freeze` | future P0 golden coverage owner | P0 golden coverage expansion gate |
| `fee_schedule` P0 | Snapshot field is present/anchored but no comparable P0 golden row in current scope | `needs_extractor_projection_gate` only after fact freeze proves expected subfields | future P0 extractor projection owner | P0 projection / strict correctness rerun gate |
| `manager_strategy_text.*` P0 | Snapshot field present/anchored but `comparable_values={}`; no current 004194 golden rows | `needs_fact_freeze` plus likely `needs_extractor_projection_gate` | future P0 manager strategy owner | P0 manager strategy fact-freeze / projection gate |
| `tracking_error` P1 conditional | Quality warn; snapshot missing with `tracking_error_unparseable`; P15/P16 direct disclosure not accepted | `needs_fact_freeze` only if direct observed disclosure is found; otherwise `defer_from_minimum_v1` and blocked for production rows | P15/P17 tracking-error evidence owner | P15 direct observed disclosure evidence gate / extractor ambiguity gate |
| `turnover_rate` P1 | Quality warn; snapshot missing | `defer_from_minimum_v1` | future quality coverage owner | turnover-rate evidence / extractor gate |
| Methodology / constituents detail beyond benchmark-only | Current rows only say `benchmark_only` | `not_in_minimum_scope` | future index evidence owner | methodology / constituents evidence gate |
| Fixture manifest state | Current `absent`, `promotion_allowed=false` | `not_in_minimum_scope` for worker; controller may only reference, not mutate in this gate | future fixture promotion gate | future promotion-prep gate |

## Exact Allowed Files For Implementation Slice

This planning worker is allowed to write only:

- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md`

Future implementation worker allowed files:

- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md`
- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-implementation-evidence-20260529.md`

Controller-only after reviews:

- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-controller-judgment-20260529.md`
- `docs/implementation-control.md` with minimal Startup Packet / Current Gate / next entry update only

## Prohibited Files

Do not modify:

- `fund_agent/**`
- `tests/**`
- `scripts/**`
- `reports/**`
- `reports/golden-answers/**`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/**`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- any promoted golden fixture / golden-answer fixture
- `pyproject.toml`
- `uv.lock`
- README files
- `docs/design.md`
- `docs/implementation-control.md` except controller-only minimal update after accepted reviews

## Implementation Slices

### Slice 1: Docs-only 004194 decision artifact

Write `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md`.

Required content:

- State gate classification `heavy` and docs/control-plane-only scope.
- Reproduce direct evidence counts from `score.json`: `150 / 5 / 5 / 0 / 145`.
- List the five matched `index_profile.*` rows and source anchors.
- State same-fund P0 strict correctness coverage is 0.
- State full fixture promotion-prep is blocked.
- State `index_profile-only` candidate is allowed only as bounded diagnostic/specialized candidate.
- State `tracking_error` production golden rows require P15-style reviewed direct observed disclosure evidence.
- Keep `fixture_state_after_gate=absent` and `promotion_allowed=false`.
- Include the field disposition matrix and residual owner / next_gate table.

### Slice 2: Docs-only implementation evidence

Write `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-implementation-evidence-20260529.md`.

Required content:

- Record read-only evidence commands or source files used.
- Record no runtime/test/report/golden/manifest/control-doc mutation.
- Record validation command outputs.
- Include worker self-check: no full promotion language, no manifest mutation, no forbidden diff.

### Slice 3: Review and controller judgment

Because this is heavy and touches baseline/golden readiness, controller must obtain two independent reviews before acceptance.

Controller may then write:

- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-controller-judgment-20260529.md`
- minimal `docs/implementation-control.md` pointer update only if the decision is accepted

No implementation worker should update control doc unless explicitly re-handoffed by controller.

## Review Requirements

Independent reviews must verify:

- 004194 score correctness counts: `coverage_scope=covered`, `total_records=150`, `comparable_records=5`, `matched_records=5`, `mismatched_records=0`, `unavailable_records=145`.
- The five comparable rows are exactly `index_profile.benchmark_text`, `benchmark_identity_status`, `methodology_availability`, `constituents_availability`, `source_tier`.
- Same-fund P0 strict correctness coverage is 0.
- `unavailable_records=145` are not 004194 intra-fund missing P0 rows; they are unavailable records from the broader golden answer scope.
- `index_profile` is conditional P1 for index / enhanced-index per `docs/design.md` §7.3.
- `quality_gate.status=warn` is caused by P1 `tracking_error` and `turnover_rate`, not by FQ1 mismatch.
- P15/P16 accepted state still blocks production `tracking_error` golden rows without direct observed disclosure evidence.
- Artifact wording does not call 004194 full fixture promotion-prep-ready.
- `fixture_state=absent` and `promotion_allowed=false` remain unchanged.
- Forbidden file diff is empty.

Controller judgment must explicitly accept, reject, or amend:

- full fixture promotion-prep blocked by P0 coverage 0;
- `index_profile-only` specialized candidate allowed or rejected;
- tracking-error direct evidence prerequisite;
- whether minimum v1 may proceed with a non-full 004194 specialized candidate or must wait for P0 expansion;
- owner and next_gate for tracking_error, turnover_rate, P0 coverage, and fixture promotion state.

## Validation Commands

Validation before completion of this planning slice:

```bash
git diff --check -- docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md
```

Forbidden diff check:

```bash
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json
```

Expected result for forbidden diff check: no output.

Future implementation slice validation:

```bash
git diff --check -- docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-implementation-evidence-20260529.md docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-controller-judgment-20260529.md docs/implementation-control.md
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json
```

`ruff` / `pytest` should not be run for this docs-only gate unless runtime/tests are changed in a future gate. If runtime/test changes appear, stop; they are not authorized here.

Optional read-only evidence checks:

```bash
jq '.correctness | {coverage_scope,total_records,comparable_records,matched_records,mismatched_records,unavailable_records}' reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json
jq '.correctness.record_results[] | select(.fund_code=="004194") | {field_name,sub_field,status,source}' reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json
jq '.rows[] | select(.fund_code=="004194")' reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json
jq '.entries[] | select(.fund_code=="004194")' docs/reviews/fixture-promotion-state-manifest-20260529.json
```

## Stop Conditions

Stop and return to controller if any of the following occurs:

- Any plan or implementation wording marks 004194 as full fixture promotion-prep-ready.
- Any row is marked `promoted`, `ready_for_future_promotion`, or `promotion_allowed=true`.
- Any runtime, test, report, golden, manifest, score, quality, snapshot projection, README, design, or control-doc edit is required by the worker.
- Any FQ1 mismatch, quality `block`, or new source identity conflict is discovered for 004194.
- Evidence suggests current five `index_profile.*` matches are not exactly the reviewed P16 rows.
- The implementation needs to add P0 golden rows, tracking-error rows, methodology rows, constituents rows, or turnover rows.
- The implementation needs to change FQ0-FQ6, score correctness denominator, preflight consumption, fixture manifest schema, or quality gate severity.
- The worker is asked to commit, push, PR, merge, release, promote, or start another gate.

## Residual Risks / Owners / Next Gate

| Residual | Current disposition | Owner | Next gate |
|---|---|---|---|
| P0 strict correctness coverage | Blocks full fixture promotion-prep; no P0 rows in current 004194 strict golden scope | future P0 golden coverage owner | 004194 P0 golden row fact-freeze / strict correctness expansion gate |
| `tracking_error` | P1 quality warn; production golden rows blocked without direct observed disclosure | P15/P17 tracking-error evidence owner | P15 direct observed disclosure evidence gate / tracking-error extractor ambiguity gate |
| `turnover_rate` | P1 quality warn; deferred from minimum diagnostic candidate | future quality coverage owner | turnover-rate evidence / extractor gate |
| Fixture promotion state | `fixture_state=absent`, `promotion_allowed=false`; blocks minimum and full v1 | future fixture promotion gate | fixture promotion-prep after accepted fund-level decisions |
| Index methodology / constituents detail | Current state is benchmark-only, not direct methodology/constituents evidence | future index evidence owner | methodology / constituents evidence gate |
| Minimum v1 route | May proceed past 004194 only if controller accepts non-full `index_profile-only` decision; otherwise waits for P0 expansion | release maintenance controller | 006597 route or P0 expansion gate, per controller judgment |

## Worker Self-Checks

Before completion, worker must verify:

- This artifact is the only file created or changed by the planning worker.
- The artifact answers all required decision questions.
- It does not authorize full fixture promotion-prep.
- It does not authorize runtime/tests/reports/golden/manifest/control-doc changes.
- It preserves `fixture_state=absent` and `promotion_allowed=false`.
- `git diff --check -- docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md` passes.
- Forbidden diff check produces no output.

## Completion Report Format

Final response must include:

- Artifact path: `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md`
- Decision summary: P0 coverage 0 blocks full fixture promotion-prep; `index_profile-only` candidate is bounded diagnostic only; `promotion_allowed=false`.
- Validation: `git diff --check` result and forbidden diff result.
- `Self-check: pass` or `Self-check: blocked` with reason.
