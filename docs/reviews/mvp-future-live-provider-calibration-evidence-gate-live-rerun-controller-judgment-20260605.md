# MVP Future Live Provider Calibration Evidence Gate — Live Rerun Controller Judgment

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Future live provider calibration evidence gate`
- Classification: `heavy`
- Role: controller judgment only; not evidence executor, reviewer, implementation/fix worker, or PR/release operator
- Evidence artifact: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-evidence-20260605.md`
- Evidence reviews:
  - `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-evidence-review-mimo-20260605.md`
  - `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-evidence-review-ds-20260605.md`
- Same-run retained artifact: `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/`

This judgment accepts only the live rerun evidence artifact correctness and residual classification. It does not accept the `Real LLM smoke re-baseline gate`, does not authorize a second live command, and does not enter any next gate.

## 2. Controller Self-Check

- Current role: controller.
- Allowed controller work: read evidence/reviews, decide findings, record durable judgment, update control/startup truth.
- Specialist work avoided: no source/test/config/runtime/provider implementation, no live provider command, no reviewer substitution.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, accepted plan `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`, and current same-run evidence/reviews.

## 3. Evidence Summary

The live rerun followed the accepted plan sequence:

- presence-only readiness passed without printing provider values or making HTTP calls;
- exactly one live command ran: `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`;
- no timeout/model/endpoint/attempt/backoff/max-output/provider overrides were used;
- command exited `1`, stdout byte count was `0`, and no deterministic fallback was used;
- retained artifact was produced at `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/`;
- all six body chapters failed at writer operation with `llm_network_error` / `ConnectError` / provider runtime category `network`;
- `orchestration_status=blocked` and `final_assembly_status=incomplete`;
- no chapter produced an accepted draft or accepted conclusion.

## 4. Review Integration

Both independent reviews verified the core evidence facts:

- plan sequence compliance: accepted;
- exactly one live command: accepted;
- fail-closed stdout/exit/no-fallback semantics: accepted;
- same-run retained artifact usage: accepted;
- secret/redaction safety: accepted;
- no unauthorized source/config/runtime/default/golden/score-loop/Agent/PR/release changes: accepted.

The reviews agreed that the evidence artifact's factual description is correct but that its Section 9 outcome label is wrong:

- MiMo classified the label mismatch as blocking until reclassified.
- AgentDS classified the label mismatch as non-blocking because controller can reclassify in judgment.

Controller decision: accept the finding. The evidence artifact's original `provider_runtime_residual_narrowed` label is superseded by this controller judgment and must be treated as `provider_runtime_error_non_timeout`.

## 5. Finding Decisions

| Finding | Source | Decision | Rationale |
|---|---|---|---|
| Outcome classification mismatch: evidence says `provider_runtime_residual_narrowed`, but same-run data is all-six-chapter `llm_network_error` / `ConnectError` with zero accepted conclusions | MiMo blocking; DS non-blocking | accepted, corrected in controller judgment | Accepted plan Section 6.3 requires a subset timeout / accepted-or-mixed split. Accepted plan Section 6.4 covers non-timeout provider runtime errors including `llm_network_error`. Same-run data matches Section 6.4, not Section 6.3. |
| A9 methodology used same-run evidence, but classification label was wrong | MiMo informational; DS pass with relabel recommendation | accepted as corrected | A9 is satisfied after this judgment because the residual classification is now explicitly `provider_runtime_error_non_timeout` and remains based on current same-run retained artifact evidence. |
| Post-evidence `pyproject.toml` tracked modification is unrelated to this gate | DS residual | deferred / out of scope | Current tracked diff exists in the workspace, but evidence execution recorded empty tracked diff before the live command. The `pyproject.toml` change is not accepted as current gate scope and must not be staged in this checkpoint. |

## 6. Controller Verdict

Verdict: `ACCEPTED_WITH_CORRECTED_CLASSIFICATION`.

Accepted residual classification: `provider_runtime_error_non_timeout`.

Direct evidence:

- readiness passed;
- the single live command reached provider calls;
- retained artifact and stderr safe summary report provider runtime failures other than timeout: all six body chapters failed with `llm_network_error` / `ConnectError` / provider runtime category `network`;
- fail-closed semantics remained intact.

This supersedes the evidence artifact's original `provider_runtime_residual_narrowed` label. No evidence rewrite or live re-execution is required because the retained artifact facts are sufficient and both reviews verified them.

## 7. Gate Status And Next Entry

`Future live provider calibration evidence gate` live rerun evidence correctness is accepted locally with corrected classification `provider_runtime_error_non_timeout`.

`Real LLM smoke re-baseline gate` remains not accepted. The current blocker is a same-run non-timeout provider runtime residual, not chapter content calibration evidence.

Next entry point: hand the same-run non-timeout provider residual to the provider runtime operator / future calibration controller. Do not retry, do not classify it as endpoint availability, and do not change provider/default/runtime/budget in this gate.

Explicitly unauthorized:

- second live provider command;
- endpoint reachability probe, PASS-only timing probe, retries, overrides, fallback, or private provider call;
- Chapter acceptance calibration, because no body chapter has an accepted draft or accepted conclusion;
- provider endpoint/model/default/runtime/budget changes without a separately reviewed gate;
- Agent runtime implementation, multi-year runtime, score-loop, golden/readiness, PR/push/release, deterministic fallback, or fail-closed relaxation.
