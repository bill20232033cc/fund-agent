# 006597 Strict Correctness Rerun / Same-Fund Unavailable Field Review — Plan Review (MiMo)

日期：2026-05-29
角色：AgentMiMo independent plan review worker。本文是独立 plan review artifact，不启动 gateflow / phaseflow，不修改代码、文档、报告、manifest、golden file 或 control doc。

## Review Target

`docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-20260529.md`

## Evidence Independently Verified

| Evidence source | Verification result |
|---|---|
| `reports/golden-answers/golden-answer.json` 006597 records | 20 rows confirmed: basic_identity (5), product_profile (2), benchmark (1), classified_fund_type (1), nav_benchmark_performance (2), manager_strategy_text (2), manager_alignment (2), holder_structure (2), share_change (3) |
| `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl` | Exists with snapshot.jsonl and errors.jsonl |
| `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json` | `coverage_scope=not_configured`, `total_records=0`, `comparable_records=0` — confirms golden answer path not consumed |
| `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json` | `partially_covered`, 150 total, 9 comparable, 9 matched, 0 mismatched, 141 unavailable; same-fund 006597: 9 matched (P0), 11 unavailable (P1) |
| `docs/design.md` §7.3 (line 743) | P0: basic_identity, classified_fund_type, benchmark, nav_benchmark_performance, fee_schedule, manager_strategy_text; P1: product_profile, index_profile, tracking_error, turnover_rate, holder_structure, manager_alignment, holdings_snapshot, share_change |
| `reports/golden-readiness-preflight/.../golden_readiness_preflight.json` 006597 | `deferred_with_owner`; blockers: `strict_golden_not_configured`, `fixture_promotion_absent` |
| `docs/reviews/fixture-promotion-state-manifest-20260529.json` 006597 | `fixture_state=absent`, `promotion_allowed=false`, `blocks_minimum_v1=true`, `blocks_v1=true` |
| Untracked follow-up artifacts | 7 files confirmed present as untracked in workspace |
| `git diff --check` on plan | Pass, no output |
| `git diff --name-only` forbidden paths | Pass, no output |

## Review Criteria Verification

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Plan is 006597-specific, not mixing old multi-fund follow-up state | PASS | Plan lines 66-83: explicitly lists 7 untracked multi-fund follow-up artifacts as read-only unaccepted workspace evidence; lines 79-83 disposition prevents staging/deleting/accepting without review; preferred path is new 006597-specific artifacts |
| 2 | Rerun uses `reports/golden-answers/golden-answer.json` | PASS | Plan line 93: `--golden-answer-path reports/golden-answers/golden-answer.json` |
| 3 | Output to new 006597-specific path, not overwriting accepted reports | PASS | Plan line 94: `--output-dir reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529`; distinct from existing `bond-risk-drawdown-nav-*` and `strict-correctness-follow-up-*` dirs |
| 4 | Distinguishes cross-fund unavailable from same-fund 006597 unavailable | PASS | Plan line 128: "distinguish same-fund 006597 unavailable from cross-fund unavailable in the 150-row corpus"; lines 156-162: same-fund unavailable handling separate from cross-fund |
| 5 | Clean pass remains `promotion_prep_candidate` only, not promoted | PASS | Plan lines 173-179: `promotion_allowed` remains `false`, `fixture_state` remains `absent`, separate promotion gate still required |
| 6 | `fixture_state=absent`, `promotion_allowed=false`, `promotion_manifest=false` preserved | PASS | Plan lines 14, 175-178: explicitly preserved in all result branches |
| 7 | Prohibited: golden fixtures / golden-answer JSON / runtime / score / quality / FQ0-FQ6 / manifests / preflight / control doc | PASS | Plan lines 18-21: comprehensive non-goals; lines 253-254: stop condition if rerun requires editing any of these |
| 8 | Mismatch/unavailable field-level ledger format with owner, next_gate, blocks_minimum_v1/full_v1 | PASS | Plan lines 181-198: complete ledger table format with all required columns including `blocks_minimum_v1`, `blocks_full_v1`, `prohibited_action` |
| 9 | Validation matrix includes json.tool, diff check, forbidden diff; ruff/pytest not required for docs/evidence-only | PASS | Plan lines 212-229: `python -m json.tool` for score/quality parsing; `git diff --check` for artifacts; `git diff --name-only` for forbidden paths; line 229: ruff/pytest explicitly not required unless runtime changed |
| 10 | UI -> Service -> Host -> Agent boundary; no extra_payload; no QDII/FOF/110020/004393/004194 scope | PASS | Plan line 22: no extra_payload; line 20: excludes QDII/FOF/110020/017641/004393/004194; no Host/Agent/dayu work authorized |
| 11 | Stop conditions are comprehensive | PASS | Plan lines 249-260: covers code-edit requirement, mismatch fix proposals, promotion language, old artifact staging, PDF access, scope creep, PR/release |

## Findings

### F1: Existing follow-up score already provides strong predictive evidence for rerun outcome (minor, non-blocking)

**Location:** Plan lines 87, 139-162

**Observation:** The existing `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json` already shows `partially_covered` with 9 matched and 11 same-fund unavailable (0 mismatched). The 9 matched rows are all P0 fields (basic_identity×5, benchmark×1, classified_fund_type×1, nav_benchmark_performance×2). The 11 unavailable rows are all P1 fields (product_profile×2, manager_strategy_text×2, manager_alignment×2, holder_structure×2, share_change×3). Since the rerun uses the same golden-answer.json and snapshot, the result will almost certainly hit the "If Same-Fund Unavailable Exists" path (lines 156-162), not the clean pass path.

**Assessment:** The plan correctly requires a fresh rerun with explicit golden-answer-path rather than accepting the old follow-up artifacts (line 87). This is the right approach because the follow-up score does not record `golden_answer_path` in its metadata, making provenance unclear. However, the plan could acknowledge the existing follow-up evidence as a likely outcome predictor to help the implementation worker prepare for the same-fund unavailable ledger.

**Impact:** None on plan correctness or handoff readiness. The plan's result handling branches are comprehensive. This is an informational observation.

### F2: Accepted score is `not_configured` — rerun is first configured strict correctness run (minor, non-blocking)

**Location:** Plan lines 44, 57-58

**Observation:** The plan states the latest accepted score has `coverage_scope=not_configured` and `total_records=0` because no golden answer path was supplied (line 57). The plan correctly identifies this as insufficient for promotion-prep (line 63). The rerun will produce the first configured strict correctness score for 006597. This is a significant state change: the preflight blocker `strict_golden_not_configured` would be resolved by a successful rerun.

**Assessment:** The plan handles this implicitly — if the rerun succeeds, the blocker resolves; if it fails (`blocked_machine_setup_failure`), the blocker persists. The plan does not explicitly discuss the preflight blocker resolution, but this is acceptable because the plan forbids modifying preflight outputs (line 19) and defers that to a separate gate.

**Impact:** None. The plan correctly scopes preflight/manifest updates as non-goals.

### F3: `fee_schedule` P0 field is absent from 006597 golden rows — plan priority map is correct (observation, non-blocking)

**Location:** Plan lines 200-210

**Observation:** Design.md §7.3 lists `fee_schedule` as P0, but the 006597 golden-answer.json has no `fee_schedule` rows. The plan's priority map (lines 204-208) does not list `fee_schedule` for 006597, which is correct — the map should only cover fields present in the golden answer.

**Assessment:** Correct omission. Noted for completeness.

## Plan Quality Assessment

**Strengths:**
- Thorough result handling with four distinct branches (not configured, mismatch, same-fund unavailable, clean pass)
- Complete manual verification ledger format with all required columns
- Correct treatment of old multi-fund follow-up artifacts as unaccepted workspace evidence
- New 006597-specific output paths prevent contamination of accepted reports
- Validation matrix is comprehensive and appropriate for docs/evidence-only gate
- Stop conditions are well-defined and cover all scope creep scenarios
- Correctly preserves fixture state in all result branches
- Priority map correctly matches design.md §7.3 for the 20 golden rows present

**Weaknesses:**
- Could acknowledge existing follow-up score as likely outcome predictor (F1)
- Could explicitly note that the rerun resolves the `strict_golden_not_configured` preflight blocker (F2)

Both are informational; neither blocks handoff.

## Conclusion

**PASS_WITH_FINDINGS**

The plan is handoff-ready. All 11 review criteria pass. Two minor findings exist:
- F1: Existing follow-up score provides strong predictive evidence for the rerun outcome (9 matched P0, 11 unavailable P1). The plan correctly requires a fresh rerun but could acknowledge this evidence.
- F2: The rerun is the first configured strict correctness run for 006597, which resolves the `strict_golden_not_configured` preflight blocker. The plan handles this implicitly.

No blocking issues. The plan correctly:
- Scopes to 006597-specific work without mixing old multi-fund follow-up state
- Uses golden-answer.json with new 006597-specific output paths
- Preserves fixture_state=absent and promotion_allowed=false in all branches
- Produces field-level ledger for mismatch/unavailable without guessing fixes
- Forbids all golden/manifest/runtime/control-doc mutations
- Includes comprehensive validation matrix

## Artifact Path

`docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-review-mimo-20260529.md`

## Self-check

Self-check: pass
