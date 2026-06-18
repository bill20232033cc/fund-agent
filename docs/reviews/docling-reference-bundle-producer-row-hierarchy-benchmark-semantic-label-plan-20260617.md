# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Planning Gate`
Role: planning worker only
Verdict: `HANDOFF_READY_NOT_READY`
Release/readiness: `NOT_READY`

## Accepted Facts

Accepted re-evidence checkpoint:

- Evidence matrix: `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`
- Evidence report: `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-20260617.md`
- Controller judgment: `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-controller-judgment-20260617.md`

Accepted facts from the controller judgment and matrix:

- `rows_total=17`
- `closed_rows_total=13`
- `residual_rows_total=4`
- `closure_dispositions.disambiguated_source_body_match=13`
- `closure_dispositions.semantic_assignment_residual=4`
- Final accepted re-evidence verdict: `RESIDUAL_CLOSURE_REEVIDENCE_PARTIAL_NOT_READY`
- Remaining residual rows:
  - `S5-F032` `equity_investment_amount`
  - `S6-F041` `benchmark`
  - `S6-F049` `equity_investment_amount`
  - `S6-F050` `stock_investment_amount`
- All rows retain `source_truth_status=not_proven`.
- Accepted residual reasons:
  - `S5-F032`, `S6-F049`, `S6-F050`: row hierarchy / aggregate-child proof is not proven.
  - `S6-F041`: benchmark semantic label is not proven.

## First-principles Boundary

This next implementation gate is a candidate helper enrichment gate only.

It is not:

- source truth acceptance;
- Docling baseline promotion;
- parser replacement;
- full field correctness proof;
- release readiness;
- PR readiness;
- golden-set readiness;
- production `EvidenceAnchor` schema admission.

The implementation must preserve:

- `NOT_READY`;
- `candidate_only=true`;
- `source_truth_status=not_proven`;
- no direct PDF/cache/source-helper access;
- no live/network/provider/LLM/analyze/checklist/golden commands;
- no Service/UI/Host/renderer/quality-gate parser path changes.

The accepted helper remains pure: `source_truth_residual_closure.py` must not read files, call `FundDocumentRepository`, call source helpers, call Docling, or construct production `EvidenceAnchor`.

## Planning Position

Implement deterministic enrichment inside the accepted helper path, not by ad hoc evidence-wrapper v2 prefill.

Primary implementation target:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- Specifically the raw legacy v1 path in `_enrich_reference_bundle_contexts()`.

Reason:

- The accepted controller judgment already accepts the v1-only enrichment guard.
- Raw legacy v1 bundles may be enriched by the helper.
- v2 bundles are treated as already enriched and must not be overwritten.
- The last re-evidence intentionally did not prefill v2 fields; remaining residuals are producer/helper enrichment gaps.

## Affected Files

Expected next implementation write set should be limited to:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md`

No README, control doc, production parser, Service/UI/Host/renderer/quality-gate, cache, source-helper, PDF, provider, or release file should be changed.

## Current Code Facts

Current helper already has:

- `RepositoryReferenceCell.row_parent_label_path`
- `RepositoryReferenceCell.row_hierarchy_path`
- `RepositoryReferenceCell.row_hierarchy_role`
- `RepositoryReferenceTextSpan.semantic_context_label`
- `ResidualClosureRule.required_parent_row_label_any`
- `ResidualClosureRule.required_row_hierarchy_role`
- `ResidualClosureRule.rejected_row_hierarchy_roles`
- `ResidualClosureRule.required_text_semantic_context`
- `FIELD_RULES` that require:
  - `equity_investment_amount`: rejects `row_hierarchy_role in ("child", "unknown")`
  - `stock_investment_amount`: requires parent `权益投资` and `row_hierarchy_role="child"`
  - `benchmark`: requires `required_text_semantic_context="benchmark"` and rejects `投资目标`
- `_enrich_reference_bundle_contexts()` currently enriches v1 bundles with:
  - table family classification;
  - share-class context;
  - period context.

Current helper does not yet derive:

- row hierarchy from raw v1 bundle cells;
- `RepositoryReferenceTextSpan.semantic_context_label` from raw v1 text spans.

## Row Hierarchy Enrichment Design

### Goal

Derive `row_parent_label_path`, `row_hierarchy_path`, and `row_hierarchy_role` only when explicit table-local evidence exists.

This targets:

- `S5-F032`: aggregate equity row in a portfolio asset composition table.
- `S6-F049`: aggregate equity row in a portfolio asset composition table.
- `S6-F050`: child stock row under the aggregate equity row.

### Inputs Allowed

The derivation may use only already loaded `RepositoryReferenceCell` fields inside the bundle:

- `fund_code`
- `document_year`
- `repository_source_name`
- `section_id`
- `table_id`
- `row_index`
- `column_index`
- `row_label_path`
- `column_header_path`
- `table_context`
- `table_family` after `_classify_bundle_tables()`
- normalized/raw cell text only for grouping consistency, not for positive row-hierarchy proof

It must not use:

- candidate expected field name as proof;
- value equality alone;
- bounded neighbor labels as positive proof;
- cross-table context;
- page-only proximity;
- PDF/cache/source-helper access.

### Explicit Evidence Rules

Add a private enrichment helper:

```python
def _enrich_row_hierarchy_contexts(
    bundle: RepositoryReferenceBundle,
) -> RepositoryReferenceBundle:
    ...
```

Call order inside `_enrich_reference_bundle_contexts()` for v1 bundles:

1. `_classify_bundle_tables(bundle)`
2. `_enrich_row_hierarchy_contexts(classified)`
3. share/period derivation over the row-hierarchy-enriched cells
4. text semantic enrichment over text spans

Row hierarchy grouping key:

```python
(
    cell.fund_code,
    cell.document_year,
    cell.repository_source_name,
    cell.section_id,
    cell.table_id,
)
```

Row label identity:

- `_row_primary_label(cell)` must return the last non-empty element of `cell.row_label_path` after stripping surrounding whitespace.
- If `row_label_path` is empty or all elements are empty after stripping, return `""`.
- Parent, child, and top-level checks must use `_row_primary_label(cell)` only, not the full joined path and not `row_label_path[0]`.
- Rationale: the last row-label path element is the most specific table-local row label closest to the value cell. For example, `("资产", "权益投资")` has primary label `权益投资`; `("资产", "权益投资", "其中：股票")` has primary label `其中：股票`.
- Earlier path elements may be retained in diagnostics or output paths, but they are not positive proof for parent/child/top-level classification in this gate.

Only classify row hierarchy for cells whose grouped table has:

- `table_family == "portfolio_asset_composition_table"`;
- `section_id == "§8"`;
- at least one explicit current row label containing `权益投资`;
- at least one explicit later child row label containing an explicit positive stock marker for this gate.

Explicit positive stock marker for `stock_investment_amount` closure in this gate:

- current row label must contain `其中` plus `股票`.

Examples accepted:

- `其中：股票`
- `其中:股票`

Examples not accepted as positive `stock_investment_amount` closure proof:

- `股票` alone;
- `美国`;
- `普通股` without `其中`;
- `其中：普通股` for positive `stock_investment_amount` closure under current `FIELD_RULES`;
- detail rows such as country, region, industry, top-ten, or fair-value hierarchy rows.

`其中：普通股` / `其中:普通股` may be treated as child-like portfolio detail context for equity/detail rejection or future rule expansion, but it is not sufficient for positive `stock_investment_amount` closure in this gate. Current `FIELD_RULES["stock_investment_amount"].required_row_label_any` does not include `普通股`, so this plan does not authorize a stock FIELD_RULES expansion for it.

Parent proof:

- Parent must be an explicit same-table row label containing `权益投资`.
- Parent must be in the same table group.
- Parent must have a lower `row_index` than the child.
- Parent must be the nearest preceding explicit aggregate parent candidate before the child, unless another explicit numbered top-level asset row appears between them.
- If there is more than one possible parent with no deterministic nearest relation, keep all involved rows `unknown`.

Aggregate proof:

- A row with current label `权益投资` may become `row_hierarchy_role="aggregate"` only when at least one explicit stock child row under it is present in the same table.
- Set for aggregate row cells:
  - `row_parent_label_path=()`
  - `row_hierarchy_path=("权益投资",)` or the exact normalized label text from `row_label_path`
  - `row_hierarchy_role="aggregate"`
- If no explicit child row under it exists, do not infer aggregate; keep role `unknown`.

Child proof:

- A stock child row may become `row_hierarchy_role="child"` only when its nearest deterministic parent is an explicit `权益投资` row.
- Set for child row cells:
  - `row_parent_label_path=(<权益投资 row label>,)`
  - `row_hierarchy_path=(<权益投资 row label>, <stock child row label>)`
  - `row_hierarchy_role="child"`

Do not set `standalone` for target portfolio rows in this gate.

### Top-level Row Boundary

To avoid treating unrelated later rows as children of `权益投资`, define a private helper:

```python
def _is_explicit_top_level_asset_row(label: str) -> bool:
    ...
```

It returns true for explicit same-table asset composition top-level labels such as:

- `权益投资`
- `基金投资`
- `固定收益投资`
- `贵金属投资`
- `金融衍生品投资`
- `买入返售金融资产`

If a new top-level asset row appears after the parent and before a possible child, it closes the parent scope.

### Ambiguity Fail-closed Rules

Keep role `unknown` when:

- table family is not `portfolio_asset_composition_table`;
- section is not `§8`;
- row labels are missing or empty;
- child label lacks explicit `其中` marker;
- parent `权益投资` is absent;
- multiple parent candidates compete without a deterministic nearest relation;
- row order is missing, non-integer, duplicated within the same table row identity, or otherwise not comparable;
- child appears before parent;
- the relation can only be inferred from value equality or `bounded_neighbor_row_labels`;
- row label indicates a detail/geography/security classification table.

Integer `row_index` gaps are comparable. A table with row indexes such as `0, 2, 5` may still use nearest-preceding-parent logic as long as every involved row has an integer row index and no duplicate row identity blocks deterministic ordering.

## Benchmark Semantic-label Enrichment Design

### Goal

Derive `RepositoryReferenceTextSpan.semantic_context_label="benchmark"` only from explicit benchmark labels in already loaded reference text span context.

This targets:

- `S6-F041` `benchmark`

### Inputs Allowed

Use only:

- `RepositoryReferenceTextSpan.context_label`
- `RepositoryReferenceTextSpan.heading_path`
- `RepositoryReferenceTextSpan.raw_text`
- `RepositoryReferenceTextSpan.normalized_text`
- `RepositoryReferenceTextSpan.section_id`
- optionally `RepositoryReferenceCell` context for table cells already handled by `_cell_has_required_text_semantic_context()`

No direct PDF/cache/source-helper access.

### Helper Functions

Add private helper:

```python
def _enrich_text_span_semantic_contexts(
    bundle: RepositoryReferenceBundle,
) -> RepositoryReferenceBundle:
    ...
```

Add private classifier:

```python
def _derive_text_semantic_context(
    span: RepositoryReferenceTextSpan,
) -> TextSemanticContext:
    ...
```

Derivation rules:

- If `span.section_id != "§2"`, return `"unknown"`.
- Evaluate label locality in this order: `context_label`, then `heading_path`, then `raw_text` prefix.
- `context_label` is the most local label. If `context_label` is explicitly `投资目标` / `投资目的`, return `"investment_objective"` and do not allow a benchmark mention in `heading_path` or `raw_text` to override it.
- If `context_label` is explicitly benchmark, return `"benchmark"` only when no same-locality investment-objective label is also present.
- If `context_label` is generic or empty, evaluate `heading_path`.
- If `heading_path` contains an explicit benchmark label and does not contain an explicit investment-objective label, return `"benchmark"`.
- If `heading_path` contains an explicit investment-objective label and no explicit benchmark label at the same locality, return `"investment_objective"`.
- If `context_label` and `heading_path` conflict across benchmark vs investment-objective labels, return `"unknown"` unless `context_label` is explicitly investment-objective, in which case return `"investment_objective"`.
- Evaluate `raw_text` prefix only when `context_label` and `heading_path` are generic, empty, or non-conflicting.
- If raw text starts with or locally labels the value as `业绩比较基准`, return `"benchmark"`.
- If raw text starts with or locally labels the value as `投资目标`, return `"investment_objective"`.
- If both benchmark and investment-objective labels are present at the same locality and cannot be separated, return `"unknown"`.
- If the value text merely mentions `业绩比较基准` inside an investment-objective sentence, return `"investment_objective"` or `"unknown"`, not `"benchmark"`.

Explicit benchmark labels:

- `业绩比较基准`
- `比较基准`
- `业绩基准`

Explicit investment objective labels:

- `投资目标`
- `投资目的`

Local label detection:

- Treat `context_label` as stronger than `heading_path`, and `heading_path` as stronger than `raw_text`.
- For `context_label` and each `heading_path` element, normalize with existing `_normalize_for_label()` and compare against explicit benchmark/objective labels using substring containment.
- For `raw_text`, prefix detection must be delimiter-aware:
  - Strip leading whitespace, including regular spaces, tabs, newlines, and full-width spaces.
  - Normalize ASCII colon `:` and Chinese colon `：` as equivalent delimiters.
  - Treat pipe `|` and full-width pipe `｜` as equivalent delimiters.
  - Treat one or more whitespace characters after a label as a delimiter.
  - A local prefix matches only when raw text begins with an explicit label followed by end-of-string or a delimiter.
- Raw text examples that are local benchmark proof:
  - `业绩比较基准 | ...`
  - `业绩比较基准｜...`
  - `业绩比较基准：...`
  - `业绩比较基准: ...`
  - `业绩比较基准 ...`
- Raw text examples that are local investment-objective proof:
  - `投资目标：...`
  - `投资目的 | ...`
- Do not classify as benchmark from a sentence such as:
  - `紧密跟踪业绩比较基准，追求跟踪偏离度...`
  when the local label is `投资目标`.

### Consumption

No rule redesign is needed for `benchmark`.

Existing `FIELD_RULES["benchmark"]` already requires:

- `expected_section_id="§2"`
- `rejected_row_label_any=("投资目标",)`
- `required_text_semantic_context="benchmark"`

Existing `_match_satisfies_rule()` already consumes `span.semantic_context_label`.

If semantic label remains `unknown` or `investment_objective`, `S6-F041` remains `semantic_assignment_residual`.

## Exact Implementation Steps

### Step 1 - Add row hierarchy helpers

In `source_truth_residual_closure.py`, add module-level private helpers near other enrichment helpers:

```python
def _enrich_row_hierarchy_contexts(
    bundle: RepositoryReferenceBundle,
) -> RepositoryReferenceBundle:
    ...

def _derive_table_row_hierarchy(
    cells: tuple[RepositoryReferenceCell, ...],
) -> dict[tuple[int, int], tuple[tuple[str, ...], tuple[str, ...], RowHierarchyRole]]:
    ...

def _row_primary_label(cell: RepositoryReferenceCell) -> str:
    ...

def _is_equity_parent_label(label: str) -> bool:
    ...

def _is_stock_child_label(label: str) -> bool:
    ...

def _is_explicit_top_level_asset_row(label: str) -> bool:
    ...
```

`_row_primary_label(cell)` exact behavior:

```python
def _row_primary_label(cell: RepositoryReferenceCell) -> str:
    for label in reversed(cell.row_label_path):
        stripped = label.strip()
        if stripped:
            return stripped
    return ""
```

All helper predicates below consume this primary label string:

- `_is_equity_parent_label(_row_primary_label(cell))`
- `_is_stock_child_label(_row_primary_label(cell))`
- `_is_explicit_top_level_asset_row(_row_primary_label(cell))`

Keying convention:

- Return mapping key `(row_index, column_index)` so enrichment can update every cell in the row.
- For all cells in a proven aggregate row, assign aggregate metadata.
- For all cells in a proven child row, assign child metadata.

Do not mutate input cells; use `dataclasses.replace()`.

### Step 2 - Add benchmark semantic helpers

In `source_truth_residual_closure.py`, add:

```python
def _enrich_text_span_semantic_contexts(
    bundle: RepositoryReferenceBundle,
) -> RepositoryReferenceBundle:
    ...

def _derive_text_semantic_context(
    span: RepositoryReferenceTextSpan,
) -> TextSemanticContext:
    ...

def _has_local_benchmark_label(values: tuple[str, ...]) -> bool:
    ...

def _has_local_investment_objective_label(values: tuple[str, ...]) -> bool:
    ...
```

Implementation must normalize labels using existing `_normalize_for_label()`.

### Step 3 - Wire helpers into v1 enrichment

Modify `_enrich_reference_bundle_contexts()` without assuming a new share/period helper exists:

```python
if bundle.reference_bundle_schema_version != _LEGACY_REFERENCE_BUNDLE_SCHEMA_VERSION:
    return bundle
classified = _classify_bundle_tables(bundle)
hierarchy_enriched = _enrich_row_hierarchy_contexts(classified)
# Run the existing inline share/period derivation loop over hierarchy_enriched.cells.
share_period_enriched = ...  # existing inline logic, moved only as needed
return _enrich_text_span_semantic_contexts(share_period_enriched)
```

Do not introduce `_enrich_share_period_contexts()` unless the implementation worker explicitly chooses a small local refactor. If introduced, it must preserve the existing share/period behavior exactly and stay private to this module.

### Step 4 - Preserve v2 non-overwrite guard

Do not enrich v2 bundles.

Existing behavior must remain:

- v1/raw legacy bundles are enriched.
- v2 bundles are treated as already enriched.
- invalid/missing v2 context remains fail-closed.

### Step 5 - Do not change FIELD_RULES

The current `FIELD_RULES` already encode the required portfolio and benchmark semantics. The implementation should avoid broadening rules.

No FIELD_RULES expansion is authorized for this gate. In particular, do not add `其中：普通股`, `其中:普通股`, or `普通股` to `FIELD_RULES["stock_investment_amount"].required_row_label_any`.

- For `equity_investment_amount`, keep `rejected_row_hierarchy_roles=("child", "unknown")`.
- For `stock_investment_amount`, keep `required_parent_row_label_any=("权益投资",)` and `required_row_hierarchy_role="child"`.
- For `stock_investment_amount`, keep current positive row-label matching aligned to `其中：股票` / `其中:股票` / `股票`; `其中：普通股` remains residual for positive stock closure unless a later gate explicitly authorizes rule expansion.
- For `benchmark`, keep `required_text_semantic_context="benchmark"` and reject `投资目标`.

## Required Tests

Add focused tests in `tests/fund/documents/test_docling_source_truth_residual_closure.py`.

### Row Hierarchy Positive Tests

1. `test_raw_legacy_portfolio_bundle_enriches_equity_aggregate_row`
   - Build raw v1 bundle with same table:
     - row 0: `权益投资`, value `1818456375.25`
     - row 1: `其中：股票`, same value
   - Do not provide `row_hierarchy_path`, `row_parent_label_path`, or `row_hierarchy_role`.
   - Run `close_source_truth_residuals()`.
   - Expected for `equity_investment_amount`: `disambiguated_source_body_match`.
   - Assert matched row label is `权益投资`.

2. `test_raw_legacy_portfolio_bundle_enriches_stock_child_under_equity_parent`
   - Build raw v1 bundle with same table:
     - row 0: `权益投资`, value `149698325.51`
     - row 1: `其中：股票`, same value
   - Expected for `stock_investment_amount`: `disambiguated_source_body_match`.
   - Assert matched row label is `其中：股票`.

3. `test_raw_legacy_identical_equity_and_stock_values_close_distinct_rows_when_hierarchy_proven`
   - Same raw v1 bundle as S6 portfolio table.
   - Run both `S6-F049` and `S6-F050`.
   - Expected:
     - `S6-F049`: closed on aggregate equity row.
     - `S6-F050`: closed on child stock row.
   - This test proves identical values are allowed only after hierarchy disambiguates rows.

### Row Hierarchy Negative Tests

4. `test_raw_legacy_stock_child_without_equity_parent_remains_residual`
   - Row label `其中：股票` exists but no preceding same-table `权益投资`.
   - Expected: `semantic_assignment_residual`.

5. `test_raw_legacy_stock_label_without_child_marker_remains_residual`
   - Row label `股票` or `普通股` exists without `其中`.
   - Expected for `stock_investment_amount`: `semantic_assignment_residual`.

6. `test_raw_legacy_stock_child_plain_common_share_label_remains_residual_under_current_rules`
   - Row label `其中：普通股` exists under a preceding same-table `权益投资`.
   - Expected for `stock_investment_amount`: `semantic_assignment_residual`.
   - This confirms the plan does not broaden current `FIELD_RULES["stock_investment_amount"].required_row_label_any`.

7. `test_raw_legacy_equity_without_explicit_child_remains_residual`
   - Row label `权益投资` exists but no explicit stock child under it.
   - Expected for `equity_investment_amount`: `semantic_assignment_residual`.

8. `test_bounded_neighbor_labels_still_do_not_prove_hierarchy_after_enrichment`
   - Keep or extend current neighbor test.
   - Provide only `bounded_neighbor_row_labels=("权益投资",)`.
   - Expected: `semantic_assignment_residual`.

9. `test_raw_legacy_detail_table_country_or_region_does_not_become_equity_aggregate`
   - Include labels like `美国` / `国家（地区）` with same value.
   - Expected for `equity_investment_amount`: `semantic_assignment_residual`.

10. `test_raw_legacy_top_level_asset_row_resets_parent_scope`
   - Rows:
     - `权益投资`
     - `基金投资`
     - `其中：股票`
   - Expected for stock child: residual, because `基金投资` closes the equity parent scope.

### Benchmark Semantic Positive Tests

11. `test_raw_legacy_text_span_with_benchmark_context_label_closes_benchmark`
    - Raw v1 text span:
      - `context_label="业绩比较基准"`
      - value equals candidate.
      - no `semantic_context_label` prefilled.
    - Expected: `disambiguated_source_body_match`.

12. `test_raw_legacy_text_span_with_benchmark_row_prefix_closes_benchmark`
    - Raw text begins `业绩比较基准 | 沪深300指数...`.
    - Expected: closed.

13. `test_raw_legacy_text_span_with_benchmark_heading_path_closes_benchmark_when_context_generic`
    - Raw v1 text span:
      - `context_label="基金概况"` or another generic/non-conflicting label.
      - `heading_path=("基金概况", "业绩比较基准")`.
      - raw text contains the benchmark value but does not need a benchmark prefix.
      - no `semantic_context_label` prefilled.
    - Expected: `disambiguated_source_body_match`.

### Benchmark Semantic Negative Tests

14. `test_raw_legacy_investment_objective_text_mentions_benchmark_but_remains_residual`
    - Raw v1 text span:
      - `context_label="投资目标"`
      - raw text mentions `紧密跟踪业绩比较基准`.
    - Expected for `benchmark`: `semantic_assignment_residual`.

15. `test_raw_legacy_ambiguous_benchmark_and_objective_labels_remain_residual`
    - Same span contains both labels with no local separation.
    - Expected: residual.

16. `test_raw_legacy_benchmark_label_outside_section_two_remains_residual`
    - `context_label="业绩比较基准"` but `section_id="§8"`.
    - Expected: residual because rule requires `§2`.

17. `test_raw_legacy_context_objective_heading_benchmark_conflict_remains_residual`
    - Raw v1 text span:
      - `context_label="投资目标"`.
      - `heading_path=("基金概况", "业绩比较基准")`.
      - raw text mentions benchmark.
    - Expected: residual because local investment-objective context rejects cross-layer benchmark inference.

### Regression Tests

18. Existing tests for F015, F020, S4-F015 must continue passing.
19. Existing tests for invalid literal coercion must continue passing.
20. Existing tests for v2 non-overwrite behavior should be added if absent:
    - v2 bundle with unknown row hierarchy remains residual.
    - v2 bundle is not repaired by v1 enrichment.

## Expected Row-level Behavior After Implementation

If raw legacy v1 reference bundles contain the same table-local evidence pattern as the accepted re-evidence projection:

| Row | Expected after implementation | Required proof |
|---|---|---|
| `S5-F032` | may close | `portfolio_asset_composition_table`; explicit aggregate `权益投资`; explicit stock child under it proves aggregate role |
| `S6-F041` | should remain residual for investment-objective text; may close only if explicit benchmark-labeled reference text exists | `semantic_context_label="benchmark"` from local benchmark label |
| `S6-F049` | may close | same-table aggregate `权益投资` row; distinct from stock child row despite identical value |
| `S6-F050` | may close | same-table `其中：股票` / `其中:股票` child under explicit `权益投资` parent; `其中：普通股` remains residual under current stock row-label rules |

Important: the plan does not require or promise 4/4 closure. If the repository-mediated raw bundle lacks explicit benchmark label or deterministic hierarchy, the correct result remains partial residual.

## Validation Commands for Implementation Gate

Allowed implementation validation:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -k "hierarchy or benchmark or raw_legacy or neighbor"
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md
```

No live/network/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release commands are authorized.

## Implementation Evidence Artifact

Implementation worker should write:

- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md`

It must include:

- changed files;
- exact helper functions added/changed;
- tests added;
- validation commands and results;
- explicit note that v1 enrichment only was changed and v2 bundles are not overwritten;
- boundary confirmation:
  - candidate-only;
  - `source_truth_status` remains `not_proven`;
  - no source truth acceptance;
  - no baseline promotion;
  - no parser replacement;
  - no full correctness/readiness claim;
  - no direct PDF/cache/source-helper access;
  - no live/network/provider/LLM/analyze/checklist/golden command.

## Review and Re-review Gates

After implementation evidence:

1. Run two independent code reviews:
   - `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-code-review-ds-20260617.md`
   - `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-code-review-mimo-20260617.md`

2. Controller judgment decides whether findings are blocking/non-blocking.

3. If blocking or accepted non-blocking implementation findings require fixes, run a fix worker with exact write set.

4. Re-review after fixes:
   - `...-rereview-ds-20260617.md`
   - `...-rereview-mimo-20260617.md`

5. Only after controller acceptance may a separate no-live re-evidence gate re-run the 17-row closure matrix.

## Stop Conditions

Implementation worker must stop and keep residual/fail-closed when:

- row hierarchy requires value equality alone;
- row hierarchy requires `bounded_neighbor_row_labels` as positive proof;
- parent `权益投资` is absent from the same table;
- child marker lacks explicit `其中` plus `股票` for positive `stock_investment_amount` closure;
- top-level asset rows make parent scope ambiguous;
- multiple parents compete without deterministic nearest relation;
- table family is not `portfolio_asset_composition_table`;
- benchmark label is inferred only from investment-objective text mentioning benchmark;
- benchmark context is outside `§2`;
- v2 bundle would need repair by helper;
- implementation would require file reads, repository calls, source-helper/PDF/cache access inside helper;
- any path would imply source truth acceptance, baseline promotion, parser replacement, full field correctness, release readiness, PR readiness, or golden readiness.

## Residual Risks

- `S6-F041` may still remain residual if the repository reference projection does not provide a benchmark-labeled span. That is acceptable.
- Row hierarchy derivation from flat legacy rows is intentionally conservative; some valid rows may remain residual rather than risking false closure.
- The accepted evidence matrix still has thin residual diagnostics (`matched_*=[]` for rejected matches). This plan does not add diagnostics unless implementation needs it for tests.
- This plan does not audit producer construction for baseline/source-truth promotion.
- Future re-evidence may be partial; do not force 17/17 or 4/4 closure.

## Next Gate Handoff

Recommended next gate:

```text
Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Implementation Gate
```

Suggested implementation worker prompt:

```text
Role: implementation worker only.
Implement the accepted plan in docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md.
Modify only:
- fund_agent/fund/documents/candidates/source_truth_residual_closure.py
- tests/fund/documents/test_docling_source_truth_residual_closure.py
- docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-evidence-20260617.md
No live/network/provider/LLM/analyze/checklist/golden commands.
No source truth acceptance, no baseline promotion, no parser replacement, no readiness.
Run the plan's allowed pytest commands and git diff --check.
Stop after implementation, tests, and implementation evidence.
```

## Open Questions

None. The next implementation worker should not need to redesign rules.

## Self-check

pass - this plan is limited to candidate helper enrichment, names exact files/functions/tests, preserves `NOT_READY` and `source_truth_status=not_proven`, and leaves source truth/baseline/readiness decisions to separate gates.
