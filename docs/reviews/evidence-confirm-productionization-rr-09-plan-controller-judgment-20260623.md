# Evidence Confirm Productionization RR-09 Plan Controller Judgment

Verdict token:

`RR_09_PLAN_REJECTED_NEEDS_PLAN_FIX_NOT_READY`

## Scope

Controller judgment for `docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md`.

No source, test, runtime, provider, PDF, PR, tag or release action was performed by this judgment.

## Decision

The RR-09 plan artifact is **rejected** and must return to a plan-fix gate before implementation or release-boundary disposition.

The artifact contains corrected direct code evidence in earlier sections, but section 7 and the recommended path still retain stale and false claims about the `017641 / 2024` blocked path.

## Direct Evidence

Static check:

```bash
rg -n "EC never runs|Evidence Confirm never runs|Quality gate runs BEFORE|_run_quality_gate_if_enabled runs before _run_evidence_confirm_if_enabled|quality gate block before EC|Branch D|Recommended path|RR_09_RESIDUAL_DISPOSITION_PLAN_READY_NOT_READY" docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md
```

Observed blockers:

- Line 227 still defines `Branch D: QUALITY-GATE/QDII DISPOSITION [RECOMMENDED]`.
- Line 255 still says: `Evidence Confirm never runs because the pipeline correctly terminates upstream`.
- Section 7 still frames `017641 / 2024` as `quality-gate block before EC`, contradicting direct code evidence in the same artifact.

The directly inspected service path is:

- `_run_analysis_core` computes `evidence_confirm_summary` before `_run_quality_gate_if_enabled`.
- `_run_quality_gate_if_enabled` receives `evidence_confirm_summary` for ECQ projection.
- `QualityGateBlockedError(quality_gate_result)` carries only the quality-gate result and drops the already-computed Evidence Confirm summary.

Therefore the `017641 / 2024` missing user-visible EC summary is not proven as "EC never runs"; it is a blocked-path propagation / exception-contract residual unless later direct evidence proves otherwise.

## Required Plan-fix

The next gate is `RR-09 Product CLI EC Fail / Quality-gate Residual Plan-fix Gate`.

The plan-fix must:

- remove stale claims that Evidence Confirm never runs or that quality gate runs before Evidence Confirm;
- split `017641 / 2024` into:
  - `R5a`: quality-gate/QDII block correctness root-cause disposition;
  - `R5b`: blocked-path Evidence Confirm summary propagation defect;
- route `R5b` to a narrow implementation plan that carries a safe Evidence Confirm summary through `QualityGateBlockedError` / CLI blocked output, if confirmed, while preserving exit code 2 and `quality_gate_status=block`;
- keep `R5a` as static/no-live root-cause disposition and only change quality gate if direct FQ rule evidence proves a QDII applicability defect;
- keep R1-R4 as evidence-first root-cause diagnostics before any release disposition;
- preserve no provider/LLM, no live/PDF, no control-doc edit by the implementation worker, no commit/push/PR/tag/release unless separately authorized.

## Agent Status

AgentDS partially corrected sections 3.1, 3.3, 3.4 and R5 inventory, but stalled before section 7 cleanup.

AgentMiMo was dispatched for a single-file plan-fix but also did not complete within the controller window.

The current artifact remains unaccepted.

## Validation

- `rg` stale-phrase check: failed as documented above.
- `git diff --check -- docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md`: passed.

## Result

Release/readiness remains `NOT_READY`.

Next entry point: `RR-09 Product CLI EC Fail / Quality-gate Residual Plan-fix Gate`.
