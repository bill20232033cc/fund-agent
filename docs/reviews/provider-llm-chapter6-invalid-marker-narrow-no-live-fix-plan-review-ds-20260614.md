# Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Plan — AgentDS Review

Date: 2026-06-14

Role: AgentDS independent plan reviewer.

Gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Planning Gate`

Review target: `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-plan-20260614.md`

Verdict: `ACCEPT_WITH_NONBLOCKING_AMENDMENTS`

Release/readiness: `NOT_READY`

## 1. Review Scope

Review only. No source/test/runtime/control/design modification. No live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands. EID single-source/no-fallback and `NOT_READY` preserved.

Truth/context read:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-20260614.md`

Code inspected (no-live reads only):

- `fund_agent/agent/runner.py` — full file
- `fund_agent/agent/repair.py` — full file
- `fund_agent/fund/chapter_writer.py` — anchor marker regex and contract lines

## 2. Cross-check Summary

Plan claims verified against current code:

| Plan claim | Code evidence | Match? |
|---|---|---|
| `runner.py` returns immediately on `writer_result.status == "blocked"`, before audit/repair | `runner.py:374-394`: blocked branch appends attempt and returns `ChapterTask`; never reaches audit section at line 396+ | Yes |
| `repair.py` builds repair context only from `ChapterAuditResult` | `repair.py:144-168`: `repair_context_from_audit()` takes `ChapterAuditResult` only | Yes |
| Generic anchor correction lacks exact `<!-- anchor:<anchor_id> -->` syntax | `repair.py:297`: `"只使用 allowed anchor marker，删除未知 anchor 或改用 allowed anchor。"` — no exact syntax | Yes |
| Existing loop is `while True` with `continue` for audit repair | `runner.py:325,582`: `while True` loop, `continue` at line 582 for regenerate action | Yes |
| `chapter_id` is `int`, not `str` | `runner.py:280`: `chapter_id: int` | Yes |
| Exact marker contract is `<!-- anchor:<anchor_id> -->` | `chapter_writer.py:68`: `re.compile(r"<!-- anchor:([^<>\s]+) -->")` | Yes |
| Writer stop reason for invalid marker is `llm_contract_violation` | `chapter_writer.py:48`: `ChapterWriteStopReason` includes `"llm_contract_violation"` | Yes |

No code claim in the plan was contradicted by current source.

## 3. Findings

### F1 — Strategy choice is directly supported by accepted evidence (no issue)

D4 proves the exact gap: `invalid_marker` writer block returns before audit/repair, so no repair context exists. D1 proves the initial prompt already renders exact marker syntax and Chapter 6 bond-risk anchor boundary. The plan's decision to add writer-block retry rather than prompt salience follows directly from these facts: D1 says "prompt already has the contract," D4 says "the missing mechanism is retry."

The rejection of prompt-salience-only (Section 4) is well-reasoned: D1 already proves the prompt renders the contract, so duplicating it would not close the D4-proven terminal-writer-block gap.

### F2 — Budget consumption semantics are explicit but one interaction is unexamined (non-blocking)

The plan states retry "consumes existing per-chapter content repair attempt budget" and explicitly rejects budget increase (Section 4). This is honest and preserves the numeric default.

One interaction is not discussed: with `max_content_repair_attempts=1`, a successful writer-block retry increments `attempt_index` to 1. If the retried writer output then fails audit, the audit repair path computes `remaining_budget = 1 - 1 = 0` and will not regenerate. In the current code (no writer-block retry), a writer that passes but then fails audit gets `remaining_budget = 1 - 0 = 1` and can regenerate once. The writer-block retry thus "borrows" the budget that would have been available for audit repair.

This is acceptable because:
- Writer-block and audit-repair are mutually exclusive in the current flow (writer-block never reaches audit).
- The net outcome is strictly better: the chapter gets a second chance at writing rather than none.
- The plan's stated scope is "consuming existing budget," which is truthful.

The implementation gate should document this interaction in a code comment at the retry branch.

### F3 — Tests 3 and 4 are labeled "red tests" but are regression guards (non-blocking)

Section 6 labels all seven tests as "red tests" expected to fail before implementation. Tests 3 (budget 0, one call) and 4 (non-Chapter-6, no retry) describe behavior that current code already exhibits: writer blocks → return after one attempt. These tests will pass green before the fix, serving as regression guards rather than red-test-first proof.

This is a terminology issue, not a plan defect. The implementation gate should still write these tests first and verify they stay green through the change. Test 3 being green-before is actually desirable: it proves budget=0 is already fail-closed and the fix doesn't break it.

### F4 — Write set is appropriately narrow (no issue)

Allowed: `repair.py`, `runner.py`, four test files. Conditional: Service test only if diagnostics change. Not allowed: `chapter_writer.py` (unless proven necessary), provider config, runtime defaults, source/FDR/cache/PDF, README, design/control docs.

The two production files are the correct intervention points: `repair.py` for the helper (repair context is its responsibility) and `runner.py` for the branch (chapter execution loop is its responsibility). The conditional Service test guard is prudent.

### F5 — Implementation steps are code-generation-ready with minor loop-structure clarification (non-blocking)

Steps 1-5 are specific enough for a competent implementer. The eligibility conditions (Chapter 6, `llm_contract_violation`, `writer:invalid_anchor_marker`, budget > 0) are enumerated. The `continue` semantics are correctly identified.

One clarification: step 2 says "continue the existing loop." The existing loop has interruption checks at lines 326-333 that run at the top of every iteration. The implementation must ensure the `continue` jumps to the top of the `while True` block (after interruption check), not to an intermediate point. The current code structure supports this naturally since the interruption check is the first statement inside the loop body. This is an implementation detail, not a planning gap.

### F6 — Chapter 6-only scoping is justified and guarded (no issue)

The plan scopes retry to `chapter_id == 6` only, with test 4 guarding non-Chapter-6 behavior. Rationale: the live blocker is Chapter 6-specific, Chapter 6 has unique bond-risk anchor complexity (internal/组级 anchors), and narrow scope limits blast radius.

If future chapters encounter the same `invalid_marker` issue, they will fail closed as before. This asymmetry is an accepted residual, not a defect. Generalizing to all chapters would be premature without evidence that other chapters share this failure mode.

### F7 — No implicit scope expansion detected (no issue)

The plan explicitly rejects: parser relaxation, budget increase, prompt-body edits, source/fallback/Docling work, annual-period LLM route changes, provider default/runtime changes, and readiness/release/PR claims. Section 1 and Section 9 are consistent. Every rejected alternative in Section 4 has a clear reason tied to accepted evidence.

## 4. Review Question Answers

**Q1: Strategy supported by accepted evidence?** Yes. D4 directly proves the gap (no repair context for writer-block), and D1 proves the prompt already has the contract. The strategy closes the proven gap without duplicating existing prompt content. See F1.

**Q2: Avoids implicit changes to budget/parser/provider/runtime/source/fallback/readiness/PR?** Yes, with one semantic nuance. The plan explicitly preserves all stated boundaries and rejects all listed alternatives. The budget "borrowing" between writer-block retry and audit repair (F2) is an acceptable semantic consequence, not a hidden default change, because the two paths are mutually exclusive. See F2.

**Q3: Write set narrow and sufficient?** Yes. Two production files (`repair.py`, `runner.py`) plus focused tests. The conditional Service test guard prevents unnecessary scope expansion. See F4.

**Q4: Red tests specific and likely to fail before implementation?** Tests 1 and 2 are true red tests that will fail before the fix. Tests 3 and 4 are regression guards (likely green before fix). Tests 5-7 test new behavior. All seven are specific enough with concrete inputs, expected attempt counts, and budget configurations. See F3.

**Q5: Implementation steps code-generation-ready?** Yes. Eligibility conditions, branch behavior, helper inputs/outputs, and verification commands are specified. Minor loop-structure clarification (F5) is an implementation detail. No design work is smuggled into implementation.

**Q6: Blocker around Chapter 6-only vs general path?** No. The narrow scope is risk-appropriate given the evidence is Chapter 6-specific. Test 4 guards non-Chapter-6 behavior. Generalization would be premature without multi-chapter failure evidence. See F6.

## 5. Accepted / Rejected Table

| Item | Disposition | Basis |
|---|---|---|
| Fix strategy: Chapter 6-only writer-block retry consuming existing budget | ACCEPT | D4-proven gap; D1-proven prompt adequacy; F1 |
| Rejection of prompt-salience-only | ACCEPT | D1 proves prompt already has contract; F1 |
| Rejection of parser relaxation | ACCEPT | D2 proves taxonomy works; F7 |
| Rejection of budget increase | ACCEPT | Explicit preservation; F2 |
| Write set boundaries | ACCEPT | Two production files + tests; F4 |
| Red-test-first plan (tests 1-2) | ACCEPT | Will fail before fix |
| Tests 3-4 labeled "red" | ACCEPT_NONBLOCKING | Regression guards, not red tests; F3 |
| Implementation steps | ACCEPT_WITH_CLARIFICATION | Loop continue semantics implicit; F5 |
| Chapter 6-only scope | ACCEPT | Evidence-supported narrow fix; F6 |
| Budget interaction unexamined | ACCEPT_NONBLOCKING | Acceptable mutual exclusion; document in implementation; F2 |
| Direct implementation | REJECT | Plan correctly defers to implementation gate |
| Scope expansion to other chapters | REJECT | No evidence; guard test exists |

## 6. Non-blocking Amendments

1. **Test labeling (F3)**: Label tests 3 and 4 as "regression guards" rather than "red tests" in the implementation gate. They should still be written first, but the expectation is green-before-green-after, not red-before-green.

2. **Budget interaction documentation (F2)**: The implementation should add a one-line comment at the writer-block retry branch noting that a successful retry consumes the budget that would otherwise be available for audit repair, and that this is acceptable because the two paths are mutually exclusive.

3. **Loop structure note (F5)**: The implementation should verify that `continue` in the new branch lands at the top of `while True` (after the interruption check at line 326), not at an intermediate point. Current code structure supports this naturally.

None of these amendments change the plan's strategy, scope, or verification matrix. They are implementation-gate clarifications.

## 7. Final Verdict

`VERDICT: ACCEPT_WITH_NONBLOCKING_AMENDMENTS`

The plan is evidence-based, appropriately narrow, and code-generation-ready. The strategy closes the D4-proven gap without duplicating prompt content or relaxing the marker contract. All scope boundaries are explicit. The three non-blocking amendments are clarifications for the implementation gate, not plan defects.

Next gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Gate`
