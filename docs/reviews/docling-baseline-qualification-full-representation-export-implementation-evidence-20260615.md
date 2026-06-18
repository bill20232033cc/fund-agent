# Docling Baseline Qualification Full Representation Export Harness Implementation Evidence - 2026-06-15

Gate: `Candidate Representation Export Harness No-live Implementation Gate`
Role: implementation worker
Release/readiness: `NOT_READY`

## 1. Scope

Implemented the candidate-only full representation export harness accepted by:

- `docs/reviews/docling-baseline-qualification-full-representation-export-plan-controller-judgment-20260615.md`

This gate does not run Docling conversion, pdfplumber full export, EID HTML discovery, live/network/PDF acquisition, `FundDocumentRepository`, provider/LLM, analyzer/checklist, golden, readiness, release, PR, push or merge commands.

## 2. Files Changed

| Path | Change |
|---|---|
| `fund_agent/fund/documents/candidates/representation_export.py` | Added candidate-only manifest, route/mode enums, path/hash validation, output envelope builder, blocked-result builder, injectable route-handler export entrypoint and CLI validation/write-blocked entrypoint. |
| `tests/fund/documents/test_candidate_representation_export.py` | Added no-live tests for manifest parsing, hash validation, production `cache/pdf` rejection, blocked JSON output, truth-claim rejection and public export guard. |
| `fund_agent/fund/README.md` | Documented candidate-only representation export harness boundary and non-proof status. |

## 3. Accepted Implementation Decisions

| Decision | Implementation |
|---|---|
| Candidate-only source kinds | Closed enum: `docling_pdf_candidate`, `pdfplumber_pdf_candidate`, `eid_xbrl_html_render_candidate`. |
| Reproducible input contract | `candidate_representation_export_manifest.v1` manifest with sample id, fund code, year, route, mode, input artifact path, accepted input hash, provenance judgment path and output path. |
| Non-proof output contract | `candidate_annual_report_representation.v1` envelope always carries `not_proven` source truth / field correctness / taxonomy status and `not_authorized` parser replacement status. |
| Production cache guard | Inputs and outputs under `cache/pdf` are rejected. Outputs must stay under `reports/representation-json`. |
| Staged path boundary | Explicit staged paths can be validated as candidate inputs, but the harness does not make them production document access. |
| EID HTML unavailable handling | Blocked JSON can be generated without raw XML, field correctness, taxonomy, source truth or readiness claims. |
| No public export | Candidate internals remain outside `fund_agent.fund.documents.__all__`. |
| No conversion in tests | Tests use fake handler output and blocked mode only. |

## 4. Command / Entrypoint Contract

Accepted local module entrypoint:

```text
uv run python -m fund_agent.fund.documents.candidates.representation_export --manifest <manifest.json>
```

Validation-only behavior:

- reads manifest;
- validates schema, paths and accepted input hash;
- writes nothing.

Blocked-output behavior:

```text
uv run python -m fund_agent.fund.documents.candidates.representation_export --manifest <manifest.json> --write-blocked
```

Allowed only for manifest entries whose mode is `blocked`, unless a future evidence gate injects reviewed route handlers through Python API. This implementation does not provide built-in Docling or pdfplumber conversion handlers.

## 5. Boundary Guards

The implementation explicitly preserves:

- `not_raw_xml_download_proof`
- `not_field_correctness_proof`
- `not_taxonomy_compatibility_proof`
- `not_source_truth`
- `not_readiness_proof`
- `no_repository_behavior_change`
- `no_parser_replacement`

The implementation rejects:

- production-shaped `cache/pdf` input/output paths;
- absolute candidate artifact/output paths;
- non-annual report entries;
- invalid fund code shape;
- unsupported route kinds such as Eastmoney/fund-company/CNINFO;
- output payloads that set source truth, field correctness, taxonomy compatibility or parser replacement beyond candidate-only status.

## 6. Validation

```text
uv run pytest tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
16 passed in 0.48s
```

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_export.py
```

Result:

```text
All checks passed!
```

## 7. Blocked Claims

This implementation does not prove:

- Docling can process S4/S5/S6;
- pdfplumber full representation can process S4/S5/S6;
- EID HTML render exists for S4/S5/S6;
- Docling is a baseline;
- any route is source truth;
- any field value is correct;
- raw XML / raw XBRL direct download;
- taxonomy compatibility;
- production parser replacement;
- release/readiness.

## 8. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Built-in Docling/pdfplumber conversion handlers are not implemented. | open | Full export evidence needs either a reviewed handler implementation gate or a controller-approved Python API injection path. |
| S4/S5/S6 EID HTML render URLs remain unaccepted. | open | Use blocked JSON by default or open bounded EID HTML discovery gate. |
| S2/S3 provenance/hash residuals remain. | open | Separate provenance resolution gate. |
| Control docs lag latest accepted gate chain. | open | Scoped control sync gate. |

## 8.1 Review Fix Amendment

MiMo review identified a blocking path-boundary defect: parent traversal such as `reports/representation-json/../../cache/pdf/out.json` could satisfy a lexical prefix check while escaping the allowed output directory.

Fix applied:

- candidate paths now reject absolute paths and any `..` parent traversal before route/cache checks;
- output path traversal and input path traversal tests were added;
- targeted tests increased from 14 to 16 passing tests.

## 9. Final Classification

`IMPLEMENTED_CANDIDATE_EXPORT_HARNESS_NO_LIVE_NOT_READY`
