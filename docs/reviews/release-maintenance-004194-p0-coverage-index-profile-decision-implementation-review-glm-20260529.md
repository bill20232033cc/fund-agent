# 004194 P0 Coverage / Index Profile-Only Fixture Decision — Implementation Review (GLM)

日期：2026-05-30

角色：AgentGLM 独立 implementation reviewer。本文是 review artifact，不启动 gateflow / phaseflow，不修改代码、文档、报告、manifest、golden file 或 control doc，不提交、不 push、不 PR、不 merge、不 release、不 promotion。

Review targets:
- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md`（decision artifact）
- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-implementation-evidence-20260529.md`（evidence artifact）

Accepted plan: `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md`

Accepted plan reviews: MiMo `PASS`; GLM `PASS_WITH_FINDINGS`（F1 P16 provenance 措辞约束）

## Verification Criteria Results

### 1. Score correctness counts

| Field | Decision artifact claim | Evidence (score.json) | Verdict |
|---|---|---|---|
| `coverage_scope` | `covered` | `covered` | PASS |
| `total_records` | 150 | 150 | PASS |
| `comparable_records` | 5 | 5 | PASS |
| `matched_records` | 5 | 5 | PASS |
| `mismatched_records` | 0 | 0 | PASS |
| `unavailable_records` | 145 | 145 | PASS |

Source: `jq '.correctness | {coverage_scope,total_records,comparable_records,matched_records,mismatched_records,unavailable_records}' reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json`

### 2. Five matched rows identity and source

Decision artifact claims exactly five matched rows, all `index_profile.*`, all from `年报2024 §2 page-5 page-5-table-1 benchmark`.

Evidence from `score.json` `.correctness.record_results[] | select(.fund_code=="004194")`:

| field_name | sub_field | status | source |
|---|---|---|---|
| index_profile | benchmark_text | match | 年报2024 §2 page-5 page-5-table-1 benchmark |
| index_profile | benchmark_identity_status | match | 年报2024 §2 page-5 page-5-table-1 benchmark |
| index_profile | methodology_availability | match | 年报2024 §2 page-5 page-5-table-1 benchmark |
| index_profile | constituents_availability | match | 年报2024 §2 page-5 page-5-table-1 benchmark |
| index_profile | source_tier | match | 年报2024 §2 page-5 page-5-table-1 benchmark |

Verdict: PASS — exactly five rows, all `index_profile.*`, all `status=match`, source anchors consistent.

### 3. Same-fund P0 strict correctness coverage is 0

Decision artifact line 52: "Same-fund P0 strict correctness coverage | `0` comparable P0 rows; no 004194 P0 golden rows exist in current strict golden scope".

Evidence:
- `score.json` record_results for fund_code=004194: exactly 5 rows, all `index_profile.*`. No P0 fields present.
- `golden-answer.json` records for fund_code=004194: exactly 5 rows, all `index_profile.*`. No P0 fields present.
- `docs/design.md` §7.3 line 743: P0 = `basic_identity`, `classified_fund_type`, `benchmark`, `nav_benchmark_performance`, `fee_schedule`, `manager_strategy_text`. None of these appear in 004194 golden rows.

Verdict: PASS — P0 coverage is definitively 0.

### 4. 145 unavailable are cross-fund score rows, not same-fund intra-fund missing fields

Decision artifact line 63: "The score-level `unavailable_records=145` are unavailable records from the broader golden-answer scope, not 004194 intra-fund missing P0 rows."

Evidence:
- `golden-answer.json` total records: 150 (from multiple fund_codes).
- `golden-answer.json` 004194 records: 5 (all `index_profile.*`, all matched).
- Remaining 145 records belong to other fund_codes (000216, 001548, 004393, 005313, 006597, 007360, 007721, 017644, 019918, 019923).
- Score pipeline marks non-004194 golden records as `unavailable` in the 004194 scoring run because those fund_codes are not in the 004194 snapshot scope.
- Computation: `5 comparable (004194) + 145 unavailable (non-004194) = 150 total` — exact match.

Verdict: PASS — decision artifact correctly distinguishes cross-fund unavailable from same-fund P0 gaps.

### 5. index_profile is conditional P1 per design.md §7.3

Decision artifact line 67: "All five matched rows are conditional P1 `index_profile` rows by `docs/design.md` §7.3 because 004194 is an `enhanced_index` fund."

Evidence from `docs/design.md` line 744: P1 includes `index_profile`. Line 747: `index_profile` 和 `tracking_error` 是指数基金 / 指数增强基金的条件 P1 字段. Preflight confirms `classified_fund_type=enhanced_index`.

Verdict: PASS.

### 6. Quality gate warn is P1 tracking_error and turnover_rate, not FQ1 mismatch

Decision artifact lines 58-59: quality gate `status=warn`; issues are FQ2 warn for P1 `tracking_error`, FQ2 warn for P1 `turnover_rate`, and FQ2F fund-level P1 failed fields; no FQ1 mismatch/block.

Evidence from `quality_gate.json`:
- `status=warn`, 3 issues
- Issue 1: FQ2, severity warn, field tracking_error, priority P1
- Issue 2: FQ2, severity warn, field turnover_rate, priority P1
- Issue 3: FQ2F, severity warn, fund 004194, P1 失败字段 tracking_error, turnover_rate
- No FQ1 issues present.

Verdict: PASS.

### 7. fixture_state=absent, promotion_allowed=false remain unchanged

Decision artifact line 60: fixture manifest `fixture_state=absent`; `promotion_allowed=false`; `blocks_minimum_v1=true`; `blocks_v1=true`.

Evidence from `fixture-promotion-state-manifest-20260529.json`:
- `fixture_state: "absent"`
- `promotion_allowed: false`
- `blocks_minimum_v1: true`
- `blocks_v1: true`

Verdict: PASS — decision artifact preserves all values correctly.

### 8. tracking_error production golden rows blocked

Decision artifact line 126: "`tracking_error_production_golden_allowed=false` until P15-style reviewed direct observed disclosure evidence is accepted."

Evidence:
- `docs/design.md` §7.4 line 785: "`tracking_error` 生产 golden rows 只有在 reviewed direct observed disclosure evidence 被接受后才能添加。"
- `quality_gate.json`: FQ2 warn for tracking_error, coverage_rate 0.0.
- Snapshot: `tracking_error` extraction_mode=missing, value_present=false.
- P15/P16 accepted state confirmed by plan reviews.

Verdict: PASS.

### 9. GLM F1 P16 provenance wording constraint satisfied

GLM plan review F1 required: P16 provenance must state P16-S1 accepted concept, P16-S2 was blocked before golden-row edits, current rows were already present and verified by scoring.

Decision artifact line 122: "P16-S1 accepted the `index_profile` benchmark-context concept and evidence classification; P16-S2 was blocked before golden-row edits; the current five 004194 golden-answer rows are existing rows verified by current scoring, not rows newly added or accepted by P16-S2."

Verdict: PASS — GLM F1 constraint is precisely incorporated.

### 10. Decision fields match accepted plan

| Decision field | Plan value | Implementation value | Verdict |
|---|---|---|---|
| `decision` | `index_profile_only_candidate_not_full_fixture_ready` | Same | PASS |
| `minimum_v1_full_fixture_promotion_prep_ready` | `false` | `false` (line 94) | PASS |
| `index_profile_only_specialized_candidate_allowed` | `true`, only under limitations | `true`, only as bounded diagnostic/specialized candidate (line 104) | PASS |
| `fixture_state_after_gate` | `absent` | `absent` (line 95) | PASS |
| `promotion_allowed` | `false` | `false` (line 96) | PASS |
| `promotion_manifest` | `false` | `false` (line 97) | PASS |
| `tracking_error_production_golden_allowed` | `false` until P15 evidence | `false` until P15-style reviewed direct observed disclosure (line 126) | PASS |

Verdict: PASS — all decision fields match plan.

### 11. File scope — only allowed docs artifacts written

Decision artifact and evidence artifact are both untracked (not yet committed), matching the gate flow state where workers produce artifacts for controller review.

Validation:
- `git diff --check -- docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-implementation-evidence-20260529.md` → no output, EXIT=0.
- `git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json` → no output, EXIT=0.

Verdict: PASS — docs-only scope respected.

### 12. No runtime/test changes; ruff/pytest correctly skipped

Evidence artifact lines 72-76 explain that ruff and pytest were not run because the slice is docs-only with no Python/runtime changes. This matches the accepted plan's validation commands section (line 253).

Verdict: PASS.

### 13. Implementation evidence artifact completeness

Evidence artifact records:
- Changed files (2 new Markdown artifacts only)
- Read-only evidence table with 15+ specific evidence probes
- Validation commands and results
- Forbidden diff check results
- Why ruff/pytest not run
- Residual risks table
- Self-checks covering startup, pre-edit, scope, GLM F1 wording, decision, evidence, and completion validation

Verdict: PASS — comprehensive evidence chain.

## Findings

### F1: golden_set.json 不包含 004194 记录（minor, non-blocking）

**Location:** `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/golden_set.json`

**Observation:** The snapshot-level `golden_set.json` contains 6 records for fund_codes 004393, 000216, 007721, 007360, 006597, 001548 — but zero records for 004194. Yet `score.json` correctly identifies and matches the 5 comparable 004194 records from `golden-answer.json`.

**Assessment:** This is a pipeline artifact construction issue, not a decision artifact error. The decision artifact's Evidence Freeze table (line 36) lists `golden_set.json` as evidence, and the evidence artifact does not make any claims that depend on `golden_set.json` containing 004194 rows. The 004194 correctness scoring works correctly because it reads from `golden-answer.json`, not from the snapshot-level `golden_set.json`. The `golden_set.json` appears to contain only non-004194 records from the broader scoring corpus.

**Impact:** None on decision correctness, fixture state, or gate outcome. The decision's evidence chain is intact through `score.json` and `golden-answer.json`. This finding is for pipeline hygiene awareness.

**Recommendation:** Future pipeline work may want to ensure `golden_set.json` includes the fund's own golden records for consistency, but this does not block the current gate.

## Structural Assessment

- **Decision artifact:** Thorough and well-structured. Correctly encodes all plan-required decision fields. Field disposition matrix is complete with owners and next gates. Non-goals / forbidden changes section is comprehensive.
- **Evidence artifact:** Complete read-only evidence chain with specific `jq` commands, file reads, and `rg` probes. Validation commands correctly executed. Self-checks cover all critical dimensions.
- **P16 provenance:** Precisely incorporates GLM F1 constraint. No implication that P16-S2 added accepted golden rows.
- **Index profile-only limitations:** Eight explicit conditions correctly define the bounded diagnostic candidate scope.
- **Residual risks:** Appropriately classified by severity with clear owners and next gates.

## Conclusion

**PASS_WITH_FINDINGS**

The implementation satisfies the accepted plan. All 13 verification criteria pass. One minor finding (F1): `golden_set.json` for the 004194 snapshot does not contain any 004194 records, which is a pipeline artifact construction observation with zero impact on the decision or gate outcome.

No blocking issues remain. The decision artifact correctly:
- Preserves `fixture_state=absent` and `promotion_allowed=false`
- Blocks full fixture promotion-prep due to P0 coverage=0
- Allows `index_profile-only` candidate only as bounded diagnostic/specialized
- Requires P15-style direct observed disclosure before `tracking_error` production golden rows
- Precisely states P16 provenance per GLM F1 constraint
- Does not authorize any runtime, test, report, golden, manifest, or control-doc changes

The evidence artifact provides a complete and verifiable evidence chain.

## Artifact Path

`docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-implementation-review-glm-20260529.md`

## Self-check

Self-check: pass
