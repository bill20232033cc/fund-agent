# Docling Baseline Qualification Built-in Representation Handler Implementation Review - MiMo - 2026-06-15

Verdict: `BLOCKED`

## Review Scope

Gate: `Built-in Candidate Representation Route Handler No-live Implementation Gate`

Review inputs:

- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-evidence-20260615.md`

Reviewed implementation files only:

- `fund_agent/fund/documents/candidates/representation_handlers.py`
- `fund_agent/fund/documents/candidates/representation_export.py`
- `tests/fund/documents/test_candidate_representation_handlers.py`
- `tests/fund/documents/test_candidate_representation_export.py`
- `fund_agent/fund/README.md`

This review did not run live/network/PDF/parser/Docling/provider/LLM/analyze/readiness/release commands and did not edit code.

## Findings

| severity | path / line | reason | fix |
|---|---|---|---|
| High | `fund_agent/fund/documents/candidates/representation_export.py:347-360`, `fund_agent/fund/documents/candidates/representation_export.py:506-516`; missing test in `tests/fund/documents/test_candidate_representation_export.py` | `export_manifest()` preflights manifest validity and existing output paths, but it does not preflight whether the current execution mode can produce every write-producing entry before the write loop starts. With no `route_handlers` (the `--write-blocked` path), a mixed manifest whose first entry is `blocked` and later entry is `handled` will write the first blocked JSON, then fail on the later handled entry with `missing route handler`. That violates the accepted no-clobber / mixed-manifest no-partial-write requirement and leaves partial evidence artifacts under `reports/representation-json`. Current tests cover existing-output partial-write prevention, but not mixed mode with missing handler. | Add a preflight before any writes that rejects unsupported write-producing entries for the selected execution mode. For `--write-blocked` / no handlers, require every write-producing entry to be `blocked`; for handler execution, require handlers for every `handled` route that will be written. Add a regression test where a manifest contains `(blocked, handled)` with no handlers and assert `export_manifest()` raises before writing the blocked output. |

## Accepted Facts

- Candidate-only boundary is otherwise preserved: implementation stays under `fund_agent/fund/documents/candidates/`, does not modify `FundDocumentRepository`, production source/cache/parser behavior, Service/UI/Host/renderer/quality gate, extractor consumers, `EvidenceAnchor`, or public `fund_agent.fund.documents.__all__`.
- EID source policy remains EID single-source/no fallback. No Eastmoney, CNINFO, fund-company or non-EID fallback route is introduced.
- EID HTML handler remains blocked and does not claim raw XML/XBRL, source truth, field correctness, taxonomy compatibility or readiness.
- Docling import is lazy in `_default_docling_converter()`, tests use fake converter paths, missing local artifacts map to `docling_local_artifacts_missing`, socket errors map to `docling_network_attempt_blocked`, and evidence records targeted no-live pytest/ruff/git diff checks as passed.
- pdfplumber handler is candidate-internal; tests use injected fake text/table/section functions and do not read real annual-report PDF bodies.
- `reference_existing_json` is read-only, requires existing valid JSON, enforces input/output path equality, and is skipped during export writes.

## Residual Risks

- After fixing the mixed-manifest preflight, re-run the targeted no-live validation from the implementation evidence.
- Later evidence must still prove no Docling model download, no network, no `cache/pdf` mutation, no non-EID fallback, and no source-truth/field-correctness/readiness claims.
- Full S4/S5/S6 representation export, Docling quality, S4/S5/S6 EID HTML render discovery and S2/S3 provenance/hash issues remain separate gates.

## Gate Recommendation

Do not accept this implementation gate yet.

Re-review only the no-partial-write / mixed-manifest closure after the preflight fix and regression test are added.
