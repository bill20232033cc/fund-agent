# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Plan Review — AgentDS

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`

Role: AgentDS visible-panel plan review only.

Status: `PLAN_REVIEW_PASS`

Release/readiness: `NOT_READY`

## Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth, source boundary, four-layer boundary, no `extra_payload`, no memory probing. |
| `docs/design.md` | Design truth for EID single-source, Route C, Service/Host/Agent/Fund boundaries. |
| `docs/current-startup-packet.md` | Current gate scope, accepted checkpoints through `4a7c191`. |
| `docs/implementation-control.md` | Control truth, current gate classification `heavy`, no-live constraint. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-controller-judgment-20260613.md` | Accepted `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` and H1-H5 dispositions. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-20260613.md` | Accepted evidence basis with residual routing. |
| `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-20260613.md` | Plan under review. |

## Verdict

**PASS.** The plan is code-generation-ready and preserves all required boundaries without findings.

## Q1 — Code-generation-ready?

**PASS.** Every element is specific enough for direct implementation.

Verified against current source:

- All referenced functions exist: `_exception_runtime_diagnostics()` (`chapter_orchestrator.py:1043`), `_terminal_runtime_diagnostic()` (`:2585`), `_service_chapter_result_from_task()` (`agent_bridge.py:314`), `serialize_chapter_runtime_diagnostics()` (`:718`), `_first_failed_runtime_diagnostic()` (`:2320`), `_representative_runtime_diagnostics()` (`:2621`), `_diagnostic_matches_terminal()` (`:2651`), `_RUNTIME_TERMINAL_STOP_REASONS` (`:181`), `_RUNTIME_STOP_REASON_CATEGORY` (`:190`).
- All existing test names referenced in evidence basis exist: `test_typed_contract_path_preserves_independent_body_execution` (`test_chapter_orchestrator.py:2093`), `test_unknown_exception_is_code_bug_not_provider_runtime` (`test_runner.py:146`), etc.
- All existing test fixtures exist: `_FakeWriter` (`test_runner.py:25`), `_FakeChapterLLMClient` (`test_fund_analysis_service_llm.py:57`, `test_chapter_orchestrator.py:64`), `_FakeAuditLLMClient` (both test files), `_ChapterPlanWriterClient` (`test_chapter_orchestrator.py:184`), `_projection()` (both files), `_execution_request()` (`test_fund_analysis_service_llm.py:1264`), `write_llm_incomplete_run_artifacts()`, `analyze_with_llm_execution()` (`fund_analysis_service.py:907`).
- Exact assertions with concrete values (`max_output_chars==12000`, `provider_attempt_count==0`, `stop_reason=="llm_exception"`, `category=="code_bug"`).
- Exact validation commands with expected output counts.
- Exact parameter signatures (`max_output_chars: int | None = None`).

The one note: `_FakeExtractor` is referenced in S1 step 5 but was not located in a direct grep of the four test files. If the implementation worker cannot find it, the plan's stop conditions require returning to controller rather than guessing. This is a non-blocking implementation detail.

## Q2 — Preserve EID single-source truth?

**PASS.** Explicitly preserved throughout.

- Section 2 (lines 65-68): `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`.
- Section 2 non-goals: "Do not change EID source policy, fallback behavior or annual-report source acquisition."
- Section 6 (line 375): "EID single-source/no-fallback and `NOT_READY` remain unchanged."
- Section 12 (lines 525-528): Repeats Eastmoney, fund-company/CDN, CNINFO not authorized.
- Stop conditions (section 8): multiple triggers if source policy change is needed.

## Q3 — Preserve no-live boundaries?

**PASS.** Comprehensively enforced.

- Non-goals (lines 38-55): forbids live/provider/LLM/network/PDF/FDR/source/cache/helper, `fund-analysis analyze/checklist/analyze-annual-period`.
- Forbidden validation (lines 417-424): lists all forbidden command categories.
- Stop conditions (lines 428-444): eight distinct stop triggers including "requires real provider calls," "requires reading PDF/cache/source bodies."
- Forbidden changes (lines 446-453): source policy, provider config, deterministic fallback, docs, cleanup, stage/commit/push/PR.

## Q4 — Typed `max_output_chars` propagation, no `extra_payload`?

**PASS.** Explicit and typed throughout.

- Non-goals (lines 51-52): "Do not pass explicit parameters via `extra_payload`."
- S2 (lines 196-197): keyword-only `max_output_chars: int | None = None` parameter.
- S2 (lines 204-211): Thread through `_service_chapter_result_from_task()`, `_service_attempt_from_agent()`, `_runtime_diagnostics_from_task()`, `_exception_runtime_diagnostics()`.
- Stop condition (line 258): "if any explicit cap must be carried through `extra_payload`."

## Q5 — Avoid exposing raw exception messages, prompts, provider bodies, headers, model names, API keys, secrets?

**PASS.** Multiple layers of defense.

- Non-goals (lines 48-49): explicit prohibition of prompt/draft/provider/raw/secret exposure.
- S1 assertions (lines 144-147): blocked reasons must not contain `Authorization`, `Bearer`, `sk-secret`, `prompt raw`.
- S2 assertions (line 242): serialized payload must not contain secret-like substrings.
- S3 assertions (lines 301-303): artifact must not include `SYSTEM_PROMPT_CANARY`, `USER_PROMPT_CANARY`, `RAW_AUDITOR_RESPONSE_CANARY`, `raw_response`, `Authorization`, `Bearer`, `sk-`.
- Stop conditions (lines 434-435): stop if diagnostics require raw exception messages, prompt text, provider response bodies, model names, headers, API keys, secrets.

## Q6 — Slice sequence safe and narrow enough?

**PASS.** Well-structured with explicit split option.

- S1 (reproducer tests): only 2 test files, no source changes.
- S2 (diagnostic propagation): 2 source files + 2 test files, exact function changes listed.
- S3 (artifact fixture): only 1 test file.
- S4 (validation): no source changes, only focused validation commands.
- Section 12 (lines 515-521) already acknowledges the split option: "assign Slice S1-S3 as one narrow pass only if the controller agrees the slice set is small enough. Otherwise split into: 1. S1 reproducer tests; 2. S2 diagnostic propagation; 3. S3 artifact fixture."

Dependency is S1 → S2 → S3, which is natural (tests validate the fix, fixture locks the result). The plan correctly notes S1 tests may fail before S2 (line 166-169).

## Q7 — Preserve `code_bug` vs provider runtime distinction and `NOT_READY`?

**PASS.** Explicitly preserved.

- S2 (lines 225-226): "Do not add `llm_exception` to a provider-runtime category mapping. The point is to keep code bugs distinguishable from provider runtime failures."
- Section 6 (lines 366-367): classification preserved.
- Stop condition (lines 436-437): stop if fix would classify internal code bugs as provider runtime availability.
- `NOT_READY` preserved (lines 375, 463, 530).

## Q8 — Avoid memory probing and treat prior `rg` as `DEVIATION_NOT_EVIDENCE`?

**PASS.** Correctly handled.

- Section 2 (lines 89-91): "The prior memory `rg` was accepted only as `DEVIATION_NOT_EVIDENCE`. This plan and the future implementation gate must not probe memory."
- Forbidden validation (line 424): "memory probing."
- No memory file paths or probing commands in the plan's validation matrix or implementation slices.

## Residual / Deferred Table

| Item | Classification | Basis |
|---|---|---|
| `_FakeExtractor` not located in a direct grep of the four allowed test files | Non-blocking implementation detail | If the implementation worker cannot find it, the plan's stop conditions require returning to controller. The plan references existing fixtures; the worker should locate the actual helper or equivalent. |
| Exact live source identity `004393 / 2025` is not replayed | Accepted planning constraint | Plan correctly treats this as deferred (section 9, line 459). |
| S1 tests may fail before S2 | Accepted expected behavior | Plan documents this (lines 166-169). S1+S2 should be implemented together or S1 committed first with S2 following. |
| Slice bundling (S1-S3 as one pass vs split) | Controller decision | Plan already provides both options (section 12). Recommend split into 3 sequential passes to isolate each residual. |

## Review Boundary

This review is plan-only. It does not authorize implementation, source/test/runtime edits, live commands, cleanup, stage, commit, push, PR, merge, mark-ready, or release/readiness state changes.

Release/readiness remains `NOT_READY`.
