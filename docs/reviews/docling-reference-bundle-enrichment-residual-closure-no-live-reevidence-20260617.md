# Docling Reference Bundle Enrichment Residual Closure No-live Re-evidence - 2026-06-17

Gate: `Docling Reference Bundle Enrichment Residual Closure No-live Re-evidence Gate`
Role: evidence worker only
Verdict: `RESIDUAL_CLOSURE_REEVIDENCE_PARTIAL_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs and Hashes

- `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json` sha256=`a7fcb523ee6bc9219033ec9ca5ed4876d83ae5ac5b1c0ca31872bcf84f9a3f99`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` sha256=`4b0b3d4714e057098e19aff3565b83eec679fb4af93feec947e7cebacc6c542f`
- `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-controller-judgment-20260617.md` sha256=`e827c8b80607a9d0c319ceabea7a8224dc8bedea81dbfe0216dc705eaf7a66ec`
- `docs/reviews/docling-source-truth-residual-closure-evidence-controller-judgment-20260616.md` sha256=`09d2edf14395143619369c784a95f3927297d1657fb088753b035269eb881a5c`
- `docs/reviews/docling-source-truth-residual-closure-evidence-20260616.md` sha256=`1ee67834d0069d825fe4dd264acdac0e17d850102962733a4067bde3498280fa`
- `reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json` sha256=`001d775271c44e454e1285bf16e2d912cc91dbfdda6b69e1963b6fd80674f0b6`

Accepted checkpoint: `44498ce gateflow: accept docling reference bundle enrichment implementation`.

## Commands Run

```text
uv run python -B - <<'PY' ... PY
```

Validation commands to run after writing:

```text
python -m json.tool reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json
git diff --check -- reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-20260617.md
```

## No-live Repository Guard

- Annual-report access path: `FundDocumentRepository.load_annual_report(..., force_refresh=False)` only.
- Network guard: `socket.socket.connect` and `socket.socket.connect_ex` blocked during repository loads.
- Direct PDF/cache/source-helper access: not used by the evidence wrapper.
- Reference bundles: raw legacy v1 dictionaries; accepted helper performs in-memory enrichment.
- V2 enrichment fields were not prefilled by the evidence wrapper. Row hierarchy was not asserted, so hierarchy-dependent rows remain residual unless the accepted helper can prove them.
- Table context is limited to section inference reason and ParsedTable headers; row labels stay row-local to avoid cross-share-class context contamination.
- Same-row `份额级别` values are included in row label context for sibling value cells because they are directly present in the ParsedTable row.
- No live/network/provider/LLM/analyze/checklist/golden command was run.

Repository loads:

- `S1` `004393/2025`: status=`loaded`, metadata_ok=`True`, cells=`3201`, text_spans=`8`, parsed_cache_hit=`True`
- `S4` `006597/2024`: status=`loaded`, metadata_ok=`True`, cells=`2529`, text_spans=`8`, parsed_cache_hit=`True`
- `S5` `017641/2024`: status=`loaded`, metadata_ok=`True`, cells=`6739`, text_spans=`6`, parsed_cache_hit=`False`
- `S6` `110020/2024`: status=`loaded`, metadata_ok=`True`, cells=`5665`, text_spans=`8`, parsed_cache_hit=`True`

## Summary vs Previous 20260616 Closure Matrix

Previous accepted 20260616 matrix:

- rows_total=`17`
- closed_rows_total=`10`
- residual_rows_total=`7`
- closure_dispositions=`{'disambiguated_source_body_match': 10, 'semantic_assignment_residual': 7}`
- verdict=`RESIDUAL_CLOSURE_PARTIAL_NOT_READY`

Current re-evidence matrix:

- rows_total=`17`
- closed_rows_total=`13`
- residual_rows_total=`4`
- closure_dispositions=`{'disambiguated_source_body_match': 13, 'semantic_assignment_residual': 4}`
- verdict=`RESIDUAL_CLOSURE_REEVIDENCE_PARTIAL_NOT_READY`

## Scoped Seven-row Table

| Sample | Fact | Field | Closure | Source | Fund | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| `S1` | `F015` | `sales_service_fee_C_current_year` | `disambiguated_source_body_match` | `same_source_reference_loaded` | `semantic_rule_satisfied` | source, processed locator and fund semantic rule agree |
| `S1` | `F020` | `manager_holding_range_A` | `disambiguated_source_body_match` | `same_source_reference_loaded` | `semantic_rule_satisfied` | source, processed locator and fund semantic rule agree |
| `S4` | `S4-F015` | `fixed_income_investment_amount` | `disambiguated_source_body_match` | `same_source_reference_loaded` | `semantic_rule_satisfied` | source, processed locator and fund semantic rule agree |
| `S5` | `S5-F032` | `equity_investment_amount` | `semantic_assignment_residual` | `same_source_reference_loaded` | `semantic_rule_rejected` | same-source value is present but fund semantic context is not proven |
| `S6` | `S6-F041` | `benchmark` | `semantic_assignment_residual` | `same_source_reference_loaded` | `semantic_rule_rejected` | same-source value is present but fund semantic context is not proven |
| `S6` | `S6-F049` | `equity_investment_amount` | `semantic_assignment_residual` | `same_source_reference_loaded` | `semantic_rule_rejected` | same-source value is present but fund semantic context is not proven |
| `S6` | `S6-F050` | `stock_investment_amount` | `semantic_assignment_residual` | `same_source_reference_loaded` | `semantic_rule_rejected` | same-source value is present but fund semantic context is not proven |

## Explicit Residual Reasons

- `S5 S5-F032 equity_investment_amount`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven
- `S6 S6-F041 benchmark`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven
- `S6 S6-F049 equity_investment_amount`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven
- `S6 S6-F050 stock_investment_amount`: `semantic_assignment_residual` / `semantic_rule_rejected` - same-source value is present but fund semantic context is not proven

## Validation Results

- `python -m json.tool reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`: passed, exit code 0.
- `git diff --check -- reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-20260617.md`: passed, exit code 0, no output.

## Boundary Check

- `candidate_only=true` preserved.
- `source_truth_status=not_proven` preserved.
- `NOT_READY` preserved.
- No source truth acceptance.
- No Docling baseline promotion.
- No parser replacement.
- No full field correctness claim.
- No release readiness or PR readiness claim.

Final verdict token: `RESIDUAL_CLOSURE_REEVIDENCE_PARTIAL_NOT_READY`

## Self-Check

pass - evidence was generated from repository-mediated ParsedAnnualReport objects and the accepted helper; no code, test, control-doc, commit, stage, push, PR, live/provider/LLM/checklist/golden action was performed.
