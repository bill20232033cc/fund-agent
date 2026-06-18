# Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Plan — MiMo Review

Date: 2026-06-14

Role: AgentMiMo reviewer, not controller

Gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Planning Gate`

Review target: `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-plan-20260614.md`

## 1. Verdict

```text
PASS_WITH_FINDINGS
```

## 2. Findings

### F1 — LOW: Conditional source rule escape-hatch wording may invite overbroad source changes

**Location**: Plan Section 5, conditional source write set paragraph

The plan states "No production Python source change is expected" but then opens a conditional escape: "If an implementation worker proves a source gap, it must stop and return to controller unless the gap is a narrow defect in `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py`, `fund_agent/services/chapter_orchestrator.py`, `fund_agent/agent/runner.py` or `fund_agent/agent/repair.py` directly required by this plan."

This is structurally correct, but "directly required by this plan" is ambiguous at implementation time. The implementation gate should adopt the same tight language: "only if a no-live test fails because the existing code does not already support the needed enum behavior, and the fix is confined to the five named files."

**Severity**: LOW — does not block planning acceptance; implementation gate controller can tighten.

### F2 — LOW: V5 issue-id naming assumes new writer output categories without explicit implementation contract

**Location**: Plan Section 6, V5 expected assertions

V5 expects `result.status == "blocked"`, `stop_reason == "missing_required_output_marker"`, and issue id starting with `writer:required_output_gap_missing:` or `writer:required_output_verification_missing:` instead of the existing `writer:required_output_block:`. This implies the implementation must introduce new issue-id categories. The plan does not state whether the existing `writer:required_output_block:` prefix is retained for the `available` fact block case or replaced entirely.

The implementation gate should preserve the existing `writer:required_output_block:` issue id for the `available`-fact block case and only add the new prefixes for the gap/verification-missing sub-cases. If this is the intent, it should be explicit in V5.

**Severity**: LOW — does not block planning; implementation can resolve naming.

### F3 — INFORMATIONAL: Controller amendment F1 "ambiguity residual" is already covered but could be more prominent

**Location**: Plan Sections 3 and 4

The plan correctly handles the fact-absence vs present-but-ignored ambiguity (controller amendment F1): typed availability is the deterministic discriminator, available facts with anchors remain fail-closed, and product wording avoids claiming source absence. The residual is explicitly recorded in Section 3 "Residual ambiguity."

This is compliant. The handling could be more prominent in Section 4 by adding a row-level guard note: "If `available` status and anchor ids are present, the implementation must not auto-gap-render the chapter to hide writer noncompliance; this is the fail-closed boundary." The equivalent statement exists in Section 4 auditor semantics bullet 3, which is sufficient.

**Severity**: INFORMATIONAL — no action required.

### F4 — INFORMATIONAL: Validation commands are scoped correctly

**Location**: Plan Section 6 validation commands

The validation commands target exactly the seven test files in the validation matrix plus `ruff` and `git diff --check`. This is narrow and feasible. The plan correctly notes that if production source becomes necessary, ruff should be extended to touched source files.

**Severity**: INFORMATIONAL — no action required.

## 3. Controller Amendment Compliance Matrix

| Amendment | Requirement | Plan compliance | Status |
|---|---|---|---|
| F1 | Distinguish fact absence from present-but-ignored; record ambiguity; constrain wording | Section 3 records ambiguity; Section 4 gates gap rendering on non-`available` status; product wording says "insufficient/unreviewed/unavailable" not "source lacks" | SATISFIED |
| F2 | Concrete validation specs: file scope, fixtures, test intent, expected assertions | Section 6 has 15 test entries (V1-V15) with exact file, fixture/stub layer, test intent and expected assertions | SATISFIED |
| F3 | Auditor/repair alignment proof | V6/V7 prove auditor accepts safe wording and blocks unsafe percentages; V10 proves repair context alignment | SATISFIED |
| F4 | Exact user-visible semantics | Section 4 table specifies per-item-group rendering action and wording guidance; Section 3 constrains default wording | SATISFIED |
| F5 | Scope to `l1_numerical_closure` unless justified otherwise | Section 1 explicitly scopes to `l1_numerical_closure`; no extension to other L1 subcategories | SATISFIED |

## 4. Allowed Write Set Assessment

| Criterion | Assessment |
|---|---|
| Narrow enough | Yes. Production source changes are not expected; conditional rule is bounded to 5 files. Template change is limited to 7 `when_evidence_missing` values. Test additions are in 7 existing test files. |
| Consistent with AGENTS.md | Yes. Module boundaries respected; no Host/Agent/dayu runtime changes; no direct source/PDF/cache access. |
| Consistent with design/control truth | Yes. `docs/design.md` and `docs/implementation-control.md` are not in write set. |
| Template change route valid | Yes. `when_evidence_missing` is a template contract field already used by Ch3/Ch6 with `render_evidence_gap` and `render_minimum_verification_question`. Ch2 items currently use `block`; changing to gap/verification actions follows the established pattern. No additional design/control authorization needed — this is the gate's explicit purpose. |

## 5. Preservation Constraints

| Constraint | Preserved | Evidence |
|---|---|---|
| EID single-source/no-fallback | Yes | Non-goal bullet: "Do not introduce Eastmoney, fund-company, CNINFO or any non-EID fallback." V15 proves same-source requirement ids only. |
| NOT_READY | Yes | Plan Sections 1 and 8 preserve `NOT_READY`. No readiness/release/PR commands. |
| Current repair budget | Yes | Section 4: `max_repair_attempts` remains unchanged; V8/V9/V10 prove request count and one-repair semantics. |
| No live/provider/source policy changes | Yes | Non-goal bullets explicitly list these as forbidden. Section 5 forbidden write set confirms. |

## 6. Masking Risk Assessment

The plan does not mask present-but-ignored facts as evidence absence:

- Gap rendering is gated on non-`available` typed availability status (Section 4, auditor semantics bullet 3).
- `available` facts with anchors remain fail-closed as `l1_numerical_closure` (Section 4, item group table note).
- V9 explicitly tests that present-but-ignored facts remain `status == "failed"` with `failure_subcategory == "l1_numerical_closure"`.
- The residual ambiguity (Section 3) is recorded and constrained by product wording that says "insufficient/unreviewed/unavailable" rather than "the annual report lacks the fact."

This is the correct approach under no-live boundaries: typed availability is the best available deterministic discriminator, and the wording constraint prevents overclaiming.

## 7. Residuals

| Residual | Disposition | Next handling |
|---|---|---|
| Live sample fact availability unknown under no-live constraints | Accepted in plan Section 3 | Future live/body evidence gate may refine; wording constraint mitigates |
| Gap rendering could theoretically be used to hide noncompliance if availability metadata is wrong | Mitigated by scope | `available` status must come from same-source `EvidenceAvailability`; V15 proves requirement mapping unchanged |
| Template change could have broader side-effects | Controlled | V1 proves Ch3 assertions unchanged; plan limits to Ch2 required-output `when_evidence_missing` only |
| New issue-id categories (F2) need explicit implementation contract | Deferred to implementation | Implementation gate should confirm naming preserves existing `writer:required_output_block:` for available-fact case |

## 8. Recommendation for Controller

The plan satisfies all five controller amendments with concrete, implementation-ready validation specifications. The allowed write set is narrow, the preservation constraints are explicit, and the masking risk is correctly mitigated through typed availability gating and constrained product wording.

The two LOW findings (conditional source rule wording, V5 issue-id naming) are implementation-resolution items that do not block planning acceptance. The template change route is valid and follows the established Ch3/Ch6 pattern.

Recommended verdict: `PASS_WITH_FINDINGS_READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`.
