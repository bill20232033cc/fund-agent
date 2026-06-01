# QDII Replacement Fallback 040046 Evidence Review — AgentDS

> Date: 2026-05-27
> Reviewer: AgentDS (independent evidence reviewer, not controller)
> Gate: `QDII replacement fallback 040046 evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-plan-controller-judgment-20260527.md`
> Verdict: **PASS**

## 1. Review Method

Cross-referenced every material claim in the evidence artifact against the public generated output files:

- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/summary.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/snapshot.jsonl`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/score.md`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/quality_gate.json`
- `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/quality_gate.md`

Also verified git status, `git diff --check`, and file existence.

No fund-analysis commands were run. No PDF/cache/source internals were inspected. No code was modified.

## 2. Question-by-Question Answers

### Q1: Did the worker follow accepted scope?

**YES.** Evidence is strictly `040046` / report_year `2024`, public CLI only. No `096001` rerun. No `019172` or fallback execution. No promotion claims. Confirmed by:
- Command log shows exactly three commands for `040046` / `2024` (section 2).
- Section 9 explicitly confirms each exclusion.
- No other fund appears in any generated output.

### Q2: Are command outcomes, generated paths, and git status claims credible against public outputs?

**YES**, with one minor documentation gap.

| Claim | Public evidence | Match |
|---|---|---|
| Snapshot exit 0 | `snapshot.jsonl` (16 records, 24556 bytes) exists | ✓ |
| Score exit 0 | `score.json` (10458 bytes), `score.md` exist | ✓ |
| Quality exit 0 | `quality_gate.json` (6590 bytes), `quality_gate.md` exist | ✓ |
| All 8 generated paths listed in section 3 | All 8 files exist on disk | ✓ |
| `errors.jsonl` listed as generated | Exists but is **empty (0 bytes)** — not mentioned in evidence | Minor gap |
| Git status: only evidence artifact untracked under `docs/reviews/` | `git status` confirms `reports/extraction-snapshots/` is not tracked | ✓ |
| `git diff --check` passes | Manual run returns clean (no output) | ✓ |

Finding F1 (LOW): Evidence section 3 lists `errors.jsonl` as a generated output but does not note it is empty (0 bytes). An empty errors file is benign, but the plan section 11 expects completeness in generated path reporting.

### Q3: Is provenance recorded correctly? Is it eligible?

**YES.** Cross-reference:

| Field | Evidence claim | Public source | Match |
|---|---|---|---|
| `source_provenance_schema_version` | `repository_source_provenance.v1` | `snapshot.jsonl` (every record) | ✓ |
| `source_strategy` | `primary_then_fallback` | `snapshot.jsonl` | ✓ |
| `resolved_source_name` | `eastmoney` | `summary.md` table, `snapshot.jsonl` | ✓ |
| `fallback_used` | `true` | `summary.md` table, `snapshot.jsonl` | ✓ |
| `primary_failure_category` | `unavailable` | `snapshot.jsonl` only (not in `summary.md`) | ✓ |
| `fallback_eligibility` | `eligible` | `summary.md` table, `snapshot.jsonl` | ✓ |
| `source_provenance_status` | `complete` | `summary.md` table, `snapshot.jsonl` | ✓ |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | `summary.md` table | ✓ |

Eligibility check: `primary_failure_category=unavailable` is in the eligible set (`not_found`, `unavailable`) per plan section 7. No fail-closed category (`schema_drift`, `identity_mismatch`, `integrity_error`) appears. Provenance is eligible. ✓

Note: `summary.md` does not expose `primary_failure_category` directly — only `snapshot.jsonl` does. The evidence artifact correctly states provenance was read from both files (section 4), so this is not an error.

### Q4: Are score and quality summaries accurate?

**YES.** Field-by-field cross-reference against `score.json` and `quality_gate.json`:

| Claim | Public value | Match |
|---|---|---|
| `field_count=14` | `score.json.field_count: 14` | ✓ |
| `fund_count=1` | `score.json.fund_count: 1` | ✓ |
| `failed_fund_count=0` | `score.json.failed_funds: []` | ✓ |
| `score_applicability_issue_count=0` | `score.json.score_applicability_issues: []` | ✓ |
| `p0_status=pass` | `score.json.p0_status: "pass"` | ✓ |
| `status_counts: pass=8, fail=6` | 8 pass + 6 fail in field_scores | ✓ |
| `correctness=unavailable` | `score.json.correctness.status: "unavailable"` | ✓ |
| `missing_field_rate=35.7%` | `score.json.fund_quality[0].missing_field_rate: 0.35714…` | ✓ |
| `missing_p0_fields=[]` | `score.json.fund_quality[0].missing_p0_fields: []` | ✓ |
| `missing_p1_fields=[holder_structure, holdings_snapshot, share_change, turnover_rate]` | Exact match in `score.json` | ✓ |
| `quality_gate_status=block` | `quality_gate.json.status: "block"` | ✓ |
| `issue_count=7` | `quality_gate.json.issue_count: 7` | ✓ |
| `rule_result_count=1` | 1 entry in `quality_gate.json.rule_results` | ✓ |
| FQ4 block: 35.7% > 35.0% | `observed_rate: 0.35714…`, `threshold: 0.35` | ✓ |
| FQ5 info: resolved for qdii_fund | `rule_results[0].status: "resolved"` | ✓ |
| 4× FQ2 warn for P1 fields | 4 FQ2 warn issues in `quality_gate.json` | ✓ |
| 1× FQ2F warn for 040046 | 1 FQ2F warn issue | ✓ |
| 1× FQ0 info | 1 FQ0 info issue | ✓ |
| `manager_strategy_text` pass, coverage 100%, traceability 100% | `score.json`: P0, pass, 1.0, 1.0 | ✓ |

Finding F2 (LOW — Completeness): `summary.md` lists 16 fields in its coverage table (includes `index_profile` and `tracking_error`), but `score.json` scores only 14 fields. The two extra fields are applicability-excluded (`index_profile`: 非指数基金不适用; `tracking_error`: QDII不适用P13规则). The evidence artifact reports `field_count=14` from score without noting this 16→14 reduction. The material quality outcome is unchanged: even if all 16 were counted, the missing rate would be 7/16=43.75% > 35%.

### Q5: Is `terminal_classification=quality_blocked_after_provenance` correct?

**YES.** Analysis:

The accepted plan's terminal-state matrix (section 9) enumerates these quality-related rows:
- P0 block on `manager_strategy_text` → `quality_blocked_after_provenance` or `disclosure_data_gap_not_baseline_ready`
- P0 block on another field → `quality_blocked_after_provenance`
- Quality `warn` with P1 residuals only → `candidate_public_evidence_warn_not_promoted`
- Quality `pass` → `candidate_public_evidence_pass_not_promoted`

FQ4 has severity `block` (confirmed in `quality_gate.json`). The quality gate status is `block`. All P0 fields pass. The block is FQ4 missing-field-rate (35.7% > 35.0%), which is a system-level quality rule, not a P0 field failure.

The matrix does not have a dedicated row for "FQ4 block with all P0 passing." The worker applied `quality_blocked_after_provenance`, which is the correct judgment:
1. Provenance is eligible ✓
2. Quality gate status is `block` (not `warn`, not `pass`) ✓
3. The closest matching row is "quality P0 block on another field" → `quality_blocked_after_provenance`
4. There is no other classification in the matrix that fits a `block`-severity outcome

Classification is correct. Flagging as a plan residual (see section 5), not an evidence error.

### Q6: Is `promotion_disposition=not_promoted` with no replacement claim?

**YES.** Evidence section 8 explicitly states `promotion_disposition=not_promoted` and confirms: not accepted, not source-safe, not scoring-ready, not baseline, not golden. Section 9 confirms no promotion actions were taken. No generated output contains promotion language for 040046. ✓

### Q7: Do generated reports stay ignored/untracked?

**YES.** `git status` shows `reports/extraction-snapshots/` is not tracked. The only untracked file under `docs/reviews/` related to this gate is the evidence artifact itself. All generated outputs are under the ignored directory. ✓

### Q8: Any boundary violations or missing required fields?

**NO boundary violations.** Evidence confirms no PDF/cache/source-helper/downloader/source-adapter inspection. No code, test, renderer, FQ0-FQ6, Service/CLI, taxonomy, extractor, Host/Agent/dayu, fixture, baseline/golden, or design/control doc modifications.

**Required fields per plan section 11** — all present:
- Startup Packet replay ✓
- Candidate identity ✓
- Preflight results ✓
- Exact commands and exit codes ✓
- Generated ignored paths ✓
- Public provenance tuple ✓
- Provenance stop-check before quality ✓
- Quality status ✓
- P0/P1 issues ✓
- `manager_strategy_text` status ✓
- False-positive suspicion ✓
- Terminal classification ✓
- `promotion_disposition=not_promoted` ✓
- No 019172/other candidate run ✓
- No PDF/cache inspection ✓
- No code/test changes ✓

Finding F3 (LOW): Plan section 11 requires `git diff --check` result in the evidence artifact. The evidence section 9 states "Allowed tracked file change is limited to this evidence artifact" but does not include the raw `git diff --check` output. Manual verification confirms it passes (clean).

## 3. Findings Summary

| ID | Severity | Category | Description |
|---|---|---|---|
| F1 | LOW | Completeness | `errors.jsonl` listed as generated output but not noted as empty (0 bytes). Benign. |
| F2 | LOW | Completeness | Evidence reports `field_count=14` without noting `summary.md` shows 16 fields (2 applicability-excluded: `index_profile`, `tracking_error`). Material conclusion unchanged. |
| F3 | LOW | Documentation | Raw `git diff --check` output not included; only a prose assertion. Manual verification confirms clean. |

No material, blocking, or P0 findings.

## 4. Explicit Answers

- **Terminal classification correctness**: `quality_blocked_after_provenance` is CORRECT. FQ4 is a `block`-severity quality rule. Provenance is eligible. The plan matrix doesn't have a dedicated FQ4 row, but this is the correct classification under the existing matrix.

- **Public generated outputs support provenance and quality claims**: YES. Every provenance field and every quality metric in the evidence artifact is independently confirmed in the public generated outputs (`summary.md`, `snapshot.jsonl`, `score.json`, `quality_gate.json`).

## 5. Required Fixes Before Acceptance

None. All three findings are LOW severity and do not affect the material correctness of the evidence or the terminal classification. The controller may accept without requiring an evidence patch.

## 6. Residual Risks for Controller

| Risk | Severity | Description |
|---|---|---|
| Plan matrix FQ4 gap | LOW | The accepted plan's terminal-state matrix does not enumerate FQ4 or other non-P0 rule blocks. The worker correctly applied the closest classification, but future evidence gates may encounter the same ambiguity. Consider adding an explicit FQ4 row to the matrix in a future plan update. |
| 16→14 field reduction undocumented | LOW | `index_profile` and `tracking_error` are applicability-excluded from scoring. The extraction notes ("非指数基金不适用指数画像", "QDII基金当前不适用P13跟踪误差规则") explain the exclusion, but the scoring pipeline's filtering of these fields is not surfaced in the evidence. Not material here, but could mask extraction gaps in other fund types. |
| Empty errors.jsonl | LOW | Benign for this run, but if a future evidence worker silently treats an empty errors file as "no errors" without verifying the file was written by the current run, stale empty files could mask errors. |
| `summary.md` lacks `primary_failure_category` | LOW | The summary.md provenance table doesn't expose `primary_failure_category`. Only `snapshot.jsonl` carries this field. If a future evidence worker reads only `summary.md`, the fail-closed check would be incomplete. The current worker correctly read both files. |

## 7. Review Integrity

- No fund-analysis commands were executed in this review.
- No PDF, cache, source-helper, downloader, or source-adapter internals were inspected.
- No code, tests, configuration, or documentation was modified.
- No git operations (commit, push, merge) were performed.
- This review artifact is the only file written.
