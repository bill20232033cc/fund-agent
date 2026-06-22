# Targeted Re-Review: EC-P4 Slice 1 Code Review Fix

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `targeted code re-review`
- Classification: `heavy`
- Slice: `Slice 1 - Fund Summary + Quality Gate ECQ Projection`
- Branch: `evidence-confirm-productionization`
- Release/readiness: `NOT_READY`
- Reviewer: AgentMiMo
- Timestamp: `2026-06-22 22:00 Asia/Shanghai`

## Reviewed Artifacts

- DS code review: `docs/reviews/code-review-20260622-214853-ds-ec-p4-slice1.md`
- MiMo code review: `docs/reviews/code-review-20260622-214853-mimo-ec-p4-slice1.md`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-slice1-code-review-fix-20260622.md`
- Fixed source: `fund_agent/fund/evidence_confirm_production.py`, `fund_agent/fund/quality_gate_integration.py`
- Fixed tests: `tests/fund/test_evidence_confirm_production.py`, `tests/fund/test_quality_gate_integration.py`

## Verdict

`PASS`

## Finding Status Table

| Finding | Severity | Status | Verification Evidence |
|---|---|---|---|
| DS-ECP4S1-01 — `hard_gate.informational_issue_ids` dropped | HIGH | 已修复 | `_warning_issue_ids()` at line 341-344 now includes `result.evidence_confirm_result.hard_gate.informational_issue_ids`. Field docstring updated to "生产可见的非阻断 issue ids，包含 reviewable 与 informational issue". Test `test_summary_from_repository_warn_keeps_reviewable_and_informational_ids` verifies both reviewable and informational IDs appear in `warning_issue_ids`. |
| DS-ECP4S1-02 — missing production summary tests | MEDIUM | 已修复 | `test_evidence_confirm_production.py` grew from 1 test to 8 tests. New tests: `test_summary_from_repository_pass_is_compact_and_counts_checked_facts` (pass path), `test_summary_from_repository_warn_keeps_reviewable_and_informational_ids` (warn path with ID verification), `test_not_run_evidence_confirm_summary_accepts_stable_reason_variants` (parametrized: `invalid_request`, `runner_exception:RuntimeError`, `repository_failure:source_unavailable`), `test_not_run_evidence_confirm_summary_rejects_invalid_reason`, `test_not_run_evidence_confirm_summary_rejects_invalid_policy`, `test_summary_from_repository_not_applicable_boundary_is_not_run`. All 56 tests pass. |
| DS-ECP4S1-03 — `policy=off` defensive guard | MEDIUM | 已修复 | `_ecq_policy_severity()` at line 279-280 now raises `ValueError("policy='off' 的 Evidence Confirm fail/warn 摘要不能投影为 ECQ warn")` when `summary.policy == "off"`. Docstring updated to document the raise. Test `test_quality_gate_integration_rejects_off_policy_fail_summary` verifies the ValueError is raised with `match="policy='off'"`. |
| MiMo F-01 — summary=None/default no ECQ test | LOW | 已修复 | Test `test_quality_gate_integration_explicit_summary_none_produces_no_ecq_issues` at line 198-225 explicitly passes `evidence_confirm_summary=None` and asserts `not any(issue.rule_code.startswith("ECQ") for issue in result.quality_gate_result.issues)` on both in-memory issues and JSON payload. |
| MiMo F-02 — pathway failure ECQ1 test | LOW | 已修复 | Test `test_quality_gate_integration_maps_pathway_fail_to_ecq1_block` at line 358-392 creates summary with `pathway_status="fail"`, `deterministic_status="not_run"`, `not_run_reason="repository_failure:source_unavailable"`. Asserts ECQ1/block with correct `issue_id="evidence-confirm:110011:2024:ECQ1:repository_failure:source_unavailable"` and gate status "block". |
| MiMo F-03 — optional ECQ2 warn-policy fail variant | INFO | 已修复 | Test `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` at line 262-294 creates summary with `policy="warn"`, `deterministic_status="fail"`. Asserts ECQ2 severity is "warn" (not "block") and gate status is "warn". |
| MiMo F-04 — off-policy clarity | INFO | 已修复 | `_ecq_policy_severity()` docstring now states "Raises: ValueError: `policy=\"off\"` 的 fail/warn 摘要进入 ECQ fail 映射时抛出". The `ValueError` raise at line 280 makes the off-policy handling explicit and fail-closed. Covered by test `test_quality_gate_integration_rejects_off_policy_fail_summary`. |

## Remaining Blockers

无。

## Residual Risks

| Risk | Owner | Notes |
|---|---|---|
| `_evidence_confirm_quality_gate_issues(summary=None)` branch is unreachable from `run_quality_gate_for_bundle` (guarded by `is not None`). The branch is dead code in Slice 1; will become reachable in Slice 2 when Service passes summary=None for policy=off. | Service owner (Slice 2) | No action needed now; Slice 2 integration test must cover this path. |
| `not_run_evidence_confirm_summary` does not validate policy/reason consistency (e.g. `policy="block"` + `reason="policy_off"` is accepted). | Fund owner | Caller (Service) is responsible for constructing consistent parameters. Acceptable for Slice 1. |
| `merge_quality_gate_issues` rewrites `quality_gate.json`/`.md` after `run_quality_gate` already wrote them (double write per request). | — | Correctness unaffected; performance impact negligible for single-fund runs. |
| ECQ4 semantic companion projection. | Semantic owner | Deferred to Slice 5. |
| Release/readiness remains `NOT_READY`. | Controller/release owner | No change in this gate. |

## Required Next Gate

Proceed to EC-P4 Slice 2 — Service deterministic opt-in propagation.

No commit, push, PR mutation, mark-ready, merge or release/readiness transition is authorized by this re-review.
