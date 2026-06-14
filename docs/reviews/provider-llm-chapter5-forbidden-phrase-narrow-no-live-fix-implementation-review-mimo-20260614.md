# Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Review — MiMo

Date: 2026-06-14

Role: AgentMiMo independent implementation reviewer. Not controller, not implementation worker.

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Gate`

Release/readiness: `NOT_READY`

Verdict: **PASS**

## 1. Review Scope

Reviewed current workspace diff for:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/agent/test_runner.py`
- `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-implementation-evidence-20260614.md`

Binding context:

- Accepted plan: `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-20260614.md`
- Controller judgment: `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-controller-judgment-20260614.md`

## 2. Review Questions

### Q1: Does the implementation match the accepted plan and binding controller judgment?

**Yes.** The implementation precisely follows the accepted plan's Option 1 and the controller's binding scope:

- Added `_ch5_forbidden_phrase_repair_guidance_prompt(chapter, repair_context) -> str` as a module-level private helper at line 1325, positioned after the existing `_ch2_l1_repair_guidance_prompt` (line 1293), exactly as the plan specified.
- Activation guard: returns empty string unless `chapter.chapter_id == 5 and repair_context is not None`. Matches the plan's "return non-empty guidance only when chapter.chapter_id == 5 and repair_context is not None."
- Appended to `_chapter_prompt_fragments()` at line 742-745, after `_ch2_l1_repair_guidance_prompt(...)`, inside the existing `for fragment in (...) if fragment` comprehension. This matches the plan's instruction to append after the Chapter 2 L1 repair guidance.
- Prompt text is an exact match to the plan's suggested checklist: 4 rules covering deletion of trading-action advice, boundary vocabulary constraint (`值得持有 / 需要关注 / 建议替换`), data-gap rendering (`数据不足` / `下一步最小验证问题`), and sentence-level self-check.

### Q2: Is the code change limited to Chapter 5 repair-only forbidden-phrase prompt guidance in Fund writer?

**Yes.** The `chapter_writer.py` diff is 36 changed lines total: 4 lines added in `_chapter_prompt_fragments()` and 30 lines for the new helper function (including docstring). No other source files in `fund_agent/` were modified. `runner.py` has zero diff.

### Q3: Did it preserve the required invariants?

**Yes.** Verified each:

| Invariant | Status | Evidence |
|---|---|---|
| `_repair_context_prompt()` unchanged | Preserved | No diff at line 1492; generic typed repair context contract intact. |
| `_FORBIDDEN_PHRASES` unchanged | Preserved | No diff at line 97; deterministic writer validation surface intact. |
| Runner retry behavior unchanged | Preserved | `fund_agent/agent/runner.py` has zero diff. `max_content_repair_attempts=1` at runner.py:111 untouched. |
| Service diagnostics unchanged | Preserved | No changes to `fund_agent/services/` files. |
| Default repair budget unchanged | Preserved | `AgentRepairPolicy(max_content_repair_attempts=1)` in runner.py:111 and contracts.py:282 untouched. |
| Source policy / NOT_READY | Preserved | Evidence artifact declares `NOT_READY`; no source/config/readiness changes in diff. |

### Q4: Are tests sufficient and do they actually prove the required behaviors?

**Yes.** Three tests were added, all passing (verified independently):

**Test 1: `test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt`** (test_chapter_writer.py)

- Builds Chapter 5 writer input with `ChapterRepairContext(previous_issue_ids=("llm:parse_failure",))` — mirrors the accepted blocker path.
- Asserts prompt contains: `第5章 forbidden phrase repair 必须改写规则`, `交易动作建议`, `仓位动作`, `收益预测`, `基金经理动机推断`, `值得持有 / 需要关注 / 建议替换`, `下一步最小验证问题`.
- Asserts `extra_payload` not in `ChapterLLMRequest.__dataclass_fields__`.
- Proves: prompt rendering on Chapter 5 repair attempt with correct content.

**Test 2: `test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair`** (test_chapter_writer.py)

- Tests three negative cases: Chapter 5 initial attempt (no repair context), Chapter 1 repair attempt, Chapter 6 repair attempt.
- Asserts `第5章 forbidden phrase repair 必须改写规则` absent from all three prompts.
- Proves: no prompt leakage outside Chapter 5 repair scope.

**Test 3: `test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance`** (test_runner.py)

- Uses existing `_FakeWriter` / `_FakeAuditor` fixtures (already in test_runner.py at lines 34, 69).
- Runs `run_agent_body_chapters` with Chapter 5 target, `max_content_repair_attempts=1`.
- Verifies: run accepted, two writer requests (initial + repair), first has `repair_context is None`, second carries `repair_context` with `"llm:parse_failure"` in `previous_issue_ids`, second prompt contains the forbidden phrase guidance.
- Proves: runner correctly propagates audit repair context into the second Chapter 5 writer request and the guidance is rendered. No hidden third retry (only 2 writer requests total).

### Q5: Are there blockers before controller acceptance?

**No blockers.** Summary:

- `git diff --check`: clean, no whitespace errors.
- `uv run ruff check`: All checks passed.
- `uv run pytest`: 3/3 targeted tests pass.
- Implementation evidence artifact reports 14 tests passing in the broader regression suite including existing forbidden-phrase, repair-context, repair-budget, Chapter 6 retry, and Service diagnostic tests.
- The diff is narrowly scoped: only `chapter_writer.py` source and two test files changed.
- No control docs, design docs, runner, repair, orchestrator, provider, config, or readiness files touched.

## 3. Findings

No blocking findings.

One informational observation: the new helper's docstring references "见模板第 5 章当前阶段" which is a valid cross-reference to the fund analysis template but not a blocking issue — it follows the same documentation pattern as `_ch2_l1_repair_guidance_prompt`.

## 4. Verdict

```text
PASS
```

The implementation faithfully executes the accepted plan within the binding controller scope. All required invariants are preserved. All three required tests pass and correctly prove prompt rendering, scope isolation, and runner propagation. No blockers for controller acceptance.
