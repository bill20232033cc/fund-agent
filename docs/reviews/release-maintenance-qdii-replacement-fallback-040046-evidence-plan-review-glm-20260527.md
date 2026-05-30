# QDII Replacement Fallback Candidate Evidence Plan Review (AgentGLM)

> Date: 2026-05-27
> Reviewer: AgentGLM, independent plan reviewer
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-20260527.md`
> Gate: `QDII replacement fallback candidate evidence plan gate for 040046`
> Verdict: **PASS**

---

## 1. Startup Packet Replay

| Check | Result |
|---|---|
| Plan §1 current phase | `release maintenance` — matches `docs/implementation-control.md` Startup Packet ✓ |
| Plan §1 current gate | `QDII replacement candidate evidence accepted locally` — matches control doc ✓ |
| Plan §1 next entry point | `QDII replacement fallback candidate evidence plan gate for 040046` — matches control doc ✓ |
| Plan §1 not a gate switch | Explicitly stated and correct — 096001 controller judgment sets this as the accepted next entry point ✓ |
| Latest accepted checkpoint | `c6a5042 docs: accept qdii replacement evidence` — matches branch HEAD lineage ✓ |

No discrepancy found.

## 2. Candidate Discipline

| Check | Result |
|---|---|
| Single planned candidate | `040046` / 2024 only ✓ |
| Fund name matches enumeration | `华安纳斯达克100ETF联接(QDII)A` matches enumeration table row ✓ |
| CSV category matches | `海外股票类` matches enumeration ✓ |
| Selection basis | Fallback order after `096001` quality-blocked — matches enumeration controller judgment ✓ |
| Provenance state | `provenance_unknown` ✓ |
| Quality state | `quality_unknown` ✓ |
| Promotion state | `not_promoted` ✓ |
| No premature claims | Plan explicitly states it does not make 040046 source-safe, scoring-ready, baseline-ready, golden-ready, accepted, promoted, or approved ✓ |

`040046` is the correct next fallback candidate per the accepted enumeration fallback order and the 096001 controller judgment.

## 3. Preserved 096001 Accepted State

| Check | Result |
|---|---|
| Source provenance preserved | `eligible complete public fallback provenance` ✓ |
| `resolved_source_name` | `eastmoney` ✓ |
| `fallback_used` | `true` ✓ |
| `primary_failure_category` | `unavailable` ✓ |
| `fallback_eligibility` | `eligible` ✓ |
| `source_provenance_status` | `complete` ✓ |
| Quality state | `quality_gate_status=block` ✓ |
| Terminal classification | `quality_blocked_after_provenance` ✓ |
| Promotion state | `not_promoted` ✓ |
| P0 blocker correctly identified | `nav_benchmark_performance`, not `manager_strategy_text` ✓ |
| No rerun authorized | Explicitly stated ✓ |

All 096001 accepted state fields match the accepted evidence artifact and controller judgment exactly.

## 4. Public Command Plan

| Check | Result |
|---|---|
| Preflight commands | `extraction-snapshot --help`, `extraction-score --help`, `quality-gate --help` — matches 096001 plan shape ✓ |
| Preflight acceptance criteria | Lists exact expected flags; mismatch triggers `cli_flag_mismatch_not_run` ✓ |
| Evidence commands use explicit paths | All `--run-id`, `--fund-code`, `--report-year`, `--source-csv`, `--output-dir`, `--snapshot-path`, `--errors-path`, `--score-path` use explicit values ✓ |
| Run id convention | `qdii-replacement-fallback-040046-2024-20260527` — consistent with 096001 convention (`qdii-replacement-candidate-*`) ✓ |
| CSV path | `docs/code_20260519.csv` — matches 096001 evidence plan ✓ |
| Generated output provenance reading | §6 explicitly requires reading `summary.md` and `snapshot.jsonl`, not stdout alone ✓ |
| Stdout vs file disagreement | Generated public files control; discrepancy recorded ✓ |

Command conventions are materially consistent with the accepted 096001 plan and evidence. The provenance field names in §7 have been corrected to match actual public output fields (e.g., `source_strategy` instead of the 096001 plan's `source_chain`), which is a valid improvement informed by the 096001 evidence experience.

## 5. Source Provenance

| Check | Result |
|---|---|
| Provenance before quality | §7 explicit: "Source provenance must be interpreted before quality status" ✓ |
| Fail-closed categories | `schema_drift`, `identity_mismatch`, `integrity_error` — matches AGENTS.md ✓ |
| Missing/incomplete provenance not eligible | Explicitly listed ✓ |
| Unknown fallback category not eligible | Explicitly listed ✓ |
| Command success without provenance not eligible | Explicitly listed ✓ |
| Eligible conditions | Primary success or fallback with `not_found`/`unavailable` + `eligible` + complete provenance — matches AGENTS.md ✓ |
| Terminal classification for fail-closed | `source_fail_closed_not_promoted` ✓ |
| Terminal for missing provenance | `provenance_unknown_public_metadata_absent` or `provenance_incomplete_not_promoted` ✓ |

Provenance discipline is correct and consistent with AGENTS.md §"年报来源 fallback 策略" and design.md §6.1.

## 6. Quality

| Check | Result |
|---|---|
| Quality only after provenance eligible | §8 explicit ✓ |
| P0 `manager_strategy_text` blocking | `quality_blocked_after_provenance` ✓ |
| P0 `manager_strategy_text` disclosure gap | `disclosure_data_gap_not_baseline_ready` only when public evidence supports ✓ |
| P0 before provenance eligible | Classify by provenance first, not `quality_blocked_after_provenance` ✓ |
| Other P0 block | Record exact field/rule, keep `not_promoted` ✓ |
| P1 handling | May allow `warn` but remain visible; durable-baseline gate decides acceptability ✓ |
| No extractor/policy fixes | §8 false-positive handling explicitly prohibits code/extractor/taxonomy changes ✓ |
| False-positive suspicion | Requires concrete reason from public output; does not authorize changes ✓ |

Quality handling is precise and correctly ordered after provenance.

## 7. Terminal-State Matrix

| Check | Result |
|---|---|
| Every state `not_promoted` | Confirmed — all 12 terminal states in §9 have `promotion_disposition=not_promoted` ✓ |
| Classification names consistent | All names match accepted pattern; one new state `snapshot_outputs_missing_not_promoted` added ✓ |
| New state justification | Covers zero-exit snapshot with missing output files — a scenario encountered in the 096001 evidence run; reasonable addition ✓ |
| Coverage completeness | Matrix covers CLI mismatch, snapshot failure, missing outputs, provenance missing/incomplete, fail-closed, ineligible, score failure, quality-gate failure, P0 blocks, P1 warn, and pass ✓ |

## 8. Fallback / Exclusion

| Check | Result |
|---|---|
| `019172` contingency-only | §10 explicit; no evidence authorized ✓ |
| `017641` excluded | §10 explicit; accepted state preserved ✓ |
| QDII-FOF excluded | §10 explicit; pending taxonomy gate ✓ |
| `013308` excluded | §10 explicit; naming/category conflict unresolved ✓ |
| Bond QDII | Requires asset-class fitness gate ✓ |
| No fallback execution authorized | Explicit throughout ✓ |

All exclusions match the accepted enumeration plan and 096001 controller judgment.

## 9. Boundary

| Check | Result |
|---|---|
| No code changes | §13 stop conditions explicit ✓ |
| No product/source-helper/taxonomy/renderer changes | §13 explicit ✓ |
| No golden/baseline changes | §13 explicit ✓ |
| No evidence run authorized | §7, §13 explicit ✓ |
| No PDF/cache/source-helper inspection | §13 explicit ✓ |
| No external web access | §13 explicit ✓ |
| No commit/push/PR/merge | §13 explicit ✓ |
| No control-doc/design-doc edits | §13 explicit ✓ |

## 10. Command/Path Convention Check Against Accepted 096001 Plan

| Convention | 096001 Plan | 040046 Plan | Assessment |
|---|---|---|---|
| CLI flags | `--run-id`, `--report-year`, `--fund-code`, `--source-csv`, `--output-dir`, `--force-refresh` (snapshot); `--snapshot-path`, `--source-csv`, `--output-dir`, `--errors-path` (score); `--score-path`, `--output-dir` (quality-gate) | Identical flag set ✓ | Consistent |
| Provenance fields | `source_provenance_status`, `resolved_source`, `fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_chain` | `source_provenance_schema_version`, `source_strategy`, `resolved_source`/`resolved_source_name`, `fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason` | Improved — matches actual 096001 evidence output fields ✓ |
| Run id prefix | `qdii-replacement-candidate-` | `qdii-replacement-fallback-` | Appropriately distinguishes fallback from first candidate ✓ |
| Terminal matrix | 11 states | 12 states (adds `snapshot_outputs_missing_not_promoted`) | Reasonable addition reflecting 096001 evidence experience ✓ |

No materially wrong conventions found. The changes from the 096001 plan are improvements informed by actual evidence experience, not errors.

---

## Accepted Strengths

1. **Provenance tuple corrected and expanded**: §7 captures the actual public output fields (`source_provenance_schema_version`, `source_strategy`, `source_provenance_reason`) observed in the 096001 evidence run, replacing the 096001 plan's speculative `source_chain` with concrete field names.

2. **Generated-output provenance precedence**: §6 explicitly establishes that generated public files (`summary.md`, `snapshot.jsonl`) control over CLI stdout when they disagree, with discrepancy recording. This directly addresses the issue that blocked the initial 096001 evidence artifact.

3. **Additional terminal state**: §9 adds `snapshot_outputs_missing_not_promoted` for the zero-exit-but-missing-files scenario, closing a gap exposed during the 096001 evidence run.

4. **Comprehensive provenance-before-quality ordering**: §7 and §8 maintain strict sequential discipline with clear terminal classifications at each failure point.

5. **Clean 096001 state preservation**: §3 accurately records all accepted 096001 fields without modification, weakening, or reopening.

6. **Controller-only responsibilities maintained**: The plan does not dispatch agents, authorize evidence, modify artifacts, or assume controller judgment scope.

## Required Fixes Before Acceptance

None. No blocking or material issues found.

## Residual Risks

| Risk | Severity | Notes |
|---|---|---|
| `040046` provenance may show fail-closed category or missing provenance | Medium | Plan correctly handles this with `source_fail_closed_not_promoted` or `provenance_unknown_public_metadata_absent`, but controller should plan for next fallback if this occurs. |
| `040046` quality may show P0 `manager_strategy_text` block like `017641` | Medium | Plan correctly classifies as `quality_blocked_after_provenance` or `disclosure_data_gap_not_baseline_ready`, but this would exhaust another QDII equity candidate without resolution. |
| `040046` quality may show `nav_benchmark_performance` P0 block like `096001` | Medium | If QDII extraction shares systematic field gaps, multiple candidates may fail the same P0 field. Plan correctly classifies but does not diagnose root cause. |
| Eastmoney fallback source quality | Low | If `040046` also falls back to Eastmoney, quality evidence reflects fallback-source extraction. Plan does not restrict source strategy, which is correct. |

## Plan Acceptance Statement

**Yes** — this plan may be accepted as a plan for later `040046` evidence without authorizing evidence now. The plan is plan-only, follows the accepted next entry point, selects the correct fallback candidate, preserves all accepted states and exclusions, and maintains all required discipline around provenance, quality, terminal classification, and boundary constraints.
