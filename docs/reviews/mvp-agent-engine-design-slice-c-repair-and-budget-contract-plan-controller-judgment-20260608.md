# MVP Agent Engine Design Slice C Repair And Budget Contract Plan Controller Judgment

## 1. Verdict

`PLAN_ACCEPTED_DESIGN_ONLY_WITH_FOLLOWUP_REQUIREMENTS`

Accepted plan:

- `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md`

Accepted reviews:

- `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-review-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-review-codex-20260608.md`

Reviewer route:

- AgentMiMo remained unavailable for this gate.
- AgentDS provided the first independent review.
- AgentCodex was used as the operator-authorized Codex reviewer capacity in MiMo's absence.

DS returned `PASS`. Codex returned `PASS_WITH_NON_BLOCKING_OBSERVATIONS`.

## 2. Boundary Judgment

This judgment accepts Slice C as design-only planning input.

This judgment does not authorize:

- Agent runtime implementation;
- `fund_agent/agent` package creation;
- repair policy, budget object, ToolRegistry, ToolTrace, adapter or schema implementation;
- migration of current Service `ChapterOrchestrator`;
- provider/default/runtime/budget/config change;
- live `--use-llm`, retry, endpoint probe, curl, DNS, socket probe or provider readiness check;
- LangGraph or MCP runtime;
- `dayu-agent`, `dayu.host` or `dayu.engine` production dependency;
- copying or rewriting upstream Dayu code;
- quality gate, golden/readiness, score-loop, multi-year runtime or public chapter ids `0-7` change;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 3. Accepted Slice C Design Facts

- Service provider runtime budget remains separate from future Agent content repair budget.
- Provider timeout retry remains Service/provider-client behavior. Agent observes final provider result or provider runtime exception category plus safe scalar diagnostics.
- Future Agent content repair budget covers chapter repair attempts only. Provider timeout retry attempts do not consume Agent repair budget.
- `hidden_retry` is defined as any Agent-initiated repeated writer, auditor, tool call or repair action not represented in attempt ledger, tool trace or repair decision ledger. `hidden_retry_allowed=false`.
- Fund owns issue ids, rule codes, repair hints, repair messages and required correction semantics. Agent repair policy consumes these signals but does not redefine them.
- `needs_more_facts` is terminal for the current Agent design and does not source-probe.
- Provider runtime timeout, rate-limit, malformed, network and HTTP errors do not trigger content repair.
- Prompt count diagnostics are derived only from in-memory prompt length heuristics and do not serialize prompt text.
- `request_id` is an optional scalar from an explicit response-header allowlist only.

## 4. Review Finding Disposition

### DS NBO-1: Terminal state name mapping not explicit

Disposition: `accepted_followup_requirement`

The later implementation planning gate must provide a mapping table from current `ChapterRunStopReason` values to future Agent terminal state names before any code changes.

### DS NBO-2: `blocked_tool_contract` may be premature

Disposition: `accepted_followup_requirement`

The later implementation planning gate must either define concrete trigger conditions for `blocked_tool_contract` or remove/rename that terminal state from the implementation contract.

### DS NBO-3: Design-only validation is minimal

Disposition: `accepted_future_validation_requirement`

The current design-only validation is sufficient. The later implementation planning gate must add contract-level validation that repair decision mapping exhaustively covers all current `ChapterRunStopReason` values and provider runtime categories.

### Codex NBO-1: Host interruption should be scheduler-normalized before repair policy input

Disposition: `accepted_followup_requirement`

Future `RepairPolicy.decide` must consume only an already-normalized interruption event/status emitted by Agent scheduling. Repair policy and tool adapters must not import, inspect or depend on Host context/state directly.

## 5. Parent Follow-Up Status

| Parent requirement | Slice C status | Judgment |
|---|---|---|
| Hidden retry semantics | resolved | accepted: hidden retry defined and forbidden |
| Prompt char/token count derivation | resolved | accepted: in-memory length heuristics only |
| `host_interrupted` scheduling boundary | resolved with follow-up | accepted: scheduler-normalized signal only before repair policy |
| `request_id` scalar allowlist shape | resolved | accepted: explicit response-header allowlist scalar only |
| Chapter-attributed blocked reasons | deferred | still owned by implementation planning or later state-model gate |
| Equivalence testing | deferred | still owned by Slice D or implementation planning before code changes |

## 6. Validation Accepted

Controller validation:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md
```

Result: pass.

DS reviewer validation:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md
```

Result: pass.

Codex reviewer validation:

```text
git branch --show-current
git status --short
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-review-codex-20260608.md
```

Result: pass.

No reviewer ran live provider, endpoint, network, PR, push, commit, source edit, test edit or control-doc edit actions.

## 7. Next Entry Point

Next authorized local entry is design-only:

- `MVP Agent Engine Design Slice D No-Live Equivalence Validation Plan`

Slice D must define no-live equivalence criteria before any implementation plan:

- accepted/partial/fail-closed chapter outcome matrix;
- terminal failure category equivalence;
- repair budget semantics equivalence;
- no weaker final assembly readiness;
- ToolTrace safe scalar assertions;
- no provider/network/live command.

Still not authorized:

- Agent runtime implementation;
- live evidence;
- provider/runtime/default changes;
- score-loop, multi-year runtime, golden/readiness or quality gate changes;
- external PR/push/release actions.
