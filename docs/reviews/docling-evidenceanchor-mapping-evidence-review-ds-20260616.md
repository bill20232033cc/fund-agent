# Docling EvidenceAnchor Mapping Evidence Review (DS) - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Evidence Gate`
Role: AgentDS (evidence review)
Release/readiness: `NOT_READY`

## 1. Scope

This artifact reviews `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` for correctness of distinction between implementation success and real-artifact yield limitation, proper handling of S1 schema mismatch, internal arithmetic consistency, preservation of candidate-only/not_proven/NOT_READY status, and correctness of next-gate recommendation. No code changes, stage, commit, push, or PR.

## 2. Inputs Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current startup truth |
| `docs/implementation-control.md` | Current control truth |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-controller-judgment-20260616.md` | Accepted implementation controller judgment |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` | Under-review evidence artifact |

## 3. Allowed Commands Executed

```bash
git diff -- docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Results:

| Check | Result |
|---|---|
| git diff (evidence doc) | No diff (unchanged since write) |
| pytest mapping tests | `12 passed in 0.75s` |

The `12 passed` count matches the implementation controller judgment claim.

## 4. Review Findings

### 4.1 Implementation Success vs Real-Artifact Yield Limitation — PASS

The evidence correctly distinguishes:
- **Implementation success**: the mapping helper is fail-closed and can emit candidate-only heading anchors where section context is explicit (§3, §7).
- **Real-artifact yield limitation**: current artifacts do not provide sufficient section context for table/cell anchor emission (§3: "Mapped anchor type coverage in this evidence: `heading` only"; §7: "current real artifacts are not sufficient for table/cell EvidenceAnchor candidate yield without section-context enrichment or mapping rule expansion").

The evidence does **not** misrepresent heading-only partial mapping as table/cell readiness or baseline promotion.

### 4.2 S1 Full JSON Schema Mismatch Disposition — PASS

S1 full JSON schema divergence is correctly identified and dispositioned:
- §2 Inputs: explicitly records that `project_candidate_representation()` rejects S1 full JSON with `ValueError: unsupported candidate representation schema_version`.
- §5 Blocked Samples: S1-full-json listed with reason `unsupported candidate representation schema_version`.
- §8 Residuals: carried forward as open residual with explicit recommendation to decide whether to regenerate/export full S1 as `candidate_annual_report_representation.v1` or keep current-envelope-only evidence.

Not ignored. Not silently absorbed into a passing count.

### 4.3 Per-Sample Matrix Internal Consistency — PASS

Each sample row in §3 is internally consistent:

| Sample | Sections+Text+Tables+Cells | Mapped+Blocked | Block reasons sum | Match |
|---|---|---|---|---|
| S1-current-envelope | 25+670+95+3493 = 4283 | 10+4273 = 4283 | 4270+3 = 4273 | ✓ |
| S4-full | 229+737+96+2759 = 3821 | 33+3788 = 3821 | 3786+2 = 3788 | ✓ |
| S5-full | 208+856+121+7060 = 8245 | 28+8217 = 8245 | 8214+3 = 8217 | ✓ |
| S6-full | 222+840+124+5940 = 7126 | 31+7095 = 7126 | 7093+2 = 7095 | ✓ |

Mapped total: 10+33+28+31 = 102. Evidence doc states 102. ✓

### 4.4 Aggregate Blocked Count Inconsistency — FINDING (F1)

Per-sample blocked totals from §3 matrix: 4273 + 3788 + 8217 + 7095 = **23373**.

Evidence doc §3 states: "Total blocked candidate blocks across accepted envelopes: **`23473`**."

The stated total exceeds the per-sample sum by **100**. The gap is unexplained. The S1-full-json entry in §5 is a sample-level block (rejected pre-mapping) with zero per-block contribution, so it does not account for the 100-block delta.

This is an internal inconsistency. The per-sample rows are self-consistent; only the aggregate figure is wrong.

**Severity**: Non-blocking. The substantive conclusions (heading-only yield, missing_section_context dominance, candidate-only status) are unaffected by the exact blocked count. The finding is a numerical accuracy issue in the evidence document.

### 4.5 Candidate-only / NOT_READY Status Preservation — PASS

All required statuses are preserved throughout:
- §4: "Every mapped output remains `candidate_only=True`, `candidate_source="docling"`, `field_correctness_status="not_proven"` and `source_truth_status="not_proven"`."
- Title: `Release/readiness: NOT_READY`
- §7 explicitly disclaims source truth, full field correctness, table/cell production anchor readiness, Docling baseline promotion, production parser replacement, and readiness/release/PR state.
- §8 Candidate anchors residual: "remain non-production and non-proof."

No promotion or readiness claim is made.

### 4.6 Next Gate Correctness — PASS

§8 Residuals recommends: "`Docling EvidenceAnchor Mapping Section-context Enrichment Planning Gate`" as the next handling for table/cell mapping yield.

This correctly targets section-context enrichment planning, not production integration, parser replacement, baseline promotion, or readiness gating. Aligned with the controller judgment's deferred entries (§7: Docling field correctness comparative evidence, performance/cache/cost evidence, baseline disposition, production parser/repository integration).

### 4.7 Missing-Section-Context Dominance — PASS

Across all four samples, `missing_section_context` accounts for 4270+3786+8214+7093 = 23363 of 23373 blocked blocks (99.96%). This is consistent with the evidence narrative (§5): "The dominant failure mode is section-context shape mismatch." The evidence correctly ties this to explicit §-token and closed-keyword-family consumption in the current mapping helper.

## 5. Findings Summary

| ID | Category | Description | Severity |
|---|---|---|---|
| F1 | Numerical accuracy | Aggregate blocked count stated as 23473, but per-sample blocked totals sum to 23373 (gap of 100). Per-sample rows are internally consistent. | Non-blocking |

## 6. Residuals

| Residual | Owner | Handling |
|---|---|---|
| F1 blocked-count discrepancy | Evidence worker / controller | Correct the aggregate figure in evidence artifact or explain the 100-block source. Does not block gate acceptance. |
| Table/cell mapping yield zero on real artifacts | Fund documents candidate owner | Carried forward in evidence artifact §8; next gate remains section-context enrichment planning. |
| S1 full JSON schema version gap | Fund documents candidate owner | Carried forward in evidence artifact §8; regeneration vs current-envelope-only decision deferred. |

## 7. Review Constraints Compliance

- [x] No code changes.
- [x] No stage/commit/push/PR.
- [x] No live/network/PDF/FDR/provider/LLM commands.
- [x] Only allowed commands used.
- [x] Verdict uses requested NOT_READY format.

## 8. Final Verdict

```text
VERDICT: PASS_WITH_FINDINGS_NOT_READY
```

The evidence correctly distinguishes implementation success from real-artifact yield limitation, does not misrepresent heading-only mapping as table/cell readiness or baseline promotion, correctly dispositions S1 full JSON schema mismatch as a residual/blocker, preserves all candidate-only/not_proven/NOT_READY statuses, and correctly recommends section-context enrichment planning (not production integration) as the next gate.

One non-blocking finding: the aggregate blocked count (23473) is inconsistent with the per-sample blocked totals (sum = 23373), a gap of 100.
