# Candidate Representation Schema / Design Plan Review - MiMo - 2026-06-15

Verdict: `PASS`

## Findings

| Severity | Evidence | Recommendation | Blocking |
|---|---|---|---|
| None | Plan keeps Release/readiness as `NOT_READY`, declares no field correctness/source truth/taxonomy/raw XML/parser replacement/baseline qualification/readiness claim, and defines guard statuses as `not_proven` / `not_authorized`. | Accept plan for controller disposition. | No |
| Info | Plan covers all three candidate route kinds: `docling_pdf_candidate`, `pdfplumber_pdf_candidate`, `eid_xbrl_html_render_candidate`; it explicitly keeps them candidate-internal and out of public `EvidenceSourceKind`. | Future implementation planning should preserve this as an internal closed enum and avoid public `EvidenceAnchor` schema changes. | No |
| Info | Plan preserves route-specific locator differences: Docling bbox/row-column offsets/spans, pdfplumber row-column indexes with optional/null bbox, and EID HTML render URL/DOM/table ordinal/row/column paths with `page_number=null`. | Implementation planning can use these fields as the minimum non-lossy normalization target. | No |
| Info | Plan keeps candidate representation inside Fund documents internals and forbids `FundDocumentRepository`, production parser, source policy, Service/UI/Host/renderer/quality-gate behavior changes. | No production integration should be authorized before a separate accepted gate. | No |
| Info | Next gate sequencing is correct: plan review -> `Candidate Representation Schema No-live Implementation Planning Gate`; production integration, public `EvidenceAnchor` mapping, field-family correctness, readiness/release/PR remain deferred. | Controller should not route directly to production implementation. | No |

## Residual Risks

- The proposed schema is sufficient for no-live implementation planning, but implementation planning still needs exact dataclass/TypedDict names, field optionality, projection function signatures and fixture strategy before code generation.
- Docling heading abundance and TOC/furniture filtering remain unresolved by design, correctly deferred to locator stability evidence.
- EID HTML render remains blocked for S4/S5/S6 and should not be treated as a comparable full-output route until a separate bounded evidence gate accepts render artifacts.

## Final Recommendation

PASS. The plan is acceptable for controller closeout and should advance only to `Candidate Representation Schema No-live Implementation Planning Gate`, not production implementation, parser replacement, field correctness promotion, readiness or release.
