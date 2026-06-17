# Docling Reference Bundle Comparability Diagnostic Evidence - 2026-06-17

Gate: `Docling Reference Bundle Comparability Diagnostic No-live Evidence Gate`
Role: evidence worker only
Verdict: `COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`
Status: `NOT_READY`

## Inputs and Hashes

- `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json` sha256=`f7fe7a3046fb40427e55179faaa40f20cd3a6c47664387f957c23b832af7639c`
- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json` sha256=`958ee899d7b9f43510ef9cd45bd402be4f69ca58f81dfbfee86832febc776948`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-20260617.md` sha256=`1609597c3dd24944a62c1622ecdfa901708896beb12220e19998cc0e0229a1e3`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-controller-judgment-20260617.md` sha256=`63b343d941f77cca84f3048c4d98f3ea667f0fd2e5d6147d0f8d105597165301`
- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-20260617.md` sha256=`a76f3830fd7b3e806d713212ab59dc56741e6e9b32da391b2098f1c4a49a701b`
- `docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-20260617.md` sha256=`9db62d36203ffd70d42e75525d28809b488af99097859d979a786f33de59f3a8`
- `docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-controller-judgment-20260617.md` sha256=`32a24d48023b5ca032585c2abb8ff8e9b2a43318d6b6bb0dc91cc9c74d678c7b`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` sha256=`f2a4f87a9d85a89c8b9ec6f3292db29c8dfe334d92958212b3126e98028d7ba8` hash/API context only.

## Commands Run

```text
sed -n '...' AGENTS.md docs/reviews/...plan... docs/reviews/...controller...
uv run python -B - <<'PY' ... PY
python -m json.tool reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null
jq -e ".candidate_only == true and .not_source_truth == true and .not_ready == true and (.row_comparison | length == 17)" reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null
jq -e ".summary.regression_rows_total == 3" reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null
git diff --check -- reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md
```

## No-live Boundary

- Comparison basis: committed JSON artifacts only.
- `FundDocumentRepository` was not called.
- No annual report object reload was performed.
- No direct PDF/cache/source-helper access was used.
- No live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR command was used.
- No source/tests/runtime/control/design/README files were edited.
- `candidate_only=true`, `source_truth_status=not_proven`, and `NOT_READY` are preserved.

## Prior vs Current Summary

| Matrix | Closed | Residual | Dispositions |
| --- | ---: | ---: | --- |
| Prior accepted checkpoint | `13` | `4` | `{'disambiguated_source_body_match': 13, 'semantic_assignment_residual': 4}` |
| Current blocked re-evidence | `10` | `7` | `{'disambiguated_source_body_match': 10, 'semantic_assignment_residual': 5, 'source_body_mismatch': 2}` |

Delta closed rows: `-3`.

## Repository Load Drift

| Sample | Cells prior/current/delta | Text spans prior/current/delta | Tables prior/current/delta | Sections prior/current/delta | Section drift |
| --- | --- | --- | --- | --- | --- |
| `S1` | `3201 / 3247 / 46` | `8 / 6 / -2` | `88 / 88 / 0` | `8 / 8 / 0` | `True` |
| `S4` | `2529 / 2561 / 32` | `8 / 6 / -2` | `85 / 85 / 0` | `8 / 8 / 0` | `True` |
| `S5` | `6739 / 6805 / 66` | `6 / 6 / 0` | `114 / 114 / 0` | `6 / 6 / 0` | `True` |
| `S6` | `5665 / 5633 / -32` | `8 / 6 / -2` | `118 / 118 / 0` | `8 / 8 / 0` | `True` |

## Section Inference Drift

| Sample | Section Count Drift | Reason Count Drift |
| --- | --- | --- |
| `S1` | `unknown:54->58; §10:1->2; §2:7->8; §7:5->8; §8:21->12` | `no deterministic section label from ParsedTable text:54->58; table text contains fee-accounting label:5->8; table text contains manager-holding label:1->2; table text contains portfolio/fair-value/financial-statement label:21->12; table text contains profile/objective label:7->8` |
| `S4` | `unknown:64->56; §10:1->2; §2:4->8; §7:7->9; §8:9->10` | `no deterministic section label from ParsedTable text:64->56; table text contains fee-accounting label:7->9; table text contains manager-holding label:1->2; table text contains portfolio/fair-value/financial-statement label:9->10; table text contains profile/objective label:4->8` |
| `S5` | `unknown:83->85; §10:1->2; §2:9->10; §8:14->10` | `no deterministic section label from ParsedTable text:83->85; table text contains manager-holding label:1->2; table text contains portfolio/fair-value/financial-statement label:14->10; table text contains profile/objective label:9->10` |
| `S6` | `unknown:83->78; §10:1->2; §2:9->14; §7:8->12; §8:17->12` | `no deterministic section label from ParsedTable text:83->78; table text contains fee-accounting label:8->12; table text contains manager-holding label:1->2; table text contains portfolio/fair-value/financial-statement label:17->12; table text contains profile/objective label:9->14` |

## Row-level Drift - All 17 Rows

| Sample | Fact | Field | Prior | Current | Source prior/current | Fund prior/current | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `S1` | `F002` | `fund_code` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S1` | `F015` | `sales_service_fee_C_current_year` | `disambiguated_source_body_match` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_rejected` | `regression_with_context_or_source_status_drift` |
| `S1` | `F020` | `manager_holding_range_A` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S4` | `S4-F001` | `fund_name` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S4` | `S4-F002` | `fund_code` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S4` | `S4-F015` | `fixed_income_investment_amount` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S5` | `S5-F018` | `fund_name` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S5` | `S5-F019` | `fund_code` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S5` | `S5-F023` | `investment_objective` | `disambiguated_source_body_match` | `source_body_mismatch` | `same_source_reference_loaded / same_source_text_absent` | `semantic_rule_satisfied / semantic_rule_unresolved` | `regression_with_context_or_source_status_drift` |
| `S5` | `S5-F032` | `equity_investment_amount` | `semantic_assignment_residual` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_rejected / semantic_rule_rejected` | `comparable_no_observed_row_drift` |
| `S6` | `S6-F035` | `fund_name` | `disambiguated_source_body_match` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_rejected` | `regression_with_context_or_source_status_drift` |
| `S6` | `S6-F036` | `fund_code` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S6` | `S6-F037` | `manager` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S6` | `S6-F038` | `custodian` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S6` | `S6-F041` | `benchmark` | `semantic_assignment_residual` | `source_body_mismatch` | `same_source_reference_loaded / same_source_text_absent` | `semantic_rule_rejected / semantic_rule_unresolved` | `status_drift_only` |
| `S6` | `S6-F049` | `equity_investment_amount` | `semantic_assignment_residual` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_rejected / semantic_rule_rejected` | `comparable_no_observed_row_drift` |
| `S6` | `S6-F050` | `stock_investment_amount` | `semantic_assignment_residual` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_rejected / semantic_rule_rejected` | `comparable_no_observed_row_drift` |

## Regression Rows

Regression rows are exactly `F015`, `S5-F023`, `S6-F035`.

| Sample | Fact | Field | Prior | Current | Source prior/current | Fund prior/current | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `S1` | `F015` | `sales_service_fee_C_current_year` | `disambiguated_source_body_match` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_rejected` | `regression_with_context_or_source_status_drift` |
| `S5` | `S5-F023` | `investment_objective` | `disambiguated_source_body_match` | `source_body_mismatch` | `same_source_reference_loaded / same_source_text_absent` | `semantic_rule_satisfied / semantic_rule_unresolved` | `regression_with_context_or_source_status_drift` |
| `S6` | `S6-F035` | `fund_name` | `disambiguated_source_body_match` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_rejected` | `regression_with_context_or_source_status_drift` |

## Target Seven

Prior target seven closed: `3/7`.
Current target seven closed: `2/7`.

| Sample | Fact | Field | Prior | Current | Source prior/current | Fund prior/current | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `S1` | `F015` | `sales_service_fee_C_current_year` | `disambiguated_source_body_match` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_rejected` | `regression_with_context_or_source_status_drift` |
| `S1` | `F020` | `manager_holding_range_A` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S4` | `S4-F015` | `fixed_income_investment_amount` | `disambiguated_source_body_match` | `disambiguated_source_body_match` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_satisfied / semantic_rule_satisfied` | `matched_context_drift_only` |
| `S5` | `S5-F032` | `equity_investment_amount` | `semantic_assignment_residual` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_rejected / semantic_rule_rejected` | `comparable_no_observed_row_drift` |
| `S6` | `S6-F041` | `benchmark` | `semantic_assignment_residual` | `source_body_mismatch` | `same_source_reference_loaded / same_source_text_absent` | `semantic_rule_rejected / semantic_rule_unresolved` | `status_drift_only` |
| `S6` | `S6-F049` | `equity_investment_amount` | `semantic_assignment_residual` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_rejected / semantic_rule_rejected` | `comparable_no_observed_row_drift` |
| `S6` | `S6-F050` | `stock_investment_amount` | `semantic_assignment_residual` | `semantic_assignment_residual` | `same_source_reference_loaded / same_source_reference_loaded` | `semantic_rule_rejected / semantic_rule_rejected` | `comparable_no_observed_row_drift` |

## Classification

- Primary class: `wrapper_or_reference_bundle_construction_drift`.
- Supporting committed-JSON evidence:
  - repository load counts drifted in all four samples;
  - section inference counts/reasons drifted in all four samples;
  - text span counts drifted in `S1`, `S4`, and `S6`;
  - matched row/header/table context drifted across closure rows;
  - source layer status drifted for `S5-F023` and `S6-F041`.
- The current `10/7` matrix remains valid blocked/regression evidence; this diagnostic does not overwrite it and does not claim successful re-evidence.
- The committed JSON artifacts identify non-comparability and wrapper/reference-bundle construction drift before helper semantics. They do not expose enough raw cell/text-span payload to identify the exact producer line. Any exact producer-line diagnosis requires a separately authorized repository-mediated follow-up gate.

Diagnostic findings: `['repository_load_count_drift', 'section_inference_drift', 'text_span_count_drift', 'matched_context_drift', 'source_layer_status_drift', 'json_artifacts_insufficient_for_exact_producer_line', 'current_10_7_artifact_remains_valid_blocked_regression_evidence']`.

## Validation Results

- `python -m json.tool reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null`: pass.
- `jq -e ".candidate_only == true and .not_source_truth == true and .not_ready == true and (.row_comparison | length == 17)" reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null`: pass.
- `jq -e ".summary.regression_rows_total == 3" reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json >/dev/null`: pass.
- `git diff --check -- reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md`: pass.

Final verdict token: `COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`

## Self-check

pass - generated from committed JSON artifacts only; preserved candidate-only/not-proven/NOT_READY; made no baseline, source truth, parser replacement, full correctness, readiness, release, PR, or golden claim.
