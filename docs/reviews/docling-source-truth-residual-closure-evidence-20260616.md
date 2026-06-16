# Docling Source-truth Residual Closure Evidence - 2026-06-16

Gate: `Docling Source-truth Residual Closure No-live Evidence Gate`
Role: evidence worker only
Verdict: `RESIDUAL_CLOSURE_PARTIAL_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Source truth matrix: `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json`
- Source truth matrix sha256: `a7fcb523ee6bc9219033ec9ca5ed4876d83ae5ac5b1c0ca31872bcf84f9a3f99`
- Accepted helper: `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- Accepted implementation judgment: `docs/reviews/docling-source-truth-residual-closure-no-live-implementation-controller-judgment-20260616.md`

Upstream input artifact hashes are preserved in `residual_closure_matrix.json` under `upstream_input_artifacts`.

## No-live Repository Guard

- Annual-report access path: `FundDocumentRepository.load_annual_report(..., force_refresh=False)` only.
- Network guard: socket connect/connect_ex disabled during repository loads.
- Direct PDF/cache/provider/source-helper access: not used.
- Docling conversion, live/source acquisition, provider/LLM/analyze commands: not run.
- Evidence scope: candidate-only residual closure attempt; not baseline promotion, not source truth, not parser replacement, not full correctness, not release/PR readiness.

Repository-mediated reference bundles:

- `S1` `004393/2025`: status=`loaded`, metadata_ok=`true`, cells=`3294`, text_spans=`8`
- `S4` `006597/2024`: status=`loaded`, metadata_ok=`true`, cells=`2620`, text_spans=`8`
- `S5` `017641/2024`: status=`loaded`, metadata_ok=`true`, cells=`6879`, text_spans=`6`
- `S6` `110020/2024`: status=`loaded`, metadata_ok=`true`, cells=`5784`, text_spans=`8`

## Result Summary

- Residual input rows processed: `17`
- Closed by helper contract: `10`
- Residuals preserved: `7`
- Closure dispositions: `disambiguated_source_body_match=10, semantic_assignment_residual=7`
- `S5-F023`: closed only with `same_source_reference_loaded` + `locator_context_available` + `semantic_rule_satisfied`.
- `S6-F041`: preserved as `semantic_assignment_residual`; benchmark-labeled source context remains unproven.

## Per-row Matrix

| Row | Field | Source | Processed | Fund | Closure | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| `S1 F002` | `fund_code` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S1 F015` | `sales_service_fee_C_current_year` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_rejected` | `semantic_assignment_residual` | same-source value is present but fund semantic context is not proven |
| `S1 F020` | `manager_holding_range_A` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_rejected` | `semantic_assignment_residual` | same-source value is present but fund semantic context is not proven |
| `S4 S4-F001` | `fund_name` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S4 S4-F002` | `fund_code` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S4 S4-F015` | `fixed_income_investment_amount` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_rejected` | `semantic_assignment_residual` | same-source value is present but fund semantic context is not proven |
| `S5 S5-F018` | `fund_name` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S5 S5-F019` | `fund_code` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S5 S5-F023` | `investment_objective` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S5 S5-F032` | `equity_investment_amount` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_rejected` | `semantic_assignment_residual` | same-source value is present but fund semantic context is not proven |
| `S6 S6-F035` | `fund_name` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S6 S6-F036` | `fund_code` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S6 S6-F037` | `manager` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S6 S6-F038` | `custodian` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_satisfied` | `disambiguated_source_body_match` | source, processed locator and fund semantic rule agree |
| `S6 S6-F041` | `benchmark` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_rejected` | `semantic_assignment_residual` | same-source value is present but fund semantic context is not proven |
| `S6 S6-F049` | `equity_investment_amount` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_rejected` | `semantic_assignment_residual` | same-source value is present but fund semantic context is not proven |
| `S6 S6-F050` | `stock_investment_amount` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_rejected` | `semantic_assignment_residual` | same-source value is present but fund semantic context is not proven |

## Residual Blockers

- `sales_service_fee_C_current_year`, `manager_holding_range_A`, `fixed_income_investment_amount`, `equity_investment_amount`, and `stock_investment_amount` rows still have same-source values but unresolved fund-semantic context.
- `S6-F041 benchmark` remains blocked because benchmark-labeled context is not proven; shared investment-objective locator is insufficient.
- This gate still does not establish source truth, full field correctness, parser replacement, baseline promotion, release readiness, or PR readiness.

## Validation Notes

Run after writing:

```text
python -m json.tool reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json
git diff --check
```
