# MVP fund report template typed contract redesign design — review (AgentDS)

## Reviewer Self-Check

- Role: AgentDS as independent review worker, not controller.
- Gate: `MVP fund report template typed contract redesign gate`, classification `heavy`.
- Review lens: adversarial plan/design review.
- Review target: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md`
- Read set satisfied: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/fund-analysis-template-draft.md`, `docs/superpowers/specs/2026-06-02-template-redesign-from-first-principles.md`, target design, Slice 1 controller judgment after provider restore, Agent-engine controller judgment, `summary.json`.
- Actions taken: read all required sources, cross-checked evidence chains, boundary consistency, and non-goal compliance.
- Actions intentionally not taken: no code, no template truth replacement, no `contracts.py`/auditor/provider budget/score-loop changes, no commit/push/PR, no edit to design artifact or truth docs.

---

## Overall Assessment

**Verdict: pass-with-risks.** The design's seven decisions are well-scoped, evidence-backed where evidence exists, and correctly defer or reject what same-source evidence cannot yet support. No blocking findings. Eight residual risks and four open questions remain for the controller to resolve before or during the next gate.

The design's strongest attribute is its discipline around what must NOT enter accepted future design: it correctly refuses 0+9 structure, timeout-improvement percentages, migration timelines, and 5Y raw ingestion. This aligns precisely with the Slice 1 controller judgment (Ch2/Ch6 deferred, Ch3 only) and the Agent-engine controller judgment (separate gates, no bundling).

---

## Finding 1: assertion polarity robustness in Chinese — unresolved residual, handoff risk

**Severity:** MEDIUM (non-blocking for design acceptance; must be resolved before any implementation gate that touches `MustNotCoverClause`)

**Evidence:**

- Decision 3 proposes `polarity: positive | negative | quasi_positive | unsupported_causal | any` as the forbidden assertion taxonomy.
- The external first-principles spec §1.2 F-1 identifies the root cause: `_must_not_cover_phrases` does pure lexical matching without understanding Chinese assertion polarity or evidence conditions.
- The design's own residual risks section asks: "How to represent assertion polarity robustly in Chinese text without falling back to brittle phrase matching."
- The design defers "exact enum names and schema implementation form" in the Deferred section.

**Impact:** A future implementation gate that accepts `MustNotCoverClause` with `polarity` as a typed field but cannot implement a robust Chinese polarity detector will either fall back to the same brittle phrase matching (defeating the purpose) or require an LLM-based polarity classifier (introducing a new failure mode). The design correctly identifies this as an open question but doesn't constrain how it must be resolved.

**Suggested fix:** Add an explicit handoff constraint to Decision 3: "Before any implementation gate creates `MustNotCoverClause` with polarity fields, a separate calibration or feasibility gate must demonstrate that quasi_positive / unsupported_causal assertions in Chinese can be detected with acceptable false-positive and false-negative rates, using either deterministic heuristics or a bounded LLM classifier with typed output contract."

**Fix risk:** LOW. This only adds a precondition, doesn't change the accepted design.

---

## Finding 2: typed subcontracts for Ch2 — concept is ambiguous, risks being misread as accepted split

**Severity:** LOW (clarification only; does not block design acceptance)

**Evidence:**

- Decision 6 says: "Accept only the narrower future-design requirement that old Chapter 2 should be representable as typed subcontracts for performance, attribution, and cost, whether or not those subcontracts later become separate chapters."
- The future contract shape lists `performance_subcontract`, `attribution_subcontract`, `cost_subcontract` but doesn't specify whether these are: (a) sub-fields within a single Ch2 `ChapterContract`, (b) separate `ChapterContract` instances that share `chapter_id=2`, or (c) an intermediate typed structure that isn't a `ChapterContract` at all.
- The current `ChapterContract` schema (Decision 1) has no `subcontracts` field.

**Impact:** A future implementer reading this as accepted design could reasonably interpret it as authorization to create three separate `ChapterContract` entries (effectively implementing the split that was deferred), or as authorization to add a `subcontracts` field to `ChapterContract` without a separate design gate.

**Suggested fix:** Add one sentence to Decision 6: "Typed subcontracts are internal organizational units within a single Ch2 `ChapterContract`; they must not have independent `chapter_id` values, must not appear in the chapter matrix, and must not change the public 0-7 chapter count."

**Fix risk:** LOW. Narrows scope without changing intent.

---

## Finding 3: audit_focus constraint interacts with evidence-conditional must_not_cover — unaddressed coupling

**Severity:** MEDIUM (design gap; controller should confirm intended interaction before handoff)

**Evidence:**

- Decision 7 says: "Programmatic C2, required markers, anchor validation, missing/degrade policy, forbidden investment advice, and implemented L1/R rules stay always-on. Any future change that lets `audit_focus` disable a blocking programmatic rule must be a separate heavy gate."
- Decision 3 says: `MustNotCoverClause.applies_when: EvidencePredicate` — meaning the clause itself becomes evidence-conditional. When evidence is missing, the clause doesn't fire.
- The interaction: If a programmatic C2 rule becomes evidence-conditional (Decision 3), then its "always-on"-ness is already qualified by evidence availability. The auditor would need to check `EvidenceAvailability` before deciding whether C2 applies. Decision 7's "always-on" framing doesn't account for this evidence-conditional gating.

**Impact:** A future implementation that makes C2 evidence-conditional (per Decision 3) while also implementing per-chapter `audit_focus` (per Decision 7) could have two independent mechanisms controlling whether a C2 check fires: evidence condition AND audit_focus subsetting. The design doesn't specify which takes precedence or whether they compose.

**Suggested fix:** Add to Decision 7: "When a programmatic rule's clause is evidence-conditional (per Decision 3), the evidence predicate gates whether the clause participates in audit at all. `audit_focus` controls only whether the auditor prompt mentions the rule category in its semantic emphasis instructions. The two mechanisms are independent: an evidence-disabled clause is never checked, regardless of audit_focus; an audit_focus-omitted category is still checked programmatically if its evidence predicate is satisfied."

**Fix risk:** LOW. Clarifies composition without changing either decision.

---

## Finding 4: Ch0 consuming unsafe Ch7 — residual risk correctly identified but unmitigated

**Severity:** MEDIUM (acceptable as design residual; controller must assign owner before Ch0 implementation)

**Evidence:**

- Decision 5 says Ch0 "must consume a Chapter 7 final judgment bundle and must not independently derive the action."
- The design's own residual risks section asks: "How to prevent Ch0 consuming Ch7 from masking an unsafe Ch7 conclusion when upstream chapters are partial or degraded."
- The current `summary.json` shows `final_assembly_status=incomplete` and correctly blocks report generation when chapters 2/3/4/6 are not accepted. This proves the current system already has the concept of "incomplete upstream means no report."
- But the design doesn't propose any additional safety mechanism for the scenario where Ch7 itself is accepted but based on degraded/partial upstream chapters (e.g., only Ch1 and Ch5 accepted, Ch7 somehow passes, Ch0 copies Ch7's action — the reader sees a confident action judgment without knowing Ch2/3/4/6 are missing).

**Impact:** If a future implementation allows Ch7 to produce a final judgment with only partial upstream acceptance, Ch0 would faithfully reproduce that judgment, creating a misleadingly confident report. The current system prevents this today by blocking final assembly when any body chapter is not accepted, but the design's typed contract doesn't encode this dependency as a contract-level constraint.

**Suggested fix:** Add to Decision 5's `ChapterContract(chapter_id=0)` shape: "`consumes_chapter_conclusions: [7]` with additional constraint: Ch0 assembly must fail-closed if any chapter in `required_body_chapters` (currently 1-6) has `status != accepted`. This constraint is not encoded in the contract shape itself but must be enforced by the final assembler."

**Fix risk:** LOW. Aligns design text with current code behavior.

---

## Finding 5: `first_class_facets` in typed ChapterContract — scope undefined

**Severity:** LOW (deferred concept; risk of premature coupling to unaccepted facet wiring spec)

**Evidence:**

- Decision 1's proposed `ChapterContract` includes `first_class_facets: list[FacetId]`.
- The external first-principles spec §5.3 references `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` as an existing spec that is "plan A + plan C" but not yet accepted.
- The design defers "exact enum names and schema implementation form."
- The template draft's `FUND_FACET_CATALOG` defines facet candidates, but there is no current code that consumes `FacetId` as a typed identifier in contract resolution.

**Impact:** Including `first_class_facets` in the accepted typed contract shape could be read as accepting the facet wiring design by reference, which the controller has not done. The field name implies a facet resolution system that doesn't exist yet.

**Suggested fix:** Either remove `first_class_facets` from the accepted contract shape and add it to Deferred, or add an explicit constraint: "`first_class_facets` is placeholder only; its type, enum domain, and resolution mechanism are deferred to a separate facet wiring gate. No implementation may populate or consume this field until that gate is accepted."

**Fix risk:** LOW. Either approach prevents premature coupling.

---

## Finding 6: EvidenceAvailability contract shape — missing year-tier availability

**Severity:** LOW (minor schema gap; won't block design acceptance)

**Evidence:**

- Decision 2's `EvidenceAvailability` shape includes `available_fact_ids`, `available_anchor_ids`, `unavailable_requirements`, `data_gaps`, `reviewed_evidence_flags`, `not_applicable_flags`, `source_strength_by_requirement`.
- Decision 4's `RequiredOutputItem` addresses missing evidence with `render_evidence_gap`, `render_minimum_verification_question`, `delete_if_not_applicable`, `block`.
- The external spec §1.2 F-10 identifies that Ch2's `must_answer` requires 1Y/3Y/5Y data, but 5Y is only available for mature funds.
- The design rejects "direct 5-year PDF/raw text injection into LLM prompts" but doesn't include year-tier availability (which years of data are available) in the `EvidenceAvailability` contract.

**Impact:** Without year-tier availability in the evidence contract, a chapter like Ch2 cannot programmatically know whether `render_evidence_gap` should fire for the 5Y row specifically vs the 1Y/3Y rows. The writer would still need to infer this from facts, recreating the current problem.

**Suggested fix:** Add to `EvidenceAvailability` contract shape: `available_report_years: list[int]` and/or `data_tier_availability: map[Literal["1Y","3Y","5Y"], bool]`. This aligns with the external spec's recommendation that must_answer items should declare their year-tier requirements.

**Fix risk:** LOW. Adds a field without changing existing semantics.

---

## Finding 7: `required_output` block semantics — undefined safety criteria

**Severity:** LOW (acceptable as design deferral; needs resolution before block is used in any chapter)

**Evidence:**

- Decision 4 says `block` is "reserved for core facts whose absence makes the chapter unsafe."
- The design doesn't define: (a) who decides which items get `block` vs `render_evidence_gap` (contract author? controller? runtime?), (b) what "unsafe" means concretely (produces misleading conclusion? violates regulatory requirement? makes Ch7 judgment unreliable?), (c) whether `block` can be overridden by repair.
- The current system already has a similar concept: missing required markers, forbidden phrases, and L1 failures all block. But these are auditor-level blocks, not contract-level `required_output` blocks.

**Impact:** If a future implementation marks an item as `block` without clear criteria, it could either be too aggressive (blocking chapters that could safely degrade) or too permissive (allowing chapters to pass with missing safety-critical facts).

**Suggested fix:** Add to Decision 4: "`block` must only be used when the missing evidence would make any conclusion in the chapter unreliable (e.g., missing cost data for a cost-reasonableness judgment in Ch2, missing pressure-test thresholds for Ch6). The decision of which items get `block` must be explicit in the contract authoring gate and reviewed for each item independently."

**Fix risk:** LOW. Tightens without restricting.

---

## Finding 8: absent explicit handoff criteria for the next gate

**Severity:** LOW (usability issue; controller can add during judgment)

**Evidence:**

- The design lists what's accepted, rejected, and deferred across seven decisions.
- The design lists residual risks and open questions for the controller.
- But it doesn't state what the next gate's minimum input requirements are: which accepted decisions must be reflected in a Ch3-only calibration plan, which deferred items may be tentatively referenced, and which rejected items must not be referenced.

**Impact:** The next gate worker (for a Ch3 calibration plan or broader typed contract implementation plan) may not know which parts of this design are mandatory input vs optional reference. This could lead to scope disputes.

**Suggested fix:** Add a "Handoff Criteria" section listing: (1) Decisions 1-5 and 7 are accepted future design and may be referenced by the next plan gate; (2) Decision 6 (Ch2 split) is deferred and must not be treated as accepted design; (3) the next gate must not accept 0+9, 0+10, migration timelines, timeout percentages, or 5Y raw ingestion; (4) any implementation gate must first resolve Findings 1, 3, and 4 from this review.

**Fix risk:** LOW. Pure documentation.

---

## Boundary Consistency Check

Checked all seven decisions against the `UI -> Service -> Host -> Agent` boundary:

| Decision | Boundary alignment | Issue |
|----------|-------------------|-------|
| D1: typed ChapterContract | Template contract semantics assigned to Fund ✓ | None |
| D2: EvidenceAvailability | Constrained to Fund/Agent evidence projection ✓ | None |
| D3: evidence-conditional must_not_cover | Programmatic audit stays in Agent/Fund ✓ | None |
| D4: required_output missing/degrade | Contract semantics in Fund; Service may select ✓ | None |
| D5: Ch0 consumes Ch7 | Aligns with current final assembly (Service layer) ✓ | None |
| D6: Ch2 split deferral | No boundary violation ✓ | None |
| D7: per-chapter audit_focus | LLM semantic audit in Agent; programmatic stays Agent/Fund ✓ | None |

No boundary violations found. The design correctly places template contract semantics in Fund, leaves Service to select/apply contracts, and keeps Host business-agnostic.

---

## Non-Goal Compliance Check

| Non-goal | Status |
|----------|--------|
| No 0+9 or 0+10 as accepted design | Compliant: Decision 6 explicitly defers |
| No timeout-improvement percentages | Compliant: rejected in recommendation summary |
| No migration timeline/rollback | Compliant: rejected in recommendation summary |
| No 5Y raw PDF ingestion | Compliant: rejected in recommendation summary |
| No provider budget/score-loop/deterministic fallback changes | Compliant: listed in non-goals |
| No current-fact wording claiming implementation | Compliant: design explicitly says "proposed future design" |
| No dayu-agent runtime dependency | Compliant: confirmed in non-goals |

---

## Residual Risks (reviewer-added to design's own list)

| ID | Risk | Severity |
|----|------|----------|
| RR-1 | If `audit_focus` subsetting is implemented before evidence-conditional must_not_cover, chapters with reduced focus may accidentally pass programmatic checks that should have fired — because the implementation coupling between the two mechanisms is not yet designed | MEDIUM |
| RR-2 | The `polarity` field in `MustNotCoverClause` (Decision 3) is the most implementation-sensitive concept in the entire design. If it can't be implemented robustly for Chinese, the entire evidence-conditional must_not_cover design collapses back to brittle phrase matching | MEDIUM |
| RR-3 | Decision 1 proposes `consumes_chapter_conclusions: list[chapter_id]` as a ChapterContract field, but only Ch0 uses it in this design. If later chapters also consume upstream conclusions (e.g., Ch7 consuming Ch6 risk assessment), the dependency graph could become cyclic or introduce cascading failure modes not addressed here | LOW |
| RR-4 | The design uses `EvidenceAvailability` as a Fund/Agent construct, but the external spec proposes it as a Python-layer injection into prompts. If `EvidenceAvailability` ends up being constructed in Service (where prompt assembly happens), it would violate the boundary rule that evidence availability is a Fund/Agent concern | LOW |

---

## Open Questions

1. Should the controller accept all seven decisions as a single design bundle, or split Decisions 1-5+7 (accepted) from Decision 6 (deferred) into separate acceptance scopes to prevent the deferred Ch2 split from being accidentally activated?
2. Does the controller want Finding 1 (Chinese polarity robustness) resolved before any implementation gate, or is it acceptable to treat it as a calibration problem to be solved during the first implementation slice?
3. Should `first_class_facets` be removed from the accepted contract shape until the facet wiring spec is itself accepted, to avoid transitive acceptance of an un-reviewed design?
4. Is the next gate strictly "Ch3-only must_not_cover calibration plan" (per Slice 1 controller judgment), or does this accepted typed contract design authorize a broader "typed ChapterContract schema plan" that encompasses Ch3 as its first calibration target?

---

## Conclusion

**Self-check: pass.** This review is complete and non-blocking. All required sources were read and cross-checked. No findings rise to blocking severity.

**Artifact path:** `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-ds-20260602.md`

**Findings summary:**
- F-1 (MEDIUM): Chinese assertion polarity robustness unresolved — handoff risk
- F-2 (LOW): typed subcontracts concept ambiguous
- F-3 (MEDIUM): audit_focus / evidence-conditional must_not_cover interaction unaddressed
- F-4 (MEDIUM): Ch0 masking unsafe Ch7 — risk identified but unmitigated
- F-5 (LOW): first_class_facets scope undefined
- F-6 (LOW): EvidenceAvailability missing year-tier availability
- F-7 (LOW): required_output block semantics undefined
- F-8 (LOW): absent explicit handoff criteria

**Residual risks:** 4 reviewer-added risks (RR-1 through RR-4) in addition to the design's own 7 open questions.

**Validation:** `git diff --check -- docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-ds-20260602.md` will confirm no whitespace errors (new file, no diff base to check against). Secret safety: this artifact contains no API keys, tokens, credentials, raw prompts, raw provider responses, or secret-bearing payloads.
