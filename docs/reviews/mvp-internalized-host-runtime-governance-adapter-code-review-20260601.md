# MVP internalized Host runtime governance adapter code review

Date: 2026-06-01
Gate: `MVP internalized Host runtime governance adapter implementation gate`
Role: code review

## Dispatch Note

Tmux review delegation was attempted first per `$init-agents`.

- AgentDS `agents:0.2`: `/clear` was sent twice; `tmux-cli capture` still showed stale `PR #21`, so no handoff was sent.
- AgentGLM `agents:0.4`: `/clear` was sent twice; `tmux-cli capture` still showed stale `PR #21`, so no handoff was sent.
- AgentMiMo had duplicate pane identities (`agents:0.3` and `0:0.2`), so no blind handoff was sent.

This artifact records local controller review because no clean review pane was available.

## Scope Reviewed

- `fund_agent/host`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/host`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- docs/readme/control sync files touched by this gate

## Finding 1 - Accepted

Severity: correctness

`_run_llm_analysis_in_host()` caught `QualityGateBlockedError` and `QualityGateNotRunBlockedError`, recorded a diagnostic, returned `None`, and only after `HostRuntimeRunner.run_sync()` returned did CLI re-raise the stored quality gate exception.

What could go wrong:

- Host emitted a successful terminal run (`run_completed`, `status=succeeded`) for an operation that actually failed the CLI command with exit code `2`.
- This violated the gate objective that Host owns terminal run state and safe diagnostics.
- It also made future event/outbox consumers observe a false successful run for a blocked analysis.

Evidence path:

- `fund_agent/ui/cli.py` `_run_llm_analysis_in_host()` operation closure caught quality gate exceptions and returned `None`.
- `HostRuntimeRunner.run_sync()` treats a normal return as `HostRunStatus.SUCCEEDED`.
- CLI then raised the saved exception outside the Host run.

Required fix:

- Do not swallow structured quality gate exceptions inside the Host operation.
- Record a safe diagnostic, then re-raise so Host produces `failed` and `run_failed`.
- CLI may still re-raise the saved typed quality gate exception after Host returns so user-facing exit code and stderr stay unchanged.
- Add regression assertions that LLM quality gate block/not-run paths do not leak a fake `status=succeeded`.

## Non-Findings

- Host package does not import Service/Fund.
- Host runner does not manage an asyncio event loop.
- Deterministic analyze/checklist remain outside Host.
- Direct `dayu-agent`, `dayu.host`, `dayu.engine` production dependency/import was not introduced.
- Incomplete LLM result now has Host failed terminal state and keeps stdout empty.

## Validation Reviewed

- Targeted tests passed before finding fix.
- Ruff passed before finding fix.
- Full pytest passed before finding fix.

## Verdict

Changes require fix and re-review for Finding 1 before accepted checkpoint.
