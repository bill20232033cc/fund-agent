# Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Plan Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Planning Gate`

Final verdict: `ACCEPT_PLAN_READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the planning gate for the accepted Chapter 5 `forbidden_phrase` no-live blocker after diagnostic evidence checkpoint `c20ab5e`.

This gate did not authorize implementation, source/test/runtime behavior changes, live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands, source-policy changes, provider-default changes, repair-budget changes, annual-period LLM route changes, Docling work, staging, pushing or PR actions.

## 2. Evidence Reviewed

| Evidence | Role |
|---|---|
| `AGENTS.md` | Rule truth: direct same-source root cause, Fund/Agent/Service boundaries, no readiness/source overreach. |
| `docs/current-startup-packet.md` | Current gate truth: Chapter 5 narrow no-live fix planning, `NOT_READY`, no implementation in planning gate. |
| `docs/implementation-control.md` | Control truth: current active gate, accepted checkpoint `c20ab5e`, next-entry expectations. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-no-live-diagnostic-evidence-20260614.md` | Accepted diagnostic evidence basis. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Accepted H1-H5 disposition and next-gate recommendation. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-20260614.md` | Plan under judgment. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-review-ds-20260614.md` | DS independent plan review, verdict `PASS_WITH_FINDINGS`. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-narrow-no-live-fix-plan-review-mimo-20260614.md` | MiMo independent plan review, verdict `PASS`. |

## 3. Accepted Plan Decision

The accepted implementation strategy is:

```text
Option 1 only: forbidden-phrase-specific repair prompt guidance.
```

Controller accepts the plan's deferral of diagnostic lineage clarification. The direct same-source causal chain is repair guidance specificity: accepted evidence shows attempt 0 consumed the regenerate path, attempt 1 entered writer validation with a forbidden phrase, and deterministic writer validation blocked it. Diagnostic lineage layering explains reporting categories but does not itself generate or accept the forbidden phrase.

## 4. Binding Implementation Scope

| Area | Accepted scope |
|---|---|
| Source file | `fund_agent/fund/chapter_writer.py` only. |
| Main change | Add `_ch5_forbidden_phrase_repair_guidance_prompt(chapter, repair_context)` and append it to `_chapter_prompt_fragments()` repair-context assembly after the existing Chapter 2 L1 repair guidance. |
| Activation guard | Return non-empty guidance only when `chapter.chapter_id == 5` and `repair_context is not None`. |
| Prompt semantics | Delete trading-action advice, position actions, return prediction, target-price language and fund-manager motive speculation; allow only `值得持有 / 需要关注 / 建议替换`; data gaps must render as `数据不足` or `下一步最小验证问题`. |
| Must remain unchanged | `_repair_context_prompt()`, `_FORBIDDEN_PHRASES`, Agent runner retry behavior, Service diagnostic schema/category mapping, provider/runtime/config/source policy, default repair budget. |

## 5. Required Implementation Tests

Implementation gate must add or verify:

| Test | Required proof |
|---|---|
| `tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_renders_on_repair_attempt` | Chapter 5 repair context renders the new forbidden-phrase guidance and keeps `extra_payload` absent. |
| `tests/fund/test_chapter_writer.py::test_ch5_forbidden_phrase_repair_guidance_absent_outside_ch5_repair` | No prompt expansion for Chapter 5 initial attempt or non-Chapter 5 repair attempts. |
| `tests/agent/test_runner.py::test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance` | Agent runner propagates audit repair context into the second Chapter 5 writer request, includes guidance, and does not create a hidden third writer retry. |

Focused regression suite must also include the existing writer forbidden-phrase, repair-context, repair-budget, Chapter 6 invalid-marker retry, and Service forbidden-phrase/audit-parse diagnostic tests listed in the plan.

## 6. Reviewer Findings Disposition

| Finding | Controller disposition | Implementation handling |
|---|---|---|
| DS F1: runner test references `_FakeWriter()` / `_FakeAuditor(...)`; fixture existence must be verified. | `ACCEPT_INFORMATIONAL_NONBLOCKING` | Implementation worker must inspect existing `tests/agent/test_runner.py` fixtures and either reuse them or construct equivalent local test helpers before writing the new test. |
| DS F2: prompt guidance is probabilistic; LLM may still violate. | `ACCEPT_INFORMATIONAL_NONBLOCKING` | Implementation only proves deterministic prompt construction and no-live propagation. Bounded live re-evidence remains a later gate after accepted implementation. |
| MiMo PASS: no blocking findings. | `ACCEPT` | No amendment required. |

## 7. Residuals And Deferred Gates

| Residual | Owner | Deferred handling |
|---|---|---|
| Live/provider behavior after prompt guidance remains unproven. | Controller / evidence owner | Separate bounded live re-evidence gate after implementation acceptance. |
| H1 raw prompt-body absence remains unproven. | Prompt/evidence owner | Keep as partial; do not claim complete initial prompt omission. |
| Diagnostic lineage clarification remains deferred. | Service/Agent diagnostics owner | Separate no-live diagnostic/implementation gate only if post-fix evidence proves it is needed. |
| Repair budget calibration remains unstarted. | Service/Agent chapter orchestration owner | Separate standard gate; no default budget change in this implementation. |
| Release/readiness remains unproven. | Release owner | Preserve `NOT_READY`. |

## 8. Next Gate Recommendation

Recommended next entry:

```text
Provider/LLM Chapter 5 Forbidden-phrase Narrow No-live Fix Implementation Gate
```

Implementation should use the accepted plan as binding scope. It must not add diagnostic lineage changes, retry-path changes, repair-budget changes or Service/Agent schema changes unless a blocker is proven and controller authorizes a revised plan.

## 9. Final Verdict

```text
ACCEPT_PLAN_READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION_NOT_READY
```
