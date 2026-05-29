# 004194 P0 Coverage / Index Profile-Only Fixture Decision Plan Review (GLM)

日期：2026-05-29
角色：AgentGLM review worker。本文是独立 plan review artifact，不是 controller judgment；不启动 `$gateflow` / `/gateflow` / `phaseflow`，不修改代码、文档、报告、manifest、golden 文件或 control doc，不提交、不 push、不 PR、不 merge、不 release、不 promotion，不进入其它 gate。

## Review Target

`docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md`

## Verification Criteria Results

### 1. 004194 score correctness counts

| Field | Plan claim | Evidence (score.json) | Verdict |
|---|---|---|---|
| `coverage_scope` | `covered` | `covered` | ✅ PASS |
| `total_records` | 150 | 150 | ✅ PASS |
| `comparable_records` | 5 | 5 | ✅ PASS |
| `matched_records` | 5 | 5 | ✅ PASS |
| `mismatched_records` | 0 | 0 | ✅ PASS |
| `unavailable_records` | 145 | 145 | ✅ PASS |

Source: `jq '.correctness | {coverage_scope,total_records,comparable_records,matched_records,mismatched_records,unavailable_records}' reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json`

### 2. Five comparable rows identity

Plan claims exactly five matched rows: `index_profile.benchmark_text`, `benchmark_identity_status`, `methodology_availability`, `constituents_availability`, `source_tier`.

Evidence from `score.json` `.correctness.record_results[] | select(.fund_code=="004194")`:

```
index_profile.benchmark_text: match
index_profile.benchmark_identity_status: match
index_profile.methodology_availability: match
index_profile.constituents_availability: match
index_profile.source_tier: match
```

Verdict: ✅ PASS — all five rows confirmed, no extra rows, no missing rows.

### 3. Same-fund P0 strict correctness coverage is 0

Plan claims P0 coverage is 0 because no 004194 P0 golden rows exist in current strict golden scope.

Evidence:
- `score.json` record_results for fund_code=004194 contain exactly 5 rows, all `index_profile.*` (P1 conditional), no P0 fields (`basic_identity`, `classified_fund_type`, `benchmark`, `nav_benchmark_performance`, `fee_schedule`, `manager_strategy_text`).
- `golden-answer.json` records for fund_code=004194: exactly 5 rows, all `index_profile.*`, no P0 fields.
- Strict golden correctness decision artifact confirms: "P0 strict correctness coverage is 0".

Verdict: ✅ PASS — zero P0 rows in both score record_results and golden-answer.

### 4. unavailable_records=145 are not 004194 intra-fund missing P0 rows

Plan claims the 145 unavailable records are from the broader golden answer scope, not 004194 intra-fund missing P0 rows.

Evidence from `golden-answer.json`:
- Total records: 150
- 004194 records: 5
- Non-004194 records: 145 (from 10 other funds: 000216, 001548, 004393, 005313, 006597, 007360, 007721, 017644, 019918, 019923)

Computation: `5 comparable (004194) + 145 unavailable (non-004194) = 150 total` — matches score.json exactly.

Verdict: ✅ PASS — unavailable=145 are cross-fund golden-answer records, not 004194 intra-fund P0 gaps.

### 5. index_profile is conditional P1 for index/enhanced-index

Plan claims `index_profile` is conditional P1 per `docs/design.md` §7.3.

Evidence from design.md §7.3 (line 747):

> `index_profile` 和 `tracking_error` 是指数基金 / 指数增强基金的条件 P1 字段。非指数基金不把这两个字段纳入 coverage / traceability / fund quality 分母；未知或冲突基金类型保持保守处理。

Verdict: ✅ PASS — explicit design.md confirmation.

### 6. Quality warn is tracking_error and turnover_rate, not FQ1 mismatch

Plan claims `quality_gate.status=warn` caused by P1 `tracking_error` and `turnover_rate` (FQ2/FQ2F), not FQ1 mismatch.

Evidence from `quality_gate.json`:
- `status=warn`, `issue_count=3`
- Issue 1: `FQ2`, severity `warn`, field `tracking_error`, priority `P1`, coverage_rate 0.0
- Issue 2: `FQ2`, severity `warn`, field `turnover_rate`, priority `P1`, coverage_rate 0.0
- Issue 3: `FQ2F`, severity `warn`, fund `004194`, "P1 字段失败；失败字段：tracking_error, turnover_rate"
- No FQ1 issues present.

Verdict: ✅ PASS — quality warn is exclusively FQ2/FQ2F for P1 fields tracking_error and turnover_rate; no FQ1 mismatch or block.

### 7. P15/P16 state blocks production tracking_error golden rows without direct observed disclosure

Plan claims P15/P16 state still blocks production tracking_error golden rows without direct observed disclosure.

Evidence:
- P15-S1 (`p15-s1-production-tracking-error-golden-evidence-plan-20260522.md`): verdict `BLOCKED_NO_REVIEWED_DIRECT_DISCLOSURE_EVIDENCE`. Target/limit text, manager narrative, benchmark-only, standard-deviation-only all rejected as proof of tracking-error value.
- P17-S1 (`p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md`): preserves tracking_error production golden block for all six enhanced-index candidates including 004194.
- Strict golden correctness controller judgment: "tracking_error requires P15 reviewed direct observed disclosure before production golden rows".
- design.md §7.4 (line 785): "tracking_error 生产 golden rows 只有在 reviewed direct observed disclosure evidence 被接受后才能添加。"

Verdict: ✅ PASS — multiple independent sources confirm tracking_error production golden rows blocked without direct observed disclosure.

### 8. Plan does not call 004194 full fixture promotion-prep-ready

Verdict: ✅ PASS — plan explicitly states:
- "do not mark 004194 as full fixture promotion-prep-ready"
- decision is `index_profile_only_candidate_not_full_fixture_ready`
- `minimum_v1_full_fixture_promotion_prep_ready=false`
- Stop conditions include: "Any plan or implementation wording marks 004194 as full fixture promotion-prep-ready"

### 9. fixture_state=absent and promotion_allowed=false remain unchanged

Evidence from fixture manifest (`docs/reviews/fixture-promotion-state-manifest-20260529.json`):
- `fixture_state: "absent"`
- `promotion_allowed: false`
- `blocks_minimum_v1: true`
- `blocks_v1: true`

Plan preserves these values:
- `fixture_state_after_gate=absent`
- `promotion_allowed=false`
- `promotion_manifest=false`

Verdict: ✅ PASS — fixture state unchanged.

### 10. Allowed/prohibited files and validation matrix correct for docs-only gate

Plan allows only docs-only decision and evidence artifacts:
- Plan file itself (already written)
- Future: decision artifact, implementation evidence artifact
- Controller-only: controller judgment, minimal control doc pointer

Prohibited files include all runtime, test, script, report, golden, manifest, config, lock, README, and design files. Validation commands check `git diff --check` and forbidden diff.

Verdict: ✅ PASS — scope is strictly docs-only with no runtime/golden/manifest edits authorized.

### 11. Next gate does not smuggle runtime/golden/manifest edits

Plan's next gate is: `006597 same-fund unavailable field review or strict correctness rerun`, with 004194 residuals routing to future P0 expansion / P15 tracking-error evidence gates. Implementation slices are docs-only. Stop conditions prohibit any runtime/test/report/golden/manifest/control-doc edit requirement.

Verdict: ✅ PASS — no smuggling of runtime/golden/manifest edits through next gate.

## Findings

### F1: P16 provenance characterization is imprecise (minor, non-blocking)

**Location:** Truth Sources table, row "P15/P16 tracking-error/index-profile artifacts"; Direct Evidence Table, row "P15/P16 state"

**Plan states:**
- "P16 accepted only index_profile benchmark-context golden rows"
- "P16 accepted index_profile benchmark-context golden rows"

**Observed evidence:**
- P16-S1 accepted the concept/plan for index_profile benchmark-context golden rows.
- P16-S2 implementation was BLOCKED before writing any golden rows, because extractor output for 2 of 5 funds (017644, 019918) had text diffs. No golden rows were added in P16-S2.
- The 5 index_profile rows for 004194 already existed in `golden-answer.json` from prior phases and were verified as matched in scoring. They were not added by P16-S2.

**Assessment:** The plan's conclusion is practically correct — 5 index_profile rows exist and are matched, tracking_error remains blocked. However, the provenance should more precisely state: "P16-S1 accepted the index_profile benchmark-context concept; P16-S2 was blocked before golden row edits; existing golden-answer rows were already present and verified through scoring" rather than "P16 accepted only index_profile benchmark-context golden rows."

**Impact:** None on decisions, fixture state, or next gate. The practical conclusion is identical. This is a documentation precision issue only.

**Recommendation:** If the plan proceeds to implementation, the decision artifact should use more precise P16 provenance language: reference P16-S1 acceptance and P16-S2 blocked status separately, noting that golden-answer rows predated P16-S2.

## Structural Assessment

- **Goal:** Clear and scoped to 004194 P0 coverage / index_profile-only fixture decision.
- **Non-Goals:** Comprehensive; correctly excludes runtime, test, golden, manifest, and control doc mutations; excludes 006597, QDII, FOF, 110020, 017641.
- **Truth Sources:** Adequate; all referenced artifacts exist and are listed in accepted artifacts or historical evidence.
- **Direct Evidence Table:** Complete; all key fields have current values.
- **Proposed Conservative Decision:** Well-defined with required decision fields, limitation list, and stop conditions.
- **Field Disposition Matrix:** Thorough; covers all relevant fields with dispositions, owners, and next gates.
- **Allowed/Prohibited Files:** Correct for docs-only gate.
- **Implementation Slices:** Appropriately scoped to docs-only artifacts.
- **Review Requirements:** Comprehensive; covers all 11 verification criteria.
- **Validation Commands:** Appropriate for docs-only gate.
- **Stop Conditions:** Adequate safety net against scope creep.
- **Residual Risks / Owners / Next Gate:** Complete with owners assigned.
- **Worker Self-Checks:** Appropriate.

## Conclusion

**PASS_WITH_FINDINGS**

The plan is handoff-ready and evidence-based. All 11 verification criteria pass. One minor finding (F1) exists: P16 provenance characterization is slightly imprecise but has zero impact on decisions, fixture state, or next gate direction.

- Artifact path: `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md`
- Review artifact path: `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-review-glm-20260529.md`
- Self-check: pass
