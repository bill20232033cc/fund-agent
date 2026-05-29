# 006597 Strict Correctness Rerun / Same-Fund Unavailable Field Review Plan

日期：2026-05-29

角色：AgentCodex planning worker。本文只写 plan，不实现、不 rerun、不修改 reports / golden / fixtures / manifests / runtime / control doc，不 stage、不 commit、不 push、不 PR、不 merge、不 release、不 promote。

## Goal

为 `006597 / 2024` 制定 heavy gate implementation plan：

1. 必须用 `reports/golden-answers/golden-answer.json` 对最新 006597 snapshot 执行 strict correctness rerun 或同等核对。
2. 如果 rerun 通过、无 mismatch、且无 same-fund unavailable，只能标记为 `promotion_prep_candidate`，不得 promoted。
3. 如果 rerun 出现 mismatch 或 same-fund unavailable，生成字段级人工核验台账；不猜测修复、不改 golden answer、不改 runtime。
4. 保持 `fixture_state=absent`、`promotion_allowed=false`，直到 separate fixture promotion gate explicitly accepts changes。

## Non-Goals

- 不修改 production code、tests、scripts、runtime、score semantics、quality gate / FQ0-FQ6、snapshot projection、renderer、Service/UI、Host/Agent/dayu。
- 不修改 `reports/golden-answers/golden-answer.json`、golden fixtures、fixture manifest、residual manifest、preflight outputs、README、`docs/design.md`、`docs/implementation-control.md`。
- 不处理 QDII / FOF / `110020` / `017641` / `004393` / `004194`。
- 不执行 PR、push、merge、release、golden promotion、fixture promotion 或 manifest mutation。
- 不使用 `extra_payload` 隐藏显式参数。

## Gate Classification

Gate classification：`heavy`。

依据：本 gate 影响 strict golden correctness、baseline/golden readiness、fixture promotion-prep eligibility 和 minimum v1 readiness。按 `AGENTS.md`，baseline/golden promotion readiness 相关 gate 必须使用 heavy；分类不确定时也应选择更重一级。

## Truth Sources Read

| Source | Plan usage |
|---|---|
| `AGENTS.md` | heavy gate、四层边界、禁止 promotion / release / external mutation、`FundDocumentRepository` 边界、显式参数约束 |
| `docs/design.md` §7.3 / §7.4 | P0/P1/P2 priority、correctness / quality gate semantics、不能把少量 golden rows 当全域证明 |
| `docs/implementation-control.md` | 当前 phase / current gate / next entry point：006597 same-fund unavailable review or strict correctness rerun |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` | Route 1 顺序；006597 bond blocker closed but strict correctness unresolved |
| `docs/reviews/release-maintenance-phase-roadmap-consolidation-controller-judgment-20260529.md` | Roadmap accepted；旧 follow-up artifacts remain unaccepted workspace evidence |
| `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md` | 006597 current decision `needs_future_gate`; rerun required with golden answer |
| `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` | 006597 not promotion-ready; next step strict correctness score rerun |
| Preflight JSON / MD | 006597 `deferred_with_owner`; blockers `strict_golden_not_configured`, `fixture_promotion_absent`; bond blocker resolved item |
| Residual / fixture manifests | 006597 `fixture_state=absent`, `promotion_allowed=false`, `blocks_minimum_v1=true`, `blocks_v1=true` |
| `reports/golden-answers/golden-answer.json` | 006597 has 20 reviewed rows |
| Latest accepted 006597 artifacts | `bond-risk-drawdown-nav-006597-2024-20260529` snapshot / score / quality; latest accepted score is `not_configured` because no golden answer path was supplied |
| Existing untracked follow-up artifacts | Read-only, unaccepted workspace evidence only; may inform stop-condition shape but cannot be accepted truth without review/controller judgment |

## Current Evidence Summary

| Evidence | Current value |
|---|---|
| Fund / year | `006597 / 2024` |
| Fund name | `国泰利享中短债债券A` |
| App category / classified type | `国内债券类` / `bond_fund` |
| Golden-answer rows | 20 rows for `006597` |
| Latest accepted snapshot | `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl` |
| Latest accepted score | `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json` |
| Latest accepted correctness | `coverage_scope=not_configured`; `total_records=0`; `comparable_records=0`; no golden answer path supplied |
| Latest accepted quality | `warn`; FQ2 warns for `turnover_rate`, `holder_structure`, `share_change`; FQ0 info `strict golden answer 未配置`; FQ4 missing-rate warn |
| Preflight | `deferred_with_owner`; `strict_golden_coverage=covered`; `fixture_promotion_state=absent`; blockers `strict_golden_not_configured`, `fixture_promotion_absent`; warning `quality_gate_warn` |
| Fixture manifest | `fixture_state=absent`; `promotion_allowed=false`; `blocks_minimum_v1=true`; `blocks_v1=true` |
| Bond blocker | `bond_risk_evidence_missing` closed as resolved context only by accepted NAV-derived drawdown metric gate |

Current accepted evidence is insufficient for promotion-prep because strict correctness was not configured against the golden answer JSON.

## Existing Untracked Follow-Up Artifacts

Workspace currently contains untracked old follow-up artifacts:

- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md`
- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md`
- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md`
- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md`
- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md`
- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md`
- `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json`

Plan disposition:

- Treat them as read-only, unaccepted workspace evidence.
- Do not stage, delete, rename, edit, or silently promote them.
- They can be cited only as prior unaccepted evidence that a 006597 rerun may trigger same-fund unavailable review.
- They can be accepted only after a dedicated review/controller judgment explicitly accepts those artifacts and reconciles them with this 006597-specific gate.
- Preferred implementation path is a new 006597-specific evidence artifact and a new 006597-specific rerun output path to avoid mixing old multi-fund follow-up state with current 006597 gate truth.

## Required Rerun / Verification Commands

Implementation worker must run the strict correctness score rerun unless controller explicitly accepts the old untracked rerun artifacts after review. Use a 006597-specific output directory:

```bash
uv run fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl \
  --errors-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/errors.jsonl \
  --golden-answer-path reports/golden-answers/golden-answer.json \
  --output-dir reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529
```

Expected outputs:

- `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json`
- `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.md`
- `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/golden_set.json`

Then run quality gate as consistency evidence, not as semantic change:

```bash
uv run fund-analysis quality-gate \
  --score-path reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json \
  --output-dir reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529
```

Expected outputs:

- `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.json`
- `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.md`

No golden answer, fixture, manifest, snapshot, or runtime file may be edited to make these commands pass.

## Required Summaries In Implementation Evidence

The implementation evidence artifact must include:

| Summary | Required fields |
|---|---|
| Correctness totals | `coverage_scope`, `total_records`, `comparable_records`, `matched_records`, `mismatched_records`, `unavailable_records`, `skipped_records`, `accuracy_rate`, `golden_answer_path` |
| Same-fund 006597 rows | All `record_results[]` where `fund_code=="006597"` with `field_name`, `sub_field`, `status`, expected value summary, actual value summary, source, reason |
| Matched rows | Exact list and count |
| Mismatch rows | Exact list and count; never auto-fix |
| Unavailable rows | Exact list and count; distinguish same-fund 006597 unavailable from cross-fund unavailable in the 150-row corpus |
| Quality gate state | `status`, issue list, especially FQ1 mismatch/block if any, FQ2/FQ2F warnings, FQ0 status |
| Fixture state | Current manifest value `fixture_state=absent`, `promotion_allowed=false`, `blocks_minimum_v1=true`, `blocks_v1=true` |
| Bond blocker | State as resolved context only; not promotion evidence |
| Output paths | Score / score.md / golden_set / quality_gate paths |
| Forbidden mutation statement | No golden, fixture, manifest, runtime, FQ, snapshot, preflight, PR/release mutation |

## Result Handling Rules

### If Rerun Is Not Configured

If output remains `coverage_scope=not_configured` or `correctness` unavailable because the golden answer path was not consumed:

- Decision: `blocked_machine_setup_failure`.
- Do not run manual field review.
- Evidence must include command, exit status, output paths, parsed correctness object, and why the golden path was not consumed.
- Stop; do not modify code to fix it inside this gate.

### If Mismatch Exists

If `mismatched_records > 0`:

- Decision: `blocked_pending_mismatch_manual_review`.
- Produce field-level manual verification ledger for mismatch rows.
- Do not edit golden answer or extractor.
- Do not infer that golden is wrong or runtime is wrong until same-source evidence confirms root cause.

### If Same-Fund Unavailable Exists

If any `record_results[]` for `fund_code=="006597"` has `status=unavailable`:

- Decision: `blocked_pending_same_fund_unavailable_field_review`.
- Produce field-level manual verification ledger for same-fund unavailable rows.
- Do not treat cross-fund unavailable rows as 006597 failure.
- Do not guess fixes; classify only machine state and required owner / next gate.

### If Clean Pass

Clean pass requires:

- `mismatched_records=0`;
- no same-fund 006597 unavailable rows;
- same-fund expected 006597 rows all matched or explicitly not applicable under accepted current scoring semantics;
- quality gate has no FQ1/block caused by correctness mismatch.

If clean pass occurs:

- Decision may be only `promotion_prep_candidate`.
- It is not `promoted`.
- `promotion_allowed` remains `false`.
- `fixture_state` remains `absent` unless a separate fixture promotion-prep gate updates it after review.
- Evidence must state that a separate promotion gate is still required.

## Manual Verification Ledger Format

If mismatch or same-fund unavailable remains, create a table in the implementation evidence artifact:

| fund_code | report_year | field_name | sub_field | priority | machine_status | expected_value_summary | actual_value_summary | source_anchor | machine_reason | manual_question | owner | next_gate | blocks_minimum_v1 | blocks_full_v1 | prohibited_action |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Rules:

- `priority` must use `docs/design.md` §7.3.
- `expected_value_summary` and `actual_value_summary` should be short summaries, not full long text dumps.
- `source_anchor` must come from golden answer / score evidence where present.
- `manual_question` must be the smallest same-source verification question, e.g. "Does current snapshot expose the reviewed golden subfield as comparable value?" or "Does annual-report anchor support expected row?"
- `owner` must name a future gate owner, not an individual.
- `next_gate` must be one of: `006597 same-fund unavailable field review gate`, `006597 mismatch evidence confirmation gate`, `006597 extractor projection gate`, or `006597 golden fact-freeze gate`.
- `blocks_minimum_v1=true` for unresolved P0 rows and for any unresolved same-fund strict-correctness blocker that prevents promotion-prep.
- `blocks_full_v1=true` for all unresolved mismatch / unavailable rows unless controller explicitly defers them.
- `prohibited_action` must say no guessing fixes, no golden edit, no runtime edit inside this gate.

## Expected 006597 Golden Row Priority Map

Current `reports/golden-answers/golden-answer.json` has 20 reviewed 006597 rows. Priority source is `docs/design.md` §7.3:

| Priority | 006597 fields in current golden answer |
|---|---|
| P0 | `basic_identity.*`; `benchmark.benchmark_name`; `classified_fund_type.fund_type`; `nav_benchmark_performance.*`; `manager_strategy_text.strategy_summary`; `manager_strategy_text.market_outlook` |
| P1 | `product_profile.investment_objective`; `product_profile.style_positioning`; `manager_alignment.*`; `holder_structure.*`; `share_change.*` |
| P2 | none in current 006597 golden rows |

Implementation evidence must compute actual matched / mismatch / unavailable breakdown by this map after rerun.

## Validation Matrix

| Check | Command / method | Expected |
|---|---|---|
| Plan whitespace | `git diff --check -- docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-20260529.md` | No output |
| Plan-only forbidden diff | `git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json docs/implementation-control.md docs/design.md reports/golden-answers` | No output during planning |
| Score output parses | `python -m json.tool reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json >/dev/null` | Pass after implementation rerun |
| Quality output parses | `python -m json.tool reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.json >/dev/null` | Pass after implementation quality run |
| Evidence artifact diff | `git diff --check -- docs/reviews/release-maintenance-006597-strict-correctness-rerun-evidence-20260529.md` | No output if evidence artifact is produced |
| Golden / fixture / manifest diff | `git diff --name-only -- reports/golden-answers docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | No output |
| Runtime diff | `git diff --name-only -- fund_agent tests scripts pyproject.toml uv.lock` | No output |
| Reports diff review | `git status --short reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529 reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529` | Only intended new rerun outputs may appear |

If running existing score/snapshot commands changes reports outside the explicit new output dirs, stop and report. Stage only accepted artifacts after controller instruction; this planning worker must not stage anything.

If Python/runtime changes would be required to run or parse the score, stop and do not implement. A separate implementation gate is required.

`ruff` / `pytest` are not required for docs/evidence-only rerun. They become required only if runtime or test files are changed, which this gate forbids.

## Review Plan

Preferred review after midnight:

- AgentMiMo plan review.
- AgentGLM plan review.

Reviewers must verify:

- The plan is 006597-specific and does not silently accept old untracked multi-fund follow-up artifacts.
- The rerun command uses `reports/golden-answers/golden-answer.json`.
- Output paths are new 006597-specific paths and do not overwrite accepted reports.
- Clean pass handling is candidate-only, not promotion.
- Mismatch / unavailable handling produces field-level ledger and forbids guessed fixes.
- `fixture_state=absent` and `promotion_allowed=false` remain unchanged.
- No QDII / FOF / `110020` / `004393` / `004194` implementation work is authorized.
- No manifest, golden, fixture, runtime, FQ, control-doc, PR/release mutation is authorized.

## Stop Conditions

Stop before or during implementation if:

- rerun requires editing code, tests, score semantics, quality gate semantics, snapshot projection, golden answer, fixture, manifest, preflight, or control doc;
- command output contains mismatch or same-fund unavailable and someone proposes an immediate fix instead of a ledger;
- clean pass is described as `promoted`, `promotion_allowed=true`, or fixture state change;
- old untracked follow-up artifacts are staged, deleted, or accepted without review/controller judgment;
- direct PDF/cache/source helper access is needed;
- QDII / FOF / `110020` / `004393` / `004194` scope appears;
- Host/Agent/dayu work appears;
- PR, push, merge, release, promotion, or external mutation is requested.

## Completion Report Format

Implementation worker final report must include:

- plan artifact path and implementation evidence path;
- exact rerun command executed;
- score output path and quality output path;
- correctness totals;
- same-fund 006597 matched / mismatch / unavailable counts;
- decision (`promotion_prep_candidate`, `blocked_pending_same_fund_unavailable_field_review`, `blocked_pending_mismatch_manual_review`, or `blocked_machine_setup_failure`);
- `fixture_state=absent`, `promotion_allowed=false`;
- validation results, including forbidden diff;
- whether old untracked follow-up artifacts were read-only only;
- next gate;
- `Self-check: pass` or `Self-check: blocked` with reason.

## Planning Validation

Before completion of this planning slice, run:

```bash
git diff --check -- docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-20260529.md
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json docs/implementation-control.md docs/design.md reports/golden-answers
```

Expected result: both commands produce no output.

Self-check: pass for plan-only scope.
