# Docling EvidenceAnchor Mapping No-live Implementation Plan - Controller Judgment

Date: 2026-06-16
Role: AgentController
Gate: `Docling EvidenceAnchor Mapping No-live Implementation Plan Review Gate`
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes review of `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-20260616.md`.

This judgment does not implement code, change source/tests/runtime behavior, update `EvidenceAnchor` schema, change `FundDocumentRepository`, parser behavior, source policy, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate behavior, and does not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/design.md` | Design truth for EvidenceAnchor / FundDisclosureDocument / Docling candidate boundaries |
| `docs/implementation-control.md` | Current control truth |
| `docs/current-startup-packet.md` | Current startup packet |
| `docs/reviews/docling-evidenceanchor-mapping-plan-controller-judgment-20260616.md` | Accepted prior mapping plan and binding constraints |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-20260616.md` | No-live implementation plan under review |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-review-ds-20260616.md` | AgentDS review |
| `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-review-mimo-20260616.md` | AgentMiMo review |

## 3. Plan Decision

| Decision Point | Controller Judgment |
| --- | --- |
| Candidate/production isolation is programmatic, not note-only | ACCEPT |
| Implementation ownership is constrained to Fund documents candidate internals | ACCEPT |
| S1 and S4/S5/S6 parent-table resolution strategies are deterministic and fail-closed | ACCEPT_WITH_LOW_FINDINGS |
| Section stability and row locator rules are mechanically testable | ACCEPT_WITH_LOW_FINDINGS |
| No-live test matrix is sufficient for implementation with additions below | ACCEPT_WITH_LOW_FINDINGS |
| Plan is ready for no-live implementation gate | ACCEPT |
| Plan authorizes production parser replacement, source truth or readiness | REJECT |

## 4. Review Finding Disposition

| Finding | Reviewer | Severity | Disposition | Binding Controller Action |
| --- | --- | --- | --- | --- |
| DS2-F1: S1 multi-page table bbox containment not addressed. | AgentDS | Low | ACCEPT_AS_IMPLEMENTATION_CHECK | Implementation must inspect S1 table representation first; if tables span pages, bbox containment must work on any page where the table appears, or fail closed. |
| DS2-F2: S4/S5/S6 `table_id` availability unvalidated. | AgentDS | Low | ACCEPT_AS_IMPLEMENTATION_CHECK | Implementation must verify table `table_id` availability before expecting S4/S5/S6 cell happy paths; if absent, convert that path to stop-path evidence. |
| DS2-F3: section keyword family list not specified. | AgentDS | Low | ACCEPT_AS_IMPLEMENTATION_CHECK | Implementation must define the section family source, preferably existing section patterns, and record it in module docstring or implementation evidence. |
| DS2-F4: test matrix missing S4/S5/S6 section-hierarchy-absent scenario. | AgentDS | Low | ACCEPT_AS_TEST_REQUIREMENT | Add no-live test coverage for S4/S5/S6 missing section hierarchy with deterministic heading-path mapping and ambiguous heading-path blocking if applicable. |
| MIMO-IMPL-F1: test matrix missing explicit `unstable_section_context` stop-path case. | AgentMiMo | Low | ACCEPT_AS_TEST_REQUIREMENT | Add no-live test coverage that distinguishes `missing_section_context` from `unstable_section_context`. |

No finding requires plan rewrite before implementation.

## 5. Accepted Implementation Constraints

The no-live implementation gate must preserve these constraints:

- allowed write set stays inside `fund_agent/fund/documents/candidates/`, `tests/fund/documents/`, and conditional README updates;
- no Service/Host/UI/renderer/quality-gate direct access to Docling, parser cache, source helpers, PDF files or mapping helpers;
- candidate mapping outputs must not be bare production `EvidenceAnchor` objects;
- no `to_evidence_anchor`, `as_evidence_anchor`, `to_production_anchor` or equivalent production-admission helper;
- candidate metadata must preserve `candidate_source="docling"`, schema family, sample id, `candidate_only=True`, and `field_correctness_status="not_proven"`;
- implementation commands must be no-live only;
- release/readiness remains `NOT_READY`.

## 6. Next Gate

Next mainline entry:

```text
Docling EvidenceAnchor Mapping No-live Implementation Gate
```

Expected implementation outputs:

- candidate-only mapping models / helpers under Fund documents candidate internals;
- no-live tests covering happy paths and stop paths;
- implementation evidence artifact;
- DS/MiMo implementation review;
- controller judgment before any control-doc sync.

Deferred entries:

- Docling EvidenceAnchor mapping evidence gate;
- Docling field correctness comparative evidence;
- Docling performance / cache / cost evidence;
- Docling baseline disposition controller judgment;
- production parser/repository integration;
- release/readiness, PR, push or merge gates.

## 7. Final Verdict

```text
VERDICT: ACCEPT_NO_LIVE_IMPLEMENTATION_PLAN_READY_FOR_IMPLEMENTATION_GATE_NOT_READY
```
