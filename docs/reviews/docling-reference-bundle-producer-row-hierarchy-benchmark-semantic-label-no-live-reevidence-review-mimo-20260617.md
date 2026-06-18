# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Re-evidence Review (AgentMiMo) - 2026-06-17

Verdict: PASS_WITH_FINDINGS
Blocking findings: 0
Non-blocking findings: 1

## Summary

This re-evidence gate produced valid BLOCKED/REGRESSION evidence, not a successful re-evidence. The current matrix regresses 3 previously-closed rows vs the prior 13-closed checkpoint. The gate verdict `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY` is the correct classification.

## Current vs Prior Checkpoint

| Metric | Prior Checkpoint | Current | Delta |
|---|---|---|---|
| rows_total | 17 | 17 | 0 |
| closed_rows_total | 13 | 10 | -3 |
| residual_rows_total | 4 | 7 | +3 |

Current closure_dispositions: `disambiguated_source_body_match=10, semantic_assignment_residual=5, source_body_mismatch=2`.

## Regression Rows

Three previously-closed rows regressed:

| Sample | Fact | Field | Prior | Current | Source Layer | Fund Layer |
|---|---|---|---|---|---|---|
| S1 | F015 | sales_service_fee_C_current_year | disambiguated_source_body_match | semantic_assignment_residual | same_source_reference_loaded | semantic_rule_rejected |
| S5 | S5-F023 | investment_objective | disambiguated_source_body_match | source_body_mismatch | same_source_text_absent | semantic_rule_unresolved |
| S6 | S6-F035 | fund_name | disambiguated_source_body_match | semantic_assignment_residual | same_source_reference_loaded | semantic_rule_rejected |

S1 F015 regressed from closed to `semantic_assignment_residual`: same-source value is present but fund semantic context is not proven.

S5 S5-F023 regressed from closed to `source_body_mismatch`: same-source repository reference contains no normalized candidate text. This is a distinct failure mode from the other residuals, indicating the reference matching or text normalization changed for this row.

S6 S6-F035 regressed from closed to `semantic_assignment_residual`: same-source value is present but fund semantic context is not proven.

## Target Seven

| Sample | Fact | Field | Disposition |
|---|---|---|---|
| S1 | F015 | sales_service_fee_C_current_year | semantic_assignment_residual |
| S1 | F020 | manager_holding_range_A | disambiguated_source_body_match |
| S4 | S4-F015 | fixed_income_investment_amount | disambiguated_source_body_match |
| S5 | S5-F032 | equity_investment_amount | semantic_assignment_residual |
| S6 | S6-F041 | benchmark | source_body_mismatch |
| S6 | S6-F049 | equity_investment_amount | semantic_assignment_residual |
| S6 | S6-F050 | stock_investment_amount | semantic_assignment_residual |

Target seven summary: 2 closed (F020, S4-F015), 5 residual (F015, S5-F032, S6-F041, S6-F049, S6-F050).

## Finding 1 (Non-blocking) - Three-row regression from prior checkpoint

The current matrix shows a -3 closed-row regression vs the prior 13-closed checkpoint. S1 F015 and S6 S6-F035 regressed to `semantic_assignment_residual`; S5 S5-F023 regressed to `source_body_mismatch`. All three were previously `disambiguated_source_body_match`. The helper update (row hierarchy and text semantic context derivation) likely changed matching or normalization behavior for these rows. This regression should be investigated in a follow-up gate to determine whether the prior closures were false positives or the current rejections are false negatives. The gate is correctly classified as BLOCKED/REGRESSION evidence.

## Boundary Verification

- `candidate_only=true` - preserved
- `source_truth_status=not_proven` - preserved on all rows
- `NOT_READY` - preserved
- No baseline promotion - confirmed
- No source truth acceptance - confirmed
- No parser replacement - confirmed
- No full field correctness claim - confirmed
- No release/readiness claim - confirmed

No-live guard:

- Repository access: `FundDocumentRepository.load_annual_report(..., force_refresh=False)`
- Socket guard: `socket.socket.connect/connect_ex blocked during repository loads`
- Raw legacy v1 bundles; no v2 hierarchy/semantic fields prefilled by wrapper

## Overclaim Check

The re-evidence report does NOT claim: helper correctness, source truth, Docling baseline, full field correctness, or readiness. The report correctly classifies the result as `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`.

## Self-check

- Row count 17 preserved
- Delta -3 closed (10 vs prior 13) verified from disk evidence artifact
- Three regression rows identified: S1 F015, S5 S5-F023, S6 S6-F035
- All boundary and no-live guard conditions verified
- No overclaims detected
- Artifact written to allowed path only
