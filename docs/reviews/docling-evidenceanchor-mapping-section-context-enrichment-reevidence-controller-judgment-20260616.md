# Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Controller Judgment - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Gate`
Controller role: AgentController
Release/readiness: `NOT_READY`

## Scope

This judgment closes the no-live/local-artifact re-evidence gate for Docling section-context enrichment.

This judgment does not authorize production parser replacement, production `EvidenceAnchor` admission, source acquisition, source policy change, Service/Host/UI/renderer/quality gate change, provider/LLM route change, baseline promotion, readiness, release, PR, push or merge.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-20260616.md` | re-evidence artifact |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-review-ds-20260616.md` | DS evidence review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-review-mimo-20260616.md` | MiMo evidence review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-fix-evidence-20260616.md` | evidence disclosure fix |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-controller-judgment-20260616.md` | accepted implementation judgment |

## Accepted Facts

- Mapping yield improved from `102 / 23475 = 0.43%` to `9389 / 23475 = 40.00%`.
- Table/cell candidate mapping improved from zero to `9101 / 19688 = 46.23%`.
- All mapped and blocked records retained candidate-only assertions:
  - `candidate_only=True`
  - `candidate_source="docling"`
  - `field_correctness_status="not_proven"`
  - `source_truth_status="not_proven"`
- S1 full JSON remains blocked as unsupported schema residual and was not used as mapped evidence.
- Re-evidence was local/no-live and did not run source acquisition, PDF/FDR, provider/LLM, readiness, release, PR, push or merge commands.

## Review Finding Disposition

| Finding | Disposition | Controller judgment |
| --- | --- | --- |
| DS finding 01: S1-current-envelope and S1-full-json relationship not disclosed | ACCEPTED_AND_FIXED | Re-evidence now states S1 counts represent the accepted envelope path only and do not prove S1-full-json behavior after future schema/export disposition. |
| DS finding 02 / MiMo finding 02: schema-family aggregation and paragraph mapping caveat | ACCEPTED_AND_FIXED | Re-evidence now warns that `S1_full` and `S4_S5_S6_lightweight` have different validation rules and that paragraph mapping is S1-envelope-specific in this matrix. |
| MiMo finding 01: S5/S6 yield variance not explained | ACCEPTED_AS_RESIDUAL | S6 low yield remains a next-gate residual; variance analysis is not required to accept the mapping-improvement fact. |

## Controller Decision

The re-evidence is accepted as a real engineering improvement signal for Docling candidate EvidenceAnchor mapping. It is not a baseline promotion proof.

The evidence answers the immediate question that motivated the section-context implementation: after applying deterministic section-context enrichment, accepted real local artifacts now produce non-zero and materially improved table/cell candidate mappings.

It does not answer the remaining baseline questions:

- Are the mapped table/cell values field-correct against same-source evidence?
- Does the low-yield S6 sample represent a structural limitation or sample-specific section duplication?
- Can S1-full-json be exported into the accepted envelope path without changing meaning?
- Are performance/cache/cost characteristics acceptable as a default baseline route?

## Residuals

| Residual | Status | Next owner |
| --- | --- | --- |
| Field correctness | not proven | comparative correctness evidence gate |
| Source truth | not proven | future source-truth/baseline disposition gate |
| S6 low yield (`507 / 6064 = 8.36%`) | carried | comparative/root-cause evidence |
| `missing_section_context` remains high among blocked records | carried | candidate mapping owner |
| S1 full JSON unsupported schema | carried | export/schema disposition gate |
| Performance/cache/cost baseline suitability | not proven | performance/cache/cost evidence gate |
| Release/readiness | `NOT_READY` | future readiness gate |

## Next Gate Recommendation

Proceed to:

```text
Docling Field Correctness Comparative Evidence Gate
```

This next gate should use accepted local candidate mappings and same-source reviewed reference facts where already available. It must not run live/source acquisition/PDF/FDR unless separately authorized, and it must not promote baseline/readiness.

Deferred after correctness:

- `Docling S6 Low-yield Root-cause Evidence Gate`
- `S1 Full-json Envelope Export Disposition Gate`
- `Docling Performance / Cache / Cost Evidence Gate`
- `Docling Baseline Disposition Controller Judgment`

## Final Verdict

```text
VERDICT: ACCEPT_REEVIDENCE_IMPROVED_MAPPING_NOT_READY
```
