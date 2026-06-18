# Docling EvidenceAnchor Mapping Section-context Enrichment Plan Re-review (AgentDS) — 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Plan Re-review Gate`
Role: AgentDS re-review worker
Release/readiness: `NOT_READY`

## Reviewed Target

Plan artifact: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md`
Fix evidence: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-fix-evidence-20260616.md`

## Scope

Re-review limited to verifying that controller-accepted findings from AgentDS review (`docling-evidenceanchor-mapping-section-context-enrichment-plan-review-ds-20260616.md`) and AgentMiMo review (`docling-evidenceanchor-mapping-section-context-enrichment-plan-review-mimo-20260616.md`) were fixed in the current plan artifact. No new adversarial review.

## Finding Disposition Verification

### DS-F1 / OQ1 — TOC heading handling

**Original**: Plan lacked TOC/body distinction; directory headings would pollute section index, marking body sections as duplicate.
**Disposition**: Accepted.
**Fix applied**: Slice 2 rule 4: TOC nodes excluded from body span seeding when deterministic TOC signal present. Rule 5: unsafe TOC/body ambiguity fails closed as duplicate. Tests: `TOC exclusion` and `unsafe TOC/body ambiguity` fixtures added.
**Verdict**: FIXED.

### DS-F2 — Monotonic ordering precision

**Original**: Plan did not distinguish inter-section monotonic from intra-section child node ordering.
**Disposition**: Accepted.
**Fix applied**: Slice 2 now defines monotonic as inter-section top-level ordering by selected body start page. Same-section child nodes do not independently break monotonic order unless they create duplicate unsafe body starts. Test: `same-section child ordering` fixture added.
**Verdict**: FIXED.

### DS-F3 / MiMo 01 — Numeric heading closed-family guard

**Original**: Plan said numeric headings must match closed keyword family, but did not call out that existing `_section_candidates_from_texts()` code bypasses keyword-family validation for `§` pattern matches.
**Disposition**: Accepted.
**Fix applied**: Slice 1 now explicitly states: "The implementation must change the existing numeric-heading candidate path in `_section_candidates_from_texts()`: an Arabic heading prefix in `1..10` must not immediately add `§N` and bypass closed keyword-family validation." Binding positive/negative examples: `8.4 报告期末按行业分类的股票投资组合` → `§8`; `8.3 任意无关文本` → `unsupported_heading_number`. Chinese numerals, bracketed Chinese numerals, Chinese section markers without Arabic numbers, and unsupported separators explicitly rejected as `unsupported_heading_number`. Deterministic Enrichment Rules #3 updated. Fail-closed Stop Rules updated. Tests: positive/negative numeric heading fixtures added.
**Verdict**: FIXED.

### DS-F4 / OQ2 — Alias scope

**Original**: "Minimum alias additions" wording left grey area for implementation-worker discretionary expansion.
**Disposition**: Accepted.
**Fix applied**: Slice 1 now says "Exact initial alias additions" with explicit prohibition: "No other alias may be added by implementation-worker discretion. Additional aliases require later evidence and controller acceptance."
**Verdict**: FIXED.

### DS-F5 / MiMo 02/03 — Test fixture gaps

**Original**: Tests listed covered normalization happy path but missed monotonic violation, multi-page cross-section, unsupported heading number, NFKC full-width, and page-based text block propagation fixtures.
**Disposition**: Accepted.
**Fix applied**: Tests section now includes concrete fixtures for: numeric heading closed-family guard, unsupported heading number and pattern guard, TOC exclusion, unsafe TOC/body ambiguity, duplicate body heading, monotonic violation, same-section child ordering, page-based table inherit, half-open boundary, missing page blocked, cross-section multi-page table blocked, cell parent inheritance only (with no-inference test), cover/report-title blocked, NFKC full-width normalization.
**Verdict**: FIXED.

### DS-F6 / OQ3 — SectionIndex structure and half-open span semantics

**Original**: Plan did not specify SectionIndex data structure, build location, parameter passing path, or span boundary semantics.
**Disposition**: Accepted.
**Fix applied**: Slice 2 now specifies: internal frozen `SectionIndex` or equivalent private structure built once in `map_candidate_document_anchor_candidates()`, passed through internal helper calls, public API signatures unchanged. Section nodes with `page=None` or `page<=0` excluded. Half-open spans defined as `[start_page, next_start_page)` with explicit boundary rule: block page equal to `next_start_page` belongs to next section. Test: `half-open boundary` fixture added.
**Verdict**: FIXED.

### MiMo 04 — Cell label dead branch

**Original**: `_section_candidates_from_block()` has `CandidateTableCell` branch extracting section from `row_label_path`/`column_header_path`, conflicting with plan invariant that cells inherit section only from parent table.
**Disposition**: Deferred-but-tested.
**Fix applied**: Slice 4 now requires "a test proving cells do not infer annual-report section from `row_label_path` or `column_header_path`." Cleanup of existing cell branch is optional implementation detail inside accepted write set. Test: `cell parent inheritance only` fixture added with explicit no-inference assertion.
**Verdict**: FIXED (via mandatory behavioral test; code cleanup deferred per controller).

## Specific Item Checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Numeric heading closed-family guard | FIXED | Slice 1 explicit code-change requirement + binding positive/negative examples |
| TOC handling | FIXED | Slice 2 rules 4–5 + TOC/unsafe-ambiguity test fixtures |
| Inter-section monotonic semantics | FIXED | Slice 2 inter-section-only definition + same-section child test |
| Exact alias scope | FIXED | Slice 1 "Exact initial alias additions" + no-discretion prohibition |
| Test fixture specs | FIXED | Tests section with 14 concrete fixture specifications |
| SectionIndex/private API rules | FIXED | Slice 2 frozen structure + build-once + internal-pass + no-public-API-change |
| Half-open spans | FIXED | Slice 2 `[start_page, next_start_page)` + boundary rule + test fixture |
| Cell label no-inference test | FIXED | Slice 4 mandatory behavioral test |

## Open Questions

None. All OQ1–OQ3 from the DS review are resolved in the plan.

## Residual Risks

All residual risks from the DS review remain tracked in the plan's own Residual Risks section. No new risks introduced by the fix.

## Final Verdict

```text
RE_REVIEW_PASS_NOT_READY
```

All seven controller-accepted findings (DS-F1 through DS-F6, MiMo 01–04) are addressed in the plan. The eight specific items (numeric heading closed-family guard, TOC handling, inter-section monotonic semantics, exact alias scope, test fixture specs, SectionIndex/private API rules, half-open spans, cell label no-inference test) are each independently verified as fixed. The plan is ready for the implementation gate.
