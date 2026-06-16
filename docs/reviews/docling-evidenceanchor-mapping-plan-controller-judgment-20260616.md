# Docling EvidenceAnchor Mapping Plan - Controller Judgment

Date: 2026-06-16
Role: AgentController
Gate: `Docling EvidenceAnchor Mapping Plan Review Gate`
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes review of `docs/reviews/docling-evidenceanchor-mapping-plan-20260616.md`.

This judgment does not implement code, change source/tests/runtime behavior, update `EvidenceAnchor` schema, change `FundDocumentRepository`, parser behavior, source policy, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate behavior, and does not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source and boundary guardrails |
| `docs/design.md` | Design truth for EvidenceAnchor / FundDisclosureDocument / Docling candidate boundaries |
| `docs/implementation-control.md` | Current control truth |
| `docs/current-startup-packet.md` | Current startup packet |
| `docs/reviews/docling-full-document-coverage-evidence-controller-judgment-20260616.md` | Accepted prior coverage judgment |
| `docs/reviews/docling-evidenceanchor-mapping-plan-20260616.md` | Plan under review |
| `docs/reviews/docling-evidenceanchor-mapping-plan-review-ds-20260616.md` | AgentDS review |
| `docs/reviews/docling-evidenceanchor-mapping-plan-review-mimo-20260616.md` | AgentMiMo review |

## 3. Plan Decision

| Decision Point | Controller Judgment |
| --- | --- |
| Plan preserves current `EvidenceAnchor` field set | ACCEPT |
| Plan forbids silent production `source_kind` expansion | ACCEPT_WITH_BINDING_CONSTRAINTS |
| Plan requires parent-table context for table-cell anchors | ACCEPT_WITH_BINDING_CONSTRAINTS |
| Plan preserves candidate-only / not-source-truth / not-full-field-correctness / not-baseline-promotion / `NOT_READY` boundaries | ACCEPT |
| Plan is sufficient for next implementation planning gate | ACCEPT |
| Plan is sufficient for immediate code implementation | REJECT |

The plan is accepted for the next planning gate only. It is not accepted as direct implementation authorization.

## 4. Review Finding Disposition

| Finding | Reviewer | Disposition | Binding Controller Action |
| --- | --- | --- | --- |
| DS-F1: candidate `source_kind="annual_report"` could be indistinguishable from production if candidate status is only in `note`. | AgentDS | ACCEPT_AS_BINDING_CONSTRAINT | Next implementation planning gate must define a programmatic candidate/production boundary; candidate anchors must not flow into production evidence store as bare production anchors. |
| DS-F2: mapping code module boundary is undeclared. | AgentDS | ACCEPT_AS_BINDING_CONSTRAINT | Next gate must bind implementation location to Fund documents candidate internals, preferably under `fund_agent/fund/documents/candidates/`, and prevent Service/Host/UI/renderer/quality-gate direct access. |
| DS-F3: S1 cell-to-parent-table resolution algorithm is unspecified. | AgentDS | ACCEPT_AS_BINDING_CONSTRAINT | Next gate must specify the deterministic parent-table resolution strategy or stop rule before implementation. |
| DS-F4: S4/S5/S6 lightweight section hierarchy availability is unvalidated. | AgentDS | ACCEPT_AS_BINDING_CONSTRAINT | Next gate must first verify section hierarchy availability or define deterministic heading-path fallback / low-yield stop behavior. |
| MIMO-F1: implementation location not explicitly constrained to `fund_agent/fund/documents/`. | AgentMiMo | ACCEPT_AS_BINDING_CONSTRAINT | Same disposition as DS-F2. |
| MIMO-F2: parent-table resolution mechanism is underspecified. | AgentMiMo | ACCEPT_AS_BINDING_CONSTRAINT | Same disposition as DS-F3. |
| MIMO-F3: section stability criteria are undefined. | AgentMiMo | ACCEPT_AS_BINDING_CONSTRAINT | Next gate must define stable vs unstable section context criteria before mapping. |
| MIMO-F4: table-level `row_locator` ordinal semantics are ambiguous. | AgentMiMo | DEFER_WITH_DEFAULT | Next gate should default table-level `row_locator=null` unless it explicitly defines ordinal basis. |
| MIMO-F5: implementation test strategy is not specified. | AgentMiMo | ACCEPT_AS_BINDING_CONSTRAINT | Next gate must include no-live tests for happy paths and stop paths, including parent-table, missing-section, missing-page, source-kind boundary and note metadata checks. |
| MIMO-F6: paragraph `row_locator` wording leaves a future exception. | AgentMiMo | DEFER_WITH_DEFAULT | Next gate should default paragraph `row_locator=null`; future paragraph-specific semantics require a separate schema/design gate. |

## 5. Accepted Residuals

| Residual | Owner | Next Handling |
| --- | --- | --- |
| Candidate/production boundary for mapped anchors | documents/schema owner | Binding requirement for no-live implementation planning |
| Module ownership for mapping helpers | Fund documents owner | Binding requirement for no-live implementation planning |
| S1 parent-table resolution | implementation planning owner | Binding requirement for no-live implementation planning |
| S4/S5/S6 section context availability | implementation planning owner | Binding requirement for no-live implementation planning |
| Field correctness beyond selected facts | baseline qualification owner | Comparative correctness evidence gate |
| Production baseline disposition | baseline qualification owner | Baseline disposition controller judgment after mapping/correctness/performance evidence |
| Release/readiness | release owner | Future readiness gate only; current state remains `NOT_READY` |

## 6. Next Gate

Next mainline entry:

```text
Docling EvidenceAnchor Mapping No-live Implementation Planning Gate
```

Required planning constraints for the next gate:

- planning only, not implementation;
- define exact allowed write set for any later implementation;
- keep mapping helpers inside Fund documents candidate internals;
- define candidate/production isolation mechanism before any code is written;
- specify parent-table resolution per schema family;
- specify section stability rules;
- specify no-live tests and validation matrix;
- preserve candidate-only / `NOT_READY` status.

Deferred entries:

- Docling EvidenceAnchor mapping implementation;
- Docling field correctness comparative evidence;
- Docling performance / cache / cost evidence;
- Docling baseline disposition controller judgment;
- FundDisclosureDocument candidate source production integration;
- release/readiness, PR, push or merge gates.

## 7. Final Verdict

```text
VERDICT: ACCEPT_PLAN_WITH_BINDING_CONSTRAINTS_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_NOT_READY
```
