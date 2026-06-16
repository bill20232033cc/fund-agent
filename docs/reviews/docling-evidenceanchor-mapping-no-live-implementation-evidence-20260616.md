# Docling EvidenceAnchor Mapping No-live Implementation Evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping No-live Implementation Gate`
Role: implementation worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records the no-live implementation evidence for candidate-only Docling EvidenceAnchor semantic mapping.

This gate implemented candidate-internal mapping only. It did not change `EvidenceAnchor` schema, `FundDocumentRepository`, parser/source policy, Service, Host, UI, renderer, quality gate, CHAPTER_CONTRACT, provider/LLM route, readiness, release, PR, push or merge state.

## 2. Source Changes

| Path | Status | Purpose |
| --- | --- | --- |
| `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` | added | Candidate-only mapping models and helpers from `CandidateRepresentationDocument` to EvidenceAnchor semantic fields. |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | added | No-live tests for happy paths, stop paths, metadata guardrails and production isolation. |

No README update was made because the helper remains candidate-internal and does not add a public usage contract or test grouping.

## 3. Candidate-only Design Evidence

Implemented candidate-only output models:

- `CandidateEvidenceAnchorFields`
- `CandidateEvidenceAnchorMapping`
- `CandidateEvidenceAnchorMappingBlocked`
- `CandidateEvidenceAnchorMappingResult`

The mapping API returns candidate wrapper objects, not production `EvidenceAnchor` objects. It has no `to_evidence_anchor`, `as_evidence_anchor`, `to_production_anchor` or equivalent production admission helper.

Required non-proof metadata is enforced on mapped outputs:

- `candidate_source="docling"`
- `candidate_only=True`
- `schema_family`
- `sample_id`
- `field_correctness_status="not_proven"`
- `source_truth_status="not_proven"`

The internal `fields.source_kind="annual_report"` mirrors current annual-report EvidenceAnchor semantics only inside the candidate wrapper. It is not a new production `source_kind` and is not exported through `fund_agent.fund.documents`.

## 4. Mapping Behavior Evidence

Implemented block mappings:

| Block | Accepted behavior |
| --- | --- |
| heading | Maps only with stable annual-report section and page. `table_id=null`, `row_locator=null`. |
| paragraph | Maps only with stable annual-report section and page. `table_id=null`, `row_locator=null`. |
| table | Maps only with stable annual-report section, table id and page. `row_locator=null`. |
| cell | Maps only with stable parent table, section, page and deterministic cell position. |

Implemented stop paths:

| Stop path | Evidence |
| --- | --- |
| unsupported source route | Non-Docling candidates are blocked with `unsupported_source_kind`. |
| missing section | Blocks with `missing_section_context`. |
| ambiguous section | Blocks with `unstable_section_context`. |
| missing page | Blocks with `missing_page_number`. |
| ambiguous or absent parent table | Blocks with `cannot_resolve_parent_table`. |
| S4/S5/S6 missing tuple member | Blocks with `missing_cell_position`. |
| S4/S5/S6 duplicate tuple | Blocks with `ambiguous_cell_tuple`. |

Implemented S1 parent table resolution:

1. shared table/source ref when unique;
2. unique bbox containment on the same page;
3. otherwise fail closed.

The implementation supports multi-page S1 table safety by blocking cell mapping when a multi-page table lacks an explicit cell page.

Implemented S4/S5/S6 tuple resolution:

```text
table_id + table.page_number + cell_index + row_start + column_start
```

Duplicate tuple and missing tuple member cases fail closed.

Section family source is closed in the module docstring and constants: explicit `§` annual-report section tokens plus a small closed annual-report heading keyword family. Keyword inference from paragraph/cell text is not used.

## 5. Validation

Commands run:

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_candidate_models.py -q
uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
git diff --check -- fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
uv run coverage run -m pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
uv run coverage report -m fund_agent/fund/documents/candidates/evidence_anchor_mapping.py
```

Results:

| Command | Result |
| --- | --- |
| targeted mapping tests | `9 passed` |
| mapping + Docling locator/candidate model tests | `21 passed` |
| ruff check | `All checks passed!` |
| scoped diff check | pass |
| coverage run | `9 passed` |
| coverage report | `87%` for `evidence_anchor_mapping.py` |

The accepted plan's pytest-cov module command:

```bash
uv run pytest --cov=fund_agent.fund.documents.candidates.evidence_anchor_mapping --cov-report=term-missing tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

was attempted but failed during collection because pytest-cov imported the `fund_agent` top-level package as a coverage source and reached `akshare -> pandas -> numpy`, which raised `ImportError: cannot load module more than once per process`. The alternate `coverage run` + file report path collected valid coverage without expanding into source acquisition imports.

## 6. Boundary Checks

`rg` check:

```bash
rg -n "to_evidence_anchor|as_evidence_anchor|to_production_anchor|EvidenceAnchor\\(" fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

Result: no matches.

`git diff --name-only` result before evidence artifact creation: no tracked diff. Current implementation files are untracked allowed-write-set files until controller acceptance/staging.

Historical untracked residue remains unrelated and was not used as proof.

## 7. Residuals

| Residual | Owner | Status |
| --- | --- | --- |
| Candidate mappings are not source truth or field correctness proof. | Future evidence gate | Accepted residual |
| Candidate mappings are not production `EvidenceAnchor` admission. | Future design/implementation gate | Accepted residual |
| Docling baseline promotion is not decided by this gate. | Future baseline disposition gate | Deferred |
| Field correctness comparison against PDF/source truth is not performed. | Future comparative evidence gate | Deferred |
| Coverage command using pytest-cov module source expands into source acquisition imports. | Tooling follow-up if needed | Accepted residual; alternate coverage evidence recorded |

## 8. Final Verdict

```text
VERDICT: IMPLEMENTED_AND_VALIDATED_NO_LIVE_NOT_READY
```
