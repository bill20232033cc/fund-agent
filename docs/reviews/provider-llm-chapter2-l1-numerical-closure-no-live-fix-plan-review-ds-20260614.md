# Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Plan — DS Review

Date: 2026-06-14

Role: AgentDS plan reviewer, not controller, not implementation worker.

## 1. Scope

Review target: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-plan-20260614.md`

Current gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Planning Gate`

This review assesses the plan against the eight review focus areas specified in the gate. It does not modify source/tests/control/design/README, stage/commit/push/open PR, or run live commands.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-no-live-fix-plan-20260614.md`

## 3. Findings

### F1 — Step 1 detection logic contains "optionally" ambiguity (severity: LOW)

Plan §5 step 1 specifies the `_has_l1_numerical_closure_repair_issue()` helper should return true:

> - true when any `previous_issue_ids` entry starts with `programmatic:L1`;
> - optionally true when a sanitized previous message contains the accepted L1 numerical-closure wording;

The word "optionally" introduces implementation ambiguity. If the second clause is intended as a supplementary detection path, it should be mandatory; if it is not intended, it should be removed. The implementation worker and reviewer need a crisp spec—not an "optionally" that could be interpreted either way.

The first clause (`previous_issue_ids` starts with `programmatic:L1`) is already a correct and sufficient detection criterion given the accepted evidence that the L1 issue ID is always present in accepted bounded live and no-live traces. The second clause is only needed if there is a known case where `previous_issue_ids` omits the L1 prefix. If such a case is known, it should be stated and the clause should be mandatory. If not, the clause should be removed.

**Recommendation**: remove the "optionally" clause, or reword to mandatory with rationale. The `previous_issue_ids` prefix check alone is deterministic and sufficient.

### F2 — Step 5 conditional text alignment creates scope uncertainty (severity: LOW)

Plan §5 step 5 says:

> Only if tests prove the current L1 correction text in Service and Agent repair context is inconsistent with the new checklist, update the L1 correction strings in both duplicate mapping locations to keep Service legacy path and Agent path aligned.

The implementation gate's exact scope depends on a test result that hasn't run yet. While the plan correctly lists the affected files as conditional in §6, this creates a fork: the implementation gate may or may not touch `chapter_orchestrator.py` and `repair.py`. The plan would be stronger if it committed to verifying alignment as part of the implementation and reporting the result, rather than making the action fully conditional.

This is not a blocker. The conditional write set in §6 correctly bounds both branches.

### F3 — Checklist "delete" instruction could amplify LLM non-adherence risk (severity: OBSERVATION, not a finding)

The checklist text in §5 step 2 includes:

> delete the concrete numerical closure assertion and write an approved data-gap / minimum-verification sentence without concrete percentages

This is a reasonable L1-preserving instruction: if the LLM cannot anchor a concrete assertion, it should not make it. However, if the LLM misidentifies which anchors are available (a known risk given that H4 facts/anchor availability is an accepted residual), this instruction could cause unnecessary content loss where an anchor actually exists but the LLM fails to locate it.

The plan's risk section (§9) partially acknowledges this: "The fix improves repair instruction quality but cannot guarantee a live provider will obey it." This is sufficient as a plan-level risk note. The implementation gate's no-live tests cannot fully validate LLM adherence to the checklist.

### F4 — Plan correctly preserves all hard boundaries (severity: NONE)

Verified against all eight review areas:

| Area | Status | Evidence |
|---|---|---|
| 1. Planning-only, preserves NOT_READY | PASS | §1 "does not implement", §1/§10/§11 all state `NOT_READY` |
| 2. Correctly uses accepted H3 only | PASS | §3 restates H3, §3 marks H1/H2 rejected, H4/H5 residual |
| 3. Does not weaken L1 | PASS | §1 "Preserve current fail-closed L1 blocker", §4 "L1 remains a blocking programmatic audit rule", §5 rejects weakening alternative |
| 4. Does not change repair budget/provider/default/source/fallback/Docling/annual-period LLM/readiness/release/PR | PASS | §1 out-of-scope, §5 rejected alternatives, §6 disallowed writes all explicitly exclude these |
| 5. Implementation strategy code-generation-ready and narrow | PASS (with F1 and F2 notes) | §5 specifies exact helpers, checklist text, insertion point |
| 6. Allowed write set correct | PASS (with F2 note) | §6 primary writes narrow, conditional writes bounded, forbidden writes exhaustive |
| 7. Tests and validation no-live, relevant, sufficient | PASS | §7 four test categories, §8 only `uv run pytest`/`ruff`/`git diff`, §8 forbidden list correct |
| 8. No missing red-test-first, no overreach | PASS (with F2 note) | §7 "red-test-first", §10 conditions for implementation gate |

### F5 — Plan does not overreach into forbidden territory (severity: NONE)

Verified that the plan does not:
- Claim implementation authority or extend beyond planning
- Modify control/design/README
- Run live/provider/network/source/PDF commands
- Change readiness/release/PR state
- Stage, commit, push, open PR

## 4. Finding Disposition Recommendation

| Finding | Severity | Recommended Disposition |
|---|---|---|
| F1 "optionally" ambiguity in detection logic | LOW | ACCEPT_WITH_AMENDMENT — remove "optionally" clause or reword to mandatory with explicit rationale |
| F2 conditional text alignment creates scope fork | LOW | ACCEPT_AS_NOTED — implementation gate worker should verify alignment and report result regardless of whether edit is needed; plan remains code-generation-ready |
| F3 checklist "delete" / LLM non-adherence risk | OBSERVATION | ACCEPT_AS_OBSERVATION — §9 risk note is sufficient; no plan amendment needed |
| F4 hard boundaries preserved | NONE | ACCEPT — all eight areas pass |
| F5 no forbidden overreach | NONE | ACCEPT — plan stays planning-only |

## 5. Required Amendments

If the controller chooses ACCEPT_WITH_REQUIRED_AMENDMENTS, the following amendment is required:

**A1 (for F1)**: In plan §5 step 1, replace:

> - optionally true when a sanitized previous message contains the accepted L1 numerical-closure wording;

with either:

> *(remove the line entirely — the `previous_issue_ids` prefix check is sufficient)*

or:

> - true when a sanitized previous message contains the accepted L1 numerical-closure wording, as a defense-in-depth check for cases where `previous_issue_ids` may not carry the full `programmatic:L1` prefix;

The second form is preferred only if the plan author knows of a concrete case where `previous_issue_ids` would omit the prefix. Otherwise the first form (removal) is simpler and avoids untestable logic.

Note: F2 (conditional text alignment) does not require a plan amendment. It is an implementation-gate concern that the worker should handle.

## 6. Final Verdict

VERDICT: PASS_WITH_FINDINGS

The plan is code-generation-ready, correctly targets accepted H3, preserves L1 and all hard boundaries, and stays within planning-only scope. F1 is a minor spec ambiguity that the implementation gate can resolve without a plan rewrite. F2 is a scope clarity note for the implementation gate. F3 is an acknowledged risk already covered in the plan's own risk section.
