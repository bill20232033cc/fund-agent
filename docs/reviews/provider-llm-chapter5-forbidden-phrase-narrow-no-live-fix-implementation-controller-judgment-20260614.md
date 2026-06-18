# Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Gate`

Final verdict: `ACCEPT_IMPLEMENTATION_READY_FOR_BOUNDED_LIVE_RE_EVIDENCE_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the no-live implementation gate for the accepted Chapter 5 `forbidden_phrase` narrow fix plan checkpoint `13e0ca8`.

This gate did not authorize live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands, source-policy changes, provider-default changes, repair-budget changes, annual-period LLM route changes, Docling work, diagnostic lineage changes, retry-path changes, pushing or PR actions.

## 2. Evidence Reviewed

| Evidence | Role |
|---|---|
| `AGENTS.md` | Rule truth: direct evidence, Fund/Agent/Service boundaries, no readiness/source overreach. |
| `docs/current-startup-packet.md` | Current gate truth: Chapter 5 narrow no-live fix implementation and `NOT_READY`. |
| `docs/implementation-control.md` | Control truth: accepted plan checkpoint and implementation boundaries. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-20260614.md` | Accepted implementation plan. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-controller-judgment-20260614.md` | Binding controller plan judgment. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-implementation-evidence-20260614.md` | Implementation evidence. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-implementation-review-ds-20260614.md` | DS independent implementation review, verdict `PASS`. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-implementation-review-mimo-20260614.md` | MiMo independent implementation review, verdict `PASS`. |

## 3. Accepted Implementation

Accepted files:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/agent/test_runner.py`

Accepted behavior:

- Added `_ch5_forbidden_phrase_repair_guidance_prompt(chapter, repair_context) -> str`.
- The helper returns non-empty text only for Chapter 5 repair attempts.
- The guidance tells the writer to remove or rewrite trading-action advice, position actions, return prediction, target-price language and fund-manager motive speculation.
- The guidance restricts final judgment wording to `值得持有 / 需要关注 / 建议替换`.
- Data gaps are routed to `数据不足` or `下一步最小验证问题`.
- `_chapter_prompt_fragments()` appends this helper after existing Chapter 2 L1 repair guidance.

Preserved invariants:

- `_repair_context_prompt()` unchanged.
- `_FORBIDDEN_PHRASES` unchanged.
- Agent runner retry behavior unchanged.
- Service diagnostics and failure-category mapping unchanged.
- Default repair budget unchanged.
- Source policy and EID single-source guardrails unchanged.
- Release/readiness remains `NOT_READY`.

## 4. Validation

Controller re-ran:

```text
uv run pytest -q tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair tests/fund/test_chapter_writer.py::test_writer_rejects_forbidden_trading_advice tests/fund/test_chapter_writer.py::test_repair_context_is_rendered_into_writer_prompt_without_extra_payload tests/fund/test_chapter_writer.py::test_ch2_l1_repair_context_renders_local_anchor_placement_checklist tests/fund/test_chapter_writer.py::test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context tests/agent/test_repair_policy.py::test_repair_budget_exhausted_stops_without_hidden_retry tests/agent/test_repair_policy.py::test_repair_context_records_issue_ids_and_sanitized_messages tests/agent/test_runner.py::test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance tests/agent/test_runner.py::test_repair_budget_exhausted_records_each_regenerate_attempt tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry tests/services/test_chapter_orchestrator.py::test_writer_forbidden_phrase_subcategory_remains_blocked tests/services/test_chapter_orchestrator.py::test_programmatic_forbidden_phrase_is_counted_not_accepted tests/services/test_chapter_orchestrator.py::test_audit_parse_failure_records_audit_parse_diagnostic
```

Result:

```text
14 passed in 0.83s
```

Controller re-ran:

```text
uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/agent/test_runner.py
```

Result:

```text
All checks passed!
```

Controller re-ran:

```text
git diff --check
```

Result: passed with no output.

## 5. Reviewer Findings Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentDS | `PASS` | Accepted. DS independently verified the implementation matches the plan, preserves all invariants, and passes allowed no-live validation. |
| AgentMiMo | `PASS` | Accepted. MiMo independently verified the implementation is narrow, tests prove prompt rendering/scope isolation/runner propagation, and no blockers remain. |

No blocking or non-blocking code-change findings remain open for this gate.

## 6. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Live/provider behavior after prompt guidance remains unproven. | Deferred | Bounded live re-evidence gate. |
| H1 raw prompt-body absence remains unproven. | Accepted residual | Do not claim complete initial prompt omission. |
| Diagnostic lineage clarification remains deferred. | Deferred | Separate no-live gate only if post-fix evidence proves it is needed. |
| Repair budget calibration remains unstarted. | Deferred | Separate standard gate; no default budget change in this gate. |
| Broader forbidden-phrase repair guidance outside Chapter 5 remains deferred. | Deferred | Only if another chapter-specific blocker proves need. |
| Release/readiness remains unproven. | Blocking readiness residual | Preserve `NOT_READY`. |

## 7. Next Gate Recommendation

Recommended next entry:

```text
Provider/LLM Chapter 5 Forbidden-phrase Post-fix Bounded Live Re-evidence Gate
```

The next gate may run exactly one bounded Route C live sample only if the current control docs route to that gate and the existing user authorization for live commands still applies. It must not claim readiness from live success alone, must preserve EID single-source/no-fallback policy, and must keep release/readiness `NOT_READY` unless a separate readiness gate proves otherwise.

## 8. Final Verdict

```text
ACCEPT_IMPLEMENTATION_READY_FOR_BOUNDED_LIVE_RE_EVIDENCE_GATE_NOT_READY
```
