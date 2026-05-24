# Release Maintenance 004393 Quality Gate Plan Review Controller Judgment - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `release-maintenance candidate selection / plan-review`
- Work unit: `004393/2024 quality gate block root-cause investigation`
- Plan under review: `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
- Handoff: `docs/reviews/release-maintenance-004393-quality-gate-plan-handoff-20260524-080633.md`
- Reviews:
  - `docs/reviews/release-maintenance-004393-quality-gate-plan-review-mimo-20260524.md`
  - `docs/reviews/release-maintenance-004393-quality-gate-plan-review-glm-20260524.md`
- Controller conclusion: `plan fix required`

## Review Summary

| Reviewer | Conclusion | Controller disposition |
|---|---|---|
| MiMo | `fail` | Accept material blockers |
| GLM | `fail` | Accept material blockers |

Both reviews agree that the selected candidate remains valid, but the current plan is not yet code-generation-ready. The blockers are plan-specification failures, not implementation failures.

## Accepted Findings

| ID | Source | Finding | Controller decision | Required plan fix |
|---|---|---|---|---|
| `004393-PLAN-C1` | MiMo PR-A, GLM PR-004393-1 | S0 evidence command and S5 smoke command are not executable gate proofs. | Accepted. A plan whose first evidence command and final smoke command can fail due to command syntax or stale CLI flags is not handoff-ready. | Replace suggested evidence command with an executable command or temporary-script pattern; require command exit code and per-fact evidence checklist in S0. Change smoke command to current CLI `--report-year 2024`; require exact command/result in implementation report. |
| `004393-PLAN-C2` | MiMo PR-B, GLM PR-004393-2 | `holdings_snapshot` status/source contract is underspecified and could hide stock-holdings absence behind an overall direct field. | Accepted. Quality gate semantics cannot depend on optional nested metadata that score/gate may ignore. | Fix a minimal machine-readable contract before implementation: either define required snapshot/score/gate handling for stock-holdings substatus or keep schema unchanged and restrict S2 to extractor-visible behavior without claiming gate coverage. Add tests that prove industry-only evidence does not satisfy stock-holdings coverage silently. |
| `004393-PLAN-C3` | MiMo PR-C, GLM PR-004393-4 | `turnover_rate` disclosure applicability is over-coupled with the direct extraction/correctness fixes. | Accepted. This is a policy/schema/gate denominator change across extractor/snapshot/score/quality gate and must not be hidden inside the 004393 extraction plan. | Split S3 into a separate follow-up Gateflow candidate: `turnover_rate disclosure applicability / quality gate denominator policy`. Current plan may record S3 as deferred owner and classify any remaining 004393 turnover block as accepted deferred applicability, not as a direct extraction bug. |
| `004393-PLAN-C4` | MiMo PR-D | Golden updates lack row-level approval and scope. | Accepted. Plan review cannot itself authorize correctness oracle changes. | Make S4 a separate controller approval gate after S0 evidence and relevant extractor tests. The plan must state default allowed rows are none until an approval artifact lists fund/field/subfield/current/new/evidence/build command. Holdings golden expansion and turnover applicability notes default to deferred unless explicitly approved. |
| `004393-PLAN-C5` | GLM PR-004393-3 | `share_change` A/C selection relies on current fund class evidence that is not available inside the S2 boundary as written. | Accepted. The plan correctly bans fund-code suffix inference but does not give implementation a safe evidence route. | Specify the direct same-source route for share-class identity. Preferred narrow fix: within `holdings_share_change.py`, use `ParsedAnnualReport.get_section_text("§2")` or §2 parsed table evidence to identify explicit A/C class, with fail-closed tests. If passing profile-derived identity through `data_extractor.py` is chosen instead, it must be declared as expanded S2 scope and reviewed. |

## Deferred / Non-Blocking Notes

- Benchmark normalization direction is acceptable if it remains field-aware for benchmark fields only and includes negative tests for non-benchmark fields.
- P0 `basic_identity` and `fee_schedule` extraction direction appears implementable after S0 evidence is made executable.
- Parser variability remains a residual risk for code review and implementation reports, not a reason to reject the candidate.

## Controller Scope Decision

The next plan revision must narrow the immediate implementation scope to:

1. S0 executable evidence artifact.
2. S1 P0 extraction/comparable fields for `basic_identity` and `fee_schedule`.
3. S2 P1 extraction/correctness for `holdings_snapshot`, `share_change`, and benchmark normalization, after fixing the holdings and share-class contracts.
4. S4 as a controller-approved golden-change gate only, not automatic implementation scope.
5. S5 validation that has two paths:
   - if turnover applicability is deferred, classify any remaining `turnover_rate` gate issue as accepted deferred policy scope;
   - if a later independent turnover plan is accepted, require a separate smoke expectation.

`turnover_rate disclosure applicability / quality gate denominator policy` is a separate future release-maintenance candidate and must receive its own plan/review before any source/test/config/runtime behavior changes.

## Next Action

Return the plan to planning specialist for a plan fix. Do not enter implementation until MiMo/GLM re-review, or equivalent independent plan re-review, passes and controller creates an accepted plan checkpoint.
