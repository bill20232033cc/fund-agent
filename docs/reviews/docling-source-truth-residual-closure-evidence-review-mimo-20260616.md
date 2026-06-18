# Docling Source-truth Residual Closure Evidence Review - 2026-06-16

Gate: `Docling Source-truth Residual Closure No-live Evidence Gate`
Role: review worker only, AgentMiMo
Verdict: **PASS**

## Scope

- Mode: role-scoped evidence review
- Review target: `reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json` and `docs/reviews/docling-source-truth-residual-closure-evidence-20260616.md`
- Source of truth read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, controller judgment, helper source, source_truth_matrix

## Validation Checks Ran

1. Row count: matrix has exactly 17 rows; source_truth_matrix residual_or_blocked_count is 17.
2. Row identity: all 17 (sample_id, fact_id, field_name) tuples match between residual_closure_matrix and source_truth_matrix residuals.
3. No live/Docling/provider access: evidence document asserts repository-mediated access only; helper code (`source_truth_residual_closure.py`) does not read files, call FundDocumentRepository, Docling, source helpers, or construct production EvidenceAnchor.
4. Repository access guard: all rows and repository_loads carry `force_refresh_false=true`, `network_socket_guard=blocked`, `repository_access_only_via_fund_document_repository=true`.
5. No row closed by value equality alone: all 10 closed rows have `matched_reference_origin`, `matched_row_label_path`, and `matched_table_context` populated.
6. Closed rows have three-layer statuses: all 10 closed rows have `source_layer_status`, `processed_layer_status`, and `fund_layer_status`.
7. S5-F023: closed as `disambiguated_source_body_match` with `same_source_reference_loaded` + `locator_context_available` + `semantic_rule_satisfied`; matched reference has `matched_row_label_path=["投资目标"]` and `matched_repository_source_name="eid"` proving same-source semantic rule support.
8. S6-F041: preserved as `semantic_assignment_residual` with `fund_layer_status=semantic_rule_rejected` and reason "same-source value is present but fund semantic context is not proven"; benchmark-labeled context remains unproven.
9. Guard flags: top-level `candidate_only=true`, `not_baseline_promotion=true`, `not_full_field_correctness=true`, `not_parser_replacement=true`, `not_raw_pdf_bbox_truth=true`, `not_release_readiness=true`. Per-row `not_source_truth=true` on all 17 rows.
10. Summary counts: `rows_total=17`, `closed_rows_total=10`, `residual_rows_total=7`, closure dispositions `{disambiguated_source_body_match:10, semantic_assignment_residual:7}` — all match actual row data.
11. Input artifact hashes: 6 upstream artifacts present; `source_truth_matrix_artifact` has sha256 `a7fcb523ee6bc9219033ec9ca5ed4876d83ae5ac5b1c0ca31872bcf84f9a3f99` matching computed hash.
12. JSON validity: `python -m json.tool` passes.

## Findings

未发现实质性问题。

## Open Questions

无。

## Residual Risk

- Evidence does not establish source truth, full field correctness, parser replacement, baseline promotion, release readiness, or PR readiness — consistent with gate scope.
- 7 residual rows (sales_service_fee_C_current_year, manager_holding_range_A, fixed_income_investment_amount, equity_investment_amount, stock_investment_amount, benchmark, equity_investment_amount S6) remain blocked on unresolved fund-semantic context; these require future semantic rule coverage or benchmark-labeled source proof.
- The helper contract depends on upstream `RepositoryReferenceBundle` quality; if repository parsing regress, closure results would silently degrade. Current guard flags mitigate promotion risk.
