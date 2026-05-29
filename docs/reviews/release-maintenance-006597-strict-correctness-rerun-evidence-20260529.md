# 006597 Strict Correctness Rerun / Same-Fund Unavailable Field Review Evidence

日期：2026-05-29

角色：AgentCodex implementation/evidence worker。本文严格执行 accepted plan `docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-20260529.md`；不是 controller judgment，不 stage、不 commit、不 push、不 PR、不 merge、不 release、不 promote。

## Verdict

**BLOCKED with reason.**

Strict correctness rerun 已使用 `reports/golden-answers/golden-answer.json` 成功配置并执行。机器结果为 `coverage_scope=partially_covered`，same-fund `006597` 有 9 行 matched、0 行 mismatch、11 行 unavailable。按 accepted plan，存在 same-fund unavailable 时只能进入字段级人工核验台账，不能猜测修复、不能改 golden、不能改 runtime，也不能标记为 clean pass 或 promoted。

Decision candidate：`blocked_pending_same_fund_unavailable_field_review`。

Fixture state remains `absent`; `promotion_allowed=false`; `blocks_minimum_v1=true`; `blocks_v1=true`.

## Commands Executed

| Step | Command | Exit status | Output paths |
|---|---|---:|---|
| Strict correctness rerun | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json --output-dir reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529` | 0 | `score.json`; `score.md`; `golden_set.json` under `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/` |
| Quality gate consistency run | `uv run fund-analysis quality-gate --score-path reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json --output-dir reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529` | 0 | `quality_gate.json`; `quality_gate.md` under `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/` |

No implementation command edited production code, tests, scripts, golden answers, fixtures, manifests, preflight, control doc, design doc, or FQ / score / quality semantics.

## Correctness Totals

Source：`reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json`

| Field | Value |
|---|---:|
| `coverage_scope` | `partially_covered` |
| `total_records` | 150 |
| `comparable_records` | 9 |
| `matched_records` | 9 |
| `mismatched_records` | 0 |
| `unavailable_records` | 141 |
| `skipped_records` | 29 |
| `accuracy_rate` | 1.0 |
| `golden_answer_path` | `reports/golden-answers/golden-answer.json` |
| `covered_fund_codes` | `006597` |

Unavailable breakdown:

| Scope | unavailable count |
|---|---:|
| Same-fund `006597` unavailable | 11 |
| Cross-fund unavailable | 130 |
| Total unavailable | 141 |

Cross-fund unavailable rows are part of the broader 150-row golden corpus and are not a 006597 same-fund failure. The blocking condition here is the 11 same-fund unavailable rows.

## Same-Fund 006597 Record Results

| field_name | sub_field | status | expected summary | actual summary | source | reason |
|---|---|---|---|---|---|---|
| `basic_identity` | `fund_name` | match | `国泰利享中短债债券型证券投资基金` | `国泰利享中短债债券型证券投资基金` | `年报2024 §2 page-5 page-5-table-0 fund_name` | 保守 normalize 后完全一致。 |
| `basic_identity` | `fund_code` | match | `006597` | `006597` | `年报2024 §2 page-5 page-5-table-0 fund_code` | 保守 normalize 后完全一致。 |
| `basic_identity` | `management_company` | match | `国泰基金管理有限公司` | `国泰基金管理有限公司` | `年报2024 §2 page-5 page-5-table-0 management_company` | 保守 normalize 后完全一致。 |
| `basic_identity` | `custodian` | match | `招商银行股份有限公司` | `招商银行股份有限公司` | `年报2024 §2 page-5 page-5-table-0 custodian` | 保守 normalize 后完全一致。 |
| `basic_identity` | `inception_date` | match | `2018年12月3日` | `2018年12月3日` | `年报2024 §2 page-5 page-5-table-0 inception_date` | 保守 normalize 后完全一致。 |
| `product_profile` | `investment_objective` | unavailable | `在严格控制风险的前提下，追求稳健的投资回报。` | empty | `年报2024 §2 page-5 page-5-table-1 investment_objective` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `product_profile` | `style_positioning` | unavailable | `本基金为债券型基金，预期收益和预期风险...` | empty | `年报2024 §2 page-5 page-5-table-1 style_positioning` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `benchmark` | `benchmark_name` | match | `中债总财富（1-3年）指数收益率*80%...` | `中债总财富（1-3年）指数收益率*80%...` | `年报2024 §2 page-5 page-5-table-1 benchmark` | 保守 normalize 后完全一致。 |
| `classified_fund_type` | `fund_type` | match | `bond_fund` | `bond_fund` | `年报2024 §2 page-5 page-5-table-0 fund_name` | 保守 normalize 后完全一致。 |
| `nav_benchmark_performance` | `nav_growth_rate` | match | `2.57%` | `2.57%` | `年报2024 §3 page-11 page-11-table-1 nav_growth_rate` | 保守 normalize 后完全一致。 |
| `nav_benchmark_performance` | `benchmark_return_rate` | match | `3.42%` | `3.42%` | `年报2024 §3 page-11 page-11-table-1 benchmark_return_rate` | 保守 normalize 后完全一致。 |
| `manager_strategy_text` | `strategy_summary` | unavailable | `2024年债市整体表现震荡走牛...` | empty | `年报2024 §4 strategy_summary` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `manager_strategy_text` | `market_outlook` | unavailable | `国际方面，美国大选结果揭晓后外部环境...` | empty | `年报2024 §4 market_outlook` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `manager_alignment` | `manager_holding` | unavailable | `本基金基金经理持有...A 10~50...` | empty | `年报2024 §9 page-64 page-64-table-2 manager_holding` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `manager_alignment` | `employee_holding` | unavailable | `基金管理人所有从业人员持有本基金...` | empty | `年报2024 §9 page-64 page-64-table-1 employee_holding` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `holder_structure` | `institutional_holder` | unavailable | `44.56%` | empty | `年报2024 §9 page-63 page-63-table-1 institutional_holder` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `holder_structure` | `individual_holder` | unavailable | `55.44%` | empty | `年报2024 §9 page-63 page-63-table-1 individual_holder` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `share_change` | `beginning_share` | unavailable | `7,699,969,800.13` | empty | `年报2024 §10 page-65 page-65-table-0 share_change` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `share_change` | `ending_share` | unavailable | `5,711,224,267.09` | empty | `年报2024 §10 page-65 page-65-table-0 share_change` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |
| `share_change` | `net_change` | unavailable | `-1,988,745,533.04` | empty | `年报2024 §10 page-65 page-65-table-0 share_change` | snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。 |

Matched fields：9, all P0 fields currently represented in golden and comparable output:

- `basic_identity.fund_name`
- `basic_identity.fund_code`
- `basic_identity.management_company`
- `basic_identity.custodian`
- `basic_identity.inception_date`
- `benchmark.benchmark_name`
- `classified_fund_type.fund_type`
- `nav_benchmark_performance.nav_growth_rate`
- `nav_benchmark_performance.benchmark_return_rate`

Mismatch fields：0.

Unavailable same-fund fields：11.

The existing untracked follow-up score predicted the same shape: 9 matched P0 and 11 same-fund unavailable P1/P0 rows. This artifact treats that old output only as predictor; the decision above is based on the new 006597-specific rerun output paths.

Important coverage limitation：`fee_schedule` is P0 in `docs/design.md` §7.3, but there are no current 006597 `fee_schedule` golden rows in `reports/golden-answers/golden-answer.json`. Therefore even a hypothetical clean pass over the current 20 rows would not prove full P0 coverage.

## Quality Gate State

Source：`reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.json`

Status：`warn`

| rule_code | severity | fund_code | field_name | priority | reason / message |
|---|---|---|---|---|---|
| FQ2 | warn | null | `turnover_rate` | P1 | P1 关键字段 coverage/traceability 未达标 |
| FQ2 | warn | null | `holder_structure` | P1 | P1 关键字段 coverage/traceability 未达标 |
| FQ2 | warn | null | `share_change` | P1 | P1 关键字段 coverage/traceability 未达标 |
| FQ2F | warn | `006597` | null | P1 | 失败字段：`turnover_rate`, `holder_structure`, `share_change` |
| FQ0 | info | `006597` | null | null | 当前基金 strict golden answer 部分字段超出 snapshot 可比合约；`coverage_scope=partially_covered`, `comparable_records=9`, `unavailable_records=141`, `golden_answer_path=reports/golden-answers/golden-answer.json` |
| FQ4 | warn | `006597` | null | null | snapshot 字段缺失率偏高；observed rate `0.2857142857142857`, threshold `0.2` |

No FQ1 correctness mismatch/block appears in the rerun quality gate.

## Fixture State

Source：`docs/reviews/fixture-promotion-state-manifest-20260529.json`

| Field | Value |
|---|---|
| `fixture_state` | `absent` |
| `promotion_allowed` | `false` |
| `blocks_minimum_v1` | `true` |
| `blocks_v1` | `true` |
| `promotion_blockers` | `strict_golden_not_configured`; `fixture_promotion_absent` |

This gate did not mutate the manifest. The old manifest still says `strict_golden_not_configured`; this rerun produces new evidence for review, but updating fixture/preflight/manifest state requires a separate controller-accepted gate.

## Manual Verification Ledger

Because same-fund unavailable rows remain, this ledger is required by the accepted plan. No fixes are inferred here.

| fund_code | report_year | field_name | sub_field | priority | machine_status | expected_value_summary | actual_value_summary | source_anchor | machine_reason | manual_question | owner | next_gate | blocks_minimum_v1 | blocks_full_v1 | prohibited_action |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 006597 | 2024 | `product_profile` | `investment_objective` | P1 | unavailable | `在严格控制风险的前提下...` | empty | `年报2024 §2 page-5 page-5-table-1 investment_objective` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `product_profile` | `style_positioning` | P1 | unavailable | `本基金为债券型基金...` | empty | `年报2024 §2 page-5 page-5-table-1 style_positioning` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `manager_strategy_text` | `strategy_summary` | P0 | unavailable | `2024年债市整体表现震荡走牛...` | empty | `年报2024 §4 strategy_summary` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 extractor projection owner | `006597 extractor projection gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `manager_strategy_text` | `market_outlook` | P0 | unavailable | `国际方面，美国大选结果揭晓后...` | empty | `年报2024 §4 market_outlook` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 extractor projection owner | `006597 extractor projection gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `manager_alignment` | `manager_holding` | P1 | unavailable | `基金经理持有...A 10~50...` | empty | `年报2024 §9 page-64 page-64-table-2 manager_holding` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `manager_alignment` | `employee_holding` | P1 | unavailable | `从业人员持有本基金...` | empty | `年报2024 §9 page-64 page-64-table-1 employee_holding` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `holder_structure` | `institutional_holder` | P1 | unavailable | `44.56%` | empty | `年报2024 §9 page-63 page-63-table-1 institutional_holder` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `holder_structure` | `individual_holder` | P1 | unavailable | `55.44%` | empty | `年报2024 §9 page-63 page-63-table-1 individual_holder` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `share_change` | `beginning_share` | P1 | unavailable | `7,699,969,800.13` | empty | `年报2024 §10 page-65 page-65-table-0 share_change` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `share_change` | `ending_share` | P1 | unavailable | `5,711,224,267.09` | empty | `年报2024 §10 page-65 page-65-table-0 share_change` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |
| 006597 | 2024 | `share_change` | `net_change` | P1 | unavailable | `-1,988,745,533.04` | empty | `年报2024 §10 page-65 page-65-table-0 share_change` | snapshot 未显式暴露该 golden 子字段 | Does current snapshot expose the reviewed golden subfield as comparable value? | future 006597 same-fund unavailable field review owner | `006597 same-fund unavailable field review gate` | true | true | no guessing fixes; no golden edit; no runtime edit inside this gate |

## Non-Mutation Statement

This worker did not modify:

- production code, tests, scripts, runtime, score semantics, quality gate semantics, FQ0-FQ6, snapshot projection, renderer, Service/UI, Host/Agent/dayu;
- `reports/golden-answers/golden-answer.json`, golden fixtures, fixture manifest, residual manifest, preflight outputs, README, `docs/design.md`, or `docs/implementation-control.md`;
- QDII / FOF / `110020` / `004393` / `004194` state;
- PR, push, merge, release, promotion, stage, commit, or deletion state.

New report outputs are limited to:

- `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/`
- `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/`

## Validation

Validation commands required by the user and accepted plan:

```bash
python -m json.tool reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json >/dev/null
python -m json.tool reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.json >/dev/null
git diff --check -- docs/reviews/release-maintenance-006597-strict-correctness-rerun-evidence-20260529.md
git diff --name-only -- reports/golden-answers docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json fund_agent tests scripts pyproject.toml uv.lock docs/implementation-control.md docs/design.md
git status --short reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529 reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529
```

Actual results：pending until validation is run after artifact write.

Actual validation results after artifact write:

| Command | Result |
|---|---|
| `python -m json.tool reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json >/dev/null` | passed, no output |
| `python -m json.tool reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.json >/dev/null` | passed, no output |
| `git diff --check -- docs/reviews/release-maintenance-006597-strict-correctness-rerun-evidence-20260529.md` | passed, no output |
| `git diff --name-only -- reports/golden-answers docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json fund_agent tests scripts pyproject.toml uv.lock docs/implementation-control.md docs/design.md` | passed, no output |
| `git status --short reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529 reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529` | no output; generated report directories are ignored by git |
| `ls reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529` | `golden_set.json`, `score.json`, `score.md` present |
| `ls reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529` | `quality_gate.json`, `quality_gate.md` present |

## Final Decision Candidate

| Field | Value |
|---|---|
| `decision` | `blocked_pending_same_fund_unavailable_field_review` |
| `clean_pass` | `false` |
| `promotion_prep_candidate` | `false` |
| `promoted` | `false` |
| `fixture_state` | `absent` |
| `promotion_allowed` | `false` |
| `blocks_minimum_v1` | `true` |
| `blocks_full_v1` | `true` |
| `next_gate` | `006597 same-fund unavailable field review gate`; P0 `manager_strategy_text` rows likely require `006597 extractor projection gate` if controller accepts projection as root cause |

Self-check: pass.
