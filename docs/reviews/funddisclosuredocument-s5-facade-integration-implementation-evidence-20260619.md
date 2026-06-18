# FundDisclosureDocument S5 Facade Integration Implementation Evidence

Verdict: `S5_FACADE_INTEGRATION_IMPLEMENTED_NOT_READY`

Date: 2026-06-19

Gate: `FundDisclosureDocument S5 Facade Integration Implementation Gate`

Role: implementation worker only

Release/readiness remains `NOT_READY`.

## Changed Files

- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md`
- `docs/reviews/funddisclosuredocument-s5-facade-integration-implementation-evidence-20260619.md`

## Implementation Summary

- Added explicit keyword-only `FundDataExtractor.extract(..., disclosure_intermediate: FundDisclosureDocumentIntermediate | None = None)`.
- Preserved default `disclosure_intermediate=None` route: loaded `ParsedAnnualReport` through `FundDocumentRepository`, validated report identity, loaded NAV, classified from parsed report, routed exact active fund through `parsed_annual_report.v1`, and preserved non-active direct legacy residual path.
- Added explicit `fund_disclosure_document.v1` facade route only when `disclosure_intermediate` is supplied.
- Added pre-NAV disclosure identity validation for `fund_code`, `report_year`, `document_kind="annual_report"` and `intermediate_kind="fund_disclosure_document.v1"`.
- Kept fund type classification sourced from loaded `ParsedAnnualReport`, not candidate content.
- Fail-closed non-active explicit disclosure route without direct legacy fallback.
- Resolved `FundProcessorRegistry` with `active_fund + annual_report + fund_disclosure_document.v1`.
- Passed only Protocol-visible `intermediate`, `candidate_boundary` and `source_provenance` through `FundProcessorInput`.
- Raised on `blocked` / `unsupported` processor statuses and processor result identity mismatches.
- Projected `missing` / `partial` / `satisfied` statuses through existing bundle projection, with drawdown and bond-risk evidence still computed from loaded `ParsedAnnualReport`.
- Added S5 tests for default path preservation, no default FDD resolution, explicit FDD route, identity failures before NAV, source/provenance/candidate failure classes, non-active no legacy fallback, default non-active preservation, registry failure, result mismatch, missing success path, residual-field semantics and AST import guard.
- Updated Fund package README to describe the current S5 explicit opt-in facade boundary and preserve candidate-only / `NOT_READY`.

## Validation Commands and Results

```bash
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_dispatch.py -q
```

Result: passed, `75 passed in 0.80s`.

```bash
uv run pytest tests/fund/documents/test_fund_disclosure_document.py tests/fund/documents/test_fund_disclosure_failure_mapping.py -q
```

Result: passed, `57 passed in 0.67s`.

```bash
uv run pytest tests/fund/processors/ -q
```

Result: passed, `57 passed in 0.54s`.

```bash
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
```

Result: passed, `All checks passed!`.

```bash
uv run ruff format --check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
```

Result: passed, `2 files already formatted`.

```bash
git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md docs/reviews/funddisclosuredocument-s5-facade-integration-implementation-evidence-20260619.md
```

Result: passed, empty output.

## Forbidden-Diff Checks

All required forbidden-diff commands returned empty output:

```bash
git diff --name-only -- fund_agent/fund/documents/repository.py
git diff --name-only -- fund_agent/fund/documents/sources.py
git diff --name-only -- fund_agent/fund/documents/models.py
git diff --name-only -- fund_agent/fund/extractors/models.py
git diff --name-only -- fund_agent/fund/processors/contracts.py
git diff --name-only -- fund_agent/fund/processors/fund_disclosure_processor.py
git diff --name-only -- fund_agent/fund/processors/fund_disclosure_dispatch.py
git diff --name-only -- fund_agent/services fund_agent/ui fund_agent/host fund_agent/agent
```

## Boundary Checks

- `data_extractor.py` imports `FundDisclosureDocumentIntermediate` only from `fund_agent.fund.processors.contracts`.
- `data_extractor.py` imports no `fund_agent.fund.documents.candidates.*` module and no `docling`.
- No repository/source/cache/parser/fallback files were edited.
- No processor contracts, registry, `fund_disclosure_processor.py`, `fund_disclosure_dispatch.py`, candidate modules, EvidenceAnchor/EvidenceSourceKind/source failure taxonomy files were edited.
- No Service/UI/Host/Agent/renderer/quality-gate/provider/LLM files were edited.
- No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM command was run.
- No S6+ actual field-family extraction was implemented.
- Explicit disclosure failure does not fallback to parsed annual production route.
- Non-active explicit disclosure route does not fallback to direct legacy path.
- Candidate-only, `not_proven`, no source-truth, no parser-replacement and `NOT_READY` boundaries remain preserved.

## Residual Risks

| Residual | Owner | Destination |
|---|---|---|
| S6+ actual field-family extraction from `FundDisclosureDocument` absent | Fund extractor owner + controller | Future S6+ field-family extraction planning gate |
| EvidenceAnchor projection strategy for candidate section/table/cell locators absent | Fund documents / extractor owner | Future EvidenceAnchor projection design/evidence gate |
| Source truth, full field correctness, raw XML/taxonomy proof, unit/date semantics and cross-year correctness unproven | Fund documents evidence owner | Separate evidence gates |
| Concrete candidate path remains blocked by candidate-only boundary | Fund extractor owner | Intentional S5 residual until source truth / field correctness gates |
| Non-active fund processors not implemented | Fund processor owner | Separate fund-type processor gates |
| Default production parser remains `parsed_annual_report.v1` path | Controller | Intentional boundary, not a defect |
| Release/readiness remains `NOT_READY` | Release owner / controller | Separate release/readiness gates |
| PR state remains unchanged | Maintainer / controller | Separate PR disposition gate |
