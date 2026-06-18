# Release-readiness Non-live Verification Matrix Repair Planning Gate

Date: 2026-06-12

Role: controller-authored planning artifact

Gate: `Release-readiness non-live verification matrix repair planning gate`

Classification: `standard`

Accepted input:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-release-readiness-non-live-verification-evidence-controller-judgment-20260612.md`
- Evidence checkpoint `02ffb2a`
- Control sync checkpoint `256556a`

## 1. Verdict Target

This plan authorizes only repair of the deterministic non-live verification matrix paths.

It does not run the repaired matrix, does not prove release readiness, and does not authorize source/test/runtime changes, source acquisition changes, provider/runtime changes, fallback reintroduction, live commands, readiness commands, cleanup, PR, push, merge or release actions.

Default release/readiness result remains `NOT_READY` until a later accepted re-evidence gate proves otherwise with direct local evidence and controller judgment.

## 2. Root Cause

The accepted non-live verification evidence gate proved that V7 and V8 could not execute as written because the accepted matrix referenced missing test paths:

| Missing path | Source matrix row | Current disposition |
|---|---|---|
| `tests/services/test_multi_year_annual_analysis.py` | V7 | Replace with existing focused service test node in `tests/services/test_fund_analysis_service.py`. |
| `tests/ui/test_cli_annual_period.py` | V7 | Replace with existing focused CLI test node in `tests/ui/test_cli.py`. |
| `tests/services/test_llm_execution.py` | V8 | Replace with current Service LLM execution-contract and hosted-run test files. |

This is verification-matrix path drift, not a product-code failure.

## 3. Path-existence Evidence

The following path-existence checks passed during planning:

- `tests/fund/test_annual_evidence.py`
- `tests/fund/test_annual_period_report.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`
- `tests/services/test_execution_contract.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_llm_run_artifacts.py`
- `tests/host`
- `tests/agent`

Observed focused test nodes:

- `tests/services/test_fund_analysis_service.py::test_multi_year_annual_analysis_maps_service_request_to_fund_scope`
- `tests/ui/test_cli.py::test_analyze_annual_period_cli_calls_multi_year_service`

Observed LLM/Host/Agent boundary surfaces:

- `tests/services/test_execution_contract.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_llm_run_artifacts.py`
- `tests/host`
- `tests/agent`

## 4. Allowed Read Set

This planning gate and the later re-evidence gate may read only:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- this repair plan
- the accepted non-live verification evidence/judgment artifacts
- DS/MiMo review artifacts for this plan
- controller judgment accepting this plan
- metadata-only `rg --files`, `rg -n "def test_"`, `test -f`, `test -d`, `git status`, `git diff --name-only`, `git diff --check` outputs
- deterministic command outputs from the later re-evidence gate

Do not read PDF bodies, generated report bodies, audit report bodies, unrelated untracked file bodies, cache contents, provider payloads, network responses, or historical review artifact bodies unless a future controller judgment explicitly adds a path.

## 5. Allowed Write Set

This planning gate may write only:

- `docs/reviews/mvp-release-readiness-non-live-verification-matrix-repair-plan-20260612.md`
- `docs/reviews/mvp-release-readiness-non-live-verification-matrix-repair-plan-review-ds-20260612.md`
- `docs/reviews/mvp-release-readiness-non-live-verification-matrix-repair-plan-review-mimo-20260612.md`
- `docs/reviews/mvp-release-readiness-non-live-verification-matrix-repair-plan-controller-judgment-20260612.md`

If accepted, post-acceptance controller sync may update only:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

The later repaired re-evidence gate may write only:

- one re-evidence artifact under `docs/reviews/`
- DS/MiMo review artifacts under `docs/reviews/`
- one controller judgment under `docs/reviews/`
- post-acceptance control sync in `docs/current-startup-packet.md` and `docs/implementation-control.md`

No source, tests, runtime files, README, `.gitignore`, cache, reports, PDFs, fixtures, golden files, provider config, lockfile, PR metadata, archive movement, deletion, cleanup, import, promotion, or release-state files are authorized.

## 6. Forbidden Commands And Actions

Forbidden:

- live EID commands
- network, DNS, socket or HTTP probes
- PDF download, parsing, body inspection, FDR or FundDocumentRepository live acquisition commands
- provider, LLM, `--use-llm`, endpoint or runtime-budget probes
- `fund-analysis analyze`
- `fund-analysis analyze-annual-period`
- `fund-analysis checklist`
- golden generation, fixture projection, baseline promotion or readiness promotion
- release/readiness commands
- GitHub PR, push, merge, mark-ready, reviewer request, approval or external comment actions
- cleanup, delete, move, archive, ignore-rule, import or promote actions
- worker-initiated `git add`, `git commit`, `git stash`, `git merge` or other local git state mutation

Controller-only exception: after review and controller judgment acceptance, the controller may stage and commit only the accepted planning/review/judgment/control-sync artifacts allowed by this plan.

## 7. Repaired Deterministic Matrix

The next re-evidence gate should use this repaired matrix:

| ID | Command | Repair from previous matrix | Success criteria | Failure classification |
|---|---|---|---|---|
| V0 | `test -f tests/fund/test_annual_evidence.py && test -f tests/fund/test_annual_period_report.py && test -f tests/services/test_fund_analysis_service.py && test -f tests/ui/test_cli.py && test -f tests/services/test_execution_contract.py && test -f tests/services/test_fund_analysis_service_llm.py && test -f tests/services/test_llm_run_artifacts.py && test -d tests/host && test -d tests/agent` | New path-existence guard | Exit 0 | blocker if fails |
| V1 | `git status --branch --short` | unchanged | Captured | metadata |
| V2 | `git status --short` | unchanged | Captured | metadata |
| V3 | `git diff --name-only` | unchanged | Captured; tracked modified files limited to current evidence artifacts before acceptance | blocker if unauthorized tracked drift |
| V4 | `git diff --check` | unchanged | Exit 0 | blocker if fails |
| V5 | `uv run ruff check fund_agent tests` | unchanged | Exit 0 | blocker if fails in source/test scope |
| V6 | `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q` | unchanged | Exit 0 | blocker if fails |
| V7 | `uv run pytest tests/fund/test_annual_evidence.py tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py::test_multi_year_annual_analysis_maps_service_request_to_fund_scope tests/ui/test_cli.py::test_analyze_annual_period_cli_calls_multi_year_service -q` | Replaces two missing V7 paths with existing focused service/UI test nodes | Exit 0 | blocker if fails |
| V8 | `uv run pytest tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_llm_run_artifacts.py tests/host tests/agent -q` | Replaces missing `tests/services/test_llm_execution.py` with current Service LLM execution-contract/artifact surfaces plus Host/Agent suites | Exit 0 | blocker if fails |
| V9 | `uv run pytest -q` | unchanged | Exit 0 | blocker if current product/readiness-critical failure; material residual only with explicit unrelated failure rationale |
| V10 | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | unchanged | Exit 0 within 10 minutes | blocker if fails; material residual if timing interruption after V6-V9 pass |

Passing V10 at the 50% floor is only a floor sanity check. It does not prove coverage sufficiency or release readiness.

## 8. Required Evidence In Repaired Re-evidence Gate

The repaired re-evidence artifact must include:

- exact command log with exit code
- V0 path-existence result
- static non-live audit with exact command, exit code and summary
- V7/V8 repaired command output
- statement that no prohibited command was run
- failure classification table
- residual owner table
- explicit readiness statement
- next entry

If any repaired command attempts live/provider/source acquisition, stop and classify as `blocking_question`; do not retry with live access.

## 9. Review Routing

Required review before acceptance:

- AgentDS: plan review
- AgentMiMo: plan review

Review focus:

- Are all repaired paths current repo paths?
- Is V7 narrow enough to cover annual-period productization without running full CLI/analyze commands?
- Is V8 the right current Service/Host/Agent LLM boundary surface?
- Does V0 prevent repeat path drift?
- Does the plan preserve `NOT_READY` and no-live/no-release/no-PR boundaries?

## 10. Acceptance Criteria

This planning gate can be accepted only if:

1. Plan artifact exists under the allowed write set.
2. DS and MiMo reviews exist, or unavailability is recorded with controller risk acceptance.
3. Controller judgment maps review findings.
4. `git diff --check` passes.
5. Accepted checkpoint stages only plan/review/controller artifacts.
6. Control docs are synchronized only after the local accepted checkpoint exists.

## 11. Next Entry

If accepted, next mainline:

`Release-readiness non-live verification repaired evidence gate`

Deferred entries remain:

- controlled live annual-period narrative evidence gate
- live provider / LLM acceptance gate
- additional EID live sample gate
- fixture/golden/readiness promotion gate
- cleanup/archive/delete/import/ignore artifact-action gate
- PR / push / merge / mark-ready external-state gate
