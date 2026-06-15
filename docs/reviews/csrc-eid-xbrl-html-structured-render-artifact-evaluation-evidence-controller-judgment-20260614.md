# CSRC EID XBRL HTML Structured Render Artifact Evaluation Evidence Controller Judgment

Date: 2026-06-14

Gate: `CSRC EID XBRL HTML Structured Render Artifact Evaluation Evidence Gate`

Controller role: controller judgment only

Readiness state: `NOT_READY`

Verdict: `ACCEPT_EVIDENCE_HTML_RENDER_AVAILABLE_PARTLY_STABLE_NOT_READY`

## 1. Scope

This judgment closes the evidence gate for evaluating whether CSRC EID XBRL HTML render artifacts can remain a candidate structured disclosure input for fund-agent.

This judgment does not authorize:

- raw XBRL route;
- raw XML direct download claim;
- field correctness claim;
- taxonomy compatibility claim;
- production parser replacement;
- `FundDocumentRepository` behavior change;
- `EvidenceAnchor` schema change;
- CHAPTER_CONTRACT change;
- Service / Host / UI / renderer / quality gate direct access to EID endpoints;
- LLM route change;
- release/readiness/PR claim.

## 2. Evidence Reviewed

Accepted inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md`

The evidence artifact was initially blocked by an execution-environment DNS result. Controller then performed the same bounded official EID HTTP access authorized for this gate and corrected the single evidence artifact with current official HTTP results. No production repository/source/parser/PDF/provider/LLM/readiness/release command was run.

## 3. Accepted Evidence Summary

Accepted current facts:

| Evidence item | Controller disposition |
|---|---|
| Official `indexXbrlData.json` returned `200 OK`, `application/json`, length `12721` | `ACCEPT` |
| Current JSON exposes `fAXBRLReportList`, `halfyearXBRLReportList`, `noticeXBRLReportList`, `seasonXBRLReportList` | `ACCEPT` |
| 12 sampled rows, three per required list, were executed | `ACCEPT` |
| Each sampled `instance_html_view.do?instanceid=<idStr>` redirected to official `/xbrl/REPORT/HTML/...html` | `ACCEPT` |
| Each final HTML render returned `200`, `text/html; charset=utf-8`, byte size and content hash | `ACCEPT` |
| Each final HTML contains `<title>XBRL</title>` and `instance_navigation` | `ACCEPT` |
| Navigation labels, headings, table cells and paragraph-like notes are locally extractable | `ACCEPT` |
| Candidate row/column locators can be formed for representative table samples | `ACCEPT_WITH_RESIDUAL` |
| Candidate source classification remains `eid_xbrl_html_render_candidate` | `ACCEPT` |

## 4. Rejected Or Blocked Claims

| Claim | Disposition | Reason |
|---|---|---|
| HTML render is raw XBRL / raw XML truth | `REJECT` | Evidence only proves official rendered HTML availability. |
| Raw XML direct download is proven | `REJECT` | No concrete raw XML endpoint was fetched or proven. |
| Rendered cell values are field-correct | `REJECT` | Values were not validated against authoritative field definitions or independent sources. |
| Taxonomy `schemaRef` / `contextRef` / `unitRef` compatibility is proven | `REJECT` | Raw instance taxonomy references were not available in this gate. |
| HTML render can replace PDF parser | `REJECT` | Narrative/page-number/full coverage was not proven. |
| `FundDocumentRepository` behavior may change now | `REJECT` | Evidence-only gate; no implementation authorization. |
| Service/UI/Host/renderer/quality gate may directly fetch EID XBRL HTML | `REJECT` | Violates AGENTS.md document repository and layer boundaries. |
| Release/readiness improves beyond `NOT_READY` | `REJECT` | This is candidate-route evidence only. |

## 5. Residual Risks

| Residual | Status | Owner / next handling |
|---|---|---|
| Ordinary non-REIT annual/interim HTML render coverage | `OPEN` | Current `halfyearXBRLReportList` sample window exposed REIT annual reports only; future discovery may widen sample selection. |
| Locator normalization for repeated headings, nested tables, hidden title tables and merged cells | `OPEN` | Candidate source design gate must define schema and failure classification before implementation. |
| Field correctness and unit/date semantics | `OPEN` | Requires later validation gate; not accepted here. |
| Raw XML and taxonomy proof | `OPEN_BLOCKED` | Remains separate from HTML render route. |
| Full CHAPTER_CONTRACT narrative coverage | `OPEN` | PDF/Docling/document representation route remains needed until proven otherwise. |
| Endpoint volatility and cache behavior | `OPEN` | Future implementation design must include content hash, fetch metadata and fail-closed source identity. |

## 6. Controller Decision

The evidence is sufficient to continue to a design/planning gate for a documents-layer candidate source schema.

The evidence is not sufficient to enter implementation, production parser replacement, readiness, release or PR gates.

## 7. Next Recommended Gate

Recommended next gate:

```text
FundDisclosureDocument Candidate Source Design Gate
```

Required boundaries for that gate:

- source kind remains `eid_xbrl_html_render_candidate`;
- design must keep endpoint access inside `fund_agent/fund/documents` / `FundDocumentRepository` ownership;
- define candidate document identity, content hash, navigation/section/table locator model, failure classes and EvidenceAnchor projection;
- preserve `NOT_READY`;
- do not implement parser behavior unless a later implementation gate is explicitly accepted.

Deferred entries:

- ordinary non-REIT annual/interim sample expansion;
- narrow table-family pilot if design discovers locator ambiguity;
- raw XML endpoint research;
- field correctness validation;
- Docling/PDF document representation route;
- production implementation;
- release/readiness/PR gates.

## 8. Final Verdict

`VERDICT: ACCEPT_EVIDENCE_HTML_RENDER_AVAILABLE_PARTLY_STABLE_NOT_READY`

Stop here. Do not automatically enter design or implementation.
