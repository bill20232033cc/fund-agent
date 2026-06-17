# Docling Reference Bundle Residual Closure Re-evidence Plan Review (MiMo) - 2026-06-17

Gate: `Docling Reference Bundle Residual Closure Re-evidence Planning Gate`
Role: plan reviewer (MiMo)
Target: `docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-20260617.md`
Verdict: `PLAN_REVIEW_PASS_NOT_READY`
Release/readiness: `NOT_READY`

## Review Posture

Adversarial, evidence-based. Source facts checked:

- `docs/reviews/docling-reference-bundle-producer-determinism-evidence-controller-judgment-20260617.md`
- `docs/reviews/docling-reference-bundle-producer-determinism-evidence-20260617.md`
- `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-controller-judgment-20260617.md`
- `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json`
- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`
- `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json`

## Finding 1 - Fingerprint Comparability Protocol When Prior Matrix Lacks Fingerprint

Severity: advisory (not a material blocker)

The plan's comparability rules (section "Comparability Rules", step 6) require `bundle_content_fingerprint` comparison before any closure-count delta interpretation. However, the prior `13/4` matrix (`reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`, schema `docling_reference_bundle_enrichment_residual_closure_reevidence.v1`) was produced before producer diagnostics existed and contains no `bundle_content_fingerprint` field.

The plan's first-principles section (line 68-69) correctly identifies this: *"The accepted producer diagnostics create the missing comparability instrument, but only prospectively. They do not retroactively attach fingerprints to old real-artifact matrices."* The plan also blocks `13/4` vs `10/7` interpretation by design.

However, the comparability rules section does not explicitly specify the evidence worker's protocol when the prior matrix lacks a fingerprint. Two defensible outcomes exist:

1. Fingerprint comparison is inapplicable when the prior has no fingerprint; the evidence worker produces a self-contained new matrix with full diagnostics, and the `13/4` vs `10/7` comparison remains blocked.
2. Missing prior fingerprint forces `BLOCKED_NON_COMPARABLE_NOT_READY`.

Both outcomes are safe. The plan's structure makes outcome (1) the natural reading, but explicit specification would remove ambiguity for the evidence worker.

Impact: low. The plan's stop conditions, verdict taxonomy, and non-claims already prevent any unauthorized interpretation. The evidence worker would safely default to `BLOCKED_NON_COMPARABLE_NOT_READY` or produce a self-contained matrix. This finding is advisory, not a blocker.

## Finding 2 - Repository Reload / Fresh Source / Live Access Authorization Check

Severity: no finding

The plan explicitly guards against unauthorized access in three independent locations:

- Non-goals (line 29-30): *"access PDF/cache/source-helper directly"* and *"perform fresh fetch, repository reload, or source acquisition"* are listed as non-goals.
- Stop conditions (line 281): *"PDF/cache/source-helper direct access, fresh fetch, or repository reload would be needed"* is an explicit stop condition.
- No-over-design judgment (line 327): *"live/source access"* is listed as intentionally excluded.

The optional pytest validation (lines 259-262) references `test_docling_source_truth_residual_closure.py`, which uses synthetic no-live in-memory objects per the accepted implementation judgment. This does not authorize live access.

No finding. The plan does not accidentally authorize repository reload, fresh source, live access, direct PDF/cache/helper access, or provider/LLM access in future evidence.

## Finding 3 - Future JSON Schema Concreteness

Severity: no finding

The plan's JSON schema section (lines 139-205) specifies:

- Top-level required fields with exact values for `schema_version`, `gate`, `no_live`, `candidate_only`, `source_truth_status`, `producer_contract_version`.
- `samples[]` items with 21 required fields including `bundle_content_fingerprint`, `cell_count`, `text_span_count`, `table_count`, `section_count`, and all count maps.
- `rows[]` items with 22+ required fields including `row_key`, `current_disposition`, `prior_disposition`, `closure_disposition`, three-layer status fields, `matched_context` sub-object, and `diagnostic_payload`.
- `non_claims` booleans.
- Verdict taxonomy with three exact allowed verdicts, all ending `NOT_READY`.
- Completion report format with exact field order.

The schema is concrete enough for evidence generation without requiring the evidence worker to invent field names, value domains, or structure. Validation commands assert schema, scope, and non-claim invariants.

No finding.

## Finding 4 - Target Seven, Regression Rows, and Fail-closed Locks Coverage

Severity: no finding

Target seven (from `10/7` matrix residuals): `F015`, `S5-F023`, `S5-F032`, `S6-F035`, `S6-F041`, `S6-F049`, `S6-F050`. All seven appear in the plan's input scope table (lines 96-115) and are explicitly listed as target seven (lines 117-125).

Regression rows (from `comparability_matrix.json` `regression_rows`): `F015` (S1), `S5-F023` (S5), `S6-F035` (S6). All three are explicitly listed (lines 127-131) and are subsets of the target seven.

Verified against source `comparability_matrix.json`:
- `S1::F015::sales_service_fee_C_current_year`: `regression_flag=true`, `closure_disposition_changed=true`
- `S5::S5-F023::investment_objective`: `regression_flag=true`, `closure_disposition_changed=true`, `source_status_changed=true`
- `S6::S6-F035::fund_name`: `regression_flag=true`, `closure_disposition_changed=true`

Fail-closed locks (lines 133-137):
- `S6-F041`: benchmark - fail-closed unless benchmark semantic context proven. Verified: accepted implementation controller judgment confirms S6-F041 remains fail-closed on investment-objective text without benchmark semantic context.
- `S6-F049`: equity aggregate - fail-closed unless row hierarchy proves aggregate semantics. Verified: accepted implementation controller judgment confirms S6-F049 remains fail-closed without proven hierarchy.
- `S6-F050`: stock child row - fail-closed unless parent/child hierarchy proves stock-child semantics. Verified: accepted implementation controller judgment confirms S6-F050 remains fail-closed without proven hierarchy.

All three fail-closed locks appear in the target seven list and have explicit semantic prerequisites in the plan.

No finding.

## Finding 5 - Status/Verdict Wording Ambiguity

Severity: advisory (not a material blocker)

The plan uses `PLAN_NOT_READY` (line 6) and `RESIDUAL_CLOSURE_REEVIDENCE_PLAN_NOT_READY` (line 8). These are plan-level status tokens, not product/release readiness tokens. The plan also carries `Release/readiness: NOT_READY` (line 7).

If this plan review produces `PLAN_REVIEW_PASS_NOT_READY`, the semantic state is: *"the plan is accepted for handoff to the evidence worker; the product/release remains NOT_READY."* The `_NOT_READY` suffix on both `PASS` and `NOT_READY` tokens could create brief confusion about what is "passing" and what is "not ready."

However, the plan consistently pairs every status with explicit `NOT_READY` release/readiness markers. The verdict taxonomy explicitly states: *"No PASS/READY verdict is allowed in this gate"* (line 231). The future evidence verdicts all end `_NOT_READY`. The completion report format separates verdict from `Release/readiness: NOT_READY` (lines 312-313).

Impact: low. The consistent contextual pairing prevents material ambiguity. A reader who encounters `PLAN_REVIEW_PASS_NOT_READY` can distinguish plan acceptance from product readiness by the explicit `Release/readiness: NOT_READY` marker. This finding is advisory.

## Overall Assessment

The plan is well-structured and evidence-based. It correctly identifies that the `13/4` vs `10/7` closure-count delta is blocked evidence, defines a concrete future evidence gate with exact write set, input scope, JSON schema, comparability rules, verdict taxonomy, and stop conditions. It preserves `candidate_only=true`, `source_truth_status=not_proven`, and `NOT_READY` throughout.

The two advisory findings (fingerprint comparability protocol when prior lacks fingerprint; status/verdict token disambiguation) do not block plan acceptance. The plan's structure, stop conditions, and verdict taxonomy provide sufficient guardrails even without explicit specification of these edge cases.

## Verdict

PLAN_REVIEW_PASS_NOT_READY

Release/readiness: NOT_READY

VERDICT: `PLAN_REVIEW_PASS_NOT_READY`
