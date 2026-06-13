# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Plan Review — MiMo

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`

Role: AgentMiMo visible-panel plan review only.

Review target: `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-20260613.md`

Memory note: MiMo auto-recalled `feedback_gateflow_review_pattern.md`. That memory is not used as gate evidence; no conclusion in this review relies on memory. All findings are derived from repo truth/control/evidence/plan files only.

## Required Context Read

| File | Role |
|---|---|
| `AGENTS.md` | Rule truth, four-layer boundary, extra_payload guardrail, EID/fallback guardrail. |
| `docs/design.md` | Design truth for Route C, EID single-source, Service/Host/Agent/Fund boundaries. |
| `docs/current-startup-packet.md` | Current gate, accepted checkpoints, EID single-source/no-fallback guardrails. |
| `docs/implementation-control.md` | Control truth, current no-live gate, next-entry routing. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-controller-judgment-20260613.md` | Accepted evidence controller judgment: `ACCEPT_EVIDENCE_NOT_READY`, `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-20260613.md` | Evidence artifact: H1-H5 dispositions, residual routing. |

## Source Verification Performed

MiMo verified the following against current source before writing findings:

- `fund_agent/services/chapter_orchestrator.py` L1043-1098: `_exception_runtime_diagnostics` current signature has NO `max_output_chars` parameter. Confirmed plan's S2 change is needed.
- `fund_agent/services/chapter_orchestrator.py` L2585-2618: `_terminal_runtime_diagnostic` current logic for `llm_exception` with `expected_category is None` scans for `diagnostic.provider_runtime_category is not None`. Pre-provider code bug (where `provider_runtime_category is None`) returns `None`. Confirmed plan's S2 terminal selection fix is needed.
- `fund_agent/services/chapter_orchestrator.py` L2651-2679: `_diagnostic_matches_terminal` current logic for `expected_category is None` checks `diagnostic.provider_runtime_category is not None`. Confirmed plan's S2 representative selection fix is needed.
- `fund_agent/services/chapter_orchestrator.py` L181-197: `_RUNTIME_TERMINAL_STOP_REASONS` includes `llm_exception`; `_RUNTIME_STOP_REASON_CATEGORY` does NOT map `llm_exception`. Confirmed.
- `fund_agent/services/chapter_orchestrator.py`: `_is_code_bug_runtime_diagnostic` does NOT exist. Confirmed plan's new helper is needed.
- `fund_agent/services/agent_bridge.py` L314: `_service_chapter_result_from_task(task, *, projection)` — NO `max_output_chars`. Confirmed plan's S2 threading is needed.
- `fund_agent/services/agent_bridge.py` L629-663: `_runtime_diagnostics_from_task` calls `_exception_runtime_diagnostics` without `max_output_chars`. Confirmed.
- `fund_agent/services/agent_bridge.py` L575-587: `_service_attempt_from_agent` calls `_exception_runtime_diagnostics` (auditor path) without `max_output_chars`. Confirmed.
- `tests/agent/test_runner.py` L25: `_FakeWriter` uses `actions: dict[int, object]` — supports per-chapter exception injection. Plan's S1 approach is feasible.
- `tests/agent/test_runner.py` L383: `_projection(chapter_ids)` exists. Plan's `_projection((3,))` call is valid.
- `tests/services/test_fund_analysis_service_llm.py` L57-100: `_FakeChapterLLMClient` accepts `texts` only, no `raises`/`exception` parameter. Plan's S1 service test needs either extending this fake or creating a new one. This is a minor implementation detail, not a plan blocker.
- `tests/services/test_fund_analysis_service_llm.py` L1264-1309: `_execution_request()` accepts `chapter_policy: ChapterOrchestrationPolicy | None`. Plan's `ChapterOrchestrationPolicy(target_chapter_ids=(3,), ...)` is valid input.
- `tests/services/test_chapter_orchestrator.py` L184: `_ChapterPlanWriterClient` supports per-chapter `actions`. Plan's S2 test approach is feasible.

## Review Questions

### Q1. Code-generation-ready?

**Verdict: PASS with minor note.**

The plan specifies exact files, functions, test names, assertions, data flow and validation commands for each slice. Specific findings:

- S1: Exact test names, fake configurations, assertion lists and stop conditions. `_FakeWriter(actions={3: ValueError(...)})` is feasible per source verification. Service test's `_FakeChapterLLMClient` only accepts `texts`, not per-chapter exceptions — the implementer will need to extend it or create a variant. This is a typical implementation detail, not a redesign.
- S2: Exact `_exception_runtime_diagnostics` signature change, bridge threading path (`input_data.policy.max_output_chars`), new `_is_code_bug_runtime_diagnostic` helper, terminal/representative selection changes, and test assertions. The plan correctly identifies that `_enrich_provider_diagnostic` behavior must be preserved.
- S3: Exact helper structure, diagnostic fields, artifact assertions and safety canaries. `_incomplete_code_bug_pre_provider_result()` construction is specific enough.
- S4: Exact validation commands with expected results.

### Q2. Preserves current operational source truth?

**Verdict: PASS.**

- Plan section 1 Non-goals: "Do not change EID source policy, fallback behavior or annual-report source acquisition."
- Plan section 2: Explicitly restates `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`.
- Plan section 8: Forbidden changes include "Source policy, source acquisition, fallback and repository behavior."
- No Eastmoney, fund-company/CDN, CNINFO or fallback references in implementation scope.

### Q3. Preserves no-live boundaries?

**Verdict: PASS.**

Plan section 1 Non-goals explicitly forbids:
- live/provider/LLM/network/PDF/FDR/source/cache/helper commands
- `fund-analysis analyze`, `fund-analysis checklist`, `fund-analysis analyze-annual-period`
- readiness/release/PR/push/merge commands

Plan section 7: Forbidden validation list matches the non-goals.

Plan section 8: Stop conditions require implementation to halt if live provider calls, network, credentials, prompt/provider payloads, raw responses, PDF/cache/source bodies or `FundDocumentRepository` access is needed.

### Q4. Keeps max_output_chars as typed explicit parameter?

**Verdict: PASS.**

- S2 step 1: `max_output_chars: int | None = None` as explicit keyword-only parameter on `_exception_runtime_diagnostics`.
- S2 step 4: Threading through `_service_chapter_result_from_task`, `_service_attempt_from_agent`, `_runtime_diagnostics_from_task` as explicit parameter.
- Plan section 3: "`max_output_chars` is already a typed field... The implementation must keep it typed and explicit."
- Plan section 1 Non-goals: "Do not pass explicit parameters via `extra_payload`."
- Plan section 8 Stop conditions: "Stop if any explicit cap must be carried through `extra_payload`."

### Q5. Avoids exposing raw exception messages, prompts, provider bodies, headers, model names, API keys or secrets?

**Verdict: PASS.**

- S1 step 4: "rendered blocked reasons do not contain `Authorization`, `Bearer`, `sk-secret` or `prompt raw`."
- S1 step 8: "diagnostics do not contain secret-like substrings."
- S2 step 8: "serialized payload string does not contain secret-like substrings."
- S3 step 6: "Assert artifact contents do not include `SYSTEM_PROMPT_CANARY`, `USER_PROMPT_CANARY`, `RAW_AUDITOR_RESPONSE_CANARY`, `raw_response`, `Authorization`, `Bearer` or `sk-`."
- Plan section 1 Non-goals: "Do not expose prompt text, draft text, provider bodies, raw responses, API keys, headers, credentials or secrets in diagnostics or artifacts."
- Plan section 8 Stop conditions: "Stop if implementation requires adding raw exception messages, prompt text, provider bodies or model names to serialized payloads."
- Test `ValueError("Authorization Bearer sk-secret prompt raw")` is specifically designed to verify secret-like substring redaction.

### Q6. Slice sequence safe and narrow enough?

**Verdict: PASS.**

- S1 (reproducer tests) → S2 (diagnostic propagation) → S3 (artifact fixture) → S4 (regression checks) is a correct dependency sequence.
- S1 tests are expected to fail before S2 (plan section 4.1 "Expected review signal"), which is the intended behavior: tests establish the target shape, S2 fixes the gap.
- Each slice has clear allowed files and stop conditions.
- The plan offers splitting S1/S2/S3 as an option if the controller prefers narrower passes.
- S2 touches 2 source files + 2 test files — focused on a single concern (threading `max_output_chars` through diagnostic pipeline).

### Q7. Preserves code_bug vs provider runtime distinction and NOT_READY?

**Verdict: PASS.**

- S2 step 6: "Do not add `llm_exception` to a provider-runtime category mapping. The point is to keep code bugs distinguishable from provider runtime failures."
- S1 step 4: "no provider runtime category is introduced."
- S2 step 5: `_is_code_bug_runtime_diagnostic` returns true only when `provider_runtime_category is None` AND `chapter_failure_category=="code_bug"` — keeps code bugs separate from provider runtime.
- Plan section 6: "provider_attempt_count remains `0`; no provider availability claim is made."
- Plan section 3: "Runtime diagnostics must remain allowlist-only safe scalar payloads."
- `NOT_READY` preserved throughout plan sections 6, 8, 9.

### Q8. Avoids memory probing and correctly treats prior memory rg as DEVIATION_NOT_EVIDENCE?

**Verdict: PASS.**

- Plan section 2: "The prior memory `rg` was accepted only as `DEVIATION_NOT_EVIDENCE`. This plan and the future implementation gate must not probe memory."
- Plan section 7: Forbidden validation includes "memory probing."
- No memory commands in any implementation slice.

## Residual / Deferred Table

| Residual / risk | Disposition |
|---|---|
| Exact live source identity `004393 / 2025` not replayed. | Accepted planning constraint: no-live gate cannot read source bodies. Implementation reproduces exact safe-metadata failure shape only. |
| Underlying live Chapter 3 `ValueError` root code path may differ from fake no-live `ValueError`. | Deferred to later controller-authorized no-live or live diagnostic gate. |
| LLM content quality remains unproven. | Deferred; not part of diagnostic implementation. |
| Provider readiness and 401/403 provider-response classification remain unproven. | Deferred; no provider commands in this work unit. |
| Release/readiness remains `NOT_READY`. | Preserved; this plan cannot close release/readiness. |
| `_FakeChapterLLMClient` in service test does not support per-chapter exception injection. | Minor implementation detail: extend the fake or create a variant. Not a plan blocker. |
| Artifact schema breadth beyond `runtime_diagnostics` remains undecided. | Do not broaden in this implementation. Route to separate artifact schema gate if needed. |

## Source Policy Judgment

Current operational annual-report source truth remains:

- `selected_source=eid`
- `source_mode=single_source_only`
- `fallback_enabled=false`

Eastmoney, fund-company/CDN, CNINFO and any annual-report fallback are not current source truth, not current execution paths and not authorized current sources. This review does not modify source acquisition policy.

## Verdict

**PASS**

The plan is code-generation-ready, preserves all required boundaries, and correctly routes the accepted `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` residuals into specific files, tests, assertions and stop conditions. No blocking findings.

Key strengths:
- Exact file/function/test/assertion specificity across all four slices.
- Correct identification of `_exception_runtime_diagnostics` signature gap, `_terminal_runtime_diagnostic` selection gap and `_diagnostic_matches_terminal` representative gap.
- Proper preservation of EID single-source/no-fallback, no-live boundaries, typed explicit parameters, safe scalar diagnostics, code_bug vs provider runtime distinction, secret redaction and `NOT_READY`.
- Clear stop conditions and forbidden changes that prevent scope creep.
- S1 tests expected to fail before S2 — correct sequencing.
