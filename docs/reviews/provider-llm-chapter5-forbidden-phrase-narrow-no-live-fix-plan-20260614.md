# Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Plan

Date: 2026-06-14

Role: AgentCodex planning worker only, not controller.

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Planning Gate`

Release/readiness: `NOT_READY`

Final verdict: `VERDICT: READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION`

## 1. Scope And Non-goals

### Scope

Write a code-generation-ready no-live implementation plan for the accepted Chapter 5 `forbidden_phrase` blocker after diagnostic evidence checkpoint `c20ab5e`.

Chosen path:

```text
Option 1 only: forbidden-phrase-specific repair prompt guidance.
```

This plan intentionally does not choose diagnostic lineage clarification for the first implementation slice. The same-source evidence shows the blocking behavior happens when attempt 1 enters writer validation with a forbidden phrase after a generic repair attempt. The diagnostic lineage mismatch is accepted as layering, but it does not directly cause the forbidden phrase to be generated or accepted.

### Non-goals

- No source/test/runtime behavior change in this planning gate.
- No live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR command.
- No source policy, provider default, provider budget, chapter repair budget, annual-period LLM route, Docling, fallback, EID policy or readiness-state change.
- No hidden retry and no increase to `max_repair_attempts=1`.
- No diagnostic schema, runtime artifact schema, Service failure-category taxonomy or CLI output contract change in this slice.
- No raw prompt body, provider payload, source body, PDF/cache body or final report body requirement.
- No control doc or design doc update in this worker task.
- Do not treat untracked residue, dirty status or metadata-only artifacts as source truth, content correctness or readiness proof.

## 2. Accepted Evidence Basis

Accepted control basis:

- `docs/current-startup-packet.md` and `docs/implementation-control.md` set the current gate to `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Planning Gate`, require planning only, and preserve `NOT_READY`.
- `docs/reviews/provider-llm-chapter5-forbidden-phrase-no-live-diagnostic-evidence-controller-judgment-20260614.md` accepts:
  - attempt 0 drafted content, reached auditor, then received regenerate repair handling;
  - attempt 1 stopped at writer forbidden-phrase validation before any second audit/repair;
  - provider attempt count for this blocker is `0`;
  - writer and auditor forbidden-phrase guards are deterministic;
  - visible repair correction mapping lacks a forbidden-phrase-specific branch;
  - default repair budget remains `max_repair_attempts=1`;
  - release/readiness remains `NOT_READY`.

Accepted no-live diagnostic basis:

- `docs/reviews/provider-llm-chapter5-forbidden-phrase-no-live-diagnostic-evidence-20260614.md` accepts H2, H3, H4 and H5 with inference boundaries:
  - H2: writer fail-closed validation correctly catches `writer:forbidden_phrase`.
  - H3: repair context lacks forbidden-phrase-specific correction or guidance.
  - H4: `audit_parse` at attempt 0 and writer `forbidden_phrase` at attempt 1 are diagnostic layering, not readiness evidence.
  - H5: current repair budget makes the second-attempt writer block terminal by design.

Current source basis:

- `fund_agent/fund/chapter_writer.py:97-110` defines writer forbidden phrases.
- `fund_agent/fund/chapter_writer.py:617-620` has broad global policy text, but no Chapter 5 repair-attempt-specific guidance.
- `fund_agent/fund/chapter_writer.py:737-742` currently renders generic repair context plus Chapter 2 L1-only guidance.
- `fund_agent/fund/chapter_writer.py:1458-1480` renders previous issue ids/messages/corrections without issue-specific forbidden-phrase guidance.
- `fund_agent/fund/chapter_writer.py:1612-1645` validates writer response before accepting a draft.
- `fund_agent/fund/chapter_writer.py:1939-1960` blocks forbidden phrases as `writer:forbidden_phrase:<index>` / `llm_contract_violation`.
- `fund_agent/agent/repair.py:151-175` builds typed repair context from audit issue ids/messages/corrections.
- `fund_agent/agent/repair.py:277-340` maps known repair corrections but only maps `llm:parse_failure` to auditor line-protocol correction.
- `fund_agent/agent/runner.py:580-607` passes `repair_context_from_audit()` into the next writer attempt.
- `fund_agent/agent/runner.py:379-420` writer-blocks are terminal unless they are the existing narrow Chapter 6 invalid-anchor retry path.
- `fund_agent/services/chapter_orchestrator.py:334-355` keeps default `max_repair_attempts=1`.
- `fund_agent/services/chapter_orchestrator.py:1360-1419` and `1422-1545` already classify writer forbidden phrase and audit parse as separate diagnostic layers.

Existing test basis:

- `tests/fund/test_chapter_writer.py::test_writer_rejects_forbidden_trading_advice`
- `tests/fund/test_chapter_writer.py::test_repair_context_is_rendered_into_writer_prompt_without_extra_payload`
- `tests/fund/test_chapter_writer.py::test_ch2_l1_repair_context_renders_local_anchor_placement_checklist`
- `tests/fund/test_chapter_writer.py::test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context`
- `tests/agent/test_repair_policy.py::test_repair_budget_exhausted_stops_without_hidden_retry`
- `tests/agent/test_repair_policy.py::test_repair_context_records_issue_ids_and_sanitized_messages`
- `tests/agent/test_runner.py::test_repair_budget_exhausted_records_each_regenerate_attempt`
- `tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry`
- `tests/services/test_chapter_orchestrator.py::test_writer_forbidden_phrase_subcategory_remains_blocked`
- `tests/services/test_chapter_orchestrator.py::test_programmatic_forbidden_phrase_is_counted_not_accepted`
- `tests/services/test_chapter_orchestrator.py::test_audit_parse_failure_records_audit_parse_diagnostic`

## 3. Root-cause Statement Using Same-source Logic Only

Same-source root cause:

1. The accepted runtime scalar path for the Chapter 5 blocker is two attempts: attempt 0 drafted and reached audit, then repair regenerated; attempt 1 stopped in writer validation with `writer:forbidden_phrase`.
2. The no-live Agent path shows attempt 0 audit repair builds the next writer input through `repair_context_from_audit()` in `fund_agent/agent/runner.py`.
3. `repair_context_from_audit()` only carries sanitized issue ids/messages and `_required_corrections_from_issues()`.
4. The current correction mapping has no forbidden-phrase-specific repair guidance. When the preceding issue is `llm:parse_failure`, it tells the next writer to fix auditor line protocol, which is not a content-writing constraint.
5. `chapter_writer.py` renders that generic repair context, but only has extra specialized repair prompt guidance for Chapter 2 L1. There is no Chapter 5 repair-attempt guard that tells the writer to remove trading-action advice, position actions, return prediction or manager-motive speculation.
6. Writer validation correctly blocks the forbidden phrase after generation; with the current one-regenerate budget, that second-attempt writer block is terminal.

Therefore the narrow root cause for this fix gate is:

```text
The Chapter 5 repair attempt is allowed to proceed with only generic audit-derived repair context, so a regenerate after an audit-layer failure does not receive a local Chapter 5 forbidden-phrase rewrite checklist before writer validation. The deterministic writer guard catches the violation, but the single repair budget is already consumed.
```

Not root cause for this slice:

- Provider behavior is not classified because accepted evidence has provider attempt count `0`.
- Source/FDR/PDF/golden/readiness state is unrelated to the no-live writer validation path.
- Diagnostic lineage layering explains why metadata can show attempt 0 `audit_parse` and attempt 1 `forbidden_phrase`, but it does not itself create the forbidden phrase.

## 4. Proposed Minimal Code Changes

### Slice A: Chapter 5 repair-only forbidden-phrase prompt guidance

Allowed source file:

- `fund_agent/fund/chapter_writer.py`

Do not change:

- `fund_agent/agent/repair.py`
- `fund_agent/agent/runner.py`
- `fund_agent/services/chapter_orchestrator.py`
- provider/runtime/config/readiness/source code

Implementation instructions:

1. Add a private helper near the existing Chapter 2 L1 repair guidance helpers:

```python
def _ch5_forbidden_phrase_repair_guidance_prompt(
    chapter: ChapterFactInput,
    repair_context: ChapterRepairContext | None,
) -> str:
    """构造第 5 章 forbidden phrase repair 局部改写清单，见模板第 5 章当前阶段与交易建议边界。"""
```

2. The helper must return an empty string unless:

```python
chapter.chapter_id == 5 and repair_context is not None
```

Reason: the accepted blocker is Chapter 5 after a repair attempt. Initial attempts and other chapters already have the global writer policy and deterministic writer validation; expanding further is not needed for this gate.

3. When active, return a short checklist. Required semantics:

- identify this as Chapter 5 repair-only guidance;
- require deleting trading-action advice, position-action language, return prediction, target-price language and fund-manager motive speculation;
- allow only the existing final-judgment boundary vocabulary: `值得持有` / `需要关注` / `建议替换`;
- require missing/uncertain facts to render as `数据不足` or `下一步最小验证问题`, not as an action instruction;
- require a sentence-level self-check before output.

Suggested exact prompt text:

```text
第5章 forbidden phrase repair 必须改写规则：
1. 输出前逐句删除交易动作建议、仓位动作、收益预测、目标价和基金经理动机推断。
2. 只使用“值得持有 / 需要关注 / 建议替换”边界表达；不得写买入、卖出、加仓、减仓、清仓或仓位比例。
3. 事实不足或锚点不足时，只写数据不足或下一步最小验证问题，不用行动指令补足。
4. 输出前逐句自查；命中交易动作、仓位动作、收益预测或经理动机推断的句子必须删除或改写为边界表达。
```

4. Append this helper to `ChapterPromptFragments.repair_context` assembly in `_chapter_prompt_fragments()` after `_ch2_l1_repair_guidance_prompt(...)`:

```python
_ch5_forbidden_phrase_repair_guidance_prompt(chapter, input_data.repair_context),
```

5. Keep `_repair_context_prompt()` unchanged. This preserves the generic typed repair context contract and avoids turning a Chapter 5 content-policy fix into a general repair-context schema change.

6. Keep `_FORBIDDEN_PHRASES` unchanged. This gate strengthens repair guidance only; it does not change the deterministic validation surface.

7. Keep Agent runner retry behavior unchanged. Do not add a writer forbidden-phrase retry path, do not model it after the Chapter 6 invalid-anchor retry, and do not change `max_content_repair_attempts`.

8. Keep Service diagnostics unchanged. Existing `prompt_contract` / `forbidden_phrase` and `audit_parse` diagnostics are accepted layering for now.

## 5. Required Tests

### New tests in `tests/fund/test_chapter_writer.py`

Add:

```python
def test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt() -> None:
```

Required assertions:

- build Chapter 5 writer input with a non-`None` `ChapterRepairContext`, preferably with `previous_issue_ids=("llm:parse_failure",)` to mirror the accepted blocker path;
- `build_chapter_prompt(input_data).user_prompt` contains `第5章 forbidden phrase repair 必须改写规则`;
- prompt contains `交易动作建议`, `仓位动作`, `收益预测`, `基金经理动机推断`;
- prompt contains `值得持有 / 需要关注 / 建议替换`;
- prompt contains `下一步最小验证问题`;
- `extra_payload` remains absent from `ChapterLLMRequest.__dataclass_fields__`.

Add:

```python
def test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair() -> None:
```

Required assertions:

- Chapter 5 initial attempt without repair context does not contain `第5章 forbidden phrase repair 必须改写规则`;
- Chapter 1 or Chapter 6 repair attempt with any repair context does not contain this guidance;
- existing Chapter 2 L1 guidance behavior remains covered by existing tests and must not be altered.

### New test in `tests/agent/test_runner.py`

Add:

```python
def test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance() -> None:
```

Required setup:

- Use `_projection((5,))`.
- Use `_FakeWriter()` so the writer records `ChapterLLMRequest` objects.
- Use `_FakeAuditor(("这不是合法行协议", "PASS|chapter|no issues"))`.
- Use `AgentRunPolicy(target_chapter_ids=(5,), repair_policy=AgentRepairPolicy(max_content_repair_attempts=1))`.

Required assertions:

- run status is `accepted`;
- writer was called exactly twice for chapter 5;
- first writer request has `repair_context is None`;
- second writer request has `repair_context is not None`;
- second writer request `repair_context.previous_issue_ids` includes `llm:parse_failure`;
- second writer request `user_prompt` contains `第5章 forbidden phrase repair 必须改写规则`;
- second writer request `user_prompt` contains `值得持有 / 需要关注 / 建议替换`;
- no third writer request is made.

### Existing tests to keep in the focused suite

- `tests/fund/test_chapter_writer.py::test_writer_rejects_forbidden_trading_advice`
- `tests/fund/test_chapter_writer.py::test_repair_context_is_rendered_into_writer_prompt_without_extra_payload`
- `tests/fund/test_chapter_writer.py::test_ch2_l1_repair_context_renders_local_anchor_placement_checklist`
- `tests/fund/test_chapter_writer.py::test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context`
- `tests/agent/test_repair_policy.py::test_repair_budget_exhausted_stops_without_hidden_retry`
- `tests/agent/test_repair_policy.py::test_repair_context_records_issue_ids_and_sanitized_messages`
- `tests/agent/test_runner.py::test_repair_budget_exhausted_records_each_regenerate_attempt`
- `tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry`
- `tests/services/test_chapter_orchestrator.py::test_writer_forbidden_phrase_subcategory_remains_blocked`
- `tests/services/test_chapter_orchestrator.py::test_programmatic_forbidden_phrase_is_counted_not_accepted`
- `tests/services/test_chapter_orchestrator.py::test_audit_parse_failure_records_audit_parse_diagnostic`

No new Service diagnostic-lineage test is required in this slice because diagnostic lineage is deliberately deferred.

## 6. Validation Commands

Implementation gate should run:

```text
uv run pytest -q \
  tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt \
  tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair \
  tests/fund/test_chapter_writer.py::test_writer_rejects_forbidden_trading_advice \
  tests/fund/test_chapter_writer.py::test_repair_context_is_rendered_into_writer_prompt_without_extra_payload \
  tests/fund/test_chapter_writer.py::test_ch2_l1_repair_context_renders_local_anchor_placement_checklist \
  tests/fund/test_chapter_writer.py::test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context \
  tests/agent/test_repair_policy.py::test_repair_budget_exhausted_stops_without_hidden_retry \
  tests/agent/test_repair_policy.py::test_repair_context_records_issue_ids_and_sanitized_messages \
  tests/agent/test_runner.py::test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance \
  tests/agent/test_runner.py::test_repair_budget_exhausted_records_each_regenerate_attempt \
  tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry \
  tests/services/test_chapter_orchestrator.py::test_writer_forbidden_phrase_subcategory_remains_blocked \
  tests/services/test_chapter_orchestrator.py::test_programmatic_forbidden_phrase_is_counted_not_accepted \
  tests/services/test_chapter_orchestrator.py::test_audit_parse_failure_records_audit_parse_diagnostic
```

Then run:

```text
uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/agent/test_runner.py
git diff --check
git status --short
```

Do not run live/provider/source/PDF/FDR/analyze/checklist/golden/readiness/release commands in the no-live implementation gate.

## 7. Residuals And Deferred Gates

| Residual | Owner | Deferred handling |
|---|---|---|
| Live/provider behavior after stronger repair guidance remains unproven. | Controller / evidence owner | Separate bounded live re-evidence gate after accepted no-live implementation. |
| H1 raw prompt-body absence remains unproven. | Prompt/evidence owner | Keep as partial evidence; do not claim complete initial prompt omission. |
| Diagnostic lineage layering remains accepted but unchanged. | Service/Agent diagnostics owner | Defer unless post-fix evidence still needs terminal lineage clarification. Any future fix must be a separate no-live diagnostic gate. |
| Repair budget calibration remains unstarted. | Service/Agent chapter orchestration owner | Separate standard gate; do not change `max_repair_attempts=1` here. |
| Broader forbidden-phrase behavior across other chapters remains guarded by existing global policy and deterministic validation only. | Fund writer owner | Defer broader repair prompt expansion unless another chapter-specific blocker proves need. |
| Release/readiness remains unproven. | Release owner | Preserve `NOT_READY`; no readiness/release claim from this plan or its implementation. |

## 8. Final Verdict

```text
VERDICT: READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION
```

