# P19 Control Update（2026-05-22）

## Verdict

`ACCEPTED_PENDING_PLAN_REVIEW`

P19 thermometer independent development is opened in `docs/implementation-control.md`. This is a planning/control update, not implementation authorization.

## Inputs

| Input | Role |
|---|---|
| `docs/p19-thermometer-technical-proposal.md` | Technical proposal |
| `docs/design-md-v22-changes.md` | Proposed design changes |
| `docs/p19-phase-definition.md` | Phase definition |
| `docs/reviews/p19-design-update-20260522.md` | Design fusion judgment |
| `docs/implementation-control.md` | Control truth |

## Control Changes

- Startup Packet now points to `P19 plan review`.
- Added P19 input and design/control artifact rows.
- Added P19 design/control update row to Active Gate Ledger.
- Added P19 row to Phase History Index and created `Archive: P19`.
- Added full P19 phase definition: goal, design-truth update, entry criteria, P19/P19-S1/S2/S3/S4 exit criteria, hard constraints, dependencies, residuals, non-goal reminder, and resume checklist.

## Corrections Against Input

| Input claim | Controller correction |
|---|---|
| P18 must be merged or parallel decision required | Current control state has no active P18 gate. P17 is merged, and P19 can open directly unless later planning redefines P18. |
| P19 overall should immediately provide `analyze` automatic valuation state | Split by gate: P19-S1/S2 build readings and CLI; P19-S3 owns automatic `valuation_state` mapping. |
| Parquet dependency is assumed | `pyarrow` or `fastparquet` remains a plan-review decision because the project does not currently declare either dependency. |
| akshare availability is assumed | Availability must be verified before implementation; current dependency presence is not sufficient evidence of interface stability. |

## Plan Review Must Answer

1. What is the reuse strategy for current `ThermometerService` and `FundThermometerAdapter`?
2. What are the first-run historical download time and storage estimates for P19-S1?
3. What deviation standard is acceptable between equal-weight calculation and Youzhiyouxing output?
4. Which akshare interfaces and fields are actually available for all-A PE/PB and index-level PE/PB?
5. Is parquet justified for P19-S1, and if so which dependency is accepted?

## Next Gate

`P19 plan review / data-source feasibility validation`.
