# EC-P4 Plan Targeted Re-Review

## Gate

- Review gate: `plan targeted re-review`
- Reviewer: AgentDS
- Classification: `heavy`
- Timestamp: `2026-06-22 21:36 Asia/Shanghai`
- Verdict: **PASS**

## Reviewed Targets

- Fixed plan: `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-plan-fix-20260622.md`
- Original DS review: `docs/reviews/plan-review-20260622-212138-ds-ec-p4-service-quality-integration.md`
- Original MiMo review: `docs/reviews/plan-review-20260622-212138-mimo-ec-p4-service-quality-integration.md`

## Scope

Targeted re-review only. Each accepted finding is checked against the fixed plan for direct evidence of resolution. No new findings, no expanded scope, no implementation.

## Finding Status Table

### DS Findings

| Finding | Severity | Status | Evidence |
|---|---|---|---|
| DS-PR-01 | HIGH | 已修复 | Plan §Goal now limits first implementation to `analyze` opt-in only (line 20-21); checklist EC CLI is deferred to later gate (line 256); Slice 3 explicitly omits checklist `--evidence-confirm-policy` (line 446); checklist stop condition added (line 432, 484) |
| DS-PR-02 | HIGH | 已修复 | Full 11-row combined blocking decision table added (lines 226-242) covering all quality_gate_policy × evidence_confirm_policy × EC status combinations with error type, exit behavior, and ECQ placement; error ordering invariant established (line 242) |
| DS-PR-03 | MEDIUM | 已修复 | Checklist remains default off/no runner; `FundChecklistResult` may carry shared field only for type symmetry but first-slice checklist is not CLI-invoked (lines 197, 369, 389) |
| DS-PR-04 | MEDIUM | 已修复 | Re-aggregation of `QualityGateResult.status` on combined FQ + ECQ issue list using `_aggregate_gate_status()` semantics explicitly required (line 321); new test `test_quality_gate_integration_ecq2_block_changes_gate_status_to_block` added (line 349) |
| DS-PR-05 | MEDIUM | 已修复 | `test_quality_gate_integration_boundary_no_repository_or_source_imports` added to Slice 1 test list (line 353) |
| DS-PR-06 | LOW | 已修复 | Slice 2 explicitly states `Depends on: Slice 1.` (line 366) |
| DS-PR-07 | LOW | 已修复 | Slice 3 specifies `EvidenceConfirmBlockedError` caught after `QualityGateBlockedError`, with ordering rationale (line 449) |

### MiMo Findings

| Finding | Severity | Status | Evidence |
|---|---|---|---|
| F-01 | MEDIUM | 已修复 | Plan adopts Option A: `summary=None` means EC not requested; quality gate helper emits `ECQ0/info reason=not_requested`; Service does not allocate summary for policy off (lines 163, 215, 339). Consistent two-tier behavior. |
| F-02 | MEDIUM | 已修复 | Runner-exception handling promoted to canonical state machine step 5 (line 220): convert to fail-closed summary with `runner_exception:<class_name>`, block/warn per policy, no unstructured exception propagation |
| F-03 | MEDIUM | 已修复 | Checklist EC support deferred; same resolution as DS-PR-01/03 (lines 20-21, 92, 256, 446) |
| F-04 | MEDIUM | 已修复 | `tests/fund/test_evidence_confirm_production.py` added to pytest validation command (line 615) |
| F-05 | LOW | 已修复 | Stable reason codes closed for EC-P4: `not_requested`, `policy_off`, `runner_exception:<class_name>`, `repository_failure:<reason>`, `invalid_request` (line 168) |
| F-06 | LOW | 已修复 | Duplicate repository load accepted for opt-in first slice; optimization assigned to future performance gate (lines 296, 664) |
| F-07 | LOW | 已修复 | Aggregate status precedence defined: `fail > warn > pass > not_run/not_applicable`, with `pathway_status="fail"` always producing aggregate `status="fail"` (lines 164, 342) |

### MiMo Open Questions

| Question | Status | Evidence |
|---|---|---|
| Source provenance summary in CLI | 已修复 | Recorded as optional future UI work, not required in EC-P4 (line 284) |
| Timestamp/run id in ECQ issue id | 已修复 | Explicitly forbidden in EC-P4 (line 284) |
| Semantic fields in Slice 1 summary type | 已修复 | Summary already reserves `semantic_status` field (line 147); kept `not_run` in deterministic slice |

## Regression Check

No regressions detected. The fix narrows scope (checklist deferred, analyze-only first implementation) without introducing new contradictions. The combined blocking decision table (lines 226-242) is internally consistent and covers all combinations. Policy-off semantics are now two-tier (Service returns `None`, quality gate helper emits `ECQ0`) with no contradiction.

## Remaining Blockers

None. All 7 DS findings and 7 MiMo findings are resolved. All 2 MiMo open questions are resolved.

## Residual Risks

| Risk | Owner | Disposition |
|---|---|---|
| Checklist Evidence Confirm CLI support deferred | Service/UI owner + controller | Assigned to later explicit checklist EC slice/gate |
| Duplicate repository load under opt-in EC | Fund documents owner | Accepted for opt-in first slice; future performance gate |
| Source provenance display not in EC-P4 summary | UI/product owner | Optional future UI work |
| `ECQ*` taxonomy may need calibration after implementation evidence | Quality gate owner | Start additive and provisional; review after implementation |
| Release/readiness | Release owner | Remains `NOT_READY`; no claim otherwise |

## Required Next Gate

- `implementation` (standard classification) per the fixed plan's Slice 1-6 order. Implementation must start with Slice 1 and respect all stop conditions, boundary constraints, and the combined blocking decision table.

## Validation

```bash
git diff --check -- docs/reviews/plan-review-rereview-20260622-213540-ds-ec-p4-service-quality-integration.md
```
