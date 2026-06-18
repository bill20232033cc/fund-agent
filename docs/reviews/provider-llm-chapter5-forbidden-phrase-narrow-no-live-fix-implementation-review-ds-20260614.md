# Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Review (DS)

Date: 2026-06-14

Role: AgentDS independent implementation reviewer only, not controller and not implementation worker.

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Gate`

Accepted plan:

- `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-20260614.md`
- `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-controller-judgment-20260614.md`

Implementation evidence:

- `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-implementation-evidence-20260614.md`

Release/readiness: `NOT_READY`

## 1. Review Method

Read all required context (`AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, accepted plan, controller judgment, implementation evidence). Read full git diffs for the three target files. Ran allowed verification commands independently:

- `git diff --check`: passed (no output)
- `git status --short`: confirmed only `fund_agent/fund/chapter_writer.py`, `tests/fund/test_chapter_writer.py`, `tests/agent/test_runner.py` modified; unrelated dirty files present but untouched
- Focused pytest (3 new tests): **3 passed in 0.87s**
- `uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/agent/test_runner.py`: **All checks passed!**

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/golden/readiness/release commands were run. No source, test, runtime, control doc, design doc or startup packet was modified.

## 2. Review Question 1: Does the implementation match the accepted plan and binding controller judgment?

**Verdict: YES.**

Plan Section 4 requires:

| Plan requirement | Implementation | Match? |
|---|---|---|
| Add private helper `_ch5_forbidden_phrase_repair_guidance_prompt(chapter, repair_context) -> str` | `chapter_writer.py:1325` — function defined with exact signature | Yes |
| Activation guard: return empty unless `chapter.chapter_id == 5` and `repair_context is not None` | `if chapter.chapter_id != 5 or repair_context is None: return ""` | Yes |
| Required semantics: delete trading-action advice, position actions, return prediction, target-price, manager-motive speculation | Rules 1-4 in returned string cover all five categories | Yes |
| Allow only `值得持有 / 需要关注 / 建议替换` boundary vocabulary | Rule 2 explicitly enumerates the three terms and forbids buy/sell/position language | Yes |
| Data gaps → `数据不足` or `下一步最小验证问题`, not action instructions | Rule 3 constrains data gaps to these two forms | Yes |
| Sentence-level self-check | Rule 4 requires sentence-level self-check before output | Yes |
| Append after `_ch2_l1_repair_guidance_prompt(...)` in `_chapter_prompt_fragments()` | `chapter_writer.py:742` — appended on next line after `_ch2_l1_repair_guidance_prompt(...)` | Yes |

Controller judgment binding amendments:

| Amendment | Implementation | Match? |
|---|---|---|
| DS F1: runner test uses `_FakeWriter()` / `_FakeAuditor(...)`; verify fixture existence | `test_runner.py` test uses `_FakeWriter()` and `_FakeAuditor(("这不是合法行协议", "PASS|chapter|no issues"))` — these are existing fixtures in `tests/agent/test_runner.py` | Yes |
| DS F2: prompt guidance is probabilistic; LLM may still violate | Informational only; no implementation change required | N/A |

The prompt text in the implementation matches the plan's suggested exact text character-by-character. The four rules are rendered identically to the plan's specification.

## 3. Review Question 2: Is the code change limited to Chapter 5 repair-only forbidden-phrase prompt guidance in Fund writer?

**Verdict: YES.**

The diff touches only `fund_agent/fund/chapter_writer.py`:

1. **One new function** `_ch5_forbidden_phrase_repair_guidance_prompt()` (lines 1325-1351 in the new file): a single-module private helper that returns an empty string when not Chapter 5 repair. Total: ~27 lines including docstring.

2. **One new line** in `_chapter_prompt_fragments()` (line 742): appends the helper output as a fragment in the repair-context assembly, after the existing `_ch2_l1_repair_guidance_prompt(...)` call.

No other function, class, constant, import or module-level statement was changed. The change is strictly additive and guarded by `chapter.chapter_id != 5 or repair_context is None`.

No changes to:
- `_repair_context_prompt()` — confirmed unchanged in diff
- `_FORBIDDEN_PHRASES` — confirmed unchanged in diff
- `fund_agent/agent/repair.py` — not in diff
- `fund_agent/agent/runner.py` — not in diff (test only)
- `fund_agent/services/chapter_orchestrator.py` — not in diff
- Any provider/runtime/config/source file — not in diff

## 4. Review Question 3: Did it preserve _repair_context_prompt(), _FORBIDDEN_PHRASES, runner retry behavior, Service diagnostics, default repair budget, source policy and NOT_READY?

**Verdict: YES, all preserved.**

| Preserved item | Evidence |
|---|---|
| `_repair_context_prompt()` | Not present in any diff hunk; function body unchanged |
| `_FORBIDDEN_PHRASES` | Not present in any diff hunk; function and constant unchanged |
| Runner retry behavior | `fund_agent/agent/runner.py` source not in diff; no new writer-block retry path added; no `max_content_repair_attempts` change |
| Service diagnostics | `fund_agent/services/chapter_orchestrator.py` not in diff; no diagnostic schema or category mapping change |
| Default repair budget | No change to `max_repair_attempts=1`; plan and controller judgment explicitly forbid budget changes |
| Source policy | No change to EID single-source policy, fallback behavior, or source acquisition |
| `NOT_READY` | Evidence artifact explicitly states `release/readiness: NOT_READY`; no readiness/release claim made |

The new helper is additive and does not modify or remove any existing function, constant, or behavior. It injects a prompt fragment only when the guard condition is met; otherwise it returns empty string and adds nothing to the prompt assembly.

## 5. Review Question 4: Are tests sufficient and do they actually prove prompt rendering, absence outside scope, runner propagation and no hidden retry?

**Verdict: YES, tests are sufficient.**

### Test 1: `test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt`

- Builds Chapter 5 writer input with `ChapterRepairContext` having `previous_issue_ids=("llm:parse_failure",)` — mirrors the accepted blocker path
- Asserts all required prompt content: `第5章 forbidden phrase repair 必须改写规则`, `交易动作建议`, `仓位动作`, `收益预测`, `基金经理动机推断`, `值得持有 / 需要关注 / 建议替换`, `下一步最小验证问题`
- Asserts `extra_payload` remains absent from `ChapterLLMRequest.__dataclass_fields__`

**Proves**: prompt rendering for Chapter 5 repair attempt; no extra_payload leakage.

### Test 2: `test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair`

- Tests three negative cases:
  - Chapter 5 initial attempt (no repair context): guidance absent
  - Chapter 1 repair attempt (with repair context): guidance absent
  - Chapter 6 repair attempt (with repair context): guidance absent

**Proves**: no leakage to non-Chapter 5 contexts or initial (non-repair) Chapter 5 attempts. Covers both the chapter-id guard and the repair-context guard independently.

### Test 3: `test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance`

- Uses `_FakeWriter()` to record `ChapterLLMRequest` objects
- Uses `_FakeAuditor(("这不是合法行协议", "PASS|chapter|no issues"))` to trigger first-attempt parse failure then second-attempt pass
- Uses `_projection((5,))` and `AgentRepairPolicy(max_content_repair_attempts=1)`
- Asserts:
  - `run.status == "accepted"` — runner completes without exception
  - `[request.chapter_id for request in writer.requests] == [5, 5]` — exactly two writer calls, no hidden third
  - First request has `repair_context is None`
  - Second request has `repair_context is not None` with `"llm:parse_failure"` in `previous_issue_ids`
  - Second request `user_prompt` contains the guidance and boundary vocabulary

**Proves**: end-to-end runner propagation of repair context into writer, guidance rendering on the repair attempt, no hidden retry beyond the declared budget.

### Existing regression tests

The 11 existing tests listed in the plan remain untouched and continue to guard:
- Writer forbidden-phrase validation (`test_writer_rejects_forbidden_trading_advice`)
- Repair context rendering (`test_repair_context_is_rendered_into_writer_prompt_without_extra_payload`)
- Chapter 2 L1 repair guidance isolation (`test_ch2_l1_repair_context_renders_local_anchor_placement_checklist`, `test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context`)
- Repair budget exhaustion (`test_repair_budget_exhausted_stops_without_hidden_retry`, `test_repair_budget_exhausted_records_each_regenerate_attempt`)
- Chapter 6 invalid-anchor retry behavior (`test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry`)
- Service diagnostic classification (`test_writer_forbidden_phrase_subcategory_remains_blocked`, `test_programmatic_forbidden_phrase_is_counted_not_accepted`, `test_audit_parse_failure_records_audit_parse_diagnostic`)

The implementation evidence reports all 14 tests (3 new + 11 existing) pass. Independent verification of the 3 new tests confirms they pass.

## 6. Review Question 5: Are there blockers before controller acceptance?

**Verdict: NO BLOCKERS.**

All five review questions return affirmative answers:

1. Implementation matches accepted plan and binding controller judgment character-by-character.
2. Code change is strictly limited to Chapter 5 repair-only forbidden-phrase prompt guidance in `chapter_writer.py`.
3. All required invariants (`_repair_context_prompt()`, `_FORBIDDEN_PHRASES`, runner retry, Service diagnostics, repair budget, source policy, `NOT_READY`) are preserved.
4. Three new targeted tests plus 11 existing regression tests prove prompt rendering, absence outside scope, runner propagation, and no hidden retry.
5. All allowed verification commands pass independently:
   - `git diff --check`: passed
   - `uv run pytest -q` (3 new tests): 3 passed in 0.87s
   - `uv run ruff check`: All checks passed!

No scope expansion, no forbidden changes, no test gaps that could mask a regression.

## 7. Residuals Carried Forward

| Residual | Status |
|---|---|
| Live/provider behavior after prompt guidance remains unproven | Deferred to bounded live re-evidence gate |
| H1 raw prompt-body absence remains unproven | Informational; does not block this implementation |
| Diagnostic lineage clarification remains deferred | Separate no-live gate only if post-fix evidence requires it |
| Repair budget calibration remains unstarted | Separate standard gate |
| Broader forbidden-phrase repair guidance outside Chapter 5 remains deferred | Only if another chapter-specific blocker proves need |
| Release/readiness remains `NOT_READY` | Preserved |

## 8. Final Verdict

```text
PASS
```

The implementation is correct, narrow, well-tested, and matches the accepted plan and binding controller judgment exactly. No blockers. Ready for controller acceptance.
