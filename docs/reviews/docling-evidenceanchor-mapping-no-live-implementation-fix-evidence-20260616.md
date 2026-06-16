# Docling EvidenceAnchor Mapping No-live Implementation Fix Evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping No-live Implementation Fix Gate`
Role: fix worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records the no-live fix after implementation review findings.

No production code path, `EvidenceAnchor` schema, `FundDocumentRepository`, parser/source policy, Service, Host, UI, renderer, quality gate, CHAPTER_CONTRACT, provider/LLM route, readiness, release, PR, push or merge state was changed.

## 2. Accepted Findings Fixed

| Finding | Source | Fix |
| --- | --- | --- |
| DS2-F4: S4/S5/S6 section-hierarchy-absent test missing | AgentDS review | Added S4/S5/S6 tests for missing section tree with one-to-one heading-path mapping and ambiguous heading-path blocking. |
| DS-IMPL-F1: S4/S5/S6 cell happy path test absent | AgentDS review | Added S4/S5/S6 happy-path test for exact `table_id + page + cell_index + row_start + column_start` tuple mapping. |
| MIMO-IMPL-F1: missing/unstable distinction incomplete for S4/S5/S6 | AgentDS review residual / MiMo prior finding | Added S4/S5/S6 ambiguous heading-path test asserting `unstable_section_context` and retained missing-section test asserting `missing_section_context`. |

## 3. Files Changed

| Path | Change |
| --- | --- |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | Added three no-live tests. |

No implementation code was changed in this fix pass.

## 4. Validation

Commands run:

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
git diff --check -- fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-evidence-20260616.md docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-review-ds-20260616.md docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-review-mimo-20260616.md
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_candidate_models.py -q
uv run coverage run -m pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
uv run coverage report -m fund_agent/fund/documents/candidates/evidence_anchor_mapping.py
```

Results:

| Command | Result |
| --- | --- |
| mapping tests | `12 passed` |
| ruff check | `All checks passed!` |
| scoped diff check | pass |
| mapping + adjacent Docling candidate tests | `24 passed` |
| coverage run | `12 passed` |
| coverage report | `87%` |

## 5. Final Verdict

```text
VERDICT: FIX_IMPLEMENTED_AND_VALIDATED_NO_LIVE_NOT_READY
```
