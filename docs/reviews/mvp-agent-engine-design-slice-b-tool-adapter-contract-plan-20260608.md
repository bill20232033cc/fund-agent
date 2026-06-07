# MVP Agent Engine Design Slice B Tool Adapter Contract Plan

## 1. Gate Role

Role: `planning worker`.

This artifact opens Slice B under the accepted `Agent Engine Design Refresh Gate`.
It is a design-only plan for future Agent tool adapter contracts. It does not
authorize implementation, source edits, tests, provider calls or runtime changes.

Accepted parent artifacts:

- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md`
- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md`
- `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md`

## 2. Objective

Define the future Agent ToolRegistry adapter contract for existing Fund
primitives without rewriting Fund logic or moving Service-owned provider
construction into Agent.

The Slice B design must be precise enough for a later implementation planning
gate to generate adapter code without deciding:

- tool names;
- input/output schema identities;
- safe trace serialization fields;
- error taxonomy;
- provider-client boundary;
- `EvidenceAvailability` boundary;
- runtime diagnostics allowlist.

## 3. Current Facts

Current Fund primitives:

- `project_chapter_facts()` / `ChapterFactProvider.project()` build
  `ChapterFactProjection` from an in-memory `StructuredFundDataBundle`.
- `derive_evidence_availability()` derives same-source `EvidenceAvailability`
  from `ChapterFactProjection`.
- `write_chapter()` consumes `ChapterWriterInput` and an explicit
  `ChapterLLMClient | None`, then returns `ChapterWriteResult`.
- `audit_chapter_programmatic()` consumes `ChapterAuditInput` and returns
  deterministic `ChapterProgrammaticAuditResult`.
- `audit_chapter_llm()` consumes `ChapterAuditInput` and an explicit
  `ChapterAuditLLMClient | None`, then returns `ChapterLLMAuditResult`.
- `audit_chapter()` currently aggregates programmatic and LLM audit into
  `ChapterAuditResult`.

Current safety facts:

- `ChapterDraft` contains `markdown` and `model_name`; this may be used
  in-memory for execution but must not be serialized into ToolTrace.
- `ChapterLLMAuditResult` contains `raw_response` and `model_name`; these may be
  used in-memory for audit aggregation but must not be serialized into ToolTrace.
- `ChapterLLMRuntimeDiagnostic` contains `model_name` and `message`; current safe
  serializers use allowlisted scalar projections and explicitly omit unsafe
  fields.
- Current `DiagnosticConsistencyStatus` values are `consistent`,
  `missing_terminal_runtime_diagnostic`, `terminal_category_conflict` and
  `non_runtime_terminal_without_scalar`.

Accepted Slice A facts:

- `EvidenceAvailability` is derived once at run level after
  `ChapterFactProjection` exists and before first `ChapterTask` preparation.
- `EvidenceAvailability` is not a ToolRegistry tool unless a later controller
  judgment explicitly reopens that boundary.
- Agent `FinalAssemblyReadiness` is a body-readiness handoff into current
  Service final assembly, not a replacement for Service final product authority.

## 4. Non-Goals

This Slice B plan forbids:

- creating `fund_agent/agent`;
- implementing ToolRegistry, ToolTrace, adapters or schemas;
- moving `ChapterOrchestrator` code;
- changing Fund primitive behavior;
- changing `FundLLMExecutionContract` or provider construction;
- putting provider writer/auditor clients into the registry as tools;
- changing timeout, retry, provider, default model, base URL or budget behavior;
- running live `--use-llm`, retry, curl, DNS, socket, endpoint or provider readiness probes;
- introducing `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime;
- changing quality gate, golden/readiness, score-loop, multi-year runtime,
  public chapter ids `0-7`, stdout semantics or final judgment semantics;
- copying or rewriting upstream Dayu code;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 5. Tool Registry Boundary

Future first Agent ToolRegistry may expose only wrappers around current Fund
primitives:

| Tool name | Existing primitive | Scope |
|---|---|---|
| `fund.project_chapter_facts` | `project_chapter_facts()` / `ChapterFactProvider.project()` | Build one `ChapterFactProjection` from explicit in-memory structured bundle |
| `fund.write_chapter` | `write_chapter()` | Produce one chapter draft or writer-blocked result from explicit writer input |
| `fund.audit_programmatic` | `audit_chapter_programmatic()` | Run deterministic programmatic audit only |
| `fund.audit_semantic` | `audit_chapter_llm()` | Run bounded semantic LLM audit only |

Explicitly not registry tools:

- `derive_evidence_availability()`: run-level same-source precomputation owned
  by Agent run preparation per Slice A.
- provider writer/auditor clients: Service-constructed typed per-run fields,
  passed into relevant Fund tool adapters but not registered as tools.
- Service final assembly: remains Service-owned until a later implementation
  gate changes the boundary.
- Host lifecycle/cancel/deadline: observed by Agent around tool calls, not a
  ToolRegistry capability.

## 6. Tool Contract Decisions

### 6.1 `fund.project_chapter_facts`

Input schema identity: `agent_tool_input.fund.project_chapter_facts.v1`.

In-memory input:

- `fund_code`
- `report_year`
- `structured_data`

Safe input identity:

- fund code;
- report year;
- structured bundle schema/type label;
- available top-level structured field names;
- no extracted values, no annual report text, no PDF/cache/source helper paths.

Output:

- in-memory `ChapterFactProjection`;
- safe output identity with projection schema version, fund code, report year,
  fund type, chapter ids, fact counts, anchor counts, global missing reasons and
  source field ids.

Error taxonomy:

- `tool_input_invalid`: fund identity mismatch or invalid structured input.
- `tool_contract_error`: projection invariant violation.
- `tool_internal_error`: unexpected exception.

Boundary:

- This tool must not read repositories, annual reports, PDF/cache/source helpers,
  filesystem state, provider config, Host state or retained artifacts.

### 6.2 Run-Level `EvidenceAvailability`

`derive_evidence_availability()` remains a run-level precomputation, not a
ToolRegistry tool.

Accepted contract:

- run preparation invokes it exactly once after `ChapterFactProjection` exists;
- result is stored on `AgentReportRun.evidence_availability`;
- all `fund.write_chapter` calls receive the same value or immutable copy;
- repair attempts reuse the same value;
- no recomputation from retained artifacts, filesystem state or external state.

Safe identity:

- availability schema version;
- source projection schema version;
- requirement ids;
- requirement statuses;
- source field ids;
- fact ids;
- evidence anchor ids;
- gap reference ids and missing reasons.

Forbidden identity:

- fact values;
- anchor notes if they disclose raw source text beyond existing safe ids;
- raw report text;
- retained artifact paths as evidence source.

### 6.3 `fund.write_chapter`

Input schema identity: `agent_tool_input.fund.write_chapter.v1`.

In-memory input:

- `ChapterWriterInput`;
- Service-constructed writer `ChapterLLMClient | None` from per-run fields.

Safe input identity:

- projection schema version;
- fund code;
- report year;
- chapter id and title;
- writer mode;
- max output chars;
- prompt payload mode;
- typed required output item ids;
- availability requirement ids and statuses used by the chapter;
- allowed fact ids;
- allowed anchor ids;
- repair attempt index;
- prior issue ids in repair context.

Serialized trace must not include:

- system prompt;
- user prompt;
- draft markdown;
- fact values;
- anchor note text;
- raw provider response;
- model value;
- base URL value;
- API key or Authorization header.

Output:

- in-memory `ChapterWriteResult`;
- safe output identity with writer status, stop reason, issue ids, issue
  reasons, issue fact ids, issue anchor ids, item rule ids, response chars,
  finish reason, max output chars, used fact ids, used anchor ids, declared
  missing reasons and deleted item rule ids.

Output safety:

- `ChapterDraft.markdown` may remain in-memory for audit and final accepted
  report flow but must not be serialized into ToolTrace.
- `ChapterDraft.model_name` must not be serialized.
- `ChapterWriterPrompt.system_prompt` and `user_prompt` must not be serialized.

Error taxonomy:

- `tool_input_invalid`: missing chapter, invalid repair context or identity mismatch.
- `writer_blocked`: writer returns blocked result.
- `provider_runtime_timeout`: provider timeout exception mapped by Service/provider
  client diagnostics.
- `provider_runtime_rate_limited`
- `provider_runtime_malformed_response`
- `provider_runtime_network`
- `provider_runtime_http_error`
- `tool_internal_error`: unexpected non-provider exception.

### 6.4 `fund.audit_programmatic`

Input schema identity: `agent_tool_input.fund.audit_programmatic.v1`.

In-memory input:

- `ChapterAuditInput` with `run_programmatic=True`;
- draft from the immediately preceding successful writer attempt.

Safe input identity:

- fund code;
- report year;
- chapter id;
- draft schema version;
- used fact ids;
- used anchor ids;
- declared missing reasons;
- deleted item rule ids;
- typed chapter contract schema/version identity when present;
- `run_programmatic=True`.

Serialized trace must not include:

- draft markdown;
- prompt text;
- raw source text.

Output:

- in-memory `ChapterProgrammaticAuditResult`;
- safe output identity with status, checked rules, issue ids, rule codes,
  severity, layer, repair hints, fact ids, anchor ids and item rule ids.

Error taxonomy:

- `tool_input_invalid`: missing draft or chapter identity mismatch.
- `audit_programmatic_failed`: deterministic audit returns fail.
- `audit_programmatic_blocked`: deterministic audit returns blocked.
- `tool_contract_error`: invalid audit result shape.
- `tool_internal_error`: unexpected exception.

Boundary:

- Programmatic audit runs before semantic audit in future Agent scheduling.
- Programmatic blockers must not be overwritten by semantic audit pass.

### 6.5 `fund.audit_semantic`

Input schema identity: `agent_tool_input.fund.audit_semantic.v1`.

In-memory input:

- `ChapterAuditInput` with `run_llm=True`;
- Service-constructed auditor `ChapterAuditLLMClient | None` from per-run fields.

Safe input identity:

- fund code;
- report year;
- chapter id;
- draft schema version;
- used fact ids;
- used anchor ids;
- declared missing reasons;
- audit focus ids;
- bounded semantic audit enabled flag.

Serialized trace must not include:

- draft markdown;
- raw audit response;
- model value;
- prompt text;
- API key or Authorization header.

Output:

- in-memory `ChapterLLMAuditResult`;
- safe output identity with status, issue ids, rule codes, severity, repair
  hints, fact ids, anchor ids, item rule ids and finish reason.

Output safety:

- `ChapterLLMAuditResult.raw_response` must not be serialized.
- `ChapterLLMAuditResult.model_name` must not be serialized.

Error taxonomy:

- `tool_input_invalid`: missing draft or identity mismatch.
- `semantic_audit_unavailable`: auditor client is absent when semantic audit is required.
- `semantic_audit_parse_blocked`: LLM audit line protocol parse failure.
- `provider_runtime_timeout`
- `provider_runtime_rate_limited`
- `provider_runtime_malformed_response`
- `provider_runtime_network`
- `provider_runtime_http_error`
- `tool_internal_error`

## 7. ToolTrace Safe Serialization

Future `ToolTrace` serialized rows must use allowlist projection only.

Allowed fields:

- schema version;
- trace id;
- run id;
- tool name;
- phase;
- chapter id;
- attempt index;
- status;
- stop reason or tool error category;
- issue ids;
- issue reason/rule-code counts;
- fact ids;
- anchor ids;
- item rule ids;
- requirement ids and statuses;
- response chars;
- finish reason;
- max output chars;
- elapsed milliseconds;
- HTTP status code;
- request id;
- provider runtime category;
- chapter failure category;
- timeout budget scalars;
- prompt char counts;
- approximate prompt token counts;
- allowed fact count;
- allowed anchor count;
- `DiagnosticConsistencyStatus` value.

Forbidden fields:

- prompt text;
- draft markdown;
- fact values;
- anchor note text if it includes source prose;
- raw provider response;
- raw audit response;
- raw provider request/body;
- API key;
- Authorization header;
- bearer token;
- model value;
- base URL value;
- provider error message beyond existing redacted safe message policy.

Runtime diagnostics rule:

- Agent serialized state and ToolTrace must not store `ChapterLLMRuntimeDiagnostic`
  wholesale.
- The implementation plan must define an allowlisted projection equivalent to
  current safe serializers.
- `diagnostic_consistency_status` must use the current
  `DiagnosticConsistencyStatus` literal set or a named explicit future equivalent:
  `consistent`, `missing_terminal_runtime_diagnostic`,
  `terminal_category_conflict`, `non_runtime_terminal_without_scalar`.

## 8. Error Taxonomy

Future adapter-level taxonomy:

| Category | Meaning | Retry/repair boundary |
|---|---|---|
| `tool_input_invalid` | Agent supplied invalid or identity-mismatched input | fail closed; implementation bug unless upstream data invalid |
| `tool_contract_error` | Fund primitive returned an invalid shape or invariant conflict | fail closed; code bug |
| `writer_blocked` | writer returned a blocked status | content/contract failure; may feed repair only if issue semantics permit |
| `audit_programmatic_failed` | deterministic audit found blocking issues | content/contract failure; programmatic-first blocker |
| `audit_programmatic_blocked` | deterministic audit could not complete safely | fail closed |
| `semantic_audit_unavailable` | required semantic auditor absent | fail closed unless policy disables semantic audit |
| `semantic_audit_parse_blocked` | LLM audit protocol parse failed | fail closed; may feed bounded repair if current semantics permit |
| `provider_runtime_timeout` | provider timeout | Service/provider runtime category; not Agent content repair |
| `provider_runtime_rate_limited` | provider rate limit | fail closed; no hidden Agent retry |
| `provider_runtime_malformed_response` | provider malformed/non-contract response | fail closed |
| `provider_runtime_network` | provider network error | fail closed |
| `provider_runtime_http_error` | provider HTTP error | fail closed |
| `host_interrupted` | Host cancel/deadline observed at scheduling boundary or after tool return | terminal host interruption |
| `tool_internal_error` | unexpected exception | fail closed; code bug |

Provider runtime timeout retry remains Service/provider-client behavior. Agent
repair policy must not convert provider runtime categories into hidden content
repair attempts.

## 9. Validation Plan

This design-only Slice B validates by artifact review and local formatting only.

Required local command:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md
```

Expected result:

- exit code `0`;
- no whitespace errors.

No source tests are required because this artifact does not edit source or tests.

Forbidden validation:

- no `uv run fund-analysis analyze --use-llm`;
- no provider readiness check;
- no endpoint/DNS/curl/socket probe;
- no test that constructs a real provider or hits network;
- no implementation scaffold.

## 10. Review Route

Use two independent reviews when available:

- AgentDS review;
- AgentCodex review as operator-authorized Codex capacity while AgentMiMo is absent.

Review focus:

- tool boundary wraps existing Fund primitives only;
- `EvidenceAvailability` remains run-level non-tool precomputation;
- provider clients remain Service-constructed per-run fields, not registry tools;
- ToolTrace and Agent serialized diagnostics are allowlist-only and exclude model
  value, base URL value, raw responses, prompt, draft and secrets;
- error taxonomy keeps runtime failures separate from content repair;
- programmatic audit remains before semantic audit and cannot be overridden by semantic pass;
- no implementation or live/provider scope is authorized.

Required review artifacts:

- `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-review-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-review-codex-20260608.md`

## 11. Stop Conditions

Stop or return to controller judgment if:

- reviewer finds the plan authorizes implementation;
- reviewer finds provider construction moved into Agent;
- reviewer finds provider clients registered as tools;
- reviewer finds `EvidenceAvailability` can be recomputed or called as a tool;
- reviewer finds ToolTrace can serialize prompt, draft, raw provider/audit response,
  model value, base URL value or secrets;
- reviewer finds runtime failures can become hidden Agent repair attempts;
- reviewer finds semantic audit can override programmatic blockers;
- local validation fails;
- user redirects to live evidence or Agent runtime implementation.

MiMo absence alone is not a stop condition after operator authorization to use
available Codex reviewer capacity.

## 12. Completion Report Format

Planning worker should report:

- artifact path;
- parent artifacts read;
- validation command and result;
- review route used;
- blocking findings, if any;
- whether the artifact is ready for controller judgment.

