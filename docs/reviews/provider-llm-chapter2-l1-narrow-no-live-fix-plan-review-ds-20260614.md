# Provider/LLM Chapter 2 L1 Narrow No-live Fix Plan Review (DS)

Date: 2026-06-14
Role: AgentDS
Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Planning Gate`
Review target: `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-20260614.md`

## Scope

Independent adversarial plan review. Verify the plan is code-generation-ready and narrow, preserves L1 fail-closed semantics and repair budget defaults, has correct write set, sufficient tests, and no blockers or overbroad scope.

No implementation. No live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands.

## Evidence Reviewed

| Artifact | Use |
|---|---|
| `AGENTS.md` | Execution rule truth source; fail-closed semantics, module boundaries |
| `docs/current-startup-packet.md` | Current gate state, accepted diagnostic facts, DS residual |
| `docs/implementation-control.md` | Control truth; binding controller judgment amendments |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-20260614.md` | Plan under review |
| `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Controller binding requirements for this planning gate |
| `fund_agent/fund/chapter_writer.py` | Current implementation of `_ch2_numerical_closure_contract_prompt()`, `_ch2_l1_repair_guidance_prompt()`, `_has_l1_numerical_closure_repair_issue()`, `_repair_context_prompt()` |
| `tests/fund/test_chapter_writer.py` | Current writer prompt and repair context tests |
| `tests/services/test_chapter_orchestrator.py` (L1 portions) | Current L1 orchestration tests: `test_l1_repair_context_guides_anchored_correction_and_accepts_after_repair`, `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory` |
| `tests/fund/test_chapter_auditor.py` | Current L1 auditor tests: unanchored fails, nearby anchor passes, formula-framework-only passes, source-section unanchored fails |

No writer Markdown, auditor feedback Markdown, repair Markdown, raw prompts, provider payloads, source/PDF/cache body, or final report body was read.

## Findings

### F1 — `_repair_context_prompt()` "minor wording" escape hatch is ambiguous (severity: medium)

Plan step 4 states:

> Keep `_repair_context_prompt()` unchanged except if minor wording is strictly needed to avoid duplicated/contradictory repair instructions; no behavior or schema change.

The stop conditions require the implementation worker to halt if any fix broadens scope. But "minor wording" is not further bounded — the implementation worker could reasonably interpret it as permission to rewrite `_repair_context_prompt()` in ways that unintentionally alter repair behavior for non-Chapter-2 chapters.

Code verification: `_repair_context_prompt()` (line 1456-1479 in `chapter_writer.py`) renders a generic repair context used by all chapters 1-6. It does not currently duplicate or contradict Chapter 2 L1 repair instructions — the L1 repair guidance is separately injected by `_ch2_l1_repair_guidance_prompt()` and guarded by `_has_l1_numerical_closure_repair_issue()`. The plan's own bounded diff result proves `1b9cd00` did not alter `chapter_writer.py`, so no known contradiction exists between `_repair_context_prompt()` and the strengthened L1 repair guidance.

**Recommendation**: Either remove the "except if minor wording" clause entirely (keep `_repair_context_prompt()` truly unchanged), or specify exactly what contradiction would justify a change and limit the change to a one-line reference to the L1 repair contract. Binding amendment.

### F2 — No full-suite regression validation in plan (severity: low)

The validation commands are all focused (`-k` selectors targeting L1-related tests). The plan does not specify running the full test suite (`pytest` without `-k`) to verify the prompt changes do not break non-Chapter-2 writer tests, non-L1 orchestrator tests, or non-L1 auditor tests.

Code verification: The existing test files have broad coverage beyond L1:
- `test_chapter_writer.py`: 28 test functions, including compact payload, required output, bond risk, forbidden phrases
- `test_chapter_orchestrator.py`: large file with extensive orchestration tests
- `test_chapter_auditor.py`: 40+ test functions covering C1, C2, P2, E1, typed contracts

The focused validation commands cover the direct change surface, but prompt text changes in `_ch2_numerical_closure_contract_prompt()` affect all Chapter 2 writer prompts (not just L1 repair), so non-L1 Chapter 2 tests should also be verified.

**Recommendation**: Add a full-suite run (`uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_auditor.py`) after the focused commands in the validation section. Non-blocking; can be addressed by implementation worker.

### F3 — `test_required_corrections_are_deterministic_for_known_issue_patterns` update is under-specified (severity: low)

Plan step for `tests/services/test_chapter_orchestrator.py` states:

> Update `test_required_corrections_are_deterministic_for_known_issue_patterns` only if wording in Service-derived correction assertions must align with the strengthened writer contract. Do not broaden Service behavior.

The plan does not specify what wording change might be needed, or provide a decision rule for whether to update or skip. The implementation worker must read the test to determine if the Service-derived correction assertions reference the old checklist text. If the test asserts specific prompt text from the old contract, it could fail after the prompt strengthening.

**Recommendation**: The implementation worker should run this test first before making changes to determine if it references old prompt text. If it does, the update should be limited to matching the new stable contract header. Non-blocking.

### F4 — Prompt strengthening may inflate Chapter 2 prompt beyond the compact threshold edge case (severity: low)

The plan adds explicit safe-output contract text to `_ch2_numerical_closure_contract_prompt()` and `_ch2_l1_repair_guidance_prompt()`. The current Chapter 2 initial prompt contract is already 4 lines (lines 1261-1265). The repair checklist is 6 lines (lines 1306-1316). The plan adds a `第2章 L1 数字闭环安全输出契约` block plus a `第2章 L1 repair 必须改写规则` block.

Code verification: The plan's test section requires asserting compact prompt mode still contains the strengthened contract (`test_compact_prompt_payload_preserves_fact_and_anchor_contract` already checks for Chapter 2 L1 text). If the new blocks are kept concise as specified, they should not materially affect compact mode behavior. The existing compact threshold is 1200 chars per fact value, not a total prompt threshold.

**Recommendation**: The implementation worker should verify that compact mode tests pass with the strengthened prompt. Already covered by the plan's test update requirements. Informational only.

### F5 — Plan correctly closes DS F1 bounded-diff residual (severity: informational, positive)

The controller judgment at `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-controller-judgment-20260614.md` required the bounded diff inspection `842362d..1b9cd00 -- fund_agent/fund/chapter_writer.py` as a binding residual.

The plan executes this check and reports exit code 0, no output, confirming `chapter_writer.py` is byte-identical between the two commits. The Chapter 3 required-output policy checkpoint did not alter Chapter 2 repair prompt assembly.

This closes DS F1 from the diagnostic gate. Verified independently against the plan's stated result. No further action needed.

### F6 — Strategy is robust to both root-cause interpretations (severity: informational, positive)

The plan's fix strategy strengthens the prompt contract (covers "checklist wording too weak") while preserving fail-closed tests for ignored/unanchored repair output (covers "checklist ignored"). This dual-coverage approach satisfies the controller judgment requirement that the plan be "robust to both interpretations."

Code verification: The existing `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory` in `test_chapter_orchestrator.py` proves the ignored-output path already fails closed. The plan strengthens the prompt contract while keeping this test updated to assert the new contract appears in the second writer request.

### F7 — Allowed write set matches the change surface (severity: informational, positive)

The four allowed source/test files correspond exactly to where the two prompt functions live and where their tests already exist:
- `chapter_writer.py`: contains `_ch2_numerical_closure_contract_prompt()` and `_ch2_l1_repair_guidance_prompt()`
- `test_chapter_writer.py`: tests prompt assembly for both functions
- `test_chapter_orchestrator.py`: tests repair context propagation to writer
- `test_chapter_auditor.py`: tests L1 auditor behavior (safe gap pass, unanchored fail)

The conditional README writes are properly scoped to staleness only.

### F8 — Stop conditions are comprehensive (severity: informational, positive)

The plan lists 8 stop conditions covering all identified risk vectors: L1 weakening, repair budget changes, scope expansion, live/provider commands, forbidden body reads, control/design doc modification, focused validation failure, and dirty workspace conflicts.

The one gap (noted in F2) is that the focused validation commands may miss regressions outside the L1 surface. If a non-L1 test fails due to prompt text changes, the stop condition "focused validation fails" would not catch it. This is partially mitigated by the implementation worker being instructed to stop if any fix broadens scope.

## Residuals

| Residual | Status | Handling |
|---|---|---|
| F1: `_repair_context_prompt()` ambiguity | Open | Add explicit bound or remove the escape clause. Binding amendment recommended before implementation. |
| F2: Full-suite regression validation | Open | Add full-suite run to validation commands. Non-blocking. |
| F3: `test_required_corrections_are_deterministic` update | Open | Implementation worker to check if test references old prompt text. Non-blocking. |
| F4: Prompt inflation edge case | Informational | Already covered by compact mode test requirement. |
| DS F1 bounded-diff residual | Closed | Plan confirms 842362d..1b9cd00 diff is empty for chapter_writer.py. |
| Live model behavior (checklist ignored vs weak) | Unproven | Plan correctly treats as unprovable without live evidence; robust to both. |
| Repair budget calibration | Deferred | Separate gate, correctly excluded. |
| Chapter 5 forbidden phrase | Deferred | Separate gate, correctly excluded. |
| Release/readiness | `NOT_READY` | Correctly preserved. |

## Verdict

**PASS_WITH_FINDINGS**

The plan is code-generation-ready, narrow, preserves L1 fail-closed semantics and repair budget defaults, has a correct and sufficient write set, and includes adequate tests and stop conditions. F1 (ambiguous `_repair_context_prompt()` wording) should be tightened before the implementation gate proceeds, ideally by removing the "except if minor wording" escape clause entirely. F2 and F3 are non-blocking and can be addressed by the implementation worker.

The plan satisfies all binding controller judgment requirements: repair-context propagation treated as working, L1 not weakened, repair budget unchanged, bounded diff closed, strategy robust to both root-cause interpretations, no implementation, EID single-source/no-fallback and `NOT_READY` preserved.

Next gate: `Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Implementation Gate` — recommended to proceed after F1 is resolved.
