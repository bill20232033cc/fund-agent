# Evidence Confirm Productionization EC-P4 Plan Fix

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `plan fix`
- Classification: `heavy`
- Plan fixed: `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-plan-fix-20260622.md`
- Release/readiness: `NOT_READY`

## Accepted Findings Addressed

| Finding | Status | Plan fix |
|---|---|---|
| DS-PR-01 HIGH checklist CLI lacks developer override mode path | Addressed | First implementation is now `analyze` CLI opt-in only; checklist Evidence Confirm CLI support is deferred to a later explicit gate; checklist tests are removed from first implementation scope. |
| DS-PR-02 HIGH combined blocking semantics underspecified | Addressed | Added explicit decision table for `quality_gate_policy` off/warn/block x `evidence_confirm_policy` warn/block x EC pass/warn/fail, including preferred error type, exit behavior and ECQ placement. |
| DS-PR-03 MEDIUM checklist Service developer override resolution ambiguous | Addressed | Checklist remains default off/no runner; `FundChecklistResult` may carry a shared result field only for type symmetry, but first-slice checklist is not user-invoked via CLI. |
| DS-PR-04 MEDIUM missing status re-aggregation after ECQ merge | Addressed | Slice 1 now requires re-aggregating `QualityGateResult.status` on combined FQ + ECQ issues and adds `test_quality_gate_integration_ecq2_block_changes_gate_status_to_block`. |
| DS-PR-05 MEDIUM missing quality gate integration boundary static test | Addressed | Slice 1 now requires `test_quality_gate_integration_boundary_no_repository_or_source_imports`. |
| DS-PR-06 LOW Slice 2 dependency not explicit | Addressed | Slice 2 now states `Depends on: Slice 1`. |
| DS-PR-07 LOW CLI handler ordering unspecified | Addressed | Slice 3 now catches `EvidenceConfirmBlockedError` after `QualityGateBlockedError`; EC-only blocking is limited to quality gate off/not runnable or quality warn plus EC block/fail. |
| MiMo F-01 MEDIUM policy off summary contradiction | Addressed | Plan uses option A: `summary=None` means EC not requested; quality gate helper may emit `ECQ0/info reason=not_requested`; Service does not allocate a summary for policy off. |
| MiMo F-02 MEDIUM runner exception handling outside canonical state machine | Addressed | State machine now converts runner exceptions to fail-closed summaries with `runner_exception:<class_name>`. |
| MiMo F-03 MEDIUM checklist ambiguity | Addressed | Same resolution as DS-PR-01/03: analyze-only first implementation; checklist EC slice deferred. |
| MiMo F-04 MEDIUM missing new test file in validation command | Addressed | Validation command now includes `tests/fund/test_evidence_confirm_production.py`. |
| MiMo F-05 LOW reason string stability | Addressed | Plan defines stable reason codes: `not_requested`, `policy_off`, `runner_exception:<class_name>`, `repository_failure:<reason>`, `invalid_request`. |
| MiMo F-06 LOW duplicate repository load | Addressed | Plan accepts duplicate repository load for opt-in first slice and assigns optimization to a future performance gate. |
| MiMo F-07 LOW aggregate status precedence | Addressed | Plan specifies precedence `fail > warn > pass > not_run/not_applicable`, with pathway fail producing aggregate fail. |
| MiMo open question: source provenance summary | Addressed | Plan records safe `source_provenance` display summary as optional future UI work, not required in EC-P4. |
| MiMo open question: timestamp/run id in ECQ issue id | Addressed | Plan forbids timestamp/run id in ECQ issue ids for EC-P4. |

## Changed Sections Summary

- `Goal / Motivation / Success Signal`: narrowed first implementation to `analyze` opt-in and deferred checklist EC CLI support.
- `Controller Artifact Five Questions`: resolved checklist policy as analyze-only first slice.
- `Contract / Schema / State-Machine / Public Interface Changes`: added stable reason codes, aggregate status precedence, policy-off `summary=None` semantics, runner-exception fail-closed handling and full combined blocking table.
- `CLI public interface`: limited EC flag to `analyze`, fixed checklist deferral and handler ordering.
- `Quality gate issue taxonomy`: clarified `ECQ0` reason behavior and ECQ issue id stability; no timestamp/run id.
- `Small Implementation Slices`: added Slice 2 dependency, status re-aggregation requirement, ECQ2 status test, quality-gate-integration boundary test and checklist stop conditions.
- `Tests / Validation Commands`: added `tests/fund/test_evidence_confirm_production.py`.
- `Risks / Open Questions / Residual Owners`: added checklist EC CLI deferred residual and duplicate repository load performance residual.

## Validation Result

- PASS. Command returned exit code `0` with no output:

```bash
git diff --check -- docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md docs/reviews/evidence-confirm-productionization-ec-p4-plan-fix-20260622.md
```

## Residual Risks

| Residual | Owner | Disposition |
|---|---|---|
| Checklist Evidence Confirm CLI support | Service/UI owner + controller | Assigned to later explicit checklist EC slice/gate; not part of first implementation. |
| Duplicate repository load under opt-in EC | Fund documents owner | Accepted for opt-in first slice; optimization belongs to future performance gate. |
| Source provenance display summary | UI/product owner | Optional future UI work; not required for EC-P4. |
| Release/readiness | Release owner/controller | Remains `NOT_READY`; no mark-ready, merge, push, PR mutation or release transition authorized. |

## Verdict

`PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`
