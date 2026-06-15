# Candidate Representation Schema No-live Implementation Plan Review - MiMo - 2026-06-15

Verdict: `PASS`

## Findings

| Severity | Evidence | Recommendation | Blocking |
|---|---|---|---|
| None | Plan defines a narrow write set: `representation_models.py`, `representation_projection.py`, two focused test files, existing no-consumption guard test, and `fund_agent/fund/README.md`; it explicitly forbids public `documents.__init__`, `EvidenceAnchor`, `FundDocumentRepository`, source/cache/adapter, Service/UI/Host and quality-gate changes. | Accept as code-generation-ready for a no-live implementation worker. | No |
| Info | Model direction is concrete enough when combined with the accepted design input: closed three-route enum, frozen/slotted dataclasses, non-proof status fields, route-neutral document/section/text/table/cell/note concepts, and projection requirements for schema version, closed source kind, non-proof guards, failure taxonomy and route-specific locators. | Implementation review should verify field optionality follows the accepted design shapes and does not collapse locators into an opaque dict-only model. | No |
| Info | Plan preserves candidate-only and `NOT_READY`: no source truth, no field correctness, no parser replacement, no public `EvidenceSourceKind` expansion, no public `EvidenceAnchor` field change, no production integration. | Keep all generated types under `fund_agent/fund/documents/candidates` and out of public exports. | No |
| Info | Plan handles all three routes without over-promoting EID HTML: Docling PDF, pdfplumber PDF, and EID HTML render are accepted as candidate source kinds; EID HTML blocked payload must project only as document-level failure. | Do not treat blocked EID HTML as available source truth or comparable full-output evidence. | No |
| Info | Validation and tests are no-live: synthetic/tiny payloads only, no committed full JSON read by default, no Docling/pdfplumber conversion, no live/network/EID/FDR/provider/LLM/analyze/readiness/release/PR commands. | Future implementation gate may run the listed targeted pytest/ruff/diff checks only. | No |

## Residual Risks

- The plan relies on the accepted design artifact for detailed section/table/cell field lists. That is acceptable for implementation planning, but implementation review should reject ad hoc field omissions that lose route-specific locator information.
- Existing `fund_agent/fund/documents/candidates/models.py` remains Docling-first; the planned new route-neutral models must not silently replace or publicize those internals outside this candidate package.
- Locator stability, heading filtering, field-family correctness, production `FundDisclosureDocument` integration and public `EvidenceAnchor` mapping remain deferred.

## Final Recommendation

PASS. The plan is sufficient to enter `Candidate Representation Schema No-live Implementation Gate`; do not route to production parser replacement, production integration, field correctness promotion, readiness, release or PR.
