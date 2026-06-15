# Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Controller Judgment

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Gate`

Controller role: controller judgment only

Readiness state: `NOT_READY`

Verdict: `ACCEPT_IMPLEMENTATION_WITH_NONBLOCKING_RESIDUALS_NOT_READY`

## 1. Scope

This judgment closes the no-live implementation gate for Docling-derived candidate `FundDisclosureDocument` mapping and normalization internals.

Accepted scope:

- candidate-only internal package under `fund_agent/fund/documents/candidates/`;
- minimal Route A excerpt fixture under `tests/fixtures/fund/docling_route_a/004393_2025/`;
- no-live tests under `tests/fund/documents/`;
- narrow repository non-behavior assertion;
- implementation evidence artifact.

This judgment does not authorize:

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
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-evidence-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-review-ds-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-review-mimo-20260615.md`
- implementation diff in the accepted write set.

## 3. Accepted Implementation Facts

| Fact | Controller judgment |
|---|---|
| Candidate internals were added under `fund_agent/fund/documents/candidates/`. | `ACCEPT` |
| Candidate internals are not exported from `fund_agent/fund/documents/__init__.py`. | `ACCEPT` |
| `EvidenceAnchor` schema and `EvidenceSourceKind` remain unchanged. | `ACCEPT` |
| `FundDocumentRepository.load_annual_report()` production behavior remains unchanged. | `ACCEPT` |
| Candidate source kind `docling_pdf_candidate` remains internal candidate metadata only. | `ACCEPT` |
| `NormalizationRuleName`, `NormalizedText`, `CandidateTableGroup` and `CandidateEvidenceAnchorNote` were implemented under candidate internals. | `ACCEPT` |
| Text normalization remains separate from table/locator helpers. | `ACCEPT` |
| Whitespace-only numeric grouping has deterministic repair and fail-closed tests. | `ACCEPT` |
| Minimal excerpt fixture contains non-empty representative table cells and Route A hash metadata. | `ACCEPT_WITH_RESIDUAL` |
| Failure mapping uses only current canonical source failure categories and introduces no fallback branch. | `ACCEPT` |
| No-consumption guards cover Service/UI/Host/template/audit/report quality/extractors. | `ACCEPT` |
| Targeted no-live tests and ruff passed. | `ACCEPT` |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentDS | `PASS_WITH_NONBLOCKING_FINDINGS` | `ACCEPT_WITH_NONBLOCKING_RESIDUALS` |
| AgentMiMo | `PASS_WITH_NONBLOCKING_FINDINGS` | `ACCEPT_WITH_NONBLOCKING_RESIDUALS` |

Accepted non-blocking findings:

| ID | Source | Severity | Finding | Controller disposition | Tracking |
|---|---|---:|---|---|---|
| DS-REV-F4 | AgentDS | info | `excerpt_hash_sha256` is a descriptive placeholder instead of a computed excerpt hash. | `ACCEPT_RESIDUAL` | Future fixture-integrity hardening gate. Current fixture is candidate-only and non-truth; tests still bind Route A full artifact hashes and non-proof statuses. |
| DS-REV-M3 / MIMO-R-F1 | DS/MiMo | info | `CandidateFailureCode` includes additional `CANDIDATE_NOT_FOUND`, `CANDIDATE_UNAVAILABLE`, `CELL_TEXT_EMPTY` members beyond the plan enum sketch. | `ACCEPT` | Additional members are justified by canonical mapping and locator failure coverage; all are exhaustively mapped and tested. |
| DS-REV-T2 | AgentDS | info | `CandidateSection`, `CandidateParagraphBlock` and closed label sets are declared but not directly exercised by tests. | `ACCEPT_RESIDUAL` | Future section/paragraph mapping evidence or implementation gate. Current implementation focuses locator/table candidate path. |
| DS-REV-T3 | AgentDS | info | Fixture `normalization_cases` are not iterated directly; tests assert equivalent inline cases. | `ACCEPT_RESIDUAL` | Future fixture-driven test hardening; current assertions cover required cases. |
| MIMO-R-F2 | AgentMiMo | info | Test-only import of `documents.__all__` is used for boundary assertion. | `ACCEPT` | Test-only boundary assertion; no production coupling. |

Rejected findings: none.

Unresolved blockers: none.

## 5. Validation Results

Controller reran the no-live validation matrix:

```text
uv run pytest tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_normalization.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_failure_mapping.py tests/fund/documents/test_docling_no_consumption_guards.py -q
Result: 20 passed

uv run pytest tests/fund/documents/test_repository.py -q
Result: 20 passed

uv run ruff check fund_agent/fund/documents tests/fund/documents
Result: All checks passed

git diff --check
Result: passed
```

Forbidden commands not run:

- PDF/Docling conversion;
- PDF parser execution;
- EID/FDR/network;
- provider/LLM;
- `fund-analysis analyze`;
- `fund-analysis checklist`;
- golden/readiness/release/PR;
- stage/commit/push/PR.

## 6. Boundary Verdict

| Boundary | Verdict |
|---|---|
| `EvidenceAnchor` schema unchanged | `PASS` |
| `EvidenceSourceKind` unchanged and excludes `docling_pdf_candidate` | `PASS` |
| `FundDocumentRepository.load_annual_report()` production behavior unchanged | `PASS` |
| Candidate internals not public-exported from production documents package | `PASS` |
| Service/UI/Host/renderer/quality gate no direct candidate/Docling/PDF/parser/cache access | `PASS` |
| EID single-source/no-fallback policy preserved | `PASS` |
| Full Route A JSON/Markdown/PDF/cache/model artifacts not committed | `PASS` |
| Source truth / field correctness / raw XML / taxonomy / parser replacement / readiness claims avoided | `PASS` |
| Release/readiness | `NOT_READY` |

## 7. Residuals

| Residual | Owner | Current blocker? | Next handling |
|---|---|---|---|
| Excerpt hash is descriptive placeholder, not computed file hash. | Fund documents candidate owner | No | Future fixture-integrity hardening gate if candidate fixtures become long-lived regression assets. |
| Route A remains one local sample: `004393 / 2025`. | Fund documents / evidence owner | No | Future multi-sample Docling evidence gate. |
| Same-report EID HTML render versus pdfplumber versus Docling comparison remains deferred. | Controller / documents evidence owner | No | Next recommended evidence gate before consumer integration or route-strength claims. |
| Local model cache provenance remains benchmark-only. | Controller / model artifact owner | No | Future model artifact provenance acceptance gate before production use. |
| Candidate locator quality is not field correctness proof. | Fund extractor/projection owner | No | Future extractor/projection validation gate. |
| Candidate section/paragraph mapping is modeled but not deeply exercised. | Fund documents candidate owner | No | Future section/paragraph mapping evidence or implementation gate. |

## 8. Next Gate Recommendation

Recommended next gate:

```text
Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence Gate
```

Purpose:

- use the newly accepted candidate internals as a no-live basis for comparing document-representation quality;
- compare section hierarchy, table blocks, locator stability, page/bbox provenance and failure classes across accepted EID HTML render evidence, current pdfplumber representation and Docling candidate outputs;
- preserve candidate-only status and `NOT_READY`;
- avoid consumer integration, source truth, field correctness, production parser replacement or readiness claims.

Deferred entries:

- Docling fixture-integrity hardening gate;
- Docling model artifact provenance acceptance gate;
- candidate source-kind / `EvidenceAnchor` schema decision gate;
- extractor projection over candidate document representation gate;
- production parser integration gate;
- readiness/release/PR gates.

## 9. Final Verdict

`VERDICT: ACCEPT_IMPLEMENTATION_WITH_NONBLOCKING_RESIDUALS_NOT_READY`
