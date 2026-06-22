# Code Review: EC-P4 Slice 1 - Fund Summary + Quality Gate ECQ Projection

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `code review`
- Classification: `heavy`
- Slice: `Slice 1 - Fund Summary + Quality Gate ECQ Projection`
- Branch: `evidence-confirm-productionization`
- Release/readiness: `NOT_READY`
- Reviewer: AgentMiMo
- Timestamp: `2026-06-22 21:48 Asia/Shanghai`

## Verdict

`PASS_WITH_FINDINGS`

## Reviewed Target

- `fund_agent/fund/evidence_confirm_production.py` (new)
- `fund_agent/fund/quality_gate.py` (modified: `QualityGateIssue.issue_id` field, `merge_quality_gate_issues()`)
- `fund_agent/fund/quality_gate_integration.py` (modified: ECQ projection helpers, `evidence_confirm_summary` parameter)
- `tests/fund/test_evidence_confirm_production.py` (new)
- `tests/fund/test_quality_gate.py` (unchanged)
- `tests/fund/test_quality_gate_integration.py` (modified: ECQ mapping tests, boundary test)

Validation results:

- `uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q` → 44 passed in 0.49s
- `uv run ruff check ...` → All checks passed
- `git diff --check ...` → no whitespace errors

## Summary

Slice 1 implementation is structurally correct and faithfully follows the accepted plan. The compact `EvidenceConfirmProductionSummary` type correctly excludes raw excerpts, PDF/cache paths, parser JSON, source adapter objects and provider results. The ECQ issue family (ECQ0/ECQ1/ECQ2/ECQ3) maps correctly to the plan's taxonomy with stable issue IDs free of timestamps and run IDs. The `merge_quality_gate_issues()` helper correctly re-aggregates status using existing `_aggregate_gate_status()` semantics and rewrites `quality_gate.json`/`quality_gate.md` without touching `score.json`. The boundary constraint is satisfied: `quality_gate_integration.py` imports no repository, source adapter, parser, Docling, provider or LLM module. Backward compatibility is preserved: `run_quality_gate_for_bundle()` without `evidence_confirm_summary` produces zero ECQ issues.

Findings are minor: one missing test for the summary-absent ECQ0 path, one missing test for ECQ1 pathway-failure mapping, and one observation about ECQ2/warn policy coverage. None are blockers.

## Findings

### F-01 [LOW] Missing integration test for summary=None → ECQ0/info path

- **File/Line**: `tests/fund/test_quality_gate_integration.py`
- **Issue**: The plan requires `test_quality_gate_integration_maps_not_run_to_ecq0_info`. This test exists but uses an explicit `not_run_evidence_confirm_summary(policy="off", reason="policy_off")`. There is no test passing `evidence_confirm_summary=None` to `run_quality_gate_for_bundle()` and asserting that the quality gate result contains zero ECQ issues (the "summary absent" path). The `_evidence_confirm_quality_gate_issues(summary=None, ...)` branch that emits `ECQ0/info reason=not_requested` is exercised only by the integration call path where `evidence_confirm_summary is not None` is False, so the branch is never hit in tests.
- **Why it matters**: The plan distinguishes between "summary=None means EC was not requested" (no ECQ issues emitted) and "explicit not-run summary" (ECQ0/info emitted). The current test only covers the latter. If a future refactor changes the `if evidence_confirm_summary is not None` guard, the summary-absent behavior would be untested.
- **Required fix**: Add a test `test_quality_gate_integration_summary_none_produces_no_ecq_issues` that passes `evidence_confirm_summary=None` and asserts zero ECQ issues in the result. This is additive and does not require production code changes.
- **Suggested owner**: Implementation worker.

### F-02 [LOW] Missing integration test for pathway failure → ECQ1 mapping

- **File/Line**: `tests/fund/test_quality_gate_integration.py`
- **Issue**: The plan lists `test_quality_gate_integration_maps_evidence_confirm_fail_to_ecq2_block` and `test_quality_gate_integration_maps_evidence_confirm_warn_to_ecq3_warn`, but there is no explicit test for the ECQ1/pathway-failure mapping. The `test_summary_from_repository_fail_is_compact_and_no_excerpt` test in `test_evidence_confirm_production.py` covers summary creation from a repository failure, but does not verify the ECQ1 projection through `run_quality_gate_for_bundle()`.
- **Why it matters**: ECQ1 is a distinct rule code from ECQ2/ECQ3 with its own severity policy (`block` when EC policy `block`, otherwise `warn`). Without an integration test, a regression in the `summary.pathway_status == "fail"` branch of `_evidence_confirm_quality_gate_issues()` would not be caught.
- **Required fix**: Add a test `test_quality_gate_integration_maps_pathway_fail_to_ecq1_block` that constructs a summary with `pathway_status="fail"`, `policy="block"` and asserts ECQ1/block with correct `issue_id` and `reason`. Optionally add a `policy="warn"` variant asserting ECQ1/warn.
- **Suggested owner**: Implementation worker.

### F-03 [INFO] ECQ2/warn policy severity not directly tested via integration

- **File/Line**: `tests/fund/test_quality_gate_integration.py`
- **Issue**: The `_summary()` test helper always uses `policy="block"`. The ECQ2 mapping test (`test_quality_gate_integration_maps_evidence_confirm_fail_to_ecq2_block`) only verifies ECQ2/block. The ECQ3 test uses a summary with `policy="block"` but deterministic_status="warn" which correctly maps to ECQ3/warn (since ECQ3 severity is always warn per spec). However, there is no integration test verifying that a summary with `policy="warn"` and `deterministic_status="fail"` produces ECQ2/warn (not ECQ2/block).
- **Why it matters**: The `_ecq_policy_severity()` function returns `SEVERITY_WARN` for any policy != "block". This is correct by code inspection, but the warn-policy fail path is not exercised by an integration test.
- **Required fix**: Optional. Add a test variant with `policy="warn"` and `deterministic_status="fail"` asserting ECQ2 severity is "warn". This is a coverage improvement, not a correctness concern.
- **Suggested owner**: Implementation worker.

### F-04 [INFO] `_ecq_policy_severity` implicit off-policy handling

- **File/Line**: `fund_agent/fund/quality_gate_integration.py:264-279`
- **Issue**: `_ecq_policy_severity()` returns `SEVERITY_WARN` for policy="off". In practice this branch is unreachable because summaries with `policy="off"` have `status="not_run"` and are caught by the ECQ0 branch before ECQ1/ECQ2 mapping. However, the function does not explicitly document or guard against `policy="off"`.
- **Why it matters**: Defensive coding would add a comment or assertion. This is a code clarity observation, not a runtime risk.
- **Required fix**: None required. An inline comment noting the off-policy unreachability would be sufficient if the owner chooses to add one.
- **Suggested owner**: Quality gate owner.

## Residual Risks / Uncovered Areas

| Residual | Owner | Notes |
|---|---|---|
| ECQ4 semantic companion projection | Semantic owner | Deferred to Slice 5; deterministic Slice 1 correctly returns empty tuple for pass/ECQ4-free path. |
| Service propagation (Slice 2) | Service owner | Slice 1 only covers Fund-layer summary + quality gate projection. Service request/result contracts, dependency injection and blocking semantics are Slice 2 scope. |
| CLI/UI summary and exit behavior (Slice 3) | UI owner | Not in Slice 1 scope. |
| Renderer non-rendering guard (Slice 4) | Renderer owner | Not in Slice 1 scope. |
| Release/readiness | Release owner/controller | Remains `NOT_READY`. |
| `ECQ*` taxonomy calibration | Quality gate owner | Start additive and provisional; review after implementation evidence. |

## Required Follow-Up

1. Add F-01 and F-02 tests (minor, additive, no production code change needed).
2. Proceed to Slice 2 - Service deterministic opt-in propagation after Slice 1 tests are complete.
3. No commit, push, PR mutation, mark-ready, merge or release/readiness transition is authorized by this review.
