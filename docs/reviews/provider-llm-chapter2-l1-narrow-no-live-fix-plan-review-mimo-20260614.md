# Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Plan Review — MiMo

Date: 2026-06-14

Reviewer: AgentMiMo

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Planning Gate`

Review target: `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-20260614.md`

## Scope

Independent adversarial review of the narrow no-live fix plan for Chapter 2 L1 repair-effectiveness failure. The review verifies that the plan is code-generation-ready, preserves L1 fail-closed semantics, has correct write-set boundaries, sufficient test coverage, and no blockers or overbroad scope.

## Evidence Reviewed

| Artifact | Role |
|---|---|
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-20260614.md` | Review target plan. |
| `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Accepted diagnostic evidence and binding planning requirements. |
| `docs/current-startup-packet.md` | Current gate context. |
| `docs/implementation-control.md` | Control truth. |
| `AGENTS.md` | Execution constraints. |
| `fund_agent/fund/chapter_writer.py` | Target implementation file; full read. |
| `tests/fund/test_chapter_writer.py` | Writer test file; full read. |
| `tests/services/test_chapter_orchestrator.py` | Orchestrator test file; focused read on L1-related tests (lines 1516-1565). |
| `tests/fund/test_chapter_auditor.py` | Auditor test file; full read. |

No writer Markdown, auditor feedback Markdown, repair Markdown, raw prompts, provider payloads, source/PDF/cache body or final report body was read.

## Findings

### F1 — Checklist replacement vs. "keep" contradiction (Severity: Minor)

**Location**: Plan step 4 vs. test update section.

**Detail**: Plan step 4 says: "Keep `_repair_context_prompt()` unchanged except if minor wording is strictly needed to avoid duplicated/contradictory repair instructions; no behavior or schema change." However, the test update section for `_ch2_l1_repair_guidance_prompt()` requires:

- Replacing header from `第2章 L1 数字闭环 repair checklist` to `第2章 L1 repair 必须改写规则`
- Replacing all five existing checklist items with four new rewrite rules plus a self-check instruction
- Adding assertions for `删除具体数字闭环断言`, `只有确认 allowed anchor`, `不确定时写数据不足`, `输出前逐行自查`

The current `_ch2_l1_repair_guidance_prompt()` (lines 1286-1316) returns a string starting with `第2章 L1 数字闭环 repair checklist` containing five checklist items. The existing test `test_ch2_l1_repair_context_renders_local_anchor_placement_checklist` (line 1198) asserts those exact strings. If the checklist is replaced, the existing test assertions break. The plan should clarify:

1. Whether the checklist is being replaced or augmented.
2. If replaced, that the existing test assertions for `第2章 L1 数字闭环 repair checklist`, `同一句或上下2行`, `百分比闭合断言` need to be updated or removed.
3. If augmented, that both old and new assertions coexist.

**Note**: The plan's step 4 says "keep `_repair_context_prompt()` unchanged" — this is about `_repair_context_prompt()` (the general repair context function), not `_ch2_l1_repair_guidance_prompt()` (the L1-specific checklist function). But the test update section requires changes to the L1-specific checklist output. The implementation worker may correctly interpret this as "only `_repair_context_prompt()` is kept; `_ch2_l1_repair_guidance_prompt()` is rewritten." The plan should be more explicit to avoid ambiguity.

### F2 — Initial contract header replacement ambiguity (Severity: Minor)

**Location**: Plan step 1 vs. existing code and tests.

**Detail**: Plan step 1 says: "Update `_ch2_numerical_closure_contract_prompt()` to add an explicit `第2章 L1 数字闭环安全输出契约` block." The current code (line 1260) returns a string starting with `第2章 R=A+B-C 数字闭环`. The test `test_writer_prompt_contains_l1_numerical_closure_anchor_rule` (line 486) asserts `第2章 R=A+B-C 数字闭环` is in the prompt. The compact-payload test (line 555) also asserts this string.

The plan says "add" a new block, but the test update section says to assert `第2章 L1 数字闭环安全输出契约` as the "stable header." The plan should clarify:

1. Whether `第2章 R=A+B-C 数字闭环` is preserved alongside the new `第2章 L1 数字闭环安全输出契约`.
2. If replaced, that existing test assertions for the old header (lines 486, 510, 555) need updating.
3. The exact relationship between the old header content and the new safe-output contract content.

### F3 — Compact-payload test not explicitly addressed (Severity: Informational)

**Location**: Plan test section for `test_compact_prompt_payload_preserves_fact_and_anchor_contract`.

**Detail**: The compact-payload test (line 555) asserts `第2章 R=A+B-C 数字闭环` in compact mode. The plan's test section mentions "Keep compact-payload coverage by asserting the strengthened Chapter 2 contract survives compact prompt mode" but does not explicitly list which assertions need updating if the header changes. If F2 results in a header replacement, this test needs a corresponding update.

### F4 — Auditor safe-gap test is correctly identified as new (Severity: Informational — no action needed)

**Location**: Plan test section for `tests/fund/test_chapter_auditor.py`.

**Detail**: The plan correctly identifies that no existing auditor test covers the safe-gap pattern `数据不足，不能完成具体 R=A+B-C 百分比闭环。下一步最小验证问题：...` for Chapter 2. Existing tests cover:

- `test_programmatic_audit_allows_l1_formula_framework_without_concrete_percentage` (line 849): formula framework only, no percentage — passes L1
- `test_programmatic_audit_blocks_l1_missing_wording_with_concrete_unanchored_percentage` (line 828): "数据不足" wrapping a concrete unanchored percentage — still fails L1

The missing case is: safe gap / verification-question wording without any concrete percentage. The plan's proposed test addition fills this gap correctly.

## Positive Observations

1. **Robust dual-interpretation strategy**: The plan correctly covers both "ignored checklist" (fail-closed test) and "weak checklist wording" (strengthened prompt test) without requiring proof of which interpretation is true.

2. **Bounded diff closure**: The plan closes the DS bounded diff residual (`842362d..1b9cd00`) by confirming `chapter_writer.py` was not modified in that range, proving the Chapter 3 required-output policy checkpoint did not alter Chapter 2 repair prompt assembly.

3. **Write-set discipline**: The allowed write set is exactly correct — `chapter_writer.py` plus three test files, with conditional README writes only if stale. No forbidden files are included.

4. **Stop conditions**: All seven stop conditions are well-defined and match the binding planning requirements from the diagnostic evidence controller judgment.

5. **Residual tracking**: All residuals are explicitly carried forward with clear ownership and next-handling instructions.

## Residuals

| Residual | Status | Next handling |
|---|---|---|
| Whether the live model will follow the strengthened prompt | Unproven | Future bounded live evidence gate only |
| F1/F2 checklist/header replacement ambiguity | Should be resolved before implementation | Implementation worker should apply consistent interpretation |
| Repair budget calibration | Deferred | Separate gate |

## Verdict

**PASS_WITH_FINDINGS**

The plan is code-generation-ready and narrow enough. It preserves L1 fail-closed semantics and repair budget defaults. The allowed write set is correct. Tests are sufficient with the caveat that F1 and F2 require the implementation worker to make consistent interpretation choices about checklist/header replacement. There are no blockers or overbroad scope. Stop conditions are well-defined.

The two minor findings (F1, F2) are implementation-detail ambiguities that the implementation worker can resolve consistently — they do not invalidate the plan's strategy, scope, or safety guarantees.
