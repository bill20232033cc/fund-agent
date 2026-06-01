# QDII Replacement Candidate Evidence Re-Review — AgentDS

> Date: 2026-05-27
> Reviewer: AgentDS (independent evidence reviewer, not controller)
> Gate: `QDII replacement candidate evidence gate` (continuation re-review)
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md` (updated after BLOCKED)
> Prior DS review: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-ds-20260527.md` (BLOCKED)
> Prior GLM review: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-glm-20260527.md` (BLOCKED)
> Re-review artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-rereview-ds-20260527.md`
> Verdict: **PASS**

## 1. Blocking Finding Resolution

### F1 (DS prior): terminal classification incorrect; provenance existed in generated files

**Status: FIXED.**

The evidence artifact now records the provenance tuple correctly from the public generated files (lines 107–118):

| Field | Recorded Value | Verified Against |
|---|---|---|
| `resolved_source` | `eastmoney` | `summary.md` line 44, `snapshot.jsonl` all 16 records |
| `fallback_used` | `true` | `summary.md` line 44, `snapshot.jsonl` all records |
| `primary_failure_category` | `unavailable` | `snapshot.jsonl` all records |
| `fallback_eligibility` | `eligible` | `summary.md` line 44, `snapshot.jsonl` all records |
| `source_provenance_status` | `complete` | `summary.md` line 44, `snapshot.jsonl` all records |
| `source_strategy` | `primary_then_fallback` | `snapshot.jsonl` all records |

The evidence artifact explicitly documents its sources (lines 102–105):

> Public provenance was read only from generated snapshot outputs:
> - `reports/.../summary.md`
> - `reports/.../snapshot.jsonl`

Provenance eligibility was correctly determined (lines 120–126): fallback with `primary_failure_category=unavailable` and `fallback_eligibility=eligible` is eligible under the accepted plan §5.

### F2 (DS prior): terminal classification name not from plan matrix

**Status: FIXED.**

The updated terminal classification is `quality_blocked_after_provenance` (line 193). This matches the accepted plan §7 matrix row: "Provenance eligible, quality P0 block on another field → `quality_blocked_after_provenance`."

### F3 (DS prior): evidence worker restricted to stdout only, ignoring generated files

**Status: FIXED.**

The evidence artifact now has an explicit "Review-Block Fix History" section (lines 15–22) acknowledging the error, and the provenance section (lines 100–126) demonstrates correct use of both `summary.md` and `snapshot.jsonl` as public evidence sources.

## 2. Updated Evidence Verification

### 2.1 Score command executed (exit 0)

**Verified.** `score.json` exists (10563 bytes), `score.md` exists (4324 bytes), `golden_set.json` exists (1612 bytes). Score results cross-referenced:

| Claim in evidence | score.json actual | Match? |
|---|---|---|
| `field_count=14` | `field_count: 14` | Yes |
| `fund_count=1` | `fund_count: 1` | Yes |
| `status_counts: pass=7, fail=7` | `pass: 7, fail: 7` | Yes |
| `p0_status=fail` | `p0_status: "fail"` | Yes |
| P0 failed: `nav_benchmark_performance` | `p0_failed_fields: ["nav_benchmark_performance"]` | Yes |
| P1 failed: `turnover_rate, holder_structure, holdings_snapshot, share_change` | `p1_failed_fields: ["turnover_rate", "holder_structure", "holdings_snapshot", "share_change"]` | Yes |
| `missing_field_rate=42.9%` | `missing_field_rate: 0.42857...` | Yes |
| `manager_strategy_text` pass, 100%/100% | `status: "pass"`, `coverage_rate: 1.0`, `traceability_rate: 1.0` | Yes |
| correctness `unavailable` | `status: "unavailable"` | Yes |

### 2.2 Quality gate executed (exit 0, status=block)

**Verified.** `quality_gate.json` exists (9128 bytes, `status: "block"`, `issue_count: 10`).

P0/block issues cross-referenced:

| Evidence claim | quality_gate.json actual | Match? |
|---|---|---|
| FQ2 block nav_benchmark_performance | Issue 0: FQ2, severity block, nav_benchmark_performance | Yes |
| FQ3 block nav_benchmark_performance | Issue 1: FQ3, severity block, nav_benchmark_performance | Yes |
| FQ2F block 096001 | Issue 6: FQ2F, severity block, fund_code 096001 | Yes |
| FQ4 block missing-field-rate | Issue 9: FQ4, severity block, observed_rate 42.9%, threshold 35% | Yes |

P1/warn issues cross-referenced:

| Evidence claim | quality_gate.json actual | Match? |
|---|---|---|
| FQ2 warn turnover_rate | Issue 2: FQ2, severity warn, turnover_rate | Yes |
| FQ2 warn holder_structure | Issue 3: FQ2, severity warn, holder_structure | Yes |
| FQ2 warn holdings_snapshot | Issue 4: FQ2, severity warn, holdings_snapshot | Yes |
| FQ2 warn share_change | Issue 5: FQ2, severity warn, share_change | Yes |
| FQ2F warn 096001 P1 fields | Issue 7: FQ2F, severity warn, fund_code 096001, P1 | Yes |

FQ0 info and FQ5 resolved also confirmed matching.

### 2.3 manager_strategy_text not overclaimed

**Verified.** Evidence line 179: "It is not the P0 blocker in this evidence run." Evidence line 189: "public-provenance eligible but not baseline-ready." No claim of baseline/golden/scoring-ready status. `score.json` confirms `manager_strategy_text: status=pass`.

### 2.4 promotion_disposition and no replacement claim

**Verified.** Evidence line 194: `not_promoted`. Lines 26–28: explicit guardrail confirmations. No source-safe, scoring-ready, baseline, golden, or accepted replacement language anywhere in the artifact.

### 2.5 Generated reports remain ignored/untracked

**Verified.** `git status --short` output (lines 77–85) shows no `reports/extraction-snapshots/` paths. All 9 generated files in that directory exist on disk but are git-ignored. The only tracked-intended artifact is the evidence document itself.

### 2.6 No boundary violations

**Verified.** Lines 29–31 confirm no code, tests, README, design doc, control doc, fixtures, golden files, baseline corpus, renderer, FQ0-FQ6, Service/CLI defaults, FundDocumentRepository, taxonomy, extractor, Host/Agent/dayu modifications. No PDF/cache/source-helper/downloader/source-adapter internals were inspected. `git diff --check` passed (line 53).

## 3. Minor Observation (non-blocking)

The score output includes two P2 failures (`investor_return` and `nav_data`) that the evidence artifact does not enumerate separately. The evidence describes `status_counts: pass=7, fail=7` which correctly accounts for the 14 fields including P2. This is not required by the accepted plan (which only mandates P0/P1 enumeration), but future evidence artifacts could optionally list P2 failures for completeness.

## 4. Required Fields Completeness

All plan §9 required fields are present:

- Startup Packet replay ✓
- Candidate identity (fund_code, fund_name, app_category, report_year, classified_fund_type, snapshot result) ✓
- Preflight help results and flag verification ✓
- Exact commands and exit codes ✓
- Generated ignored paths (actual, not assumed) ✓
- Public provenance tuple ✓
- Provenance stop-check before quality ✓
- Quality status, P0 issues, P1 issues ✓
- `manager_strategy_text` status ✓
- False-positive suspicion ✓
- Terminal classification from plan matrix ✓
- `promotion_disposition=not_promoted` ✓
- No internal inspection confirmation ✓
- No code/tests/docs changes confirmation ✓
- `git diff --check` result ✓

## 5. Residual Risks for Controller

| Risk | Severity | Notes |
|---|---|---|
| Eastmoney fallback source | MEDIUM | All extraction data for 096001 comes from Eastmoney (primary source was unavailable). This is eligible under the plan but the controller should note the fallback path when considering baseline quality. |
| nav_benchmark_performance missing (P0) | HIGH | Root cause unknown: could be a disclosure gap (QDII annual report doesn't publish this data) or an extractor gap. Resolution requires a separate gate with explicit disclosure-vs-extractor diagnosis. |
| FQ4 missing-field-rate 42.9% (threshold 35%) | HIGH | Six fields missing out of 14. Four are P1 (disclosure-dependent), one is P0 (nav_benchmark_performance), one is P2 (investor_return). The high rate is driven by the Eastmoney fallback path limitations. |
| P1 residuals (4 fields) | MEDIUM | turnover_rate, holder_structure, holdings_snapshot, share_change all at 0%. These are disclosure-dependent and may be inherently missing for QDII funds on Eastmoney. A durable-baseline gate would need to decide acceptability. |
| nav_data traceability 0% | LOW | P2 field with 100% coverage but 0% traceability. Not a blocker at current gate. |
