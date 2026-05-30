# 006597 Strict Correctness Rerun / Same-Fund Unavailable Field Review — Evidence Review (GLM)

日期：2026-05-30

角色：AgentGLM 独立 implementation/evidence reviewer。本文是 review artifact，不启动 gateflow / phaseflow，不修改代码、文档、报告、manifest、golden file 或 control doc，不 stage、不 commit、不 push、不 PR、不 merge、不 release、不 promote、不 rerun、不 fix。

Review targets:
- `docs/reviews/release-maintenance-006597-strict-correctness-rerun-evidence-20260529.md`（evidence artifact）
- `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/score.json`, `score.md`, `golden_set.json`
- `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/quality_gate.json`, `quality_gate.md`

Accepted plan: `docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-20260529.md`

Accepted plan reviews: MiMo `PASS`; GLM `PASS_WITH_FINDINGS`（F1 fee_schedule P0 golden-row gap）

## Verification Criteria Results

### 1. Rerun used golden-answer.json and 006597-specific output paths

**Verdict: PASS**

Evidence:
- Evidence artifact line 21: command uses `--golden-answer-path reports/golden-answers/golden-answer.json`。
- score.json confirms `golden_answer_path = "reports/golden-answers/golden-answer.json"`。
- Output dir: `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/` — new 006597-specific path，不覆盖 accepted `bond-risk-drawdown-nav-006597-2024-20260529`。
- Quality output: `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/` — 同样新路径。
- Both commands exit status = 0。

### 2. Correctness summary accurate

**Verdict: PASS**

| Field | Evidence artifact claim | score.json actual | Match |
|---|---|---|---|
| `coverage_scope` | `partially_covered` | `partially_covered` | ✅ |
| `total_records` | 150 | 150 | ✅ |
| `comparable_records` | 9 | 9 | ✅ |
| `matched_records` | 9 | 9 | ✅ |
| `mismatched_records` | 0 | 0 | ✅ |
| `unavailable_records` | 141 | 141 | ✅ |
| `skipped_records` | 29 | 29 | ✅ |
| `accuracy_rate` | 1.0 | 1.0 | ✅ |
| `golden_answer_path` | `reports/golden-answers/golden-answer.json` | Same | ✅ |
| `covered_fund_codes` | `006597` | `["006597"]` | ✅ |

Unavailable breakdown verified:
- Same-fund 006597 unavailable: 11（counted from `record_results[]` where `fund_code=="006597"` and `status=="unavailable"`）
- Cross-fund unavailable: 130（counted from `record_results[]` where `fund_code!="006597"` and `status=="unavailable"`）
- Total: 11 + 130 = 141 ✅

### 3. Same-fund row table accurate: 9 matched, 11 unavailable

**Verdict: PASS**

Score.json `record_results[]` for `fund_code=="006597"` returns exactly 20 records:

Matched (9):
| field_name | sub_field | Evidence artifact status | score.json status |
|---|---|---|---|
| basic_identity | fund_name | match | match ✅ |
| basic_identity | fund_code | match | match ✅ |
| basic_identity | management_company | match | match ✅ |
| basic_identity | custodian | match | match ✅ |
| basic_identity | inception_date | match | match ✅ |
| benchmark | benchmark_name | match | match ✅ |
| classified_fund_type | fund_type | match | match ✅ |
| nav_benchmark_performance | nav_growth_rate | match | match ✅ |
| nav_benchmark_performance | benchmark_return_rate | match | match ✅ |

Unavailable (11):
| field_name | sub_field | Priority | Evidence artifact status | score.json status |
|---|---|---|---|---|
| product_profile | investment_objective | P1 | unavailable | unavailable ✅ |
| product_profile | style_positioning | P1 | unavailable | unavailable ✅ |
| manager_strategy_text | strategy_summary | P0 | unavailable | unavailable ✅ |
| manager_strategy_text | market_outlook | P0 | unavailable | unavailable ✅ |
| manager_alignment | manager_holding | P1 | unavailable | unavailable ✅ |
| manager_alignment | employee_holding | P1 | unavailable | unavailable ✅ |
| holder_structure | institutional_holder | P1 | unavailable | unavailable ✅ |
| holder_structure | individual_holder | P1 | unavailable | unavailable ✅ |
| share_change | beginning_share | P1 | unavailable | unavailable ✅ |
| share_change | ending_share | P1 | unavailable | unavailable ✅ |
| share_change | net_change | P1 | unavailable | unavailable ✅ |

P0 unavailable: `manager_strategy_text.strategy_summary` + `market_outlook` = 2 rows。These block minimum_v1 per plan rules.

P1 unavailable: 9 rows across product_profile(2), manager_alignment(2), holder_structure(2), share_change(3)。

Priority assignments verified against `docs/design.md` §7.3 line 743-744: P0 = basic_identity, classified_fund_type, benchmark, nav_benchmark_performance, fee_schedule, manager_strategy_text; P1 = product_profile, index_profile, tracking_error, turnover_rate, holder_structure, manager_alignment, holdings_snapshot, share_change。All correct。

### 4. Manual ledger includes all 11 unavailable rows with required columns

**Verdict: PASS**

Evidence artifact lines 133-145 contain a 16-column ledger for all 11 same-fund unavailable rows:
- `fund_code`, `report_year`, `field_name`, `sub_field`, `priority`, `machine_status`, `expected_value_summary`, `actual_value_summary`, `source_anchor`, `machine_reason`, `manual_question`, `owner`, `next_gate`, `blocks_minimum_v1`, `blocks_full_v1`, `prohibited_action` — all 16 columns present for each row。
- All 11 rows have `blocks_minimum_v1=true` and `blocks_full_v1=true`。
- All 11 rows have `prohibited_action` = "no guessing fixes; no golden edit; no runtime edit inside this gate"。
- `owner` correctly names future gate owners (not individuals)。
- `next_gate` correctly uses one of the plan's four allowed values: `006597 same-fund unavailable field review gate` for 9 P1 rows; `006597 extractor projection gate` for 2 P0 `manager_strategy_text` rows。
- `manual_question` is the smallest same-source verification question as required by the plan。

### 5. fee_schedule P0 no-current-golden-row limitation is present

**Verdict: PASS**

Evidence artifact line 96: "`fee_schedule` is P0 in `docs/design.md` §7.3, but there are no current 006597 `fee_schedule` golden rows in `reports/golden-answers/golden-answer.json`. Therefore even a hypothetical clean pass over the current 20 rows would not prove full P0 coverage."

This addresses GLM plan review F1. The limitation is clearly stated and correctly scoped。

### 6. Quality gate status/issues accurate, no FQ1 mismatch/block

**Verdict: PASS**

Evidence artifact claims: `status=warn`, 6 issues (FQ2×3, FQ2F×1, FQ0×1, FQ4×1), no FQ1。

Verified from quality_gate.json:
| # | rule_code | severity | fund_code | field_name | priority | Evidence claim | Actual | Match |
|---|---|---|---|---|---|---|---|---|
| 1 | FQ2 | warn | null | turnover_rate | P1 | ✓ | ✓ | ✅ |
| 2 | FQ2 | warn | null | holder_structure | P1 | ✓ | ✓ | ✅ |
| 3 | FQ2 | warn | null | share_change | P1 | ✓ | ✓ | ✅ |
| 4 | FQ2F | warn | 006597 | null | P1 | ✓ | ✓ | ✅ |
| 5 | FQ0 | info | 006597 | null | null | ✓ | ✓ | ✅ |
| 6 | FQ4 | warn | 006597 | null | null | ✓ | ✓ | ✅ |

No FQ1 present。✅

### 7. Fixture state absent, promotion_allowed=false, not promoted

**Verdict: PASS**

Evidence artifact final decision (lines 188-200):

| Field | Evidence artifact value | Verified |
|---|---|---|
| `decision` | `blocked_pending_same_fund_unavailable_field_review` | ✅ consistent with same-fund unavailable |
| `clean_pass` | `false` | ✅ (11 same-fund unavailable exist) |
| `promotion_prep_candidate` | `false` | ✅ |
| `promoted` | `false` | ✅ |
| `fixture_state` | `absent` | ✅ matches manifest `absent` |
| `promotion_allowed` | `false` | ✅ matches manifest `false` |
| `blocks_minimum_v1` | `true` | ✅ matches manifest `true` |
| `blocks_full_v1` | `true` | ✅ matches manifest `true` |

Fixture manifest unchanged: `fixture_state=absent`, `promotion_allowed=false`, `blocks_minimum_v1=true`, `blocks_v1=true`。✅

### 8. No golden/fixture/manifest/preflight/runtime/control-doc/design/FQ semantic changes

**Verdict: PASS**

Evidence:
- Forbidden diff: `git diff --name-only -- reports/golden-answers docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json fund_agent tests scripts pyproject.toml uv.lock docs/implementation-control.md docs/design.md` → no output, EXIT=0。✅
- Rerun output dirs (`reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/`, `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/`) are untracked/ignored by git。✅
- Non-mutation statement (lines 148-160) correctly lists all prohibited mutations。
- No runtime/test changes; ruff/pytest correctly not run per plan (docs/evidence-only rerun, no Python code modified)。

### 9. Validation commands passed

**Verdict: PASS**

| Command | Expected | Actual |
|---|---|---|
| `python -m json.tool score.json` | Pass | EXIT=0 ✅ |
| `python -m json.tool quality_gate.json` | Pass | EXIT=0 ✅ |
| `git diff --check -- evidence artifact` | No output | No output, EXIT=0 ✅ |
| Forbidden diff | No output | No output, EXIT=0 ✅ |
| `git status --short` rerun dirs | Ignored/untracked | No output (gitignored) ✅ |
| `ls` rerun dirs | Files present | score.json, score.md, golden_set.json; quality_gate.json, quality_gate.md ✅ |

## Findings

No findings.

## Cross-Reference: Accepted Plan Compliance

| Plan requirement | Evidence artifact compliance |
|---|---|
| Use golden-answer.json rerun | ✅ Confirmed by command and score.json |
| New 006597-specific output paths | ✅ Both score and quality in new dirs |
| Not-configured fallback | Not needed (rerun produced `partially_covered`) |
| Mismatch handling | Not triggered (0 mismatches) |
| Same-fund unavailable handling | ✅ Correctly routes to `blocked_pending_same_fund_unavailable_field_review` |
| Clean pass handling | Not triggered (11 same-fund unavailable) |
| Manual ledger for 11 rows | ✅ Complete with 16 columns each |
| fixture_state=absent preserved | ✅ |
| promotion_allowed=false preserved | ✅ |
| fee_schedule P0 gap noted | ✅ Line 96 |
| No golden/runtime/manifest mutation | ✅ Forbidden diff clean |
| Validation matrix executed | ✅ All 7 checks pass |
| Old untracked follow-up artifacts read-only only | ✅ Line 94 treats as predictor only |

## Cross-Reference: Plan Review F1 (fee_schedule gap)

GLM plan review F1 noted that fee_schedule P0 has no golden rows for 006597. Evidence artifact line 96 explicitly addresses this. The implementation worker correctly incorporated this finding.

## Structural Assessment

- **Verdict section**: Clear and upfront. Decision candidate matches plan's result handling rule for same-fund unavailable.
- **Commands executed**: Exact commands with exit status and output paths.
- **Correctness totals**: Complete with all required fields including skipped_records and accuracy_rate.
- **Same-fund table**: All 20 records listed with field, subfield, status, expected/actual summary, source, reason.
- **Quality gate**: All 6 issues listed with rule_code, severity, fund_code, field_name, priority.
- **Manual ledger**: All 11 unavailable rows with all 16 required columns.
- **Non-mutation statement**: Comprehensive.
- **Validation results**: All checks pass.
- **fee_schedule limitation**: Explicitly noted.

## Conclusion

**PASS**

The evidence artifact satisfies the accepted plan. All 9 verification criteria pass with no findings. The implementation correctly:

- Used `reports/golden-answers/golden-answer.json` with new 006597-specific output paths
- Produced accurate correctness summary: `partially_covered`, 9 matched, 0 mismatch, 11 same-fund unavailable, 130 cross-fund unavailable
- Correctly identifies P0 `manager_strategy_text.strategy_summary` and `market_outlook` as unavailable rows that block minimum_v1
- Includes complete manual verification ledger for all 11 unavailable rows with all 16 required columns
- Notes fee_schedule P0 golden-row gap
- Preserves `fixture_state=absent` and `promotion_allowed=false`
- Decision is `blocked_pending_same_fund_unavailable_field_review` — not promotion_prep_candidate, not promoted
- No mutations to golden/fixture/manifest/preflight/runtime/control-doc/design/FQ semantics
- All validation commands passed

No blocking issues remain for the evidence artifact itself. The gate outcome is `blocked` pending the `006597 same-fund unavailable field review gate` and `006597 extractor projection gate` for P0 `manager_strategy_text` rows.

## Artifact Path

`docs/reviews/release-maintenance-006597-strict-correctness-rerun-evidence-review-glm-20260529.md`

## Self-check

Self-check: pass
