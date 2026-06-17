# Docling Reference Bundle Residual Closure Re-evidence Plan Review (DS) - 2026-06-17

Gate: `Docling Reference Bundle Residual Closure Re-evidence Planning Gate`
Role: AgentDS plan reviewer
Target: `docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-20260617.md`
Status: `PLAN_REVIEW_COMPLETE_NOT_READY`
Verdict: `PLAN_REVIEW_PASS_NOT_READY`

## Review Method

Adversarial, evidence-based review. Did not edit the plan. Did not run live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR commands. Verified plan claims against required source facts only.

## Source Facts Checked

- `docs/reviews/docling-reference-bundle-producer-determinism-evidence-controller-judgment-20260617.md` — controller accepted producer determinism evidence; confirmed `PRODUCER_CONTRACT_VERSION`, `bundle_content_fingerprint`, fail-closed locks for S6-F041/S6-F049/S6-F050, and that prior 13/4 and current 10/7 are blocked evidence.
- `docs/reviews/docling-reference-bundle-producer-determinism-evidence-20260617.md` — evidence matrix proves same-input repeat → same fingerprint, reordered cells → same fingerprint, content perturbation → changed fingerprint, companion metadata-only → unchanged fingerprint, blocked generation → null fingerprint.
- `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-controller-judgment-20260617.md` — accepted implementation at commit `8fe0bb4`; 89 tests pass; S6-F041/S6-F049/S6-F050 remain fail-closed.
- `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json` — records regression rows F015/S5-F023/S6-F035, count drift for all 4 samples, section inference drift for all 4 samples; verdict `COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`.
- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json` — 17 rows, 13 closed/4 residual, verdict `RESIDUAL_CLOSURE_REEVIDENCE_PARTIAL_NOT_READY`. No `diagnostic_payload_available` at row level.
- `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json` — 17 rows, 10 closed/7 residual (5 semantic_assignment_residual + 2 source_body_mismatch), delta=-3, regression rows F015/S5-F023/S6-F035; verdict `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`. No `diagnostic_payload_available` at row level.

## Findings

### Finding 1: `force_refresh` Constraint Is Implicit, Not Explicit in Schema (Non-blocking)

The plan's non-goals (line 28-30) forbid fresh fetch and repository reload. The stop conditions (line 280) require the worker to stop if "PDF/cache/source-helper direct access, fresh fetch, or repository reload would be needed." The comparability rules (line 214) compare `repository_source_name`, `source_mode`, `fallback_used`, `metadata_ok`, and `metadata_reason`.

However, neither the future JSON schema nor the validation assertions explicitly require `force_refresh=false` in the sample-level or repository-load diagnostics. The prior accepted matrices all record `force_refresh=false`, but a future evidence worker could set `force_refresh=true` and still produce validator-passing JSON — the metadata comparison might not catch this because the same cached source would likely return identical metadata.

Severity: Low. The non-goals and stop conditions are jointly sufficient to communicate intent. The plan is not required to be a strict JSON schema specification; it is a planning gate output. The future evidence gate's own stop conditions would catch any fresh-fetch attempt.

Recommendation: If the controller wants belt-and-suspenders, add `force_refresh: false` as a required field in the `samples[]` schema, or add a JSON assertion that `force_refresh` is `false` across all samples. Not a gate condition for this planning review.

### Finding 2: Diagnostic Payload Sub-schema References Implementation, Not Specification (Non-blocking)

The plan's row diagnostic payload schema (lines 201-204) names three payload types:
- `selected_reference_match`
- `candidate_search_no_source_match`
- semantic residual diagnostics with considered match diagnostics and rejection categories

These names reference the implemented helper payloads rather than spelling out their exact JSON shape. The plan claims to be "code-generation-ready for an evidence worker without requiring them to invent scope, schema" (line 19).

Cross-check: the accepted implementation (commit `8fe0bb4`) already defines these payload structures in `source_truth_residual_closure.py`. The evidence worker can read the helper code to discover the exact fields. This is acceptable for a planning gate — the plan correctly delegates structural detail to the already-accepted implementation.

Severity: Low. The plan references implemented payloads that exist in accepted code. An evidence worker can introspect them. No ambiguity about what to emit.

### Finding 3: Count Map Sub-structures Are Named Without Value Type Specification (Observation)

The sample-level schema names `table_family_counts`, `section_inference_counts`, `section_inference_reason_counts`, `row_hierarchy_role_counts`, and `text_semantic_context_counts` (lines 176-180) but does not specify whether these are `{string: integer}` maps or arrays of objects.

Cross-check: the existing comparability diagnostic matrix and enrichment matrix already use `{string: integer}` maps for these fields (e.g., `section_inference_counts: {"unknown": 58, "§10": 2, ...}`). The pattern is established and self-documenting in prior artifacts.

Severity: Observation only. No change needed.

## Required Five-Question Assessment

### Q1: Does the plan fully prevent interpreting 13/4 vs 10/7 unless fingerprint/count/source metadata/row identity comparability passes?

**PASS.** The plan's comparability rules (lines 206-221) impose 8 mandatory ordered checks. The first decision in the future evidence gate is comparability, not delta interpretation. Rule 8 explicitly requires row-level matched diagnostic payloads for target seven and regression rows. If any drift exists, verdict must be `BLOCKED_NON_COMPARABLE_NOT_READY` and the evidence must not describe helper improvement or regression. The stop conditions reinforce this with 9 distinct halt triggers (lines 276-286).

Cross-check against accepted controller judgment: the controller explicitly requires "fingerprint/count comparability checks before closure-count interpretation" (line 77). The plan satisfies this requirement directly.

### Q2: Does it accidentally authorize repository reload/fresh source/live/direct PDF/cache/helper access in future evidence?

**PASS (with Finding 1 caveat).** The plan's non-goals (lines 24-31) explicitly forbid: live/network/provider/LLM commands, PDF/cache/source-helper direct access, fresh fetch, repository reload, source acquisition. The stop conditions (lines 278-286) require the worker to halt if any of these would be needed.

The optional validation commands (lines 260-262) reference `uv run pytest` and `uv run ruff` on the existing helper, with the explicit caveat: "Optional validation is only for future evidence worker confidence if they need to prove the existing helper still emits diagnostics. It does not authorize implementation changes." This is properly bounded.

The `force_refresh` constraint is communicated through non-goals and stop conditions rather than schema fields (see Finding 1), but the intent is unambiguous.

### Q3: Is the future JSON schema concrete enough for evidence generation and review?

**PASS (with Finding 2 and Finding 3 observations).** The schema specifies:
- Exact `schema_version` enum (`docling_reference_bundle_residual_closure_reevidence.v1`)
- Exact values for `gate`, `no_live`, `candidate_only`, `source_truth_status`, `producer_contract_version`
- Exact verdict taxonomy with 3 enum values, all ending in `NOT_READY`
- Required fields for top-level, `samples[]`, and `rows[]`
- `matched_context` sub-object with 17 named fields
- Diagnostic payload references to implemented helper payloads

The count map sub-structures and diagnostic payload shapes reference existing artifacts and code rather than re-specifying them inline. This is valid for a planning gate — the implementation already exists and the evidence worker can introspect it.

### Q4: Are target seven, regression rows F015/S5-F023/S6-F035, and fail-closed locks S6-F041/S6-F049/S6-F050 covered?

**PASS.** The plan covers all required rows:

- Target seven: explicitly enumerated at lines 117-124 (F015, F020, S4-F015, S5-F032, S6-F041, S6-F049, S6-F050). Note: the target seven from the `10/7` matrix include F020 and S4-F015 (which remained closed) plus the actual residuals. The plan's target seven list matches the comparability diagnostic's `target_seven_summary` which lists 7 rows.

Actually, cross-checking more carefully: the plan says "target seven are the current blocked/residual rows from the `10/7` matrix" (line 116), then lists F015, S5-F023, S5-F032, S6-F035, S6-F041, S6-F049, S6-F050. But S5-F023 is listed in target seven above (line 119) yet is separately listed as a regression row. Let me verify.

Looking at the 10/7 matrix `target_seven_summary.rows` — it contains F015, F020, S4-F015, S5-F032, S6-F041, S6-F049, S6-F050 (7 rows). The plan's list at lines 117-124 is: F015, S5-F023, S5-F032, S6-F035, S6-F041, S6-F049, S6-F050. This is different from the actual target_seven in the matrix (which includes F020 and S4-F015 instead of S5-F023 and S6-F035).

Wait, let me re-read. The plan says "target seven are the current blocked/residual rows from the `10 / 7` matrix." The 10/7 matrix has 7 residual rows. But looking at the rows[] in the 10/7 matrix, the residuals are: F015 (semantic_assignment_residual), S5-F023 (source_body_mismatch), S5-F032 (semantic_assignment_residual), S6-F035 (semantic_assignment_residual), S6-F041 (source_body_mismatch), S6-F049 (semantic_assignment_residual), S6-F050 (semantic_assignment_residual). That's 7 residuals. The `target_seven_summary` in the 10/7 matrix has different rows (F015, F020, S4-F015, S5-F032, S6-F041, S6-F049, S6-F050) — this is the "target seven" from the prior 13/4 checkpoint.

So there's a terminology collision: the 10/7 matrix has its own `target_seven_summary` which reflects the prior enrichment gate's target seven. The plan defines its own "target seven" as "the current blocked/residual rows from the 10/7 matrix."

The plan's list (F015, S5-F023, S5-F032, S6-F035, S6-F041, S6-F049, S6-F050) correctly identifies all 7 residual rows from the 10/7 matrix. This is internally consistent.

- Regression rows: explicitly listed at lines 127-131 (F015, S5-F023, S6-F035). Cross-check: the comparability diagnostic matrix confirms these three as regression rows. PASS.

- Fail-closed locks: S6-F041, S6-F049, S6-F050 with specific conditions at lines 133-136. Cross-check: the accepted implementation controller judgment confirms these three remain fail-closed. PASS.

- Stop condition lines 282-283 require target seven and regression rows to be explicitly representable. PASS.

### Q5: Does the plan status/verdict wording create ambiguity between plan handoff readiness and product/release NOT_READY?

**PASS.** The plan uses three distinct NOT_READY tokens:
- `Status: PLAN_NOT_READY` — planning gate status; the plan artifact is not a completed/finalized product.
- `Release/readiness: NOT_READY` — standard across all artifacts in the Docling evidence chain; gates release claims.
- `Verdict: RESIDUAL_CLOSURE_REEVIDENCE_PLAN_NOT_READY` — gate-specific verdict; clearly a planning verdict, not an evidence or product verdict.

The verdict taxonomy for the future evidence gate (lines 223-231) uses `COMPARABLE_PARTIAL_NOT_READY`, `BLOCKED_NON_COMPARABLE_NOT_READY`, and `DIAGNOSTIC_MISSING_NOT_READY` — all distinct from the planning verdict. No ambiguity between plan handoff readiness and product NOT_READY.

The success signals (line 20) explicitly state the plan preserves `NOT_READY`. The non-goals (lines 33-41) forbid claiming release readiness.

## Verdict

No material blockers found. The plan correctly derives from accepted evidence facts, specifies a concrete future evidence schema, mandates comparability before delta interpretation, covers all required rows, and preserves NOT_READY throughout.

Findings 1-3 are non-blocking observations. Finding 1 (implicit `force_refresh`) is the strongest but does not prevent the plan from serving as a valid handoff to an evidence worker, since the non-goals and stop conditions jointly communicate the constraint.

VERDICT: `PLAN_REVIEW_PASS_NOT_READY`
