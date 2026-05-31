# MVP internalized Host runtime governance adapter implementation evidence

Date: 2026-06-01 07:06:48 CST
Gate: `MVP internalized Host runtime governance adapter implementation gate`
Gate type: heavy implementation gate
Role: implementation evidence

## Scope Self-Check

- Current gate: `MVP internalized Host runtime governance adapter implementation gate`.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/reviews/mvp-internalized-host-runtime-governance-adapter-plan-20260601.md`, and plan controller judgment.
- Scope boundary: local, process-scoped Host runtime governance for explicit `fund-analysis analyze --use-llm`; no next gate work.
- Non-goals preserved: no `dayu-agent`, no `dayu.host` / `dayu.engine` production runtime dependency, no Agent runner/tool loop, no score/golden/quality gate semantic change, no deterministic fallback.
- The older `docs/reviews/mvp-dayu-host-runtime-governance-adapter-implementation-preflight-20260601.md` remains blocked evidence for the superseded direct `dayu.host` path and is not restored as the current implementation route.

## Changed Scope

Current gate files:

- `fund_agent/host/__init__.py`
- `fund_agent/host/runtime.py`
- `fund_agent/host/README.md`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/host/test_runtime_state.py`
- `tests/host/test_runtime_runner.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `fund_agent/README.md`
- `fund_agent/config/README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`

Unrelated untracked historical/release artifacts remain unstaged and are not part of this accepted gate unless a later artifact-disposition gate accepts them.

## Implementation Summary

- Added `fund_agent.host` with internalized Host runtime governance types: run status, cancellation reason, timeout classification, safe events, safe diagnostics, cancellation token, run context, and `HostRuntimeRunner`.
- `HostRuntimeRunner.run_sync()` accepts an opaque synchronous operation closure, computes run ID, timestamps, `deadline_at`, elapsed time, terminal status, safe diagnostics and run-local events. It does not import Service/Fund and does not manage an asyncio event loop.
- Added Service and chapter orchestration `host_context` boundary checks at stable phase boundaries: before writer, before auditor, before repair/regenerate boundary and before final assembly.
- Added safe phase events for writer, auditor, repair and final assembly.
- Routed only explicit CLI `analyze --use-llm` through Host. Deterministic `analyze` and `checklist` remain outside Host.
- CLI-owned closure bridges async Service with `asyncio.run(...)`; Host runner stays synchronous.
- Incomplete LLM final assembly now forms a Host failed terminal result and stderr includes both existing safe LLM incomplete details and safe Host run summary. Stdout remains empty and no deterministic fallback occurs.
- Documentation synced to the current internalized Host route and corrected stale “future direct dayu runtime” wording.

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q` | PASS, `76 passed in 1.25s` after code-review fix |
| `uv run ruff check .` | PASS after code-review fix, `All checks passed!` |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS after code-review fix, `1221 passed in 5.61s`, total coverage `91.92%` |
| `uv run fund-analysis analyze 006597 --report-year 2024 --dev-override --quality-gate-policy off` | PASS, exit `0`, rendered chapters `0-7`, quality gate not run because `policy=off` |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, exit `0`, `overall_signal: yellow`, `overall_status: watch` |
| `env -u FUND_AGENT_LLM_PROVIDER -u FUND_AGENT_LLM_BASE_URL -u FUND_AGENT_LLM_API_KEY -u FUND_AGENT_LLM_MODEL uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | PASS fail-closed, exit `1`, stdout empty, stderr `LLM provider 配置错误：missing FUND_AGENT_LLM_PROVIDER` |
| `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | ENV BLOCKED: current shell has no `FUND_AGENT_LLM_*` configuration, so this reproduces missing-config fail-closed instead of live provider smoke |
| `env | rg '^FUND_AGENT_LLM_(...)'` | No matches; confirms live provider smoke blocked by absent env, not by Host implementation |
| `rg -n "fund_agent\\.services|fund_agent\\.fund" fund_agent/host` | PASS, no matches |
| `rg -n "^(from|import) dayu|dayu_agent|dayu\\.host|dayu\\.engine|dayu-agent" fund_agent tests pyproject.toml uv.lock` | PASS for production import/dependency; matches are documentation-only “do not depend” text |
| `git diff --check` | PASS |

## Safety Notes

- Host diagnostics reject forbidden diagnostic keys such as prompt, draft, raw provider/audit response, API key and Authorization header.
- Host event payloads accept only safe scalar values and truncate long strings.
- Provider runtime timeout classification remains owned by existing provider/runtime diagnostics. Host adds run-level terminal state and safe summary; it does not claim hard preemption of blocking provider HTTP calls.
- Live provider smoke was not executed against a configured provider in this shell. Acceptance evidence is local validation plus missing-config fail-closed; the current provider blocker remains `provider_runtime_timeout_small_prompt` from prior accepted evidence.

## Disposition

Code review found one accepted correctness issue: LLM quality gate exceptions were being swallowed inside the Host operation, so Host could emit a false `succeeded` terminal state before CLI re-raised the typed quality gate exception. The fix now records a safe diagnostic and re-raises inside the Host operation, so Host emits `failed`; CLI still preserves the typed quality gate exit behavior. Re-review passed.

Accepted checkpoint has not yet been created in this artifact.
