# Evidence Confirm Productionization RR-09 Plan-fix

Verdict token:

`RR_09_PLAN_FIXED_READY_FOR_REREVIEW_NOT_READY`

## Scope

Plan-fix for `docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md`.

Controller judgment input:

- `docs/reviews/evidence-confirm-productionization-rr-09-plan-controller-judgment-20260623.md`
- Rejected token: `RR_09_PLAN_REJECTED_NEEDS_PLAN_FIX_NOT_READY`

No source code, tests, README, control docs, PR state, tag, release, live/PDF, provider, or LLM action was performed by this plan-fix.

## Required Fixes Addressed

| Required fix from controller judgment | Plan-fix result |
|---|---|
| Remove stale claims that EC does not execute or that quality gate precedes EC. | Removed the stale section 7 / recommended-path claims and rewrote the closeout language to state that EC already executes before quality gate. |
| Split `017641 / 2024` into quality-gate/QDII block correctness and blocked-path EC summary propagation. | Split R5 into `R5a` and `R5b` in the residual inventory, decision tree, docs/control sync decision, residual owner table, and completion report format. |
| Route `R5b` to a narrow implementation plan that carries a safe Evidence Confirm summary through `QualityGateBlockedError` / CLI blocked output if confirmed. | Added Branch F and Slice F-1, limited to Service/UI exception contract and CLI blocked-output propagation. |
| Preserve exit code 2 and `quality_gate_status=block`. | Branch F invariants explicitly preserve exit code 2, `quality_gate_status=block`, report-body suppression, and no quality-gate decision change. |
| Keep `R5a` as static/no-live root-cause disposition unless direct FQ rule evidence proves a QDII applicability defect. | Branch D now requires static/no-live FQ rule evidence; Branch E remains the only quality-gate fix path. |
| Keep R1-R4 evidence-first before release disposition. | Branch A now requires fact-level diagnostic evidence before reclassifying R1-R4 as accepted known behavior. |
| Preserve no provider/LLM, no live/PDF, no control-doc edit, no commit/push/PR/tag/release. | Non-goals remain explicit; this artifact records no such action. |

## Direct Code Evidence Preserved

The plan continues to cite the current Service path:

- `fund_agent/services/fund_analysis_service.py` computes `evidence_confirm_summary` before `_run_quality_gate_if_enabled`.
- `_run_quality_gate_if_enabled` receives `evidence_confirm_summary` for ECQ projection.
- `QualityGateBlockedError(quality_gate_result)` carries only `quality_gate_result`, so the already-computed safe Evidence Confirm summary is unavailable to CLI blocked-output handling.
- CLI currently handles `QualityGateBlockedError` by echoing only the quality-gate blocked summary, then exits 2.

## Validation

Commands run:

```bash
rg -n "<stale EC ordering phrases>" docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md
```

Result: no matches. Exit code 1 is the expected success signal for this stale-phrase check.

```bash
rg -n "RR_09_RESIDUAL_DISPOSITION_PLAN_READY_NOT_READY" docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md
```

Result: verdict token present.

```bash
rg -n "RR-S2|RR-S4|RR-S6|release-boundary-residual-routing|design.md|implementation-control.md" docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md
```

Result: required references present.

```bash
git diff --check -- docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md
```

Result: passed.

## Residual Risks

| Residual | Classification | Owner / Destination |
|---|---|---|
| R1-R4 product CLI EC `fail` under `warn` still need fact-level root-cause evidence before release disposition. | `needs-more-evidence` | RR-09 disposition / evidence gate |
| R5a `017641 / 2024` quality-gate/QDII block correctness is not closed by this plan-fix. | `needs-more-evidence` | Static/no-live FQ rule disposition or Branch E |
| R5b blocked-path safe EC summary propagation is now routed but not implemented. | `needs_implementation` | Branch F implementation gate after plan re-review acceptance |
| Release/readiness remains `NOT_READY`. | `tracked` | Release-boundary gate |
| Checklist, report-body rendering, provider-backed semantic default-on, tag and release remain separate gates. | `deferred_with_owner` | Separate future gates |

## Result

The RR-09 plan artifact is fixed for targeted re-review.

Next entry point:

`RR-09 Product CLI EC Fail / Quality-gate Residual Plan Re-review Gate`

Completion token: `RR_09_PLAN_FIXED_READY_FOR_REREVIEW_NOT_READY`
