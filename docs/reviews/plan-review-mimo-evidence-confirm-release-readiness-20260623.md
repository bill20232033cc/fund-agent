# Plan Review: Evidence Confirm Productionization Release/readiness Plan

- Review target: `docs/reviews/evidence-confirm-productionization-release-readiness-plan-20260623.md`
- Role: AgentMiMo plan reviewer (adversarial)
- Date: 2026-06-23
- Gate: Evidence Confirm Productionization Release/readiness Planning Gate
- Classification: `heavy`
- Branch: `evidence-confirm-productionization`
- PR-40 remote head: `b59aed754c491adb05e533fde812b3ba93fa3f96`, CI `test` success, merge state `CLEAN`

## Review Inputs

- `AGENTS.md` (module boundaries, hard constraints, evidence traceability)
- `docs/design.md` v2.34 (Evidence Confirm V1/V2 no-live current-state, Service/UI/Host/Agent boundaries)
- `docs/implementation-control.md` (current gate, non-goals, authorization boundaries)
- `docs/current-startup-packet.md` (PR-40 state, NOT_READY blockers)
- `docs/reviews/evidence-confirm-productionization-default-on-policy-draft-pr-pass-final-closeout-20260623.md` (residual routing)
- Target plan (470 lines, 8 slices, 11 requirements)

## Methodology

Adversarial read focusing on: (1) code-generation readiness per slice, (2) scope/sequencing correctness, (3) live/PDF/provider authorization boundary explicitness, (4) product decision actionability, (5) release/readiness proof discipline vs overclaiming, (6) architecture boundary preservation.

---

## Findings

### F-01 [medium] RR-S2 Sample Policy Ambiguity May Block Gate Execution

RR-S2 states: "At minimum one previously accepted sample plus at least three additional funds/years across different fund types **if available** in the selected-fund universe."

Problems:
- The "selected-fund universe" is not defined. The startup packet references only `004393` as the accepted live sample. No enumeration of available funds/years/fund-types exists.
- "If available" creates an escape hatch: if no additional samples exist, the gate could pass with only the previously accepted single sample — but this contradicts the RR-01 requirement for "multi-sample live evidence."
- The gate does not specify who decides what's "available" or how to prove availability.

Assumption tested: that a concrete sample list exists or can be deterministically derived. Finding: it cannot from current control docs.

Impact: RR-S2 executor must either (a) enumerate available samples before gate execution, or (b) accept that the gate may be satisfied by fewer than four samples — which undermines the multi-sample readiness claim.

Recommendation: Add a preflight step to RR-S2 that requires explicit enumeration of the available fund universe from `FundDocumentRepository` or accepted evidence, and define minimum sample count as a hard floor (not "if available").

### F-02 [medium] RR-S4 Checklist Options Lack Decision Criteria

RR-S4 presents three options:
- Option A: keep checklist off, write deferral artifact
- Option B: add explicit CLI policy `off|warn|block`
- Option C: default checklist to `warn` after separate product review

The plan does not specify which option is recommended, what criteria should drive the decision, or who the product owner is. This makes RR-S4 non-actionable as a code-generation slice — the executor must first make a product decision that the plan defers.

Assumption tested: that the plan provides sufficient guidance for the gate executor to choose. Finding: it does not; the decision is deferred within the deferral plan.

Recommendation: Recommend Option A (deferral) as the default for this release, with explicit rationale (checklist UX semantics differ from analyze, no user-facing evidence yet, and checklist is a lower-risk surface). If the controller/product owner disagrees, they can override at RR-S4 gate time.

### F-03 [low-medium] RR-S6 Report-body Decision Similarly Non-actionable

RR-S6 presents three options for report-body Evidence Confirm rendering without recommending one. The plan's own non-goals state "no parser replacement, golden promotion, broad extractor correctness claim" — suggesting the surface is immature. But the plan doesn't connect this to a recommendation.

Recommendation: Recommend Option A (keep Evidence Confirm outside report body) as default, with rationale that CLI summary + quality gate ECQ issues are sufficient UX for `warn` policy, and report-body rendering requires wording review and audit contract review that are not yet done.

### F-04 [low] RR-S1 Renderer Test Module Not Explicitly Listed

RR-S1's validation commands list test files `tests/fund/test_evidence_confirm*.py`, `tests/fund/test_quality_gate_integration.py`, `tests/services/test_fund_analysis_service.py`, `tests/ui/test_cli.py`. The expected assertions include "Renderer report body remains free of Evidence Confirm summary." However, no renderer-specific test file (e.g., `tests/fund/test_template_renderer.py`) is in the validation command set.

Assumption tested: that renderer behavior is covered by the listed test files. Finding: `fund_agent/fund/template/renderer.py` is listed as read-only production module, but its test coverage is not explicitly validated.

Impact: Low — the renderer has no Evidence Confirm code path, so absence of renderer tests does not create a false-pass risk. But the assertion "renderer report body remains free of Evidence Confirm summary" should be backed by at least one test that verifies renderer output does not contain EC summary strings.

Recommendation: Add renderer test file to RR-S1 validation commands if a test module exists; otherwise note the assertion is verified by code inspection only.

### F-05 [low] RR-S7/RR-S8 Sequencing: Docs Sync Before PR Authorization

RR-S7 (docs/hygiene) runs before RR-S8 (PR authorization). RR-S7's expected assertions include "No doc claims release readiness before RR-S8." This is correct in principle, but creates a risk: if RR-S7 updates docs to describe current behavior (which includes Evidence Confirm default-on), a reader might interpret the docs as claiming readiness even if they don't use the word "ready."

The plan mitigates this with "Docs state only accepted current behavior" — which is correct. No finding beyond confirming the mitigation is intentional.

### F-06 [low] RR-S2 Validation Command Shows Only CLI Surface

RR-S2 lists "Existing callable surfaces only: `fund_agent.fund.evidence_confirm_runner.run_repository_bounded_evidence_confirm`, `FundAnalysisService.analyze()`, or `fund-analysis analyze` CLI." But the validation command pattern only shows the CLI:

```
uv run fund-analysis analyze <fund_code> --report-year <year> --valuation-state unavailable --quality-gate-policy warn
```

The plan does not show how to invoke `run_repository_bounded_evidence_confirm` directly for testing. This is acceptable since CLI is the primary surface, but the gate should clarify whether direct runner invocation is needed for any assertion.

Recommendation: No change needed; CLI surface is sufficient for readiness proof. Note that `--valuation-state unavailable` prevents live thermometer fetch, which is correct for source/PDF-focused evidence.

### F-07 [low] RR-S3 Service-owned Adapter Placement Question

RR-S3 proposes a new `fund_agent/services/evidence_confirm_semantic_provider.py` as a "Service-owned adapter" implementing `EvidenceEntailmentClient` (a Fund-layer Protocol). This creates a dependency: Service depends on Fund's Protocol definition.

This is consistent with the current architecture where Service calls Fund-layer capabilities. The Fund Protocol is the contract boundary, and Service implements it — similar to how Service constructs provider writer/auditor clients that Fund tools consume. No boundary violation.

However, the plan should note that this adapter must not access `FundDocumentRepository`, PDF cache, or source helpers — which it does in the stop conditions. Confirmed consistent.

### F-08 [informational] Local-ahead State Not Reconciled

The plan notes: "Local `HEAD=89ccc44` is one commit ahead of `origin/evidence-confirm-productionization`" and "Local branch is ahead of remote by one closeout commit; external-state readiness must reconcile whether PR-40 should include that local artifact or whether it remains local-only evidence."

This reconciliation is deferred to RR-S8. The plan does not specify whether the local closeout commit (`89ccc44`) should be pushed before RR-S8 or left local-only. This is acceptable — RR-S8 explicitly requires "push local accepted readiness/closeout commits if needed" — but the executor should be aware that the local-ahead state exists.

### F-09 [informational] Completion Report Format Is Well-specified

The plan's completion report format (lines 453-468) provides a structured template for future gates. This is good practice and reduces ambiguity in gate closeout. No finding.

---

## Assumptions Tested

| # | Assumption | Result |
|---|---|---|
| A-1 | Each slice has exact allowed files/modules | **Pass** — all 8 slices enumerate exact files |
| A-2 | Each slice has validation commands | **Pass** — all implementation slices have commands |
| A-3 | Each slice has stop conditions | **Pass** — all 8 slices have explicit stop conditions |
| A-4 | Authorization boundaries are explicit | **Pass** — RR-S2/S3/S8 require explicit authorization |
| A-5 | Architecture UI->Service->Host->Agent preserved | **Pass** — no boundary violations detected |
| A-6 | FundDocumentRepository boundary preserved | **Pass** — no direct PDF/cache/source access outside Fund layer |
| A-7 | Multi-sample policy is actionable | **Fail** — see F-01 |
| A-8 | Checklist decision is actionable | **Fail** — see F-02 |
| A-9 | Report-body decision is actionable | **Fail** — see F-03 |
| A-10 | Plan does not overclaim readiness from PR cleanliness | **Pass** — plan explicitly separates PR state from readiness proof |

---

## Open Questions

| # | Question | Owner | Impact |
|---|---|---|---|
| Q-1 | What is the "selected-fund universe" for RR-S2 multi-sample evidence? | Controller / Fund documents owner | Blocks RR-S2 execution |
| Q-2 | Should RR-S4 default to Option A (deferral) for this release? | Product owner / controller | Blocks RR-S4 execution |
| Q-3 | Should RR-S6 default to Option A (no report-body rendering) for this release? | Product owner / controller | Blocks RR-S6 execution |
| Q-4 | Should the local closeout commit (`89ccc44`) be pushed before RR-S8 or remain local-only? | Controller | Affects RR-S8 preflight |

---

## Residual Risks

| # | Risk | Severity | Mitigation in Plan |
|---|---|---|---|
| R-1 | RR-S2 may pass with single sample if no additional funds available | Medium | Plan says "if available" — should be hard floor |
| R-2 | RR-S4/S6 decisions deferred within a deferral plan | Medium | Recommend default options to make slices actionable |
| R-3 | RR-S3 provider behavior may be unstable across providers | Low | Plan requires deterministic V2 to remain authoritative |
| R-4 | RR-S7 docs update may inadvertently signal readiness | Low | Plan requires "no doc claims release readiness before RR-S8" |
| R-5 | Local-ahead state creates confusion about PR-40 contents | Low | RR-S8 explicitly handles push/reconciliation |

---

## Architecture Boundary Check

| Boundary | Status | Detail |
|---|---|---|
| UI does not call Host/Agent internals | **Pass** | CLI only calls Service |
| Service does not call PDF/cache/source helper | **Pass** | RR-S2/S3 stop conditions enforce |
| Host is business-opaque | **Pass** | No Host changes in plan |
| Agent FundDocumentRepository is sole PDF entry | **Pass** | RR-S2 validation enforces |
| No Docling/pdfplumber direct consumption | **Pass** | Plan non-goals explicitly block |
| EvidenceEntailmentClient Protocol boundary | **Pass** | Fund defines Protocol, Service implements |
| No extra_payload for explicit params | **Pass** | All params through typed request/contract |

---

## Verdict

### PLAN_REVIEW_PASS_WITH_RISKS

The plan is well-structured, correctly scoped, and maintains architecture boundaries. It successfully separates readiness proof from PR cleanliness and enforces explicit authorization for all external state mutations. The 8-slice decomposition is logical and the validation commands are specific.

However, three findings (F-01, F-02, F-03) create execution ambiguity that could block gate implementation:

1. **RR-S2 sample policy** needs a concrete fund universe enumeration and a hard minimum sample floor.
2. **RR-S4 checklist decision** needs a recommended default (Option A: deferral) to be code-generation-ready.
3. **RR-S6 report-body decision** needs a recommended default (Option A: no rendering) to be code-generation-ready.

These are medium-severity findings that do not invalidate the plan but require controller/product-owner disposition before the corresponding slices can be executed. The plan is acceptable for review-channel acceptance with these risks noted and routed to the appropriate owners.

---

## Checks

- Artifact written: `docs/reviews/plan-review-mimo-evidence-confirm-release-readiness-20260623.md`
- `git diff --check` on artifact: pending (see below)
- No production code, plan, control docs, or PR body modified
- No commit, push, mark-ready, merge, request reviewers, or release performed
