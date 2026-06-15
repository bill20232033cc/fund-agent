# FundDisclosureDocument Candidate Source Design Controller Judgment

Date: 2026-06-14

Gate: `FundDisclosureDocument Candidate Source Design Gate`

Controller role: controller judgment only

Readiness state: `NOT_READY`

Verdict: `ACCEPT_DESIGN_READY_FOR_SCHEMA_PLANNING_GATE_NOT_READY`

## 1. Scope

This judgment closes the design gate for projecting accepted CSRC EID XBRL HTML render evidence into a future documents-layer candidate source design.

This judgment does not authorize:

- implementation;
- production parser replacement;
- `FundDocumentRepository` behavior change;
- `EvidenceAnchor` schema change;
- CHAPTER_CONTRACT change;
- Service / Host / UI / renderer / quality gate direct access to EID XBRL HTML endpoints;
- raw XML/XBRL route;
- raw XML direct download claim;
- field correctness claim;
- taxonomy compatibility claim;
- source truth claim;
- LLM route change;
- readiness/release/PR claim.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-evidence-closeout-control-sync-controller-judgment-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-review-ds-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-review-mimo-20260614.md`

## 3. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| DS | `PASS` | `ACCEPT` |
| MiMo | `PASS` | `ACCEPT` |

Accepted review findings:

| Finding | Disposition |
|---|---|
| Design keeps `eid_xbrl_html_render_candidate` distinct from raw XML/XBRL instance truth. | `ACCEPT` |
| Repository boundary is preserved: endpoint/fetch/parser/cache ownership remains inside Fund documents / future `FundDocumentRepository` internal implementation. | `ACCEPT` |
| Service/UI/Host/renderer/quality gate direct endpoint access is explicitly forbidden. | `ACCEPT` |
| Rendered cells are not promoted to field correctness, source truth or readiness. | `ACCEPT` |
| Existing `EvidenceAnchor` fields can carry a candidate mapping at design level with `page_number=null`, but schema planning must verify concrete model constraints. | `ACCEPT_WITH_BINDING_RESIDUAL` |
| Failure taxonomy is adequate for design, but schema planning must map candidate failures to canonical source outcomes. | `ACCEPT_WITH_BINDING_RESIDUAL` |

No rejected reviewer findings.

No unresolved blocker.

## 4. Accepted Design Facts

Accepted design facts:

| Fact | Controller judgment |
|---|---|
| Candidate source kind remains `eid_xbrl_html_render_candidate`. | `ACCEPT` |
| HTML render artifacts are candidate document-representation inputs, not raw XML, raw XBRL, source truth or readiness proof. | `ACCEPT` |
| Future endpoint access, fetch/cache handling, parsing and failure classification must be encapsulated inside `fund_agent/fund/documents` / `FundDocumentRepository` ownership. | `ACCEPT` |
| Candidate `FundDisclosureDocument` fields should include EID identity, report type, redirect/render URL, content hash, fetch metadata, navigation, sections, blocks and failure class. | `ACCEPT` |
| Candidate locator model should include render URL, section anchor, heading path, table ordinal, row locator, column header path and cell text/hash. | `ACCEPT` |
| Candidate `EvidenceAnchor.page_number` remains `null` for HTML render because no PDF page coordinate is accepted. | `ACCEPT` |
| `EvidenceAnchor.note` should carry `idStr`, render URL, redirect location, content hash, report type, source list and locator stability class. | `ACCEPT` |

## 5. Binding Residuals For Next Gate

| Residual | Required handling |
|---|---|
| Existing code may not currently accept `eid_xbrl_html_render_candidate` as a concrete `EvidenceAnchor.source_kind`. | Schema planning must inspect model constraints and define explicit migration/projection strategy before implementation. |
| Candidate-specific failure classes must not invent source semantics. | Schema planning must map them to canonical `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error` or explicitly justify any extension. |
| Ordinary non-REIT annual/interim HTML render coverage remains open. | Do not generalize current REIT annual/interim sample to all ordinary annual reports; carry sample expansion as separate evidence gate. |
| Field correctness, unit/date semantics, raw XML/taxonomy proof and source truth remain unproven. | Keep as separate evidence gates; do not treat schema planning as validation. |
| Full CHAPTER_CONTRACT narrative coverage is not proven by HTML render. | PDF/pdfplumber and optional Docling document-representation gates remain available if needed. |

## 6. Blocked Claims

| Claim | Disposition |
|---|---|
| `eid_xbrl_html_render_candidate` is raw XML / raw XBRL instance truth | `REJECT` |
| Raw XML direct download is proven | `REJECT` |
| Rendered HTML cells are field-correct facts | `REJECT` |
| Taxonomy cross-year compatibility is proven | `REJECT` |
| HTML render can replace the current production PDF parser | `REJECT` |
| Service/UI/Host/renderer/quality gate may directly access EID XBRL HTML endpoints | `REJECT` |
| `FundDocumentRepository` behavior may change under this gate | `REJECT` |
| Release/readiness improves beyond `NOT_READY` | `REJECT` |

## 7. Next Gate

Recommended next gate:

```text
FundDisclosureDocument Candidate Source Schema Planning Gate
```

Required scope:

- no code changes;
- no runtime behavior changes;
- inspect current model/source/outcome constraints as needed;
- define schema planning handoff for candidate source identity, locator structures, failure classification and projection into current/future `EvidenceAnchor`;
- keep `eid_xbrl_html_render_candidate` as candidate only;
- preserve `NOT_READY`;
- do not run live/provider/PDF/FDR/analyze/checklist/golden/readiness/release/PR commands.

Deferred entries:

- same-report comparison evidence gate: EID HTML render versus current pdfplumber;
- ordinary non-REIT annual/interim EID HTML sample expansion;
- optional Docling benchmark gate;
- raw XML endpoint research;
- field correctness validation;
- implementation gate;
- readiness/release/PR gates.

## 8. Final Verdict

`VERDICT: ACCEPT_DESIGN_READY_FOR_SCHEMA_PLANNING_GATE_NOT_READY`

Stop here for this gate. Do not enter implementation.
