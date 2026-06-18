# Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Plan Review — AgentMiMo

Date: 2026-06-14

Role: AgentMiMo independent plan reviewer.

Gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Planning Gate`

Review target: `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-plan-20260614.md`

## 1. Truth/context files read

| File | Controller use |
|---|---|
| `AGENTS.md` | Rule truth: standard gate expectations, root-cause discipline, EID single-source/no-fallback and `NOT_READY` preservation. |
| `docs/design.md` | Design truth: Route C `--use-llm` is explicit opt-in and fail-closed; writer marker contract is exact. |
| `docs/current-startup-packet.md` | Current active gate and checkpoint `10d9373`. |
| `docs/implementation-control.md` | Control truth: standard classification, no-live fix planning gate, no implementation/live by default. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Accepted routing basis: D1-D4 proven, D4 gap is `invalid_marker` blocks before repair context. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-20260614.md` | Accepted diagnostic facts D1-D5. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-plan-20260614.md` | Plan artifact under review. |
| `fund_agent/agent/runner.py` | Source truth: current writer-block terminal path (lines 374-394) and existing audit-decided repair loop (lines 554-582). |
| `fund_agent/agent/repair.py` | Source truth: current `repair_context_from_audit()` and `_sanitize_text()` mechanics. |

No writer/auditor/repair markdown bodies, provider payloads, PDF/source/cache bodies or final report bodies were read.

No live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands were run.

## 2. Findings

### F1. Strategy evidence support — PASS

The plan's chosen strategy (Chapter 6-only writer-block retry for `writer:invalid_anchor_marker`, consuming existing repair budget) is directly supported by accepted diagnostic facts:

- D1 proves the initial Chapter 6 prompt already renders the exact `<!-- anchor:<anchor_id> -->` syntax, allowed-anchor boundary, no synthesized IDs and bond-risk internal/组级 anchor prohibition. This supports rejecting "prompt salience only" as insufficient.
- D4 proves the gap: `invalid_marker` writer blocks return immediately in `runner.py:374-394` before reaching `decide_repair()` or `repair_context_from_audit()`. A writer-block retry directly closes this proven gap.
- The decision to consume existing `max_content_repair_attempts=1` budget is consistent with D4 evidence and avoids the rejected alternative of budget increase.

No finding.

### F2. Scope discipline — PASS

The plan avoids:

- Implicit repair-budget default changes: Section 3 explicitly states "Do not introduce new provider/runtime budget knobs" and Section 4 rejects budget increase.
- Parser relaxation: Section 4 rejects parser relaxation; D2 proves strict taxonomy is correct.
- Provider/runtime/source/fallback/readiness/PR changes: Section 1 scope and Section 4 rejected alternatives are explicit.
- Prompt-body markdown edits: Section 9 non-goals exclude this.

The only behavioral change is a narrow writer-block retry path scoped to Chapter 6 `invalid_marker`. This is the minimum viable fix for the D4-proven gap.

No finding.

### F3. Allowed write set — PASS with observation

The allowed write set (Section 5) includes:

- `fund_agent/agent/repair.py` — for the new helper
- `fund_agent/agent/runner.py` — for the writer-block retry branch
- `tests/agent/test_repair_policy.py` — for helper tests
- `tests/agent/test_runner.py` — for runner retry tests
- `tests/services/test_chapter_orchestrator.py` — for orchestration-level tests
- `tests/fund/test_chapter_writer.py` — for repair-context renderer tests

**Observation (non-blocking)**: The plan does not mention whether `runner.py` needs a new import for the helper function from `repair.py`. The existing `runner.py:24` imports `repair_context_from_audit` from `fund_agent.agent.repair`, so adding `repair_context_from_writer_invalid_marker` to the same import line is trivial. The implementation gate can handle this without plan amendment.

The conditional write for `tests/services/test_fund_analysis_service_llm.py` is appropriately gated: "only if the implementation changes Service-level incomplete-run or final-assembly diagnostics."

The exclusion of `fund_agent/fund/chapter_writer.py` is correct with a sensible escape hatch: "unless implementation proves the existing repair-context renderer cannot render the exact correction text from `ChapterRepairContext`." The current `_required_correction_from_issue()` in `repair.py:296` already maps anchor issues to `"只使用 allowed anchor marker，删除未知 anchor 或改用 allowed anchor。"`, and the new helper can produce equivalent or more specific correction text through the same `ChapterRepairContext.required_corrections` field. The `chapter_writer.py` renderer likely does not need changes.

No finding.

### F4. Red-test-first specificity — PASS

Section 6 defines 7 red-test-first cases. Verifying specificity and likely-to-fail-before-implementation:

1. **Chapter 6 first invalid then valid retry** (test_runner.py): With `max_content_repair_attempts=1`, current code returns after one writer-block attempt (verified at `runner.py:374-394`). This test will red-fail because current code never calls writer twice for a writer-block case. Specific and correct.

2. **Chapter 6 repeated invalid marker** (test_runner.py): With budget 1, current code returns after one attempt. This test verifies exactly two writer calls and fail-closed (no hidden third). Will red-fail for same reason. Specific and correct.

3. **Budget 0 no retry** (test_runner.py): With `max_content_repair_attempts=0`, current code already fails immediately. This test verifies preservation of current behavior. It should pass before implementation (green test in red-test-first sequence), which is acceptable as a regression guard.

4. **Non-Chapter-6 no retry** (test_runner.py): Current code already does not retry for any chapter. This test should pass before implementation (green test), serving as a scope boundary regression guard.

5. **Helper sanitization** (test_repair_policy.py): New helper does not exist yet, so this test will red-fail with `ImportError` or `AttributeError`. Specific and correct.

6. **Orchestration-level retry** (test_chapter_orchestrator.py): Tests `orchestrate_chapters()` with Chapter 6 invalid-marker flow. Will red-fail because current orchestration does not produce writer-block retry. Specific and correct.

7. **Repair-context renderer** (test_chapter_writer.py): Tests that existing renderer can render exact correction text from `ChapterRepairContext`. This verifies the renderer contract before implementation. Likely passes before (green test), serving as a contract guard.

The mix of red-failing and green-passing tests in a red-test-first sequence is acceptable: tests 3, 4, 7 establish behavioral contracts that must not regress, while tests 1, 2, 5, 6 verify the new behavior does not yet exist.

No finding.

### F5. Implementation steps code-generation readiness — PASS

Section 7 defines 5 implementation steps:

1. **Repair-policy helper** (`repair.py`): Specifies function name, input types (`writer_result`, `attempt_index`), use of existing `_sanitize_text()`, output type (`ChapterRepairContext`), and exact correction text content. Imports are implicit from existing code patterns. Code-generation-ready.

2. **Agent runner branch** (`runner.py`): Specifies exact insertion point (before existing writer-block return at line 374), eligibility conditions (chapter_id==6, status==blocked, stop_reason==llm_contract_violation, issue prefix starts with writer:invalid_anchor_marker, remaining budget > 0), and behavior (append attempt, increment index, rebuild writer_input with repair context, continue loop). Code-generation-ready.

3. **Preserve diagnostics**: Specifies what must not change (`_terminal_from_writer_stop_reason`, `_failure_category_from_writer_result`, parser taxonomy) and what must be visible (attempt ledger with budget consumption). Code-generation-ready.

4. **Update tests**: References the red-test-first sequence from Section 6. Code-generation-ready.

5. **Run verification**: References Section 8 matrix. Code-generation-ready.

No design work is smuggled into implementation. The strategy decision (Section 3) is clearly separated from implementation steps (Section 7).

No finding.

### F6. Chapter 6-only scope vs general invalid_marker path — PASS

The plan explicitly scopes the retry to Chapter 6 only. Test case 4 (non-Chapter-6 invalid-anchor marker must not retry) guards this boundary.

The eligibility conditions in Section 7 step 2 require `chapter_id == 6` as the first check. This is the narrowest possible scope that closes the D4-proven gap for the current live blocker (Chapter 6 `invalid_marker` from `bcbbfd3`).

If future chapters encounter `invalid_marker`, a separate gate can generalize the path. The current Chapter 6-only scope is correct under the "narrow fix" classification. The plan does not create a general `invalid_marker` retry path and then restrict it to Chapter 6; it creates a Chapter 6-specific branch. This avoids premature abstraction.

No finding.

## 3. Verification against review questions

| # | Question | Finding |
|---|---|---|
| Q1 | Strategy supported by evidence? | PASS. D1 supports rejecting prompt-salience-only; D4 supports writer-block retry; budget consumption is consistent. |
| Q2 | Avoids implicit scope changes? | PASS. No repair-budget default, parser relaxation, provider/runtime/source/fallback/readiness/PR changes. |
| Q3 | Allowed write set narrow and sufficient? | PASS. Two production files + four test files; conditional write appropriately gated. |
| Q4 | Red-test-first specific and likely to fail? | PASS. 4 red-failing tests for new behavior, 3 green-passing tests for regression guards. |
| Q5 | Implementation steps code-generation-ready? | PASS. No design work smuggled; strategy and implementation cleanly separated. |
| Q6 | Chapter 6-only vs general path blocker? | PASS. Chapter 6-only scope is narrowest viable; generalization deferred to future gate. |

## 4. Verdict

All six review questions pass. The plan is evidence-supported, scope-disciplined, code-generation-ready, and appropriately narrow. No blocking or non-blocking amendments required.

`VERDICT: ACCEPT`

Stop. Do not stage, commit, push, PR or enter next gate.
