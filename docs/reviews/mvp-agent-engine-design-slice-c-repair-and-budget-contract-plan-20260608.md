# MVP Agent Engine Design Slice C Repair And Budget Contract Plan

## 1. Gate Role

Role: `planning worker`.

This artifact opens Slice C under the accepted `Agent Engine Design Refresh Gate`.
It is a design-only plan for future Agent repair and budget contracts. It does
not authorize implementation, source edits, tests, provider calls or runtime
changes.

Accepted parent artifacts:

- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md`
- `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-controller-judgment-20260608.md`

## 2. Objective

Define the future Agent repair and budget contract without changing current
provider runtime behavior or Fund audit semantics.

The Slice C design must separate:

- Service-owned provider runtime ceilings;
- provider-client timeout retry;
- Agent-owned content repair attempts;
- Fund-owned issue ids and `repair_hint` semantics;
- Host-owned cancel/deadline lifecycle;
- fail-closed terminal states.

## 3. Current Facts

Current Service runtime facts:

- `ProviderRuntimeBudget` owns writer timeout, auditor timeout, repair timeout,
  timeout max attempts, timeout backoff, max output chars and prompt payload mode.
- Provider timeout retry is implemented in provider client `_complete()`: only
  `httpx.TimeoutException` retries within `timeout_max_attempts`; network,
  rate limit, malformed response and HTTP failures fail closed without retry.
- `FundLLMRuntimePlan` owns `chapter_policy`, `assembly_policy`,
  `provider_runtime_budget`, `quality_fail_closed_policy`,
  `safe_diagnostic_policy`, `typed_template_path` and Host-readable
  `host_timeout_seconds`.

Current chapter repair facts:

- `ChapterOrchestrationPolicy.max_repair_attempts` is the current content repair
  budget.
- `_decide_repair()` returns `none`, `regenerate`, `needs_more_facts` or `stop`.
- `repair_hint=needs_more_facts` maps to terminal `needs_more_facts`; Service
  does not source-probe.
- `repair_hint=none` maps to stop.
- `patch` and `regenerate` currently map to bounded whole-chapter regenerate.
- `remaining_budget <= 0` maps to terminal `repair_budget_exhausted`.
- missing auditor client or LLM unavailable maps to terminal `llm_unavailable`.
- `_repair_context_from_audit()` builds `ChapterRepairContext` from previous
  issue ids, sanitized issue messages and deterministic required corrections.

Accepted Slice B facts:

- provider runtime categories must not become hidden Agent content repair attempts;
- prompt char/token counts must be derived from in-memory length heuristics only;
- `host_interrupted` belongs to Host/Agent scheduling boundary, not adapter implementation;
- `request_id` must later be an explicit scalar allowlist field.

## 4. Non-Goals

This Slice C plan forbids:

- creating `fund_agent/agent`;
- implementing repair policy, budget objects, ToolRegistry, ToolTrace, adapters or schemas;
- changing current `ProviderRuntimeBudget`, timeout defaults or retry behavior;
- changing `ChapterOrchestrationPolicy.max_repair_attempts`;
- changing Fund `ChapterAuditRepairHint` semantics;
- adding source probing, repository/PDF access or retained artifact lookup;
- changing provider/default/runtime/budget/config behavior;
- running live `--use-llm`, retry, curl, DNS, socket, endpoint or provider readiness probes;
- introducing `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime;
- changing quality gate, golden/readiness, score-loop, multi-year runtime,
  public chapter ids `0-7`, stdout semantics or final judgment semantics;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 5. Budget Ownership

### 5.1 Service Provider Runtime Budget

Service continues to own provider runtime ceilings:

- writer initial timeout;
- auditor timeout;
- writer repair timeout;
- provider timeout max attempts;
- provider timeout backoff;
- max output chars;
- prompt payload mode;
- Host timeout scalar.

Future Agent may read these as explicit per-run runtime inputs, but must not
construct providers, infer defaults, mutate budgets, perform endpoint probes or
fallback to another runtime.

Provider timeout retry remains inside the Service/provider client. Agent must
observe only the final provider result or provider runtime exception category,
plus safe scalar diagnostics.

### 5.2 Agent Content Repair Budget

Agent owns content repair attempt accounting after implementation:

- per chapter `max_repair_attempts`;
- attempt index;
- remaining content repair budget;
- repair exhaustion terminal state;
- repair decision ledger.

This budget is separate from provider timeout attempts.

Rules:

- one writer attempt plus one audit pass is attempt index `0`;
- a regenerate decision consumes one content repair attempt;
- provider timeout retry attempts inside one provider request do not consume
  Agent content repair budget;
- provider runtime failure does not trigger content repair;
- hidden Agent retry is forbidden.

### 5.3 Hidden Retry Definition

`hidden_retry` means any Agent-initiated repeated writer, auditor, tool call or
repair action that is not represented in the chapter attempt ledger, tool trace
or repair decision ledger.

Accepted rule:

- `hidden_retry_allowed=false`;
- every Agent-initiated repeated writer/auditor/tool action must have a new
  attempt ledger entry or explicit ToolTrace row;
- provider client internal timeout attempts remain provider runtime diagnostics,
  not hidden Agent retries;
- Host re-entry/resume is future Host scope and must not silently duplicate an
  Agent content attempt.

## 6. Repair Decision Contract

Future Agent `RepairPolicy.decide` consumes Fund-owned audit output:

- `ChapterAuditResult.status`;
- `ChapterAuditResult.accepted`;
- `ChapterAuditResult.repair_hint`;
- `ChapterAuditIssue.issue_id`;
- `ChapterAuditIssue.rule_code`;
- `ChapterAuditIssue.repair_hint`;
- current remaining Agent content repair budget;
- auditor availability policy.

Agent must not redefine Fund issue meaning. Fund remains owner of issue ids,
rule codes, `repair_hint`, repair messages and required correction semantics.

Decision mapping:

| Condition | Agent action | Terminal stop reason |
|---|---|---|
| audit accepted | `none` | `none` |
| semantic auditor required but unavailable | `stop` | `llm_unavailable` |
| LLM audit unavailable issue | `stop` | `llm_unavailable` |
| aggregate `repair_hint=needs_more_facts` | `needs_more_facts` | `needs_more_facts` |
| aggregate `repair_hint=none` | `stop` | current auditor failure stop reason |
| remaining content repair budget <= 0 | `stop` | `repair_budget_exhausted` |
| audit failed/blocked and `repair_hint in {patch, regenerate}` | `regenerate` | `none` |
| unsupported audit state | `stop` | current auditor failure stop reason |
| provider runtime timeout/rate-limit/malformed/network/http error | `stop` | mapped provider runtime stop reason |
| Host cancel/deadline observed | `stop` | `host_interrupted` |

`patch` remains mapped to whole-chapter regenerate until a separate accepted gate
adds a typed patch API.

## 7. Repair Context Contract

Future `ChapterRepairContext` equivalent must contain only:

- next attempt index;
- previous issue ids;
- sanitized previous issue messages;
- deterministic required corrections.

It must not contain:

- raw audit response;
- raw provider response;
- prompt text;
- draft markdown beyond the in-memory writer input needed for execution;
- API key, Authorization header, bearer token, model value or base URL value;
- source probing instructions.

Required correction semantics remain derived from Fund/programmatic audit issue
semantics and must be deterministic.

## 8. Terminal State Contract

Future Agent chapter terminal states:

| Terminal state | Meaning |
|---|---|
| `accepted` | draft and audits accepted |
| `blocked_content` | content/contract issue cannot be repaired safely |
| `blocked_needs_more_facts` | same-source facts are insufficient; no source probing in Agent |
| `blocked_provider_runtime` | provider runtime failure; not content repair |
| `blocked_repair_budget_exhausted` | content repair attempts exhausted |
| `blocked_tool_contract` | adapter/Fund tool invariant conflict |
| `host_interrupted` | Host cancel/deadline observed at scheduling boundary or after tool return |

Run-level status remains compatible with Slice A:

- all required body chapters accepted plus body readiness ready -> `accepted`;
- any body chapter terminal block -> `partial_fail_closed`;
- Host interruption -> `host_interrupted`.

Service final product fail-closed mapping remains unchanged until a later
implementation gate explicitly changes it.

## 9. Diagnostics And Trace Requirements

Every Agent repair decision must be traceable by safe ids and scalar fields:

- chapter id;
- attempt index;
- previous issue ids;
- aggregate repair hint;
- action;
- remaining content repair budget before decision;
- remaining content repair budget after decision;
- terminal stop reason;
- provider runtime category when applicable;
- `DiagnosticConsistencyStatus` when applicable.

Prompt char counts and approximate prompt token counts, when present, must be
derived from in-memory prompt length heuristics only. They must not serialize
prompt text, call external token-count services or read retained prompts.

`request_id`, when present, must be an optional scalar from an explicit response
header allowlist only. No arbitrary header map, provider URL, cookie,
Authorization header or provider config value may be serialized.

## 10. Validation Plan

This design-only Slice C validates by artifact review and local formatting only.

Required local command:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md
```

Expected result:

- exit code `0`;
- no whitespace errors.

Forbidden validation:

- no `uv run fund-analysis analyze --use-llm`;
- no provider readiness check;
- no endpoint/DNS/curl/socket probe;
- no test that constructs a real provider or hits network;
- no implementation scaffold.

## 11. Review Route

Use two independent reviews when available:

- AgentDS review;
- AgentCodex review as operator-authorized Codex capacity while AgentMiMo is absent.

Review focus:

- Service provider runtime budget is separate from Agent content repair budget;
- provider timeout retry remains provider-client behavior only;
- hidden retry is explicitly defined and forbidden;
- Fund issue ids and repair hints remain Fund-owned semantics;
- `needs_more_facts` does not source-probe;
- provider runtime failures do not trigger content repair;
- Host interruption stays scheduling/lifecycle boundary;
- diagnostics remain allowlist-only;
- no implementation or live/provider scope is authorized.

Required review artifacts:

- `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-review-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-review-codex-20260608.md`

## 12. Stop Conditions

Stop or return to controller judgment if:

- reviewer finds the plan authorizes implementation;
- reviewer finds Agent mutates provider runtime budget or constructs provider clients;
- reviewer finds provider runtime failures can trigger content repair;
- reviewer finds hidden Agent retry allowed;
- reviewer finds `needs_more_facts` can source-probe;
- reviewer finds Fund issue semantics redefined in Agent;
- reviewer finds Host lifecycle implemented inside tool adapters or repair policy;
- local validation fails;
- user redirects to live evidence or Agent runtime implementation.

MiMo absence alone is not a stop condition after operator authorization to use
available Codex reviewer capacity.

## 13. Completion Report Format

Planning worker should report:

- artifact path;
- parent artifacts read;
- validation command and result;
- review route used;
- blocking findings, if any;
- whether the artifact is ready for controller judgment.
