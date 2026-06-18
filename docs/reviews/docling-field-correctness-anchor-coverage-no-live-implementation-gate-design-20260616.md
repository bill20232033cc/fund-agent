# Docling Field Correctness Anchor Coverage No-live Implementation Gate Design - 2026-06-16

Status: `GATE_DESIGN_NOT_READY`
Gate to design: `Docling Field Correctness Anchor Coverage No-live Implementation Planning Gate`
Controller prerequisite: root-cause evidence review and controller judgment must be accepted before this implementation-planning gate is executed.
Release/readiness: `NOT_READY`

## 1. Problem Statement

Accepted root-cause evidence shows the anchor coverage blocker is not missing candidate cells and not value extraction error.

Current facts:

| Fact | Evidence |
| --- | --- |
| Selected Docling values match reviewed references | `72 / 72` exact or normalized match |
| Candidate anchor coverage before root-cause evidence | `44 / 72` |
| Missing-anchor rows analyzed | `28 / 28` |
| Parent table exists | `28 / 28` |
| Candidate cell exists | `28 / 28` |
| Rows mapped when directly passed to current helper | `0 / 28` |
| Dominant repair surface | `section_context_mapping_rule` for `28 / 28` rows |
| Blocked reasons | `duplicate_section_heading=16`, `missing_section_context=12` |

Therefore the implementation problem is:

```text
Current candidate section-context safety logic is too coarse for accepted table/cell anchors.
It fail-closes valid in-report candidate cells because duplicate section headings and section-span boundaries are not resolved with enough deterministic context.
```

This gate must preserve fail-closed behavior. It must not solve anchor coverage by accepting ambiguous anchors, widening public schemas, or turning Docling output into source truth.

## 2. Gate Objective

Produce an implementation-ready plan for a no-live patch that improves candidate EvidenceAnchor coverage for accepted Docling reviewed facts while keeping candidate-only boundaries.

Target outcome for the later implementation gate:

| Metric | Current | Target |
| --- | ---: | ---: |
| Accepted reviewed facts with candidate anchor | `44 / 72` | materially improved; target `72 / 72` if deterministic rules support it |
| Missing-anchor rows with candidate cell present | `28 / 28` | `0 / 28` unresolved without explicit reason |
| S5 positive-control anchor coverage | `17 / 17` | remains `17 / 17` |
| Public `EvidenceAnchor` schema changes | `0` | `0` |
| Production parser/repository behavior changes | `0` | `0` |

## 3. Entry Conditions

This gate may start only after:

1. `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-20260616.md` is independently reviewed.
2. Controller judgment accepts or amends the root-cause evidence.
3. Controller confirms the next gate is implementation planning, not more evidence or reduced-scope disposition.

If root-cause review rejects `section_context_mapping_rule` as the dominant repair surface, this gate must not run.

## 4. Non-goals

- No production implementation in this gate.
- No source/test edits in this gate.
- No live/network/source acquisition/PDF/FDR/Docling conversion/pdfplumber export.
- No provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge/stage/commit.
- No production `EvidenceAnchor` schema change.
- No `EvidenceSourceKind` expansion.
- No `FundDocumentRepository`, parser, source policy, Service, Host, UI, renderer or quality gate behavior change.
- No performance/cache/cost gate.
- No baseline disposition.

## 5. Proposed Implementation Strategy

The implementation plan should be narrow and stay inside:

```text
fund_agent/fund/documents/candidates/evidence_anchor_mapping.py
tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

README updates are conditional only if the implementation changes documented candidate behavior. Default: no README update.

### Slice A. Duplicate Section Heading Disambiguation

Problem:

`_duplicate_sections()` marks a section unsafe when more than one non-child body section node maps to the same annual-report section. This blocks S4/S6 identity and product-contract tables on pages 5-6 with `duplicate_section_heading`.

Design requirement:

Add deterministic duplicate-handling before marking a section unsafe. The rule should keep fail-closed behavior unless exactly one section node can be selected as the stable body start.

Candidate rule:

1. Group entries by `section_id`.
2. Ignore TOC entries and child headings as today.
3. For duplicate top-level nodes in the same `section_id`, select a stable start only if:
   - all candidates map to the same supported `section_id`;
   - pages are positive;
   - selecting the earliest body page preserves global section monotonicity;
   - later duplicate pages can be treated as repeated render/navigation headings or continuation headings rather than independent section starts.
4. If these conditions fail, keep `duplicate_section_heading`.

Expected effect:

- S4/S6 `docling_table_2` and `docling_table_3` / `docling_table_4` should no longer block solely because the section heading appears more than once.
- Any truly ambiguous multi-start section remains fail-closed.

### Slice B. Stable Span Boundary Relaxation For In-section Tables

Problem:

`_section_spans()` uses both next stable section start and unindexed boundary pages as span endpoints. Some in-report financial/expense tables then fall outside stable spans and block with `missing_section_context`.

Design requirement:

Adjust span construction or table-page fallback so table/cell pages can resolve to a stable annual-report section when the page lies between two deterministic section starts, even if an unindexed boundary page exists.

Candidate rule:

1. Prefer stable section starts over unindexed boundary pages for table/cell mapping.
2. Use unindexed boundary pages only when they are proven to be a real top-level section boundary, not arbitrary unparsed headings.
3. For table/cell blocks with no explicit section id or heading path, allow page-span fallback only when:
   - exactly one stable span contains the page;
   - the span does not cross into another supported top-level section;
   - the owning section is not marked duplicate or non-monotonic after Slice A;
   - the result is one supported `§N`.
4. If a table page remains outside all stable spans, preserve `missing_section_context`.

Expected effect:

- S1 expense tables on pages 37-38, S4 performance table on page 10, and S6 performance/expense tables on pages 25 and 40 should receive deterministic section context if the surrounding section starts support it.
- Unknown out-of-report or cross-section tables remain fail-closed.

### Slice C. Regression And Safety Tests

The implementation plan must require tests before code or alongside code.

Required tests:

| Test | Purpose |
| --- | --- |
| Duplicate heading fixture maps stable table cell | Proves repeated same-section headings do not automatically block when deterministic earliest body start is safe. |
| Ambiguous duplicate fixture remains blocked | Proves genuinely ambiguous duplicate sections still return `duplicate_section_heading`. |
| Span fallback maps in-report table page | Proves table/cell with no section id can map by stable page span. |
| Outside-span table remains blocked | Proves unknown pages still return `missing_section_context`. |
| Current S5 positive control remains mapped | Prevents regression in already-complete sample coverage. |
| Candidate-only assertions remain unchanged | Ensures `field_correctness_status="not_proven"` and `source_truth_status="not_proven"` are preserved. |

Optional evidence test:

- A no-live fixture or script-style test that loads the accepted local envelopes and verifies the 28 missing-anchor rows improve. If too large for unit tests, this belongs in implementation evidence, not necessarily committed test suite.

## 6. Implementation Plan Requirements

The formal implementation plan must include:

1. Exact write set.
2. Exact helper functions to touch.
3. Exact tests to add or update.
4. Before/after metric target for the accepted local evidence matrix.
5. Stop conditions for ambiguous section cases.
6. Documentation decision.
7. Review requirements.

Recommended exact write set:

```text
fund_agent/fund/documents/candidates/evidence_anchor_mapping.py
tests/fund/documents/test_docling_evidence_anchor_mapping.py
docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-plan-20260616.md
```

Conditional write set:

```text
fund_agent/fund/README.md
```

Only update README if the accepted implementation changes documented candidate mapping behavior. Do not update README merely because evidence metrics changed.

## 7. Allowed Commands For Implementation Planning

```bash
sed -n '<range>p' <allowed-file>
rg '<pattern>' <allowed-file...>
jq '<filter>' reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json
jq '<filter>' reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json
python -m json.tool reports/docling-field-correctness-anchor-coverage-root-cause/20260616/anchor_coverage_root_cause_matrix.json >/dev/null
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
git diff --check
```

No live/network/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM commands are allowed.

## 8. Acceptance Criteria For The Later Implementation Gate

The later implementation gate should be accepted only if:

- targeted tests pass;
- `git diff --check` passes;
- candidate-only status remains programmatically enforced;
- public `EvidenceAnchor` is not imported or returned by candidate mapping;
- accepted local root-cause rows improve under no-live evidence;
- ambiguous duplicate and outside-span cases still fail closed;
- release/readiness remains `NOT_READY`.

Suggested no-live evidence threshold:

```text
minimum: anchor_present_for_reference_facts > 44 / 72
target: 72 / 72 if deterministic section rules support all 28 rows
must preserve: S5 remains 17 / 17
must preserve: 0 locator collisions
```

If the implementation improves some rows but not all, the evidence must classify remaining rows with closed reason codes and route them to either another implementation planning gate or reduced-scope controller decision.

## 9. Review Requirements

Plan review must be done by two review workers before implementation.

Reviewers must verify:

- the plan addresses both `duplicate_section_heading` and `missing_section_context`;
- no production boundary is crossed;
- fail-closed behavior remains explicit;
- tests cover positive and negative cases;
- acceptance criteria are measurable;
- the plan does not use performance/cache/cost evidence to bypass anchor coverage.

Review verdict tokens:

```text
REVIEW_PASS_NOT_READY
REVIEW_BLOCKED_NEEDS_FIX_NOT_READY
```

## 10. Stop Conditions

Stop before implementation if:

- root-cause evidence has not been reviewed and accepted by controller;
- implementation requires public `EvidenceAnchor` schema changes;
- implementation requires production parser/repository behavior changes;
- deterministic duplicate-heading disambiguation cannot be specified without manual review;
- page-span fallback would allow cross-section or out-of-report tables to map;
- test fixtures cannot prove both recovery and fail-closed behavior.

## 11. Final Gate Design Verdict

```text
VERDICT: GATE_DESIGN_READY_FOR_ROOT_CAUSE_REVIEW_THEN_IMPLEMENTATION_PLANNING_NOT_READY
```
