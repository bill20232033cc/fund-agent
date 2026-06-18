# Docling Baseline Qualification Plan Review - DS

Date: 2026-06-15

Gate: `Docling Baseline Qualification Planning Gate`

Role: DS plan review worker only

Verdict: `PASS_WITH_NONBLOCKING_FINDINGS`

## 1. Reviewed Target And Scope

- **Target**: `docs/reviews/docling-baseline-qualification-plan-20260615.md`
- **Plan scope**: Define evidence sequence (Gates A-F) to decide whether Docling can qualify as a production baseline candidate for annual-report document representation.
- **Plan output**: One planning artifact with sample matrix, gate definitions, pass/fail thresholds, stop conditions, verdict criteria, and deferred residuals.
- **Plan boundary**: Planning-only; no source/test/runtime/control/design edits; no live/network/EID/FDR/PDF download/provider/LLM; no production baseline claim; NOT_READY preserved.

## 2. Sources Reviewed

- Target plan: `docs/reviews/docling-baseline-qualification-plan-20260615.md`
- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md` (front matter and current gate)
- `docs/design.md` (Docling/FundDocumentRepository/EvidenceAnchor/EID lines via grep)
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md`
- `docs/reviews/bounded-same-report-eid-html-render-discovery-controller-judgment-20260615.md`
- Validation: `git diff --check` passed.

## 3. Assumptions Tested

| # | Plan assumption | Verdict |
|---|-----------------|---------|
| A1 | Six-sample matrix can be acquired through EID-only paths without non-EID fallback. | Partially supported — S1 has accepted local artifact; S2-S6 acquisition status is unclassified. |
| A2 | pdfplumber full representation exports exist or can be produced for all six samples to serve as Gate B/D baselines. | Unsupported — only S1 has accepted pdfplumber full JSON; plan does not address producing pdfplumber baselines for S2-S6. |
| A3 | Accepted reviewed/golden facts exist or will exist for S2-S6 to serve as Gate D field correctness references. | Unsupported — current accepted golden/reviewed facts cover only `004393 / 2025`; plan does not explain how references are established for the other five samples. |
| A4 | EID HTML render candidate representations will be available for comparison across S2-S6 where Gate D references them. | Unsupported — only S1 has accepted EID HTML render JSON; plan says "where available" but doesn't classify expected availability. |
| A5 | Docling conversion can run socket-blocked for all six samples without model download. | Reasonable for S1 (proven); untested for S2-S6 but same artifact configuration should apply. |
| A6 | Field families listed in Gate D are extractable from Docling output for all six fund profiles. | Reasonable given Docling's full-document coverage on S1, but normalization for bond/QDII/ETF-linked profiles is unproven. |
| A7 | Candidate internals under `fund_agent/fund/documents/candidates/` are sufficient for Gate C EvidenceAnchor mapping. | Supported by accepted mapping/normalization implementation judgment. |
| A8 | Controller will authorize sample acquisition and evidence execution gates when needed. | Reasonable — plan explicitly defers acquisition to controller-approved gates. |

## 4. Findings

### DS-F1-未修复-中-field correctness reference facts undefined for S2-S6

- **位置**: Section 6 Gate D inputs and pass thresholds; Section 4 accepted evidence facts; Section 5 sample matrix
- **问题类型**: 契约缺失 / open question 未收敛
- **当前写法**: Gate D requires "High-priority field correctness versus accepted reviewed/golden facts: >= 98% exact/normalized match, 0 critical mismatch" and "Medium-priority field correctness: >= 95% exact/normalized match." Inputs list "Current extractor/golden reviewed field sets where already accepted." Section 4 confirms only single-sample `004393 / 2025` evidence is accepted.
- **反例/失败场景**: Evidence worker arrives at Gate D and discovers that "accepted reviewed/golden facts" exist only for S1. The worker cannot execute field correctness comparison for S2-S6 without inventing reference facts. If the worker treats pdfplumber output as reference, it violates the plan's own rule that "Route agreement can prioritize manual review, but cannot prove field correctness." If the worker requires manual review, no budget or process is defined.
- **为什么有问题**: The plan's multi-sample field correctness gate is untestable for 5 of 6 samples under current accepted evidence. This creates a hidden prerequisite (establish golden/reviewed facts for S2-S6) that Gate D consumes but no preceding gate produces. The plan's own residual table (Section 12) acknowledges "Field correctness remains unproven for Docling across samples" but does not address the prerequisite reference data problem.
- **直接证据**:
  - Plan Section 4: only `004393 / 2025` evidence is accepted as current fact.
  - Plan Section 6 Gate D: pass thresholds reference "accepted reviewed/golden facts" without defining how they are established for S2-S6.
  - Plan Section 7 comparison axes: "field correctness: only against accepted reviewed/golden facts and same-report manual evidence, not route agreement alone." This correctly rules out route-agreement-as-truth but does not explain the manual evidence process.
  - Current accepted implementation facts: only `004393 / 2025` has same-year reviewed golden content (seven tracked rows); S2-S6 have no accepted golden/reviewed facts.
- **影响**: Implementation agent at Gate D either stalls (waiting for undefined reference facts), invents references from route agreement (violating plan constraints), or executes a hollow comparison that cannot distinguish Docling errors from reference gaps. The multi-sample claim collapses to single-sample if Gate D can only be executed for S1.
- **建议改法和验证点**:
  1. Add an explicit prerequisite gate or sub-gate between C and D that defines how field correctness reference facts are established for S2-S6 (options: same-report manual excerpt review, cross-route consensus with manual adjudication of disagreements, or accept that S2-S6 field correctness is limited to identity + structural coverage only).
  2. Clarify whether "accepted reviewed/golden facts" for S2-S6 means: (a) same-year manual review of specific field families, (b) cross-route agreement after manual adjudication, or (c) deferred to a future gate with Gate D scoped to identity/structural correctness only for non-S1 samples.
  3. If manual review is the intended path, add explicit scope (which field families, how many fields per sample) and stop conditions (e.g., "manual review budget exhausted before threshold sample coverage").
- **修复风险（中）**: Requires scoping a prerequisite gate or narrowing Gate D's field correctness scope for S2-S6.
- **严重程度（中）**: Does not block plan acceptance as a planning artifact, but blocks evidence execution unless resolved before Gate D.

### DS-F2-未修复-中-pdfplumber baseline reference undefined for S2-S6

- **位置**: Section 6 Gate B inputs and pass thresholds
- **问题类型**: 契约缺失 / open question 未收敛
- **当前写法**: Gate B requires "Page count parity with pdfplumber for every PDF-backed sample: 100%" and "Table coverage versus pdfplumber: Docling table count within 0.80x to 1.30x." Inputs list "Current pdfplumber full representation exports for the same samples."
- **反例/失败场景**: S2-S6 do not have accepted pdfplumber full representation exports. The evidence worker either cannot compute page/table parity for 5 of 6 samples, or must run pdfplumber conversion during Gate B, which the plan does not authorize as a Gate B command.
- **为什么有问题**: The plan assumes pdfplumber reference data exists but only S1 has it. Producing pdfplumber full representation JSONs for S2-S6 is non-trivial (requires PDF acquisition, pdfplumber conversion, representation export) and is not scoped in any gate.
- **直接证据**:
  - Plan Section 4: accepted same-report representation JSON exists for Docling and pdfplumber for `004393 / 2025` only.
  - Plan Section 6 Gate B inputs: "Current pdfplumber full representation exports for the same samples" — no evidence these exist for S2-S6.
  - Current accepted evidence facts: pdfplumber full JSON exists only for S1.
- **影响**: Gate B coverage metrics are computable only for S1, undermining the multi-sample claim. The evidence worker may skip pdfplumber comparison and use Docling-only metrics, which cannot prove coverage relative to current production parser.
- **建议改法和验证点**:
  1. Add pdfplumber representation export to the sample acquisition or Gate A scope as a prerequisite artifact, or
  2. Narrow Gate B pass thresholds to allow Docling-only structural coverage metrics for samples without pdfplumber reference, while keeping pdfplumber comparison mandatory only for S1, or
  3. Add an explicit prerequisite gate to produce pdfplumber full representation JSONs for S2-S6 before Gate B.
- **修复风险（中）**: Requires scoping pdfplumber exports or adjusting Gate B comparison design.
- **严重程度（中）**: Does not block plan acceptance but blocks faithful Gate B execution.

### DS-F3-未修复-低-Gate A auxiliary verdict escape hatch undefined in verdict criteria

- **位置**: Section 6 Gate A pass thresholds; Section 10 verdict criteria
- **问题类型**: 契约缺失
- **当前写法**: Gate A pass thresholds allow "up to 1 profile-specific fail-closed conversion failure can still allow auxiliary verdict if failure taxonomy is complete." Section 10 defines four verdicts: `ELIGIBLE_AS_BASELINE_CANDIDATE`, `ELIGIBLE_AS_HYBRID_PRIMARY`, `REMAINS_AUXILIARY_CANDIDATE`, `REJECTED_AS_BASELINE_CANDIDATE`. None explicitly maps to the "auxiliary verdict" mentioned in Gate A.
- **反例/失败场景**: Exactly one sample fails Gate A conversion with a complete failure taxonomy. The evidence worker does not know which Section 10 verdict to recommend. `REMAINS_AUXILIARY_CANDIDATE` is the closest but its criteria require Docling to "miss one or more baseline thresholds" — Gate A's auxiliary escape hatch doesn't specify whether a single conversion failure counts as "missing baseline thresholds."
- **为什么有问题**: The plan introduces a verdict outcome in Gate A that has no corresponding entry in the verdict criteria section, creating ambiguity for the evidence and controller workers at Gate F.
- **直接证据**:
  - Plan Section 6 Gate A: "up to 1 profile-specific fail-closed conversion failure can still allow auxiliary verdict."
  - Plan Section 10: no verdict explicitly maps to "auxiliary verdict" as a Gate A outcome.
- **影响**: Evidence worker may misclassify the verdict or stall at Gate F waiting for controller clarification.
- **建议改法和验证点**: Either: (a) add an explicit Gate A sub-verdict that maps to one of the four Section 10 verdicts, or (b) clarify that "auxiliary verdict" means the Gate A evidence artifact records a `conversion_failure` residual without blocking baseline candidacy, and the final disposition is resolved at Gate F, or (c) remove the auxiliary escape hatch and require 100% conversion success for baseline candidate eligibility.
- **修复风险（低）**: Text clarification in Section 6 or Section 10.
- **严重程度（低）**: Does not block plan logic but creates ambiguity at verdict time.

### DS-F4-未修复-低-table count threshold range lacks justification

- **位置**: Section 6 Gate B pass thresholds
- **问题类型**: 不可直接实施
- **当前写法**: "Table coverage versus pdfplumber: Docling table count within 0.80x to 1.30x, or differences classified by layout/data-table taxonomy."
- **反例/失败场景**: For S1 (95 Docling tables), the acceptable range is 76-124 tables. The plan does not explain why a 30% overcount (potentially 29 extra non-table blocks classified as tables) is acceptable as "coverage" evidence. If Docling produces 124 "tables" and pdfplumber produces 95, the difference of 29 could mask systematic table hallucination or layout-table misclassification that the taxonomy classification is supposed to catch but may not.
- **为什么有问题**: A 0.80-1.30 range is broad enough that it may pass samples with material table structure problems. The "layout/data-table taxonomy" classification is mentioned as an alternative but the taxonomy itself is not defined in the plan.
- **直接证据**: Plan Section 6 Gate B pass thresholds; no justification for the 0.80-1.30 range.
- **影响**: Evidence worker may accept samples with significant table structure problems if the count falls within range, and the undefined taxonomy doesn't catch them.
- **建议改法和验证点**: Either: (a) tighten the range (e.g., 0.85-1.20) with justification from S1 evidence, or (b) require the layout/data-table taxonomy to be defined and validated before Gate B execution, or (c) add a per-sample table count difference cap (e.g., max 15 table count difference regardless of ratio).
- **修复风险（低）**: Threshold tuning or taxonomy scoping.
- **严重程度（低）**: The range is a judgment call; S1 evidence (95 tables) provides a reasonable anchor but the upper bound is generous.

### DS-F5-未修复-低-EID HTML render availability for S2-S6 unclassified

- **位置**: Section 6 Gate D inputs; Section 7 comparison design
- **问题类型**: open question 未收敛
- **当前写法**: Gate D lists "EID HTML render candidate representations where available" as input. Section 7 comparison design lists EID HTML render's role. The plan does not state expected EID HTML render availability for S2-S6.
- **反例/失败场景**: S2-S6 may or may not have EID HTML render artifacts. If they don't, Gate D's tri-route comparison degrades to two-route (Docling vs pdfplumber) for most samples, weakening the comparison design. If the evidence worker attempts to acquire EID HTML render during Gate D, they violate the plan's prohibition on live/network commands.
- **为什么有问题**: The plan's comparison design assumes tri-route comparison as an ideal but doesn't classify expected availability. The bounded discovery gate proved EID HTML render exists for `004393 / 2025` but didn't establish whether the same endpoint serves S2-S6.
- **直接证据**:
  - Plan Section 4: EID HTML render accepted only for `004393 / 2025`.
  - Plan Section 6 Gate D: "where available" is a hedge without classification.
  - Bounded discovery controller judgment: scope was explicitly bounded to `004393 / 2025`.
- **影响**: Gate D comparison may be two-route for 5/6 samples, reducing the evidence strength for hybrid disposition. The plan does not classify this as an expected limitation.
- **建议改法和验证点**: Add explicit expected EID HTML render availability classification for S2-S6 (e.g., "expected unavailable pending separate discovery gate" or "expected available based on EID search API coverage") and state the degraded comparison design.
- **修复风险（低）**: Text clarification.
- **严重程度（低）**: Does not block plan execution but affects Gate D evidence quality expectations.

## 5. Plan Strengths

The plan demonstrates strong structural discipline:

1. **Clear candidate vs production baseline distinction** (Section 2): The plan explicitly prevents overclaim. All verdicts carry `NOT_READY`.
2. **Forbidden claims are exhaustive and specific** (Section 3): Source truth, field correctness, raw XML, taxonomy, readiness, and parser replacement overclaims are all explicitly blocked.
3. **EID single-source policy preserved**: No non-EID fallback anywhere; expansion rule requires controller-approved EID-only acquisition.
4. **FundDocumentRepository boundary preserved**: Direct parser/PDF/Docling access by Service/UI/Host/renderer/quality-gate is consistently blocked.
5. **Multi-sample requirement** (Section 5): Six samples across fund profiles (active, enhanced index, bond, QDII, ETF-linked) is a genuine improvement over the single-sample `004393 / 2025` evidence.
6. **Stop conditions per gate**: Each gate has explicit stop conditions that fail closed on boundary violations, network escapes, identity mismatches, and overclaims.
7. **Failure taxonomy** (Section 8): Closed categories with clear baseline impact, preventing ad-hoc failure classification.
8. **EvidenceAnchor schema preservation**: No public schema change authorized; candidate metadata stays in `note` fields.

## 6. Open Questions

| # | Question | Relevance |
|---|----------|-----------|
| Q1 | What is the expected timeline or budget for manual field correctness reference review if S2-S6 require it for Gate D? | Affects Gate D feasibility. |
| Q2 | Does the pdfplumber full representation export script used for S1 work for S2-S6 without modification? | Affects Gate B prerequisite. |
| Q3 | Will the same `artifacts_path` and Docling configuration used for S1 work for S2-S6 (different PDF structures, potentially different page counts and layouts)? | Affects Gate A feasibility. |
| Q4 | Should the "auxiliary verdict" escape hatch in Gate A be clarified now or deferred to the evidence worker's Gate F controller judgment? | Affects verdict consistency. |

## 7. Residual Risks

| Residual risk | Likelihood | Impact | Suggested tracking |
|---------------|-----------|--------|-------------------|
| S2-S6 sample acquisition blocked by EID unavailability for specific fund/year combinations, triggering expansion rule and delaying all downstream gates. | Medium | High — blocks entire qualification sequence. | Track in recommended next gate (Sample Matrix Acquisition Planning Gate). |
| Docling conversion produces materially different output quality for bond/QDII/ETF-linked reports compared to active equity (S1), revealing profile-specific weaknesses not visible in single-sample evidence. | Medium | Medium — may force hybrid or auxiliary disposition even if all gates pass thresholds. | Track as a Gate B/D observation; classify by profile in evidence artifacts. |
| Field correctness comparison for S5 (QDII) and S6 (ETF-linked) generates high mismatch rates because Docling's representation of overseas holdings or target-fund holdings differs structurally from pdfplumber extraction, not because Docling is wrong. | Medium | Medium — may incorrectly suggest Docling quality problems. | Require mismatch classification by root cause (representation difference vs extraction error) in Gate D. |
| Normalization rules defined in mapping/normalization plan fail on bond fund numeric formats or QDII multi-currency values in S4/S5, causing spurious field mismatches. | Low | Medium — affects Gate D pass rates. | Covered by normalization failure taxonomy; ensure bond/QDII numeric formats are in test fixtures. |

## 8. Final Plan Review Conclusion

**Verdict: `PASS_WITH_NONBLOCKING_FINDINGS`**

The plan is structurally sound, disciplined about boundaries, and correctly scoped to baseline candidate qualification only. The multi-sample matrix, gate sequence, pass/fail thresholds, stop conditions, and verdict criteria provide a testable framework that an implementation agent can follow.

The five findings (DS-F1 through DS-F5) are material but non-blocking for plan acceptance as a planning artifact. They must be resolved before or during evidence execution:

- **DS-F1** (field correctness reference facts for S2-S6) and **DS-F2** (pdfplumber baseline for S2-S6) are the most consequential — they affect whether Gates B and D can be faithfully executed for the full sample matrix.
- **DS-F3** (auxiliary verdict mapping) is a text clarification.
- **DS-F4** (table count threshold) and **DS-F5** (EID HTML render availability) are threshold/scoping refinements.

All findings can be addressed through plan amendments without restructuring the gate sequence or verdict framework.

## 9. Recommended Controller Disposition

**`ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_NEXT_GATE_NOT_READY`**

Recommended binding amendments:

1. **Define field correctness reference establishment for S2-S6** (DS-F1): Add a prerequisite sub-gate or explicit scope limitation to Gate D that either (a) defines how reference facts are established for non-S1 samples, or (b) limits field correctness comparison to identity/structural correctness for samples without accepted golden facts, with full field comparison deferred.
2. **Define pdfplumber baseline production for S2-S6** (DS-F2): Either (a) add pdfplumber representation export as a Gate A or prerequisite artifact, or (b) allow Gate B to use Docling-only structural coverage metrics where pdfplumber reference is unavailable.
3. **Clarify auxiliary verdict mapping** (DS-F3): Map the Gate A "auxiliary verdict" escape hatch to a specific Section 10 verdict or remove it.
4. **Preserve all existing boundary constraints, forbidden claims, EID single-source policy, FundDocumentRepository boundary, and NOT_READY.**

## 10. Validation

```text
git diff --check: passed
```

## 11. Reviewer Self-Check

- [x] Reviewed target, scope, source of truth and assumptions tested are stated.
- [x] Findings are evidence-based, adversarial, actionable; no style/nit/speculation.
- [x] Open questions, residual risks, and tracking destination are separate from findings.
- [x] Conclusion is `PASS_WITH_NONBLOCKING_FINDINGS`.
- [x] Output path matches required artifact path.
