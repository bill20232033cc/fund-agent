# MVP Agent Engine Design Slice D No-Live Equivalence Validation Plan

## 1. Gate Role

Role: `planning worker`.

This artifact opens Slice D under the accepted `Agent Engine Design Refresh Gate`.
It is a design-only validation plan for future Agent-engine implementation
planning. It does not authorize implementation, source edits, tests, provider
calls or runtime changes.

Accepted parent artifacts:

- `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-controller-judgment-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-controller-judgment-20260608.md`

## 2. Objective

Define no-live equivalence criteria that a later Agent implementation plan must
satisfy before moving current Service `ChapterOrchestrator` execution mechanics
into Agent.

The objective is not byte-for-byte internal state equivalence. The required
equivalence is behavioral and safety-oriented:

- same accepted/partial/fail-closed chapter outcome matrix;
- same terminal failure category and stop-reason meaning;
- same bounded content repair budget semantics;
- no weaker final assembly readiness;
- no deterministic fallback on LLM failure;
- safe ToolTrace scalar assertions;
- no provider/network/live command.

## 3. Current Evidence Surface

Existing local tests already cover equivalent acceptance surfaces:

- `tests/services/test_chapter_orchestrator.py` covers accepted chapters,
  provider runtime failures, prompt-contract failures, repair budget exhaustion,
  `needs_more_facts`, mixed accepted/blocked/failed matrices and safe runtime
  diagnostics.
- `tests/services/test_final_chapter_assembler.py` covers accepted final assembly,
  partial/blocked orchestration fail-closed behavior, missing accepted draft,
  missing accepted conclusion and source accepted chapter ids.
- `tests/services/test_fund_analysis_service_llm.py` covers Service LLM result
  assembly, partial result no deterministic fallback and final assembly status.
- `tests/services/test_llm_run_artifacts.py` covers incomplete result artifacts,
  chapter matrices and runtime diagnostic serialization.

Future implementation planning may add tests or adapt these assertions, but it
must not weaken them.

## 4. Non-Goals

This Slice D plan forbids:

- creating `fund_agent/agent`;
- implementing Agent runtime, ToolRegistry, ToolTrace, adapters or schemas;
- moving `ChapterOrchestrator` code;
- adding or editing tests in this gate;
- changing provider/default/runtime/budget/config behavior;
- running live `--use-llm`, retry, curl, DNS, socket, endpoint or provider readiness probes;
- changing quality gate, golden/readiness, score-loop, multi-year runtime,
  public chapter ids `0-7`, stdout semantics or final judgment semantics;
- introducing `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 5. Equivalence Matrix

### 5.1 Chapter Outcome Matrix

Future Agent implementation must preserve these current outcomes:

| Scenario | Current expected outcome | Future Agent expected outcome |
|---|---|---|
| all required body chapters accepted | orchestration accepted | run accepted and body readiness ready |
| one body chapter writer blocked | orchestration partial/blocked fail-closed | partial_fail_closed; failed chapter not accepted |
| one body chapter provider timeout | chapter stop reason `llm_timeout`; no report markdown | blocked_provider_runtime; no report markdown |
| one body chapter provider network/rate/malformed/http error | provider runtime fail-closed | blocked_provider_runtime; no content repair |
| audit parse/protocol blocked | chapter blocked/failed according to current stop reason | content/contract block; no semantic override |
| `repair_hint=needs_more_facts` | `needs_more_facts`; no source probing | blocked_needs_more_facts; no source probing |
| repair budget exhausted | `repair_budget_exhausted` | blocked_repair_budget_exhausted |
| mixed accepted/failed chapters | all body chapters attempted independently | same attempted matrix; no prior-failure skip |

Minimum assertion:

- generated/attempted chapter ids must remain row-complete for body chapters in
  scope, except true explicit scope exclusion or global dependency stop;
- accepted conclusions include only accepted chapters;
- failed/blocked chapters never become accepted final sources.

### 5.2 Terminal Category Equivalence

Future implementation planning must provide a mapping table from current
`ChapterRunStopReason` and `ChapterFailureCategory` to future Agent terminal
state. The mapping key is the pair `(stop_reason, failure_category)`, not
`stop_reason` alone.

Required minimum mappings:

- `none` -> accepted path;
- `llm_timeout`, `llm_rate_limited`, `llm_malformed_response`,
  `llm_network_error`, `llm_unavailable`, `llm_empty_response` with
  provider-classified failure categories -> provider/runtime blocked state;
- `llm_exception` with `failure_category=code_bug` -> fail-closed internal
  code bug state, not provider/runtime;
- `missing_required_structure`, `missing_required_output_marker`,
  `unknown_anchor`, `response_too_long`, `response_incomplete`,
  `llm_contract_violation` -> prompt/content contract blocked state;
- `auditor_failed`, `auditor_blocked` -> audit blocked/content state;
- `repair_budget_exhausted` -> repair budget exhausted state;
- `needs_more_facts`, `missing_required_facts` -> needs more facts/fact gap state;
- `fund_type_unknown` -> fund identity/fact-gap precondition state;
- `writer_blocked` -> writer precondition blocked state with no provider call;
- `dependency_missing` -> true dependency state only;
- `chapter_not_in_scope` -> explicit scope exclusion.

The future state names may differ, but the fail-closed meaning must not weaken.
The implementation plan must explicitly enumerate every current
`ChapterRunStopReason` and every current `ChapterFailureCategory`, including
`provider_runtime`, `llm_timeout`, `prompt_contract`, `audit_parse`,
`audit_rule_too_strict`, `fact_gap` and `code_bug`.

### 5.3 Repair Budget Equivalence

Future Agent implementation must preserve:

- attempt index starts at `0`;
- regenerate consumes content repair budget;
- provider timeout retry attempts do not consume content repair budget;
- provider runtime failures do not trigger content repair;
- `repair_hint=patch` and `repair_hint=regenerate` remain whole-chapter
  regenerate until a separate typed patch API gate;
- `repair_hint=none` stops;
- `repair_hint=needs_more_facts` stops without source probing;
- hidden Agent retry remains forbidden.

Minimum assertions:

- repair budget exhausted produces terminal `repair_budget_exhausted` equivalent;
- accepted-after-repair remains possible only within budget;
- no untraced writer/auditor/tool repetition exists.

### 5.4 Final Assembly Readiness Equivalence

Future Agent body readiness must not be weaker than current Service final
assembly readiness.

Minimum assertions:

- final report accepted only when required body chapters have accepted drafts and
  accepted conclusions;
- partial/blocked orchestration cannot produce complete report markdown;
- chapter 0 and chapter 7 are not accepted if required body readiness is blocked;
- source accepted chapter ids exclude blocked/failed chapters;
- required body chapter rows and source accepted chapter ids are unique;
- duplicate chapter rows remain fail-closed with no report markdown;
- Service final product fail-closed mapping and stdout semantics remain current
  authority until a later implementation gate changes them.

### 5.5 ToolTrace Safe Scalar Equivalence

Future no-live validation must assert ToolTrace serialized evidence includes
only safe scalar identities and excludes:

- prompt text;
- draft markdown;
- fact values;
- unsafe anchor prose;
- raw provider response;
- raw audit response;
- raw provider request/body;
- API key;
- Authorization header;
- bearer token;
- model value;
- base URL value;
- arbitrary response headers or provider config values.

Allowed diagnostic assertions:

- chapter id;
- attempt index;
- tool name;
- stop reason or terminal category;
- issue ids;
- fact ids;
- anchor ids;
- item rule ids;
- requirement ids/statuses;
- response chars;
- finish reason;
- elapsed milliseconds;
- status code;
- allowlisted request id scalar from an explicit response-header allowlist only;
- provider runtime category;
- chapter failure category;
- timeout budget scalar fields;
- prompt char counts and approximate token counts derived from in-memory length
  heuristics only;
- `DiagnosticConsistencyStatus`.

## 6. No-Live Validation Commands For Future Implementation Plan

Slice D does not run these commands now. A later implementation planning gate
must select exact tests from this no-live set or justify replacements:

```text
uv run pytest tests/services/test_chapter_orchestrator.py
uv run pytest tests/services/test_final_chapter_assembler.py
uv run pytest tests/services/test_fund_analysis_service_llm.py
uv run pytest tests/services/test_llm_run_artifacts.py
```

Allowed future test doubles:

- fake writer client;
- fake auditor client;
- `httpx.MockTransport`;
- monkeypatch/test doubles that do not hit network;
- in-memory `StructuredFundDataBundle` / `ChapterFactProjection`.

Forbidden future validation for this equivalence gate:

- real provider API call;
- `fund-analysis analyze --use-llm` live command;
- provider readiness check;
- endpoint/DNS/curl/socket probe;
- network-dependent token counting;
- retained live artifact as the only equivalence source.

## 7. Implementation Planning Preconditions

A later implementation plan must not start until it includes:

- current-to-future terminal mapping table;
- same-run chapter outcome matrix tests;
- repair budget equivalence tests;
- no weaker final assembly readiness tests;
- ToolTrace safe serialization tests;
- explicit no-live command list;
- explicit forbidden live/provider/network command list;
- residual risk owner for any current Service behavior not yet representable by
  future Agent contracts.

## 8. Review Route

Use two independent reviews when available:

- AgentDS review;
- AgentCodex review as operator-authorized Codex capacity while AgentMiMo is absent.

Review focus:

- equivalence criteria are concrete enough for later implementation planning;
- no-live constraints are enforceable;
- final assembly readiness is not weakened;
- repair budget and provider runtime budget remain separate;
- ToolTrace safety assertions are complete;
- no implementation or live/provider scope is authorized.

Required review artifacts:

- `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-codex-20260608.md`

## 9. Validation Plan

This design-only Slice D validates by artifact review and local formatting only.

Required local command:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md
```

Expected result:

- exit code `0`;
- no whitespace errors.

## 10. Stop Conditions

Stop or return to controller judgment if:

- reviewer finds the plan authorizes implementation;
- reviewer finds live/provider/network validation required;
- reviewer finds final assembly readiness weaker than current Service readiness;
- reviewer finds provider runtime failures can become content repair;
- reviewer finds ToolTrace can serialize unsafe fields;
- reviewer finds no concrete equivalence matrix;
- local validation fails;
- user redirects to live evidence or Agent runtime implementation.

MiMo absence alone is not a stop condition after operator authorization to use
available Codex reviewer capacity.

## 11. Completion Report Format

Planning worker should report:

- artifact path;
- parent artifacts read;
- validation command and result;
- review route used;
- blocking findings, if any;
- whether the artifact is ready for controller judgment.
