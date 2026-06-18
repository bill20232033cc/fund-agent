# Docling Baseline Qualification Full Representation Export Implementation Review - MiMo - 2026-06-15

Verdict: `FAIL`

## Review Scope

Reviewed target files:

- `fund_agent/fund/documents/candidates/representation_export.py`
- `tests/fund/documents/test_candidate_representation_export.py`
- `fund_agent/fund/README.md` relevant added paragraph
- `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-evidence-20260615.md`

Accepted plan/controller input:

- `docs/reviews/docling-baseline-qualification-full-representation-export-plan-controller-judgment-20260615.md`

This review did not run live/network/PDF/parser/Docling/provider/LLM/analyze/readiness/release commands. I did not rerun pytest/ruff because static review found a blocking path-boundary defect.

## Findings

| severity | evidence | recommendation | blocking |
|---|---|---|---|
| High | `representation_export.py` validates paths with lexical `Path.is_relative_to()` before filesystem normalization. `_ensure_output_path()` accepts any `.json` path lexically under `reports/representation-json` and then `export_manifest()` writes `workspace_root / entry.output_path`; a manifest output such as `reports/representation-json/../../cache/pdf/out.json` passes the prefix check but writes under `cache/pdf`. The same issue exists for input validation: `_ensure_not_production_cache()` rejects direct `cache/pdf/...` but does not reject `cache/eid-artifact-capture/../../pdf/foo.pdf`, which resolves to `cache/pdf/foo.pdf`. This breaks the accepted controller constraint that the harness must not write `cache/pdf` or make production-shaped cache paths valid candidate inputs. Relevant code: `fund_agent/fund/documents/candidates/representation_export.py` `_ensure_output_path()`, `_ensure_not_production_cache()`, `_ensure_reference_json_path()`, and `export_manifest()` path join/write path. Current tests only reject direct `cache/pdf/...`, not traversal. | Normalize and confine paths before validation and before read/write. Resolve `workspace_root`, `output_root`, `PRODUCTION_CACHE_ROOT`, candidate input paths and output paths with `resolve(strict=False)` or an equivalent safe normalizer, then assert resolved paths remain within allowed roots and outside resolved `workspace_root/cache/pdf`. Add tests for `reports/representation-json/../../cache/pdf/out.json`, `reports/representation-json/../outside.json`, `cache/eid-artifact-capture/../../pdf/foo.pdf`, and `reports/representation-json/../../cache/pdf/ref.json` for `REFERENCE_EXISTING_JSON`. | yes |

## Accepted Facts

- The implementation remains under `fund_agent/fund/documents/candidates/` and does not modify `FundDocumentRepository`, source policy, production parser, Service/UI/Host/renderer/quality gate, or public `fund_agent.fund.documents.__all__`.
- Candidate route kinds are closed to `docling_pdf_candidate`, `pdfplumber_pdf_candidate`, and `eid_xbrl_html_render_candidate`; non-EID/fallback route strings are rejected by enum parsing.
- Output envelopes preserve `candidate_status=not_proven`, `source_truth_status=not_proven`, `field_correctness_status=not_proven`, `taxonomy_compatibility_status=not_proven`, and `production_parser_replacement_status=not_authorized`.
- `REFERENCE_EXISTING_JSON` now validates existing JSON under `reports/representation-json/` and is not rewritten by `export_manifest()`, which matches the S1 reference-existing-json intent.
- Lack of built-in Docling/pdfplumber handlers is not itself blocking for this no-live harness slice. The implementation evidence correctly records that future evidence needs either reviewed handlers or a controller-approved injection path.

## Residuals

- After the path confinement fix, rerun the targeted no-live validation recorded by the implementation evidence:

```text
uv run pytest tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run ruff check fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_export.py
git diff --check
```

- Next evidence gate must still verify no Docling model download, no network, no `cache/pdf` mutation, no fallback, and no readiness/source-truth/field-correctness claims.

## Final Recommendation

`FAIL`: fix path normalization/confinement before controller accepts this implementation or opens full representation export evidence.
