# DS Plan Review: Release-readiness Non-live Verification Matrix Repair Plan

Date: 2026-06-12

Role: AgentDS plan reviewer

Review target: `docs/reviews/mvp-release-readiness-non-live-verification-matrix-repair-plan-20260612.md`

Gate: `Release-readiness non-live verification matrix repair planning gate` (standard)

## Verdict

**PASS_WITH_FINDINGS**

The plan correctly identifies path drift as the root cause, repairs all three missing paths with current repository equivalents, adds a V0 path-existence guard, and preserves all boundary constraints. No blocking issue found.

## Findings

| # | Severity | Finding | Evidence | Required change |
|---|---|---|---|---|
| F1 | LOW | V0 uses `test -d` for Host/Agent directories but `test -f` for all other paths. If all files inside `tests/host/` or `tests/agent/` were deleted while the directory remained, V0 would pass but V8 would fail at execution time. | Plan Section 7: V0 checks `test -d tests/host && test -d tests/agent`; confirmed both directories contain 7 test files across them. | None required; V8 catches the regression. Future matrix versions could list individual host/agent test files in V0 for symmetry. |
| F2 | INFO | Plan does not enumerate the current test files inside `tests/host/` and `tests/agent/` directories for future drift comparison. | Plan Section 3 lists only `tests/host` and `tests/agent` as directory paths; observed contents: `tests/host/test_runtime_runner.py`, `tests/host/test_runtime_state.py`, `tests/agent/test_tool_adapters.py`, `tests/agent/test_contracts.py`, `tests/agent/test_service_bridge.py`, `tests/agent/test_runner.py`, `tests/agent/test_repair_policy.py`. | None required; V8 pytest invocation implicitly covers all files. Recording the file list would improve future diffability but adds maintenance burden. |
| F3 | INFO | Plan Section 5 (Allowed Write Set) authorizes the controller to sync `docs/current-startup-packet.md` and `docs/implementation-control.md` post-acceptance, but does not list the exact sections to update. | Plan Section 5: "post-acceptance controller sync may update only: docs/current-startup-packet.md docs/implementation-control.md". | None required; controller judgment is the natural place to specify sync scope. The constraint "only" prevents uncontrolled edits. |

## Review Question Disposition

### Q1: Are all repaired paths current repo paths?

**PASS.** All 9 paths verified to exist:

| Path | Type | Exists | Test nodes confirmed |
|---|---|---|---|
| `tests/fund/test_annual_evidence.py` | file | yes | N/A (full file) |
| `tests/fund/test_annual_period_report.py` | file | yes | N/A (full file) |
| `tests/services/test_fund_analysis_service.py` | file | yes | `test_multi_year_annual_analysis_maps_service_request_to_fund_scope` at line 1430 |
| `tests/ui/test_cli.py` | file | yes | `test_analyze_annual_period_cli_calls_multi_year_service` at line 1640 |
| `tests/services/test_execution_contract.py` | file | yes | N/A (full file) |
| `tests/services/test_fund_analysis_service_llm.py` | file | yes | N/A (full file) |
| `tests/services/test_llm_run_artifacts.py` | file | yes | N/A (full file) |
| `tests/host` | directory | yes | `test_runtime_runner.py`, `test_runtime_state.py` |
| `tests/agent` | directory | yes | `test_tool_adapters.py`, `test_contracts.py`, `test_service_bridge.py`, `test_runner.py`, `test_repair_policy.py` |

The three previously missing paths (`tests/services/test_multi_year_annual_analysis.py`, `tests/ui/test_cli_annual_period.py`, `tests/services/test_llm_execution.py`) are correctly replaced with existing paths that cover the same verification surface.

### Q2: Is V7 narrow enough to cover annual-period productization without running full CLI/analyze commands?

**PASS.** V7 covers the full annual-period productization layered trace without any CLI execution:

- **Fund layer**: `tests/fund/test_annual_evidence.py` — `AnnualEvidenceBundle` loading, cross-year facts
- **Fund layer**: `tests/fund/test_annual_period_report.py` — deterministic annual-period report renderer
- **Service layer**: `tests/services/test_fund_analysis_service.py::test_multi_year_annual_analysis_maps_service_request_to_fund_scope` — Service request→Fund scope mapping
- **UI layer**: `tests/ui/test_cli.py::test_analyze_annual_period_cli_calls_multi_year_service` — CLI→Service routing

No `fund-analysis analyze-annual-period`, no `fund-analysis analyze`, no live EID/PDF/FDR/network command. All tests are deterministic unit/integration tests that exercise the typed product path without side effects.

### Q3: Is V8 the right current Service/Host/Agent LLM boundary surface?

**PASS.** V8 covers the accepted LLM boundary architecture (`CLI -> Service (ExecutionContract) -> Host runner -> Agent body runner`) at the correct granularity:

- **Service execution contract**: `tests/services/test_execution_contract.py` — ExecutionContract assembly/semantics
- **Service LLM**: `tests/services/test_fund_analysis_service_llm.py` — Service→LLM path orchestration
- **Service LLM run artifacts**: `tests/services/test_llm_run_artifacts.py` — run output/artifact handling
- **Host**: `tests/host/` — runtime runner, runtime state (lifecycle governance)
- **Agent**: `tests/agent/` — tool adapters, contracts, service bridge, runner, repair policy (tool loop, execution)

This matches the architecture documented in `docs/current-startup-packet.md` Section 3 and `AGENTS.md` boundary rules. No live LLM calls, no provider probes.

### Q4: Does V0 prevent repeat path drift?

**PASS, with observation.** V0 (`test -f` / `test -d` on all 9 paths before any test execution) catches the exact failure mode that caused the V7/V8 blockers: a path referenced in the matrix that does not exist on disk. The controller judgment additionally accepts the process residual (DS F2) that "future matrix plans must include path-existence verification before plan acceptance." Together these form a reasonable prevention mechanism.

Observation (see F1): V0 uses `test -d` for host/agent directories, which is coarser than the `test -f` checks for individual files. However, V8's pytest invocation on the directories provides the content-level safety net — if all files were deleted from the directory, V8 would fail.

### Q5: Does the plan preserve NOT_READY and no-live/no-release/no-PR boundaries?

**PASS.** Constraints are explicit and comprehensive:

- Section 1: "Default release/readiness result remains NOT_READY until a later accepted re-evidence gate proves otherwise"
- Section 6: enumerates 11 categories of forbidden commands (live EID, network, PDF, provider, analyze, checklist, golden, release/readiness, PR/push/merge, cleanup/delete/move, git state mutation)
- Section 9: review routing requires DS+MiMo reviews; no unilateral acceptance path
- Section 11: deferred entries explicitly list live, provider, PR, mark-ready as separate gates
- Allowed write set (Section 5) is restricted to plan/review/judgment artifacts and control-doc sync

## Cross-check: Plan vs Controller Judgment Residuals

The plan addresses all three controller judgment residuals from `02ffb2a`:

| Controller judgment residual | Plan disposition | Status |
|---|---|---|
| V7 missing path `tests/services/test_multi_year_annual_analysis.py` | Replaced with focused service test node | Addressed |
| V7 missing path `tests/ui/test_cli_annual_period.py` | Replaced with focused CLI test node | Addressed |
| V8 missing path `tests/services/test_llm_execution.py` | Replaced with current LLM boundary surfaces | Addressed |
| DS F2 process residual: path-existence in plan acceptance | V0 guard added; process residual recorded | Addressed |

## Residual / Risk Table

| Item | Severity | Owner | Mitigation |
|---|---|---|---|
| V0 directory-only check for host/agent | LOW | Matrix maintainer | V8 catches missing content; future matrix could enumerate individual files |
| Host/agent test file inventory not recorded in plan | INFO | Matrix maintainer | V8 automatically discovers files via pytest collection |
| Focused test node names are not checked in V0 | LOW | Matrix maintainer | V7 pytest invocation fails with non-zero exit if node doesn't exist |
| Post-acceptance control sync sections not specified | INFO | Controller | Controller judgment will scope the sync; "only" constraint prevents drift |
| Plan does not specify max V10 runtime | INFO | Matrix maintainer | V10 includes `--cov-fail-under=50` at 10-minute timeout; acceptable for floor check |
| Repaired re-evidence gate may discover new path drift between now and then | LOW | Controller | Same class as V0; V0 would catch it before re-evidence attempts V7/V8 |

## Final Recommendation

**PROCEED.** The plan correctly diagnoses path drift as the root cause, repairs all three missing paths with current repository equivalents verified to exist, and adds a V0 path-existence guard. All five review questions pass. The three findings are LOW or INFO severity, none blocking.

The repaired matrix is narrower (V7: focused test nodes instead of full test files; V8: explicit boundary files instead of a single missing file) while covering the same verification surface. No new scope is introduced. All boundary constraints (NOT_READY, no-live, no-release, no-PR) are preserved.
