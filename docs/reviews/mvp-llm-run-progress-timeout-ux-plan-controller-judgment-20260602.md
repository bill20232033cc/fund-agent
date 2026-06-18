# Controller Judgment: MVP LLM Run Progress And Timeout UX Plan Acceptance

## Self-check

- Phase: `MVP real LLM observability and chapter acceptance phase`.
- Gate: `MVP LLM run progress and timeout UX gate`.
- Role: controller only.
- Work type: plan acceptance judgment and local checkpoint bookkeeping.
- Scope boundary: no runtime code, tests, provider budget, chapter acceptance calibration, score-loop, golden/readiness, push, PR, or mark-ready action.
- Source of truth: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, the updated plan, both independent plan reviews, controller review judgment, fix evidence, and both re-reviews.

## Inputs

| Purpose | Artifact |
|---|---|
| Updated plan | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md` |
| AgentDS plan review | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-review-ds-20260602.md` |
| AgentMiMo plan review | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-review-mimo-20260602.md` |
| Controller review judgment | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-review-controller-judgment-20260602.md` |
| Plan fix evidence | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-fix-evidence-20260602.md` |
| AgentDS plan re-review | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-rereview-ds-20260602.md` |
| AgentMiMo plan re-review | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-rereview-mimo-20260602.md` |

## Review Outcome

Both independent reviewers passed the fixed plan.

| Reviewer | Verdict | Blocking findings |
|---|---|---|
| AgentDS | `ALL ACCEPTED FIXES VERIFIED -- PLAN IS CODE-GENERATION-READY` | None |
| AgentMiMo | `PASS -- no blocking plan findings remain` | None |

## Accepted Finding Disposition

| Finding | Controller disposition | Evidence |
|---|---|---|
| DS F1 / MiMo F3: heartbeat lifecycle underspecified | accepted and fixed in plan | The plan now requires CLI-owned `threading.Event`, one shared lock, lock-protected state, bounded stop/join, post-terminal no-heartbeat guarantee, and deterministic `_heartbeat_tick()` tests. |
| DS F2 / MiMo F2: `event_sink` failure semantics ambiguous | accepted and fixed in plan | The plan now assigns no-raise safety to the CLI reporter, leaves Host sink invocation uncaught/untranslated, and requires tests proving progress sink failure cannot affect terminal state or exit behavior. |
| DS F3: `event_sink` integration point unspecified | accepted and fixed in plan | The plan now requires one Host-local event commit helper: construct safe event, append to `HostRunResult.events`, then call the sink with that same committed event. |
| MiMo F1: Service test name mismatch | accepted and fixed in plan | The plan now references `test_host_runner_records_llm_service_phase_events` and requires `analysis_core` phase events before writer events. |

Non-blocking guidance from both reviewers was incorporated where it improved implementation precision: TTY auto-detection helper, `run_terminal` source from `HostRunResult.elapsed_ms`, non-overfitted progress assertions, and narrowed secret canaries.

## Controller Decision

The plan is accepted as code-generation-ready for the implementation gate.

Based on the design and control truth, this is the best current plan because it makes long-running real `--use-llm` execution observable through safe stderr-only progress while preserving the already accepted fail-closed behavior: stdout remains reserved for final accepted reports, deterministic `analyze/checklist` remain unaffected, Host remains business-agnostic, and provider timeout budget / chapter acceptance calibration / score-loop work stay out of this gate.

## Required Implementation Guardrails

- Implement only Slice P1 live safe progress UX from the accepted plan.
- Keep progress output stderr-only and prefixed with `LLM progress:`.
- Preserve incomplete-result behavior: exit code `1`, empty stdout, no deterministic fallback, and no fake success.
- Do not expose prompts, drafts, raw provider responses, raw auditor responses, API keys, Authorization headers, cookies, model names, full config, or arbitrary diagnostics.
- Do not change provider timeout/retry/backoff budgets, chapter acceptance logic, auditor strictness, artifact retention schema, score/golden/readiness semantics, or PR state.
- Do not introduce `dayu-agent`, `dayu.host`, or `dayu.engine`.
- Keep Host generic: no fund business fields, no ExecutionContract business inspection, and no explicit business parameters in `extra_payload`.

## Required Implementation Validation

The implementation evidence must record at minimum:

```bash
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
uv run ruff check .
```

If the implementation touches wider shared contracts, also run the broader relevant host/service/ui subset and explain the reason in evidence.

## Next Entry Point

Create an accepted plan checkpoint, update controller truth with that checkpoint, then dispatch the implementation handoff through `$init-agents`. The implementation worker must write durable implementation evidence under `docs/reviews/` and must not stage, commit, push, create PR, or mark ready.
