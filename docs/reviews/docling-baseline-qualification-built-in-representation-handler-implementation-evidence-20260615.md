# Docling Baseline Qualification Built-in Representation Handler Implementation Evidence - 2026-06-15

Gate: `Built-in Candidate Representation Route Handler No-live Implementation Gate`
Role: implementation worker
Release/readiness: `NOT_READY`

## 1. Scope

Implemented the accepted built-in candidate representation route handler plan.

This gate does not run real annual-report Docling conversion, real pdfplumber export, live/network/EID/FDR/provider/LLM/analyze/readiness/release/PR commands, and does not change production repository/source/parser behavior.

## 2. Source Of Truth

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-controller-judgment-20260615.md`

## 3. Files Changed

Implementation:

- `fund_agent/fund/documents/candidates/representation_handlers.py`
- `fund_agent/fund/documents/candidates/representation_export.py`

Tests:

- `tests/fund/documents/test_candidate_representation_handlers.py`
- `tests/fund/documents/test_candidate_representation_export.py`

Documentation:

- `fund_agent/fund/README.md`

## 4. Implemented Behavior

### Candidate route handlers

- Added `CandidateHandlerConfig`.
- Added `built_in_route_handlers(config)`.
- Added `build_pdfplumber_candidate_representation(...)`.
- Added `build_docling_candidate_representation(...)`.
- Added `build_eid_html_candidate_representation(...)`.

### Docling candidate route

- Docling import remains lazy inside the default converter factory.
- Handler supports injected fake converter for no-live tests.
- Handler requires local `cache/docling-artifacts` by default.
- Handler sets offline environment during conversion.
- Handler blocks socket access by default and maps socket errors to `docling_network_attempt_blocked`.
- Default Docling converter binds `PdfPipelineOptions.artifacts_path` to the configured local artifact path.
- Default Docling converter binds `do_ocr` and `do_table_structure` from `CandidateHandlerConfig`.
- Missing local artifacts map to `docling_local_artifacts_missing`.
- Local conversion/model availability failures map to `docling_model_artifact_unavailable`.
- Output remains candidate envelope only and preserves non-proof blocked claims.

### pdfplumber candidate route

- Handler stays inside `fund_agent/fund/documents/candidates`.
- Handler may call existing `fund_agent.fund.pdf.parser` helpers only as candidate-internal default dependencies.
- Tests inject fake text/table/section functions and do not read real annual-report PDF bodies.
- Output includes sections, headings, paragraphs, tables, text blocks and route-comparison summary metrics.

### EID HTML render candidate route

- Handler returns blocked JSON only.
- Failure code: `eid_html_render_url_not_accepted_for_sample`.
- It does not discover URLs, fetch HTML, claim raw XML/XBRL, claim source truth, or claim field correctness.

### Harness / CLI

- Added explicit `--run-built-in-handlers`.
- Added `--docling-artifacts-path`.
- Added `--docling-no-socket-block`; default remains socket-blocked.
- Added `--allow-overwrite`.
- `--write-blocked` and `--run-built-in-handlers` are mutually exclusive.
- Default command remains validation-only.
- `reference_existing_json` remains read-only and is never rewritten.
- Default write-producing entries are no-clobber.
- Mixed manifests fail before partial writes if any write-producing output already exists.
- Mixed manifests fail before partial writes if any handled route lacks a route handler for the current execution mode.

## 5. Boundary Checks

- No `FundDocumentRepository` behavior change.
- No source policy change.
- No Eastmoney, fund-company website, CNINFO or non-EID fallback.
- No write to `cache/pdf`.
- No public `fund_agent.fund.documents` export of candidate internals.
- No Service/UI/Host/renderer/quality-gate integration.
- No extractor / EvidenceAnchor / CHAPTER_CONTRACT consumer integration.
- No field correctness validation.
- No source truth, raw XML, taxonomy compatibility, parser replacement or readiness claim.

## 6. Validation

Commands run:

```text
uv run pytest tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
25 passed in 3.15s
```

Command run:

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_handlers.py fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py
```

Result:

```text
All checks passed!
```

Command run:

```text
git diff --check
```

Result: passed.

## 7. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Full S4/S5/S6 Docling/pdfplumber JSON export not run. | Deferred | Full representation export evidence gate after implementation review acceptance. |
| Docling quality for full annual reports not proven by this gate. | Deferred | Evidence gate must run bounded full export and compare output quality. |
| S4/S5/S6 EID HTML render artifacts not accepted. | Deferred | Keep blocked JSON unless separate discovery/evidence gate accepts HTML render artifacts. |
| S2/S3 provenance/hash issues remain unresolved. | Deferred | Separate provenance/disposition gate only. |
| Release/readiness remains `NOT_READY`. | Accepted residual | Do not claim readiness/release/PR. |

## 8. Review-driven Fixes

| Review finding | Disposition | Fix |
|---|---|---|
| `DS-IMPL-F1`: default Docling converter checked artifact path existence but did not bind the converter to that path. | ACCEPT_WITH_FIX | `_default_docling_converter()` now constructs `PdfPipelineOptions(artifacts_path=workspace_root / docling_artifacts_path, do_ocr=..., do_table_structure=...)` and passes it through `PdfFormatOption` for `InputFormat.PDF`. A no-live test asserts the configured artifact path and options are present on the converter without running conversion. |
| `MiMo`: mixed manifest could write blocked entry before failing on later handled entry with missing route handler. | ACCEPT_WITH_FIX | `export_manifest()` now preflights all write-producing handled entries against the available route handlers before any write. A regression test asserts blocked+handled with no handler fails before writing either output. |

## 9. Final Verdict

`VERDICT: IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY`
