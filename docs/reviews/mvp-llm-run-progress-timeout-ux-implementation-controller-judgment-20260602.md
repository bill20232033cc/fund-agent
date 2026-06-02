# Controller Judgment: MVP LLM Run Progress And Timeout UX Implementation Acceptance

## Self-check

- Phase: `MVP real LLM observability and chapter acceptance phase`.
- Gate: `MVP LLM run progress and timeout UX gate`.
- Role: controller only.
- Work type: implementation review loop closeout and accepted checkpoint preparation.
- Scope boundary: no further implementation, no provider budget change, no chapter acceptance calibration, no score/golden/readiness change, no push, no PR, and no next gate implementation.
- Source of truth: accepted plan, implementation evidence, code reviews, fix evidence, re-reviews, and controller validation reruns.

## Inputs

| Purpose | Artifact |
|---|---|
| Accepted plan | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md` |
| Plan acceptance judgment | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-controller-judgment-20260602.md` |
| Implementation evidence | `docs/reviews/mvp-llm-run-progress-timeout-ux-implementation-evidence-20260602.md` |
| AgentDS code review | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-ds-20260602.md` |
| AgentMiMo code review | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-mimo-20260602.md` |
| Code review controller judgment | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-controller-judgment-20260602.md` |
| Fix evidence | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-fix-evidence-20260602.md` |
| AgentDS re-review | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-rereview-ds-20260602.md` |
| AgentMiMo re-review | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-rereview-mimo-20260602.md` |

## Implementation Summary

The gate implemented safe live progress for `fund-analysis analyze --use-llm` only:

- CLI option: `--llm-progress/--no-llm-progress` with auto default based on stderr TTY.
- Progress output: stderr-only, prefix `LLM progress:`.
- Event types: `run_started`, `phase_started`, `phase_completed`, `still_running`, `run_terminal`.
- Host integration: generic optional `event_sink` on `HostRuntimeRunner.run_sync()` with a single append-before-sink commit helper.
- CLI safety: no-raise reporter sink, allowlisted progress fields, secret canary rejection, bounded heartbeat lifecycle, and deterministic heartbeat tests.
- Service phase visibility: `analysis_core` Host phase events around the LLM service analysis core when `host_context` exists.

## Review And Fix Disposition

| Finding | Controller disposition | Outcome |
|---|---|---|
| DS F1: quality gate block / not-run with progress could hit `UnboundLocalError` and corrupt the existing quality gate error path | accepted blocking | Fixed. `host_result` is initialized and terminal progress is emitted only when a Host result is returned. Two regression tests cover block and not-run with `--llm-progress`. |
| DS low observation: `_handle_phase_completed()` scalar sanitization fail-safe | rejected-with-reason | No fix required because failure marks the sink failed and suppresses heartbeat; no current user impact. |
| MiMo NB-1: heartbeat may emit one stale `still_running` before terminal in a narrow race | accepted non-blocking | No fix required in this gate; not a post-terminal line and no accepted invariant is violated. |
| MiMo NB-2: fake CLI runner does not exercise real sink exception escape path | accepted non-blocking | No fix required; Host-level propagation is separately tested, and CLI fake tests the CLI no-raise wrapper. |
| MiMo NB-3: `_mark_sink_failed()` sets Event inside lock | accepted non-blocking | No fix required; `threading.Event.set()` is thread-safe and bounded. |

Both re-reviews passed after the fix:

- AgentDS: `PASS`; DS F1 fixed, no new blocking findings.
- AgentMiMo: `PASS`; fix did not regress prior PASS findings.

## Controller Validation

Controller reran the required validations after the fix:

```text
uv run pytest tests/ui/test_cli.py -q
72 passed in 1.16s

uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
191 passed in 1.30s

uv run ruff check .
All checks passed!
```

## Boundary And Fail-closed Decision

The implementation is accepted because it satisfies the current phase objective directly: real `--use-llm` runs now expose safe live progress without weakening fail-closed semantics or moving calibration/provider/runtime-budget work into this gate.

Accepted invariants:

- Deterministic `analyze` and `checklist` remain unchanged.
- Incomplete / Host failed `--use-llm` runs still keep stdout empty, exit non-zero, and do not fall back to deterministic output.
- Quality gate block / not-run paths preserve exit code `2`, stdout empty, and existing quality gate stderr.
- Progress is stderr-only and does not print prompts, drafts, raw provider responses, raw auditor responses, API keys, Authorization headers, cookies, model names, full config, or arbitrary diagnostics.
- Host remains generic and business-agnostic: no Service/Fund imports, no fund business semantics, no provider clients, no CHAPTER_CONTRACT/ITEM_RULE/preferred_lens, and no explicit business parameters in `extra_payload`.
- No provider timeout/retry/backoff, chapter acceptance calibration, artifact schema, auditor strictness, score/golden/readiness, or PR state changes were made.

## Residual Risks / Owners

| Risk | Disposition | Owner / Destination |
|---|---|---|
| Provider endpoint may still timeout while progress is visible | Accepted residual | Future `MVP provider runtime budget calibration gate` |
| Progress does not expose provider attempt boundaries live | Accepted residual | Future provider observability gate if controller opens it |
| Artifact schema does not retain progress timeline | Deferred | Future observability artifact schema gate, only with controller approval |
| Chapter acceptance for real LLM chapters remains low | Deferred | Future `MVP real LLM chapter acceptance calibration gate` |
| Heartbeat stale pre-terminal race noted by MiMo | Non-blocking accepted risk | Revisit only if real UX evidence shows misleading ordering |

## Decision

Accept the implementation. Create a local accepted implementation checkpoint for `MVP LLM run progress and timeout UX gate`, then perform controller-level truth sync before selecting the next phase gate. Do not push, create PR, mark ready, or enter calibration/provider budget/score-loop implementation from this judgment.
