# MVP internalized Agent engine implementation planning plan review (MiMo)

## Worker Self-Check

- Role: AgentMiMo plan review worker only; not controller, not implementation.
- Gate: `MVP internalized Agent engine implementation planning gate`.
- Classification: heavy.
- CWD: /Users/maomao/fund-agent
- Output artifact: this file.
- Required reads completed: `AGENTS.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/design.md`, `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`, `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-controller-judgment-20260603.md`, `fund_agent/services/chapter_orchestrator.py`, `fund_agent/services/execution_contract.py`, `fund_agent/services/final_chapter_assembler.py`, `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py`, `fund_agent/fund/evidence_availability.py`, `fund_agent/host/runtime.py`.
- Actions intentionally not taken: no source code, test, config, or doc edits; no live provider probe; no runtime/provider command.

## Findings

### F1. `ChapterOrchestrationResult` adapter shape gap (Medium, non-blocking)

**Evidence**: `chapter_orchestrator.py:511-537` defines `ChapterOrchestrationResult` with fields `projection`, `blocked_reasons`, `generated_chapter_ids`, `skipped_chapter_ids` that have no direct equivalent in the proposed `AgentRunResult`. `final_chapter_assembler.py:580` consumes `orchestration_result.chapter_results` via `_chapter_result_map()` but does not consume `projection` directly.

**Why non-blocking**: The plan acknowledges this in Risks: "existing artifact retention and final assembler consume this Service shape. The Service adapter must either produce an equivalent shape or update serializers and tests in the same slice." The adapter can synthesize `projection` from the input, `blocked_reasons` from `AgentRunResult` terminal state, `generated_chapter_ids` from task results, and `skipped_chapter_ids` from missing tasks. The `FinalChapterAssembler` only consumes `chapter_results` and `fund_code`/`report_year` from the orchestration result; other fields are diagnostic.

**Why it matters**: If the adapter does not produce a compatible shape, `FinalChapterAssembler` and `llm_run_artifacts.py` will break. This must be resolved before Slice 5 implementation starts.

### F2. `ChapterRunResult.attempts` diagnostic mapping (Medium, non-blocking)

**Evidence**: `chapter_orchestrator.py:478-508` defines `ChapterRunResult` with `attempts: tuple[ChapterAttemptRecord, ...]` where each `ChapterAttemptRecord` (line 459-475) contains `ChapterLLMRuntimeDiagnostic` with 30+ typed fields including `provider_runtime_category`, `elapsed_ms`, `timeout_seconds`, `approx_prompt_tokens`.

**Why non-blocking**: The plan's Slice 7 says "extend Service artifact serialization to include safe `ToolTrace` summary only." The mapping from `ChapterAttemptRecord.runtime_diagnostics` to `ToolTrace` entries must be lossless for safe scalar fields. The plan does not define this mapping explicitly.

**Why it matters**: Current artifact retention in `llm_run_artifacts.py` serializes `ChapterRunResult.attempts` directly. If Agent `ToolTrace` does not preserve the same safe scalar fields, the retained artifact format will change. The plan should note that `ToolTrace` must be a superset of currently serialized safe diagnostic fields.

### F3. `AgentRunControl` Protocol shape underspecified (Low, non-blocking)

**Evidence**: Plan section "Implementation Decisions" says "Define an Agent-side `AgentRunControl` Protocol with `raise_if_cancelled_or_deadline_exceeded()` and safe phase event methods; Service can adapt `HostRunContext` to that Protocol." Current `HostRunContext` at `runtime.py:215-280` exposes `raise_if_cancelled_or_deadline_exceeded()`, `record_phase_started()`, `record_phase_completed()`, `record_diagnostic()`, `deadline_exceeded()`, `cancel_if_deadline_exceeded()`.

**Why non-blocking**: The Protocol should mirror `HostRunContext` methods that Agent actually calls. The plan's Slice 1 creates contracts; the exact Protocol can be defined there. The adaptation is straightforward since `HostRunContext` already has the right shape.

**Why it matters**: If the Protocol is too narrow, Agent will need to import `HostRunContext` directly, violating the boundary. If too wide, it leaks Host internals.

### F4. `RepairSemantics` ownership decision deferred (Low, non-blocking)

**Evidence**: Plan Slice 3 says "Add or expose Fund `RepairSemantics` if current `ChapterAuditRepairHint` is insufficient as a stable typed domain contract." Current `ChapterAuditRepairHint` at `chapter_auditor.py:47` is `Literal["none", "patch", "regenerate", "needs_more_facts"]`.

**Why non-blocking**: The existing 4-value enum is coarse but stable. Agent `RepairPolicy` can consume it directly for the first MVP. A richer `RepairSemantics` module can be added later if issue-to-repair mapping needs more granularity.

**Why it matters**: If implementation workers start Slice 3 without deciding whether to create `fund_agent/fund/repair_semantics.py`, they may either over-engineer (new module for 4 values) or under-engineer (hardcode mapping in Agent).

### F5. ToolRegistry call/result envelope deferred to Slice 2 (Low, non-blocking)

**Evidence**: Plan Risks section: "ToolRegistry schema, call/result envelopes, versioning, and dependency injection shape must be defined before Fund tool wrapping." Slice 2 says "Add typed tool call/result envelope with explicit fields" but does not define the envelope shape.

**Why non-blocking**: This is correctly sequenced — Slice 2 defines the envelope before Slice 3 wraps Fund tools. The design artifact provides enough context (tool ids, allowed inputs/outputs per tool) for Slice 2 to define the envelope.

**Why it matters**: If the envelope is too generic (e.g., `dict[str, Any]`), type safety is lost. If too rigid, it cannot accommodate all 5 tool types.

### F6. Legacy `typed_template_path` maintenance burden (Low, non-blocking)

**Evidence**: Plan Implementation Decisions: "first MVP applies only to `typed_template_path="typed_template_contract"` for `--use-llm`; legacy Service orchestrator path can remain until a later cleanup." Slice 8: "Remove or deprecate Service-owned `_run_single_chapter`, `_decide_repair`, attempt loop and Agent-owned trace logic from `chapter_orchestrator.py` for typed path."

**Why non-blocking**: The side-by-side migration approach is correct. The legacy path (`legacy_contract`) remains functional for backward compatibility. The plan correctly defers legacy cleanup.

**Why it matters**: The `chapter_orchestrator.py` file is already ~1000+ lines. Keeping both paths increases complexity. The plan should note that legacy path removal is a follow-up gate, not part of this gate.

### F7. Test scenario enumeration gap (Low, non-blocking)

**Evidence**: Each slice lists validation commands (e.g., `uv run pytest tests/agent/test_agent_contracts.py`) but does not enumerate specific test scenarios. For a heavy gate, the plan should list critical test scenarios per slice.

**Why non-blocking**: The validation commands reference test files that will be created during implementation. The plan correctly defers test design to implementation workers.

**Why it matters**: Without explicit test scenarios, implementation workers may miss edge cases like: Agent cancellation mid-tool-call, ToolTrace serializer rejecting prompt text, RepairPolicy budget exhaustion, etc.

## Boundary Compliance

### UI -> Service -> Host -> Agent

| Layer | Plan ownership | Boundary check |
|---|---|---|
| Service | use case, ExecutionContract, provider construction, runtime ceilings, quality policy, final product mapping | ✓ Correct; Service constructs `AgentReportRunInput` and maps `AgentRunResult` back |
| Host | lifecycle-only: global deadline, cancel, terminal state, safe diagnostics | ✓ Correct; Host does not inspect fund business; Agent uses `AgentRunControl` Protocol |
| Agent | runner, task graph, tool loop, ToolRegistry, ToolTrace, RepairPolicy, FinalAssemblyReadiness | ✓ Correct; Agent does not import Service types |
| Fund | domain tools, typed contracts, EvidenceAvailability, writer, audit, RepairSemantics | ✓ Correct; Fund tools consume explicit typed inputs only |

### Provider clients / EvidenceAvailability / extra_payload

| Prohibition | Status |
|---|---|
| Provider clients not in ToolRegistry | ✓ "Provider clients are excluded from registry" |
| EvidenceAvailability not a tool | ✓ "precomputed derived input from same-source `ChapterFactProjection`" |
| No extra_payload/kwargs bags | ✓ "Tools receive explicit typed parameters only; no `extra_payload`" |

### Fail-closed semantics

| Requirement | Status |
|---|---|
| Empty stdout on incomplete | ✓ "Preserve empty stdout and exit code `1`" |
| No deterministic fallback | ✓ `QualityFailClosedPolicy.deterministic_fallback_allowed=False` preserved |
| Artifacts safe | ✓ "no prompt/draft/raw provider/audit response/API key/header is serialized" |
| Current provider defaults unchanged | ✓ Non-goal: "Do not change provider budgets, timeout defaults" |

### Prohibited actions

| Prohibition | Status |
|---|---|
| No live provider probe | ✓ Explicitly forbidden in validation commands |
| No provider budget/default changes | ✓ Non-goal and stop condition |
| No score-loop | ✓ Non-goal |
| No template truth replacement | ✓ Non-goal: "keep `docs/fund-analysis-template-draft.md`, `contracts.py`, public chapter ids `0-7`" |
| No dayu runtime dependency | ✓ Non-goal and stop condition |
| No Ch3 calibration | ✓ Non-goal |

## Slice Sequencing Assessment

```text
Slice 0: Preflight/baseline ──────────────────────────────────────── ✓ no code change
Slice 1: Agent contracts + README ─────────────────────────────────── ✓ no Fund/Service dep
Slice 2: ToolRegistry + ToolTrace ─────────────────────────────────── ✓ fake tools only
Slice 3: Fund tool adapters ───────────────────────────────────────── ✓ depends on 1-2
Slice 4: Sequential body chapter runner ───────────────────────────── ✓ depends on 3
Slice 5: Service adapter side-by-side ─────────────────────────────── ✓ depends on 4
Slice 6: Agent FinalAssemblyReadiness ─────────────────────────────── ✓ depends on 4
Slice 7: Diagnostics/artifact mapping ─────────────────────────────── ✓ depends on 2, 5
Slice 8: Boundary cleanup + docs ──────────────────────────────────── ✓ depends on 5-7
```

Sequencing is minimal and correct. Slices 5 and 6 could theoretically run in parallel (both depend on Slice 4 only), but sequential is safer for first MVP as the plan states.

## Validation Commands (read-only checks performed)

```bash
# Confirm branch
git branch --show-current
# → feat/mvp-llm-incomplete-run-artifacts

# Confirm fund_agent/agent/ does not exist
test -d fund_agent/agent && echo "EXISTS" || echo "ABSENT"
# → ABSENT (correct; Slice 0 will record this)

# Confirm Host runtime does not import Service/Fund
grep -c "from fund_agent.services\|from fund_agent.fund" fund_agent/host/runtime.py
# → 0 (correct)

# Confirm EvidenceAvailability is not registered as a tool anywhere
grep -c "ToolRegistry\|register_tool" fund_agent/fund/evidence_availability.py
# → 0 (correct)

# Confirm chapter_writer.py does not import Service/Host/dayu
grep -c "from fund_agent.services\|from fund_agent.host\|dayu" fund_agent/fund/chapter_writer.py
# → 0 (correct)

# Confirm chapter_auditor.py does not import Service/Host/dayu
grep -c "from fund_agent.services\|from fund_agent.host\|dayu" fund_agent/fund/chapter_auditor.py
# → 0 (correct)
```

All boundary checks pass.

## Residual Risks for Implementation

| Risk | Severity | Owner |
|---|---|---|
| `ChapterOrchestrationResult` adapter shape must be defined before Slice 5 | Medium | Slice 5 implementation worker |
| `ToolTrace` must be superset of current `ChapterLLMRuntimeDiagnostic` safe fields | Medium | Slice 2 + Slice 7 implementation worker |
| `AgentRunControl` Protocol exact methods should be enumerated in Slice 1 | Low | Slice 1 implementation worker |
| `RepairSemantics` decision (new module vs reuse `ChapterAuditRepairHint`) before Slice 3 | Low | Slice 3 implementation worker |
| ToolRegistry call/result envelope type safety in Slice 2 | Low | Slice 2 implementation worker |
| Legacy `legacy_contract` path cleanup is a separate follow-up gate | Low | Future gate controller |
| Test scenarios per slice should be enumerated before or during implementation | Low | Each slice implementation worker |

## Verdict

**PASS-WITH-RISKS**

The plan is code-generation-ready. All six review dimensions pass:

1. **Code-generation-ready**: Contracts, schemas, state machine, files, slices, tests, docs, and stop conditions are sufficient for implementation workers to execute Slices 0-4 directly. Slices 5-8 have adapter shape gaps (F1, F2) that should be resolved during Slice 5 design but do not block plan acceptance.

2. **Boundary compliance**: UI → Service → Host → Agent boundaries are correctly preserved. Service keeps use case/ExecutionContract/provider construction/runtime ceilings/final product mapping. Host stays lifecycle-only. Agent owns runner/tool-loop/task graph/ToolRegistry/ToolTrace/RepairPolicy/FinalAssemblyReadiness. Fund owns domain tools/typed contracts/EvidenceAvailability/writer/audit/RepairSemantics.

3. **Prohibition compliance**: Provider clients are not ToolRegistry tools. EvidenceAvailability is not a tool. No extra_payload/kwargs/free dict business bags.

4. **Fail-closed semantics preserved**: Empty stdout on incomplete, no deterministic fallback, artifacts safe, current provider defaults unchanged.

5. **No prohibited actions**: No live provider probe, no provider default/runtime/budget changes, no score-loop, no multi-year runtime, no template truth replacement, no dayu runtime dependency.

6. **Slice sequencing correct**: Slices are ordered to minimize dependencies: contracts/trace first, then Fund adapters/runner, then Service side-by-side migration, then diagnostics/docs cleanup. First MVP is sequential as required.

The medium-severity adapter shape findings (F1, F2) are non-blocking for plan acceptance but must be tracked as implementation residuals. The plan's stop conditions already cover the case where adapter shape becomes intractable.
