# MVP internalized Agent engine/tool-loop contract execution design review fix evidence

## Worker Self-Check

- Role: scoped design-fix specialist only, not controller.
- Gate: `MVP internalized Agent engine/tool-loop contract execution design gate`.
- Classification: heavy.
- Scope: design/review artifact fix only.
- Files changed: `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`; this fix evidence artifact.
- Actions intentionally not taken: no implementation, no source/test/runtime/config/provider/auditor/score-loop/report artifact edit, no truth-doc edit, no commit, no push, no PR.

## Reviewer Findings Addressed

| Finding | Disposition |
|---|---|
| Ch3 evidence-to-diagnosis mismatch | Fixed. Ch3 retained evidence is now described as `programmatic:C2` / `code_bug_other` under `prompt_contract` with `repair_budget_exhausted`; the artifact no longer states that `must_not_cover` / `言行一致` is proven root cause. |
| EvidenceAvailability registered as a ToolRegistry tool | Fixed. `fund.evidence_availability_projection` was removed from the registry table; `EvidenceAvailability` is a precomputed derived input from `ChapterFactProjection` before the loop. |
| Provider client injection unclear | Fixed. First Agent MVP now uses explicit per-run typed writer/auditor Protocol clients constructed by Service and passed by Agent into Fund tools as typed inputs; not a tool and not `extra_payload`. |
| Repair ownership ambiguity | Fixed. Fund owns `RepairSemantics`; Agent owns `RepairPolicy`, attempt counting, budget enforcement, and stop/retry decisions. |
| Cancellation/deadline observation unclear | Fixed. Agent checks Host cancel token/deadline at task scheduling boundaries and after tool-call return; mid-tool-call interruption relies on provider client timeout. |
| Service `ChapterOrchestrator` / `FinalChapterAssembler` migration relationship unclear | Fixed. Agent task graph subsumes current chapter 1-6 orchestrator behavior in a future gate; Agent readiness may feed or replace Service readiness only in a future implementation gate while preserving stdout/fail-closed behavior. |
| Missing `PLAN_REPAIR -> STOP_FAIL_CLOSED` transition | Fixed. State machine now shows stop transition for exhausted budget or planner stop after programmatic and semantic audit failures. |
| Mixed failure terminal states over-designed | Fixed. First MVP run terminal states are simplified to `accepted`, `partial_fail_closed`, and `host_interrupted`; detailed classifications remain per-chapter/per-attempt in `ToolTrace`. |
| Residual planning notes missing | Fixed. Added residual notes for Ch2 sub-requirement ids, Evidence Confirm future phase, ToolRegistry wiring/schema in Slice A, and trace serializer allowlist tests. |
| ToolRegistry phasing unclear | Fixed. Added phasing note: schema contracts in Slice A, fake-tool execution in Slice B, Fund wrapping in Slice C, migration in Slice D, readiness integration in Slice E. |

## Explicit Non-Changes

- No code changed.
- No `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, README, template, `contracts.py`, auditor, provider, score-loop, or retained report artifact changed.
- No runtime behavior, provider budget, score-loop behavior, stdout/fail-closed behavior, deterministic fallback behavior, or Ch3 calibration implementation changed.
- This artifact does not authorize implementation.

## Validation

- Command: `python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json >/dev/null`
- Result: pass.
- Command: `git diff --check -- docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-fix-evidence-20260603.md`
- Result: pass.

## Secret Safety

No API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, or raw PDF/source text was added. The fix only references safe artifact paths, enum labels, issue ids, counts, and high-level diagnostic categories.
