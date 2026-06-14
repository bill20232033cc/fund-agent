# Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Plan Review — AgentDS

Date: 2026-06-14

Role: AgentDS independent plan reviewer. Not controller, not implementation worker.

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Planning Gate`

Review target: `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-20260614.md`

Verdict: `PASS_WITH_FINDINGS`

Release/readiness: `NOT_READY`

## 1. Review Questions

### Q1: Does the plan use the accepted diagnostic evidence without overreading runtime metadata, provider behavior, source policy or readiness?

**Pass.** The plan's Section 2 correctly reproduces the accepted controller judgment facts:

- attempt 0 drafted, reached auditor, regenerate repair handling (`ACCEPT`)
- attempt 1 stopped at writer forbidden-phrase validation (`ACCEPT`)
- provider attempt count is `0` (`ACCEPT` — plan does not classify provider behavior)
- writer/auditor forbidden-phrase guards are deterministic (`ACCEPT`)
- repair correction mapping lacks forbidden-phrase-specific branch (`ACCEPT_WITH_INFERENCE_BOUNDARY`)
- default repair budget remains `max_repair_attempts=1` (`ACCEPT_CURRENT_BEHAVIOR`)

The plan's root-cause statement (Section 3 item 4) references `llm:parse_failure` as "the preceding issue" — this aligns with the controller's accepted inference boundary for H3 (code-path inference from `audit_parse`, not a direct persisted attempt scalar). The DS F1 finding from the diagnostic evidence review (overread of `issue_ids`) is correctly respected.

H1 remains properly deferred as partial. Provider behavior is not classified because provider attempt count is `0`. Source policy, readiness, and `NOT_READY` are explicitly preserved throughout.

**Finding: none.**

### Q2: Is choosing only forbidden-phrase-specific repair prompt guidance justified over diagnostic lineage changes for this implementation slice?

**Pass.** The plan's Section 1 justification is sound:

> "The diagnostic lineage mismatch is accepted as layering, but it does not directly cause the forbidden phrase to be generated or accepted."

The same-source root cause (Section 3) traces a concrete chain: audit repair context lacks forbidden-phrase-specific correction → generic repair context feeds attempt 1 writer → writer generates forbidden phrase → writer validation blocks → budget exhausted. Diagnostic lineage layering (attempt 0 chapter-level `audit_parse` vs attempt 1 prompt-diagnostic `forbidden_phrase`) is a reporting concern, not a causal link in this chain.

The controller judgment for the diagnostic evidence gate recommended combining both only "if the plan proves both are necessary." This plan proves diagnostic lineage is not necessary for the current fix slice by demonstrating that the causal gap is in repair guidance content, not in how failure categories are reported.

Diagnostic lineage normalization is correctly deferred to Section 7 (Residuals And Deferred Gates) with a separate owner and gate.

**Finding: none.**

### Q3: Are proposed source changes narrowly scoped and consistent with Service/Host/Agent/Fund boundaries?

**Pass.** The plan limits changes to a single file:

- `fund_agent/fund/chapter_writer.py` — add one private module-level helper, append one line to fragment assembly

And explicitly does not touch:
- `fund_agent/agent/repair.py` — repair correction mapping unchanged
- `fund_agent/agent/runner.py` — retry behavior unchanged
- `fund_agent/services/chapter_orchestrator.py` — diagnostics unchanged

The proposed `_ch5_forbidden_phrase_repair_guidance_prompt()` follows the exact pattern of the existing `_ch2_l1_repair_guidance_prompt()` (same type signature `(chapter: ChapterFactInput, repair_context: ChapterRepairContext | None) -> str`, same early-return guard pattern, same `"\n".join(...)` checklist return). Verified at `chapter_writer.py:1289-1318`.

The append location in `_chapter_prompt_fragments()` (line 737-744) is clean: the new call goes after `_ch2_l1_repair_guidance_prompt(...)` inside the same `"\n".join(...)` tuple. No structural change to the fragment assembly.

Boundary consistency: the writer prompt assembly in `chapter_writer.py` is in `fund_agent/fund` (Fund layer). Per AGENTS.md, Fund owns domain rules and audit/evidence rules. The existing Ch2 L1 repair guidance already lives here, so the new Ch5 guidance follows established boundary practice. No Service/Host/Agent boundary violation.

The plan correctly keeps `_repair_context_prompt()` unchanged (Section 4.5) and `_FORBIDDEN_PHRASES` unchanged (Section 4.6). This preserves the generic repair context contract and the deterministic validation surface.

**Finding: none.**

### Q4: Are tests sufficient to prove prompt rendering, runner propagation, no hidden retry, and no budget/default changes?

**Pass with one informational finding.** Three new tests are specified:

| Test | What it proves |
|---|---|
| `test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt` | Prompt rendering: guidance text appears in `user_prompt` when Ch5 + repair context; `extra_payload` absent |
| `test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair` | Negative cases: guidance absent for Ch5 initial attempt, Ch1 repair, Ch6 repair; existing Ch2 L1 behavior unaltered |
| `test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance` | E2E runner propagation: audit parse failure → repair → writer called twice → second call has repair context with `llm:parse_failure` → prompt contains guidance → no third writer call |

The eleven existing tests listed in Section 5 prove:
- Writer validation still rejects forbidden phrases (deterministic guard unchanged)
- Repair budget exhaustion stops without hidden retry
- Chapter 6 invalid-anchor is the only special writer-block retry path
- Service diagnostics still classify forbidden phrase correctly
- Repair context contract unchanged (no extra payload)

No budget/default changes: the plan explicitly prohibits touching `max_repair_attempts`, and existing budget-exhaustion tests remain in the suite.

**Finding F1 (informational):** The runner test spec references `_FakeWriter()` and `_FakeAuditor(("这不是合法行协议", "PASS|chapter|no issues"))`. Implementation should verify these test fixtures exist or are straightforward to construct from existing test patterns before writing the test. This is a pre-implementation verification step, not a plan defect.

### Q5: Are there blockers before implementation?

**No blockers.** The plan is code-generation-ready:
- Exact source locations specified with line numbers
- Function signature, guard condition, and prompt text are fully specified
- Append location in fragment assembly is explicit
- Test specifications include concrete assertions, setup, and expected values
- Validation commands are provided
- Non-goals, residuals, and deferred gates are documented

**Finding: none.**

## 2. Additional Review Observations

### O1: Repair guidance is probabilistic — correctly deferred

The plan adds prompt guidance to reduce forbidden-phrase generation probability. Even with specific guidance, an LLM may still violate the policy. This inherent limitation is correctly deferred to Section 7 ("Live/provider behavior after stronger repair guidance remains unproven") with a bounded live re-evidence gate after no-live implementation. No plan change needed.

### O2: Prompt text specificity

The proposed repair guidance text (Section 4.3) directly targets the `_FORBIDDEN_PHRASES` list at `chapter_writer.py:97-110`:

| Forbidden phrase category | Guidance coverage |
|---|---|
| 交易动作建议 (`建议买入`, `建议卖出`, etc.) | "交易动作建议" |
| 仓位动作 (`加仓`, `减仓`, `清仓`, `仓位比例`) | "仓位动作" |
| 收益预测 (`预测收益`, `目标价`) | "收益预测", "目标价" |
| 经理动机推断 (`基金经理动机`) | "基金经理动机推断" |

The guidance also reinforces the allowed boundary vocabulary (`值得持有 / 需要关注 / 建议替换`) from `AGENTS.md:253`. Coverage is complete against the current `_FORBIDDEN_PHRASES` tuple.

### O3: Source line number stability

The plan cites specific line numbers (e.g., `chapter_writer.py:737-742`). These were verified against the current code at commit `c20ab5e` and are accurate. If intervening commits shift line numbers before implementation, the implementation worker should use function names and content anchors, not line numbers, as the authoritative reference.

## 3. Verification

| Check | Result |
|---|---|
| Plan uses accepted diagnostic evidence without overread | Pass |
| Root cause respects inference boundaries (H1 partial, H3 code-path inference) | Pass |
| Option 1 (repair guidance only) justified over diagnostic lineage | Pass |
| Source changes limited to one file | Pass |
| Proposed function follows existing `_ch2_l1_repair_guidance_prompt` pattern | Pass |
| `_repair_context_prompt()` and `_FORBIDDEN_PHRASES` preserved | Pass |
| Repair budget, runner retry, Service diagnostics unchanged | Pass |
| Test coverage: prompt rendering, absence, E2E propagation, no hidden retry | Pass |
| Residuals and deferred gates documented | Pass |
| `NOT_READY` preserved | Pass |
| `git diff --check` | Passed (no output) |
| `git status --short` | Dirty with pre-existing modifications and untracked docs; not used as proof |

## 4. Findings Summary

| ID | Severity | Finding | Recommendation |
|---|---|---|---|
| F1 | Informational | Runner test references `_FakeWriter()` / `_FakeAuditor(...)` — fixture existence not verified | Verify or construct fixtures before implementation; does not block plan acceptance |
| F2 | Informational | Repair guidance is probabilistic; LLM may still violate even with specific guidance | Already deferred to bounded live re-evidence gate in Section 7; no plan change needed |

## 5. Verdict

```text
VERDICT: PASS_WITH_FINDINGS
```

Both findings are informational and non-blocking. The plan is code-generation-ready with narrow scope, correct evidence basis, justified implementation choice, and sufficient test coverage. No blockers before the next gate (`Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Gate`).
