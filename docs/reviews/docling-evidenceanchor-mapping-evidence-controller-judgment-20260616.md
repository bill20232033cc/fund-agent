# Docling EvidenceAnchor Mapping Evidence Controller Judgment - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Evidence Gate`
Role: AgentController
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the no-live evidence gate for applying accepted candidate-only Docling EvidenceAnchor mapping to accepted local candidate representation artifacts.

This judgment does not change code, tests, runtime behavior, production `EvidenceAnchor` schema, `FundDocumentRepository`, parser/source policy, Service, Host, UI, renderer, quality gate, provider/LLM route, readiness, release, PR, push or merge state.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-controller-judgment-20260616.md` | Accepted implementation checkpoint |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` | Evidence artifact |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-review-ds-20260616.md` | AgentDS evidence review |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-review-mimo-20260616.md` | AgentMiMo evidence review |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-fix-evidence-20260616.md` | Evidence fix |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-re-review-ds-20260616.md` | AgentDS re-review |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-re-review-mimo-20260616.md` | AgentMiMo re-review |

## 3. Accepted Evidence Facts

| Fact | Controller Judgment |
| --- | --- |
| S1 current envelope and S4/S5/S6 accepted envelopes can be loaded by candidate projection and mapping helpers. | ACCEPT |
| S1 full JSON is not a current candidate envelope schema and is blocked by `unsupported candidate representation schema_version`. | ACCEPT |
| Mapping emits candidate-only heading anchors where section context is explicit enough. | ACCEPT |
| Current real artifacts produce no table/cell candidate anchors under accepted fail-closed rules. | ACCEPT |
| Dominant blocker is missing section context: `23363 / 23373 = 99.96%` of blocked candidate blocks. | ACCEPT |
| Overall mapped yield is `102 / 23475 = 0.43%`. | ACCEPT |
| Evidence remains candidate-only and not source truth, not full field correctness, not baseline promotion, not readiness. | ACCEPT |

## 4. Finding Disposition

| Finding | Source | Disposition | Result |
| --- | --- | --- | --- |
| DS-F1: aggregate blocked count wrong (`23473` vs `23373`). | AgentDS | ACCEPTED_AND_FIXED | Corrected; DS/MiMo re-review PASS. |
| MiMo-F4: zero-yield severity not explicit enough. | AgentMiMo | ACCEPTED_AND_FIXED | Added yield ratio `102 / 23475 = 0.43%`; MiMo re-review PASS. |
| MiMo-F6: missing vs unstable context ratio not consolidated. | AgentMiMo | ACCEPTED_AND_FIXED | Added distribution `missing_section_context=23363`, `unstable_section_context=10`; DS/MiMo re-review PASS. |

No unresolved blocker remains for this evidence gate.

## 5. Residuals

| Residual | Owner | Next handling |
| --- | --- | --- |
| Table/cell mapping yield is zero on accepted real artifacts. | Fund documents candidate owner | `Docling EvidenceAnchor Mapping Section-context Enrichment Planning Gate` |
| S1 full JSON is not current candidate envelope schema. | Fund documents candidate owner | Same section-context/envelope planning gate should decide regenerate/export vs current-envelope-only route. |
| Candidate anchors remain non-production and non-proof. | Future design/evidence owner | Carry to baseline disposition; no production admission. |
| Docling baseline promotion remains undecided. | Controller / product owner | Deferred until section-context, comparative correctness and performance/cache/cost evidence are dispositioned. |

## 6. Next Gate

Recommended next mainline entry:

```text
Docling EvidenceAnchor Mapping Section-context Enrichment Planning Gate
```

Purpose:

- decide whether to enrich candidate representation with deterministic annual-report section context before retrying table/cell mapping evidence;
- define a section normalization rule for headings such as `2.1 基金基本情况` without weakening fail-closed semantics;
- decide S1 full JSON envelope regeneration/export handling;
- keep mapping outputs candidate-only and preserve `NOT_READY`.

Deferred entries:

- Docling field correctness comparative evidence;
- Docling performance/cache/cost evidence;
- Docling baseline disposition controller judgment;
- production parser/repository integration;
- release/readiness, PR, push or merge gates.

## 7. Final Verdict

```text
VERDICT: ACCEPT_PARTIAL_HEADING_ONLY_MAPPING_EVIDENCE_NOT_READY
```
