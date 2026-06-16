# Docling EvidenceAnchor Mapping Section-context Enrichment Plan Re-review (AgentMiMo) - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Plan Re-review Gate`
Role: AgentMiMo re-review worker
Release/readiness: `NOT_READY`

## Re-review Target

- Plan: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md`
- MiMo prior review: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-review-mimo-20260616.md`
- DS review: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-review-ds-20260616.md`
- Fix evidence: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-fix-evidence-20260616.md`

## Scope

Re-review only whether controller-accepted findings from the MiMo prior review and DS review were fixed in the plan. Does not check source code, tests, control docs, design docs, or any implementation artifacts.

## Controller-Accepted Findings Disposition

| Finding | Source | Disposition | Re-review target |
| --- | --- | --- | --- |
| MiMo 01 / DS-F3 numeric heading closure | MiMo + DS | accepted | Slice 1 numeric-heading keyword-family guard |
| DS-F1 / OQ1 TOC handling | DS | accepted | Slice 2 TOC exclusion rules |
| DS-F2 monotonic ordering precision | DS | accepted | Slice 2 inter-section monotonic semantics |
| DS-F4 / OQ2 alias scope | DS | accepted | Slice 1 exact alias scope |
| DS-F5 + MiMo 02/03 test fixture gaps | DS + MiMo | accepted | Tests and Validation Commands |
| DS-F6 / OQ3 SectionIndex / private API rules | DS | accepted | Slice 2/3 SectionIndex construction and span semantics |
| MiMo 04 cell label no-inference test | MiMo | deferred-but-tested | Slice 4 behavioral test requirement |

## Re-review: Numeric Heading Closed-Family Guard (MiMo 01 / DS-F3)

**Plan text (Slice 1, line 72):** "The implementation must change the existing numeric-heading candidate path in `_section_candidates_from_texts()`: an Arabic heading prefix in `1..10` must not immediately add `§N` and bypass closed keyword-family validation. The current pattern-match-and-`continue` behavior is insufficient for numeric headings."

**Positive example:** `8.4 报告期末按行业分类的股票投资组合` maps to `§8` — alias match required.
**Negative example:** `8.3 任意无关文本` blocks as `unsupported_heading_number` — prefix alone insufficient.

**Verdict: FIXED.** The plan now explicitly identifies the existing `_section_candidates_from_texts()` `continue` behavior as the code path requiring change, names the function, and provides binding positive/negative examples. An implementation agent cannot reasonably interpret the current code as already satisfying this requirement.

## Re-review: TOC Handling (DS-F1 / OQ1)

**Plan text (Slice 2, line 95-96):** "Directory or table-of-contents section nodes must not seed stable body section spans when a deterministic TOC signal is present, such as an explicit TOC/目录 node, a section path under a TOC/目录 parent, or another accepted structural TOC marker in the candidate representation."

**Plan text (Slice 2, line 96):** "If TOC/body cannot be distinguished safely and the same annual section family appears in both candidate locations, the duplicate section family must fail closed instead of guessing which node is body."

**Tests (line 201-202):** TOC exclusion test (deterministic TOC signal → body start selected) and unsafe TOC/body ambiguity test (fail closed as `duplicate_section_heading`).

**Verdict: FIXED.** The plan now explicitly addresses TOC pollution in the section index construction rules. Deterministic TOC signals are defined (explicit TOC/目录 node, path under TOC parent). When TOC/body cannot be distinguished, the plan requires fail-closed duplicate handling rather than guessing. Two concrete test fixtures cover both paths.

## Re-review: Inter-Section Monotonic Semantics (DS-F2)

**Plan text (Slice 2, line 100):** "Monotonic ordering means inter-section top-level ordering by each annual section family's selected body start page. Same-section child nodes do not independently break monotonic order."

**Test (line 205):** "same-section child ordering: multiple `§8.x` child nodes under the selected `§8` body span do not independently trigger `section_order_not_monotonic`; the selected body start remains the minimum safe body page after TOC exclusion."

**Verdict: FIXED.** The plan now explicitly limits monotonic ordering to inter-section top-level ordering and clarifies that same-section child nodes (e.g., `§8.x`) do not independently trigger monotonic violations. A concrete test fixture validates this boundary.

## Re-review: Exact Alias Scope (DS-F4 / OQ2)

**Plan text (Slice 1, line 79-85):** Lists exact aliases under the heading "Exact initial alias additions" (changed from "Minimum alias additions").

**Plan text (Slice 1, line 85):** "No other alias may be added by implementation-worker discretion. Additional aliases require later evidence and controller acceptance."

**Verdict: FIXED.** The plan now uses "Exact" instead of "Minimum", lists the precise aliases, and explicitly forbids implementation-worker discretionary expansion. The guardrail is clear: additional aliases require separate evidence and controller acceptance.

## Re-review: Test Fixture Specs (DS-F5 / MiMo 02/03)

**Plan Tests section (lines 196-212)** now includes 16 concrete test fixtures:

| Test | Finding addressed |
| --- | --- |
| numeric heading positive: `2.1 基金基本情况` → `§2` | Normalization happy path |
| explicit token + NFKC positive: `§ 2`, full-width `２．１` | NFKC handling |
| closed-family guard: `8.4` maps, `8.3` blocks | MiMo 01 / DS-F3 |
| unsupported heading number: `11.1`, Chinese numerals, `2、` | DS-F3 pattern rejection |
| TOC exclusion | DS-F1 |
| unsafe TOC/body ambiguity | DS-F1 |
| duplicate body heading | MiMo 02 |
| monotonic violation | DS-F2, DS-F5 |
| same-section child ordering | DS-F2 |
| page-based table inherit | MiMo 03 |
| half-open boundary | DS-F6 / OQ3 |
| missing page blocked | MiMo 03 |
| cross-section multi-page table blocked | MiMo 03, DS-F5 |
| cell parent inheritance only | MiMo 04 |
| cover/report-title headings blocked | Baseline safety |
| S1 full JSON schema mismatch blocked | Slice 6 |

**Verdict: FIXED.** All three MiMo findings (01, 02, 03) and DS-F5 are addressed by concrete test fixtures with input/expected-output specifications. The test list now covers normalization happy paths, NFKC, closed-family guard, pattern rejection, TOC handling, duplicate headings, monotonic ordering, same-section ordering, page-based propagation, half-open boundaries, missing pages, cross-section blocking, cell inheritance, cover headings, and S1 schema mismatch.

## Re-review: SectionIndex / Private API Rules (DS-F6 / OQ3)

**Plan text (Slice 2, line 97-98):** "Exclude section nodes with `page=None` or `page<=0` from the stable index."

**Plan text (Slice 2, line 98):** "Build an internal frozen `SectionIndex` or equivalent private structure once in `map_candidate_document_anchor_candidates()` and pass it through internal helper calls. Do not change public API signatures."

**Plan text (Slice 2, line 104):** "Section spans are half-open `[start_page, next_start_page)`. A block page equal to `next_start_page` belongs to the next section, not the previous section."

**Test (line 207):** "half-open boundary: with spans `[10, 60)` for `§3` and `[60, next)` for `§8`, table page 60 maps to `§8`."

**Verdict: FIXED.** The plan now specifies: (a) page filtering rules (exclude `page=None` and `page<=0`); (b) SectionIndex is built once in the document-level function and passed internally; (c) public API signatures must not change; (d) half-open span semantics with concrete boundary example. The OQ3 boundary case (page equal to `next_start_page`) is explicitly addressed by the half-open span rule and the dedicated test fixture.

## Re-review: Cell Label No-Inference Test (MiMo 04)

**Plan text (Slice 4, line 121):** "The implementation must include a test proving cells do not infer annual-report section from `row_label_path` or `column_header_path`."

**Test (line 210):** "cell parent inheritance only: a cell under a parent table mapped to `§8` maps to `§8`; a cell whose `row_label_path` or `column_header_path` contains `§2` must not override or independently infer section from those labels."

**Verdict: FIXED.** MiMo 04 was deferred-but-tested. The plan now requires a mandatory behavioral test (not just optional cleanup). The test fixture specifies both the positive path (cell inherits from parent table) and the negative path (cell does not infer from `row_label_path`/`column_header_path`).

## Re-review Summary Table

| Finding | Source | Disposition | Re-review Verdict |
| --- | --- | --- | --- |
| MiMo 01 / DS-F3 numeric heading closure | MiMo + DS | accepted | FIXED |
| DS-F1 / OQ1 TOC handling | DS | accepted | FIXED |
| DS-F2 monotonic ordering precision | DS | accepted | FIXED |
| DS-F4 / OQ2 alias scope | DS | accepted | FIXED |
| DS-F5 + MiMo 02/03 test fixture gaps | DS + MiMo | accepted | FIXED |
| DS-F6 / OQ3 SectionIndex / private API rules | DS | accepted | FIXED |
| MiMo 04 cell label no-inference test | MiMo | deferred-but-tested | FIXED |

## Open Questions

None. All controller-accepted findings have been addressed in the plan with sufficient specificity for implementation.

## Residual Risks

| Risk | Severity | Tracking |
| --- | --- | --- |
| Implementation must still change `_section_candidates_from_texts()` to close numeric-heading keyword-family validation | 中 | Implementation gate |
| TOC exclusion depends on deterministic TOC signal presence in candidate representation; if signal is absent, duplicate fallback may reduce yield | 低 | Re-evidence gate |
| Exact alias set may be insufficient for real heading diversity; additional aliases require evidence + controller gate | 低 | Re-evidence gate |
| Table/cell yield, field correctness, source truth, baseline promotion, runtime/cache/cost and readiness remain unproven | — | Deferred gates |

## Final Verdict

All 7 controller-accepted findings (6 from MiMo/DS reviews, 1 deferred-but-tested) are fixed in the plan with binding implementation guidance, concrete test fixtures, and explicit guardrails. No unfixed accepted findings remain.

```text
RE_REVIEW_PASS_NOT_READY
```
