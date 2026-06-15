# Docling Controlled Same-source Reference Acquisition Plan Controller Judgment - 2026-06-16

Gate: `Docling Controlled Same-source Reference Acquisition Planning Gate`
Controller: AgentController
Release/readiness: `NOT_READY`
Verdict: `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL_READY_FOR_EVIDENCE_GATE_NOT_READY`

## Scope

This judgment accepts the bounded planning artifact for controlled same-source reference acquisition evidence on S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024`.

This is planning acceptance only. It does not execute live/EID/PDF/source acquisition, does not perform correctness review, and does not change source/tests/runtime behavior, `FundDocumentRepository`, source policy, parser behavior, EvidenceAnchor schema, Service, Host, UI, renderer, quality gate, provider/LLM route, readiness, release, PR or merge state.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-controlled-same-source-reference-acquisition-plan-20260616.md` | Plan under review |
| `docs/reviews/plan-review-20260616-071629.md` | Local planreview fallback |
| `docs/reviews/docling-baseline-qualification-scope-decision-controller-judgment-20260616.md` | Accepted option-2 route decision |
| `docs/reviews/docling-same-source-reference-cache-metadata-evidence-controller-judgment-20260616.md` | Accepted blocked metadata evidence |
| `fund_agent/fund/documents/repository.py` | Repository public method fact |
| `fund_agent/fund/documents/models.py` | Metadata proof model fact |

## Review Disposition

| Finding / risk | Disposition | Controller judgment |
| --- | --- | --- |
| `load_annual_report()` parameter and proof-surface ambiguity | ACCEPT_FIXED | Plan now uses `force_refresh=True` and forbids inspecting returned parsed body; proof must come from post-acquisition `AnnualReportReferenceMetadataResult`. |
| Subagent review unavailable | ACCEPT_RESIDUAL | `multi_agent_v1.spawn_agent` failed with thread limit reached. This is a review-channel residual, not a plan content blocker. |
| Partial acquisition success possible | ACCEPT_RESIDUAL | Plan has explicit `ACCEPT_PARTIAL_REFERENCES_AVAILABLE_NOT_READY` outcome and next-gate routing. |

## Accepted Plan Constraints

The evidence gate may use only the planned repository boundary:

1. pre-check `FundDocumentRepository.get_annual_report_reference_metadata(fund_code, year)`;
2. if needed, bounded `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=True)` for S4/S5/S6 only;
3. post-check `get_annual_report_reference_metadata(fund_code, year)`.

The evidence worker must not inspect or use returned parsed report body, sections, tables, text, anchors or PDF paths. It must accept proof only from metadata facade fields.

## Blocked / Non-claims

- Current unsafe metadata is not proof.
- Acquisition failure must not be stated as EID public unavailability.
- Same-source reference proof is not field correctness proof.
- Same-source reference proof is not source truth or full field correctness.
- Docling remains candidate-only and not production parser replacement.
- Release/readiness remains `NOT_READY`.

## Next Gate

Proceed to:

```text
Docling Controlled Same-source Reference Acquisition Evidence Gate
```

Evidence deliverable:

```text
docs/reviews/docling-controlled-same-source-reference-acquisition-evidence-20260616.md
```

## Final Verdict

```text
VERDICT: ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL_READY_FOR_EVIDENCE_GATE_NOT_READY
```
