# MVP Agent Engine Design Slice E Implementation Planning Gate Plan

## 1. Gate Role

Role: `planning worker`.

This artifact opens Slice E under the accepted `Agent Engine Design Refresh
Gate`. It is a code-generation-ready implementation plan, not an implementation.

It consumes accepted Slices A-D:

- Slice A dataclass design checkpoint `8d50b40`;
- Slice B tool adapter contract checkpoint `1c3c031`;
- Slice C repair and budget contract checkpoint `bc45778`;
- Slice D no-live equivalence validation checkpoint `9f6d360`.

This plan must be independently reviewed and receive controller judgment before
any implementation worker may create `fund_agent/agent` or change runtime code.

## 2. Objective

Implement the first internalized Agent execution mechanics for current LLM body
chapter generation while preserving Service, Host, Agent and Fund boundaries.

The implementation objective is:

- add an Agent-owned `fund_agent/agent` package for chapter task state, tool
  envelopes, safe ToolTrace, repair policy and body chapter runner;
- wrap existing Fund primitives instead of rewriting Fund logic;
- keep Service-owned provider construction, `FundLLMExecutionRequest`,
  provider runtime ceilings, use-case semantics and final product fail-closed
  mapping;
- keep Host lifecycle-only and business-opaque;
- preserve current no-live behavioral equivalence for accepted/partial/blocked
  chapter outcomes, repair budget semantics, terminal categories, final body
  readiness and safe diagnostics;
- migrate Service `ChapterOrchestrator` execution mechanics only after parity
  tests pass in the same implementation gate.

## 3. Non-Goals And Forbidden Actions

This Slice E plan does not authorize these actions by itself:

- implementation before controller accepts this plan;
- live `--use-llm`, retry, endpoint probe, curl, DNS, socket, provider readiness
  check or network-dependent validation;
- provider/default/runtime/budget/config behavior change;
- provider writer/auditor clients as registry tools;
- moving provider construction into Agent;
- Host inspecting fund code, chapter ids, business request fields, provider
  clients, CHAPTER_CONTRACT, ITEM_RULE or audit results;
- copying or rewriting upstream Dayu code;
- adding `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime as a
  production dependency;
- changing deterministic `analyze/checklist`, quality gate, golden/readiness,
  score-loop, multi-year runtime, public chapter ids `0-7`, stdout semantics or
  final judgment semantics;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 4. Implementation Slice Plan

### E1: Agent Contracts Package

Allowed files:

- `fund_agent/agent/__init__.py`
- `fund_agent/agent/contracts.py`
- `tests/agent/test_contracts.py`
- `fund_agent/agent/README.md`
- `fund_agent/README.md` if package map changes
- `tests/README.md` if new test layer is added

Implementation requirements:

- define Agent dataclasses from Slice A:
  `AgentReportRun`, `ChapterTask`, `ChapterAttempt`, `AgentRepairPolicy`,
  `ToolCallRequest`, `ToolCallResult`, `ToolTrace` and
  `FinalAssemblyReadiness`;
- define Agent-owned `AgentSchedulerInterruption` with explicit fields:
  `status`, `reason`, `phase`, `chapter_id` and `attempt_index`; accepted
  `status` values are `none`, `cancelled` and `deadline_exceeded`;
- include Chinese module/class/function docstrings with parameters, returns and
  exceptions where applicable;
- keep classes frozen or otherwise immutable unless a mutation point is
  explicitly justified in the implementation evidence;
- derive `EvidenceAvailability` exactly once after `ChapterFactProjection` and
  before first task preparation;
- preserve chapter-attributed blocked reasons: chapter id, stop reason and
  failure category must be reconstructable without unsafe payloads;
- pin `DiagnosticConsistencyStatus` to current literals or an explicit named
  future equivalent.

Validation:

```text
uv run pytest tests/agent/test_contracts.py
uv run ruff check fund_agent/agent tests/agent
```

### E2: Tool Adapter And ToolTrace Package

Allowed files:

- `fund_agent/agent/tools.py`
- `fund_agent/agent/contracts.py`
- `tests/agent/test_tool_adapters.py`
- related README files from E1 if public extension points are documented

Implementation requirements:

- implement typed wrappers for existing Fund primitives only:
  `project_chapter_facts()`, `write_chapter()`,
  `audit_chapter_programmatic()` and `audit_chapter_llm()`;
- keep `derive_evidence_availability()` as run-level same-source precomputation,
  not a ToolRegistry tool;
- Service-constructed writer/auditor clients may be carried into Agent as typed
  per-run fields and passed to Fund adapters, but must not become registry tools;
- ToolTrace serialization must be allowlist-only and must not store prompt text,
  draft markdown, fact values, unsafe anchor prose, raw provider response, raw
  audit response, raw provider request/body, API key, Authorization header,
  bearer token, model value, base URL value, arbitrary response headers or
  provider config values;
- `request_id` may only be an optional scalar from an explicit response-header
  allowlist.
- prompt char counts and approximate token counts must be derived from
  in-memory prompt length heuristics only; they must not require retained prompt
  text, external token-count service calls or network access.

Validation:

```text
uv run pytest tests/agent/test_tool_adapters.py
uv run pytest tests/services/test_llm_run_artifacts.py
uv run ruff check fund_agent/agent tests/agent
```

### E3: Agent Runner And Repair Policy

Allowed files:

- `fund_agent/agent/runner.py`
- `fund_agent/agent/repair.py`
- `fund_agent/agent/contracts.py`
- `tests/agent/test_runner.py`
- `tests/agent/test_repair_policy.py`

Implementation requirements:

- run template body chapters `1-6` from the same `ChapterFactProjection` and
  run-level `EvidenceAvailability`;
- attempt index starts at `0`;
- hidden Agent retry is forbidden: every repeated writer, auditor, tool or
  repair action must be represented in attempt ledger, repair decision ledger or
  ToolTrace;
- provider timeout retry remains Service/provider-client behavior and does not
  consume Agent content repair budget;
- provider runtime failures do not trigger content repair;
- `repair_hint=patch` and `repair_hint=regenerate` remain whole-chapter
  regenerate until a separate typed patch API gate;
- `repair_hint=needs_more_facts` is terminal and does not source-probe;
- Host interruption may enter repair policy only as an already-normalized Agent
  scheduler event/status; repair policy and tool adapters must not import or
  inspect Host context/state;
- Agent runner checks scheduler interruption before the first chapter, between
  writer and auditor, after tool-call return and before repair decision;
- cancelled or deadline-exceeded interruption fails closed, cannot produce
  complete report markdown and does not consume content repair budget.

Validation:

```text
uv run pytest tests/agent/test_runner.py
uv run pytest tests/agent/test_repair_policy.py
uv run pytest tests/services/test_chapter_orchestrator.py
uv run ruff check fund_agent/agent tests/agent
```

### E4: Service Bridge And No-Live Equivalence Migration

Allowed files:

- `fund_agent/services/agent_bridge.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_final_chapter_assembler.py`
- `tests/agent/test_service_bridge.py`
- relevant README files if public behavior or package boundaries change

Implementation requirements:

- Service remains the use-case owner and provider-construction owner;
- Service may call Agent runner for body chapter execution, then project Agent
  body readiness back into the existing Service final assembly path;
- Service bridge owns translation from current `HostRunContext` checks into
  `AgentSchedulerInterruption`; Agent contracts, runner, repair policy and tools
  must not import `fund_agent.host`;
- `fund_agent/services/fund_analysis_service.py` edits are limited to
  `analyze_with_llm_execution()` or a new bridge call path; deterministic
  `analyze()` and existing `analyze_with_llm()` behavior must remain unchanged
  unless implementation evidence explicitly proves the change is equivalent;
- before changing Service bridge behavior, implementation evidence must record
  the pre-migration local Service baseline command output for the relevant
  no-live tests;
- current `FinalChapterAssembler`, final product fail-closed mapping, stdout
  behavior and quality policy remain authoritative;
- no deterministic fallback on LLM failure;
- partial/blocked Agent body readiness cannot produce complete report markdown;
- chapter 0 and chapter 7 are not accepted if required body readiness is blocked;
- required body chapter rows and source accepted chapter ids are unique;
- duplicate chapter rows remain fail-closed with no report markdown;
- no public chapter id change.

Validation:

```text
uv run pytest tests/agent/test_service_bridge.py
uv run pytest tests/services/test_chapter_orchestrator.py
uv run pytest tests/services/test_final_chapter_assembler.py
uv run pytest tests/services/test_fund_analysis_service_llm.py
uv run pytest tests/services/test_llm_run_artifacts.py
uv run ruff check fund_agent/agent fund_agent/services tests/agent tests/services
```

### E5: Implementation Evidence And Triggered Documentation

Allowed files:

- `docs/reviews/mvp-agent-engine-design-slice-e-implementation-evidence-20260608.md`
- `fund_agent/agent/README.md`
- `fund_agent/README.md`
- `tests/README.md`

Implementation requirements:

- document Agent package as current code fact only after implementation tests pass;
- keep README scope aligned with `AGENTS.md` fixed README roles;
- record validation commands and outcomes in implementation evidence;
- if any implementation slice cannot preserve equivalence, stop before staging
  or committing implementation work and return to controller with the residual
  owner;
- implementation worker must not write code-review artifacts, controller
  judgment artifacts, `docs/current-startup-packet.md` or
  `docs/implementation-control.md`; those are reviewer/controller responsibilities
  after implementation evidence and code review.

Validation:

```text
git diff --check
uv run pytest tests/agent tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/services/test_llm_run_artifacts.py
uv run ruff check fund_agent/agent fund_agent/services tests/agent tests/services
```

Post-implementation lifecycle:

- implementation worker writes implementation evidence only;
- independent reviewer writes code review artifact;
- controller writes implementation controller judgment;
- only controller/control-sync worker updates `docs/current-startup-packet.md`
  and `docs/implementation-control.md` after accepted judgment.

## 5. Required Terminal Mapping

Implementation must include an explicit mapping over both current
`ChapterRunStopReason` and `ChapterFailureCategory`.

Minimum accepted mapping:

| Current stop reason | Failure category condition | Future Agent terminal |
|---|---|---|
| `none` | none | `accepted` |
| `chapter_not_in_scope` | any non-accepted category | `skipped_explicit_scope` |
| `dependency_missing` | any non-accepted category | `blocked_dependency_missing` |
| `fund_type_unknown` | `fact_gap` or equivalent | `blocked_fund_identity_fact_gap` |
| `missing_required_facts` | `fact_gap` | `blocked_fact_gap` |
| `writer_blocked` | non-provider writer precondition | `blocked_writer_precondition` |
| `auditor_failed` | `audit_parse` or `audit_rule_too_strict` | `blocked_audit_failed` |
| `auditor_blocked` | `audit_parse` or `audit_rule_too_strict` | `blocked_audit_contract` |
| `repair_budget_exhausted` | any content category | `blocked_repair_budget_exhausted` |
| `needs_more_facts` | `fact_gap` | `blocked_needs_more_facts` |
| `llm_unavailable` | provider-classified category | `blocked_provider_runtime` |
| `llm_empty_response` | provider-classified category | `blocked_provider_runtime` |
| `llm_contract_violation` | `prompt_contract` | `blocked_prompt_contract` |
| `missing_required_structure` | `prompt_contract` | `blocked_prompt_contract` |
| `missing_required_output_marker` | `prompt_contract` | `blocked_prompt_contract` |
| `unknown_anchor` | `prompt_contract` | `blocked_prompt_contract` |
| `response_too_long` | `prompt_contract` | `blocked_prompt_contract` |
| `response_incomplete` | `prompt_contract` | `blocked_prompt_contract` |
| `llm_timeout` | `llm_timeout` or `provider_runtime` | `blocked_provider_runtime` |
| `llm_rate_limited` | `provider_runtime` | `blocked_provider_runtime` |
| `llm_malformed_response` | `provider_runtime` | `blocked_provider_runtime` |
| `llm_network_error` | `provider_runtime` | `blocked_provider_runtime` |
| `llm_exception` | `code_bug` | `blocked_internal_code_bug` |

The implementation plan must reject any mapping that collapses
`llm_exception + code_bug` into provider/runtime. Provider/runtime terminal
states must not consume Agent content repair budget.

`blocked_tool_contract` disposition: it is removed from the first Agent terminal
set. The first implementation wraps existing Fund primitives and introduces no
new tool-contract terminal beyond current stop reasons. A future gate may add
`blocked_tool_contract` only after it defines concrete trigger conditions and
equivalence tests.

## 6. No-Live Validation Matrix

Implementation acceptance requires local-only tests or explicit equivalent
replacement tests for:

| Requirement | Minimum test surface | Expected test file |
|---|---|---|
| all body chapters accepted | Agent run accepted; Service final assembly can complete | `tests/agent/test_runner.py`, `tests/agent/test_service_bridge.py` |
| one body chapter writer blocked | Agent body readiness partial/blocked; no accepted source for failed chapter | `tests/agent/test_runner.py` |
| provider timeout/network/rate/malformed/http error | provider runtime blocked; no content repair budget consumed | `tests/agent/test_repair_policy.py`, `tests/agent/test_runner.py` |
| prompt contract failure | content/contract blocked; no provider-runtime classification | `tests/agent/test_runner.py` |
| `llm_exception + code_bug` | internal code-bug fail-closed; secret canaries redacted | `tests/agent/test_runner.py`, `tests/agent/test_tool_adapters.py` |
| `needs_more_facts` | terminal fact gap; no source probing | `tests/agent/test_repair_policy.py` |
| repair budget exhausted | terminal repair budget exhausted | `tests/agent/test_repair_policy.py`, `tests/agent/test_runner.py` |
| mixed accepted/failed chapters | all in-scope body chapters attempted independently | `tests/agent/test_runner.py`, `tests/services/test_chapter_orchestrator.py` |
| duplicate chapter rows | fail-closed; no report markdown | `tests/agent/test_service_bridge.py`, `tests/services/test_final_chapter_assembler.py` |
| unsafe ToolTrace data | prompt/draft/raw provider/audit/API key/header/model/base URL absent | `tests/agent/test_tool_adapters.py`, `tests/services/test_llm_run_artifacts.py` |
| cancel before first chapter | fail closed before body generation; no report markdown | `tests/agent/test_runner.py`, `tests/agent/test_service_bridge.py` |
| deadline between writer and auditor | fail closed; no content repair budget consumed | `tests/agent/test_runner.py`, `tests/agent/test_repair_policy.py` |
| Agent package Host isolation | `fund_agent/agent` does not import `fund_agent.host` | `tests/agent/test_contracts.py` or import-boundary test |

Forbidden validation:

- real provider API call;
- `fund-analysis analyze --use-llm` live command;
- provider readiness check;
- endpoint/DNS/curl/socket probe;
- network-dependent token counting;
- retained live artifact as the only equivalence source.

Allowed test doubles:

- fake writer client;
- fake auditor client;
- `httpx.MockTransport`;
- monkeypatch/test doubles that do not hit network;
- in-memory `StructuredFundDataBundle` / `ChapterFactProjection`.

## 7. Residual Owners

Known residuals after this first Agent implementation:

| Residual | Owner | Disposition |
|---|---|---|
| typed patch repair API | future typed patch API gate | current `patch` remains whole-chapter regenerate |
| provider timeout retry attempt visibility | Service/provider-client owner | Agent observes final provider result and safe scalar diagnostics only |
| prompt-contract subcategory terminal naming | Agent implementation evidence / code review | terminal may stay coarse, but chapter-attributed blocked reasons must preserve subcategory |
| `blocked_tool_contract` terminal | future tool-contract gate | omitted from first terminal set until concrete trigger conditions exist |

If implementation discovers another current Service behavior not representable
by Agent contracts, it must stop before staging or committing implementation work
and return to controller with a named owner.

## 8. Review Route

Use two independent reviews when available:

- AgentDS review;
- AgentCodex review as operator-authorized Codex capacity while AgentMiMo is
  absent.

Review focus:

- plan is code-generation-ready but does not implement code;
- allowed files are sufficient and not overbroad;
- Service/Host/Agent/Fund ownership is preserved;
- terminal mapping is complete and does not misclassify code bugs;
- no-live equivalence matrix is enforceable;
- ToolTrace safe scalar contract is complete;
- validation commands are local-only;
- implementation scope does not include live provider, runtime/default changes,
  score-loop, multi-year, golden/readiness, PR/push/release or external state.

Required review artifacts:

- `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-codex-20260608.md`

## 9. Controller Decision Options

Controller may choose one of:

- `PLAN_ACCEPTED_IMPLEMENTATION_AUTHORIZED`: implementation may proceed exactly
  through E1-E4 plus implementation evidence and triggered README updates from
  E5 with no live/provider/network commands; implementation must stop before
  code review, controller judgment or control-doc sync;
- `PLAN_ACCEPTED_WITH_PRE_IMPLEMENTATION_FIXES`: planning worker must revise
  specific plan gaps before implementation;
- `PLAN_BLOCKED`: implementation remains forbidden and the blocker owner must be
  recorded.

Even if implementation is authorized, the implementation worker must stop before
any action outside allowed files or allowed no-live commands.

Partial acceptance rule:

- implementation must proceed sequentially through E1-E4;
- if E4 Service bridge equivalence fails, implementation worker must stop before
  staging or committing implementation work and return to controller;
- accepting E1-E3 without E4 requires a separate controller judgment that
  explicitly reclassifies the partial Agent package as non-production code.

## 10. Local Validation For This Plan

This planning artifact validates by review and formatting only:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md
```

No source tests are required before this plan is accepted because no source code
is changed by this gate.

## 11. Stop Conditions

Stop or return to controller if:

- reviewer finds this plan authorizes live/provider/network validation;
- reviewer finds Service provider construction moves into Agent;
- reviewer finds Host business opacity is weakened;
- reviewer finds Fund domain logic rewritten in Agent;
- reviewer finds final assembly readiness weaker than current Service behavior;
- reviewer finds terminal mapping incomplete or `llm_exception + code_bug`
  misclassified;
- reviewer finds ToolTrace can serialize unsafe data;
- local validation fails;
- implementation worker needs to write code-review artifact, controller judgment
  artifact, `docs/current-startup-packet.md` or `docs/implementation-control.md`;
- implementation worker needs to import `fund_agent.host` from `fund_agent/agent`;
- user redirects to live evidence or runtime implementation before review and
  controller judgment.
