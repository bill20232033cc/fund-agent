# Docling EvidenceAnchor Mapping Section-context Enrichment Plan - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## Scope

Design a deterministic, candidate-only section-context enrichment and normalization path for Docling candidate EvidenceAnchor mapping. The next implementation gate should improve table/cell candidate mapping from the current heading-only partial evidence while preserving fail-closed behavior.

This plan is limited to Fund documents candidate internals under `fund_agent/fund/documents/candidates/`. It does not authorize source, parser, repository, Service, Host, UI, renderer, quality gate, provider/LLM, CHAPTER_CONTRACT, production `EvidenceAnchor` schema, readiness, release, PR, push, merge or baseline promotion changes.

## Source Evidence

| Source | Evidence used |
| --- | --- |
| `AGENTS.md` | Production document access must stay behind `FundDocumentRepository`; Service/UI/Host/renderer/quality gate must not directly call parser/source/cache helpers; evidence must stay traceable and fail-closed. |
| `docs/design.md` | Docling is candidate-layer annual-report document representation only; Docling output is not source truth, not parser replacement and not production EvidenceAnchor proof. |
| `docs/implementation-control.md` | Current gate is heavy planning for deterministic section-context enrichment; release/readiness remains `NOT_READY`. |
| `docs/current-startup-packet.md` | Current accepted mapping evidence is partial heading-only with table/cell anchor yield zero; candidate/production isolation remains binding. |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-controller-judgment-20260616.md` | Verdict `ACCEPT_PARTIAL_HEADING_ONLY_MAPPING_EVIDENCE_NOT_READY`; next gate should decide section-context enrichment, heading normalization and S1 envelope handling. |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` | Accepted real-artifact matrix: `102 / 23475 = 0.43%` mapped, `23373` blocked, `missing_section_context=23363`, `unstable_section_context=10`, table/cell yield zero. |
| `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` | Current helper resolves sections from explicit `§` tokens, closed keyword families and limited block/document fields; output is candidate wrapper, not production `EvidenceAnchor`. |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | Synthetic tests already prove candidate-only wrapper, table/cell happy path, parent-table resolution and fail-closed behavior when stable section context exists. |

## Accepted Facts

- Evidence Gate accepted only partial heading-only mapping.
- Total mapped count is `102 / 23475 = 0.43%`.
- Total blocked count is `23373`.
- Blocked reason distribution is `missing_section_context=23363`, `unstable_section_context=10`.
- Table/cell anchor yield is currently zero on accepted real artifacts.
- S1 full JSON is not the current candidate envelope schema and is rejected by `unsupported candidate representation schema_version`.
- S1 current envelope maps headings only.
- Candidate anchors remain non-production, not source truth, not field-correctness proof, not baseline promotion proof and not readiness proof.

## Non-goals

- No live/network/PDF/FDR/source acquisition.
- No Docling conversion, pdfplumber export or parser replacement.
- No production `EvidenceAnchor` schema change or bare production `EvidenceAnchor` construction.
- No repository/cache/source policy/fallback change.
- No Service/Host/UI/renderer/quality gate/provider/LLM/CHAPTER_CONTRACT change.
- No analyze/checklist/golden/readiness/release/PR/push/merge/stage/commit action.
- No baseline promotion until comparative correctness plus runtime/cache/cost evidence are accepted by later gates.

## Root Cause Hypotheses

| ID | Hypothesis | Evidence status | Planning consequence |
| --- | --- | --- | --- |
| H1 | Real headings often use annual-report numeric headings such as `2.1 基金基本情况` instead of explicit `§2` tokens. | Supported by evidence representative blocked samples. | Add closed deterministic heading-token normalization for numbered Chinese annual-report headings. |
| H2 | Table/cell blocks have strong table/cell locator coverage but lack section context in the form consumed by the mapping helper. | Supported by accepted full-document coverage and zero table/cell mapping yield. | Build a stable section index and propagate nearest stable section context to table/cell blocks. |
| H3 | Cover/title/header/footer-like headings create section candidates that are not annual-report body sections. | Supported by blocked representative cover headings. | Exclude non-body report-title headings from section index; do not infer sections from fund title/date lines. |
| H4 | Duplicate or repeated headings can make page-based propagation unsafe. | Plausible from annual-report TOC/body repetition; not yet directly quantified. | Add duplicate/unstable handling and explicit blocked reason codes instead of guessing. |
| H5 | Parent table resolution is not the dominant blocker once mapping is run through document-level nested tables. | Supported by synthetic tests and evidence blocker distribution dominated by section context. | Preserve existing structural parent-table rules; do not add content-based parent resolution. |

## Implementation Slices

### Slice 1: Section Token Normalization

Add a private normalizer in `evidence_anchor_mapping.py` that converts stable annual-report heading tokens to top-level `§1` through `§10` candidates.

Accepted patterns should be closed and deterministic:

- explicit `§2`, `§ 2`, `§2  基金简介`;
- numeric body headings such as `2 基金简介`, `2.1 基金基本情况`, `8.4 报告期末按行业分类的股票投资组合`;
- Chinese chapter markers such as `第2章 基金简介` only when the number is Arabic and within `1..10`;
- full-width digits and punctuation after Unicode NFKC normalization.

The normalizer must not accept arbitrary numbers. Numeric headings map to an annual section only when the top-level number is `1..10` and the normalized heading text matches the closed keyword family for that section or an accepted section-family alias added in the same helper.

The implementation must change the existing numeric-heading candidate path in `_section_candidates_from_texts()`: an Arabic heading prefix in `1..10` must not immediately add `§N` and bypass closed keyword-family validation. The current pattern-match-and-`continue` behavior is insufficient for numeric headings. Positive and negative examples are binding:

- `8.4 报告期末按行业分类的股票投资组合` maps to `§8` after NFKC normalization because `8` is supported and the remaining heading text matches the exact accepted `§8` alias.
- `8.3 任意无关文本` blocks as `unsupported_heading_number` because the numeric prefix is supported but the remaining heading text does not match the closed `§8` keyword family or exact accepted aliases.
- Chinese numerals such as `二、基金简介`, bracketed Chinese numerals such as `（二）基金基本情况`, Chinese section markers without Arabic numbers such as `第八节 基金投资组合报告`, and unsupported separators outside the closed pattern such as `2、基金简介` block as `unsupported_heading_number` unless separately accepted by a later controller gate.
- `§2.1 基金基本情况` remains governed by the explicit `§` token path; it may map to top-level `§2` only if the explicit-token parser normalizes top-level section id without using unsupported numeric-heading fallback.

Exact initial alias additions:

- `§2`: `基金基本情况`
- `§8`: `报告期末按行业分类的股票投资组合`, `报告期末基金资产组合情况`
- `§9`: `期末基金份额持有人户数及持有人结构`

No other alias may be added by implementation-worker discretion. Additional aliases require later evidence and controller acceptance.

### Slice 2: Stable Section Index

Build a deterministic internal section index from `document.sections` before block mapping.

Rules:

- Index only section nodes that normalize to exactly one supported annual-report section.
- Ignore cover/report-title/date headings that do not normalize to `§1..§10`.
- Directory or table-of-contents section nodes must not seed stable body section spans when a deterministic TOC signal is present, such as an explicit TOC/目录 node, a section path under a TOC/目录 parent, or another accepted structural TOC marker in the candidate representation.
- If TOC/body cannot be distinguished safely and the same annual section family appears in both candidate locations, the duplicate section family must fail closed instead of guessing which node is body.
- Exclude section nodes with `page=None` or `page<=0` from the stable index.
- Build an internal frozen `SectionIndex` or equivalent private structure once in `map_candidate_document_anchor_candidates()` and pass it through internal helper calls. Do not change public API signatures.
- The index should store selected body start page per annual section family, duplicate/unsafe section families, and span boundaries needed for propagation.
- Monotonic ordering means inter-section top-level ordering by each annual section family's selected body start page. Same-section child nodes do not independently break monotonic order.
- The selected body start page is the minimum safe body page for that annual section after TOC exclusion.
- If selected body start pages place a later top-level annual section before an earlier top-level annual section, block affected propagation with `section_order_not_monotonic`.
- If two distinct body section nodes normalize to the same annual section and cannot be proven to be the same source node or same selected body start, mark that section family as duplicate and unsafe for propagation with `duplicate_section_heading`.
- Section spans are half-open `[start_page, next_start_page)`. A block page equal to `next_start_page` belongs to the next section, not the previous section.
- Never infer across an unstable, duplicate, non-monotonic or unknown section boundary.

### Slice 3: Section Propagation to Tables and Text Blocks

For `CandidateTextBlock` and `CandidateTableBlock`, resolve section context by precedence:

1. block-owned explicit section candidates from normalized `section_id`, `heading_path`, caption/label where available;
2. unique matching `CandidateSectionNode` when block `section_id` equals a document section id;
3. page-based nearest previous stable section span when the block page or all table pages fall inside one stable section span.

If a table spans pages across two stable section spans, block with `section_span_crosses_multiple_sections`. If a table has no stable page number and no section candidate, block with `missing_section_context`. Page-based propagation must use the `SectionIndex` built once for the document; it must not rescan and rebuild section state per block.

### Slice 4: Cell Section Inheritance From Parent Table Only

Cells must inherit annual-report section context from their resolved parent table. Do not infer annual-report section from `row_label_path`, `column_header_path` or cell text because those are table facts, not document-section locators.

The implementation must include a test proving cells do not infer annual-report section from `row_label_path` or `column_header_path`. Cleanup of the existing `_section_candidates_from_block()` `CandidateTableCell` branch is optional implementation detail only if it remains inside the accepted implementation write set; the behavioral invariant is mandatory.

Parent table resolution remains deterministic:

- explicit parent table argument from document-level iteration first;
- unique structural `source_ref` / table id match second;
- unique same-page bbox containment third;
- otherwise fail closed with `cannot_resolve_parent_table`.

### Slice 5: Blocked Reason Taxonomy

Add explicit blocked reason codes so re-evidence can distinguish true section gaps from safety stops:

- `missing_section_context`
- `unstable_section_context`
- `duplicate_section_heading`
- `section_order_not_monotonic`
- `section_span_crosses_multiple_sections`
- `unsupported_heading_number`
- existing parent/table/cell/page codes remain unchanged.

### Slice 6: S1 Envelope Disposition

Do not make `project_candidate_representation()` accept arbitrary S1 full JSON in the enrichment implementation gate. The first implementation should map only current accepted candidate envelopes.

S1 full JSON handling should be a separate evidence/export disposition:

- preferred route: regenerate or export S1 full artifact as `candidate_annual_report_representation.v1` through the accepted candidate export path, then re-run mapping evidence;
- fallback route: keep S1 full JSON as blocked schema-shape residual and use S1 current envelope only for current-envelope evidence.

No helper should silently treat S1 full JSON as current envelope schema.

## Exact Allowed Write Set for Later Implementation

The next no-live implementation gate should write only:

- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`

Do not write source, repository, parser, source policy, production `EvidenceAnchor`, representation model schema, CHAPTER_CONTRACT, Service, Host, UI, renderer, quality gate, provider/LLM, README, design, control docs, reports, cache or artifacts in the implementation gate.

If the controller chooses S1 full-envelope regeneration, that must be a separate gate with a separate allowed write set; it is not part of this first implementation write set.

## Deterministic Enrichment Rules

1. Normalize heading text with NFKC and whitespace collapse before pattern matching.
2. Extract explicit `§` section tokens first.
3. Extract annual-report numeric prefixes second, but only for top-level `1..10` and only when the remaining heading text matches the closed section keyword family or the exact initial aliases in Slice 1; do not add `§N` immediately after regex match.
4. Resolve section candidates from block-owned fields before page propagation.
5. Use page propagation only from a stable `SectionIndex` built once from document section nodes after TOC exclusion and positive-page filtering.
6. Propagate nearest stable section context to tables and text blocks only when the block page range is fully inside one half-open stable section span.
7. Cells inherit section context from the resolved parent table only.
8. Parent table resolution must remain structural and unique; no text, row label, value or field-correctness heuristic may resolve parentage.
9. Duplicate headings, out-of-order headings and multi-section spans block mapping instead of picking a best guess.
10. Mapped outputs must preserve `candidate_only=True`, `candidate_source="docling"`, `field_correctness_status="not_proven"` and `source_truth_status="not_proven"`.

## Fail-closed Stop Rules

Stop and return blocked records when any of the following occurs:

- source kind is not `docling_pdf_candidate`;
- candidate envelope schema is unsupported;
- normalized heading maps to zero or multiple annual sections;
- normalized section is outside `§1..§10` or uses an unsupported numeric heading pattern;
- stable section index has duplicate or non-monotonic annual section boundaries for the target span;
- block has no page and no explicit stable section context;
- table page range crosses multiple stable section spans;
- cell parent table cannot be resolved structurally and uniquely;
- cell position tuple is missing or duplicate under `S4_S5_S6_lightweight`;
- mapping would require changing proof statuses or creating production `EvidenceAnchor`;
- S1 full JSON is not regenerated as current envelope but is treated as if it were.

## Tests and Validation Commands

Future implementation should add no-live synthetic tests for these concrete fixtures:

- numeric heading positive: section/text heading `2.1 基金基本情况` normalizes to `§2`.
- explicit token and NFKC positive: `§ 2 基金简介` and full-width `２．１ 基金基本情况` normalize to `§2` after NFKC.
- numeric heading closed-family guard: `8.4 报告期末按行业分类的股票投资组合` maps to `§8`; `8.3 任意无关文本` blocks as `unsupported_heading_number`.
- unsupported heading number and pattern guard: `11.1 任意文本`, `二、基金简介`, `（二）基金基本情况`, `第八节 基金投资组合报告`, and `2、基金简介` each block as `unsupported_heading_number`.
- TOC exclusion: a deterministic TOC/目录 section node for `§2 基金简介` on page 2 and body `§2 基金简介` on page 5 must select page 5 as the `§2` body start, not mark the body span duplicate.
- unsafe TOC/body ambiguity: if the same fixture lacks a deterministic TOC signal and the two `§2` nodes cannot be distinguished safely, propagation for `§2` blocks as `duplicate_section_heading`.
- duplicate body heading: two distinct body section nodes both normalize to `§8` with different section ids or unsafe starts; a table inside the affected span blocks as `duplicate_section_heading`.
- monotonic violation: selected body starts place `§8` before `§3`; page-based propagation for affected blocks returns `section_order_not_monotonic`.
- same-section child ordering: multiple `§8.x` child nodes under the selected `§8` body span do not independently trigger `section_order_not_monotonic`; the selected body start remains the minimum safe body page after TOC exclusion.
- page-based table inherit: stable starts `§3` page 10 and `§8` page 60, table page 62 with no heading path maps to `§8`.
- half-open boundary: with spans `[10, 60)` for `§3` and `[60, next)` for `§8`, table page 60 maps to `§8`.
- missing page blocked: table with no stable page, no page range and no explicit section context blocks as `missing_section_context`.
- cross-section multi-page table blocked: table pages 58-62 across `§3` `[10, 60)` and `§8` `[60, next)` blocks as `section_span_crosses_multiple_sections`.
- cell parent inheritance only: a cell under a parent table mapped to `§8` maps to `§8`; a cell whose `row_label_path` or `column_header_path` contains `§2` must not override or independently infer section from those labels.
- cover/report-title headings remain blocked as `missing_section_context`.
- S1 full JSON schema mismatch remains blocked outside this implementation.

Allowed later validation commands:

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
git diff --check
```

Optional later no-live evidence command, only in a separate evidence gate, may run a local JSON dry-run over accepted artifacts without live/network/PDF/FDR/source acquisition.

## Re-evidence Design

The follow-up evidence gate should use the same accepted local candidate envelopes:

- S1 current envelope: `reports/representation-json/004393_2025_docling_current_envelope.json`
- S4 full envelope: `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json`
- S5 full envelope: `reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json`
- S6 full envelope: `reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json`

Evidence output should include:

- per-sample section/text/table/cell counts;
- mapped total and mapped counts by block type;
- blocked total and blocked reason distribution;
- before/after comparison against accepted baseline `102 / 23475 = 0.43%`;
- explicit table/cell yield and examples;
- representative blocked samples for each new fail-closed reason;
- S1 full JSON disposition as either blocked schema residual or regenerated current-envelope evidence;
- repeated candidate-only status assertions.

Acceptance should require table or cell candidate yield greater than zero on accepted real artifacts without reducing fail-closed guardrails. It still must not claim source truth, full field correctness, baseline promotion, production parser replacement or readiness.

## Residual Risks

- Numeric heading normalization may increase false-positive section mapping if closed keyword families are too broad.
- Page-based propagation can be unsafe around TOC, repeated headings, headers/footers or cross-page tables.
- Duplicate heading handling may reduce yield but is necessary to avoid source-truth claims.
- S1 full JSON remains incomplete for full-document S1 mapping until regenerated/exported as current candidate envelope.
- Table/cell candidate yield does not prove field correctness; later comparative correctness evidence is still required.
- Runtime/cache/cost containment must be re-evidenced before any Docling baseline disposition.

## Review Criteria

Review should verify:

- plan stays inside Fund documents candidate internals;
- exact later write set is narrow and excludes production/runtime/control surfaces;
- section normalization is closed, deterministic and auditable;
- table/cell propagation uses stable section index and unique structural parent-table resolution;
- duplicate/unstable heading behavior is fail-closed;
- S1 full JSON mismatch is not silently bypassed;
- candidate-only and `NOT_READY` guardrails are explicit;
- tests cover both positive enrichment and safety stops.

## Completion Criteria

This planning gate is complete when:

- this artifact is reviewed by designated reviewers or controller;
- controller accepts or amends the exact later implementation write set;
- controller chooses whether S1 full JSON regeneration is separate/deferred or required before re-evidence;
- release/readiness remains `NOT_READY`.

The later implementation gate is complete only after targeted no-live tests and lint/diff checks pass within the accepted write set. The later evidence gate is complete only after accepted local artifacts are re-run and table/cell candidate yield plus blocked distributions are recorded without production claims.

## Next Gate Recommendation

Recommended next gate:

```text
Docling EvidenceAnchor Mapping Section-context Enrichment Plan Re-review Gate
```

If accepted, route to:

```text
Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Gate
```

Then route to:

```text
Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Gate
```

Defer baseline promotion until after comparative correctness evidence and runtime/cache/cost evidence are accepted.

## Final Verdict

```text
VERDICT: PLAN_FIXED_READY_FOR_RE_REVIEW_NOT_READY
```
