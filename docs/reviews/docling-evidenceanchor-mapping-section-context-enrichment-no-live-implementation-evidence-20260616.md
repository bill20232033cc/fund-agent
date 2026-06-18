# Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Gate`
Implementation worker: AgentCodex
Controller: AgentController
Release/readiness: `NOT_READY`

## Scope

Implemented the accepted plan from:

- `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md`
- `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-controller-judgment-20260616.md`

Allowed write set used:

- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`

No source acquisition, repository/cache/downloader, parser production behavior, source policy, production `EvidenceAnchor` schema, CHAPTER_CONTRACT, Service, Host, UI, renderer, quality gate, provider/LLM, README, design, control, report, readiness, release, PR, push or merge files/actions were changed.

## Implementation Summary

- Added deterministic section-context enrichment for candidate-only Docling mapping.
- Added an internal document-level section index built once in `map_candidate_document_anchor_candidates()` and passed through private helper calls.
- Preserved public API signatures for `map_candidate_document_anchor_candidates()` and `map_candidate_locator_to_anchor_candidate()`.
- Added closed numeric heading normalization with NFKC handling and explicit unsupported-number fail-closed behavior.
- Added exact accepted aliases for `§2`, `§8` and `§9`; no discretionary alias expansion was added.
- Added deterministic TOC/目录 exclusion for section index span seeding.
- Added duplicate-section, non-monotonic-section, multi-section-span and unsupported-heading blocked reason paths.
- Added page-based propagation for text/table blocks only when a block page range is inside one stable half-open section span.
- Preserved cell section inheritance from the resolved parent table only; cells do not infer section context from row or column labels.
- Preserved candidate-only output metadata: `candidate_only=True`, `candidate_source="docling"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`.

## Test Coverage Added

New tests cover:

- positive numeric heading normalization for `2.1 基金基本情况`, explicit `§ 2`, full-width `２．１`, and `8.4 报告期末按行业分类的股票投资组合`;
- unsupported numeric/chinese heading patterns including `8.3 任意无关文本`, `11.1`, Chinese numerals, Chinese section markers and unsupported separator `2、`;
- TOC exclusion and unsafe TOC/body ambiguity;
- duplicate body headings;
- inter-section monotonic violations and same-section child headings;
- page-based table inheritance and half-open section span boundaries;
- missing page blocked as `missing_section_context`;
- cross-section multi-page table blocked as `section_span_crosses_multiple_sections`;
- cell parent-section inheritance and no row/column label section inference;
- cover/report-title heading blocking;
- S1 full JSON schema mismatch remaining blocked by the candidate envelope parser.

## Validation

Controller re-ran the implementation worker's validation commands:

```text
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
34 passed in 0.69s
```

```text
uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

Result:

```text
All checks passed!
```

```text
git diff --check
```

Result: passed.

## Residuals

| Residual | Status |
| --- | --- |
| Table/cell yield on accepted real artifacts | still unproven; requires re-evidence gate |
| Field correctness | not proven |
| Source truth | not proven |
| S1 full JSON current-envelope mismatch | still deferred |
| Runtime/cache/cost baseline suitability | not proven by this implementation |
| Release/readiness | `NOT_READY` |

## Next Review Gate

Proceed to DS/MiMo implementation review before controller acceptance.

## Final Status

```text
IMPLEMENTED_AND_VALIDATED_NO_LIVE_NOT_READY
```
