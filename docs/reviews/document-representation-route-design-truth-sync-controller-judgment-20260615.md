# Document Representation Route Design-truth Sync Controller Judgment

Date: 2026-06-15

Gate: `Document Representation Route Design-truth Sync Gate`

Role: controller

Readiness state: `NOT_READY`

Verdict: `ACCEPT_DESIGN_SYNC_FOR_CANDIDATE_DOCUMENT_REPRESENTATION_ROUTE_NOT_READY`

## 1. Scope

This judgment accepts the current `docs/design.md` diff that aligns design truth with the accepted XBRL HTML render and Docling candidate document representation route.

This judgment does not authorize implementation, production parser replacement, raw XML/XBRL direct-download claims, field correctness claims, taxonomy compatibility claims, source-truth claims, readiness/release/PR state, fallback/source expansion, Service/UI/Host/renderer/quality-gate direct parser access, or `FundDocumentRepository` behavior changes.

## 2. Evidence Reviewed

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-controller-judgment-20260614.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md`
- `docs/reviews/scoped-accepted-checkpoint-plan-20260615.md`

## 3. Accepted Design Facts

| Design fact | Disposition |
|---|---|
| `fund-analysis analyze-annual-period` is deterministic and is not Route C LLM body-chapter writing. | ACCEPT |
| The current Chapter 1-6 repair budget is one regenerate attempt per chapter and is not a calibrated product default. | ACCEPT |
| Route C post-live narrow fixes are deferred stabilization, not the current product mainline. | ACCEPT |
| Current production parser remains `pdfplumber + locate_sections + self-owned extractor`; Docling is candidate/future benchmark input only. | ACCEPT |
| The current design gap is annual-report document representation rather than another single-field extractor rule. | ACCEPT |
| `FundDisclosureDocument` remains a candidate/future internal document representation concept under Fund documents. | ACCEPT |
| Docling output, raw text, Markdown, OCR text, HTML and JSON are not source truth and must pass through extractor/projection/EvidenceAnchor/fail-closed classification before report consumption. | ACCEPT |
| EID XBRL HTML render remains `eid_xbrl_html_render_candidate`, not raw XML/XBRL instance truth. | ACCEPT |
| Raw XML direct download, field correctness and taxonomy compatibility remain unproven. | ACCEPT |
| Future implementation must remain inside `fund_agent/fund/documents` / `FundDocumentRepository`; Service/UI/Host/renderer/quality gate must not call parser/XBRL/HTML endpoints directly. | ACCEPT |

## 4. Blocked Claims

The following remain blocked:

- Docling is production baseline;
- Docling is source truth;
- EID HTML render is raw XML/XBRL instance truth;
- raw XML direct download is proven;
- field correctness is proven;
- taxonomy cross-year compatibility is proven;
- production parser replacement is authorized;
- `FundDocumentRepository` behavior may change;
- Service/UI/Host/renderer/quality gate may directly consume Docling/PDF/parser/XBRL/HTML artifacts;
- release/readiness or PR readiness.

## 5. Validation

Planned validation for this sync:

```text
git diff --check
rg -n "当前 PDF parser 边界与 Docling 候选|CSRC EID XBRL HTML render artifact|候选/研究输入|NOT_READY|FundDocumentRepository" docs/design.md
```

## 6. Next Gate

Return to the current mainline after scoped checkpoint closeout:

```text
Docling Baseline Qualification Acquisition Status Planning Gate
```

## 7. Final Verdict

`VERDICT: ACCEPT_DESIGN_SYNC_FOR_CANDIDATE_DOCUMENT_REPRESENTATION_ROUTE_NOT_READY`
