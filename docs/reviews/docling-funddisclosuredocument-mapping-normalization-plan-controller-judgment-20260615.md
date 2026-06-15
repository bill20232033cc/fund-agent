# Docling FundDisclosureDocument Mapping And Normalization Plan Controller Judgment

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization Planning Gate`

Controller role: controller judgment only

Readiness state: `NOT_READY`

Verdict: `ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_GATE_NOT_READY`

## 1. Scope

This judgment closes the planning gate for mapping the accepted Route A Docling output to a candidate `FundDisclosureDocument` / `EvidenceAnchor` representation and normalization plan.

This judgment does not authorize:

- code implementation;
- production parser replacement;
- `FundDocumentRepository` behavior change;
- `EvidenceAnchor` schema change;
- extractor, renderer, audit, source-label, Service, Host, UI or quality-gate consumer integration;
- direct Service/UI/Host/renderer/quality-gate access to Docling, PDF files, parser cache or parser helpers;
- EID source policy change;
- Eastmoney, CNINFO, fund-company website or any other fallback route;
- PDF/Docling conversion, live source, provider/LLM, analyze/checklist/golden/readiness/release/PR execution;
- raw XML/XBRL claim, field correctness claim, taxonomy compatibility claim, source truth claim or readiness/release claim.

Release/readiness remains `NOT_READY`.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`
- `reports/docling-route-a/004393_2025_docling_quality_summary.json`
- `reports/docling-route-a/artifact-manifest.json`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-ds-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-mimo-20260615.md`

## 3. Accepted Plan Facts

| Plan fact | Controller judgment |
|---|---|
| `docling_pdf_candidate` is a candidate-only Fund documents-layer representation derived from PDF through Docling. | `ACCEPT` |
| `docling_pdf_candidate` is not a current production `EvidenceAnchor.source_kind`, not source truth and not current production source policy. | `ACCEPT` |
| Current production annual-report source policy remains EID single-source with no fallback. | `ACCEPT` |
| Candidate acquisition, parsing, normalization, cache metadata and failure classification must remain inside Fund documents ownership and behind `FundDocumentRepository` boundaries if later implemented. | `ACCEPT` |
| Service/UI/Host/renderer/quality gate must not directly call Docling, PDF files, parser cache, parser helpers or candidate artifacts. | `ACCEPT` |
| Docling JSON `tables[].data.table_cells`, not Markdown tables, is the primary structured input for later candidate mapping. | `ACCEPT` |
| Candidate `FundDisclosureDocument` mapping must preserve artifact identity, section hierarchy, page spans, paragraph blocks, table blocks, table cell locators, raw/normalized text and failure classes. | `ACCEPT` |
| Candidate `EvidenceAnchor` projection must not change the current schema in this gate; bbox, column header path, cell text/hash, locator hash and normalization notes remain candidate metadata in `note` for later fixtures. | `ACCEPT` |
| Normalization must be deterministic, fixture-backed and preserve raw values. | `ACCEPT` |
| Later validation must be no-live fixture/excerpt based and must not run PDF/Docling conversion, EID/FDR/network, provider/LLM, analyze/checklist/golden/readiness/release/PR. | `ACCEPT` |
| Route A Docling output is not field correctness proof, raw XML/XBRL proof, taxonomy compatibility proof, source truth, parser replacement or readiness proof. | `ACCEPT` |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentDS | `PASS` | `ACCEPT` |
| AgentMiMo | `PASS_WITH_NONBLOCKING_FINDINGS` | `ACCEPT_WITH_BINDING_AMENDMENT` |

Findings:

| ID | Source | Severity | Finding | Controller disposition | Required handling |
|---|---|---:|---|---|---|
| DS-F1 | AgentDS | low | Document-level normalization and extractor-level normalization boundaries can be clearer. | `ACCEPT_NONBLOCKING` | Next implementation planning must explicitly split document normalization from extractor/value parsing. |
| DS-F2 | AgentDS | low | Normalization rule name vocabulary is not closed. | `ACCEPT_NONBLOCKING` | Next implementation planning must define a controlled rule-name vocabulary for normalization notes. |
| DS-F3 | AgentDS | low | Same-report comparison sequencing is present as residual but not cross-referenced in every projection fixture section. | `ACCEPT_NONBLOCKING` | Next implementation planning must explicitly reference the prior same-report comparison residual before any consumer integration or production projection. |
| MIMO-001 | AgentMiMo | low | Numeric token repair does not specify whitespace-only grouped numbers such as `100 000` or `1 234 567`. | `ACCEPT_NONBLOCKING_BINDING` | Next implementation planning must define either deterministic repair or explicit block semantics for whitespace-only numeric grouping, with fixture cases. |

Rejected findings: none.

Unresolved blockers: none.

## 5. Binding Amendments For Next Gate

The next gate must treat these amendments as binding:

1. Keep `docling_pdf_candidate` candidate-only unless a later controller explicitly accepts a source-kind/schema change.
2. Define a closed normalization-rule vocabulary before implementation.
3. Split document-level normalization from extractor/value parsing. Document normalization may repair text for locator stability; field-value parsing and correctness remain later extractor/projection scope.
4. Define whitespace-only numeric grouping semantics. Ambiguous cases must fail closed and must not project field facts.
5. Keep candidate projection fixture-only until same-report comparison and consumer-integration gates are explicitly accepted.
6. Preserve `FundDocumentRepository` boundary and no-consumption guards for Service/UI/Host/renderer/quality gate.
7. Preserve EID single-source/no-fallback policy and `NOT_READY`.

## 6. Residual Risks

| Residual | Owner | Current blocker? | Tracking |
|---|---|---|---|
| Route A covers only `004393 / 2025`. | Fund documents / parser owner | No for planning acceptance | Future multi-sample Docling benchmark or document-representation evidence gate |
| Local HuggingFace cache provenance is not production model provenance acceptance. | Controller / model artifact owner | No for planning acceptance | Future model artifact provenance acceptance gate before production use |
| Same-report comparison across EID HTML render, current pdfplumber and Docling remains deferred. | Controller / documents evidence owner | No for candidate-only planning | Required before consumer integration or route-strength claims |
| Field correctness and source truth remain unproven. | Fund extractor/projection owner | No for planning acceptance | Future field validation / source-truth evidence gates |
| Current `EvidenceAnchor` schema remains unchanged. | Fund extractor/model owner | No for planning acceptance | Future schema gate only if candidate projection requires public source-kind change |

## 7. Next Gate Recommendation

Recommended next gate:

```text
Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Planning Gate
```

Allowed scope:

- planning only;
- candidate model/module location under Fund documents ownership;
- excerpt fixture shape derived from Route A JSON snippets;
- normalization-rule vocabulary;
- document-normalization versus extractor-parsing boundary;
- table cell locator and EvidenceAnchor projection fixture plan;
- canonical failure mapping tests;
- repository non-behavior-change tests;
- no-consumption guards for Service/UI/Host/renderer/quality gate;
- explicit stop conditions for source truth, field correctness, parser replacement and readiness overclaims.

Forbidden scope:

- implementation;
- PDF/Docling conversion;
- live EID/FDR/network/provider/LLM commands;
- production `FundDocumentRepository` behavior change;
- source policy or fallback change;
- extractor/renderer/audit/source-label/CHAPTER_CONTRACT consumer integration;
- readiness/release/PR/push/merge.

Deferred entries:

- Docling model artifact provenance acceptance gate;
- same-report EID HTML render versus pdfplumber versus Docling comparison evidence gate;
- candidate source-kind / `EvidenceAnchor` schema decision gate;
- field correctness validation gate;
- production parser integration gate;
- readiness/release/PR gates.

## 8. Final Verdict

`VERDICT: ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_NO_LIVE_IMPLEMENTATION_PLANNING_GATE_NOT_READY`

Stop here for this gate. Do not enter implementation in this judgment.
