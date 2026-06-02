# MVP internalized Agent engine/tool-loop contract execution design controller judgment

## Controller Self-Check

- Role: phaseflow controller.
- Gate: `MVP internalized Agent engine/tool-loop contract execution design gate`.
- Classification: heavy.
- Scope: design/review only; no implementation authorized.
- Inputs reviewed: design artifact, DS/MiMo reviews, design-fix evidence, DS/MiMo re-reviews, `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, and retained `006597 / 2024` `summary.json`.
- Actions intentionally not taken: no source/test/config/runtime/provider/auditor/template/score-loop/golden/readiness edit, no Ch3 calibration implementation, no provider budget change, no PR/push.

## Judgment

**Accepted as design-only future architecture.** The gate has plan/design, independent review, fix, independent re-review, and controller judgment. It does not change current runtime behavior.

Accepted future design:

- Agent owns `AgentReportRun`, `ChapterTask`, task graph scheduling, tool loop, attempt ledger, repair/budget spending, `ToolRegistry`, `ToolTrace`, and `FinalAssemblyReadiness`.
- Service keeps use case, report strategy, `ExecutionContract`, quality policy, provider construction for first Agent MVP, runtime ceilings, and final product fail-closed mapping.
- Host remains lifecycle-only: global deadline, cancel token, terminal state, safe diagnostics/events. Agent observes Host cancel/deadline at scheduling boundaries and after tool-call return; mid-tool-call interruption relies on provider client timeout.
- Fund owns domain tools and semantics: `ChapterContract`, `ChapterFactProjection`, derived `EvidenceAvailability`, writer, programmatic audit, bounded semantic audit adapter, and `RepairSemantics`.
- `EvidenceAvailability` is a precomputed derived input from same-source `ChapterFactProjection`, not a ToolRegistry tool.
- Provider writer/auditor clients are Service-constructed explicit per-run typed fields passed by Agent into Fund tools; they are not tools, pseudo-tools, or `extra_payload`.
- Repair ownership is split: Fund provides issue-to-repair semantics; Agent enforces `RepairPolicy`, attempt counting, ceilings, and stop/retry decisions.
- The Agent task graph subsumes current Service `ChapterOrchestrator` behavior for chapters 1-6 in a future implementation gate, preserving independent chapter execution and fail-closed aggregation.
- Agent `FinalAssemblyReadiness` may feed or replace current Service `FinalChapterAssembler` readiness only in a future implementation gate; current stdout/fail-closed behavior remains unchanged.
- First MVP run terminal states are intentionally simple: `accepted`, `partial_fail_closed`, `host_interrupted`; detailed runtime/content/dependency classifications stay per-chapter/per-attempt in `ToolTrace`.
- Programmatic audit remains authoritative. Bounded semantic audit cannot override programmatic blockers and runs after programmatic pass in first Agent MVP.

Deferred / rejected for this gate:

- No Agent runner/tool-loop implementation.
- No typed template/runtime contract implementation.
- No `docs/fund-analysis-template-draft.md`, `contracts.py`, renderer, auditor, provider, score-loop, golden/readiness, deterministic `analyze/checklist`, or retained artifact mutation.
- No provider runtime budget tuning.
- No Ch3 calibration implementation. Retained Ch3 evidence is `programmatic:C2` / `code_bug_other` under `prompt_contract` with `repair_budget_exhausted`; it does not prove `must_not_cover` / `言行一致` root cause.
- No multi-year annual evidence implementation.
- No `chapter_generation_score` wiring.
- No Ch2 public split, `0+9`, or `0+10` chapter structure.
- No `dayu-agent`, `dayu.host`, or `dayu.engine` production runtime dependency.

## Review Disposition

DS first review: pass-with-risks, 4 non-blocking findings. All material findings were fixed or routed.

MiMo first review: pass-with-risks, 12 findings. The Ch3 same-source evidence mismatch was accepted as material and fixed before judgment; all other material ambiguity findings were fixed or explicitly deferred.

DS re-review: PASS, no blocking findings. DS verified all fix claims and accepted remaining minor residuals.

MiMo re-review: PASS, no blocking findings. MiMo verified no new blocker, no scope leak, no implementation/provider budget/score-loop/Ch3 calibration leakage.

Accepted non-blocking residuals for future implementation planning:

- ToolTrace serializer safety needs allowlist tests and secret scan.
- ToolRegistry schema, call/result envelopes, versioning, and dependency injection shape must be defined before Fund tool wrapping.
- Body chapter scheduling model must be explicit before implementation; sequential first MVP is acceptable unless a later async gate accepts concurrency.
- `audit_focus` needs typed enforcement so it cannot disable programmatic blockers.
- Ch2 internal sub-requirement ids must remain inside public chapter id `2`.
- Evidence Confirm remains a future phase.
- Blocking provider calls rely on provider timeout for mid-call interruption; cancellation propagation beyond that belongs to implementation/runtime planning.

## Acceptance Evidence

| Purpose | Artifact |
|---|---|
| Design artifact | `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md` |
| DS review | `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-ds-20260603.md` |
| MiMo review | `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-mimo-20260603.md` |
| Fix evidence | `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-fix-evidence-20260603.md` |
| DS re-review | `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-rereview-ds-20260603.md` |
| MiMo re-review | `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-rereview-mimo-20260603.md` |

## Next Entry Point

Per phase sequencing, the next design-only gate is `MVP multi-year annual evidence scope design gate`.

Scope guard for that next gate:

- Design five-year annual report evidence scope only.
- Do not feed five years of raw PDF text directly to LLM.
- Evidence must flow through `FundDocumentRepository` and typed evidence bundles.
- Quarterly reports remain a separate gate.
- Do not implement Agent/tool-loop, provider runtime budgets, or score-loop in that gate.

## Validation

- `python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json >/dev/null` — pass.
- DS/MiMo re-reviews — pass with no blocking findings.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, or raw PDF/source text.
