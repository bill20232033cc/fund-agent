# Re-review: MVP LLM Run Progress And Timeout UX — DS F1 Fix Regression Confirmation

## Gate / Role

- Gate: `MVP LLM run progress and timeout UX gate`
- Role: independent code reviewer (`AgentMiMo`)
- Re-review type: regression confirmation after DS F1 fix
- Review date: 2026-06-02

## Inputs

| Purpose | Artifact |
|---|---|
| Prior MiMo review | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-mimo-20260602.md` |
| Prior DS review | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-ds-20260602.md` |
| Controller judgment | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-controller-judgment-20260602.md` |
| Fix evidence | `docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-fix-evidence-20260602.md` |

## Fix Scope Confirmation

Changed files: `fund_agent/ui/cli.py`, `tests/ui/test_cli.py` only. No Host, Service, provider, artifact, design/control/startup changes.

### Fix mechanism (`cli.py:786-797`)

```python
host_result: HostRunResult | None = None       # line 786: pre-initialized
try:
    reporter.start()
    host_result = _run_llm_analysis_in_host(    # line 789: may raise
        execution_request,
        event_sink=reporter.event_sink,
    )
finally:
    reporter.stop()                             # line 794: always runs
if host_result is None:                         # line 795: guard
    raise RuntimeError("LLM Host run did not return a result")
reporter.emit_terminal(host_result)             # line 797: only if host_result bound
```

When `_run_llm_analysis_in_host()` re-raises `QualityGateBlockedError` / `QualityGateNotRunBlockedError`:
1. Assignment to `host_result` does not complete → remains `None`
2. `finally` runs `reporter.stop()` → heartbeat cleaned up
3. Exception propagates to outer `except QualityGateBlockedError` / `except QualityGateNotRunBlockedError` handlers (lines 820-825)
4. `emit_terminal` is never called → no fake `run_terminal` line
5. Existing quality gate stderr + exit code 2 preserved

## Verification: DS F1 Fix Correctness

**Verdict: PASS**

- `host_result` initialized to `None` before try block ✓
- `reporter.stop()` in `finally` ensures heartbeat cleanup on all paths ✓
- `emit_terminal` guarded by `host_result is None` check ✓
- Quality gate exceptions bypass `emit_terminal` and reach existing handlers ✓
- `test_analyze_cli_use_llm_progress_quality_gate_block_preserves_error` asserts:
  - `exit_code == 2` ✓
  - `stdout == ""` ✓
  - quality gate stderr content preserved ✓
  - `run_started` progress present (Host started before exception) ✓
  - `run_terminal` NOT present ✓
  - `UnboundLocalError` NOT present ✓
  - `分析失败：` NOT present ✓
  - `LLM Host run 未完成` NOT present ✓
- `test_analyze_cli_use_llm_progress_quality_gate_not_run_preserves_error` asserts same contract for not-run path ✓

## Regression Check: Prior PASS Findings

| # | Prior finding | Status after fix |
|---|---|---|
| 1 | Progress UX scope: `--use-llm` only | **No change** — fix is inside `use_llm` branch only |
| 2 | Stdout contract: strict final-report-only | **No change** — quality gate still exits 2 with empty stdout |
| 3 | `--llm-progress` / `--no-llm-progress` / auto TTY | **No change** — fix does not touch `_resolve_llm_progress_enabled` |
| 4 | Host `event_sink` generic, business-agnostic | **No change** — no Host file changed |
| 5 | Host does not catch/translate sink exceptions; CLI no-raise | **No change** — sink wrapper unchanged |
| 6 | Heartbeat lifecycle: Event + Lock + `_heartbeat_tick` | **No change** — `reporter.stop()` still in `finally` |
| 7 | `run_terminal` after `run_sync()` returns | **Improved** — quality gate path now correctly skips `emit_terminal` |
| 8 | Secret safety | **No change** — formatter unchanged |
| 9 | Host boundary remains clear | **No change** — no Host file changed |
| 10 | Tests cover negative boundary and fail-closed | **Improved** — 2 new quality gate regression tests added |
| 11 | Docs sync accuracy | **No change** — no docs changed in fix |

## Non-blocking Observations from Prior Review

- NB-1 (heartbeat lock-release race): **Unchanged** — fix does not touch `_heartbeat_tick`
- NB-2 (fake runner doesn't exercise real sink escape): **Unchanged** — fake runner unchanged
- NB-3 (`_mark_sink_failed` stop_event inside lock): **Unchanged** — `_mark_sink_failed` unchanged

## Controller Constraint Verification

| Constraint | Status |
|---|---|
| No Host event_sink semantic change | ✓ No Host file changed |
| No provider budget change | ✓ No provider file changed |
| No artifact schema change | ✓ No artifact file changed |
| No chapter acceptance / auditor change | ✓ No fund file changed |
| No score/golden/readiness change | ✓ No score file changed |
| No design/control/startup change | ✓ No design file changed |
| Quality gate block preserves exit code 2 | ✓ Test-verified |
| Quality gate not-run preserves exit code 2 | ✓ Test-verified |
| No `UnboundLocalError` | ✓ Test-verified |
| No invented `run_terminal` on quality gate path | ✓ Test-verified |
| stdout remains empty on quality gate path | ✓ Test-verified |

## Validation Re-run

```bash
uv run pytest tests/ui/test_cli.py -q
```

Result: `72 passed in 1.33s` (was 70 before fix; 2 new regression tests)

```bash
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
```

Result: `191 passed in 1.25s` (was 189 before fix; 2 new CLI tests)

```bash
uv run ruff check .
```

Result: `All checks passed!`

All match controller rerun validation numbers.

## Findings

未发现实质性问题。

The DS F1 fix is correct, narrow, and does not regress any prior PASS finding. The quality gate exception path now correctly preserves exit code 2, empty stdout, existing quality gate stderr, and no invented `run_terminal` line. Two focused regression tests cover both block and not-run paths with `--llm-progress` enabled.

## Verdict

**PASS** — no blocking findings remain. DS F1 fix confirmed correct; no regressions to prior PASS findings.
