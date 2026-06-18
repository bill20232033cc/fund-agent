# Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Evidence

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Gate`

Role: implementation worker

Readiness state: `NOT_READY`

Final verdict: `IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY`

## 1. Scope

Implemented only the accepted candidate-only no-live write set authorized by:

- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-plan-controller-judgment-20260615.md`

No production parser replacement, production repository behavior change, `EvidenceAnchor` schema change, consumer integration, source policy change, fallback expansion, source truth claim, field correctness claim, raw XML/taxonomy claim, readiness/release/PR state change, or live/provider/LLM execution was performed.

## 2. Changed Files

Candidate internals:

- `fund_agent/fund/documents/candidates/__init__.py`
- `fund_agent/fund/documents/candidates/models.py`
- `fund_agent/fund/documents/candidates/normalization.py`
- `fund_agent/fund/documents/candidates/locators.py`
- `fund_agent/fund/documents/candidates/failures.py`

Fixture:

- `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json`

Tests:

- `tests/fund/documents/test_docling_candidate_models.py`
- `tests/fund/documents/test_docling_normalization.py`
- `tests/fund/documents/test_docling_locators.py`
- `tests/fund/documents/test_docling_failure_mapping.py`
- `tests/fund/documents/test_docling_no_consumption_guards.py`
- `tests/fund/documents/test_repository.py` narrow non-behavior assertion only

Evidence artifact:

- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-evidence-20260615.md`

No README update was needed; tests and module docstrings carry the candidate-only/no-live boundary.

## 3. Implemented Slices

| Slice | Status | Evidence |
|---|---|---|
| Slice 0: fixture contract | Implemented | Minimal `excerpt.json` with accepted Route A hashes, non-proof statuses, non-empty required `table_cells`, and retained table/text provenance entries present in each excerpted object. Full Route A JSON/Markdown/PDF/cache/model artifacts were not committed. |
| Slice 1: candidate models | Implemented | Candidate-only dataclasses/TypedDicts/enums in `models.py`; `NormalizationRuleName = Literal[...]` exactly matches closed vocabulary; `NormalizedText` explicitly defined; `CandidateEvidenceAnchorNote` placed under candidate internals; statuses remain `not_proven` / `not_authorized`. |
| Slice 2: text normalization | Implemented | Text-level API in `normalization.py` only: CJK repair, date repair, numeric punctuation repair, whitespace-only numeric grouping repair/block. No Decimal parsing or field correctness logic. |
| Slice 3/4/5: locator/stitch/projection | Implemented as one cohesive pass | `locators.py` builds table blocks from `table_cells`, reconstructs header/row paths, records merged-cell and path-generation rules, excludes TOC tables, hashes cells/locators, returns `CandidateTableGroup` for stitching, and builds fixture-only candidate anchor notes. |
| Slice 6: failure mapping | Implemented | Every `CandidateFailureCode` maps to current canonical `AnnualReportSourceFailureCategory`; no fallback category or source expansion. |
| Slice 7: repository/no-consumption guards | Implemented | Tests prove `FundDocumentRepository.load_annual_report` has no candidate route and no candidate import appears in Service/UI/Host/template/audit/report quality/extractors guarded scopes. |
| Slice 8: docs | Not needed | No public docs were changed; candidate internals remain non-public. |

## 4. Binding Amendments Closure

| Amendment | Closure |
|---|---|
| Define `NormalizationRuleName = Literal[...]` exactly matching closed vocabulary | Implemented in `models.py`; tested via `get_args(NormalizationRuleName) == NORMALIZATION_RULE_NAMES`. |
| Define `NormalizedText` before normalization APIs | Implemented in `models.py`; `normalization.py` returns it. |
| Split text normalization API from table/locator helper API | `normalization.py` exposes text rules; `locators.py` exposes table/locator/stitch/projection helpers; tested separately. |
| Define stitched return contract | `CandidateTableGroup` implemented in `models.py`; `stitch_candidate_tables()` returns it. |
| Include `fund_agent/fund/extractors` in no-consumption guard | Included in `GUARDED_PATHS`. |
| Fixture non-empty representative table cells | Required table cases assert non-empty `table_cells`; fixture includes non-empty cells for all required cases. |
| Fixture provenance retention | Each excerpted table/text object retains its table/text-level `prov` entries from Route A excerpts. |
| Implement Slice 3/4/5 as cohesive locator pass | Implemented in one `locators.py` pass and one locator test file. |
| Test implemented normalization rule names equal closed vocabulary | Implemented in `test_docling_locators.py` and `test_docling_candidate_models.py`. |
| Put `CandidateEvidenceAnchorNote` under candidate internals | Implemented in `models.py`; constructed by `locators.py`. |

## 5. Validation Commands And Results

Allowed no-live commands run:

```text
uv run pytest tests/fund/documents/test_docling_candidate_models.py -q
Result: 6 passed

uv run pytest tests/fund/documents/test_docling_normalization.py -q
Initial result: 1 failed, 3 passed
Fix: allow decimal whitespace grouping `12 345.67`.
Second result: 1 failed, 3 passed
Fix: inspect adjacent non-space characters for `A 100 000` fail-closed.
Final result: 4 passed

uv run pytest tests/fund/documents/test_docling_locators.py -q
Initial result: 1 failed, 5 passed
Fix: record `merged_cell_expansion` when row path uses a spanned label.
Second result: 1 failed, 5 passed
Fix: propagate row-path text normalization rules to value-cell locator notes.
Final result: 6 passed

uv run pytest tests/fund/documents/test_docling_failure_mapping.py -q
Result: 2 passed

uv run pytest tests/fund/documents/test_docling_no_consumption_guards.py -q
Result: 2 passed

uv run pytest tests/fund/documents/test_repository.py -q
Result: 20 passed

uv run ruff check fund_agent/fund/documents tests/fund/documents
Initial result: 2 ruff issues
Fix: remove unused import; use functional TypedDict for bbox key `l`.
Final result: All checks passed.

uv run pytest tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_normalization.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_failure_mapping.py tests/fund/documents/test_docling_no_consumption_guards.py -q
Final combined result: 20 passed

uv run pytest tests/fund/documents/test_repository.py -q
Final rerun result: 20 passed
```

## 6. Forbidden Commands Not Run

- PDF/Docling conversion: not run.
- PDF parser execution: not run.
- EID/FDR/network: not run.
- Provider/LLM: not run.
- `fund-analysis analyze`: not run.
- `fund-analysis checklist`: not run.
- golden/readiness/release/PR commands: not run.
- stage/commit/push/PR: not run.

## 7. Boundary Verdicts

| Boundary | Verdict | Evidence |
|---|---|---|
| `EvidenceAnchor` schema unchanged | Pass | `fund_agent/fund/extractors/models.py` has no diff; tests assert `EvidenceSourceKind` excludes `docling_pdf_candidate`. |
| Candidate internals not exported from production documents public surface | Pass | `fund_agent/fund/documents/__init__.py` has no diff; tests assert no candidate export. |
| `FundDocumentRepository.load_annual_report()` behavior unchanged | Pass | No production source changes; repository suite `20 passed`; new test asserts no candidate route/source reference. |
| Service/UI/Host/renderer/quality gate no-consumption | Pass | AST guard passes for Service/UI/Host/template/audit/report quality and extractors. |
| EID single-source/no-fallback preserved | Pass | No source policy files changed; failure mapping keeps canonical terminal outcomes and adds no fallback branch. |
| Full Route A artifacts not committed | Pass | Only minimal `excerpt.json` added; no full JSON/Markdown/PDF/cache/model artifact added by this implementation. |
| Source truth / field correctness / raw XML / taxonomy / parser replacement / readiness claims | Pass | Candidate statuses fixed to `not_proven` / `not_authorized`; final state remains `NOT_READY`. |

## 8. Residuals

- Route A remains one local sample only: `004393 / 2025`.
- Candidate locator quality is not field correctness proof.
- Same-report comparison across EID HTML render, current pdfplumber and Docling remains deferred.
- Local model cache provenance remains benchmark-only, not production model provenance acceptance.
- Production parser integration, public source-kind/schema decisions and consumer integration remain separate controller gates.

## 9. Final Verdict

```text
VERDICT: IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY
```

Stop here for implementation evidence. Do not stage, commit, push or open PR.
