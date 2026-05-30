# QDII Replacement Candidate Evidence Re-Review — AgentGLM

> Date: 2026-05-27
> Reviewer: AgentGLM, independent evidence re-reviewer
> Gate: `QDII replacement candidate evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md`
> Prior review: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-glm-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md`

## Verdict: PASS

The prior blocking finding (F1: provenance not read from generated files) is fully fixed. The corrected evidence artifact now records provenance from public generated outputs, continues through extraction-score and quality-gate, and applies the correct terminal classification from the accepted plan matrix. All recorded values verified against public generated files.

## Prior Blocking Finding Resolution

### F1 (was BLOCKING): Public generated snapshot files contain complete eligible provenance — worker did not read them

**Status: FIXED**

The evidence artifact now includes:

1. **Review-Block Fix History** section (lines 15-22) documenting the correction and referencing both independent reviews that blocked the initial artifact.

2. **Public Source Provenance** section (lines 100-126) explicitly stating provenance was "read only from generated snapshot outputs" — `summary.md` and `snapshot.jsonl`.

3. **Correct provenance tuple recorded**:

| Field | Recorded value | Verified against public output |
|---|---|---|
| `resolved_source_name` | `eastmoney` | `summary.md` line 46, `snapshot.jsonl` all 16 records: match |
| `fallback_used` | `true` | `summary.md` line 46, `snapshot.jsonl`: match |
| `primary_failure_category` | `unavailable` | `snapshot.jsonl`: match |
| `fallback_eligibility` | `eligible` | `summary.md` line 46, `snapshot.jsonl`: match |
| `source_provenance_status` | `complete` | `summary.md` line 46, `snapshot.jsonl`: match |
| `source_strategy` | `primary_then_fallback` | `snapshot.jsonl`: match |
| `source_provenance_schema_version` | `repository_source_provenance.v1` | `snapshot.jsonl`: match |

4. **Correct eligibility interpretation**: Provenance is eligible because `fallback_used=true` with `primary_failure_category=unavailable` (eligible category), `fallback_eligibility=eligible`, and complete provenance. No fail-closed category present.

### F2 (was MINOR): `fallback_eligibility` incorrectly recorded as `not_eligible`

**Status: FIXED** — now correctly recorded as `eligible`.

### F3 (was INFORMATIONAL): `manager_strategy_text` coverage not evaluated

**Status: FIXED** — now recorded as `pass` with 100% coverage and 100% traceability. Correctly stated as "not the P0 blocker in this evidence run."

## Re-Review Check Answers

### Q1: Public provenance now recorded correctly from generated files?

**Yes.** All five required provenance fields plus schema version and strategy are recorded from `summary.md` and `snapshot.jsonl`. Values verified against public output files — all match.

### Q2: Evidence continued to extraction-score and quality-gate with exit 0?

**Yes.** Commands 5 and 6 now show exit code 0. Generated output files exist on disk and match recorded paths:

- `score.json` (10563 bytes), `score.md` (4324 bytes), `golden_set.json` (1612 bytes) from score command
- `quality_gate.json` (9128 bytes), `quality_gate.md` (2654 bytes) from quality-gate command

### Q3: Quality terminal classification from accepted plan matrix?

**Yes.** The terminal classification `quality_blocked_after_provenance` correctly maps to the accepted plan Section 7 row: "Provenance eligible, quality P0 block on another field" → `quality_blocked_after_provenance`, `promotion_disposition=not_promoted`.

The P0 block is on `nav_benchmark_performance` (not `manager_strategy_text`), so the alternate classification `disclosure_data_gap_not_baseline_ready` does not apply.

### Q4: Quality gate results accurately summarized?

**Yes.** Verified against `quality_gate.md` and `score.md`:

- `quality_gate_status=block`: confirmed ✓
- `issue_count=10`: confirmed (4 block + 5 warn + 1 info = 10) ✓
- P0 blockers: FQ2 `nav_benchmark_performance`, FQ3 `nav_benchmark_performance`, FQ2F `096001`, FQ4 `096001` — all match `quality_gate.md` ✓
- P1 warnings: `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`, plus FQ2F fund-level rollup — all match ✓
- `manager_strategy_text`: correctly reported as `pass`, correctly stated as "not the P0 blocker," not overclaimed as baseline-ready ✓
- `missing_field_rate=42.9%` exceeds FQ4 threshold of 35.0%: confirmed from `quality_gate.md` line 21 ✓
- `nav_benchmark_performance` coverage/traceability both 0.0%: confirmed from `score.md` line 71 ✓

### Q5: `promotion_disposition=not_promoted` confirmed?

**Yes.** No source-safe, scoring-ready, baseline, golden, or accepted replacement claim anywhere in the artifact.

### Q6: Generated reports remain ignored/untracked?

**Yes.** `git status --short` in the artifact shows no `reports/` paths. `.gitignore` covers `reports/extraction-snapshots/`. Only `docs/reviews/` artifacts appear as untracked.

### Q7: No boundary violations?

**Confirmed.** No code, tests, design docs, control docs, PDF, cache, source-helper, downloader, or source-adapter inspection. No fallback candidates run. No promotion attempted.

## New Findings

None. All prior findings are fixed and no new issues were identified.

## Residual Risks for Controller

| Risk | Description | Mitigation |
|---|---|---|
| `096001` quality-blocked on P0 `nav_benchmark_performance` | Coverage/traceability 0% for a P0 field. Root cause unknown from public evidence alone (disclosure gap vs extractor gap). | Separate authorized gate needed to diagnose root cause before any promotion consideration. |
| High missing-field rate (42.9%) | 6 of 14 fields at 0% coverage. May indicate systemic extraction gap for this QDII fund. | Do not promote until missing-field rate is addressed or explicitly accepted by a durable-baseline gate. |
| P1 residuals on 4 fields | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` all at 0% coverage. | Future durable-baseline gate must decide acceptability. |
| `correctness` oracle unavailable | Golden answer was not configured; correctness was not evaluated. | Cannot claim extraction correctness. A separate gate with golden answer configuration would be required. |
| Fallback source provenance | Primary source failed (`unavailable`), resolved via `eastmoney` fallback. Quality results reflect fallback source quality. | Controller should note that these quality results reflect the fallback source, not the primary. |
