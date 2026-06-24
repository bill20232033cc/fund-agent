# Evidence Confirm Productionization RR-09 Plan Re-review Controller Judgment

Verdict token:

`ACCEPT_RR_09_PLAN_FIX_READY_FOR_BRANCH_F_IMPLEMENTATION_NOT_READY`

## Scope

Controller judgment for the RR-09 plan-fix and targeted plan re-review:

- Plan: `docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md`
- Prior rejected judgment: `docs/reviews/evidence-confirm-productionization-rr-09-plan-controller-judgment-20260623.md`
- Plan-fix: `docs/reviews/evidence-confirm-productionization-rr-09-plan-fix-20260623.md`
- Targeted re-review: `docs/reviews/plan-review-20260623-233706.md`

No source code, tests, runtime, provider, PDF, PR, tag, release, or readiness promotion was performed by this judgment.

## Decision

The RR-09 plan-fix is accepted for the controller-required findings.

The next implementation gate is:

`RR-09 Branch F - Blocked-path Evidence Confirm Summary Propagation Implementation Gate`

Release/readiness remains `NOT_READY`.

## Direct Evidence

The prior rejected judgment required the plan-fix to:

- remove stale claims that EC does not execute or that quality gate precedes EC;
- split `017641 / 2024` into `R5a` quality-gate/QDII block correctness and `R5b` blocked-path EC summary propagation;
- route `R5b` to a narrow implementation plan carrying safe EC summary through `QualityGateBlockedError` / CLI blocked output;
- preserve exit code 2 and `quality_gate_status=block`;
- keep `R5a` as static/no-live root-cause disposition unless direct FQ rule evidence proves a QDII applicability defect;
- keep R1-R4 evidence-first before release disposition;
- preserve no provider/LLM, no live/PDF, no control-doc edit by implementation worker, no commit/push/PR/tag/release unless separately authorized.

The plan-fix artifact records those items as addressed with completion token `RR_09_PLAN_FIXED_READY_FOR_REREVIEW_NOT_READY`.

The targeted re-review artifact records:

- conclusion `pass-with-risks`;
- no material findings;
- Branch F limited to Service/UI exception contract and CLI display path;
- R1-R4, R5a, checklist, report-body rendering, provider-backed semantic default-on and release/readiness as separate residual destinations.

Static validation run during this controller pass:

```bash
rg -n "<stale EC ordering phrases>" docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md docs/reviews/evidence-confirm-productionization-rr-09-plan-fix-20260623.md docs/reviews/plan-review-20260623-233706.md
```

Result: no matches. Exit code 1 is the expected success signal.

```bash
git diff --check -- docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md docs/reviews/evidence-confirm-productionization-rr-09-plan-fix-20260623.md docs/reviews/plan-review-20260623-233706.md
```

Result: passed.

## Accepted Implementation Boundary

Branch F implementation may modify only:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`

Allowed behavior:

- Add optional safe `EvidenceConfirmProductionSummary` propagation through `QualityGateBlockedError`.
- Echo the same safe compact Evidence Confirm summary on CLI quality-gate-blocked output when present.

Required invariants:

- preserve exit code 2;
- preserve `quality_gate_status=block`;
- preserve report-body suppression on blocked path;
- do not expose excerpts, file paths, PDF/cache/source internals, provider payloads, or raw fact-level diagnostics;
- do not change quality-gate decision semantics;
- do not add checklist Evidence Confirm support;
- do not add report-body Evidence Confirm rendering;
- do not switch provider-backed semantic default-on;
- do not perform live/PDF/provider/LLM actions.

## Required Validation For Branch F

Minimum validation:

```bash
uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q --tb=short
git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Expected assertions:

- `QualityGateBlockedError` can carry optional safe Evidence Confirm summary without changing quality-gate status.
- CLI quality-gate-blocked output includes safe Evidence Confirm summary when present.
- Absent summary preserves current quality-gate-only blocked output.
- Exit code 2 and report-body suppression are preserved.

## Residual Risks

| Residual | Disposition |
|---|---|
| R1-R4 product CLI EC `fail` under `warn` remain fact-level root-cause unproven. | Deferred to RR-09 evidence/disposition gate. |
| R5a QDII quality-gate block correctness remains unproven. | Deferred to static/no-live FQ rule disposition or Branch E. |
| Checklist Evidence Confirm support remains deferred. | Separate gate. |
| Report-body Evidence Confirm rendering remains deferred. | Separate gate. |
| Provider-backed semantic production default remains deferred. | Separate gate. |
| Tag, release and release/readiness promotion remain blocked. | Separate release-boundary authorization and accepted evidence gate required. |

## Result

Plan-fix accepted. Proceed to Branch F implementation only.

Completion token: `ACCEPT_RR_09_PLAN_FIX_READY_FOR_BRANCH_F_IMPLEMENTATION_NOT_READY`
