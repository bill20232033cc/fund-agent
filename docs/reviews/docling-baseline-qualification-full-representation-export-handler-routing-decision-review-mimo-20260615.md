# Docling Baseline Qualification Full Representation Export Handler Routing Decision Review - MiMo - 2026-06-15

Verdict: `PASS`

## Review Scope

Reviewed target:

- `docs/reviews/docling-baseline-qualification-full-representation-export-handler-routing-decision-20260615.md`

Context inputs:

- `AGENTS.md`
- `docs/design.md` relevant Docling / `FundDisclosureDocument` / EID HTML / `FundDocumentRepository` / EID single-source sections
- `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-controller-judgment-20260615.md`

This review did not run live/network/PDF/parser/Docling/provider/LLM/analyze/readiness/release commands.

## Findings

| severity | evidence | recommendation | blocking |
|---|---|---|---|
| None | The decision routes to `Built-in Candidate Representation Route Handler Planning Gate` instead of evidence-time ad hoc Python handler injection. It preserves candidate-only status, `NOT_READY`, Fund documents candidate ownership, EID single-source/no fallback, and the blocked claims for field correctness/source truth/taxonomy/readiness. It forbids production repository/source/cache behavior changes and gives the next planning worker concrete decisions to specify: handler API, module layout, lazy imports, Docling containment, pdfplumber candidate PDF handling, blocked EID HTML JSON, manifest entries, overwrite policy, no-live tests and later evidence commands. | No blocking change required. Controller can accept this decision and route to built-in handler planning. | no |

## Review Notes

- Routing to built-in handler planning is the safer next gate versus evidence injection because the accepted implementation judgment explicitly leaves built-in Docling/pdfplumber handlers as an open residual. A reviewed handler surface is more reproducible than one-off evidence scripts and better aligned with the accepted command/module entrypoint constraint.
- The decision keeps handler work under `fund_agent/fund/documents/candidates/` and does not authorize `FundDocumentRepository`, sources, cache, Service, UI, Host, renderer, quality gate or extractor behavior changes.
- The decision correctly treats explicit staged PDF paths as candidate-evidence inputs only, not production document access or cache promotion.
- The decision preserves EID single-source/no fallback and does not reopen Eastmoney, fund-company website, CNINFO or other fallback routes.
- The decision avoids raw XML, field correctness, source truth, taxonomy compatibility, baseline qualification and readiness claims.
- S4/S5/S6 EID HTML render availability remains deferred; blocked JSON is acceptable until a separate bounded discovery gate accepts render URLs.

## Residuals

- The next planning worker must still define the exact handler contract, no-network/no-model-download guard strategy, parser dependency handling, output overwrite policy and evidence command matrix.
- Full representation export evidence remains blocked until handler planning and implementation are accepted.
- S2/S3 provenance/hash residuals and S4/S5/S6 EID HTML discovery remain separate gates.

## Final Recommendation

`PASS`: proceed to `Built-in Candidate Representation Route Handler Planning Gate`. Do not proceed directly to full export evidence, production integration, field correctness validation, readiness or release.
