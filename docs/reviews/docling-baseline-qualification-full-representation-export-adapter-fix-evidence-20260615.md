# Docling Baseline Qualification Full Representation Export Adapter Fix Evidence - 2026-06-15

Gate: `Full Representation Export Evidence Gate`
Role: implementation/evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

During the full representation export evidence run, the first generated S4/S5/S6 Docling candidate JSONs exposed an adapter mapping defect:

- Docling conversion succeeded locally.
- The candidate envelope had page/paragraph/table counts.
- But `heading_count=0`, `section_count=0`, and `table_cell_count=0`.

Root cause: the adapter read only simplified keys such as `sections`, `headings`, `tables[*].cells`, and `tables[*].table_cells`. Current Docling `export_to_dict()` stores:

- headings/sections in `texts[*]` with labels such as `section_header`;
- table cells in `tables[*].data.table_cells`;
- page/bbox provenance in `prov`.

This artifact records the narrow fix. It does not change production repository/source/parser behavior and does not claim source truth, field correctness, parser replacement or readiness.

## 2. Files Changed

- `fund_agent/fund/documents/candidates/representation_handlers.py`
- `tests/fund/documents/test_candidate_representation_handlers.py`

## 3. Fix

The Docling candidate adapter now:

- derives headings from `texts[*]` with `label in {"section_header", "title"}` or obvious annual-report heading text;
- derives section candidates from those headings when explicit sections are absent;
- preserves heading/page/bbox/content hash metadata;
- reads table cells from `tables[*].data.table_cells`;
- computes row/column counts from `end_row_offset_idx` and `end_col_offset_idx`;
- emits cell locators with row/column offsets, spans, header flags, bbox and content hash;
- preserves table provenance page number and bbox.

## 4. Regression Test

Added test:

- `test_docling_handler_maps_exported_text_labels_and_nested_table_cells`

The test uses a fake Docling `export_to_dict()` shape with:

- `texts[*].label="section_header"`;
- `tables[*].data.table_cells`;
- `prov.page_no`;
- `prov.bbox`.

It does not run real Docling conversion.

## 5. Validation

Command:

```text
uv run pytest tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
26 passed in 2.27s
```

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_handlers.py fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py
```

Result:

```text
All checks passed!
```

Command:

```text
git diff --check
```

Result: passed.

## 6. Output Overwrite

The first full export outputs were overwritten with `--allow-overwrite` after the adapter fix.

Reason:

- The first outputs were generated in the same evidence gate.
- They were known-defective candidate evidence because Docling table cells and heading/section locators were not mapped.
- No production cache was overwritten.
- `reference_existing_json` S1 files were not rewritten.

Old Docling output hashes:

| Sample | Old path | Old SHA-256 | Old metrics |
|---|---|---|---|
| S4 `006597/2024` | `reports/representation-json/006597_2024_docling_full.json` | `fc2dedc3acc799dcfef7d795bc45d8d7dd395086f4f9a8829830522e020a149c` | `heading_count=0`, `section_count=0`, `table_cell_count=0` |
| S5 `017641/2024` | `reports/representation-json/017641_2024_docling_full.json` | `8982a37535d2978ea1b47d08237195c2759dc4579b68a28743dcfe6b3443e2b8` | `heading_count=0`, `section_count=0`, `table_cell_count=0` |
| S6 `110020/2024` | `reports/representation-json/110020_2024_docling_full.json` | `451f58e1b37baf772b33c0d10a9f41c192fdce7a89406f55ee17879f2860c72c` | `heading_count=0`, `section_count=0`, `table_cell_count=0` |

New Docling output hashes:

| Sample | New path | New SHA-256 | New metrics |
|---|---|---|---|
| S4 `006597/2024` | `reports/representation-json/006597_2024_docling_full.json` | `ee193cc74542fb2792f2baf1984cf288cf9b55bd321ccee43aff7a6e69258307` | `heading_count=229`, `section_count=229`, `table_cell_count=2759` |
| S5 `017641/2024` | `reports/representation-json/017641_2024_docling_full.json` | `7fe3c36eb3cb10108482bbe877bcdbbac7706471137046394d8322ccf77e56d7` | `heading_count=208`, `section_count=208`, `table_cell_count=7060` |
| S6 `110020/2024` | `reports/representation-json/110020_2024_docling_full.json` | `ce2cbeb348101a21df563be4a60dd57d54ac73a3a14a7454845e7d36d56f86fb` | `heading_count=222`, `section_count=222`, `table_cell_count=5940` |

## 7. Residuals

- These candidate JSONs are still not source truth.
- These candidate JSONs do not prove field correctness.
- These candidate JSONs do not prove taxonomy compatibility.
- These candidate JSONs do not replace the production parser.
- Release/readiness remains `NOT_READY`.

## 8. Final Verdict

`VERDICT: ADAPTER_FIX_READY_FOR_TARGETED_REVIEW_NOT_READY`
