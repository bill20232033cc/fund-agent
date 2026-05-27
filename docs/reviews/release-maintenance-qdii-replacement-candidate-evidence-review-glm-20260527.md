# QDII Replacement Candidate Evidence Review — AgentGLM

> Date: 2026-05-27
> Reviewer: AgentGLM, independent evidence reviewer
> Gate: `QDII replacement candidate evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md`
> Accepted plan controller judgment: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-controller-judgment-20260527.md`

## Verdict: BLOCKED

One material/blocking finding. The evidence worker failed to read public generated output files that contain complete source provenance, resulting in an incorrect terminal classification and premature termination before extraction-score and quality-gate.

## Findings

### F1 (BLOCKING): Public generated snapshot files contain complete eligible provenance — worker did not read them

**Severity**: BLOCKING / material

The evidence artifact records:

- `source_provenance_status`: `incomplete_not_exposed_in_completed_cli_stdout`
- `resolved_source`: not exposed by completed public CLI stdout
- `fallback_used`: not exposed by completed public CLI stdout
- `primary_failure_category`: not exposed by completed public CLI stdout
- `fallback_eligibility`: `not_eligible`
- `source_chain`: not exposed by completed public CLI stdout

These recordings are **factually incorrect**. The public generated files expose the complete provenance tuple:

**Evidence from `summary.md` (lines 42-46)**:

```
| fund_code | resolved_source_name | fallback_used | fallback_eligibility | source_provenance_status | source_provenance_reason |
| 096001 | eastmoney | true | eligible | complete | fallback_used_primary_failure_category_eligible |
```

**Evidence from `snapshot.jsonl` (all 16 records, 1 unique provenance tuple)**:

```json
{
  "source_provenance_schema_version": "repository_source_provenance.v1",
  "source_strategy": "primary_then_fallback",
  "resolved_source_name": "eastmoney",
  "fallback_used": true,
  "primary_failure_category": "unavailable",
  "fallback_eligibility": "eligible",
  "source_provenance_status": "complete",
  "source_provenance_reason": "fallback_used_primary_failure_category_eligible"
}
```

Under the accepted plan Section 5, this provenance is **eligible**:

- `fallback_used=true` with `primary_failure_category` exactly `unavailable` — matches eligible category (`not_found` or `unavailable`)
- `fallback_eligibility=eligible`
- Complete public provenance tuple with no missing fields
- No fail-closed category (`schema_drift`, `identity_mismatch`, `integrity_error`)

The accepted plan Section 5 states: "The future evidence artifact must record the public provenance tuple from the snapshot output." The snapshot output includes the generated files (`snapshot.jsonl`, `summary.md`, `errors.jsonl`) listed in the plan Section 4 as "Expected generated ignored paths." The worker narrowly interpreted "snapshot output" as CLI stdout only, ignoring the generated public files.

The controller judgment also states: "Keep generated outputs in ignored report paths and record actual generated paths in a tracked summary artifact." This implies the worker should have interacted with the generated paths.

**Required fix**: The evidence worker must re-run the evidence gate, reading `summary.md` or `snapshot.jsonl` after the snapshot command to extract the provenance tuple. With complete eligible provenance, the worker should then proceed to `extraction-score` and `quality-gate` and record quality results.

### F2 (MINOR): `fallback_eligibility` incorrectly recorded as `not_eligible`

**Severity**: Minor (subsumed by F1)

The evidence artifact records `fallback_eligibility: not_eligible` in the Public Source Provenance section. This is the worker's own assessment, not a recording of what the CLI output showed. The actual value in both `summary.md` and `snapshot.jsonl` is `eligible`. The worker appears to have set `not_eligible` based on the incorrect belief that provenance was not exposed, rather than recording the actual value from public outputs.

### F3 (INFORMATIONAL): `manager_strategy_text` shows 100% coverage in generated summary

**Severity**: Informational (not evaluated by worker, relevant for re-run)

The `summary.md` Field Coverage table shows:

```
| manager | manager_strategy_text | 1 | 100.0% (1/1) | 100.0% (1/1) |
```

This means `manager_strategy_text` has 100% coverage and 100% traceability. If the evidence re-run reaches quality interpretation, this field should not be a P0 block for missing data. However, the worker did not evaluate this because of the premature stop, which is consequential to F1.

## Review Question Answers

### Q1: Did the evidence worker follow the accepted gate scope?

**Partially.** The worker correctly limited to 096001/2024, ran no fallback candidates, attempted no promotion, and used only public CLI commands. However, the worker failed to read the public generated output files that the CLI produced, which are part of the "snapshot output" referenced in the accepted plan Section 5.

### Q2: Are the recorded command outcomes and generated paths credible?

**Partially.** The snapshot command exit code 0 and generated file paths match actual files on disk. The `errors.jsonl` is empty (0 bytes), consistent with successful snapshot generation. 16 snapshot records match `summary.md` report. However, the provenance recording is incorrect — not because the command failed, but because the worker did not read the generated files.

### Q3: Is the terminal classification `provenance_incomplete_not_run_quality` correct?

**No. This is incorrect.** The provenance is complete and eligible in the public generated files. The correct action was to record the provenance tuple from `summary.md` or `snapshot.jsonl`, determine eligibility, and continue to `extraction-score` and `quality-gate`. The terminal classification should be determined after quality evaluation, not at the provenance step.

The worker should have read the public generated files (`snapshot.jsonl` or `summary.md`) to extract source provenance. Both files are public CLI outputs generated by the `extraction-snapshot` command, listed as expected outputs in the accepted plan Section 4, and are accessible without inspecting any PDF/cache/source-helper/downloader/source-adapter internals.

### Q4: Is provenance truly not exposed in public outputs?

**No. Provenance IS fully exposed in public outputs.** See F1 for complete evidence with file paths and exact field values. All five required provenance fields are present: `resolved_source_name`, `fallback_used`, `primary_failure_category`, `fallback_eligibility`, and `source_provenance_status`. Additionally, `source_strategy` and `source_provenance_schema_version` are available.

### Q5: Is `promotion_disposition=not_promoted` confirmed?

**Yes.** The evidence artifact records `promotion_disposition=not_promoted` and no source-safe/scoring-ready/baseline/golden/accepted replacement claim was made. This field is correctly recorded even though the reason (provenance incompleteness) is incorrect.

### Q6: Do generated reports stay ignored/untracked?

**Yes.** `reports/extraction-snapshots/` is covered by `.gitignore`. `git status --short` in the evidence artifact confirms no reports path appeared. The only tracked-intended artifact is the evidence document itself in `docs/reviews/`.

### Q7: Are there boundary violations or missing required fields?

**No boundary violations detected.** The worker did not modify code, tests, design docs, control docs, or internals. No PDF/cache/source-helper inspection occurred.

**Missing/incomplete fields (consequential to F1):**

- Public provenance tuple: recorded as "not exposed" when it is exposed — material incorrectness
- Quality status, P0 issues, P1 issues: not evaluated due to premature stop — would have been required if provenance were correctly identified as eligible
- `manager_strategy_text` status: not evaluated — would have been required
- Candidate identity missing explicit accepted enumeration row reference (plan Section 9 requires "accepted enumeration row identity")

## Required Fixes Before Acceptance

1. **Re-run the evidence gate**: The worker must re-execute the gate, reading `summary.md` or `snapshot.jsonl` after the snapshot command succeeds to extract the provenance tuple.
2. **Record correct provenance values**: `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`.
3. **Determine provenance eligibility**: Under the accepted plan, this tuple is eligible (fallback with `unavailable` primary failure and `eligible` fallback eligibility).
4. **Continue to extraction-score and quality-gate**: Run the planned score and quality commands with explicit paths.
5. **Record quality results**: Including P0/P1 issues, `manager_strategy_text` status, and determine the correct terminal classification from the plan's terminal-state matrix.
6. **Update terminal classification**: Based on actual quality results, not premature provenance stop.

## Residual Risks for Controller

| Risk | Description | Mitigation |
|---|---|---|
| Provenance eligible but quality unknown | The snapshot generated successfully with eligible provenance, but quality has not been evaluated. | Re-run evidence gate through quality-gate. |
| `manager_strategy_text` coverage is 100% but quality not assessed | Summary shows full coverage/traceability, but actual field quality requires extraction-score and quality-gate evaluation. | Do not assume quality pass from coverage alone. |
| Worker methodology gap | The worker interpreted "snapshot output" narrowly as CLI stdout only. Future gates should explicitly state that generated public output files are valid provenance sources. | Controller may consider adding explicit guidance to future evidence plan templates. |
| Score and quality-gate command outcomes unknown | Commands 5 and 6 were not run. Their exit codes and outputs are untested. | Re-run must cover full planned command sequence. |
