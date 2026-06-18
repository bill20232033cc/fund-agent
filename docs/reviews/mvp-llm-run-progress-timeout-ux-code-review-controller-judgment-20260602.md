# Controller Judgment: MVP LLM Run Progress And Timeout UX Code Review

## Self-check

- Phase: `MVP real LLM observability and chapter acceptance phase`.
- Gate: `MVP LLM run progress and timeout UX gate`.
- Role: controller only.
- Work type: code review finding judgment and fix handoff preparation.
- Scope boundary: no runtime/code/test fix by controller, no staging, no commit, no push, no PR, and no next gate.
- Source of truth: accepted plan, implementation evidence, AgentDS code review, AgentMiMo code review, and local validation evidence.

## Inputs

| Purpose | Artifact |
|---|---|
| Accepted plan | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md` |
| Plan acceptance judgment | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-controller-judgment-20260602.md` |
| Implementation evidence | `docs/reviews/mvp-llm-run-progress-timeout-ux-implementation-evidence-20260602.md` |
| AgentDS code review | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-ds-20260602.md` |
| AgentMiMo code review | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-mimo-20260602.md` |

## Review Verdicts

| Reviewer | Verdict | Blocking findings |
|---|---|---|
| AgentDS | `PASS with 1 blocking finding` | 1 |
| AgentMiMo | `PASS` | 0 |

Controller local validation before review dispatch:

```text
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
189 passed in 1.23s

uv run ruff check .
All checks passed!
```

## Finding Disposition

| Finding | Controller judgment | Required action |
|---|---|---|
| DS F1: quality gate block / not-run path with progress enabled can raise `UnboundLocalError` because `host_result` is not bound when `_run_llm_analysis_in_host()` re-raises the quality gate exception | accepted blocking | Fix the CLI progress wrapper so quality gate exceptions preserve the existing quality gate stderr/exit behavior and do not attempt to emit a fake terminal progress line from an unbound `host_result`. Add focused regression coverage for `--use-llm --llm-progress` quality gate block and not-run paths. |
| DS low observation: `_handle_phase_completed()` fail-safe path marks sink failed if scalar sanitization raises | rejected-with-reason | The reviewer itself confirms the behavior is fail-safe: `_mark_sink_failed()` clears active state and suppresses heartbeat. No current-user impact or accepted-plan violation. |
| MiMo NB-1: narrow race where heartbeat might emit one stale `still_running` before terminal | accepted non-blocking | No action in this fix. It is pre-terminal, not post-terminal, and does not violate the accepted guarantee. Code review after fix should re-check no `still_running` can appear after `run_terminal`. |
| MiMo NB-2: fake CLI runner does not exercise real Host sink exception escape path | accepted non-blocking | No action in this fix. Host-level propagation is covered separately by Host tests; CLI fake covers the CLI no-raise wrapper contract. |
| MiMo NB-3: `_mark_sink_failed()` sets `_stop_event` inside the lock | accepted non-blocking | No action in this fix. `threading.Event.set()` is thread-safe and the behavior remains bounded and fail-safe. |

## Required Fix Scope

The fix must stay narrow:

- Allowed files: `fund_agent/ui/cli.py`, `tests/ui/test_cli.py`, implementation evidence update or separate fix evidence under `docs/reviews/`.
- Do not change Host event sink semantics, provider timeout budget, artifact schema, chapter acceptance logic, auditor rules, score/golden/readiness, or design/control/startup docs.
- Preserve accepted contracts:
  - quality gate block and not-run still exit code `2`;
  - existing quality gate stderr remains visible;
  - no `UnboundLocalError`;
  - no terminal progress line is invented on quality gate re-raise path;
  - stdout remains empty;
  - deterministic paths remain unchanged.

## Required Fix Validation

At minimum, rerun:

```bash
uv run pytest tests/ui/test_cli.py -q
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
uv run ruff check .
```

## Next Entry Point

Dispatch a same-task fix handoff to AgentCodex. After fix evidence is produced, send re-review to AgentDS focused on the accepted blocking finding and optionally to AgentMiMo for regression confirmation.
