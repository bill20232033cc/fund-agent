# Docling Semantic Residual Rule Design Controller Judgment - 2026-06-17

Gate: `Docling Semantic Residual Rule Design Gate`
Role: controller judgment
Verdict: `ACCEPT_DESIGN_WITH_BINDING_NEXT_GATE_AMENDMENTS_NOT_READY`
Release/readiness: `NOT_READY`

## Accepted Artifacts

- Design: `docs/reviews/docling-semantic-residual-rule-design-20260617.md`
- AgentDS review: `docs/reviews/docling-semantic-residual-rule-design-review-ds-20260617.md`
- AgentMiMo review: `docs/reviews/docling-semantic-residual-rule-design-review-mimo-20260617.md`

## Judgment

Accepted as the design direction for the seven remaining Docling source-truth residual rows.

The design correctly identifies the current blocker as missing fund-semantic context, not source access, numeric normalization, or a proof that Docling cannot parse the source. It preserves the accepted boundary:

- candidate-only
- repository-mediated annual-report access
- no direct PDF/cache/source-helper access
- no live/source acquisition
- no row closure by value equality alone
- no source-truth acceptance
- no baseline promotion
- no parser replacement
- no full field correctness claim
- no release or PR readiness

`NOT_READY` remains the controlling status.

## Covered Residual Rows

The design covers all seven residual rows from the accepted residual closure evidence:

- `F015` `sales_service_fee_C_current_year`
- `F020` `manager_holding_range_A`
- `S4-F015` `fixed_income_investment_amount`
- `S5-F032` `equity_investment_amount`
- `S6-F041` `benchmark`
- `S6-F049` `equity_investment_amount`
- `S6-F050` `stock_investment_amount`

The design correctly keeps `S6-F041` fail-closed unless benchmark-labeled context is proven, and keeps `S6-F049` / `S6-F050` fail-closed unless row hierarchy distinguishes equity aggregate from stock child-row semantics.

## Review Disposition

AgentDS verdict: `PASS_WITH_FINDINGS`.

AgentMiMo verdict: `PASS_WITH_FINDINGS`.

No reviewer found a boundary violation or missing residual row. Both reviewers identified the same material gap: the design is directionally correct, but not yet precise enough for direct implementation because reference-bundle fields, table-family classification, and row-hierarchy encoding are not specified at code-generation-ready granularity.

## Binding Amendments For Next Gate

The next gate must not jump straight to implementation. It must first produce a field-level implementation plan or narrow design addendum that resolves:

1. Reference-bundle data model fields:
   - exact field names
   - types
   - serialization / deserialization behavior
   - whether each field belongs on `RepositoryReferenceCell`, `RepositoryReferenceTextSpan`, or `RepositoryReferenceBundle`

2. Table-family classification:
   - deterministic input signals
   - allowed family labels
   - unknown/failure behavior
   - how classification is consumed by residual closure rules

3. Row hierarchy encoding:
   - parent/child row representation
   - whether current `row_label_path` is preserved or extended
   - how `equity_investment_amount` and `stock_investment_amount` are distinguished when values are identical

4. Share-class and period-context checks:
   - whether share class may be proven from column header, row label, or table context
   - current-period vs prior-period canonical variants

5. Diagnostic scope:
   - rejected-match diagnostics are optional/future unless explicitly justified as needed for closure evidence

6. Partial enrichment behavior:
   - missing enriched context must fail closed for the relevant predicate
   - partially enriched bundles may close only when the field-specific required predicates are fully proven

These amendments are binding before any implementation worker is asked to change candidate internals.

## Non-goals Preserved

This gate does not authorize:

- code implementation
- production parser replacement
- source truth acceptance
- baseline promotion
- release readiness
- PR readiness
- direct PDF/cache/source-helper access
- Service/UI/Host/renderer/quality-gate parser access
- live acquisition or provider/LLM/analyze/checklist commands

## Validation

Controller observed:

```text
git diff --check -- docs/reviews/docling-semantic-residual-rule-design-20260617.md
```

The command completed successfully with no output.

## Next Gate

Recommended next gate: `Docling Reference Bundle Field-spec Planning Gate`.

Purpose: resolve the binding amendments above into a code-generation-ready field-level plan for candidate-only reference-bundle enrichment and semantic-rule predicate expansion, while preserving `NOT_READY` and all no-live/source-truth boundaries.
