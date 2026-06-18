# MVP internalized Agent engine and typed audit contract design review fix evidence

## Controller / Fix Self-Check

- Gate / role: Gateflow-governed design review fix for `MVP internalized Agent engine and typed audit contract design gate`; no code implementation.
- Source review: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-review-20260602.md`.
- Fixed artifact: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-20260602.md`.
- Scope: docs/reviews only; no code, prompt, provider budget, score-loop, fail-closed behavior, truth-doc sync, commit, push or PR changes.
- Stop condition: request re-review before accepting design or syncing truth docs.

## Accepted Findings And Fix Status

### 01-已修复-[中]-Agent runner 与 provider client ownership 没有收敛，后续实现可能重新设计跨层边界

Controller decision: accepted.

Fix:

- Added `MVP boundary handoff`.
- Explicitly states provider construction remains Service-owned for the first Agent-engine MVP unless a later provider-factory migration gate changes it.
- Defines Service-declared runtime ceilings vs Agent-owned spending/tracing.
- Defines minimal Agent runner input and output shapes.
- Keeps Fund as typed domain tool owner rather than generic runner owner.

Validation point:

- Future implementation planning can now preserve existing `FundLLMExecutionRequest` / provider factory boundary while moving write-audit-repair execution mechanics into Agent.

### 02-已修复-[中]-Typed audit contract 仍是概念清单，缺少可验收的 MVP schema、状态机和现有类型映射

Controller decision: accepted.

Fix:

- Added `MVP typed schema and current-type mapping`.
- Defines MVP enum domains and schema version.
- Maps current `ChapterAuditIssue`, `ChapterProgrammaticAuditResult`, `ChapterLLMAuditResult`, `ChapterAuditResult.accepted`, `ChapterRepairAction`, `ChapterRunStopReason`, and `ChapterFailureCategory` / `ChapterFailureSubcategory` into the proposed audit contract.
- Narrows MVP programmatic-first scope to current acceptance-loop essentials.
- Explicitly defers Evidence Confirm, final-judgment consistency expansion, full Ch6 threshold semantics and broader domain rule expansion.

Validation point:

- Future implementation planning can target a compatibility wrapper first instead of inventing parallel Service/Agent/Fund schemas.

### 03-已修复-[低]-Next gate 建议把 Ch3-only calibration 放入 Agent engine planning slices，容易突破 controller 已收窄的 Ch3 gate

Controller decision: accepted.

Fix:

- Removed Ch3 calibration from the suggested Agent-engine implementation slices.
- Added explicit statement that Ch3-only deterministic contract / wording calibration remains a separate controller gate.
- Preserved Ch3 as motivating evidence only.

Validation point:

- Agent-engine planning and Ch3-only calibration now remain separate gates; no implicit authorization to change Ch3, Ch2, Ch6, provider budget or auditor strictness.

## Validation

To be run after this fix:

- `git diff --check -- docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-20260602.md docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-review-fix-evidence-20260602.md`
- Secret-oriented scan for API key / Authorization / Bearer / cookies / password patterns in the modified review artifacts.
- Re-review of the accepted findings only.

## Residual Risks

- This remains design-only and is not current implementation fact.
- Truth-source sync is still blocked until re-review accepts this design.
- Implementation planning must still be a separate gate and must not start here.

Self-check: pass.
