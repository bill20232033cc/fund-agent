# Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Plan Controller Judgment

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Planning Gate`

Controller role: controller judgment only

Readiness state: `NOT_READY`

Verdict: `ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`

## 1. Scope

This judgment closes the no-live implementation planning gate for candidate Docling-derived `FundDisclosureDocument` mapping and normalization internals.

This judgment authorizes only the next no-live implementation gate within the accepted candidate-only write set. It does not authorize:

- production parser replacement;
- `FundDocumentRepository.load_annual_report()` behavior change;
- current `EvidenceAnchor` schema or `EvidenceSourceKind` expansion;
- extractor, renderer, audit, source-label, Service, Host, UI or quality-gate consumer integration;
- direct Service/UI/Host/renderer/quality-gate access to Docling, PDF files, parser cache, parser helpers or candidate artifacts;
- PDF/Docling conversion, PDF parser execution, EID/FDR/network, provider/LLM, analyze/checklist, golden, readiness/release/PR commands;
- source truth, field correctness, raw XML/XBRL, taxonomy compatibility, parser replacement or readiness claims;
- EID source policy change or Eastmoney/CNINFO/fund-company website fallback.

Release/readiness remains `NOT_READY`.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-review-ds-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-review-mimo-20260615.md`
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`

## 3. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentDS | `PASS_WITH_NONBLOCKING_FINDINGS` | `ACCEPT_WITH_BINDING_AMENDMENTS` |
| AgentMiMo | `PASS_WITH_NONBLOCKING_FINDINGS_NOT_READY` | `ACCEPT_WITH_BINDING_AMENDMENTS` |

Findings:

| ID | Source | Severity | Finding | Controller disposition | Required handling |
|---|---|---:|---|---|---|
| DS-IMPL-F1 | AgentDS | low | `NormalizedText` value object is referenced but not formally declared in the plan's dataclass section. | `ACCEPT_NONBLOCKING_BINDING` | Implementation must define `NormalizedText` explicitly before using it in normalization APIs. |
| DS-IMPL-F2 | AgentDS | low | Text-level and table-level normalization rule return signatures are not fully separated. | `ACCEPT_NONBLOCKING_BINDING` | Implementation must split text normalization API contracts from table/locator helper API contracts. |
| DS-IMPL-F3 | AgentDS | low | Stitched table group container shape is not explicitly declared. | `ACCEPT_NONBLOCKING_BINDING` | Implementation must define either `CandidateTableGroup` or an explicit stitched `CandidateTableBlock` return contract before cross-page stitching helper code. |
| DS-IMPL-F4 | AgentDS | low | `fund_agent/fund/extractors` is not listed in no-consumption import guard scope. | `ACCEPT_NONBLOCKING_BINDING` | No-consumption guard must include `fund_agent/fund/extractors`. |
| DS-IMPL-F5 | AgentDS | info | Fixture `prov` retention count is not specified. | `ACCEPT_INFO_BINDING` | Fixture builder must retain all provenance entries present in each excerpted object unless explicitly trimmed with reason. |
| DS-IMPL-F6 | AgentDS | info | Test file names bind to Docling implementation details. | `ACCEPT_INFO_DEFER` | Keep current Docling-specific names for this gate; revisit generic candidate naming only if a second candidate source is introduced. |
| MIMO-NLIP-001 | AgentMiMo | medium | `NormalizationRuleName` closed vocabulary is listed but not declared as a Python type alias. | `ACCEPT_NONBLOCKING_BINDING` | Implementation must define `NormalizationRuleName = Literal[...]` matching the closed vocabulary exactly. |
| MIMO-NLIP-002 | AgentMiMo | medium | `table_cells: []` in the fixture shape example could be misread as expected empty fixture content. | `ACCEPT_NONBLOCKING_BINDING` | Actual checked-in fixture must contain non-empty representative `table_cells` for table cases; tests must fail if required table cells are empty. |
| MIMO-NLIP-003 | AgentMiMo | low | Slice 3/4/5 commit separation default is unspecified. | `ACCEPT_NONBLOCKING_BINDING` | In this no-live implementation gate, implement Slice 3/4/5 as one cohesive locator implementation pass unless the controller later splits commits. |
| MIMO-NLIP-004 | AgentMiMo | low | No test asserts implemented normalization rule names match the closed vocabulary exactly. | `ACCEPT_NONBLOCKING_BINDING` | Add a test that implemented normalization rule names equal the closed vocabulary set exactly. |
| MIMO-NLIP-005 | AgentMiMo | low | `CandidateEvidenceAnchorNote` module location is implicit. | `ACCEPT_NONBLOCKING_BINDING` | Put `CandidateEvidenceAnchorNote` under candidate internals, preferably `fund_agent/fund/documents/candidates/models.py`; locator helper may construct it. |

Rejected findings: none.

Unresolved blockers: none.

## 4. Accepted Plan Facts

| Plan fact | Controller judgment |
|---|---|
| The next implementation may add candidate internals under `fund_agent/fund/documents/candidates/`. | `ACCEPT` |
| The next implementation may add minimal no-live excerpt fixtures under `tests/fixtures/fund/docling_route_a/004393_2025/`. | `ACCEPT` |
| The next implementation may add no-live tests under `tests/fund/documents/` and narrow repository non-behavior assertions. | `ACCEPT` |
| The next implementation may conditionally update `fund_agent/fund/README.md` or `tests/README.md` only to document candidate-only status and no-live fixture/test boundaries. | `ACCEPT` |
| The next implementation must not export candidate internals from the production `fund_agent/fund/documents/__init__.py` public surface. | `ACCEPT` |
| Current `EvidenceAnchor` schema and `EvidenceSourceKind` must remain unchanged. | `ACCEPT` |
| Current `FundDocumentRepository.load_annual_report()` production behavior must remain unchanged. | `ACCEPT` |
| Validation remains targeted no-live pytest and ruff only. | `ACCEPT` |

## 5. Accepted Write Set

Allowed for the next implementation gate:

- `fund_agent/fund/documents/candidates/__init__.py`
- `fund_agent/fund/documents/candidates/models.py`
- `fund_agent/fund/documents/candidates/normalization.py`
- `fund_agent/fund/documents/candidates/locators.py`
- `fund_agent/fund/documents/candidates/failures.py`
- `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json`
- `tests/fund/documents/test_docling_candidate_models.py`
- `tests/fund/documents/test_docling_normalization.py`
- `tests/fund/documents/test_docling_locators.py`
- `tests/fund/documents/test_docling_failure_mapping.py`
- `tests/fund/documents/test_docling_no_consumption_guards.py`
- narrow additions to `tests/fund/documents/test_repository.py`
- optional `fund_agent/fund/README.md` or `tests/README.md` only if needed for candidate-only/no-live test documentation.

Forbidden in the next implementation gate:

- source policy or fallback code;
- production repository behavior changes;
- public `EvidenceAnchor` / `EvidenceSourceKind` changes;
- Service/UI/Host/renderer/quality-gate consumer integration;
- full Route A JSON/Markdown/PDF/cache/model artifacts;
- live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- source truth, field correctness, raw XML/taxonomy or readiness claims.

## 6. Next Gate

Authorized next gate:

```text
Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Gate
```

Implementation worker must report:

- files changed;
- implemented slices;
- validation commands and results;
- forbidden commands not run;
- boundary verdict for `EvidenceAnchor`, repository behavior, no-consumption guards, EID single-source/no-fallback and `NOT_READY`;
- residuals;
- final verdict.

## 7. Final Verdict

`VERDICT: ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`
