# MVP internalized Agent engine implementation planning plan fix evidence

## Worker Self-Check

- Role: planning fix worker only; not controller, not implementation.
- Gate: `MVP internalized Agent engine implementation planning gate`.
- Classification: `heavy`.
- Scope: fix DS blocking findings in the plan artifact only.
- Allowed edits used:
  - `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md`
  - `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md`
- Prohibited actions preserved: no source code, tests, README, design, control, startup, runtime/provider command, live probe, commit, push or PR.

## Findings Fixed / Not Fixed

- DS B1 fixed: added a concrete Fund-owned `RepairSemantics` contract with module placement, slice placement, input fields, output fields, action enum, issue-level semantics, mapping source, precedence rules, relation to current `ChapterAuditRepairHint`, and the exact subset consumed by Agent `RepairPolicy`.
- DS B2 fixed: added the exact Agent-side `AgentRunControl` Protocol signature and the Service adapter location `fund_agent/services/agent_adapter.py`. The plan now states that Agent must not import concrete Host runtime and that the adapter must not expose Host internals such as `run_id`, `deadline_at`, `timeout_seconds` or `cancellation_token`.
- DS B3 fixed: added an explicit `AgentRunResult` to `ChapterOrchestrationResult` / `ChapterRunResult` mapping table covering terminal state, per-chapter status, attempts, repair decision projection, runtime diagnostics, ToolTrace relation, projection, fund code, report year, generated/skipped fields, chapter policy handling and additive diagnostics.
- Direct clarification fixed: renamed the Agent-side readiness type to `AgentFinalAssemblyReadiness` to avoid collision with the existing Service `FinalAssemblyReadiness`.
- Direct clarification fixed: stated `ToolTrace` must be a safe superset of the current `ChapterLLMRuntimeDiagnostic` scalar fields and remain projectable into existing artifact diagnostics.
- Not fixed: no MiMo-only non-blocking findings were fully expanded unless directly necessary for DS B1-B3 or naming/diagnostics clarification.

## Files Changed

- `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md`
- `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md`

## Validation Commands Run

```bash
sed -n '1,240p' AGENTS.md
sed -n '1,260p' docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md
sed -n '1,260p' docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-ds-20260603.md
sed -n '1,260p' docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-mimo-20260603.md
sed -n '430,560p' fund_agent/services/chapter_orchestrator.py
sed -n '1,220p' fund_agent/services/execution_contract.py
sed -n '140,340p' fund_agent/host/runtime.py
sed -n '1,120p' fund_agent/fund/chapter_auditor.py
sed -n '300,410p' fund_agent/fund/chapter_auditor.py
sed -n '2320,2560p' fund_agent/services/chapter_orchestrator.py
rg -n "RepairSemantics|AgentRunControl|ChapterOrchestrationResult|AgentFinalAssemblyReadiness|ToolTrace" docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md
git diff --check -- docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md
git diff -- docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md
git status --short -- docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md
```

Check outcomes:

- `git diff --check -- ...` passed with no whitespace errors.
- Required `rg -n "RepairSemantics|AgentRunControl|ChapterOrchestrationResult|AgentFinalAssemblyReadiness|ToolTrace" ...` returned matches for all required terms.
- `git status --short -- ...` shows only the two allowed review artifacts in this fix scope; both are currently untracked in this worktree.
- No runtime/provider/live probe command was run.

## Non-Goals Preserved

- No source code implementation.
- No tests changed or executed.
- No README, `docs/design.md`, `docs/implementation-control.md` or startup packet edits.
- No provider/default/runtime budget, endpoint, model or fallback changes.
- No `fund-analysis analyze --use-llm` live run or other provider probe.
- No score-loop, golden promotion, baseline promotion or multi-year runtime action.
- No `dayu-agent`, `dayu.host` or `dayu.engine` runtime dependency decision.
- No commit, push or PR.

## Residual Risks

- Implementation workers still need to prove the new Service adapter mapping with existing Service, artifact and CLI tests.
- `RepairSemantics` correction text must be migrated carefully from current Service repair helpers without introducing a second divergent mapping.
- ToolTrace serializer still needs implementation-time secret-safety tests to prove prompt, draft, raw responses and credentials cannot leak.
- `AgentFinalAssemblyReadiness` remains diagnostic/projection-only in the first MVP; replacing Service final assembly remains a separate gate.
