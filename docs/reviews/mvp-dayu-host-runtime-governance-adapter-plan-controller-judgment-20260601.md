# MVP dayu.host runtime governance adapter plan controller judgment

Date: 2026-06-01
Gate: `MVP dayu.host runtime governance adapter plan gate`
Gate type: heavy plan gate
Role: Gateflow controller
Judgment: accepted plan checkpoint

## Decision

Accepted.

The plan is handoff-ready and code-generation-ready for the next implementation gate. It keeps the current transition execution body intact while requiring `dayu.host` to own run lifecycle, global deadline, cancellation, terminal state and safe diagnostics for `fund-analysis analyze --use-llm`.

## Evidence

- Plan artifact: `docs/reviews/mvp-dayu-host-runtime-governance-adapter-plan-20260601.md`
- MiMo plan review: `docs/reviews/mvp-dayu-host-runtime-governance-adapter-plan-review-mimo-20260601.md`

MiMo conclusion: `pass-with-risks`, no blocking findings.

## Accepted Review Risks Folded Into Plan

The plan was amended after review to explicitly require:

- synchronous CLI adapter bridges async `FundAnalysisService.analyze_with_llm()` with `asyncio.run()`;
- adapter computes `started_at`, `deadline_at` and `completed_at` because `HostedRunContext` only carries `run_id` and `cancellation_token`;
- adapter uses `Host.run_operation_sync(..., on_cancel=...)` for fail-closed cancellation result;
- `timeout_seconds` to `HostedRunSpec.timeout_ms` conversion is tested;
- `phase_timeout` must be producible through a narrow Service-owned phase-budget check or the implementation must stop with a controller decision.

## Boundary Judgment

- Current implementation fact remains `CLI -> Service -> fund_agent/fund -> provider HTTP call`.
- The future implementation must add only a thin `fund_agent.host` direct-operation adapter around the existing Service LLM path.
- Host must not parse fund code, report year, CHAPTER_CONTRACT, prompt content, evidence anchors or score semantics as business logic.
- Service remains owner of business semantics, prompt/ExecutionContract assembly, chapter policy and provider client construction.
- `dayu.engine`, ToolRegistry, ToolTrace, Agent runner and tool loop remain out of scope.
- Deterministic `analyze` and `checklist` remain unchanged.
- The current provider blocker `provider_runtime_timeout_small_prompt` is not fixed by this plan; the implementation acceptance target is Host lifecycle correctness and safe timeout classification.

## Next Entry Point

`MVP dayu.host runtime governance adapter implementation gate`

Implementation must follow the accepted slices in the plan:

1. Host API and dependency preflight.
2. Host runtime adapter package.
3. Service cancellation and deadline propagation.
4. CLI `--use-llm` Host entry.
5. Diagnostic secret scan and runtime evidence.

## Required Implementation Validation

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- deterministic analyze `006597 / 2024` unchanged PASS
- deterministic checklist `006597 / 2024` unchanged PASS
- missing-config `--use-llm` fail-closed PASS
- real provider smoke: `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`
- cancellation/deadline tests PASS
- secret leak scan PASS
- no new `dayu.engine`, `ToolRegistry` or `ToolTrace` usage from this gate

## Non-Goals Preserved

- No runtime/code/tests were modified in this plan gate.
- No dependency files were modified in this plan gate.
- No score, quality gate, golden, fixture promotion, release-readiness or PR state changed.
- No push, PR, merge, mark-ready or release action occurred.
- Historical untracked residuals remain out of scope.

## Validation For This Plan Gate

Plan gate validation:

- `git diff --check` PASS before controller judgment.
- Final accepted checkpoint must stage only:
  - `docs/reviews/mvp-dayu-host-runtime-governance-adapter-plan-20260601.md`
  - `docs/reviews/mvp-dayu-host-runtime-governance-adapter-plan-review-mimo-20260601.md`
  - `docs/reviews/mvp-dayu-host-runtime-governance-adapter-plan-controller-judgment-20260601.md`

Ruff/pytest were not run for this docs-only plan gate because no runtime, code or tests changed.
