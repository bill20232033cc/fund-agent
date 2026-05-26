# Source Provenance Output Design Plan Review — MiMo

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-coverage-replacement-source-provenance-design-plan-20260527.md`
> Checkpoint: `e41c829 docs: accept index qdii recovery evidence`
> Review scope: adversarial plan review; no code, commit, push, or PR changes authorized

## Review Focus Items

| # | Focus | Verdict |
|---|---|---|
| 1 | Prefer additive provenance over replacement-candidate selection given no approved candidates? | PASS |
| 2 | Avoid unsafe inference from successful CLI extraction to fallback eligibility? | PASS |
| 3 | Preserve FundDocumentRepository source strategy and fail-closed categories? | PASS |
| 4 | Keep renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, golden/baseline out of scope? | PASS |
| 5 | Output contract breadth, field completeness, and test coverage? | PASS_WITH_FINDINGS |
| 6 | Future implementation file/test scope code-generation readiness? | PASS_WITH_FINDINGS |

## Overall Verdict

**PASS_WITH_FINDINGS**

The plan is architecturally sound. It correctly identifies the two paths, selects the safe one with evidence-based reasoning, avoids the unsafe inference fallacy, preserves all fail-closed source semantics, and maintains correct non-scope boundaries. Findings are informational and do not block acceptance.

## Detailed Analysis

### 1. Path Selection: Additive Provenance over Replacement

The plan's reasoning is correct and well-grounded:

- Checkpoint `e41c829` evidence shows `not_run_no_approved_candidates` for both rows' replacement subgates.
- The plan correctly identifies that replacement selection without candidates is either a no-op or would violate `no ad hoc web/search` and `no direct PDF/cache/helper` constraints.
- The decision to design additive provenance as the next safe gate path is the shortest safe path forward.

No findings.

### 2. Unsafe Inference Avoidance

The plan explicitly addresses the core safety argument in the "First-Principles Decision" section:

> "A successful later extraction is only indirect evidence that a document was obtained; it is not direct evidence that the fallback was allowed. Using it as a baseline proof would collapse the fail-closed source contract into 'the run succeeded', which is exactly the unsafe inference the repository fallback taxonomy exists to prevent."

This is correct. The plan preserves the distinction between "the CLI completed a run" (downstream observation) and "the source fallback was eligible" (upstream contract). No findings.

### 3. Fail-Closed Source Strategy Preservation

The contract correctly:

- Lists all 5 failure categories (`not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`) in `primary_failure_category`.
- Derives `fallback_eligibility` with explicit `fail_closed` for the three blocking categories.
- States contract rule: "Fail-closed preserving: schema_drift, identity_mismatch, and integrity_error must remain non-eligible and must not be hidden by downstream score or quality-gate success."
- Does not modify `FundDocumentRepository` source strategy, fallback eligibility decisions, or source adapters (explicit non-scope).

No findings.

### 4. Non-Scope Boundaries

The plan's explicit non-scope section correctly excludes:

- `FundDocumentRepository` source strategy and fallback eligibility decisions
- Source helpers, downloaders, cache layout, PDF access, source-specific adapters
- Renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, golden/baseline fixtures

No findings.

### 5. Output Contract Field Completeness

#### Finding 5.1 — `primary_failure_category` for multi-source failure chains (Informational)

The current source orchestration in `documents/sources.py` records a `failures: tuple[AnnualReportSourceFailure, ...]` chain when multiple sources are attempted. `AnnualReportSourceFallbackBlockedError.blocking_failure` identifies the terminal blocking category, while `AnnualReportSourceAggregateError.failures` records all non-blocking failures.

The contract defines `primary_failure_category` as a single value. For multi-source chains where the primary source fails with `not_found` (eligible) and the fallback succeeds, the category should be `not_found`. For chains where the primary fails with `schema_drift` (blocking), the category should be `schema_drift`. The plan does not explicitly specify which failure to select from the chain when multiple exist.

**Recommendation**: The future implementation gate should specify that `primary_failure_category` comes from the first failure in the chain when fallback did not occur, or from the blocking failure when `AnnualReportSourceFallbackBlockedError` was raised. When fallback succeeded, it should come from the primary source's failure that triggered the fallback attempt. This maps naturally to existing `AnnualReportSourceFailure.category` but should be stated to avoid ambiguity.

#### Finding 5.2 — `source_strategy` field derivation (Informational)

The contract lists `source_strategy` with example value `primary_then_fallback`. Today, no code records which strategy or priority order was used. The source orchestration in `sources.py` implicitly implements `primary_then_fallback` through its control flow, but this is not explicitly named or versioned.

**Recommendation**: The future implementation gate should define whether `source_strategy` is a new constant (e.g., always `primary_then_fallback` for current production), derived from source orchestration configuration, or read from a new metadata field. A constant is sufficient for v1 since the repository only has one strategy today.

#### Finding 5.3 — `fallback_eligibility` derivation completeness (Informational)

The contract lists four `fallback_eligibility` values: `eligible`, `fail_closed`, `not_applicable`, `unknown_public_metadata_absent`. The derivation rules are clear for the first three, but the plan should confirm:

- `eligible`: fallback occurred and the primary failure was `not_found` or `unavailable`.
- `fail_closed`: primary failure was `schema_drift`, `identity_mismatch`, or `integrity_error` (regardless of whether fallback was attempted).
- `not_applicable`: no primary failure occurred (direct source success).
- `unknown_public_metadata_absent`: source metadata is not available at the public output boundary.

These are implied by the plan's conservative-by-default rule but could be stated more explicitly in the implementation gate.

### 6. Implementation Readiness

#### Finding 6.1 — Source metadata propagation gap (Informational)

The agent exploration confirmed a critical implementation detail: `ParsedAnnualReport.metadata` (which carries `AnnualReportSourceMetadata` with `source`, `fallback_used`) is available at the document-repository layer but is **dropped at every downstream boundary**:

- `FundDataExtractor.extract()` discards metadata when building `StructuredFundDataBundle`.
- `SnapshotRecord` has no slot for source metadata.
- `extraction_score.py` has zero provenance fields.
- `quality_gate.py` is entirely blind to source provenance.

The plan's "Future Implementation File Scope" section correctly identifies "Agent/Fund public model — Add provenance projection fields to the extraction snapshot / score public records only where repository metadata is already available" and "Document repository metadata consumption — Read existing AnnualReportSourceMetadata / repository result metadata; do not change source orchestration."

**Recommendation**: The future implementation gate should explicitly call out the propagation chain: `StructuredFundDataBundle` needs an optional `source_metadata` field (or a new `SourceProvenanceRecord`), `SnapshotRecord` needs provenance slots, and `extraction_score.py` / `quality_gate.py` need to forward these fields. The plan's current "smallest plausible implementation surface" table is directionally correct but should specify that `StructuredFundDataBundle` is the first dataclass to change (it's where metadata is currently dropped).

#### Finding 6.2 — Test scope completeness (Informational)

The six test categories in "Future Test Scope" cover the critical paths:

1. Fallback eligible categories → `eligible`
2. Fail-closed categories → `fail_closed`
3. No-fallback primary success → `not_applicable`
4. Missing legacy provenance → `unknown` / `incomplete`
5. Public summary / JSONL includes provenance without changing existing keys
6. Existing CLI defaults, exit-code semantics, FQ thresholds, renderer, Service control flow unchanged

These are sufficient for the initial provenance contract gate. Category 6 (boundary regression) is particularly important since provenance is additive-only and must not change existing behavior.

**Optional enhancement**: The future gate may also want a test for the case where source metadata is available but `primary_failure_category` is `None` (direct primary success with no fallback attempt) to verify the `not_applicable` path end-to-end through snapshot/score/quality-gate.

#### Finding 6.3 — `primary_failure_category` not recoverable for existing rows (Informational)

The plan's "Residual Risks" section correctly notes that "Source provenance output may require threading existing repository metadata through public snapshot outputs." This is actually the harder constraint: for rows that were already extracted before the provenance contract exists, the `primary_failure_category` will not be available in their historical snapshot/score/gate outputs.

The plan's conservative-by-default rule handles this: "missing provenance for fallback-backed rows must classify as unknown/incomplete, not eligible." This is correct. The future implementation gate should confirm that historical outputs (including the `110020` and `017641` evidence runs) would retroactively show `unknown_public_metadata_absent` rather than `eligible`, which keeps them outside the clean denominator as expected.

## Summary of Findings

| # | Severity | Finding |
|---|---|---|
| 5.1 | Informational | `primary_failure_category` selection from multi-source failure chains should be specified |
| 5.2 | Informational | `source_strategy` derivation method should be defined (constant vs. config vs. metadata) |
| 5.3 | Informational | `fallback_eligibility` derivation rules could be more explicit in implementation gate |
| 6.1 | Informational | Source metadata propagation gap: `StructuredFundDataBundle` is the first dataclass to change |
| 6.2 | Informational | Test scope is complete; optional enhancement for direct-success `not_applicable` end-to-end path |
| 6.3 | Informational | Historical rows will show `unknown_public_metadata_absent`; conservative default is correct |

All findings are informational. The plan is architecturally sound and safe for acceptance.
