# UI-Service-Host Boundary Reconciliation Plan Controller Judgment

## Scope

- Gate: `UI-Service-Host boundary reconciliation gate`
- Judgment type: plan controller judgment
- Plan: `docs/reviews/mvp-ui-service-host-boundary-reconciliation-plan-20260611-135130.md`
- AgentDS review: `docs/reviews/mvp-ui-service-host-boundary-reconciliation-plan-review-ds-20260611-140916.md`
- AgentMiMo review: `docs/reviews/mvp-ui-service-host-boundary-reconciliation-plan-review-mimo-20260611-140916.md`
- Verdict: `ACCEPT_WITH_AMENDMENTS`

## Basis

- `AGENTS.md`: UI must only depend on Service; Service owns business use-case orchestration, ExecutionContract assembly, provider construction/runtime ceilings and final product fail-closed mapping; Host owns lifecycle/deadline/cancel/events only.
- `docs/design.md`: current text records Route C `--use-llm` Host wrapping, but some current wording still describes CLI handing a synchronous operation closure and Host timeout to Host. This is a code/design fact to reconcile with the stricter UI boundary.
- `docs/implementation-control.md`: current active gate is `UI-Service-Host boundary reconciliation gate`; implementation has not started; Host durable session/resume/memory/outbox, Agent full tool-loop expansion, provider/runtime changes, live commands and fallback/source expansion remain non-goals.
- `docs/current-startup-packet.md`: current entry is planning; no implementation write set was accepted before this judgment.
- AgentDS and AgentMiMo: both accepted the amended plan after re-review.

## Controller Decision

The plan is accepted with its recorded amendments. The gate is reclassified from `standard` to `heavy` because it changes the ownership boundary for the public `--use-llm` path across `UI -> Service -> Host -> Agent`. This meets the `AGENTS.md` heavy classification criteria for architecture boundary and public layer ownership.

The accepted target is:

```text
Current: UI -> Service request builder, UI -> Host runner -> Service operation -> Agent/Fund
Target:  UI -> Service hosted LLM use case -> Host runner -> Service operation -> Agent/Fund
```

The accepted plan resolves the reviewer blockers by specifying:

- Service-owned `FundLLMHostedRunResult` with exact safe fields.
- Service-owned `FundAnalysisService.analyze_with_llm_hosted(request, *, event_sink=None)`.
- UI progress reporter migration to duck-typed event consumption without importing Host symbols.
- UI test migration away from Host runner fakes and `cli.HostRun*` symbols.
- Static `rg` validation that UI production code and UI tests no longer import or reference Host runtime symbols.

## Accepted Implementation Write Set

Implementation is authorized only for:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `docs/design.md`
- `fund_agent/README.md`

`docs/design.md` is authorized only as post-code current-fact synchronization for the UI-Service-Host boundary. It must not introduce future Host durable features, Agent runtime expansion, provider runtime changes, source/fallback changes or design speculation.

`fund_agent/README.md` is authorized only if current wording still describes UI/CLI owning Host invocation.

## Explicit Non-Goals

The accepted plan does not authorize:

- live provider, endpoint, DNS, socket, curl, network, EID, PDF, FDR, extractor, analyze/checklist, golden/readiness, score-loop or release commands
- provider default/model/base URL/timeout/retry/backoff/max-output/runtime budget/prompt payload mode changes
- Host durable session/resume/memory/reply outbox
- Agent full tool-loop/runtime expansion
- fallback/source acquisition changes
- `extra_payload`, open business payload bags, hidden kwargs or metadata/context parameter bags
- PR, push, merge, mark-ready or release-state changes
- implementation edits outside the accepted write set

## Required Validation After Implementation

```bash
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py tests/host/test_runtime_runner.py -q
uv run ruff check fund_agent/ui/cli.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py
rg -n "from fund_agent.host|HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEventType|HostRunEventSink|build_fund_llm_execution_request" fund_agent/ui/cli.py
rg -n "from fund_agent.host|HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEventType|HostRunEventSink|cli\\.HostRun" tests/ui/test_cli.py
git diff --check
git diff --name-only
```

Both `rg` commands must return no matches.

## Residuals / Deferred Entries

- `docs/design.md` section targeting is left to implementation, but the likely current-fact sync points are Route C / current implementation paragraphs that still describe CLI-owned Host invocation.
- Existing Service LLM tests should remain behavior-preserving; hosted-wrapper assertions should be additive unless the UI migration forces a test boundary update.
- LLM path parity with deterministic `_validate_request()` remains deferred.
- Host durable session/resume/memory/reply outbox remains deferred.
- Full Agent tool-loop/runtime expansion remains deferred.
- Provider live acceptance and runtime default changes remain deferred.

## Next Action

Before implementation, synchronize control truth to record:

- plan accepted by this controller judgment
- gate classification `heavy`
- accepted plan/review artifacts
- implementation may proceed under the accepted write set and validation matrix

After control sync and local accepted checkpoint, enter the implementation gate using the accepted plan. The `PR #22` pane footer is not evidence of MiMo/DS unavailability per user clarification.
