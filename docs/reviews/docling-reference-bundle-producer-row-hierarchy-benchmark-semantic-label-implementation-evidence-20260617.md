# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Implementation Evidence - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Implementation Gate`
Role: implementation worker only
Verdict: `IMPLEMENTATION_COMPLETE_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Accepted plan: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
- Controller judgment: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-controller-judgment-20260617.md`
- Accepted plan commit: `a4f2803`

## Changed Files

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md`

No other files were intentionally modified.

## Implementation Summary

Implemented deterministic candidate helper enrichment only in the raw legacy v1 path of `_enrich_reference_bundle_contexts()`.

Added/changed helper behavior in `source_truth_residual_closure.py`:

- `_enrich_reference_bundle_contexts()` now keeps the v2 guard unchanged and enriches only `repository_reference_bundle.v1`.
- `_enrich_row_hierarchy_contexts()` groups cells by table identity and broadcasts proven row hierarchy metadata.
- `_derive_table_row_hierarchy()` derives §8 `portfolio_asset_composition_table` aggregate/child roles from explicit same-table row labels only.
- `_row_primary_label()` uses the last non-empty stripped `row_label_path` element.
- `_is_equity_parent_label()`, `_is_stock_child_label()`, `_is_explicit_top_level_asset_row()`, `_is_detail_or_geography_row()`, and `_is_comparable_row_index()` implement fail-closed row hierarchy predicates.
- `_enrich_text_span_semantic_contexts()` derives semantic labels for raw legacy text spans.
- `_derive_text_semantic_context()` applies `context_label > heading_path > raw_text prefix` precedence.
- `_has_local_benchmark_label()`, `_has_local_investment_objective_label()`, and `_raw_text_has_local_label()` implement benchmark/objective label detection, including delimiter-aware raw prefix handling.

No `FIELD_RULES` expansion was made. In particular, `普通股` was not added to `FIELD_RULES["stock_investment_amount"].required_row_label_any`.

## Tests Added

Added focused tests covering the accepted plan intent:

- raw v1 `权益投资` + `其中：股票` closes `equity_investment_amount` aggregate row.
- raw v1 `权益投资` + `其中：股票` / `其中:股票` closes `stock_investment_amount` child row.
- identical equity/stock values close distinct rows only after hierarchy enrichment.
- no parent remains residual.
- `股票` / `普通股` without `其中` remains residual.
- `其中：普通股` under `权益投资` remains residual for `stock_investment_amount`.
- equity row without explicit child remains residual.
- `bounded_neighbor_row_labels` does not prove hierarchy.
- country/geography/detail row does not bridge parent to child.
- top-level asset row resets parent scope.
- v2 bundle with unknown hierarchy is not repaired by raw v1 enrichment.
- raw v1 benchmark positive cases from `context_label`, raw prefix, and `heading_path`.
- raw v1 benchmark negative cases for investment objective mention, ambiguous objective/benchmark label, outside §2, and context objective plus heading benchmark conflict.

Existing regression coverage for F015, F020, S4-F015, invalid literal coercion, boundary flags, and pure helper behavior remains in the same test file.

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Result:

```text
80 passed in 0.80s
```

Command:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -k "hierarchy or benchmark or raw_legacy or neighbor"
```

Result:

```text
28 passed, 52 deselected in 0.78s
```

Command:

```text
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md
```

Result: pass - exit 0, no output.

## Boundary Confirmation

- Preserves `NOT_READY`.
- Preserves `candidate_only=true`.
- Preserves `source_truth_status=not_proven`.
- No source truth acceptance.
- No Docling baseline promotion.
- No parser replacement.
- No full field correctness claim.
- No release readiness, PR readiness, or golden readiness.
- No live/network/provider/LLM/analyze/checklist/golden command.
- No direct PDF/cache/source-helper access.
- No `FundDocumentRepository` call.
- No Service/UI/Host/renderer/quality-gate change.
- No evidence-wrapper v2 prefill solution.
- v2 bundles are treated as already enriched and are not overwritten.
- No `FIELD_RULES` expansion for `普通股`.
- No stage/commit/push/PR.

## Residual Risks

- This remains candidate helper enrichment only; any changed closure count requires a separate no-live re-evidence gate.
- Some real legacy table layouts may remain residual if table-local row labels are ambiguous or lack explicit `其中：股票` under `权益投资`.
- `S6-F041` may remain residual when repository text spans do not expose an explicit benchmark local label.
