# Docling EvidenceAnchor Mapping No-live Implementation Plan - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping No-live Implementation Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Write a code-generation-ready no-live implementation handoff for mapping candidate Docling locators into current `EvidenceAnchor` semantics while preserving candidate-only isolation.

The future implementation must produce candidate mapping outputs for review, comparison and later extractor projection planning. It must not admit Docling-derived anchors into the production evidence store, replace the current parser, alter source policy, or claim source truth, full field correctness, baseline promotion, release readiness or PR readiness.

## 2. Non-goals

- No source/test/runtime behavior change in this planning gate.
- No `EvidenceAnchor` schema change and no new production `source_kind`.
- No `FundDocumentRepository`, source acquisition, parser cache, Service, Host, UI, renderer, quality gate, CHAPTER_CONTRACT, provider/LLM, analyze/checklist/golden/readiness/release/PR behavior change.
- No Docling conversion, live/network/EID/FDR/PDF/source acquisition, pdfplumber export or manual reference review.
- No use of unrelated untracked residue as proof.
- Preserve `release/readiness = NOT_READY`.

## 3. Direct Evidence Inputs

| Input | Use |
| --- | --- |
| `AGENTS.md` | Rule truth, Fund documents boundary, no direct Service/Host/UI/renderer/quality-gate parser access, testing/doc sync constraints |
| `docs/design.md` relevant EvidenceAnchor / FundDisclosureDocument / Docling sections | Current `EvidenceAnchor` field semantics, candidate `FundDisclosureDocument` boundary, Docling candidate-only status |
| `docs/implementation-control.md` front current-control section | Current active gate, accepted chain, deferred gates and `NOT_READY` guardrails |
| `docs/current-startup-packet.md` | Current startup truth and Docling mapping constraints |
| `docs/reviews/docling-evidenceanchor-mapping-plan-controller-judgment-20260616.md` | Binding constraints for this implementation planning gate |
| `docs/reviews/docling-evidenceanchor-mapping-plan-20260616.md` | Accepted mapping concept and element-level mapping rules |
| `docs/reviews/docling-evidenceanchor-mapping-plan-review-ds-20260616.md` | DS findings DS-F1 through DS-F4 |
| `docs/reviews/docling-evidenceanchor-mapping-plan-review-mimo-20260616.md` | MiMo findings MIMO-F1 through MIMO-F6 |

Bounded accepted facts remain candidate-only: S1/S4/S5/S6 coverage and selected fact matches support mapping implementation planning, not source truth, full field correctness, production parser replacement, baseline promotion or readiness.

## 4. Future Allowed Write Set

Future no-live implementation should write only these paths unless controller narrows them further:

| Path | Purpose |
| --- | --- |
| `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` | New candidate-only mapping logic and public candidate-internal API |
| `fund_agent/fund/documents/candidates/models.py` | Candidate output dataclasses only if existing candidate models need extension |
| `fund_agent/fund/documents/candidates/__init__.py` | Export candidate-internal symbols only if tests require package import |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | Main no-live unit tests for happy paths and stop paths |
| `fund_agent/fund/README.md` | Update only if future implementation changes documented Fund candidate-internals behavior |
| `tests/README.md` | Update only if the new test file changes documented test grouping or commands |

Forbidden future implementation writes without a separate controller-approved gate: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, Service/Host/UI/renderer/quality-gate modules, source acquisition modules, parser cache modules, production extractor fact surfaces, readiness/release/PR artifacts, golden/baseline artifacts.

## 5. Module Ownership Recommendation

Implementation belongs inside Fund documents candidate internals:

```text
fund_agent/fund/documents/candidates/evidence_anchor_mapping.py
```

The module must be candidate-internal and must not be imported directly by Service, Host, UI, renderer or quality gate code. It may depend on existing candidate representation models and locator helpers under `fund_agent/fund/documents/candidates/`. It must not call Docling, parser cache, source helpers, PDF files, live acquisition, `FundDocumentRepository`, provider/LLM, analyzer or checklist commands.

The recommended callable surface is narrow:

```text
map_candidate_locator_to_anchor_candidate(...)
map_candidate_document_anchor_candidates(...)
```

Both functions must return candidate mapping result types, not bare production `EvidenceAnchor` objects or `list[EvidenceAnchor]`.

## 6. Candidate Output Model Strategy

Candidate/production isolation must be programmatic, not convention-only.

Future implementation should add candidate-only output models such as:

```text
CandidateEvidenceAnchorFields
CandidateEvidenceAnchorMapping
CandidateEvidenceAnchorMappingResult
CandidateEvidenceAnchorMappingBlocked
```

Required strategy:

- `CandidateEvidenceAnchorFields` mirrors current `EvidenceAnchor` semantic fields: `source_kind`, `document_year`, `section_id`, `page_number`, `table_id`, `row_locator`, `note`.
- It is not the production `EvidenceAnchor` dataclass and must not subclass it.
- `CandidateEvidenceAnchorMapping` wraps the fields with required metadata: `candidate_source="docling"`, `schema_family`, `sample_id`, `candidate_only=True`, `field_correctness_status="not_proven"`, original locator summary and block type.
- Mapping functions return `CandidateEvidenceAnchorMappingResult`, containing `mapped` and `blocked` candidate records.
- There must be no method named `to_evidence_anchor`, `as_evidence_anchor`, `to_production_anchor` or equivalent production-admission helper in this implementation slice.
- Production evidence store insertion is out of scope. Tests must assert the public mapping API does not return bare `EvidenceAnchor` objects or `list[EvidenceAnchor]`.

`source_kind="annual_report"` may appear only inside `CandidateEvidenceAnchorFields` to express current annual-report evidence semantics. Candidate status must be enforced by the wrapper type and package boundary, not only by `note`.

## 7. Mapping Algorithm Slices

### 7.1 Common Preflight

For every candidate block:

1. Confirm explicit document identity inputs: sample id, fund code, document year, report type when available and schema family.
2. Confirm `candidate_source="docling"` and `candidate_only=True`.
3. Determine schema family: `S1_full` or `S4_S5_S6_lightweight`.
4. Determine block type: heading, paragraph, table, cell or unsupported.
5. Resolve section context using the stability rules in section 10.
6. Resolve page number using block-specific rules.
7. Return a blocked record instead of fabricating any missing required field.

### 7.2 Headings

Output a candidate text anchor when all required fields are stable:

- `source_kind="annual_report"` inside candidate fields only.
- `document_year` from document identity.
- `section_id` from stable section context.
- `page_number` from heading locator.
- `table_id=null`.
- `row_locator=null`.
- `note` includes heading path, original locator summary, candidate metadata and `field_correctness_status=not_proven`.

Stop with `missing_section_context` or `missing_page_number` when section/page cannot be resolved deterministically.

### 7.3 Paragraphs

Output a candidate text anchor only when paragraph locator has stable section and page:

- `table_id=null`.
- `row_locator=null` always.
- paragraph/block identity belongs in candidate metadata and `note`, not in `row_locator`.

Stop on missing section, missing page or unsupported paragraph locator. Future paragraph-specific row semantics require a separate schema/design gate.

### 7.4 Tables

Output a table-level candidate anchor only when parent table identity, section and page are available:

- `table_id` uses the candidate table identity.
- `row_locator=null` by default.
- Do not emit row/value/cell claims from table presence alone.
- `note` preserves table shape, table locator summary and candidate metadata.

`row_locator="table:<ordinal>"` is forbidden in this slice unless the implementation plan defines an explicit ordinal basis. This plan chooses the simpler default: table-level `row_locator=null`.

### 7.5 Cells

Output a cell candidate anchor only with resolved parent-table context:

- `table_id` must come from the parent table, not from a cell-local synthetic value.
- `page_number` uses explicit cell page if present, otherwise parent table page.
- `row_locator` must include cell position at minimum: `cell:r<row_start>:c<column_start>:idx<cell_index>` when `cell_index` is available; for S1 without `cell_index`, use deterministic row/column position and omit the index segment.
- Append row/column header path only when present and deterministic.
- `note` preserves original locator fields, schema family, sample id, text hash or bounded excerpt marker, and `candidate_only=true`.

Stop with `missing_parent_table_context`, `missing_table_id`, `missing_page_number`, `missing_cell_position` or `unsupported_cell_locator` rather than emitting a partial cell anchor.

## 8. S1 Full-schema Parent-table Resolution

S1 resolution must use deterministic structural links only:

1. Prefer explicit parent table reference on the cell object if present.
2. Else prefer containment in the candidate JSON structure: cell nested under a table node or table cell collection.
3. Else use explicit shared table identifier between cell locator and table entry if present.
4. Else, if both cell and table carry bounding boxes, allow bbox containment only when exactly one table on the same page contains the cell bbox.
5. Else stop with `cannot_resolve_parent_table`.

Forbidden S1 heuristics:

- nearest previous table by document order without structural or bbox containment proof;
- page-only matching when multiple tables exist on the page;
- heading/table title text similarity as a parent-table substitute;
- synthetic table ids created from cell-only metadata.

S1 cell implementation must include stop-path tests for ambiguous same-page tables, missing parent links and missing/ambiguous bbox containment.

## 9. S4/S5/S6 Lightweight Parent-table Resolution

S4/S5/S6 resolution is tuple-based:

```text
table_id + table.page_number + cell_index + row_start + column_start
```

Rules:

1. Resolve parent table by exact `table_id` match to a table entry in the same candidate document.
2. Confirm table page from `table.page_number`.
3. Confirm cell tuple has `cell_index`, `row_start` and `column_start`.
4. Confirm no duplicate cell tuple exists under the same `table_id`.
5. Emit a cell candidate only when all tuple fields are present and unique.

Stop with `missing_parent_table_context`, `missing_page_number`, `missing_cell_position` or `ambiguous_cell_tuple` if any required tuple component is absent or non-unique.

If future evidence shows S4/S5/S6 have no table entry to match `table_id`, implementation must fail closed for cell anchors instead of creating table ids from cell tuples.

## 10. Section Stability Rules

A section context is stable only when at least one of these holds:

- explicit candidate section id is present and maps one-to-one to a known annual-report section family in the candidate representation;
- nearest enclosing section hierarchy exists and contains the block without multiple possible parent sections;
- normalized heading path deterministically maps to one annual-report section family with no multi-match ambiguity.

A section context is unstable when:

- section id is missing;
- heading path maps to multiple section families;
- only page proximity is available;
- section is inferred from arbitrary keywords in paragraph/cell text;
- section depends on fund-analysis template chapter inference rather than annual-report document structure.

Missing or unstable section behavior:

- Heading/paragraph/table/cell mappings must return blocked records with `missing_section_context` or `unstable_section_context`.
- Do not emit report-facing candidate anchors with `section_id=null` for Docling PDF annual-report mapping.
- Do not infer fund-analysis template chapter ids in this slice.

For S4/S5/S6, the implementation must first verify whether section hierarchy exists in the lightweight candidate object. If it does not exist, it may use deterministic heading-path mapping only when one-to-one; otherwise it must accept low yield and fail closed for affected blocks.

## 11. Row Locator Rules

| Anchor kind | Rule |
| --- | --- |
| Heading | `row_locator=null`; heading path in metadata/note |
| Paragraph | `row_locator=null`; paragraph/block id in metadata/note |
| Table-level | `row_locator=null`; no ordinal unless separately accepted |
| Cell | `cell:r<row_start>:c<column_start>:idx<cell_index>` when tuple fields exist; S1 may omit `idx` only when no `cell_index` exists and row/column are deterministic |
| Derived metric | Out of scope; existing derived rules unchanged |

Cell `row_locator` must not be used to compensate for missing `table_id`, page or section.

## 12. No-live Test Matrix

Recommended exact test file:

```text
tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

Required cases:

| Case | Fixture shape | Expected result |
| --- | --- | --- |
| S1 heading happy path | explicit section + page locator | mapped candidate with heading metadata, no table fields, `row_locator=null` |
| S1 paragraph happy path | explicit section + page locator | mapped candidate, no table fields, `row_locator=null` |
| S1 table happy path | section + table id + page | mapped table-level candidate, `row_locator=null` |
| S1 cell happy path by parent pointer | cell links to parent table | mapped cell candidate with parent `table_id`, page and cell row locator |
| S1 cell happy path by unique bbox containment | one table bbox contains cell bbox | mapped cell candidate |
| S1 cell stop: ambiguous bbox | two table bboxes contain or match same cell | blocked `cannot_resolve_parent_table` |
| S1 cell stop: page-only table candidate | multiple tables on page, no structural/bbox proof | blocked `cannot_resolve_parent_table` |
| S4/S5/S6 cell happy path | exact `table_id + table.page_number + cell_index + row_start + column_start` | mapped cell candidate |
| S4/S5/S6 stop: missing tuple member | absent `cell_index`, `row_start`, `column_start` or table page | blocked with specific reason |
| S4/S5/S6 stop: duplicate tuple | same tuple appears twice under table | blocked `ambiguous_cell_tuple` |
| Missing section stop | heading/paragraph/table/cell without stable section | blocked, no anchor emitted |
| Missing page stop | Docling PDF locator without page | blocked, no anchor emitted |
| Source-kind boundary | candidate annual-report mapping | no new production `source_kind`; output type is candidate wrapper, not `EvidenceAnchor` |
| Candidate metadata | any mapped output | required `candidate_source`, `schema_family`, `sample_id`, `candidate_only`, `field_correctness_status=not_proven` present |
| Production isolation | public API output | no bare `EvidenceAnchor` or `list[EvidenceAnchor]` returned |
| Service/Host/UI containment | import scan in test or static assertion | mapping module stays under Fund documents candidates; no direct external layer dependency |

Single-file coverage target for the new implementation module should be at least 80% unless implementation evidence records a reviewed residual and follow-up plan.

## 13. Future Validation Commands

Future implementation gate should use only no-live commands such as:

```bash
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_candidate_models.py
uv run pytest --cov=fund_agent.fund.documents.candidates.evidence_anchor_mapping --cov-report=term-missing tests/fund/documents/test_docling_evidence_anchor_mapping.py
git diff --check -- fund_agent/fund/documents/candidates/evidence_anchor_mapping.py fund_agent/fund/documents/candidates/models.py fund_agent/fund/documents/candidates/__init__.py tests/fund/documents/test_docling_evidence_anchor_mapping.py fund_agent/fund/README.md tests/README.md
```

Do not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge commands in the implementation gate unless a later controller gate explicitly authorizes them.

## 14. Docs Decision

This planning gate writes only this artifact.

Future implementation must not update `docs/design.md`, `docs/implementation-control.md` or `docs/current-startup-packet.md`. If candidate-internal behavior becomes documented public developer surface, update `fund_agent/fund/README.md`. If test grouping or commands change, update `tests/README.md`. Otherwise record "README unchanged; candidate-internal helper only; no public usage contract change" in implementation evidence.

No design truth sync, control truth sync, baseline disposition, release readiness or PR documentation update is authorized by this plan.

## 15. Stop Conditions

Stop and return to controller if any condition occurs:

- Mapping requires changing `EvidenceAnchor` schema or adding a production `source_kind`.
- Candidate output cannot be kept programmatically isolated from production `EvidenceAnchor`.
- Implementation would return or store bare production `EvidenceAnchor` objects.
- Mapping code needs to live outside `fund_agent/fund/documents/candidates/`.
- Service, Host, UI, renderer or quality gate would need direct access to Docling, parser cache, source helpers, PDF files or mapping helpers.
- S1 parent table cannot be resolved by explicit parent link, structural containment, shared id or unique bbox containment.
- S4/S5/S6 tuple-based parent table resolution is missing or ambiguous.
- Section context is missing, unstable or only keyword-inferred.
- Table-level mapping requires ordinal `row_locator` without an accepted ordinal basis.
- Paragraph mapping requires non-null `row_locator`.
- No-live tests cannot cover both happy paths and stop paths.
- Any future worker attempts live/source acquisition, Docling conversion, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge commands.
- Any future worker attempts to use unrelated untracked residue as proof.

## 16. Review Focus For DS And MiMo

AgentDS should review:

- Whether the candidate output model enforces programmatic isolation from production `EvidenceAnchor`.
- Whether S1 parent-table resolution is deterministic enough and rejects ambiguous page/bbox cases.
- Whether S4/S5/S6 tuple resolution is complete and fail-closed.
- Whether section stability and row locator rules are mechanically testable.
- Whether no-live stop-path tests are sufficient for missing parent table, missing section, missing page and ambiguous locator cases.

AgentMiMo should review:

- Whether implementation ownership is fully contained in `fund_agent/fund/documents/candidates/`.
- Whether Service/Host/UI/renderer/quality-gate direct access is blocked by plan and tests.
- Whether candidate metadata and no bare `EvidenceAnchor` output avoid the DS-F1 source-kind boundary risk.
- Whether docs decision avoids design/control drift while respecting README triggers.
- Whether future validation commands remain no-live and do not imply readiness.

## 17. Exact Next Gate Recommendation

Immediate next gate:

```text
Docling EvidenceAnchor Mapping No-live Implementation Plan Review Gate
```

Scope:

- DS and MiMo scoped review of this no-live implementation plan.
- Controller judgment on readiness for a separate no-live implementation gate.
- No code changes, no tests/runtime behavior changes, no Docling conversion, no live/source acquisition, no provider/LLM/analyze/checklist/golden/readiness/release/PR commands.

If accepted by controller, the next implementation gate should be:

```text
Docling EvidenceAnchor Mapping No-live Implementation Gate
```

The implementation gate must preserve candidate-only status and `NOT_READY`.

## 18. Final Verdict

```text
VERDICT: NO_LIVE_IMPLEMENTATION_PLAN_READY_FOR_DS_MIMO_REVIEW_NOT_READY
```
