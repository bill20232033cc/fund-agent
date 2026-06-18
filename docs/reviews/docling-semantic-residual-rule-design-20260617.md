# Docling Semantic Residual Rule Design - 2026-06-17

Status: DRAFT_FOR_REVIEW

## Scope And Non-goals

Gate: `Docling Semantic Residual Rule Design Gate`

Role: design worker only, AgentCodex.

This artifact designs the minimum fund-domain semantic rules or reference-bundle additions needed to address the seven residual rows preserved by the accepted residual closure evidence:

- `F015` `sales_service_fee_C_current_year`
- `F020` `manager_holding_range_A`
- `S4-F015` `fixed_income_investment_amount`
- `S5-F032` `equity_investment_amount`
- `S6-F041` `benchmark`
- `S6-F049` `equity_investment_amount`
- `S6-F050` `stock_investment_amount`

Non-goals:

- No code implementation.
- No production parser replacement.
- No baseline promotion.
- No source-truth acceptance.
- No full field correctness claim.
- No release readiness, PR readiness, push, commit, or control-doc update.
- No Service/UI/Host/renderer/quality-gate direct access to PDF/cache/source helper/Docling output.
- No row closure by value equality alone.
- No weakening of no-live, candidate-only, repository-mediated annual-report access, or `NOT_READY`.

Production annual-report access must remain through `FundDocumentRepository`; any future reference-bundle construction must preserve `force_refresh=False`, blocked network socket guard in no-live validation, and candidate-only output status.

## Accepted Evidence Inputs

Read inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/docling-source-truth-residual-closure-evidence-controller-judgment-20260616.md`
- `docs/reviews/docling-source-truth-residual-closure-evidence-20260616.md`
- `reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`

Accepted evidence facts:

- Residual closure matrix verdict is `RESIDUAL_CLOSURE_PARTIAL_NOT_READY`.
- Controller judgment verdict is `ACCEPT_SOURCE_TRUTH_RESIDUAL_CLOSURE_EVIDENCE_PARTIAL_NOT_READY`.
- `rows_total=17`, `closed_rows_total=10`, `residual_rows_total=7`.
- All 17 rows have `source_layer_status=same_source_reference_loaded` and `processed_layer_status=locator_context_available`.
- The seven residual rows have `fund_layer_status=semantic_rule_rejected` and `closure_disposition=semantic_assignment_residual`.
- Repository-mediated reference bundles were loaded for `S1 004393/2025`, `S4 006597/2024`, `S5 017641/2024`, and `S6 110020/2024`.
- Guard flags preserve candidate-only, not source truth, not baseline promotion, not parser replacement, not full field correctness, not release readiness, force-refresh false, blocked network socket, and repository-only annual-report access.
- `S6-F041 benchmark` is residual because benchmark-labeled source context is not proven; investment-objective context is insufficient.

Current helper facts:

- `ResidualClosureRule` already supports expected section, required/rejected row labels, required table family, required column header, share-class context, duplicate residual preservation, and semantic guard.
- Existing rules already cover all seven residual field names.
- Current helper closes a row only when same-source value, candidate locator context, and fund semantic rule agree.
- Existing rules reject the seven rows because same-source values exist but matched reference context does not prove the required fund semantics.

## Residual Row Diagnosis

| Row | Field | Diagnosis | Likely fix class |
|---|---|---|---|
| `F015` | `sales_service_fee_C_current_year` | The candidate is in `§7` with table locator and value `75815.59`, but same-source matches do not prove all of: sales service fee row, C share-class context, current-period column, and fee table context. Existing rule already requires these dimensions and allows semantic-equivalent duplicates to remain residual. | Reference-bundle enrichment first; semantic rule addition only if current-period / C-share labels need canonical variants. |
| `F020` | `manager_holding_range_A` | The candidate is in `§10` with value `50~100`, but same-source matches do not prove manager-holding row, A share-class context, and manager/management-holder table family. Value ranges can recur in holder tables, aggregate rows, or other share classes. | Reference-bundle enrichment plus minimal semantic rule variants for A-share holder context. |
| `S4-F015` | `fixed_income_investment_amount` | The candidate is in `§8` with value `12106715596.39`, but same-source matches do not prove it is the fixed-income investment amount in the fund asset portfolio table rather than an accounting/fair-value hierarchy/total row duplicate. | Reference-bundle enrichment plus stricter portfolio-table semantic rule. |
| `S5-F032` | `equity_investment_amount` | The candidate is in `§8` with value `1818456375.25`, but same-source matches do not prove the equity-investment aggregate row in the fund asset portfolio table. It must not close on stock subrows, region/country rows, fair-value hierarchy rows, or repeated totals. | Reference-bundle enrichment plus stricter portfolio-table semantic rule. |
| `S6-F041` | `benchmark` | The candidate is in `§2` but normalized text is investment-objective style text: `紧密跟踪业绩比较基准,追求跟踪偏离度及跟踪误差的最小化.` The accepted evidence explicitly says benchmark-labeled source context is unproven and investment-objective context is insufficient. | Explicit residual preservation unless a benchmark-labeled text span or row is added; do not fix by value equality. |
| `S6-F049` | `equity_investment_amount` | The candidate is in `§8` with value `149698325.51`, but same-source matches do not prove equity-investment aggregate context. Same value also appears in `S6-F050`, so equity vs stock semantics are unresolved. | Explicit residual preservation until reference context distinguishes aggregate equity row from stock subrow; semantic rule must reject ambiguous equality. |
| `S6-F050` | `stock_investment_amount` | The candidate is in `§8` with the same value as `S6-F049`. Existing rule requires stock row and rejects equity row, but accepted evidence shows current reference context cannot prove the stock subrow assignment. | Explicit residual preservation until row hierarchy proves stock subrow under equity investment; semantic rule must require parent/child row context. |

First-principles diagnosis:

- The current blocker is not source access or candidate locator availability.
- The blocker is not numeric normalization.
- The blocker is missing or insufficient fund-semantic context for duplicate or near-duplicate same-source matches.
- Therefore the minimum design should enrich context and tighten acceptance predicates; it must not relax rules to accept any same-source value.

## Proposed Minimum Rule Changes

### Rule 1: Fee Current-period Share-class Disambiguation

Applies to `sales_service_fee_C_current_year`.

Minimum acceptance predicate for future implementation:

- section must be `§7`;
- matched reference must be table/cell based, not free text only;
- row label path or table context must prove `销售服务费`;
- column header path must prove current period, such as `本期`, `本报告期`, or canonical equivalent;
- column header path, row label path, or adjacent table header context must prove C share class;
- if more than one same-source match satisfies all predicates, keep `semantic_equivalent_duplicate_residual` rather than closing.

Do not accept:

- management fee, custodian fee, transaction cost, or expense total rows;
- A-share sales service fee;
- prior-period or cumulative columns unless the field explicitly requires them in a later gate;
- value-only matches.

Likely fix classification for `F015`: reference-bundle enrichment first, with a small semantic-rule variant list only for canonical current-period and C-share labels.

### Rule 2: Manager Holding Share-class Range Disambiguation

Applies to `manager_holding_range_A`.

Minimum acceptance predicate for future implementation:

- section must be `§10`;
- row/table context must prove `基金经理持有本开放式基金` or equivalent manager-holding disclosure;
- the matched range must be tied to A share class through column header, row label path, fund-share class label, or table-level share-class header;
- aggregate, total, company employee, senior management, or other-holder context must be rejected;
- range normalization may compare `50~100`, `50-100`, and Chinese interval variants only after context is proven.

Likely fix classification for `F020`: reference-bundle enrichment plus minimal semantic rule addition for A-share class context variants.

### Rule 3: Portfolio Asset-composition Row-family Disambiguation

Applies to `fixed_income_investment_amount`, `equity_investment_amount`, and `stock_investment_amount`.

Minimum acceptance predicate for future implementation:

- section must be `§8`;
- matched reference must come from a fund asset portfolio / period-end portfolio composition table, not a fair-value hierarchy, accounting statement, note, regional exposure, industry exposure, top holding table, or subtotal-only table;
- amount column must be proven by header context such as `金额`, `公允价值`, `期末`, or canonical portfolio amount equivalent;
- percentage/proportion columns must not satisfy amount fields;
- totals and `合计` rows must be rejected unless a field explicitly targets total assets in a later gate.

Field-specific acceptance:

- `fixed_income_investment_amount`: row hierarchy must prove `固定收益投资`; reject `第二层次`, `第三层次`, `合计`, and fair-value hierarchy contexts.
- `equity_investment_amount`: row hierarchy must prove aggregate `权益投资`; reject child stock rows (`其中：股票`), region/country rows, common stock rows, and duplicated stock-only contexts.
- `stock_investment_amount`: row hierarchy must prove `其中：股票` or equivalent stock child row under equity investment; reject aggregate equity row unless the same row path explicitly encodes child stock semantics.

Likely fix classification:

- `S4-F015`: reference-bundle enrichment plus stricter portfolio-table rule.
- `S5-F032`: reference-bundle enrichment plus stricter portfolio-table rule.
- `S6-F049`: explicit residual preservation until aggregate equity vs stock row hierarchy is proven.
- `S6-F050`: explicit residual preservation until stock child-row hierarchy is proven.

### Rule 4: Benchmark-labeled Context Requirement

Applies to `benchmark`.

Minimum acceptance predicate for future implementation:

- section must be `§2`;
- source context must be explicitly labeled `业绩比较基准` or canonical benchmark equivalent;
- investment-objective context must be rejected even when it mentions tracking the benchmark;
- benchmark text must be associated with the benchmark label by row label, heading, or text-span context, not by nearby value equality or shared section alone.

Likely fix classification for `S6-F041`: explicit residual preservation now; reference-bundle enrichment is required before any closure attempt. Do not add a semantic rule that accepts investment-objective text as benchmark context.

## Reference Bundle Requirements

Future reference-bundle enrichment should be candidate-only and repository-mediated. It should not read PDF/cache/source helper directly and should not call live acquisition.

Minimum additions:

1. Preserve table title / caption / preceding heading path for each `RepositoryReferenceCell`.
2. Preserve multi-row and multi-column header hierarchy, including share-class header bands and current/prior-period header bands.
3. Preserve row hierarchy, including parent row and child row relation for rows such as `权益投资 -> 其中：股票`.
4. Preserve nearby row labels only as bounded context, with deterministic distance limits, to distinguish aggregate and child rows without accepting arbitrary nearby values.
5. Preserve table-family classification as candidate metadata, for example `expense_fee_table`, `manager_holding_table`, `portfolio_asset_composition_table`, `fair_value_hierarchy_table`, `financial_statement_table`, and `holding_detail_table`.
6. Preserve section text spans with context labels that distinguish `投资目标` from `业绩比较基准`.
7. Preserve matched-reference diagnostics for residual rows, including rejected match count and first few rejected contexts, without treating diagnostics as source truth.

Reference-bundle stop conditions:

- If a matched same-source value has no table title, header path, or row hierarchy sufficient for the field-specific predicate, keep `semantic_assignment_residual`.
- If two field candidates share the same value and the bundle cannot prove distinct row semantics, keep both rows residual or classify as an explicit unresolved duplicate; do not close one by expected field name.
- If benchmark text is only available under investment-objective context, keep `S6-F041` residual.

## Implementation Slices For Later Gate

Slice 1: Reference-bundle context enrichment plan and implementation.

- Allowed area: Fund documents candidate internals only.
- Add table title, heading path, row hierarchy, header hierarchy, table-family classification, and section text-span context labels to repository reference bundle construction.
- Preserve existing guard flags and candidate-only output model.
- Do not alter production parser, extractor, renderer, Service, UI, Host, quality gate, source policy, or annual-report fallback.

Slice 2: Semantic-rule predicate expansion.

- Extend `ResidualClosureRule` or a successor candidate-only rule model only as needed for:
  - current-period header variants;
  - share-class context variants;
  - table-family allow/reject lists;
  - row-hierarchy parent/child predicates;
  - benchmark-labeled text-span predicates.
- Keep current fail-closed behavior: missing context yields residual, not pass.

Slice 3: Residual closure re-evidence.

- Re-run no-live residual closure against the same seven-row target set and same upstream matrix identity.
- Expected acceptable outcomes:
  - rows close only when same-source value, locator context, and new fund-semantic context all agree;
  - rows remain residual when context is still insufficient;
  - `S6-F041` remains residual unless benchmark-labeled context is proven;
  - `S6-F049` / `S6-F050` remain residual unless row hierarchy distinguishes equity aggregate from stock child row.

## Tests And No-live Validation For Later Gate

Minimum test coverage for later implementation gate:

- Unit tests for share-class header context:
  - C-share current-period sales service fee can pass when all contexts are present.
  - A-share or prior-period sales service fee does not pass for `sales_service_fee_C_current_year`.
  - manager holding A-share range can pass only under manager-holding disclosure context.
  - aggregate or non-manager holder rows are rejected.

- Unit tests for portfolio row hierarchy:
  - fixed-income amount passes only under `固定收益投资` in portfolio asset composition context.
  - equity aggregate amount rejects `其中：股票` child row and non-portfolio duplicated contexts.
  - stock amount passes only with stock child-row context.
  - identical equity and stock numeric values remain residual without parent/child proof.

- Unit tests for benchmark context:
  - benchmark passes only with `业绩比较基准` label.
  - investment-objective text mentioning benchmark remains rejected.

- No-live evidence validation:
  - `python -m json.tool <new residual closure matrix>`
  - focused pytest for candidate residual closure helper and reference bundle projection
  - `git diff --check`

Expected invariant assertions:

- `candidate_only=true`
- `not_source_truth=true`
- `not_baseline_promotion=true`
- `not_parser_replacement=true`
- `not_full_field_correctness=true`
- `not_release_readiness=true`
- repository access only via `FundDocumentRepository`
- `force_refresh=False`
- network socket guard remains blocked for no-live repository loads
- no direct PDF/cache/source helper/provider/LLM/analyze/checklist/golden/readiness command is introduced

## Stop Conditions

Stop and keep `semantic_assignment_residual` if any of the following holds:

- Same-source value exists but table family is not proven.
- Same-source value exists but row label or row hierarchy is missing.
- Same-source value exists but share-class context is missing for share-class-specific fields.
- Same-source value exists but current/prior-period column context is missing for current-year fee fields.
- Same-source value exists under investment-objective context but not benchmark-labeled context.
- Same value appears for aggregate and child portfolio fields and row hierarchy cannot distinguish them.
- Reference bundle construction would require live acquisition, direct PDF/cache/source-helper access, or non-repository access.
- Closure would require claiming source truth, full correctness, parser replacement, baseline promotion, or readiness.

## Residual Risks

- The accepted residual closure matrix does not expose rejected match context, so this design identifies minimum required context dimensions but does not prove which exact reference-bundle fields are absent for each rejected match.
- Existing repository parsed tables may not preserve enough merged-cell header hierarchy or parent/child row hierarchy for all samples; later implementation may still need to preserve residuals for some rows.
- `F015` may remain residual even after context enrichment if multiple semantically equivalent C-share current-period sales service fee rows remain.
- `S6-F049` and `S6-F050` are high-risk because identical normalized values can be valid for both aggregate equity and stock child rows in some index fund disclosures; they must not close without explicit row semantics.
- `S6-F041` must remain residual unless benchmark-labeled context is directly proven; investment-objective wording is not a benchmark field.
- This design is not evidence of baseline suitability, production integration readiness, release readiness, or source-truth correctness.

## Completion Report Format

Future implementation/evidence worker report should include:

```text
Gate:
Role:
Artifact:
Changed files:
Rows targeted:
Rows closed:
Rows preserved residual:
Per-row disposition:
Guard flags:
Validation:
Residual risks:
Self-check: pass | blocked - <reason>
```

This design worker completion status:

- Artifact written: `docs/reviews/docling-semantic-residual-rule-design-20260617.md`
- Code implementation: not performed
- Control docs: not modified
- Commit/stage/push/PR: not performed
- Release/readiness: `NOT_READY`
- Blocking questions: none
- Self-check: pass
