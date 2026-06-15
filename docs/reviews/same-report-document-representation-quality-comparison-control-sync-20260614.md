# Same-report Document Representation Quality Comparison Control Sync

Date: 2026-06-14

Scope: scoped control sync before entering `Same-report Document Representation Quality Comparison Planning Gate`.

## Decision

User steering requires Docling data-quality comparison before candidate source implementation planning. The current mainline is therefore adjusted from:

```text
FundDisclosureDocument Candidate Source No-live Implementation Planning Gate
```

to:

```text
Same-report Document Representation Quality Comparison Planning Gate
```

## Files Updated

| Path | Change |
|---|---|
| `docs/current-startup-packet.md` | Current active gate, next entry point, residual row and resume checklist now point to same-report comparison planning. |
| `docs/implementation-control.md` | Current status, Active gate, next entry point, long-run queue and resume checklist now point to same-report comparison planning. |

## Basis

- `AGENTS.md`: parser and document-intermediate outputs must remain inside Fund documents / `FundDocumentRepository` boundaries; document intermediates are not source truth.
- `docs/design.md`: EID XBRL HTML render is a candidate/research input; Docling is a future benchmark candidate, not a production parser.
- `docs/implementation-control.md`: HTML render evidence, candidate source design and schema plan are accepted only as `NOT_READY` planning inputs.
- `docs/reviews/workspace-artifact-disposition-before-same-report-comparison-20260614.md`: recommends inserting same-report comparison before candidate source implementation planning.

## Guardrails

- release/readiness remains `NOT_READY`.
- No implementation is accepted.
- No parser execution is accepted.
- No Docling dependency or adapter is accepted.
- No production parser replacement is accepted.
- No `FundDocumentRepository` behavior change is accepted.
- No Service/UI/Host/renderer/quality-gate direct parser, XBRL endpoint or HTML render access is accepted.
- No raw XML download proof, field correctness proof, taxonomy compatibility proof, source truth proof or readiness proof is accepted.
- EID remains single-source; no Eastmoney, fund-company, CNINFO or fallback expansion is accepted.

## Next Entry

```text
Same-report Document Representation Quality Comparison Planning Gate
```

The planning artifact should define identity-matched samples and a quality matrix comparing:

1. `eid_xbrl_html_render_candidate`
2. current pdfplumber parser output
3. Docling candidate output

The next gate must remain planning-only.

VERDICT: CONTROL_SYNC_ACCEPTED_NOT_READY
