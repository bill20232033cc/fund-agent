# Docling Baseline Qualification Full Representation Export Implementation Review - DS - 2026-06-15

Verdict: `FAIL`

Scope reviewed:

- `fund_agent/fund/documents/candidates/representation_export.py`
- `tests/fund/documents/test_candidate_representation_export.py`
- `fund_agent/fund/README.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-evidence-20260615.md`
- Accepted judgment: `docs/reviews/docling-baseline-qualification-full-representation-export-plan-controller-judgment-20260615.md`

## Findings

| ID | Severity | Evidence | Risk | Recommendation | Blocking |
|---|---|---|---|---|---|
| DS-IMPL-001 | High | `representation_export.py` validates output/reference/input paths with lexical `Path.is_relative_to()` only: output path check at lines 500-520, production cache check at lines 523-539, reference JSON check at lines 542-558. `export_manifest()` then writes `workspace_root / entry.output_path` at lines 345-350, and hash validation reads `workspace_root / entry.input_artifact_path` at lines 207-210. Tests cover direct `cache/pdf/...` rejection at `test_candidate_representation_export.py` lines 138-164 and direct reference JSON acceptance at lines 167-194, but do not cover `..` traversal. | A manifest path such as `reports/representation-json/../escape.json` can satisfy the lexical output/root check while writing outside `reports/representation-json`. Likewise an input path containing `..` can resolve into `cache/pdf` without matching the direct lexical `cache/pdf` guard. This weakens the accepted constraints that outputs stay in the allowed directory and that candidate harness must not read/write production-shaped `cache/pdf`. | Normalize or resolve paths against `workspace_root` before boundary checks, or reject any `..` path parts. Compare resolved candidate paths against resolved allowed roots, and add no-live tests for output traversal, reference JSON traversal, and input traversal into `cache/pdf`. | yes |

## Accepted Facts

- Candidate-only / `NOT_READY` status is preserved in the implementation evidence and envelope: `candidate_status`, `field_correctness_status`, `source_truth_status`, `taxonomy_compatibility_status` remain `not_proven`, and parser replacement remains `not_authorized`.
- The route enum is closed to `docling_pdf_candidate`, `pdfplumber_pdf_candidate`, and `eid_xbrl_html_render_candidate`; unsupported fallback source kinds are not accepted by enum parsing.
- Candidate internals are not exported from `fund_agent.fund.documents.__all__`; the public exports remain `DocumentKey`, `ParsedAnnualReport`, `ParsedTable`, `ReportSection`, `FundDocumentRepository`, and `ANNUAL_REPORT_DOCUMENT_KIND`.
- The amended `REFERENCE_EXISTING_JSON` validation path accepts existing JSON under `reports/representation-json/` for validation-only use. This closes the specific S1 reference validation gap, but does not close DS-IMPL-001.
- Lack of built-in Docling/pdfplumber handlers is not blocking for this no-live harness slice because the accepted judgment requires a candidate harness and explicitly defers conversion/export evidence. It remains a future evidence-gate residual.

## Validation

No live/network/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM/analyze/checklist/golden/readiness/release/PR command was run.

No-live validation run:

```text
uv run pytest tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
14 passed in 0.49s
```

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_export.py
```

Result:

```text
All checks passed!
```

## Residuals

- Built-in Docling/pdfplumber export handlers remain deferred to a later reviewed handler implementation or controller-approved Python API injection path.
- S2/S3 provenance/hash residuals and S4/S5/S6 EID HTML render availability remain outside this implementation review.
- The next evidence gate should not proceed until DS-IMPL-001 is fixed and covered by targeted no-live tests.

## Final Recommendation

Do not accept the implementation gate yet. Fix the path normalization/boundary check blocker, add traversal tests, then request targeted DS re-review of DS-IMPL-001 only.
