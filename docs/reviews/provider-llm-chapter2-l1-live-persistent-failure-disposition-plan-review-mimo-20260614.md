# Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Plan — Adversarial Review

Date: 2026-06-14

Role: AgentMiMo plan reviewer

Gate: `Provider/LLM Chapter 2 L1 Live-persistent Failure Disposition Gate`

Review target: `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-20260614.md`

## 1. Verdict

`PASS_WITH_FINDINGS`

## 2. Review Questions

### Q1: Does the plan correctly respect current control truth, EID single-source/no-fallback, and NOT_READY?

**Verdict: YES**

The plan explicitly preserves:
- `NOT_READY` (Section 1, Section 6, Section 7 validation matrix entry 9)
- EID single-source/no-fallback (Section 1, Section 6 non-goals)
- No source policy, fallback, provider default or runtime changes (Section 6)

The evidence chain traces correctly from checkpoint `648c439` through the accepted controller judgment sequence. The plan does not overreach the disposition scope.

### Q2: Is deterministic Chapter 2 gap rendering planning the best next gate given accepted evidence, or does the plan overstate the evidence?

**Verdict: BEST AVAILABLE, WITH CAVEAT**

The plan's core reasoning is sound:
- Checklist propagation is no-live proven (checkpoint `7fbc862`)
- Prompt strengthening was accepted (checkpoint `ee65f69`)
- Live repair still fails and worsened L1 from 1→2 (checkpoint `648c439`)
- Controller judgment explicitly says this is not an implementation acceptance failure

The plan correctly identifies that prompt-only convergence is unreliable for this sample and that stacking more prompt wording changes is not the primary route.

**Caveat**: The plan's hypothesis H2 (insufficient facts) is marked `POSSIBLE_NOT_PROVEN` but the planning consequence implicitly favors gap rendering for all three sub-cases (absent, insufficient, ignored). If the model is ignoring present facts, gap rendering would produce a misleading "evidence gap" when the real issue is model noncompliance. The plan should acknowledge this as a residual risk.

### Q3: Are rejected/deferred alternatives justified?

**Verdict: YES, WITH MINOR QUALIFICATIONS**

- **More no-live diagnostic evidence**: Rejected correctly. Existing diagnostics prove the mechanical path; metadata-only diagnostics cannot close the live semantic gap under current read boundaries.
- **Repair budget calibration**: Deferred correctly. The dependency reasoning (gap rendering → budget calibration) is sound, though the plan should explicitly scope the interaction.
- **Narrower code fix**: Rejected correctly. No specific minimal code defect identified after the accepted no-live implementation.
- **Blocked**: Rejected correctly, though the product direction (evidence gap > opaque failure) is implicit and should be confirmed by the controller.

### Q4: Does it avoid unauthorized implementation, live/provider commands, source-policy/fallback changes, provider defaults, repair budget, annual-period LLM route, Docling, PR/release/readiness claims?

**Verdict: YES**

The plan does not authorize:
- Implementation (explicit in Section 1, Section 6, Section 8)
- Live/provider commands (Section 6 non-goals)
- Source-policy/fallback changes (Section 1, Section 6)
- Provider defaults, repair budget changes (Section 6)
- Annual-period LLM route, Docling (not mentioned, correctly out of scope)
- PR/release/readiness claims (Section 6, Section 7 validation matrix entry 9)

Section 6 non-goals are comprehensive and aligned with the gate scope.

### Q5: Is the next-gate validation matrix code-generation-ready enough, or missing direct proof requirements?

**Verdict: PARTIALLY — NEEDS AMENDMENT**

The validation matrix (Section 7) specifies nine validation targets with required proof descriptions. However, several entries describe *what* must be proved without specifying *how*:

- "A no-live fake-writer or fixture case where Chapter 2 L1 cannot be numerically closed" — does not specify fixture location, mock mechanism or test function scope.
- "A concrete unanchored percentage or unclosed numerical claim must still fail L1" — does not specify test input string or fixture content.
- "Tests must cover both initial and repair attempts" — does not specify which existing test files must be extended.

The matrix is a validation *contract* but not an implementation specification. The future planning gate must convert each entry into concrete test specifications before implementation is authorized.

## 3. Findings

### Finding 1 — Gap rendering may mask model noncompliance (severity: medium)

Location: Section 4, Hypothesis H2

The plan disposes H2 as `POSSIBLE_NOT_PROVEN` but the planning consequence — "render an explicit Chapter 2 evidence gap/minimum-verification path" — implicitly assumes the "facts are absent" case. If facts are present but the model ignores them, gap rendering produces a misleading output.

**Recommendation**: The future implementation gate must either:
1. Scope gap rendering to the case where facts are genuinely insufficient (not present-but-ignored), or
2. Explicitly accept the ambiguity as a residual and document it in the gap output.

### Finding 2 — Validation matrix is a contract, not an implementation spec (severity: medium)

Location: Section 7

The nine validation targets are well-defined as acceptance criteria but lack implementation specificity. The future planning gate must produce:
- Exact fixture file locations or mock writer specifications
- Test function naming conventions and file scope
- Expected assertion patterns

**Recommendation**: The controller should require the future planning gate to produce a concrete validation specification before implementation is authorized.

### Finding 3 — Repair budget interaction is unscoped (severity: low)

Location: Section 6, "Deferred Gates" table

The plan defers repair budget calibration with the reasoning that it needs a separate gate "after deterministic fail-closed behavior is defined." This creates a dependency chain: gap rendering planning → gap rendering implementation → repair budget calibration. But the plan does not specify whether the gap rendering gate itself should decide whether repair budget interaction is in-scope.

**Recommendation**: The future gap rendering planning gate must explicitly decide whether repair budget interaction is in-scope or out-of-scope, rather than leaving it as an implicit assumption.

### Finding 4 — Product direction is implicit (severity: low)

Location: Section 5, candidate next gate table

The plan rejects "blocked pending user/product decision" with: "The project already has a consistent fail-closed principle that supports planning deterministic gap rendering without a separate product decision blocker." This is correct as a planning judgment, but the plan does not explicitly state what product decision it is making — namely, that an explicit evidence gap is a better user experience than an opaque `repair_budget_exhausted` failure.

**Recommendation**: The controller should confirm this product direction when accepting the plan.

### Finding 5 — L1 subcategory scope unclear (severity: low)

Location: Section 4, Hypothesis H1

The plan identifies `l1_numerical_closure` as the specific failure subcategory but does not explicitly address whether the proposed gap rendering approach applies only to numerical closure or to all L1 subcategories. If other L1 subcategories have different failure modes, the gap rendering approach may need to be subcategory-specific.

**Recommendation**: The future planning gate should specify whether gap rendering applies to all L1 subcategories or only to numerical closure.

## 4. Residuals

| Residual | Severity | Owner / Next handling |
|---|---|---|
| Gap rendering may mask model noncompliance if facts are present but ignored | medium | Future implementation gate must scope gap rendering or accept ambiguity |
| Validation matrix needs implementation-level specification | medium | Future planning gate must produce concrete test specs |
| Repair budget interaction with gap rendering is unscoped | low | Future gap rendering planning gate must decide in-scope/out-of-scope |
| Product direction (evidence gap > opaque failure) is implicit | low | Controller should confirm when accepting the plan |
| L1 subcategory scope for gap rendering is unspecified | low | Future planning gate should specify subcategory scope |

## 5. Findings Assessment Against Review Questions

| Review Question | Assessment |
|---|---|
| Q1: Control truth / EID / NOT_READY | PASS — fully respected |
| Q2: Best next gate / evidence overstatement | PASS_WITH_CAVEAT — best available, but H2 has a gap |
| Q3: Rejected/deferred alternatives justified | PASS_WITH_MINOR — all justified, product direction implicit |
| Q4: Avoids unauthorized actions | PASS — comprehensive non-goals |
| Q5: Validation matrix code-generation-ready | PASS_WITH_FINDINGS — contract-level, needs implementation spec |

## 6. Recommendation for Controller

Accept with the following controller amendments:

1. **Amendment 1**: Add a residual acknowledging that gap rendering may not be the correct product response if the model is ignoring present facts. The future implementation gate must either scope gap rendering to genuinely insufficient facts or explicitly accept the ambiguity.

2. **Amendment 2**: Record that the future gap rendering planning gate must produce a concrete validation specification (test function names, fixture locations, expected assertions) before implementation is authorized.

3. **Amendment 3**: Record that the future gap rendering planning gate must explicitly decide whether repair budget interaction is in-scope or out-of-scope.

4. **Confirmation**: Confirm the product direction that an explicit evidence gap is a better user experience than an opaque `repair_budget_exhausted` failure.

5. **Amendment 5**: Record that the future gap rendering planning gate should specify whether the approach applies to all L1 subcategories or only to numerical closure.

With these amendments, the plan is suitable as the disposition basis for the next gate.

---

*Review artifact written to: `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-review-mimo-20260614.md`*
