# MVP Agent Engine Design Slice E Implementation Planning Gate — Targeted Re-Review (AgentDS)

## 1. Review Metadata

| Field | Value |
|---|---|
| Reviewer | AgentDS |
| Target revised plan | `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md` |
| Prior DS review | `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-ds-20260608.md` |
| Prior Codex review | `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-codex-20260608.md` |
| Re-review artifact | `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-rereview-ds-20260608.md` |
| Date | 2026-06-08 |
| Scope | targeted re-review only — verify absorption of prior DS NBOs and Codex blocking findings; no new full-scope review |

## 2. Verdict

**`PASS`**

The revised plan absorbs all seven DS non-blocking observations and both Codex blocking findings. No residual blocking issues remain. Implementation may be authorized by controller judgment under the constraints recorded in §7.

## 3. DS NBO Absorption Verification

### F1: `blocked_tool_contract` disposition — RESOLVED

Plan §5 now includes explicit disposition:

> `blocked_tool_contract` disposition: it is removed from the first Agent terminal set. The first implementation wraps existing Fund primitives and introduces no new tool-contract terminal beyond current stop reasons. A future gate may add `blocked_tool_contract` only after it defines concrete trigger conditions and equivalence tests.

This satisfies Slice C DS NBO-2.

### F2: Residual owners — RESOLVED

Plan §7 "Residual Owners" table enumerates four residuals with owners and dispositions: typed patch repair API, provider timeout retry attempt visibility, prompt-contract subcategory terminal naming, and `blocked_tool_contract` terminal.

This satisfies Slice D §5.

### F3: Prompt char/token derivation rule — RESOLVED

Plan E2 now includes:

> prompt char counts and approximate token counts must be derived from in-memory prompt length heuristics only; they must not require retained prompt text, external token-count service calls or network access.

This satisfies Slice B DS NBO-1.

### F4: Pre-migration Service baseline — RESOLVED

Plan E4 now requires:

> before changing Service bridge behavior, implementation evidence must record the pre-migration local Service baseline command output for the relevant no-live tests.

### F5: Validation matrix test-file mapping — RESOLVED

Plan §6 table now includes an "Expected test file" column mapping each of the 13 validation rows to specific test files.

### F6: E4 allowed-file narrowing — RESOLVED

Plan E4 now constrains:

> `fund_agent/services/fund_analysis_service.py` edits are limited to `analyze_with_llm_execution()` or a new bridge call path; deterministic `analyze()` and existing `analyze_with_llm()` behavior must remain unchanged unless implementation evidence explicitly proves the change is equivalent.

### F7: Partial-acceptance mechanism — RESOLVED

Plan §9 now includes a "Partial acceptance rule":

> implementation must proceed sequentially through E1-E4; if E4 Service bridge equivalence fails, implementation worker must stop before staging or committing implementation work and return to controller; accepting E1-E3 without E4 requires a separate controller judgment that explicitly reclassifies the partial Agent package as non-production code.

## 4. Codex Blocking Findings Fix Verification

### Codex F1 (HIGH): E5 role/file authorization boundary — FIXED

Three changes resolve this:

1. **E5 allowed files narrowed**: removed `docs/reviews/*-code-review-*.md`, `docs/reviews/*-controller-judgment-*.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`. Now only: `docs/reviews/mvp-agent-engine-design-slice-e-implementation-evidence-20260608.md`, `fund_agent/agent/README.md`, `fund_agent/README.md`, `tests/README.md`.

2. **E5 implementation requirements add**: "implementation worker must not write code-review artifacts, controller judgment artifacts, `docs/current-startup-packet.md` or `docs/implementation-control.md`; those are reviewer/controller responsibilities after implementation evidence and code review."

3. **§9 controller decision option scoped**: "implementation may proceed exactly through E1-E4 plus implementation evidence and triggered README updates from E5 with no live/provider/network commands; implementation must stop before code review, controller judgment or control-doc sync."

4. **E5 post-implementation lifecycle** explicitly separates: implementation worker → implementation evidence only; independent reviewer → code review artifact; controller → controller judgment; only controller/control-sync worker → control docs.

### Codex F2 (MEDIUM): Host cancel/deadline normalized scheduler contract — FIXED

Five changes resolve this:

1. **E1 contracts**: defines `AgentSchedulerInterruption` dataclass with explicit fields `status`, `reason`, `phase`, `chapter_id`, `attempt_index`; accepted `status` values: `none`, `cancelled`, `deadline_exceeded`.

2. **E3 runner check points**: "Agent runner checks scheduler interruption before the first chapter, between writer and auditor, after tool-call return and before repair decision."

3. **E3 interrupt behavior**: "cancelled or deadline-exceeded interruption fails closed, cannot produce complete report markdown and does not consume content repair budget."

4. **E4 Service bridge**: "Service bridge owns translation from current `HostRunContext` checks into `AgentSchedulerInterruption`; Agent contracts, runner, repair policy and tools must not import `fund_agent.host`."

5. **§6 validation matrix**: two dedicated rows — "cancel before first chapter" (mapped to `tests/agent/test_runner.py`, `tests/agent/test_service_bridge.py`) and "deadline between writer and auditor" (mapped to `tests/agent/test_runner.py`, `tests/agent/test_repair_policy.py`), plus "Agent package Host isolation" import-boundary test.

## 5. No New Findings

The revised plan introduces no new violations, overbroad authorizations, boundary weakenings, or contract gaps. All changes are additive clarifications within the existing structure.

## 6. Validation

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-rereview-ds-20260608.md
```

No source tests were run — this is a plan re-review only. No live provider, endpoint, network, PR, push, commit, source edit, test edit or control-doc edit actions were performed.

## 7. Implementation Authorization Scope

If controller accepts this re-review, implementation is authorized for:

- Creating and populating `fund_agent/agent/` per E1-E3 allowed files
- Modifying `fund_agent/services/` per E4 allowed files and narrowed method constraints
- Creating test files per E1-E4 allowed files
- Writing implementation evidence and triggered README updates per E5
- Running local-only validation commands per E1-E5

Implementation remains forbidden for all actions in plan §3, and must stop before code review, controller judgment, or control-doc sync per plan E5 and §9.

The implementation worker must not proceed to code review, controller judgment, PR, push, merge, or any live/provider/network action without a separate explicit controller authorization.
