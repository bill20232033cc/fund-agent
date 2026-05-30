# Source Provenance Output Design Plan Targeted Re-Review — MiMo

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-coverage-replacement-source-provenance-design-plan-20260527.md` (revised)
> Original review: `docs/reviews/release-maintenance-coverage-replacement-source-provenance-design-plan-review-mimo-20260527.md`
> Review scope: targeted re-review of revisions against original findings; no code, commit, push, or PR changes authorized

## Re-Review Checklist

| # | Original Finding | Revision Location | Addressed? |
|---|---|---|---|
| 5.1 | `primary_failure_category` multi-source chain selection rule | Contract rules, line 84 | YES |
| 5.2 | `source_strategy` derivation method | No change needed; plan already adequate | YES |
| 5.3 | `fallback_eligibility` derivation rules explicitness | Contract rules, line 82 + test scope, lines 115-116 | YES |
| 6.1 | Source metadata propagation gap / ownership | File scope table, lines 94 + 96 | YES |
| 6.2 | `not_applicable` consistency end-to-end test | Test scope, line 113 | YES |
| 6.3 | Historical rows `unknown_public_metadata_absent` | Contract rules, line 82 + test scope, line 115 | YES |

## Detailed Re-Review

### Finding 5.1 — Multi-source chain selection rule

**Revision** (contract rules, line 84):
> "Multi-source chains must have their `primary_failure_category` selection rule specified in the future implementation gate. If the public output cannot determine the applicable primary failure category for the chain, conservative `unknown_public_metadata_absent` applies."

**Assessment**: Adequately addressed. The plan defers the exact selection rule to the implementation gate (where code-level access to `AnnualReportSourceFailure` chain semantics is available) while requiring a conservative fallback if the rule cannot be determined. This is the correct design-level boundary: the plan establishes the invariant (conservative default), the implementation gate specifies the mechanism.

### Finding 5.2 — `source_strategy` derivation

**Assessment**: No revision needed. The plan uses `primary_then_fallback` as a descriptive example. Since the repository only has one strategy today, a constant is sufficient. The implementation gate can formalize this without plan-level change.

### Finding 5.3 — `fallback_eligibility` derivation completeness

**Revision** (contract rules, line 82):
> "If `fallback_used=true` and `primary_failure_category` is `null` or unavailable because current metadata does not persist the failure category, `fallback_eligibility` MUST be `unknown_public_metadata_absent`, not `eligible`. This cannot be relaxed except by a later accepted gate that threads `AnnualReportSourceFailure.category` through metadata and public output."

**Revision** (test scope, lines 115-116):
> "Fallback-backed rows with `fallback_used=true` and missing / unavailable `primary_failure_category` classify as `fallback_eligibility="unknown_public_metadata_absent"`, not eligible."

**Assessment**: Adequately addressed. The contract rule now explicitly defines the critical edge case: `fallback_used=true` + missing category = `unknown_public_metadata_absent`, never `eligible`. The gate-relaxation condition is correctly scoped to a future accepted gate that threads the failure category through metadata. The test scope adds a dedicated test case for this path.

### Finding 6.1 — Source metadata propagation gap / ownership

**Revision** (file scope table):
- Line 94: "Own a pure projection function in `fund_agent/fund` that maps `AnnualReportSourceMetadata` / public repository metadata to additive public provenance fields. This function must be deterministic, side-effect-free, and must not reach into source helpers."
- Line 96: "Consume the Agent/Fund projection result and include additive provenance fields in `ExtractionSnapshotService` output and any summary artifact generated from that output. Service must not invert dependencies into source internals or access source helpers."

**Assessment**: Adequately addressed. The revised plan explicitly defines:
- **Ownership**: `fund_agent/fund` owns the pure projection function.
- **Consumption**: Service consumes the projection result; no dependency inversion.
- **Boundary**: No reaching into source helpers from either layer.

This answers the propagation gap question: the projection function is the bridge between `AnnualReportSourceMetadata` (document layer) and public output fields (snapshot/score layer). The implementation gate will need to thread metadata through `StructuredFundDataBundle` to make this projection possible, but the plan correctly identifies the ownership boundary.

### Finding 6.2 — `not_applicable` consistency test

**Revision** (test scope, line 113):
> "Consistency assertion: rows with `source_provenance_status="not_applicable"` must have `fallback_eligibility="not_applicable"` and `fallback_used=false`."

**Assessment**: Adequately addressed. This is an explicit cross-field consistency assertion that ensures the `not_applicable` path is internally coherent end-to-end.

### Finding 6.3 — Historical rows

**Revision** (contract rules, line 82 + test scope, line 115):
The `fallback_used=true` + missing category → `unknown_public_metadata_absent` rule, combined with the dedicated test case, ensures historical rows that lack source provenance metadata will be classified conservatively.

**Assessment**: Adequately addressed. Historical rows (including `110020` and `017641` evidence runs) will show `unknown_public_metadata_absent` because their snapshot/score/gate outputs do not contain source provenance fields. The conservative default keeps them outside the clean denominator as expected.

## Verdict

**PASS**

All 6 original findings are adequately addressed by the revised plan. The revisions are scoped correctly: they add design-level invariants and deferral rules without over-specifying implementation details that belong in the implementation gate.
