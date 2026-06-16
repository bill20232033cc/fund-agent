# Docling Source-truth Residual Closure Evidence Controller Judgment - 2026-06-16

Gate: `Docling Source-truth Residual Closure No-live Evidence Gate`
Role: controller judgment
Verdict: `ACCEPT_SOURCE_TRUTH_RESIDUAL_CLOSURE_EVIDENCE_PARTIAL_NOT_READY`
Release/readiness: `NOT_READY`

## Accepted Artifacts

- Evidence matrix: `reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json`
- Evidence report: `docs/reviews/docling-source-truth-residual-closure-evidence-20260616.md`
- AgentDS review: `docs/reviews/docling-source-truth-residual-closure-evidence-review-ds-20260616.md`
- AgentMiMo review: `docs/reviews/docling-source-truth-residual-closure-evidence-review-mimo-20260616.md`

## Judgment

Accepted as a no-live residual-closure evidence checkpoint.

The evidence processed all 17 residual rows from `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json` through the accepted helper contract. The matrix records:

- `rows_total=17`
- `closed_rows_total=10`
- `residual_rows_total=7`
- `closure_dispositions.disambiguated_source_body_match=10`
- `closure_dispositions.semantic_assignment_residual=7`
- `verdict=RESIDUAL_CLOSURE_PARTIAL_NOT_READY`

This is not source truth acceptance, not parser replacement, not baseline promotion, not full field correctness, not release readiness, and not PR readiness.

## Review Disposition

AgentDS verdict: `PASS`.

AgentMiMo verdict: `PASS`.

Both reviewers confirmed:

- The 17-row residual set matches the source truth matrix residual set.
- JSON summary counts are internally consistent with row data.
- The source truth matrix hash matches `a7fcb523ee6bc9219033ec9ca5ed4876d83ae5ac5b1c0ca31872bcf84f9a3f99`.
- Row-level guard flags preserve candidate-only, not-source-truth, no baseline promotion, no parser replacement, no full correctness, no release readiness, `force_refresh_false=true`, `network_socket_guard=blocked`, and repository-only annual-report access.
- Closed rows are not closed by value equality alone; they require same-source reference, processed locator context, and fund semantic rule satisfaction.
- `S5-F023` is closed only with same-source and semantic-rule support.
- `S6-F041` remains residual because benchmark-labeled context is not proven.

Controller note: AgentDS states it did not cover the repository reference bundle construction internals. This does not block this gate because the accepted evidence artifact records guard flags, repository load status, and per-row closure inputs, while AgentMiMo independently reviewed those guard flags and helper boundary. It remains a residual risk for future promotion gates: this evidence cannot be used as baseline/source-truth proof without a stronger construction audit.

## Residuals

The following rows remain residual:

- `F015` `sales_service_fee_C_current_year`
- `F020` `manager_holding_range_A`
- `S4-F015` `fixed_income_investment_amount`
- `S5-F032` `equity_investment_amount`
- `S6-F041` `benchmark`
- `S6-F049` `equity_investment_amount`
- `S6-F050` `stock_investment_amount`

Residual owner: next Docling semantic residual rule gate.

Residual reason: same-source values are present, but fund-semantic assignment is not proven under the accepted helper contract. `S6-F041` specifically requires benchmark-labeled source context.

## Validation

Controller observed:

```text
python -m json.tool reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json
git diff --check
```

Both completed successfully. `git diff --check` produced no output.

## Next Gate

Recommended next gate: `Docling Semantic Residual Rule Design Gate`.

Purpose: design the minimum fund-domain semantic rules or reference-bundle additions needed to address the 7 remaining residual rows without weakening the no-live/source-truth boundary.
