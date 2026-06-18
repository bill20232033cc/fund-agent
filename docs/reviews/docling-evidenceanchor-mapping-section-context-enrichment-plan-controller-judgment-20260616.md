# Docling EvidenceAnchor Mapping Section-context Enrichment Plan Controller Judgment - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Planning Gate`
Controller role: AgentController
Release/readiness: `NOT_READY`

## Scope

This controller judgment closes the planning gate for deterministic Docling section-context enrichment before any no-live implementation or mapping re-evidence.

This judgment does not authorize production parser replacement, production `EvidenceAnchor` output, source-truth claims, field-correctness claims, baseline promotion, live/source acquisition, provider/LLM commands, readiness/release actions, PR, push or merge.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | execution boundary, module ownership, evidence traceability and `NOT_READY` guardrails |
| `docs/design.md` | Docling candidate-layer status and candidate/production separation |
| `docs/implementation-control.md` | current mainline and accepted Docling evidence chain |
| `docs/current-startup-packet.md` | startup truth for current Docling mapping evidence residual |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-controller-judgment-20260616.md` | accepted prior gate: partial heading-only mapping evidence |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` | accepted counts: `102 / 23475 = 0.43%`, `23373` blocked, zero table/cell yield |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md` | plan under review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-review-ds-20260616.md` | DS plan review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-review-mimo-20260616.md` | MiMo plan review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-fix-evidence-20260616.md` | plan fix evidence |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-re-review-ds-20260616.md` | DS re-review |
| `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-re-review-mimo-20260616.md` | MiMo re-review |

## Accepted Current Facts

- Prior mapping evidence is accepted only as partial heading-only evidence.
- Accepted mapped yield is `102 / 23475 = 0.43%`.
- Accepted blocked total is `23373`, with `missing_section_context=23363` and `unstable_section_context=10`.
- Accepted table/cell candidate anchor yield is zero on accepted real artifacts.
- Candidate anchors remain non-production, non-source-truth, non-field-correctness proof and non-readiness proof.
- S1 full JSON remains outside the current candidate envelope schema and must not be silently accepted by mapping helpers.

## Review Finding Disposition

| Finding | Disposition | Controller judgment |
| --- | --- | --- |
| MiMo 01 / DS-F3 numeric heading closure | ACCEPT | Plan now explicitly requires changing the numeric-heading candidate path so `1..10` prefixes cannot bypass closed keyword-family validation. |
| DS-F1 / OQ1 TOC handling | ACCEPT | Plan now excludes deterministic TOC nodes from body section span seeding and fails closed when TOC/body ambiguity cannot be safely resolved. |
| DS-F2 monotonic ordering precision | ACCEPT | Plan now defines monotonicity as inter-section top-level ordering by selected body start page; same-section child nodes do not independently break ordering. |
| DS-F4 / OQ2 alias scope | ACCEPT | Plan now uses exact initial aliases only and prohibits implementation-worker discretionary alias expansion. |
| DS-F5 and MiMo 02/03 test fixture gaps | ACCEPT | Plan now includes concrete synthetic fixtures for new reason codes, numeric guards, TOC, page propagation, half-open spans and cell no-inference. |
| DS-F6 / OQ3 SectionIndex and span semantics | ACCEPT | Plan now requires an internal frozen `SectionIndex` or equivalent built once, private internal signature changes only, and half-open page spans. |
| MiMo 04 cell label dead branch | ACCEPT_WITH_REWRITE | Plan keeps code cleanup optional but makes behavioral test mandatory: cells must not infer sections from row or column labels. |

## Controller Decision

The fixed plan is accepted as handoff-ready for a narrow no-live implementation gate.

Binding implementation write set:

- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`

Implementation must not modify source acquisition, repository/cache/downloader, parser production behavior, production `EvidenceAnchor` schema, CHAPTER_CONTRACT, Service, Host, UI, renderer, quality gate, provider/LLM code, README, design docs, reports or control docs unless a later controller step explicitly authorizes control sync after acceptance.

## Residuals

| Residual | Status | Owner |
| --- | --- | --- |
| Table/cell yield remains unproven on accepted real artifacts | carried to re-evidence gate | evidence worker |
| Field correctness remains unproven | deferred | comparative correctness gate |
| Source truth remains unproven | deferred | baseline disposition gate |
| S1 full JSON envelope mismatch | deferred / separate export disposition | controller |
| Runtime/cache/cost baseline suitability | deferred | performance/cache/cost gate |

## Next Gate Recommendation

Proceed to:

```text
Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Gate
```

After accepted implementation, run:

```text
Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Gate
```

## Final Verdict

```text
VERDICT: ACCEPT_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY
```
