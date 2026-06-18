# MVP internalized Agent engine and typed audit contract design re-review

## Re-review Context

- Gate: `MVP internalized Agent engine and typed audit contract design gate`
- Role: Gateflow-governed re-review agent; not controller.
- Reviewed design artifact: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-20260602.md`
- Source review: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-review-20260602.md`
- Fix evidence: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-review-fix-evidence-20260602.md`
- Status: `pass`

## Scope

This re-review only checks whether the three accepted review findings were fixed in the design artifact. It does not implement code, change prompt/provider/runtime/score-loop/fail-closed semantics, sync truth docs, stage, commit, push or open PRs.

## Finding Re-review

### 01-fixed-Agent runner 与 provider client ownership 是否已收敛到 MVP handoff

Conclusion: `fixed`

Evidence:

- Design lines 86-88 add `MVP boundary handoff` and explicitly state provider construction remains Service-owned for the first Agent-engine MVP unless a later provider-factory migration gate changes it.
- Design lines 90-97 split ownership: Service owns business request/provider config/runtime ceilings; Agent owns chapter task execution and `ToolTrace`; Fund exposes typed writer/programmatic audit/semantic audit tool adapters.
- Design lines 99-112 define minimal Agent runner input/output shape, including Service-declared ceilings, injected typed tools, accepted chapters, chapter results, typed audit results, tool trace and final assembly readiness.
- Fix evidence lines 19-27 claim the same fix and validation point.

Re-review judgment:

The fix resolves the original ambiguity. An implementation worker no longer needs to guess whether provider construction migrates into Agent/Fund in the first MVP; the design now preserves current Service-owned provider construction while moving execution mechanics into Agent.

### 02-fixed-Typed audit contract 是否已有足够 MVP schema/current-type mapping/programmatic-first boundary

Conclusion: `fixed`

Evidence:

- Design lines 128-140 add `MVP typed schema and current-type mapping`, including `schema_version`, closed audit/runtime enum domains and MVP status/action names.
- Design lines 141-151 map current `ChapterAuditIssue`, `ChapterProgrammaticAuditResult`, `ChapterLLMAuditResult`, `ChapterAuditResult.accepted`, `ChapterRepairAction`, `ChapterRunStopReason`, and failure category/subcategory into the MVP audit contract.
- Design lines 153-160 narrow MVP programmatic-first scope to current acceptance-loop essentials: required output markers, anchor/missing marker semantics, must-not-cover issue identity, Ch3-style missing-fact downgrade identity, implemented L1 identity and timeout/runtime failure separation.
- Design line 162 explicitly defers Evidence Confirm, final-judgment consistency expansion, full Ch6 threshold semantics and broader domain rule expansion.
- Design lines 164-172 preserve invariants: programmatic audit before semantic audit, semantic audit cannot override programmatic blockers, repair exhaustion cites issue/attempt ids, and timeout is runtime failure rather than content proof.
- Fix evidence lines 35-43 claim the mapping and narrowed MVP scope.

Re-review judgment:

The fix is sufficient for design-gate acceptance. It is still not implementation-ready by itself, but it now gives a later planning agent a concrete MVP schema boundary, compatibility mapping, and programmatic-first scope instead of a pure concept list.

### 03-fixed-Ch3-only calibration 是否已从 Agent-engine implementation slices 中拆出

Conclusion: `fixed`

Evidence:

- Design lines 274-278 now list only Slice A/B/C for Agent-engine planning: schema without runtime/provider ownership changes, fake-client runner/ToolTrace wrapper, and later Service facade to Agent state-machine migration.
- Design line 276 explicitly says Slice A must not change provider construction ownership.
- Design line 278 keeps Service use case/policy/report strategy and Service-owned provider construction while migrating write-audit-repair mechanics.
- Design line 280 states Ch3-only deterministic contract / wording calibration remains a separate controller gate and must not be bundled into Agent-engine implementation planning.
- Fix evidence lines 51-57 claim Ch3 was removed from Agent-engine slices and kept as a separate gate.

Re-review judgment:

The fix resolves the scope-creep risk. Ch3 remains motivating evidence only, and the design no longer authorizes Ch3, Ch2, Ch6, provider budget or auditor-strictness changes inside the Agent-engine implementation slices.

## Residual Risks

- Non-blocking: The design remains design-only and must not be copied into truth docs or implementation plans as accepted current fact until controller acceptance.
- Non-blocking: `docs/implementation-control.md` and `docs/current-startup-packet.md` still contain some stale provider-config wording relative to the provider-restored review/fix evidence. This is a controller truth-source sync residual, not a blocker for this re-review.
- Non-blocking: Future implementation planning still needs exact file ownership, tests and validation commands; this re-review only verifies the design-fix sufficiency for accepted findings.

## Secret-safety Note

This re-review artifact contains no API keys, Authorization headers, Bearer tokens, cookies, passwords, raw provider responses, hidden prompts or complete provider config values. It only references safe artifact paths, section names and design excerpts.

## Re-review Self-check

- Role/scope: pass; re-review only, not controller.
- Allowed reads: pass; used only the specified design/review/fix evidence and allowed truth docs for consistency.
- Allowed write: pass; wrote only `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-rereview-20260602.md`.
- Finding status mapping: pass; all three accepted findings have fixed/still-open conclusions with evidence.
- Residual risks separated from finding status: pass.
- Secret safety: pass.
- Final status is `pass`: pass.

Self-check: pass
