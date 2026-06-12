# Plan Review: Release-readiness Non-live Verification Matrix Repair Planning Gate

Date: 2026-06-12

Reviewer: AgentMiMo

Review target: `docs/reviews/mvp-release-readiness-non-live-verification-matrix-repair-plan-20260612.md`

## 1. Verdict

**PASS**

The plan correctly identifies the root cause (path drift in the accepted matrix), proposes valid replacement paths that exist in the current repo, adds a V0 path-existence guard to prevent recurrence, and preserves all `NOT_READY` / no-live / no-release / no-PR boundaries.

## 2. Review Questions

### Q1: Are all repaired paths current repo paths?

**PASS.** Independent path-existence verification confirmed all nine V0 guard paths exist:

| V0 path | Verified |
|---|---|
| `tests/fund/test_annual_evidence.py` | EXISTS |
| `tests/fund/test_annual_period_report.py` | EXISTS |
| `tests/services/test_fund_analysis_service.py` | EXISTS |
| `tests/ui/test_cli.py` | EXISTS |
| `tests/services/test_execution_contract.py` | EXISTS |
| `tests/services/test_fund_analysis_service_llm.py` | EXISTS |
| `tests/services/test_llm_run_artifacts.py` | EXISTS |
| `tests/host` (directory) | EXISTS |
| `tests/agent` (directory) | EXISTS |

Additionally confirmed the two specific V7 test nodes exist:
- `tests/services/test_fund_analysis_service.py::test_multi_year_annual_analysis_maps_service_request_to_fund_scope` (line 1430)
- `tests/ui/test_cli.py::test_analyze_annual_period_cli_calls_multi_year_service` (line 1640)

And confirmed the three original missing paths remain missing:
- `tests/services/test_multi_year_annual_analysis.py` — MISSING
- `tests/ui/test_cli_annual_period.py` — MISSING
- `tests/services/test_llm_execution.py` — MISSING

### Q2: Is V7 narrow enough to cover annual-period productization without running full CLI/analyze commands?

**PASS.** V7 runs four focused test targets:
- `tests/fund/test_annual_evidence.py` — Fund-layer annual evidence bundle tests
- `tests/fund/test_annual_period_report.py` — Fund-layer annual-period report renderer tests
- `tests/services/test_fund_analysis_service.py::test_multi_year_annual_analysis_maps_service_request_to_fund_scope` — Service-layer multi-year request mapping
- `tests/ui/test_cli.py::test_analyze_annual_period_cli_calls_multi_year_service` — CLI-layer annual-period surface

This covers the deterministic annual-period productization surface (Fund → Service → CLI) without invoking `fund-analysis analyze`, `fund-analysis analyze-annual-period`, `fund-analysis checklist`, or any live/provider/network command. The scope is appropriately narrow.

### Q3: Is V8 the right current Service/Host/Agent LLM boundary surface?

**PASS.** V8 runs:
- `tests/services/test_execution_contract.py` — Service-layer ExecutionContract semantics
- `tests/services/test_fund_analysis_service_llm.py` — Service-layer LLM execution path
- `tests/services/test_llm_run_artifacts.py` — Service-layer LLM run artifact surfaces
- `tests/host` — Host lifecycle test suite
- `tests/agent` — Agent body runner / tool-loop test suite

This replaces the missing `tests/services/test_llm_execution.py` with the actual current boundary surface: Service execution contract + Service LLM execution + Service LLM artifacts + Host directory + Agent directory. This aligns with the startup packet's description of the `--use-llm` path as `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> Agent body runner`.

### Q4: Does V0 prevent repeat path drift?

**PASS.** V0 is a new path-existence guard that runs `test -f` / `test -d` against all nine paths before any test execution. If any path is missing, V0 classifies as `blocker` and prevents proceeding. This directly addresses the process residual from the prior evidence gate (DS F2 / MiMo F3) where plan reviews missed missing test paths. V0 makes path drift a first-class blocker rather than a post-hoc discovery.

### Q5: Does the plan preserve NOT_READY and no-live/no-release/no-PR boundaries?

**PASS.** The plan explicitly states in Section 1:

> "It does not run the repaired matrix, does not prove release readiness, and does not authorize source/test/runtime changes, source acquisition changes, provider/runtime changes, fallback reintroduction, live commands, readiness commands, cleanup, PR, push, merge or release actions."

> "Default release/readiness result remains `NOT_READY` until a later accepted re-evidence gate proves otherwise with direct local evidence and controller judgment."

The forbidden commands list in Section 6 is comprehensive and consistent with prior gate boundaries. Section 8 requires the re-evidence artifact to include "statement that no prohibited command was run."

## 3. Findings

| Severity | Finding | Evidence | Required Change |
|---|---|---|---|
| info | V0 guard uses shell `test -f` / `test -d` which is correct for path existence but does not verify test *content* (e.g., that a test function still exists at the expected line number). | V0 command definition in Section 7. | No change required. V0 is a path-existence guard, not a content guard. Test node content is implicitly validated when V7/V8 pytest runs against the specific node IDs. |
| info | The plan references `tests/services/test_fund_analysis_service_llm.py` and `tests/services/test_llm_run_artifacts.py` as V8 targets but does not list specific test node IDs within those files (unlike V7 which lists specific `::test_*` nodes). | V8 command in Section 7. | No change required. Running the full file targets for Host/Agent/LLM surfaces is appropriate since these are boundary test suites, not narrowly scoped product-path tests. V7 needs specific nodes because it targets a specific product feature; V8 targets architectural boundary coverage. |

No blocking or non-blocking findings.

## 4. Residual / Risk Table

| Residual | Risk | Mitigation |
|---|---|---|
| Repaired matrix has not been executed yet | V7/V8 repair could fail at runtime despite paths existing | Re-evidence gate will run the actual commands; V0 guards path existence, V9/V10 provide fallback validation |
| V0 does not guard against test function rename/removal | A test file could exist but the specific `::test_*` node could be renamed | V7/V8 pytest will fail with clear "not found" error if a specific node is missing; V0 catches file-level drift |
| `tests/host` and `tests/agent` are directories, not specific files | Directory-level `test -d` check is weaker than file-level checks | Appropriate for boundary test suites; V9 broad pytest covers these anyway |

## 5. Final Recommendation

The plan is well-structured and addresses the root cause directly. The V0 path-existence guard is the key improvement over the prior matrix — it converts a process residual (DS F2) into a first-class blocker. All repaired paths are verified as existing in the current repo. The plan correctly preserves all `NOT_READY` and boundary constraints.

Recommendation: **Accept the plan as-is.**
