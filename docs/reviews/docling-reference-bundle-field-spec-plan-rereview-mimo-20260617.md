# Docling Reference Bundle Field-spec Plan Re-review — AgentMiMo — 2026-06-17

Gate: `Docling Reference Bundle Field-spec Planning Gate`
Role: re-review worker only, AgentMiMo
Verdict: `PASS`

## Re-review Target

- `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md` (plan after fix)

## Prior Review

- `docs/reviews/docling-reference-bundle-field-spec-plan-review-mimo-20260617.md`
- Prior verdict: `PASS_WITH_FINDINGS`, 5 findings (2 中, 3 低)

## Scope

Verify whether prior findings were resolved by the plan fix. Check no new blocker was introduced. Re-check core boundaries and fail-closed behavior.

## Source Of Truth And Evidence Read

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md`
- `docs/reviews/docling-reference-bundle-field-spec-plan-review-mimo-20260617.md`
- `docs/reviews/docling-semantic-residual-rule-design-controller-judgment-20260617.md`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`

## Findings

No blocking findings.

## Prior Finding Disposition Table

| # | Severity | Description | Disposition | Evidence |
|---|----------|-------------|-------------|----------|
| 01 | 中 | `ResidualClosureRule` serialization/deserialization contract not specified | **RESOLVED** | Plan line 178: "ResidualClosureRule remains a Python-only constant configuration in this gate. This plan does not authorize JSON serialization, JSON deserialization, to_dict(), _coerce_rule(), or config-file loading for rules." Line 382: "ResidualClosureRule has no serialization/coercion contract in this gate because rules remain Python-only constants." The prior ambiguity is eliminated — implementation agent now knows rules are Python-only constants, no serialization needed. |
| 02 | 中 | `_coerce_bundle()` derivation of `enrichment_status` for legacy payloads not specified | **RESOLVED** | Plan line 381: "_coerce_bundle() must set missing or invalid enrichment_status to 'not_enriched'. It must not infer bundle-level 'partially_enriched' or 'enriched' status from cell-level enriched fields; only an explicit upstream bundle construction/enrichment step may set those statuses." Line 427: "Keep missing bundle enrichment_status as 'not_enriched' and do not derive bundle status from cells." The derivation contract is now explicit. |
| 03 | 低 | Table-family classifier same-priority signal conflict resolution not fully specified | **RESOLVED** | Plan lines 210-211 now specify: "When multiple families match at the same priority level, prefer the more specific target-safe family only if its decisive term is explicit in that signal... If same-priority signals remain ambiguous after the specific-family check, set table_family='unknown' and fail closed for target rules." The prior gap is closed with deterministic precedence. |
| 04 | 低 | `_has_share_class_context` replacement path not explicitly described in Slice 2 | **RESOLVED** | Plan line 441: "Replace or wrap the existing _has_share_class_context() column-header-only check with a helper that consumes cell.share_class_context plus allowed_share_class_context_sources. The old helper may be retained only as an internal derivation helper for canonical share-class construction; it must not silently broaden _match_satisfies_rule() by scanning extra raw sources at match time." Implementation path is now explicit. |
| 05 | 低 | Existing test fixture backward-compatibility path not explicitly stated | **RESOLVED** | Plan line 467: "existing _cell() / _bundle() test fixtures remain compatible through dataclass defaults after Slice 1". Line 468: "new tests that need enriched semantics should pass the new fields explicitly by keyword instead of relying on positional constructor order." Backward-compatibility expectation is now stated. |

## Boundary Re-check

| Boundary | Status | Evidence |
|----------|--------|----------|
| NOT_READY | **PASS** | Plan line 3: "HANDOFF_READY_NOT_READY". Line 514: "No code implementation in this planning gate." |
| Candidate-only | **PASS** | Plan line 55: "source_truth_residual_closure.py is a pure candidate helper." |
| Repository-mediated | **PASS** | Plan lines 17-19: "no direct PDF/cache/source-helper access". Line 510: "reference-bundle enrichment would require live acquisition, direct PDF/cache/source-helper access, or non-repository access". |
| No source truth | **PASS** | Plan line 519: "No source-truth acceptance." |
| No baseline promotion | **PASS** | Plan line 520: "No baseline promotion." |
| No parser replacement | **PASS** | Plan line 521: "No parser replacement." |
| No full correctness | **PASS** | Plan line 522: "No full field correctness claim." |
| No readiness/release/PR | **PASS** | Plan lines 523-524: "No release readiness or PR readiness." |

## Fail-closed Behavior Re-check

| Target | Fail-closed rule | Status | Evidence |
|--------|-----------------|--------|----------|
| S6-F041 | Remains RESIDUAL unless benchmark-labeled context proven | **PASS** | Plan line 360: "S6-F041 remains RESIDUAL unless benchmark-labeled context is proven. Do not close it from investment-objective wording, section proximity, text equality, or expected field name." Line 332 in prior review confirms benchmark acceptance predicate requires semantic_context_label=="benchmark" or explicit 业绩比较基准 label. |
| S6-F049 | Remains RESIDUAL unless row hierarchy distinguishes aggregate equity semantics | **PASS** | Plan line 261: "If equity_investment_amount and stock_investment_amount share the same normalized value in the same table, both may close only if their matched references have distinct row_index or distinct proven row_hierarchy_path, and the field-specific hierarchy predicates are fully satisfied." Line 262: "keep S6-F049 and S6-F050 as RESIDUAL." |
| S6-F050 | Remains RESIDUAL unless child stock hierarchy under equity is proven | **PASS** | Plan line 267: row_hierarchy_role=="child" and parent path contains 权益投资 required. Line 261-262: identical values without proven hierarchy keep both RESIDUAL. |
| Value equality | Must not prove hierarchy or closure alone | **PASS** | Plan line 254: "Value equality, expected field name, row order alone, or nearby duplicate text alone must not prove hierarchy." Line 509: "closure would rely on value equality, expected field name, row order alone, or nearby context alone". |

## New Blocker Check

No new blocker introduced. The plan fix addressed all 5 prior findings without altering the boundary constraints, adding implementation scope, or introducing new ambiguity.

## Residual Risks

All residual risks from the prior review remain unchanged and are tracked for the next implementation/evidence gate:

1. Repository parsed tables may not preserve enough merged-cell header hierarchy or parent/child row hierarchy for all samples.
2. F015 may remain residual even after enrichment if multiple semantically equivalent C-share current-period sales service fee rows remain.
3. S6-F049 and S6-F050 identical-value risk if upstream reference bundle cannot prove hierarchy.
4. S6-F041 benchmark-labeled context availability is an implementation-time discovery.
5. Table-family classifier may produce `unknown` for non-standard table layouts; plan correctly fails closed.

These are known upstream limitations, not plan defects.

## Final Verdict

**PASS**

All 5 prior findings are resolved. No new blockers. Core boundaries (NOT_READY, candidate-only, repository-mediated, no source truth, no baseline promotion, no parser replacement, no full correctness, no readiness/release/PR) are preserved. Fail-closed behavior for S6-F041, S6-F049, and S6-F050 is confirmed. The plan is safe to proceed to implementation.

## Self-check

- Re-read prior review findings: done
- Verified each finding resolution against plan text: done (5/5 resolved)
- Re-checked all 8 core boundaries: done (8/8 pass)
- Re-checked fail-closed for S6-F041, S6-F049, S6-F050: done (3/3 pass)
- Checked for new blockers: none found
- Artifact path: `docs/reviews/docling-reference-bundle-field-spec-plan-rereview-mimo-20260617.md`
