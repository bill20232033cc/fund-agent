# MVP LLM Tool Calling And State Machine Calibration Spike Controller Judgment

## 1. Verdict

`SPIKE_ACCEPTED_WITH_DS_ONLY_REVIEW`

The non-live learning/evidence spike is accepted for use as input to the next design/plan gate.

Accepted spike artifact:

- `docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-20260607.md`

Accepted review artifact:

- `docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-review-ds-20260607.md`

Superseded preliminary judgment:

- `docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-controller-preliminary-judgment-20260607.md`

## 2. Reviewer Availability And Authorization

AgentDS completed the review with verdict `PASS` and zero blocking findings.

AgentMiMo was retried after a clean `/clear`; the pane again entered API retry state and did not produce a durable review artifact before operator instruction. The operator then authorized DS-only review for tonight and instructed not to continue sending work to MiMo.

Controller accepts the DS-only review risk for this spike because:

- the spike is non-live, docs/reviews-only and does not change runtime behavior;
- DS review directly checked state ownership, future/current runtime separation, ToolRegistry wrapping, fail-closed invariants, Dayu boundary and next-gate readiness;
- MiMo unavailability is caused by network/API certificate failure, not by a spike content blocker;
- no Agent runtime implementation is authorized by this judgment.

## 3. DS Review Findings Disposition

### NBO-1: EvidenceAvailability Production Ambiguity

Disposition: `accepted_followup_input`

The next `Agent Engine Design Refresh Gate` plan must decide whether `EvidenceAvailability` is computed inside Agent task setup from same-source `ChapterFactProjection` or passed as explicit Service-prepared task input. It must not be fetched from retained artifacts, files or external state.

### NBO-2: Service ProviderRuntimeBudget vs Agent Repair Budget Interaction

Disposition: `accepted_followup_input`

The next plan must keep Service-owned provider runtime ceilings separate from Agent-owned repair attempt policy. Provider timeout/max-attempt fields are not Agent business state and must remain explicit typed inputs.

### NBO-3: Tool Table Omits `repair_hint` Semantics

Disposition: `accepted_followup_input`

The next plan must explicitly model how Fund audit `repair_hint` and issue ids feed Agent `RepairPolicy.decide` without moving Fund issue-to-repair semantics into Service or Host.

## 4. Accepted Facts

- The current write-audit-repair loop is best understood as a bounded task graph/state machine, not an open-ended autonomous agent.
- Current Service-owned `ChapterOrchestrator` remains current code fact until a later implementation gate migrates execution mechanics.
- Future Agent should own chapter task graph, attempt ledger, repair policy execution, ToolRegistry calls, ToolTrace and final body readiness matrix.
- Service should retain use case, ExecutionContract, provider construction, quality policy and final product fail-closed mapping.
- Host remains lifecycle-only.
- Fund primitives should be wrapped as typed tools; Fund logic should not be rewritten in Agent.
- Provider writer/auditor clients are explicit per-run typed inputs, not ToolRegistry tools.
- Dayu remains reference-only; no `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime is authorized.

## 5. Boundary Judgment

No live LLM command, provider retry, endpoint probe, curl, DNS, socket probe, runtime/default/budget change, source/test/config implementation, Host/Agent runtime implementation, multi-year runtime, score-loop, golden/readiness, PR, push, merge or external state action was performed or authorized.

## 6. Next Entry Point

Open `Agent Engine Design Refresh Gate` as design/plan only.

Required next artifact:

- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md`

Required review route for tonight:

- DS-only review is authorized by operator instruction due MiMo network/API failure.

Stop before implementation. No Agent runtime code, ToolRegistry code, schema, provider, config, quality gate, golden/readiness, PR or external state action is authorized.
