# 004393 Partial Coverage Decision / Expansion Gate Plan

日期：2026-05-29

角色：AgentCodex planning worker。本文是 handoff-ready plan artifact，不是 controller judgment，不启动 `$gateflow` / `/gateflow` / `phaseflow`，不授权 commit、push、PR、merge、release、promotion 或进入其它 gate。

## Goal

为 `004393 / 2024` strict golden correctness 的 partial coverage 状态形成保守、可审查、可移交的决策计划：

- 基于已有 accepted control-plane 与 score/snapshot/golden artifacts，判定当前 `9/150` score-wide comparable、同基金 P0 `9/11`、P1 `0/10` 是否足以进入 minimum golden v1 promotion-prep。
- 明确 9 个已 matched 字段、2 个 P0 missing 字段、10 个 P1 missing 字段的优先级、缺失原因和处置类别。
- 默认保持 `fixture_state=absent`、`promotion_allowed=false`，不修改 fixture manifest、golden answer、snapshot、score、quality gate、runtime 或 reports。
- 如果需要 coverage expansion，只把它拆成后续最小 implementation gate；本 gate 只做 docs/control-plane decision。

## Non-Goals

- 不修改 Python runtime、tests、golden fixtures、golden-answer JSON、score policy、quality gate、snapshot projection、manifests 或 reports。
- 不新增、删除或重跑 004393 snapshot / score / quality artifacts。
- 不把 partial correctness 自动升级为 `promotion-prep-ready`。
- 不设置 `promotion_allowed=true`。
- 不改变 FQ0-FQ6 语义、final judgment、renderer、Service/UI、Host/Agent/dayu、来源策略或 `FundDocumentRepository` 边界。
- 不处理 `004194`、`006597`、QDII、FOF、`017641`、`110020` 的后续 gate。

## Truth Sources

必须读取并只把下列文件作为本 gate 证据来源：

| Source | Usage |
|---|---|
| `AGENTS.md` | gate 分类、四层边界、禁止事项、证据可溯源、promotion 约束 |
| `docs/design.md` | 当前设计真源；§7.3 字段优先级；§7.4 quality gate 语义 |
| `docs/implementation-control.md` | 当前 phase / next entry / non-goals / residual owners |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` | release maintenance 五路线与 004393 next entry |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-controller-judgment-20260529.md` | roadmap accepted local validation |
| `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md` | strict correctness decision table 与 004393 partial breakdown |
| `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` | accepted controller decision：004393 conditional candidate only |
| `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` / `.md` | overall block、004393 fixture absent、quality warn |
| `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | residual disposition state |
| `docs/reviews/fixture-promotion-state-manifest-20260529.json` | fixture state: `absent`, `promotion_allowed=false` |
| `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/snapshot.jsonl` | field-level `value_present` / `anchor_present` / `comparable_values` |
| `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json` / `.md` | correctness totals, record-level match/unavailable reasons |
| `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/quality_gate.json` / `.md` | `warn` status, FQ0 partial coverage info, turnover_rate warning |
| `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/golden_set.json` | source-scoped golden set, if needed for cross-check |
| `reports/golden-answers/golden-answer.json` 004393 rows | reviewed expected values and source anchors |

## Direct Evidence Table

| Evidence | Current value |
|---|---|
| Score-wide correctness | `coverage_scope=partially_covered`; `total_records=150`; `comparable_records=9`; `matched_records=9`; `mismatched_records=0`; `unavailable_records=141` |
| Same-fund 004393 comparable rows | 9 matched rows, all P0 by `docs/design.md` §7.3 field priority |
| Same-fund 004393 P0 unavailable rows | 2 rows: `manager_strategy_text.strategy_summary`, `manager_strategy_text.market_outlook` |
| Same-fund 004393 P1 unavailable rows | 10 rows: `product_profile.*`, `manager_alignment.*`, `holder_structure.*`, `share_change.*` |
| Missing reason in score | `snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。` |
| Snapshot root cause | several field-level snapshot records have `value_present=true` and `anchor_present=true`, but `comparable_values={}` for the golden subfields |
| Quality gate | `status=warn`; FQ2/FQ2F warn for `turnover_rate`; FQ0 info says strict golden fields exceed snapshot comparable contract and `coverage_scope=partially_covered` |
| Preflight state | `overall_status=block`; `004393` readiness `deferred_with_owner`; quality `warn`; strict golden `covered`; fixture `absent` |
| Fixture state manifest | `004393` entry has `fixture_state=absent`, `promotion_allowed=false`, blocker `fixture_promotion_absent` |
| Accepted controller state | `004393` decision is `conditional_candidate_pending_partial_coverage_decision`; next gate is partial coverage decision / strict golden fixture promotion review |

## 9 Matched Fields And Priorities

All 9 matched same-fund rows are P0 because their `field_name` is in `docs/design.md` §7.3 P0 list.

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

## Field Disposition Matrix

Disposition categories used by this plan:

- `fix_now`: allowed only for docs/control-plane corrections in this gate; no runtime/golden/report field uses this category here.
- `needs_extractor_projection_gate`: mandatory before any future minimum v1 promotion-prep, but must be implemented in a separate runtime/snapshot projection gate.
- `defer_from_minimum_v1`: not mandatory for minimum v1 strict correctness, but remains a tracked full-v1 or quality residual.
- `needs_fact_freeze`: requires reviewed expected fact/value freeze before implementation.
- `not_in_minimum_scope`: outside the 004393 strict correctness minimum-v1 decision.

| Field | Subfield | Priority | Mandatory for minimum v1 strict correctness? | Missing reason from artifacts | Disposition |
|---|---|---|---|---|---|
| `manager_strategy_text` | `strategy_summary` | P0 | Yes | Snapshot has field-level `value_present=true` / `anchor_present=true` for `manager_strategy_text`, but `comparable_values={}`; score says snapshot did not explicitly expose this golden subfield. | `needs_extractor_projection_gate` |
| `manager_strategy_text` | `market_outlook` | P0 | Yes | Same as above: annual-report §4 text is anchored, but not exposed as comparable subfield. | `needs_extractor_projection_gate` |
| `product_profile` | `investment_objective` | P1 | Deferred from minimum v1 | Snapshot has `product_profile` value/anchor at §2 page-5 table-1, but `comparable_values={}`; score cannot compare subfield. | `defer_from_minimum_v1` |
| `product_profile` | `style_positioning` | P1 | Deferred from minimum v1 | Same snapshot projection gap; source points to `investment_objective`. | `defer_from_minimum_v1` |
| `product_profile` | `investment_scope` | P1 | Deferred from minimum v1 | Snapshot has anchor at §2 page-5 table-1, but no comparable subfield. | `defer_from_minimum_v1` |
| `manager_alignment` | `manager_holding` | P1 | Deferred from minimum v1 | Snapshot has §9 page-63 table-2 anchor, but `comparable_values={}`. | `defer_from_minimum_v1` |
| `manager_alignment` | `employee_holding` | P1 | Deferred from minimum v1 | Snapshot has §9 page-63 table-2/field anchor path, but no comparable subfield for score. | `defer_from_minimum_v1` |
| `holder_structure` | `institutional_holder` | P1 | Deferred from minimum v1 | Snapshot has §9 page-63 table-0 anchor, but `comparable_values={}`. | `defer_from_minimum_v1` |
| `holder_structure` | `individual_holder` | P1 | Deferred from minimum v1 | Snapshot has §9 page-63 table-0 anchor, but no comparable subfield. | `defer_from_minimum_v1` |
| `share_change` | `beginning_share` | P1 | Deferred from minimum v1 | Snapshot has §10 page-64 table-0 anchor, but `comparable_values={}`. | `defer_from_minimum_v1` |
| `share_change` | `ending_share` | P1 | Deferred from minimum v1 | Snapshot has §10 page-64 table-0 anchor, but no comparable subfield. | `defer_from_minimum_v1` |
| `share_change` | `net_change` | P1 | Deferred from minimum v1 | Snapshot has §10 page-64 table-0 anchor, but no comparable subfield. | `defer_from_minimum_v1` |
| `turnover_rate` | not in current 004393 golden rows | P1 | No for this strict-correctness decision | Quality gate warns `turnover_rate` coverage/traceability is 0%; it is a quality residual, not one of the 004393 strict golden comparable/unavailable rows. | `not_in_minimum_scope` |

## Proposed Decision Default

Conservative default: **reject current 004393 partial coverage for minimum v1 promotion-prep**.

Rationale:

- The 9 matched rows prove only already exposed P0 subfields; they do not prove the two P0 `manager_strategy_text` subfields that are central to active-fund manager narrative and CHAPTER_CONTRACT downstream writing.
- `coverage_scope=partially_covered` plus FQ0 info explicitly says the golden fields exceed snapshot comparable contract.
- The root cause is not a value mismatch; it is a projection/comparability gap. Treating it as promotion-prep-ready would convert untested golden subfields into assumed correctness.
- `quality_gate.status=warn` and `fixture_state=absent` remain accepted blockers.

Decision to encode in the implementation artifact:

- `decision=reject_partial_coverage_for_minimum_v1_promotion_prep`
- `fixture_state_after_gate=absent`
- `promotion_allowed=false`
- `next_gate=004393 P0 manager_strategy_text extractor projection / strict correctness rerun gate`

Narrow alternative, only if controller explicitly chooses it after reviews: `limited_fixture_role=diagnostic_only`. It may be used only as a non-promotion, non-baseline, docs/control-plane diagnostic row for the 9 matched P0 fields, with explicit exclusions for missing P0/P1 fields and `promotion_allowed=false`. This plan does not recommend that alternative as the default.

## Reviewed Fact Freeze Decision

No new reviewed fact freeze is required to make this docs-only decision, because the relevant expected values and annual-report source anchors already exist in `reports/golden-answers/golden-answer.json` and are echoed by `score.json`.

No fact-freeze-only gate is required before a future P0 projection gate if that gate only exposes existing already-reviewed `manager_strategy_text.strategy_summary` and `manager_strategy_text.market_outlook` values as comparable snapshot subfields without changing expected facts.

Stop and require `needs_fact_freeze` if a future worker needs to:

- change expected golden values;
- split, summarize, normalize, or materially rewrite manager text beyond existing reviewed golden rows;
- add new golden rows not currently present for 004393;
- resolve a conflict between extracted raw text and reviewed golden answer.

## Coverage Expansion Decision

Coverage expansion is needed before any future minimum v1 promotion-prep for 004393, but it is **not authorized in this gate**.

Future minimal gate should be split as:

1. `004393 P0 manager_strategy_text extractor projection gate`
2. rerun only the necessary 004393 snapshot / score / quality validation under that future gate
3. review strict correctness output
4. only then decide whether P1 fields remain deferred or must be expanded before promotion-prep

The future gate may need runtime/snapshot projection changes, but this plan does not authorize them and does not name runtime files as allowed implementation targets. The future plan must inspect current code ownership first and produce its own allowed file list, tests, and validation matrix.

## Exact Allowed Files For This Implementation Slice

Implementation worker allowed files:

- `docs/reviews/release-maintenance-004393-partial-coverage-decision-20260529.md`
- `docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-evidence-20260529.md`

Controller-only after reviews:

- `docs/reviews/release-maintenance-004393-partial-coverage-decision-controller-judgment-20260529.md`
- `docs/implementation-control.md` with minimal Startup Packet / Current Gate / next entry update only

The current planning worker is allowed to write only this plan artifact:

- `docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-20260529.md`

## Prohibited Files

Do not modify:

- `fund_agent/**`
- `tests/**`
- `scripts/**`
- `reports/**`
- `reports/golden-answers/golden-answer.json`
- `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/**`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- any golden fixture directory or JSON fixture
- `pyproject.toml`
- `uv.lock`
- README files, unless a later controller explicitly authorizes a docs sync for changed behavior

## Implementation Slices

### Slice 1: Docs-only 004393 partial coverage decision artifact

Allowed worker output:

- Write `docs/reviews/release-maintenance-004393-partial-coverage-decision-20260529.md`.
- Optionally write `docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-evidence-20260529.md` if the controller requires separate evidence.

Required content:

- State this is a heavy docs/control-plane decision, not a promotion gate.
- Copy the direct evidence table and field disposition matrix from this plan, updating only if source artifacts prove a mismatch.
- Encode the conservative default: reject current partial coverage for minimum v1 promotion-prep.
- Keep `promotion_allowed=false` and `fixture_state=absent`.
- Record next gate as P0 `manager_strategy_text` extractor projection / strict correctness rerun gate.
- Record P1 fields as `defer_from_minimum_v1` unless reviewers find an accepted minimum-v1 requirement.
- Record no new fact freeze required for the decision, with stop conditions for future value changes.

### Slice 2: Review and controller acceptance

Controller action after Slice 1:

- Obtain two independent reviews because this is a heavy gate and affects baseline/golden promotion readiness.
- Controller writes judgment only after resolving findings.
- If accepted, controller may minimally update `docs/implementation-control.md` to point to the accepted decision and next gate.

No implementation worker should update `docs/implementation-control.md` unless explicitly included in a controller handoff.

## Review Requirements

Two independent reviews must check:

- Field counts: score-wide `150/9/9/0/141`, same-fund P0 `9/11`, same-fund P1 `0/10`.
- Priority mapping comes from `docs/design.md` §7.3, not from absent `priority` keys in score record rows.
- Missing reasons are copied from `score.json` and cross-checked against `snapshot.jsonl` `comparable_values={}`.
- P0 `manager_strategy_text.strategy_summary` and `manager_strategy_text.market_outlook` are mandatory before minimum v1 promotion-prep.
- P1 ten missing rows are deferred from minimum v1 by default, with explicit residual ownership.
- `turnover_rate` remains a quality warning outside current strict correctness row set.
- `promotion_allowed=false` and fixture state remains `absent`.
- Forbidden file diff is empty.

Controller judgment must explicitly accept, reject, or amend:

- reject-current-partial-coverage default;
- P0 mandatory coverage expansion;
- P1 deferred status;
- fact-freeze decision;
- next gate owner and stop conditions.

## Validation Commands

Docs-only validation:

```bash
git diff --check -- docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-20260529.md docs/reviews/release-maintenance-004393-partial-coverage-decision-20260529.md docs/reviews/release-maintenance-004393-partial-coverage-decision-implementation-evidence-20260529.md docs/reviews/release-maintenance-004393-partial-coverage-decision-controller-judgment-20260529.md docs/implementation-control.md
```

Forbidden diff check:

```bash
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json
```

Expected result for forbidden diff check: no output.

JSON validation is not applicable unless a later controller authorizes JSON edits. `ruff` / `pytest` should not be run for this docs-only gate unless runtime/tests are changed in a future gate. If runtime changes appear, stop; do not validate them inside this gate.

Optional read-only evidence checks:

```bash
jq '.correctness | {coverage_scope,total_records,comparable_records,matched_records,mismatched_records,unavailable_records}' reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json
jq '.rows[] | select(.fund_code=="004393")' reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json
jq '.entries[] | select(.fund_code=="004393")' docs/reviews/fixture-promotion-state-manifest-20260529.json
```

## Stop Conditions

Stop and return to controller if:

- any source artifact is missing or contradicts the accepted counts;
- reviewers require changing golden answer, fixture manifest, score policy, quality gate, snapshot projection, reports, or runtime code;
- any proposal sets `promotion_allowed=true`;
- any proposal treats `coverage_scope=partially_covered` as broad correctness coverage;
- any implementation needs to rewrite expected 004393 facts rather than project existing reviewed facts;
- unrelated dirty files make ownership unclear;
- controller asks to include 004194 / 006597 in the same gate.

## Residual Risks, Owners, Next Gate

| Risk / residual | Owner | Next gate |
|---|---|---|
| 004393 P0 manager strategy text not comparable | future baseline / strict golden owner | `004393 P0 manager_strategy_text extractor projection / strict correctness rerun gate` |
| 004393 P1 product profile / alignment / holder / share-change not comparable | future fixture promotion or full-v1 coverage owner | after P0 gate, decide whether P1 remains deferred or needs expansion |
| 004393 `turnover_rate` quality warning | future quality residual owner | P1 quality coverage / active-fund manager evidence gate, not this strict correctness decision |
| Fixture state absent | future fixture promotion gate | fixture promotion-prep only after fund-level strict correctness decisions are accepted |
| Current partial coverage may be overread by future agents | controller | decision artifact and implementation-control update must explicitly say rejected for minimum v1 promotion-prep |

## Completion Report Format

Implementation worker final report must include:

```text
Artifact: <path>
Decision encoded: <reject_current_partial_coverage_for_minimum_v1_promotion_prep | blocked>
Promotion state: promotion_allowed=false; fixture_state=absent
Validation: <commands run and result>
Forbidden changes: <no output | blocked with paths>
Next gate: <P0 manager_strategy_text extractor projection / strict correctness rerun gate>
Self-check: <pass | blocked: reason>
```

## Worker Self-Checks

Before starting: pass. Current role is planning worker, not controller; assignment is one plan artifact only.

Before edit: pass. The only file to add in this turn is `docs/reviews/release-maintenance-004393-partial-coverage-decision-plan-20260529.md`; runtime, tests, reports, manifests, golden answer, score, quality gate and control doc are out of scope.

Before completion: required. Run `git diff --check` for this plan artifact and verify no prohibited files were modified by this worker.
