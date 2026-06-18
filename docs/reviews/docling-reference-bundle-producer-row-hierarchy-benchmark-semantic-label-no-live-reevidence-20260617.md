# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Re-evidence - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Re-evidence Gate`
Role: evidence worker only
Verdict: `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs and Hashes

- `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json` sha256=`a7fcb523ee6bc9219033ec9ca5ed4876d83ae5ac5b1c0ca31872bcf84f9a3f99`
- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json` sha256=`958ee899d7b9f43510ef9cd45bd402be4f69ca58f81dfbfee86832febc776948`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` sha256=`f2a4f87a9d85a89c8b9ec6f3292db29c8dfe334d92958212b3126e98028d7ba8`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-implementation-controller-judgment-20260617.md` sha256=`bff88dfe1131de9da2f2309337ce5450adc86ca08d9b5efd13b9497c355dc76a`
- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-20260617.md` sha256=`a76f3830fd7b3e806d713212ab59dc56741e6e9b32da391b2098f1c4a49a701b`

Accepted implementation commit: `7f1d0f6`.
Prior accepted checkpoint: `13 closed / 4 residual` at `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`.

## Commands Run

```text
uv run python -B - <<'PY' ... PY
```

Validation commands:

```text
python -m json.tool reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json
git diff --check -- reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-20260617.md
```

## No-live Repository Guard

- Annual-report access path: `FundDocumentRepository.load_annual_report(..., force_refresh=False)` only.
- Network guard: `socket.socket.connect` and `socket.socket.connect_ex` blocked during repository loads.
- Direct PDF/cache/source-helper access: not used by the evidence wrapper.
- Reference bundles: raw legacy v1 dictionaries; current helper performs in-memory enrichment.
- V2 hierarchy/semantic fields were not prefilled by the evidence wrapper.
- No live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR command was run.

Repository loads:

- `S1` `004393/2025`: status=`loaded`, metadata_ok=`True`, cells=`3247`, text_spans=`6`, parsed_cache_hit=`True`
- `S4` `006597/2024`: status=`loaded`, metadata_ok=`True`, cells=`2561`, text_spans=`6`, parsed_cache_hit=`True`
- `S5` `017641/2024`: status=`loaded`, metadata_ok=`True`, cells=`6805`, text_spans=`6`, parsed_cache_hit=`False`
- `S6` `110020/2024`: status=`loaded`, metadata_ok=`True`, cells=`5633`, text_spans=`6`, parsed_cache_hit=`True`

## Current Summary

- rows_total=`17`
- closed_rows_total=`10`
- residual_rows_total=`7`
- closure_dispositions=`{'disambiguated_source_body_match': 10, 'semantic_assignment_residual': 5, 'source_body_mismatch': 2}`
- verdict=`RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`

## Delta vs Prior 13/4 Checkpoint

- previous closed/residual: `13/4`
- current closed/residual: `10/7`
- delta closed rows: `-3`

## Target Seven-row Table

| Sample | Fact | Field | Closure | Source | Fund | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| `S1` | `F015` | `sales_service_fee_C_current_year` | `semantic_assignment_residual` | `same_source_reference_loaded` | `semantic_rule_rejected` | same-source value is present but fund semantic context is not proven |
| `S1` | `F020` | `manager_holding_range_A` | `disambiguated_source_body_match` | `same_source_reference_loaded` | `semantic_rule_satisfied` | source, processed locator and fund semantic rule agree |
| `S4` | `S4-F015` | `fixed_income_investment_amount` | `disambiguated_source_body_match` | `same_source_reference_loaded` | `semantic_rule_satisfied` | source, processed locator and fund semantic rule agree |
| `S5` | `S5-F032` | `equity_investment_amount` | `semantic_assignment_residual` | `same_source_reference_loaded` | `semantic_rule_rejected` | same-source value is present but fund semantic context is not proven |
| `S6` | `S6-F041` | `benchmark` | `source_body_mismatch` | `same_source_text_absent` | `semantic_rule_unresolved` | same-source repository reference contains no normalized candidate text |
| `S6` | `S6-F049` | `equity_investment_amount` | `semantic_assignment_residual` | `same_source_reference_loaded` | `semantic_rule_rejected` | same-source value is present but fund semantic context is not proven |
| `S6` | `S6-F050` | `stock_investment_amount` | `semantic_assignment_residual` | `same_source_reference_loaded` | `semantic_rule_rejected` | same-source value is present but fund semantic context is not proven |

## Explicit Residual Reasons

- `S1 F015 sales_service_fee_C_current_year`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven
- `S5 S5-F023 investment_objective`: `source_body_mismatch` / `semantic_rule_unresolved` - same-source repository reference contains no normalized candidate text
- `S5 S5-F032 equity_investment_amount`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven
- `S6 S6-F035 fund_name`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven
- `S6 S6-F041 benchmark`: `source_body_mismatch` / `semantic_rule_unresolved` - same-source repository reference contains no normalized candidate text
- `S6 S6-F049 equity_investment_amount`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven
- `S6 S6-F050 stock_investment_amount`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven

## Validation Results

- `python -m json.tool reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json`: controller-observed pass after artifact generation.
- `git diff --check -- reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-20260617.md`: controller-observed pass after artifact generation.

## Boundary Check

- `candidate_only=true` preserved.
- `source_truth_status=not_proven` preserved.
- `NOT_READY` preserved.
- No source truth acceptance.
- No Docling baseline promotion.
- No parser replacement.
- No full field correctness claim.
- No release readiness, PR readiness, or golden readiness claim.
- No code/tests/control/design/README changes.
- No stage/commit/push/PR.

Final verdict token: `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`

## Self-check

pass - evidence was generated from repository-mediated `ParsedAnnualReport` objects and the current accepted helper; matrix rows remain candidate-only/not-proven and require separate review before any next gate.
