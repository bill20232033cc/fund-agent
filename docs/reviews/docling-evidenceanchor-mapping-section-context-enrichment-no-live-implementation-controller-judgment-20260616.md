# Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Controller Judgment - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Gate`
Controller role: AgentController
Release/readiness: `NOT_READY`

## Scope

This controller judgment closes the no-live implementation gate for deterministic Docling section-context enrichment.

Accepted implementation write set:

- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`

This judgment does not authorize production parser replacement, source acquisition, source policy changes, production `EvidenceAnchor` conversion, Service/Host/UI/renderer/quality gate changes, provider/LLM commands, field-correctness claims, source-truth claims, baseline promotion, readiness/release action, PR, push or merge.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-controller-judgment-20260616.md` | accepted implementation plan and write set |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-evidence-20260616.md` | implementation evidence and validation |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-review-ds-20260616.md` | DS implementation review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-review-mimo-20260616.md` | MiMo implementation review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-fix-evidence-20260616.md` | accepted fix evidence |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-re-review-ds-20260616.md` | DS re-review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-re-review-mimo-20260616.md` | MiMo re-review |

## Accepted Implementation Facts

- The implementation adds deterministic section-context enrichment under candidate internals only.
- Public mapping API signatures remain stable.
- Document-level mapping builds an internal section index once and passes it through private helpers.
- Numeric headings require closed keyword-family validation; unsupported numeric/chinese heading patterns fail closed.
- Deterministic TOC/目录 nodes do not seed body spans.
- Duplicate, non-monotonic, cross-section and unsupported-heading cases fail closed with explicit reason codes.
- Text/table blocks may inherit section context only through stable page spans.
- Cells inherit section context from the resolved parent table only; row/column labels do not infer sections.
- Candidate output remains non-production: `candidate_only=True`, `candidate_source="docling"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`.

## Review Finding Disposition

| Finding | Disposition | Controller judgment |
| --- | --- | --- |
| DS finding 01: final stable span could absorb later unindexed pages | ACCEPTED_AND_FIXED | Later unindexed positive section-node pages now close previous stable spans; re-review PASS. |
| MiMo finding 02: same-page distinct top-level duplicate not detected | ACCEPTED_AND_FIXED | Duplicate detection now uses distinct non-child node IDs; re-review PASS. |
| Public single-block API rebuilds `SectionIndex` | DEFER | Correctness unaffected; document-level API builds once; public API signature remains stable. |
| Non-dot child heading detection may over-block | DEFER | Current behavior fails closed; real-artifact frequency belongs to re-evidence. |
| Remaining performance/residual observations | DEFER | Not part of accepted fix set and not blocking no-live implementation acceptance. |

## Validation

Controller re-ran:

```text
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
36 passed in 0.55s
```

```text
uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

Result:

```text
All checks passed!
```

```text
git diff --check
```

Result: passed.

## Residuals

| Residual | Status | Next owner |
| --- | --- | --- |
| Table/cell yield on accepted real artifacts | unproven | re-evidence gate |
| Field correctness | not proven | comparative correctness gate |
| Source truth | not proven | baseline disposition gate |
| S1 full JSON current-envelope mismatch | deferred | separate export/evidence disposition |
| Runtime/cache/cost baseline suitability | not proven | performance/cache/cost gate |
| Release/readiness | `NOT_READY` | future readiness gate |

## Next Gate Recommendation

Proceed to:

```text
Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Gate
```

The re-evidence gate must use accepted local candidate artifacts only and must not claim field correctness, source truth, baseline promotion or readiness.

## Final Verdict

```text
VERDICT: ACCEPT_IMPLEMENTATION_NO_LIVE_NOT_READY
```
