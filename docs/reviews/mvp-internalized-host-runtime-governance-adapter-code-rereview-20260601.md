# MVP internalized Host runtime governance adapter code re-review

Date: 2026-06-01
Gate: `MVP internalized Host runtime governance adapter implementation gate`
Role: code re-review

## Reviewed Fix

Accepted Finding 1 from `docs/reviews/mvp-internalized-host-runtime-governance-adapter-code-review-20260601.md` is fixed.

Fix evidence:

- `_run_llm_analysis_in_host()` now records the safe quality gate error type and re-raises `QualityGateBlockedError` / `QualityGateNotRunBlockedError` inside the Host operation.
- `HostRuntimeRunner.run_sync()` therefore sees the operation exception and emits a failed terminal state instead of a successful terminal state.
- CLI still re-raises the stored typed quality gate exception after Host returns, preserving existing user-facing quality gate stderr and exit code.
- `tests/ui/test_cli.py` asserts LLM quality gate block/not-run paths do not emit `status=succeeded` or an unrelated Host incomplete summary.

## Validation

| Command | Result |
|---|---|
| `uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q` | PASS, `76 passed in 1.25s` |
| `uv run ruff check .` | PASS |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, `1221 passed in 5.61s`, total coverage `91.92%` |

## Residual Risks

- Live provider smoke could not run in this shell because `FUND_AGENT_LLM_*` env config is absent. This is already recorded in implementation evidence and does not change the local Host correctness verdict.
- Durable session/resume/memory/outbox remains future Host scope by plan.

## Verdict

PASS. No accepted findings remain for this implementation gate.
