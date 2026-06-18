# MVP Agent Engine Design Slice E Implementation Planning Gate Plan Controller Judgment

## 1. Judgment

Decision: `PLAN_ACCEPTED_IMPLEMENTATION_AUTHORIZED`.

Accepted plan:

- `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md`

Accepted reviews:

- `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-codex-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-rereview-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-rereview-codex-20260608.md`

Controller judgment: the revised Slice E plan is accepted and implementation is
authorized only within the constraints in this judgment.

## 2. Review Outcome

Initial reviews:

- AgentDS: `PASS_WITH_NON_BLOCKING_OBSERVATIONS`;
- AgentCodex: `BLOCKED`.

The planning artifact was revised to resolve:

- E5 role/file authorization overreach;
- missing Host cancel/deadline normalized scheduler contract and tests;
- DS observations on `blocked_tool_contract`, residual owners, prompt count
  derivation, pre-migration baseline, validation-matrix mapping, E4 narrowing
  and partial acceptance.

Supplemental re-reviews:

- AgentDS: `PASS`;
- AgentCodex: `PASS`.

Controller assessment: the blocking findings are resolved and no remaining
review finding blocks implementation authorization.

## 3. Authorized Implementation Scope

Implementation may proceed sequentially through E1-E4 and E5 evidence/docs:

- create and populate `fund_agent/agent/` per E1-E3;
- implement Agent contracts, ToolTrace, Fund tool adapters, runner and repair
  policy according to the accepted plan;
- add no-live Agent tests under `tests/agent/`;
- add `fund_agent/services/agent_bridge.py`;
- modify `fund_agent/services/chapter_orchestrator.py` only as needed for the
  accepted Service bridge migration;
- modify `fund_agent/services/fund_analysis_service.py` only in
  `analyze_with_llm_execution()` or a new bridge call path;
- update `fund_agent/agent/README.md`, `fund_agent/README.md` and
  `tests/README.md` only as triggered by implemented code/test boundaries;
- write `docs/reviews/mvp-agent-engine-design-slice-e-implementation-evidence-20260608.md`.

Implementation must record pre-migration Service baseline output before changing
Service bridge behavior.

## 4. Required Implementation Contracts

Implementation must preserve these accepted contracts:

- Service owns use case, provider construction, provider runtime ceilings,
  final product fail-closed mapping, stdout semantics and quality policy;
- Host remains lifecycle-only and business-opaque;
- Agent owns body chapter execution mechanics, task state, attempt ledger, repair
  policy, ToolTrace and final body readiness;
- Fund primitives are wrapped, not rewritten;
- Agent must not import `fund_agent.host`;
- `AgentSchedulerInterruption` is Agent-owned and receives only normalized
  Service bridge translation from current Host checks;
- provider timeout retry remains Service/provider-client behavior and does not
  consume Agent content repair budget;
- hidden Agent retry is forbidden;
- `llm_exception + code_bug` maps to fail-closed internal code bug, not
  provider/runtime;
- duplicate body chapter rows and duplicate accepted source ids remain
  fail-closed with no report markdown;
- ToolTrace and serialized diagnostics remain safe-scalar allowlist only.

## 5. Forbidden Scope

This judgment does not authorize:

- live `--use-llm`;
- provider readiness, retry, endpoint probe, curl, DNS, socket or network probe;
- provider/default/runtime/budget/config behavior change;
- deterministic `analyze/checklist` behavior change;
- quality gate, golden/readiness, score-loop, multi-year runtime, public chapter
  ids `0-7`, stdout semantics or final judgment semantic change;
- `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime production
  dependency;
- provider writer/auditor clients as registry tools;
- code review artifact creation by implementation worker;
- controller judgment artifact creation by implementation worker;
- `docs/current-startup-packet.md` or `docs/implementation-control.md` edits by
  implementation worker;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 6. Stop Conditions

Implementation worker must stop before staging or committing implementation work
and return to controller if:

- E4 Service bridge equivalence cannot be preserved;
- any implementation slice cannot meet its no-live validation contract;
- Agent needs to import `fund_agent.host`;
- provider construction would need to move into Agent;
- current Service behavior is not representable and no residual owner exists;
- validation requires live/provider/network commands;
- implementation needs files outside the accepted scope.

Partial E1-E3 acceptance without E4 Service bridge equivalence requires a
separate controller judgment that explicitly reclassifies that code as
non-production.

## 7. Required Validation

Implementation evidence must include local-only results for the accepted plan
commands, at minimum:

```text
git diff --check
uv run pytest tests/agent tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/services/test_llm_run_artifacts.py
uv run ruff check fund_agent/agent fund_agent/services tests/agent tests/services
```

No source tests were run for this controller judgment because this gate only
accepted an implementation plan.

## 8. Next Entry

Next entry: `MVP Agent Engine Design Slice E Implementation`.

The implementation worker may start within this judgment's authorized scope.
After implementation evidence is written, the next lifecycle step is independent
code review, then controller implementation judgment, then control-doc sync only
if implementation is accepted.
