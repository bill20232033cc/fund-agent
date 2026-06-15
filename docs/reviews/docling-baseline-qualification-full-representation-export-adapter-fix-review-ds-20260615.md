# Docling Adapter Fix Targeted Review - DS

Date: 2026-06-15

Gate: Full Representation Export Evidence Gate - Docling adapter fix targeted review

Verdict: PASS

## Scope

Reviewed only:

- `docs/reviews/docling-baseline-qualification-full-representation-export-adapter-fix-evidence-20260615.md`
- `fund_agent/fund/documents/candidates/representation_handlers.py`
- `tests/fund/documents/test_candidate_representation_handlers.py`

No source/code changes were made by this review.

## Findings

| ID | Severity | Evidence | Recommendation | Blocking |
|---|---|---|---|---|
| DS-AF-1 | Info | `representation_handlers.py` maps Docling `export_to_dict()` through `_docling_result_to_mapping()`, derives sections/headings from `texts[*].label in {"section_header", "title"}`, reads nested `tables[*].data.table_cells`, maps row/column offsets and header flags into cell locators, and reads `prov[0].page_no` / `prov[0].bbox` for page and bbox. | Accept the adapter fix for this targeted gate. | No |
| DS-AF-2 | Info | `test_docling_handler_maps_exported_text_labels_and_nested_table_cells` uses a fake converter returning a Docling-like dict and asserts section/heading/table-cell counts, section heading text, table page, row/column counts, and row-header mapping. No real Docling conversion or PDF parser execution is used. | Keep future evidence review focused on generated candidate JSON outputs and metrics, not field correctness. | No |
| DS-AF-3 | Info | Reviewed files remain inside candidate representation handler/test scope. No FundDocumentRepository, source policy, production parser, Service, UI, Host, renderer, or quality gate behavior is touched in this adapter fix. Evidence artifact preserves NOT_READY and candidate-only wording. | No further boundary fix required for this gate. | No |
| DS-AF-4 | Info | Evidence documents `--allow-overwrite` as a same-gate rerun over known-defective candidate outputs, with no production cache overwrite and no S1 reference rewrite. This is acceptable for candidate evidence regeneration within this gate. | Controller may accept the rerun rationale; do not treat regenerated outputs as source truth/readiness. | No |

## Validation

- `uv run pytest tests/fund/documents/test_candidate_representation_handlers.py -q` -> 9 passed
- `uv run ruff check fund_agent/fund/documents/candidates/representation_handlers.py tests/fund/documents/test_candidate_representation_handlers.py` -> passed
- `git diff --check` -> passed

## Residuals

- The adapter fix proves candidate representation mapping shape only. It does not prove disclosed fact correctness, taxonomy compatibility, parser replacement, Docling baseline qualification, source truth, release readiness, or MVP readiness.
- Test assertions cover the core broken path. Future evidence review should inspect generated candidate JSON metrics and hashes before any downstream route decision.

Final recommendation: PASS. This targeted adapter fix can proceed to controller judgment for the evidence gate while preserving NOT_READY and candidate-only status.
