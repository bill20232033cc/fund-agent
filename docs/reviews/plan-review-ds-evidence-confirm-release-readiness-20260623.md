# Plan Review: Evidence Confirm Productionization Release/readiness Plan

- Review role: AgentDS plan reviewer (adversarial)
- Target: `docs/reviews/evidence-confirm-productionization-release-readiness-plan-20260623.md`
- Date: 2026-06-23
- Verdict: **PLAN_REVIEW_PASS_WITH_RISKS**

## Review Method

Adversarial review against: AGENTS.md module boundaries (UI→Service→Host→Agent), `FundDocumentRepository` access discipline, fallback classification rules, current control truth in `docs/current-startup-packet.md`, final closeout artifact `docs/reviews/evidence-confirm-productionization-default-on-policy-draft-pr-pass-final-closeout-20260623.md`, and live code at `fund_agent/`.

Evidence gathered via static read-only checks: `rg`, file reads, `git status --short --branch`. No live/PDF/provider/LLM commands run. No production code, plan, control docs, or PR body edited.

## Assumptions Tested

### A1 — Plan claims real codebase gaps exist

**Test**: Verify annual-period CLI gap, checklist off enforcement, renderer non-rendering, Service Evidence Confirm flow.

**Result**: All claims confirmed.

| Claim | Source | Verdict |
|---|---|---|
| Annual-period CLI doesn't print EC summary | `cli.py:1080-1083` — calls `_echo_quality_gate_summary` then `_echo_multi_year_annual_summary` then report body; no `_echo_evidence_confirm_summary` call | CONFIRMED |
| Checklist forces EC off | `fund_analysis_service.py:1683-1684` — `_effective_evidence_confirm_policy` returns `"off"` for `command_source == "checklist"` | CONFIRMED |
| Renderer has no EC content | Zero matches for `evidence_confirm` or `EvidenceConfirm` in `renderer.py` | CONFIRMED |
| Service feeds EC summary to quality gate | `fund_analysis_service.py:1198-1210` — runs EC, passes summary to `_run_quality_gate_if_enabled` | CONFIRMED |
| `FundDocumentRepository` is the only annual report access path | `evidence_confirm_runner.py` facade exports `run_repository_bounded_evidence_confirm`; `evidence_confirm_sources.py:252-397` calls only `repository.load_annual_report()` | CONFIRMED |

### A2 — Architecture boundaries are preserved in slice designs

**Test**: Check each slice's allowed files against AGENTS.md module boundaries.

**Result**: Boundaries respected with one note.

- RR-S1 through RR-S8 file allowlists all respect UI→Service→Host→Agent layering.
- RR-S3 places the new provider adapter in `fund_agent/services/` (Service layer), consistent with AGENTS.md rule that provider construction belongs to Service.
- RR-S3 requires the adapter to consume `EvidenceEntailmentClient` Protocol from Fund layer — Protocol confirmed at `evidence_confirm_semantic.py:105-119`. Cross-layer dependency is through typed contract, not implementation import, so boundary is preserved.
- No slice allows Service/UI/renderer/quality-gate direct PDF/cache/source-helper access.

### A3 — Plan doesn't overclaim from PR cleanliness

**Test**: Check whether any slice claims release-readiness from CI success or PR merge state alone.

**Result**: Plan explicitly disclaims this. RR-S8 requires explicit user authorization for each external action. Non-goals section (line 52) states "No claim that single-sample live evidence, no-live tests, or CI success proves release readiness." The plan keeps proof layers separate: no-live static → live source → provider semantic → product UX → docs → PR external. Each layer gates the next.

### A4 — `EvidenceEntailmentClient` Protocol exists

**Test**: Verify the Protocol RR-S3's adapter must implement actually exists.

**Result**: CONFIRMED at `fund_agent/fund/evidence_confirm_semantic.py:105-119`. The Protocol declares `judge(request: EvidenceEntailmentRequest) -> EvidenceEntailmentJudgment`. RR-S3's adapter can implement it without modifying the Fund layer.

## Findings

### F1 — Missing explicit slice dependency ordering (medium)

The plan sequences slices RR-S1 through RR-S8 but does not state which slices MUST complete before others. Dependencies exist and are material:

- RR-S2 stop condition: "if RR-S1 proves an instrumentation gap, stop" — implies RR-S2 depends on RR-S1.
- RR-S5 stop condition: "Display change requires new annual-period request contract" — RR-S5 depends on RR-S1 confirming Service projection is sufficient.
- RR-S7: "sync current behavior only after evidence/product gates close" — RR-S7 depends on RR-S1 through RR-S6.
- RR-S8: "separate local release readiness from external GitHub/release state mutation" — RR-S8 depends on RR-S7.

Without an explicit dependency DAG, an implementer could attempt parallel execution of dependent slices and hit blockers, or execute RR-S8 before RR-S7 completes.

**Recommendation**: Add a dependency declaration before the slice list. Minimum acceptable form:

```
RR-S1 (no deps) → RR-S2 (depends on S1), RR-S3 (depends on S1), RR-S4 (no deps), RR-S5 (depends on S1), RR-S6 (no deps) → RR-S7 (depends on S1-S6) → RR-S8 (depends on S7)
```

### F2 — RR-S4 and RR-S6 are decision gates, not implementation gates (medium)

RR-S4 (Checklist CLI/support) lists Option A (keep off + deferral artifact), Option B (add CLI policy), Option C (default to warn). No recommendation is made. RR-S6 (Report-body rendering) similarly lists Option A (keep out), Option B (audit metadata section), Option C (per-chapter labels). No recommendation is made.

The plan self-describes as `PLAN_READY_FOR_REVIEW` and positions itself for "code-generation-ready" implementation. But a slice with three open options and no recommendation is a decision gate, not an implementation gate. An implementer reading RR-S4 cannot start coding without first making a product decision the plan defers.

**Recommendation**: Either (a) make a recommendation in the plan (e.g., "Option A is recommended for this release because checklist UX design and report-body wording review are separate product gates"), or (b) reclassify RR-S4 and RR-S6 as `DECISION_REQUIRED` and move them before implementation slices in the dependency order. The latter is more honest about current state.

### F3 — Untracked residue not enumerated as input to RR-S7 (medium)

RR-S7 requires classifying "visible untracked residue" but the plan does not list what residue currently exists. From `git status --short --branch` at review time:

```
?? docs/code-wiki.md
?? docs/codewiki.md
?? docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md
?? docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md
?? docs/next-development-phaseflow.md
?? docs/reviews/code-review-20260623-033703.md
?? docs/reviews/evidence-confirm-productionization-release-readiness-plan-20260623.md
?? docs/reviews/pr-40-review-mimo-ec-p3-20260622.md
?? docs/tmux-agent-memory-store.md
?? scripts/claude_mimo_simple.py
?? scripts/review-artifact.sh
```

Eleven untracked paths. The hygiene gate cannot start without knowing its input set. The plan should enumerate these as a pre-RR-S7 inventory, even if classification happens during RR-S7.

**Recommendation**: Add the current `git status --short --branch` output as an appendix or inline list in RR-S7, with a note that this is the classification starting set and may change if other gates produce new artifacts.

### F4 — Local-ahead / PR-head reconciliation not specified (medium)

Current state: local HEAD = `89ccc44`, PR-40 remote head = `b59aed7`, local is ahead by 1 (the closeout commit). RR-S8 expects "PR head matches the intended accepted commit" before mark-ready. Two scenarios, neither specified:

1. If the closeout commit at `89ccc44` should be part of the release PR: it must be pushed to PR-40 before mark-ready. RR-S8 says push requires explicit user authorization — but doesn't state whether this specific commit SHOULD be pushed.
2. If the closeout commit is local-only evidence: PR-40 head `b59aed7` is already the intended accepted commit, and `89ccc44` is out-of-PR evidence. But then the local tree is not clean (ahead of remote), which contradicts RR-S7's hygiene expectation.

**Recommendation**: RR-S8's preflight should explicitly check whether the local-ahead commit(s) are intended for PR-40 and, if so, require a push authorization sub-step before mark-ready. If not, document why the local-ahead state is acceptable for release.

### F5 — RR-S3 conditional implementation weakens code-generation claim (low-medium)

RR-S3 states "If implementation is needed, new Service-owned adapter module" and "Exact allowed changes if code is required." The conditional means the plan doesn't know whether RR-S3 will produce code, a no-code evidence artifact, or a deferral. This is legitimate uncertainty (provider semantic may not be ready), but it contradicts the plan's self-positioning as "code-generation-ready."

**Recommendation**: Either remove the conditional and assert one path (e.g., "RR-S3 always requires a Service adapter implementation because the current semantic path is no-live/injected-client only"), or split RR-S3 into RR-S3a (decide: is provider adapter needed for this release?) and RR-S3b (implement if decided yes).

### F6 — No cross-slice integration smoke test (low)

Each slice has per-slice validation commands, but there is no cross-slice integration scenario. Example of what's missing: "After RR-S1/S2/S5 complete, run `fund-analysis analyze 004393 --report-year 2025` and assert: exit 0, stderr contains `evidence_confirm_status`, stdout report body has no `evidence_confirm` section, quality gate artifact has expected ECQ issues."

**Recommendation**: Add a lightweight integration smoke test to RR-S7 that exercises the full chain (CLI → Service → EC → quality gate → CLI display → report body) without requiring live authorization. This smoke test can reuse RR-S1 no-live test data.

### F7 — RR-S2 negative case under-specified (low)

RR-S2 says "Include one controlled negative or unavailable case only if the source failure class is explicit and safe to run." It does not define which failure classes are safe to test. `not_found` and `unavailable` are safe (no source manipulation needed — use a non-existent fund or disable network). `schema_drift`, `identity_mismatch`, and `integrity_error` require manipulating the source response or infrastructure, which may not be safe or possible in a read-only evidence gate.

**Recommendation**: Restrict negative cases to `not_found` (unknown fund code) and, if infrastructure allows, controlled `unavailable` (network disabled). Explicitly exclude `schema_drift`/`identity_mismatch`/`integrity_error` as unsafe for a read-only evidence gate unless a controlled test fixture exists.

### F8 — RR-S1 test scope may miss adjacent regressions (low)

RR-S1 validation runs only the explicitly listed test files. Adjacent test modules that exercise the same production code through different entry points (e.g., `test_evidence_confirm_runner.py` or integration-level Service tests) are not included. If an adjacent test catches a regression, RR-S1 could pass while a broader test suite fails.

**Recommendation**: Expand RR-S1 validation to include `tests/fund/test_evidence_confirm_runner.py` (if it exists) and a full focused `pytest tests/fund/ tests/services/ tests/ui/ -q` as a secondary check, with the understanding that only the listed test files are the primary evidence surface.

## Open Questions

1. **Q1**: Should the closeout commit at `89ccc44` (this plan artifact + prior closeout) be pushed to PR-40 before mark-ready, or does it remain local-only evidence? This determines RR-S8's push preflight.

2. **Q2**: For RR-S4, is the product owner available to make the checklist decision, or should the plan recommend Option A (keep off, defer) as the default for this release?

3. **Q3**: For RR-S6, is there a product/UX owner who can decide whether audit metadata belongs in the investment report body, or should Option A (keep out) be the default?

4. **Q4**: Does the plan author intend RR-S3 to always produce a Service adapter implementation, or is a no-code deferral acceptable if the current no-live/injected-client semantic path is deemed sufficient for release?

5. **Q5**: Are there existing test fixtures or controlled environments for provoking `schema_drift` / `identity_mismatch` / `integrity_error` failures without live source manipulation? If not, should RR-S2's negative case be limited to `not_found` only?

## Architecture Boundary Verification

All eight slices respect the UI→Service→Host→Agent layering:

| Slice | New code layer | Boundary check |
|---|---|---|
| RR-S1 | No new code | N/A — read-only evidence |
| RR-S2 | No new code | N/A — live execution evidence |
| RR-S3 | Service (`fund_agent/services/`) | Service owns provider construction; adapter consumes Fund Protocol, doesn't import Fund internals. PASS |
| RR-S4 | Service + CLI | Service orchestrates policy; CLI exposes flag. No Host/Agent leakage. PASS |
| RR-S5 | CLI only | CLI calls existing Service result field. No new layer crossing. PASS |
| RR-S6 | Renderer (Fund layer) only if implemented | Renderer is Fund-owned template rendering per AGENTS.md. PASS |
| RR-S7 | Docs only | N/A |
| RR-S8 | No code | N/A — external state mutation |

`FundDocumentRepository` boundary: No slice allows bypassing the repository. RR-S2 explicitly requires all live samples to go through the repository-bounded runner. RR-S3 requires the provider adapter to accept only `EvidenceEntailmentRequest`, with no repository/PDF/source access. PASS.

Fallback classification: The plan does not change fallback policy (listed as non-goal). The failure categories `schema_drift`/`identity_mismatch`/`integrity_error` remain fail-closed per AGENTS.md. PASS.

Dayu runtime independence: No slice introduces `dayu-agent` as a production runtime dependency. PASS.

## Residual Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Implementer executes slices out of order due to missing dependency DAG | Medium | Add explicit dependency graph (F1) |
| RR-S4/RR-S6 stall because product decision is unavailable | Medium | Either recommend Option A or reclassify as decision gates (F2) |
| RR-S8 cannot complete because local-ahead/PR-head reconciliation is undefined | Medium | Specify whether `89ccc44` should be in PR-40 (F4) |
| Untracked residue surprises during RR-S7 | Low-Medium | Enumerate residue as input (F3) |
| RR-S3 implementation scope ambiguity causes rework | Low-Medium | Assert whether code is required (F5) |
| RR-S1 passes but broader test suite fails | Low | Expand test scope or document why narrow scope is sufficient (F8) |
| Negative case in RR-S2 provokes unsafe source manipulation | Low | Restrict to `not_found` (F7) |
| Cross-slice integration regressions undetected | Low | Add integration smoke test to RR-S7 (F6) |

## Conclusion

The plan correctly identifies real, verifiable gaps in the codebase, respects all architecture boundaries (UI→Service→Host→Agent, `FundDocumentRepository`, fallback classification, Dayu independence), and separates proof layers properly. Authorization boundaries for live/PDF/provider/PR-state operations are explicit and correctly gated.

However, the plan has four material issues that prevent it from being code-generation-ready:
1. Missing explicit slice dependency ordering (F1)
2. RR-S4 and RR-S6 contain unresolved product decisions with no recommendation (F2)
3. Untracked residue not enumerated as input to the hygiene gate (F3)
4. Local-ahead/PR-head reconciliation not specified (F4)

These are fixable in-plan (no code changes needed). Once addressed, the plan will be ready for implementation gate handoff.

## Verdict Token

**PLAN_REVIEW_PASS_WITH_RISKS**

## Checks

- `git diff --check -- docs/reviews/plan-review-ds-evidence-confirm-release-readiness-20260623.md` — clean (new file, no whitespace errors)
- All claims verified against live code at `fund_agent/` via static read-only checks
- No production code, plan, control docs, or PR body edited
- No live/PDF/provider/LLM commands run
