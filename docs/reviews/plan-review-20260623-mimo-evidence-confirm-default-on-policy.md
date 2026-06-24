# Evidence Confirm Default-on Policy Plan Review

## Reviewed Target

- Plan artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`
- Work unit: Evidence Confirm Productionization default-on Evidence Confirm policy.
- Gate: plan review.
- Reviewer: AgentMiMo independent plan reviewer.
- Review timestamp: `20260623-030748`.

## Scope

Adversarial evaluation of:

1. Whether the plan is code-generation-ready.
2. Whether analyze-only default `warn` is justified.
3. Whether checklist `off` is a safe scoped choice.
4. Whether developer override remains bounded.
5. Whether tests prove product default behavior.
6. Whether docs/control sync is sufficient.
7. Whether boundaries remain intact.

## Source Of Truth Consulted

- Design truth: `docs/design.md` (Evidence Confirm sections).
- Control truth: `docs/implementation-control.md`, `docs/current-startup-packet.md`.
- Goal-confirmation: `docs/reviews/evidence-confirm-productionization-release-readiness-goal-confirmation-20260623.md`.
- Requirements audit: `docs/reviews/evidence-confirm-productionization-release-readiness-requirements-audit-20260623.md`.
- Source code: `fund_agent/services/fund_analysis_service.py`, `fund_agent/ui/cli.py`, `fund_agent/fund/evidence_confirm_production.py`, `fund_agent/fund/quality_gate_integration.py`.
- Tests: `tests/services/test_fund_analysis_service.py`, `tests/ui/test_cli.py`, `tests/fund/test_quality_gate_integration.py`.

## Assumptions Tested

| # | Assumption | Verification | Result |
|---|---|---|---|
| 1 | Product-mode `_resolve_analyze_contract()` sets `evidence_confirm_policy="off"` at line 1587. | Read source at line 1587: `evidence_confirm_policy="off"`. | Confirmed. |
| 2 | Developer-mode default is `overrides.evidence_confirm_policy or "off"` at line 1614. | Read source at line 1614. | Confirmed. |
| 3 | `_effective_evidence_confirm_policy()` returns `"off"` for checklist at line 1679-1680. | Read source at lines 1679-1680. | Confirmed. |
| 4 | `_effective_evidence_confirm_policy()` returns resolved policy for analyze at line 1682. | Read source at line 1682. | Confirmed. |
| 5 | `_raise_evidence_confirm_block_if_required()` only blocks when `policy == "block"` and `status == "fail"` at line 1748. | Read source at line 1748. | Confirmed. Under product default `warn`, fail summaries will NOT raise `EvidenceConfirmBlockedError`. |
| 6 | `evidence_confirm_runner` defaults to `run_repository_bounded_evidence_confirm` in production at line 726. | Read source at line 726. | Confirmed. Changing default to `warn` will cause the real runner to be called. |
| 7 | Runner exceptions are caught and converted to safe summary at lines 1343-1349. | Read source at lines 1343-1349. | Confirmed. |
| 8 | Existing Service tests assert default analyze/checklist do NOT call runner (lines 577-578, 614-615). | Read test source. | Confirmed. These tests must be updated as plan states. |
| 9 | Existing CLI test asserts default analyze output has no Evidence Confirm lines (line 2873). | Read test source. | Confirmed. This test must be updated as plan states. |
| 10 | Quality gate integration has pathway fail + block policy test but NOT pathway fail + warn policy test. | Searched `test_quality_gate_integration.py`. `test_quality_gate_integration_maps_pathway_fail_to_ecq1_block` exists at line 465; no warn-policy variant exists. | Confirmed gap. Plan correctly identifies this in Slice EC-DO-3 as "Add or keep... if not already covered". |
| 11 | Quality gate integration has ECQ2 deterministic fail + warn policy test at line 262. | Read test source. | Confirmed. |
| 12 | `--evidence-confirm-policy` is behind `--dev-override` in CLI. | Grep confirmed at CLI source. | Confirmed. |
| 13 | Checklist has no Evidence Confirm CLI parameter. | Grep confirmed. | Confirmed. |

## Findings

### 001-未修复-[中]-pathway fail + warn policy ECQ1 test not yet covered in quality gate integration

- **位置**: Slice EC-DO-3, `tests/fund/test_quality_gate_integration.py`
- **问题类型**: 测试缺口
- **当前写法**: Plan says "Add or keep an explicit regression that `policy='warn', status='fail', deterministic_status='fail'` maps to `ECQ2/warn` and gate status `warn`. Add or keep pathway fail with `policy='warn'` mapping to `ECQ1/warn` if not already covered."
- **反例/失败场景**: If implementation agent adds only the ECQ2/warn regression (which already exists at line 262) and skips the pathway fail test (which does NOT exist), the ECQ1/warn mapping code path through `_ecq_policy_severity()` remains untested for the new default policy. A regression in `_ecq_policy_severity()` could silently change pathway fail severity from `warn` to `block` or `info` without detection.
- **为什么有问题**: The quality gate integration code at line 224 calls `_ecq_policy_severity(summary)` to determine ECQ1 severity. The `_ecq_policy_severity()` function (line 291) returns `block` for `policy == "block"` and `warn` otherwise. If this logic breaks, the product default `warn` pathway fail would project incorrectly. No existing test covers this path.
- **直接证据**: `test_quality_gate_integration.py` has `test_quality_gate_integration_maps_pathway_fail_to_ecq1_block` (line 465) but no warn-policy variant. `quality_gate_integration.py` line 224: `severity=_ecq_policy_severity(summary)`.
- **影响**: Implementation agent may skip adding the pathway fail warn test, leaving a quality gate mapping regression undetected.
- **建议改法和验证点**: Make the pathway fail + warn policy test explicit in Slice EC-DO-3's required test list. Test should assert: `policy="warn"`, `pathway_status="fail"` maps to `ECQ1` with severity `warn` (not `block`).
- **修复风险（低/中/高）**: 低 — plan already lists it with "if not already covered" qualifier; implementation agent just needs to confirm it's not covered and add it.
- **严重程度（低/中/高/严重）**: 中 — the test gap is real but the underlying code is simple and unlikely to regress if touched carefully.

### 002-未修复-[低]-runner exception under default product warn mode not explicitly tested

- **位置**: Slice EC-DO-1 required tests, `tests/services/test_fund_analysis_service.py`
- **问题类型**: 测试缺口
- **当前写法**: Plan specifies two product-mode tests: (1) runner returns pass, (2) runner fail with quality gate off or warn. Neither explicitly tests runner exception behavior under default product mode.
- **反例/失败场景**: When the production Evidence Confirm runner throws an exception (e.g., repository unavailable, timeout), the exception is caught at lines 1343-1349 and converted to a safe summary. The existing `test_fund_analysis_service_evidence_confirm_runner_exception_becomes_safe_summary` (line 707) covers this for developer override mode but not for the new default product mode. If the default mode change introduces a code path that bypasses the exception handler, the product `analyze` command would crash instead of degrading gracefully.
- **为什么有问题**: The exception handling code is in `_run_evidence_confirm_if_enabled()` which is shared across all modes. The risk is low because the code path is the same, but the plan's test matrix should explicitly cover this for completeness given this is a default-on behavioral change.
- **直接证据**: `_run_evidence_confirm_if_enabled()` at lines 1343-1349 catches all exceptions. Existing test at line 707 uses developer override mode.
- **影响**: Low — the exception handler is shared code, but an explicit product-mode test would catch any future refactoring that separates the paths.
- **建议改法和验证点**: Add a product-mode test with fake runner raising an exception, asserting safe summary is returned and no exception propagates to the caller. This can be added to Slice EC-DO-1.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

None. All plan assumptions verified against code facts.

## Residual Risks

| Risk | Classification | Destination |
|---|---|---|
| Multi-fund live source/PDF coverage remains unproven | Deferred evidence gate | Separate multi-sample live source/PDF evidence gate after this work unit. |
| Provider-backed semantic quality remains unproven | Deferred evidence gate | Separate provider-backed semantic quality evidence gate after this work unit. |
| Checklist Evidence Confirm CLI support remains absent | Separate blocker | Checklist CLI/support gate after this work unit. |
| Report-body Evidence Confirm rendering remains unauthorized | Product decision gate | Report rendering policy gate if required for release scope. |
| PR-40 mark-ready, merge and release transition remain unauthorized | External state gate | Mark-ready / merge / release gate after all blockers close. |
| `warn` may surface EC fail summaries to product users without blocking | Intentional behavior | Acceptable for first default-on step; `block` requires later evidence gates. |

## Reviewer Self-Check

- [x] Reviewed target, scope, source of truth and assumptions tested are written above.
- [x] Findings are evidence-based, adversarial, executable, and free of style/nit/speculation.
- [x] Open questions, residual risks and tracking destination are separated from findings.
- [x] Conclusion is one of `pass`, `pass-with-risks`, or `fail`.
- [x] Output path uses system clock timestamp `20260623-030748` and matches `plan-review-[0-9]{8}-[0-9]{6}.md`.

## Conclusion

**PLAN_REVIEW_PASS_WITH_FINDINGS**

The plan is code-generation-ready and structurally sound. It correctly identifies the minimum viable change (product `analyze` default `warn`), preserves all existing boundaries (checklist off, no product opt-out, developer override bounded behind `--dev-override`), specifies exact file-level changes and stop conditions, and aligns with design/control truth. The two findings are non-blocking: one medium (pathway fail + warn policy ECQ1 test gap, explicitly listed in the plan but not yet covered) and one low (runner exception under default product mode). Neither finding indicates a structural risk that would cause the plan to fail during implementation.

The plan's conservative approach — changing only one state-machine edge (`evidence_confirm_policy="off"` to `"warn"` for product `analyze`), reusing existing EC-P4 plumbing, and explicitly deferring checklist, provider, rendering, and release transitions — is the correct sequencing for a first default-on release-readiness step.
