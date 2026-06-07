# MVP Agent Engine Design Slice E Implementation Evidence

## Scope

Implemented no-live Slice E within the accepted controller scope:

- E1 Agent contracts package in `fund_agent/agent/contracts.py`.
- E2 Fund tool adapters and safe ToolTrace in `fund_agent/agent/tools.py`.
- E3 Agent repair policy and body runner in `fund_agent/agent/repair.py` and
  `fund_agent/agent/runner.py`.
- E4 Service bridge migration in `fund_agent/services/agent_bridge.py` and
  `fund_agent/services/chapter_orchestrator.py`.
- Triggered README updates in `fund_agent/agent/README.md`,
  `fund_agent/README.md` and `tests/README.md`.

No live LLM command, provider readiness check, endpoint probe, curl, DNS,
socket probe, runtime/default/budget/config change, golden/readiness change,
PR/push/release action, control-doc update, controller judgment artifact or code
review artifact was performed by this implementation worker.

## Implementation Summary

- `ChapterOrchestrator` now resolves/validates Service input, then delegates
  body chapter execution to `run_agent_chapter_orchestration_bridge()`.
- Service remains owner of use-case semantics, provider construction,
  `FundLLMExecutionRequest`, typed `EvidenceAvailability` derivation, Host
  context translation, Service diagnostics and final assembly.
- Agent runner executes template body chapters `1-6` from the same
  `ChapterFactProjection`, records attempts and ToolTrace, and returns
  `FinalAssemblyReadiness`.
- Agent tool adapters wrap only existing Fund primitives:
  `project_chapter_facts()`, `write_chapter()`,
  `audit_chapter_programmatic()` and `audit_chapter_llm()`.
- `derive_evidence_availability()` remains run-level same-source
  precomputation, not a registry tool.
- ToolTrace serialization is allowlist-only and excludes prompt text, draft
  markdown, fact values, unsafe anchor prose, raw provider/audit responses,
  provider request/body, API key, Authorization header, bearer token, model
  value, base URL, arbitrary headers and provider config.
- Host cancel/deadline enters Agent only as `AgentSchedulerInterruption` from
  the Service bridge; `fund_agent/agent` does not import `fund_agent.host` or
  `fund_agent.services`.
- Service bridge projects Agent results back into existing
  `ChapterOrchestrationResult`, including accepted conclusions, Service
  prompt/runtime diagnostics and Host phase events.
- Service bridge now replays regenerate repair decisions as explicit Host
  `phase="repair"` started/completed events, preserving the old phase timeline
  signal without making Agent import Host.
- `chapter_orchestrator.py` no longer retains the old direct single-chapter
  execution path; the remaining helper functions are Service projection,
  diagnostics, prompt-contract and artifact utilities still used by bridge or
  tests.

## Pre-Migration Baseline

Before switching `ChapterOrchestrator` default execution to Agent bridge, local
baseline checks passed:

```text
uv run pytest tests/services/test_chapter_orchestrator.py
78 passed in 0.58s
```

```text
uv run pytest tests/services/test_llm_run_artifacts.py
7 passed in 0.49s
```

During the first bridge activation attempt, `tests/services/test_chapter_orchestrator.py`
failed with 31 mismatches. The activation was reverted, the bridge was extended
to project Service diagnostics and exact stop/category semantics, then
reactivated. A second activation attempt reduced the gap to 15 mismatches; a
third reduced it to 2; the final activation passed the full orchestrator suite.

## Validation

Final validation after README/evidence updates:

```text
git diff --check
PASS
```

```text
uv run pytest tests/agent tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/services/test_llm_run_artifacts.py
163 passed in 1.07s
```

```text
uv run ruff check fund_agent/agent fund_agent/services tests/agent tests/services
PASS
```

Additional focused validation observed during implementation:

```text
uv run pytest tests/agent
39 passed in 0.54s
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py
78 passed in 0.59s
```

Post-review P1 closure validation:

```text
uv run pytest tests/agent/test_service_bridge.py tests/services/test_chapter_orchestrator.py
82 passed in 0.60s
```

```text
uv run ruff check fund_agent/services/agent_bridge.py fund_agent/services/chapter_orchestrator.py tests/agent/test_service_bridge.py
PASS
```

## Review Follow-up

AgentDS review artifact:
`docs/reviews/mvp-agent-engine-design-slice-e-implementation-code-review-ds-20260608.md`.

- DS P1 repair phase Host event loss: fixed in
  `fund_agent/services/agent_bridge.py`; covered by
  `test_service_bridge_records_repair_phase_events`.
- DS P1 old orchestrator dead code: fixed by deleting the direct
  `_run_single_chapter()` path and its private Host phase/exception wrapper
  helpers from `fund_agent/services/chapter_orchestrator.py`.
- DS P0 `pyproject.toml` unrelated `claude-mimo` entry point: not modified by
  this implementation worker and observed as pre-existing workspace dirty
  state before Slice E edits. After owner disposition, the unrelated
  `claude-mimo` entry point was removed from `pyproject.toml`; it is not part
  of the Slice E accepted file set.

AgentCodex review artifact:
`docs/reviews/mvp-agent-engine-design-slice-e-implementation-code-review-codex-20260608.md`.

- Verdict: `PASS_WITH_RESIDUALS`; no Slice E P0/P1 implementation code defect.
- Codex P2 module docstring drift: fixed by updating
  `fund_agent/services/chapter_orchestrator.py` to describe the current Service
  input / fail-closed / Agent bridge delegation boundary.
- Codex P2 evidence count drift: fixed by updating this evidence artifact to
  the post-P1 full matrix count (`163 passed`) and Agent test count
  (`39 passed`).

## Residuals

- typed patch repair API remains future work; current `patch` and `regenerate`
  both map to recorded whole-chapter regenerate.
- provider timeout retry attempt visibility remains owned by Service/provider
  clients; Agent observes final provider outcomes and Service-projected safe
  diagnostics.
- `blocked_tool_contract` remains intentionally absent from first Agent terminal
  set because no concrete trigger conditions exist in this implementation.
