# Docling Reference Bundle Field-spec Plan - 2026-06-17

Status: HANDOFF_READY_NOT_READY

## Gate / Role / Scope

Gate: `Docling Reference Bundle Field-spec Planning Gate`

Role: planning worker only.

Scope: produce a code-generation-ready field-level plan for candidate-only repository reference-bundle enrichment and semantic-rule predicate expansion after the accepted `Docling Semantic Residual Rule Design Gate`.

This plan authorizes no implementation in this turn. It preserves:

- `NOT_READY`
- candidate-only output
- repository-mediated annual-report access through `FundDocumentRepository`
- no direct PDF/cache/source-helper access
- no live/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release commands
- no source truth acceptance
- no baseline promotion
- no parser replacement
- no full field correctness claim
- no release readiness or PR readiness

Annual-report access remains repository-mediated. Future implementation must not add Service/UI/Host/renderer/quality-gate direct parser, PDF, cache, source-helper, Docling, or provider access.

## Accepted Inputs

Read first and treated as current gate inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/docling-semantic-residual-rule-design-controller-judgment-20260617.md`
- `docs/reviews/docling-semantic-residual-rule-design-20260617.md`
- `docs/reviews/docling-semantic-residual-rule-design-review-ds-20260617.md`
- `docs/reviews/docling-semantic-residual-rule-design-review-mimo-20260617.md`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`

Accepted controller verdict: `ACCEPT_DESIGN_WITH_BINDING_NEXT_GATE_AMENDMENTS_NOT_READY`.

Binding next-gate amendments resolved by this plan:

- exact reference-bundle field names, types, defaults, and serialization/coercion behavior
- deterministic table-family classification
- row hierarchy encoding and consumption
- share-class and period-context checks
- diagnostic scope kept optional/future
- partial enrichment fail-closed behavior

## Current Code Facts

`source_truth_residual_closure.py` is a pure candidate helper. It does not read files, does not call Docling, does not access `FundDocumentRepository`, does not call source helpers, and does not construct production `EvidenceAnchor`.

Current dataclasses:

- `RepositoryReferenceCell` has `row_label_path`, `column_header_path`, `table_context`, and source metadata, but no `table_family`, no table-title path, no heading path, no header-band context, no parent/child row hierarchy, no canonical share-class context, and no canonical period context.
- `RepositoryReferenceTextSpan` has `context_label`, but no heading path and no canonical semantic text context label.
- `RepositoryReferenceBundle` has metadata and cell/text span tuples, but no enrichment status or bundle schema marker.
- `ResidualClosureRule` has flat string predicates: required/rejected row labels, required table context, required column header, share-class context, duplicate preservation, and semantic guard.

Current evaluator facts:

- `_match_satisfies_rule()` uses flat substring checks over row labels, column headers, and table context.
- `_has_share_class_context()` only checks column-header values.
- Current portfolio tests split `equity_investment_amount` and `stock_investment_amount` by flat row label. That is not sufficient for the accepted S6-F049/S6-F050 residual because identical values require proven row hierarchy, not value equality plus expected field name.
- Current serialization/deserialization only emits and accepts existing fields.

Therefore implementation must enrich the candidate reference model before expanding semantic predicates. It must not close any target row from current flat labels alone when the accepted residual requires richer context.

## Field Spec with dataclass-level changes

Add module-level literal aliases in `source_truth_residual_closure.py`:

```python
TableFamily = Literal[
    "unknown",
    "expense_fee_table",
    "manager_holding_table",
    "portfolio_asset_composition_table",
    "fair_value_hierarchy_table",
    "financial_statement_table",
    "holding_detail_table",
    "fund_profile_table",
    "benchmark_context_table",
    "other",
]

RowHierarchyRole = Literal["unknown", "standalone", "aggregate", "child"]
ShareClassContext = Literal["unknown", "not_applicable", "A", "C"]
ShareClassContextSource = Literal[
    "unknown",
    "not_applicable",
    "column_header",
    "header_band",
    "row_label",
    "table_context",
]
PeriodContext = Literal[
    "unknown",
    "not_applicable",
    "current_period",
    "prior_period",
    "period_end",
]
PeriodContextSource = Literal[
    "unknown",
    "not_applicable",
    "column_header",
    "header_band",
    "table_context",
]
TextSemanticContext = Literal[
    "unknown",
    "benchmark",
    "investment_objective",
    "fund_profile",
    "other",
]
ReferenceEnrichmentStatus = Literal["not_enriched", "partially_enriched", "enriched"]
```

`RepositoryReferenceCell` additions:

| Field | Type | Default | Serialization / coercion | Purpose |
|---|---|---|---|---|
| `table_title_path` | `tuple[str, ...]` | `()` | serialize as list; missing input -> `()` | table title, caption, or local table heading path |
| `heading_path` | `tuple[str, ...]` | `()` | serialize as list; missing input -> `()` | section/subsection heading path preceding the table |
| `column_header_band_path` | `tuple[str, ...]` | `()` | serialize as list; missing input -> `()` | multi-row/multi-column header bands, outer-to-inner |
| `table_family` | `TableFamily` | `"unknown"` | serialize as string; missing input -> `"unknown"`; invalid input -> `"unknown"` | deterministic table-family classification, populated only by an explicit table-level enrichment/classification step |
| `row_parent_label_path` | `tuple[str, ...]` | `()` | serialize as list; missing input -> `()` | proven parent row labels, outer-to-inner, excluding current row |
| `row_hierarchy_path` | `tuple[str, ...]` | `()` | serialize as list; missing input -> `()`; if upstream proves the row is standalone, set to current `row_label_path` and set `row_hierarchy_role="standalone"`; if standalone/no-parent status is not proven, keep `()` and `row_hierarchy_role="unknown"` | full proven row hierarchy path, parent labels plus current row |
| `row_hierarchy_role` | `RowHierarchyRole` | `"unknown"` | serialize as string; missing/invalid input -> `"unknown"` | aggregate/child/standalone row role |
| `bounded_neighbor_row_labels` | `tuple[str, ...]` | `()` | serialize as list; missing input -> `()` | diagnostic-only / negative-disambiguation context; must not provide positive closure proof |
| `share_class_context` | `ShareClassContext` | `"unknown"` | serialize as string; missing/invalid input -> `"unknown"` | canonical share-class proven for this cell context |
| `share_class_context_source` | `ShareClassContextSource` | `"unknown"` | serialize as string; missing/invalid input -> `"unknown"` | where share class was proven |
| `period_context` | `PeriodContext` | `"unknown"` | serialize as string; missing/invalid input -> `"unknown"` | canonical current/prior/period-end context |
| `period_context_source` | `PeriodContextSource` | `"unknown"` | serialize as string; missing/invalid input -> `"unknown"` | where period context was proven |

Existing `row_label_path` is preserved. Do not overload it with parent labels. Existing `column_header_path` is preserved. `column_header_band_path` adds header-band information that may not fit the current flat path.

`RepositoryReferenceTextSpan` additions:

| Field | Type | Default | Serialization / coercion | Purpose |
|---|---|---|---|---|
| `heading_path` | `tuple[str, ...]` | `()` | serialize as list; missing input -> `()` | heading path around this text span |
| `semantic_context_label` | `TextSemanticContext` | `"unknown"` | serialize as string; missing/invalid input -> `"unknown"` | canonical text context for benchmark vs investment-objective disambiguation |

Existing `context_label` remains raw/local context.

`RepositoryReferenceBundle` additions:

| Field | Type | Default | Serialization / coercion | Purpose |
|---|---|---|---|---|
| `reference_bundle_schema_version` | `str` | `"repository_reference_bundle.v2"` | serialize as string; missing input -> `"repository_reference_bundle.v1"` for legacy payloads | identify enriched vs legacy bundle payloads |
| `enrichment_status` | `ReferenceEnrichmentStatus` | `"not_enriched"` | serialize as string; missing/invalid input -> `"not_enriched"` | evidence/status only; not a pass condition |
| `enrichment_notes` | `tuple[str, ...]` | `()` | serialize as list; missing input -> `()` | non-proof notes; not consumed for closure |

`ResidualClosureRule` additions:

| Field | Type | Default | Consumption |
|---|---|---|---|
| `allowed_table_families` | `tuple[TableFamily, ...]` | `()` | if non-empty, match must have `cell.table_family` in tuple; `"unknown"` never satisfies unless explicitly listed, which target rules must not do |
| `rejected_table_families` | `tuple[TableFamily, ...]` | `()` | if match family is in tuple, reject |
| `required_parent_row_label_any` | `tuple[str, ...]` | `()` | require parent label context in `row_parent_label_path` or parent segment of `row_hierarchy_path` |
| `rejected_parent_row_label_any` | `tuple[str, ...]` | `()` | reject parent label context |
| `required_row_hierarchy_role` | `RowHierarchyRole | None` | `None` | if set, `cell.row_hierarchy_role` must equal it |
| `rejected_row_hierarchy_roles` | `tuple[RowHierarchyRole, ...]` | `()` | reject matching roles |
| `required_period_context` | `PeriodContext | None` | `None` | if set, match must have exact canonical period |
| `rejected_period_contexts` | `tuple[PeriodContext, ...]` | `()` | reject prior/unknown where relevant |
| `allowed_share_class_context_sources` | `tuple[ShareClassContextSource, ...]` | `()` | empty means any proven non-unknown source; otherwise source must be listed |
| `required_text_semantic_context` | `TextSemanticContext | None` | `None` | text-span-only predicate; benchmark requires `"benchmark"` |

Existing `required_table_family_any` remains as legacy raw-context fallback for non-target rules. For the seven target residual rows, implementation must use `allowed_table_families` / `rejected_table_families`, not only raw `table_context` substring matching.

`ResidualClosureRule` remains a Python-only constant configuration in this gate. This plan does not authorize JSON serialization, JSON deserialization, `to_dict()`, `_coerce_rule()`, or config-file loading for rules. Future JSON-loadable rule support would require a separate gate.

## Table-family Classification Spec

Classification is deterministic and candidate-only. It uses only already loaded repository-reference context passed into the helper or constructed upstream through `FundDocumentRepository`; it must not read PDF/cache/source-helper directly.

Allowed labels:

- `unknown`
- `expense_fee_table`
- `manager_holding_table`
- `portfolio_asset_composition_table`
- `fair_value_hierarchy_table`
- `financial_statement_table`
- `holding_detail_table`
- `fund_profile_table`
- `benchmark_context_table`
- `other`

Input signals, in priority order:

1. `section_id`
2. normalized `table_title_path`
3. normalized `heading_path`
4. normalized `table_context`
5. normalized `row_label_path` and `row_hierarchy_path`
6. normalized `column_header_path` and `column_header_band_path`

Conflict resolution:

- First apply explicit reject/override rules: fair-value hierarchy signals override portfolio guesses; detail/statement/fund-profile signals must not satisfy portfolio amount fields.
- When multiple families match from different priority levels, prefer the family supported by the highest-priority signal listed above.
- When multiple families match at the same priority level, prefer the more specific target-safe family only if its decisive term is explicit in that signal; for example, explicit `基金资产组合` / `报告期末基金资产组合` beats generic financial-statement context for portfolio target rows, while explicit `公允价值层次` still overrides both.
- If same-priority signals remain ambiguous after the specific-family check, set `table_family="unknown"` and fail closed for target rules.

Deterministic classification rules:

| Family | Required signals | Reject / precedence |
|---|---|---|
| `expense_fee_table` | `section_id == "§7"` and any title/context/row/header signal contains fee-table terms such as `销售服务费`, `管理人报酬`, `托管费`, `费用` | if only transaction detail/expense total without row-level fee context, use `other` |
| `manager_holding_table` | `section_id == "§10"` and title/context/row signal contains `基金经理持有`, `管理人持有`, or `本基金基金经理持有本开放式基金` | reject employee/senior-management/aggregate-holder tables unless manager-holding row is explicit |
| `portfolio_asset_composition_table` | `section_id == "§8"` and title/context/row signal contains `基金资产组合`, `期末基金资产组合`, `报告期末基金资产组合`, or portfolio rows such as `固定收益投资`, `权益投资`, `其中：股票` | lower priority than `fair_value_hierarchy_table` when fair-value hierarchy terms are present |
| `fair_value_hierarchy_table` | title/context/row/header signal contains `公允价值层次`, `第一层次`, `第二层次`, `第三层次` | must override portfolio row guesses for S4-F015 |
| `financial_statement_table` | title/context signal contains statement terms such as `资产负债表`, `利润表`, `所有者权益`, `现金流量表` | must not satisfy portfolio amount fields |
| `holding_detail_table` | title/context signal contains `前十名`, `明细`, `行业分类`, `地区`, `国家`, `券种`, `股票投资明细` | must not satisfy aggregate portfolio fields |
| `fund_profile_table` | `section_id == "§2"` and title/context/row signal contains fund profile terms | only for identity/profile fields, not target residual closures except as rejection context |
| `benchmark_context_table` | title/context/row signal explicitly contains `业绩比较基准` | may support benchmark only with text/table label proof |
| `other` | enough signals show table exists but no allowed family matches | fail closed for target rules |
| `unknown` | insufficient or absent signals | fail closed for target rules |

Unknown/failure behavior:

- If classification cannot be derived, set `table_family="unknown"`.
- `unknown` and `other` do not satisfy any target residual rule.
- Classification is not source truth; it is candidate metadata used only to prevent unsafe closure.

Consumption by residual closure:

- Target rules set `allowed_table_families` and, where needed, `rejected_table_families`.
- `_match_satisfies_rule()` checks rejected families before allowed families.
- When `allowed_table_families` or `rejected_table_families` is non-empty, the new fields take precedence and `required_table_family_any` is ignored for that rule. If both new and legacy fields are present, rejected families still reject first, allowed families must pass, and legacy raw-context matching cannot override a new-field rejection.
- Legacy `required_table_family_any` may remain for existing tests and rules that do not set new table-family fields, but target rows must not rely on it as the sole proof.

## Row-hierarchy Predicate Spec

Encoding:

- Preserve `row_label_path` as the current row label path exactly as currently modeled.
- Add `row_parent_label_path` for proven parent row labels only.
- Add `row_hierarchy_path` for proven parent-plus-current path.
- Add `row_hierarchy_role` for `standalone`, `aggregate`, `child`, or `unknown`.

Proof requirement:

- Parent/child proof may come from repository parsed table structure, merged-cell/header hierarchy, explicit indentation/level metadata if available, or a deterministic upstream reference-bundle projection.
- Bounded neighbor labels may be stored for diagnostics or negative disambiguation only. They may help explain why an ambiguous match was rejected, but they must not satisfy a positive parent/child, aggregate, standalone, share-class, period, or table-family predicate.
- Value equality, expected field name, row order alone, or nearby duplicate text alone must not prove hierarchy.

Predicate behavior:

- If a rule requires `required_parent_row_label_any` and no parent path is proven, fail closed.
- If a rule requires `required_row_hierarchy_role` and role is `unknown`, fail closed.
- If `equity_investment_amount` and `stock_investment_amount` share the same normalized value in the same table, both may close only if their matched references have distinct `row_index` or distinct proven `row_hierarchy_path`, and the field-specific hierarchy predicates are fully satisfied.
- If they share the same value and hierarchy cannot distinguish aggregate `权益投资` from child `其中：股票`, keep `S6-F049` and `S6-F050` as `RESIDUAL`.

Field-specific hierarchy:

- `fixed_income_investment_amount`: require current row/hierarchy contains `固定收益投资`; reject fair-value hierarchy family and rejected row labels such as `第二层次`, `第三层次`, `合计`.
- `equity_investment_amount`: require aggregate row semantics for `权益投资`; `row_hierarchy_role` must be `aggregate` or `standalone` with no stock-child marker; reject `child`, `其中：股票`, `普通股`, country/region/detail rows.
- `stock_investment_amount`: require child row semantics; `row_hierarchy_role == "child"` and parent path contains `权益投资`; current row/hierarchy must contain `其中：股票` or canonical stock-child equivalent.

## Share-class and Period-context Spec

Share-class proof may come from:

- `column_header_path`
- `column_header_band_path`
- `row_label_path`
- `table_context`

Share-class derivation and consumption:

- Derivation scans allowed sources in this deterministic order: `column_header_path` -> `column_header_band_path` -> `row_label_path` -> `table_context`.
- `column_header_band_path` is the canonical source for outer multi-row/multi-column header bands; it may contain share-class context that is absent from `column_header_path`.
- If the same textual label appears in both `column_header_path` and `column_header_band_path`, normalize and deduplicate it; duplicated evidence must not count as two independent proofs.
- If one source provides an unambiguous A/C value and lower-priority sources are absent or compatible, set `share_class_context` to that value and `share_class_context_source` to the first proving source.
- If same-priority or cross-source signals conflict between A and C, set `share_class_context="unknown"` and fail closed.
- `_match_satisfies_rule()` consumes `cell.share_class_context` and `cell.share_class_context_source`; it must not re-open raw path scanning as a broader positive proof path.

Canonical share-class values:

- `A`
- `C`
- `not_applicable`
- `unknown`

`share_class_context="unknown"` fails any rule that has `ResidualClosureRule.share_class_context` set.

For F015 and F020, allowed proof sources are:

- `column_header`
- `header_band`
- `row_label`
- `table_context`

Accepted A/C variants include exact `A`, `A类`, `A份额`, fund-share suffixes such as `混合A` / `债券A`, and equivalent C variants. Arbitrary Latin suffix words remain rejected, preserving current guard behavior.

Period-context proof may come from:

- `column_header_path`
- `column_header_band_path`
- `table_context`

Period-context derivation and consumption:

- Derivation scans allowed sources in this deterministic order: `column_header_path` -> `column_header_band_path` -> `table_context`.
- `column_header_band_path` is the canonical source for outer period bands such as share-class/group headers that sit above flat current/prior columns.
- If period labels appear in both `column_header_path` and `column_header_band_path`, normalize and deduplicate them.
- If one source provides an unambiguous current/prior/period-end value and lower-priority sources are absent or compatible, set `period_context` to that value and `period_context_source` to the first proving source.
- If same-priority or cross-source signals conflict between current/prior/period-end, set `period_context="unknown"` and fail closed.
- `_match_satisfies_rule()` consumes `cell.period_context` and `cell.period_context_source`; it must not infer a passing period predicate from raw `table_context` when the canonical field is `unknown`.

Canonical period values:

- `current_period`: `本期`, `本报告期`, `报告期`, `本期发生额`, `本年`, and equivalent current-period labels
- `prior_period`: `上期`, `上年度`, `上年同期`, `上年度可比期间`, and equivalent prior-period labels
- `period_end`: `期末`, `报告期末`, `期末余额`, `期末公允价值`, and equivalent period-end labels
- `not_applicable`
- `unknown`

F015 requires:

- `share_class_context == "C"`
- `period_context == "current_period"`
- `table_family == "expense_fee_table"`
- row label proves `销售服务费`

Prior-period and unknown period fail closed for F015.

F020 requires:

- `share_class_context == "A"`
- `table_family == "manager_holding_table"`
- row/table context proves manager holding, not employee/senior-management/aggregate-holder context

## Benchmark Text-span Context Spec

`S6-F041 benchmark` may be evaluated against text spans or table cells, but closure requires explicit benchmark-labeled context.

`RepositoryReferenceTextSpan.semantic_context_label` must be:

- `"benchmark"` for accepted benchmark context
- `"investment_objective"` for investment-objective context
- `"unknown"` when label is missing or ambiguous

Benchmark acceptance predicate:

- `section_id == "§2"`
- source text or row text matches the candidate value
- `semantic_context_label == "benchmark"` for text spans, or table/row/heading context explicitly contains `业绩比较基准` for cells
- investment-objective context is rejected even if the text mentions benchmark tracking

`S6-F041` remains `RESIDUAL` unless benchmark-labeled context is proven. Do not close it from investment-objective wording, section proximity, text equality, or expected field name.

## Serialization and Coercion Contract

Serialization:

- `to_dict()` must emit all new fields with defaults.
- Tuple fields serialize as JSON lists.
- Literal fields serialize as strings.
- Existing output guard fields remain unchanged: candidate-only, not baseline promotion, not parser replacement, not full field correctness, not release readiness.

Coercion:

- `_coerce_cell()` accepts legacy payloads without new fields.
- Missing tuple fields become `()`.
- Missing literal fields become `"unknown"` or `"not_enriched"` as defined above.
- Invalid literal values become `"unknown"` for context fields and do not pass target predicates.
- `_coerce_cell()` is a pure per-cell data coercion step. If `table_family` is missing, it must set `"unknown"` and must not run per-cell table-family classification.
- Table-family derivation belongs to an explicit bundle/table-level enrichment step, such as `_classify_bundle_tables()`, which groups by available table identity and broadcasts one deterministic family to all cells from the same table. If no stable table identity or sufficient table-level signals exist, keep `"unknown"`.
- `row_hierarchy_path` must not be fabricated from neighbor labels. If upstream proves a row is standalone, set `row_hierarchy_path=row_label_path` and `row_hierarchy_role="standalone"`. If standalone/no-parent status is not proven, leave `row_hierarchy_path=()` and set `row_hierarchy_role="unknown"`.
- `share_class_context` and `period_context` may be derived from current flat paths/header bands/table context. If no deterministic variant matches, set `"unknown"`.
- `_coerce_bundle()` must set missing or invalid `enrichment_status` to `"not_enriched"`. It must not infer bundle-level `"partially_enriched"` or `"enriched"` status from cell-level enriched fields; only an explicit upstream bundle construction/enrichment step may set those statuses.
- `ResidualClosureRule` has no serialization/coercion contract in this gate because rules remain Python-only constants.

Compatibility:

- Existing tests and legacy bundles should still deserialize.
- Legacy bundles may keep existing already-proven simple closures, but the seven target residual rows must use enriched predicates. Missing enriched context for a target predicate fails closed.
- Schema version bump for `SourceTruthResidualClosureMatrix` is optional unless result-row fields are added. This plan does not require result-row schema changes.

Diagnostics:

- Rejected-match diagnostics are optional/future.
- Do not add rejected-match diagnostics in the first implementation slice unless implementation evidence proves they are necessary to explain a closure result.
- Diagnostics, if added later, are non-proof observability metadata and must not influence closure.
- `bounded_neighbor_row_labels` belongs to this diagnostic/negative-disambiguation category. It is not a rule-evaluation input for positive closure in Slice 1-3.

Partial enrichment behavior:

- `RepositoryReferenceBundle.enrichment_status` is evidence/status only.
- A partially enriched bundle may close a row only when every field-specific required predicate is proven.
- Missing enriched context fails closed for that predicate dimension.
- A bundle does not need every possible enriched field to close a row; it needs only the fields required by that row's rule.

## Per-residual Expected Behavior for F015, F020, S4-F015, S5-F032, S6-F041, S6-F049, S6-F050

| Row | Field | Required closure proof | Expected behavior |
|---|---|---|---|
| `F015` | `sales_service_fee_C_current_year` | `§7`; same-source value; `expense_fee_table`; row proves `销售服务费`; share class `C`; period `current_period`; no semantic-equivalent duplicate | Close only if all predicates are proven. If multiple semantic-equivalent C/current sales-service-fee matches remain, keep `semantic_equivalent_duplicate_residual`. Missing share/period/table family -> `RESIDUAL`. |
| `F020` | `manager_holding_range_A` | `§10`; same-source value/range after context proof; `manager_holding_table`; manager-holding row/table context; share class `A`; reject employee/senior-management/aggregate holder context | Close only when A share-class manager holding is proven. Missing A share proof or manager-holding family -> `RESIDUAL`. |
| `S4-F015` | `fixed_income_investment_amount` | `§8`; same-source value; `portfolio_asset_composition_table`; row/hierarchy proves `固定收益投资`; amount column context; reject fair-value hierarchy and totals | Close only from portfolio asset-composition row. If classified as fair-value hierarchy/statement/detail/unknown -> `RESIDUAL`. |
| `S5-F032` | `equity_investment_amount` | `§8`; same-source value; `portfolio_asset_composition_table`; aggregate `权益投资` row semantics; amount/period-end context; reject stock child/detail/country/region/fair-value rows | Close only when aggregate equity row semantics are proven. Child stock or detail rows -> `RESIDUAL`. |
| `S6-F041` | `benchmark` | `§2`; same-source text; explicit benchmark label from text span, row label, table context, or heading path | Remains `RESIDUAL` unless `semantic_context_label=="benchmark"` or equivalent table/cell benchmark label is proven. Investment-objective context is rejected. |
| `S6-F049` | `equity_investment_amount` | `§8`; same-source value; `portfolio_asset_composition_table`; aggregate `权益投资` hierarchy; distinct row semantics from S6-F050 if values match | Remains `RESIDUAL` unless hierarchy distinguishes aggregate equity from stock child semantics. Do not close by value equality. |
| `S6-F050` | `stock_investment_amount` | `§8`; same-source value; `portfolio_asset_composition_table`; child stock row under parent `权益投资`; distinct row semantics from S6-F049 if values match | Remains `RESIDUAL` unless child stock hierarchy under equity is proven. Do not close by value equality. |

## Implementation Slices

Slice 1: candidate reference model fields and coercion.

- Modify only candidate internals and targeted tests:
  - `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
  - `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- Add literal aliases and dataclass fields listed above.
- Update `to_dict()`, `_coerce_cell()`, `_coerce_text_span()`, and `_coerce_bundle()`.
- Add deterministic coercion helpers for literals and tuple fields.
- Keep `ResidualClosureRule` as Python-only constant config; do not add rule JSON serialization/deserialization in this gate.
- Keep missing bundle `enrichment_status` as `"not_enriched"` and do not derive bundle status from cells.
- Preserve pure-helper boundary: no file reads, no repository calls, no source helper imports.

Slice 2: table-family, share-class, period, and row-hierarchy predicates.

- Add deterministic classifier helpers using already available cell fields.
- Run table-family classification as a bundle/table-level enrichment step where table identity is available; do not derive missing `table_family` inside `_coerce_cell()`.
- Extend `_match_satisfies_rule()` to evaluate:
  - rejected/allowed table families
  - required/rejected parent labels
  - required/rejected row hierarchy role
  - canonical share-class context and allowed sources
  - canonical period context
  - text semantic context for benchmark
- Replace or wrap the existing `_has_share_class_context()` column-header-only check with a helper that consumes `cell.share_class_context` plus `allowed_share_class_context_sources`. The old helper may be retained only as an internal derivation helper for canonical share-class construction; it must not silently broaden `_match_satisfies_rule()` by scanning extra raw sources at match time.
- Keep missing/unknown context fail-closed.
- Keep legacy predicates only where already safe.

Slice 3: target-rule configuration.

- Update `FIELD_RULES` for the seven target residual fields:
  - F015 uses `expense_fee_table`, C share, current period, duplicate residual preservation.
  - F020 uses `manager_holding_table`, A share.
  - S4-F015 uses `portfolio_asset_composition_table`, rejects `fair_value_hierarchy_table`, fixed-income row.
  - S5-F032 and S6-F049 use aggregate equity row semantics.
  - S6-F050 uses child stock row under equity.
  - S6-F041 uses benchmark semantic text context and rejects investment objective.

Slice 4: no-live residual closure re-evidence.

- Re-run only no-live residual closure against the same accepted target identity if an evidence gate authorizes it.
- Accept closure only when same-source value, locator context, and enriched fund-semantic context all agree.
- Preserve `RESIDUAL` for insufficient enriched context.

## Tests and Validation Commands

Future implementation gate should add or update focused tests:

- serialization emits all new fields with defaults
- legacy payloads deserialize with missing enriched fields set to unknown/defaults
- existing `_cell()` / `_bundle()` test fixtures remain compatible through dataclass defaults after Slice 1
- new tests that need enriched semantics should pass the new fields explicitly by keyword instead of relying on positional constructor order
- invalid literal context deserializes to unknown and fails target predicates
- missing bundle `enrichment_status` coerces to `"not_enriched"` and is not derived from cell-level fields
- table-family classifier returns expected labels for expense fee, manager holding, portfolio asset composition, fair-value hierarchy, financial statement, holding detail, unknown
- table-family conflicts at the same signal priority produce the specified family or `unknown` according to the conflict-resolution rules
- rules that set new table-family fields ignore legacy `required_table_family_any` as a positive override
- F015 closes only with C share + current period + expense fee table; A share/prior period/unknown context remains residual
- F020 closes only with A share + manager holding table; aggregate/employee/senior-management holder remains residual
- S4-F015 rejects fair-value hierarchy and closes only portfolio fixed-income row
- S5-F032 / S6-F049 close only aggregate equity row, not stock/detail child rows
- S6-F050 closes only stock child row under equity parent
- S6-F049/S6-F050 identical values remain residual without proven distinct hierarchy
- S6-F041 remains residual for investment-objective context and closes only with benchmark label
- pure-helper boundary still passes with `open()` blocked and without `FundDocumentRepository` imports

Allowed future validation commands for implementation worker:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -k "reference or table_family or hierarchy or share_class or period or benchmark"
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Optional evidence-gate command only if a later accepted evidence gate authorizes the specific local artifact:

```text
python -m json.tool <accepted-local-no-live-residual-closure-matrix.json>
```

No live/network/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release commands are authorized by this plan.

## Stop Conditions

Stop and keep `RESIDUAL` / `semantic_assignment_residual` when:

- table family is `unknown`, `other`, rejected, or not in the field's allowed family list
- row hierarchy is missing for any field that requires parent/child or aggregate/child distinction
- share-class context is missing or not the required class for F015/F020
- period context is missing, prior, or not current for F015
- benchmark text is only under investment-objective context
- S6-F049 and S6-F050 share the same value but hierarchy does not distinguish aggregate equity from stock child semantics
- closure would rely on value equality, expected field name, row order alone, or nearby context alone
- reference-bundle enrichment would require live acquisition, direct PDF/cache/source-helper access, or non-repository access
- implementation would require source truth acceptance, full field correctness, parser replacement, baseline promotion, release readiness, PR readiness, or production integration

## Non-goals

- No code implementation in this planning gate.
- No review artifact creation beyond this plan.
- No control-doc update.
- No commit, stage, push, PR, merge, mark-ready, or release state action.
- No source-truth acceptance.
- No baseline promotion.
- No parser replacement.
- No full field correctness claim.
- No production integration.
- No direct PDF/cache/source-helper access.
- No Service/UI/Host/renderer/quality-gate direct parser access.
- No live/network/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release command.
- No rejected-match diagnostics unless a future gate justifies them as necessary.

## Completion Report Format

Future implementation/evidence worker should report:

```text
Gate:
Role:
Artifact / changed files:
Rows targeted:
Dataclass fields added:
Rules changed:
Rows closed:
Rows preserved residual:
Per-row disposition:
Guard flags:
Validation:
Stop conditions encountered:
Residual risks:
Self-check: pass | blocked - <reason>
```

This planning gate completion status:

- Artifact: `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md`
- Changed files authorized: this artifact only
- Handoff status: `HANDOFF_READY_NOT_READY`
- Blocking questions: none
- Residuals: implementation, review, re-evidence, production integration, source-truth acceptance, baseline disposition, readiness/release all remain separate gates
- Self-check: plan resolves the accepted binding next-gate amendments while preserving candidate-only, repository-mediated, fail-closed, and `NOT_READY` boundaries
