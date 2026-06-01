# MVP internalized Host runtime governance adapter controller judgment

Date: 2026-06-01
Gate: `MVP internalized Host runtime governance adapter implementation gate`
Gate type: heavy implementation gate
Role: Gateflow controller
Judgment: accepted local implementation checkpoint

## Decision

Accepted locally.

The implementation adds a process-local internalized Host runtime governance adapter for explicit `fund-analysis analyze --use-llm` without adding `dayu-agent`, `dayu.host` or `dayu.engine` as production runtime dependencies.

## Evidence

- Plan: `docs/reviews/mvp-internalized-host-runtime-governance-adapter-plan-20260601.md`
- Plan controller judgment: `docs/reviews/mvp-internalized-host-runtime-governance-adapter-plan-controller-judgment-20260601.md`
- Implementation evidence: `docs/reviews/mvp-internalized-host-runtime-governance-adapter-implementation-evidence-20260601.md`
- Code review: `docs/reviews/mvp-internalized-host-runtime-governance-adapter-code-review-20260601.md`
- Code re-review: `docs/reviews/mvp-internalized-host-runtime-governance-adapter-code-rereview-20260601.md`

## Accepted Finding Disposition

One accepted correctness finding was fixed:

- LLM quality gate exceptions are no longer swallowed inside the Host operation. They now record a safe diagnostic and re-raise so Host emits `failed` instead of a false `succeeded`; CLI still preserves typed quality gate exit behavior.

Re-review passed with no remaining accepted findings.

## Validation

- `uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q`: PASS, `76 passed`
- `uv run ruff check .`: PASS
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: PASS, `1221 passed`, coverage `91.92%`
- Deterministic analyze `006597 / 2024 --dev-override --quality-gate-policy off`: PASS
- Deterministic checklist `006597 / 2024`: PASS
- Missing-config `--use-llm`: PASS fail-closed, exit `1`, stdout empty
- Host reverse-import scan: PASS, no `fund_agent.services` or `fund_agent.fund` imports under `fund_agent/host`
- Production Dayu dependency/import scan: PASS; remaining matches are documentation-only “do not depend” constraints
- `git diff --check`: PASS

Live provider smoke could not run in this shell because no `FUND_AGENT_LLM_*` env config was present. This does not change the prior accepted provider residual: `provider_runtime_timeout_small_prompt`.

## Boundary Judgment

- Default deterministic `analyze/checklist` bypass Host and remain unchanged.
- Explicit `analyze --use-llm` now runs through `CLI -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`.
- Host owns process-local run lifecycle, global deadline, cancel token, terminal state, safe diagnostics and run-local phase events.
- Host does not import Service/Fund, construct provider clients, inspect fund business semantics, implement Agent tool loop, or claim hard preemption of synchronous provider I/O.
- Durable session/resume/memory/reply outbox and internalized Agent engine/tool-loop remain future gates.
- The blocked direct `dayu.host` preflight remains historical blocked evidence and is not restored as the current route.

## Next Entry Point

`MVP Service ExecutionContract boundary hardening gate` remains the next entry point, but this checkpoint does not enter that gate.
