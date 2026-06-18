# 004393 / 004194 / 006597 Strict Correctness Follow-up Plan Review — AgentDS

日期：2026-05-29

角色：AgentDS，independent plan reviewer；不是 controller，不做实现。

## Verdict

**PASS**

本 plan 与 AGENTS.md、docs/design.md、docs/implementation-control.md、controller judgment、decision artifact、fixture promotion state manifest、golden readiness residual disposition manifest 和 golden readiness preflight 输出一致。五个重点挑战问题均通过验证。无需 required fixes；两条 observations 供实现 worker 参考。

## Truth Sources Verified

| Source | Path | Key constraints checked |
|---|---|---|
| AGENTS.md | repo root | Gate 分类 `heavy` 正确；四层边界未违反；显式参数未隐藏在 extra_payload；禁止 promotion 隐含授权 |
| design.md | `docs/design.md` | extraction-score CLI 接口（§9.0）、quality-gate CLI 接口（§9.0）、golden answer correctness 语义（§7.3/§7.4/§7.6）、P0/P1 字段优先级（§7.3）、FQ0-FQ6 语义（§7.4）均与 plan 的 rerun 命令和约束一致 |
| implementation-control.md | `docs/implementation-control.md` | Next entry point 确认为 `004393 / 004194 / 006597 strict correctness follow-up gate`；allowed scope 与 plan non-goals 一致；golden promotion 明确 excluded |
| controller judgment | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` | 004393=`conditional_candidate_pending_partial_coverage_decision`；004194=`conditional_candidate_pending_p0_coverage_decision`；006597=`needs_future_gate`；全部 `promotion_allowed=false` |
| decision artifact | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md` | 004393 P0 9/11、P1 0/10 分解；004194 index_profile-only 5/5；006597 not_configured → 需要 golden answer rerun |
| fixture promotion state manifest | `docs/reviews/fixture-promotion-state-manifest-20260529.json` | 全部 entry `promotion_allowed=false`；004393/004194/006597 均为 `fixture_state=absent`、`blocks_minimum_v1=true` |
| golden readiness residual disposition | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | 006597 blockers 含 `strict_golden_not_configured` 和 `fixture_promotion_absent`；bond blocker 已 resolved |
| golden readiness preflight | `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` | overall_status=block；006597 strict_golden_coverage=covered 但 correctness not_configured |

## Challenge 1: 006597 Rerun Command — Public CLI Completeness

**Verdict: PASS**

Plan 的命令：

```bash
uv run fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl \
  --errors-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/errors.jsonl \
  --golden-answer-path reports/golden-answers/golden-answer.json \
  --output-dir reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529
```

逐项验证：

- `extraction-score` 子命令存在，通过 `uv run fund-analysis extraction-score --help` 确认
- `--snapshot-path`：必需参数，snapshot 文件存在（22076 bytes，有效 JSONL）
- `--errors-path`：可选参数，errors.jsonl 存在（0 bytes，空文件；无失败基金，符合预期）
- `--golden-answer-path`：可选参数，golden-answer.json 存在（140962 bytes，含 150 条 golden 记录覆盖 11 只基金，其中 006597 有 20 条记录）
- `--output-dir`：可选参数，指向新目录
- `--source-csv`：未提供，使用默认值 `docs/code_20260519.csv`，与原始 snapshot 来源一致

Quality gate 命令：

```bash
uv run fund-analysis quality-gate \
  --score-path reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json \
  --output-dir reports/quality-gate-runs/strict-correctness-follow-up-006597-2024-20260529
```

- `quality-gate` 子命令存在，`--score-path` 和 `--output-dir` 均为有效参数
- 无需 `--source-csv`（quality-gate CLI 不接受此参数）

**Observation 1**（无需修复）：golden-answer.json 中所有 150 条记录的 `report_year` 均为 `null`。代码按兼容性默认处理为 2024。plan 不需要提及此实现细节，但实现 worker 应注意：rerun 后 `correctness.golden_answer_path` 将指向全量 golden answer（含 11 只基金的 150 条记录），其中 130 条 cross-fund 记录将显示为 `unavailable`。plan 的 result handling 规则（line 102-103）已正确处理此情况。

## Challenge 2: Mismatch/Unavailable — Stop Condition Handling

**Verdict: PASS**

Plan 的 result handling 规则（lines 100-104）：

| 场景 | 处理方式 | 是否对齐 stop conditions |
|---|---|---|
| `correctness` 仍为 `unavailable`/`not_configured` | 归类为 machine setup failure，不归因为 fund evidence failure | ✅ 不编辑 golden answer（stop condition line 150） |
| `mismatched_records > 0` | 仅对 mismatched records 打开 manual evidence confirmation；不编辑 golden answer | ✅ 不编辑 golden answer；不设置 promotion_allowed=true（stop condition line 151） |
| `unavailable_records > 0` | 仅检查 same-fund 006597 unavailable records；不检查 cross-fund | ✅ 正确区分 same-fund vs cross-fund unavailable |
| 全部 comparable records matched 且无 same-fund unavailable | 记录 improved strict correctness 状态，但仍不标记 promotion-ready | ✅ 不进入 promotion（stop condition line 151） |
| bond blocker closure 被用作 strict correctness 替代 | STOP（line 153） | ✅ 显式 stop condition |

Stop conditions（lines 150-156）覆盖完整：不编辑 golden answer、不设 promotion_allowed=true、不升级 partial coverage 为 full readiness、不将 bond blocker closure 代用为 strict correctness evidence、不触发 preflight rerun 或 manifest consumption、不拉入 QDII/FOF/110020 scope。

## Challenge 3: 004393 Partial Coverage — 未被升级为 Minimum V1 Promotion-Prep

**Verdict: PASS**

Plan 对 004393 的处理（lines 82-87）：

- 显式声明 `not_minimum_v1_promotion_prep_by_default`
- 记录 `promotion_allowed=false`、`fixture_state=absent`
- 明确 `strict_golden_coverage=covered`（preflight 口径）不等于 full correctness readiness
- Required residual owner：future partial-coverage / extractor coverage decision gate
- 升级条件：只有 controller 显式接受 P0 `9/11` 和 P1 `0/10` 的 residual risk 后才允许

当前 score.json 验证：004393 `total_records=150`、`comparable_records=9`、`matched_records=9`、`mismatched=0`、`unavailable=141`，与 plan 的 `9/150` 描述一致。`record_results[]` 中 004393 有 21 条记录（含 None result 值；按 priority 分类汇总的正确性取决于 golden answer priority 映射，不在本 plan scope 内）。

## Challenge 4: 004194 index_profile-only — 未被误判为 Full Fixture Ready

**Verdict: PASS**

Plan 对 004194 的处理（lines 91-95）：

- 显式声明 `index_profile_only_candidate_not_full_fixture_ready`
- 不将 5 条 matched `index_profile.*` records 视为 full fixture readiness
- P0 strict correctness coverage 为 `0`
- Required residual owner：P0 strict correctness coverage gate；P15 tracking-error direct-disclosure evidence 保持独立

当前 score.json 验证：004194 `total_records=150`、`comparable_records=5`、`matched=5`。`record_results[]` 中 004194 确为 5 条 `index_profile.*` 记录（benchmark_text、benchmark_identity_status、methodology_availability、constituents_availability、source_tier）。`unavailable_records=145` 均为 cross-fund 004393 golden records，非 004194 intra-fund 缺失。

Plan 另有 stop condition（line 95）：若 implementation wording 暗示 004194 是 full `promotion-prep-ready` 则停止。这是正确的防御性约束。

## Challenge 5: Manifest / Preflight / Promotion / FQ — 不变性验证

**Verdict: PASS**

Plan 的 Manifest / Decision / Preflight Answers 表（lines 108-113）：

| 问题 | Plan 答案 | 验证 |
|---|---|---|
| Update fixture manifest? | No | ✅ fixture-promotion-state-manifest 是 accepted control-plane evidence，且所有 3 行仍 `promotion_allowed=false`、`fixture_state=absent` |
| Add machine-readable decision artifact? | Yes, in implementation | ✅ 创建新的 control-plane JSON，但标注 `not_promotion_manifest=true` 和 `runtime_consumed=false` |
| Rerun preflight? | No in this gate | ✅ preflight 路径和 disposition 是 static accepted evidence；rerun 需单独 gate |

Plan scope and non-goals 确认：

- 不修改 golden answers / golden fixtures（line 48）
- 不更新 fixture promotion state manifest（line 49）
- 不更新 golden readiness residual disposition manifest（line 50）
- 不改变 score / quality / snapshot / FQ0-FQ6 语义（line 51）
- 不设 `promotion_allowed=true`（line 151）
- 不改变 FQ0-FQ6 语义（quality-gate rerun 约束，line 77）

Validation matrix 包含 `git diff -- reports/golden-answers docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` 期望 Empty（line 143），确保无 golden/fixture/manifest 变更。

## Observation 2: Quality Gate Rerun — 结果解释未定义

**Severity: Low，不要求修复**

Plan 将 quality-gate rerun 标记为 optional read-only consistency check（line 43、69-77），但不指定如何处理 rerun 结果与之前 run 的差异。当前 006597 quality gate 为 `warn`（issues: turnover_rate、holder_structure、share_change、fund-level P1、FQ0 golden not configured、FQ4 missing rate）。Rerun 后 golden not configured 的 FQ0/info 将消失（因为 `--golden-answer-path` 已提供），其他 warn 不变，gate 很可能仍为 `warn`。

若意外变为 `block`，plan 没有明确的升级路径。但 plan 的约束（不改变 FQ0-FQ6 语义、不用于推断 promotion readiness）已提供足够保护。实现 worker 只需记录 rerun 结果作为 evidence，不做语义变更。

## Findings Summary

| # | Category | Finding | Verdict |
|---|---|---|---|
| F1 | CLI completeness | 006597 extraction-score 和 quality-gate rerun 命令均使用 public CLI，全部参数有效 | PASS |
| F2 | 004393 partial coverage | 显式拒绝升级为 minimum v1 promotion-prep；promotion_allowed=false 保持不变 | PASS |
| F3 | 004194 index_profile-only | 显式拒绝将 5 条 index_profile.* 记录误判为 full fixture ready | PASS |
| F4 | Manifest/preflight 不变性 | 不更新 fixture manifest、不更新 residual disposition manifest、不 rerun preflight | PASS |
| F5 | Promotion/golden/FQ 不变性 | 不设 promotion_allowed=true、不改 golden answer/fixture、不改 FQ0-FQ6 语义 | PASS |
| F6 | Stop conditions | mismatch/unavailable 按用户停止条件处理；covered all invariants | PASS |
| F7 | Truth source consistency | 与 controller judgment、decision、manifest、preflight 全部一致 | PASS |

## Required Fixes

无。

## Observations for Implementation Worker

1. golden-answer.json 的 `report_year` 全部为 `null`（兼容默认 2024）。rerun 后 150 条 golden records 中仅 20 条 006597 records 为 comparable，其余 130 条 cross-fund 为 unavailable。按 plan line 102-103 过滤。
2. Quality gate rerun 结果若与之前 `warn` 不同，只记录为 evidence，不触发 promotion 推断或 FQ 语义变更。
