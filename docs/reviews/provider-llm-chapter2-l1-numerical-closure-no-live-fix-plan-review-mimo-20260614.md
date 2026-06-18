# Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Plan Review (MiMo)

Date: 2026-06-14

Reviewer role: AgentMiMo plan reviewer, not controller.

## 1. Scope

Review target: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-plan-20260614.md`

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Planning Gate`.

This review evaluates whether the plan is a valid, code-generation-ready planning artifact that stays within the accepted H3 root-cause scope and respects all hard boundaries. This review does not implement the fix, modify source/tests/control/design/README, stage/commit/push/open PR, or run live/provider/network/source/PDF/readiness/release commands.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-controller-judgment-20260614.md`
- Target plan: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-plan-20260614.md`
- Code verification via Explore agent against `fund_agent/fund/chapter_writer.py`, `fund_agent/services/chapter_orchestrator.py`, `fund_agent/agent/repair.py`, `fund_agent/fund/chapter_auditor.py`, `fund_agent/agent/contracts.py`, `fund_agent/agent/runner.py`, and four test files

## 3. Findings (severity ordered)

### F1 [Informational] — Plan correctly preserves planning-only boundary and NOT_READY

The plan explicitly states: "This plan does not implement the fix, change source code, change tests, update control/design/README files, run live/provider/network/source/PDF/readiness/release/PR commands, stage, commit, push or open a PR." Final verdict is `READY_FOR_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY`. Section 1 out-of-scope list and section 6 disallowed write targets align with gate constraints. `NOT_READY` is preserved.

### F2 [Informational] — Plan correctly uses accepted H3 as sole root cause

Section 3 restates H3 with accurate runtime metadata: `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`, attempt 0 `patch` mapped to regenerate, attempt 1 repeated L1, budget exhausted. H1/H2 are rejected with correct rationale (required_output_missing_count=0, L1 contract/auditor alignment). H4/H5 correctly classified as residual/diagnostic gap, not the runtime cause. This matches the accepted controller judgment at `d7c2c79`.

### F3 [Informational] — Plan preserves L1 contract integrity

Section 4 explicitly states: "L1 remains a blocking programmatic audit rule" and "The fix must not hide L1 by moving the failure to a warning, skipping audit, changing failure category, or weakening anchor proximity." The proposed checklist instructs the writer to either place anchors correctly or delete concrete numerical assertions — both paths result in L1-valid output, not L1 bypass.

### F4 [Informational] — Blocked scope boundaries correctly preserved

Section 1 out-of-scope list and section 6 disallowed targets cover: repair budget defaults, provider defaults, source policy, fallback, Docling, annual-period LLM route, readiness/release/PR state, EID single-source/no-fallback. This aligns with the root-cause evidence controller judgment's required constraints for this gate.

### F5 [Informational] — Implementation strategy is code-grounded and narrow

The plan references exact symbols that I verified exist:
- `ChapterRepairContext` at chapter_writer.py:194 with fields `attempt_index`, `previous_issue_ids`, `previous_messages`, `required_corrections`
- `build_chapter_prompt()` at chapter_writer.py:599
- `_chapter_prompt_fragments()` at chapter_writer.py:660
- `_ch2_numerical_closure_contract_prompt()` at chapter_writer.py:1238
- `_repair_context_prompt()` at chapter_writer.py:1398
- `_repair_context_from_audit()` at chapter_orchestrator.py:1928
- `_required_correction_from_issue()` at chapter_orchestrator.py:1978 and repair.py:260

The auditor's L1 proximity check at chapter_auditor.py:1284 uses a +/-2 line window (`lines[max(0, index-2) : min(len(lines), index+3)]`), which matches the checklist's "same sentence or within two surrounding lines" wording. The checklist is grounded in the auditor's actual behavior.

The patch-to-regenerate mapping is confirmed at repair.py:126-129 and chapter_orchestrator.py:1893-1896: `"MVP 暂无 typed patch API，将 patch/regenerate 映射为预算内整章重写。"` The plan correctly avoids introducing a typed patch API.

### F6 [Low] — Conditional write set for orchestrator/repair needs tighter test-evidence gate

Section 6 allows `chapter_orchestrator.py` and `repair.py` writes "only if aligning the existing L1 `required_corrections` text is necessary" and "only if `chapter_orchestrator.py` L1 correction text is changed." The plan's section 7 test 4 says: "If Service/Agent L1 correction text is changed, add or update tests."

**Risk**: The condition "only if tests prove inconsistency" is vague about what evidence constitutes proof. The duplicate `_required_correction_from_issue()` implementations (chapter_orchestrator.py:2008 and repair.py:289) could diverge silently. The plan should specify: what specific test assertion proves or disproves inconsistency, so the implementation worker does not over-interpret the condition.

**Severity**: Low. The plan does scope the conditional write narrowly, and the implementation gate's red-test-first requirement provides additional guardrail. This is not a blocker but should be noted.

### F7 [Informational] — Test plan is no-live, relevant and sufficient

The test plan covers:
- Positive test: Ch2 writer prompt with L1 repair context renders checklist (section 7.1)
- Negative/leakage tests: checklist absent for initial attempt, non-Ch2, non-L1 issues (section 7.2)
- Orchestrator integration: second writer request contains checklist, L1 accepted/rejected paths preserved (section 7.3)
- Conditional Service/Agent alignment tests (section 7.4)

Validation commands (section 8) are all no-live/local: focused pytest with `-k` filters, ruff check, `git diff --check`. No live/provider/network/PDF/readiness/release commands. Existing L1 auditor and repair-budget-exhausted tests are required to pass unchanged as regression.

### F8 [Informational] — Risks and residuals correctly identified

Section 9 correctly identifies: live provider may not obey improved prompt (residual), H4/H5 remain diagnostic residuals, repair budget remains uncalibrated. The plan does not treat any of these as resolved, and correctly routes them to future gates.

### F9 [Informational] — Rejected alternatives are appropriate

Section 5 rejected alternatives: increase repair budget (separate gate), weaken L1 (dilutes contract), typed patch API (too broad), H4/H5 diagnostics in main fix (not required for H3). All rejections are consistent with gate constraints.

## 4. Finding Disposition Recommendation

| Finding | Disposition | Rationale |
|---|---|---|
| F1 planning-only / NOT_READY | ACCEPT | Explicit scope boundary and verdict text preserve gate constraints |
| F2 H3 as sole root cause | ACCEPT | Restatement matches accepted root-cause evidence controller judgment |
| F3 L1 contract preserved | ACCEPT | Checklist strengthens repair instruction without weakening L1 |
| F4 Blocked scope boundaries | ACCEPT | Out-of-scope and disallowed write sets align with gate constraints |
| F5 Code-grounded implementation | ACCEPT | All referenced symbols verified; auditor proximity check matches checklist |
| F6 Conditional write set ambiguity | ACCEPT_WITH_NOTE | Low severity; implementation gate's red-test-first mitigates, but condition could be tightened |
| F7 Test plan sufficient | ACCEPT | Red-test-first, no-live validation, regression preservation |
| F8 Risks correctly identified | ACCEPT | Residuals properly classified and routed to future gates |
| F9 Rejected alternatives appropriate | ACCEPT | Consistent with gate constraints and accepted root cause |

## 5. Required Amendments

None. All findings are acceptable for a planning artifact. F6 is noted as a low-severity observation that the implementation gate's red-test-first requirement already mitigates.

## 6. Final Verdict

VERDICT: PASS
