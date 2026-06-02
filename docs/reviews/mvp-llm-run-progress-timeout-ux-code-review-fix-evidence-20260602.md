# MVP LLM Run Progress And Timeout UX Code Review Fix Evidence

## Gate / Role

- Gate: `MVP LLM run progress and timeout UX gate`
- Role: fix specialist (`AgentCodex`)
- Source review artifacts:
  - `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-ds-20260602.md`
  - `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-mimo-20260602.md`
  - `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-controller-judgment-20260602.md`
- Accepted finding fixed: DS F1 quality gate block / not-run path with `--use-llm --llm-progress` could raise `UnboundLocalError` because `host_result` was unbound when `_run_llm_analysis_in_host()` re-raised quality gate exceptions.

## Self-check

- Current gate / role: code-review fix pass only.
- Scope boundary: changed only `fund_agent/ui/cli.py`, `tests/ui/test_cli.py`, and this fix evidence artifact.
- Non-goals preserved: no Host event sink semantic changes, provider timeout/retry/backoff changes, artifact schema changes, chapter acceptance/auditor changes, score/golden/readiness/quality gate semantic changes, or design/control/startup doc updates.
- External actions: no staging, commit, push, PR, or next gate action.

## Fix Summary

- Initialized `host_result: HostRunResult | None = None` before the Host call in the `--use-llm` branch.
- Kept `reporter.stop()` in the existing `finally` so heartbeat cleanup still occurs on success, incomplete, Host failure, and quality gate re-raise.
- Added a guard so `reporter.emit_terminal(host_result)` runs only after `_run_llm_analysis_in_host()` actually returns a `HostRunResult`.
- On `QualityGateBlockedError` / `QualityGateNotRunBlockedError` re-raise, the code now skips fake terminal progress and lets the existing outer quality gate exception handlers preserve stderr and exit code `2`.

## Regression Tests Added

- `test_analyze_cli_use_llm_progress_quality_gate_block_preserves_error`
- `test_analyze_cli_use_llm_progress_quality_gate_not_run_preserves_error`

The tests assert:

- exit code remains `2`;
- stdout remains empty;
- existing quality gate blocked / not-run stderr remains visible;
- no `UnboundLocalError`;
- no generic `分析失败：` wrapper;
- no invented `LLM progress: run_terminal` line;
- no `LLM Host run 未完成` fake incomplete summary.

## Validation Results

```bash
uv run pytest tests/ui/test_cli.py -q
```

Result:

```text
72 passed in 1.33s
```

```bash
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
```

Result:

```text
191 passed in 1.12s
```

```bash
uv run ruff check .
```

Result:

```text
All checks passed!
```

## Residual Risks / Owners

| Risk | Disposition | Owner / Destination |
|---|---|---|
| Progress may still emit `run_started` before a quality gate exception occurs inside Host | Accepted behavior; not a fake terminal line and does not corrupt quality gate stderr/exit | Current UX contract |
| Provider timeout and chapter acceptance remain unresolved | Out of scope for this fix | Future provider/runtime and chapter acceptance gates |

## Completion

DS F1 is fixed and covered by focused regression tests. Self-check: pass.
