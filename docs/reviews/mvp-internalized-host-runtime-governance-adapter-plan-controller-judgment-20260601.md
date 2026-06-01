# MVP internalized Host runtime governance adapter plan controller judgment

Date: 2026-06-01
Gate: `MVP internalized Host runtime governance adapter plan gate`
Gate type: heavy plan gate
Role: Gateflow controller
Judgment: accepted plan checkpoint

## Decision

Accepted.

The plan is handoff-ready and code-generation-ready for a local Host runtime governance implementation that does not import or depend on `dayu-agent`, `dayu.host` or `dayu.engine`.

## Evidence

- Plan artifact: `docs/reviews/mvp-internalized-host-runtime-governance-adapter-plan-20260601.md`
- MiMo plan review: `docs/reviews/mvp-internalized-host-runtime-governance-adapter-plan-review-mimo-20260601.md`

MiMo conclusion: `pass-with-risks`, no blocking findings.

## Review Risks Folded Into Plan

The plan was amended after review to require:

- Host request carries an opaque synchronous operation closure instead of Service-layer `ChapterOrchestratorLLMClients` / policy types.
- `fund_agent/host` must not import `fund_agent.services` or `fund_agent.fund`.
- `HostRuntimeRunner.run_sync()` must not manage an asyncio event loop.
- CLI-owned operation closure is responsible for `asyncio.run(FundAnalysisService().analyze_with_llm(...))` from the synchronous Typer call site.
- `timeout_seconds` is the only deadline input; Host computes `deadline_at`.
- MVP `repair` phase events map to the current regenerate attempt boundary.
- Event ordering invariant is explicit and testable.

## Boundary Judgment

- Current implementation remains `CLI -> Service -> fund_agent/fund -> provider HTTP call`.
- Deterministic `analyze` and `checklist` remain unchanged.
- The implementation gate may create `fund_agent/host` for local Host runtime governance only.
- Host owns lifecycle, deadline/cancel classification, terminal state, safe diagnostics and run-local events.
- Service owns business semantics, prompt/ExecutionContract, provider clients, chapter policy and final assembly.
- No `dayu-agent`, `dayu.host` or `dayu.engine` dependency/import is allowed.
- No upstream Dayu code may be copied or rewritten without a later license/compliance gate.

## Next Entry Point

`MVP internalized Host runtime governance adapter implementation gate`

Approved slices:

1. Host domain model.
2. Host runner facade.
3. Service cancellation / deadline boundary.
4. CLI `--use-llm` Host entry.
5. Evidence, docs and validation.

## Required Implementation Validation

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- deterministic analyze `006597 / 2024` unchanged PASS
- deterministic checklist `006597 / 2024` unchanged PASS
- missing-config `--use-llm` fail-closed PASS
- real provider smoke `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`
- cancellation/deadline targeted tests PASS
- secret leak scan PASS
- no `dayu-agent`, `dayu.host`, `dayu.engine` production dependency/import
- no Host imports from `fund_agent.services` or `fund_agent.fund`

## Validation For This Plan Gate

- `git diff --check` PASS before review.
- Ruff/pytest were not run because this plan gate modified only review docs.

## Non-Goals Preserved

- No runtime/code/tests modified in this plan gate.
- No dependency files modified.
- No `fund_agent/host` created in this plan gate.
- No score, quality gate, golden, fixture promotion, release-readiness or PR state changed.
- No push, PR, merge, mark-ready or release action occurred.
