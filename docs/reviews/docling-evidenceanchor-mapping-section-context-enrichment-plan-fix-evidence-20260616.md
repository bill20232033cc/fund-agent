# Docling EvidenceAnchor Mapping Section-context Enrichment Plan Fix Evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Plan Fix Gate`
Role: plan-fix worker
Release/readiness: `NOT_READY`

## Scope Boundary

This fix evidence covers only controller-accepted review findings for:

- `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md`
- `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-review-ds-20260616.md`
- `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-review-mimo-20260616.md`
- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` as needed to identify the existing numeric-heading and cell-label branches.

No source, tests, control docs, design docs, README, reports, cache, repository, parser, source policy, production `EvidenceAnchor` schema, CHAPTER_CONTRACT, Service, Host, UI, renderer, quality gate, provider or LLM files were modified. No live, network, PDF, FDR, source acquisition, analyze, checklist, golden, readiness, release, stage, commit, push or PR action was performed.

## Finding Disposition Table

| Finding | Disposition | Changed plan locations | Residuals |
| --- | --- | --- | --- |
| MiMo 01 / DS-F3 numeric heading closure | accepted | Slice 1; Deterministic Enrichment Rules; Fail-closed Stop Rules; Tests and Validation Commands | Implementation must still change `_section_candidates_from_texts()` so numeric prefixes `1..10` do not bypass closed keyword-family validation. |
| DS-F1 / OQ1 deterministic TOC handling | accepted | Slice 2; Tests and Validation Commands | If TOC/body distinction is unsafe, duplicate section family remains fail-closed; no heuristic body guessing authorized. |
| DS-F2 monotonic ordering precision | accepted | Slice 2; Tests and Validation Commands | Monotonicity is limited to inter-section selected body start ordering; same-section child nodes remain non-breaking unless they create duplicate unsafe body starts. |
| DS-F4 / OQ2 alias scope | accepted | Slice 1 | Alias additions are exact initial aliases only; any additional alias requires later evidence and controller acceptance. |
| DS-F5 plus MiMo 02/03 test fixture gaps | accepted | Tests and Validation Commands | Tests are still future implementation-gate work inside the accepted implementation write set only. |
| DS-F6 / OQ3 internal SectionIndex and span semantics | accepted | Slice 2; Slice 3; Deterministic Enrichment Rules; Tests and Validation Commands | Internal helper signatures may change privately, but public API signatures must not change. |
| MiMo 04 cell label dead branch | deferred-but-tested | Slice 4; Tests and Validation Commands | Code cleanup remains optional implementation detail inside exact write set; behavioral test proving no row/column label section inference is mandatory. |

## Applied Fix Summary

- The plan now explicitly states the existing numeric heading candidate path must be changed so an Arabic prefix in `1..10` does not immediately add `§N` before keyword-family validation.
- The plan adds binding positive and negative heading examples: `8.4 报告期末按行业分类的股票投资组合` maps to `§8`; `8.3 任意无关文本` blocks as `unsupported_heading_number`.
- The plan rejects Chinese numerals, bracketed Chinese numerals, Chinese section markers without Arabic numbers and unsupported separators outside the closed pattern as `unsupported_heading_number` unless separately accepted later.
- The plan replaces "Minimum alias additions" with "Exact initial alias additions" and forbids implementation-worker discretionary alias expansion.
- The plan adds deterministic TOC handling: TOC nodes do not seed body spans when a deterministic TOC signal exists; unsafe TOC/body ambiguity fails closed as duplicate instead of guessing.
- The plan defines monotonic ordering as inter-section top-level ordering by selected body start page and specifies same-section child nodes do not independently break monotonic order.
- The plan requires an internal frozen `SectionIndex` or equivalent private structure built once in `map_candidate_document_anchor_candidates()` and passed internally without public API change.
- The plan excludes section nodes with `page=None` or `page<=0` from the stable index and defines half-open section spans `[start_page, next_start_page)`.
- The plan adds concrete synthetic fixture specs for duplicate section heading, non-monotonic ordering, unsupported heading number, NFKC full-width heading, page-based table inheritance, missing page blocking, cross-section multi-page table blocking, TOC exclusion and unsafe TOC ambiguity.
- The plan treats MiMo 04 as deferred-but-tested by requiring a behavior test proving cells do not infer section from `row_label_path` or `column_header_path`.

## Remaining Residuals

- This is a plan fix only; no implementation or test files were changed.
- Release/readiness remains `NOT_READY`.
- Table/cell yield, field correctness, source truth, baseline promotion, runtime/cache/cost and readiness remain unproven.
- S1 full JSON handling remains deferred to the separate evidence/export disposition described in the plan.

## Final Status

```text
PLAN_FIXED_READY_FOR_RE_REVIEW_NOT_READY
```
