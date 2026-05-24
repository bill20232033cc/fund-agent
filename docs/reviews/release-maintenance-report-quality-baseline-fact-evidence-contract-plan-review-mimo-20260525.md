# Plan Review: Report-Quality Baseline / Fact-Evidence Contract Plan

> Date: 2026-05-25
> Reviewer: AgentMiMo
> Artifact reviewed: `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md`
> Gate: `release-maintenance report-quality baseline / Fact-Evidence contract candidate selection / plan-review`
> Current phase: release maintenance

## Verdict

**PASS_WITH_FINDINGS**

The plan is well-structured, correctly positioned at the declared gate, and respects all hard constraints. It properly references the three accepted upstream artifacts, preserves the four-layer boundary, and does not introduce renderer, quality gate, Host/Agent, or Dayu runtime changes. The scoring dimensions faithfully cite §5.4.1, the Fact/Evidence contract faithfully cites §5.4.2, and the methodology matrix constraints faithfully cite §5.4.3 including fund-type lens priority, evidence hierarchy, and missing-fact degradation semantics. Findings are non-blocking documentation refinements.

## Scope Check

| Constraint | Status | Evidence |
|---|---|---|
| No renderer changes | PASS | §Non-Goals explicitly states "Do not change renderer output or current v0 8-chapter structure." |
| No quality gate changes | PASS | §Non-Goals explicitly states "Do not change current FQ0-FQ6 quality gate behavior." |
| No Host/Agent package creation | PASS | §Non-Goals explicitly states "Do not create `fund_agent/host` or `fund_agent/agent`." |
| No Dayu runtime introduction | PASS | §Non-Goals explicitly states "Do not introduce `dayu.host`, `dayu.engine`, external `dayu-agent` runtime, queue, model dependency, prompt registry, or tool loop." |
| Four-layer boundary preserved | PASS | §Current Architecture Boundary correctly describes `UI -> Service -> Host -> Agent` with explicit Host/Agent gating. |
| Future Host = `dayu.host` | PASS | §Current Architecture Boundary line 36-37: "Host is not created in this gate. If future session / run lifecycle...that must be a separate Host gate using `dayu.host`." |
| Future Agent = `dayu.engine` | PASS | §Current Architecture Boundary line 38: "If future tool loop, runner, ToolRegistry, ToolTrace, or context budget is required, that must be a separate Agent gate using `dayu.engine`." |
| No `extra_payload` for business params | PASS | §Current Architecture Boundary line 39, §Slice 3 ReportEvidenceBundle top-level, §Plan Review Checklist line 359 all enforce this. |
| Fact/Evidence via `FundDocumentRepository` only | PASS | §Slice 1 FundDocumentRepository Boundary and §Slice 3 `facts` source boundary both enforce this. |

## Truth Source Alignment

| Source | Alignment | Notes |
|---|---|---|
| `AGENTS.md` | PASS | Source failure taxonomy (§Slice 1) matches exactly: fallback for `not_found`/`unavailable`; fail-closed for `schema_drift`/`identity_mismatch`/`integrity_error`. Fund-type-first principle enforced. Evidence traceability required. |
| `docs/design.md` §5.4 | PASS | Plan correctly cites the "score first, then decide data vs template" sequence from the accepted chapter-audit design implementation. |
| `docs/design.md` §5.4.1 | PASS | All 7 scoring dimensions from §5.4.1 are present: fact_coverage, extraction_correctness, evidence_traceability, chapter_contract_completeness, final_judgment_consistency, investment_advice_boundary, readability_actionability. |
| `docs/design.md` §5.4.2 | PASS | Fact/Evidence contract covers all 5 input categories: facts, derived_calculations, evidence_anchors, data_gaps, quality_context. |
| `docs/design.md` §5.4.3 | PASS | §Slice 2 Methodology Matrix Constraints correctly cites: Morningstar as coverage lenses (not ratings), 有知有行 as behavior-safety lenses, fund-type priority changing scoring denominator, CHAPTER_CONTRACT / preferred_lens / ITEM_RULE as chapter obligations, evidence source hierarchy, and missing-fact degradation to `未披露`/`数据不足`/`下一步最小验证问题`. |
| Accepted artifact 1: chapter-audit pipeline design | PASS | Plan follows the accepted "measurable baseline first" principle. |
| Accepted artifact 2: methodology coverage matrix plan | PASS | Scoring schema explicitly requires §5.4.3 citation per dimension. |
| Accepted artifact 3: methodology coverage matrix implementation | PASS | Current 8-chapter boundary preserved; 0-10 mapping deferred. |

## Product Methodology Coverage

The plan adequately covers the product methodology requirements for personal investor decision safety:

1. **Morningstar dimensions**: Referenced as coverage lenses only (People, Process, Parent, Price, Performance). No medal/star output. PASS.

2. **有知有行 dimensions**: R=A+B-C, fund-type-first, knowledge/emotion/willingness, four-money suitability, thermometer/valuation-state discipline, next minimal validation question. All present in scoring dimensions. PASS.

3. **Fund type lens priority**: Corpus selection requires all 6 fund types (active, index, enhanced_index, bond, qdii, fof). Scoring denominator changes by fund type. PASS.

4. **CHAPTER_CONTRACT / evidence hierarchy / missing-fact degradation**: All explicitly referenced in §Slice 2 Methodology Matrix Constraints. PASS.

## Findings

### F-1: Manual Review State Machine Lacks Transition Conditions (Severity: 3)

**Location**: §Slice 1, "Manual Review State" table (lines 93-103)

**Issue**: The 6 review states (`candidate` → `repository_verified` → `fact_prefill_generated` → `fact_prefill_reviewed` → `scoring_ready` → `accepted_baseline`) define allowed next actions but not the transition trigger conditions. Specifically:
- What automated process transitions `repository_verified` to `fact_prefill_generated`? Is this a script run, a Service call, or a manual step?
- What constitutes "human accepted or corrected" for `fact_prefill_reviewed`? A signed-off Markdown table? A JSON fixture with reviewer annotations?
- Who decides `accepted_baseline`? A single reviewer or controller approval?

**Impact**: Without explicit transition triggers, the review state could stall or be incorrectly advanced, especially when manual review becomes the bottleneck (acknowledged in §Residual Risks).

**Recommendation**: Add a transition table with: trigger (automated/manual), actor (script/reviewer/controller), and minimum evidence required. This is non-blocking because the state definitions themselves are correct, and the transition details can be refined during S0 implementation.

**Blocking**: No.

### F-2: FOF Corpus Handling Ambiguity Between Open Questions and Selection Table (Severity: 3)

**Location**: §Slice 1 "Required Coverage" table (line 58) vs §Open Questions #1 (line 383)

**Issue**: The corpus table says FOF is "0 to 1 in first pass, required by second pass" and the fallback rule says "If QDII or FOF annual reports cannot be repository-verified in the first pass, the plan must record a `data_gap`." Meanwhile, Open Question #1 asks whether FOF should be required in S0. These are internally consistent but leave the implementer without a default resolution.

**Impact**: Low. The plan correctly identifies this as an open question and provides a reasonable fallback (keep at 5-6 cases with explicit `data_gap`). The ambiguity is intentional.

**Recommendation**: No change needed for plan review. The open question is appropriately flagged for controller resolution during S0.

**Blocking**: No.

### F-3: Scoring Scale N/A Semantics Not Fully Defined (Severity: 3)

**Location**: §Slice 2 "Scoring Scale" table (lines 163-174)

**Issue**: The scale defines `N/A` as "Dimension is not applicable for this fund type / chapter, with reason" but does not specify how N/A interacts with weighted totals or issue counts. For example:
- If People dimension is N/A for `index_fund`, does it reduce the denominator in a weighted total?
- Does a chapter with all dimensions N/A count as "passing" or "skipped"?

The plan says "Weighted total is optional in the first implementation. The mandatory output is issue localization and next-gate recommendation," which defers this correctly. But the N/A semantic should be explicit even in the observational phase to prevent misinterpretation of issue counts.

**Impact**: Low. The plan correctly makes weighted totals optional. The N/A semantic only matters when aggregation is attempted.

**Recommendation**: Add a note: "N/A dimensions must be excluded from any denominator; a chapter with all N/A dimensions is `skipped`, not `passing`." Non-blocking.

**Blocking**: No.

### F-4: Tie-Breaker Rule Could Cite Accepted Design Principle (Severity: 4)

**Location**: §Slice 4, "Tie-breaker" (line 325)

**Issue**: The tie-breaker "data-source / extraction correctness precedes template writing" is correct and aligns with the accepted chapter-audit design principle ("better report quality comes from clean, structured, low-noise facts and measurable evaluation, not from giving a model more raw documents or polishing prose blindly"). The plan does not explicitly cite this source.

**Impact**: Minimal. The principle is correctly applied.

**Recommendation**: Optionally add a citation to the chapter-audit design implementation artifact. Non-blocking.

**Blocking**: No.

### F-5: Evidence Anchor `source_strength` Missing `third_party_reference` vs `derived` Distinction Note (Severity: 4)

**Location**: §Slice 3, `evidence_anchors` table (line 269)

**Issue**: The `source_strength` field lists `fund_disclosure, official_reference, manager_statement, third_party_reference, derived`. This matches the evidence hierarchy in §5.4.3. However, `third_party_reference` and `derived` serve very different purposes (external comparison vs internal calculation), and a brief note distinguishing them would improve clarity.

**Impact**: Minimal. The field values are correct.

**Recommendation**: Optionally add a parenthetical: "`third_party_reference` for external comparison only; `derived` for internal calculation with listed input fact ids." Non-blocking.

**Blocking**: No.

### F-6: Fact/Evidence Contract "Top-Level Shape" Does Not Clarify Design-vs-Implementation Boundary (Severity: 4)

**Location**: §Slice 3, "Top-Level Shape" (lines 194-209)

**Issue**: The `ReportEvidenceBundle` top-level shape uses pseudo-code notation (`bundle_id`, `corpus_id`, etc.) without stating whether this is a design sketch for future dataclass definition or a specification that S2 implementation must follow literally. The §Executable Next Gate Proposal says S2 is "Define the typed contract in code only after S0/S1 plan review passes," confirming this is design-level.

**Impact**: Minimal. The intent is clear from context.

**Recommendation**: Optionally add a header note: "Design-level shape; concrete Python dataclass definition deferred to S2 implementation gate." Non-blocking.

**Blocking**: No.

## Methodology Coverage Assessment

The scoring dimensions serve personal investor decision safety through the following mapping:

| Scoring Dimension | Decision Safety Served | Evidence |
|---|---|---|
| `fact_coverage` | Ensures required facts exist before any judgment is made | Cites §5.4.3 CHAPTER_CONTRACT and fund-type lens |
| `extraction_correctness` | Prevents wrong values from driving decisions | Locatable to field_path and evidence_anchor_id |
| `evidence_traceability` | Every judgment must be traceable to source | Cites §5.4.3 evidence hierarchy |
| `chapter_contract_completeness` | Each chapter must answer its decision question | Cites §5.4.3 CHAPTER_CONTRACT |
| `final_judgment_consistency` | Final judgment must not ignore gaps or context | Cites §5.4.3 assembly audit |
| `investment_advice_boundary` | Prevents buy/sell advice, return prediction | Directly serves investor safety |
| `readability_actionability` | Reader gets next minimal validation question | Cites §5.4.3 有知有行 behavior lens |

The missing-fact degradation semantics (`未披露`, `数据不足`, `下一步最小验证问题`) are correctly enforced across scoring dimensions and the Fact/Evidence contract's `data_gaps` section.

## Baseline Corpus Representativeness

The 6-8 fund-year corpus with 6 required fund-type slots is appropriately broad for a first baseline:

- `active_fund` (1-2): Tests the most complex lens (People/Process/Parent).
- `index_fund` (1): Tests tracking/fee/benchmark lens.
- `enhanced_index` (1): Tests structural vs stage alpha separation.
- `bond_fund` (1): Tests risk/credit/duration lens.
- `qdii_fund` (1): Tests cross-border/currency lens.
- `fof_fund` (0-1, required by second pass): Tests allocator/dual-fee lens.

The identity verification requirements and repository boundary enforcement are appropriate. The `data_gap` fallback for unverifiable QDII/FOF is correct.

## Residual Risks Acknowledged

The plan's residual risks are honest and appropriate:
- Small corpus overfitting risk (acknowledged, mitigated by "baseline observability" framing).
- Manual review bottleneck (acknowledged, mitigated by state machine).
- Source gaps may be more urgent than writing quality (acknowledged, intentionally prioritized).
- LLM audit/repair blocked until separate Host/Agent gate (correct).

## Summary

The plan is a well-designed next step for report-quality observability. It correctly follows the accepted "measurable baseline first" principle from the chapter-audit design, properly cites all three accepted upstream artifacts, and maintains all hard constraints (four-layer boundary, no renderer/quality-gate/Host/Agent/Dayu changes, explicit parameters, FundDocumentRepository boundary). The 6 findings are all severity 3-4 (non-blocking documentation refinements) and do not affect the plan's executability.

Recommended resolution: address F-1 (transition conditions) and F-3 (N/A semantics) as part of S0 implementation refinement; F-2 is appropriately an open question for controller resolution; F-4, F-5, F-6 are optional polish.
