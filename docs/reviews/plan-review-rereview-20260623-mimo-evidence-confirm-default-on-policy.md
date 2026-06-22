# Evidence Confirm Default-on Policy Plan — MiMo Re-Review

## Reviewed Target

- Fixed plan artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`
- Prior review artifact: `docs/reviews/plan-review-20260623-mimo-evidence-confirm-default-on-policy.md`
- Prior review timestamp: `20260623-030748`
- Re-review timestamp: `20260623-031531`
- Scope: targeted re-review of MiMo findings F001 and F002 only.

## Re-Review Method

Read the fixed plan artifact end-to-end and compare each MiMo finding's requirement against the updated plan text. No new attack surface evaluation was performed; only F001 and F002 disposition is judged.

## MiMo F001: Pathway Fail + Warn Policy ECQ1 Test

**Prior finding**: Slice EC-DO-3 used conditional wording "Add or keep... if not already covered" for the pathway fail + warn policy ECQ1 regression. The implementation agent could skip adding the test if it interpreted the ECQ2/warn regression at line 262 as sufficient coverage.

**What the fixed plan says now**:

- Slice EC-DO-3 exact changes, line 259: `"Add an explicit pathway regression that policy='warn' and pathway_status='fail' maps to ECQ1/warn, not block."` — unconditional, no "if not already covered" qualifier.
- Tests and validation commands, line 347: `test_quality_gate_integration_maps_pathway_fail_warn_policy_to_ecq1_warn` — explicit test label listed in the quality-gate targeted validation block.
- Plan review fix notes, line 388: `"MiMo F001 fixed: ECQ1 pathway fail under product/default warn is now an explicit required regression, not conditional wording."`

**Assessment**: The conditional loophole is eliminated. The pathway fail + warn policy test is now a mandatory regression with an explicit test label and validation command. The implementation agent cannot skip it.

**F001 status: FIXED.**

## MiMo F002: Runner Exception Under Default Product Warn Mode

**Prior finding**: Slice EC-DO-1 test matrix specified runner pass and runner fail tests but did not include a runner exception test for the new default product mode. The existing exception test at line 707 covers developer override mode only.

**What the fixed plan says now**:

- Slice EC-DO-1 required tests, lines 187-192: `"Add a product-mode analyze test with fake runner raising an exception: assert the exception does not propagate; assert result carries a safe compact Evidence Confirm summary; assert summary policy is warn; assert no raw exception internals, excerpt, PDF path, parser payload or provider payload leaks."` — explicit, detailed assertions.
- Tests and validation commands, line 307: `test_fund_analysis_service_product_analyze_warn_runner_exception_becomes_safe_summary` — explicit test label in the Service targeted validation block.
- Validation command, line 316: the test label is included in the `uv run pytest` command.
- Plan review fix notes, line 389: `"MiMo F002 fixed: product default warn runner-exception safe-summary behavior is now an explicit required service regression."`

**Assessment**: The runner exception behavior under product default `warn` is now an explicit required regression with detailed assertions covering propagation, summary safety, policy value, and payload leakage. The implementation agent has no ambiguity about whether to add this test.

**F002 status: FIXED.**

## Reviewer Self-Check

- [x] Reviewed target and scope are written above.
- [x] Only F001 and F002 were evaluated; no new findings generated.
- [x] Assessment is evidence-based, citing exact plan line numbers and text.
- [x] Output path uses system clock timestamp `20260623-031531` and matches `plan-review-rereview-[0-9]{8}-[0-9]{6}.md`.

## Verdict

**PLAN_REREVIEW_PASS**

Both MiMo F001 and F002 are fixed. The plan's fix notes accurately describe the changes, and the updated plan text unconditionally mandates the ECQ1 pathway fail + warn regression (F001) and the product default warn runner exception regression (F002) with explicit test labels, detailed assertions, and validation commands.
