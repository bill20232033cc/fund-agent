# QDII Replacement Candidate Evidence Review — AgentDS

> Date: 2026-05-27
> Reviewer: AgentDS (independent evidence reviewer, not controller)
> Gate: `QDII replacement candidate evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-controller-judgment-20260527.md`
> Review artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-ds-20260527.md`
> Verdict: **BLOCKED**

## 1. Review Scope Adherence

This review inspects only:
- The tracked evidence artifact.
- The accepted plan and controller judgment.
- Public generated output files under `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/`, as explicitly authorized by the review scope.

This review does NOT run new fund-analysis commands, inspect PDF/cache/source-helper/downloader/source-adapter internals, or modify code/tests/docs.

## 2. Findings

### Finding 1 — BLOCKING: Terminal classification is incorrect; public generated files contain complete provenance

**Severity: BLOCKING**

The evidence artifact claims (line 72):

> `source_provenance_status`: `incomplete_not_exposed_in_completed_cli_stdout`

And at line 108–109:

> `terminal_classification`: `provenance_incomplete_not_run_quality`
> `promotion_disposition`: `not_promoted`

This claim is **factually contradicted by the public generated output files** that the snapshot command itself produced.

**Evidence from `summary.md`** (lines 42–46):

| fund_code | resolved_source_name | fallback_used | fallback_eligibility | source_provenance_status | source_provenance_reason |
|---|---|---|---|---|---|
| 096001 | eastmoney | true | eligible | complete | fallback_used_primary_failure_category_eligible |

**Evidence from `snapshot.jsonl`** — every one of the 16 records contains identical provenance fields:

```json
{
  "resolved_source_name": "eastmoney",
  "fallback_used": true,
  "primary_failure_category": "unavailable",
  "fallback_eligibility": "eligible",
  "source_provenance_status": "complete",
  "source_provenance_reason": "fallback_used_primary_failure_category_eligible",
  "source_strategy": "primary_then_fallback",
  "source_provenance_schema_version": "repository_source_provenance.v1"
}
```

The required provenance tuple under the accepted plan §5 is fully present:

| Required field | Present? | Value |
|---|---|---|
| `source_provenance_status` | Yes | `complete` |
| `resolved_source` | Yes | `eastmoney` |
| `fallback_used` | Yes | `true` |
| `primary_failure_category` | Yes | `unavailable` |
| `fallback_eligibility` | Yes | `eligible` |
| source_chain / equivalent | Yes | `source_strategy=primary_then_fallback` + `source_provenance_schema_version` |

Under the accepted plan §5, `primary_failure_category=unavailable` with `fallback_eligibility=eligible` is an **eligible provenance state**. The plan states (line 146–147):

> - primary source success with no fallback and complete public provenance; or
> - fallback with `primary_failure_category` exactly `not_found` or `unavailable`, public `fallback_eligibility=eligible`, and complete public provenance.

All conditions for the second eligible path are met.

**Correct terminal classification should have been**: proceed to `extraction-score`, then `quality-gate`. The terminal state should have been determined by score/quality results per the accepted plan §7 matrix — NOT by a premature `provenance_incomplete` stop.

**Impact**: The evidence worker stopped before running `extraction-score` and `quality-gate` (commands 5 and 6), depriving the controller of the full evidence picture. The gate must be re-run.

### Finding 2 — Terminal classification name does not match plan matrix

**Severity: HIGH**

The evidence artifact uses `provenance_incomplete_not_run_quality` (line 108). This classification does not appear in the accepted plan §7 terminal-state matrix. The plan defines:

- `provenance_unknown_public_metadata_absent`
- `provenance_incomplete_not_promoted`

Neither matches `provenance_incomplete_not_run_quality`. The evidence worker introduced a non-standard classification. Even if provenance were truly missing (which it is not, per F1), the correct classification under the plan would be `provenance_incomplete_not_promoted`.

### Finding 3 — Evidence worker relied exclusively on CLI stdout, ignoring public generated output files that the accepted plan explicitly treats as evidence

**Severity: HIGH (root cause of F1)**

The evidence artifact states (line 81):

> The completed public snapshot command succeeded, but the bounded stdout exposed only generated artifact paths.

And (line 82):

> Within the explicitly allowed command set, no additional public provenance inspection command was available before running score or quality-gate.

These statements treat "public evidence" as equivalent to "CLI stdout text only." But the accepted plan §4 (lines 88–93) explicitly lists the expected generated ignored paths (`snapshot.jsonl`, `summary.md`, `errors.jsonl`) and §5 (lines 127–135) requires recording the provenance tuple "from the snapshot output" — it does not restrict the evidence source to stdout. The controller judgment (line 64) also refers to "generated output paths" without restricting them to stdout-only inspection.

The generated `summary.md` is a human-readable public output that the snapshot command printed a path for. Reading it is within the public CLI surface. The evidence worker's self-imposed restriction to stdout-only is not in the plan and caused the premature stop.

### Finding 4 — Scope compliance: single candidate, no fallback, no promotion

**Severity: INFO (positive finding)**

The evidence worker correctly:
- Limited scope to `096001` / 2024 only (plan §2, line 27–35).
- Did not run fallback candidates (plan §9, preserved fallback order untouched).
- Did not attempt promotion to source-safe, scoring-ready, baseline, golden, or accepted replacement.
- `promotion_disposition=not_promoted` is correctly recorded.
- No code, tests, renderer, FQ0-FQ6, Service/CLI defaults, FundDocumentRepository, taxonomy, extractor, Host/Agent/dayu, fixtures, baseline/golden corpus, design doc, or control doc were modified.

### Finding 5 — Generated reports are untracked

**Severity: INFO (positive finding)**

`git status --short` confirmed no `reports/extraction-snapshots/` paths appear. Generated output files remain ignored/untracked. The only tracked artifact from this evidence run is the evidence artifact itself.

### Finding 6 — No boundary violations in evidence fields

**Severity: INFO (positive finding)**

The evidence artifact includes all required fields from the plan §9: Startup Packet replay, candidate identity, preflight help results, exact commands and exit codes, generated ignored paths, provenance section, quality section (correctly marked not run), terminal classification, `promotion_disposition=not_promoted`, and confirmations of no internal inspection or code/docs mutation. The fields themselves are structurally complete, even though the provenance values within them are wrong (per F1).

### Finding 7 — Provenance values, when read from generated files, are eligible for scoring

**Severity: INFO (for controller awareness)**

The actual provenance from the generated outputs is:
- `resolved_source_name=eastmoney` — Eastmoney fallback was used
- `primary_failure_category=unavailable` — eligible under plan §5
- `fallback_eligibility=eligible` — eligible
- `source_provenance_status=complete` — complete

This is a fully eligible provenance state. The `manager_strategy_text` field has `value_present=true`, `anchor_present=true`, and 100% coverage/traceability per `summary.md`. The quality gate should have been reachable.

## 3. Explicit Answers to Review Questions

### Q1: Did the evidence worker follow the accepted gate scope?

**Yes**, with respect to candidate identity (`096001` / 2024 only), public CLI only, no fallback candidates, no promotion. The scope boundary was respected.

### Q2: Are the recorded command outcomes and generated paths credible?

**Partially**. Commands 1–4 (help + snapshot) have correct exit codes and the generated paths are verified to exist. But the provenance values recorded in the evidence artifact (lines 72–77) are **not credible** — they claim provenance is incomplete/not-exposed, while the generated files prove otherwise.

### Q3: Is `provenance_incomplete_not_run_quality` correct?

**No. This is the blocking finding.** The public generated files (`summary.md` line 42–46, `snapshot.jsonl` every record) expose complete source provenance. The correct action under the accepted plan was to proceed to `extraction-score` and `quality-gate`. The terminal classification is factually wrong.

### Q4: Do public generated files expose provenance?

**Yes, conclusively.** See Finding 1 evidence above. Both `snapshot.jsonl` (all 16 records) and `summary.md` (Source Provenance table) contain the full provenance tuple required by the plan §5.

### Q5: Is `promotion_disposition=not_promoted` and no replacement claim confirmed?

**Yes.** The evidence worker correctly maintained `not_promoted` and made no source-safe/scoring-ready/baseline/golden/accepted replacement claim.

### Q6: Are generated reports ignored/untracked except the evidence artifact?

**Yes.** Confirmed via `git status --short` and direct file listing. Only the evidence artifact is tracked (untracked, intended for commit).

### Q7: Boundary violations or missing required fields?

**No boundary violations.** No code, tests, docs, or internals were modified. Required fields are structurally present, though the provenance field values are incorrect (see F1).

## 4. Required Fixes Before Acceptance

1. **The evidence gate must be re-run** with correct interpretation of public outputs. The evidence worker must:
   - Read `snapshot.jsonl` and/or `summary.md` to extract the public provenance tuple.
   - Recognize that `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete` is an eligible state under plan §5.
   - Proceed to run `extraction-score` and `quality-gate` with explicit paths.
   - Record the actual terminal classification from the plan §7 matrix based on score/quality results.

2. The evidence worker must not restrict "public CLI output" to stdout alone. Generated artifact paths printed by the CLI and written to the public output directory are public outputs.

3. The terminal classification must use a name from the plan §7 matrix, not an ad-hoc name.

## 5. Residual Risks for Controller

| Risk | Severity | Notes |
|---|---|---|
| Eastmoney fallback was used (`resolved_source_name=eastmoney`) | MEDIUM | `primary_failure_category=unavailable` means the primary source was not reachable. The controller should note that all extraction data for 096001 comes from the Eastmoney fallback path. This is eligible under the plan but may affect baseline quality expectations. |
| Evidence worker may have misread the scope instruction | MEDIUM | The instruction says "public CLI only" but the worker interpreted this as "stdout only," ignoring generated public files. The controller should clarify in future evidence handoffs that generated public output files under `reports/` are within the public evidence surface. |
| `extraction-score` and `quality-gate` remain not run | HIGH | These commands are pending and must be run in the re-executed evidence gate. Their results will determine the actual terminal classification. |
| `manager_strategy_text` has `value_present=true` with 100% traceability from snapshot | LOW | This is positive — the P0 field is present, reducing the chance of a `quality_blocked_after_provenance` outcome when score/quality-gate are re-run. |

## 6. Review Method

- Read the evidence artifact in full.
- Read the accepted plan and controller judgment in full.
- Verified generated output file existence and contents (`snapshot.jsonl`, `summary.md`, `errors.jsonl`).
- Cross-referenced provenance claims in the evidence artifact against the actual generated file contents.
- Checked `git status --short` for boundary violations.
- No fund-analysis commands were executed; no code, tests, or docs were modified.
