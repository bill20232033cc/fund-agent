# Docling Full-document Coverage Evidence - Controller Judgment

Date: 2026-06-16
Role: AgentController
Gate: `Docling Full-document Coverage Evidence Gate`
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the full-document coverage evidence gate for candidate Docling outputs across S1/S4/S5/S6.

This judgment does not implement code, update source/tests/runtime behavior, rerun Docling conversion, run live/network/EID/FDR/PDF/source acquisition, run provider/LLM/analyze/checklist/golden/readiness/release/PR commands, or change `FundDocumentRepository`, parser behavior, source policy, `EvidenceAnchor`, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate behavior.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/design.md` | Design truth source and non-goal guardrails |
| `docs/current-startup-packet.md` | Current control packet |
| `docs/implementation-control.md` | Current control truth |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-controller-judgment-20260616.md` | Prior accepted runtime-containment evidence |
| `docs/reviews/docling-full-document-coverage-evidence-20260616.md` | Evidence under judgment |
| `reports/docling-full-document-coverage/20260616/coverage-summary.json` | Machine-readable coverage summary |
| `docs/reviews/docling-full-document-coverage-evidence-review-ds-20260616.md` | AgentDS scoped review |
| `docs/reviews/docling-full-document-coverage-evidence-review-mimo-20260616.md` | AgentMiMo scoped review |

## 3. Accepted Candidate Facts

| Fact | Status |
| --- | --- |
| S1 `004393 / 2025`, S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024` were covered by the evidence matrix. | ACCEPT |
| Each declared page in the four candidate Docling JSONs has at least one extracted candidate block. | ACCEPT |
| Heading locator, paragraph locator, table shape, and table-cell locator coverage are 100% in the coverage summary for the measured candidate representation fields. | ACCEPT |
| Each sample contains the 12 common annual-report section keyword families used by this evidence gate. | ACCEPT_AS_COVERAGE_SIGNAL_ONLY |
| The evidence is sufficient to enter EvidenceAnchor mapping planning. | ACCEPT |

## 4. Rejected Claims

| Claim | Disposition | Reason |
| --- | --- | --- |
| Full field correctness is proven. | REJECT | The evidence measures representation coverage only; it does not verify values against source truth. |
| Docling candidate output is source truth. | REJECT | Candidate JSON is a representation artifact, not an authoritative disclosure source. |
| Docling is promoted to production baseline. | REJECT | Baseline disposition and production integration remain future gates. |
| Release/readiness is proven. | REJECT | Release/readiness remains `NOT_READY`. |
| Parser replacement or repository behavior change is authorized. | REJECT | This gate is evidence-only and does not authorize implementation. |

## 5. Review Finding Disposition

| Finding | Reviewer | Disposition | Controller Judgment |
| --- | --- | --- | --- |
| DS-F1: cell locator wording is functionally correct but should be treated as a composite table-plus-cell path because `table_id` and `page_number` live on the parent table. | AgentDS | ACCEPT_AS_NEXT_GATE_CONSTRAINT | Evidence need not be amended; EvidenceAnchor mapping planning must model table context explicitly. |
| DS-F2: computation script was not preserved. | AgentDS | ACCEPT_AS_RESIDUAL | Not blocking because `coverage-summary.json` is the machine-readable evidence output; future expansion gates should preserve reproducibility logic where useful. |
| DS-F3: 12 section keyword families are not fund-type-calibrated. | AgentDS | ACCEPT_AS_RESIDUAL | Not blocking for coverage signal; cannot be used as correctness proof without later fund-type-aware validation. |
| MIMO-F0: no blocking or non-blocking finding. | AgentMiMo | ACCEPT | No action required. |

## 6. Residuals

| Residual | Owner | Next Handling |
| --- | --- | --- |
| EvidenceAnchor mapping from candidate locators must preserve parent table context for cell anchors. | documents/schema owner | `Docling EvidenceAnchor Mapping Planning Gate` |
| Field-level correctness beyond selected facts remains unproven. | baseline qualification owner | Comparative correctness / fact-family expansion gate |
| Comparative quality against pdfplumber and EID HTML render remains open. | baseline qualification owner | Route disposition gate |
| Production model artifact provenance, dependency policy, cost/performance and cache policy remain open. | production integration / baseline qualification owners | Separate provenance and performance/cache/cost gates |
| Release/readiness remains `NOT_READY`. | release owner | Future readiness gate only after accepted baseline disposition and residual closure |

## 7. Next Gate Recommendation

Next mainline entry:

```text
Docling EvidenceAnchor Mapping Planning Gate
```

The next gate should be planning-only unless the controller explicitly accepts an implementation plan later. It should define how candidate Docling locators map into the project EvidenceAnchor model, including parent table context for cells, document representation identity, page/table/row/column path semantics, and non-goals for source truth, production parser replacement and readiness.

Deferred entries:

- Docling field correctness comparative evidence
- Docling performance / cache / cost evidence
- Docling baseline disposition controller judgment
- FundDisclosureDocument candidate source implementation planning
- Production parser/repository integration
- Release/readiness, PR, push or merge gates

## 8. Final Verdict

```text
VERDICT: ACCEPT_FULL_DOCUMENT_COVERAGE_EVIDENCE_READY_FOR_EVIDENCEANCHOR_MAPPING_PLANNING_NOT_READY
```
