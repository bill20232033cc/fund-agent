# Docling Field Correctness Anchor Coverage No-live Implementation Plan - 2026-06-16

Gate: `Docling Field Correctness Anchor Coverage No-live Implementation Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Plan a no-live implementation slice that closes the accepted anchor-coverage blocker for Docling candidate reviewed facts.

Accepted evidence shows:

| Fact | Value |
| --- | ---: |
| Selected Docling reviewed values matching same-source references | `72 / 72` |
| Current selected reviewed-fact anchor coverage | `44 / 72` |
| Missing-anchor rows analyzed | `28 / 28` |
| Parent table exists | `28 / 28` |
| Candidate cell exists | `28 / 28` |
| Rows mapped when passed to current helper | `0 / 28` |
| Root-cause repair surface | `section_context_mapping_rule` for `28 / 28` |
| Blocked reason split | `duplicate_section_heading=16`, `missing_section_context=12` |

The implementation goal is to change only deterministic candidate section-context mapping rules so those existing candidate table/cell locators can map to candidate EvidenceAnchor semantic fields without weakening fail-closed behavior.

## 2. Why `72 / 72` Matters

`72 / 72` is not a release-readiness requirement and does not prove source truth, full field correctness, baseline promotion, or production parser replacement.

It is required as the strong closure target for this local blocker because the accepted evidence already shows all `28 / 28` missing-anchor rows have existing candidate cells and share the same repair surface. If the implementation only improves coverage from `44 / 72` to a partial number, the gate has not proven that the known section-context defect is closed; it has only proven an incremental improvement.

Planning target:

```text
strong target: 72 / 72 selected reviewed facts have candidate anchors
minimum useful improvement: >44 / 72, but only with closed residual classification
must preserve: S5 reviewed-fact positive control remains 17 / 17
must preserve: candidate_field_correctness_status=not_proven
must preserve: source_truth_status=not_proven
```

If a row cannot safely reach `72 / 72`, the implementation evidence must not hide it. It must classify the remaining row with a closed reason and route it to either a follow-up implementation plan or a reduced-scope controller decision.

S6-F041 is the known planning caution: it shares the same candidate cell as S6-F040 while being labeled `benchmark`. The implementation plan may keep S6-F041 in the target only after validating that the accepted comparative input intentionally maps it to that cell. If not validated, S6-F041 must become a scope exception rather than forcing an unsafe mapping rule.

## 3. Scope

Exact implementation write set:

```text
fund_agent/fund/documents/candidates/evidence_anchor_mapping.py
tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

Exact implementation evidence write set:

```text
docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-evidence-20260616.md
reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json
```

Conditional documentation write set:

```text
fund_agent/fund/README.md
```

Update `fund_agent/fund/README.md` only if implementation changes documented candidate mapping behavior. Do not update README merely because evidence metrics changed.

## 4. Non-goals

- No live/network/source acquisition/PDF/FDR/Docling conversion/pdfplumber export.
- No provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge.
- No public `EvidenceAnchor` schema change.
- No `EvidenceSourceKind` expansion.
- No source policy, FundDocumentRepository, Service, Host, UI, renderer, or quality gate behavior change.
- No production parser replacement claim.
- No source-truth or full-field-correctness claim.
- No manual JSON patch to make the 28 anchors appear.

## 5. Current Code Evidence

Current target module:

```text
fund_agent/fund/documents/candidates/evidence_anchor_mapping.py
```

Relevant current behavior:

- `_build_section_index()` builds `duplicate_sections`, `selected_pages`, `non_monotonic_sections`, `boundary_pages`, and `spans`.
- `_duplicate_sections()` marks a section unsafe when more than one non-child body node maps to the same annual-report section.
- `_section_spans()` uses the smaller of the next stable section start and the next unindexed boundary page as the span end.
- `_SectionIndex.section_for_pages()` returns `duplicate_section_heading` or `missing_section_context` before mapping a candidate table/cell.

Current targeted test file:

```text
tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

Baseline validation:

```text
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
36 passed
```

## 6. Implementation Decisions

### Slice A. Duplicate Section Heading Disambiguation

Target rows:

- `16 / 28` blocked with `duplicate_section_heading`.
- Primarily S4 and S6 identity/product-contract rows on pages 5-6.

Implementation decision:

Replace the binary duplicate-section block with deterministic duplicate classification:

1. Keep TOC and child-heading exclusion unchanged.
2. For each annual-report `section_id`, group body entries by section.
3. Treat same-section duplicates as safe only when all of these hold:
   - every duplicate maps to the same supported `§N`;
   - all candidate pages are positive;
   - the earliest page can be selected as stable body start without making global section order non-monotonic;
   - duplicate pages are strictly later than the selected start page;
   - no duplicate has the same page as the selected start page;
   - there is no competing supported `§N` on the same selected page.
4. If the rule cannot prove a unique stable start, preserve `duplicate_section_heading`.

Expected code shape:

- Add a private helper near `_duplicate_sections()`, such as `_unsafe_duplicate_sections(...)` or `_selected_section_pages(...)`, to compute both selected pages and unsafe duplicates from the same grouped entries.
- Keep helpers module-private and flat; do not add nested functions/classes.
- Preserve existing `CandidateEvidenceAnchorMappingBlocked.reason_code` values.

### Slice B. Stable Span Boundary Adjustment

Target rows:

- `12 / 28` blocked with `missing_section_context`.
- S1 expense rows on pages 37-38, S4 performance rows on page 10, S6 performance/expense rows on pages 25 and 40.

Implementation decision:

Change span construction so unindexed boundaries do not automatically truncate a stable supported annual-report section unless they are proven to be a real top-level boundary.

1. Stable supported section starts remain the primary span boundaries.
2. Unindexed boundary pages should only close a span when the boundary is a non-TOC, non-child body node and is classified as a hard unsupported top-level boundary.
3. Unknown or unparseable section nodes inside an otherwise stable span must not by themselves make in-report table/cell pages unreachable.
4. A page-span fallback may map a table/cell only when exactly one stable supported span contains all block pages.
5. Multi-page blocks crossing stable supported spans must still return `section_span_crosses_multiple_sections`.
6. Pages outside all stable supported spans must still return `missing_section_context`.

Expected code shape:

- Adjust `_unindexed_section_boundary_pages()` and/or `_section_spans()` rather than changing table/cell locator parsing.
- Preserve half-open span semantics for stable supported section starts.
- Preserve existing fail-closed tests by amending only those whose old expectation was intentionally too coarse.

### Slice C. Candidate-only And Evidence Metric Guard

Implementation must keep mapped outputs candidate-only:

- `candidate_only=True`
- `field_correctness_status="not_proven"`
- `source_truth_status="not_proven"`
- no production `EvidenceAnchor` construction or import

Implementation evidence must regenerate a no-live after matrix from the accepted local envelopes and compare:

```text
before: 44 / 72 candidate anchors
target after: 72 / 72 candidate anchors
minimum after: >44 / 72 with closed residual rows
S5 must remain: 17 / 17
```

## 7. Required Tests

Add or update tests in:

```text
tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

Required test cases:

| Test | Expected assertion |
| --- | --- |
| deterministic later duplicate heading maps stable table cell | repeated same-section later body heading does not automatically block page-based table/cell mapping |
| same-page duplicate top-level body heading remains blocked | preserves `duplicate_section_heading` for genuinely ambiguous duplicate start |
| unsafe TOC/body ambiguity remains blocked | preserves existing fail-closed behavior when TOC cannot be distinguished |
| non-monotonic section order remains blocked | preserves `section_order_not_monotonic` |
| stable span ignores soft unindexed internal boundary | in-report table page can map when exactly one supported stable span contains it |
| hard unsupported boundary still blocks outside page | table after a real unsupported boundary remains `missing_section_context` |
| multi-page table crossing stable sections remains blocked | preserves `section_span_crosses_multiple_sections` |
| candidate-only wrapper invariants remain unchanged | no source truth or field correctness proof |

If existing tests encode the old over-conservative behavior, update their assertions with comments explaining that the old behavior was the accepted root cause.

## 8. No-live Implementation Evidence Requirements

Implementation evidence must write:

```text
reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json
docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-evidence-20260616.md
```

The JSON must include:

- input artifact paths and SHA-256 values;
- before metrics from accepted comparative/root-cause evidence;
- after metrics;
- per-row result for the prior `28 / 28` missing-anchor rows;
- S5 positive-control coverage;
- residual rows, if any, with closed reason codes;
- negative guard flags: `not_source_truth=true`, `not_full_field_correctness=true`, `not_production_parser_replacement=true`, `not_readiness_proof=true`.

The evidence artifact must state whether the strong target was met:

```text
72 / 72 achieved
```

or, if not:

```text
PARTIAL_IMPROVEMENT_NOT_READY
```

with exact residual routing.

## 9. Validation Commands

Required commands:

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
python -m json.tool reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json >/dev/null
git diff --check
```

Allowed evidence commands:

```bash
jq '<filter>' reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json
jq '<filter>' reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json
uv run python - <<'PY'
# no-live local envelope projection and mapping metric regeneration only
PY
```

Forbidden commands:

- live/network commands;
- PDF/FDR/Docling conversion/pdfplumber export;
- provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands.

## 10. Stop Conditions

Stop before implementation completion if:

- a rule requires manual field-specific anchor exceptions;
- a rule requires public `EvidenceAnchor` or source policy changes;
- duplicate-heading disambiguation cannot preserve fail-closed behavior for same-page or non-monotonic duplicates;
- span fallback maps pages across multiple supported stable sections;
- S5 reviewed-fact positive-control coverage regresses;
- S6-F041 cannot be validated as an intended reference-side `benchmark` assignment and no reduced-scope controller decision exists;
- after evidence cannot classify every remaining residual row with a closed reason code.

## 11. Review Requirements

Before implementation, this plan must receive two independent reviews.

Reviewers must verify:

- `72 / 72` is used only as local blocker closure, not readiness;
- partial `>44 / 72` improvement cannot be accepted as full closure without residual routing;
- write set is limited;
- both `duplicate_section_heading` and `missing_section_context` are addressed;
- fail-closed behavior remains tested;
- candidate-only invariants remain explicit;
- no live/source/parser/release boundary is crossed.

Allowed review verdicts:

```text
REVIEW_PASS_NOT_READY
REVIEW_BLOCKED_NEEDS_FIX_NOT_READY
```

## 12. Final Verdict

```text
VERDICT: PLAN_READY_FOR_REVIEW_NOT_READY
```
