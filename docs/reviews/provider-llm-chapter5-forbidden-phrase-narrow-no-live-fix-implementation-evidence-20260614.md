# Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Evidence

Date: 2026-06-14

Role: AgentCodex implementation worker only, not controller and not reviewer.

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Gate`

Accepted plan:

- `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-20260614.md`
- `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-controller-judgment-20260614.md`

Release/readiness: `NOT_READY`

## 1. Scope And Files Changed

Implemented accepted Option 1 only: Chapter 5 repair-only forbidden-phrase prompt guidance.

Changed files:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/agent/test_runner.py`
- `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-implementation-evidence-20260614.md`

README decision:

- `fund_agent/fund/README.md` was inspected for writer / repair / prompt behavior. No update was made because this slice only adds an internal Chapter 5 repair-attempt prompt fragment. It does not change public APIs, deterministic validation, `ChapterRepairContext` shape, retry budget, diagnostics, source policy or user-facing Fund package workflow.

Existing unrelated dirty files were not modified:

- `AGENTS.md`
- `README.md`
- `docs/design.md`
- pre-existing untracked docs/reports/reviews/scripts residue shown by `git status --short`

## 2. Implementation Summary

`fund_agent/fund/chapter_writer.py`:

- Added module-level private helper `_ch5_forbidden_phrase_repair_guidance_prompt(chapter, repair_context) -> str` near the existing Chapter 2 L1 repair guidance helper.
- The helper returns an empty string unless `chapter.chapter_id == 5` and `repair_context is not None`.
- When active, it renders Chapter 5 repair-only guidance requiring sentence-level removal or rewrite of trading-action advice, position-action language, return prediction, target-price language and fund-manager motive speculation.
- The guidance permits only `值得持有 / 需要关注 / 建议替换` boundary wording.
- Data gaps are constrained to `数据不足` or `下一步最小验证问题`, not action instructions.
- `_chapter_prompt_fragments()` appends the helper output after `_ch2_l1_repair_guidance_prompt(...)`.

Tests:

- Added `tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt`.
- Added `tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair`.
- Added `tests/agent/test_runner.py::test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance`.

Unchanged by design:

- `_repair_context_prompt()`
- `_FORBIDDEN_PHRASES`
- Agent runner retry behavior
- Service diagnostics and failure-category mapping
- provider/runtime/config/source policy
- default repair budget

## 3. Tests And Validation

Command:

```text
uv run pytest -q tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair tests/fund/test_chapter_writer.py::test_writer_rejects_forbidden_trading_advice tests/fund/test_chapter_writer.py::test_repair_context_is_rendered_into_writer_prompt_without_extra_payload tests/fund/test_chapter_writer.py::test_ch2_l1_repair_context_renders_local_anchor_placement_checklist tests/fund/test_chapter_writer.py::test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context tests/agent/test_repair_policy.py::test_repair_budget_exhausted_stops_without_hidden_retry tests/agent/test_repair_policy.py::test_repair_context_records_issue_ids_and_sanitized_messages tests/agent/test_runner.py::test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance tests/agent/test_runner.py::test_repair_budget_exhausted_records_each_regenerate_attempt tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry tests/services/test_chapter_orchestrator.py::test_writer_forbidden_phrase_subcategory_remains_blocked tests/services/test_chapter_orchestrator.py::test_programmatic_forbidden_phrase_is_counted_not_accepted tests/services/test_chapter_orchestrator.py::test_audit_parse_failure_records_audit_parse_diagnostic
```

Result:

```text
14 passed in 0.93s
```

Command:

```text
uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/agent/test_runner.py
```

Result:

```text
All checks passed!
```

Command:

```text
git diff --check
```

Result:

```text
passed with no output
```

Command:

```text
git status --short
```

Result summary:

- Current gate modified files: `fund_agent/fund/chapter_writer.py`, `tests/agent/test_runner.py`, `tests/fund/test_chapter_writer.py`.
- Existing unrelated dirty files remain present: `AGENTS.md`, `README.md`, `docs/design.md`, and historical untracked residue under docs/reports/reviews/scripts and Chinese-named local artifacts.
- Evidence artifact is newly added at this path.

## 4. Boundary Compliance

- No live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR command was run.
- No source policy, provider default, repair budget, annual-period LLM route, Docling, fallback, EID policy, diagnostic lineage or retry-path behavior was changed.
- No `_repair_context_prompt()` or `_FORBIDDEN_PHRASES` change was made.
- No Service diagnostics, provider/runtime/config/source files, control docs, design docs, startup packet, staging, commit, push or PR action.
- Release/readiness remains `NOT_READY`.
- Self-check: pass. Work remained inside assigned implementation gate/scope, changed only allowed implementation/test/evidence files, and did not enter review/controller/commit/PR gates.

## 5. Residuals And Next Gate Recommendation

Residuals:

- Live/provider behavior after prompt guidance remains unproven by this no-live implementation gate.
- H1 raw prompt-body absence remains unproven.
- Diagnostic lineage clarification remains deferred and unchanged.
- Repair budget calibration remains unstarted and unchanged.
- Broader forbidden-phrase repair guidance outside Chapter 5 remains deferred.
- Release/readiness remains unproven and `NOT_READY`.

Next gate recommendation:

- Proceed to implementation review for this narrow no-live fix.
- If accepted, a separate bounded live re-evidence gate can test whether the prompt guidance changes provider behavior.
- Any diagnostic-lineage or budget change should remain a separate planned gate.

## 6. Final Verdict

VERDICT: READY_FOR_IMPLEMENTATION_REVIEW_NOT_READY
