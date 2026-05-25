# Re-Review: Fact-Evidence Contract S2 Bundle Candidate Plan

> Reviewer: AgentMiMo
> Date: 2026-05-25
> Original review: `release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-review-mimo-20260525.md`
> Patched artifact: `release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md`
> Conclusion: **PASS**

---

## Finding Resolution

### F-01 review_status 转换语义 — RESOLVED

Patch adds (L210-L248):

- Legal progression aligned with S0 transitions (L210-L219): explicit `candidate -> repository_verified -> fact_prefill_generated -> fact_prefill_reviewed -> scoring_ready -> accepted_baseline` linear path.
- Transition semantics table (L222-L229): each transition has required trigger/evidence and actor.
- Terminal states (L231-L235): `rejected` and `expired` are terminal; `deferred` is non-terminal but not scoring-ready.
- `review_status priority` ordering (L237-L241): `rejected > expired > deferred > scoring_ready > fact_prefill_reviewed > fact_prefill_generated > repository_verified > candidate`.
- Conflict examples (L243-L247): three concrete scenarios showing how priority resolves ambiguity.
- Two new invalid combinations added (L257-L258): `classified_fund_type="unknown"` and unresolved `data_gap_refs` cannot be `scoring_ready`.

Adequately addresses the original concern. Implementation agent now has explicit transition rules, priority, and conflict resolution guidance.

### F-02 locator_hash 规格不足 — RESOLVED

Patch adds (L277, L281-L289):

- Algorithm: `sha256` first 8 lowercase hex characters (L277).
- 5-step normalization procedure (L281-L287): ordered JSON object, None→empty string, string conversion with whitespace normalization, NFC, sorted-keys UTF-8 serialization, sha256 digest.
- Collision handling (L289): deterministic `-2`, `-3` suffix in sort order with validation warning; tests required for stable hashing and collision suffixing.

Adequately addresses the original concern. Implementation agent has exact algorithm, normalization, and collision strategy.

### F-03 chapter_contract wording constraint 仍为候选 — RESOLVED

Patch updates (L375-L382):

- Wording constraint now reads: "Required `chapter_contract` wording constraint, accepted for this S2 plan based on the S1 dry-run controller judgment" (L375).
- Explicit acceptance scope: "The accepted constraint is narrow: it governs active-fund Chapter 3 stability/style-consistency claims and does not require automatic turnover extraction" (L382).
- Slice 5 updated to say "Add the active-fund Chapter 3 turnover stability accepted constraint" (L470), not "candidate constraint".

Adequately addresses the original concern. Constraint is now accepted, not candidate, consistent with S1 controller judgment.

### F-04 Multi-anchor ExtractedField mapping — RESOLVED

Patch adds (L123, L414, L427):

- Multi-anchor mapping rule (L123): "each `ExtractedField` should normally map to one `ReportFact` whose `source_anchor_ids` contains every projected `anchor_id` from `ExtractedField.anchors`". Splitting allowed only for distinct subfield paths; every original anchor must be preserved.
- Slice 2 task (L414): "Apply the multi-anchor rule: one `ExtractedField` fact references all projected anchor ids unless explicitly split into subfacts without dropping anchors."
- Slice 2 validation (L427): "Tests with a multi-anchor `ExtractedField` prove no anchor is dropped from `source_anchor_ids`."

Adequately addresses the original concern. Implementation agent has clear default mapping and explicit no-drop rule.

## New Blocker Check

Patch also adds several other improvements not related to original findings:

- `nav_data` explicit exclusion from initial facts projection (L121-L122) — sound; `NavDataResult` lacks `ExtractedField` structure.
- `external_official` boundary clarification (L97) — sound; prevents ad hoc API calls.
- `corpus_id` format specification (L59, L74) — sound; links to S0 review artifacts.
- `classified_fund_type` validation rules (L76) — sound; explicit rejection of unknown values.
- `preferred_lens` format specification (L78) — sound; serializable projection with `unknown` handling.
- Additional negative tests in Slices 1-3 (L402-L404, L424-L426, L444-L446) — sound; improve testability.

**No new blockers introduced.**

## Validation Commands

```bash
rg -n "transition semantics|locator_hash|sha256|multi-anchor|accepted constraint|review_status priority|classified_fund_type.*unknown|nav_data.*excluded" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md
```

All 4 finding patches confirmed present in the artifact.

## Conclusion

**PASS**

All 4 findings resolved. No new blockers. Plan is code-generation-ready for a later implementation gate.
